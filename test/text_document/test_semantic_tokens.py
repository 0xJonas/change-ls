from pathlib import Path
from typing import AsyncGenerator

import pytest

from change_ls import StdIOConnectionParams, TextDocument, Workspace


@pytest.fixture
async def mock_workspace_1(request: pytest.FixtureRequest) -> AsyncGenerator[Workspace, None]:
    test_sequence_marker = request.node.get_closest_marker('test_sequence')
    assert test_sequence_marker
    test_sequence = test_sequence_marker.args[0]

    workspace = Workspace(Path("test/mock-ws-1"))
    launch_params = StdIOConnectionParams(
        launch_command=f"node mock-server/out/index.js --stdio {test_sequence}")
    async with workspace.create_client(launch_params) as client:
        repo_uri = Path(".").resolve().as_uri()
        await client.send_request("$/setTemplateParams", {"expand": {"REPO_URI": repo_uri}})
        yield workspace


@pytest.fixture
async def mock_document_1(mock_workspace_1: Workspace) -> AsyncGenerator[TextDocument, None]:
    with mock_workspace_1.open_text_document(Path("test-1.py")) as doc:
        yield doc


@pytest.mark.test_sequence("test/text_document/test_semantic_tokens_enrich_basic.json")
async def test_semantic_tokens_enrich_basic(mock_document_1: TextDocument) -> None:
    await mock_document_1.load_tokens("enrich")

    assert mock_document_1.tokens[0].sem_type == "function"
    assert mock_document_1.tokens[0].sem_modifiers == {"defaultLibrary"}
    assert mock_document_1.tokens[3].sem_type == "string"
    assert mock_document_1.tokens[3].sem_modifiers == set()

    assert mock_document_1.sem_tokens[0].sem_type == "function"
    assert mock_document_1.sem_tokens[0].sem_modifiers == {"defaultLibrary"}
    assert mock_document_1.sem_tokens[1].sem_type == "string"
    assert mock_document_1.sem_tokens[1].sem_modifiers == set()


@pytest.mark.test_sequence("test/text_document/test_semantic_tokens_enrich_multiple_semantic_tokens_per_syntactic_token.json")
async def test_semantic_tokens_enrich_multiple_semantic_tokens_per_syntactic_token(mock_document_1: TextDocument) -> None:
    await mock_document_1.load_tokens("enrich")

    assert mock_document_1.tokens[0].sem_type == "function"
    assert mock_document_1.tokens[0].sem_modifiers == {"defaultLibrary"}

    assert mock_document_1.sem_tokens[0].lexeme == "pr"
    assert mock_document_1.sem_tokens[0].sem_type == "variable"
    assert mock_document_1.sem_tokens[0].sem_modifiers == set()
    assert mock_document_1.sem_tokens[1].lexeme == "int"
    assert mock_document_1.sem_tokens[1].sem_type == "function"
    assert mock_document_1.sem_tokens[1].sem_modifiers == {"defaultLibrary"}


@pytest.mark.test_sequence("test/text_document/test_semantic_tokens_enrich_nested_semantic_tokens.json")
async def test_semantic_tokens_enrich_nested_semantic_tokens(mock_document_1: TextDocument) -> None:
    await mock_document_1.load_tokens("enrich")

    assert mock_document_1.tokens[0].sem_type == "function"
    assert mock_document_1.tokens[0].sem_modifiers == {"defaultLibrary"}
    assert mock_document_1.tokens[1].sem_type == "function"
    assert mock_document_1.tokens[1].sem_modifiers == {"defaultLibrary"}
    assert mock_document_1.tokens[3].sem_type == "string"
    assert mock_document_1.tokens[3].sem_modifiers == set()

    assert mock_document_1.sem_tokens[0].lexeme == 'print("Hello, World!")'
    assert mock_document_1.sem_tokens[0].sem_type == "function"
    assert mock_document_1.sem_tokens[0].sem_modifiers == {"defaultLibrary"}
    assert mock_document_1.sem_tokens[1].lexeme == '"Hello, World!"'
    assert mock_document_1.sem_tokens[1].sem_type == "string"
    assert mock_document_1.sem_tokens[1].sem_modifiers == set()


@pytest.mark.test_sequence("test/text_document/test_semantic_tokens_apply_delta.json")
@pytest.mark.filterwarnings("ignore::change_ls.DroppedChangesWarning")
async def test_semantic_tokens_apply_delta(mock_document_1: TextDocument) -> None:
    await mock_document_1.load_tokens("semantic")
    mock_document_1.edit("logging.info", 0, 5)
    mock_document_1.commit_edits()
    await mock_document_1.load_tokens("semantic")  # New data: [0,0,7,2,2, 0,8,4,0,2, 0,5,15,3,0]

    assert mock_document_1.sem_tokens[0].lexeme == "logging"
    assert mock_document_1.sem_tokens[0].sem_type == "variable"
    assert mock_document_1.sem_tokens[0].sem_modifiers == {"defaultLibrary"}
    assert mock_document_1.sem_tokens[1].lexeme == "info"
    assert mock_document_1.sem_tokens[1].sem_type == "function"
    assert mock_document_1.sem_tokens[1].sem_modifiers == {"defaultLibrary"}
    assert mock_document_1.sem_tokens[2].lexeme == '"Hello, World!"'
    assert mock_document_1.sem_tokens[2].sem_type == "string"
    assert mock_document_1.sem_tokens[2].sem_modifiers == set()
