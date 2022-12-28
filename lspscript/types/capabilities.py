from typing import List, Optional
from dataclasses import dataclass
from .structures import *


@dataclass
class FeatureRegistration:
    id: Optional[str]
    method: str
    document_selector: Optional[DocumentSelector]
    options: Any


def _capability_to_feature_registration(capability: Any, method: str) -> FeatureRegistration:
    if isinstance(capability, TextDocumentRegistrationOptions):
        document_selector = capability.documentSelector
    else:
        document_selector = None
    if isinstance(capability, StaticRegistrationOptions):
        id = capability.id
    else:
        id = None
    return FeatureRegistration(id, method, document_selector, capability)


def server_capabilities_to_feature_registrations(capabilities: ServerCapabilities) -> List[FeatureRegistration]:
    out: List[FeatureRegistration] = []
    if capabilities and capabilities.implementationProvider:
        out.append(_capability_to_feature_registration(capabilities.implementationProvider, "textDocument/implementation"))
    if capabilities and capabilities.typeDefinitionProvider:
        out.append(_capability_to_feature_registration(capabilities.typeDefinitionProvider, "textDocument/typeDefinition"))
    if capabilities and capabilities.colorProvider:
        out.append(_capability_to_feature_registration(capabilities.colorProvider, "textDocument/documentColor"))
    if capabilities and capabilities.foldingRangeProvider:
        out.append(_capability_to_feature_registration(capabilities.foldingRangeProvider, "textDocument/foldingRange"))
    if capabilities and capabilities.declarationProvider:
        out.append(_capability_to_feature_registration(capabilities.declarationProvider, "textDocument/declaration"))
    if capabilities and capabilities.selectionRangeProvider:
        out.append(_capability_to_feature_registration(capabilities.selectionRangeProvider, "textDocument/selectionRange"))
    if capabilities and capabilities.callHierarchyProvider:
        out.append(_capability_to_feature_registration(capabilities.callHierarchyProvider, "textDocument/prepareCallHierarchy"))
    if capabilities and capabilities.semanticTokensProvider:
        out.append(_capability_to_feature_registration(capabilities.semanticTokensProvider, "textDocument/semanticTokens"))
    if capabilities and capabilities.linkedEditingRangeProvider:
        out.append(_capability_to_feature_registration(capabilities.linkedEditingRangeProvider, "textDocument/linkedEditingRange"))
    if capabilities and capabilities.workspace and capabilities.workspace.get("fileOperations") and capabilities.workspace.get("fileOperations").willCreate:
        out.append(_capability_to_feature_registration(capabilities.workspace["fileOperations"].willCreate, "workspace/willCreateFiles"))
    if capabilities and capabilities.workspace and capabilities.workspace.get("fileOperations") and capabilities.workspace.get("fileOperations").willRename:
        out.append(_capability_to_feature_registration(capabilities.workspace["fileOperations"].willRename, "workspace/willRenameFiles"))
    if capabilities and capabilities.workspace and capabilities.workspace.get("fileOperations") and capabilities.workspace.get("fileOperations").willDelete:
        out.append(_capability_to_feature_registration(capabilities.workspace["fileOperations"].willDelete, "workspace/willDeleteFiles"))
    if capabilities and capabilities.monikerProvider:
        out.append(_capability_to_feature_registration(capabilities.monikerProvider, "textDocument/moniker"))
    if capabilities and capabilities.typeHierarchyProvider:
        out.append(_capability_to_feature_registration(capabilities.typeHierarchyProvider, "textDocument/prepareTypeHierarchy"))
    if capabilities and capabilities.inlineValueProvider:
        out.append(_capability_to_feature_registration(capabilities.inlineValueProvider, "textDocument/inlineValue"))
    if capabilities and capabilities.inlayHintProvider:
        out.append(_capability_to_feature_registration(capabilities.inlayHintProvider, "textDocument/inlayHint"))
    if capabilities and capabilities.diagnosticProvider:
        out.append(_capability_to_feature_registration(capabilities.diagnosticProvider, "textDocument/diagnostic"))
    if capabilities and capabilities.completionProvider:
        out.append(_capability_to_feature_registration(capabilities.completionProvider, "textDocument/completion"))
    if capabilities and capabilities.hoverProvider:
        out.append(_capability_to_feature_registration(capabilities.hoverProvider, "textDocument/hover"))
    if capabilities and capabilities.signatureHelpProvider:
        out.append(_capability_to_feature_registration(capabilities.signatureHelpProvider, "textDocument/signatureHelp"))
    if capabilities and capabilities.definitionProvider:
        out.append(_capability_to_feature_registration(capabilities.definitionProvider, "textDocument/definition"))
    if capabilities and capabilities.referencesProvider:
        out.append(_capability_to_feature_registration(capabilities.referencesProvider, "textDocument/references"))
    if capabilities and capabilities.documentHighlightProvider:
        out.append(_capability_to_feature_registration(capabilities.documentHighlightProvider, "textDocument/documentHighlight"))
    if capabilities and capabilities.documentSymbolProvider:
        out.append(_capability_to_feature_registration(capabilities.documentSymbolProvider, "textDocument/documentSymbol"))
    if capabilities and capabilities.codeActionProvider:
        out.append(_capability_to_feature_registration(capabilities.codeActionProvider, "textDocument/codeAction"))
    if capabilities and capabilities.workspaceSymbolProvider:
        out.append(_capability_to_feature_registration(capabilities.workspaceSymbolProvider, "workspace/symbol"))
    if capabilities and capabilities.codeLensProvider:
        out.append(_capability_to_feature_registration(capabilities.codeLensProvider, "textDocument/codeLens"))
    if capabilities and capabilities.documentLinkProvider:
        out.append(_capability_to_feature_registration(capabilities.documentLinkProvider, "textDocument/documentLink"))
    if capabilities and capabilities.documentFormattingProvider:
        out.append(_capability_to_feature_registration(capabilities.documentFormattingProvider, "textDocument/formatting"))
    if capabilities and capabilities.documentRangeFormattingProvider:
        out.append(_capability_to_feature_registration(capabilities.documentRangeFormattingProvider, "textDocument/rangeFormatting"))
    if capabilities and capabilities.documentOnTypeFormattingProvider:
        out.append(_capability_to_feature_registration(capabilities.documentOnTypeFormattingProvider, "textDocument/onTypeFormatting"))
    if capabilities and capabilities.renameProvider:
        out.append(_capability_to_feature_registration(capabilities.renameProvider, "textDocument/rename"))
    if capabilities and capabilities.executeCommandProvider:
        out.append(_capability_to_feature_registration(capabilities.executeCommandProvider, "workspace/executeCommand"))
    if capabilities and capabilities.workspace and capabilities.workspace.get("fileOperations") and capabilities.workspace.get("fileOperations").didCreate:
        out.append(_capability_to_feature_registration(capabilities.workspace["fileOperations"].didCreate, "workspace/didCreateFiles"))
    if capabilities and capabilities.workspace and capabilities.workspace.get("fileOperations") and capabilities.workspace.get("fileOperations").didRename:
        out.append(_capability_to_feature_registration(capabilities.workspace["fileOperations"].didRename, "workspace/didRenameFiles"))
    if capabilities and capabilities.workspace and capabilities.workspace.get("fileOperations") and capabilities.workspace.get("fileOperations").didDelete:
        out.append(_capability_to_feature_registration(capabilities.workspace["fileOperations"].didDelete, "workspace/didDeleteFiles"))
    if capabilities and capabilities.notebookDocumentSync:
        out.append(_capability_to_feature_registration(capabilities.notebookDocumentSync, "notebookDocument/sync"))
    return out


_method_to_options_mapping = {
    "textDocument/implementation": ImplementationRegistrationOptions,
    "textDocument/typeDefinition": TypeDefinitionRegistrationOptions,
    "textDocument/documentColor": DocumentColorRegistrationOptions,
    "textDocument/foldingRange": FoldingRangeRegistrationOptions,
    "textDocument/declaration": DeclarationRegistrationOptions,
    "textDocument/selectionRange": SelectionRangeRegistrationOptions,
    "textDocument/prepareCallHierarchy": CallHierarchyRegistrationOptions,
    "textDocument/semanticTokens": SemanticTokensRegistrationOptions,
    "textDocument/linkedEditingRange": LinkedEditingRangeRegistrationOptions,
    "workspace/willCreateFiles": FileOperationRegistrationOptions,
    "workspace/willRenameFiles": FileOperationRegistrationOptions,
    "workspace/willDeleteFiles": FileOperationRegistrationOptions,
    "textDocument/moniker": MonikerRegistrationOptions,
    "textDocument/prepareTypeHierarchy": TypeHierarchyRegistrationOptions,
    "textDocument/inlineValue": InlineValueRegistrationOptions,
    "textDocument/inlayHint": InlayHintRegistrationOptions,
    "textDocument/diagnostic": DiagnosticRegistrationOptions,
    "textDocument/willSaveWaitUntil": TextDocumentRegistrationOptions,
    "textDocument/completion": CompletionRegistrationOptions,
    "textDocument/hover": HoverRegistrationOptions,
    "textDocument/signatureHelp": SignatureHelpRegistrationOptions,
    "textDocument/definition": DefinitionRegistrationOptions,
    "textDocument/references": ReferenceRegistrationOptions,
    "textDocument/documentHighlight": DocumentHighlightRegistrationOptions,
    "textDocument/documentSymbol": DocumentSymbolRegistrationOptions,
    "textDocument/codeAction": CodeActionRegistrationOptions,
    "workspace/symbol": WorkspaceSymbolRegistrationOptions,
    "textDocument/codeLens": CodeLensRegistrationOptions,
    "textDocument/documentLink": DocumentLinkRegistrationOptions,
    "textDocument/formatting": DocumentFormattingRegistrationOptions,
    "textDocument/rangeFormatting": DocumentRangeFormattingRegistrationOptions,
    "textDocument/onTypeFormatting": DocumentOnTypeFormattingRegistrationOptions,
    "textDocument/rename": RenameRegistrationOptions,
    "workspace/executeCommand": ExecuteCommandRegistrationOptions,
    "workspace/didCreateFiles": FileOperationRegistrationOptions,
    "workspace/didRenameFiles": FileOperationRegistrationOptions,
    "workspace/didDeleteFiles": FileOperationRegistrationOptions,
    "workspace/didChangeConfiguration": DidChangeConfigurationRegistrationOptions,
    "textDocument/didOpen": TextDocumentRegistrationOptions,
    "textDocument/didChange": TextDocumentChangeRegistrationOptions,
    "textDocument/didClose": TextDocumentRegistrationOptions,
    "textDocument/didSave": TextDocumentSaveRegistrationOptions,
    "textDocument/willSave": TextDocumentRegistrationOptions,
    "workspace/didChangeWatchedFiles": DidChangeWatchedFilesRegistrationOptions
}


def registration_to_feature_registration(registration: Registration) -> FeatureRegistration:
    cls = _method_to_options_mapping[registration.method]
    options = cls.from_json(registration.registerOptions)
    if isinstance(options, TextDocumentRegistrationOptions):
        document_selector = options.documentSelector
    else:
        document_selector = None
    if isinstance(options, StaticRegistrationOptions):
        id = options.id
    else:
        id = registration.id
    return FeatureRegistration(id, registration.method, document_selector, options)