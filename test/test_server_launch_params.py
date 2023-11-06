import sys

from change_ls import Client, PipeConnectionParams, SocketConnectionParams, StdIOConnectionParams


async def test_stdio_connection_params() -> None:
    params = StdIOConnectionParams(
        launch_command="node ./mock-server/out/index.js --stdio test/test_empty.json"
    )
    async with Client(params):
        pass


async def test_socket_connection_params() -> None:
    port = 5555
    params = SocketConnectionParams(
        launch_command=f"node ./mock-server/out/index.js --socket={port} test/test_empty.json",
        port=port,
    )
    async with Client(params):
        pass


async def test_pipe_connection_params() -> None:
    pipe_name = r"\\.\pipe\test_pipe" if sys.platform == "win32" else "test_pipe"
    params = PipeConnectionParams(
        launch_command=f"node ./mock-server/out/index.js --pipe={pipe_name} test/test_empty.json",
        pipe_name=pipe_name,
    )
    async with Client(params):
        pass
