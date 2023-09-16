import functools
from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path, WindowsPath
from typing import Generator, List, Optional
from urllib.parse import urlsplit

import change_ls._languages as languages
from change_ls.tokens import Grammar
from change_ls.types import (FileOperationFilter, FileOperationPatternKind,
                             TextDocumentFilter)


@dataclass
class _LSPGlobSelection:
    start: int
    end: int
    items: List[str]


@functools.lru_cache
def _extract_selections(lsp_glob: str) -> List[_LSPGlobSelection]:
    selections: List[_LSPGlobSelection] = []

    escape = False
    in_selection = False
    selection_start = 0
    selection_item_start = 0
    selection_items: List[str] = []

    for i, c in enumerate(lsp_glob):
        if escape:
            escape = False
            continue
        if c == "\\":
            escape = True
            continue

        if c == "{" and not in_selection:
            in_selection = True
            selection_start = i
            selection_item_start = i + 1
            selection_items = []
        elif c == "}" and in_selection:
            selection_items.append(lsp_glob[selection_item_start:i])
            in_selection = False
            selections.append(_LSPGlobSelection(selection_start, i + 1, selection_items))
        elif c == "," and in_selection:
            selection_items.append(lsp_glob[selection_item_start:i])
            selection_item_start = i + 1

    return selections


def _expand_lsp_glob_rec(lsp_glob: str, selections: List[_LSPGlobSelection], index: int, start: int) -> Generator[str, None, None]:
    if index == len(selections):
        yield lsp_glob[start:len(lsp_glob)]
        return

    tails = _expand_lsp_glob_rec(lsp_glob, selections, index + 1, selections[index].end)
    selection_start = selections[index].start

    for t in tails:
        for i in selections[index].items:
            segment = lsp_glob[start:selection_start] + i
            yield segment + t


def _expand_lsp_glob(lsp_glob: str) -> Generator[str, None, None]:
    """
    Expands the `{...}` syntax in the given glob by returning each
    combination of values.
    """
    # Interestingly, this syntax is not actually part of the standard unix glob
    # (so fnmatch does not support it), but is instead provided by bash.
    selections = _extract_selections(lsp_glob)
    return _expand_lsp_glob_rec(lsp_glob, selections, 0, 0)


def guess_language_id(path: Path) -> Optional[str]:
    name = path.name

    # Check full filename
    if language_id := languages.extension_to_language_id.get(name):
        return language_id

    # Check suffixes, from each . to the end
    start = 0
    while (start := name.find(".", start)) != -1:
        if language_id := languages.extension_to_language_id.get(name[start:]):
            return language_id
    return None


class TextDocumentInfo:
    _uri: str
    _language_id: Optional[str]

    def __init__(self, uri: str, language_id: Optional[str]) -> None:
        self._uri = uri
        self._language_id = language_id

    @property
    def uri(self) -> str:
        return self._uri

    @property
    def language_id(self) -> Optional[str]:
        return self._language_id


def matches_text_document_filter(info: TextDocumentInfo, filter: TextDocumentFilter) -> bool:
    """
    Checks whether the given `uri` matches the `TextDocumentFilter`.

    If `language_id` is not given, it is guessed from the file extension.
    """

    (scheme, _, path_raw, _, _) = urlsplit(info.uri, scheme="file")

    if "scheme" in filter and filter["scheme"] != scheme:
        return False

    if filter_language_id := filter.get("language"):
        language_id = guess_language_id(Path(path_raw)) if not info.language_id else info.language_id
        if not language_id or language_id != filter_language_id:
            return False

    if lsp_glob := filter.get("pattern"):
        found = False
        for glob in _expand_lsp_glob(lsp_glob):
            if fnmatch(path_raw, glob):
                found = True
                break
        if not found:
            return False

    return True


def matches_file_operation_filter(uri: str, filter: FileOperationFilter) -> bool:
    """
    Checks whether a given `uri` matches the `FileOperationFilter`.
    """

    (scheme, _, path_raw, _, _) = urlsplit(uri, scheme="file")

    if filter.scheme and scheme != filter.scheme:
        return False

    if filter.pattern:
        ignore_case = filter.pattern.options and filter.pattern.options.ignoreCase
        lsp_glob = filter.pattern.glob

        if ignore_case:
            path_raw = path_raw.casefold()
            lsp_glob = lsp_glob.casefold()

        found = False
        for glob in _expand_lsp_glob(lsp_glob):
            if fnmatch(path_raw, glob):
                found = True
                break
        if not found:
            return False

        path = Path(path_raw)
        if isinstance(path, WindowsPath) and path_raw[0] == "/":
            # as_uri() on Windows adds an additional '/' to the beginning for some reason.
            # If this is kept, it is not possible to create valid (i.e. existing) Paths from
            # the uri.
            path = Path(path_raw[1:])

        is_directory = path.is_dir()
        if filter.pattern.matches is FileOperationPatternKind.file and is_directory:
            return False
        elif filter.pattern.matches is FileOperationPatternKind.folder and not is_directory:
            return False

    return True


def install_language(*, language_id: str, extensions: List[str] = [], grammar: Optional[Grammar] = None, embedded_grammars: List[Grammar] = [], allow_overwrite: bool = False) -> None:
    """
    Adds a new language to be used by the library functions.


    :param language_id: The language id of the new language.
    :param extensions: List of file extensions associated with the new language.
    :param grammar: Main :class:`Grammar` of the new language.
    :param embedded_grammars: Additional ``Grammars`` used by the main grammar.
    :param allow_overwrite: Allow overriding of existing language information. Default is ``False``.
        When overwriting properties for existing languages, only the properties which were actually
        supplied are overwritten.
    """

    if len(extensions) == 0:
        raise ValueError("At least one file extension must be given.")

    grammars = list(embedded_grammars)
    if grammar:
        grammars.append(grammar)

    if not allow_overwrite:
        if language_id in languages.language_id_to_scope:
            raise ValueError(f"Language id {language_id} is already in use")

        for e in extensions:
            if e in languages.extension_to_language_id:
                raise ValueError(
                    f"file extension {e} is already defined for language id {languages.extension_to_language_id[e]}.")

        for g in grammars:
            if g.get_scope_name() in languages.scope_to_grammar:
                raise ValueError(f"Grammar scope {g.get_scope_name()} is already used")

    for e in extensions:
        languages.extension_to_language_id[e] = language_id

    if grammar:
        languages.language_id_to_scope[language_id] = grammar.get_scope_name()

    for g in grammars:
        languages.scope_to_grammar[g.get_scope_name()] = g
