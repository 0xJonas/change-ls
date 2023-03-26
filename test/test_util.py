from pathlib import Path

import pytest

import lspscript.languages as languages
from lspscript.tokens import Grammar, GrammarFormat
from lspscript.types.enumerations import FileOperationPatternKind
from lspscript.types.structures import (FileOperationFilter,
                                        FileOperationPattern,
                                        FileOperationPatternOptions,
                                        TextDocumentFilter)
from lspscript.util import (install_language, matches_file_operation_filter,
                            matches_text_document_filter)


def test_matches_text_document_filter() -> None:
    filter1: TextDocumentFilter = {
        "pattern": "**/test.py"
    }

    base = Path(".").absolute()
    path1 = base / "test/test.py"
    path2 = base / "test/test.json"
    path3 = base / "test/test.ts"

    assert matches_text_document_filter(path1.as_uri(), filter1)
    assert not matches_text_document_filter(path2.as_uri(), filter1)

    filter2: TextDocumentFilter = {
        "language": "python",
        "scheme": "file"
    }

    assert matches_text_document_filter(path1.as_uri(), filter2)
    assert not matches_text_document_filter(path2.as_uri(), filter2)

    filter3: TextDocumentFilter = {
        "pattern": "**/test.{py,json}"
    }

    assert matches_text_document_filter(path1.as_uri(), filter3)
    assert matches_text_document_filter(path2.as_uri(), filter3)
    assert not matches_text_document_filter(path3.as_uri(), filter3)


def test_matches_file_operation_filter() -> None:
    filter1 = FileOperationFilter(pattern=FileOperationPattern(glob="**/test.py"))
    filter2 = FileOperationFilter(pattern=FileOperationPattern(glob="**/test.{py,json}"))
    filter3 = FileOperationFilter(pattern=FileOperationPattern(glob="**/test", matches=FileOperationPatternKind.folder))
    filter4 = FileOperationFilter(pattern=FileOperationPattern(
        glob="**/test/xxx", options=FileOperationPatternOptions(ignoreCase=True)))

    base = Path(".").absolute()
    path1 = base / "test/test.py"
    path2 = base / "test/test.json"
    path3 = base / "test/test.ts"
    path4 = base / "test/"
    path5 = base / "test/xxx"
    path6 = base / "test/XXX"

    assert matches_file_operation_filter(path1.as_uri(), filter1)
    assert not matches_file_operation_filter(path2.as_uri(), filter1)

    assert matches_file_operation_filter(path1.as_uri(), filter2)
    assert matches_file_operation_filter(path2.as_uri(), filter2)
    assert not matches_file_operation_filter(path3.as_uri(), filter2)

    assert not matches_file_operation_filter(path1.as_uri(), filter3)
    assert matches_file_operation_filter(path4.as_uri(), filter3)

    assert not matches_file_operation_filter(path4.as_uri(), filter4)
    assert matches_file_operation_filter(path5.as_uri(), filter4)
    assert matches_file_operation_filter(path6.as_uri(), filter4)


class MockGrammar(Grammar):
    content: str

    def __init__(self, scope_name: str, content: str) -> None:
        super().__init__(scope_name)
        self.content = content

    def get_content(self) -> str:
        return self.content

    def get_format(self) -> GrammarFormat:
        return super().get_format()


def test_install_language_success() -> None:
    assert ".madeup" not in languages.extension_to_language_id
    assert "madeup" not in languages.language_id_to_scope
    assert "source.madeup" not in languages.scope_to_grammar

    grammar = MockGrammar("source.madeup", "")
    install_language(
        language_id="madeup",
        extensions=[".madeup"],
        grammar=grammar)

    assert languages.extension_to_language_id[".madeup"] == "madeup"
    assert languages.language_id_to_scope["madeup"] == "source.madeup"
    assert languages.scope_to_grammar["source.madeup"] == grammar


def test_install_language_override() -> None:
    assert ".c" in languages.extension_to_language_id
    assert "c" in languages.language_id_to_scope
    assert "source.c" in languages.scope_to_grammar

    grammar = MockGrammar("source.madeup", "")

    with pytest.raises(ValueError):
        install_language(
            language_id="c",
            extensions=[".madeup"],
            grammar=grammar)

    with pytest.raises(ValueError):
        install_language(
            language_id="madeup",
            extensions=[".c"],
            grammar=grammar)

    with pytest.raises(ValueError):
        install_language(
            language_id="madeup",
            extensions=[".madeup"],
            grammar=MockGrammar("source.c", ""))

    install_language(
        language_id="c",
        extensions=[".madeup"],
        grammar=grammar,
        allow_override=True)

    assert languages.language_id_to_scope["c"] == "source.madeup"
