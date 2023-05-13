from pathlib import Path
from typing import Optional

from lspscript.client import StdIOConnectionParams
from lspscript.types.structures import LSPAny
from lspscript.workspace import Workspace


async def test_workspace_launch_clients() -> None:
    workspace = Workspace(Path("test/mock-ws-1"),
                          Path("test/mock-ws-2"),
                          names=["mock-ws-1", "mock-ws-2"])
    launch_params = StdIOConnectionParams(
        launch_command="node mock-server/out/index.js --stdio test/test_workspace.json")
    async with workspace.create_client(launch_params) as client:
        repo_uri = Path(".").resolve().as_uri()
        await client.send_request("$/setTemplateParams", {"expand": {"REPO_URI": repo_uri}})
        await client.send_request("$/go", None)


def mock_config_provider(scope_uri: Optional[str], section: Optional[str]) -> LSPAny:
    if section == "Test1":
        assert scope_uri == "file:///repo/test/mock-ws-1"
        return 5
    elif section == "Test2":
        assert scope_uri == "file:///repo/test/mock-ws-2"
        return 10
    else:
        assert False


async def test_workspace_configuration_provider() -> None:
    workspace = Workspace(Path("test/mock-ws-1"), Path("test/mock-ws-2"))
    workspace.set_configuration_provider(mock_config_provider)
    launch_params = StdIOConnectionParams(
        launch_command="node mock-server/out/index.js --stdio test/test_configuration_provider.json")
    async with workspace.create_client(launch_params) as client:
        await client.send_request("$/go", None)


async def test_workspace_context_manager() -> None:
    async with Workspace(Path("test/mock-ws-1")) as ws:
        launch_params = StdIOConnectionParams(
            launch_command="node mock-server/out/index.js --stdio test/text_document/test_text_document_open_close.json")
        client = await ws.launch_client(launch_params)
        assert client.get_state() == "running"

        repo_uri = Path(".").resolve().as_uri()
        await client.send_request("$/setTemplateParams", {"expand": {"REPO_URI": repo_uri}})

        doc = ws.open_text_document(Path("test-1.py"))

    assert doc.is_closed()
    assert client.get_state() == "disconnected"
