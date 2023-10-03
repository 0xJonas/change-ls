from asyncio import iscoroutinefunction
from contextvars import ContextVar
from functools import wraps
from logging import INFO, Logger, LoggerAdapter, getLogger
from types import FunctionType, TracebackType
from typing import (TYPE_CHECKING, Any, Callable, Dict, List, MutableMapping,
                    Optional, Tuple, Type, TypeVar, Union, cast, overload)
from uuid import UUID, uuid4


class OperationInfo:
    """
    Information on a specific invocation of an :class:`Operation`.

    .. attribute:: name
        :type: str

        The name of the invoked ``Operation``

    .. attribute:: id
        :type: UUID

        The id of the specific invocation
    """

    name: str
    id: UUID

    def __init__(self, name: str) -> None:
        self.name = name
        self.id = uuid4()

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, OperationInfo) and other.id == self.id and other.name == self.name


_operation_stack: ContextVar[List[OperationInfo]] = ContextVar("_operation_stack", default=[])


if TYPE_CHECKING:
    _LoggerAdapter = LoggerAdapter[Any]
else:
    _LoggerAdapter = LoggerAdapter


class OperationLoggerAdapter(_LoggerAdapter):
    """
    A :class:`logging.LoggerAdapter` which adds properties of the :class:`Operation` stack
    to the :class:`LogRecords`.

    The following attributes are added:

    * ``cls_operation_stack_raw: List[OperationInfo]``: The raw operation stack at the time of the log message.
    * ``cls_operation_stack_names: str``: The names of all operations on the stack as a ``str``. Names are separated by a '.'.
        If there are no operations active, this attribute is ``None``.
    * ``cls_operation_stack_ids: str``: The ids of all operations on the stack as a ``str``. Ids are separated by a '.'.
        If there are no operations active, this attribute is ``None``.
    * ``cls_current_operation_name: str``: The name of the current ``Operation``, i.e. the top of the operation stack.
        If there are no operations active, this attribute is ``None``.
    * ``cls_current_operation_id: str``: The id of the current ``Operation``, i.e. the top of the operation stack.
        If there are no operations active, this attribute is ``None``.
    """

    def __init__(self, logger: Union[Logger, _LoggerAdapter]) -> None:
        super().__init__(logger, {})

    def process(self, msg: str, kwargs: MutableMapping[str, Any]) -> Tuple[Any, MutableMapping[str, Any]]:
        operation_stack = _operation_stack.get()
        length = len(operation_stack)
        extra = {
            "cls_operation_stack_raw": operation_stack,
            "cls_operation_stack_names": ".".join(o.name for o in operation_stack) if length > 0 else None,
            "cls_operation_stack_ids": ".".join(str(o.id) for o in operation_stack) if length > 0 else None,
            "cls_current_operation_name": operation_stack[-1].name if length > 0 else None,
            "cls_current_operation_id": str(operation_stack[-1].id) if length > 0 else None
        }
        kwargs["extra"] = extra
        return msg, kwargs


def _resolve_logger(logger: Optional[Union[str, Logger, _LoggerAdapter]]) -> Optional[OperationLoggerAdapter]:
    if logger is None:
        return None
    elif isinstance(logger, OperationLoggerAdapter):
        return logger
    elif isinstance(logger, Logger) or isinstance(logger, LoggerAdapter):
        return OperationLoggerAdapter(logger)
    else:
        return OperationLoggerAdapter(getLogger(logger))


class Operation:
    """
    An ``Operation`` is used to show a task as context in emitted log messages. ``Operations`` represent
    specific functionalies provided by the library and can contain nested ``Operations``.

    An ``Operation`` can be used as a context manager::

        with Operation("foo"):
            ...  # Any log messages in here will have the context 'foo'
    """

    _name: str
    _start_message: Optional[str]
    _end_message: Optional[str]
    _logger: Optional[OperationLoggerAdapter]
    _log_level: int
    _info: Optional[OperationInfo]

    def __init__(self, name: str, logger: Optional[Union[str, Logger, _LoggerAdapter]] = None, start_message: Optional[str] = None, end_message: Optional[str] = None, log_level: int = INFO) -> None:
        """
        Constructs a new ``Operation``.

        :param name: The name of the ``Operation``.
        :param logger: The :class:`logging.Logger` which should log the start and end messages.
            This parameter is optional, but must be present if a start or end message is given.
        :param start_message: Message that should be logged when the ``Operation`` is started.
        :param end_message: Message that should be logged when the ``Operation`` is finished.
        :param log_level: Log level with which the start and end messages should be logged.
        """
        self._name = name
        if logger is None and (start_message is not None or end_message is not None):
            raise ValueError("A logger is required to log start_message or end_message.")
        self._logger = _resolve_logger(logger)
        self._start_message = start_message
        self._end_message = end_message
        self._log_level = log_level
        self._info = None

    def __enter__(self) -> "Operation":
        assert self._info is None
        self._info = OperationInfo(self._name)
        stack = _operation_stack.get()
        stack.append(self._info)
        _operation_stack.set(stack)

        if self._start_message is not None:
            assert self._logger
            self._logger.log(self._log_level, self._start_message)

        return self

    def __exit__(self, exc_type: Type[Exception], exc_value: Exception, traceback: TracebackType) -> bool:
        if self._end_message is not None:
            assert self._logger
            self._logger.log(self._log_level, self._end_message)

        assert self._info is not None
        stack = _operation_stack.get()
        assert stack[-1] == self._info
        stack.pop()
        _operation_stack.set(stack)

        return False


def _reconstruct_argument_dict(func: Callable[..., Any], args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> Dict[str, Any]:
    code = func.__code__

    # Handle positional parameters
    positional_parameters = code.co_varnames[:code.co_argcount]
    default_arguments = func.__defaults__
    arg_values = args + default_arguments if default_arguments else args
    out = {param: value for param, value in zip(positional_parameters, arg_values)}
    out.update({param: kwargs[param] for param in positional_parameters if param in kwargs})

    # Handle variadic parameter
    if (code.co_flags & 0x4) != 0:
        variadic_parameter = code.co_varnames[code.co_argcount]
        out[variadic_parameter] = args[code.co_argcount:]
        kw_parameters_start = code.co_argcount + 1
    else:
        kw_parameters_start = code.co_argcount

    # Handle keyword parameters
    kw_parameters_end = kw_parameters_start + code.co_kwonlyargcount
    keywoard_parameters = code.co_varnames[kw_parameters_start:kw_parameters_end]
    for param in keywoard_parameters:
        if param in kwargs:
            out[param] = kwargs[param]
        else:
            out[param] = func.__kwdefaults__[param]

    # Handle variadic keyword parameter
    if (code.co_flags & 0x8) != 0:
        variadic_keyword_parameter = code.co_varnames[kw_parameters_end]
        known_keyword_parameters = set(code.co_varnames[kw_parameters_start:kw_parameters_end])
        unknown_keyword_parameters = set(kwargs.keys()).difference(known_keyword_parameters)
        out[variadic_keyword_parameter] = {key: kwargs[key] for key in unknown_keyword_parameters}

    return out


_T = TypeVar("_T", bound=Callable[..., Any])


@overload
def operation(name: Optional[str] = None,
              logger_name: Optional[str] = None,
              start_message: Optional[str] = None,
              end_message: Optional[str] = None,
              log_level: int = INFO,
              get_logger_from_context: Optional[Callable[..., Union[Logger, _LoggerAdapter]]] = None) -> Callable[[_T], _T]: ...


@overload
def operation(name: _T,
              logger_name: Optional[str] = None,
              start_message: Optional[str] = None,
              end_message: Optional[str] = None,
              log_level: int = INFO,
              get_logger_from_context: Optional[Callable[..., Union[Logger, _LoggerAdapter]]] = None) -> _T: ...


def operation(name: Union[_T, Optional[str]] = None,
              logger_name: Optional[str] = None,
              start_message: Optional[str] = None,
              end_message: Optional[str] = None,
              log_level: int = INFO,
              get_logger_from_context: Optional[Callable[..., Union[Logger, _LoggerAdapter]]] = None) -> Union[_T, Callable[[_T], _T]]:
    """
    Decorator to turn a function into an :class:`Operation`::

        @operation
        def foo():
            ...

    :param name: The name of the ``Operation``. If this is ``None``, the name of the function
        is used as the ``Operation's`` name.
    :param logger_name: The name of the :class:`logging.Logger` that should log the start and end message.
        This paramter is optional, but one of ``logger_name`` and ``get_logger_from_context``
        must be present if a start or end message is given.
    :param start_message: Message that should be logged when the ``Operation`` is started.
        The message can be an ``str.format()``-style format string referencing the
        decorated function's parameters. It is required that the parameters are referenced by
        name in the format string, positional formatting (e.g. ``"thing: {}"``) is not supported.
    :param end_message: Message that should be logged when the ``Operation`` is finished.
        Similar to ``start_message`` this message can also be formatted by ``str.format()``.
        Note the the formatted messages are created before the decorated function is invoked,
        so the formatted output will reflect the arguments as they were initially passed to the
        function.
    :param log_level: Log level with which the start and end messages should be logged.
    :param get_logger_from_context: Callable which returns a logger from the arguments to
        the decorated function. Since this callable receives the same arguments as the
        decorated function, the callable must have a compatible signature.

        An example use case is to fetch a logger from an object::

            class Thing:
                # ...

                def get_logger(self, *args, **kwargs):
                    return self._logger

                @operation(get_logger_from_context=get_logger, start_message="doing stuff")
                def do_stuff(self):
                    ...
    """
    if type(name) is str:
        name_arg = name
    else:
        name_arg = None

    if logger_name is not None:
        named_logger = getLogger(logger_name)
    else:
        named_logger = None

    def resolve_logger(*args: Any, **kwargs: Any) -> Union[None, Logger, _LoggerAdapter]:
        """
        Try to get a logger from the arguments supplied to the decorator.
        """
        if get_logger_from_context is not None:
            return get_logger_from_context(*args, **kwargs)
        else:
            return named_logger

    def format_start_end_messages(func: _T, args: Tuple[Any, ...], kwargs: Dict[str, Any],
                                  start_message: Optional[str], end_message: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
        if start_message or end_message:
            argument_dict = _reconstruct_argument_dict(func, args, kwargs)
        else:
            argument_dict = {}
        start_message_formatted = start_message.format(**argument_dict) if start_message else start_message
        end_message_formatted = end_message.format(**argument_dict) if end_message else end_message
        return start_message_formatted, end_message_formatted

    def decorator(func: _T) -> _T:
        opname: str = name_arg if name_arg is not None else func.__name__  # type: ignore

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_message_formatted, end_message_formatted = format_start_end_messages(
                func, args, kwargs, start_message, end_message)
            with Operation(opname, resolve_logger(*args, **kwargs), start_message_formatted, end_message_formatted, log_level):
                return func(*args, **kwargs)

        @wraps(func)
        async def coro_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_message_formatted, end_message_formatted = format_start_end_messages(
                func, args, kwargs, start_message, end_message)
            with Operation(opname, resolve_logger(*args, **kwargs), start_message_formatted, end_message_formatted, log_level):
                return await func(*args, **kwargs)

        if iscoroutinefunction(func):
            return cast(_T, coro_wrapper)
        else:
            return cast(_T, wrapper)

    if type(name) is FunctionType:
        return decorator(name)
    else:
        return decorator
