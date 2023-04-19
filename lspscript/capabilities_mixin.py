from asyncio import Event, wait_for
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

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
                                        TextDocumentChangeRegistrationOptions,
                                        TextDocumentSaveRegistrationOptions,
                                        TextDocumentSyncOptions,
                                        Unregistration, WorkspaceSymbolOptions)
from lspscript.util import (TextDocumentInfo, matches_file_operation_filter,
                            matches_text_document_filter)

from .types.capabilities import (FeatureRegistration,
                                 registration_to_feature_registration,
                                 server_capabilities_to_feature_registrations)


@dataclass
class _FeatureRequest:
    method: str
    params: Dict[str, Any]
    event: Event


def _registration_fulfils_feature_request(request_params: Dict[str, Any], registration: FeatureRegistration) -> bool:
    if "text_documents" in request_params and registration.document_selector:
        # TODO does this really need a special member in FeatureRegistration?

        text_documents: List[TextDocumentInfo] = request_params["text_documents"]

        for t in text_documents:
            document_matched = False
            for filter in registration.document_selector:
                if isinstance(filter, NotebookCellTextDocumentFilter):
                    continue

                if matches_text_document_filter(t, filter):
                    document_matched = True
                    break
            if not document_matched:
                return False

    if "sync_kind" in request_params:
        if isinstance(registration.options, TextDocumentChangeRegistrationOptions):
            if request_params["sync_kind"] != registration.options.syncKind:
                return False
        elif isinstance(registration.options, TextDocumentSyncOptions):
            if request_params["sync_kind"] != registration.options.change:
                return False

    if "include_text" in request_params and (isinstance(registration.options, SaveOptions)
                                             or isinstance(registration.options, TextDocumentSaveRegistrationOptions)):
        if request_params["include_text"] != bool(registration.options.includeText):
            return False

    if "file_operations" in request_params and isinstance(registration.options, FileOperationRegistrationOptions):
        uris: List[str] = request_params["file_operations"]

        for t in uris:
            uri_matched = False
            for filter in registration.options.filters:
                if matches_file_operation_filter(t, filter):
                    uri_matched = True
                    break
            if not uri_matched:
                return False

    if "semantic_tokens" in request_params and isinstance(registration.options, SemanticTokensOptions):
        for r in request_params["semantic_tokens"]:
            if r == "full" and not registration.options.full:
                return False
            elif r == "full/delta" and not (isinstance(registration.options.full, Dict) and registration.options.full.get("delta")):
                return False
            elif r == "range" and not registration.options.range:
                return False

    if "code_actions" in request_params and isinstance(registration.options, CodeActionOptions):
        for c in request_params["code_actions"]:
            if c not in registration.options.codeActionKinds:
                return False

    if "code_action_resolve" in request_params and isinstance(registration.options, CodeActionOptions):
        if request_params["code_action_resolve"] != bool(registration.options.resolveProvider):
            return False

    if "workspace_commands" in request_params and isinstance(registration.options, ExecuteCommandOptions):
        for c in request_params["workspace_commands"]:
            if c not in registration.options.commands:
                return False

    if "completion_item_resolve" in request_params and isinstance(registration.options, CompletionOptions):
        if request_params["completion_item_resolve"] != bool(registration.options.resolveProvider):
            return False

    if "completion_item_label_details" in request_params and isinstance(registration.options, CompletionOptions):
        if request_params["completion_item_label_details"] != (registration.options.completionItem and registration.options.completionItem.get("labelDetailsSupport")):
            return False

    if "inlay_hint_resolve" in request_params and isinstance(registration.options, InlayHintOptions):
        if request_params["inlay_hint_resolve"] != bool(registration.options.resolveProvider):
            return False

    if "workspace_diagnostic" in request_params and isinstance(registration.options, DiagnosticOptions):
        if request_params["workspace_diagnostic"] != bool(registration.options.workspaceDiagnostics):
            return False

    if "workspace_symbol_resolve" in request_params and isinstance(registration.options, WorkspaceSymbolOptions):
        if request_params["workspace_symbol_resolve"] != bool(registration.options.resolveProvider):
            return False

    if "code_lens_resolve" in request_params and isinstance(registration.options, CodeLensOptions):
        if request_params["code_lens_resolve"] != bool(registration.options.resolveProvider):
            return False

    if "document_link_resolve" in request_params and isinstance(registration.options, DocumentLinkOptions):
        if request_params["document_link_resolve"] != bool(registration.options.resolveProvider):
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
        out.append(FeatureRegistration(None, "textDocument/didOpen", None, options))
        out.append(FeatureRegistration(None, "textDocument/didClose", None, options))

    if options.save:
        out.append(FeatureRegistration(None, "textDocument/didSave", None, options.save))
    if options.willSave:
        out.append(FeatureRegistration(None, "textDocument/willSave", None, options))
    if options.willSaveWaitUntil:
        out.append(FeatureRegistration(None, "textDocument/willSaveWaitUntil", None, options))

    if options.change is not None and options.change != TextDocumentSyncKind.None_:
        out.append(FeatureRegistration(None, "textDocument/didChange", None, options))

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

        # workspace/diagnostics is a special case inside the registration options for textDocument/diagnostics.
        # While it would be possible to handle this in the generator, it would be a lot of effort because
        # capabilities.diagnosticProvider is an OR-type. Since this is the only case of this pattern, it is
        # currently easier to just add the FeatureRegistration manually.
        if capabilities.diagnosticProvider and capabilities.diagnosticProvider.workspaceDiagnostics:
            registration_list.append(FeatureRegistration(
                None, "workspace/diagnostics", None, capabilities.diagnosticProvider))

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

        :param method: The *registration* method for the feature (might be different from the request/notification method).

        :param text_documents: List of :class:`TextDocuments <TextDocument>` for which this feature should be checked.
        :type text_documents: List[TextDocumentInfo]

        :param sync_kind: How to synchronize ``TextDocument`` content with the language server over *textDocument/didChange*
            notifications.
        :type sync_kind: TextDocumentSyncKind

        :param include_text: Whether a ``TextDocuments`` content should be sent for *textDocument/didSave* notifications.
        :type include_text: bool

        :param file_operations: Uris of documents, for which file operation messages should be sent. Used with
            *workspace/willCreateFiles*, *workspace/didCreateFiles*, *workspace/willRenameFiles*, *workspace/didRenameFiles*,
            *workspace/willDeleteFiles*, *workspace/didDeleteFiles*
        :type file_operations: List[str]

        :param semantic_tokens: Which of *textDocument/semanticTokens/full*, *textDocument/semanticTokens/range* and
            *textDocument/semanticTokens/delta* is required. Note the the registration ``method`` for these requests is
            *textDocument/semanticTokens*.
        :type semantic_tokens: List[Literal["full", "delta", "range]]

        :param code_actions: Which kinds of code actions are required. Used with *textDocument/codeAction*.
        :type code_actions: List[CodeActionKind]

        :param code_action_resolve: Whether the *codeAction/resolve* request is supported. Used with *textDocument/codeAction*.
        :type code_action_resolve: bool

        :param workspace_commands: Which workspace commands are required. Used with *workspace/executeCommand*.
        :type workspace_commands: List[str]

        :param completion_item_resolve: Whether the *completionItem/resolve* request is supported. Used with *textDocument/completion*.
        :type completion_item_resolve: bool

        :param completion_item_label_details: Whether the server supports the :attr:`CompletionItem.labelDetails` field.
            Used with *textDocument/completion*.
        :type completion_item_label_details: bool

        :param inlay_hint_resolve: Whether the *inlayHint/resolve* request is supported. Used with *textDocument/inlayHint*.
        :type inlay_hint_resolve: bool

        :param workspace_symbol_resolve: Whether the *workspaceSymbol/resolve* request is supported. Used with *workspace/symbol*.
        :type workspace_symbol_resolve: bool

        :param code_lens_resolve: Whether the *codeLens/resolve* request is supported. Used with *textDocument/codeLens*.
        :type code_lens_resolve: bool

        :param document_link_resolve: Whether the *documentLink/resolve* request is supported. Used with *textDocument/documentLink*.
        :type document_link_resolve: bool
        """

        registrations = self._registrations.get(method)
        if not registrations or len(registrations) == 0:
            return False

        if any(_registration_fulfils_feature_request(kwargs, r) for r in registrations):
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

        For a list of additional keyword parameters see :meth:`check_feature()`.

        :param method: The *registration* method for the feature (might be different from the request/notification method).
        :param timeout: How long to wait for a dynamic registration. Use `None` to wait indefinitly.
            When the ``timeout`` is reached without a matching registration, an ``asyncio.TimeoutError`` is raised.
        """
        if self.check_feature(method, **kwargs):
            return

        event = Event()
        request = _FeatureRequest(method, kwargs, event)

        if method not in self._pending_feature_requests:
            self._pending_feature_requests[method] = []
        self._pending_feature_requests[method].append(request)

        await wait_for(event.wait(), timeout)
