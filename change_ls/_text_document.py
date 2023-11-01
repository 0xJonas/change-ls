import asyncio
import warnings
from bisect import bisect_right
from dataclasses import dataclass, field
from logging import LoggerAdapter
from pathlib import Path
from types import TracebackType
from typing import (TYPE_CHECKING, Any, Callable, Dict, List, Literal,
                    Optional, Type, overload)

import change_ls._symbol as sym
import change_ls._workspace as ws
from change_ls._change_ls_error import ChangeLSError
from change_ls._client import Client
from change_ls._util import TextDocumentInfo, guess_language_id
from change_ls.logging import _get_change_ls_default_logger  # type: ignore
from change_ls.logging import operation
from change_ls.tokens import SyntacticToken, TokenList, tokenize
from change_ls.tokens._semantic_tokens_mixin import (SemanticTokensMixin,
                                                     enrich_syntactic_tokens)
from change_ls.types import (DidChangeTextDocumentParams,
                             DidCloseTextDocumentParams,
                             DidSaveTextDocumentParams, DocumentSymbolParams,
                             OptionalVersionedTextDocumentIdentifier, Position,
                             PositionEncodingKind, Range, SymbolKind,
                             SymbolTag, TextDocumentContentChangeEvent,
                             TextDocumentIdentifier, TextDocumentItem,
                             TextDocumentSaveReason, TextDocumentSyncKind,
                             TextEdit, VersionedTextDocumentIdentifier,
                             WillSaveTextDocumentParams)


@dataclass(order=True)
class _Edit:
    from_offset: int
    to_offset: int
    new_text: str = field(compare=False)

    def overlaps(self, other: "_Edit") -> bool:
        covers_from_offset = self.from_offset <= other.from_offset and self.to_offset > other.from_offset
        covers_to_offset = self.from_offset < other.to_offset and self.to_offset >= other.to_offset

        # The '<' when comparing to_offset ensures that zero-length edits at the same position
        # will not overlap. Per the LSP-spec, these edits are applied in the order they are received.
        # The cases where to_offset is equal are already covered by the other conditions.
        covers_both = self.from_offset >= other.from_offset and self.to_offset < other.to_offset

        return covers_from_offset or covers_to_offset or covers_both

    def as_text_document_content_change_event(self, line_offsets: List[int]) -> TextDocumentContentChangeEvent:
        from_line = bisect_right(line_offsets, self.from_offset) - 1
        from_character = self.from_offset - line_offsets[from_line]
        from_position = Position(line=from_line, character=from_character)
        to_line = bisect_right(line_offsets, self.to_offset) - 1
        to_character = self.to_offset - line_offsets[to_line]
        to_position = Position(line=to_line, character=to_character)
        return {
            "text": self.new_text,
            "range": Range(start=from_position, end=to_position)
        }

    def __str__(self) -> str:
        if self.from_offset == self.to_offset:
            return f"Insert {self.new_text} at offset {self.from_offset}"
        elif self.new_text == "":
            return f"Delete characters in range [{self.from_offset}:{self.to_offset}]"
        else:
            return f"Change characters in range [{self.from_offset}:{self.to_offset}] to {self.new_text}"


class DroppedChangesWarning(Warning):
    """
    Warning category used when dropping changes when closing a TextDocument.
    """


def _skip_to_next_line(text: str, offset: int) -> int:
    for i in range(offset, len(text)):
        if text[i:i+2] == "\r\n":
            return i + 2
        if text[i] in ["\n", "\r"]:
            return i + 1
    return -1


def _calculate_line_offsets(text: str) -> List[int]:
    offset = 0
    line_offsets: List[int] = []
    # This loop will include trailing newlines. This is intentional because it
    # is needed for edits at the end of the file.
    while offset >= 0:
        line_offsets.append(offset)
        offset = _skip_to_next_line(text, offset)
    return line_offsets


def _utf_8_character_length(char: int) -> int:
    if char <= 0x7f:
        return 1
    elif char <= 0x7ff:
        return 2
    elif char <= 0xffff:
        return 3
    else:
        return 4


def _utf_16_character_length(char: int) -> int:
    if char <= 0xffff:
        return 1
    else:
        return 2


_code_units_to_character_length: Dict[PositionEncodingKind, Callable[[int], int]] = {
    PositionEncodingKind.UTF8: _utf_8_character_length,
    PositionEncodingKind.UTF16: _utf_16_character_length,
    PositionEncodingKind.UTF32: lambda _: 1,
}


def _code_units_to_offset(reference: str, code_units: int, encoding: PositionEncodingKind) -> int:
    get_character_length = _code_units_to_character_length[encoding]
    counter = 0
    for i, c in enumerate(reference):
        if counter == code_units:
            return i
        if counter > code_units:
            raise IndexError(f"Code unit {code_units} is not a valid codepoint boundary.")
        counter += get_character_length(ord(c))
    return len(reference)


def _offset_to_code_units(reference: str, offset: int, encoding: PositionEncodingKind) -> int:
    get_character_length = _code_units_to_character_length[encoding]
    return sum(get_character_length(ord(c)) for c in reference[:offset])


if TYPE_CHECKING:
    _LoggerAdapter = LoggerAdapter[Any]
else:
    _LoggerAdapter = LoggerAdapter


class TextDocument(TextDocumentInfo, SemanticTokensMixin):
    """
    A :class:`TextDocument` is a single file in a :class:`Workspace`, which can be edited or queried for information.

    ``TextDocuments`` are not instantiated directly, but are instead obtained by calling
    :meth:`~Workspace.open_text_document()` on a ``Workspace`` instance. The ``Workspace`` will automatically
    close the ``TextDocoment`` when it itself is closed. It is also possible to use the ``TextDocument`` itself
    with a ``with`` statement, or to close it manually using :meth:`close()`.

    Methods on a ``TextDocument`` can make use of all :class:`Clients <Client>` opened in the workspace it
    originated from. This includes ``Clients`` started after the ``TextDocument`` was opened.

    .. attribute:: text
        :type: str

        The contents of the ``TextDocument``.

    .. attribute:: language_id
        :type: str

        The id of the language used by this ``TextDocument``. This is either passed explicitly to ``open_text_document()`` or it is guessed from the file extension.

    .. attribute:: uri
        :type: str

        The URI of the document. Used do identify this ``TextDocument`` throughout the LSP.

    .. attribute:: version
        :type: int

        The ``TextDocument's`` version counter. Each change to the document increments this counter, e.g. calls to :meth:`commit_edits()`.

    .. attribute:: encoding
        :type: str

        The character encoding used by this ``TextDocument``.

    .. attribute:: tokens
        :type: TokenList | None

        The tokens for this document. This attribute is only populated after :meth:`load_tokens` has been called.
    """

    _text: str
    _version: int

    _path: Path
    _encoding: str
    _clients: Dict[str, Client]
    _workspace: "ws.Workspace"
    _tokens: Optional[TokenList[SyntacticToken]]
    _outlines: Dict[Client, List["sym.DocumentSymbol"]]
    _pending_edits: List[_Edit]
    _line_offsets: List[int]
    _reference_count: int
    _content_saved: bool
    _logger: _LoggerAdapter

    # Cache for position_to_offset, to speed up processing of semantic tokens
    _cached_line: int
    _cached_version: int
    _cached_start_offset: int
    _cached_reference_string: str

    def __init__(self, path: Path, workspace: "ws.Workspace", language_id: Optional[str] = None, version: int = 0, encoding: Optional[str] = None) -> None:
        self._path = path
        with path.open(encoding=encoding) as file:
            self._text = file.read()
            self._encoding = file.encoding

        if not language_id:
            guessed_id = guess_language_id(path)
            if not guessed_id:
                raise ChangeLSError(f"Unable to determine language id for '{str(path)}'")
            language_id = guessed_id

        self._version = version
        self._workspace = workspace
        self._tokens = None
        self._outlines = {}
        self._pending_edits = []
        self._line_offsets = _calculate_line_offsets(self._text)
        self._reference_count = 0
        self._content_saved = True

        self._cached_line = -1
        self._cached_version = -1
        self._cached_start_offset = -1
        self._cached_reference_string = ""

        uri = path.as_uri()
        TextDocumentInfo.__init__(self, uri, language_id)
        SemanticTokensMixin.__init__(self)

        self._logger = _get_change_ls_default_logger(
            "change-ls.workspace", cls_workspace=str(workspace._id), cls_text_document=uri)  # type: ignore

        self._reopen()

    @property
    def logger(self) -> _LoggerAdapter:
        return self._logger

    def _get_logger_from_context(self, *args: Any, **kwargs: Any) -> _LoggerAdapter:
        return self._logger

    def _reopen(self) -> None:
        self._reference_count += 1
        self.logger.info(f"Incremented reference count. New count is {self._reference_count}.")

    def _set_path(self, new_path: Path) -> None:
        del self._workspace._opened_text_documents[self.uri]  # type: ignore
        self._path = new_path
        self._uri = new_path.as_uri()
        self._workspace._opened_text_documents[self.uri] = self  # type: ignore

    async def rename_file(self, new_path: Path, *, overwrite: bool = False, ignore_if_exists: bool = False) -> None:
        """
        Renames this :class:`TextDocument` to ``new_path``.

        See :meth:`Workspace.rename_text_document`.
        """
        await self._workspace.rename_text_document(self._path, new_path, overwrite=overwrite, ignore_if_exists=ignore_if_exists)

    async def delete_file(self) -> None:
        """
        Deletes this :class:`TextDocument`. This will automatically close the document.

        See :meth:`Workspace.delete_text_document()`.
        """
        await self._workspace.delete_text_document(self._path)

    @operation(name="close_text_document")
    def _final_close(self) -> None:
        self.logger.info(f"Closing TextDocument {self.path}...")
        if len(self._pending_edits) > 0:
            warnings.warn(
                f"Dropping {len(self._pending_edits)} uncommitted edits for Textdocument '{self.uri}'. Call text_document.commit_edits() followed by text_document.save() to save the changes.",
                DroppedChangesWarning)
        if not self._content_saved:
            warnings.warn(
                f"TextDocument {self.uri} has unsaved changes. Call text_document.save() to save the changes.",
                DroppedChangesWarning)

        for client in self._workspace.clients:
            if not client.check_feature("textDocument/didClose", text_documents=[self]):
                continue
            params = DidCloseTextDocumentParams(textDocument=self.get_text_document_identifier())
            client.send_text_document_did_close(params)

        # Set the reference_count to 0 explicitly, so documents from a closed
        # Workspace return True on is_closed().
        self._reference_count = 0
        del self._workspace._opened_text_documents[self.uri]
        self.logger.info("TextDocument closed!")

    def is_closed(self) -> bool:
        return self._reference_count <= 0

    def _check_closed(self) -> None:
        if self.is_closed():
            raise ChangeLSError("TextDocument is closed")

    def close(self) -> None:
        """
        Manually closes this ``TextDocument``. If a ``TextDocument`` has been opened multiple times,
        it needs to be closed that many times to fully close it.

        It is preferred to use a ``with`` statement instead of manually closing the ``TextDocument``
        """
        self._check_closed()

        self._reference_count -= 1
        self.logger.info(f"Decremented reference count. New count is {self._reference_count}.")
        if self._reference_count <= 0:
            self._final_close()

    def __enter__(self) -> "TextDocument":
        return self

    def __exit__(self, exc_type: Type[Exception], exc_value: Exception, traceback: TracebackType) -> bool:
        self.close()
        return False

    def _resolve_client_parameter(self, client: Optional[Client]) -> Client:
        return self._workspace._resolve_client_parameter(client)

    @property
    def text(self) -> str:
        return self._text

    @property
    def version(self) -> int:
        return self._version

    @property
    def encoding(self) -> str:
        return self._encoding

    @property
    def language_id(self) -> str:
        assert self._language_id is not None
        return self._language_id

    @property
    def path(self) -> Path:
        return self._path

    @property
    def tokens(self) -> TokenList[SyntacticToken]:
        if not self._tokens:
            raise AttributeError(
                "Tokens are not loaded for this TextDocument. Use load_tokens() to fill the tokens property.")
        return self._tokens

    @operation(start_message="Loading tokens with mode '{mode}' using client '{client}'...", get_logger_from_context=_get_logger_from_context)
    async def load_tokens(self, mode: Literal["enrich", "syntactic", "semantic"] = "enrich", *, include_whitespace: bool = False, client: Optional[Client] = None) -> None:
        """
        Tokenizes this ``TextDocument``. After this method is called, :attr:`tokens` will contain the computed tokens.

        .. important:: Syntactic tokenization (mode ``"syntactic"``) requires that a compatible version of node.js is available on ``PATH``.

        :param mode: Which types of tokens should be loaded. Must be one of the following strings:

            * ``"enrich"``: Load both syntactic and semantic tokens and enrich the syntactic tokens in :attr:`tokens` with semantic information
                from the semantic tokens. This is the default.

            * ``"syntactic"``: Load only syntactic tokens. The tokens can be accessed via the :attr:`tokens` property.

            * ``"semantic"``: Load only semantic tokens.

        :param include_whitespace: If this is ``True``, whitespace-only tokens are included in ``tokens``, otherwise
            they are removed.
        :param client: The :class:`Client` to load the semantic tokens from. If only one ``Client`` is
            open in the current :class:`Workspace`, this parameter is optional.
        """
        self._check_closed()

        if mode in ["enrich", "syntactic"]:
            self._tokens = await tokenize(self.text, self.language_id, include_whitespace=include_whitespace)
        if mode in ["enrich", "semantic"]:
            await self._load_semantic_tokens(client)
        if mode == "enrich":
            assert self._tokens is not None
            enrich_syntactic_tokens(self._tokens, self.get_loaded_semantic_tokens(client), _logger=self.logger)
        self.logger.info("Tokens loaded!")

    def get_loaded_outline(self, client: Optional[Client] = None) -> List["sym.DocumentSymbol"]:
        """
        Returns a previously loaded outline.

        :param client: The :class:`Client` to retrieve the outline for. If only one ``Client``
            is open in the current :class:`Workspace`, this parameter is optional.
        """

        if client is None:
            if len(self._workspace.clients) == 0:
                raise AttributeError(
                    "No outline is loaded for this TextDocument because the Workspace does not have any open Clients.")
            elif len(self._workspace.clients) == 1:
                client = self._workspace.clients[0]
            else:
                raise AttributeError(
                    "Outline is ambiguous because the Workspace has multiple open Clients. Pass a Client to load_outline to load the outline for that Client.")

        out = self._outlines.get(client)
        if out is None:
            raise AttributeError(
                f"No outline is loaded for Client {client}. Use load_outline(...) to fill the outline property.")
        else:
            return out

    @operation(start_message="Loading document outline using Client '{client}'...", get_logger_from_context=_get_logger_from_context)
    async def load_outline(self, *, client: Optional[Client] = None) -> None:
        """
        Loads the document outline (list of symbols defined in the document, maybe hierarchical) for a given :class:`Client`.

        After an outline is loaded, it can be retrieved by calling :meth:`~TextDocument.get_loaded_outline()`. An
        outline is valid as long as the ``TextDocument`` is not changed.

        :param client: The ``Client`` to load the document outline for. If only one ``Client`` is open
            in the :class:`Workspace`, this parameter is optional.
        """

        client = self._resolve_client_parameter(client)
        if not client.check_feature("textDocument/documentSymbol", text_document=self):
            raise ChangeLSError(f"Client '{client}' does not support document outlines.")

        res = await client.send_text_document_document_symbol(DocumentSymbolParams(textDocument=self.get_text_document_identifier()))
        if res is None:
            raise ChangeLSError(f"Client '{client}' returned an empty outline.")

        outline = [sym.DocumentSymbol(client, self._workspace, self, symbol, None) for symbol in res]
        self._outlines[client] = outline
        self.logger.info("Outline loaded!")

    def get_text_document_item(self) -> TextDocumentItem:
        """
        Returns a :class:`TextDocumentItem` for this ``TextDocument``.
        """
        return TextDocumentItem(uri=self.uri, languageId=self.language_id, version=self._version, text=self._text)

    def get_text_document_identifier(self) -> TextDocumentIdentifier:
        """
        Returns a :class:`TextDocumentIdentifier` for this ``TextDocument``.
        """
        return TextDocumentIdentifier(uri=self.uri)

    def get_versioned_text_document_identifier(self) -> VersionedTextDocumentIdentifier:
        """
        Returns a :class:`VersionedTextDocumentIdentifier` for this ``TextDocument``.
        """
        return VersionedTextDocumentIdentifier(uri=self.uri, version=self._version)

    def get_optional_versioned_text_document_identifier(self) -> OptionalVersionedTextDocumentIdentifier:
        """
        Returns a :class:`OptionalVersionedTextDocumentIdentifier` for this ``TextDocument``.
        The returned instance will always have its :attr:`~OptionalVersionedTextDocumentIdentifier.version`
        attribute filled.
        """
        return OptionalVersionedTextDocumentIdentifier(uri=self.uri, version=self._version)

    def _queue_edit(self, new_edit: _Edit) -> None:
        self.logger.debug(f"Queuing edit: {new_edit}")

        # Use bisect_right, so insertions at the same position are applied in insertion order.
        insertion_point = bisect_right(self._pending_edits, new_edit)

        if insertion_point > 0 and self._pending_edits[insertion_point - 1].overlaps(new_edit):
            raise ValueError(f"Edit '{new_edit}' overlaps existing edit '{self._pending_edits[insertion_point - 1]}'")
        if insertion_point < len(self._pending_edits) - 1 and self._pending_edits[insertion_point + 1].overlaps(new_edit):
            raise ValueError(f"Edit '{new_edit}' overlaps existing edit '{self._pending_edits[insertion_point + 1]}'")

        self._pending_edits.insert(insertion_point, new_edit)

    @overload
    def edit(self, new_text: str, from_offset: int, to_offset: int) -> None: ...

    @overload
    def edit(self, new_text: str, from_offset: int, *, length: int) -> None: ...

    def edit(self, new_text: str, from_offset: int, to_offset: Optional[int] = None, *, length: Optional[int] = None) -> None:
        """
        Queue an edit replacing either the range ``[from_offset:to_offset)`` or ``length`` characters
        starting from ``from_offset`` with ``new_text``.

        Queued edits must not contain overlapping changes. A slight exception to this is insertions
        (edits with ``length == 0`` or ``from_offset == to_offset``) at the same position. As per the LSP
        specification, these kinds of insertions are added one after the other in the order they are queued.

        To actually perform the edit, call ``textDocument.commit_edits()``. To then save the changed
        data to disc, call ``textDocument.save()``.

        :param new_text: The new text for the selected range.
        :param from_offset: The start of the range that should be replaced by ``new_text``.
        :param to_offset: The end of the selected range. ``to_offset`` is exclusive, so the character at
            ``text[to_offset]`` is not changed.
        :param length: The length of the selected range.
        """
        self._check_closed()

        if to_offset is None:
            if length is None:
                raise IndexError("One of 'to_offset' and 'length' must be given.")
            to_offset = from_offset + length

        if to_offset < from_offset:
            raise IndexError(f"'to_offset' ({to_offset}) must be greater or equal to 'from_offset' ({from_offset})")

        if from_offset < 0 or from_offset > len(self._text) or to_offset < 0 or to_offset > len(self._text):
            raise IndexError(
                f"edit() offsets are out of bounds: from_offset {from_offset}, to_offset {to_offset}, document length {len(self._text)}")

        self._queue_edit(_Edit(from_offset, to_offset, new_text))

    @overload
    def edit_tokens(self, new_text: str, from_index: int) -> None: ...
    @overload
    def edit_tokens(self, new_text: str, from_index: int, to_index: int) -> None: ...
    @overload
    def edit_tokens(self, new_text: str, from_index: int, *, num_tokens: int) -> None: ...

    def edit_tokens(self, new_text: str, from_index: int, to_index: Optional[int] = None, *, num_tokens: Optional[int] = None) -> None:
        """
        Similar to :meth:`edit()`, but takes it's range from indices into the :attr:`tokens` list. This method
        requires that :meth:`load_tokens()` was called before. It provides the following overloads:

        * ``edit_tokens(new_text, from_index)`` edits the range token at ``tokens[from_index]``.

        * ``edit_tokens(new_text, from_index, to_index)`` edits the range starting at the beginning of ``tokens[from_index]``
            and ends at the end of ``tokens[to_index - 1]``.

        * ``edit_tokens(new_text, from_index, num_tokens=num_tokens)`` edits the range starting at the beginning of ``tokens[from_index]``
            and ends at the end of ``tokens[from_index + num_tokens - 1]``.
        """
        if to_index is None:
            if num_tokens is None:
                to_index = from_index + 1
            else:
                to_index = from_index + num_tokens

        from_offset = self.tokens[from_index].offset
        to_offset = self.tokens[to_index - 1].offset + len(self.tokens[to_index - 1].lexeme)

        self.edit(new_text, from_offset, to_offset)

    def insert(self, new_text: str, offset: int) -> None:
        """
        Inserts text at the given position. Shorthand/more readable alternative for ::

            text_document.edit(new_text, offset, offset)
        """
        self.edit(new_text, offset, offset)

    @overload
    def delete(self, from_offset: int, to_offset: int) -> None: ...
    @overload
    def delete(self, from_offset: int, *, length: int) -> None: ...

    def delete(self, from_offset: int, to_offset: Optional[int] = None, *, length: Optional[int] = None) -> None:
        """
        Deletes the text from the given range. Shorthand/more readable alternative for ::

            text_document.edit("", from_offset, to_offset)
        """
        if to_offset is None and length is None:
            raise ValueError("One of 'to_offset' and 'length' must be given.")

        if to_offset is not None:
            self.edit("", from_offset, to_offset)
        else:
            assert length is not None
            self.edit("", from_offset, length=length)

    def push_text_edit(self, text_edit: TextEdit) -> None:
        """
        Queue an edit which performs the given :class:`TextEdit`.
        """
        from_offset = self.position_to_offset(text_edit.range.start)
        to_offset = self.position_to_offset(text_edit.range.end)
        self.edit(text_edit.newText, from_offset, to_offset)

    def _edit_to_text_document_change_event(self, edit: _Edit, client: Client) -> TextDocumentContentChangeEvent:
        from_position = self.offset_to_position(edit.from_offset, client)
        to_position = self.offset_to_position(edit.to_offset, client)
        return {
            "text": edit.new_text,
            "range": Range(start=from_position, end=to_position)
        }

    def _handle_text_change(self, client: Client) -> None:
        self.logger.info(f"Updating document content for Client '{client}'")

        if client.check_feature("textDocument/didChange", sync_kind=TextDocumentSyncKind.Full):
            content_changes: List[TextDocumentContentChangeEvent] = [{"text": self._text}]
        elif client.check_feature("textDocument/didChange", sync_kind=TextDocumentSyncKind.Incremental):
            # The edits are reversed because, unlike commit_edits, ContentChangeEvents are applied one
            # at a time, in the order they are received. So in order for edits earlier in the document
            # to not invalidate later edits, the edits are entered in reverse order.
            content_changes = [self._edit_to_text_document_change_event(edit, client)
                               for edit in reversed(self._pending_edits)]
        else:
            # Document Sync is disabled for this client
            return

        params = DidChangeTextDocumentParams(
            textDocument=self.get_versioned_text_document_identifier(),
            contentChanges=content_changes)
        client.send_text_document_did_change(params)

    def commit_edits(self) -> None:
        """
        Processes the queued edits and updates the ``TextDocument's`` attributes accordingly.
        After calling ``commit_edits()``, the following attributes are changed:

        * :attr:`text`: Contains the document's contents after performing the queued edits.
        * :attr:`version`: Incremented to reflect that the document has changed.
        * :attr:`tokens`: Set to ``None``, since the loaded tokens will likely no longer be valid.
            After calling ``commit_edits()``, :meth:`load_tokens` will need to be called again if
            updated tokens are needed.

        This function will NOT save the document to file, this needs to be done separately by calling
        :meth:`save()`.
        """
        self._check_closed()

        text_offset = 0
        segments: List[str] = []
        for edit in self._pending_edits:
            if text_offset < edit.from_offset:
                segments.append(self._text[text_offset:edit.from_offset])
            segments.append(edit.new_text)
            text_offset = edit.to_offset
        if text_offset < len(self._text):
            segments.append(self._text[text_offset:])

        self._text = "".join(segments)
        self._version += 1
        for client in self._workspace.clients:
            self._handle_text_change(client)
        self._pending_edits = []
        self._tokens = None
        self._loaded_semantic_tokens = {}
        self._outlines = {}
        self._content_saved = False

    @operation
    def discard_edits(self) -> None:
        """
        Discards the currently queued edits.
        """
        self.logger.info(f"Discarding {len(self._pending_edits)} pending edits.")
        self._check_closed()
        self._pending_edits = []

    @operation(start_message="Saving TextDocument...", get_logger_from_context=_get_logger_from_context)
    async def save(self) -> None:
        """
        Saves the ``TextDocument`` to file.

        .. warning::

            The LSP defines the ``textDocument/willSaveWaitUntil`` request, which can modify the document
            during saving. If any of the language servers try to perform illegal (overlapping) edits at this point,
            this method will raise an Exception and the document WILL NOT get saved. If this becomes an issue,
            the contents of :attr:`~TextDocument.text` may need to be saved manually using the standard Python I/O functions.
        """
        self._check_closed()

        clients = self._workspace.clients

        will_save_params = WillSaveTextDocumentParams(
            textDocument=self.get_text_document_identifier(), reason=TextDocumentSaveReason.Manual)

        self.logger.info("Sending textDocument/willSave notifications.")
        for client in clients:
            if not client.check_feature("textDocument/willSave", text_document=self):
                continue
            client.send_text_document_will_save(will_save_params)

        self.logger.info("Sending textDocument/willSaveWaitUntil requests.")
        requests = [client.send_text_document_will_save_wait_until(will_save_params)
                    for client in clients
                    if client.check_feature("textDocument/willSaveWaitUntil", text_document=self)]
        edit_lists: List[Optional[List[TextEdit]]] = await asyncio.gather(*requests)

        for edit_list in edit_lists:
            if not edit_list:
                continue
            for e in edit_list:
                self.push_text_edit(e)
        if len(self._pending_edits) > 0:
            self.commit_edits()

        self.logger.info("Writing text content to file.")
        with self._path.open("w", encoding=self._encoding) as file:
            file.write(self._text)

        self.logger.info("Sending textDocument/didSave notifications.")
        did_save_params = DidSaveTextDocumentParams(textDocument=self.get_text_document_identifier())
        did_save_params_include_text = DidSaveTextDocumentParams(
            textDocument=self.get_text_document_identifier(), text=self._text)
        for client in clients:
            if client.check_feature("textDocument/didSave", include_text=True, text_document=self):
                client.send_text_document_did_save(did_save_params_include_text)
            elif client.check_feature("textDocument/didSave", include_text=False, text_document=self):
                client.send_text_document_did_save(did_save_params)

        self._content_saved = True
        self.logger.info("TextDocument saved!")

    def position_to_offset(self, position: Position, client: Optional[Client] = None) -> int:
        """
        Converts a :class:`change_ls.types.Position` into an offset into :attr:`text`.

        :param client: The :class:`Client` for which the ``Position`` should be converted.
            This info is needed because the language servers can use different :attr:`position encodings <change_ls.types.InitializeResult>`,
            which affect how the ``Position`` is interpreted. If the ``TextDocument`` is only open in a single
            ``Client``, this parameter is optional.
        """
        self._check_closed()

        if self._version == self._cached_version and position.line == self._cached_line:
            start_offset = self._cached_start_offset
            reference_string = self._cached_reference_string
        else:
            if position.line >= len(self._line_offsets):
                raise IndexError(f"Line {position.line} is out of bounds")

            start_offset = self._line_offsets[position.line]
            end_offset = (self._line_offsets[position.line + 1]
                          if position.line < len(self._line_offsets) else len(self._text))
            reference_string = self._text[start_offset:end_offset]

            if position.character >= len(reference_string):
                raise IndexError(f"Position at line {position.line} character {position.character} does not exist")

            self._cached_version = self._version
            self._cached_line = position.line
            self._cached_start_offset = start_offset
            self._cached_reference_string = reference_string

        encoding = self._resolve_client_parameter(client).get_position_encoding_kind()
        return start_offset + _code_units_to_offset(reference_string, position.character, encoding)

    def offset_to_position(self, offset: int, client: Optional[Client] = None) -> Position:
        """
        Converts an offset into :attr:`text` into a :class:`change_ls.types.Position`.

        :param client: The :class:`Client` for which the ``Position`` should be converted.
            This info is needed because the language servers can use different :attr:`position encodings <change_ls.types.InitializeResult>`,
            which affect how the ``Position`` is interpreted. If the ``TextDocument`` is only open in a single
            ``Client``, this parameter is optional.
        """
        self._check_closed()

        if offset >= len(self._text):
            raise IndexError(f"Offset {offset} is out of bounds.")

        line = bisect_right(self._line_offsets, offset) - 1

        start_offset = self._line_offsets[line]
        end_offset = self._line_offsets[line + 1] if line < len(self._line_offsets) - 1 else len(self._text)
        reference_string = self._text[start_offset:end_offset]
        encoding = self._resolve_client_parameter(client).get_position_encoding_kind()
        character = _offset_to_code_units(reference_string, offset - self._line_offsets[line], encoding)

        return Position(line=line, character=character)

    def offset_to_token_index(self, offset: int) -> Optional[int]:
        """
        Converts an offset into :attr:`text` into an offset into :attr:`tokens`.

        Returns None if there is no token at the given offset, e.g. if the offset points
        to whitespace and tokens were loaded without whitespace.

        :param offset: The offset to convert.
        """

        if offset < 0 or offset >= len(self._text):
            raise ValueError("offset is out of bounds.")

        # Inline bisection because the key parameter for bisect_left is not supported until Python 3.10.
        # Also, this bisection algorithm has some adjustments to make it fit better for tokens.

        tokens = self.tokens
        left = 0
        right = len(tokens)
        middle = 0

        if tokens[left].offset > offset or tokens[right - 1].offset + len(tokens[right - 1].lexeme) <= offset:
            return None

        while left < right - 1:
            middle = (left + right) // 2
            current_offset = tokens[middle].offset
            if current_offset == offset:
                left = middle
                break
            elif current_offset < offset:
                left = middle
            else:
                right = middle

        if left >= 0 and left < len(tokens) and tokens[left].offset + len(tokens[left].lexeme) > offset:
            return left
        else:
            return None

    @operation(start_message="Creating custom symbol at [{start}:{end}] using Client '{client}'...", get_logger_from_context=_get_logger_from_context)
    def create_symbol_at(self, start: int, end: int, kind: SymbolKind, *,
                         tags: Optional[List[SymbolTag]] = None, container_name: Optional[str] = None,
                         client: Optional[Client] = None) -> sym.CustomSymbol:
        """
        Creates a :class:`CustomSymbol` at the specified location. It is the caller's responsibility
        to ensure that the given range actually contains something that can be used as a symbol.

        The name of the symbol is derived from the selected text.

        :param start: Offset into :attr:`text` for the first character of the symbol.
        :param end: Offset into :attr:`text` for the first character no longer part of the symbol
        :param kind: The :class:`SymbolKind` for the symbol.
        :param tags: A list of :class:`SymbolTags <SymbolTag>` for the symbol.
        :param container_name: Name of a containing symbol. This is NOT used to form a hierarchy, so it can be
            any arbitrary string.
        :param client: The :class:`Client` with which this symbol should be associated. This
            is the ``Client`` which will receive the request sent by the methods of the symbol.
        """
        client = self._resolve_client_parameter(client)
        out = sym.CustomSymbol(client, self, (start, end), kind, tags, container_name)
        self.logger.info(f"Custom symbol {out} created!")
        return out

    def __str__(self) -> str:
        return self.uri

    def __repr__(self) -> str:
        # text and tokens would dominate the output if they
        # were printed in their entirety, so we use the default
        # object representation instead.
        values = {
            "text": object.__repr__(self._text),
            "uri": self.uri,
            "version": self._version,
            "language_id": self.language_id,
            "encoding": self.encoding,
            "tokens": object.__repr__(self.tokens) if self._tokens else None,
        }

        return f"{object.__repr__(self)} {values!r}"
