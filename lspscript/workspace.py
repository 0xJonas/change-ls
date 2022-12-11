from pathlib import Path
from typing import Callable, List, Optional, Sequence

from .client import _ServerLaunchParams  # type: ignore
from .client import (Client, WorkspaceRequestHandler,
                     get_default_initialize_params)
from .types.structures import (ConfigurationParams, LSPAny,
                               PublishDiagnosticsParams, WorkspaceFolder)

ConfigurationProvider = Callable[[Optional[str], Optional[str]], LSPAny]


class Workspace(WorkspaceRequestHandler):
    _roots: List[Path]
    _root_names: List[str]
    _clients: List[Client]
    _configuration_provider: Optional[ConfigurationProvider]

    def __init__(self, *roots: Path, names: Optional[Sequence[str]] = None) -> None:
        self._roots = list(roots)
        if names:
            self._root_names = list(names)
        else:
            self._root_names = [r.stem for r in roots]
        self._clients = []
        self._configuration_provider = None

    def _get_workspace_folders(self) -> List[WorkspaceFolder]:
        return [WorkspaceFolder(uri=path.resolve().as_uri(), name=name) for path, name in zip(self._roots, self._root_names)]

    def launch_client(self, params: _ServerLaunchParams, name: Optional[str] = None) -> Client:
        initialize_params = get_default_initialize_params()
        initialize_params.workspaceFolders = self._get_workspace_folders()
        client = Client(params, initialize_params, name)
        self.register_client(client)
        return client

    def register_client(self, client: Client) -> None:
        """
        Registers an existing `Client` with this `Workspace`.
        """
        if client in self._clients:
            raise ValueError(
                "Client was already registered with this Workspace")

        self._clients.append(client)
        client.set_workspace_request_handler(self)

    def unregister_client(self, client: Client) -> None:
        """
        Unregisters an existing `Client` with this `Workspace`.
        """
        if client not in self._clients:
            raise ValueError("Client is not registered with this Workspace")

        client.set_workspace_request_handler(None)
        self._clients.remove(client)

    def set_configuration_provider(self, configuration_provider: Optional[ConfigurationProvider]) -> None:
        self._configuration_provider = configuration_provider

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
