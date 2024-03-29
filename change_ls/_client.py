import asyncio
import os
import subprocess
import sys
import uuid
from abc import ABC, abstractmethod
from asyncio import AbstractEventLoop, get_running_loop, wait_for
from dataclasses import dataclass
from os import getpid
from pathlib import Path
from socket import AF_INET
from sys import argv
from types import TracebackType
from typing import Any, Callable, Dict, List, Literal, Mapping, Optional, Sequence, Type, Union

from change_ls._capabilities_mixin import CapabilitiesMixin
from change_ls._protocol import (
    LSPClientException,
    LSProtocol,
    LSStreamingProtocol,
    LSSubprocessProtocol,
)
from change_ls.logging import get_change_ls_default_logger  # type: ignore
from change_ls.logging import OperationLoggerAdapter, operation
from change_ls.types import (
    JSON_VALUE,
    ApplyWorkspaceEditParams,
    ApplyWorkspaceEditResult,
    CancelParams,
    ClientCapabilities,
    ConfigurationParams,
    DeclarationClientCapabilities,
    DefinitionClientCapabilities,
    DocumentSymbolClientCapabilities,
    FailureHandlingKind,
    FileOperationClientCapabilities,
    GeneralClientCapabilities,
    ImplementationClientCapabilities,
    InitializedParams,
    InitializeParams,
    InitializeResult,
    LogMessageParams,
    LogTraceParams,
    LSPAny,
    MessageActionItem,
    MessageType,
    PositionEncodingKind,
    ProgressParams,
    PublishDiagnosticsParams,
    ReferenceClientCapabilities,
    RegistrationParams,
    ResourceOperationKind,
    SemanticTokensClientCapabilities,
    ShowDocumentParams,
    ShowDocumentResult,
    ShowMessageParams,
    ShowMessageRequestParams,
    SymbolKind,
    SymbolTag,
    TextDocumentClientCapabilities,
    TokenFormat,
    TypeDefinitionClientCapabilities,
    UnregistrationParams,
    WorkDoneProgressCreateParams,
    WorkspaceClientCapabilities,
    WorkspaceEditClientCapabilities,
    WorkspaceFolder,
    WorkspaceSymbolClientCapabilities,
)
from change_ls.types._client_requests import ClientRequestsMixin, ServerRequestsMixin

if sys.platform == "win32":
    from asyncio import ProactorEventLoop

CHANGE_LS_VERSION = "0.1.0"


class ServerLaunchParams(ABC):
    """
    Abstract base class for parameters to launch a language server.

    The following concrete subclasses are available, each establishing the communication in a different way:

    * :class:`StdIOConnectionParams`: Communicate with the language server over standard input/output streams.

    * :class:`SocketConnectionParams`: Communicate over TCP sockets.

    * :class:`PipeConnectionParams`: Communicate over named pipes.
    """

    server_path: Optional[Path]
    args: Sequence[str]
    launch_command: Optional[str]
    cwd: Optional[Path]

    def __init__(
        self,
        *,
        server_path: Optional[Path] = None,
        args: Optional[Sequence[str]] = None,
        launch_command: Optional[str] = None,
        cwd: Optional[Path] = None,
    ) -> None:
        self.server_path = server_path
        self.args = args or []
        self.launch_command = launch_command
        self.cwd = cwd

    def _start_server_process(self, client: "Client") -> None:
        if self.server_path:
            client.logger.info(
                "Launching language server %s with arguments %s.", self.server_path, str(self.args)
            )
            subprocess.Popen([self.server_path.absolute()] + list(self.args), cwd=self.cwd)
        elif self.launch_command:
            client.logger.info("Launching language server using '%s'.", self.launch_command)
            subprocess.Popen(self.launch_command, shell=True, cwd=self.cwd)

    @abstractmethod
    async def _launch_server_from_event_loop(self, client: "Client") -> LSProtocol:
        ...


class StdIOConnectionParams(ServerLaunchParams):
    """
    Launch parameters which launch a language server with stdio communication.

    The :class:`Client` will send messages to the server's stdin and receive
    responses on the server's stdout.

    Either ``server_path`` or ``launch_command`` must be set.

    :param server_path: Path to the server binary.
    :param args: List of arguments passed to the server.
    :param launch_command: Shell command to launch the language server.
    :param cwd: Working directory for the language server process. Defaults to the current directory.
    """

    def __init__(
        self,
        *,
        server_path: Optional[Path] = None,
        args: Optional[Sequence[str]] = None,
        launch_command: Optional[str] = None,
        cwd: Optional[Path] = None,
    ) -> None:
        if not server_path and not launch_command:
            raise ValueError("Either server_path or launch_command need to be set.")

        super().__init__(server_path=server_path, args=args, launch_command=launch_command, cwd=cwd)

    async def _launch_server_from_event_loop(self, client: "Client") -> LSProtocol:
        client.logger.info("Using stdio connection.")
        loop = get_running_loop()
        if self.server_path:
            client.logger.info(
                "Launching language server %s with arguments %s.", self.server_path, str(self.args)
            )
            _, protocol = await loop.subprocess_exec(
                lambda: LSSubprocessProtocol(client.dispatch_request, client.dispatch_notification),
                self.server_path,
                *self.args,
                cwd=self.cwd,
            )
            return protocol
        elif self.launch_command:
            client.logger.info("Launching language server using '%s'.", self.launch_command)
            _, protocol = await loop.subprocess_shell(
                lambda: LSSubprocessProtocol(client.dispatch_request, client.dispatch_notification),
                self.launch_command,
                cwd=self.cwd,
            )
            return protocol
        else:
            assert False


class SocketConnectionParams(ServerLaunchParams):
    """Launch parameters which launch a language server with tcp socket communication."""

    port: int

    def __init__(
        self,
        *,
        server_path: Optional[Path] = None,
        args: Optional[Sequence[str]] = None,
        launch_command: Optional[str] = None,
        cwd: Optional[Path] = None,
        port: int,
    ) -> None:
        """
        Constructs a new SocketConnectionParams instance. This instance can then
        be used to launch a new client/server connection.

        :param server_path: The path were the language server executable is located.
        :param args: List of arguments to pass to the server.
        :param launch_command: Shell command to start the server.
        :param cwd: Working directory of the server process. Defaults to the current directory.
        :param port: The port number to use for the TCP connection.
        """

        super().__init__(server_path=server_path, launch_command=launch_command, args=args, cwd=cwd)
        self.port = port

    async def _launch_server_from_event_loop(self, client: "Client") -> LSProtocol:
        client.logger.info("Using TCP socket connection.")

        loop = get_running_loop()
        protocol = LSStreamingProtocol(client.dispatch_request, client.dispatch_notification)
        server = await loop.create_server(
            lambda: protocol, host="127.0.0.1", port=self.port, family=AF_INET
        )

        protocol.set_server(server)
        self._start_server_process(client)
        await protocol.wait_for_connection()
        return protocol


class PipeConnectionParams(ServerLaunchParams):
    """Launch parametes which launch a language server using either named pipes (windows) or UNIX Domain Sockets (UNIX)."""

    pipe_name: str

    def __init__(
        self,
        *,
        server_path: Optional[Path] = None,
        args: Optional[Sequence[str]] = None,
        launch_command: Optional[str] = None,
        cwd: Optional[Path] = None,
        pipe_name: str,
    ) -> None:
        r"""
        Constructs a new PipeConnectionParams instance. This instance can then
        be used to launch a new client/server connection.

        :param server_path: The path were the language server executable is located.
        :param args: List of arguments to pass to the server.
        :param launch_command: Shell command to start the server.
        :param cwd: Working directory of the server process. Defaults to the current directory.
        :param pipe_name: The name of the pipe/socket file that should be used. On windows, this must
            be a path in the namespace '\\.\pipe\'.
        """
        super().__init__(server_path=server_path, args=args, launch_command=launch_command, cwd=cwd)
        self.pipe_name = pipe_name

    async def _launch_server_from_event_loop(self, client: "Client") -> LSProtocol:
        if sys.platform == "win32":
            client.logger.info(f"Using named pipe connection with pipe '{self.pipe_name}'.")
            loop = get_running_loop()
            if not isinstance(loop, ProactorEventLoop):
                raise LSPClientException("Pipe connections on Windows require a ProactorEventLoop")

            # typeshed expects this to be a StreamReaderProtocol, but that does not make sense.
            protocol = LSStreamingProtocol(client.dispatch_request, client.dispatch_notification)
            [server] = await loop.start_serving_pipe(
                lambda: protocol, self.pipe_name  # type: ignore
            )
            # Hold on to the PipeServer to prevent the named pipe from being closed.
            protocol.set_server(server)

            self._start_server_process(client)
            await protocol.wait_for_connection()
            return protocol
        elif os.name == "posix":
            client.logger.info(f"Using UNIX Domain Socket connection with name '{self.pipe_name}'")

            loop = get_running_loop()
            protocol = LSStreamingProtocol(client.dispatch_request, client.dispatch_notification)
            server = await loop.create_unix_server(lambda: protocol, self.pipe_name)
            protocol.set_server(server)

            self._start_server_process(client)
            await protocol.wait_for_connection()
            return protocol
        else:
            raise LSPClientException(
                f"PipeConnectionParams are not support on platform {sys.platform}"
            )


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
        SymbolKind.Array,
        SymbolKind.Boolean,
        SymbolKind.Class,
        SymbolKind.Constant,
        SymbolKind.Constructor,
        SymbolKind.Enum,
        SymbolKind.EnumMember,
        SymbolKind.Event,
        SymbolKind.Field,
        SymbolKind.File,
        SymbolKind.Function,
        SymbolKind.Interface,
        SymbolKind.Key,
        SymbolKind.Method,
        SymbolKind.Module,
        SymbolKind.Namespace,
        SymbolKind.Null,
        SymbolKind.Number,
        SymbolKind.Object,
        SymbolKind.Operator,
        SymbolKind.Package,
        SymbolKind.Property,
        SymbolKind.String,
        SymbolKind.Struct,
        SymbolKind.TypeParameter,
        SymbolKind.Variable,
    ]
    all_symbol_tags = [SymbolTag.Deprecated]

    return ClientCapabilities(
        general=GeneralClientCapabilities(
            positionEncodings=[
                PositionEncodingKind.UTF32,
                PositionEncodingKind.UTF8,
                PositionEncodingKind.UTF16,
            ]
        ),
        workspace=WorkspaceClientCapabilities(
            workspaceEdit=WorkspaceEditClientCapabilities(
                documentChanges=True,
                resourceOperations=[
                    ResourceOperationKind.Create,
                    ResourceOperationKind.Rename,
                    ResourceOperationKind.Delete,
                ],
                failureHandling=FailureHandlingKind.Abort,
            ),
            fileOperations=FileOperationClientCapabilities(
                willCreate=True,
                didCreate=True,
                willRename=True,
                didRename=True,
                willDelete=True,
                didDelete=True,
            ),
            symbol=WorkspaceSymbolClientCapabilities(
                symbolKind={"valueSet": all_symbols_kinds},
                tagSupport={"valueSet": all_symbol_tags},
                resolveSupport={"properties": ["location.range", "containerName", "tags"]},
            ),
        ),
        textDocument=TextDocumentClientCapabilities(
            references=ReferenceClientCapabilities(),
            declaration=DeclarationClientCapabilities(linkSupport=True),
            definition=DefinitionClientCapabilities(linkSupport=True),
            typeDefinition=TypeDefinitionClientCapabilities(linkSupport=True),
            implementation=ImplementationClientCapabilities(linkSupport=True),
            documentSymbol=DocumentSymbolClientCapabilities(
                symbolKind={"valueSet": all_symbols_kinds},
                tagSupport={"valueSet": all_symbol_tags},
                hierarchicalDocumentSymbolSupport=True,
            ),
            semanticTokens=SemanticTokensClientCapabilities(
                requests={"full": {"delta": True}},
                tokenTypes=[
                    "namespace",
                    "type",
                    "class",
                    "enum",
                    "interface",
                    "struct",
                    "typeParameter",
                    "parameter",
                    "variable",
                    "property",
                    "enumMember",
                    "event",
                    "function",
                    "method",
                    "macro",
                    "keyword",
                    "modifier",
                    "comment",
                    "string",
                    "number",
                    "regexp",
                    "operator",
                    "decorator",
                ],
                tokenModifiers=[
                    "declaration",
                    "definition",
                    "readonly",
                    "static",
                    "deprecated",
                    "abstract",
                    "async",
                    "modification",
                    "documentation",
                    "defaultLibrary",
                ],
                formats=[TokenFormat.Relative],
            ),
        ),
    )


def get_default_initialize_params() -> InitializeParams:
    """
    Returns the :class:`InitializeParams` which will be used when a :class:`Client` is
    constructed without explicit ``InitializeParams``.
    """
    return InitializeParams(
        processId=getpid(),
        clientInfo={"name": "[change_ls]: " + argv[0], "version": CHANGE_LS_VERSION},
        rootUri=None,
        capabilities=get_default_client_capabilities(),
    )


ClientState = Literal["disconnected", "uninitialized", "initializing", "running", "shutdown"]


@dataclass(frozen=True)
class ServerInfo:
    name: str
    version: str

    def __str__(self) -> str:
        return f"{self.name} version {self.version}"


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
    available under ``change_ls.types``. However, users may find it easier to use the abstractions
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
    """

    _state: ClientState
    _protocol: Optional[LSProtocol]
    _launch_params: ServerLaunchParams
    _id: uuid.UUID
    _logger_client: OperationLoggerAdapter
    _logger_server: OperationLoggerAdapter
    _logger_messages: OperationLoggerAdapter

    # Whether or not an 'exit' notification was sent. This is used
    # to distinguish a normal termination of the server from a crash.
    _exit_sent: bool

    _initialize_params: InitializeParams
    _server_info: Optional[ServerInfo]
    _workspace_request_handler: Optional[WorkspaceRequestHandler]
    _state_callbacks: Dict[ClientState, List[Callable[[], None]]]

    def __init__(
        self,
        launch_params: ServerLaunchParams,
        initialize_params: InitializeParams = get_default_initialize_params(),
    ) -> None:
        super().__init__()

        self._state = "disconnected"
        self._protocol = None
        self._launch_params = launch_params
        self._exit_sent = False
        self._id = uuid.uuid4()
        self._logger_client = get_change_ls_default_logger(
            "change-ls.client", cls_client=str(self._id), cls_server=None
        )
        self._logger_server = get_change_ls_default_logger(
            "change-ls.server", cls_client=str(self._id), cls_server=None
        )
        self._logger_messages = get_change_ls_default_logger(
            "change-ls.messages", cls_client=str(self._id), cls_server=None
        )
        self._initialize_params = initialize_params
        self._server_info = None
        self._workspace_request_handler = None
        self._state_callbacks = {
            "disconnected": [],
            "uninitialized": [],
            "initializing": [],
            "running": [],
            "shutdown": [],
        }

    def __eq__(self, other: Any) -> bool:
        return other is self

    def __hash__(self) -> int:
        return self._id.int

    @property
    def logger(self) -> OperationLoggerAdapter:
        return self._logger_client

    def _get_logger_from_context(self, *_args: Any, **_kwargs: Any) -> OperationLoggerAdapter:
        return self._logger_client

    def _set_server_info(self, server_info: Optional[ServerInfo]) -> None:
        self._server_info = server_info
        self._logger_client = get_change_ls_default_logger(
            "change-ls.client", cls_client=str(self._id), cls_server=str(server_info)
        )
        self._logger_server = get_change_ls_default_logger(
            "change-ls.server", cls_client=str(self._id), cls_server=str(server_info)
        )
        self._logger_messages = get_change_ls_default_logger(
            "change-ls.messages", cls_client=str(self._id), cls_server=str(server_info)
        )
        if self._protocol:
            self._protocol._set_loggers(self._logger_client, self._logger_server, self._logger_messages)  # type: ignore

    @property
    def server_info(self) -> Optional[ServerInfo]:
        return self._server_info

    def set_workspace_request_handler(self, handler: Optional[WorkspaceRequestHandler]) -> None:
        self._workspace_request_handler = handler

    def _client_thread_exception_handler(
        self, _loop: AbstractEventLoop, context: Dict[str, Any]
    ) -> None:
        exception = context.get("exception")
        if exception is None:
            exception = LSPClientException(context["message"])
        self._logger_client.exception(exception)

        if self._protocol:
            self._protocol.reject_active_requests(exception)

    def _set_state(self, state: ClientState) -> None:
        self._state = state
        for callback in self._state_callbacks[state]:
            callback()
        self._logger_client.info(f"Client is now in state {self._state}.")

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

    @operation(
        start_message="Launching language server.", get_logger_from_context=_get_logger_from_context
    )
    async def launch(self) -> None:
        """
        Launches the Language Server process.

        The next step in the launch process is to call :meth:`send_initialize()`.
        """
        self._exit_sent = False

        get_running_loop().set_exception_handler(self._client_thread_exception_handler)
        self._protocol = await self._launch_params._launch_server_from_event_loop(self)  # type: ignore
        self._protocol._set_loggers(self._logger_client, self._logger_server, self._logger_messages)  # type: ignore
        self._set_state("uninitialized")

    async def _send_request_internal(
        self, method: str, params: JSON_VALUE, timeout: Optional[float] = 10.0
    ) -> JSON_VALUE:
        assert self._protocol

        future = get_running_loop().create_future()
        self._protocol.send_request(method, params, future)
        await wait_for(future, timeout)

        assert not future.cancelled()
        if exception := future.exception():
            self._logger_client.info("Request failed (%s)", method)
            raise exception
        else:
            return future.result()

    @operation(
        start_message="Sending request {method}.", get_logger_from_context=_get_logger_from_context
    )
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
        self._protocol.send_notification(method, params)

    @operation(
        start_message="Sending notification {method}.",
        get_logger_from_context=_get_logger_from_context,
    )
    def send_notification(self, method: str, params: JSON_VALUE) -> None:
        """
        Sends a notification to the server. The method and contents of the notification are arbitrary
        and need not be defined in the LSP.
        """
        if self._state != "running":
            raise LSPClientException("Invalid state, expected 'running'.")
        self._send_notification_internal(method, params)

    @operation(
        start_message="Sending initialize request.",
        get_logger_from_context=_get_logger_from_context,
    )
    async def send_initialize(
        self, params: Optional[InitializeParams] = None, **kwargs: Any
    ) -> InitializeResult:
        if self._state != "uninitialized":
            raise LSPClientException("Invalid state, expected 'uninitialized'.")

        if not params:
            params = self._initialize_params

        # We need to call _send_request_internal directly here, since the
        # normal send_request method requires the state to be "running".
        out_json = await self._send_request_internal("initialize", params.to_json(), **kwargs)
        assert isinstance(out_json, Mapping)
        out = InitializeResult.from_json(out_json)
        if out.serverInfo:
            self._server_info = ServerInfo(out.serverInfo["name"], out.serverInfo["version"])

        self._set_server_capabilities(out.capabilities)

        self._set_state("initializing")
        return out

    @operation(
        start_message="Sending initialized notification.",
        get_logger_from_context=_get_logger_from_context,
    )
    def send_initialized(self, params: InitializedParams) -> None:
        if self._state != "initializing":
            raise LSPClientException("Invalid state, expected 'initializing'.")

        self._send_notification_internal("initialized", params.to_json())
        self._set_state("running")

    @operation(
        start_message="Sending shutdown request.", get_logger_from_context=_get_logger_from_context
    )
    async def send_shutdown(self, **kwargs: Any) -> None:
        await super().send_shutdown(**kwargs)
        self._set_state("shutdown")

    @operation(
        start_message="Sending exit notification.", get_logger_from_context=_get_logger_from_context
    )
    async def send_exit(self) -> None:  # type: ignore  # pylint: disable=invalid-overridden-method
        """
        The exit event is sent from the client to the server to ask the server to exit its process.

        .. warning: This method is ``async``, despite only sending a notification, as it also waits for
            the language server process to exit.
        """
        if self._state != "shutdown":
            raise LSPClientException("Invalid state, expected 'shutdown'.")

        self._send_notification_internal("exit", None)

        try:
            assert self._protocol
            await wait_for(self._protocol.wait_for_disconnect(), 10.0)
            self._server_info = None
            self._server_capabilities = None
            self._set_state("disconnected")
        except asyncio.TimeoutError as e:
            raise LSPClientException("Unable to stop server thread.") from e

    async def __aenter__(self) -> "Client":
        # These 'if's are here so that the method can be called from any state.

        if self._state == "shutdown":
            await self.send_exit()
        if self._state == "disconnected":
            await self.launch()
        if self._state == "uninitialized":
            await self.send_initialize()
        if self._state == "initializing":
            self.send_initialized(InitializedParams())

        assert self._state == "running"
        return self

    async def __aexit__(
        self, exc_type: Type[Exception], exc_value: Exception, traceback: TracebackType
    ) -> bool:
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
            return self._workspace_request_handler.on_configuration(
                ConfigurationParams(items=params.items)
            )
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
            return ApplyWorkspaceEditResult(
                applied=False, failureReason="Client is not registered with a Workspace."
            )

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

    def on_window_show_message_request(
        self, params: ShowMessageRequestParams
    ) -> Union[MessageActionItem, None]:
        return NotImplemented

    def on_window_show_message(self, params: ShowMessageParams) -> None:
        if params.type is MessageType.Log:
            self._logger_server.debug("window/showMessage: %s", params.message)
        elif params.type is MessageType.Info:
            self._logger_server.info("window/showMessage: %s", params.message)
        elif params.type is MessageType.Warning:
            self._logger_server.warning("window/showMessage: %s", params.message)
        elif params.type is MessageType.Error:
            self._logger_server.error("window/showMessage: %s", params.message)

    def on_window_log_message(self, params: LogMessageParams) -> None:
        if params.type is MessageType.Log:
            self._logger_server.debug("window/logMessage: %s", params.message)
        elif params.type is MessageType.Info:
            self._logger_server.info("window/logMessage: %s", params.message)
        elif params.type is MessageType.Warning:
            self._logger_server.warning("window/logMessage: %s", params.message)
        elif params.type is MessageType.Error:
            self._logger_server.error("window/logMessage: %s", params.message)

    def on_telemetry_event(self, params: LSPAny) -> None:
        pass

    def on_s_log_trace(self, params: LogTraceParams) -> None:
        self._logger_server.debug("$/logTrace: %s", params.message)

    def on_s_cancel_request(self, params: CancelParams) -> None:
        pass

    def on_s_progress(self, params: ProgressParams) -> None:
        pass

    def __str__(self) -> str:
        return "client:" + str(self._id)

    def __repr__(self) -> str:
        values = {"id": self._id, "state": self._state}
        return f"{object.__repr__(self)} {values!r}"
