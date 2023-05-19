import shutil
from pathlib import Path
from typing import Any, Generator, Optional

import pytest

from lspscript.client import StdIOConnectionParams
from lspscript.types.structures import (
    CreateFile, DeleteFile, LSPAny, OptionalVersionedTextDocumentIdentifier,
    Position, Range, RenameFile, TextDocumentEdit, TextEdit, WorkspaceEdit)
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


@pytest.fixture
def scratch_workspace_path() -> Generator[Path, Any, None]:
    scratch_path = Path("./.temp/mock-ws-1/")
    shutil.copytree(Path("./test/mock-ws-1/"), scratch_path)
    yield scratch_path
    shutil.rmtree(scratch_path)


async def test_workspace_edit_changes(scratch_workspace_path: Path) -> None:
    doc_path = Path("test-1.py")
    doc_uri = (scratch_workspace_path / doc_path).resolve().as_uri()
    async with Workspace(scratch_workspace_path) as ws:
        launch_params = StdIOConnectionParams(
            launch_command="node mock-server/out/index.js --stdio test/test_workspace_edit_changes.json")
        client = await ws.launch_client(launch_params)

        workspace_uri = scratch_workspace_path.resolve().as_uri()
        await client.send_request("$/setTemplateParams", {"expand": {"WORKSPACE_URI": workspace_uri}})

        edit = WorkspaceEdit(changes={
            doc_uri: [
                TextEdit(range=Range(start=Position(line=0, character=7), end=Position(line=0, character=12)),
                         newText="Good morning")
            ]
        })

        await ws.perform_edit_and_save(edit)

        doc = ws.open_text_document(doc_path)
        assert doc.text == 'print("Good morning, World!")\n'


async def test_workspace_edit_document_changes(scratch_workspace_path: Path) -> None:
    doc1_path = Path("test-1.py")
    doc1_uri = (scratch_workspace_path / doc1_path).resolve().as_uri()
    temp_doc1_path = Path("temp_doc1.py")
    temp_doc1_uri = (scratch_workspace_path / temp_doc1_path).resolve().as_uri()
    temp_doc2_path = Path("temp_doc2.py")
    temp_doc2_uri = (scratch_workspace_path / temp_doc2_path).resolve().as_uri()

    async with Workspace(scratch_workspace_path) as ws:
        launch_params = StdIOConnectionParams(
            launch_command="node mock-server/out/index.js --stdio test/test_workspace_edit_document_changes.json")
        client = await ws.launch_client(launch_params)

        workspace_uri = scratch_workspace_path.resolve().as_uri()
        await client.send_request("$/setTemplateParams", {"expand": {"WORKSPACE_URI": workspace_uri}})

        edit = WorkspaceEdit(documentChanges=[
            TextDocumentEdit(textDocument=OptionalVersionedTextDocumentIdentifier(uri=doc1_uri, version=0), edits=[
                TextEdit(range=Range(start=Position(line=0, character=7), end=Position(line=0, character=12)),
                         newText="Good morning")
            ]),
            CreateFile(kind="create", uri=temp_doc1_uri),
            RenameFile(kind="rename", oldUri=temp_doc1_uri, newUri=temp_doc2_uri),
            DeleteFile(kind="delete", uri=temp_doc2_uri)
        ])

        await ws.perform_edit_and_save(edit)

        doc = ws.open_text_document(doc1_path)
        assert doc.text == 'print("Good morning, World!")\n'
