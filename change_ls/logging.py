from contextvars import ContextVar
from logging import INFO, Logger, LoggerAdapter, getLogger
from types import TracebackType
from typing import (TYPE_CHECKING, Any, Callable, Generic, List,
                    MutableMapping, Optional, Tuple, Type, TypeAlias, TypeVar,
                    Union, cast)
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


# Why do you have to be like this, TypeShed?
if TYPE_CHECKING:
    _L_tmp: TypeAlias = "_L"
    _LoggerAdapter = LoggerAdapter[_L_tmp]
else:
    _LoggerAdapter = LoggerAdapter
_L = TypeVar("_L", Logger, _LoggerAdapter)


class OperationLoggerAdapter(LoggerAdapter[_L], Generic[_L]):
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

    def __init__(self, logger: _L) -> None:
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


def _resolve_logger(logger: Optional[Union[str, Logger, OperationLoggerAdapter[Any]]]) -> Optional[OperationLoggerAdapter[Logger]]:
    if logger is None:
        return None
    elif isinstance(logger, Logger):
        return OperationLoggerAdapter(logger)
    elif isinstance(logger, OperationLoggerAdapter):
        return logger
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
    _logger: Optional[OperationLoggerAdapter[Any]]
    _log_level: int
    _info: Optional[OperationInfo]

    def __init__(self, name: str, logger: Optional[Union[str, Logger, OperationLoggerAdapter[Any]]] = None, start_message: Optional[str] = None, end_message: Optional[str] = None, log_level: int = INFO) -> None:
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


T = TypeVar("T")


def operation(name: Optional[str] = None,
              logger_name: Optional[str] = None,
              start_message: Optional[str] = None,
              end_message: Optional[str] = None,
              log_level: int = INFO) -> Callable[[T], T]:
    """
    Decorator to turn a function into an :class:`Operation`::

        @operation
        def foo():
            ...

    :param name: The name of the ``Operation``. If this is ``None``, the name of the function
        is used as the ``Operation's`` name.
    :param logger_name: The name of the :class:`logging.Logger` that should log the start and end message.
        This paramter is optional, but must be present if a start or end message is given.
    :param start_message: Message that should be logged when the ``Operation`` is started.
    :param end_message: Message that should be logged when the ``Operation`` is finished.
    :param log_level: Log level with which the start and end messages should be logged.
    """
    if logger_name is not None:
        logger = getLogger(logger_name)
    else:
        logger = None

    def decorator(func: T) -> T:
        nonlocal name
        assert isinstance(func, Callable)
        opname = name if name is not None else func.__name__

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with Operation(opname, logger, start_message, end_message, log_level):
                return func(*args, **kwargs)

        return cast(T, wrapper)
    return decorator
