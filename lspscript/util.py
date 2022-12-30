import functools
from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path, WindowsPath
from typing import Generator, List, Optional
from urllib.parse import urlsplit

from lspscript.types.enumerations import FileOperationPatternKind

from .types.structures import FileOperationFilter, TextDocumentFilter

_suffix_to_language_id = {
    # https://gist.github.com/ppisarczyk/43962d06686722d26d176fad46879d41

    "abap": "abap",

    "bat": "bat",

    "cmd": "bat",

    "bib": "bibtex",

    "clj": "clojure",
    "boot": "clojure",
    "cl2": "clojure",
    "cljc": "clojure",
    "cljs": "clojure",
    "cljscm": "clojure",
    "cljx": "clojure",
    "hic": "clojure",

    "coffee": "coffeescript",
    "_coffee": "coffeescript",
    "cjsx": "coffeescript",
    "cson": "coffeescript",
    "iced": "coffeescript",

    "c": "c",
    "cats": "c",
    "h": "c",
    "idc": "c",
    "w": "c",

    "cpp": "cpp",
    "cp": "cpp",
    "c++": "cpp",
    "cc": "cpp",
    "cxx": "cpp",
    "hpp": "cpp",
    "h++": "cpp",
    "hh": "cpp",
    "inc": "cpp",
    "inl": "cpp",
    "ipp": "cpp",
    "tcc": "cpp",
    "tpp": "cpp",

    "cs": "csharp",
    "cake": "csharp",
    "csx": "csharp",

    "css": "css",

    "dart": "dart",

    "diff": "diff",
    "patch": "diff",

    "dockerfile": "dockerfile",

    "ex": "elixir",
    "exs": "elixir",

    "erl": "erlang",
    "es": "erlang",
    "escript": "erlang",
    "hrl": "erlang",
    "xrl": "erlang",
    "yrl": "erlang",

    "fs": "fsharp",
    "fsi": "fsharp",
    "fsx": "fsharp",

    "": "git-commit",
    "": "git-rebase",

    "go": "go",

    "groovy": "groovy",
    "grt": "groovy",
    "gtpl": "groovy",
    "gvy": "groovy",

    "handlebars": "handlebars",
    "hbs": "handlebars",

    "html": "html",
    "htm": "html",
    "st": "html",
    "xht": "html",
    "xhtml": "html",

    "ini": "ini",
    "cfg": "ini",
    "prefs": "ini",
    "pro": "ini",
    "properties": "ini",

    "java": "java",

    "js": "javascript",
    "_js": "javascript",
    "es6": "javascript",
    "jsm": "javascript",
    "njs": "javascript",

    "jsx": "javascriptreact",

    "json": "json",
    "lock": "json",

    "tex": "latex",
    "ltx": "latex",
    "aux": "latex",
    "cbx": "latex",
    "sty": "latex",
    "toc": "latex",

    "less": "less",

    "lua": "lua",
    "nse": "lua",
    "pd_lua": "lua",
    "rbxs": "lua",
    "wlua": "lua",

    "mk": "makefile",
    "mkfile": "makefile",

    "md": "markdown",
    "markdown": "markdown",
    "mkd": "markdown",
    "mkdn": "markdown",
    "mkdown": "markdown",

    "m": "objective-c",

    "mm": "objective-cpp",

    "pl": "perl",
    "al": "perl",
    "cgi": "perl",
    "ph": "perl",
    "plx": "perl",
    "pm": "perl",
    "pod": "perl",

    "6pl": "perl6",
    "6pm": "perl6",
    "nqp": "perl6",
    "p6": "perl6",
    "p6l": "perl6",
    "p6m": "perl6",
    "pl6": "perl6",
    "pm6": "perl6",

    "php": "php",
    "aw": "php",
    "ctp": "php",
    "fcgi": "php",
    "php3": "php",
    "php4": "php",
    "php5": "php",
    "phps": "php",
    "phpt": "php",

    "ps1": "powershell",
    "psm1": "powershell",
    "psd1": "powershell",

    "": "jade",

    "py": "python",
    "pyde": "python",
    "pyp": "python",
    "pyt": "python",
    "pyw": "python",
    "rpy": "python",
    "xpy": "python",

    "r": "r",
    "rd": "r",
    "rsx": "r",

    "razor": "razor",
    "cshtml": "razor",
    "vbhtml": "razor",

    "rb": "ruby",
    "builder": "ruby",
    "god": "ruby",
    "irbrc": "ruby",
    "rake": "ruby",
    "rbw": "ruby",
    "rbx": "ruby",
    "ru": "ruby",
    "ruby": "ruby",
    "thor": "ruby",
    "watchr": "ruby",

    "rs": "rust",

    "scss": "scss",

    "sass": "sass",

    "scala": "scala",
    "sbt": "scala",
    "sc": "scala",

    "": "shaderlab",

    "sh": "shellscript",
    "bash": "shellscript",
    "bats": "shellscript",
    "ksh": "shellscript",
    "zsh": "shellscript",
    "tmux": "shellscript",
    "command": "shellscript",

    "sql": "sql",
    "cql": "sql",
    "ddl": "sql",
    "prc": "sql",
    "tab": "sql",
    "udf": "sql",
    "viw": "sql",

    "swift": "swift",

    "ts": "typescript",

    "tsx": "typescriptreact",

    # "tex": "tex",

    "vb": "vb",
    "bas": "vb",
    "cls": "vb",
    "frm": "vb",
    "frx": "vb",
    "vba": "vb",
    "vbs": "vb",

    "xml": "xml",

    "xsl": "xsl",
    "xslt": "xsl",

    "yaml": "yaml",
    "yml": "yaml",
}


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


def matches_text_document_filter(uri: str, filter: TextDocumentFilter, language_id: Optional[str] = None) -> bool:
    """
    Checks whether the given `uri` matches the `TextDocumentFilter`.

    If `language_id` is not given, it is guessed from the file extension.
    """

    (scheme, _, path_raw, _, _) = urlsplit(uri, scheme="file")
    suffix = Path(path_raw).suffix[1:]

    if "scheme" in filter and filter["scheme"] != scheme:
        return False

    if filter_language_id := filter.get("language"):
        if not language_id:
            language_id = _suffix_to_language_id.get(suffix)
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
