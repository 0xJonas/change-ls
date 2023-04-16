import asyncio
from bisect import bisect_right
from dataclasses import dataclass, field
from pathlib import Path
from types import TracebackType
from typing import Callable, Dict, List, Optional, Type, overload

from lspscript.client import Client
from lspscript.lsp_exception import LSPScriptException
from lspscript.tokens import TokenList, tokenize
from lspscript.types import (DidCloseTextDocumentParams,
                             OptionalVersionedTextDocumentIdentifier,
                             TextDocumentItem, VersionedTextDocumentIdentifier)
from lspscript.types.enumerations import (PositionEncodingKind,
                                          TextDocumentSaveReason,
                                          TextDocumentSyncKind)
from lspscript.types.structures import (DidChangeTextDocumentParams,
                                        DidSaveTextDocumentParams, Position,
                                        Range, TextDocumentContentChangeEvent,
                                        TextDocumentIdentifier, TextEdit,
                                        WillSaveTextDocumentParams)
from lspscript.util import TextDocumentInfo, guess_language_id


@dataclass(order=True)
class _Edit:
    from_offset: int
    to_offset: int
    new_text: str = field(compare=False)

    @classmethod
    def from_text_edit(cls, text_edit: TextEdit, line_offsets: List[int]) -> "_Edit":
        from_offset = line_offsets[text_edit.range.start.line] + text_edit.range.start.character
        to_offset = line_offsets[text_edit.range.end.line] + text_edit.range.end.character
        return cls(from_offset, to_offset, text_edit.newText)

    def overlaps(self, other: "_Edit") -> bool:
        covers_from_offset = self.from_offset <= other.from_offset and self.to_offset > other.from_offset
        covers_to_offset = self.from_offset < other.to_offset and self.to_offset >= other.to_offset

        # The '<' when comparing to_offset ensures that zero-length edits at the same position
        # will not overlap. Per the LSP-spec, these edits are applied in the order they are received.
        # The cases where to_overlap is equal are already covered by the other conditions.
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


class TextDocument(TextDocumentInfo, TextDocumentItem):
    """
    A :class:`TextDocument` is a single file in a :class:`Workspace`, which can be edited or queried for information.

    ``TextDocuments`` are not instantiated directly, but are instead obtained by calling
    :meth:`~Workspace.open_text_document()` on a ``Workspace`` instance. When a ``TextDocument``
    is opened this way, all ``Clients`` which were specified on the call to ``open_text_document()``
    (defaults to all currently running ``Clients``) are notified that this ``TextDocument`` is now
    managed by LSPScript. ``TextDocuments`` are context managers and the recommended way to handle them
    is using a ``with`` statement::

        with workspace.open_text_document(Path("script.py")) as doc:
            ...

    Once the ``with`` statement is exited, the ``TextDocument`` is closed for all ``Clients``
    it was opened with. It is also possible to manually close a ``TextDocument`` by calling :meth:`close()`.
    Once a ``TextDocument`` is closed for a ``Client``, this ``Client`` can no longer be used
    by methods which call a language server.

    ``TextDocument`` inherits from :class:`TextDocumentInfo` and :class:`TextDocumentItem` and can
    therefore by used anywhere an instance of one of these classes is required.

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

    _path: Path
    _encoding: str
    _clients: Dict[str, Client]
    _tokens: Optional[TokenList]
    _pending_edits: List[_Edit]
    _line_offsets: List[int]

    language_id: str

    def __init__(self, path: Path, clients: Dict[str, Client], language_id: Optional[str] = None, version: int = 0, encoding: Optional[str] = None) -> None:
        self._path = path
        with path.open(encoding=encoding) as file:
            text = file.read()
            self._encoding = file.encoding

        if not language_id:
            guessed_id = guess_language_id(path)
            if not guessed_id:
                raise LSPScriptException(f"Unable to determine language id for '{str(path)}'")
            language_id = guessed_id

        self._clients = clients
        self._tokens = None
        self._pending_edits = []
        self._line_offsets = _calculate_line_offsets(text)

        uri = path.as_uri()
        TextDocumentInfo.__init__(self, uri, language_id)
        TextDocumentItem.__init__(self, uri=uri, languageId=language_id, version=version, text=text)

    def close(self, client_names: Optional[List[str]] = None) -> None:
        """
        Manually closes the document for the given ``Clients``. These ``Clients`` can no longer be
        used by methods which call a language server.

        It is preferred to use a ``with`` statement instead of manually closing the ``TextDocument``
        """
        if client_names is None:
            client_names = list(self._clients.keys())

        for name in client_names:
            params = DidCloseTextDocumentParams(textDocument=self.get_text_document_identifier())
            self._clients[name].send_text_document_did_close(params)
            del self._clients[name]

    def __enter__(self) -> "TextDocument":
        return self

    def __exit__(self, exc_type: Type[Exception], exc_value: Exception, traceback: TracebackType) -> bool:
        self.close()
        return False

    def _get_client(self, client_name: Optional[str]) -> Client:
        if not self._clients:
            raise LSPScriptException("TextDocument is not open in any Client")

        if not client_name:
            if len(self._clients) == 1:
                return list(self._clients.values())[0]
            else:
                raise ValueError("Unable to identify Client without a name.")
        return self._clients[client_name]

    @property
    def encoding(self) -> str:
        return self._encoding

    @property
    def tokens(self) -> TokenList:
        if not self._tokens:
            raise AttributeError("Tokens are not loaded for this TextDocument")
        return self._tokens

    async def load_tokens(self, *, include_whitespace: bool = False) -> None:
        """
        Tokenizes this ``TextDocument``. After this method is called, :attr:`tokens` will contain the computed tokens.

        .. important:: Tokenization requires that a compatible version of node.js is available on ``PATH``.

        :param include_whitespace: If this is ``True``, whitespace-only tokens are included in ``tokens``, otherwise
            they are removed.
        """
        self._tokens = await tokenize(self.text, self.language_id, include_whitespace=include_whitespace)

    def get_text_document_identifier(self) -> TextDocumentIdentifier:
        """
        Returns a :class:`TextDocumentIdentifier` for this ``TextDocument``.
        """
        return TextDocumentIdentifier(uri=self.uri)

    def get_versioned_text_document_identifier(self) -> VersionedTextDocumentIdentifier:
        """
        Returns a :class:`VersionedTextDocumentIdentifier` for this ``TextDocument``.
        """
        return VersionedTextDocumentIdentifier(uri=self.uri, version=self.version)

    def get_optional_versioned_text_document_identifier(self) -> OptionalVersionedTextDocumentIdentifier:
        """
        Returns a :class:`OptionalVersionedTextDocumentIdentifier` for this ``TextDocument``.
        The returned instance will always have its :attr:`~OptionalVersionedTextDocumentIdentifier.version`
        attribute filled.
        """
        return OptionalVersionedTextDocumentIdentifier(uri=self.uri, version=self.version)

    def _queue_edit(self, new_edit: _Edit) -> None:
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
        if to_offset is None:
            if length is None:
                raise IndexError("One of 'to_offset' and 'length' must be given.")
            to_offset = from_offset + length

        if to_offset < from_offset:
            raise IndexError(f"'to_offset' ({to_offset}) must be greater or equal to 'from_offset' ({from_offset})")

        if from_offset < 0 or from_offset > len(self.text) or to_offset < 0 or to_offset > len(self.text):
            raise IndexError(
                f"edit() offsets are out of bounds: from_offset {from_offset}, to_offset {to_offset}, document length {len(self.text)}")

        self._queue_edit(_Edit(from_offset, to_offset, new_text))

    @overload
    def edit_tokens(self, new_text: str, from_index: int) -> None: ...
    @overload
    def edit_tokens(self, new_text: str, from_index: int, to_index: int) -> None: ...
    @overload
    def edit_tokens(self, new_text: str, from_index: int, *, num_tokens: int) -> None: ...

    def edit_tokens(self, new_text: str, from_index: int, to_index: Optional[int] = None, *, num_tokens: Optional[int] = None) -> None:
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

    def _handle_text_change(self, client: Client) -> None:
        if client.check_feature("textDocument/didChange", sync_kind=TextDocumentSyncKind.Full):
            contentChanges: List[TextDocumentContentChangeEvent] = [{"text": self.text}]
        elif client.check_feature("textDocument/didChange", sync_kind=TextDocumentSyncKind.Incremental):
            # The edits are reversed because, unlike commit_edits, ContentChangeEvents are applied one
            # at a time, in the order they are received. So in order for edits earlier in the document
            # to not invalidate later edits, the edits are entered in reverse order.
            contentChanges = [edit.as_text_document_content_change_event(self._line_offsets)
                              for edit in reversed(self._pending_edits)]
        else:
            # Document Sync is disabled for this client
            return

        params = DidChangeTextDocumentParams(
            textDocument=self.get_versioned_text_document_identifier(),
            contentChanges=contentChanges)
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
        text_offset = 0
        segments: List[str] = []
        for edit in self._pending_edits:
            if text_offset < edit.from_offset:
                segments.append(self.text[text_offset:edit.from_offset])
            segments.append(edit.new_text)
            text_offset = edit.to_offset
        if text_offset < len(self.text):
            segments.append(self.text[text_offset:])

        self.text = "".join(segments)
        self.version += 1
        for client in self._clients.values():
            self._handle_text_change(client)
        self._pending_edits = []
        self._tokens = None

    def discard_edits(self) -> None:
        """
        Discards the currently queued edits.
        """
        self._pending_edits = []

    async def save(self) -> None:
        """
        Saves the ``TextDocument`` to file.

        .. warning::

            The LSP defines the ``textDocument/willSaveWaitUntil`` request, which can modify the document
            during saving. If any of the language servers try to perform illegal (overlapping) edits at this point,
            this method will raise an Exception and the document WILL NOT get saved. If this becomes an issue,
            the contents of :attr:`~TextDocument.text` may need to be saved manually using the standard Python I/O functions.
        """
        will_save_params = WillSaveTextDocumentParams(
            textDocument=self.get_text_document_identifier(), reason=TextDocumentSaveReason.Manual)

        # textDocument/willSave
        for client in self._clients.values():
            if not client.check_feature("textDocument/willSave"):
                continue
            client.send_text_document_will_save(will_save_params)

        # textDocument/willSaveWaitUntil
        requests = [client.send_text_document_will_save_wait_until(will_save_params)
                    for client in self._clients.values()
                    if client.check_feature("textDocument/willSaveWaitUntil")]
        edit_lists: List[Optional[List[TextEdit]]] = await asyncio.gather(*requests)

        for edit_list in edit_lists:
            if not edit_list:
                continue
            for e in edit_list:
                self._queue_edit(_Edit.from_text_edit(e, self._line_offsets))
        self.commit_edits()

        # Actual saving
        with self._path.open("w", encoding=self._encoding) as file:
            file.write(self.text)

        # textDocument/didSave
        did_save_params = DidSaveTextDocumentParams(textDocument=self.get_text_document_identifier())
        did_save_params_include_text = DidSaveTextDocumentParams(
            textDocument=self.get_text_document_identifier(), text=self.text)
        for client in self._clients.values():
            if client.check_feature("textDocument/didSave", include_text=True):
                client.send_text_document_did_save(did_save_params_include_text)
            elif client.check_feature("textDocument/didSave", include_text=False):
                client.send_text_document_did_save(did_save_params)

    def position_to_offset(self, position: Position, client_name: Optional[str] = None) -> int:
        """
        Converts a :class:`lspscript.types.Position` into an offset into :attr:`text`.

        :param client_name: The name of the :class:`Client` for which the ``Position`` should be converted.
            This info is needed because the language servers can use different :attr:`position encodings <lspscript.types.InitializeResult>`,
            which affect how the ``Position`` is interpreted. If the ``TextDocument`` is only open in a single
            ``Client``, this parameter is optional.
        """
        if position.line >= len(self._line_offsets):
            raise IndexError(f"Line {position.line} is out of bounds")

        start_offset = self._line_offsets[position.line]
        end_offset = (self._line_offsets[position.line + 1]
                      if position.line < len(self._line_offsets) else len(self.text))
        reference_string = self.text[start_offset:end_offset]

        if position.character >= len(reference_string):
            raise IndexError(f"Position at line {position.line} character {position.character} does not exist")

        encoding = self._get_client(client_name).get_position_encoding_kind()
        return start_offset + _code_units_to_offset(reference_string, position.character, encoding)

    def offset_to_position(self, offset: int, client_name: Optional[str] = None) -> Position:
        """
        Converts an offset into :attr:`text` into a :class:`lspscript.types.Position`.

        :param client_name: The name of the :class:`Client` for which the ``Position`` should be converted.
            This info is needed because the language servers can use different :attr:`position encodings <lspscript.types.InitializeResult>`,
            which affect how the ``Position`` is interpreted. If the ``TextDocument`` is only open in a single
            ``Client``, this parameter is optional.
        """
        if offset >= len(self.text):
            raise IndexError(f"Offset {offset} is out of bounds.")

        line = bisect_right(self._line_offsets, offset) - 1

        start_offset = self._line_offsets[line]
        end_offset = self._line_offsets[line + 1] if line < len(self._line_offsets) else len(self.text)
        reference_string = self.text[start_offset:end_offset]
        encoding = self._get_client(client_name).get_position_encoding_kind()
        character = _offset_to_code_units(reference_string, offset - self._line_offsets[line], encoding)

        return Position(line=line, character=character)
