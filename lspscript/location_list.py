import os
from itertools import groupby
from types import TracebackType
from typing import Dict, Iterator, List, Mapping, Sequence, Tuple, Type, Union

import lspscript.text_document as td
import lspscript.workspace as ws
from lspscript.lsp_exception import LSPScriptException
from lspscript.types.structures import Location, LocationLink


def _text_document_matches_uri_posix(doc: "td.TextDocument", uri: str) -> bool:
    return doc.uri == uri


def _text_document_matches_uri_windows(doc: "td.TextDocument", uri: str) -> bool:
    return doc.uri.casefold() == uri.casefold()


if os.name == "nt":
    _text_document_matches_uri = _text_document_matches_uri_windows
else:
    _text_document_matches_uri = _text_document_matches_uri_posix


class LocationList(Mapping["td.TextDocument", List[Tuple[int, int]]]):
    """
    A Mapping from :class:`TextDocuments <TextDocument>` to a list of ranges within that document.
    Ranges are represented as tuples [start offset, end offset). Because all ``TextDocuments`` referenced
    by the ``LocationList`` are opened automatically, a ``LocationList`` is a context manager to
    enable closing the documents when the list is no longer needed. Since opening and closing is handled
    by the :class:`Workspace` as well, it is also possible to simply leave the ``TextDocuments`` open.

    A typical usage might look like this::

        for text_document in locations:
            for start_offset, end_offset in locations[text_document]:
                ...

    An entry in a ``LocationList`` is only valid as long as the underlying ``TextDocument`` is not changed
    (e.g. by calling :meth:`TextDocument.commit_edits()` or :meth:`Workspace.perform_edit_and_save()`). When
    a ``TextDocument`` is changed, it is no longer returned by the ``LocationList``, but other entries are unaffected
    by this. It is therefore possible to commit changes once to a document while iterating through the entries of a list
    (i.e. at the end of the outer loop in the example above).
    """

    _text_documents: List["td.TextDocument"]
    _original_keys: List[Tuple[str, int]]
    _data: Dict[str, List[Tuple[int, int]]]

    class _LocationListIterator(Iterator["td.TextDocument"]):
        _location_list: "LocationList"
        _location_list_length: int
        _current_index: int

        def __init__(self, location_list: "LocationList") -> None:
            self._location_list = location_list
            self._current_index = 0
            self._location_list_length = len(location_list)

        def __iter__(self) -> Iterator["td.TextDocument"]:
            return self

        def __next__(self) -> "td.TextDocument":
            if self._current_index >= self._location_list_length:
                raise StopIteration

            out = self._location_list._text_documents[self._current_index]

            self._current_index += 1
            while not self._location_list._is_valid_index(self._current_index) and self._current_index < self._location_list_length:
                self._current_index += 1

            return out

    def __init__(self, text_documents: List["td.TextDocument"], locations: List[List[Tuple[int, int]]]) -> None:
        self._text_documents = list(text_documents)
        self._original_keys = [(doc.uri, doc.version) for doc in text_documents]
        self._data = {doc.uri: l for doc, l in zip(text_documents, locations)}

        for doc in self._text_documents:
            doc._reopen()  # type: ignore

    @classmethod
    def from_lsp_locations(cls, workspace: ws.Workspace, lsp_locations: Union[Location, Sequence[Location], Sequence[LocationLink]]) -> "LocationList":
        """
        Creates a ``LocationList`` from a sequence of LSP locations (e.g. :class:`Location`, :class:`LocationLink`)
        as returned by various requests. This will open all :class:`TextDocuments <TextDocument>` referenced in
        these locations.

        :param workspace: The :class:`Workspace` in which the ``TextDocuments`` should be opened.
        :param lsp_locations: The list of LSP locations to convert to a ``LocationList``.
        """

        if not isinstance(lsp_locations, Sequence):
            lsp_locations = [lsp_locations]

        grouped_locations = groupby(lsp_locations, lambda l: l.uri if isinstance(l, Location) else l.targetUri)
        text_documents: List["td.TextDocument"] = []
        locations: List[List[Tuple[int, int]]] = []
        for uri, lsp_locations_in_document in grouped_locations:
            doc = workspace.open_text_document(uri)
            text_documents.append(doc)

            offset_locations_in_document: List[Tuple[int, int]] = []
            for l in lsp_locations_in_document:
                if isinstance(l, Location):
                    range = l.range
                else:
                    range = l.targetSelectionRange
                start = doc.position_to_offset(range.start)
                end = doc.position_to_offset(range.end)
                offset_locations_in_document.append((start, end))

            offset_locations_in_document.sort()
            locations.append(offset_locations_in_document)

        out = cls(text_documents, locations)

        for doc in text_documents:
            doc.close()

        return out

    def __enter__(self) -> "LocationList":
        return self

    def __exit__(self, exc_type: Type[Exception], exc_value: Exception, traceback: TracebackType) -> bool:
        for doc in self._text_documents:
            doc.close()
        self._text_documents = []
        self._original_keys = []
        self._data = {}
        return False

    def _is_valid_index(self, index: int) -> bool:
        if index >= len(self._text_documents):
            return False
        return (self._text_documents[index].uri, self._text_documents[index].version) == self._original_keys[index]

    def __getitem__(self, key: Union["td.TextDocument", str]) -> List[Tuple[int, int]]:
        if isinstance(key, td.TextDocument):
            doc = key
            try:
                index = self._text_documents.index(key)
            except ValueError:
                raise KeyError(key.uri)
        else:
            index, doc = next(filter(lambda e: _text_document_matches_uri(e[1], key), enumerate(self._text_documents)),
                              (None, None))
            if index is None or doc is None:
                raise KeyError(key)

        if not self._is_valid_index(index):
            raise KeyError(doc.uri)

        return self._data[doc.uri]

    def __iter__(self) -> Iterator["td.TextDocument"]:
        return LocationList._LocationListIterator(self)

    def __len__(self) -> int:
        return sum(1 for i in range(len(self._text_documents)) if self._is_valid_index(i))

    def get_single_entry(self) -> Tuple["td.TextDocument", Tuple[int, int]]:
        """
        Convenience method to retrieve the single entry from a ``LocationList`` with only one entry.
        Some methods on :class:`Symbol` (e.g. :meth:`Symbol.find_definition()`)
        tend to return single-entry lists, so this method can be used to quickly retrieve that entry.

        If the ``LocationList`` contains more than one entry, an exception is raised.
        """
        if len(self._text_documents) != 1 or len(self._data[self._text_documents[0].uri]) != 1:
            raise LSPScriptException("LocationList contains more than one entry.")
        return self._text_documents[0], self._data[self._text_documents[0].uri][0]
