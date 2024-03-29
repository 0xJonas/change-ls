import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Generator, Optional, Type

import pytest

from change_ls import StdIOConnectionParams, Workspace


@pytest.fixture
def scratch_workspace_path() -> Generator[Path, Any, None]:
    scratch_path = Path("./.temp/mock-ws-1/")
    shutil.copytree(Path("./test/mock-ws-1/"), scratch_path)
    shutil.copytree(Path("./test/mock-ws-1/"), scratch_path / Path("copy1"))
    shutil.copytree(Path("./test/mock-ws-1/"), scratch_path / Path("copy2"))
    yield scratch_path
    shutil.rmtree(scratch_path)


@dataclass
class FileCreateInput:
    test_sequence: str
    path: Path
    overwrite: bool
    ignore_if_exists: bool
    open_document: bool


@dataclass
class FileCreateExpectation:
    raises: Optional[Type[Exception]]
    document_empty: bool


@pytest.mark.parametrize(
    ["input", "expectation"],
    [
        (
            FileCreateInput(
                "./test/file_operations/test_create_file.json",
                Path("temp_doc.py"),
                False,
                False,
                False,
            ),
            FileCreateExpectation(None, True),
        ),
        (
            FileCreateInput("./test/test_empty.json", Path("test-1.py"), False, False, False),
            FileCreateExpectation(FileExistsError, False),
        ),
        (
            FileCreateInput(
                "./test/file_operations/test_scratch_document_open_close.json",
                Path("test-1.py"),
                False,
                True,
                False,
            ),
            FileCreateExpectation(None, False),
        ),
        (
            FileCreateInput(
                "./test/file_operations/test_create_file_overwrite.json",
                Path("test-1.py"),
                True,
                False,
                False,
            ),
            FileCreateExpectation(None, True),
        ),
        (
            FileCreateInput(
                "./test/file_operations/test_create_file_overwrite_open.json",
                Path("test-1.py"),
                True,
                False,
                True,
            ),
            FileCreateExpectation(None, True),
        ),
    ],
)
async def test_file_create(
    scratch_workspace_path: Path, input: FileCreateInput, expectation: FileCreateExpectation
) -> None:
    file_path = scratch_workspace_path / input.path
    existing_path = file_path.exists()

    async with Workspace(scratch_workspace_path) as ws:
        params = StdIOConnectionParams(
            launch_command=f"node ./mock-server/out/index.js --stdio {input.test_sequence}"
        )
        client = await ws.launch_client(params)
        workspace_uri = scratch_workspace_path.resolve().as_uri()
        await client.send_request(
            "$/setTemplateParams", {"expand": {"WORKSPACE_URI": workspace_uri}}
        )

        open_doc = None
        if input.open_document:
            open_doc = ws.open_text_document(input.path)

        if expectation.raises is not None:
            with pytest.raises(expectation.raises):
                await ws.create_text_document(
                    input.path, overwrite=input.overwrite, ignore_if_exists=input.ignore_if_exists
                )
            return

        doc = await ws.create_text_document(
            input.path, overwrite=input.overwrite, ignore_if_exists=input.ignore_if_exists
        )

        if not file_path.exists():
            assert False

        if open_doc is not None:
            assert open_doc is doc

        if expectation.document_empty:
            assert doc.text == ""

    if not existing_path:
        file_path.unlink()


@dataclass
class FileRenameInput:
    test_sequence: str
    source: Path
    destination: Path
    overwrite: bool
    ignore_if_exists: bool
    open_source: bool
    open_destination: bool


@dataclass
class FileRenameExpectation:
    raises: Optional[Type[Exception]]
    destination_content: str


@pytest.mark.parametrize(
    ["input", "expectation"],
    [
        (
            FileRenameInput(
                "./test/file_operations/test_rename_file.json",
                Path("test-1.py"),
                Path("destination.py"),
                False,
                False,
                False,
                False,
            ),
            FileRenameExpectation(None, 'print("Hello, World!")\n'),
        ),
        (
            FileRenameInput(
                "./test/file_operations/test_rename_file_error.json",
                Path("test-1.py"),
                Path("test-2.py"),
                False,
                False,
                False,
                False,
            ),
            FileRenameExpectation(FileExistsError, ""),
        ),
        (
            FileRenameInput(
                "./test/file_operations/test_scratch_document_open_close.json",
                Path("test-2.py"),
                Path("test-1.py"),
                False,
                True,
                False,
                False,
            ),
            FileRenameExpectation(None, 'print("Hello, World!")\n'),
        ),
        (
            FileRenameInput(
                "test/file_operations/test_rename_file_overwrite.json",
                Path("test-1.py"),
                Path("test-2.py"),
                True,
                False,
                False,
                False,
            ),
            FileRenameExpectation(None, 'print("Hello, World!")\n'),
        ),
        (
            FileRenameInput(
                "test/file_operations/test_rename_file_overwrite_open.json",
                Path("test-1.py"),
                Path("test-2.py"),
                True,
                False,
                True,
                True,
            ),
            FileRenameExpectation(None, 'print("Hello, World!")\n'),
        ),
    ],
)
async def test_file_rename(
    scratch_workspace_path: Path, input: FileRenameInput, expectation: FileRenameExpectation
) -> None:
    source_path = scratch_workspace_path / input.source
    destination_path = scratch_workspace_path / input.destination

    async with Workspace(scratch_workspace_path) as ws:
        params = StdIOConnectionParams(
            launch_command=f"node ./mock-server/out/index.js --stdio {input.test_sequence}"
        )
        client = await ws.launch_client(params)
        workspace_uri = scratch_workspace_path.resolve().as_uri()
        await client.send_request(
            "$/setTemplateParams", {"expand": {"WORKSPACE_URI": workspace_uri}}
        )

        source_doc = None
        if input.open_source:
            source_doc = ws.open_text_document(input.source, encoding="utf-8")

        destination_doc = None
        if input.open_destination:
            destination_doc = ws.open_text_document(input.destination, encoding="utf-8")

        if expectation.raises is not None:
            with pytest.raises(expectation.raises):
                await ws.rename_text_document(
                    input.source,
                    input.destination,
                    overwrite=input.overwrite,
                    ignore_if_exists=input.ignore_if_exists,
                )
            return

        await ws.rename_text_document(
            input.source,
            input.destination,
            overwrite=input.overwrite,
            ignore_if_exists=input.ignore_if_exists,
        )

        if destination_path.exists():
            assert source_path.exists() == input.ignore_if_exists
        assert destination_path.exists()

        if source_doc:
            assert source_doc.uri == destination_path.resolve().as_uri()
        if destination_doc:
            assert destination_doc.is_closed()

        doc = ws.open_text_document(input.destination)
        if input.open_source:
            assert doc is source_doc
        assert doc.text == expectation.destination_content


@dataclass
class DirectoryRenameInput:
    test_sequence: str
    source: Path
    destination: Path
    overwrite: bool
    ignore_if_exists: bool
    open_source_path: Optional[Path]
    source_new_path: Optional[Path]
    open_destination_path: Optional[Path]


@dataclass
class DirectoryRenameExpectation:
    raises: Optional[Type[Exception]]


@pytest.mark.parametrize(
    ["input", "expectation"],
    [
        (
            DirectoryRenameInput(
                "./test/file_operations/test_rename_directory.json",
                Path("./copy1/"),
                Path("./new/"),
                False,
                False,
                None,
                None,
                None,
            ),
            DirectoryRenameExpectation(None),
        ),
        (
            DirectoryRenameInput(
                "./test/test_empty.json",
                Path("./copy1/"),
                Path("./test-1.py"),
                True,
                False,
                None,
                None,
                None,
            ),
            DirectoryRenameExpectation(NotADirectoryError),
        ),
        (
            DirectoryRenameInput(
                "./test/test_empty.json",
                Path("./copy1/"),
                Path("./copy2/"),
                False,
                False,
                None,
                None,
                None,
            ),
            DirectoryRenameExpectation(FileExistsError),
        ),
        (
            DirectoryRenameInput(
                "./test/file_operations/test_rename_directory_overwrite_open.json",
                Path("./copy1/"),
                Path("./copy2/"),
                True,
                False,
                Path("./copy1/test-1.py"),
                Path("./copy2/test-1.py"),
                Path("./copy2/test-1.py"),
            ),
            DirectoryRenameExpectation(None),
        ),
        (
            DirectoryRenameInput(
                "./test/test_empty.json",
                Path("./copy1/"),
                Path("./copy2/"),
                False,
                True,
                None,
                None,
                None,
            ),
            DirectoryRenameExpectation(None),
        ),
    ],
)
async def test_rename_directory(
    scratch_workspace_path: Path,
    input: DirectoryRenameInput,
    expectation: DirectoryRenameExpectation,
) -> None:
    source_path = scratch_workspace_path / input.source
    destination_path = scratch_workspace_path / input.destination

    async with Workspace(scratch_workspace_path) as ws:
        params = StdIOConnectionParams(
            launch_command=f"node ./mock-server/out/index.js --stdio {input.test_sequence}"
        )
        client = await ws.launch_client(params)
        workspace_uri = scratch_workspace_path.resolve().as_uri()
        await client.send_request(
            "$/setTemplateParams", {"expand": {"WORKSPACE_URI": workspace_uri}}
        )

        source_doc = None
        if input.open_source_path:
            source_doc = ws.open_text_document(input.open_source_path, encoding="utf-8")

        destination_doc = None
        if input.open_destination_path:
            destination_doc = ws.open_text_document(input.open_destination_path, encoding="utf-8")

        if expectation.raises is not None:
            with pytest.raises(expectation.raises):
                await ws.rename_directory(
                    input.source,
                    input.destination,
                    overwrite=input.overwrite,
                    ignore_if_exists=input.ignore_if_exists,
                )
            return

        await ws.rename_directory(
            input.source,
            input.destination,
            overwrite=input.overwrite,
            ignore_if_exists=input.ignore_if_exists,
        )

        if destination_path.exists():
            assert source_path.exists() == input.ignore_if_exists
        assert destination_path.exists()

        if source_doc and input.source_new_path:
            assert (
                source_doc.uri
                == (scratch_workspace_path / input.source_new_path).resolve().as_uri()
            )
        if destination_doc:
            assert destination_doc.is_closed()

        if input.open_source_path and input.source_new_path:
            doc = ws.open_text_document(input.source_new_path)
            assert doc is source_doc


@dataclass
class DeleteFileInput:
    test_sequence: str
    path: Path
    ignore_if_not_exists: bool
    open_document: bool


@dataclass
class DeleteFileExpectation:
    raises: Optional[Type[Exception]]


@pytest.mark.parametrize(
    ["input", "expectation"],
    [
        (
            DeleteFileInput(
                "test/file_operations/test_delete_file.json", Path("test-1.py"), False, False
            ),
            DeleteFileExpectation(None),
        ),
        (
            DeleteFileInput(
                "test/file_operations/test_delete_file_open.json", Path("test-1.py"), False, True
            ),
            DeleteFileExpectation(None),
        ),
        (
            DeleteFileInput("test/test_empty.json", Path("does_not_exist.py"), False, False),
            DeleteFileExpectation(FileNotFoundError),
        ),
        (
            DeleteFileInput("test/test_empty.json", Path("does_not_exist.py"), True, False),
            DeleteFileExpectation(None),
        ),
    ],
)
async def test_delete_file(
    scratch_workspace_path: Path, input: DeleteFileInput, expectation: DeleteFileExpectation
) -> None:
    async with Workspace(scratch_workspace_path) as ws:
        params = StdIOConnectionParams(
            launch_command=f"node ./mock-server/out/index.js --stdio {input.test_sequence}"
        )
        client = await ws.launch_client(params)
        workspace_uri = scratch_workspace_path.resolve().as_uri()
        await client.send_request(
            "$/setTemplateParams", {"expand": {"WORKSPACE_URI": workspace_uri}}
        )

        doc = None
        if input.open_document:
            doc = ws.open_text_document(input.path)

        if expectation.raises:
            with pytest.raises(expectation.raises):
                await ws.delete_text_document(
                    input.path, ignore_if_not_exists=input.ignore_if_not_exists
                )
            return

        await ws.delete_text_document(input.path, ignore_if_not_exists=input.ignore_if_not_exists)

        if not input.ignore_if_not_exists:
            assert not input.path.exists()
        if doc:
            assert doc.is_closed()


@dataclass
class DeleteDirectoryInput:
    test_sequence: str
    path: Path
    ignore_if_not_exists: bool
    recursive: bool
    open_document_path: Optional[Path]


@dataclass
class DeleteDirectoryExpectation:
    raises: Optional[Type[Exception]]


@pytest.mark.parametrize(
    ["input", "expectation"],
    [
        (
            DeleteDirectoryInput(
                "test/file_operations/test_delete_directory_recursive.json",
                Path("./copy1/"),
                False,
                True,
                None,
            ),
            DeleteDirectoryExpectation(None),
        ),
        (
            DeleteDirectoryInput("test/test_empty.json", Path("./copy1/"), False, False, None),
            DeleteDirectoryExpectation(FileExistsError),
        ),
        (
            DeleteDirectoryInput("test/test_empty.json", Path("./nothing/"), True, False, None),
            DeleteDirectoryExpectation(None),
        ),
        (
            DeleteDirectoryInput(
                "test/file_operations/test_delete_directory_recursive_open.json",
                Path("./copy1/"),
                False,
                True,
                Path("./copy1/test-1.py"),
            ),
            DeleteDirectoryExpectation(None),
        ),
    ],
)
async def test_delete_directory(
    scratch_workspace_path: Path,
    input: DeleteDirectoryInput,
    expectation: DeleteDirectoryExpectation,
) -> None:
    async with Workspace(scratch_workspace_path) as ws:
        params = StdIOConnectionParams(
            launch_command=f"node ./mock-server/out/index.js --stdio {input.test_sequence}"
        )
        client = await ws.launch_client(params)
        workspace_uri = scratch_workspace_path.resolve().as_uri()
        await client.send_request(
            "$/setTemplateParams", {"expand": {"WORKSPACE_URI": workspace_uri}}
        )

        doc = None
        if input.open_document_path:
            doc = ws.open_text_document(input.open_document_path)

        if expectation.raises:
            with pytest.raises(expectation.raises):
                await ws.delete_directory(
                    input.path,
                    recursive=input.recursive,
                    ignore_if_not_exists=input.ignore_if_not_exists,
                )
            return

        await ws.delete_directory(
            input.path, recursive=input.recursive, ignore_if_not_exists=input.ignore_if_not_exists
        )

        if not input.ignore_if_not_exists:
            assert not input.path.exists()
        if doc:
            assert doc.is_closed()
