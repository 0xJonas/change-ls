import asyncio
import warnings
from pathlib import Path
from types import TracebackType
from typing import Callable, Dict, List, Optional, Sequence, Type

import lspscript.text_document as td

from .client import (Client, ServerLaunchParams, WorkspaceRequestHandler,
                     get_default_initialize_params)
from .types.structures import (ConfigurationParams, DidOpenTextDocumentParams,
                               InitializeParams, LSPAny,
                               PublishDiagnosticsParams, WorkspaceFolder)

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
        self._roots = [p.resolve() for p in roots]
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

    def _resolve_path_in_workspace(self, path: Path) -> Path:
        if path.is_absolute():
            if not any(_path_is_relative_to(path, root) for root in self._roots):
                warnings.warn(f"File '{str(path)}' is not part of any workspace root.")
            return path.resolve()
        else:
            full_paths = [(root / path) for root in self._roots]
            existing_paths = [p for p in full_paths if p.exists()]
            if len(existing_paths) == 0:
                raise FileNotFoundError(f"File not found in workspace: '{str(path)}'")
            if len(existing_paths) > 1:
                raise FileNotFoundError(
                    f"Path is ambiguous in workspace: '{str(path)}' can be any of {[str(p) for p in existing_paths]}")
            return existing_paths[0].resolve()

    def open_text_document(self, path: Path, *, encoding: Optional[str] = None, language_id: Optional[str] = None) -> "td.TextDocument":
        """
        Opens a :class:`TextDocument` from this :class:`Workspace`.

        When ``open_text_document`` is called with the path of a document that is currently open, the call will return the existing instance.
        ``TextDocuments`` keep a reference count, so each document needs to be closed the same number of times it has been opened.

        :param path: The :class:`Path` from which to load the document. If this is an absolute path, it is opened directly, although a warning will be
            issued, if the path is not actually part of one of the workspace roots. If ``path`` is a relative path, it is combined with each workspace
            root and checked if the resulting full path points to an existing file. If no file or more than one file is found this way, a ``FileNotFoundError``
            will be raised.
        :param encoding: The encoding of the document. If ``encoding`` is ``None``, :func:`locale.getencoding` is used, similar to Python's :func:`open`.
        :param language_id: The language id of the document. If this is not given, it is guessed from the file extension.
        """

        full_path = self._resolve_path_in_workspace(path)
        uri = full_path.as_uri()

        if text_document := self._opened_text_documents.get(uri):
            if encoding is not None and encoding != text_document.encoding:
                raise ValueError(f"Textdocument {path} was already opened with encoding {text_document.encoding}.")
            if language_id is not None and language_id != text_document.language_id:
                raise ValueError(
                    f"Textdocument {path} was already opened with language_id {text_document.language_id}.")

            text_document._reopen()  # type: ignore
            return text_document

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
