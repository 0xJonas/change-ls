from bisect import bisect_left, bisect_right
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Dict, List, Optional, Type, overload

from lspscript.client import Client
from lspscript.lsp_exception import LSPScriptException
from lspscript.tokens import TokenList, tokenize
from lspscript.types import (DidCloseTextDocumentParams,
                             OptionalVersionedTextDocumentIdentifier,
                             TextDocumentItem, VersionedTextDocumentIdentifier)
from lspscript.types.enumerations import TextDocumentSyncKind
from lspscript.types.structures import (DidChangeTextDocumentParams, Position,
                                        Range, TextDocumentContentChangeEvent,
                                        TextDocumentIdentifier)
from lspscript.util import TextDocumentInfo, guess_language_id


@dataclass(order=True)
class _Edit:
    from_offset: int
    to_offset: int
    new_text: str

    def overlaps(self, other: "_Edit") -> bool:
        return (
            self.from_offset <= other.from_offset and self.to_offset > other.from_offset
            or self.from_offset < other.to_offset and self.to_offset >= other.to_offset
            or self.from_offset >= other.from_offset and self.to_offset <= other.to_offset
        )

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
    return len(text)


def _calculate_line_offsets(text: str) -> List[int]:
    offset = 0
    text_len = len(text)
    line_offsets: List[int] = []
    while offset < text_len:
        line_offsets.append(offset)
        offset = _skip_to_next_line(text, offset)
    return line_offsets


class TextDocument(TextDocumentInfo, TextDocumentItem):
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
        self._tokens = await tokenize(self.text, self.language_id, include_whitespace=include_whitespace)

    def get_text_document_identifier(self) -> TextDocumentIdentifier:
        return TextDocumentIdentifier(uri=self.uri)

    def get_versioned_text_document_identifier(self) -> VersionedTextDocumentIdentifier:
        return VersionedTextDocumentIdentifier(uri=self.uri, version=self.version)

    def get_optional_versioned_text_document_identifier(self) -> OptionalVersionedTextDocumentIdentifier:
        return OptionalVersionedTextDocumentIdentifier(uri=self.uri, version=self.version)

    @overload
    def edit(self, new_text: str, from_offset: int, to_offset: int) -> None: ...

    @overload
    def edit(self, new_text: str, from_offset: int, *, length: int) -> None: ...

    def edit(self, new_text: str, from_offset: int, to_offset: Optional[int] = None, *, length: Optional[int] = None) -> None:
        """
        Queue an edit replacing either the range `[from_offset:to_offset)` or `length` characters starting from `from_offset`
        with `new_text`.

        Queued edits must not contain overlapping changes.

        To actually perform the edit, call `textDocument.commit_edits()`. To then save the changed data to disc, call `textDocument.save()`.
        """
        if to_offset is None:
            if length is None:
                raise IndexError("One of 'to_offset' and 'length' must be given.")
            to_offset = from_offset + length

        if to_offset < from_offset:
            raise IndexError(f"'to_offset' ({to_offset}) must be greater or equal to 'from_offset' ({from_offset})")

        if from_offset < 0 or to_offset >= len(self.text):
            raise IndexError(
                f"edit() offsets are out of bounds: from_offset {from_offset}, to_offset {to_offset}, document length {len(self.text)}")

        new_edit = _Edit(from_offset, to_offset, new_text)
        insertion_point = bisect_left(self._pending_edits, new_edit)

        if insertion_point > 0 and self._pending_edits[insertion_point - 1].overlaps(new_edit):
            raise ValueError(f"Edit '{new_edit}' overlaps existing edit '{self._pending_edits[insertion_point - 1]}'")
        if insertion_point < len(self._pending_edits) - 1 and self._pending_edits[insertion_point + 1].overlaps(new_edit):
            raise ValueError(f"Edit '{new_edit}' overlaps existing edit '{self._pending_edits[insertion_point + 1]}'")

        self._pending_edits.insert(insertion_point, new_edit)

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
        self.edit(new_text, offset, offset)

    @overload
    def delete(self, from_offset: int, to_offset: int) -> None: ...
    @overload
    def delete(self, from_offset: int, *, length: int) -> None: ...

    def delete(self, from_offset: int, to_offset: Optional[int] = None, *, length: Optional[int] = None) -> None:
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
            contentChanges = [edit.as_text_document_content_change_event(
                self._line_offsets) for edit in reversed(self._pending_edits)]
        else:
            # Document Sync is disabled for this client
            return

        params = DidChangeTextDocumentParams(
            textDocument=self.get_versioned_text_document_identifier(),
            contentChanges=contentChanges)
        client.send_text_document_did_change(params)

    def commit_edits(self) -> None:
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

    def discard_edits(self) -> None:
        self._pending_edits = []

        #
        # save()
        # - textDocument/willSave
        # - textDocument/willSaveWaitUntil
