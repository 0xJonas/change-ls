import asyncio
import os.path
import warnings
from pathlib import Path
from types import TracebackType
from typing import Callable, Dict, List, Optional, Sequence, Tuple, Type, Union
from urllib.parse import urlsplit

import lspscript.text_document as td
from lspscript.lsp_exception import LSPScriptException

from .client import (Client, ServerLaunchParams, WorkspaceRequestHandler,
                     get_default_initialize_params)
from .types.structures import (ConfigurationParams, CreateFile,
                               CreateFilesParams, DeleteFilesParams,
                               DidOpenTextDocumentParams, FileCreate,
                               FileDelete, FileRename, InitializeParams,
                               LSPAny, PublishDiagnosticsParams, RenameFile,
                               RenameFilesParams, TextDocumentEdit, TextEdit,
                               WorkspaceEdit, WorkspaceFolder)

ConfigurationProvider = Callable[[Optional[str], Optional[str]], LSPAny]


def _path_is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


class Workspace(WorkspaceRequestHandler):
    """
    A :class:`Workspace` contains one or more workspace roots and provides access to the roots' files,
    as well as managing Language Servers for these files.

    A ``Workspace`` is a context manager. If a ``Workspace`` is used with a ``with`` statement, all resources
    associated with the ``Workspace`` will be closed when exiting the block. This includes all opened
    :class:`TextDocuments <TextDocument>` and all started :class:`Clients <Client>`::

        async with Workspace(Path("...")) as ws:
            params = StdIOConnectionParams(...)
            await ws.launch_client(params)
            doc = ws.open_text_document(Path(...))
            # ...

    ``Clients`` and
    ``TextDocuments`` are also context managers themselves, if you need a more fine-grained control over
    resources.

    :param roots: The :class:`Paths <pathlib.Path>` to the roots of the workspace. The ``Paths`` must be directories.
    :param names: An optional list of names for the workspace roots. If given, there must be a name for each root.
    """

    _roots: List[Path]
    _root_names: List[str]
    _clients: Dict[str, Client]
    _configuration_provider: Optional[ConfigurationProvider]
    _opened_text_documents: Dict[str, "td.TextDocument"]

    def __init__(self, *roots: Path, names: Optional[Sequence[str]] = None) -> None:
        # pathlib.Path.resolve() does not work correctly on windows, so
        # we use abspath in addition to resolve to deal with both making
        # the path absolute and resolving symlinks. Also, it gets us
        # a consistent casing for drive letters.
        self._roots = [Path(os.path.abspath(p)).resolve() for p in roots]
        if names:
            self._root_names = list(names)
        else:
            self._root_names = [r.stem for r in roots]
        self._clients = {}
        self._configuration_provider = None
        self._opened_text_documents = {}

    def _get_workspace_folders(self) -> List[WorkspaceFolder]:
        return [WorkspaceFolder(uri=path.as_uri(), name=name) for path, name in zip(self._roots, self._root_names)]

    def create_client(self, params: ServerLaunchParams, name: Optional[str] = None, initialize_params: Optional[InitializeParams] = None) -> Client:
        """
        Like :meth:`launch_client`, but does not immediately start the underlying language server.
        """
        if not initialize_params:
            initialize_params = get_default_initialize_params()
        initialize_params.workspaceFolders = self._get_workspace_folders()
        client = Client(params, initialize_params, name)
        self._register_client(client)
        return client

    async def launch_client(self, params: ServerLaunchParams, name: Optional[str] = None, initialize_params: Optional[InitializeParams] = None) -> Client:
        """
        Creates a :class:`Client` associated with this :class:`Workspace`, which manages a language server.
        The underlying language server is started immediatly, so the returned ``Client`` will be in the ``"running"`` state.

        :param params: The :class:`ServerLaunchParams` which will be used to start the language server.
        :param name: The name for the language server. This name can later be used to reference the server started by the returned ``Client``.
            If no name is given, a name will be automatically generated.
        :param initialize_params: The :class:`InitializeParams` which should be used to start the server. If no parameters are given,
            the value returned from :func:`get_default_initialize_params()` is used.
        """
        client = self.create_client(params, name, initialize_params)
        await client.__aenter__()
        return client

    def _register_client(self, client: Client) -> None:
        def send_did_open_notifications() -> None:
            for doc in self._opened_text_documents.values():
                if not client.check_feature("textDocument/didOpen", text_documents=[doc]):
                    continue
                client.send_text_document_did_open(DidOpenTextDocumentParams(textDocument=doc))

        def unregister_client() -> None:
            client.set_workspace_request_handler(None)
            del self._clients[client.get_name()]

        name = client.get_name()
        if name in self._clients.values():
            raise ValueError(f"A Client with the same name '{name}' was already registered with this Workspace")

        self._clients[name] = client
        client.set_workspace_request_handler(self)
        client.register_state_callback("running", send_did_open_notifications)
        client.register_state_callback("disconnected", unregister_client)

    @property
    def clients(self) -> Dict[str, Client]:
        return self._clients

    def set_configuration_provider(self, configuration_provider: Optional[ConfigurationProvider]) -> None:
        """
        Sets the :data:`ConfigurationProvider` for this :class:`Workspace`.

        The ``ConfigurationProvider`` manages any configurations that a language server might need.

        :param configuration_provider: The ``ConfigurationProvider`` to be used. Can be ``None`` to clear
            the current provider.
        """
        self._configuration_provider = configuration_provider

    def _check_roots_for_path(self, path: Path) -> None:
        if not any(_path_is_relative_to(path, root) for root in self._roots):
            warnings.warn(f"File '{str(path)}' is not part of any workspace root.")

    def _resolve_path_in_workspace(self, path: Path) -> Path:
        if path.is_absolute():
            self._check_roots_for_path(path)
            return path.resolve()
        elif len(self._roots) == 1:
            return (self._roots[0] / path).resolve()
        else:
            full_paths = [(root / path) for root in self._roots]
            existing_paths = [p for p in full_paths if p.exists()]
            if len(existing_paths) == 0:
                raise FileNotFoundError(
                    f"Relative path is ambiguous in workspace: '{str(path)}' is not found under any of the roots.")
            if len(existing_paths) > 1:
                raise FileNotFoundError(
                    f"Relative path is ambiguous in workspace: '{str(path)}' can be any of {[str(p) for p in existing_paths]}")
            return existing_paths[0].resolve()

    def _normalize_path_parameter(self, path: Union[Path, str]) -> Tuple[Path, str]:
        """
        Used to convert the value passed to :meth:`open_text_document` and
        :meth:`rename_text_document` into a tuple with a :class:`pathlib.Path` and a URI.
        """
        if isinstance(path, Path):
            full_path = self._resolve_path_in_workspace(path)
            uri = full_path.as_uri()
        else:
            # This also takes care of string paths
            (_, _, path_component, _, _) = urlsplit(path, scheme="file")
            if len(path_component) >= 3 and path_component[2] == ":":
                # Uris which originate from windows paths have a '/' before the
                # drive letter and are not recognized as absolute paths. So if we
                # detect that the first segment is a drive, we remove the leading
                # '/' so path is actually absolute.
                path_component = path_component[1:]

            full_path = self._resolve_path_in_workspace(Path(path_component))
            uri = path

        return (full_path, uri)

    def open_text_document(self, path: Union[Path, str], *, encoding: Optional[str] = None, language_id: Optional[str] = None) -> "td.TextDocument":
        """
        Opens a :class:`TextDocument` from this :class:`Workspace`.

        When ``open_text_document`` is called with the path of a document that is currently open, the call will return the existing instance.
        ``TextDocuments`` keep a reference count, so each document needs to be closed the same number of times it has been opened.

        :param path: The path from which to load the document. This can either be :class:`pathlib.Path`, or an ``str`` path or uri.

            If this is an absolute path, it is opened directly, although a warning will be issued, if the path is not actually part
            of one of the workspace roots. If ``path`` is a relative path, it is combined with each workspace root and checked if the
            resulting full path points to an existing file. If no file or more than one file is found this way, a ``FileNotFoundError``
            will be raised.
        :param encoding: The character encoding of the document. If ``encoding`` is ``None``, :func:`locale.getencoding()` is used,
            similar to Python's :func:`open`.
        :param language_id: The language id of the document. If this is not given, it is guessed from the file extension.
        """

        full_path, uri = self._normalize_path_parameter(path)

        if text_document := self._opened_text_documents.get(uri):
            if encoding is not None and encoding != text_document.encoding:
                raise ValueError(f"Textdocument {path} was already opened with encoding {text_document.encoding}.")
            if language_id is not None and language_id != text_document.language_id:
                raise ValueError(
                    f"Textdocument {path} was already opened with language_id {text_document.language_id}.")

            text_document._reopen()  # type: ignore
            return text_document

        if not full_path.exists():
            raise FileNotFoundError(f"File not found in workspace: '{str(path)}'")

        text_document = td.TextDocument(full_path, self, language_id, 0, encoding)

        for client in self._clients.values():
            if not client.check_feature("textDocument/didOpen", text_documents=[text_document]):
                continue
            client.send_text_document_did_open(DidOpenTextDocumentParams(textDocument=text_document))

        self._opened_text_documents[uri] = text_document
        return text_document

    async def __aenter__(self) -> "Workspace":
        return self

    async def __aexit__(self, exc_type: Type[Exception], exc_value: Exception, traceback: TracebackType) -> bool:
        for doc in list(reversed(self._opened_text_documents.values())):
            doc._final_close()  # type: ignore
        self._opened_text_documents = {}

        futures = [client.__aexit__(exc_type, exc_value, traceback)
                   for client in list(reversed(self._clients.values()))]
        await asyncio.gather(*futures)
        self._clients = {}

        return False

    def _get_client(self, client_name: Optional[str]) -> Client:
        if not client_name:
            if len(self._clients) == 1:
                return list(self._clients.values())[0]
            else:
                raise ValueError("Unable to identify Client without a name.")
        return self._clients[client_name]

    async def _perform_text_document_edits(self, uri: str, edits: List[TextEdit], version: Optional[int] = None) -> None:
        with self.open_text_document(uri) as doc:
            if version is not None and doc.version != version:
                raise LSPScriptException(
                    f"Encountered edit for version {version} of {doc.uri}, but the current version is {doc.version}")
            if len(doc._pending_edits) > 0:  # type: ignore
                raise LSPScriptException(
                    f"Edit cannot be applied, because TextDocument {doc.uri} has uncommitted edits.")

            for edit in edits:
                doc.push_text_edit(edit)
            doc.commit_edits()
            await doc.save()

    async def perform_edit_and_save(self, edit: WorkspaceEdit) -> None:
        """
        Perform the edits described by the given :class:`WorkspaceEdit` and save the affected
        :class:`TextDocuments <TextDocument>`.

        Because edits inside a ``Workspace`` edit may depend on each other, the edits are committed immediately
        (see :meth:`TextDocument.commit_edits()`). Because edits may affect opened as well as unopened ``TextDocuments``
        all affected documents are saved after the changes are made to ensure a consistent behavior
        (see :meth:`TextDocument.save()`). ``TextDocuments`` must not have any uncommitted edits when this method is
        called.

        :param edit: The :class:`WorkspaceEdit` to perform.
        """
        if edit.changes is not None and edit.documentChanges is not None:
            raise ValueError("Only one of WorkspaceEdit.changes and WorkspaceEdit.documentChanges may be set.")

        if edit.documentChanges:
            for action in edit.documentChanges:
                if isinstance(action, TextDocumentEdit):
                    await self._perform_text_document_edits(action.textDocument.uri, action.edits, action.textDocument.version)
                elif isinstance(action, CreateFile):
                    overwrite = bool(action.options and action.options.overwrite)
                    ignore_if_exists = bool(action.options and action.options.ignoreIfExists)
                    await self._handle_create_file(action.uri, overwrite, ignore_if_exists)
                elif isinstance(action, RenameFile):
                    overwrite = bool(action.options and action.options.overwrite)
                    ignore_if_exists = bool(action.options and action.options.ignoreIfExists)
                    await self.rename_text_document(action.oldUri, action.newUri, overwrite=overwrite, ignore_if_exists=ignore_if_exists)
                else:
                    recursive = bool(action.options and action.options.recursive)
                    ignore_if_not_exists = bool(action.options and action.options.ignoreIfNotExists)
                    await self._handle_delete_file(action.uri, recursive, ignore_if_not_exists)

        elif edit.changes:
            for path, edits in edit.changes.items():
                await self._perform_text_document_edits(path, edits)

    async def _send_will_create_file_requests(self, uri: str) -> None:
        params = CreateFilesParams(files=[FileCreate(uri=uri)])
        for client in self.clients.values():
            if not client.check_feature("workspace/willCreateFiles", file_operations=[uri]):
                continue
            edit = await client.send_workspace_will_create_files(params)
            if edit:
                await self.perform_edit_and_save(edit)

    def _send_did_create_file_notifications(self, uri: str) -> None:
        params = CreateFilesParams(files=[FileCreate(uri=uri)])
        for client in self.clients.values():
            if not client.check_feature("workspace/didCreateFiles", file_operations=[uri]):
                continue
            client.send_workspace_did_create_files(params)

    async def _handle_create_file(self, path: Union[Path, str], overwrite: bool, ignore_if_exists: bool) -> None:
        full_path, _ = self._normalize_path_parameter(path)
        if full_path.exists() and not overwrite:
            if ignore_if_exists:
                return
            else:
                raise FileExistsError()

        uri = full_path.as_uri()
        text_document = self._opened_text_documents.get(uri)

        await self._send_will_create_file_requests(uri)

        if overwrite and text_document:
            # 'Creating' and overwriting an already exisiting file is simply clearing its contents.
            text_document.delete(0, len(text_document.text))
            text_document.commit_edits()
            await text_document.save()
        else:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.unlink(missing_ok=True)
            full_path.touch(exist_ok=False)

        self._send_did_create_file_notifications(uri)

    async def create_text_document(self, path: Union[Path, str], *, overwrite: bool = False, ignore_if_exists: bool = False, encoding: Optional[str] = None, language_id: Optional[str] = None) -> "td.TextDocument":
        """
        Creates a new :class:`TextDocument` and opens it. Any required directories which do not already
        exist will be created as well.

        :param path: The path of the document which should be created. This can either be :class:`pathlib.Path`,
            or an ``str`` path or uri. If the workspace has multiple roots, the path must be absolute.
        :param overwrite: Whether to overwrite an existing file. If ``overwrite`` is ``True`` and the file was already opened,
            the returned ``TextDocument`` will be the existing instance and will have its contents cleared. This has the limitation
            that ``language_id`` and ``encoding`` cannot be changed this way. If both ``overwrite`` and ``ignore_if_exists`` are
            given, ``overwrite`` takes priority.
        :param ignore_if_exists: Whether an existing file should be opened as-is, without changes to its contents.
        :param encoding: The character encoding of the document. If ``encoding`` is ``None``, :func:`locale.getencoding()`
            is used, similar to Python's :func:`open`.
        :param language_id: The language id of the document. If this is not given, it is guessed from the file extension.
        """
        await self._handle_create_file(path, overwrite, ignore_if_exists)
        return self.open_text_document(path, encoding=encoding, language_id=language_id)

    async def _send_will_rename_requests(self, source_uri: str, destination_uri: str) -> None:
        params = RenameFilesParams(files=[FileRename(oldUri=source_uri, newUri=destination_uri)])
        for client in self.clients.values():
            if not client.check_feature("workspace/willRenameFiles", file_operations=[source_uri]):
                continue
            edit = await client.send_workspace_will_rename_files(params)
            if edit:
                await self.perform_edit_and_save(edit)

    def _send_did_rename_notifications(self, source_uri: str, destination_uri: str) -> None:
        params = RenameFilesParams(files=[FileRename(oldUri=source_uri, newUri=destination_uri)])
        for client in self.clients.values():
            if not client.check_feature("workspace/didRenameFiles", file_operations=[source_uri]):
                continue
            client.send_workspace_did_rename_files(params)

    async def rename_text_document(self, source: Union[Path, str], destination: Union[Path, str], *, overwrite: bool = False, ignore_if_exists: bool = False) -> None:
        """
        Renames a document.

        :param source: The source path that should be renamed. Can be either a :class:`pathlib.Path` or an
            ``str`` path or uri. If this path does not exist, a :class:`FileNotFoundError` is raised.
        :param destination: The path that ``source`` should be renamed to. Can be either a :class:`pathlib.Path` or an
            ``str`` path or uri. If neither ``overwrite`` nor ``ignore_if_exists`` are ``True`` and the path
            already exists, a :class:`FileExistsError` is raised.
        :param overwrite: The destination should be overwritten if it already exists. If both ``overwrite`` and
            ``ignore_if_exists`` are given, ``overwrite`` takes priority.
        :param ignore_if_exists: If the destination already exists, no rename should be performed.
        """
        path_source, uri_source = self._normalize_path_parameter(source)
        path_destination, uri_destination = self._normalize_path_parameter(destination)

        if path_source == path_destination:
            return

        if not path_source.exists():
            raise FileNotFoundError()
        elif path_destination.exists() and not overwrite:
            if ignore_if_exists:
                return
            else:
                raise FileExistsError()

        await self._send_will_rename_requests(uri_source, uri_destination)

        source_text_document = self._opened_text_documents.get(uri_source)
        destination_text_document = self._opened_text_documents.get(uri_destination)

        if path_destination.exists():
            if destination_text_document:
                destination_text_document._final_close()  # type: ignore
        if source_text_document:
            source_text_document._set_path(path_destination)  # type: ignore
            self._opened_text_documents[source_text_document.uri] = source_text_document

        # Windows requires the destination file to not exist
        path_destination.unlink(missing_ok=True)
        path_source.rename(path_destination)

        self._send_did_rename_notifications(uri_source, uri_destination)

        return

    async def _send_will_delete_file_requests(self, uri: str) -> None:
        params = DeleteFilesParams(files=[FileDelete(uri=uri)])
        for client in self.clients.values():
            if not client.check_feature("workspace/willDeleteFiles", file_operations=[uri]):
                continue
            edit = await client.send_workspace_will_delete_files(params)
            if edit:
                await self.perform_edit_and_save(edit)

    def _send_did_delete_file_notifications(self, uri: str) -> None:
        params = DeleteFilesParams(files=[FileDelete(uri=uri)])
        for client in self.clients.values():
            if not client.check_feature("workspace/didCreateFiles", file_operations=[uri]):
                continue
            client.send_workspace_did_delete_files(params)

    def _delete_directory_recursive(self, path: Path) -> None:
        for item in path.iterdir():
            if item.is_dir():
                self._delete_directory_recursive(item)
            elif item.is_symlink():
                item.unlink()
            else:
                uri = item.as_uri()
                document = self._opened_text_documents.get(uri)
                if document:
                    document._final_close()  # type: ignore
                item.unlink()
        path.rmdir()

    async def _handle_delete_file(self, path: Union[Path, str], recursive: bool, ignore_if_not_exists: bool, *, expect_directory: bool = False) -> None:
        full_path, uri = self._normalize_path_parameter(path)

        if not full_path.exists():
            if ignore_if_not_exists:
                return
            else:
                raise FileNotFoundError()

        is_directory = full_path.is_dir()
        if expect_directory and not is_directory:
            raise LSPScriptException(f"{uri} is not a directory.")

        if is_directory and not recursive:
            try:
                next(full_path.iterdir())
                raise LSPScriptException("Attempted to delete a directory which is not empty.")
            except StopIteration:
                pass

        await self._send_will_delete_file_requests(uri)

        if is_directory:
            self._delete_directory_recursive(full_path)
        else:
            doc = self._opened_text_documents.get(uri)
            if doc:
                doc._final_close()  # type: ignore
            full_path.unlink()

        self._send_did_delete_file_notifications(uri)

    async def delete_text_document(self, path: Union[Path, str], *, ignore_if_not_exists: bool = False) -> None:
        """
        Deletes a document from this :class:`Workspace`. If the document is currently open, it will be
        closed automatically.

        :param path: The path of the document to be deleted. Can be either a :class:`pathlib.Path` or an
            ``str`` path or uri.
        :param ignore_if_not_exists: Whether to raise a :class:`FileNotFoundError` if the ``path`` does not exist.
        """
        await self._handle_delete_file(path, False, ignore_if_not_exists)

    async def delete_directory(self, path: Union[Path, str], *, recursive: bool = False, ignore_if_not_exists: bool = False) -> None:
        """
        Deletes a directory from this :class:`Workspace`. Any opened :class:`TextDocuments` which are below ``path``
        will be closed.

        :param path: The path of the document to be deleted. Can be either a :class:`pathlib.Path` or an
            ``str`` path or uri.
        :param recursive: Whether to recursively delete files and subdirectories below ``path``. If this is ``False``,
            then ``path`` must be an empty directory.
        :param ignore_if_not_exists: Whether to raise a :class:`FileNotFoundError` if the ``path`` does not exist.
        """
        await self._handle_delete_file(path, recursive, ignore_if_not_exists, expect_directory=True)

    def on_workspace_folders(self) -> List[WorkspaceFolder]:
        return self._get_workspace_folders()

    def on_configuration(self, params: ConfigurationParams) -> List[LSPAny]:
        if self._configuration_provider:
            return [self._configuration_provider(i.scopeUri, i.section) for i in params.items]
        else:
            return []

    def on_semantic_tokens_refresh(self) -> None:
        # TODO
        pass

    def on_inline_value_refresh(self) -> None:
        # TODO
        pass

    def on_inlay_hint_refresh(self) -> None:
        # TODO
        pass

    def on_diagnostic_refresh(self) -> None:
        # TODO
        pass

    def on_code_lens_refresh(self) -> None:
        # TODO
        pass

    def on_apply_edit(self) -> None:
        # TODO
        pass

    def on_publish_diagnostics(self, params: PublishDiagnosticsParams) -> None:
        # TODO
        pass
