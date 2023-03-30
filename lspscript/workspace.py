import warnings
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence

from lspscript.text_document import TextDocument

from .client import _ServerLaunchParams  # type: ignore
from .client import (Client, WorkspaceRequestHandler,
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
    _roots: List[Path]
    _root_names: List[str]
    _clients: Dict[str, Client]
    _configuration_provider: Optional[ConfigurationProvider]

    def __init__(self, *roots: Path, names: Optional[Sequence[str]] = None) -> None:
        self._roots = [p.resolve() for p in roots]
        if names:
            self._root_names = list(names)
        else:
            self._root_names = [r.stem for r in roots]
        self._clients = {}
        self._configuration_provider = None

    def _get_workspace_folders(self) -> List[WorkspaceFolder]:
        return [WorkspaceFolder(uri=path.as_uri(), name=name) for path, name in zip(self._roots, self._root_names)]

    def launch_client(self, params: _ServerLaunchParams, name: Optional[str] = None, initialize_params: Optional[InitializeParams] = None) -> Client:
        if not initialize_params:
            initialize_params = get_default_initialize_params()
        initialize_params.workspaceFolders = self._get_workspace_folders()
        client = Client(params, initialize_params, name)
        self._register_client(client)
        return client

    def _register_client(self, client: Client) -> None:
        """
        Registers an existing `Client` with this `Workspace`.
        """
        name = client.get_name()
        if name in self._clients.values():
            raise ValueError(
                f"A Client with the same name '{name}' was already registered with this Workspace")

        self._clients[name] = client
        client.set_workspace_request_handler(self)

    def set_configuration_provider(self, configuration_provider: Optional[ConfigurationProvider]) -> None:
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

    def open_text_document(self, path: Path, client_names: Optional[List[str]] = None, *, encoding: Optional[str] = None, language_id: Optional[str] = None) -> TextDocument:
        """
        Opens a `TextDocument` from this `Workspace`.
        """
        if client_names is None:
            client_names = list(self._clients.keys())
        clients = {name: self._clients[name] for name in client_names}

        full_path = self._resolve_path_in_workspace(path)
        text_document = TextDocument(full_path, clients, language_id, 0, encoding)

        for client in clients.values():
            if not client.check_feature("textDocument/didOpen", text_documents=[text_document]):
                continue
            client.send_text_document_did_open(DidOpenTextDocumentParams(textDocument=text_document))

        return text_document

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
