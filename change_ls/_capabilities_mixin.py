from abc import ABC, abstractmethod
from asyncio import Event, wait_for
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import cattrs
from lsprotocol.types import (
    METHOD_TO_TYPES,
    CodeActionOptions,
    CodeLensOptions,
    CompletionOptions,
    DiagnosticOptions,
    DocumentLinkOptions,
    DocumentSelector,
    ExecuteCommandOptions,
    FileOperationRegistrationOptions,
    InlayHintOptions,
    NotebookCellTextDocumentFilter,
    NotebookDocumentSyncRegistrationOptions,
    Registration,
    SaveOptions,
    SemanticTokensOptions,
    SemanticTokensOptionsFullType1,
    SemanticTokensRegistrationOptions,
    ServerCapabilities,
    StaticRegistrationOptions,
    TextDocumentChangeRegistrationOptions,
    TextDocumentRegistrationOptions,
    TextDocumentSaveRegistrationOptions,
    TextDocumentSyncKind,
    TextDocumentSyncOptions,
    Unregistration,
    WorkspaceSymbolOptions,
)

from change_ls._util import (
    TextDocumentInfo,
    matches_file_operation_filter,
    matches_text_document_filter,
)
from change_ls.logging import OperationLoggerAdapter, operation


@dataclass
class FeatureRegistration:
    id: Optional[str]
    method: str
    document_selector: Optional[DocumentSelector]
    options: Any


def _capability_to_feature_registration(capability: Any, method: str) -> FeatureRegistration:
    if hasattr(capability, "document_selector"):
        document_selector = capability.document_selector
    else:
        document_selector = None
    if hasattr(capability, "id"):
        id = capability.id
    else:
        id = None
    return FeatureRegistration(id, method, document_selector, capability)


def server_capabilities_to_feature_registrations(
    capabilities: ServerCapabilities,
) -> List[FeatureRegistration]:
    out: List[FeatureRegistration] = []
    if capabilities.text_document_sync:
        if isinstance(capabilities.text_document_sync, TextDocumentSyncKind):
            options = _text_document_sync_kind_to_options(capabilities.text_document_sync)
        else:
            options = capabilities.text_document_sync
        out += _text_document_sync_options_to_feature_registrations(options)

    if capabilities.implementation_provider not in [None, False]:
        out.append(
            _capability_to_feature_registration(
                capabilities.implementation_provider, "textDocument/implementation"
            )
        )
    if capabilities.type_definition_provider not in [None, False]:
        out.append(
            _capability_to_feature_registration(
                capabilities.type_definition_provider, "textDocument/typeDefinition"
            )
        )
    if capabilities.color_provider not in [None, False]:
        out.append(
            _capability_to_feature_registration(
                capabilities.color_provider, "textDocument/documentColor"
            )
        )
    if capabilities.folding_range_provider not in [None, False]:
        out.append(
            _capability_to_feature_registration(
                capabilities.folding_range_provider, "textDocument/foldingRange"
            )
        )
    if capabilities.declaration_provider not in [None, False]:
        out.append(
            _capability_to_feature_registration(
                capabilities.declaration_provider, "textDocument/declaration"
            )
        )
    if capabilities.selection_range_provider not in [None, False]:
        out.append(
            _capability_to_feature_registration(
                capabilities.selection_range_provider, "textDocument/selectionRange"
            )
        )
    if capabilities.call_hierarchy_provider not in [None, False]:
        out.append(
            _capability_to_feature_registration(
                capabilities.call_hierarchy_provider, "textDocument/prepareCallHierarchy"
            )
        )
    if capabilities.semantic_tokens_provider not in [None, False]:
        out.append(
            _capability_to_feature_registration(
                capabilities.semantic_tokens_provider, "textDocument/semanticTokens"
            )
        )
    if capabilities.linked_editing_range_provider not in [None, False]:
        out.append(
            _capability_to_feature_registration(
                capabilities.linked_editing_range_provider, "textDocument/linkedEditingRange"
            )
        )
    if capabilities.moniker_provider not in [None, False]:
        out.append(
            _capability_to_feature_registration(
                capabilities.moniker_provider, "textDocument/moniker"
            )
        )
    if capabilities.type_hierarchy_provider not in [None, False]:
        out.append(
            _capability_to_feature_registration(
                capabilities.type_hierarchy_provider, "textDocument/prepareTypeHierarchy"
            )
        )
    if capabilities.inline_value_provider not in [None, False]:
        out.append(
            _capability_to_feature_registration(
                capabilities.inline_value_provider, "textDocument/inlineValue"
            )
        )
    if capabilities.inlay_hint_provider not in [None, False]:
        out.append(
            _capability_to_feature_registration(
                capabilities.inlay_hint_provider, "textDocument/inlayHint"
            )
        )
    if capabilities.diagnostic_provider not in [None, False]:
        out.append(
            _capability_to_feature_registration(
                capabilities.diagnostic_provider, "textDocument/diagnostic"
            )
        )
    if capabilities.completion_provider not in [None, False]:
        out.append(
            _capability_to_feature_registration(
                capabilities.completion_provider, "textDocument/completion"
            )
        )
    if capabilities.hover_provider not in [None, False]:
        out.append(
            _capability_to_feature_registration(capabilities.hover_provider, "textDocument/hover")
        )
    if capabilities.signature_help_provider not in [None, False]:
        out.append(
            _capability_to_feature_registration(
                capabilities.signature_help_provider, "textDocument/signatureHelp"
            )
        )
    if capabilities.definition_provider not in [None, False]:
        out.append(
            _capability_to_feature_registration(
                capabilities.definition_provider, "textDocument/definition"
            )
        )
    if capabilities.references_provider not in [None, False]:
        out.append(
            _capability_to_feature_registration(
                capabilities.references_provider, "textDocument/references"
            )
        )
    if capabilities.document_highlight_provider not in [None, False]:
        out.append(
            _capability_to_feature_registration(
                capabilities.document_highlight_provider, "textDocument/documentHighlight"
            )
        )
    if capabilities.document_symbol_provider not in [None, False]:
        out.append(
            _capability_to_feature_registration(
                capabilities.document_symbol_provider, "textDocument/documentSymbol"
            )
        )
    if capabilities.code_action_provider not in [None, False]:
        out.append(
            _capability_to_feature_registration(
                capabilities.code_action_provider, "textDocument/codeAction"
            )
        )
    if capabilities.workspace_symbol_provider not in [None, False]:
        out.append(
            _capability_to_feature_registration(
                capabilities.workspace_symbol_provider, "workspace/symbol"
            )
        )
    if capabilities.code_lens_provider not in [None, False]:
        out.append(
            _capability_to_feature_registration(
                capabilities.code_lens_provider, "textDocument/codeLens"
            )
        )
    if capabilities.document_link_provider not in [None, False]:
        out.append(
            _capability_to_feature_registration(
                capabilities.document_link_provider, "textDocument/documentLink"
            )
        )
    if capabilities.document_formatting_provider not in [None, False]:
        out.append(
            _capability_to_feature_registration(
                capabilities.document_formatting_provider, "textDocument/formatting"
            )
        )
    if capabilities.document_range_formatting_provider not in [None, False]:
        out.append(
            _capability_to_feature_registration(
                capabilities.document_range_formatting_provider, "textDocument/rangeFormatting"
            )
        )
    if capabilities.document_on_type_formatting_provider not in [None, False]:
        out.append(
            _capability_to_feature_registration(
                capabilities.document_on_type_formatting_provider, "textDocument/onTypeFormatting"
            )
        )
    if capabilities.rename_provider not in [None, False]:
        out.append(
            _capability_to_feature_registration(capabilities.rename_provider, "textDocument/rename")
        )
    if capabilities.execute_command_provider not in [None, False]:
        out.append(
            _capability_to_feature_registration(
                capabilities.execute_command_provider, "workspace/executeCommand"
            )
        )
    if capabilities.notebook_document_sync not in [None, False]:
        out.append(
            _capability_to_feature_registration(
                capabilities.notebook_document_sync, "notebookDocument/sync"
            )
        )

    if capabilities.workspace:
        if (
            capabilities.workspace.workspace_folders
            and capabilities.workspace.workspace_folders.change_notifications
        ):
            val = capabilities.workspace.workspace_folders.change_notifications
            if isinstance(val, str):
                out.append(
                    FeatureRegistration(val, "workspace/didChangeWorkspaceFolders", None, None)
                )

        if capabilities.workspace.file_operations:
            if capabilities.workspace.file_operations.will_create not in [None, False]:
                out.append(
                    _capability_to_feature_registration(
                        capabilities.workspace.file_operations.will_create,
                        "workspace/willCreateFiles",
                    )
                )
            if capabilities.workspace.file_operations.will_rename not in [None, False]:
                out.append(
                    _capability_to_feature_registration(
                        capabilities.workspace.file_operations.will_rename,
                        "workspace/willRenameFiles",
                    )
                )
            if capabilities.workspace.file_operations.will_delete not in [None, False]:
                out.append(
                    _capability_to_feature_registration(
                        capabilities.workspace.file_operations.will_delete,
                        "workspace/willDeleteFiles",
                    )
                )
            if capabilities.workspace.file_operations.did_create not in [None, False]:
                out.append(
                    _capability_to_feature_registration(
                        capabilities.workspace.file_operations.did_create,
                        "workspace/didCreateFiles",
                    )
                )
            if capabilities.workspace.file_operations.did_rename not in [None, False]:
                out.append(
                    _capability_to_feature_registration(
                        capabilities.workspace.file_operations.did_rename,
                        "workspace/didRenameFiles",
                    )
                )
            if capabilities.workspace.file_operations.did_delete not in [None, False]:
                out.append(
                    _capability_to_feature_registration(
                        capabilities.workspace.file_operations.did_delete,
                        "workspace/didDeleteFiles",
                    )
                )
    return out


@dataclass
class _FeatureRequest:
    method: str
    params: Dict[str, Any]
    event: Event


def _registration_fulfils_feature_request(
    request_params: Dict[str, Any], registration: FeatureRegistration
) -> bool:
    if "text_documents" in request_params and registration.document_selector:
        # TODO does this really need a special member in FeatureRegistration?

        text_documents: List[TextDocumentInfo] = request_params["text_documents"]

        for t in text_documents:
            document_matched = False
            for document_filter in registration.document_selector:
                if isinstance(document_filter, NotebookCellTextDocumentFilter):
                    continue

                if matches_text_document_filter(t, document_filter):
                    document_matched = True
                    break
            if not document_matched:
                return False

    if "sync_kind" in request_params:
        if isinstance(registration.options, TextDocumentChangeRegistrationOptions):
            if request_params["sync_kind"] != registration.options.sync_kind:
                return False
        elif isinstance(registration.options, TextDocumentSyncOptions):
            if request_params["sync_kind"] != registration.options.change:
                return False

    if "include_text" in request_params and (
        isinstance(registration.options, (SaveOptions, TextDocumentSaveRegistrationOptions))
    ):
        if request_params["include_text"] != bool(registration.options.include_text):
            return False

    if "file_operations" in request_params and isinstance(
        registration.options, FileOperationRegistrationOptions
    ):
        uris: List[str] = request_params["file_operations"]

        for t in uris:
            uri_matched = False
            for document_filter in registration.options.filters:
                if matches_file_operation_filter(t, document_filter):
                    uri_matched = True
                    break
            if not uri_matched:
                return False

    if "semantic_tokens" in request_params and isinstance(
        registration.options, SemanticTokensOptions
    ):
        for r in request_params["semantic_tokens"]:
            if r == "full" and not registration.options.full:
                return False
            elif r == "full/delta" and not (
                isinstance(registration.options.full, SemanticTokensOptionsFullType1)
                and registration.options.full.delta
            ):
                return False
            elif r == "range" and not registration.options.range:
                return False

    if "code_actions" in request_params and isinstance(registration.options, CodeActionOptions):
        for c in request_params["code_actions"]:
            if c not in registration.options.code_action_kinds:
                return False

    if "code_action_resolve" in request_params and isinstance(
        registration.options, CodeActionOptions
    ):
        if request_params["code_action_resolve"] != bool(registration.options.resolve_provider):
            return False

    if "workspace_commands" in request_params and isinstance(
        registration.options, ExecuteCommandOptions
    ):
        for c in request_params["workspace_commands"]:
            if c not in registration.options.commands:
                return False

    if "completion_item_resolve" in request_params and isinstance(
        registration.options, CompletionOptions
    ):
        if request_params["completion_item_resolve"] != bool(registration.options.resolve_provider):
            return False

    if "completion_item_label_details" in request_params and isinstance(
        registration.options, CompletionOptions
    ):
        if request_params["completion_item_label_details"] != (
            registration.options.completion_item
            and registration.options.completion_item.label_details_support
        ):
            return False

    if "inlay_hint_resolve" in request_params and isinstance(
        registration.options, InlayHintOptions
    ):
        if request_params["inlay_hint_resolve"] != bool(registration.options.resolve_provider):
            return False

    if "workspace_diagnostic" in request_params and isinstance(
        registration.options, DiagnosticOptions
    ):
        if request_params["workspace_diagnostic"] != bool(
            registration.options.workspace_diagnostics
        ):
            return False

    if "workspace_symbol_resolve" in request_params and isinstance(
        registration.options, WorkspaceSymbolOptions
    ):
        if request_params["workspace_symbol_resolve"] != bool(
            registration.options.resolve_provider
        ):
            return False

    if "code_lens_resolve" in request_params and isinstance(registration.options, CodeLensOptions):
        if request_params["code_lens_resolve"] != bool(registration.options.resolve_provider):
            return False

    if "document_link_resolve" in request_params and isinstance(
        registration.options, DocumentLinkOptions
    ):
        if request_params["document_link_resolve"] != bool(registration.options.resolve_provider):
            return False

    return True


def _text_document_sync_kind_to_options(kind: TextDocumentSyncKind) -> TextDocumentSyncOptions:
    # Is this anywhere in the spec? Taken from https://github.com/microsoft/vscode-languageserver-node/blob/c91c2f89e0a3d8aa8923355a65a2977b2b3d3b57/client/src/common/client.ts#L1168
    if kind is TextDocumentSyncKind.None_:
        return TextDocumentSyncOptions(open_close=False, change=TextDocumentSyncKind.None_)
    else:
        return TextDocumentSyncOptions(
            open_close=True, change=kind, save=SaveOptions(include_text=False)
        )


def _text_document_sync_options_to_feature_registrations(
    options: TextDocumentSyncOptions,
) -> List[FeatureRegistration]:
    out: List[FeatureRegistration] = []

    if options.open_close:
        out.append(FeatureRegistration(None, "textDocument/didOpen", None, options))
        out.append(FeatureRegistration(None, "textDocument/didClose", None, options))

    if options.save:
        out.append(FeatureRegistration(None, "textDocument/didSave", None, options.save))
    if options.will_save:
        out.append(FeatureRegistration(None, "textDocument/willSave", None, options))
    if options.will_save_wait_until:
        out.append(FeatureRegistration(None, "textDocument/willSaveWaitUntil", None, options))

    if options.change is not None and options.change != TextDocumentSyncKind.None_:
        out.append(FeatureRegistration(None, "textDocument/didChange", None, options))

    return out


def _registration_to_feature_registration(
    registration: Registration, converter: cattrs.Converter
) -> Optional[FeatureRegistration]:
    # Requests/Notifications which have a registrationMethod set need to be handled separately.
    if registration.method == "textDocument/semanticTokens":
        cls = SemanticTokensRegistrationOptions
    elif registration.method == "notebookDocument/sync":
        cls = NotebookDocumentSyncRegistrationOptions
    elif registration.method not in METHOD_TO_TYPES or not (
        cls := METHOD_TO_TYPES[registration.method][3]
    ):
        return None

    options = converter.structure(registration.register_options, cls)
    if isinstance(options, TextDocumentRegistrationOptions):
        document_selector = options.document_selector
    else:
        document_selector = None
    if isinstance(options, StaticRegistrationOptions):
        id = options.id
    else:
        id = registration.id
    return FeatureRegistration(id, registration.method, document_selector, options)


class CapabilitiesMixin(ABC):
    _registrations: Dict[str, List[FeatureRegistration]]
    _pending_feature_requests: Dict[str, List[_FeatureRequest]]
    _server_capabilities: Optional[ServerCapabilities]

    def __init__(self) -> None:
        self._registrations = {}
        self._pending_feature_requests = {}
        self._server_capabilities = None

    @property
    @abstractmethod
    def logger(self) -> OperationLoggerAdapter:
        ...

    @property
    @abstractmethod
    def _converter(self) -> cattrs.Converter:
        ...

    def _set_server_capabilities(self, capabilities: ServerCapabilities) -> None:
        self._server_capabilities = capabilities
        registration_list = server_capabilities_to_feature_registrations(capabilities)

        self._registrations = {}
        for r in registration_list:
            if r.method not in self._registrations:
                self._registrations[r.method] = []
            self._registrations[r.method].append(r)

        self._check_pending_feature_requests()

    def _add_dynamic_registration(self, registration: Registration) -> None:
        feature_registration = _registration_to_feature_registration(registration, self._converter)
        if not feature_registration:
            self.logger.warning(
                f"Unable to process dynamic feature registraction for {registration.method}"
            )
            return

        if feature_registration.method not in self._registrations:
            self._registrations[feature_registration.method] = []
        self._registrations[feature_registration.method].append(feature_registration)
        self.logger.info(
            f"Added dynamic feature registration for {feature_registration.method} with id {feature_registration.id}"
        )

    def _remove_dynamic_registration(self, unregistration: Unregistration) -> None:
        registrations = self._registrations.get(unregistration.method, [])

        for i, r in enumerate(registrations):
            if r.id and r.id == unregistration.id:
                del registrations[i]
                self.logger.info(
                    f"Removed dynamic feature registration with id {unregistration.id}"
                )
                return

        self.logger.warning(
            f"Dynamic registration {unregistration.id} for {unregistration.method} could not be removed because it was not found."
        )

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

    @operation
    async def require_feature(
        self, method: str, *, timeout: Optional[float] = 10.0, **kwargs: Any
    ) -> None:
        """
        Requires that the language server provides the feature described by `method` and `params`. This
        should be used when a language server registers some of its features dynamically, since the client
        potentially has to wait until the language server is ready to provide the feature.

        For a list of additional keyword parameters see :meth:`check_feature()`.

        :param method: The *registration* method for the feature (might be different from the request/notification method).
        :param timeout: How long to wait for a dynamic registration. Use `None` to wait indefinitly.
            When the ``timeout`` is reached without a matching registration, an ``asyncio.TimeoutError`` is raised.
        """
        self.logger.info(f"Requiring dynamic feature {method}.")
        if self.check_feature(method, **kwargs):
            return

        event = Event()
        request = _FeatureRequest(method, kwargs, event)

        if method not in self._pending_feature_requests:
            self._pending_feature_requests[method] = []
        self._pending_feature_requests[method].append(request)

        await wait_for(event.wait(), timeout)
