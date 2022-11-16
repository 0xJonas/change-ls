from abc import ABC, abstractmethod
import subprocess
from asyncio import (AbstractEventLoop, BaseTransport, Future,
                     get_running_loop, new_event_loop, set_event_loop)
from os import getpid
from pathlib import Path
from socket import AF_INET
from threading import Thread
from types import TracebackType
from typing import Callable, Literal, Optional, Sequence, Tuple, Type

from lspscript.generated.client_requests import ClientRequestsMixin
from lspscript.generated.structures import ClientCapabilities, InitializeParams, InitializeResult, InitializedParams
from lspscript.generated.util import JSON_VALUE, json_assert_type_object
from lspscript.protocol import (LSPClientException, LSProtocol, LSStreamingProtocol,
                                LSSubprocessProtocol)


class _ServerLaunchParams(ABC):
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
    async def launch_server_from_event_loop(self, receive_callback: Callable[[str, JSON_VALUE], None]) -> Tuple[BaseTransport, LSProtocol]:
        pass


class StdIOConnectionParams(_ServerLaunchParams):
    """Launch parameters which launch a language server with stdio communication."""

    def __init__(self, *,
                 server_path: Optional[Path] = None,
                 launch_command: Optional[str] = None,
                 additional_args: Sequence[str] = [],
                 additional_only: bool = False) -> None:
        """Constructs a new StdIOConnectionParams instance. This instance can then be
        used to launch a new client/server connection.

        Either `server_path` or `launch_command` must be set.

        Parameters:
        - `server_path`: The path were the language server executable is located.
        - `launch_command`: Shell command to start the server. If a launch command is given,
          no additional arguments are appended. This means that the caller may also need
          to add `--stdio` to the command to select a connection via standard input/output streams.
        - `additional_args`: List of additional arguments to pass to the server.
        - `additional_only`: Do not send any standard arguments, only those in `additional_args`."""

        if not server_path and not launch_command:
            raise ValueError("Either server_path or launch_command need to be set.")

        super().__init__(server_path=server_path, additional_args=additional_args, launch_command=launch_command, additional_only=additional_only)

    async def launch_server_from_event_loop(self, receive_callback: Callable[[str, JSON_VALUE], None]) -> Tuple[BaseTransport, LSProtocol]:
        args = ["--stdio", f"--clientProcessId={getpid()}"]
        if self.additional_only:
            args = self.additional_args
        else:
            args += self.additional_args
        loop = get_running_loop()
        if self.server_path:
            return await loop.subprocess_exec(lambda: LSSubprocessProtocol(receive_callback), self.server_path, *args)
        elif self.launch_command:
            return await loop.subprocess_shell(lambda: LSSubprocessProtocol(receive_callback), self.launch_command)
        else:
            assert False


class SocketConnectionParams(_ServerLaunchParams):
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

        super().__init__(server_path=server_path, launch_command=launch_command, additional_args=additional_args, additional_only=additional_only)
        self.hostname = hostname
        self.port = port

    async def launch_server_from_event_loop(self, receive_callback: Callable[[str, JSON_VALUE], None]) -> Tuple[BaseTransport, LSProtocol]:
        args = [f"--socket={self.port}", f"--clientProcessId={getpid()}"]
        if self.additional_only:
            args = self.additional_args
        else:
            args += self.additional_args

        if self.server_path:
            subprocess.Popen([self.server_path.absolute()] + list(args))
        elif self.launch_command:
            subprocess.Popen(self.launch_command, shell=True)

        loop = get_running_loop()
        return await loop.create_connection(lambda: LSStreamingProtocol(receive_callback), host=self.hostname, port=self.port, family=AF_INET)


class PipeConnectionParams(_ServerLaunchParams):
    # Unix:
    #   event_loop.create_unix_connection(...)
    # Win:
    #   fd = create named pipe
    #   event_loop.subprocess_exec(stdin=fd, stdout=fd, ...)
    pipename: str


def get_default_client_capabilities() -> ClientCapabilities:
    out = ClientCapabilities()
    return out

ClientState = Literal["disconnected", "uninitialized", "initializing", "running", "shutdown"]

class Client(ClientRequestsMixin):
    # Manages capabilities (client and server).
    # Handles dispatching requests/responses/notifications.

    _state: ClientState
    _protocol: Optional[LSProtocol]
    _launch_params: _ServerLaunchParams
    _comm_thread: Optional[Thread]
    _comm_thread_event_loop: Optional[AbstractEventLoop]

    # Whether or not an 'exit' notification was sent. This is used
    # to distinguish a normal termination of the server from a crash.
    _exit_sent: bool

    def __init__(self, launch_params: _ServerLaunchParams) -> None:
        self._state = "disconnected"
        self._protocol = None
        self._launch_params = launch_params
        self._comm_thread = None
        self._comm_thread_event_loop = None
        self._exit_sent = False

    async def _launch_internal(self) -> None:
        # TODO add callback
        (_, self._protocol) = await self._launch_params.launch_server_from_event_loop(lambda _1, _2: None)

    def _client_loop(self, server_ready: "Future[None]") -> None:
        # Runs on the Client's thread
        self._comm_thread_event_loop = new_event_loop()
        set_event_loop(self._comm_thread_event_loop)
        self._comm_thread_event_loop.run_until_complete(self._comm_thread_event_loop.create_task(self._launch_internal()))
        server_ready.get_loop().call_soon_threadsafe(lambda: server_ready.set_result(None))
        self._comm_thread_event_loop.run_forever()
        self._state = "disconnected"
        if not self._exit_sent:
            raise LSPClientException("Server stopped unexpectedly.")

    def get_state(self) -> ClientState:
        """
        Returns the current state of the `Client`.

        Possible values:
        - `disconnected`: No server process is running. When a server process is launched with `client.launch()`,
                        the server enters the `uninitialized` state.
        - `uninitialized`: The server is running, but no 'initialize' request has been sent. After the 'initialize'
                         request has been sent, the `Client` enters the `initializing` state.
        - `initializing`: The `Client` has received the result of the 'initialize' request, but has not yet sent the
                        'initialized' notification. Doing so will put the `Client` in the `running` state.
        - `running`: The server is running and ready to receive requests. Sending a 'shutdown' request
                   will put the `Client` in the `shutdown` state.
        - `shutdown`: The server shutting down. Sending an 'exit' notification will cause the `Client` to
                    enter the `disconnected` state.
        """
        return self._state

    async def launch(self) -> None:
        """
        Starts the Language Server.
        """
        self._exit_sent = False
        server_ready = get_running_loop().create_future()
        self._comm_thread = Thread(target=self._client_loop, args=[server_ready])
        self._comm_thread.start()
        await server_ready
        self._state = "uninitialized"

    async def _send_request_internal(self, method: str, params: JSON_VALUE) -> JSON_VALUE:
        assert self._comm_thread_event_loop

        future = get_running_loop().create_future()
        self._comm_thread_event_loop.call_soon_threadsafe(lambda: self._protocol and self._protocol.send_request(method, params, future))
        await future

        assert not future.cancelled()
        if exception := future.exception():
            raise exception
        else:
            return future.result()

    async def send_request(self, method: str, params: JSON_VALUE) -> JSON_VALUE:
        """
        Sends a request to the server. The method and contents of the request are arbitrary
        and need not be defined in the LSP.
        """
        if self._state != "running":
            raise LSPClientException("Invalid state, expected 'running'.")
        return await self._send_request_internal(method, params)

    async def send_request_iter(self, method: str, params: JSON_VALUE) -> JSON_VALUE:
        # Version of send_request which returns an async iterator.
        # This method is used when partial results are requested.
        pass

    async def _send_notification_internal(self, method: str, params: JSON_VALUE) -> None:
        assert self._comm_thread_event_loop
        self._comm_thread_event_loop.call_soon_threadsafe(lambda: self._protocol and self._protocol.send_notification(method, params))

    async def send_notification(self, method: str, params: JSON_VALUE) -> None:
        """
        Sends a notification to the server. The method and contents of the notification are arbitrary
        and need not be defined in the LSP.
        """
        if self._state != "running":
            raise LSPClientException("Invalid state, expected 'running'.")
        await self._send_notification_internal(method, params)

    async def send_initialize(self, params: InitializeParams) -> InitializeResult:
        if self._state != "uninitialized":
            raise LSPClientException("Invalid state, expected 'uninitialized'.")

        out_json = await self._send_request_internal("initialize", params.to_json())
        out = InitializeResult.from_json(json_assert_type_object(out_json))
        self._state = "initializing"
        return out

    async def send_initialized(self, params: InitializedParams) -> None:
        if self._state != "initializing":
            raise LSPClientException("Invalid state, expected 'initializing'.")

        await self._send_notification_internal("initialized", params.to_json())
        self._state = "running"

    async def send_shutdown(self) -> None:
        await super().send_shutdown()
        self._state = "shutdown"

    async def send_exit(self) -> None:
        if self._state != "shutdown":
            raise LSPClientException("Invalid state, expected 'shutdown'.")

        # We set _exit_sent optimistically before the notification is actually sent.
        # This has to be set beforehand because otherwise the thread might switch after
        # the notification was sent, but before _exit_sent is set to True.
        self._exit_sent = True
        try:
            await self._send_notification_internal("exit", None)
        except:
            # Something went wrong, so assume we did not actually send the notification.
            self._exit_sent = False
            raise

        assert self._comm_thread
        self._comm_thread.join(10.0)
        if self._comm_thread.is_alive():
            raise LSPClientException("Unable to stop server thread.")

    async def __aenter__(self) -> "Client":
        # These 'if's are here so that the method can be called from any state.

        if self._state == "shutdown":
            await self.send_exit()
        if self._state == "disconnected":
            await self.launch()
        if self._state == "uninitialized":
            # TODO provide actual parameters
            # TODO store result
            await self.send_initialize(InitializeParams(processId=getpid(), rootUri=None, capabilities=ClientCapabilities()))
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
