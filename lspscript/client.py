import subprocess
from asyncio import (AbstractEventLoop, BaseTransport, Future, get_running_loop,
                     new_event_loop, set_event_loop)
from os import getpid
from pathlib import Path
from socket import AF_INET
from threading import Thread
from typing import Any, Callable, Optional, Sequence, Tuple, Union

from lspscript.generated.dispatch import (write_notification_params,
                                          write_request_params)
from lspscript.generated.util import JSON_VALUE
from lspscript.protocol import (LSPException, LSProtocol, LSStreamingProtocol,
                                LSSubprocessProtocol)


class _ServerLaunchParams:
    server_path: Path
    additional_args: Sequence[str]
    additional_only: bool

    def __init__(self, *, server_path: Path, additional_args: Sequence[str] = [], additional_only: bool = False) -> None:
        self.server_path = server_path
        self.additional_args = additional_args
        self.additional_only = additional_only

    async def launch_server_from_event_loop(self, receive_callback: Callable[[str, JSON_VALUE], None]) -> Tuple[BaseTransport, LSProtocol]:
        raise NotImplemented


class StdIOConnectionParams(_ServerLaunchParams):
    """Launch parameters which launch a language server with stdio communication."""

    def __init__(self, *, server_path: Path, additional_args: Sequence[str] = [], additional_only: bool = False) -> None:
        """Constructs a new StdIOConnectionParams instance. This instance can then be
        used to launch a new client/server connection.

        Parameters:
        - `server_path`: The path were the language server executable is located.
        - `additional_args`: List of additional arguments to pass to the server.
        - `additional_only`: Do not send any standard arguments, only those in `additional_args`."""

        super().__init__(server_path=server_path, additional_args=additional_args, additional_only=additional_only)

    async def launch_server_from_event_loop(self, receive_callback: Callable[[str, JSON_VALUE], None]) -> Tuple[BaseTransport, LSProtocol]:
        args = ["--stdio", f"--clientProcessId={getpid()}"]
        if self.additional_only:
            args = self.additional_args
        else:
            args += self.additional_args
        loop = get_running_loop()
        return await loop.subprocess_exec(lambda: LSSubprocessProtocol(receive_callback), self.server_path, *args)


class SocketConnectionParams(_ServerLaunchParams):
    """Launch parameters which launch a language server with tcp socket communication."""

    server_path_opt: Optional[Path]
    hostname: str
    port: int

    def __init__(self, *,
                server_path: Optional[Path],
                port: int,
                hostname: str = "localhost",
                additional_args: Sequence[str] = [],
                additional_only: bool = False) -> None:
        """Constructs a new SocketConnectionParams instance. This instance can then
        be used to launch a new client/server connection.

        Parameters:
        - `server_path`: The path were the language server executable is located. When connecting
           to an already running server, the server_path may be `None`.
        - `port`: The port number to use for the TCP connection.
        - `hostname`: An optional name of a host to connect to. The default is 'localhost'.
        - `additional_args`: List of additional arguments to pass to the server.
        - `additional_only`: Do not send any standard arguments, only those in `additional_args`."""

        self.server_path_opt = server_path
        self.hostname = hostname
        self.port = port
        self.additional_args = additional_args
        self.additional_only = additional_only

    async def launch_server_from_event_loop(self, receive_callback: Callable[[str, JSON_VALUE], None]) -> Tuple[BaseTransport, LSProtocol]:
        args = [f"--socket={self.port}", f"--clientProcessId={getpid()}"]
        if self.additional_only:
            args = self.additional_args
        else:
            args += self.additional_args

        if self.server_path_opt:
            subprocess.Popen([self.server_path_opt.absolute()] + list(args))

        loop = get_running_loop()
        return await loop.create_connection(lambda: LSStreamingProtocol(receive_callback), host=self.hostname, port=self.port, family=AF_INET)


class PipeConnectionParams(_ServerLaunchParams):
    # Unix:
    #   event_loop.create_unix_connection(...)
    # Win:
    #   fd = create named pipe
    #   event_loop.subprocess_exec(stdin=fd, stdout=fd, ...)
    pipename: str


class Client:
    # Manages capabilities (client and server).
    # Handles dispatching requests/responses/notifications.

    _protocol: LSProtocol
    _launch_params: _ServerLaunchParams
    _comm_thread: Thread
    _comm_thread_event_loop: AbstractEventLoop

    def __init__(self, launch_params: _ServerLaunchParams) -> None:
        self._launch_params = launch_params

    async def _launch_internal(self) -> None:
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

    async def send_request(self, method: str, params: Any) -> Union[Any, LSPException]:
        """
        Sends a request to the server. If the server returns an error, the resulting
        exception is returned, but not raised.
        """

        json_data = write_request_params[method](params)
        future = get_running_loop().create_future()
        self._comm_thread_event_loop.call_soon_threadsafe(lambda: self._protocol.send_request(method, json_data, future))
        await future

        if result := future.result():
            return result
        elif exception := future.exception():
            return exception
        else:
            assert False # Future was cancelled # TODO raise something

    async def send_request_iter(self, method: str, params: Any) -> Any:
        # Version of send_request which returns an async iterator.
        # This method is used when partial results are requested.
        pass

    async def send_notification(self, method: str, params: Any) -> None:
        json_data = write_notification_params[method](params)
        self._comm_thread_event_loop.call_soon_threadsafe(lambda: self._protocol.send_notification(method, json_data))
