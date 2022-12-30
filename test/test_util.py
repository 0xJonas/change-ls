from pathlib import Path

from lspscript.types.enumerations import FileOperationPatternKind
from lspscript.types.structures import (FileOperationFilter,
                                        FileOperationPattern,
                                        FileOperationPatternOptions,
                                        TextDocumentFilter)
from lspscript.util import (matches_file_operation_filter,
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
