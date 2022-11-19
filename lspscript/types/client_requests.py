from .util import *
from .enumerations import *
from .structures import *

from abc import ABC, abstractmethod
from typing import Any

class ClientRequestsMixin(ABC):

    @abstractmethod
    async def send_request(self, method: str, params: JSON_VALUE, **kwargs: Any) -> JSON_VALUE:
        pass

    @abstractmethod
    async def send_notification(self, method: str, params: JSON_VALUE) -> None:
        pass

    async def send_text_document_implementation(self, params: "ImplementationParams", **kwargs: Any) -> Union["Definition", List["DefinitionLink"], None]:
        """
        A request to resolve the implementation locations of a symbol at a given text
        document position. The request's parameter is of type [TextDocumentPositionParams]
        (#TextDocumentPositionParams) the response is of type [Definition](#Definition) or a
        Thenable that resolves to such.
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("textDocument/implementation", params_json, **kwargs)
        return parse_or_type((result_json), (lambda v: parse_Definition((v)), lambda v: [parse_DefinitionLink(json_assert_type_object(i)) for i in json_assert_type_array(v)], lambda v: json_assert_type_null(v)))
    
    async def send_text_document_type_definition(self, params: "TypeDefinitionParams", **kwargs: Any) -> Union["Definition", List["DefinitionLink"], None]:
        """
        A request to resolve the type definition locations of a symbol at a given text
        document position. The request's parameter is of type [TextDocumentPositionParams]
        (#TextDocumentPositionParams) the response is of type [Definition](#Definition) or a
        Thenable that resolves to such.
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("textDocument/typeDefinition", params_json, **kwargs)
        return parse_or_type((result_json), (lambda v: parse_Definition((v)), lambda v: [parse_DefinitionLink(json_assert_type_object(i)) for i in json_assert_type_array(v)], lambda v: json_assert_type_null(v)))
    
    async def send_text_document_document_color(self, params: "DocumentColorParams", **kwargs: Any) -> List["ColorInformation"]:
        """
        A request to list all color symbols found in a given text document. The request's
        parameter is of type [DocumentColorParams](#DocumentColorParams) the
        response is of type [ColorInformation[]](#ColorInformation) or a Thenable
        that resolves to such.
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("textDocument/documentColor", params_json, **kwargs)
        return [ColorInformation.from_json(json_assert_type_object(i)) for i in json_assert_type_array(result_json)]
    
    async def send_text_document_color_presentation(self, params: "ColorPresentationParams", **kwargs: Any) -> List["ColorPresentation"]:
        """
        A request to list all presentation for a color. The request's
        parameter is of type [ColorPresentationParams](#ColorPresentationParams) the
        response is of type [ColorInformation[]](#ColorInformation) or a Thenable
        that resolves to such.
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("textDocument/colorPresentation", params_json, **kwargs)
        return [ColorPresentation.from_json(json_assert_type_object(i)) for i in json_assert_type_array(result_json)]
    
    async def send_text_document_folding_range(self, params: "FoldingRangeParams", **kwargs: Any) -> Union[List["FoldingRange"], None]:
        """
        A request to provide folding ranges in a document. The request's
        parameter is of type [FoldingRangeParams](#FoldingRangeParams), the
        response is of type [FoldingRangeList](#FoldingRangeList) or a Thenable
        that resolves to such.
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("textDocument/foldingRange", params_json, **kwargs)
        return parse_or_type((result_json), (lambda v: [FoldingRange.from_json(json_assert_type_object(i)) for i in json_assert_type_array(v)], lambda v: json_assert_type_null(v)))
    
    async def send_text_document_declaration(self, params: "DeclarationParams", **kwargs: Any) -> Union["Declaration", List["DeclarationLink"], None]:
        """
        A request to resolve the type definition locations of a symbol at a given text
        document position. The request's parameter is of type [TextDocumentPositionParams]
        (#TextDocumentPositionParams) the response is of type [Declaration](#Declaration)
        or a typed array of [DeclarationLink](#DeclarationLink) or a Thenable that resolves
        to such.
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("textDocument/declaration", params_json, **kwargs)
        return parse_or_type((result_json), (lambda v: parse_Declaration((v)), lambda v: [parse_DeclarationLink(json_assert_type_object(i)) for i in json_assert_type_array(v)], lambda v: json_assert_type_null(v)))
    
    async def send_text_document_selection_range(self, params: "SelectionRangeParams", **kwargs: Any) -> Union[List["SelectionRange"], None]:
        """
        A request to provide selection ranges in a document. The request's
        parameter is of type [SelectionRangeParams](#SelectionRangeParams), the
        response is of type [SelectionRange[]](#SelectionRange[]) or a Thenable
        that resolves to such.
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("textDocument/selectionRange", params_json, **kwargs)
        return parse_or_type((result_json), (lambda v: [SelectionRange.from_json(json_assert_type_object(i)) for i in json_assert_type_array(v)], lambda v: json_assert_type_null(v)))
    
    async def send_text_document_prepare_call_hierarchy(self, params: "CallHierarchyPrepareParams", **kwargs: Any) -> Union[List["CallHierarchyItem"], None]:
        """
        A request to result a `CallHierarchyItem` in a document at a given position.
        Can be used as an input to an incoming or outgoing call hierarchy.
        
        @since 3.16.0
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("textDocument/prepareCallHierarchy", params_json, **kwargs)
        return parse_or_type((result_json), (lambda v: [CallHierarchyItem.from_json(json_assert_type_object(i)) for i in json_assert_type_array(v)], lambda v: json_assert_type_null(v)))
    
    async def send_call_hierarchy_incoming_calls(self, params: "CallHierarchyIncomingCallsParams", **kwargs: Any) -> Union[List["CallHierarchyIncomingCall"], None]:
        """
        A request to resolve the incoming calls for a given `CallHierarchyItem`.
        
        @since 3.16.0
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("callHierarchy/incomingCalls", params_json, **kwargs)
        return parse_or_type((result_json), (lambda v: [CallHierarchyIncomingCall.from_json(json_assert_type_object(i)) for i in json_assert_type_array(v)], lambda v: json_assert_type_null(v)))
    
    async def send_call_hierarchy_outgoing_calls(self, params: "CallHierarchyOutgoingCallsParams", **kwargs: Any) -> Union[List["CallHierarchyOutgoingCall"], None]:
        """
        A request to resolve the outgoing calls for a given `CallHierarchyItem`.
        
        @since 3.16.0
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("callHierarchy/outgoingCalls", params_json, **kwargs)
        return parse_or_type((result_json), (lambda v: [CallHierarchyOutgoingCall.from_json(json_assert_type_object(i)) for i in json_assert_type_array(v)], lambda v: json_assert_type_null(v)))
    
    async def send_text_document_semantic_tokens_full(self, params: "SemanticTokensParams", **kwargs: Any) -> Union["SemanticTokens", None]:
        """
        @since 3.16.0
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("textDocument/semanticTokens/full", params_json, **kwargs)
        return parse_or_type((result_json), (lambda v: SemanticTokens.from_json(json_assert_type_object(v)), lambda v: json_assert_type_null(v)))
    
    async def send_text_document_semantic_tokens_full_delta(self, params: "SemanticTokensDeltaParams", **kwargs: Any) -> Union["SemanticTokens", "SemanticTokensDelta", None]:
        """
        @since 3.16.0
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("textDocument/semanticTokens/full/delta", params_json, **kwargs)
        return parse_or_type((result_json), (lambda v: SemanticTokens.from_json(json_assert_type_object(v)), lambda v: SemanticTokensDelta.from_json(json_assert_type_object(v)), lambda v: json_assert_type_null(v)))
    
    async def send_text_document_semantic_tokens_range(self, params: "SemanticTokensRangeParams", **kwargs: Any) -> Union["SemanticTokens", None]:
        """
        @since 3.16.0
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("textDocument/semanticTokens/range", params_json, **kwargs)
        return parse_or_type((result_json), (lambda v: SemanticTokens.from_json(json_assert_type_object(v)), lambda v: json_assert_type_null(v)))
    
    async def send_workspace_semantic_tokens_refresh(self, **kwargs: Any) -> None:
        """
        @since 3.16.0
    
        *Generated from the TypeScript documentation*
        """
        result_json = await self.send_request("workspace/semanticTokens/refresh", None, **kwargs)
        return json_assert_type_null(result_json)
    
    async def send_text_document_linked_editing_range(self, params: "LinkedEditingRangeParams", **kwargs: Any) -> Union["LinkedEditingRanges", None]:
        """
        A request to provide ranges that can be edited together.
        
        @since 3.16.0
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("textDocument/linkedEditingRange", params_json, **kwargs)
        return parse_or_type((result_json), (lambda v: LinkedEditingRanges.from_json(json_assert_type_object(v)), lambda v: json_assert_type_null(v)))
    
    async def send_workspace_will_create_files(self, params: "CreateFilesParams", **kwargs: Any) -> Union["WorkspaceEdit", None]:
        """
        The will create files request is sent from the client to the server before files are actually
        created as long as the creation is triggered from within the client.
        
        @since 3.16.0
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("workspace/willCreateFiles", params_json, **kwargs)
        return parse_or_type((result_json), (lambda v: WorkspaceEdit.from_json(json_assert_type_object(v)), lambda v: json_assert_type_null(v)))
    
    async def send_workspace_will_rename_files(self, params: "RenameFilesParams", **kwargs: Any) -> Union["WorkspaceEdit", None]:
        """
        The will rename files request is sent from the client to the server before files are actually
        renamed as long as the rename is triggered from within the client.
        
        @since 3.16.0
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("workspace/willRenameFiles", params_json, **kwargs)
        return parse_or_type((result_json), (lambda v: WorkspaceEdit.from_json(json_assert_type_object(v)), lambda v: json_assert_type_null(v)))
    
    async def send_workspace_will_delete_files(self, params: "DeleteFilesParams", **kwargs: Any) -> Union["WorkspaceEdit", None]:
        """
        The did delete files notification is sent from the client to the server when
        files were deleted from within the client.
        
        @since 3.16.0
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("workspace/willDeleteFiles", params_json, **kwargs)
        return parse_or_type((result_json), (lambda v: WorkspaceEdit.from_json(json_assert_type_object(v)), lambda v: json_assert_type_null(v)))
    
    async def send_text_document_moniker(self, params: "MonikerParams", **kwargs: Any) -> Union[List["Moniker"], None]:
        """
        A request to get the moniker of a symbol at a given text document position.
        The request parameter is of type [TextDocumentPositionParams](#TextDocumentPositionParams).
        The response is of type [Moniker[]](#Moniker[]) or `null`.
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("textDocument/moniker", params_json, **kwargs)
        return parse_or_type((result_json), (lambda v: [Moniker.from_json(json_assert_type_object(i)) for i in json_assert_type_array(v)], lambda v: json_assert_type_null(v)))
    
    async def send_text_document_prepare_type_hierarchy(self, params: "TypeHierarchyPrepareParams", **kwargs: Any) -> Union[List["TypeHierarchyItem"], None]:
        """
        A request to result a `TypeHierarchyItem` in a document at a given position.
        Can be used as an input to a subtypes or supertypes type hierarchy.
        
        @since 3.17.0
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("textDocument/prepareTypeHierarchy", params_json, **kwargs)
        return parse_or_type((result_json), (lambda v: [TypeHierarchyItem.from_json(json_assert_type_object(i)) for i in json_assert_type_array(v)], lambda v: json_assert_type_null(v)))
    
    async def send_type_hierarchy_supertypes(self, params: "TypeHierarchySupertypesParams", **kwargs: Any) -> Union[List["TypeHierarchyItem"], None]:
        """
        A request to resolve the supertypes for a given `TypeHierarchyItem`.
        
        @since 3.17.0
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("typeHierarchy/supertypes", params_json, **kwargs)
        return parse_or_type((result_json), (lambda v: [TypeHierarchyItem.from_json(json_assert_type_object(i)) for i in json_assert_type_array(v)], lambda v: json_assert_type_null(v)))
    
    async def send_type_hierarchy_subtypes(self, params: "TypeHierarchySubtypesParams", **kwargs: Any) -> Union[List["TypeHierarchyItem"], None]:
        """
        A request to resolve the subtypes for a given `TypeHierarchyItem`.
        
        @since 3.17.0
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("typeHierarchy/subtypes", params_json, **kwargs)
        return parse_or_type((result_json), (lambda v: [TypeHierarchyItem.from_json(json_assert_type_object(i)) for i in json_assert_type_array(v)], lambda v: json_assert_type_null(v)))
    
    async def send_text_document_inline_value(self, params: "InlineValueParams", **kwargs: Any) -> Union[List["InlineValue"], None]:
        """
        A request to provide inline values in a document. The request's parameter is of
        type [InlineValueParams](#InlineValueParams), the response is of type
        [InlineValue[]](#InlineValue[]) or a Thenable that resolves to such.
        
        @since 3.17.0
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("textDocument/inlineValue", params_json, **kwargs)
        return parse_or_type((result_json), (lambda v: [parse_InlineValue((i)) for i in json_assert_type_array(v)], lambda v: json_assert_type_null(v)))
    
    async def send_workspace_inline_value_refresh(self, **kwargs: Any) -> None:
        """
        @since 3.17.0
    
        *Generated from the TypeScript documentation*
        """
        result_json = await self.send_request("workspace/inlineValue/refresh", None, **kwargs)
        return json_assert_type_null(result_json)
    
    async def send_text_document_inlay_hint(self, params: "InlayHintParams", **kwargs: Any) -> Union[List["InlayHint"], None]:
        """
        A request to provide inlay hints in a document. The request's parameter is of
        type [InlayHintsParams](#InlayHintsParams), the response is of type
        [InlayHint[]](#InlayHint[]) or a Thenable that resolves to such.
        
        @since 3.17.0
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("textDocument/inlayHint", params_json, **kwargs)
        return parse_or_type((result_json), (lambda v: [InlayHint.from_json(json_assert_type_object(i)) for i in json_assert_type_array(v)], lambda v: json_assert_type_null(v)))
    
    async def send_inlay_hint_resolve(self, params: "InlayHint", **kwargs: Any) -> "InlayHint":
        """
        A request to resolve additional properties for an inlay hint.
        The request's parameter is of type [InlayHint](#InlayHint), the response is
        of type [InlayHint](#InlayHint) or a Thenable that resolves to such.
        
        @since 3.17.0
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("inlayHint/resolve", params_json, **kwargs)
        return InlayHint.from_json(json_assert_type_object(result_json))
    
    async def send_workspace_inlay_hint_refresh(self, **kwargs: Any) -> None:
        """
        @since 3.17.0
    
        *Generated from the TypeScript documentation*
        """
        result_json = await self.send_request("workspace/inlayHint/refresh", None, **kwargs)
        return json_assert_type_null(result_json)
    
    async def send_text_document_diagnostic(self, params: "DocumentDiagnosticParams", **kwargs: Any) -> "DocumentDiagnosticReport":
        """
        The document diagnostic request definition.
        
        @since 3.17.0
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("textDocument/diagnostic", params_json, **kwargs)
        return parse_DocumentDiagnosticReport((result_json))
    
    async def send_workspace_diagnostic(self, params: "WorkspaceDiagnosticParams", **kwargs: Any) -> "WorkspaceDiagnosticReport":
        """
        The workspace diagnostic request definition.
        
        @since 3.17.0
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("workspace/diagnostic", params_json, **kwargs)
        return WorkspaceDiagnosticReport.from_json(json_assert_type_object(result_json))
    
    async def send_workspace_diagnostic_refresh(self, **kwargs: Any) -> None:
        """
        The diagnostic refresh request definition.
        
        @since 3.17.0
    
        *Generated from the TypeScript documentation*
        """
        result_json = await self.send_request("workspace/diagnostic/refresh", None, **kwargs)
        return json_assert_type_null(result_json)
    
    async def send_initialize(self, params: "InitializeParams", **kwargs: Any) -> "InitializeResult":
        """
        The initialize request is sent from the client to the server.
        It is sent once as the request after starting up the server.
        The requests parameter is of type [InitializeParams](#InitializeParams)
        the response if of type [InitializeResult](#InitializeResult) of a Thenable that
        resolves to such.
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("initialize", params_json, **kwargs)
        return InitializeResult.from_json(json_assert_type_object(result_json))
    
    async def send_shutdown(self, **kwargs: Any) -> None:
        """
        A shutdown request is sent from the client to the server.
        It is sent once when the client decides to shutdown the
        server. The only notification that is sent after a shutdown request
        is the exit event.
    
        *Generated from the TypeScript documentation*
        """
        result_json = await self.send_request("shutdown", None, **kwargs)
        return json_assert_type_null(result_json)
    
    async def send_text_document_will_save_wait_until(self, params: "WillSaveTextDocumentParams", **kwargs: Any) -> Union[List["TextEdit"], None]:
        """
        A document will save request is sent from the client to the server before
        the document is actually saved. The request can return an array of TextEdits
        which will be applied to the text document before it is saved. Please note that
        clients might drop results if computing the text edits took too long or if a
        server constantly fails on this request. This is done to keep the save fast and
        reliable.
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("textDocument/willSaveWaitUntil", params_json, **kwargs)
        return parse_or_type((result_json), (lambda v: [TextEdit.from_json(json_assert_type_object(i)) for i in json_assert_type_array(v)], lambda v: json_assert_type_null(v)))
    
    async def send_text_document_completion(self, params: "CompletionParams", **kwargs: Any) -> Union[List["CompletionItem"], "CompletionList", None]:
        """
        Request to request completion at a given text document position. The request's
        parameter is of type [TextDocumentPosition](#TextDocumentPosition) the response
        is of type [CompletionItem[]](#CompletionItem) or [CompletionList](#CompletionList)
        or a Thenable that resolves to such.
        
        The request can delay the computation of the [`detail`](#CompletionItem.detail)
        and [`documentation`](#CompletionItem.documentation) properties to the `completionItem/resolve`
        request. However, properties that are needed for the initial sorting and filtering, like `sortText`,
        `filterText`, `insertText`, and `textEdit`, must not be changed during resolve.
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("textDocument/completion", params_json, **kwargs)
        return parse_or_type((result_json), (lambda v: [CompletionItem.from_json(json_assert_type_object(i)) for i in json_assert_type_array(v)], lambda v: CompletionList.from_json(json_assert_type_object(v)), lambda v: json_assert_type_null(v)))
    
    async def send_completion_item_resolve(self, params: "CompletionItem", **kwargs: Any) -> "CompletionItem":
        """
        Request to resolve additional information for a given completion item.The request's
        parameter is of type [CompletionItem](#CompletionItem) the response
        is of type [CompletionItem](#CompletionItem) or a Thenable that resolves to such.
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("completionItem/resolve", params_json, **kwargs)
        return CompletionItem.from_json(json_assert_type_object(result_json))
    
    async def send_text_document_hover(self, params: "HoverParams", **kwargs: Any) -> Union["Hover", None]:
        """
        Request to request hover information at a given text document position. The request's
        parameter is of type [TextDocumentPosition](#TextDocumentPosition) the response is of
        type [Hover](#Hover) or a Thenable that resolves to such.
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("textDocument/hover", params_json, **kwargs)
        return parse_or_type((result_json), (lambda v: Hover.from_json(json_assert_type_object(v)), lambda v: json_assert_type_null(v)))
    
    async def send_text_document_signature_help(self, params: "SignatureHelpParams", **kwargs: Any) -> Union["SignatureHelp", None]:
        """
    
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("textDocument/signatureHelp", params_json, **kwargs)
        return parse_or_type((result_json), (lambda v: SignatureHelp.from_json(json_assert_type_object(v)), lambda v: json_assert_type_null(v)))
    
    async def send_text_document_definition(self, params: "DefinitionParams", **kwargs: Any) -> Union["Definition", List["DefinitionLink"], None]:
        """
        A request to resolve the definition location of a symbol at a given text
        document position. The request's parameter is of type [TextDocumentPosition]
        (#TextDocumentPosition) the response is of either type [Definition](#Definition)
        or a typed array of [DefinitionLink](#DefinitionLink) or a Thenable that resolves
        to such.
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("textDocument/definition", params_json, **kwargs)
        return parse_or_type((result_json), (lambda v: parse_Definition((v)), lambda v: [parse_DefinitionLink(json_assert_type_object(i)) for i in json_assert_type_array(v)], lambda v: json_assert_type_null(v)))
    
    async def send_text_document_references(self, params: "ReferenceParams", **kwargs: Any) -> Union[List["Location"], None]:
        """
        A request to resolve project-wide references for the symbol denoted
        by the given text document position. The request's parameter is of
        type [ReferenceParams](#ReferenceParams) the response is of type
        [Location[]](#Location) or a Thenable that resolves to such.
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("textDocument/references", params_json, **kwargs)
        return parse_or_type((result_json), (lambda v: [Location.from_json(json_assert_type_object(i)) for i in json_assert_type_array(v)], lambda v: json_assert_type_null(v)))
    
    async def send_text_document_document_highlight(self, params: "DocumentHighlightParams", **kwargs: Any) -> Union[List["DocumentHighlight"], None]:
        """
        Request to resolve a [DocumentHighlight](#DocumentHighlight) for a given
        text document position. The request's parameter is of type [TextDocumentPosition]
        (#TextDocumentPosition) the request response is of type [DocumentHighlight[]]
        (#DocumentHighlight) or a Thenable that resolves to such.
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("textDocument/documentHighlight", params_json, **kwargs)
        return parse_or_type((result_json), (lambda v: [DocumentHighlight.from_json(json_assert_type_object(i)) for i in json_assert_type_array(v)], lambda v: json_assert_type_null(v)))
    
    async def send_text_document_document_symbol(self, params: "DocumentSymbolParams", **kwargs: Any) -> Union[List["SymbolInformation"], List["DocumentSymbol"], None]:
        """
        A request to list all symbols found in a given text document. The request's
        parameter is of type [TextDocumentIdentifier](#TextDocumentIdentifier) the
        response is of type [SymbolInformation[]](#SymbolInformation) or a Thenable
        that resolves to such.
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("textDocument/documentSymbol", params_json, **kwargs)
        return parse_or_type((result_json), (lambda v: [SymbolInformation.from_json(json_assert_type_object(i)) for i in json_assert_type_array(v)], lambda v: [DocumentSymbol.from_json(json_assert_type_object(i)) for i in json_assert_type_array(v)], lambda v: json_assert_type_null(v)))
    
    async def send_text_document_code_action(self, params: "CodeActionParams", **kwargs: Any) -> Union[List[Union["Command", "CodeAction"]], None]:
        """
        A request to provide commands for the given text document and range.
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("textDocument/codeAction", params_json, **kwargs)
        return parse_or_type((result_json), (lambda v: [parse_or_type((i), (lambda v: Command.from_json(json_assert_type_object(v)), lambda v: CodeAction.from_json(json_assert_type_object(v)))) for i in json_assert_type_array(v)], lambda v: json_assert_type_null(v)))
    
    async def send_code_action_resolve(self, params: "CodeAction", **kwargs: Any) -> "CodeAction":
        """
        Request to resolve additional information for a given code action.The request's
        parameter is of type [CodeAction](#CodeAction) the response
        is of type [CodeAction](#CodeAction) or a Thenable that resolves to such.
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("codeAction/resolve", params_json, **kwargs)
        return CodeAction.from_json(json_assert_type_object(result_json))
    
    async def send_workspace_symbol(self, params: "WorkspaceSymbolParams", **kwargs: Any) -> Union[List["SymbolInformation"], List["WorkspaceSymbol"], None]:
        """
        A request to list project-wide symbols matching the query string given
        by the [WorkspaceSymbolParams](#WorkspaceSymbolParams). The response is
        of type [SymbolInformation[]](#SymbolInformation) or a Thenable that
        resolves to such.
        
        @since 3.17.0 - support for WorkspaceSymbol in the returned data. Clients
         need to advertise support for WorkspaceSymbols via the client capability
         `workspace.symbol.resolveSupport`.
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("workspace/symbol", params_json, **kwargs)
        return parse_or_type((result_json), (lambda v: [SymbolInformation.from_json(json_assert_type_object(i)) for i in json_assert_type_array(v)], lambda v: [WorkspaceSymbol.from_json(json_assert_type_object(i)) for i in json_assert_type_array(v)], lambda v: json_assert_type_null(v)))
    
    async def send_workspace_symbol_resolve(self, params: "WorkspaceSymbol", **kwargs: Any) -> "WorkspaceSymbol":
        """
        A request to resolve the range inside the workspace
        symbol's location.
        
        @since 3.17.0
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("workspaceSymbol/resolve", params_json, **kwargs)
        return WorkspaceSymbol.from_json(json_assert_type_object(result_json))
    
    async def send_text_document_code_lens(self, params: "CodeLensParams", **kwargs: Any) -> Union[List["CodeLens"], None]:
        """
        A request to provide code lens for the given text document.
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("textDocument/codeLens", params_json, **kwargs)
        return parse_or_type((result_json), (lambda v: [CodeLens.from_json(json_assert_type_object(i)) for i in json_assert_type_array(v)], lambda v: json_assert_type_null(v)))
    
    async def send_code_lens_resolve(self, params: "CodeLens", **kwargs: Any) -> "CodeLens":
        """
        A request to resolve a command for a given code lens.
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("codeLens/resolve", params_json, **kwargs)
        return CodeLens.from_json(json_assert_type_object(result_json))
    
    async def send_text_document_document_link(self, params: "DocumentLinkParams", **kwargs: Any) -> Union[List["DocumentLink"], None]:
        """
        A request to provide document links
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("textDocument/documentLink", params_json, **kwargs)
        return parse_or_type((result_json), (lambda v: [DocumentLink.from_json(json_assert_type_object(i)) for i in json_assert_type_array(v)], lambda v: json_assert_type_null(v)))
    
    async def send_document_link_resolve(self, params: "DocumentLink", **kwargs: Any) -> "DocumentLink":
        """
        Request to resolve additional information for a given document link. The request's
        parameter is of type [DocumentLink](#DocumentLink) the response
        is of type [DocumentLink](#DocumentLink) or a Thenable that resolves to such.
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("documentLink/resolve", params_json, **kwargs)
        return DocumentLink.from_json(json_assert_type_object(result_json))
    
    async def send_text_document_formatting(self, params: "DocumentFormattingParams", **kwargs: Any) -> Union[List["TextEdit"], None]:
        """
        A request to to format a whole document.
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("textDocument/formatting", params_json, **kwargs)
        return parse_or_type((result_json), (lambda v: [TextEdit.from_json(json_assert_type_object(i)) for i in json_assert_type_array(v)], lambda v: json_assert_type_null(v)))
    
    async def send_text_document_range_formatting(self, params: "DocumentRangeFormattingParams", **kwargs: Any) -> Union[List["TextEdit"], None]:
        """
        A request to to format a range in a document.
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("textDocument/rangeFormatting", params_json, **kwargs)
        return parse_or_type((result_json), (lambda v: [TextEdit.from_json(json_assert_type_object(i)) for i in json_assert_type_array(v)], lambda v: json_assert_type_null(v)))
    
    async def send_text_document_on_type_formatting(self, params: "DocumentOnTypeFormattingParams", **kwargs: Any) -> Union[List["TextEdit"], None]:
        """
        A request to format a document on type.
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("textDocument/onTypeFormatting", params_json, **kwargs)
        return parse_or_type((result_json), (lambda v: [TextEdit.from_json(json_assert_type_object(i)) for i in json_assert_type_array(v)], lambda v: json_assert_type_null(v)))
    
    async def send_text_document_rename(self, params: "RenameParams", **kwargs: Any) -> Union["WorkspaceEdit", None]:
        """
        A request to rename a symbol.
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("textDocument/rename", params_json, **kwargs)
        return parse_or_type((result_json), (lambda v: WorkspaceEdit.from_json(json_assert_type_object(v)), lambda v: json_assert_type_null(v)))
    
    async def send_text_document_prepare_rename(self, params: "PrepareRenameParams", **kwargs: Any) -> Union["PrepareRenameResult", None]:
        """
        A request to test and perform the setup necessary for a rename.
        
        @since 3.16 - support for default behavior
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("textDocument/prepareRename", params_json, **kwargs)
        return parse_or_type((result_json), (lambda v: parse_PrepareRenameResult((v)), lambda v: json_assert_type_null(v)))
    
    async def send_workspace_execute_command(self, params: "ExecuteCommandParams", **kwargs: Any) -> Union["LSPAny", None]:
        """
        A request send from the client to the server to execute a command. The request might return
        a workspace edit which the client will apply to the workspace.
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        result_json = await self.send_request("workspace/executeCommand", params_json, **kwargs)
        return parse_or_type((result_json), (lambda v: parse_LSPAny((v)), lambda v: json_assert_type_null(v)))

    async def send_workspace_did_change_workspace_folders(self, params: "DidChangeWorkspaceFoldersParams") -> None:
        """
        The `workspace/didChangeWorkspaceFolders` notification is sent from the client to the server when the workspace
        folder configuration changes.
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        await self.send_notification("workspace/didChangeWorkspaceFolders", params_json)
    
    async def send_window_work_done_progress_cancel(self, params: "WorkDoneProgressCancelParams") -> None:
        """
        The `window/workDoneProgress/cancel` notification is sent from  the client to the server to cancel a progress
        initiated on the server side.
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        await self.send_notification("window/workDoneProgress/cancel", params_json)
    
    async def send_workspace_did_create_files(self, params: "CreateFilesParams") -> None:
        """
        The did create files notification is sent from the client to the server when
        files were created from within the client.
        
        @since 3.16.0
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        await self.send_notification("workspace/didCreateFiles", params_json)
    
    async def send_workspace_did_rename_files(self, params: "RenameFilesParams") -> None:
        """
        The did rename files notification is sent from the client to the server when
        files were renamed from within the client.
        
        @since 3.16.0
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        await self.send_notification("workspace/didRenameFiles", params_json)
    
    async def send_workspace_did_delete_files(self, params: "DeleteFilesParams") -> None:
        """
        The will delete files request is sent from the client to the server before files are actually
        deleted as long as the deletion is triggered from within the client.
        
        @since 3.16.0
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        await self.send_notification("workspace/didDeleteFiles", params_json)
    
    async def send_notebook_document_did_open(self, params: "DidOpenNotebookDocumentParams") -> None:
        """
        A notification sent when a notebook opens.
        
        @since 3.17.0
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        await self.send_notification("notebookDocument/didOpen", params_json)
    
    async def send_notebook_document_did_change(self, params: "DidChangeNotebookDocumentParams") -> None:
        """
    
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        await self.send_notification("notebookDocument/didChange", params_json)
    
    async def send_notebook_document_did_save(self, params: "DidSaveNotebookDocumentParams") -> None:
        """
        A notification sent when a notebook document is saved.
        
        @since 3.17.0
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        await self.send_notification("notebookDocument/didSave", params_json)
    
    async def send_notebook_document_did_close(self, params: "DidCloseNotebookDocumentParams") -> None:
        """
        A notification sent when a notebook closes.
        
        @since 3.17.0
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        await self.send_notification("notebookDocument/didClose", params_json)
    
    async def send_initialized(self, params: "InitializedParams") -> None:
        """
        The initialized notification is sent from the client to the
        server after the client is fully initialized and the server
        is allowed to send requests from the server to the client.
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        await self.send_notification("initialized", params_json)
    
    async def send_exit(self) -> None:
        """
        The exit event is sent from the client to the server to
        ask the server to exit its process.
    
        *Generated from the TypeScript documentation*
        """
        await self.send_notification("exit", None)
    
    async def send_workspace_did_change_configuration(self, params: "DidChangeConfigurationParams") -> None:
        """
        The configuration change notification is sent from the client to the server
        when the client's configuration has changed. The notification contains
        the changed configuration as defined by the language client.
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        await self.send_notification("workspace/didChangeConfiguration", params_json)
    
    async def send_text_document_did_open(self, params: "DidOpenTextDocumentParams") -> None:
        """
        The document open notification is sent from the client to the server to signal
        newly opened text documents. The document's truth is now managed by the client
        and the server must not try to read the document's truth using the document's
        uri. Open in this sense means it is managed by the client. It doesn't necessarily
        mean that its content is presented in an editor. An open notification must not
        be sent more than once without a corresponding close notification send before.
        This means open and close notification must be balanced and the max open count
        is one.
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        await self.send_notification("textDocument/didOpen", params_json)
    
    async def send_text_document_did_change(self, params: "DidChangeTextDocumentParams") -> None:
        """
        The document change notification is sent from the client to the server to signal
        changes to a text document.
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        await self.send_notification("textDocument/didChange", params_json)
    
    async def send_text_document_did_close(self, params: "DidCloseTextDocumentParams") -> None:
        """
        The document close notification is sent from the client to the server when
        the document got closed in the client. The document's truth now exists where
        the document's uri points to (e.g. if the document's uri is a file uri the
        truth now exists on disk). As with the open notification the close notification
        is about managing the document's content. Receiving a close notification
        doesn't mean that the document was open in an editor before. A close
        notification requires a previous open notification to be sent.
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        await self.send_notification("textDocument/didClose", params_json)
    
    async def send_text_document_did_save(self, params: "DidSaveTextDocumentParams") -> None:
        """
        The document save notification is sent from the client to the server when
        the document got saved in the client.
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        await self.send_notification("textDocument/didSave", params_json)
    
    async def send_text_document_will_save(self, params: "WillSaveTextDocumentParams") -> None:
        """
        A document will save notification is sent from the client to the server before
        the document is actually saved.
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        await self.send_notification("textDocument/willSave", params_json)
    
    async def send_workspace_did_change_watched_files(self, params: "DidChangeWatchedFilesParams") -> None:
        """
        The watched files notification is sent from the client to the server when
        the client detects changes to file watched by the language client.
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        await self.send_notification("workspace/didChangeWatchedFiles", params_json)
    
    async def send_s_set_trace(self, params: "SetTraceParams") -> None:
        """
    
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        await self.send_notification("$/setTrace", params_json)
    
    async def send_s_cancel_request(self, params: "CancelParams") -> None:
        """
    
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        await self.send_notification("$/cancelRequest", params_json)
    
    async def send_s_progress(self, params: "ProgressParams") -> None:
        """
    
    
        *Generated from the TypeScript documentation*
        """
        params_json = params.to_json()
        await self.send_notification("$/progress", params_json)
