from pathlib import Path
from typing import AsyncGenerator, Tuple

import pytest

from change_ls import (
    ChangeLSError,
    Client,
    CustomSymbol,
    StdIOConnectionParams,
    UnresolvedWorkspaceSymbol,
    Workspace,
    WorkspaceSymbol,
)
from change_ls.types import (
    OptionalVersionedTextDocumentIdentifier,
    Position,
    Range,
    SymbolKind,
    TextDocumentEdit,
    TextEdit,
    WorkspaceEdit,
)


@pytest.mark.filterwarnings("ignore::change_ls.DroppedChangesWarning")
async def test_symbol_invalid_anchor() -> None:
    async with Workspace(Path("test/mock-ws-1")) as ws:
        launch_params = StdIOConnectionParams(
            launch_command=f"node mock-server/out/index.js --stdio test/symbol/test_symbol_invalid_anchor.json"
        )
        client = await ws.launch_client(launch_params)

        repo_uri = Path(".").resolve().as_uri()
        await client.send_request("$/setTemplateParams", {"expand": {"REPO_URI": repo_uri}})

        doc = ws.open_text_document(Path("./test-2.py"), encoding="utf-8")
        symbol = doc.create_symbol_at(4, 8, SymbolKind.Function)

        doc.edit("changed", 4, 8)
        doc.commit_edits()

        with pytest.raises(ChangeLSError):
            await symbol.find_references()


@pytest.fixture
async def mock_ws_1(
    request: pytest.FixtureRequest,
) -> AsyncGenerator[Tuple[Workspace, Client], None]:
    # pytest does not annotate request.node correctly
    test_sequence_marker = request.node.get_closest_marker("test_sequence")  # type: ignore
    assert test_sequence_marker
    test_sequence = test_sequence_marker.args[0]  # type: ignore

    async with Workspace(Path("test/mock-ws-1")) as ws:
        launch_params = StdIOConnectionParams(
            launch_command=f"node mock-server/out/index.js --stdio {test_sequence}"
        )
        client = await ws.launch_client(launch_params)

        repo_uri = Path(".").resolve().as_uri()
        await client.send_request("$/setTemplateParams", {"expand": {"REPO_URI": repo_uri}})
        yield ws, client


@pytest.fixture
async def custom_symbol(mock_ws_1: Tuple[Workspace, Client]) -> AsyncGenerator[CustomSymbol, None]:
    ws, _ = mock_ws_1
    doc = ws.open_text_document(Path("./test-2.py"), encoding="utf-8")
    yield doc.create_symbol_at(4, 8, SymbolKind.Function)


@pytest.mark.test_sequence("test/symbol/test_symbol_rename.json")
async def test_symbol_rename(custom_symbol: CustomSymbol) -> None:
    edit = await custom_symbol.get_rename_workspace_edit("test")

    document_uri = Path("./test/mock-ws-1/test-2.py").resolve().as_uri()
    expected = WorkspaceEdit(
        documentChanges=[
            TextDocumentEdit(
                textDocument=OptionalVersionedTextDocumentIdentifier(uri=document_uri, version=1),
                edits=[
                    TextEdit(
                        newText="test",
                        range=Range(
                            start=Position(line=0, character=4), end=Position(line=0, character=8)
                        ),
                    ),
                    TextEdit(
                        newText="test",
                        range=Range(
                            start=Position(line=6, character=4), end=Position(line=6, character=8)
                        ),
                    ),
                ],
            )
        ]
    )
    assert edit == expected


@pytest.mark.test_sequence("test/symbol/test_symbol_find_references.json")
async def test_symbol_find_references(custom_symbol: CustomSymbol) -> None:
    doc, (start, end) = (
        await custom_symbol.find_references(include_declaration=False)
    ).get_single_entry()

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


@pytest.mark.test_sequence("test/symbol/test_query_symbols_no_resolve.json")
async def test_query_symbols_no_resolve(mock_ws_1: Tuple[Workspace, Client]) -> None:
    ws, _ = mock_ws_1

    unresolved_symbols = await ws.query_symbols("main", resolve=False)
    assert len(unresolved_symbols) == 1

    sym = unresolved_symbols[0]
    assert isinstance(sym, UnresolvedWorkspaceSymbol)
    assert sym.name == "main"
    assert sym.kind == SymbolKind.Function
    assert sym.uri == Path("test/mock-ws-1/test-2.py").resolve().as_uri()
    assert sym.tags == []
    assert sym.container_name is None


@pytest.mark.test_sequence("test/symbol/test_query_symbols_resolve.json")
async def test_query_symbols_resolve(mock_ws_1: Tuple[Workspace, Client]) -> None:
    ws, _ = mock_ws_1

    symbols = await ws.query_symbols("main")
    assert len(symbols) == 1

    with symbols[0] as sym:
        assert isinstance(sym, WorkspaceSymbol)
        assert sym.name == "main"
        assert sym.kind == SymbolKind.Function
        assert sym.uri == Path("test/mock-ws-1/test-2.py").resolve().as_uri()
        assert sym.tags == []
        assert sym.container_name == "test-2.py"
        assert sym.range == (4, 8)

    with pytest.raises(ChangeLSError):
        # Symbol was closed
        await sym.find_references()


@pytest.mark.test_sequence("test/symbol/test_load_all_symbols.json")
async def test_load_all_symbols(mock_ws_1: Tuple[Workspace, Client]) -> None:
    ws, _ = mock_ws_1

    unresolved_symbols = await ws.load_all_symbols()
    assert len(unresolved_symbols) == 2

    assert isinstance(unresolved_symbols[0], UnresolvedWorkspaceSymbol)
    assert unresolved_symbols[0].name == "print"
    assert unresolved_symbols[0].kind == SymbolKind.Function
    assert unresolved_symbols[0].uri == Path("test/mock-ws-1/test-1.py").resolve().as_uri()
    assert unresolved_symbols[0].tags == []
    assert unresolved_symbols[0].container_name is None

    assert isinstance(unresolved_symbols[1], UnresolvedWorkspaceSymbol)
    assert unresolved_symbols[1].name == "main"
    assert unresolved_symbols[1].kind == SymbolKind.Function
    assert unresolved_symbols[1].uri == Path("test/mock-ws-1/test-2.py").resolve().as_uri()
    assert unresolved_symbols[1].tags == []
    assert unresolved_symbols[1].container_name is None


@pytest.mark.test_sequence("test/symbol/test_load_outline.json")
async def test_load_outline(mock_ws_1: Tuple[Workspace, Client]) -> None:
    ws, _ = mock_ws_1

    doc = ws.open_text_document(Path("test-2.py"))
    await doc.load_outline()
    outline = doc.get_loaded_outline()

    assert len(outline) == 1
    assert outline[0].name == "main"
    assert outline[0].uri == doc.uri
    assert outline[0].range == (4, 8)
    assert outline[0].symbol_range == (4, 8)
    assert outline[0].context_range == (0, 11)
    assert outline[0].detail == "def main() -> None"
    assert outline[0].kind == SymbolKind.Function
    assert outline[0].children is not None
    assert len(outline[0].children) == 2
    for c in outline[0].children:
        assert c.name == "print"
        assert c.uri == doc.uri
        assert c.kind == SymbolKind.Variable
        assert c.children is None
