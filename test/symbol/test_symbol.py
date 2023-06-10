from pathlib import Path
from typing import AsyncGenerator

import pytest

from lspscript.client import StdIOConnectionParams
from lspscript.lsp_exception import LSPScriptException
from lspscript.symbol import CustomSymbol
from lspscript.types.enumerations import SymbolKind
from lspscript.types.structures import (
    OptionalVersionedTextDocumentIdentifier, Position, Range, TextDocumentEdit,
    TextEdit, WorkspaceEdit)
from lspscript.workspace import Workspace


async def test_symbol_invalid_anchor() -> None:
    async with Workspace(Path("test/mock-ws-1")) as ws:
        launch_params = StdIOConnectionParams(
            launch_command=f"node mock-server/out/index.js --stdio test/symbol/test_symbol_invalid_anchor.json")
        client = await ws.launch_client(launch_params)

        repo_uri = Path(".").resolve().as_uri()
        await client.send_request("$/setTemplateParams", {"expand": {"REPO_URI": repo_uri}})

        doc = ws.open_text_document(Path("./test-2.py"), encoding="utf-8")
        symbol = doc.create_symbol_at(4, 8, SymbolKind.Function)

        doc.edit("changed", 4, 8)
        doc.commit_edits()

        with pytest.raises(LSPScriptException):
            await symbol.find_references()


@pytest.fixture
async def custom_symbol(request: pytest.FixtureRequest) -> AsyncGenerator[CustomSymbol, None]:
    test_sequence_marker = request.node.get_closest_marker('test_sequence')
    assert test_sequence_marker
    test_sequence = test_sequence_marker.args[0]

    async with Workspace(Path("test/mock-ws-1")) as ws:
        launch_params = StdIOConnectionParams(launch_command=f"node mock-server/out/index.js --stdio {test_sequence}")
        client = await ws.launch_client(launch_params)

        repo_uri = Path(".").resolve().as_uri()
        await client.send_request("$/setTemplateParams", {"expand": {"REPO_URI": repo_uri}})

        doc = ws.open_text_document(Path("./test-2.py"), encoding="utf-8")
        yield doc.create_symbol_at(4, 8, SymbolKind.Function)


@pytest.mark.test_sequence("test/symbol/test_symbol_rename.json")
async def test_symbol_rename(custom_symbol: CustomSymbol) -> None:
    edit = await custom_symbol.get_rename_workspace_edit("test")

    document_uri = Path("./test/mock-ws-1/test-2.py").resolve().as_uri()
    expected = WorkspaceEdit(documentChanges=[
        TextDocumentEdit(textDocument=OptionalVersionedTextDocumentIdentifier(uri=document_uri, version=1),
                         edits=[TextEdit(newText="test",
                                         range=Range(start=Position(line=0, character=4),
                                                     end=Position(line=0, character=8))),
                                TextEdit(newText="test",
                                         range=Range(start=Position(line=6, character=4),
                                                     end=Position(line=6, character=8)))])
    ])
    assert edit == expected


@pytest.mark.test_sequence("test/symbol/test_symbol_find_references.json")
async def test_symbol_find_references(custom_symbol: CustomSymbol) -> None:
    doc, (start, end) = (await custom_symbol.find_references(include_declaration=False)).get_single_entry()

    assert doc.uri.endswith("test/mock-ws-1/test-2.py")
    assert start == 77
    assert end == 81

    locations = await custom_symbol.find_references(include_declaration=True)
    assert len(locations) == 1
    document_locations = next(iter(locations.values()))
    assert document_locations[0] == (4, 8)
    assert document_locations[1] == (77, 81)


@pytest.mark.test_sequence("test/symbol/test_symbol_find_declaration.json")
async def test_symbol_find_declaration(custom_symbol: CustomSymbol) -> None:
    doc, (start, end) = (await custom_symbol.find_declaration()).get_single_entry()

    assert doc.uri.endswith("test/mock-ws-1/test-2.py")
    assert start == 4
    assert end == 8


@pytest.mark.test_sequence("test/symbol/test_symbol_find_definition.json")
async def test_symbol_find_definition(custom_symbol: CustomSymbol) -> None:
    doc, (start, end) = (await custom_symbol.find_definition()).get_single_entry()

    assert doc.uri.endswith("test/mock-ws-1/test-2.py")
    assert start == 4
    assert end == 8


@pytest.mark.test_sequence("test/symbol/test_symbol_find_type_definition.json")
async def test_symbol_find_type_definition(custom_symbol: CustomSymbol) -> None:
    doc, (start, end) = (await custom_symbol.find_type_definition()).get_single_entry()

    assert doc.uri.endswith("test/mock-ws-1/test-2.py")
    assert start == 4
    assert end == 8


@pytest.mark.test_sequence("test/symbol/test_symbol_find_implementation.json")
async def test_symbol_find_implementation(custom_symbol: CustomSymbol) -> None:
    doc, (start, end) = (await custom_symbol.find_implementation()).get_single_entry()

    assert doc.uri.endswith("test/mock-ws-1/test-2.py")
    assert start == 4
    assert end == 8
