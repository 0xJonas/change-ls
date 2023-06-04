from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Tuple

import lspscript.text_document as td
import lspscript.workspace as ws
from lspscript.client import Client
from lspscript.location_list import LocationList
from lspscript.lsp_exception import LSPScriptException
from lspscript.types.enumerations import SymbolKind, SymbolTag
from lspscript.types.structures import (DeclarationParams, DefinitionParams,
                                        ImplementationParams, Position,
                                        ReferenceContext, ReferenceParams,
                                        RenameParams, TextDocumentIdentifier,
                                        TypeDefinitionParams, WorkspaceEdit)
from lspscript.util import TextDocumentInfo


@dataclass
class _SymbolAnchor:
    info: TextDocumentInfo
    position: Position


@dataclass
class _Symbol(ABC):
    _workspace: ws.Workspace
    _client: Client
    name: str
    uri: str
    kind: SymbolKind
    tags: List[SymbolTag]
    container_name: Optional[str]

    @abstractmethod
    def _get_anchor(self) -> _SymbolAnchor: ...

    async def get_rename_workspace_edit(self, new_name: str) -> Optional[WorkspaceEdit]:
        """
        Returns a :class:`WorkspaceEdit` which renames this ``Symbol`` to ``new_name``.

        This edit can be applied by calling :meth:`Workspace.perform_edit_and_save()`.
        """
        anchor = self._get_anchor()
        if not self._client.check_feature("textDocument/rename", text_documents=[anchor.info]):
            raise LSPScriptException(f"Client {self._client.get_name()} does not support renaming.")

        params = RenameParams(
            textDocument=TextDocumentIdentifier(uri=anchor.info.uri), position=anchor.position, newName=new_name)
        return await self._client.send_text_document_rename(params)

    async def find_references(self, *, include_declaration: bool = True) -> LocationList:
        """
        Returns all references to this ``Symbol`` within its :class:`Workspace`.

        :param include_declaration: Whether to include the declaration of the symbol in the returned list of locations.
        """
        anchor = self._get_anchor()
        if not self._client.check_feature("textDocument/references", text_documents=[anchor.info]):
            raise LSPScriptException(f"Client {self._client.get_name()} does not support find_references.")

        res = await self._client.send_text_document_references(ReferenceParams(
            textDocument=TextDocumentIdentifier(uri=anchor.info.uri),
            position=anchor.position,
            context=ReferenceContext(includeDeclaration=include_declaration)))
        if res is None:
            res = []
        return LocationList.from_lsp_locations(self._workspace, res)

    async def find_declaration(self) -> LocationList:
        """
        Returns the declaration sites of this ``Symbol``.

        For most languages, this is a single location which can be retrieved from the return value like this::

            text_document, (start, end) = (await symbol.find_declaration()).get_single_entry()
        """
        anchor = self._get_anchor()
        if not self._client.check_feature("textDocument/declaration", text_documents=[anchor.info]):
            raise LSPScriptException(f"Client {self._client.get_name()} does not support find_declaration.")

        res = await self._client.send_text_document_declaration(
            DeclarationParams(textDocument=TextDocumentIdentifier(uri=anchor.info.uri), position=anchor.position))
        if res is None:
            res = []
        return LocationList.from_lsp_locations(self._workspace, res)

    async def find_definition(self) -> LocationList:
        """
        Returns the definition sites of this ``Symbol``.

        For most languages, this is a single location which can be retrieved from the return value like this::

            text_document, (start, end) = (await symbol.find_definition()).get_single_entry()
        """
        anchor = self._get_anchor()
        if not self._client.check_feature("textDocument/definition", text_documents=[anchor.info]):
            raise LSPScriptException(f"Client {self._client.get_name()} does not support find_definition.")

        res = await self._client.send_text_document_definition(
            DefinitionParams(textDocument=TextDocumentIdentifier(uri=anchor.info.uri), position=anchor.position))
        if res is None:
            res = []
        return LocationList.from_lsp_locations(self._workspace, res)

    async def find_type_definition(self) -> LocationList:
        """
        Returns the type definition sites of this ``Symbol``.

        For most languages, this is a single location which can be retrieved from the return value like this::

            text_document, (start, end) = (await symbol.find_type_definition()).get_single_entry()
        """
        anchor = self._get_anchor()
        if not self._client.check_feature("textDocument/typeDefinition", text_documents=[anchor.info]):
            raise LSPScriptException(f"Client {self._client.get_name()} does not support find_type_definition.")

        res = await self._client.send_text_document_type_definition(
            TypeDefinitionParams(textDocument=TextDocumentIdentifier(uri=anchor.info.uri), position=anchor.position))
        if res is None:
            res = []
        return LocationList.from_lsp_locations(self._workspace, res)

    async def find_implementation(self) -> LocationList:
        """
        Returns the implementation sites of this ``Symbol``.

        For most languages, this is a single location which can be retrieved from the return value like this::

            text_document, (start, end) = (await symbol.find_implementation()).get_single_entry()
        """
        anchor = self._get_anchor()
        if not self._client.check_feature("textDocument/implementation", text_documents=[anchor.info]):
            raise LSPScriptException(f"Client {self._client.get_name()} does not support find_implementation.")

        res = await self._client.send_text_document_implementation(
            ImplementationParams(textDocument=TextDocumentIdentifier(uri=anchor.info.uri), position=anchor.position))
        if res is None:
            res = []
        return LocationList.from_lsp_locations(self._workspace, res)


class CustomSymbol(_Symbol):
    range: Tuple[int, int]
    _anchor: _SymbolAnchor

    def __init__(self, client: Client, text_document: "td.TextDocument", range: Tuple[int, int], kind: SymbolKind,
                 tags: Optional[List[SymbolTag]] = None, container_name: Optional[str] = None) -> None:
        if range[0] >= range[1]:
            raise ValueError("Invalid range for CustomSymbol")
        self._client = client
        self._workspace = text_document._workspace  # type: ignore
        self.uri = text_document.uri
        self.name = text_document.text[range[0]:range[1]]
        self.range = range
        self.kind = kind
        self.tags = list(tags) if tags is not None else []
        self.container_name = container_name

        position = text_document.offset_to_position(range[0], client.get_name())
        self._anchor = _SymbolAnchor(TextDocumentInfo(text_document.uri, text_document.language_id), position)

    def _get_anchor(self) -> _SymbolAnchor:
        return self._anchor
