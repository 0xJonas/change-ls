from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest

from lspscript import Workspace
from lspscript.client import StdIOConnectionParams
from lspscript.text_document import TextDocument


@pytest.fixture
async def mock_workspace_1(request: pytest.FixtureRequest) -> AsyncGenerator[Workspace, None]:
    test_sequence_marker = request.node.get_closest_marker('test_sequence')
    assert test_sequence_marker
    test_sequence = test_sequence_marker.args[0]

    workspace = Workspace(Path("test/mock-ws-1"))
    launch_params = StdIOConnectionParams(
        launch_command=f"node mock-server/out/index.js --stdio {test_sequence}")
    async with workspace.launch_client(launch_params) as client:
        repo_uri = Path(".").resolve().as_uri()
        await client.send_request("$/setTemplateParams", {"expand": {"REPO_URI": repo_uri}})
        yield workspace


@pytest.fixture
async def mock_document_1(mock_workspace_1: Workspace) -> AsyncGenerator[TextDocument, None]:
    with mock_workspace_1.open_text_document(Path("test-1.py")) as doc:
        yield doc


@pytest.mark.test_sequence("test/test_text_document_open_close.json")
def test_text_documents_open_close(mock_document_1: TextDocument) -> None:
    assert mock_document_1.text == 'print("Hello, World!")\n'
    assert mock_document_1.language_id == "python"
    assert mock_document_1.version == 0

    repo_uri = Path(".").resolve().as_uri()
    assert mock_document_1.uri == repo_uri + "/test/mock-ws-1/test-1.py"


@pytest.mark.test_sequence("test/test_text_document_edit.json")
def test_text_document_edit(mock_document_1: TextDocument) -> None:
    mock_document_1.edit("Good morning", 7, 12)
    mock_document_1.commit_edits()
    assert mock_document_1.text == 'print("Good morning, World!")\n'
    assert mock_document_1.version == 1


@pytest.mark.test_sequence("test/test_text_document_edit_incremental.json")
def test_text_document_edit_incremental(mock_document_1: TextDocument) -> None:
    mock_document_1.edit("Hi", 7, 12)
    mock_document_1.edit("logging.info", 0, length=5)
    mock_document_1.commit_edits()
    assert mock_document_1.text == 'logging.info("Hi, World!")\n'
    assert mock_document_1.version == 1


@pytest.mark.test_sequence("test/test_text_document_open_close.json")
def test_text_documents_disallowed_edits(mock_document_1: TextDocument) -> None:
    mock_document_1.edit("Good morning", 7, 12)

    # overlapping edit
    with pytest.raises(ValueError):
        mock_document_1.edit("Error", 8, 15)

    # Out of bounds edit
    with pytest.raises(IndexError):
        mock_document_1.edit("Error", 12, length=100)


@pytest.mark.test_sequence("test/test_text_document_edit_tokens.json")
async def test_text_document_edit_tokens(mock_document_1: TextDocument) -> None:
    await mock_document_1.load_tokens()
    mock_document_1.edit_tokens("logging.info", 0)
    mock_document_1.edit_tokens("'Hi, World!'", 2, 5)  # Note the single quotes
    mock_document_1.commit_edits()
    assert mock_document_1.text == "logging.info('Hi, World!')\n"


@pytest.fixture
def temp_file_path() -> Generator[Path, None, None]:
    path = Path("./test/mock-ws-1/tempfile.py")
    with path.open("w") as file:
        file.write("print('Hi!')\n")
    yield path.absolute()
    path.unlink()


@pytest.mark.test_sequence("test/test_text_document_save.json")
async def test_text_document_save(temp_file_path: Path, mock_workspace_1: Workspace) -> None:
    with mock_workspace_1.open_text_document(temp_file_path) as doc:
        doc.edit("Bye", 7, 9)
        doc.commit_edits()
        await doc.save()
        with temp_file_path.open() as file:
            assert file.read() == "print('Good Bye!')\n"
