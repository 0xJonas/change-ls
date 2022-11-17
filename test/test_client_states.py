from lspscript.client import Client, StdIOConnectionParams
from lspscript.types import ClientCapabilities, InitializeParams, InitializedParams
from os import getpid


async def test_client_assumes_correct_states() -> None:
    params = StdIOConnectionParams(launch_command="node mock-server/out/index.js --stdio test/test_client_states.json")
    client = Client(params)
    assert client.get_state() == "disconnected"

    await client.launch()
    assert client.get_state() == "uninitialized"

    await client.send_initialize(InitializeParams(processId=getpid(), rootUri=None, capabilities=ClientCapabilities()))
    assert client.get_state() == "initializing"

    await client.send_initialized(InitializedParams())
    assert client.get_state() == "running"

    await client.send_shutdown()
    assert client.get_state() == "shutdown"

    await client.send_exit()
    assert client.get_state() == "disconnected"


async def test_client_context_manager_normal() -> None:
    params = StdIOConnectionParams(launch_command="node mock-server/out/index.js --stdio test/test_client_states.json")
    async with Client(params) as client:
        assert client.get_state() == "running"
