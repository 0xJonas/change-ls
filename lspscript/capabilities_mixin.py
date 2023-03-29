from asyncio import Event, wait_for
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Union

from lspscript.types.enumerations import TextDocumentSyncKind
from lspscript.types.structures import (CodeActionOptions, CodeLensOptions,
                                        CompletionOptions, DiagnosticOptions,
                                        DocumentLinkOptions,
                                        ExecuteCommandOptions,
                                        FileOperationRegistrationOptions,
                                        InlayHintOptions,
                                        NotebookCellTextDocumentFilter,
                                        Registration, SaveOptions,
                                        SemanticTokensOptions,
                                        ServerCapabilities,
                                        TextDocumentSyncOptions,
                                        Unregistration, WorkspaceSymbolOptions)
from lspscript.util import (matches_file_operation_filter,
                            matches_text_document_filter)

from .types.capabilities import (FeatureRegistration,
                                 registration_to_feature_registration,
                                 server_capabilities_to_feature_registrations)


@dataclass
class _FeatureRequest:
    method: str
    params: Dict[str, Any]
    event: Event


_FeatureCheckState = Dict[str, Union[List[bool], bool]]


def _create_feature_check_state(params: Dict[str, Any]) -> _FeatureCheckState:
    out: Dict[str, Union[List[bool], bool]] = {}
    for k in params.keys():
        if isinstance(params[k], Sequence):
            out[k] = [False] * len(params[k])
        else:
            out[k] = False
    return out


def _update_feature_check_state(request_params: Dict[str, Any], state: _FeatureCheckState, registration: FeatureRegistration) -> None:
    if "text_documents" in state and registration.document_selector:
        # TODO does this really need a special member in FeatureRegistration?

        assert isinstance(state["text_documents"], List)

        for i, t in enumerate(request_params["text_documents"]):
            for filter in registration.document_selector:
                if isinstance(filter, NotebookCellTextDocumentFilter):
                    continue

                # TODO language_id
                if matches_text_document_filter(t, filter):
                    state["text_documents"][i] = True
                    break

    if "file_operations" in state and isinstance(registration.options, FileOperationRegistrationOptions):
        assert isinstance(state["file_operations"], List)

        for i, t in enumerate(request_params["file_operations"]):
            for filter in registration.options.filters:
                if matches_file_operation_filter(t, filter):
                    state["file_operations"][i] = True
                    break

    if "semantic_tokens" in state and isinstance(registration.options, SemanticTokensOptions):
        assert isinstance(state["semantic_tokens"], List)

        for i, r in enumerate(request_params["semantic_tokens"]):
            if r == "full" and registration.options.full:
                state["semantic_tokens"][i] = True
            elif r == "full/delta" and isinstance(registration.options.full, Dict) and registration.options.full.get("delta"):
                state["semantic_tokens"][i] = True
            elif r == "range" and registration.options.range:
                state["semantic_tokens"][i] = True

    if "code_actions" in state and isinstance(registration.options, CodeActionOptions):
        assert isinstance(state["code_actions"], List)

        for i, c in enumerate(request_params["code_actions"]):
            if c in registration.options.codeActionKinds:
                state["code_actions"][i] = True

    if "code_action_resolve" in state and isinstance(registration.options, CodeActionOptions):
        if request_params["code_action_resolve"] and registration.options.resolveProvider:
            state["code_action_resolve"] = True

    if "workspace_commands" in state and isinstance(registration.options, ExecuteCommandOptions):
        assert isinstance(state["workspace_commands"], List)

        for i, c in enumerate(request_params["workspace_commands"]):
            if c in registration.options.commands:
                state["workspace_commands"][i] = True

    if "completion_item_resolve" in state and isinstance(registration.options, CompletionOptions):
        if request_params["completion_item_resolve"] and registration.options.resolveProvider:
            state["completion_item_resolve"] = True

    if "completion_item_label_details" in state and isinstance(registration.options, CompletionOptions):
        if request_params["completion_item_label_details"] and registration.options.completionItem and registration.options.completionItem.get("labelDetailsSupport"):
            state["completion_item_label_details"] = True

    if "inlay_hint_resolve" in state and isinstance(registration.options, InlayHintOptions):
        if request_params["inlay_hint_resolve"] and registration.options.resolveProvider:
            state["inlay_hint_resolve"] = True

    if "workspace_diagnostic" in state and isinstance(registration.options, DiagnosticOptions):
        if request_params["workspace_diagnostic"] and registration.options.workspaceDiagnostics:
            state["workspace_diagnostic"] = True

    if "workspace_symbol_resolve" in state and isinstance(registration.options, WorkspaceSymbolOptions):
        if request_params["workspace_symbol_resolve"] and registration.options.resolveProvider:
            state["workspace_symbol_resolve"] = True

    if "code_lens_resolve" in state and isinstance(registration.options, CodeLensOptions):
        if request_params["code_lens_resolve"] and registration.options.resolveProvider:
            state["code_lens_resolve"] = True

    if "document_link_resolve" in state and isinstance(registration.options, DocumentLinkOptions):
        if request_params["document_link_resolve"] and registration.options.resolveProvider:
            state["document_link_resolve"] = True


def _check_feature_check_fulfilled(state: _FeatureCheckState) -> bool:
    # Note: If a state is empty (i.e. when the FeatureRequest does not contain any
    # parameters), this is supposed to return True.
    for k in state.keys():
        val = state[k]
        if isinstance(val, List):
            if not all(val):
                return False
        elif not val:
            return False
    return True


def _text_document_sync_kind_to_options(kind: TextDocumentSyncKind) -> TextDocumentSyncOptions:
    # Is this anywhere in the spec? Taken from https://github.com/microsoft/vscode-languageserver-node/blob/c91c2f89e0a3d8aa8923355a65a2977b2b3d3b57/client/src/common/client.ts#L1168
    if kind is TextDocumentSyncKind.None_:
        return TextDocumentSyncOptions(openClose=False, change=TextDocumentSyncKind.None_)
    else:
        return TextDocumentSyncOptions(openClose=True, change=kind, save=SaveOptions(includeText=False))


def _text_document_sync_options_to_feature_registrations(options: TextDocumentSyncOptions) -> List[FeatureRegistration]:
    out: List[FeatureRegistration] = []

    if options.openClose:
        out.append(FeatureRegistration(None, "textDocument/didOpen", None, options.openClose))
        out.append(FeatureRegistration(None, "textDocument/didClose", None, options.openClose))

    if options.save:
        out.append(FeatureRegistration(None, "textDocument/didSave", None, options.save))
    if options.willSave:
        out.append(FeatureRegistration(None, "textDocument/willSave", None, options.willSave))
    if options.willSaveWaitUntil:
        out.append(FeatureRegistration(None, "textDocument/willSaveWaitUntil", None, options.willSaveWaitUntil))

    return out


class CapabilitiesMixin:
    _registrations: Dict[str, List[FeatureRegistration]]
    _pending_feature_requests: Dict[str, List[_FeatureRequest]]
    _server_capabilities: Optional[ServerCapabilities]

    def __init__(self) -> None:
        self._registrations = {}
        self._pending_feature_requests = {}
        self._server_capabilities = None

    def _set_server_capabilities(self, capabilities: ServerCapabilities) -> None:
        self._server_capabilities = capabilities
        registration_list = server_capabilities_to_feature_registrations(capabilities)

        # A few capabilities cannot be turned into registrations from generated code

        if capabilities.workspace and capabilities.workspace.get("workspaceFolders") and capabilities.workspace["workspaceFolders"].changeNotifications:
            val = capabilities.workspace["workspaceFolders"].changeNotifications
            if type(val) is str:
                registration_list.append(FeatureRegistration(val, "workspace/didChangeWorkspaceFolders", None, None))

        if capabilities.textDocumentSync:
            if isinstance(capabilities.textDocumentSync, TextDocumentSyncKind):
                options = _text_document_sync_kind_to_options(capabilities.textDocumentSync)
            else:
                options = capabilities.textDocumentSync
            registration_list += _text_document_sync_options_to_feature_registrations(options)

        self._registrations = {}
        for r in registration_list:
            if r.method not in self._registrations:
                self._registrations[r.method] = []
            self._registrations[r.method].append(r)

        self._check_pending_feature_requests()

    def _add_dynamic_registration(self, registration: Registration) -> None:
        feature_registration = registration_to_feature_registration(registration)
        if feature_registration.method not in self._registrations:
            self._registrations[feature_registration.method] = []
        self._registrations[feature_registration.method].append(feature_registration)

    def _remove_dynamic_registration(self, unregistration: Unregistration) -> None:
        registrations = self._registrations.get(unregistration.method)
        if not registrations:
            # No registration with that id
            # TODO raise something?
            return

        for i, r in enumerate(registrations):
            if r.id and r.id == unregistration.id:
                del registrations[i]
                return

    def check_feature(self, method: str, **kwargs: Any) -> bool:
        """
        Checks whether the features currently registered by the server can fulfill the
        given feature request.

        - `method` is the *registration* method for the feature (might be different from the request/notification method).
        - Some methods provide a more granular control over the feature. `kwargs` can be used to specify exactly which realization of a feature is requested.
        """

        registrations = self._registrations.get(method)
        if not registrations or len(registrations) == 0:
            return False

        state = _create_feature_check_state(kwargs)

        for r in registrations:
            _update_feature_check_state(kwargs, state, r)

        # If the feature_request contains only a method and nothing else,
        # this will set the event, since at least one registration for that
        # method exists (otherwise we would have already returned).
        if _check_feature_check_fulfilled(state):
            return True
        else:
            return False

    def _check_pending_feature_requests(self) -> None:
        for fs in self._pending_feature_requests.values():
            index = 0
            while index < len(fs):
                if self.check_feature(fs[index].method, **fs[index].params):
                    fs[index].event.set()
                    del fs[index]
                else:
                    index += 1

    async def require_feature(self, method: str, *, timeout: Optional[float] = 10.0, **kwargs: Any) -> None:
        """
        Requires that the language server provides the feature described by `method` and `params`. This
        should be used when a language server registers some of its features dynamically, since the client
        potentially has to wait until the language server is ready to provide the feature.

        - `method` is the *registration* method for the feature (might be different from the request/notification method).
        - Some methods provide a more granular control over the feature. `params` can be used to specify exactly which realization of a feature is requested.
        - `timeout` specifies how long to wait for a dynamic registration. Use `None` to wait indefinitly.
        When the `timeout` is reached without a matching registration, an `asyncio.TimeoutError` is raised.
        """
        if self.check_feature(method, **kwargs):
            return

        event = Event()
        request = _FeatureRequest(method, kwargs, event)

        if method not in self._pending_feature_requests:
            self._pending_feature_requests[method] = []
        self._pending_feature_requests[method].append(request)

        await wait_for(event.wait(), timeout)
