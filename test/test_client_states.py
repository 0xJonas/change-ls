from os import getpid

from change_ls import Client, StdIOConnectionParams
from change_ls.types import ClientCapabilities, InitializedParams, InitializeParams


async def test_client_assumes_correct_states() -> None:
    params = StdIOConnectionParams(
        launch_command="node mock-server/out/index.js --stdio test/test_empty.json"
    )
    client = Client(params)
    assert client.get_state() == "disconnected"

    await client.launch()
    assert client.get_state() == "uninitialized"

    await client.send_initialize(
        InitializeParams(processId=getpid(), rootUri=None, capabilities=ClientCapabilities())
    )
    assert client.get_state() == "initializing"

    client.send_initialized(InitializedParams())
    assert client.get_state() == "running"

    await client.send_shutdown()
    assert client.get_state() == "shutdown"

    await client.send_exit()
    assert client.get_state() == "disconnected"


async def test_client_context_manager_normal() -> None:
    params = StdIOConnectionParams(
        launch_command="node mock-server/out/index.js --stdio test/test_empty.json"
    )
    async with Client(params) as client:
        assert client.get_state() == "running"


async def test_client_state_callbacks() -> None:
    marker = 0

    def set_marker(val: int) -> None:
        nonlocal marker
        marker = val

    params = StdIOConnectionParams(
        launch_command="node mock-server/out/index.js --stdio test/test_empty.json"
    )
    client = Client(params)

    client.register_state_callback("uninitialized", lambda: set_marker(1))
    client.register_state_callback("initializing", lambda: set_marker(2))
    client.register_state_callback("running", lambda: set_marker(3))
    client.register_state_callback("shutdown", lambda: set_marker(4))
    client.register_state_callback("disconnected", lambda: set_marker(5))

    await client.launch()
    assert marker == 1

    await client.send_initialize(
        InitializeParams(processId=getpid(), rootUri=None, capabilities=ClientCapabilities())
    )
    assert marker == 2

    client.send_initialized(InitializedParams())
    assert marker == 3

    await client.send_shutdown()
    assert marker == 4

    await client.send_exit()
    assert marker == 5
