from abc import ABC, abstractmethod
from dataclasses import dataclass
from types import TracebackType
from typing import Any, Dict, List, Optional, Tuple, Type, Union

import change_ls._location_list as ll
import change_ls._text_document as td
import change_ls._workspace as ws
import change_ls.types as lsptypes
from change_ls._change_ls_error import ChangeLSError
from change_ls._client import Client
from change_ls.types import (DeclarationParams, DefinitionParams,
                             ImplementationParams, Location, Position,
                             ReferenceContext, ReferenceParams, RenameParams,
                             SymbolKind, SymbolTag, TextDocumentIdentifier,
                             TypeDefinitionParams, WorkspaceEdit)


@dataclass
class _SymbolAnchor:
    text_document: "td.TextDocument"
    position: Position

    _original_uri: str
    _original_version: int

    def __init__(self, text_document: "td.TextDocument", position: Position) -> None:
        self.text_document = text_document
        self.position = position
        self._original_uri = text_document.uri
        self._original_version = text_document.version

    def is_valid(self) -> bool:
        return (not self.text_document.is_closed()
                and self.text_document.uri == self._original_uri
                and self.text_document.version == self._original_version)


@dataclass
class Symbol(ABC):
    """
    A ``Symbol`` represents a symbol in a :class:`TextDocument`. This is the base class for more specific kinds
    of ``Symbols`` and provides the basic methods and properties available on all ``Symbols``.

    A ``Symbol`` keeps a reference to the ``TextDocument`` it was obtained from. If the document changes or is closed,
    the Symbol will be invalidated and its methods can no longer be used.

    .. property:: name
        :type: str

        The name of this ``Symbol``.

    .. property:: uri
        :type: str

        The URI of the ``TextDocument`` from which the ``Symbol`` was sourced. Depending
        on how the ``Symbol`` was obtained, this need not be the document in which the ``Symbol``
        is defined, but can be any document which contains a reference to this ``Symbol``.

    .. property:: range
        :type: Tuple[int, int]

        The range [start offset, end offset] in the ``TextDocument`` which contains this reference to the ``Symbol``.

    .. property:: kind
        :type: change_ls.types.SymbolKind

        The :class:`SymbolKind` of this ``Symbold``, which describes which element of the language (e.g. class, function)
        this ``Symbol`` represents.

    .. property:: tags
        :type: List[SymbolTag]

        The list of :class:`SymbolTags <SymbolTag>` for this ``Symbol``. ``SymbolTags`` add additional information to a ``Symbol``.
        Currently the only ``SymbolTag`` is ``Deprecated``.

    .. property:: container_name
        :type: Optional[str]

        The name of the ``Symbol`` containing this ``Symbol``. This information is for
        user interface purposes (e.g. to render a qualifier in the user interface
        if necessary). It can't be used to re-infer a hierarchy for Symbols.
    """

    _workspace: ws.Workspace
    _client: Client

    @abstractmethod
    def _get_anchor(self) -> _SymbolAnchor: ...

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def uri(self) -> str: ...

    @property
    @abstractmethod
    def range(self) -> Tuple[int, int]: ...

    @property
    @abstractmethod
    def kind(self) -> SymbolKind: ...

    @property
    @abstractmethod
    def tags(self) -> List[SymbolTag]: ...

    @property
    @abstractmethod
    def container_name(self) -> Optional[str]: ...

    def is_valid(self) -> bool:
        """
        Checks whether a ``Symbol`` is still valid.
        Symbols are invalidated when their underlying :class:`TextDocument`
        changes.
        """
        return self._get_anchor().is_valid()

    def _assert_valid(self) -> None:
        if not self.is_valid():
            raise ChangeLSError("Symbol is no longer valid")

    async def get_rename_workspace_edit(self, new_name: str) -> Optional[WorkspaceEdit]:
        """
        Returns a :class:`WorkspaceEdit` which renames this ``Symbol`` to ``new_name``.

        This edit can be applied by calling :meth:`Workspace.perform_edit_and_save()`.
        """
        self._assert_valid()
        anchor = self._get_anchor()
        if not self._client.check_feature("textDocument/rename", text_documents=[anchor.text_document]):
            raise ChangeLSError(f"Client {self._client.get_name()} does not support renaming.")

        params = RenameParams(
            textDocument=TextDocumentIdentifier(uri=anchor.text_document.uri), position=anchor.position, newName=new_name)
        return await self._client.send_text_document_rename(params)

    async def find_references(self, *, include_declaration: bool = True) -> "ll.LocationList":
        """
        Returns all references to this ``Symbol`` within its :class:`Workspace`.

        :param include_declaration: Whether to include the declaration of the symbol in the returned list of locations.
        """
        self._assert_valid()
        anchor = self._get_anchor()
        if not self._client.check_feature("textDocument/references", text_documents=[anchor.text_document]):
            raise ChangeLSError(f"Client {self._client.get_name()} does not support find_references.")

        res = await self._client.send_text_document_references(ReferenceParams(
            textDocument=TextDocumentIdentifier(uri=anchor.text_document.uri),
            position=anchor.position,
            context=ReferenceContext(includeDeclaration=include_declaration)))
        if res is None:
            res = []
        return ll.LocationList.from_lsp_locations(self._workspace, res)

    async def find_declaration(self) -> "ll.LocationList":
        """
        Returns the declaration sites of this ``Symbol``.

        For most languages, this is a single location which can be retrieved from the return value like this::

            text_document, (start, end) = (await symbol.find_declaration()).get_single_entry()
        """
        self._assert_valid()
        anchor = self._get_anchor()
        if not self._client.check_feature("textDocument/declaration", text_documents=[anchor.text_document]):
            raise ChangeLSError(f"Client {self._client.get_name()} does not support find_declaration.")

        res = await self._client.send_text_document_declaration(
            DeclarationParams(textDocument=TextDocumentIdentifier(uri=anchor.text_document.uri), position=anchor.position))
        if res is None:
            res = []
        return ll.LocationList.from_lsp_locations(self._workspace, res)

    async def find_definition(self) -> "ll.LocationList":
        """
        Returns the definition sites of this ``Symbol``.

        For most languages, this is a single location which can be retrieved from the return value like this::

            text_document, (start, end) = (await symbol.find_definition()).get_single_entry()
        """
        self._assert_valid()
        anchor = self._get_anchor()
        if not self._client.check_feature("textDocument/definition", text_documents=[anchor.text_document]):
            raise ChangeLSError(f"Client {self._client.get_name()} does not support find_definition.")

        res = await self._client.send_text_document_definition(
            DefinitionParams(textDocument=TextDocumentIdentifier(uri=anchor.text_document.uri), position=anchor.position))
        if res is None:
            res = []
        return ll.LocationList.from_lsp_locations(self._workspace, res)

    async def find_type_definition(self) -> "ll.LocationList":
        """
        Returns the type definition sites of this ``Symbol``.

        For most languages, this is a single location which can be retrieved from the return value like this::

            text_document, (start, end) = (await symbol.find_type_definition()).get_single_entry()
        """
        self._assert_valid()
        anchor = self._get_anchor()
        if not self._client.check_feature("textDocument/typeDefinition", text_documents=[anchor.text_document]):
            raise ChangeLSError(f"Client {self._client.get_name()} does not support find_type_definition.")

        res = await self._client.send_text_document_type_definition(
            TypeDefinitionParams(textDocument=TextDocumentIdentifier(uri=anchor.text_document.uri), position=anchor.position))
        if res is None:
            res = []
        return ll.LocationList.from_lsp_locations(self._workspace, res)

    async def find_implementation(self) -> "ll.LocationList":
        """
        Returns the implementation sites of this ``Symbol``.

        For most languages, this is a single location which can be retrieved from the return value like this::

            text_document, (start, end) = (await symbol.find_implementation()).get_single_entry()
        """
        self._assert_valid()
        anchor = self._get_anchor()
        if not self._client.check_feature("textDocument/implementation", text_documents=[anchor.text_document]):
            raise ChangeLSError(f"Client {self._client.get_name()} does not support find_implementation.")

        res = await self._client.send_text_document_implementation(
            ImplementationParams(textDocument=TextDocumentIdentifier(uri=anchor.text_document.uri), position=anchor.position))
        if res is None:
            res = []
        return ll.LocationList.from_lsp_locations(self._workspace, res)

    def __str__(self) -> str:
        if self.is_valid():
            anchor = self._get_anchor()
            return f"{self.name}@{anchor.text_document.uri}:{anchor.position.line}:{anchor.position.character}"
        else:
            return "INVALIDED SYMBOL!"

    def _get_repr_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "uri": self.uri,
            "range": self.range,
            "kind": self.kind,
            "tags": self.tags,
            "container_name": self.container_name
        }

    def __repr__(self) -> str:
        if self.is_valid():
            status = " "
        else:
            status = " INVALIDED SYMBOL! "

        return f"{object.__repr__(self)}{status}{self._get_repr_dict()!r}"


class CustomSymbol(Symbol):
    """
    A :class:`Symbol` which was created directly by the user based on a location in a :class:`TextDocument`,
    as opposed to being return by an LSP-request. A ``CustomSymbol`` has all of the methods and attributes
    from ``Symbol`` but does not add any features of its own.
    """

    _anchor: _SymbolAnchor
    _name: str
    _uri: str
    _range: Tuple[int, int]
    _kind: SymbolKind
    _tags: List[SymbolTag]
    _container_name: Optional[str]

    def __init__(self, client: Client, text_document: "td.TextDocument", range: Tuple[int, int], kind: SymbolKind,
                 tags: Optional[List[SymbolTag]] = None, container_name: Optional[str] = None) -> None:
        if range[0] >= range[1]:
            raise ValueError("Invalid range for CustomSymbol")
        self._client = client
        self._workspace = text_document._workspace  # type: ignore
        self._name = text_document.text[range[0]:range[1]]
        self._uri = text_document.uri
        self._range = range
        self._kind = kind
        self._tags = list(tags) if tags is not None else []
        self._container_name = container_name

        position = text_document.offset_to_position(range[0], client.get_name())
        self._anchor = _SymbolAnchor(text_document, position)

    def _get_anchor(self) -> _SymbolAnchor:
        return self._anchor

    @property
    def name(self) -> str:
        return self._name

    @property
    def uri(self) -> str:
        return self._uri

    @property
    def range(self) -> Tuple[int, int]:
        return self._range

    @property
    def kind(self) -> SymbolKind:
        return self._kind

    @property
    def tags(self) -> List[SymbolTag]:
        return self._tags

    @property
    def container_name(self) -> Optional[str]:
        return self._container_name


class UnresolvedWorkspaceSymbol:
    """
    An early stage of a :class:`WorkspaceSymbol` which may not yet contain all properties
    of a complete ``WorkspaceSymbol``. To obtain a ``WorkspaceSymbol`` from an ``UnresolvedWorkspaceSymbol``
    call :meth:`UnresolvedWorkspaceSymbol.resolve()`, which will also open the :class:`TextDocument` which contains
    the ``WorkspaceSymbol``.

    ``UnresolvedWorkspaceSymbols`` are used when a request returns a potentially large number of symbols, so that
    the language server does not have to compute all details for all symbols when only a few of them are actually used.

    While not inheriting from :class:`Symbol`, an ``UnresolvedWorkspaceSymbol`` contains the properties
    :attr:`~Symbol.name`, :attr:`~Symbol.uri`, :attr:`~Symbol.kind`, :attr:`~Symbol.tags` and :attr:`~Symbol.container_name`
    of ``Symbol``, however these properties might not have their final value yet (e.g. ``tags`` may be
    empty and ``container_name`` may be ``None``).
    """

    _workspace: ws.Workspace
    _client: Client
    _lsp_workspace_symbol: Union[lsptypes.WorkspaceSymbol, lsptypes.SymbolInformation]

    def __init__(self, client: Client, workspace: "ws.Workspace", lsp_workspace_symbol: Union[lsptypes.WorkspaceSymbol, lsptypes.SymbolInformation]) -> None:
        self._client = client
        self._workspace = workspace
        self._lsp_workspace_symbol = lsp_workspace_symbol

    async def resolve(self) -> "WorkspaceSymbol":
        """
        Resolves this ``UnresolvedWorkspaceSymbol`` into a full :class:`WorkspaceSymbol`.

        This will open the :class:`TextDocument` which contains this symbol.
        """
        if isinstance(self._lsp_workspace_symbol, lsptypes.WorkspaceSymbol) and self._client.check_feature("workspace/symbol", workspace_symbol_resolve=True):
            resolved_symbol = await self._client.send_workspace_symbol_resolve(self._lsp_workspace_symbol)
            return WorkspaceSymbol(self._client, self._workspace, resolved_symbol)
        else:
            return WorkspaceSymbol(self._client, self._workspace, self._lsp_workspace_symbol)

    @property
    def name(self) -> str:
        return self._lsp_workspace_symbol.name

    @property
    def uri(self) -> str:
        if isinstance(self._lsp_workspace_symbol.location, Location):
            return self._lsp_workspace_symbol.location.uri
        else:
            return self._lsp_workspace_symbol.location["uri"]

    @property
    def kind(self) -> SymbolKind:
        return self._lsp_workspace_symbol.kind

    @property
    def tags(self) -> List[SymbolTag]:
        return self._lsp_workspace_symbol.tags if self._lsp_workspace_symbol.tags is not None else []

    @property
    def container_name(self) -> Optional[str]:
        return self._lsp_workspace_symbol.containerName

    def __str__(self) -> str:
        return f"{self.name}@{self.uri}"

    def _get_repr_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "uri": self.uri,
            "kind": self.kind,
            "tags": self.tags,
            "container_name": self.container_name
        }

    def __repr__(self) -> str:
        return f"{object.__repr__(self)} {self._get_repr_dict()!r}"


class WorkspaceSymbol(UnresolvedWorkspaceSymbol, Symbol):
    """
    A :class:`Symbol` obtained through by querying the :class:`Workspace` for ``Symbols``.

    Since this ``Symbol`` is not obtained from an already open :class:`TextDocument`, it
    will automatically open the ``TextDocument`` it is contained in. For this reason,
    a ``WorkspaceSymbol`` is a context manager so that the referenced ``TextDocument`` can
    be closed when the ``WorkspaceSymbol`` is no longer needed. Like all ``Symbols``, closing
    the underlying ``TextDocument`` will invalidate the ``WorkspaceSymbol``.
    """

    _anchor: _SymbolAnchor
    _lsp_workspace_symbol: Union[lsptypes.WorkspaceSymbol, lsptypes.SymbolInformation]
    _range: Tuple[int, int]
    _is_closed: bool

    def __init__(self, client: Client, workspace: "ws.Workspace", lsp_workspace_symbol: Union[lsptypes.WorkspaceSymbol, lsptypes.SymbolInformation]) -> None:
        if not isinstance(lsp_workspace_symbol.location, Location):
            raise ChangeLSError("Client did not return a WorkspaceSymbol with filled range after resolve.")

        self._client = client
        self._workspace = workspace
        self._lsp_workspace_symbol = lsp_workspace_symbol
        text_document = workspace.open_text_document(self.uri)
        self._anchor = _SymbolAnchor(text_document, lsp_workspace_symbol.location.range.start)
        self._range = (text_document.position_to_offset(lsp_workspace_symbol.location.range.start),
                       text_document.position_to_offset(lsp_workspace_symbol.location.range.end))
        self._is_closed = False

    def _get_anchor(self) -> _SymbolAnchor:
        return self._anchor

    @property
    def range(self) -> Tuple[int, int]:
        return self._range

    def __enter__(self) -> "WorkspaceSymbol":
        return self

    def __exit__(self, exc_type: Type[Exception], exc_value: Exception, traceback: TracebackType) -> bool:
        self.close()
        return False

    def close(self) -> None:
        """
        Manually closes the :class:`TextDocument` that this ``WorkspaceSymbol`` is contained in.

        The ``TextDocument`` will only be closed once, calling this method multiple times has no effect.
        """
        if not self._is_closed:
            self._anchor.text_document.close()
        self._is_closed = True


class DocumentSymbol(Symbol):
    """
    A :class:`Symbol` which is part of a :class:`TextDocument`'s outline.

    In addition to the base properties provided by ``Symbol``, ``DocumentSymbol`` adds
    the following properties:

    .. property:: detail
        :type: Optional[str]

        Additional details for this symbol, e.g. the signature of a function.

    .. property:: symbol_range
        :type: Tuple[int, int]

        The range of this symbol, identical to :attr:`Symbol.range`.

    .. property:: context_range
        :type: Tuple[int, int]

        The range of this symbol with additional context included, e.g. visibility modifiers or comments.

    .. property:: parent
        :type: Optional[DocumentSymbol]

        The parent symbol. Unline :attr:`Symbol.container_name` this property and :attr:`~DocumentSymbol.children` do
        form a hierarchy.

    .. property:: children
        :type: Optional[List[DocumentSymbol]]

        The children of this symbol. If there are no children, this property can be either ``None`` or ``[]``, depending
        on whether the language server wants to indicate that a symbol is empty but can theoretically have children
        (e.g. a class without properties).
    """

    _text_document: "td.TextDocument"
    _lsp_symbol: Union[lsptypes.DocumentSymbol, lsptypes.SymbolInformation]
    _tags: List[SymbolTag]
    _context_range: Tuple[int, int]
    _symbol_range: Tuple[int, int]
    _parent: Optional["DocumentSymbol"]
    _children: Optional[List["DocumentSymbol"]]
    _anchor: _SymbolAnchor

    def __init__(self, client: Client, workspace: "ws.Workspace", text_document: "td.TextDocument",
                 lsp_symbol: Union[lsptypes.DocumentSymbol, lsptypes.SymbolInformation], parent: Optional["DocumentSymbol"]) -> None:
        self._client = client
        self._workspace = workspace
        self._text_document = text_document
        self._lsp_symbol = lsp_symbol
        self._tags = list(lsp_symbol.tags) if lsp_symbol.tags else []
        self._parent = parent

        if isinstance(lsp_symbol, lsptypes.DocumentSymbol):
            if lsp_symbol.children is not None:
                self._children = [DocumentSymbol(client, workspace, text_document, child, self)
                                  for child in lsp_symbol.children]
            else:
                self._children = None

            if lsp_symbol.deprecated:
                self._tags.append(SymbolTag.Deprecated)

            self._context_range = (text_document.position_to_offset(lsp_symbol.range.start),
                                   text_document.position_to_offset(lsp_symbol.range.end))
            self._symbol_range = (text_document.position_to_offset(lsp_symbol.selectionRange.start),
                                  text_document.position_to_offset(lsp_symbol.selectionRange.end))

            self._anchor = _SymbolAnchor(text_document, lsp_symbol.selectionRange.start)
        else:
            self._children = None
            self._context_range = (text_document.position_to_offset(lsp_symbol.location.range.start),
                                   text_document.position_to_offset(lsp_symbol.location.range.end))
            self._symbol_range = self._context_range

            self._anchor = _SymbolAnchor(text_document, lsp_symbol.location.range.start)

    def _get_anchor(self) -> _SymbolAnchor:
        return self._anchor

    @property
    def name(self) -> str:
        return self._lsp_symbol.name

    @property
    def uri(self) -> str:
        return self._text_document.uri

    @property
    def range(self) -> Tuple[int, int]:
        return self.symbol_range

    @property
    def symbol_range(self) -> Tuple[int, int]:
        return self._symbol_range

    @property
    def context_range(self) -> Tuple[int, int]:
        return self._context_range

    @property
    def detail(self) -> Optional[str]:
        if isinstance(self._lsp_symbol, lsptypes.DocumentSymbol):
            return self._lsp_symbol.detail
        else:
            return None

    @property
    def kind(self) -> SymbolKind:
        return self._lsp_symbol.kind

    @property
    def tags(self) -> List[SymbolTag]:
        return self._lsp_symbol.tags if self._lsp_symbol.tags is not None else []

    @property
    def container_name(self) -> Optional[str]:
        if self._parent is not None:
            return self._parent.name
        elif isinstance(self._lsp_symbol, lsptypes.SymbolInformation):
            return self._lsp_symbol.containerName
        else:
            return None

    @property
    def parent(self) -> Optional["DocumentSymbol"]:
        return self._parent

    @property
    def children(self) -> Optional[List["DocumentSymbol"]]:
        return self._children

    def __repr__(self) -> str:
        if self.is_valid():
            status = " "
        else:
            status = " INVALIDED SYMBOL! "

        values = self._get_repr_dict()
        values.update({
            "symbol_range": self.symbol_range,
            "context_range": self.context_range,
            # Use the informal str representation for parent and children
            # to not print huge sections of the document outline every time.
            "parent": str(self.parent),
            "children": [str(c) for c in self.children] if self.children else None
        })
        return f"{object.__repr__(self)}{status}{values!r}"
