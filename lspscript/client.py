import subprocess
from abc import ABC, abstractmethod
from asyncio import (AbstractEventLoop, BaseTransport, get_running_loop,
                     wait_for)
from logging import Logger, getLogger
from os import getpid
from pathlib import Path
from socket import AF_INET
from sys import argv
from types import TracebackType
from typing import (Any, Callable, Dict, List, Literal, Mapping, Optional,
                    Sequence, Set, Tuple, Type, Union)

from lspscript.capabilities_mixin import CapabilitiesMixin
from lspscript.protocol import (LSPClientException, LSProtocol,
                                LSStreamingProtocol, LSSubprocessProtocol)
from lspscript.types import (ClientCapabilities, InitializedParams,
                             InitializeParams, InitializeResult)
from lspscript.types.client_requests import (ClientRequestsMixin,
                                             ServerRequestsMixin)
from lspscript.types.enumerations import (FailureHandlingKind, MessageType,
                                          PositionEncodingKind,
                                          ResourceOperationKind, SymbolKind,
                                          SymbolTag)
from lspscript.types.structures import (ApplyWorkspaceEditParams,
                                        ApplyWorkspaceEditResult, CancelParams,
                                        ConfigurationParams,
                                        DeclarationClientCapabilities,
                                        DefinitionClientCapabilities,
                                        DocumentSymbolClientCapabilities,
                                        FileOperationClientCapabilities,
                                        GeneralClientCapabilities,
                                        ImplementationClientCapabilities,
                                        LogMessageParams, LogTraceParams,
                                        LSPAny, MessageActionItem,
                                        ProgressParams,
                                        PublishDiagnosticsParams,
                                        ReferenceClientCapabilities,
                                        RegistrationParams, ShowDocumentParams,
                                        ShowDocumentResult, ShowMessageParams,
                                        ShowMessageRequestParams,
                                        TextDocumentClientCapabilities,
                                        TypeDefinitionClientCapabilities,
                                        UnregistrationParams,
                                        WorkDoneProgressCreateParams,
                                        WorkspaceClientCapabilities,
                                        WorkspaceEditClientCapabilities,
                                        WorkspaceFolder,
                                        WorkspaceSymbolClientCapabilities)
from lspscript.types.util import JSON_VALUE

LSPSCRIPT_VERSION = "0.1.0"


# Global list of client names, currently only used for logging purposes.
_client_names: Set[str] = set()
_anonymous_client_counter: int = 0


_RequestHandler = Callable[[str, Union[Sequence[JSON_VALUE], Mapping[str, JSON_VALUE], None]], JSON_VALUE]
_NotificationHandler = Callable[[str, Union[Sequence[JSON_VALUE], Mapping[str, JSON_VALUE], None]], None]


class ServerLaunchParams(ABC):
    """
    Abstract base class for parameters to launch a language server.

    The following concrete subclasses are available, each establishing the communication in a different way:

    * :class:`StdIOConnectionParams`: Communicate with the language server over standard input/output streams.

    * :class:`SocketConnectionParams`: Communicate over TCP sockets.

    * :class:`PipeConnectionParams`: Communicate over named pipes.
    """

    server_path: Optional[Path]
    launch_command: Optional[str]
    additional_args: Sequence[str]
    additional_only: bool

    def __init__(self, *,
                 server_path: Optional[Path] = None,
                 launch_command: Optional[str] = None,
                 additional_args: Sequence[str] = [],
                 additional_only: bool = False) -> None:
        self.server_path = server_path
        self.launch_command = launch_command
        self.additional_args = additional_args
        self.additional_only = additional_only

    @abstractmethod
    async def _launch_server_from_event_loop(self, request_handler: _RequestHandler, notification_handler: _NotificationHandler, logger: Logger) -> Tuple[BaseTransport, LSProtocol]:
        pass


class StdIOConnectionParams(ServerLaunchParams):
    """
    Launch parameters which launch a language server with stdio communication.

    The :class:`Client` will send messages to the server's stdin and receive
    responses on the server's stdout.

    Either ``server_path`` or ``launch_command`` must be set.

    :param server_path: Path to the server binary.
    :param launch_command: Shell command to launch the language server. If this is given, only this command
        is run, without any additional arguments. Therefore, the ``launch_command`` needs to make sure that
        the server is started with stdio communication, e.g. by passing ``--stdio`` for some node.js-based servers.
    :param additional_args: List of additional commandline arguments passed to the server.
    :param additional_only: Only add the arguments inside ``additional_args``, do not add any default arguments.
        By default, ``StdIOConnectionParams`` adds ``--stdio`` and ``cliendProcessId=<pid>``, as recommended by
        the LSP spec.
    """

    def __init__(self, *,
                 server_path: Optional[Path] = None,
                 launch_command: Optional[str] = None,
                 additional_args: Sequence[str] = [],
                 additional_only: bool = False) -> None:
        if not server_path and not launch_command:
            raise ValueError(
                "Either server_path or launch_command need to be set.")

        super().__init__(server_path=server_path, additional_args=additional_args,
                         launch_command=launch_command, additional_only=additional_only)

    async def _launch_server_from_event_loop(self, request_handler: _RequestHandler, notification_handler: _NotificationHandler, logger: Logger) -> Tuple[BaseTransport, LSProtocol]:
        args = ["--stdio", f"--clientProcessId={getpid()}"]
        if self.additional_only:
            args = self.additional_args
        else:
            args += self.additional_args
        loop = get_running_loop()
        if self.server_path:
            logger.info("Launching server %s, connection over stdio, with arguments %s",
                        self.server_path, ", ".join(args))
            return await loop.subprocess_exec(lambda: LSSubprocessProtocol(request_handler, notification_handler, logger), self.server_path, *args)
        elif self.launch_command:
            logger.info(
                "launching server, connection over stdio, using '%s'", self.launch_command)
            return await loop.subprocess_shell(lambda: LSSubprocessProtocol(request_handler, notification_handler, logger), self.launch_command)
        else:
            assert False


class SocketConnectionParams(ServerLaunchParams):
    """Launch parameters which launch a language server with tcp socket communication."""

    hostname: str
    port: int

    def __init__(self, *,
                 server_path: Optional[Path] = None,
                 launch_command: Optional[str] = None,
                 port: int,
                 hostname: str = "localhost",
                 additional_args: Sequence[str] = [],
                 additional_only: bool = False) -> None:
        """Constructs a new SocketConnectionParams instance. This instance can then
        be used to launch a new client/server connection.

        If neither `server_path` nor `launch_command` are set, no server is launched. Instead,
        the Client tries to connect to an already running server.

        Parameters:
        - `server_path`: The path were the language server executable is located.
        - `launch_command`: Shell command to start the server. If a launch command is given,
          no additional arguments are appended. This means that the caller may also need
          to add `--socket=<port>` to the command to select a connection via TCP-sockets.
        - `port`: The port number to use for the TCP connection.
        - `hostname`: An optional name of a host to connect to. The default is 'localhost'.
        - `additional_args`: List of additional arguments to pass to the server.
        - `additional_only`: Do not send any standard arguments, only those in `additional_args`."""

        super().__init__(server_path=server_path, launch_command=launch_command,
                         additional_args=additional_args, additional_only=additional_only)
        self.hostname = hostname
        self.port = port

    async def _launch_server_from_event_loop(self, request_handler: _RequestHandler, notification_handler: _NotificationHandler, logger: Logger) -> Tuple[BaseTransport, LSProtocol]:
        args = [f"--socket={self.port}", f"--clientProcessId={getpid()}"]
        if self.additional_only:
            args = self.additional_args
        else:
            args += self.additional_args

        if self.server_path:
            logger.info("Launching server %s, connection over TCP sockets, with arguments %s",
                        self.server_path, ", ".join(args))
            subprocess.Popen([self.server_path.absolute()] + list(args))
        elif self.launch_command:
            logger.info(
                "launching server, connection over TCP sockets, using '%s'", self.launch_command)
            subprocess.Popen(self.launch_command, shell=True)

        loop = get_running_loop()
        logger.info("Connecting to running server at %s:%d",
                    self.hostname, self.port)
        return await loop.create_connection(lambda: LSStreamingProtocol(request_handler, notification_handler, logger), host=self.hostname, port=self.port, family=AF_INET)


class PipeConnectionParams(ServerLaunchParams):
    # Unix:
    #   event_loop.create_unix_connection(...)
    # Win:
    #   fd = create named pipe
    #   event_loop.subprocess_exec(stdin=fd, stdout=fd, ...)
    pipename: str


class WorkspaceRequestHandler(ABC):

    @abstractmethod
    def on_workspace_folders(self) -> List[WorkspaceFolder]:
        return NotImplemented

    @abstractmethod
    def on_configuration(self, params: ConfigurationParams) -> List[LSPAny]:
        return NotImplemented

    @abstractmethod
    def on_semantic_tokens_refresh(self) -> None:
        pass

    @abstractmethod
    def on_inline_value_refresh(self) -> None:
        pass

    @abstractmethod
    def on_inlay_hint_refresh(self) -> None:
        pass

    @abstractmethod
    def on_diagnostic_refresh(self) -> None:
        pass

    @abstractmethod
    def on_code_lens_refresh(self) -> None:
        pass

    @abstractmethod
    def on_apply_edit(self, params: ApplyWorkspaceEditParams) -> ApplyWorkspaceEditResult:
        return NotImplemented

    @abstractmethod
    def on_publish_diagnostics(self, params: PublishDiagnosticsParams) -> None:
        pass


def get_default_client_capabilities() -> ClientCapabilities:
    """
    Returns the :class:`ClientCapabilities` which are used for the default
    :class:`InitializeParams` (see `get_default_initialize_params`).
    """
    all_symbols_kinds = [
        SymbolKind.Array, SymbolKind.Boolean, SymbolKind.Class, SymbolKind.Constant,
        SymbolKind.Constructor, SymbolKind.Enum, SymbolKind.EnumMember, SymbolKind.Event,
        SymbolKind.Field, SymbolKind.File, SymbolKind.Function, SymbolKind.Interface,
        SymbolKind.Key, SymbolKind.Method, SymbolKind.Module, SymbolKind.Namespace,
        SymbolKind.Null, SymbolKind.Number, SymbolKind.Object, SymbolKind.Operator,
        SymbolKind.Package, SymbolKind.Property, SymbolKind.String, SymbolKind.Struct,
        SymbolKind.TypeParameter, SymbolKind.Variable]
    all_symbol_tags = [SymbolTag.Deprecated]

    return ClientCapabilities(
        general=GeneralClientCapabilities(
            positionEncodings=[PositionEncodingKind.UTF32, PositionEncodingKind.UTF8, PositionEncodingKind.UTF16]),
        workspace=WorkspaceClientCapabilities(
            workspaceEdit=WorkspaceEditClientCapabilities(
                documentChanges=True,
                resourceOperations=[ResourceOperationKind.Create,
                                    ResourceOperationKind.Rename,
                                    ResourceOperationKind.Delete],
                failureHandling=FailureHandlingKind.Abort),
            fileOperations=FileOperationClientCapabilities(
                willCreate=True, didCreate=True,
                willRename=True, didRename=True,
                willDelete=True, didDelete=True),
            symbol=WorkspaceSymbolClientCapabilities(
                symbolKind={"valueSet": all_symbols_kinds},
                tagSupport={"valueSet": all_symbol_tags},
                resolveSupport={"properties": ["location.range", "containerName", "tags"]})),
        textDocument=TextDocumentClientCapabilities(
            references=ReferenceClientCapabilities(),
            declaration=DeclarationClientCapabilities(linkSupport=True),
            definition=DefinitionClientCapabilities(linkSupport=True),
            typeDefinition=TypeDefinitionClientCapabilities(linkSupport=True),
            implementation=ImplementationClientCapabilities(linkSupport=True),
            documentSymbol=DocumentSymbolClientCapabilities(
                symbolKind={"valueSet": all_symbols_kinds},
                tagSupport={"valueSet": all_symbol_tags},
                hierarchicalDocumentSymbolSupport=True)))


def get_default_initialize_params() -> InitializeParams:
    """
    Returns the :class:`InitializeParams` which will be used when a :class:`Client` is
    constructed without explicit ``InitializeParams``.
    """
    return InitializeParams(
        processId=getpid(),
        clientInfo={
            "name": "[LSPScript]: " + argv[0],
            "version": LSPSCRIPT_VERSION
        },
        rootUri=None,
        capabilities=get_default_client_capabilities())


def _generate_client_name(launch_params: ServerLaunchParams) -> str:
    global _anonymous_client_counter
    if launch_params.server_path:
        basename = launch_params.server_path.stem
        suffix = ""
        index = 0
        while basename + suffix in _client_names:
            index += 1
            suffix = "-" + str(index)
        return basename + suffix
    else:
        name = str(_anonymous_client_counter)
        _anonymous_client_counter += 1
        return name


ClientState = Literal["disconnected", "uninitialized",
                      "initializing", "running", "shutdown"]


class Client(ClientRequestsMixin, ServerRequestsMixin, CapabilitiesMixin):
    """
    A Client manages the low-level communication with a language server using the Language Server Protocol.

    To obtain an instance of a ``Client``, call :meth:`~Workspace.launch_client()` on a :class:`Workspace` instance
    with appropriate :class:`ServerLaunchParams`. This will create a ``Client`` associated with the ``Workspace``,
    which will be connected to a language server and shut down when the ``Workspace`` is closed. The ``Client``
    itself is also a context manager, so it can closed independently of the ``Workspace``.

    The ``Client`` class provides methods for each request in the
    `LSP <https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/>`_
    that is sent from the client to the server. The types used in the parameters to these requests are
    available under ``lspscript.types``. However, users may find it easier to use the abstractions
    provided by :class:`Workspace`, :class:`TextDocument`, etc. The ``send_*`` methods which send a request
    (i.e. expect a response from the server) also provide the following keyword arguments:

    * ``timeout``: A timeout in seconds after which the request is considered to have failed. A value of ``None``
        indicates an infinite timeout. The default timeout is 10 seconds.

    Depending on which features the language server advertises in its :class:`InitializeResult`, a
    subset of the requests/notification of the LSP are available. To check whether a language server
    supports a particular request, the :meth:`check_feature()` method can be used.

    It is also possible to go through the launch and shutdown processes for the language server manually.
    To do this, first obtain a ``Client`` without automatically starting the language server by calling
    :meth:`Workspace.create_client`. Then perform the following operation:

    * ``"disconnected"``: No server process is running. When a server process is launched with :meth:`launch()`,
        the server enters the ``"uninitialized"`` state.

    * ``"uninitialized"``: The server is running, but no *initialize* request has been sent with :meth:`send_initialize()`.
        After the *initialize* request has been sent, the ``Client`` enters the ``"initializing"`` state.

    * ``"initializing"``: The ``Client`` has received the result of the *initialize* request, but has not yet sent the
        *initialized* notification (with :meth:`send_initialized()`). Doing so will put the ``Client`` in the ``"running"`` state.

    * ``"running"``: The server is running and ready to receive requests. Calling :meth:`send_shutdown()` to send
        a *shutdown* request will put the ``Client`` in the ``"shutdown"`` state.

    * ``"shutdown"``: The server is shutting down. Sending an *exit* notification using :meth:`send_exit()`
        will cause the ``Client`` to enter the ``"disconnected"`` state.

    The context manager functions are state-agnostic, so the ``Client`` will always be in the ``"running"`` state
    inside a ``with`` statement and always in the ``"disconnected"`` state after the ``with`` statement is exited.
    To facilitate this, the language server process may be relaunched.
    """

    _state: ClientState
    _protocol: Optional[LSProtocol]
    _launch_params: ServerLaunchParams
    _name: str
    _logger: Logger

    # Whether or not an 'exit' notification was sent. This is used
    # to distinguish a normal termination of the server from a crash.
    _exit_sent: bool

    _initialize_params: InitializeParams
    _workspace_request_handler: Optional[WorkspaceRequestHandler]
    _state_callbacks: Dict[ClientState, List[Callable[[], None]]]

    def __init__(self, launch_params: ServerLaunchParams, initialize_params: InitializeParams = get_default_initialize_params(), name: Optional[str] = None) -> None:
        super().__init__()

        self._state = "disconnected"
        self._protocol = None
        self._launch_params = launch_params
        self._exit_sent = False
        self._initialize_params = initialize_params

        if name is None:
            name = _generate_client_name(launch_params)
        self._name = name
        _client_names.add(name)
        self._logger = getLogger("lspscript.client." + name)
        self._state_callbacks = {
            "disconnected": [],
            "uninitialized": [],
            "initializing": [],
            "running": [],
            "shutdown": [],
        }

    def set_workspace_request_handler(self, handler: Optional[WorkspaceRequestHandler]) -> None:
        self._workspace_request_handler = handler

    def _client_thread_exception_handler(self, _loop: AbstractEventLoop, context: Dict[str, Any]) -> None:
        exception = context.get("exception")
        if exception is None:
            exception = LSPClientException(context["message"])
        self._logger.exception(exception)

        if self._protocol:
            self._protocol.reject_active_requests(exception)

    def _set_state(self, state: ClientState) -> None:
        self._state = state
        for callback in self._state_callbacks[state]:
            callback()

    def get_state(self) -> ClientState:
        """
        Returns the current state of the ``Client``.
        """
        return self._state

    def register_state_callback(self, state: ClientState, callback: Callable[[], None]) -> None:
        """
        Registers a callback to run when the ``Client`` enters a given state.

        :param state: The state at which the callback should be called.
        :param callback: The callback. This should be a function receiving no arguments and
            return no value.
        """
        self._state_callbacks[state].append(callback)

    def get_name(self) -> str:
        return self._name

    async def launch(self) -> None:
        """
        Launches the Language Server process.

        The next step in the launch process is to call :meth:`send_initialize()`.
        """
        self._exit_sent = False

        get_running_loop().set_exception_handler(self._client_thread_exception_handler)
        (_, self._protocol) = await self._launch_params._launch_server_from_event_loop(self.dispatch_request, self.dispatch_notification, self._logger)  # type: ignore
        self._set_state("uninitialized")
        self._logger.info("Client is now uninitialized")

    async def _send_request_internal(self, method: str, params: JSON_VALUE, timeout: Optional[float] = 10.0) -> JSON_VALUE:
        assert self._protocol

        future = get_running_loop().create_future()
        self._logger.info("Sending request (%s)", method)
        self._protocol.send_request(method, params, future)
        await wait_for(future, timeout)

        assert not future.cancelled()
        if exception := future.exception():
            self._logger.info("Request failed (%s)", method)
            raise exception
        else:
            return future.result()

    async def send_request(self, method: str, params: JSON_VALUE, **kwargs: Any) -> JSON_VALUE:
        """
        Sends a request to the server and returns the result.
        The method and contents of the request are arbitrary and need not be defined in the LSP.

        :param timeout: Number of seconds after which the request must be resolved. A value of
            ``None`` indicates an infinite timeout. If the request is not resolved before the given
            timeout, an ``asyncio.exceptions.TimeoutError`` is raised (not to be confused with ``TimeoutError(OSError)``).
        """
        if self._state != "running":
            raise LSPClientException("Invalid state, expected 'running'.")
        return await self._send_request_internal(method, params, **kwargs)

    async def send_request_iter(self, method: str, params: JSON_VALUE) -> JSON_VALUE:
        # Version of send_request which returns an async iterator.
        # This method is used when partial results are requested.
        pass

    def _send_notification_internal(self, method: str, params: JSON_VALUE) -> None:
        assert self._protocol
        self._logger.info("Sending notification (%s)", method)
        self._protocol.send_notification(method, params)

    def send_notification(self, method: str, params: JSON_VALUE) -> None:
        """
        Sends a notification to the server. The method and contents of the notification are arbitrary
        and need not be defined in the LSP.
        """
        if self._state != "running":
            raise LSPClientException("Invalid state, expected 'running'.")
        self._send_notification_internal(method, params)

    async def send_initialize(self, params: Optional[InitializeParams] = None, **kwargs: Any) -> InitializeResult:
        if self._state != "uninitialized":
            raise LSPClientException(
                "Invalid state, expected 'uninitialized'.")

        if not params:
            params = self._initialize_params

        # We need to call _send_request_internal directly here, since the
        # normal send_request method requires the state to be "running".
        out_json = await self._send_request_internal("initialize", params.to_json(), **kwargs)
        assert isinstance(out_json, Mapping)
        out = InitializeResult.from_json(out_json)
        self._set_server_capabilities(out.capabilities)

        self._set_state("initializing")
        self._logger.info("Client is now initializing")
        return out

    async def send_initialized(self, params: InitializedParams) -> None:
        if self._state != "initializing":
            raise LSPClientException("Invalid state, expected 'initializing'.")

        self._send_notification_internal("initialized", params.to_json())
        self._set_state("running")
        self._logger.info("Client is now running")

    async def send_shutdown(self, **kwargs: Any) -> None:
        await super().send_shutdown(**kwargs)
        self._set_state("shutdown")
        self._logger.info("Client is now shutting down")

    async def send_exit(self) -> None:
        if self._state != "shutdown":
            raise LSPClientException("Invalid state, expected 'shutdown'.")

        self._send_notification_internal("exit", None)

        try:
            assert self._protocol
            await wait_for(self._protocol.wait_for_disconnect(), 10.0)
            self._set_state("disconnected")
        except:
            raise LSPClientException("Unable to stop server thread.")

    async def __aenter__(self) -> "Client":
        # These 'if's are here so that the method can be called from any state.

        if self._state == "shutdown":
            await self.send_exit()
        if self._state == "disconnected":
            await self.launch()
        if self._state == "uninitialized":
            # TODO store result
            await self.send_initialize()
        if self._state == "initializing":
            await self.send_initialized(InitializedParams())

        assert self._state == "running"
        return self

    async def __aexit__(self, exc_type: Type[Exception], exc_value: Exception, traceback: TracebackType) -> bool:
        if self._state in ["uninitialized", "initializing", "running"]:
            await self.send_shutdown()
        if self._state == "shutdown":
            await self.send_exit()
        assert self._state == "disconnected"
        return False

    def get_position_encoding_kind(self) -> PositionEncodingKind:
        """
        Returns the :class:`PositionEncodingKind` used by the language server.
        """

        if self._state not in ["initializing", "running"]:
            raise LSPClientException("Invalid state, expected 'initializing' or 'running'.")
        assert self._server_capabilities
        out = self._server_capabilities.positionEncoding
        if not out:
            return PositionEncodingKind.UTF16
        else:
            return out

    # -----------------------------
    # Callbacks for server requests
    # -----------------------------

    def on_workspace_workspace_folders(self) -> Union[List[WorkspaceFolder], None]:
        if self._workspace_request_handler:
            return self._workspace_request_handler.on_workspace_folders()
        else:
            return None

    def on_workspace_configuration(self, params: ConfigurationParams) -> List[LSPAny]:
        if self._workspace_request_handler:
            return self._workspace_request_handler.on_configuration(ConfigurationParams(items=params.items))
        else:
            return []

    def on_workspace_semantic_tokens_refresh(self) -> None:
        if self._workspace_request_handler:
            self._workspace_request_handler.on_semantic_tokens_refresh()

    def on_workspace_inline_value_refresh(self) -> None:
        if self._workspace_request_handler:
            self._workspace_request_handler.on_inline_value_refresh()

    def on_workspace_inlay_hint_refresh(self) -> None:
        if self._workspace_request_handler:
            self._workspace_request_handler.on_inlay_hint_refresh()

    def on_workspace_diagnostic_refresh(self) -> None:
        if self._workspace_request_handler:
            self._workspace_request_handler.on_diagnostic_refresh()

    def on_workspace_code_lens_refresh(self) -> None:
        if self._workspace_request_handler:
            self._workspace_request_handler.on_code_lens_refresh()

    def on_workspace_apply_edit(self, params: ApplyWorkspaceEditParams) -> ApplyWorkspaceEditResult:
        if self._workspace_request_handler:
            return self._workspace_request_handler.on_apply_edit(params)
        else:
            return ApplyWorkspaceEditResult(applied=False, failureReason="Client is not registered with a Workspace.")

    def on_text_document_publish_diagnostics(self, params: PublishDiagnosticsParams) -> None:
        if self._workspace_request_handler:
            self._workspace_request_handler.on_publish_diagnostics(params)

    def on_client_register_capability(self, params: RegistrationParams) -> None:
        for r in params.registrations:
            self._add_dynamic_registration(r)
        self._check_pending_feature_requests()

    def on_client_unregister_capability(self, params: UnregistrationParams) -> None:
        for r in params.unregisterations:
            self._remove_dynamic_registration(r)

    def on_window_work_done_progress_create(self, params: WorkDoneProgressCreateParams) -> None:
        pass

    def on_window_show_document(self, params: ShowDocumentParams) -> ShowDocumentResult:
        return NotImplemented

    def on_window_show_message_request(self, params: ShowMessageRequestParams) -> Union[MessageActionItem, None]:
        return NotImplemented

    def on_window_show_message(self, params: ShowMessageParams) -> None:
        logger = self._logger.getChild("server")
        if params.type is MessageType.Log:
            logger.debug("window/showMessage: %s", params.message)
        elif params.type is MessageType.Info:
            logger.info("window/showMessage: %s", params.message)
        elif params.type is MessageType.Warning:
            logger.warning("window/showMessage: %s", params.message)
        elif params.type is MessageType.Error:
            logger.error("window/showMessage: %s", params.message)

    def on_window_log_message(self, params: LogMessageParams) -> None:
        logger = self._logger.getChild("server")
        if params.type is MessageType.Log:
            logger.debug("window/logMessage: %s", params.message)
        elif params.type is MessageType.Info:
            logger.info("window/logMessage: %s", params.message)
        elif params.type is MessageType.Warning:
            logger.warning("window/logMessage: %s", params.message)
        elif params.type is MessageType.Error:
            logger.error("window/logMessage: %s", params.message)

    def on_telemetry_event(self, params: LSPAny) -> None:
        pass

    def on_s_log_trace(self, params: LogTraceParams) -> None:
        logger = self._logger.getChild("server")
        logger.debug("$/logTrace: %s", params.message)

    def on_s_cancel_request(self, params: CancelParams) -> None:
        pass

    def on_s_progress(self, params: ProgressParams) -> None:
        pass
