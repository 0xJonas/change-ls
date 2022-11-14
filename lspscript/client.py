import subprocess
from asyncio import (AbstractEventLoop, BaseTransport, Future, get_running_loop,
                     new_event_loop, set_event_loop)
from os import getpid
from pathlib import Path
from socket import AF_INET
from threading import Thread
from typing import Any, Callable, Optional, Sequence, Tuple, Union

from lspscript.generated.client_requests import ClientRequestsMixin
from lspscript.generated.util import JSON_VALUE
from lspscript.protocol import (LSPException, LSProtocol, LSStreamingProtocol,
                                LSSubprocessProtocol)


class _ServerLaunchParams:
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

    async def launch_server_from_event_loop(self, receive_callback: Callable[[str, JSON_VALUE], None]) -> Tuple[BaseTransport, LSProtocol]:
        raise NotImplemented


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


class Client(ClientRequestsMixin):
    # Manages capabilities (client and server).
    # Handles dispatching requests/responses/notifications.

    _protocol: LSProtocol
    _launch_params: _ServerLaunchParams
    _comm_thread: Thread
    _comm_thread_event_loop: AbstractEventLoop

    def __init__(self, launch_params: _ServerLaunchParams) -> None:
        self._launch_params = launch_params

    async def _launch_internal(self) -> None:
        # TODO add callback
        (_, self._protocol) = await self._launch_params.launch_server_from_event_loop(lambda _1, _2: None)

    def _client_loop(self, server_ready: "Future[None]") -> None:
        self._comm_thread_event_loop = new_event_loop()
        set_event_loop(self._comm_thread_event_loop)
        self._comm_thread_event_loop.run_until_complete(self._comm_thread_event_loop.create_task(self._launch_internal()))
        server_ready.get_loop().call_soon_threadsafe(lambda: server_ready.set_result(None))
        self._comm_thread_event_loop.run_forever()

    async def start(self) -> None:
        server_ready = get_running_loop().create_future()
        self._comm_thread = Thread(target=self._client_loop, args=[server_ready])
        self._comm_thread.start()
        await server_ready

    async def send_request(self, method: str, params: JSON_VALUE) -> Union[JSON_VALUE, LSPException]:
        """
        Sends a request to the server. If the server returns an error, the resulting
        exception is returned, but not raised.
        """

        future = get_running_loop().create_future()
        self._comm_thread_event_loop.call_soon_threadsafe(lambda: self._protocol.send_request(method, params, future))
        await future

        if result := future.result():
            return result
        elif exception := future.exception():
            assert isinstance(exception, LSPException)
            return exception
        else:
            assert False # Future was cancelled # TODO raise something

    async def send_request_iter(self, method: str, params: Any) -> Any:
        # Version of send_request which returns an async iterator.
        # This method is used when partial results are requested.
        pass

    async def send_notification(self, method: str, params: Any) -> None:
        self._comm_thread_event_loop.call_soon_threadsafe(lambda: self._protocol.send_notification(method, params))
