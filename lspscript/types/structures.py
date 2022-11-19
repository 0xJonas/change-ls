from .util import *
from .enumerations import *

from dataclasses import dataclass
from typing import Dict, List, Literal, Mapping, Optional, Tuple, Union


@dataclass
class TextDocumentIdentifier():
    """
    A literal to identify a text document in the client.

    *Generated from the TypeScript documentation*
    """

    # The text document's uri.
    uri: str

    def __init__(self, *, uri: str) -> None:
        """
        - uri: The text document's uri.
        """
        self.uri = uri

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "TextDocumentIdentifier":
        uri = json_get_string(obj, "uri")
        return cls(uri=uri)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["uri"] = self.uri
        return out


@dataclass
class Position():
    """
    Position in a text document expressed as zero-based line and character
    offset. Prior to 3.17 the offsets were always based on a UTF-16 string
    representation. So a string of the form `a𐐀b` the character offset of the
    character `a` is 0, the character offset of `𐐀` is 1 and the character
    offset of b is 3 since `𐐀` is represented using two code units in UTF-16.
    Since 3.17 clients and servers can agree on a different string encoding
    representation (e.g. UTF-8). The client announces it's supported encoding
    via the client capability [`general.positionEncodings`](#clientCapabilities).
    The value is an array of position encodings the client supports, with
    decreasing preference (e.g. the encoding at index `0` is the most preferred
    one). To stay backwards compatible the only mandatory encoding is UTF-16
    represented via the string `utf-16`. The server can pick one of the
    encodings offered by the client and signals that encoding back to the
    client via the initialize result's property
    [`capabilities.positionEncoding`](#serverCapabilities). If the string value
    `utf-16` is missing from the client's capability `general.positionEncodings`
    servers can safely assume that the client supports UTF-16. If the server
    omits the position encoding in its initialize result the encoding defaults
    to the string value `utf-16`. Implementation considerations: since the
    conversion from one encoding into another requires the content of the
    file / line the conversion is best done where the file is read which is
    usually on the server side.
    
    Positions are line end character agnostic. So you can not specify a position
    that denotes `\r|\n` or `\n|` where `|` represents the character offset.
    
    @since 3.17.0 - support for negotiated position encoding.

    *Generated from the TypeScript documentation*
    """

    # Line position in a document (zero-based).
    # 
    # If a line number is greater than the number of lines in a document, it defaults back to the number of lines in the document.
    # If a line number is negative, it defaults to 0.
    line: int
    
    # Character offset on a line in a document (zero-based).
    # 
    # The meaning of this offset is determined by the negotiated
    # `PositionEncodingKind`.
    # 
    # If the character value is greater than the line length it defaults back to the
    # line length.
    character: int

    def __init__(self, *, line: int, character: int) -> None:
        """
        - line: Line position in a document (zero-based).
            
            If a line number is greater than the number of lines in a document, it defaults back to the number of lines in the document.
            If a line number is negative, it defaults to 0.
        - character: Character offset on a line in a document (zero-based).
            
            The meaning of this offset is determined by the negotiated
            `PositionEncodingKind`.
            
            If the character value is greater than the line length it defaults back to the
            line length.
        """
        self.line = line
        self.character = character

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "Position":
        line = json_get_int(obj, "line")
        character = json_get_int(obj, "character")
        return cls(line=line, character=character)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["line"] = self.line
        out["character"] = self.character
        return out


@dataclass
class TextDocumentPositionParams():
    """
    A parameter literal used in requests to pass a text document and a position inside that
    document.

    *Generated from the TypeScript documentation*
    """

    # The text document.
    textDocument: "TextDocumentIdentifier"
    
    # The position inside the text document.
    position: "Position"

    def __init__(self, *, textDocument: "TextDocumentIdentifier", position: "Position") -> None:
        """
        - textDocument: The text document.
        - position: The position inside the text document.
        """
        self.textDocument = textDocument
        self.position = position

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "TextDocumentPositionParams":
        textDocument = TextDocumentIdentifier.from_json(json_get_object(obj, "textDocument"))
        position = Position.from_json(json_get_object(obj, "position"))
        return cls(textDocument=textDocument, position=position)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["textDocument"] = self.textDocument.to_json()
        out["position"] = self.position.to_json()
        return out


ProgressToken = Union[int, str]

def parse_ProgressToken(arg: JSON_VALUE) -> ProgressToken:
    return parse_or_type((arg), (lambda v: json_assert_type_int(v), lambda v: json_assert_type_string(v)))

def write_ProgressToken(arg: ProgressToken) -> JSON_VALUE:
    return write_or_type(arg, (lambda i: isinstance(i, int), lambda i: isinstance(i, str)), (lambda i: i, lambda i: i))


@dataclass
class ImplementationParams(TextDocumentPositionParams):
    """


    *Generated from the TypeScript documentation*
    """

    # The text document.
    textDocument: "TextDocumentIdentifier"
    
    # The position inside the text document.
    position: "Position"
    
    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]
    
    # An optional token that a server can use to report partial results (e.g. streaming) to
    # the client.
    partialResultToken: Optional["ProgressToken"]

    def __init__(self, *, textDocument: "TextDocumentIdentifier", position: "Position", workDoneToken: Optional["ProgressToken"] = None, partialResultToken: Optional["ProgressToken"] = None) -> None:
        """
        - textDocument: The text document.
        - position: The position inside the text document.
        - workDoneToken: An optional token that a server can use to report work done progress.
        - partialResultToken: An optional token that a server can use to report partial results (e.g. streaming) to
            the client.
        """
        self.textDocument = textDocument
        self.position = position
        self.workDoneToken = workDoneToken
        self.partialResultToken = partialResultToken

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "ImplementationParams":
        textDocument = TextDocumentIdentifier.from_json(json_get_object(obj, "textDocument"))
        position = Position.from_json(json_get_object(obj, "position"))
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        if partialResultToken_json := obj.get("partialResultToken"):
            partialResultToken = parse_ProgressToken(partialResultToken_json)
        else:
            partialResultToken = None
        return cls(textDocument=textDocument, position=position, workDoneToken=workDoneToken, partialResultToken=partialResultToken)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["textDocument"] = self.textDocument.to_json()
        out["position"] = self.position.to_json()
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        if self.partialResultToken is not None:
            out["partialResultToken"] = write_ProgressToken(self.partialResultToken)
        return out


@dataclass
class Range():
    """
    A range in a text document expressed as (zero-based) start and end positions.
    
    If you want to specify a range that contains a line including the line ending
    character(s) then use an end position denoting the start of the next line.
    For example:
    ```ts
    {
        start: { line: 5, character: 23 }
        end : { line 6, character : 0 }
    }
    ```

    *Generated from the TypeScript documentation*
    """

    # The range's start position.
    start: "Position"
    
    # The range's end position.
    end: "Position"

    def __init__(self, *, start: "Position", end: "Position") -> None:
        """
        - start: The range's start position.
        - end: The range's end position.
        """
        self.start = start
        self.end = end

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "Range":
        start = Position.from_json(json_get_object(obj, "start"))
        end = Position.from_json(json_get_object(obj, "end"))
        return cls(start=start, end=end)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["start"] = self.start.to_json()
        out["end"] = self.end.to_json()
        return out


@dataclass
class Location():
    """
    Represents a location inside a resource, such as a line
    inside a text file.

    *Generated from the TypeScript documentation*
    """

    uri: str
    
    range: "Range"

    def __init__(self, *, uri: str, range: "Range") -> None:
        """
    
        """
        self.uri = uri
        self.range = range

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "Location":
        uri = json_get_string(obj, "uri")
        range = Range.from_json(json_get_object(obj, "range"))
        return cls(uri=uri, range=range)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["uri"] = self.uri
        out["range"] = self.range.to_json()
        return out


AnonymousStructure42Keys = Literal["language","scheme","pattern"]

def parse_AnonymousStructure42(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure42Keys, Any]:
    out: Dict[AnonymousStructure42Keys, Any] = {}
    out["language"] = json_get_string(obj, "language")
    if scheme_json := json_get_optional_string(obj, "scheme"):
        out["scheme"] = scheme_json
    else:
        out["scheme"] = None
    if pattern_json := json_get_optional_string(obj, "pattern"):
        out["pattern"] = pattern_json
    else:
        out["pattern"] = None
    return out

def write_AnonymousStructure42(obj: Dict[AnonymousStructure42Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    out["language"] = obj["language"]
    if obj.get("scheme") is not None:
        out["scheme"] = obj.get("scheme")
    if obj.get("pattern") is not None:
        out["pattern"] = obj.get("pattern")
    return out


AnonymousStructure43Keys = Literal["language","scheme","pattern"]

def parse_AnonymousStructure43(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure43Keys, Any]:
    out: Dict[AnonymousStructure43Keys, Any] = {}
    if language_json := json_get_optional_string(obj, "language"):
        out["language"] = language_json
    else:
        out["language"] = None
    out["scheme"] = json_get_string(obj, "scheme")
    if pattern_json := json_get_optional_string(obj, "pattern"):
        out["pattern"] = pattern_json
    else:
        out["pattern"] = None
    return out

def write_AnonymousStructure43(obj: Dict[AnonymousStructure43Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    if obj.get("language") is not None:
        out["language"] = obj.get("language")
    out["scheme"] = obj["scheme"]
    if obj.get("pattern") is not None:
        out["pattern"] = obj.get("pattern")
    return out


AnonymousStructure44Keys = Literal["language","scheme","pattern"]

def parse_AnonymousStructure44(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure44Keys, Any]:
    out: Dict[AnonymousStructure44Keys, Any] = {}
    if language_json := json_get_optional_string(obj, "language"):
        out["language"] = language_json
    else:
        out["language"] = None
    if scheme_json := json_get_optional_string(obj, "scheme"):
        out["scheme"] = scheme_json
    else:
        out["scheme"] = None
    out["pattern"] = json_get_string(obj, "pattern")
    return out

def write_AnonymousStructure44(obj: Dict[AnonymousStructure44Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    if obj.get("language") is not None:
        out["language"] = obj.get("language")
    if obj.get("scheme") is not None:
        out["scheme"] = obj.get("scheme")
    out["pattern"] = obj["pattern"]
    return out


# A document filter denotes a document by different properties like
# the [language](#TextDocument.languageId), the [scheme](#Uri.scheme) of
# its resource, or a glob-pattern that is applied to the [path](#TextDocument.fileName).
# 
# Glob patterns can have the following syntax:
# - `*` to match one or more characters in a path segment
# - `?` to match on one character in a path segment
# - `**` to match any number of path segments, including none
# - `{}` to group sub patterns into an OR expression. (e.g. `**​/*.{ts,js}` matches all TypeScript and JavaScript files)
# - `[]` to declare a range of characters to match in a path segment (e.g., `example.[0-9]` to match on `example.0`, `example.1`, …)
# - `[!...]` to negate a range of characters to match in a path segment (e.g., `example.[!0-9]` to match on `example.a`, `example.b`, but not `example.0`)
# 
# @sample A language filter that applies to typescript files on disk: `{ language: 'typescript', scheme: 'file' }`
# @sample A language filter that applies to all package.json paths: `{ language: 'json', pattern: '**package.json' }`
# 
# @since 3.17.0
TextDocumentFilter = Union[Dict[AnonymousStructure42Keys, Any], Dict[AnonymousStructure43Keys, Any], Dict[AnonymousStructure44Keys, Any]]

def parse_TextDocumentFilter(arg: JSON_VALUE) -> TextDocumentFilter:
    return parse_or_type((arg), (lambda v: parse_AnonymousStructure42(json_assert_type_object(v)), lambda v: parse_AnonymousStructure43(json_assert_type_object(v)), lambda v: parse_AnonymousStructure44(json_assert_type_object(v))))

def write_TextDocumentFilter(arg: TextDocumentFilter) -> JSON_VALUE:
    return write_or_type(arg, (lambda i: isinstance(i, Dict) and "language" in i.keys(), lambda i: isinstance(i, Dict) and "scheme" in i.keys(), lambda i: isinstance(i, Dict) and "pattern" in i.keys()), (lambda i: write_AnonymousStructure42(i), lambda i: write_AnonymousStructure43(i), lambda i: write_AnonymousStructure44(i)))


AnonymousStructure45Keys = Literal["notebookType","scheme","pattern"]

def parse_AnonymousStructure45(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure45Keys, Any]:
    out: Dict[AnonymousStructure45Keys, Any] = {}
    out["notebookType"] = json_get_string(obj, "notebookType")
    if scheme_json := json_get_optional_string(obj, "scheme"):
        out["scheme"] = scheme_json
    else:
        out["scheme"] = None
    if pattern_json := json_get_optional_string(obj, "pattern"):
        out["pattern"] = pattern_json
    else:
        out["pattern"] = None
    return out

def write_AnonymousStructure45(obj: Dict[AnonymousStructure45Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    out["notebookType"] = obj["notebookType"]
    if obj.get("scheme") is not None:
        out["scheme"] = obj.get("scheme")
    if obj.get("pattern") is not None:
        out["pattern"] = obj.get("pattern")
    return out


AnonymousStructure46Keys = Literal["notebookType","scheme","pattern"]

def parse_AnonymousStructure46(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure46Keys, Any]:
    out: Dict[AnonymousStructure46Keys, Any] = {}
    if notebookType_json := json_get_optional_string(obj, "notebookType"):
        out["notebookType"] = notebookType_json
    else:
        out["notebookType"] = None
    out["scheme"] = json_get_string(obj, "scheme")
    if pattern_json := json_get_optional_string(obj, "pattern"):
        out["pattern"] = pattern_json
    else:
        out["pattern"] = None
    return out

def write_AnonymousStructure46(obj: Dict[AnonymousStructure46Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    if obj.get("notebookType") is not None:
        out["notebookType"] = obj.get("notebookType")
    out["scheme"] = obj["scheme"]
    if obj.get("pattern") is not None:
        out["pattern"] = obj.get("pattern")
    return out


AnonymousStructure47Keys = Literal["notebookType","scheme","pattern"]

def parse_AnonymousStructure47(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure47Keys, Any]:
    out: Dict[AnonymousStructure47Keys, Any] = {}
    if notebookType_json := json_get_optional_string(obj, "notebookType"):
        out["notebookType"] = notebookType_json
    else:
        out["notebookType"] = None
    if scheme_json := json_get_optional_string(obj, "scheme"):
        out["scheme"] = scheme_json
    else:
        out["scheme"] = None
    out["pattern"] = json_get_string(obj, "pattern")
    return out

def write_AnonymousStructure47(obj: Dict[AnonymousStructure47Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    if obj.get("notebookType") is not None:
        out["notebookType"] = obj.get("notebookType")
    if obj.get("scheme") is not None:
        out["scheme"] = obj.get("scheme")
    out["pattern"] = obj["pattern"]
    return out


# A notebook document filter denotes a notebook document by
# different properties. The properties will be match
# against the notebook's URI (same as with documents)
# 
# @since 3.17.0
NotebookDocumentFilter = Union[Dict[AnonymousStructure45Keys, Any], Dict[AnonymousStructure46Keys, Any], Dict[AnonymousStructure47Keys, Any]]

def parse_NotebookDocumentFilter(arg: JSON_VALUE) -> NotebookDocumentFilter:
    return parse_or_type((arg), (lambda v: parse_AnonymousStructure45(json_assert_type_object(v)), lambda v: parse_AnonymousStructure46(json_assert_type_object(v)), lambda v: parse_AnonymousStructure47(json_assert_type_object(v))))

def write_NotebookDocumentFilter(arg: NotebookDocumentFilter) -> JSON_VALUE:
    return write_or_type(arg, (lambda i: isinstance(i, Dict) and "notebookType" in i.keys(), lambda i: isinstance(i, Dict) and "scheme" in i.keys(), lambda i: isinstance(i, Dict) and "pattern" in i.keys()), (lambda i: write_AnonymousStructure45(i), lambda i: write_AnonymousStructure46(i), lambda i: write_AnonymousStructure47(i)))


@dataclass
class NotebookCellTextDocumentFilter():
    """
    A notebook cell text document filter denotes a cell text
    document by different properties.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # A filter that matches against the notebook
    # containing the notebook cell. If a string
    # value is provided it matches against the
    # notebook type. '*' matches every notebook.
    notebook: Union[str, "NotebookDocumentFilter"]
    
    # A language id like `python`.
    # 
    # Will be matched against the language id of the
    # notebook cell document. '*' matches every language.
    language: Optional[str]

    def __init__(self, *, notebook: Union[str, "NotebookDocumentFilter"], language: Optional[str] = None) -> None:
        """
        - notebook: A filter that matches against the notebook
            containing the notebook cell. If a string
            value is provided it matches against the
            notebook type. '*' matches every notebook.
        - language: A language id like `python`.
            
            Will be matched against the language id of the
            notebook cell document. '*' matches every language.
        """
        self.notebook = notebook
        self.language = language

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "NotebookCellTextDocumentFilter":
        notebook = parse_or_type(obj["notebook"], (lambda v: json_assert_type_string(v), lambda v: parse_NotebookDocumentFilter((v))))
        if language_json := json_get_optional_string(obj, "language"):
            language = language_json
        else:
            language = None
        return cls(notebook=notebook, language=language)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["notebook"] = write_or_type(self.notebook, (lambda i: isinstance(i, str), lambda i: (isinstance(i, Dict) and "notebookType" in i.keys()) or (isinstance(i, Dict) and "scheme" in i.keys()) or (isinstance(i, Dict) and "pattern" in i.keys())), (lambda i: i, lambda i: write_NotebookDocumentFilter(i)))
        if self.language is not None:
            out["language"] = self.language
        return out


# A document filter describes a top level text document or
# a notebook cell document.
# 
# @since 3.17.0 - proposed support for NotebookCellTextDocumentFilter.
DocumentFilter = Union["TextDocumentFilter", "NotebookCellTextDocumentFilter"]

def parse_DocumentFilter(arg: JSON_VALUE) -> DocumentFilter:
    return parse_or_type((arg), (lambda v: parse_TextDocumentFilter((v)), lambda v: NotebookCellTextDocumentFilter.from_json(json_assert_type_object(v))))

def write_DocumentFilter(arg: DocumentFilter) -> JSON_VALUE:
    return write_or_type(arg, (lambda i: (isinstance(i, Dict) and "language" in i.keys()) or (isinstance(i, Dict) and "scheme" in i.keys()) or (isinstance(i, Dict) and "pattern" in i.keys()), lambda i: isinstance(i, NotebookCellTextDocumentFilter)), (lambda i: write_TextDocumentFilter(i), lambda i: i.to_json()))


# A document selector is the combination of one or many document filters.
# 
# @sample `let sel:DocumentSelector = [{ language: 'typescript' }, { language: 'json', pattern: '**∕tsconfig.json' }]`;
# 
# The use of a string as a document filter is deprecated @since 3.16.0.
DocumentSelector = List["DocumentFilter"]

def parse_DocumentSelector(arg: JSON_VALUE) -> DocumentSelector:
    return [parse_DocumentFilter((i)) for i in json_assert_type_array(arg)]

def write_DocumentSelector(arg: DocumentSelector) -> JSON_VALUE:
    return [write_DocumentFilter(i) for i in arg]


@dataclass
class TextDocumentRegistrationOptions():
    """
    General text document registration options.

    *Generated from the TypeScript documentation*
    """

    # A document selector to identify the scope of the registration. If set to null
    # the document selector provided on the client side will be used.
    documentSelector: Union["DocumentSelector", None]

    def __init__(self, *, documentSelector: Union["DocumentSelector", None]) -> None:
        """
        - documentSelector: A document selector to identify the scope of the registration. If set to null
            the document selector provided on the client side will be used.
        """
        self.documentSelector = documentSelector

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "TextDocumentRegistrationOptions":
        documentSelector = parse_or_type(obj["documentSelector"], (lambda v: parse_DocumentSelector(json_assert_type_array(v)), lambda v: json_assert_type_null(v)))
        return cls(documentSelector=documentSelector)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["documentSelector"] = write_or_type(self.documentSelector, (lambda i: isinstance(i, List) and (len(i) == 0 or (((isinstance(i[0], Dict) and "language" in i[0].keys()) or (isinstance(i[0], Dict) and "scheme" in i[0].keys()) or (isinstance(i[0], Dict) and "pattern" in i[0].keys())) or (isinstance(i[0], NotebookCellTextDocumentFilter)))), lambda i: i is None), (lambda i: write_DocumentSelector(i), lambda i: i))
        return out


@dataclass
class ImplementationOptions():
    """


    *Generated from the TypeScript documentation*
    """

    workDoneProgress: Optional[bool]

    def __init__(self, *, workDoneProgress: Optional[bool] = None) -> None:
        """
    
        """
        self.workDoneProgress = workDoneProgress

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "ImplementationOptions":
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        return cls(workDoneProgress=workDoneProgress)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        return out


@dataclass
class ImplementationRegistrationOptions(TextDocumentRegistrationOptions, ImplementationOptions):
    """


    *Generated from the TypeScript documentation*
    """

    # A document selector to identify the scope of the registration. If set to null
    # the document selector provided on the client side will be used.
    documentSelector: Union["DocumentSelector", None]
    
    workDoneProgress: Optional[bool]
    
    # The id used to register the request. The id can be used to deregister
    # the request again. See also Registration#id.
    id: Optional[str]

    def __init__(self, *, documentSelector: Union["DocumentSelector", None], workDoneProgress: Optional[bool] = None, id: Optional[str] = None) -> None:
        """
        - documentSelector: A document selector to identify the scope of the registration. If set to null
            the document selector provided on the client side will be used.
        - id: The id used to register the request. The id can be used to deregister
            the request again. See also Registration#id.
        """
        self.documentSelector = documentSelector
        self.workDoneProgress = workDoneProgress
        self.id = id

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "ImplementationRegistrationOptions":
        documentSelector = parse_or_type(obj["documentSelector"], (lambda v: parse_DocumentSelector(json_assert_type_array(v)), lambda v: json_assert_type_null(v)))
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        if id_json := json_get_optional_string(obj, "id"):
            id = id_json
        else:
            id = None
        return cls(documentSelector=documentSelector, workDoneProgress=workDoneProgress, id=id)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["documentSelector"] = write_or_type(self.documentSelector, (lambda i: isinstance(i, List) and (len(i) == 0 or (((isinstance(i[0], Dict) and "language" in i[0].keys()) or (isinstance(i[0], Dict) and "scheme" in i[0].keys()) or (isinstance(i[0], Dict) and "pattern" in i[0].keys())) or (isinstance(i[0], NotebookCellTextDocumentFilter)))), lambda i: i is None), (lambda i: write_DocumentSelector(i), lambda i: i))
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        if self.id is not None:
            out["id"] = self.id
        return out


@dataclass
class TypeDefinitionParams(TextDocumentPositionParams):
    """


    *Generated from the TypeScript documentation*
    """

    # The text document.
    textDocument: "TextDocumentIdentifier"
    
    # The position inside the text document.
    position: "Position"
    
    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]
    
    # An optional token that a server can use to report partial results (e.g. streaming) to
    # the client.
    partialResultToken: Optional["ProgressToken"]

    def __init__(self, *, textDocument: "TextDocumentIdentifier", position: "Position", workDoneToken: Optional["ProgressToken"] = None, partialResultToken: Optional["ProgressToken"] = None) -> None:
        """
        - textDocument: The text document.
        - position: The position inside the text document.
        - workDoneToken: An optional token that a server can use to report work done progress.
        - partialResultToken: An optional token that a server can use to report partial results (e.g. streaming) to
            the client.
        """
        self.textDocument = textDocument
        self.position = position
        self.workDoneToken = workDoneToken
        self.partialResultToken = partialResultToken

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "TypeDefinitionParams":
        textDocument = TextDocumentIdentifier.from_json(json_get_object(obj, "textDocument"))
        position = Position.from_json(json_get_object(obj, "position"))
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        if partialResultToken_json := obj.get("partialResultToken"):
            partialResultToken = parse_ProgressToken(partialResultToken_json)
        else:
            partialResultToken = None
        return cls(textDocument=textDocument, position=position, workDoneToken=workDoneToken, partialResultToken=partialResultToken)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["textDocument"] = self.textDocument.to_json()
        out["position"] = self.position.to_json()
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        if self.partialResultToken is not None:
            out["partialResultToken"] = write_ProgressToken(self.partialResultToken)
        return out


@dataclass
class TypeDefinitionOptions():
    """


    *Generated from the TypeScript documentation*
    """

    workDoneProgress: Optional[bool]

    def __init__(self, *, workDoneProgress: Optional[bool] = None) -> None:
        """
    
        """
        self.workDoneProgress = workDoneProgress

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "TypeDefinitionOptions":
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        return cls(workDoneProgress=workDoneProgress)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        return out


@dataclass
class TypeDefinitionRegistrationOptions(TextDocumentRegistrationOptions, TypeDefinitionOptions):
    """


    *Generated from the TypeScript documentation*
    """

    # A document selector to identify the scope of the registration. If set to null
    # the document selector provided on the client side will be used.
    documentSelector: Union["DocumentSelector", None]
    
    workDoneProgress: Optional[bool]
    
    # The id used to register the request. The id can be used to deregister
    # the request again. See also Registration#id.
    id: Optional[str]

    def __init__(self, *, documentSelector: Union["DocumentSelector", None], workDoneProgress: Optional[bool] = None, id: Optional[str] = None) -> None:
        """
        - documentSelector: A document selector to identify the scope of the registration. If set to null
            the document selector provided on the client side will be used.
        - id: The id used to register the request. The id can be used to deregister
            the request again. See also Registration#id.
        """
        self.documentSelector = documentSelector
        self.workDoneProgress = workDoneProgress
        self.id = id

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "TypeDefinitionRegistrationOptions":
        documentSelector = parse_or_type(obj["documentSelector"], (lambda v: parse_DocumentSelector(json_assert_type_array(v)), lambda v: json_assert_type_null(v)))
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        if id_json := json_get_optional_string(obj, "id"):
            id = id_json
        else:
            id = None
        return cls(documentSelector=documentSelector, workDoneProgress=workDoneProgress, id=id)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["documentSelector"] = write_or_type(self.documentSelector, (lambda i: isinstance(i, List) and (len(i) == 0 or (((isinstance(i[0], Dict) and "language" in i[0].keys()) or (isinstance(i[0], Dict) and "scheme" in i[0].keys()) or (isinstance(i[0], Dict) and "pattern" in i[0].keys())) or (isinstance(i[0], NotebookCellTextDocumentFilter)))), lambda i: i is None), (lambda i: write_DocumentSelector(i), lambda i: i))
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        if self.id is not None:
            out["id"] = self.id
        return out


@dataclass
class WorkspaceFolder():
    """
    A workspace folder inside a client.

    *Generated from the TypeScript documentation*
    """

    # The associated URI for this workspace folder.
    uri: str
    
    # The name of the workspace folder. Used to refer to this
    # workspace folder in the user interface.
    name: str

    def __init__(self, *, uri: str, name: str) -> None:
        """
        - uri: The associated URI for this workspace folder.
        - name: The name of the workspace folder. Used to refer to this
            workspace folder in the user interface.
        """
        self.uri = uri
        self.name = name

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "WorkspaceFolder":
        uri = json_get_string(obj, "uri")
        name = json_get_string(obj, "name")
        return cls(uri=uri, name=name)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["uri"] = self.uri
        out["name"] = self.name
        return out


@dataclass
class WorkspaceFoldersChangeEvent():
    """
    The workspace folder change event.

    *Generated from the TypeScript documentation*
    """

    # The array of added workspace folders
    added: List["WorkspaceFolder"]
    
    # The array of the removed workspace folders
    removed: List["WorkspaceFolder"]

    def __init__(self, *, added: List["WorkspaceFolder"], removed: List["WorkspaceFolder"]) -> None:
        """
        - added: The array of added workspace folders
        - removed: The array of the removed workspace folders
        """
        self.added = added
        self.removed = removed

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "WorkspaceFoldersChangeEvent":
        added = [WorkspaceFolder.from_json(json_assert_type_object(i)) for i in json_get_array(obj, "added")]
        removed = [WorkspaceFolder.from_json(json_assert_type_object(i)) for i in json_get_array(obj, "removed")]
        return cls(added=added, removed=removed)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["added"] = [i.to_json() for i in self.added]
        out["removed"] = [i.to_json() for i in self.removed]
        return out


@dataclass
class DidChangeWorkspaceFoldersParams():
    """
    The parameters of a `workspace/didChangeWorkspaceFolders` notification.

    *Generated from the TypeScript documentation*
    """

    # The actual workspace folder change event.
    event: "WorkspaceFoldersChangeEvent"

    def __init__(self, *, event: "WorkspaceFoldersChangeEvent") -> None:
        """
        - event: The actual workspace folder change event.
        """
        self.event = event

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DidChangeWorkspaceFoldersParams":
        event = WorkspaceFoldersChangeEvent.from_json(json_get_object(obj, "event"))
        return cls(event=event)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["event"] = self.event.to_json()
        return out


@dataclass
class ConfigurationItem():
    """


    *Generated from the TypeScript documentation*
    """

    # The scope to get the configuration section for.
    scopeUri: Optional[str]
    
    # The configuration section asked for.
    section: Optional[str]

    def __init__(self, *, scopeUri: Optional[str] = None, section: Optional[str] = None) -> None:
        """
        - scopeUri: The scope to get the configuration section for.
        - section: The configuration section asked for.
        """
        self.scopeUri = scopeUri
        self.section = section

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "ConfigurationItem":
        if scopeUri_json := json_get_optional_string(obj, "scopeUri"):
            scopeUri = scopeUri_json
        else:
            scopeUri = None
        if section_json := json_get_optional_string(obj, "section"):
            section = section_json
        else:
            section = None
        return cls(scopeUri=scopeUri, section=section)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.scopeUri is not None:
            out["scopeUri"] = self.scopeUri
        if self.section is not None:
            out["section"] = self.section
        return out


@dataclass
class ConfigurationParams():
    """
    The parameters of a configuration request.

    *Generated from the TypeScript documentation*
    """

    items: List["ConfigurationItem"]

    def __init__(self, *, items: List["ConfigurationItem"]) -> None:
        """
    
        """
        self.items = items

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "ConfigurationParams":
        items = [ConfigurationItem.from_json(json_assert_type_object(i)) for i in json_get_array(obj, "items")]
        return cls(items=items)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["items"] = [i.to_json() for i in self.items]
        return out


@dataclass
class PartialResultParams():
    """


    *Generated from the TypeScript documentation*
    """

    # An optional token that a server can use to report partial results (e.g. streaming) to
    # the client.
    partialResultToken: Optional["ProgressToken"]

    def __init__(self, *, partialResultToken: Optional["ProgressToken"] = None) -> None:
        """
        - partialResultToken: An optional token that a server can use to report partial results (e.g. streaming) to
            the client.
        """
        self.partialResultToken = partialResultToken

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "PartialResultParams":
        if partialResultToken_json := obj.get("partialResultToken"):
            partialResultToken = parse_ProgressToken(partialResultToken_json)
        else:
            partialResultToken = None
        return cls(partialResultToken=partialResultToken)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.partialResultToken is not None:
            out["partialResultToken"] = write_ProgressToken(self.partialResultToken)
        return out


@dataclass
class DocumentColorParams():
    """
    Parameters for a [DocumentColorRequest](#DocumentColorRequest).

    *Generated from the TypeScript documentation*
    """

    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]
    
    # An optional token that a server can use to report partial results (e.g. streaming) to
    # the client.
    partialResultToken: Optional["ProgressToken"]
    
    # The text document.
    textDocument: "TextDocumentIdentifier"

    def __init__(self, *, workDoneToken: Optional["ProgressToken"] = None, partialResultToken: Optional["ProgressToken"] = None, textDocument: "TextDocumentIdentifier") -> None:
        """
        - workDoneToken: An optional token that a server can use to report work done progress.
        - partialResultToken: An optional token that a server can use to report partial results (e.g. streaming) to
            the client.
        - textDocument: The text document.
        """
        self.workDoneToken = workDoneToken
        self.partialResultToken = partialResultToken
        self.textDocument = textDocument

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DocumentColorParams":
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        if partialResultToken_json := obj.get("partialResultToken"):
            partialResultToken = parse_ProgressToken(partialResultToken_json)
        else:
            partialResultToken = None
        textDocument = TextDocumentIdentifier.from_json(json_get_object(obj, "textDocument"))
        return cls(workDoneToken=workDoneToken, partialResultToken=partialResultToken, textDocument=textDocument)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        if self.partialResultToken is not None:
            out["partialResultToken"] = write_ProgressToken(self.partialResultToken)
        out["textDocument"] = self.textDocument.to_json()
        return out


@dataclass
class Color():
    """
    Represents a color in RGBA space.

    *Generated from the TypeScript documentation*
    """

    # The red component of this color in the range [0-1].
    red: float
    
    # The green component of this color in the range [0-1].
    green: float
    
    # The blue component of this color in the range [0-1].
    blue: float
    
    # The alpha component of this color in the range [0-1].
    alpha: float

    def __init__(self, *, red: float, green: float, blue: float, alpha: float) -> None:
        """
        - red: The red component of this color in the range [0-1].
        - green: The green component of this color in the range [0-1].
        - blue: The blue component of this color in the range [0-1].
        - alpha: The alpha component of this color in the range [0-1].
        """
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "Color":
        red = json_get_float(obj, "red")
        green = json_get_float(obj, "green")
        blue = json_get_float(obj, "blue")
        alpha = json_get_float(obj, "alpha")
        return cls(red=red, green=green, blue=blue, alpha=alpha)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["red"] = self.red
        out["green"] = self.green
        out["blue"] = self.blue
        out["alpha"] = self.alpha
        return out


@dataclass
class ColorInformation():
    """
    Represents a color range from a document.

    *Generated from the TypeScript documentation*
    """

    # The range in the document where this color appears.
    range: "Range"
    
    # The actual color value for this color range.
    color: "Color"

    def __init__(self, *, range: "Range", color: "Color") -> None:
        """
        - range: The range in the document where this color appears.
        - color: The actual color value for this color range.
        """
        self.range = range
        self.color = color

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "ColorInformation":
        range = Range.from_json(json_get_object(obj, "range"))
        color = Color.from_json(json_get_object(obj, "color"))
        return cls(range=range, color=color)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["range"] = self.range.to_json()
        out["color"] = self.color.to_json()
        return out


@dataclass
class DocumentColorOptions():
    """


    *Generated from the TypeScript documentation*
    """

    workDoneProgress: Optional[bool]

    def __init__(self, *, workDoneProgress: Optional[bool] = None) -> None:
        """
    
        """
        self.workDoneProgress = workDoneProgress

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DocumentColorOptions":
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        return cls(workDoneProgress=workDoneProgress)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        return out


@dataclass
class DocumentColorRegistrationOptions(TextDocumentRegistrationOptions, DocumentColorOptions):
    """


    *Generated from the TypeScript documentation*
    """

    # A document selector to identify the scope of the registration. If set to null
    # the document selector provided on the client side will be used.
    documentSelector: Union["DocumentSelector", None]
    
    workDoneProgress: Optional[bool]
    
    # The id used to register the request. The id can be used to deregister
    # the request again. See also Registration#id.
    id: Optional[str]

    def __init__(self, *, documentSelector: Union["DocumentSelector", None], workDoneProgress: Optional[bool] = None, id: Optional[str] = None) -> None:
        """
        - documentSelector: A document selector to identify the scope of the registration. If set to null
            the document selector provided on the client side will be used.
        - id: The id used to register the request. The id can be used to deregister
            the request again. See also Registration#id.
        """
        self.documentSelector = documentSelector
        self.workDoneProgress = workDoneProgress
        self.id = id

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DocumentColorRegistrationOptions":
        documentSelector = parse_or_type(obj["documentSelector"], (lambda v: parse_DocumentSelector(json_assert_type_array(v)), lambda v: json_assert_type_null(v)))
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        if id_json := json_get_optional_string(obj, "id"):
            id = id_json
        else:
            id = None
        return cls(documentSelector=documentSelector, workDoneProgress=workDoneProgress, id=id)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["documentSelector"] = write_or_type(self.documentSelector, (lambda i: isinstance(i, List) and (len(i) == 0 or (((isinstance(i[0], Dict) and "language" in i[0].keys()) or (isinstance(i[0], Dict) and "scheme" in i[0].keys()) or (isinstance(i[0], Dict) and "pattern" in i[0].keys())) or (isinstance(i[0], NotebookCellTextDocumentFilter)))), lambda i: i is None), (lambda i: write_DocumentSelector(i), lambda i: i))
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        if self.id is not None:
            out["id"] = self.id
        return out


@dataclass
class ColorPresentationParams():
    """
    Parameters for a [ColorPresentationRequest](#ColorPresentationRequest).

    *Generated from the TypeScript documentation*
    """

    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]
    
    # An optional token that a server can use to report partial results (e.g. streaming) to
    # the client.
    partialResultToken: Optional["ProgressToken"]
    
    # The text document.
    textDocument: "TextDocumentIdentifier"
    
    # The color to request presentations for.
    color: "Color"
    
    # The range where the color would be inserted. Serves as a context.
    range: "Range"

    def __init__(self, *, workDoneToken: Optional["ProgressToken"] = None, partialResultToken: Optional["ProgressToken"] = None, textDocument: "TextDocumentIdentifier", color: "Color", range: "Range") -> None:
        """
        - workDoneToken: An optional token that a server can use to report work done progress.
        - partialResultToken: An optional token that a server can use to report partial results (e.g. streaming) to
            the client.
        - textDocument: The text document.
        - color: The color to request presentations for.
        - range: The range where the color would be inserted. Serves as a context.
        """
        self.workDoneToken = workDoneToken
        self.partialResultToken = partialResultToken
        self.textDocument = textDocument
        self.color = color
        self.range = range

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "ColorPresentationParams":
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        if partialResultToken_json := obj.get("partialResultToken"):
            partialResultToken = parse_ProgressToken(partialResultToken_json)
        else:
            partialResultToken = None
        textDocument = TextDocumentIdentifier.from_json(json_get_object(obj, "textDocument"))
        color = Color.from_json(json_get_object(obj, "color"))
        range = Range.from_json(json_get_object(obj, "range"))
        return cls(workDoneToken=workDoneToken, partialResultToken=partialResultToken, textDocument=textDocument, color=color, range=range)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        if self.partialResultToken is not None:
            out["partialResultToken"] = write_ProgressToken(self.partialResultToken)
        out["textDocument"] = self.textDocument.to_json()
        out["color"] = self.color.to_json()
        out["range"] = self.range.to_json()
        return out


@dataclass
class TextEdit():
    """
    A text edit applicable to a text document.

    *Generated from the TypeScript documentation*
    """

    # The range of the text document to be manipulated. To insert
    # text into a document create a range where start === end.
    range: "Range"
    
    # The string to be inserted. For delete operations use an
    # empty string.
    newText: str

    def __init__(self, *, range: "Range", newText: str) -> None:
        """
        - range: The range of the text document to be manipulated. To insert
            text into a document create a range where start === end.
        - newText: The string to be inserted. For delete operations use an
            empty string.
        """
        self.range = range
        self.newText = newText

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "TextEdit":
        range = Range.from_json(json_get_object(obj, "range"))
        newText = json_get_string(obj, "newText")
        return cls(range=range, newText=newText)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["range"] = self.range.to_json()
        out["newText"] = self.newText
        return out


@dataclass
class ColorPresentation():
    """


    *Generated from the TypeScript documentation*
    """

    # The label of this color presentation. It will be shown on the color
    # picker header. By default this is also the text that is inserted when selecting
    # this color presentation.
    label: str
    
    # An [edit](#TextEdit) which is applied to a document when selecting
    # this presentation for the color.  When `falsy` the [label](#ColorPresentation.label)
    # is used.
    textEdit: Optional["TextEdit"]
    
    # An optional array of additional [text edits](#TextEdit) that are applied when
    # selecting this color presentation. Edits must not overlap with the main [edit](#ColorPresentation.textEdit) nor with themselves.
    additionalTextEdits: Optional[List["TextEdit"]]

    def __init__(self, *, label: str, textEdit: Optional["TextEdit"] = None, additionalTextEdits: Optional[List["TextEdit"]] = None) -> None:
        """
        - label: The label of this color presentation. It will be shown on the color
            picker header. By default this is also the text that is inserted when selecting
            this color presentation.
        - textEdit: An [edit](#TextEdit) which is applied to a document when selecting
            this presentation for the color.  When `falsy` the [label](#ColorPresentation.label)
            is used.
        - additionalTextEdits: An optional array of additional [text edits](#TextEdit) that are applied when
            selecting this color presentation. Edits must not overlap with the main [edit](#ColorPresentation.textEdit) nor with themselves.
        """
        self.label = label
        self.textEdit = textEdit
        self.additionalTextEdits = additionalTextEdits

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "ColorPresentation":
        label = json_get_string(obj, "label")
        if textEdit_json := json_get_optional_object(obj, "textEdit"):
            textEdit = TextEdit.from_json(textEdit_json)
        else:
            textEdit = None
        if additionalTextEdits_json := json_get_optional_array(obj, "additionalTextEdits"):
            additionalTextEdits = [TextEdit.from_json(json_assert_type_object(i)) for i in additionalTextEdits_json]
        else:
            additionalTextEdits = None
        return cls(label=label, textEdit=textEdit, additionalTextEdits=additionalTextEdits)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["label"] = self.label
        if self.textEdit is not None:
            out["textEdit"] = self.textEdit.to_json()
        if self.additionalTextEdits is not None:
            out["additionalTextEdits"] = [i.to_json() for i in self.additionalTextEdits]
        return out


@dataclass
class WorkDoneProgressOptions():
    """


    *Generated from the TypeScript documentation*
    """

    workDoneProgress: Optional[bool]

    def __init__(self, *, workDoneProgress: Optional[bool] = None) -> None:
        """
    
        """
        self.workDoneProgress = workDoneProgress

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "WorkDoneProgressOptions":
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        return cls(workDoneProgress=workDoneProgress)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        return out


@dataclass
class FoldingRangeParams():
    """
    Parameters for a [FoldingRangeRequest](#FoldingRangeRequest).

    *Generated from the TypeScript documentation*
    """

    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]
    
    # An optional token that a server can use to report partial results (e.g. streaming) to
    # the client.
    partialResultToken: Optional["ProgressToken"]
    
    # The text document.
    textDocument: "TextDocumentIdentifier"

    def __init__(self, *, workDoneToken: Optional["ProgressToken"] = None, partialResultToken: Optional["ProgressToken"] = None, textDocument: "TextDocumentIdentifier") -> None:
        """
        - workDoneToken: An optional token that a server can use to report work done progress.
        - partialResultToken: An optional token that a server can use to report partial results (e.g. streaming) to
            the client.
        - textDocument: The text document.
        """
        self.workDoneToken = workDoneToken
        self.partialResultToken = partialResultToken
        self.textDocument = textDocument

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "FoldingRangeParams":
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        if partialResultToken_json := obj.get("partialResultToken"):
            partialResultToken = parse_ProgressToken(partialResultToken_json)
        else:
            partialResultToken = None
        textDocument = TextDocumentIdentifier.from_json(json_get_object(obj, "textDocument"))
        return cls(workDoneToken=workDoneToken, partialResultToken=partialResultToken, textDocument=textDocument)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        if self.partialResultToken is not None:
            out["partialResultToken"] = write_ProgressToken(self.partialResultToken)
        out["textDocument"] = self.textDocument.to_json()
        return out


@dataclass
class FoldingRange():
    """
    Represents a folding range. To be valid, start and end line must be bigger than zero and smaller
    than the number of lines in the document. Clients are free to ignore invalid ranges.

    *Generated from the TypeScript documentation*
    """

    # The zero-based start line of the range to fold. The folded area starts after the line's last character.
    # To be valid, the end must be zero or larger and smaller than the number of lines in the document.
    startLine: int
    
    # The zero-based character offset from where the folded range starts. If not defined, defaults to the length of the start line.
    startCharacter: Optional[int]
    
    # The zero-based end line of the range to fold. The folded area ends with the line's last character.
    # To be valid, the end must be zero or larger and smaller than the number of lines in the document.
    endLine: int
    
    # The zero-based character offset before the folded range ends. If not defined, defaults to the length of the end line.
    endCharacter: Optional[int]
    
    # Describes the kind of the folding range such as `comment' or 'region'. The kind
    # is used to categorize folding ranges and used by commands like 'Fold all comments'.
    # See [FoldingRangeKind](#FoldingRangeKind) for an enumeration of standardized kinds.
    kind: Optional["FoldingRangeKind"]
    
    # The text that the client should show when the specified range is
    # collapsed. If not defined or not supported by the client, a default
    # will be chosen by the client.
    # 
    # @since 3.17.0
    collapsedText: Optional[str]

    def __init__(self, *, startLine: int, startCharacter: Optional[int] = None, endLine: int, endCharacter: Optional[int] = None, kind: Optional["FoldingRangeKind"] = None, collapsedText: Optional[str] = None) -> None:
        """
        - startLine: The zero-based start line of the range to fold. The folded area starts after the line's last character.
            To be valid, the end must be zero or larger and smaller than the number of lines in the document.
        - startCharacter: The zero-based character offset from where the folded range starts. If not defined, defaults to the length of the start line.
        - endLine: The zero-based end line of the range to fold. The folded area ends with the line's last character.
            To be valid, the end must be zero or larger and smaller than the number of lines in the document.
        - endCharacter: The zero-based character offset before the folded range ends. If not defined, defaults to the length of the end line.
        - kind: Describes the kind of the folding range such as `comment' or 'region'. The kind
            is used to categorize folding ranges and used by commands like 'Fold all comments'.
            See [FoldingRangeKind](#FoldingRangeKind) for an enumeration of standardized kinds.
        - collapsedText: The text that the client should show when the specified range is
            collapsed. If not defined or not supported by the client, a default
            will be chosen by the client.
            
            @since 3.17.0
        """
        self.startLine = startLine
        self.startCharacter = startCharacter
        self.endLine = endLine
        self.endCharacter = endCharacter
        self.kind = kind
        self.collapsedText = collapsedText

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "FoldingRange":
        startLine = json_get_int(obj, "startLine")
        if startCharacter_json := json_get_optional_int(obj, "startCharacter"):
            startCharacter = startCharacter_json
        else:
            startCharacter = None
        endLine = json_get_int(obj, "endLine")
        if endCharacter_json := json_get_optional_int(obj, "endCharacter"):
            endCharacter = endCharacter_json
        else:
            endCharacter = None
        if kind_json := json_get_optional_string(obj, "kind"):
            kind = FoldingRangeKind(kind_json)
        else:
            kind = None
        if collapsedText_json := json_get_optional_string(obj, "collapsedText"):
            collapsedText = collapsedText_json
        else:
            collapsedText = None
        return cls(startLine=startLine, startCharacter=startCharacter, endLine=endLine, endCharacter=endCharacter, kind=kind, collapsedText=collapsedText)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["startLine"] = self.startLine
        if self.startCharacter is not None:
            out["startCharacter"] = self.startCharacter
        out["endLine"] = self.endLine
        if self.endCharacter is not None:
            out["endCharacter"] = self.endCharacter
        if self.kind is not None:
            out["kind"] = self.kind.value
        if self.collapsedText is not None:
            out["collapsedText"] = self.collapsedText
        return out


@dataclass
class FoldingRangeOptions():
    """


    *Generated from the TypeScript documentation*
    """

    workDoneProgress: Optional[bool]

    def __init__(self, *, workDoneProgress: Optional[bool] = None) -> None:
        """
    
        """
        self.workDoneProgress = workDoneProgress

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "FoldingRangeOptions":
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        return cls(workDoneProgress=workDoneProgress)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        return out


@dataclass
class FoldingRangeRegistrationOptions(TextDocumentRegistrationOptions, FoldingRangeOptions):
    """


    *Generated from the TypeScript documentation*
    """

    # A document selector to identify the scope of the registration. If set to null
    # the document selector provided on the client side will be used.
    documentSelector: Union["DocumentSelector", None]
    
    workDoneProgress: Optional[bool]
    
    # The id used to register the request. The id can be used to deregister
    # the request again. See also Registration#id.
    id: Optional[str]

    def __init__(self, *, documentSelector: Union["DocumentSelector", None], workDoneProgress: Optional[bool] = None, id: Optional[str] = None) -> None:
        """
        - documentSelector: A document selector to identify the scope of the registration. If set to null
            the document selector provided on the client side will be used.
        - id: The id used to register the request. The id can be used to deregister
            the request again. See also Registration#id.
        """
        self.documentSelector = documentSelector
        self.workDoneProgress = workDoneProgress
        self.id = id

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "FoldingRangeRegistrationOptions":
        documentSelector = parse_or_type(obj["documentSelector"], (lambda v: parse_DocumentSelector(json_assert_type_array(v)), lambda v: json_assert_type_null(v)))
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        if id_json := json_get_optional_string(obj, "id"):
            id = id_json
        else:
            id = None
        return cls(documentSelector=documentSelector, workDoneProgress=workDoneProgress, id=id)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["documentSelector"] = write_or_type(self.documentSelector, (lambda i: isinstance(i, List) and (len(i) == 0 or (((isinstance(i[0], Dict) and "language" in i[0].keys()) or (isinstance(i[0], Dict) and "scheme" in i[0].keys()) or (isinstance(i[0], Dict) and "pattern" in i[0].keys())) or (isinstance(i[0], NotebookCellTextDocumentFilter)))), lambda i: i is None), (lambda i: write_DocumentSelector(i), lambda i: i))
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        if self.id is not None:
            out["id"] = self.id
        return out


@dataclass
class DeclarationParams(TextDocumentPositionParams):
    """


    *Generated from the TypeScript documentation*
    """

    # The text document.
    textDocument: "TextDocumentIdentifier"
    
    # The position inside the text document.
    position: "Position"
    
    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]
    
    # An optional token that a server can use to report partial results (e.g. streaming) to
    # the client.
    partialResultToken: Optional["ProgressToken"]

    def __init__(self, *, textDocument: "TextDocumentIdentifier", position: "Position", workDoneToken: Optional["ProgressToken"] = None, partialResultToken: Optional["ProgressToken"] = None) -> None:
        """
        - textDocument: The text document.
        - position: The position inside the text document.
        - workDoneToken: An optional token that a server can use to report work done progress.
        - partialResultToken: An optional token that a server can use to report partial results (e.g. streaming) to
            the client.
        """
        self.textDocument = textDocument
        self.position = position
        self.workDoneToken = workDoneToken
        self.partialResultToken = partialResultToken

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DeclarationParams":
        textDocument = TextDocumentIdentifier.from_json(json_get_object(obj, "textDocument"))
        position = Position.from_json(json_get_object(obj, "position"))
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        if partialResultToken_json := obj.get("partialResultToken"):
            partialResultToken = parse_ProgressToken(partialResultToken_json)
        else:
            partialResultToken = None
        return cls(textDocument=textDocument, position=position, workDoneToken=workDoneToken, partialResultToken=partialResultToken)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["textDocument"] = self.textDocument.to_json()
        out["position"] = self.position.to_json()
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        if self.partialResultToken is not None:
            out["partialResultToken"] = write_ProgressToken(self.partialResultToken)
        return out


@dataclass
class DeclarationOptions():
    """


    *Generated from the TypeScript documentation*
    """

    workDoneProgress: Optional[bool]

    def __init__(self, *, workDoneProgress: Optional[bool] = None) -> None:
        """
    
        """
        self.workDoneProgress = workDoneProgress

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DeclarationOptions":
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        return cls(workDoneProgress=workDoneProgress)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        return out


@dataclass
class DeclarationRegistrationOptions(DeclarationOptions, TextDocumentRegistrationOptions):
    """


    *Generated from the TypeScript documentation*
    """

    workDoneProgress: Optional[bool]
    
    # A document selector to identify the scope of the registration. If set to null
    # the document selector provided on the client side will be used.
    documentSelector: Union["DocumentSelector", None]
    
    # The id used to register the request. The id can be used to deregister
    # the request again. See also Registration#id.
    id: Optional[str]

    def __init__(self, *, workDoneProgress: Optional[bool] = None, documentSelector: Union["DocumentSelector", None], id: Optional[str] = None) -> None:
        """
        - documentSelector: A document selector to identify the scope of the registration. If set to null
            the document selector provided on the client side will be used.
        - id: The id used to register the request. The id can be used to deregister
            the request again. See also Registration#id.
        """
        self.workDoneProgress = workDoneProgress
        self.documentSelector = documentSelector
        self.id = id

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DeclarationRegistrationOptions":
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        documentSelector = parse_or_type(obj["documentSelector"], (lambda v: parse_DocumentSelector(json_assert_type_array(v)), lambda v: json_assert_type_null(v)))
        if id_json := json_get_optional_string(obj, "id"):
            id = id_json
        else:
            id = None
        return cls(workDoneProgress=workDoneProgress, documentSelector=documentSelector, id=id)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        out["documentSelector"] = write_or_type(self.documentSelector, (lambda i: isinstance(i, List) and (len(i) == 0 or (((isinstance(i[0], Dict) and "language" in i[0].keys()) or (isinstance(i[0], Dict) and "scheme" in i[0].keys()) or (isinstance(i[0], Dict) and "pattern" in i[0].keys())) or (isinstance(i[0], NotebookCellTextDocumentFilter)))), lambda i: i is None), (lambda i: write_DocumentSelector(i), lambda i: i))
        if self.id is not None:
            out["id"] = self.id
        return out


@dataclass
class SelectionRangeParams():
    """
    A parameter literal used in selection range requests.

    *Generated from the TypeScript documentation*
    """

    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]
    
    # An optional token that a server can use to report partial results (e.g. streaming) to
    # the client.
    partialResultToken: Optional["ProgressToken"]
    
    # The text document.
    textDocument: "TextDocumentIdentifier"
    
    # The positions inside the text document.
    positions: List["Position"]

    def __init__(self, *, workDoneToken: Optional["ProgressToken"] = None, partialResultToken: Optional["ProgressToken"] = None, textDocument: "TextDocumentIdentifier", positions: List["Position"]) -> None:
        """
        - workDoneToken: An optional token that a server can use to report work done progress.
        - partialResultToken: An optional token that a server can use to report partial results (e.g. streaming) to
            the client.
        - textDocument: The text document.
        - positions: The positions inside the text document.
        """
        self.workDoneToken = workDoneToken
        self.partialResultToken = partialResultToken
        self.textDocument = textDocument
        self.positions = positions

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "SelectionRangeParams":
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        if partialResultToken_json := obj.get("partialResultToken"):
            partialResultToken = parse_ProgressToken(partialResultToken_json)
        else:
            partialResultToken = None
        textDocument = TextDocumentIdentifier.from_json(json_get_object(obj, "textDocument"))
        positions = [Position.from_json(json_assert_type_object(i)) for i in json_get_array(obj, "positions")]
        return cls(workDoneToken=workDoneToken, partialResultToken=partialResultToken, textDocument=textDocument, positions=positions)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        if self.partialResultToken is not None:
            out["partialResultToken"] = write_ProgressToken(self.partialResultToken)
        out["textDocument"] = self.textDocument.to_json()
        out["positions"] = [i.to_json() for i in self.positions]
        return out


@dataclass
class SelectionRange():
    """
    A selection range represents a part of a selection hierarchy. A selection range
    may have a parent selection range that contains it.

    *Generated from the TypeScript documentation*
    """

    # The [range](#Range) of this selection range.
    range: "Range"
    
    # The parent selection range containing this range. Therefore `parent.range` must contain `this.range`.
    parent: Optional["SelectionRange"]

    def __init__(self, *, range: "Range", parent: Optional["SelectionRange"] = None) -> None:
        """
        - range: The [range](#Range) of this selection range.
        - parent: The parent selection range containing this range. Therefore `parent.range` must contain `this.range`.
        """
        self.range = range
        self.parent = parent

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "SelectionRange":
        range = Range.from_json(json_get_object(obj, "range"))
        if parent_json := json_get_optional_object(obj, "parent"):
            parent = SelectionRange.from_json(parent_json)
        else:
            parent = None
        return cls(range=range, parent=parent)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["range"] = self.range.to_json()
        if self.parent is not None:
            out["parent"] = self.parent.to_json()
        return out


@dataclass
class SelectionRangeOptions():
    """


    *Generated from the TypeScript documentation*
    """

    workDoneProgress: Optional[bool]

    def __init__(self, *, workDoneProgress: Optional[bool] = None) -> None:
        """
    
        """
        self.workDoneProgress = workDoneProgress

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "SelectionRangeOptions":
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        return cls(workDoneProgress=workDoneProgress)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        return out


@dataclass
class SelectionRangeRegistrationOptions(SelectionRangeOptions, TextDocumentRegistrationOptions):
    """


    *Generated from the TypeScript documentation*
    """

    workDoneProgress: Optional[bool]
    
    # A document selector to identify the scope of the registration. If set to null
    # the document selector provided on the client side will be used.
    documentSelector: Union["DocumentSelector", None]
    
    # The id used to register the request. The id can be used to deregister
    # the request again. See also Registration#id.
    id: Optional[str]

    def __init__(self, *, workDoneProgress: Optional[bool] = None, documentSelector: Union["DocumentSelector", None], id: Optional[str] = None) -> None:
        """
        - documentSelector: A document selector to identify the scope of the registration. If set to null
            the document selector provided on the client side will be used.
        - id: The id used to register the request. The id can be used to deregister
            the request again. See also Registration#id.
        """
        self.workDoneProgress = workDoneProgress
        self.documentSelector = documentSelector
        self.id = id

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "SelectionRangeRegistrationOptions":
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        documentSelector = parse_or_type(obj["documentSelector"], (lambda v: parse_DocumentSelector(json_assert_type_array(v)), lambda v: json_assert_type_null(v)))
        if id_json := json_get_optional_string(obj, "id"):
            id = id_json
        else:
            id = None
        return cls(workDoneProgress=workDoneProgress, documentSelector=documentSelector, id=id)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        out["documentSelector"] = write_or_type(self.documentSelector, (lambda i: isinstance(i, List) and (len(i) == 0 or (((isinstance(i[0], Dict) and "language" in i[0].keys()) or (isinstance(i[0], Dict) and "scheme" in i[0].keys()) or (isinstance(i[0], Dict) and "pattern" in i[0].keys())) or (isinstance(i[0], NotebookCellTextDocumentFilter)))), lambda i: i is None), (lambda i: write_DocumentSelector(i), lambda i: i))
        if self.id is not None:
            out["id"] = self.id
        return out


@dataclass
class WorkDoneProgressCreateParams():
    """


    *Generated from the TypeScript documentation*
    """

    # The token to be used to report progress.
    token: "ProgressToken"

    def __init__(self, *, token: "ProgressToken") -> None:
        """
        - token: The token to be used to report progress.
        """
        self.token = token

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "WorkDoneProgressCreateParams":
        token = parse_ProgressToken(obj["token"])
        return cls(token=token)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["token"] = write_ProgressToken(self.token)
        return out


@dataclass
class WorkDoneProgressCancelParams():
    """


    *Generated from the TypeScript documentation*
    """

    # The token to be used to report progress.
    token: "ProgressToken"

    def __init__(self, *, token: "ProgressToken") -> None:
        """
        - token: The token to be used to report progress.
        """
        self.token = token

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "WorkDoneProgressCancelParams":
        token = parse_ProgressToken(obj["token"])
        return cls(token=token)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["token"] = write_ProgressToken(self.token)
        return out


@dataclass
class CallHierarchyPrepareParams(TextDocumentPositionParams):
    """
    The parameter of a `textDocument/prepareCallHierarchy` request.
    
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # The text document.
    textDocument: "TextDocumentIdentifier"
    
    # The position inside the text document.
    position: "Position"
    
    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]

    def __init__(self, *, textDocument: "TextDocumentIdentifier", position: "Position", workDoneToken: Optional["ProgressToken"] = None) -> None:
        """
        - textDocument: The text document.
        - position: The position inside the text document.
        - workDoneToken: An optional token that a server can use to report work done progress.
        """
        self.textDocument = textDocument
        self.position = position
        self.workDoneToken = workDoneToken

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "CallHierarchyPrepareParams":
        textDocument = TextDocumentIdentifier.from_json(json_get_object(obj, "textDocument"))
        position = Position.from_json(json_get_object(obj, "position"))
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        return cls(textDocument=textDocument, position=position, workDoneToken=workDoneToken)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["textDocument"] = self.textDocument.to_json()
        out["position"] = self.position.to_json()
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        return out


@dataclass
class LSPObject():
    """
    LSP object definition.
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """





    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "LSPObject":
    
        return cls()

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
    
        return out


# LSP arrays.
# @since 3.17.0
LSPArray = List["LSPAny"]

def parse_LSPArray(arg: JSON_VALUE) -> LSPArray:
    return [parse_LSPAny((i)) for i in json_assert_type_array(arg)]

def write_LSPArray(arg: LSPArray) -> JSON_VALUE:
    return [write_LSPAny(i) for i in arg]


# The LSP any type.
# Please note that strictly speaking a property with the value `undefined`
# can't be converted into JSON preserving the property name. However for
# convenience it is allowed and assumed that all these properties are
# optional as well.
# @since 3.17.0
LSPAny = Union["LSPObject", "LSPArray", str, int, int, float, bool, None]

def parse_LSPAny(arg: JSON_VALUE) -> LSPAny:
    return parse_or_type((arg), (lambda v: LSPObject.from_json(json_assert_type_object(v)), lambda v: parse_LSPArray(json_assert_type_array(v)), lambda v: json_assert_type_string(v), lambda v: json_assert_type_int(v), lambda v: json_assert_type_int(v), lambda v: json_assert_type_float(v), lambda v: json_assert_type_bool(v), lambda v: json_assert_type_null(v)))

def write_LSPAny(arg: LSPAny) -> JSON_VALUE:
    return write_or_type(arg, (lambda i: isinstance(i, LSPObject), lambda i: isinstance(i, List) and (len(i) == 0 or (True)), lambda i: isinstance(i, str), lambda i: isinstance(i, int), lambda i: isinstance(i, int), lambda i: isinstance(i, float), lambda i: isinstance(i, bool), lambda i: i is None), (lambda i: i.to_json(), lambda i: write_LSPArray(i), lambda i: i, lambda i: i, lambda i: i, lambda i: i, lambda i: i, lambda i: i))


@dataclass
class CallHierarchyItem():
    """
    Represents programming constructs like functions or constructors in the context
    of call hierarchy.
    
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # The name of this item.
    name: str
    
    # The kind of this item.
    kind: "SymbolKind"
    
    # Tags for this item.
    tags: Optional[List["SymbolTag"]]
    
    # More detail for this item, e.g. the signature of a function.
    detail: Optional[str]
    
    # The resource identifier of this item.
    uri: str
    
    # The range enclosing this symbol not including leading/trailing whitespace but everything else, e.g. comments and code.
    range: "Range"
    
    # The range that should be selected and revealed when this symbol is being picked, e.g. the name of a function.
    # Must be contained by the [`range`](#CallHierarchyItem.range).
    selectionRange: "Range"
    
    # A data entry field that is preserved between a call hierarchy prepare and
    # incoming calls or outgoing calls requests.
    data: Optional["LSPAny"]

    def __init__(self, *, name: str, kind: "SymbolKind", tags: Optional[List["SymbolTag"]] = None, detail: Optional[str] = None, uri: str, range: "Range", selectionRange: "Range", data: Optional["LSPAny"] = None) -> None:
        """
        - name: The name of this item.
        - kind: The kind of this item.
        - tags: Tags for this item.
        - detail: More detail for this item, e.g. the signature of a function.
        - uri: The resource identifier of this item.
        - range: The range enclosing this symbol not including leading/trailing whitespace but everything else, e.g. comments and code.
        - selectionRange: The range that should be selected and revealed when this symbol is being picked, e.g. the name of a function.
            Must be contained by the [`range`](#CallHierarchyItem.range).
        - data: A data entry field that is preserved between a call hierarchy prepare and
            incoming calls or outgoing calls requests.
        """
        self.name = name
        self.kind = kind
        self.tags = tags
        self.detail = detail
        self.uri = uri
        self.range = range
        self.selectionRange = selectionRange
        self.data = data

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "CallHierarchyItem":
        name = json_get_string(obj, "name")
        kind = SymbolKind(json_get_int(obj, "kind"))
        if tags_json := json_get_optional_array(obj, "tags"):
            tags = [SymbolTag(json_assert_type_int(i)) for i in tags_json]
        else:
            tags = None
        if detail_json := json_get_optional_string(obj, "detail"):
            detail = detail_json
        else:
            detail = None
        uri = json_get_string(obj, "uri")
        range = Range.from_json(json_get_object(obj, "range"))
        selectionRange = Range.from_json(json_get_object(obj, "selectionRange"))
        if data_json := obj.get("data"):
            data = parse_LSPAny(data_json)
        else:
            data = None
        return cls(name=name, kind=kind, tags=tags, detail=detail, uri=uri, range=range, selectionRange=selectionRange, data=data)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["name"] = self.name
        out["kind"] = self.kind.value
        if self.tags is not None:
            out["tags"] = [i.value for i in self.tags]
        if self.detail is not None:
            out["detail"] = self.detail
        out["uri"] = self.uri
        out["range"] = self.range.to_json()
        out["selectionRange"] = self.selectionRange.to_json()
        if self.data is not None:
            out["data"] = write_LSPAny(self.data)
        return out


@dataclass
class CallHierarchyOptions():
    """
    Call hierarchy options used during static registration.
    
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    workDoneProgress: Optional[bool]

    def __init__(self, *, workDoneProgress: Optional[bool] = None) -> None:
        """
    
        """
        self.workDoneProgress = workDoneProgress

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "CallHierarchyOptions":
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        return cls(workDoneProgress=workDoneProgress)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        return out


@dataclass
class CallHierarchyRegistrationOptions(TextDocumentRegistrationOptions, CallHierarchyOptions):
    """
    Call hierarchy options used during static or dynamic registration.
    
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # A document selector to identify the scope of the registration. If set to null
    # the document selector provided on the client side will be used.
    documentSelector: Union["DocumentSelector", None]
    
    workDoneProgress: Optional[bool]
    
    # The id used to register the request. The id can be used to deregister
    # the request again. See also Registration#id.
    id: Optional[str]

    def __init__(self, *, documentSelector: Union["DocumentSelector", None], workDoneProgress: Optional[bool] = None, id: Optional[str] = None) -> None:
        """
        - documentSelector: A document selector to identify the scope of the registration. If set to null
            the document selector provided on the client side will be used.
        - id: The id used to register the request. The id can be used to deregister
            the request again. See also Registration#id.
        """
        self.documentSelector = documentSelector
        self.workDoneProgress = workDoneProgress
        self.id = id

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "CallHierarchyRegistrationOptions":
        documentSelector = parse_or_type(obj["documentSelector"], (lambda v: parse_DocumentSelector(json_assert_type_array(v)), lambda v: json_assert_type_null(v)))
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        if id_json := json_get_optional_string(obj, "id"):
            id = id_json
        else:
            id = None
        return cls(documentSelector=documentSelector, workDoneProgress=workDoneProgress, id=id)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["documentSelector"] = write_or_type(self.documentSelector, (lambda i: isinstance(i, List) and (len(i) == 0 or (((isinstance(i[0], Dict) and "language" in i[0].keys()) or (isinstance(i[0], Dict) and "scheme" in i[0].keys()) or (isinstance(i[0], Dict) and "pattern" in i[0].keys())) or (isinstance(i[0], NotebookCellTextDocumentFilter)))), lambda i: i is None), (lambda i: write_DocumentSelector(i), lambda i: i))
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        if self.id is not None:
            out["id"] = self.id
        return out


@dataclass
class CallHierarchyIncomingCallsParams():
    """
    The parameter of a `callHierarchy/incomingCalls` request.
    
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]
    
    # An optional token that a server can use to report partial results (e.g. streaming) to
    # the client.
    partialResultToken: Optional["ProgressToken"]
    
    item: "CallHierarchyItem"

    def __init__(self, *, workDoneToken: Optional["ProgressToken"] = None, partialResultToken: Optional["ProgressToken"] = None, item: "CallHierarchyItem") -> None:
        """
        - workDoneToken: An optional token that a server can use to report work done progress.
        - partialResultToken: An optional token that a server can use to report partial results (e.g. streaming) to
            the client.
        """
        self.workDoneToken = workDoneToken
        self.partialResultToken = partialResultToken
        self.item = item

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "CallHierarchyIncomingCallsParams":
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        if partialResultToken_json := obj.get("partialResultToken"):
            partialResultToken = parse_ProgressToken(partialResultToken_json)
        else:
            partialResultToken = None
        item = CallHierarchyItem.from_json(json_get_object(obj, "item"))
        return cls(workDoneToken=workDoneToken, partialResultToken=partialResultToken, item=item)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        if self.partialResultToken is not None:
            out["partialResultToken"] = write_ProgressToken(self.partialResultToken)
        out["item"] = self.item.to_json()
        return out


@dataclass
class CallHierarchyIncomingCall():
    """
    Represents an incoming call, e.g. a caller of a method or constructor.
    
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # The item that makes the call.
    from_: "CallHierarchyItem"
    
    # The ranges at which the calls appear. This is relative to the caller
    # denoted by [`this.from`](#CallHierarchyIncomingCall.from).
    fromRanges: List["Range"]

    def __init__(self, *, from_: "CallHierarchyItem", fromRanges: List["Range"]) -> None:
        """
        - from: The item that makes the call.
        - fromRanges: The ranges at which the calls appear. This is relative to the caller
            denoted by [`this.from`](#CallHierarchyIncomingCall.from).
        """
        self.from_ = from_
        self.fromRanges = fromRanges

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "CallHierarchyIncomingCall":
        from_ = CallHierarchyItem.from_json(json_get_object(obj, "from"))
        fromRanges = [Range.from_json(json_assert_type_object(i)) for i in json_get_array(obj, "fromRanges")]
        return cls(from_=from_, fromRanges=fromRanges)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["from"] = self.from_.to_json()
        out["fromRanges"] = [i.to_json() for i in self.fromRanges]
        return out


@dataclass
class CallHierarchyOutgoingCallsParams():
    """
    The parameter of a `callHierarchy/outgoingCalls` request.
    
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]
    
    # An optional token that a server can use to report partial results (e.g. streaming) to
    # the client.
    partialResultToken: Optional["ProgressToken"]
    
    item: "CallHierarchyItem"

    def __init__(self, *, workDoneToken: Optional["ProgressToken"] = None, partialResultToken: Optional["ProgressToken"] = None, item: "CallHierarchyItem") -> None:
        """
        - workDoneToken: An optional token that a server can use to report work done progress.
        - partialResultToken: An optional token that a server can use to report partial results (e.g. streaming) to
            the client.
        """
        self.workDoneToken = workDoneToken
        self.partialResultToken = partialResultToken
        self.item = item

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "CallHierarchyOutgoingCallsParams":
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        if partialResultToken_json := obj.get("partialResultToken"):
            partialResultToken = parse_ProgressToken(partialResultToken_json)
        else:
            partialResultToken = None
        item = CallHierarchyItem.from_json(json_get_object(obj, "item"))
        return cls(workDoneToken=workDoneToken, partialResultToken=partialResultToken, item=item)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        if self.partialResultToken is not None:
            out["partialResultToken"] = write_ProgressToken(self.partialResultToken)
        out["item"] = self.item.to_json()
        return out


@dataclass
class CallHierarchyOutgoingCall():
    """
    Represents an outgoing call, e.g. calling a getter from a method or a method from a constructor etc.
    
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # The item that is called.
    to: "CallHierarchyItem"
    
    # The range at which this item is called. This is the range relative to the caller, e.g the item
    # passed to [`provideCallHierarchyOutgoingCalls`](#CallHierarchyItemProvider.provideCallHierarchyOutgoingCalls)
    # and not [`this.to`](#CallHierarchyOutgoingCall.to).
    fromRanges: List["Range"]

    def __init__(self, *, to: "CallHierarchyItem", fromRanges: List["Range"]) -> None:
        """
        - to: The item that is called.
        - fromRanges: The range at which this item is called. This is the range relative to the caller, e.g the item
            passed to [`provideCallHierarchyOutgoingCalls`](#CallHierarchyItemProvider.provideCallHierarchyOutgoingCalls)
            and not [`this.to`](#CallHierarchyOutgoingCall.to).
        """
        self.to = to
        self.fromRanges = fromRanges

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "CallHierarchyOutgoingCall":
        to = CallHierarchyItem.from_json(json_get_object(obj, "to"))
        fromRanges = [Range.from_json(json_assert_type_object(i)) for i in json_get_array(obj, "fromRanges")]
        return cls(to=to, fromRanges=fromRanges)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["to"] = self.to.to_json()
        out["fromRanges"] = [i.to_json() for i in self.fromRanges]
        return out


@dataclass
class SemanticTokensParams():
    """
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]
    
    # An optional token that a server can use to report partial results (e.g. streaming) to
    # the client.
    partialResultToken: Optional["ProgressToken"]
    
    # The text document.
    textDocument: "TextDocumentIdentifier"

    def __init__(self, *, workDoneToken: Optional["ProgressToken"] = None, partialResultToken: Optional["ProgressToken"] = None, textDocument: "TextDocumentIdentifier") -> None:
        """
        - workDoneToken: An optional token that a server can use to report work done progress.
        - partialResultToken: An optional token that a server can use to report partial results (e.g. streaming) to
            the client.
        - textDocument: The text document.
        """
        self.workDoneToken = workDoneToken
        self.partialResultToken = partialResultToken
        self.textDocument = textDocument

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "SemanticTokensParams":
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        if partialResultToken_json := obj.get("partialResultToken"):
            partialResultToken = parse_ProgressToken(partialResultToken_json)
        else:
            partialResultToken = None
        textDocument = TextDocumentIdentifier.from_json(json_get_object(obj, "textDocument"))
        return cls(workDoneToken=workDoneToken, partialResultToken=partialResultToken, textDocument=textDocument)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        if self.partialResultToken is not None:
            out["partialResultToken"] = write_ProgressToken(self.partialResultToken)
        out["textDocument"] = self.textDocument.to_json()
        return out


@dataclass
class SemanticTokens():
    """
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # An optional result id. If provided and clients support delta updating
    # the client will include the result id in the next semantic token request.
    # A server can then instead of computing all semantic tokens again simply
    # send a delta.
    resultId: Optional[str]
    
    # The actual tokens.
    data: List[int]

    def __init__(self, *, resultId: Optional[str] = None, data: List[int]) -> None:
        """
        - resultId: An optional result id. If provided and clients support delta updating
            the client will include the result id in the next semantic token request.
            A server can then instead of computing all semantic tokens again simply
            send a delta.
        - data: The actual tokens.
        """
        self.resultId = resultId
        self.data = data

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "SemanticTokens":
        if resultId_json := json_get_optional_string(obj, "resultId"):
            resultId = resultId_json
        else:
            resultId = None
        data = [json_assert_type_int(i) for i in json_get_array(obj, "data")]
        return cls(resultId=resultId, data=data)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.resultId is not None:
            out["resultId"] = self.resultId
        out["data"] = [i for i in self.data]
        return out


@dataclass
class SemanticTokensPartialResult():
    """
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    data: List[int]

    def __init__(self, *, data: List[int]) -> None:
        """
    
        """
        self.data = data

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "SemanticTokensPartialResult":
        data = [json_assert_type_int(i) for i in json_get_array(obj, "data")]
        return cls(data=data)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["data"] = [i for i in self.data]
        return out


@dataclass
class SemanticTokensLegend():
    """
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # The token types a server uses.
    tokenTypes: List[str]
    
    # The token modifiers a server uses.
    tokenModifiers: List[str]

    def __init__(self, *, tokenTypes: List[str], tokenModifiers: List[str]) -> None:
        """
        - tokenTypes: The token types a server uses.
        - tokenModifiers: The token modifiers a server uses.
        """
        self.tokenTypes = tokenTypes
        self.tokenModifiers = tokenModifiers

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "SemanticTokensLegend":
        tokenTypes = [json_assert_type_string(i) for i in json_get_array(obj, "tokenTypes")]
        tokenModifiers = [json_assert_type_string(i) for i in json_get_array(obj, "tokenModifiers")]
        return cls(tokenTypes=tokenTypes, tokenModifiers=tokenModifiers)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["tokenTypes"] = [i for i in self.tokenTypes]
        out["tokenModifiers"] = [i for i in self.tokenModifiers]
        return out


AnonymousStructure5Keys = Literal[None]

def parse_AnonymousStructure5(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure5Keys, Any]:
    out: Dict[AnonymousStructure5Keys, Any] = {}

    return out

def write_AnonymousStructure5(obj: Dict[AnonymousStructure5Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}

    return out


AnonymousStructure6Keys = Literal["delta"]

def parse_AnonymousStructure6(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure6Keys, Any]:
    out: Dict[AnonymousStructure6Keys, Any] = {}
    if delta_json := json_get_optional_bool(obj, "delta"):
        out["delta"] = delta_json
    else:
        out["delta"] = None
    return out

def write_AnonymousStructure6(obj: Dict[AnonymousStructure6Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    if obj.get("delta") is not None:
        out["delta"] = obj.get("delta")
    return out


@dataclass
class SemanticTokensOptions():
    """
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    workDoneProgress: Optional[bool]
    
    # The legend used by the server
    legend: "SemanticTokensLegend"
    
    # Server supports providing semantic tokens for a specific range
    # of a document.
    range: Optional[Union[bool, Dict[AnonymousStructure5Keys, Any]]]
    
    # Server supports providing semantic tokens for a full document.
    full: Optional[Union[bool, Dict[AnonymousStructure6Keys, Any]]]

    def __init__(self, *, workDoneProgress: Optional[bool] = None, legend: "SemanticTokensLegend", range: Optional[Union[bool, Dict[AnonymousStructure5Keys, Any]]] = None, full: Optional[Union[bool, Dict[AnonymousStructure6Keys, Any]]] = None) -> None:
        """
        - legend: The legend used by the server
        - range: Server supports providing semantic tokens for a specific range
            of a document.
        - full: Server supports providing semantic tokens for a full document.
        """
        self.workDoneProgress = workDoneProgress
        self.legend = legend
        self.range = range
        self.full = full

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "SemanticTokensOptions":
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        legend = SemanticTokensLegend.from_json(json_get_object(obj, "legend"))
        if range_json := obj.get("range"):
            range = parse_or_type(range_json, (lambda v: json_assert_type_bool(v), lambda v: parse_AnonymousStructure5(json_assert_type_object(v))))
        else:
            range = None
        if full_json := obj.get("full"):
            full = parse_or_type(full_json, (lambda v: json_assert_type_bool(v), lambda v: parse_AnonymousStructure6(json_assert_type_object(v))))
        else:
            full = None
        return cls(workDoneProgress=workDoneProgress, legend=legend, range=range, full=full)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        out["legend"] = self.legend.to_json()
        if self.range is not None:
            out["range"] = write_or_type(self.range, (lambda i: isinstance(i, bool), lambda i: isinstance(i, Dict)), (lambda i: i, lambda i: write_AnonymousStructure5(i)))
        if self.full is not None:
            out["full"] = write_or_type(self.full, (lambda i: isinstance(i, bool), lambda i: isinstance(i, Dict)), (lambda i: i, lambda i: write_AnonymousStructure6(i)))
        return out


@dataclass
class SemanticTokensRegistrationOptions(TextDocumentRegistrationOptions, SemanticTokensOptions):
    """
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # A document selector to identify the scope of the registration. If set to null
    # the document selector provided on the client side will be used.
    documentSelector: Union["DocumentSelector", None]
    
    workDoneProgress: Optional[bool]
    
    # The legend used by the server
    legend: "SemanticTokensLegend"
    
    # Server supports providing semantic tokens for a specific range
    # of a document.
    range: Optional[Union[bool, Dict[AnonymousStructure5Keys, Any]]]
    
    # Server supports providing semantic tokens for a full document.
    full: Optional[Union[bool, Dict[AnonymousStructure6Keys, Any]]]
    
    # The id used to register the request. The id can be used to deregister
    # the request again. See also Registration#id.
    id: Optional[str]

    def __init__(self, *, documentSelector: Union["DocumentSelector", None], workDoneProgress: Optional[bool] = None, legend: "SemanticTokensLegend", range: Optional[Union[bool, Dict[AnonymousStructure5Keys, Any]]] = None, full: Optional[Union[bool, Dict[AnonymousStructure6Keys, Any]]] = None, id: Optional[str] = None) -> None:
        """
        - documentSelector: A document selector to identify the scope of the registration. If set to null
            the document selector provided on the client side will be used.
        - legend: The legend used by the server
        - range: Server supports providing semantic tokens for a specific range
            of a document.
        - full: Server supports providing semantic tokens for a full document.
        - id: The id used to register the request. The id can be used to deregister
            the request again. See also Registration#id.
        """
        self.documentSelector = documentSelector
        self.workDoneProgress = workDoneProgress
        self.legend = legend
        self.range = range
        self.full = full
        self.id = id

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "SemanticTokensRegistrationOptions":
        documentSelector = parse_or_type(obj["documentSelector"], (lambda v: parse_DocumentSelector(json_assert_type_array(v)), lambda v: json_assert_type_null(v)))
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        legend = SemanticTokensLegend.from_json(json_get_object(obj, "legend"))
        if range_json := obj.get("range"):
            range = parse_or_type(range_json, (lambda v: json_assert_type_bool(v), lambda v: parse_AnonymousStructure5(json_assert_type_object(v))))
        else:
            range = None
        if full_json := obj.get("full"):
            full = parse_or_type(full_json, (lambda v: json_assert_type_bool(v), lambda v: parse_AnonymousStructure6(json_assert_type_object(v))))
        else:
            full = None
        if id_json := json_get_optional_string(obj, "id"):
            id = id_json
        else:
            id = None
        return cls(documentSelector=documentSelector, workDoneProgress=workDoneProgress, legend=legend, range=range, full=full, id=id)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["documentSelector"] = write_or_type(self.documentSelector, (lambda i: isinstance(i, List) and (len(i) == 0 or (((isinstance(i[0], Dict) and "language" in i[0].keys()) or (isinstance(i[0], Dict) and "scheme" in i[0].keys()) or (isinstance(i[0], Dict) and "pattern" in i[0].keys())) or (isinstance(i[0], NotebookCellTextDocumentFilter)))), lambda i: i is None), (lambda i: write_DocumentSelector(i), lambda i: i))
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        out["legend"] = self.legend.to_json()
        if self.range is not None:
            out["range"] = write_or_type(self.range, (lambda i: isinstance(i, bool), lambda i: isinstance(i, Dict)), (lambda i: i, lambda i: write_AnonymousStructure5(i)))
        if self.full is not None:
            out["full"] = write_or_type(self.full, (lambda i: isinstance(i, bool), lambda i: isinstance(i, Dict)), (lambda i: i, lambda i: write_AnonymousStructure6(i)))
        if self.id is not None:
            out["id"] = self.id
        return out


@dataclass
class SemanticTokensDeltaParams():
    """
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]
    
    # An optional token that a server can use to report partial results (e.g. streaming) to
    # the client.
    partialResultToken: Optional["ProgressToken"]
    
    # The text document.
    textDocument: "TextDocumentIdentifier"
    
    # The result id of a previous response. The result Id can either point to a full response
    # or a delta response depending on what was received last.
    previousResultId: str

    def __init__(self, *, workDoneToken: Optional["ProgressToken"] = None, partialResultToken: Optional["ProgressToken"] = None, textDocument: "TextDocumentIdentifier", previousResultId: str) -> None:
        """
        - workDoneToken: An optional token that a server can use to report work done progress.
        - partialResultToken: An optional token that a server can use to report partial results (e.g. streaming) to
            the client.
        - textDocument: The text document.
        - previousResultId: The result id of a previous response. The result Id can either point to a full response
            or a delta response depending on what was received last.
        """
        self.workDoneToken = workDoneToken
        self.partialResultToken = partialResultToken
        self.textDocument = textDocument
        self.previousResultId = previousResultId

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "SemanticTokensDeltaParams":
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        if partialResultToken_json := obj.get("partialResultToken"):
            partialResultToken = parse_ProgressToken(partialResultToken_json)
        else:
            partialResultToken = None
        textDocument = TextDocumentIdentifier.from_json(json_get_object(obj, "textDocument"))
        previousResultId = json_get_string(obj, "previousResultId")
        return cls(workDoneToken=workDoneToken, partialResultToken=partialResultToken, textDocument=textDocument, previousResultId=previousResultId)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        if self.partialResultToken is not None:
            out["partialResultToken"] = write_ProgressToken(self.partialResultToken)
        out["textDocument"] = self.textDocument.to_json()
        out["previousResultId"] = self.previousResultId
        return out


@dataclass
class SemanticTokensEdit():
    """
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # The start offset of the edit.
    start: int
    
    # The count of elements to remove.
    deleteCount: int
    
    # The elements to insert.
    data: Optional[List[int]]

    def __init__(self, *, start: int, deleteCount: int, data: Optional[List[int]] = None) -> None:
        """
        - start: The start offset of the edit.
        - deleteCount: The count of elements to remove.
        - data: The elements to insert.
        """
        self.start = start
        self.deleteCount = deleteCount
        self.data = data

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "SemanticTokensEdit":
        start = json_get_int(obj, "start")
        deleteCount = json_get_int(obj, "deleteCount")
        if data_json := json_get_optional_array(obj, "data"):
            data = [json_assert_type_int(i) for i in data_json]
        else:
            data = None
        return cls(start=start, deleteCount=deleteCount, data=data)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["start"] = self.start
        out["deleteCount"] = self.deleteCount
        if self.data is not None:
            out["data"] = [i for i in self.data]
        return out


@dataclass
class SemanticTokensDelta():
    """
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    resultId: Optional[str]
    
    # The semantic token edits to transform a previous result into a new result.
    edits: List["SemanticTokensEdit"]

    def __init__(self, *, resultId: Optional[str] = None, edits: List["SemanticTokensEdit"]) -> None:
        """
        - edits: The semantic token edits to transform a previous result into a new result.
        """
        self.resultId = resultId
        self.edits = edits

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "SemanticTokensDelta":
        if resultId_json := json_get_optional_string(obj, "resultId"):
            resultId = resultId_json
        else:
            resultId = None
        edits = [SemanticTokensEdit.from_json(json_assert_type_object(i)) for i in json_get_array(obj, "edits")]
        return cls(resultId=resultId, edits=edits)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.resultId is not None:
            out["resultId"] = self.resultId
        out["edits"] = [i.to_json() for i in self.edits]
        return out


@dataclass
class SemanticTokensDeltaPartialResult():
    """
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    edits: List["SemanticTokensEdit"]

    def __init__(self, *, edits: List["SemanticTokensEdit"]) -> None:
        """
    
        """
        self.edits = edits

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "SemanticTokensDeltaPartialResult":
        edits = [SemanticTokensEdit.from_json(json_assert_type_object(i)) for i in json_get_array(obj, "edits")]
        return cls(edits=edits)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["edits"] = [i.to_json() for i in self.edits]
        return out


@dataclass
class SemanticTokensRangeParams():
    """
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]
    
    # An optional token that a server can use to report partial results (e.g. streaming) to
    # the client.
    partialResultToken: Optional["ProgressToken"]
    
    # The text document.
    textDocument: "TextDocumentIdentifier"
    
    # The range the semantic tokens are requested for.
    range: "Range"

    def __init__(self, *, workDoneToken: Optional["ProgressToken"] = None, partialResultToken: Optional["ProgressToken"] = None, textDocument: "TextDocumentIdentifier", range: "Range") -> None:
        """
        - workDoneToken: An optional token that a server can use to report work done progress.
        - partialResultToken: An optional token that a server can use to report partial results (e.g. streaming) to
            the client.
        - textDocument: The text document.
        - range: The range the semantic tokens are requested for.
        """
        self.workDoneToken = workDoneToken
        self.partialResultToken = partialResultToken
        self.textDocument = textDocument
        self.range = range

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "SemanticTokensRangeParams":
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        if partialResultToken_json := obj.get("partialResultToken"):
            partialResultToken = parse_ProgressToken(partialResultToken_json)
        else:
            partialResultToken = None
        textDocument = TextDocumentIdentifier.from_json(json_get_object(obj, "textDocument"))
        range = Range.from_json(json_get_object(obj, "range"))
        return cls(workDoneToken=workDoneToken, partialResultToken=partialResultToken, textDocument=textDocument, range=range)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        if self.partialResultToken is not None:
            out["partialResultToken"] = write_ProgressToken(self.partialResultToken)
        out["textDocument"] = self.textDocument.to_json()
        out["range"] = self.range.to_json()
        return out


@dataclass
class ShowDocumentParams():
    """
    Params to show a document.
    
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # The document uri to show.
    uri: str
    
    # Indicates to show the resource in an external program.
    # To show for example `https://code.visualstudio.com/`
    # in the default WEB browser set `external` to `true`.
    external: Optional[bool]
    
    # An optional property to indicate whether the editor
    # showing the document should take focus or not.
    # Clients might ignore this property if an external
    # program is started.
    takeFocus: Optional[bool]
    
    # An optional selection range if the document is a text
    # document. Clients might ignore the property if an
    # external program is started or the file is not a text
    # file.
    selection: Optional["Range"]

    def __init__(self, *, uri: str, external: Optional[bool] = None, takeFocus: Optional[bool] = None, selection: Optional["Range"] = None) -> None:
        """
        - uri: The document uri to show.
        - external: Indicates to show the resource in an external program.
            To show for example `https://code.visualstudio.com/`
            in the default WEB browser set `external` to `true`.
        - takeFocus: An optional property to indicate whether the editor
            showing the document should take focus or not.
            Clients might ignore this property if an external
            program is started.
        - selection: An optional selection range if the document is a text
            document. Clients might ignore the property if an
            external program is started or the file is not a text
            file.
        """
        self.uri = uri
        self.external = external
        self.takeFocus = takeFocus
        self.selection = selection

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "ShowDocumentParams":
        uri = json_get_string(obj, "uri")
        if external_json := json_get_optional_bool(obj, "external"):
            external = external_json
        else:
            external = None
        if takeFocus_json := json_get_optional_bool(obj, "takeFocus"):
            takeFocus = takeFocus_json
        else:
            takeFocus = None
        if selection_json := json_get_optional_object(obj, "selection"):
            selection = Range.from_json(selection_json)
        else:
            selection = None
        return cls(uri=uri, external=external, takeFocus=takeFocus, selection=selection)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["uri"] = self.uri
        if self.external is not None:
            out["external"] = self.external
        if self.takeFocus is not None:
            out["takeFocus"] = self.takeFocus
        if self.selection is not None:
            out["selection"] = self.selection.to_json()
        return out


@dataclass
class ShowDocumentResult():
    """
    The result of a showDocument request.
    
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # A boolean indicating if the show was successful.
    success: bool

    def __init__(self, *, success: bool) -> None:
        """
        - success: A boolean indicating if the show was successful.
        """
        self.success = success

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "ShowDocumentResult":
        success = json_get_bool(obj, "success")
        return cls(success=success)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["success"] = self.success
        return out


@dataclass
class LinkedEditingRangeParams(TextDocumentPositionParams):
    """


    *Generated from the TypeScript documentation*
    """

    # The text document.
    textDocument: "TextDocumentIdentifier"
    
    # The position inside the text document.
    position: "Position"
    
    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]

    def __init__(self, *, textDocument: "TextDocumentIdentifier", position: "Position", workDoneToken: Optional["ProgressToken"] = None) -> None:
        """
        - textDocument: The text document.
        - position: The position inside the text document.
        - workDoneToken: An optional token that a server can use to report work done progress.
        """
        self.textDocument = textDocument
        self.position = position
        self.workDoneToken = workDoneToken

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "LinkedEditingRangeParams":
        textDocument = TextDocumentIdentifier.from_json(json_get_object(obj, "textDocument"))
        position = Position.from_json(json_get_object(obj, "position"))
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        return cls(textDocument=textDocument, position=position, workDoneToken=workDoneToken)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["textDocument"] = self.textDocument.to_json()
        out["position"] = self.position.to_json()
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        return out


@dataclass
class LinkedEditingRanges():
    """
    The result of a linked editing range request.
    
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # A list of ranges that can be edited together. The ranges must have
    # identical length and contain identical text content. The ranges cannot overlap.
    ranges: List["Range"]
    
    # An optional word pattern (regular expression) that describes valid contents for
    # the given ranges. If no pattern is provided, the client configuration's word
    # pattern will be used.
    wordPattern: Optional[str]

    def __init__(self, *, ranges: List["Range"], wordPattern: Optional[str] = None) -> None:
        """
        - ranges: A list of ranges that can be edited together. The ranges must have
            identical length and contain identical text content. The ranges cannot overlap.
        - wordPattern: An optional word pattern (regular expression) that describes valid contents for
            the given ranges. If no pattern is provided, the client configuration's word
            pattern will be used.
        """
        self.ranges = ranges
        self.wordPattern = wordPattern

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "LinkedEditingRanges":
        ranges = [Range.from_json(json_assert_type_object(i)) for i in json_get_array(obj, "ranges")]
        if wordPattern_json := json_get_optional_string(obj, "wordPattern"):
            wordPattern = wordPattern_json
        else:
            wordPattern = None
        return cls(ranges=ranges, wordPattern=wordPattern)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["ranges"] = [i.to_json() for i in self.ranges]
        if self.wordPattern is not None:
            out["wordPattern"] = self.wordPattern
        return out


@dataclass
class LinkedEditingRangeOptions():
    """


    *Generated from the TypeScript documentation*
    """

    workDoneProgress: Optional[bool]

    def __init__(self, *, workDoneProgress: Optional[bool] = None) -> None:
        """
    
        """
        self.workDoneProgress = workDoneProgress

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "LinkedEditingRangeOptions":
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        return cls(workDoneProgress=workDoneProgress)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        return out


@dataclass
class LinkedEditingRangeRegistrationOptions(TextDocumentRegistrationOptions, LinkedEditingRangeOptions):
    """


    *Generated from the TypeScript documentation*
    """

    # A document selector to identify the scope of the registration. If set to null
    # the document selector provided on the client side will be used.
    documentSelector: Union["DocumentSelector", None]
    
    workDoneProgress: Optional[bool]
    
    # The id used to register the request. The id can be used to deregister
    # the request again. See also Registration#id.
    id: Optional[str]

    def __init__(self, *, documentSelector: Union["DocumentSelector", None], workDoneProgress: Optional[bool] = None, id: Optional[str] = None) -> None:
        """
        - documentSelector: A document selector to identify the scope of the registration. If set to null
            the document selector provided on the client side will be used.
        - id: The id used to register the request. The id can be used to deregister
            the request again. See also Registration#id.
        """
        self.documentSelector = documentSelector
        self.workDoneProgress = workDoneProgress
        self.id = id

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "LinkedEditingRangeRegistrationOptions":
        documentSelector = parse_or_type(obj["documentSelector"], (lambda v: parse_DocumentSelector(json_assert_type_array(v)), lambda v: json_assert_type_null(v)))
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        if id_json := json_get_optional_string(obj, "id"):
            id = id_json
        else:
            id = None
        return cls(documentSelector=documentSelector, workDoneProgress=workDoneProgress, id=id)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["documentSelector"] = write_or_type(self.documentSelector, (lambda i: isinstance(i, List) and (len(i) == 0 or (((isinstance(i[0], Dict) and "language" in i[0].keys()) or (isinstance(i[0], Dict) and "scheme" in i[0].keys()) or (isinstance(i[0], Dict) and "pattern" in i[0].keys())) or (isinstance(i[0], NotebookCellTextDocumentFilter)))), lambda i: i is None), (lambda i: write_DocumentSelector(i), lambda i: i))
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        if self.id is not None:
            out["id"] = self.id
        return out


@dataclass
class FileCreate():
    """
    Represents information on a file/folder create.
    
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # A file:// URI for the location of the file/folder being created.
    uri: str

    def __init__(self, *, uri: str) -> None:
        """
        - uri: A file:// URI for the location of the file/folder being created.
        """
        self.uri = uri

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "FileCreate":
        uri = json_get_string(obj, "uri")
        return cls(uri=uri)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["uri"] = self.uri
        return out


@dataclass
class CreateFilesParams():
    """
    The parameters sent in notifications/requests for user-initiated creation of
    files.
    
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # An array of all files/folders created in this operation.
    files: List["FileCreate"]

    def __init__(self, *, files: List["FileCreate"]) -> None:
        """
        - files: An array of all files/folders created in this operation.
        """
        self.files = files

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "CreateFilesParams":
        files = [FileCreate.from_json(json_assert_type_object(i)) for i in json_get_array(obj, "files")]
        return cls(files=files)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["files"] = [i.to_json() for i in self.files]
        return out


@dataclass
class OptionalVersionedTextDocumentIdentifier(TextDocumentIdentifier):
    """
    A text document identifier to optionally denote a specific version of a text document.

    *Generated from the TypeScript documentation*
    """

    # The text document's uri.
    uri: str
    
    # The version number of this document. If a versioned text document identifier
    # is sent from the server to the client and the file is not open in the editor
    # (the server has not received an open notification before) the server can send
    # `null` to indicate that the version is unknown and the content on disk is the
    # truth (as specified with document content ownership).
    version: Union[int, None]

    def __init__(self, *, uri: str, version: Union[int, None]) -> None:
        """
        - uri: The text document's uri.
        - version: The version number of this document. If a versioned text document identifier
            is sent from the server to the client and the file is not open in the editor
            (the server has not received an open notification before) the server can send
            `null` to indicate that the version is unknown and the content on disk is the
            truth (as specified with document content ownership).
        """
        self.uri = uri
        self.version = version

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "OptionalVersionedTextDocumentIdentifier":
        uri = json_get_string(obj, "uri")
        version = parse_or_type(obj["version"], (lambda v: json_assert_type_int(v), lambda v: json_assert_type_null(v)))
        return cls(uri=uri, version=version)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["uri"] = self.uri
        out["version"] = write_or_type(self.version, (lambda i: isinstance(i, int), lambda i: i is None), (lambda i: i, lambda i: i))
        return out


# An identifier to refer to a change annotation stored with a workspace edit.
ChangeAnnotationIdentifier = str

def parse_ChangeAnnotationIdentifier(arg: JSON_VALUE) -> ChangeAnnotationIdentifier:
    return json_assert_type_string(arg)

def write_ChangeAnnotationIdentifier(arg: ChangeAnnotationIdentifier) -> JSON_VALUE:
    return arg


@dataclass
class AnnotatedTextEdit(TextEdit):
    """
    A special text edit with an additional change annotation.
    
    @since 3.16.0.

    *Generated from the TypeScript documentation*
    """

    # The range of the text document to be manipulated. To insert
    # text into a document create a range where start === end.
    range: "Range"
    
    # The string to be inserted. For delete operations use an
    # empty string.
    newText: str
    
    # The actual identifier of the change annotation
    annotationId: "ChangeAnnotationIdentifier"

    def __init__(self, *, range: "Range", newText: str, annotationId: "ChangeAnnotationIdentifier") -> None:
        """
        - range: The range of the text document to be manipulated. To insert
            text into a document create a range where start === end.
        - newText: The string to be inserted. For delete operations use an
            empty string.
        - annotationId: The actual identifier of the change annotation
        """
        self.range = range
        self.newText = newText
        self.annotationId = annotationId

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "AnnotatedTextEdit":
        range = Range.from_json(json_get_object(obj, "range"))
        newText = json_get_string(obj, "newText")
        annotationId = parse_ChangeAnnotationIdentifier(json_get_string(obj, "annotationId"))
        return cls(range=range, newText=newText, annotationId=annotationId)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["range"] = self.range.to_json()
        out["newText"] = self.newText
        out["annotationId"] = write_ChangeAnnotationIdentifier(self.annotationId)
        return out


@dataclass
class TextDocumentEdit():
    """
    Describes textual changes on a text document. A TextDocumentEdit describes all changes
    on a document version Si and after they are applied move the document to version Si+1.
    So the creator of a TextDocumentEdit doesn't need to sort the array of edits or do any
    kind of ordering. However the edits must be non overlapping.

    *Generated from the TypeScript documentation*
    """

    # The text document to change.
    textDocument: "OptionalVersionedTextDocumentIdentifier"
    
    # The edits to be applied.
    # 
    # @since 3.16.0 - support for AnnotatedTextEdit. This is guarded using a
    # client capability.
    edits: List[Union["TextEdit", "AnnotatedTextEdit"]]

    def __init__(self, *, textDocument: "OptionalVersionedTextDocumentIdentifier", edits: List[Union["TextEdit", "AnnotatedTextEdit"]]) -> None:
        """
        - textDocument: The text document to change.
        - edits: The edits to be applied.
            
            @since 3.16.0 - support for AnnotatedTextEdit. This is guarded using a
            client capability.
        """
        self.textDocument = textDocument
        self.edits = edits

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "TextDocumentEdit":
        textDocument = OptionalVersionedTextDocumentIdentifier.from_json(json_get_object(obj, "textDocument"))
        edits = [parse_or_type((i), (lambda v: TextEdit.from_json(json_assert_type_object(v)), lambda v: AnnotatedTextEdit.from_json(json_assert_type_object(v)))) for i in json_get_array(obj, "edits")]
        return cls(textDocument=textDocument, edits=edits)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["textDocument"] = self.textDocument.to_json()
        out["edits"] = [write_or_type(i, (lambda i: isinstance(i, TextEdit), lambda i: isinstance(i, AnnotatedTextEdit)), (lambda i: i.to_json(), lambda i: i.to_json())) for i in self.edits]
        return out


@dataclass
class ResourceOperation():
    """
    A generic resource operation.

    *Generated from the TypeScript documentation*
    """

    # The resource operation kind.
    kind: str
    
    # An optional annotation identifier describing the operation.
    # 
    # @since 3.16.0
    annotationId: Optional["ChangeAnnotationIdentifier"]

    def __init__(self, *, kind: str, annotationId: Optional["ChangeAnnotationIdentifier"] = None) -> None:
        """
        - kind: The resource operation kind.
        - annotationId: An optional annotation identifier describing the operation.
            
            @since 3.16.0
        """
        self.kind = kind
        self.annotationId = annotationId

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "ResourceOperation":
        kind = json_get_string(obj, "kind")
        if annotationId_json := json_get_optional_string(obj, "annotationId"):
            annotationId = parse_ChangeAnnotationIdentifier(annotationId_json)
        else:
            annotationId = None
        return cls(kind=kind, annotationId=annotationId)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["kind"] = self.kind
        if self.annotationId is not None:
            out["annotationId"] = write_ChangeAnnotationIdentifier(self.annotationId)
        return out


@dataclass
class CreateFileOptions():
    """
    Options to create a file.

    *Generated from the TypeScript documentation*
    """

    # Overwrite existing file. Overwrite wins over `ignoreIfExists`
    overwrite: Optional[bool]
    
    # Ignore if exists.
    ignoreIfExists: Optional[bool]

    def __init__(self, *, overwrite: Optional[bool] = None, ignoreIfExists: Optional[bool] = None) -> None:
        """
        - overwrite: Overwrite existing file. Overwrite wins over `ignoreIfExists`
        - ignoreIfExists: Ignore if exists.
        """
        self.overwrite = overwrite
        self.ignoreIfExists = ignoreIfExists

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "CreateFileOptions":
        if overwrite_json := json_get_optional_bool(obj, "overwrite"):
            overwrite = overwrite_json
        else:
            overwrite = None
        if ignoreIfExists_json := json_get_optional_bool(obj, "ignoreIfExists"):
            ignoreIfExists = ignoreIfExists_json
        else:
            ignoreIfExists = None
        return cls(overwrite=overwrite, ignoreIfExists=ignoreIfExists)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.overwrite is not None:
            out["overwrite"] = self.overwrite
        if self.ignoreIfExists is not None:
            out["ignoreIfExists"] = self.ignoreIfExists
        return out


@dataclass
class CreateFile(ResourceOperation):
    """
    Create file operation.

    *Generated from the TypeScript documentation*
    """

    # A create
    kind: str
    
    # An optional annotation identifier describing the operation.
    # 
    # @since 3.16.0
    annotationId: Optional["ChangeAnnotationIdentifier"]
    
    # The resource to create.
    uri: str
    
    # Additional options
    options: Optional["CreateFileOptions"]

    def __init__(self, *, kind: str, annotationId: Optional["ChangeAnnotationIdentifier"] = None, uri: str, options: Optional["CreateFileOptions"] = None) -> None:
        """
        - kind: A create
        - annotationId: An optional annotation identifier describing the operation.
            
            @since 3.16.0
        - uri: The resource to create.
        - options: Additional options
        """
        self.kind = kind
        self.annotationId = annotationId
        self.uri = uri
        self.options = options

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "CreateFile":
        kind = match_string(json_get_string(obj, "kind"), "create")
        if annotationId_json := json_get_optional_string(obj, "annotationId"):
            annotationId = parse_ChangeAnnotationIdentifier(annotationId_json)
        else:
            annotationId = None
        uri = json_get_string(obj, "uri")
        if options_json := json_get_optional_object(obj, "options"):
            options = CreateFileOptions.from_json(options_json)
        else:
            options = None
        return cls(kind=kind, annotationId=annotationId, uri=uri, options=options)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["kind"] = "create"
        if self.annotationId is not None:
            out["annotationId"] = write_ChangeAnnotationIdentifier(self.annotationId)
        out["uri"] = self.uri
        if self.options is not None:
            out["options"] = self.options.to_json()
        return out


@dataclass
class RenameFileOptions():
    """
    Rename file options

    *Generated from the TypeScript documentation*
    """

    # Overwrite target if existing. Overwrite wins over `ignoreIfExists`
    overwrite: Optional[bool]
    
    # Ignores if target exists.
    ignoreIfExists: Optional[bool]

    def __init__(self, *, overwrite: Optional[bool] = None, ignoreIfExists: Optional[bool] = None) -> None:
        """
        - overwrite: Overwrite target if existing. Overwrite wins over `ignoreIfExists`
        - ignoreIfExists: Ignores if target exists.
        """
        self.overwrite = overwrite
        self.ignoreIfExists = ignoreIfExists

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "RenameFileOptions":
        if overwrite_json := json_get_optional_bool(obj, "overwrite"):
            overwrite = overwrite_json
        else:
            overwrite = None
        if ignoreIfExists_json := json_get_optional_bool(obj, "ignoreIfExists"):
            ignoreIfExists = ignoreIfExists_json
        else:
            ignoreIfExists = None
        return cls(overwrite=overwrite, ignoreIfExists=ignoreIfExists)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.overwrite is not None:
            out["overwrite"] = self.overwrite
        if self.ignoreIfExists is not None:
            out["ignoreIfExists"] = self.ignoreIfExists
        return out


@dataclass
class RenameFile(ResourceOperation):
    """
    Rename file operation

    *Generated from the TypeScript documentation*
    """

    # A rename
    kind: str
    
    # An optional annotation identifier describing the operation.
    # 
    # @since 3.16.0
    annotationId: Optional["ChangeAnnotationIdentifier"]
    
    # The old (existing) location.
    oldUri: str
    
    # The new location.
    newUri: str
    
    # Rename options.
    options: Optional["RenameFileOptions"]

    def __init__(self, *, kind: str, annotationId: Optional["ChangeAnnotationIdentifier"] = None, oldUri: str, newUri: str, options: Optional["RenameFileOptions"] = None) -> None:
        """
        - kind: A rename
        - annotationId: An optional annotation identifier describing the operation.
            
            @since 3.16.0
        - oldUri: The old (existing) location.
        - newUri: The new location.
        - options: Rename options.
        """
        self.kind = kind
        self.annotationId = annotationId
        self.oldUri = oldUri
        self.newUri = newUri
        self.options = options

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "RenameFile":
        kind = match_string(json_get_string(obj, "kind"), "rename")
        if annotationId_json := json_get_optional_string(obj, "annotationId"):
            annotationId = parse_ChangeAnnotationIdentifier(annotationId_json)
        else:
            annotationId = None
        oldUri = json_get_string(obj, "oldUri")
        newUri = json_get_string(obj, "newUri")
        if options_json := json_get_optional_object(obj, "options"):
            options = RenameFileOptions.from_json(options_json)
        else:
            options = None
        return cls(kind=kind, annotationId=annotationId, oldUri=oldUri, newUri=newUri, options=options)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["kind"] = "rename"
        if self.annotationId is not None:
            out["annotationId"] = write_ChangeAnnotationIdentifier(self.annotationId)
        out["oldUri"] = self.oldUri
        out["newUri"] = self.newUri
        if self.options is not None:
            out["options"] = self.options.to_json()
        return out


@dataclass
class DeleteFileOptions():
    """
    Delete file options

    *Generated from the TypeScript documentation*
    """

    # Delete the content recursively if a folder is denoted.
    recursive: Optional[bool]
    
    # Ignore the operation if the file doesn't exist.
    ignoreIfNotExists: Optional[bool]

    def __init__(self, *, recursive: Optional[bool] = None, ignoreIfNotExists: Optional[bool] = None) -> None:
        """
        - recursive: Delete the content recursively if a folder is denoted.
        - ignoreIfNotExists: Ignore the operation if the file doesn't exist.
        """
        self.recursive = recursive
        self.ignoreIfNotExists = ignoreIfNotExists

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DeleteFileOptions":
        if recursive_json := json_get_optional_bool(obj, "recursive"):
            recursive = recursive_json
        else:
            recursive = None
        if ignoreIfNotExists_json := json_get_optional_bool(obj, "ignoreIfNotExists"):
            ignoreIfNotExists = ignoreIfNotExists_json
        else:
            ignoreIfNotExists = None
        return cls(recursive=recursive, ignoreIfNotExists=ignoreIfNotExists)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.recursive is not None:
            out["recursive"] = self.recursive
        if self.ignoreIfNotExists is not None:
            out["ignoreIfNotExists"] = self.ignoreIfNotExists
        return out


@dataclass
class DeleteFile(ResourceOperation):
    """
    Delete file operation

    *Generated from the TypeScript documentation*
    """

    # A delete
    kind: str
    
    # An optional annotation identifier describing the operation.
    # 
    # @since 3.16.0
    annotationId: Optional["ChangeAnnotationIdentifier"]
    
    # The file to delete.
    uri: str
    
    # Delete options.
    options: Optional["DeleteFileOptions"]

    def __init__(self, *, kind: str, annotationId: Optional["ChangeAnnotationIdentifier"] = None, uri: str, options: Optional["DeleteFileOptions"] = None) -> None:
        """
        - kind: A delete
        - annotationId: An optional annotation identifier describing the operation.
            
            @since 3.16.0
        - uri: The file to delete.
        - options: Delete options.
        """
        self.kind = kind
        self.annotationId = annotationId
        self.uri = uri
        self.options = options

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DeleteFile":
        kind = match_string(json_get_string(obj, "kind"), "delete")
        if annotationId_json := json_get_optional_string(obj, "annotationId"):
            annotationId = parse_ChangeAnnotationIdentifier(annotationId_json)
        else:
            annotationId = None
        uri = json_get_string(obj, "uri")
        if options_json := json_get_optional_object(obj, "options"):
            options = DeleteFileOptions.from_json(options_json)
        else:
            options = None
        return cls(kind=kind, annotationId=annotationId, uri=uri, options=options)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["kind"] = "delete"
        if self.annotationId is not None:
            out["annotationId"] = write_ChangeAnnotationIdentifier(self.annotationId)
        out["uri"] = self.uri
        if self.options is not None:
            out["options"] = self.options.to_json()
        return out


@dataclass
class ChangeAnnotation():
    """
    Additional information that describes document changes.
    
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # A human-readable string describing the actual change. The string
    # is rendered prominent in the user interface.
    label: str
    
    # A flag which indicates that user confirmation is needed
    # before applying the change.
    needsConfirmation: Optional[bool]
    
    # A human-readable string which is rendered less prominent in
    # the user interface.
    description: Optional[str]

    def __init__(self, *, label: str, needsConfirmation: Optional[bool] = None, description: Optional[str] = None) -> None:
        """
        - label: A human-readable string describing the actual change. The string
            is rendered prominent in the user interface.
        - needsConfirmation: A flag which indicates that user confirmation is needed
            before applying the change.
        - description: A human-readable string which is rendered less prominent in
            the user interface.
        """
        self.label = label
        self.needsConfirmation = needsConfirmation
        self.description = description

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "ChangeAnnotation":
        label = json_get_string(obj, "label")
        if needsConfirmation_json := json_get_optional_bool(obj, "needsConfirmation"):
            needsConfirmation = needsConfirmation_json
        else:
            needsConfirmation = None
        if description_json := json_get_optional_string(obj, "description"):
            description = description_json
        else:
            description = None
        return cls(label=label, needsConfirmation=needsConfirmation, description=description)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["label"] = self.label
        if self.needsConfirmation is not None:
            out["needsConfirmation"] = self.needsConfirmation
        if self.description is not None:
            out["description"] = self.description
        return out


@dataclass
class WorkspaceEdit():
    """
    A workspace edit represents changes to many resources managed in the workspace. The edit
    should either provide `changes` or `documentChanges`. If documentChanges are present
    they are preferred over `changes` if the client can handle versioned document edits.
    
    Since version 3.13.0 a workspace edit can contain resource operations as well. If resource
    operations are present clients need to execute the operations in the order in which they
    are provided. So a workspace edit for example can consist of the following two changes:
    (1) a create file a.txt and (2) a text document edit which insert text into file a.txt.
    
    An invalid sequence (e.g. (1) delete file a.txt and (2) insert text into file a.txt) will
    cause failure of the operation. How the client recovers from the failure is described by
    the client capability: `workspace.workspaceEdit.failureHandling`

    *Generated from the TypeScript documentation*
    """

    # Holds changes to existing resources.
    changes: Optional[Dict[str, List["TextEdit"]]]
    
    # Depending on the client capability `workspace.workspaceEdit.resourceOperations` document changes
    # are either an array of `TextDocumentEdit`s to express changes to n different text documents
    # where each text document edit addresses a specific version of a text document. Or it can contain
    # above `TextDocumentEdit`s mixed with create, rename and delete file / folder operations.
    # 
    # Whether a client supports versioned document edits is expressed via
    # `workspace.workspaceEdit.documentChanges` client capability.
    # 
    # If a client neither supports `documentChanges` nor `workspace.workspaceEdit.resourceOperations` then
    # only plain `TextEdit`s using the `changes` property are supported.
    documentChanges: Optional[List[Union["TextDocumentEdit", "CreateFile", "RenameFile", "DeleteFile"]]]
    
    # A map of change annotations that can be referenced in `AnnotatedTextEdit`s or create, rename and
    # delete file / folder operations.
    # 
    # Whether clients honor this property depends on the client capability `workspace.changeAnnotationSupport`.
    # 
    # @since 3.16.0
    changeAnnotations: Optional[Dict[ChangeAnnotationIdentifier, "ChangeAnnotation"]]

    def __init__(self, *, changes: Optional[Dict[str, List["TextEdit"]]] = None, documentChanges: Optional[List[Union["TextDocumentEdit", "CreateFile", "RenameFile", "DeleteFile"]]] = None, changeAnnotations: Optional[Dict[ChangeAnnotationIdentifier, "ChangeAnnotation"]] = None) -> None:
        """
        - changes: Holds changes to existing resources.
        - documentChanges: Depending on the client capability `workspace.workspaceEdit.resourceOperations` document changes
            are either an array of `TextDocumentEdit`s to express changes to n different text documents
            where each text document edit addresses a specific version of a text document. Or it can contain
            above `TextDocumentEdit`s mixed with create, rename and delete file / folder operations.
            
            Whether a client supports versioned document edits is expressed via
            `workspace.workspaceEdit.documentChanges` client capability.
            
            If a client neither supports `documentChanges` nor `workspace.workspaceEdit.resourceOperations` then
            only plain `TextEdit`s using the `changes` property are supported.
        - changeAnnotations: A map of change annotations that can be referenced in `AnnotatedTextEdit`s or create, rename and
            delete file / folder operations.
            
            Whether clients honor this property depends on the client capability `workspace.changeAnnotationSupport`.
            
            @since 3.16.0
        """
        self.changes = changes
        self.documentChanges = documentChanges
        self.changeAnnotations = changeAnnotations

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "WorkspaceEdit":
        if changes_json := json_get_optional_object(obj, "changes"):
            changes = { json_assert_type_string(key): [TextEdit.from_json(json_assert_type_object(i)) for i in json_assert_type_array(value)] for key, value in changes_json.items()}
        else:
            changes = None
        if documentChanges_json := json_get_optional_array(obj, "documentChanges"):
            documentChanges = [parse_or_type((i), (lambda v: TextDocumentEdit.from_json(json_assert_type_object(v)), lambda v: CreateFile.from_json(json_assert_type_object(v)), lambda v: RenameFile.from_json(json_assert_type_object(v)), lambda v: DeleteFile.from_json(json_assert_type_object(v)))) for i in documentChanges_json]
        else:
            documentChanges = None
        if changeAnnotations_json := json_get_optional_object(obj, "changeAnnotations"):
            changeAnnotations = { json_assert_type_string(key): ChangeAnnotation.from_json(json_assert_type_object(value)) for key, value in changeAnnotations_json.items()}
        else:
            changeAnnotations = None
        return cls(changes=changes, documentChanges=documentChanges, changeAnnotations=changeAnnotations)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.changes is not None:
            out["changes"] = { key: [i.to_json() for i in val] for key, val in self.changes.items() }
        if self.documentChanges is not None:
            out["documentChanges"] = [write_or_type(i, (lambda i: isinstance(i, TextDocumentEdit), lambda i: isinstance(i, CreateFile), lambda i: isinstance(i, RenameFile), lambda i: isinstance(i, DeleteFile)), (lambda i: i.to_json(), lambda i: i.to_json(), lambda i: i.to_json(), lambda i: i.to_json())) for i in self.documentChanges]
        if self.changeAnnotations is not None:
            out["changeAnnotations"] = { write_ChangeAnnotationIdentifier(key): val.to_json() for key, val in self.changeAnnotations.items() }
        return out


@dataclass
class FileOperationPatternOptions():
    """
    Matching options for the file operation pattern.
    
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # The pattern should be matched ignoring casing.
    ignoreCase: Optional[bool]

    def __init__(self, *, ignoreCase: Optional[bool] = None) -> None:
        """
        - ignoreCase: The pattern should be matched ignoring casing.
        """
        self.ignoreCase = ignoreCase

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "FileOperationPatternOptions":
        if ignoreCase_json := json_get_optional_bool(obj, "ignoreCase"):
            ignoreCase = ignoreCase_json
        else:
            ignoreCase = None
        return cls(ignoreCase=ignoreCase)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.ignoreCase is not None:
            out["ignoreCase"] = self.ignoreCase
        return out


@dataclass
class FileOperationPattern():
    """
    A pattern to describe in which file operation requests or notifications
    the server is interested in receiving.
    
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # The glob pattern to match. Glob patterns can have the following syntax:
    # - `*` to match one or more characters in a path segment
    # - `?` to match on one character in a path segment
    # - `**` to match any number of path segments, including none
    # - `{}` to group sub patterns into an OR expression. (e.g. `**​/*.{ts,js}` matches all TypeScript and JavaScript files)
    # - `[]` to declare a range of characters to match in a path segment (e.g., `example.[0-9]` to match on `example.0`, `example.1`, …)
    # - `[!...]` to negate a range of characters to match in a path segment (e.g., `example.[!0-9]` to match on `example.a`, `example.b`, but not `example.0`)
    glob: str
    
    # Whether to match files or folders with this pattern.
    # 
    # Matches both if undefined.
    matches: Optional["FileOperationPatternKind"]
    
    # Additional options used during matching.
    options: Optional["FileOperationPatternOptions"]

    def __init__(self, *, glob: str, matches: Optional["FileOperationPatternKind"] = None, options: Optional["FileOperationPatternOptions"] = None) -> None:
        """
        - glob: The glob pattern to match. Glob patterns can have the following syntax:
            - `*` to match one or more characters in a path segment
            - `?` to match on one character in a path segment
            - `**` to match any number of path segments, including none
            - `{}` to group sub patterns into an OR expression. (e.g. `**​/*.{ts,js}` matches all TypeScript and JavaScript files)
            - `[]` to declare a range of characters to match in a path segment (e.g., `example.[0-9]` to match on `example.0`, `example.1`, …)
            - `[!...]` to negate a range of characters to match in a path segment (e.g., `example.[!0-9]` to match on `example.a`, `example.b`, but not `example.0`)
        - matches: Whether to match files or folders with this pattern.
            
            Matches both if undefined.
        - options: Additional options used during matching.
        """
        self.glob = glob
        self.matches = matches
        self.options = options

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "FileOperationPattern":
        glob = json_get_string(obj, "glob")
        if matches_json := json_get_optional_string(obj, "matches"):
            matches = FileOperationPatternKind(matches_json)
        else:
            matches = None
        if options_json := json_get_optional_object(obj, "options"):
            options = FileOperationPatternOptions.from_json(options_json)
        else:
            options = None
        return cls(glob=glob, matches=matches, options=options)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["glob"] = self.glob
        if self.matches is not None:
            out["matches"] = self.matches.value
        if self.options is not None:
            out["options"] = self.options.to_json()
        return out


@dataclass
class FileOperationFilter():
    """
    A filter to describe in which file operation requests or notifications
    the server is interested in receiving.
    
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # A Uri scheme like `file` or `untitled`.
    scheme: Optional[str]
    
    # The actual file operation pattern.
    pattern: "FileOperationPattern"

    def __init__(self, *, scheme: Optional[str] = None, pattern: "FileOperationPattern") -> None:
        """
        - scheme: A Uri scheme like `file` or `untitled`.
        - pattern: The actual file operation pattern.
        """
        self.scheme = scheme
        self.pattern = pattern

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "FileOperationFilter":
        if scheme_json := json_get_optional_string(obj, "scheme"):
            scheme = scheme_json
        else:
            scheme = None
        pattern = FileOperationPattern.from_json(json_get_object(obj, "pattern"))
        return cls(scheme=scheme, pattern=pattern)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.scheme is not None:
            out["scheme"] = self.scheme
        out["pattern"] = self.pattern.to_json()
        return out


@dataclass
class FileOperationRegistrationOptions():
    """
    The options to register for file operations.
    
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # The actual filters.
    filters: List["FileOperationFilter"]

    def __init__(self, *, filters: List["FileOperationFilter"]) -> None:
        """
        - filters: The actual filters.
        """
        self.filters = filters

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "FileOperationRegistrationOptions":
        filters = [FileOperationFilter.from_json(json_assert_type_object(i)) for i in json_get_array(obj, "filters")]
        return cls(filters=filters)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["filters"] = [i.to_json() for i in self.filters]
        return out


@dataclass
class FileRename():
    """
    Represents information on a file/folder rename.
    
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # A file:// URI for the original location of the file/folder being renamed.
    oldUri: str
    
    # A file:// URI for the new location of the file/folder being renamed.
    newUri: str

    def __init__(self, *, oldUri: str, newUri: str) -> None:
        """
        - oldUri: A file:// URI for the original location of the file/folder being renamed.
        - newUri: A file:// URI for the new location of the file/folder being renamed.
        """
        self.oldUri = oldUri
        self.newUri = newUri

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "FileRename":
        oldUri = json_get_string(obj, "oldUri")
        newUri = json_get_string(obj, "newUri")
        return cls(oldUri=oldUri, newUri=newUri)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["oldUri"] = self.oldUri
        out["newUri"] = self.newUri
        return out


@dataclass
class RenameFilesParams():
    """
    The parameters sent in notifications/requests for user-initiated renames of
    files.
    
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # An array of all files/folders renamed in this operation. When a folder is renamed, only
    # the folder will be included, and not its children.
    files: List["FileRename"]

    def __init__(self, *, files: List["FileRename"]) -> None:
        """
        - files: An array of all files/folders renamed in this operation. When a folder is renamed, only
            the folder will be included, and not its children.
        """
        self.files = files

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "RenameFilesParams":
        files = [FileRename.from_json(json_assert_type_object(i)) for i in json_get_array(obj, "files")]
        return cls(files=files)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["files"] = [i.to_json() for i in self.files]
        return out


@dataclass
class FileDelete():
    """
    Represents information on a file/folder delete.
    
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # A file:// URI for the location of the file/folder being deleted.
    uri: str

    def __init__(self, *, uri: str) -> None:
        """
        - uri: A file:// URI for the location of the file/folder being deleted.
        """
        self.uri = uri

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "FileDelete":
        uri = json_get_string(obj, "uri")
        return cls(uri=uri)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["uri"] = self.uri
        return out


@dataclass
class DeleteFilesParams():
    """
    The parameters sent in notifications/requests for user-initiated deletes of
    files.
    
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # An array of all files/folders deleted in this operation.
    files: List["FileDelete"]

    def __init__(self, *, files: List["FileDelete"]) -> None:
        """
        - files: An array of all files/folders deleted in this operation.
        """
        self.files = files

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DeleteFilesParams":
        files = [FileDelete.from_json(json_assert_type_object(i)) for i in json_get_array(obj, "files")]
        return cls(files=files)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["files"] = [i.to_json() for i in self.files]
        return out


@dataclass
class MonikerParams(TextDocumentPositionParams):
    """


    *Generated from the TypeScript documentation*
    """

    # The text document.
    textDocument: "TextDocumentIdentifier"
    
    # The position inside the text document.
    position: "Position"
    
    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]
    
    # An optional token that a server can use to report partial results (e.g. streaming) to
    # the client.
    partialResultToken: Optional["ProgressToken"]

    def __init__(self, *, textDocument: "TextDocumentIdentifier", position: "Position", workDoneToken: Optional["ProgressToken"] = None, partialResultToken: Optional["ProgressToken"] = None) -> None:
        """
        - textDocument: The text document.
        - position: The position inside the text document.
        - workDoneToken: An optional token that a server can use to report work done progress.
        - partialResultToken: An optional token that a server can use to report partial results (e.g. streaming) to
            the client.
        """
        self.textDocument = textDocument
        self.position = position
        self.workDoneToken = workDoneToken
        self.partialResultToken = partialResultToken

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "MonikerParams":
        textDocument = TextDocumentIdentifier.from_json(json_get_object(obj, "textDocument"))
        position = Position.from_json(json_get_object(obj, "position"))
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        if partialResultToken_json := obj.get("partialResultToken"):
            partialResultToken = parse_ProgressToken(partialResultToken_json)
        else:
            partialResultToken = None
        return cls(textDocument=textDocument, position=position, workDoneToken=workDoneToken, partialResultToken=partialResultToken)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["textDocument"] = self.textDocument.to_json()
        out["position"] = self.position.to_json()
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        if self.partialResultToken is not None:
            out["partialResultToken"] = write_ProgressToken(self.partialResultToken)
        return out


@dataclass
class Moniker():
    """
    Moniker definition to match LSIF 0.5 moniker definition.
    
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # The scheme of the moniker. For example tsc or .Net
    scheme: str
    
    # The identifier of the moniker. The value is opaque in LSIF however
    # schema owners are allowed to define the structure if they want.
    identifier: str
    
    # The scope in which the moniker is unique
    unique: "UniquenessLevel"
    
    # The moniker kind if known.
    kind: Optional["MonikerKind"]

    def __init__(self, *, scheme: str, identifier: str, unique: "UniquenessLevel", kind: Optional["MonikerKind"] = None) -> None:
        """
        - scheme: The scheme of the moniker. For example tsc or .Net
        - identifier: The identifier of the moniker. The value is opaque in LSIF however
            schema owners are allowed to define the structure if they want.
        - unique: The scope in which the moniker is unique
        - kind: The moniker kind if known.
        """
        self.scheme = scheme
        self.identifier = identifier
        self.unique = unique
        self.kind = kind

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "Moniker":
        scheme = json_get_string(obj, "scheme")
        identifier = json_get_string(obj, "identifier")
        unique = UniquenessLevel(json_get_string(obj, "unique"))
        if kind_json := json_get_optional_string(obj, "kind"):
            kind = MonikerKind(kind_json)
        else:
            kind = None
        return cls(scheme=scheme, identifier=identifier, unique=unique, kind=kind)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["scheme"] = self.scheme
        out["identifier"] = self.identifier
        out["unique"] = self.unique.value
        if self.kind is not None:
            out["kind"] = self.kind.value
        return out


@dataclass
class MonikerOptions():
    """


    *Generated from the TypeScript documentation*
    """

    workDoneProgress: Optional[bool]

    def __init__(self, *, workDoneProgress: Optional[bool] = None) -> None:
        """
    
        """
        self.workDoneProgress = workDoneProgress

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "MonikerOptions":
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        return cls(workDoneProgress=workDoneProgress)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        return out


@dataclass
class MonikerRegistrationOptions(TextDocumentRegistrationOptions, MonikerOptions):
    """


    *Generated from the TypeScript documentation*
    """

    # A document selector to identify the scope of the registration. If set to null
    # the document selector provided on the client side will be used.
    documentSelector: Union["DocumentSelector", None]
    
    workDoneProgress: Optional[bool]

    def __init__(self, *, documentSelector: Union["DocumentSelector", None], workDoneProgress: Optional[bool] = None) -> None:
        """
        - documentSelector: A document selector to identify the scope of the registration. If set to null
            the document selector provided on the client side will be used.
        """
        self.documentSelector = documentSelector
        self.workDoneProgress = workDoneProgress

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "MonikerRegistrationOptions":
        documentSelector = parse_or_type(obj["documentSelector"], (lambda v: parse_DocumentSelector(json_assert_type_array(v)), lambda v: json_assert_type_null(v)))
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        return cls(documentSelector=documentSelector, workDoneProgress=workDoneProgress)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["documentSelector"] = write_or_type(self.documentSelector, (lambda i: isinstance(i, List) and (len(i) == 0 or (((isinstance(i[0], Dict) and "language" in i[0].keys()) or (isinstance(i[0], Dict) and "scheme" in i[0].keys()) or (isinstance(i[0], Dict) and "pattern" in i[0].keys())) or (isinstance(i[0], NotebookCellTextDocumentFilter)))), lambda i: i is None), (lambda i: write_DocumentSelector(i), lambda i: i))
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        return out


@dataclass
class TypeHierarchyPrepareParams(TextDocumentPositionParams):
    """
    The parameter of a `textDocument/prepareTypeHierarchy` request.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # The text document.
    textDocument: "TextDocumentIdentifier"
    
    # The position inside the text document.
    position: "Position"
    
    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]

    def __init__(self, *, textDocument: "TextDocumentIdentifier", position: "Position", workDoneToken: Optional["ProgressToken"] = None) -> None:
        """
        - textDocument: The text document.
        - position: The position inside the text document.
        - workDoneToken: An optional token that a server can use to report work done progress.
        """
        self.textDocument = textDocument
        self.position = position
        self.workDoneToken = workDoneToken

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "TypeHierarchyPrepareParams":
        textDocument = TextDocumentIdentifier.from_json(json_get_object(obj, "textDocument"))
        position = Position.from_json(json_get_object(obj, "position"))
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        return cls(textDocument=textDocument, position=position, workDoneToken=workDoneToken)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["textDocument"] = self.textDocument.to_json()
        out["position"] = self.position.to_json()
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        return out


@dataclass
class TypeHierarchyItem():
    """
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # The name of this item.
    name: str
    
    # The kind of this item.
    kind: "SymbolKind"
    
    # Tags for this item.
    tags: Optional[List["SymbolTag"]]
    
    # More detail for this item, e.g. the signature of a function.
    detail: Optional[str]
    
    # The resource identifier of this item.
    uri: str
    
    # The range enclosing this symbol not including leading/trailing whitespace
    # but everything else, e.g. comments and code.
    range: "Range"
    
    # The range that should be selected and revealed when this symbol is being
    # picked, e.g. the name of a function. Must be contained by the
    # [`range`](#TypeHierarchyItem.range).
    selectionRange: "Range"
    
    # A data entry field that is preserved between a type hierarchy prepare and
    # supertypes or subtypes requests. It could also be used to identify the
    # type hierarchy in the server, helping improve the performance on
    # resolving supertypes and subtypes.
    data: Optional["LSPAny"]

    def __init__(self, *, name: str, kind: "SymbolKind", tags: Optional[List["SymbolTag"]] = None, detail: Optional[str] = None, uri: str, range: "Range", selectionRange: "Range", data: Optional["LSPAny"] = None) -> None:
        """
        - name: The name of this item.
        - kind: The kind of this item.
        - tags: Tags for this item.
        - detail: More detail for this item, e.g. the signature of a function.
        - uri: The resource identifier of this item.
        - range: The range enclosing this symbol not including leading/trailing whitespace
            but everything else, e.g. comments and code.
        - selectionRange: The range that should be selected and revealed when this symbol is being
            picked, e.g. the name of a function. Must be contained by the
            [`range`](#TypeHierarchyItem.range).
        - data: A data entry field that is preserved between a type hierarchy prepare and
            supertypes or subtypes requests. It could also be used to identify the
            type hierarchy in the server, helping improve the performance on
            resolving supertypes and subtypes.
        """
        self.name = name
        self.kind = kind
        self.tags = tags
        self.detail = detail
        self.uri = uri
        self.range = range
        self.selectionRange = selectionRange
        self.data = data

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "TypeHierarchyItem":
        name = json_get_string(obj, "name")
        kind = SymbolKind(json_get_int(obj, "kind"))
        if tags_json := json_get_optional_array(obj, "tags"):
            tags = [SymbolTag(json_assert_type_int(i)) for i in tags_json]
        else:
            tags = None
        if detail_json := json_get_optional_string(obj, "detail"):
            detail = detail_json
        else:
            detail = None
        uri = json_get_string(obj, "uri")
        range = Range.from_json(json_get_object(obj, "range"))
        selectionRange = Range.from_json(json_get_object(obj, "selectionRange"))
        if data_json := obj.get("data"):
            data = parse_LSPAny(data_json)
        else:
            data = None
        return cls(name=name, kind=kind, tags=tags, detail=detail, uri=uri, range=range, selectionRange=selectionRange, data=data)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["name"] = self.name
        out["kind"] = self.kind.value
        if self.tags is not None:
            out["tags"] = [i.value for i in self.tags]
        if self.detail is not None:
            out["detail"] = self.detail
        out["uri"] = self.uri
        out["range"] = self.range.to_json()
        out["selectionRange"] = self.selectionRange.to_json()
        if self.data is not None:
            out["data"] = write_LSPAny(self.data)
        return out


@dataclass
class TypeHierarchyOptions():
    """
    Type hierarchy options used during static registration.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    workDoneProgress: Optional[bool]

    def __init__(self, *, workDoneProgress: Optional[bool] = None) -> None:
        """
    
        """
        self.workDoneProgress = workDoneProgress

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "TypeHierarchyOptions":
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        return cls(workDoneProgress=workDoneProgress)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        return out


@dataclass
class TypeHierarchyRegistrationOptions(TextDocumentRegistrationOptions, TypeHierarchyOptions):
    """
    Type hierarchy options used during static or dynamic registration.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # A document selector to identify the scope of the registration. If set to null
    # the document selector provided on the client side will be used.
    documentSelector: Union["DocumentSelector", None]
    
    workDoneProgress: Optional[bool]
    
    # The id used to register the request. The id can be used to deregister
    # the request again. See also Registration#id.
    id: Optional[str]

    def __init__(self, *, documentSelector: Union["DocumentSelector", None], workDoneProgress: Optional[bool] = None, id: Optional[str] = None) -> None:
        """
        - documentSelector: A document selector to identify the scope of the registration. If set to null
            the document selector provided on the client side will be used.
        - id: The id used to register the request. The id can be used to deregister
            the request again. See also Registration#id.
        """
        self.documentSelector = documentSelector
        self.workDoneProgress = workDoneProgress
        self.id = id

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "TypeHierarchyRegistrationOptions":
        documentSelector = parse_or_type(obj["documentSelector"], (lambda v: parse_DocumentSelector(json_assert_type_array(v)), lambda v: json_assert_type_null(v)))
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        if id_json := json_get_optional_string(obj, "id"):
            id = id_json
        else:
            id = None
        return cls(documentSelector=documentSelector, workDoneProgress=workDoneProgress, id=id)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["documentSelector"] = write_or_type(self.documentSelector, (lambda i: isinstance(i, List) and (len(i) == 0 or (((isinstance(i[0], Dict) and "language" in i[0].keys()) or (isinstance(i[0], Dict) and "scheme" in i[0].keys()) or (isinstance(i[0], Dict) and "pattern" in i[0].keys())) or (isinstance(i[0], NotebookCellTextDocumentFilter)))), lambda i: i is None), (lambda i: write_DocumentSelector(i), lambda i: i))
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        if self.id is not None:
            out["id"] = self.id
        return out


@dataclass
class TypeHierarchySupertypesParams():
    """
    The parameter of a `typeHierarchy/supertypes` request.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]
    
    # An optional token that a server can use to report partial results (e.g. streaming) to
    # the client.
    partialResultToken: Optional["ProgressToken"]
    
    item: "TypeHierarchyItem"

    def __init__(self, *, workDoneToken: Optional["ProgressToken"] = None, partialResultToken: Optional["ProgressToken"] = None, item: "TypeHierarchyItem") -> None:
        """
        - workDoneToken: An optional token that a server can use to report work done progress.
        - partialResultToken: An optional token that a server can use to report partial results (e.g. streaming) to
            the client.
        """
        self.workDoneToken = workDoneToken
        self.partialResultToken = partialResultToken
        self.item = item

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "TypeHierarchySupertypesParams":
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        if partialResultToken_json := obj.get("partialResultToken"):
            partialResultToken = parse_ProgressToken(partialResultToken_json)
        else:
            partialResultToken = None
        item = TypeHierarchyItem.from_json(json_get_object(obj, "item"))
        return cls(workDoneToken=workDoneToken, partialResultToken=partialResultToken, item=item)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        if self.partialResultToken is not None:
            out["partialResultToken"] = write_ProgressToken(self.partialResultToken)
        out["item"] = self.item.to_json()
        return out


@dataclass
class TypeHierarchySubtypesParams():
    """
    The parameter of a `typeHierarchy/subtypes` request.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]
    
    # An optional token that a server can use to report partial results (e.g. streaming) to
    # the client.
    partialResultToken: Optional["ProgressToken"]
    
    item: "TypeHierarchyItem"

    def __init__(self, *, workDoneToken: Optional["ProgressToken"] = None, partialResultToken: Optional["ProgressToken"] = None, item: "TypeHierarchyItem") -> None:
        """
        - workDoneToken: An optional token that a server can use to report work done progress.
        - partialResultToken: An optional token that a server can use to report partial results (e.g. streaming) to
            the client.
        """
        self.workDoneToken = workDoneToken
        self.partialResultToken = partialResultToken
        self.item = item

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "TypeHierarchySubtypesParams":
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        if partialResultToken_json := obj.get("partialResultToken"):
            partialResultToken = parse_ProgressToken(partialResultToken_json)
        else:
            partialResultToken = None
        item = TypeHierarchyItem.from_json(json_get_object(obj, "item"))
        return cls(workDoneToken=workDoneToken, partialResultToken=partialResultToken, item=item)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        if self.partialResultToken is not None:
            out["partialResultToken"] = write_ProgressToken(self.partialResultToken)
        out["item"] = self.item.to_json()
        return out


@dataclass
class InlineValueContext():
    """
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # The stack frame (as a DAP Id) where the execution has stopped.
    frameId: int
    
    # The document range where execution has stopped.
    # Typically the end position of the range denotes the line where the inline values are shown.
    stoppedLocation: "Range"

    def __init__(self, *, frameId: int, stoppedLocation: "Range") -> None:
        """
        - frameId: The stack frame (as a DAP Id) where the execution has stopped.
        - stoppedLocation: The document range where execution has stopped.
            Typically the end position of the range denotes the line where the inline values are shown.
        """
        self.frameId = frameId
        self.stoppedLocation = stoppedLocation

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "InlineValueContext":
        frameId = json_get_int(obj, "frameId")
        stoppedLocation = Range.from_json(json_get_object(obj, "stoppedLocation"))
        return cls(frameId=frameId, stoppedLocation=stoppedLocation)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["frameId"] = self.frameId
        out["stoppedLocation"] = self.stoppedLocation.to_json()
        return out


@dataclass
class InlineValueParams():
    """
    A parameter literal used in inline value requests.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]
    
    # The text document.
    textDocument: "TextDocumentIdentifier"
    
    # The document range for which inline values should be computed.
    range: "Range"
    
    # Additional information about the context in which inline values were
    # requested.
    context: "InlineValueContext"

    def __init__(self, *, workDoneToken: Optional["ProgressToken"] = None, textDocument: "TextDocumentIdentifier", range: "Range", context: "InlineValueContext") -> None:
        """
        - workDoneToken: An optional token that a server can use to report work done progress.
        - textDocument: The text document.
        - range: The document range for which inline values should be computed.
        - context: Additional information about the context in which inline values were
            requested.
        """
        self.workDoneToken = workDoneToken
        self.textDocument = textDocument
        self.range = range
        self.context = context

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "InlineValueParams":
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        textDocument = TextDocumentIdentifier.from_json(json_get_object(obj, "textDocument"))
        range = Range.from_json(json_get_object(obj, "range"))
        context = InlineValueContext.from_json(json_get_object(obj, "context"))
        return cls(workDoneToken=workDoneToken, textDocument=textDocument, range=range, context=context)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        out["textDocument"] = self.textDocument.to_json()
        out["range"] = self.range.to_json()
        out["context"] = self.context.to_json()
        return out


@dataclass
class InlineValueOptions():
    """
    Inline value options used during static registration.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    workDoneProgress: Optional[bool]

    def __init__(self, *, workDoneProgress: Optional[bool] = None) -> None:
        """
    
        """
        self.workDoneProgress = workDoneProgress

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "InlineValueOptions":
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        return cls(workDoneProgress=workDoneProgress)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        return out


@dataclass
class InlineValueRegistrationOptions(InlineValueOptions, TextDocumentRegistrationOptions):
    """
    Inline value options used during static or dynamic registration.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    workDoneProgress: Optional[bool]
    
    # A document selector to identify the scope of the registration. If set to null
    # the document selector provided on the client side will be used.
    documentSelector: Union["DocumentSelector", None]
    
    # The id used to register the request. The id can be used to deregister
    # the request again. See also Registration#id.
    id: Optional[str]

    def __init__(self, *, workDoneProgress: Optional[bool] = None, documentSelector: Union["DocumentSelector", None], id: Optional[str] = None) -> None:
        """
        - documentSelector: A document selector to identify the scope of the registration. If set to null
            the document selector provided on the client side will be used.
        - id: The id used to register the request. The id can be used to deregister
            the request again. See also Registration#id.
        """
        self.workDoneProgress = workDoneProgress
        self.documentSelector = documentSelector
        self.id = id

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "InlineValueRegistrationOptions":
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        documentSelector = parse_or_type(obj["documentSelector"], (lambda v: parse_DocumentSelector(json_assert_type_array(v)), lambda v: json_assert_type_null(v)))
        if id_json := json_get_optional_string(obj, "id"):
            id = id_json
        else:
            id = None
        return cls(workDoneProgress=workDoneProgress, documentSelector=documentSelector, id=id)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        out["documentSelector"] = write_or_type(self.documentSelector, (lambda i: isinstance(i, List) and (len(i) == 0 or (((isinstance(i[0], Dict) and "language" in i[0].keys()) or (isinstance(i[0], Dict) and "scheme" in i[0].keys()) or (isinstance(i[0], Dict) and "pattern" in i[0].keys())) or (isinstance(i[0], NotebookCellTextDocumentFilter)))), lambda i: i is None), (lambda i: write_DocumentSelector(i), lambda i: i))
        if self.id is not None:
            out["id"] = self.id
        return out


@dataclass
class InlayHintParams():
    """
    A parameter literal used in inlay hint requests.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]
    
    # The text document.
    textDocument: "TextDocumentIdentifier"
    
    # The document range for which inlay hints should be computed.
    range: "Range"

    def __init__(self, *, workDoneToken: Optional["ProgressToken"] = None, textDocument: "TextDocumentIdentifier", range: "Range") -> None:
        """
        - workDoneToken: An optional token that a server can use to report work done progress.
        - textDocument: The text document.
        - range: The document range for which inlay hints should be computed.
        """
        self.workDoneToken = workDoneToken
        self.textDocument = textDocument
        self.range = range

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "InlayHintParams":
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        textDocument = TextDocumentIdentifier.from_json(json_get_object(obj, "textDocument"))
        range = Range.from_json(json_get_object(obj, "range"))
        return cls(workDoneToken=workDoneToken, textDocument=textDocument, range=range)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        out["textDocument"] = self.textDocument.to_json()
        out["range"] = self.range.to_json()
        return out


@dataclass
class MarkupContent():
    """
    A `MarkupContent` literal represents a string value which content is interpreted base on its
    kind flag. Currently the protocol supports `plaintext` and `markdown` as markup kinds.
    
    If the kind is `markdown` then the value can contain fenced code blocks like in GitHub issues.
    See https://help.github.com/articles/creating-and-highlighting-code-blocks/#syntax-highlighting
    
    Here is an example how such a string can be constructed using JavaScript / TypeScript:
    ```ts
    let markdown: MarkdownContent = {
     kind: MarkupKind.Markdown,
     value: [
       '# Header',
       'Some text',
       '```typescript',
       'someCode();',
       '```'
     ].join('\n')
    };
    ```
    
    *Please Note* that clients might sanitize the return markdown. A client could decide to
    remove HTML from the markdown to avoid script execution.

    *Generated from the TypeScript documentation*
    """

    # The type of the Markup
    kind: "MarkupKind"
    
    # The content itself
    value: str

    def __init__(self, *, kind: "MarkupKind", value: str) -> None:
        """
        - kind: The type of the Markup
        - value: The content itself
        """
        self.kind = kind
        self.value = value

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "MarkupContent":
        kind = MarkupKind(json_get_string(obj, "kind"))
        value = json_get_string(obj, "value")
        return cls(kind=kind, value=value)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["kind"] = self.kind.value
        out["value"] = self.value
        return out


@dataclass
class Command():
    """
    Represents a reference to a command. Provides a title which
    will be used to represent a command in the UI and, optionally,
    an array of arguments which will be passed to the command handler
    function when invoked.

    *Generated from the TypeScript documentation*
    """

    # Title of the command, like `save`.
    title: str
    
    # The identifier of the actual command handler.
    command: str
    
    # Arguments that the command handler should be
    # invoked with.
    arguments: Optional[List["LSPAny"]]

    def __init__(self, *, title: str, command: str, arguments: Optional[List["LSPAny"]] = None) -> None:
        """
        - title: Title of the command, like `save`.
        - command: The identifier of the actual command handler.
        - arguments: Arguments that the command handler should be
            invoked with.
        """
        self.title = title
        self.command = command
        self.arguments = arguments

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "Command":
        title = json_get_string(obj, "title")
        command = json_get_string(obj, "command")
        if arguments_json := json_get_optional_array(obj, "arguments"):
            arguments = [parse_LSPAny((i)) for i in arguments_json]
        else:
            arguments = None
        return cls(title=title, command=command, arguments=arguments)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["title"] = self.title
        out["command"] = self.command
        if self.arguments is not None:
            out["arguments"] = [write_LSPAny(i) for i in self.arguments]
        return out


@dataclass
class InlayHintLabelPart():
    """
    An inlay hint label part allows for interactive and composite labels
    of inlay hints.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # The value of this label part.
    value: str
    
    # The tooltip text when you hover over this label part. Depending on
    # the client capability `inlayHint.resolveSupport` clients might resolve
    # this property late using the resolve request.
    tooltip: Optional[Union[str, "MarkupContent"]]
    
    # An optional source code location that represents this
    # label part.
    # 
    # The editor will use this location for the hover and for code navigation
    # features: This part will become a clickable link that resolves to the
    # definition of the symbol at the given location (not necessarily the
    # location itself), it shows the hover that shows at the given location,
    # and it shows a context menu with further code navigation commands.
    # 
    # Depending on the client capability `inlayHint.resolveSupport` clients
    # might resolve this property late using the resolve request.
    location: Optional["Location"]
    
    # An optional command for this label part.
    # 
    # Depending on the client capability `inlayHint.resolveSupport` clients
    # might resolve this property late using the resolve request.
    command: Optional["Command"]

    def __init__(self, *, value: str, tooltip: Optional[Union[str, "MarkupContent"]] = None, location: Optional["Location"] = None, command: Optional["Command"] = None) -> None:
        """
        - value: The value of this label part.
        - tooltip: The tooltip text when you hover over this label part. Depending on
            the client capability `inlayHint.resolveSupport` clients might resolve
            this property late using the resolve request.
        - location: An optional source code location that represents this
            label part.
            
            The editor will use this location for the hover and for code navigation
            features: This part will become a clickable link that resolves to the
            definition of the symbol at the given location (not necessarily the
            location itself), it shows the hover that shows at the given location,
            and it shows a context menu with further code navigation commands.
            
            Depending on the client capability `inlayHint.resolveSupport` clients
            might resolve this property late using the resolve request.
        - command: An optional command for this label part.
            
            Depending on the client capability `inlayHint.resolveSupport` clients
            might resolve this property late using the resolve request.
        """
        self.value = value
        self.tooltip = tooltip
        self.location = location
        self.command = command

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "InlayHintLabelPart":
        value = json_get_string(obj, "value")
        if tooltip_json := obj.get("tooltip"):
            tooltip = parse_or_type(tooltip_json, (lambda v: json_assert_type_string(v), lambda v: MarkupContent.from_json(json_assert_type_object(v))))
        else:
            tooltip = None
        if location_json := json_get_optional_object(obj, "location"):
            location = Location.from_json(location_json)
        else:
            location = None
        if command_json := json_get_optional_object(obj, "command"):
            command = Command.from_json(command_json)
        else:
            command = None
        return cls(value=value, tooltip=tooltip, location=location, command=command)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["value"] = self.value
        if self.tooltip is not None:
            out["tooltip"] = write_or_type(self.tooltip, (lambda i: isinstance(i, str), lambda i: isinstance(i, MarkupContent)), (lambda i: i, lambda i: i.to_json()))
        if self.location is not None:
            out["location"] = self.location.to_json()
        if self.command is not None:
            out["command"] = self.command.to_json()
        return out


@dataclass
class InlayHint():
    """
    Inlay hint information.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # The position of this hint.
    position: "Position"
    
    # The label of this hint. A human readable string or an array of
    # InlayHintLabelPart label parts.
    # 
    # *Note* that neither the string nor the label part can be empty.
    label: Union[str, List["InlayHintLabelPart"]]
    
    # The kind of this hint. Can be omitted in which case the client
    # should fall back to a reasonable default.
    kind: Optional["InlayHintKind"]
    
    # Optional text edits that are performed when accepting this inlay hint.
    # 
    # *Note* that edits are expected to change the document so that the inlay
    # hint (or its nearest variant) is now part of the document and the inlay
    # hint itself is now obsolete.
    textEdits: Optional[List["TextEdit"]]
    
    # The tooltip text when you hover over this item.
    tooltip: Optional[Union[str, "MarkupContent"]]
    
    # Render padding before the hint.
    # 
    # Note: Padding should use the editor's background color, not the
    # background color of the hint itself. That means padding can be used
    # to visually align/separate an inlay hint.
    paddingLeft: Optional[bool]
    
    # Render padding after the hint.
    # 
    # Note: Padding should use the editor's background color, not the
    # background color of the hint itself. That means padding can be used
    # to visually align/separate an inlay hint.
    paddingRight: Optional[bool]
    
    # A data entry field that is preserved on an inlay hint between
    # a `textDocument/inlayHint` and a `inlayHint/resolve` request.
    data: Optional["LSPAny"]

    def __init__(self, *, position: "Position", label: Union[str, List["InlayHintLabelPart"]], kind: Optional["InlayHintKind"] = None, textEdits: Optional[List["TextEdit"]] = None, tooltip: Optional[Union[str, "MarkupContent"]] = None, paddingLeft: Optional[bool] = None, paddingRight: Optional[bool] = None, data: Optional["LSPAny"] = None) -> None:
        """
        - position: The position of this hint.
        - label: The label of this hint. A human readable string or an array of
            InlayHintLabelPart label parts.
            
            *Note* that neither the string nor the label part can be empty.
        - kind: The kind of this hint. Can be omitted in which case the client
            should fall back to a reasonable default.
        - textEdits: Optional text edits that are performed when accepting this inlay hint.
            
            *Note* that edits are expected to change the document so that the inlay
            hint (or its nearest variant) is now part of the document and the inlay
            hint itself is now obsolete.
        - tooltip: The tooltip text when you hover over this item.
        - paddingLeft: Render padding before the hint.
            
            Note: Padding should use the editor's background color, not the
            background color of the hint itself. That means padding can be used
            to visually align/separate an inlay hint.
        - paddingRight: Render padding after the hint.
            
            Note: Padding should use the editor's background color, not the
            background color of the hint itself. That means padding can be used
            to visually align/separate an inlay hint.
        - data: A data entry field that is preserved on an inlay hint between
            a `textDocument/inlayHint` and a `inlayHint/resolve` request.
        """
        self.position = position
        self.label = label
        self.kind = kind
        self.textEdits = textEdits
        self.tooltip = tooltip
        self.paddingLeft = paddingLeft
        self.paddingRight = paddingRight
        self.data = data

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "InlayHint":
        position = Position.from_json(json_get_object(obj, "position"))
        label = parse_or_type(obj["label"], (lambda v: json_assert_type_string(v), lambda v: [InlayHintLabelPart.from_json(json_assert_type_object(i)) for i in json_assert_type_array(v)]))
        if kind_json := json_get_optional_int(obj, "kind"):
            kind = InlayHintKind(kind_json)
        else:
            kind = None
        if textEdits_json := json_get_optional_array(obj, "textEdits"):
            textEdits = [TextEdit.from_json(json_assert_type_object(i)) for i in textEdits_json]
        else:
            textEdits = None
        if tooltip_json := obj.get("tooltip"):
            tooltip = parse_or_type(tooltip_json, (lambda v: json_assert_type_string(v), lambda v: MarkupContent.from_json(json_assert_type_object(v))))
        else:
            tooltip = None
        if paddingLeft_json := json_get_optional_bool(obj, "paddingLeft"):
            paddingLeft = paddingLeft_json
        else:
            paddingLeft = None
        if paddingRight_json := json_get_optional_bool(obj, "paddingRight"):
            paddingRight = paddingRight_json
        else:
            paddingRight = None
        if data_json := obj.get("data"):
            data = parse_LSPAny(data_json)
        else:
            data = None
        return cls(position=position, label=label, kind=kind, textEdits=textEdits, tooltip=tooltip, paddingLeft=paddingLeft, paddingRight=paddingRight, data=data)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["position"] = self.position.to_json()
        out["label"] = write_or_type(self.label, (lambda i: isinstance(i, str), lambda i: isinstance(i, List) and (len(i) == 0 or (isinstance(i[0], InlayHintLabelPart)))), (lambda i: i, lambda i: [i.to_json() for i in i]))
        if self.kind is not None:
            out["kind"] = self.kind.value
        if self.textEdits is not None:
            out["textEdits"] = [i.to_json() for i in self.textEdits]
        if self.tooltip is not None:
            out["tooltip"] = write_or_type(self.tooltip, (lambda i: isinstance(i, str), lambda i: isinstance(i, MarkupContent)), (lambda i: i, lambda i: i.to_json()))
        if self.paddingLeft is not None:
            out["paddingLeft"] = self.paddingLeft
        if self.paddingRight is not None:
            out["paddingRight"] = self.paddingRight
        if self.data is not None:
            out["data"] = write_LSPAny(self.data)
        return out


@dataclass
class InlayHintOptions():
    """
    Inlay hint options used during static registration.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    workDoneProgress: Optional[bool]
    
    # The server provides support to resolve additional
    # information for an inlay hint item.
    resolveProvider: Optional[bool]

    def __init__(self, *, workDoneProgress: Optional[bool] = None, resolveProvider: Optional[bool] = None) -> None:
        """
        - resolveProvider: The server provides support to resolve additional
            information for an inlay hint item.
        """
        self.workDoneProgress = workDoneProgress
        self.resolveProvider = resolveProvider

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "InlayHintOptions":
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        if resolveProvider_json := json_get_optional_bool(obj, "resolveProvider"):
            resolveProvider = resolveProvider_json
        else:
            resolveProvider = None
        return cls(workDoneProgress=workDoneProgress, resolveProvider=resolveProvider)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        if self.resolveProvider is not None:
            out["resolveProvider"] = self.resolveProvider
        return out


@dataclass
class InlayHintRegistrationOptions(InlayHintOptions, TextDocumentRegistrationOptions):
    """
    Inlay hint options used during static or dynamic registration.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    workDoneProgress: Optional[bool]
    
    # The server provides support to resolve additional
    # information for an inlay hint item.
    resolveProvider: Optional[bool]
    
    # A document selector to identify the scope of the registration. If set to null
    # the document selector provided on the client side will be used.
    documentSelector: Union["DocumentSelector", None]
    
    # The id used to register the request. The id can be used to deregister
    # the request again. See also Registration#id.
    id: Optional[str]

    def __init__(self, *, workDoneProgress: Optional[bool] = None, resolveProvider: Optional[bool] = None, documentSelector: Union["DocumentSelector", None], id: Optional[str] = None) -> None:
        """
        - resolveProvider: The server provides support to resolve additional
            information for an inlay hint item.
        - documentSelector: A document selector to identify the scope of the registration. If set to null
            the document selector provided on the client side will be used.
        - id: The id used to register the request. The id can be used to deregister
            the request again. See also Registration#id.
        """
        self.workDoneProgress = workDoneProgress
        self.resolveProvider = resolveProvider
        self.documentSelector = documentSelector
        self.id = id

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "InlayHintRegistrationOptions":
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        if resolveProvider_json := json_get_optional_bool(obj, "resolveProvider"):
            resolveProvider = resolveProvider_json
        else:
            resolveProvider = None
        documentSelector = parse_or_type(obj["documentSelector"], (lambda v: parse_DocumentSelector(json_assert_type_array(v)), lambda v: json_assert_type_null(v)))
        if id_json := json_get_optional_string(obj, "id"):
            id = id_json
        else:
            id = None
        return cls(workDoneProgress=workDoneProgress, resolveProvider=resolveProvider, documentSelector=documentSelector, id=id)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        if self.resolveProvider is not None:
            out["resolveProvider"] = self.resolveProvider
        out["documentSelector"] = write_or_type(self.documentSelector, (lambda i: isinstance(i, List) and (len(i) == 0 or (((isinstance(i[0], Dict) and "language" in i[0].keys()) or (isinstance(i[0], Dict) and "scheme" in i[0].keys()) or (isinstance(i[0], Dict) and "pattern" in i[0].keys())) or (isinstance(i[0], NotebookCellTextDocumentFilter)))), lambda i: i is None), (lambda i: write_DocumentSelector(i), lambda i: i))
        if self.id is not None:
            out["id"] = self.id
        return out


@dataclass
class DocumentDiagnosticParams():
    """
    Parameters of the document diagnostic request.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]
    
    # An optional token that a server can use to report partial results (e.g. streaming) to
    # the client.
    partialResultToken: Optional["ProgressToken"]
    
    # The text document.
    textDocument: "TextDocumentIdentifier"
    
    # The additional identifier  provided during registration.
    identifier: Optional[str]
    
    # The result id of a previous response if provided.
    previousResultId: Optional[str]

    def __init__(self, *, workDoneToken: Optional["ProgressToken"] = None, partialResultToken: Optional["ProgressToken"] = None, textDocument: "TextDocumentIdentifier", identifier: Optional[str] = None, previousResultId: Optional[str] = None) -> None:
        """
        - workDoneToken: An optional token that a server can use to report work done progress.
        - partialResultToken: An optional token that a server can use to report partial results (e.g. streaming) to
            the client.
        - textDocument: The text document.
        - identifier: The additional identifier  provided during registration.
        - previousResultId: The result id of a previous response if provided.
        """
        self.workDoneToken = workDoneToken
        self.partialResultToken = partialResultToken
        self.textDocument = textDocument
        self.identifier = identifier
        self.previousResultId = previousResultId

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DocumentDiagnosticParams":
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        if partialResultToken_json := obj.get("partialResultToken"):
            partialResultToken = parse_ProgressToken(partialResultToken_json)
        else:
            partialResultToken = None
        textDocument = TextDocumentIdentifier.from_json(json_get_object(obj, "textDocument"))
        if identifier_json := json_get_optional_string(obj, "identifier"):
            identifier = identifier_json
        else:
            identifier = None
        if previousResultId_json := json_get_optional_string(obj, "previousResultId"):
            previousResultId = previousResultId_json
        else:
            previousResultId = None
        return cls(workDoneToken=workDoneToken, partialResultToken=partialResultToken, textDocument=textDocument, identifier=identifier, previousResultId=previousResultId)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        if self.partialResultToken is not None:
            out["partialResultToken"] = write_ProgressToken(self.partialResultToken)
        out["textDocument"] = self.textDocument.to_json()
        if self.identifier is not None:
            out["identifier"] = self.identifier
        if self.previousResultId is not None:
            out["previousResultId"] = self.previousResultId
        return out


@dataclass
class DocumentDiagnosticReportPartialResult():
    """
    A partial result for a document diagnostic report.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    relatedDocuments: Dict[str, Union["FullDocumentDiagnosticReport", "UnchangedDocumentDiagnosticReport"]]

    def __init__(self, *, relatedDocuments: Dict[str, Union["FullDocumentDiagnosticReport", "UnchangedDocumentDiagnosticReport"]]) -> None:
        """
    
        """
        self.relatedDocuments = relatedDocuments

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DocumentDiagnosticReportPartialResult":
        relatedDocuments = { json_assert_type_string(key): parse_or_type((value), (lambda v: FullDocumentDiagnosticReport.from_json(json_assert_type_object(v)), lambda v: UnchangedDocumentDiagnosticReport.from_json(json_assert_type_object(v)))) for key, value in json_get_object(obj, "relatedDocuments").items()}
        return cls(relatedDocuments=relatedDocuments)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["relatedDocuments"] = { key: write_or_type(val, (lambda i: isinstance(i, FullDocumentDiagnosticReport), lambda i: isinstance(i, UnchangedDocumentDiagnosticReport)), (lambda i: i.to_json(), lambda i: i.to_json())) for key, val in self.relatedDocuments.items() }
        return out


@dataclass
class DiagnosticServerCancellationData():
    """
    Cancellation data returned from a diagnostic request.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    retriggerRequest: bool

    def __init__(self, *, retriggerRequest: bool) -> None:
        """
    
        """
        self.retriggerRequest = retriggerRequest

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DiagnosticServerCancellationData":
        retriggerRequest = json_get_bool(obj, "retriggerRequest")
        return cls(retriggerRequest=retriggerRequest)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["retriggerRequest"] = self.retriggerRequest
        return out


@dataclass
class DiagnosticOptions():
    """
    Diagnostic options.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    workDoneProgress: Optional[bool]
    
    # An optional identifier under which the diagnostics are
    # managed by the client.
    identifier: Optional[str]
    
    # Whether the language has inter file dependencies meaning that
    # editing code in one file can result in a different diagnostic
    # set in another file. Inter file dependencies are common for
    # most programming languages and typically uncommon for linters.
    interFileDependencies: bool
    
    # The server provides support for workspace diagnostics as well.
    workspaceDiagnostics: bool

    def __init__(self, *, workDoneProgress: Optional[bool] = None, identifier: Optional[str] = None, interFileDependencies: bool, workspaceDiagnostics: bool) -> None:
        """
        - identifier: An optional identifier under which the diagnostics are
            managed by the client.
        - interFileDependencies: Whether the language has inter file dependencies meaning that
            editing code in one file can result in a different diagnostic
            set in another file. Inter file dependencies are common for
            most programming languages and typically uncommon for linters.
        - workspaceDiagnostics: The server provides support for workspace diagnostics as well.
        """
        self.workDoneProgress = workDoneProgress
        self.identifier = identifier
        self.interFileDependencies = interFileDependencies
        self.workspaceDiagnostics = workspaceDiagnostics

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DiagnosticOptions":
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        if identifier_json := json_get_optional_string(obj, "identifier"):
            identifier = identifier_json
        else:
            identifier = None
        interFileDependencies = json_get_bool(obj, "interFileDependencies")
        workspaceDiagnostics = json_get_bool(obj, "workspaceDiagnostics")
        return cls(workDoneProgress=workDoneProgress, identifier=identifier, interFileDependencies=interFileDependencies, workspaceDiagnostics=workspaceDiagnostics)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        if self.identifier is not None:
            out["identifier"] = self.identifier
        out["interFileDependencies"] = self.interFileDependencies
        out["workspaceDiagnostics"] = self.workspaceDiagnostics
        return out


@dataclass
class DiagnosticRegistrationOptions(TextDocumentRegistrationOptions, DiagnosticOptions):
    """
    Diagnostic registration options.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # A document selector to identify the scope of the registration. If set to null
    # the document selector provided on the client side will be used.
    documentSelector: Union["DocumentSelector", None]
    
    workDoneProgress: Optional[bool]
    
    # An optional identifier under which the diagnostics are
    # managed by the client.
    identifier: Optional[str]
    
    # Whether the language has inter file dependencies meaning that
    # editing code in one file can result in a different diagnostic
    # set in another file. Inter file dependencies are common for
    # most programming languages and typically uncommon for linters.
    interFileDependencies: bool
    
    # The server provides support for workspace diagnostics as well.
    workspaceDiagnostics: bool
    
    # The id used to register the request. The id can be used to deregister
    # the request again. See also Registration#id.
    id: Optional[str]

    def __init__(self, *, documentSelector: Union["DocumentSelector", None], workDoneProgress: Optional[bool] = None, identifier: Optional[str] = None, interFileDependencies: bool, workspaceDiagnostics: bool, id: Optional[str] = None) -> None:
        """
        - documentSelector: A document selector to identify the scope of the registration. If set to null
            the document selector provided on the client side will be used.
        - identifier: An optional identifier under which the diagnostics are
            managed by the client.
        - interFileDependencies: Whether the language has inter file dependencies meaning that
            editing code in one file can result in a different diagnostic
            set in another file. Inter file dependencies are common for
            most programming languages and typically uncommon for linters.
        - workspaceDiagnostics: The server provides support for workspace diagnostics as well.
        - id: The id used to register the request. The id can be used to deregister
            the request again. See also Registration#id.
        """
        self.documentSelector = documentSelector
        self.workDoneProgress = workDoneProgress
        self.identifier = identifier
        self.interFileDependencies = interFileDependencies
        self.workspaceDiagnostics = workspaceDiagnostics
        self.id = id

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DiagnosticRegistrationOptions":
        documentSelector = parse_or_type(obj["documentSelector"], (lambda v: parse_DocumentSelector(json_assert_type_array(v)), lambda v: json_assert_type_null(v)))
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        if identifier_json := json_get_optional_string(obj, "identifier"):
            identifier = identifier_json
        else:
            identifier = None
        interFileDependencies = json_get_bool(obj, "interFileDependencies")
        workspaceDiagnostics = json_get_bool(obj, "workspaceDiagnostics")
        if id_json := json_get_optional_string(obj, "id"):
            id = id_json
        else:
            id = None
        return cls(documentSelector=documentSelector, workDoneProgress=workDoneProgress, identifier=identifier, interFileDependencies=interFileDependencies, workspaceDiagnostics=workspaceDiagnostics, id=id)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["documentSelector"] = write_or_type(self.documentSelector, (lambda i: isinstance(i, List) and (len(i) == 0 or (((isinstance(i[0], Dict) and "language" in i[0].keys()) or (isinstance(i[0], Dict) and "scheme" in i[0].keys()) or (isinstance(i[0], Dict) and "pattern" in i[0].keys())) or (isinstance(i[0], NotebookCellTextDocumentFilter)))), lambda i: i is None), (lambda i: write_DocumentSelector(i), lambda i: i))
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        if self.identifier is not None:
            out["identifier"] = self.identifier
        out["interFileDependencies"] = self.interFileDependencies
        out["workspaceDiagnostics"] = self.workspaceDiagnostics
        if self.id is not None:
            out["id"] = self.id
        return out


@dataclass
class PreviousResultId():
    """
    A previous result id in a workspace pull request.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # The URI for which the client knowns a
    # result id.
    uri: str
    
    # The value of the previous result id.
    value: str

    def __init__(self, *, uri: str, value: str) -> None:
        """
        - uri: The URI for which the client knowns a
            result id.
        - value: The value of the previous result id.
        """
        self.uri = uri
        self.value = value

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "PreviousResultId":
        uri = json_get_string(obj, "uri")
        value = json_get_string(obj, "value")
        return cls(uri=uri, value=value)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["uri"] = self.uri
        out["value"] = self.value
        return out


@dataclass
class WorkspaceDiagnosticParams():
    """
    Parameters of the workspace diagnostic request.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]
    
    # An optional token that a server can use to report partial results (e.g. streaming) to
    # the client.
    partialResultToken: Optional["ProgressToken"]
    
    # The additional identifier provided during registration.
    identifier: Optional[str]
    
    # The currently known diagnostic reports with their
    # previous result ids.
    previousResultIds: List["PreviousResultId"]

    def __init__(self, *, workDoneToken: Optional["ProgressToken"] = None, partialResultToken: Optional["ProgressToken"] = None, identifier: Optional[str] = None, previousResultIds: List["PreviousResultId"]) -> None:
        """
        - workDoneToken: An optional token that a server can use to report work done progress.
        - partialResultToken: An optional token that a server can use to report partial results (e.g. streaming) to
            the client.
        - identifier: The additional identifier provided during registration.
        - previousResultIds: The currently known diagnostic reports with their
            previous result ids.
        """
        self.workDoneToken = workDoneToken
        self.partialResultToken = partialResultToken
        self.identifier = identifier
        self.previousResultIds = previousResultIds

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "WorkspaceDiagnosticParams":
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        if partialResultToken_json := obj.get("partialResultToken"):
            partialResultToken = parse_ProgressToken(partialResultToken_json)
        else:
            partialResultToken = None
        if identifier_json := json_get_optional_string(obj, "identifier"):
            identifier = identifier_json
        else:
            identifier = None
        previousResultIds = [PreviousResultId.from_json(json_assert_type_object(i)) for i in json_get_array(obj, "previousResultIds")]
        return cls(workDoneToken=workDoneToken, partialResultToken=partialResultToken, identifier=identifier, previousResultIds=previousResultIds)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        if self.partialResultToken is not None:
            out["partialResultToken"] = write_ProgressToken(self.partialResultToken)
        if self.identifier is not None:
            out["identifier"] = self.identifier
        out["previousResultIds"] = [i.to_json() for i in self.previousResultIds]
        return out


@dataclass
class CodeDescription():
    """
    Structure to capture a description for an error code.
    
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # An URI to open with more information about the diagnostic error.
    href: str

    def __init__(self, *, href: str) -> None:
        """
        - href: An URI to open with more information about the diagnostic error.
        """
        self.href = href

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "CodeDescription":
        href = json_get_string(obj, "href")
        return cls(href=href)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["href"] = self.href
        return out


@dataclass
class DiagnosticRelatedInformation():
    """
    Represents a related message and source code location for a diagnostic. This should be
    used to point to code locations that cause or related to a diagnostics, e.g when duplicating
    a symbol in a scope.

    *Generated from the TypeScript documentation*
    """

    # The location of this related diagnostic information.
    location: "Location"
    
    # The message of this related diagnostic information.
    message: str

    def __init__(self, *, location: "Location", message: str) -> None:
        """
        - location: The location of this related diagnostic information.
        - message: The message of this related diagnostic information.
        """
        self.location = location
        self.message = message

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DiagnosticRelatedInformation":
        location = Location.from_json(json_get_object(obj, "location"))
        message = json_get_string(obj, "message")
        return cls(location=location, message=message)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["location"] = self.location.to_json()
        out["message"] = self.message
        return out


@dataclass
class Diagnostic():
    """
    Represents a diagnostic, such as a compiler error or warning. Diagnostic objects
    are only valid in the scope of a resource.

    *Generated from the TypeScript documentation*
    """

    # The range at which the message applies
    range: "Range"
    
    # The diagnostic's severity. Can be omitted. If omitted it is up to the
    # client to interpret diagnostics as error, warning, info or hint.
    severity: Optional["DiagnosticSeverity"]
    
    # The diagnostic's code, which usually appear in the user interface.
    code: Optional[Union[int, str]]
    
    # An optional property to describe the error code.
    # Requires the code field (above) to be present/not null.
    # 
    # @since 3.16.0
    codeDescription: Optional["CodeDescription"]
    
    # A human-readable string describing the source of this
    # diagnostic, e.g. 'typescript' or 'super lint'. It usually
    # appears in the user interface.
    source: Optional[str]
    
    # The diagnostic's message. It usually appears in the user interface
    message: str
    
    # Additional metadata about the diagnostic.
    # 
    # @since 3.15.0
    tags: Optional[List["DiagnosticTag"]]
    
    # An array of related diagnostic information, e.g. when symbol-names within
    # a scope collide all definitions can be marked via this property.
    relatedInformation: Optional[List["DiagnosticRelatedInformation"]]
    
    # A data entry field that is preserved between a `textDocument/publishDiagnostics`
    # notification and `textDocument/codeAction` request.
    # 
    # @since 3.16.0
    data: Optional["LSPAny"]

    def __init__(self, *, range: "Range", severity: Optional["DiagnosticSeverity"] = None, code: Optional[Union[int, str]] = None, codeDescription: Optional["CodeDescription"] = None, source: Optional[str] = None, message: str, tags: Optional[List["DiagnosticTag"]] = None, relatedInformation: Optional[List["DiagnosticRelatedInformation"]] = None, data: Optional["LSPAny"] = None) -> None:
        """
        - range: The range at which the message applies
        - severity: The diagnostic's severity. Can be omitted. If omitted it is up to the
            client to interpret diagnostics as error, warning, info or hint.
        - code: The diagnostic's code, which usually appear in the user interface.
        - codeDescription: An optional property to describe the error code.
            Requires the code field (above) to be present/not null.
            
            @since 3.16.0
        - source: A human-readable string describing the source of this
            diagnostic, e.g. 'typescript' or 'super lint'. It usually
            appears in the user interface.
        - message: The diagnostic's message. It usually appears in the user interface
        - tags: Additional metadata about the diagnostic.
            
            @since 3.15.0
        - relatedInformation: An array of related diagnostic information, e.g. when symbol-names within
            a scope collide all definitions can be marked via this property.
        - data: A data entry field that is preserved between a `textDocument/publishDiagnostics`
            notification and `textDocument/codeAction` request.
            
            @since 3.16.0
        """
        self.range = range
        self.severity = severity
        self.code = code
        self.codeDescription = codeDescription
        self.source = source
        self.message = message
        self.tags = tags
        self.relatedInformation = relatedInformation
        self.data = data

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "Diagnostic":
        range = Range.from_json(json_get_object(obj, "range"))
        if severity_json := json_get_optional_int(obj, "severity"):
            severity = DiagnosticSeverity(severity_json)
        else:
            severity = None
        if code_json := obj.get("code"):
            code = parse_or_type(code_json, (lambda v: json_assert_type_int(v), lambda v: json_assert_type_string(v)))
        else:
            code = None
        if codeDescription_json := json_get_optional_object(obj, "codeDescription"):
            codeDescription = CodeDescription.from_json(codeDescription_json)
        else:
            codeDescription = None
        if source_json := json_get_optional_string(obj, "source"):
            source = source_json
        else:
            source = None
        message = json_get_string(obj, "message")
        if tags_json := json_get_optional_array(obj, "tags"):
            tags = [DiagnosticTag(json_assert_type_int(i)) for i in tags_json]
        else:
            tags = None
        if relatedInformation_json := json_get_optional_array(obj, "relatedInformation"):
            relatedInformation = [DiagnosticRelatedInformation.from_json(json_assert_type_object(i)) for i in relatedInformation_json]
        else:
            relatedInformation = None
        if data_json := obj.get("data"):
            data = parse_LSPAny(data_json)
        else:
            data = None
        return cls(range=range, severity=severity, code=code, codeDescription=codeDescription, source=source, message=message, tags=tags, relatedInformation=relatedInformation, data=data)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["range"] = self.range.to_json()
        if self.severity is not None:
            out["severity"] = self.severity.value
        if self.code is not None:
            out["code"] = write_or_type(self.code, (lambda i: isinstance(i, int), lambda i: isinstance(i, str)), (lambda i: i, lambda i: i))
        if self.codeDescription is not None:
            out["codeDescription"] = self.codeDescription.to_json()
        if self.source is not None:
            out["source"] = self.source
        out["message"] = self.message
        if self.tags is not None:
            out["tags"] = [i.value for i in self.tags]
        if self.relatedInformation is not None:
            out["relatedInformation"] = [i.to_json() for i in self.relatedInformation]
        if self.data is not None:
            out["data"] = write_LSPAny(self.data)
        return out


@dataclass
class FullDocumentDiagnosticReport():
    """
    A diagnostic report with a full set of problems.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # A full document diagnostic report.
    kind: str
    
    # An optional result id. If provided it will
    # be sent on the next diagnostic request for the
    # same document.
    resultId: Optional[str]
    
    # The actual items.
    items: List["Diagnostic"]

    def __init__(self, *, kind: str, resultId: Optional[str] = None, items: List["Diagnostic"]) -> None:
        """
        - kind: A full document diagnostic report.
        - resultId: An optional result id. If provided it will
            be sent on the next diagnostic request for the
            same document.
        - items: The actual items.
        """
        self.kind = kind
        self.resultId = resultId
        self.items = items

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "FullDocumentDiagnosticReport":
        kind = match_string(json_get_string(obj, "kind"), "full")
        if resultId_json := json_get_optional_string(obj, "resultId"):
            resultId = resultId_json
        else:
            resultId = None
        items = [Diagnostic.from_json(json_assert_type_object(i)) for i in json_get_array(obj, "items")]
        return cls(kind=kind, resultId=resultId, items=items)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["kind"] = "full"
        if self.resultId is not None:
            out["resultId"] = self.resultId
        out["items"] = [i.to_json() for i in self.items]
        return out


@dataclass
class WorkspaceFullDocumentDiagnosticReport(FullDocumentDiagnosticReport):
    """
    A full document diagnostic report for a workspace diagnostic result.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # A full document diagnostic report.
    kind: str
    
    # An optional result id. If provided it will
    # be sent on the next diagnostic request for the
    # same document.
    resultId: Optional[str]
    
    # The actual items.
    items: List["Diagnostic"]
    
    # The URI for which diagnostic information is reported.
    uri: str
    
    # The version number for which the diagnostics are reported.
    # If the document is not marked as open `null` can be provided.
    version: Union[int, None]

    def __init__(self, *, kind: str, resultId: Optional[str] = None, items: List["Diagnostic"], uri: str, version: Union[int, None]) -> None:
        """
        - kind: A full document diagnostic report.
        - resultId: An optional result id. If provided it will
            be sent on the next diagnostic request for the
            same document.
        - items: The actual items.
        - uri: The URI for which diagnostic information is reported.
        - version: The version number for which the diagnostics are reported.
            If the document is not marked as open `null` can be provided.
        """
        self.kind = kind
        self.resultId = resultId
        self.items = items
        self.uri = uri
        self.version = version

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "WorkspaceFullDocumentDiagnosticReport":
        kind = match_string(json_get_string(obj, "kind"), "full")
        if resultId_json := json_get_optional_string(obj, "resultId"):
            resultId = resultId_json
        else:
            resultId = None
        items = [Diagnostic.from_json(json_assert_type_object(i)) for i in json_get_array(obj, "items")]
        uri = json_get_string(obj, "uri")
        version = parse_or_type(obj["version"], (lambda v: json_assert_type_int(v), lambda v: json_assert_type_null(v)))
        return cls(kind=kind, resultId=resultId, items=items, uri=uri, version=version)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["kind"] = "full"
        if self.resultId is not None:
            out["resultId"] = self.resultId
        out["items"] = [i.to_json() for i in self.items]
        out["uri"] = self.uri
        out["version"] = write_or_type(self.version, (lambda i: isinstance(i, int), lambda i: i is None), (lambda i: i, lambda i: i))
        return out


@dataclass
class UnchangedDocumentDiagnosticReport():
    """
    A diagnostic report indicating that the last returned
    report is still accurate.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # A document diagnostic report indicating
    # no changes to the last result. A server can
    # only return `unchanged` if result ids are
    # provided.
    kind: str
    
    # A result id which will be sent on the next
    # diagnostic request for the same document.
    resultId: str

    def __init__(self, *, kind: str, resultId: str) -> None:
        """
        - kind: A document diagnostic report indicating
            no changes to the last result. A server can
            only return `unchanged` if result ids are
            provided.
        - resultId: A result id which will be sent on the next
            diagnostic request for the same document.
        """
        self.kind = kind
        self.resultId = resultId

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "UnchangedDocumentDiagnosticReport":
        kind = match_string(json_get_string(obj, "kind"), "unchanged")
        resultId = json_get_string(obj, "resultId")
        return cls(kind=kind, resultId=resultId)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["kind"] = "unchanged"
        out["resultId"] = self.resultId
        return out


@dataclass
class WorkspaceUnchangedDocumentDiagnosticReport(UnchangedDocumentDiagnosticReport):
    """
    An unchanged document diagnostic report for a workspace diagnostic result.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # A document diagnostic report indicating
    # no changes to the last result. A server can
    # only return `unchanged` if result ids are
    # provided.
    kind: str
    
    # A result id which will be sent on the next
    # diagnostic request for the same document.
    resultId: str
    
    # The URI for which diagnostic information is reported.
    uri: str
    
    # The version number for which the diagnostics are reported.
    # If the document is not marked as open `null` can be provided.
    version: Union[int, None]

    def __init__(self, *, kind: str, resultId: str, uri: str, version: Union[int, None]) -> None:
        """
        - kind: A document diagnostic report indicating
            no changes to the last result. A server can
            only return `unchanged` if result ids are
            provided.
        - resultId: A result id which will be sent on the next
            diagnostic request for the same document.
        - uri: The URI for which diagnostic information is reported.
        - version: The version number for which the diagnostics are reported.
            If the document is not marked as open `null` can be provided.
        """
        self.kind = kind
        self.resultId = resultId
        self.uri = uri
        self.version = version

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "WorkspaceUnchangedDocumentDiagnosticReport":
        kind = match_string(json_get_string(obj, "kind"), "unchanged")
        resultId = json_get_string(obj, "resultId")
        uri = json_get_string(obj, "uri")
        version = parse_or_type(obj["version"], (lambda v: json_assert_type_int(v), lambda v: json_assert_type_null(v)))
        return cls(kind=kind, resultId=resultId, uri=uri, version=version)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["kind"] = "unchanged"
        out["resultId"] = self.resultId
        out["uri"] = self.uri
        out["version"] = write_or_type(self.version, (lambda i: isinstance(i, int), lambda i: i is None), (lambda i: i, lambda i: i))
        return out


# A workspace diagnostic document report.
# 
# @since 3.17.0
WorkspaceDocumentDiagnosticReport = Union["WorkspaceFullDocumentDiagnosticReport", "WorkspaceUnchangedDocumentDiagnosticReport"]

def parse_WorkspaceDocumentDiagnosticReport(arg: JSON_VALUE) -> WorkspaceDocumentDiagnosticReport:
    return parse_or_type((arg), (lambda v: WorkspaceFullDocumentDiagnosticReport.from_json(json_assert_type_object(v)), lambda v: WorkspaceUnchangedDocumentDiagnosticReport.from_json(json_assert_type_object(v))))

def write_WorkspaceDocumentDiagnosticReport(arg: WorkspaceDocumentDiagnosticReport) -> JSON_VALUE:
    return write_or_type(arg, (lambda i: isinstance(i, WorkspaceFullDocumentDiagnosticReport), lambda i: isinstance(i, WorkspaceUnchangedDocumentDiagnosticReport)), (lambda i: i.to_json(), lambda i: i.to_json()))


@dataclass
class WorkspaceDiagnosticReport():
    """
    A workspace diagnostic report.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    items: List["WorkspaceDocumentDiagnosticReport"]

    def __init__(self, *, items: List["WorkspaceDocumentDiagnosticReport"]) -> None:
        """
    
        """
        self.items = items

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "WorkspaceDiagnosticReport":
        items = [parse_WorkspaceDocumentDiagnosticReport((i)) for i in json_get_array(obj, "items")]
        return cls(items=items)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["items"] = [write_WorkspaceDocumentDiagnosticReport(i) for i in self.items]
        return out


@dataclass
class WorkspaceDiagnosticReportPartialResult():
    """
    A partial result for a workspace diagnostic report.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    items: List["WorkspaceDocumentDiagnosticReport"]

    def __init__(self, *, items: List["WorkspaceDocumentDiagnosticReport"]) -> None:
        """
    
        """
        self.items = items

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "WorkspaceDiagnosticReportPartialResult":
        items = [parse_WorkspaceDocumentDiagnosticReport((i)) for i in json_get_array(obj, "items")]
        return cls(items=items)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["items"] = [write_WorkspaceDocumentDiagnosticReport(i) for i in self.items]
        return out


@dataclass
class ExecutionSummary():
    """


    *Generated from the TypeScript documentation*
    """

    # A strict monotonically increasing value
    # indicating the execution order of a cell
    # inside a notebook.
    executionOrder: int
    
    # Whether the execution was successful or
    # not if known by the client.
    success: Optional[bool]

    def __init__(self, *, executionOrder: int, success: Optional[bool] = None) -> None:
        """
        - executionOrder: A strict monotonically increasing value
            indicating the execution order of a cell
            inside a notebook.
        - success: Whether the execution was successful or
            not if known by the client.
        """
        self.executionOrder = executionOrder
        self.success = success

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "ExecutionSummary":
        executionOrder = json_get_int(obj, "executionOrder")
        if success_json := json_get_optional_bool(obj, "success"):
            success = success_json
        else:
            success = None
        return cls(executionOrder=executionOrder, success=success)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["executionOrder"] = self.executionOrder
        if self.success is not None:
            out["success"] = self.success
        return out


@dataclass
class NotebookCell():
    """
    A notebook cell.
    
    A cell's document URI must be unique across ALL notebook
    cells and can therefore be used to uniquely identify a
    notebook cell or the cell's text document.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # The cell's kind
    kind: "NotebookCellKind"
    
    # The URI of the cell's text document
    # content.
    document: str
    
    # Additional metadata stored with the cell.
    # 
    # Note: should always be an object literal (e.g. LSPObject)
    metadata: Optional["LSPObject"]
    
    # Additional execution summary information
    # if supported by the client.
    executionSummary: Optional["ExecutionSummary"]

    def __init__(self, *, kind: "NotebookCellKind", document: str, metadata: Optional["LSPObject"] = None, executionSummary: Optional["ExecutionSummary"] = None) -> None:
        """
        - kind: The cell's kind
        - document: The URI of the cell's text document
            content.
        - metadata: Additional metadata stored with the cell.
            
            Note: should always be an object literal (e.g. LSPObject)
        - executionSummary: Additional execution summary information
            if supported by the client.
        """
        self.kind = kind
        self.document = document
        self.metadata = metadata
        self.executionSummary = executionSummary

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "NotebookCell":
        kind = NotebookCellKind(json_get_int(obj, "kind"))
        document = json_get_string(obj, "document")
        if metadata_json := json_get_optional_object(obj, "metadata"):
            metadata = LSPObject.from_json(metadata_json)
        else:
            metadata = None
        if executionSummary_json := json_get_optional_object(obj, "executionSummary"):
            executionSummary = ExecutionSummary.from_json(executionSummary_json)
        else:
            executionSummary = None
        return cls(kind=kind, document=document, metadata=metadata, executionSummary=executionSummary)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["kind"] = self.kind.value
        out["document"] = self.document
        if self.metadata is not None:
            out["metadata"] = self.metadata.to_json()
        if self.executionSummary is not None:
            out["executionSummary"] = self.executionSummary.to_json()
        return out


@dataclass
class NotebookDocument():
    """
    A notebook document.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # The notebook document's uri.
    uri: str
    
    # The type of the notebook.
    notebookType: str
    
    # The version number of this document (it will increase after each
    # change, including undo/redo).
    version: int
    
    # Additional metadata stored with the notebook
    # document.
    # 
    # Note: should always be an object literal (e.g. LSPObject)
    metadata: Optional["LSPObject"]
    
    # The cells of a notebook.
    cells: List["NotebookCell"]

    def __init__(self, *, uri: str, notebookType: str, version: int, metadata: Optional["LSPObject"] = None, cells: List["NotebookCell"]) -> None:
        """
        - uri: The notebook document's uri.
        - notebookType: The type of the notebook.
        - version: The version number of this document (it will increase after each
            change, including undo/redo).
        - metadata: Additional metadata stored with the notebook
            document.
            
            Note: should always be an object literal (e.g. LSPObject)
        - cells: The cells of a notebook.
        """
        self.uri = uri
        self.notebookType = notebookType
        self.version = version
        self.metadata = metadata
        self.cells = cells

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "NotebookDocument":
        uri = json_get_string(obj, "uri")
        notebookType = json_get_string(obj, "notebookType")
        version = json_get_int(obj, "version")
        if metadata_json := json_get_optional_object(obj, "metadata"):
            metadata = LSPObject.from_json(metadata_json)
        else:
            metadata = None
        cells = [NotebookCell.from_json(json_assert_type_object(i)) for i in json_get_array(obj, "cells")]
        return cls(uri=uri, notebookType=notebookType, version=version, metadata=metadata, cells=cells)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["uri"] = self.uri
        out["notebookType"] = self.notebookType
        out["version"] = self.version
        if self.metadata is not None:
            out["metadata"] = self.metadata.to_json()
        out["cells"] = [i.to_json() for i in self.cells]
        return out


@dataclass
class TextDocumentItem():
    """
    An item to transfer a text document from the client to the
    server.

    *Generated from the TypeScript documentation*
    """

    # The text document's uri.
    uri: str
    
    # The text document's language identifier.
    languageId: str
    
    # The version number of this document (it will increase after each
    # change, including undo/redo).
    version: int
    
    # The content of the opened text document.
    text: str

    def __init__(self, *, uri: str, languageId: str, version: int, text: str) -> None:
        """
        - uri: The text document's uri.
        - languageId: The text document's language identifier.
        - version: The version number of this document (it will increase after each
            change, including undo/redo).
        - text: The content of the opened text document.
        """
        self.uri = uri
        self.languageId = languageId
        self.version = version
        self.text = text

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "TextDocumentItem":
        uri = json_get_string(obj, "uri")
        languageId = json_get_string(obj, "languageId")
        version = json_get_int(obj, "version")
        text = json_get_string(obj, "text")
        return cls(uri=uri, languageId=languageId, version=version, text=text)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["uri"] = self.uri
        out["languageId"] = self.languageId
        out["version"] = self.version
        out["text"] = self.text
        return out


@dataclass
class DidOpenNotebookDocumentParams():
    """
    The params sent in an open notebook document notification.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # The notebook document that got opened.
    notebookDocument: "NotebookDocument"
    
    # The text documents that represent the content
    # of a notebook cell.
    cellTextDocuments: List["TextDocumentItem"]

    def __init__(self, *, notebookDocument: "NotebookDocument", cellTextDocuments: List["TextDocumentItem"]) -> None:
        """
        - notebookDocument: The notebook document that got opened.
        - cellTextDocuments: The text documents that represent the content
            of a notebook cell.
        """
        self.notebookDocument = notebookDocument
        self.cellTextDocuments = cellTextDocuments

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DidOpenNotebookDocumentParams":
        notebookDocument = NotebookDocument.from_json(json_get_object(obj, "notebookDocument"))
        cellTextDocuments = [TextDocumentItem.from_json(json_assert_type_object(i)) for i in json_get_array(obj, "cellTextDocuments")]
        return cls(notebookDocument=notebookDocument, cellTextDocuments=cellTextDocuments)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["notebookDocument"] = self.notebookDocument.to_json()
        out["cellTextDocuments"] = [i.to_json() for i in self.cellTextDocuments]
        return out


@dataclass
class VersionedNotebookDocumentIdentifier():
    """
    A versioned notebook document identifier.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # The version number of this notebook document.
    version: int
    
    # The notebook document's uri.
    uri: str

    def __init__(self, *, version: int, uri: str) -> None:
        """
        - version: The version number of this notebook document.
        - uri: The notebook document's uri.
        """
        self.version = version
        self.uri = uri

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "VersionedNotebookDocumentIdentifier":
        version = json_get_int(obj, "version")
        uri = json_get_string(obj, "uri")
        return cls(version=version, uri=uri)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["version"] = self.version
        out["uri"] = self.uri
        return out


@dataclass
class NotebookCellArrayChange():
    """
    A change describing how to move a `NotebookCell`
    array from state S to S'.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # The start oftest of the cell that changed.
    start: int
    
    # The deleted cells
    deleteCount: int
    
    # The new cells, if any
    cells: Optional[List["NotebookCell"]]

    def __init__(self, *, start: int, deleteCount: int, cells: Optional[List["NotebookCell"]] = None) -> None:
        """
        - start: The start oftest of the cell that changed.
        - deleteCount: The deleted cells
        - cells: The new cells, if any
        """
        self.start = start
        self.deleteCount = deleteCount
        self.cells = cells

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "NotebookCellArrayChange":
        start = json_get_int(obj, "start")
        deleteCount = json_get_int(obj, "deleteCount")
        if cells_json := json_get_optional_array(obj, "cells"):
            cells = [NotebookCell.from_json(json_assert_type_object(i)) for i in cells_json]
        else:
            cells = None
        return cls(start=start, deleteCount=deleteCount, cells=cells)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["start"] = self.start
        out["deleteCount"] = self.deleteCount
        if self.cells is not None:
            out["cells"] = [i.to_json() for i in self.cells]
        return out


AnonymousStructure7Keys = Literal["array","didOpen","didClose"]

def parse_AnonymousStructure7(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure7Keys, Any]:
    out: Dict[AnonymousStructure7Keys, Any] = {}
    out["array"] = NotebookCellArrayChange.from_json(json_get_object(obj, "array"))
    if didOpen_json := json_get_optional_array(obj, "didOpen"):
        out["didOpen"] = [TextDocumentItem.from_json(json_assert_type_object(i)) for i in didOpen_json]
    else:
        out["didOpen"] = None
    if didClose_json := json_get_optional_array(obj, "didClose"):
        out["didClose"] = [TextDocumentIdentifier.from_json(json_assert_type_object(i)) for i in didClose_json]
    else:
        out["didClose"] = None
    return out

def write_AnonymousStructure7(obj: Dict[AnonymousStructure7Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    out["array"] = obj["array"].to_json()
    if obj.get("didOpen") is not None:
        out["didOpen"] = [i.to_json() for i in obj.get("didOpen")]
    if obj.get("didClose") is not None:
        out["didClose"] = [i.to_json() for i in obj.get("didClose")]
    return out


@dataclass
class VersionedTextDocumentIdentifier(TextDocumentIdentifier):
    """
    A text document identifier to denote a specific version of a text document.

    *Generated from the TypeScript documentation*
    """

    # The text document's uri.
    uri: str
    
    # The version number of this document.
    version: int

    def __init__(self, *, uri: str, version: int) -> None:
        """
        - uri: The text document's uri.
        - version: The version number of this document.
        """
        self.uri = uri
        self.version = version

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "VersionedTextDocumentIdentifier":
        uri = json_get_string(obj, "uri")
        version = json_get_int(obj, "version")
        return cls(uri=uri, version=version)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["uri"] = self.uri
        out["version"] = self.version
        return out


AnonymousStructure39Keys = Literal["range","rangeLength","text"]

def parse_AnonymousStructure39(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure39Keys, Any]:
    out: Dict[AnonymousStructure39Keys, Any] = {}
    out["range"] = Range.from_json(json_get_object(obj, "range"))
    if rangeLength_json := json_get_optional_int(obj, "rangeLength"):
        out["rangeLength"] = rangeLength_json
    else:
        out["rangeLength"] = None
    out["text"] = json_get_string(obj, "text")
    return out

def write_AnonymousStructure39(obj: Dict[AnonymousStructure39Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    out["range"] = obj["range"].to_json()
    if obj.get("rangeLength") is not None:
        out["rangeLength"] = obj.get("rangeLength")
    out["text"] = obj["text"]
    return out


AnonymousStructure40Keys = Literal["text"]

def parse_AnonymousStructure40(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure40Keys, Any]:
    out: Dict[AnonymousStructure40Keys, Any] = {}
    out["text"] = json_get_string(obj, "text")
    return out

def write_AnonymousStructure40(obj: Dict[AnonymousStructure40Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    out["text"] = obj["text"]
    return out


# An event describing a change to a text document. If only a text is provided
# it is considered to be the full content of the document.
TextDocumentContentChangeEvent = Union[Dict[AnonymousStructure39Keys, Any], Dict[AnonymousStructure40Keys, Any]]

def parse_TextDocumentContentChangeEvent(arg: JSON_VALUE) -> TextDocumentContentChangeEvent:
    return parse_or_type((arg), (lambda v: parse_AnonymousStructure39(json_assert_type_object(v)), lambda v: parse_AnonymousStructure40(json_assert_type_object(v))))

def write_TextDocumentContentChangeEvent(arg: TextDocumentContentChangeEvent) -> JSON_VALUE:
    return write_or_type(arg, (lambda i: isinstance(i, Dict) and "range" in i.keys() and "text" in i.keys(), lambda i: isinstance(i, Dict) and "text" in i.keys()), (lambda i: write_AnonymousStructure39(i), lambda i: write_AnonymousStructure40(i)))


AnonymousStructure8Keys = Literal["document","changes"]

def parse_AnonymousStructure8(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure8Keys, Any]:
    out: Dict[AnonymousStructure8Keys, Any] = {}
    out["document"] = VersionedTextDocumentIdentifier.from_json(json_get_object(obj, "document"))
    out["changes"] = [parse_TextDocumentContentChangeEvent((i)) for i in json_get_array(obj, "changes")]
    return out

def write_AnonymousStructure8(obj: Dict[AnonymousStructure8Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    out["document"] = obj["document"].to_json()
    out["changes"] = [write_TextDocumentContentChangeEvent(i) for i in obj["changes"]]
    return out


AnonymousStructure9Keys = Literal["structure","data","textContent"]

def parse_AnonymousStructure9(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure9Keys, Any]:
    out: Dict[AnonymousStructure9Keys, Any] = {}
    if structure_json := json_get_optional_object(obj, "structure"):
        out["structure"] = parse_AnonymousStructure7(structure_json)
    else:
        out["structure"] = None
    if data_json := json_get_optional_array(obj, "data"):
        out["data"] = [NotebookCell.from_json(json_assert_type_object(i)) for i in data_json]
    else:
        out["data"] = None
    if textContent_json := json_get_optional_array(obj, "textContent"):
        out["textContent"] = [parse_AnonymousStructure8(json_assert_type_object(i)) for i in textContent_json]
    else:
        out["textContent"] = None
    return out

def write_AnonymousStructure9(obj: Dict[AnonymousStructure9Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    if obj.get("structure") is not None:
        out["structure"] = write_AnonymousStructure7(obj.get("structure"))
    if obj.get("data") is not None:
        out["data"] = [i.to_json() for i in obj.get("data")]
    if obj.get("textContent") is not None:
        out["textContent"] = [write_AnonymousStructure8(i) for i in obj.get("textContent")]
    return out


@dataclass
class NotebookDocumentChangeEvent():
    """
    A change event for a notebook document.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # The changed meta data if any.
    # 
    # Note: should always be an object literal (e.g. LSPObject)
    metadata: Optional["LSPObject"]
    
    # Changes to cells
    cells: Optional[Dict[AnonymousStructure9Keys, Any]]

    def __init__(self, *, metadata: Optional["LSPObject"] = None, cells: Optional[Dict[AnonymousStructure9Keys, Any]] = None) -> None:
        """
        - metadata: The changed meta data if any.
            
            Note: should always be an object literal (e.g. LSPObject)
        - cells: Changes to cells
        """
        self.metadata = metadata
        self.cells = cells

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "NotebookDocumentChangeEvent":
        if metadata_json := json_get_optional_object(obj, "metadata"):
            metadata = LSPObject.from_json(metadata_json)
        else:
            metadata = None
        if cells_json := json_get_optional_object(obj, "cells"):
            cells = parse_AnonymousStructure9(cells_json)
        else:
            cells = None
        return cls(metadata=metadata, cells=cells)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.metadata is not None:
            out["metadata"] = self.metadata.to_json()
        if self.cells is not None:
            out["cells"] = write_AnonymousStructure9(self.cells)
        return out


@dataclass
class DidChangeNotebookDocumentParams():
    """
    The params sent in a change notebook document notification.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # The notebook document that did change. The version number points
    # to the version after all provided changes have been applied. If
    # only the text document content of a cell changes the notebook version
    # doesn't necessarily have to change.
    notebookDocument: "VersionedNotebookDocumentIdentifier"
    
    # The actual changes to the notebook document.
    # 
    # The changes describe single state changes to the notebook document.
    # So if there are two changes c1 (at array index 0) and c2 (at array
    # index 1) for a notebook in state S then c1 moves the notebook from
    # S to S' and c2 from S' to S''. So c1 is computed on the state S and
    # c2 is computed on the state S'.
    # 
    # To mirror the content of a notebook using change events use the following approach:
    # - start with the same initial content
    # - apply the 'notebookDocument/didChange' notifications in the order you receive them.
    # - apply the `NotebookChangeEvent`s in a single notification in the order
    #   you receive them.
    change: "NotebookDocumentChangeEvent"

    def __init__(self, *, notebookDocument: "VersionedNotebookDocumentIdentifier", change: "NotebookDocumentChangeEvent") -> None:
        """
        - notebookDocument: The notebook document that did change. The version number points
            to the version after all provided changes have been applied. If
            only the text document content of a cell changes the notebook version
            doesn't necessarily have to change.
        - change: The actual changes to the notebook document.
            
            The changes describe single state changes to the notebook document.
            So if there are two changes c1 (at array index 0) and c2 (at array
            index 1) for a notebook in state S then c1 moves the notebook from
            S to S' and c2 from S' to S''. So c1 is computed on the state S and
            c2 is computed on the state S'.
            
            To mirror the content of a notebook using change events use the following approach:
            - start with the same initial content
            - apply the 'notebookDocument/didChange' notifications in the order you receive them.
            - apply the `NotebookChangeEvent`s in a single notification in the order
              you receive them.
        """
        self.notebookDocument = notebookDocument
        self.change = change

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DidChangeNotebookDocumentParams":
        notebookDocument = VersionedNotebookDocumentIdentifier.from_json(json_get_object(obj, "notebookDocument"))
        change = NotebookDocumentChangeEvent.from_json(json_get_object(obj, "change"))
        return cls(notebookDocument=notebookDocument, change=change)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["notebookDocument"] = self.notebookDocument.to_json()
        out["change"] = self.change.to_json()
        return out


@dataclass
class NotebookDocumentIdentifier():
    """
    A literal to identify a notebook document in the client.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # The notebook document's uri.
    uri: str

    def __init__(self, *, uri: str) -> None:
        """
        - uri: The notebook document's uri.
        """
        self.uri = uri

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "NotebookDocumentIdentifier":
        uri = json_get_string(obj, "uri")
        return cls(uri=uri)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["uri"] = self.uri
        return out


@dataclass
class DidSaveNotebookDocumentParams():
    """
    The params sent in a save notebook document notification.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # The notebook document that got saved.
    notebookDocument: "NotebookDocumentIdentifier"

    def __init__(self, *, notebookDocument: "NotebookDocumentIdentifier") -> None:
        """
        - notebookDocument: The notebook document that got saved.
        """
        self.notebookDocument = notebookDocument

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DidSaveNotebookDocumentParams":
        notebookDocument = NotebookDocumentIdentifier.from_json(json_get_object(obj, "notebookDocument"))
        return cls(notebookDocument=notebookDocument)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["notebookDocument"] = self.notebookDocument.to_json()
        return out


@dataclass
class DidCloseNotebookDocumentParams():
    """
    The params sent in a close notebook document notification.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # The notebook document that got closed.
    notebookDocument: "NotebookDocumentIdentifier"
    
    # The text documents that represent the content
    # of a notebook cell that got closed.
    cellTextDocuments: List["TextDocumentIdentifier"]

    def __init__(self, *, notebookDocument: "NotebookDocumentIdentifier", cellTextDocuments: List["TextDocumentIdentifier"]) -> None:
        """
        - notebookDocument: The notebook document that got closed.
        - cellTextDocuments: The text documents that represent the content
            of a notebook cell that got closed.
        """
        self.notebookDocument = notebookDocument
        self.cellTextDocuments = cellTextDocuments

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DidCloseNotebookDocumentParams":
        notebookDocument = NotebookDocumentIdentifier.from_json(json_get_object(obj, "notebookDocument"))
        cellTextDocuments = [TextDocumentIdentifier.from_json(json_assert_type_object(i)) for i in json_get_array(obj, "cellTextDocuments")]
        return cls(notebookDocument=notebookDocument, cellTextDocuments=cellTextDocuments)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["notebookDocument"] = self.notebookDocument.to_json()
        out["cellTextDocuments"] = [i.to_json() for i in self.cellTextDocuments]
        return out


@dataclass
class Registration():
    """
    General parameters to to register for an notification or to register a provider.

    *Generated from the TypeScript documentation*
    """

    # The id used to register the request. The id can be used to deregister
    # the request again.
    id: str
    
    # The method / capability to register for.
    method: str
    
    # Options necessary for the registration.
    registerOptions: Optional["LSPAny"]

    def __init__(self, *, id: str, method: str, registerOptions: Optional["LSPAny"] = None) -> None:
        """
        - id: The id used to register the request. The id can be used to deregister
            the request again.
        - method: The method / capability to register for.
        - registerOptions: Options necessary for the registration.
        """
        self.id = id
        self.method = method
        self.registerOptions = registerOptions

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "Registration":
        id = json_get_string(obj, "id")
        method = json_get_string(obj, "method")
        if registerOptions_json := obj.get("registerOptions"):
            registerOptions = parse_LSPAny(registerOptions_json)
        else:
            registerOptions = None
        return cls(id=id, method=method, registerOptions=registerOptions)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["id"] = self.id
        out["method"] = self.method
        if self.registerOptions is not None:
            out["registerOptions"] = write_LSPAny(self.registerOptions)
        return out


@dataclass
class RegistrationParams():
    """


    *Generated from the TypeScript documentation*
    """

    registrations: List["Registration"]

    def __init__(self, *, registrations: List["Registration"]) -> None:
        """
    
        """
        self.registrations = registrations

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "RegistrationParams":
        registrations = [Registration.from_json(json_assert_type_object(i)) for i in json_get_array(obj, "registrations")]
        return cls(registrations=registrations)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["registrations"] = [i.to_json() for i in self.registrations]
        return out


@dataclass
class Unregistration():
    """
    General parameters to unregister a request or notification.

    *Generated from the TypeScript documentation*
    """

    # The id used to unregister the request or notification. Usually an id
    # provided during the register request.
    id: str
    
    # The method to unregister for.
    method: str

    def __init__(self, *, id: str, method: str) -> None:
        """
        - id: The id used to unregister the request or notification. Usually an id
            provided during the register request.
        - method: The method to unregister for.
        """
        self.id = id
        self.method = method

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "Unregistration":
        id = json_get_string(obj, "id")
        method = json_get_string(obj, "method")
        return cls(id=id, method=method)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["id"] = self.id
        out["method"] = self.method
        return out


@dataclass
class UnregistrationParams():
    """


    *Generated from the TypeScript documentation*
    """

    unregisterations: List["Unregistration"]

    def __init__(self, *, unregisterations: List["Unregistration"]) -> None:
        """
    
        """
        self.unregisterations = unregisterations

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "UnregistrationParams":
        unregisterations = [Unregistration.from_json(json_assert_type_object(i)) for i in json_get_array(obj, "unregisterations")]
        return cls(unregisterations=unregisterations)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["unregisterations"] = [i.to_json() for i in self.unregisterations]
        return out


AnonymousStructure10Keys = Literal["name","version"]

def parse_AnonymousStructure10(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure10Keys, Any]:
    out: Dict[AnonymousStructure10Keys, Any] = {}
    out["name"] = json_get_string(obj, "name")
    if version_json := json_get_optional_string(obj, "version"):
        out["version"] = version_json
    else:
        out["version"] = None
    return out

def write_AnonymousStructure10(obj: Dict[AnonymousStructure10Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    out["name"] = obj["name"]
    if obj.get("version") is not None:
        out["version"] = obj.get("version")
    return out


AnonymousStructure17Keys = Literal["groupsOnLabel"]

def parse_AnonymousStructure17(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure17Keys, Any]:
    out: Dict[AnonymousStructure17Keys, Any] = {}
    if groupsOnLabel_json := json_get_optional_bool(obj, "groupsOnLabel"):
        out["groupsOnLabel"] = groupsOnLabel_json
    else:
        out["groupsOnLabel"] = None
    return out

def write_AnonymousStructure17(obj: Dict[AnonymousStructure17Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    if obj.get("groupsOnLabel") is not None:
        out["groupsOnLabel"] = obj.get("groupsOnLabel")
    return out


@dataclass
class WorkspaceEditClientCapabilities():
    """


    *Generated from the TypeScript documentation*
    """

    # The client supports versioned document changes in `WorkspaceEdit`s
    documentChanges: Optional[bool]
    
    # The resource operations the client supports. Clients should at least
    # support 'create', 'rename' and 'delete' files and folders.
    # 
    # @since 3.13.0
    resourceOperations: Optional[List["ResourceOperationKind"]]
    
    # The failure handling strategy of a client if applying the workspace edit
    # fails.
    # 
    # @since 3.13.0
    failureHandling: Optional["FailureHandlingKind"]
    
    # Whether the client normalizes line endings to the client specific
    # setting.
    # If set to `true` the client will normalize line ending characters
    # in a workspace edit to the client-specified new line
    # character.
    # 
    # @since 3.16.0
    normalizesLineEndings: Optional[bool]
    
    # Whether the client in general supports change annotations on text edits,
    # create file, rename file and delete file changes.
    # 
    # @since 3.16.0
    changeAnnotationSupport: Optional[Dict[AnonymousStructure17Keys, Any]]

    def __init__(self, *, documentChanges: Optional[bool] = None, resourceOperations: Optional[List["ResourceOperationKind"]] = None, failureHandling: Optional["FailureHandlingKind"] = None, normalizesLineEndings: Optional[bool] = None, changeAnnotationSupport: Optional[Dict[AnonymousStructure17Keys, Any]] = None) -> None:
        """
        - documentChanges: The client supports versioned document changes in `WorkspaceEdit`s
        - resourceOperations: The resource operations the client supports. Clients should at least
            support 'create', 'rename' and 'delete' files and folders.
            
            @since 3.13.0
        - failureHandling: The failure handling strategy of a client if applying the workspace edit
            fails.
            
            @since 3.13.0
        - normalizesLineEndings: Whether the client normalizes line endings to the client specific
            setting.
            If set to `true` the client will normalize line ending characters
            in a workspace edit to the client-specified new line
            character.
            
            @since 3.16.0
        - changeAnnotationSupport: Whether the client in general supports change annotations on text edits,
            create file, rename file and delete file changes.
            
            @since 3.16.0
        """
        self.documentChanges = documentChanges
        self.resourceOperations = resourceOperations
        self.failureHandling = failureHandling
        self.normalizesLineEndings = normalizesLineEndings
        self.changeAnnotationSupport = changeAnnotationSupport

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "WorkspaceEditClientCapabilities":
        if documentChanges_json := json_get_optional_bool(obj, "documentChanges"):
            documentChanges = documentChanges_json
        else:
            documentChanges = None
        if resourceOperations_json := json_get_optional_array(obj, "resourceOperations"):
            resourceOperations = [ResourceOperationKind(json_assert_type_string(i)) for i in resourceOperations_json]
        else:
            resourceOperations = None
        if failureHandling_json := json_get_optional_string(obj, "failureHandling"):
            failureHandling = FailureHandlingKind(failureHandling_json)
        else:
            failureHandling = None
        if normalizesLineEndings_json := json_get_optional_bool(obj, "normalizesLineEndings"):
            normalizesLineEndings = normalizesLineEndings_json
        else:
            normalizesLineEndings = None
        if changeAnnotationSupport_json := json_get_optional_object(obj, "changeAnnotationSupport"):
            changeAnnotationSupport = parse_AnonymousStructure17(changeAnnotationSupport_json)
        else:
            changeAnnotationSupport = None
        return cls(documentChanges=documentChanges, resourceOperations=resourceOperations, failureHandling=failureHandling, normalizesLineEndings=normalizesLineEndings, changeAnnotationSupport=changeAnnotationSupport)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.documentChanges is not None:
            out["documentChanges"] = self.documentChanges
        if self.resourceOperations is not None:
            out["resourceOperations"] = [i.value for i in self.resourceOperations]
        if self.failureHandling is not None:
            out["failureHandling"] = self.failureHandling.value
        if self.normalizesLineEndings is not None:
            out["normalizesLineEndings"] = self.normalizesLineEndings
        if self.changeAnnotationSupport is not None:
            out["changeAnnotationSupport"] = write_AnonymousStructure17(self.changeAnnotationSupport)
        return out


@dataclass
class DidChangeConfigurationClientCapabilities():
    """


    *Generated from the TypeScript documentation*
    """

    # Did change configuration notification supports dynamic registration.
    dynamicRegistration: Optional[bool]

    def __init__(self, *, dynamicRegistration: Optional[bool] = None) -> None:
        """
        - dynamicRegistration: Did change configuration notification supports dynamic registration.
        """
        self.dynamicRegistration = dynamicRegistration

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DidChangeConfigurationClientCapabilities":
        if dynamicRegistration_json := json_get_optional_bool(obj, "dynamicRegistration"):
            dynamicRegistration = dynamicRegistration_json
        else:
            dynamicRegistration = None
        return cls(dynamicRegistration=dynamicRegistration)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.dynamicRegistration is not None:
            out["dynamicRegistration"] = self.dynamicRegistration
        return out


@dataclass
class DidChangeWatchedFilesClientCapabilities():
    """


    *Generated from the TypeScript documentation*
    """

    # Did change watched files notification supports dynamic registration. Please note
    # that the current protocol doesn't support static configuration for file changes
    # from the server side.
    dynamicRegistration: Optional[bool]
    
    # Whether the client has support for {@link  RelativePattern relative pattern}
    # or not.
    # 
    # @since 3.17.0
    relativePatternSupport: Optional[bool]

    def __init__(self, *, dynamicRegistration: Optional[bool] = None, relativePatternSupport: Optional[bool] = None) -> None:
        """
        - dynamicRegistration: Did change watched files notification supports dynamic registration. Please note
            that the current protocol doesn't support static configuration for file changes
            from the server side.
        - relativePatternSupport: Whether the client has support for {@link  RelativePattern relative pattern}
            or not.
            
            @since 3.17.0
        """
        self.dynamicRegistration = dynamicRegistration
        self.relativePatternSupport = relativePatternSupport

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DidChangeWatchedFilesClientCapabilities":
        if dynamicRegistration_json := json_get_optional_bool(obj, "dynamicRegistration"):
            dynamicRegistration = dynamicRegistration_json
        else:
            dynamicRegistration = None
        if relativePatternSupport_json := json_get_optional_bool(obj, "relativePatternSupport"):
            relativePatternSupport = relativePatternSupport_json
        else:
            relativePatternSupport = None
        return cls(dynamicRegistration=dynamicRegistration, relativePatternSupport=relativePatternSupport)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.dynamicRegistration is not None:
            out["dynamicRegistration"] = self.dynamicRegistration
        if self.relativePatternSupport is not None:
            out["relativePatternSupport"] = self.relativePatternSupport
        return out


AnonymousStructure18Keys = Literal["valueSet"]

def parse_AnonymousStructure18(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure18Keys, Any]:
    out: Dict[AnonymousStructure18Keys, Any] = {}
    if valueSet_json := json_get_optional_array(obj, "valueSet"):
        out["valueSet"] = [SymbolKind(json_assert_type_int(i)) for i in valueSet_json]
    else:
        out["valueSet"] = None
    return out

def write_AnonymousStructure18(obj: Dict[AnonymousStructure18Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    if obj.get("valueSet") is not None:
        out["valueSet"] = [i.value for i in obj.get("valueSet")]
    return out


AnonymousStructure19Keys = Literal["valueSet"]

def parse_AnonymousStructure19(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure19Keys, Any]:
    out: Dict[AnonymousStructure19Keys, Any] = {}
    out["valueSet"] = [SymbolTag(json_assert_type_int(i)) for i in json_get_array(obj, "valueSet")]
    return out

def write_AnonymousStructure19(obj: Dict[AnonymousStructure19Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    out["valueSet"] = [i.value for i in obj["valueSet"]]
    return out


AnonymousStructure20Keys = Literal["properties"]

def parse_AnonymousStructure20(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure20Keys, Any]:
    out: Dict[AnonymousStructure20Keys, Any] = {}
    out["properties"] = [json_assert_type_string(i) for i in json_get_array(obj, "properties")]
    return out

def write_AnonymousStructure20(obj: Dict[AnonymousStructure20Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    out["properties"] = [i for i in obj["properties"]]
    return out


@dataclass
class WorkspaceSymbolClientCapabilities():
    """
    Client capabilities for a [WorkspaceSymbolRequest](#WorkspaceSymbolRequest).

    *Generated from the TypeScript documentation*
    """

    # Symbol request supports dynamic registration.
    dynamicRegistration: Optional[bool]
    
    # Specific capabilities for the `SymbolKind` in the `workspace/symbol` request.
    symbolKind: Optional[Dict[AnonymousStructure18Keys, Any]]
    
    # The client supports tags on `SymbolInformation`.
    # Clients supporting tags have to handle unknown tags gracefully.
    # 
    # @since 3.16.0
    tagSupport: Optional[Dict[AnonymousStructure19Keys, Any]]
    
    # The client support partial workspace symbols. The client will send the
    # request `workspaceSymbol/resolve` to the server to resolve additional
    # properties.
    # 
    # @since 3.17.0
    resolveSupport: Optional[Dict[AnonymousStructure20Keys, Any]]

    def __init__(self, *, dynamicRegistration: Optional[bool] = None, symbolKind: Optional[Dict[AnonymousStructure18Keys, Any]] = None, tagSupport: Optional[Dict[AnonymousStructure19Keys, Any]] = None, resolveSupport: Optional[Dict[AnonymousStructure20Keys, Any]] = None) -> None:
        """
        - dynamicRegistration: Symbol request supports dynamic registration.
        - symbolKind: Specific capabilities for the `SymbolKind` in the `workspace/symbol` request.
        - tagSupport: The client supports tags on `SymbolInformation`.
            Clients supporting tags have to handle unknown tags gracefully.
            
            @since 3.16.0
        - resolveSupport: The client support partial workspace symbols. The client will send the
            request `workspaceSymbol/resolve` to the server to resolve additional
            properties.
            
            @since 3.17.0
        """
        self.dynamicRegistration = dynamicRegistration
        self.symbolKind = symbolKind
        self.tagSupport = tagSupport
        self.resolveSupport = resolveSupport

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "WorkspaceSymbolClientCapabilities":
        if dynamicRegistration_json := json_get_optional_bool(obj, "dynamicRegistration"):
            dynamicRegistration = dynamicRegistration_json
        else:
            dynamicRegistration = None
        if symbolKind_json := json_get_optional_object(obj, "symbolKind"):
            symbolKind = parse_AnonymousStructure18(symbolKind_json)
        else:
            symbolKind = None
        if tagSupport_json := json_get_optional_object(obj, "tagSupport"):
            tagSupport = parse_AnonymousStructure19(tagSupport_json)
        else:
            tagSupport = None
        if resolveSupport_json := json_get_optional_object(obj, "resolveSupport"):
            resolveSupport = parse_AnonymousStructure20(resolveSupport_json)
        else:
            resolveSupport = None
        return cls(dynamicRegistration=dynamicRegistration, symbolKind=symbolKind, tagSupport=tagSupport, resolveSupport=resolveSupport)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.dynamicRegistration is not None:
            out["dynamicRegistration"] = self.dynamicRegistration
        if self.symbolKind is not None:
            out["symbolKind"] = write_AnonymousStructure18(self.symbolKind)
        if self.tagSupport is not None:
            out["tagSupport"] = write_AnonymousStructure19(self.tagSupport)
        if self.resolveSupport is not None:
            out["resolveSupport"] = write_AnonymousStructure20(self.resolveSupport)
        return out


@dataclass
class ExecuteCommandClientCapabilities():
    """
    The client capabilities of a [ExecuteCommandRequest](#ExecuteCommandRequest).

    *Generated from the TypeScript documentation*
    """

    # Execute command supports dynamic registration.
    dynamicRegistration: Optional[bool]

    def __init__(self, *, dynamicRegistration: Optional[bool] = None) -> None:
        """
        - dynamicRegistration: Execute command supports dynamic registration.
        """
        self.dynamicRegistration = dynamicRegistration

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "ExecuteCommandClientCapabilities":
        if dynamicRegistration_json := json_get_optional_bool(obj, "dynamicRegistration"):
            dynamicRegistration = dynamicRegistration_json
        else:
            dynamicRegistration = None
        return cls(dynamicRegistration=dynamicRegistration)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.dynamicRegistration is not None:
            out["dynamicRegistration"] = self.dynamicRegistration
        return out


@dataclass
class SemanticTokensWorkspaceClientCapabilities():
    """
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # Whether the client implementation supports a refresh request sent from
    # the server to the client.
    # 
    # Note that this event is global and will force the client to refresh all
    # semantic tokens currently shown. It should be used with absolute care
    # and is useful for situation where a server for example detects a project
    # wide change that requires such a calculation.
    refreshSupport: Optional[bool]

    def __init__(self, *, refreshSupport: Optional[bool] = None) -> None:
        """
        - refreshSupport: Whether the client implementation supports a refresh request sent from
            the server to the client.
            
            Note that this event is global and will force the client to refresh all
            semantic tokens currently shown. It should be used with absolute care
            and is useful for situation where a server for example detects a project
            wide change that requires such a calculation.
        """
        self.refreshSupport = refreshSupport

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "SemanticTokensWorkspaceClientCapabilities":
        if refreshSupport_json := json_get_optional_bool(obj, "refreshSupport"):
            refreshSupport = refreshSupport_json
        else:
            refreshSupport = None
        return cls(refreshSupport=refreshSupport)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.refreshSupport is not None:
            out["refreshSupport"] = self.refreshSupport
        return out


@dataclass
class CodeLensWorkspaceClientCapabilities():
    """
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # Whether the client implementation supports a refresh request sent from the
    # server to the client.
    # 
    # Note that this event is global and will force the client to refresh all
    # code lenses currently shown. It should be used with absolute care and is
    # useful for situation where a server for example detect a project wide
    # change that requires such a calculation.
    refreshSupport: Optional[bool]

    def __init__(self, *, refreshSupport: Optional[bool] = None) -> None:
        """
        - refreshSupport: Whether the client implementation supports a refresh request sent from the
            server to the client.
            
            Note that this event is global and will force the client to refresh all
            code lenses currently shown. It should be used with absolute care and is
            useful for situation where a server for example detect a project wide
            change that requires such a calculation.
        """
        self.refreshSupport = refreshSupport

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "CodeLensWorkspaceClientCapabilities":
        if refreshSupport_json := json_get_optional_bool(obj, "refreshSupport"):
            refreshSupport = refreshSupport_json
        else:
            refreshSupport = None
        return cls(refreshSupport=refreshSupport)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.refreshSupport is not None:
            out["refreshSupport"] = self.refreshSupport
        return out


@dataclass
class FileOperationClientCapabilities():
    """
    Capabilities relating to events from file operations by the user in the client.
    
    These events do not come from the file system, they come from user operations
    like renaming a file in the UI.
    
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # Whether the client supports dynamic registration for file requests/notifications.
    dynamicRegistration: Optional[bool]
    
    # The client has support for sending didCreateFiles notifications.
    didCreate: Optional[bool]
    
    # The client has support for sending willCreateFiles requests.
    willCreate: Optional[bool]
    
    # The client has support for sending didRenameFiles notifications.
    didRename: Optional[bool]
    
    # The client has support for sending willRenameFiles requests.
    willRename: Optional[bool]
    
    # The client has support for sending didDeleteFiles notifications.
    didDelete: Optional[bool]
    
    # The client has support for sending willDeleteFiles requests.
    willDelete: Optional[bool]

    def __init__(self, *, dynamicRegistration: Optional[bool] = None, didCreate: Optional[bool] = None, willCreate: Optional[bool] = None, didRename: Optional[bool] = None, willRename: Optional[bool] = None, didDelete: Optional[bool] = None, willDelete: Optional[bool] = None) -> None:
        """
        - dynamicRegistration: Whether the client supports dynamic registration for file requests/notifications.
        - didCreate: The client has support for sending didCreateFiles notifications.
        - willCreate: The client has support for sending willCreateFiles requests.
        - didRename: The client has support for sending didRenameFiles notifications.
        - willRename: The client has support for sending willRenameFiles requests.
        - didDelete: The client has support for sending didDeleteFiles notifications.
        - willDelete: The client has support for sending willDeleteFiles requests.
        """
        self.dynamicRegistration = dynamicRegistration
        self.didCreate = didCreate
        self.willCreate = willCreate
        self.didRename = didRename
        self.willRename = willRename
        self.didDelete = didDelete
        self.willDelete = willDelete

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "FileOperationClientCapabilities":
        if dynamicRegistration_json := json_get_optional_bool(obj, "dynamicRegistration"):
            dynamicRegistration = dynamicRegistration_json
        else:
            dynamicRegistration = None
        if didCreate_json := json_get_optional_bool(obj, "didCreate"):
            didCreate = didCreate_json
        else:
            didCreate = None
        if willCreate_json := json_get_optional_bool(obj, "willCreate"):
            willCreate = willCreate_json
        else:
            willCreate = None
        if didRename_json := json_get_optional_bool(obj, "didRename"):
            didRename = didRename_json
        else:
            didRename = None
        if willRename_json := json_get_optional_bool(obj, "willRename"):
            willRename = willRename_json
        else:
            willRename = None
        if didDelete_json := json_get_optional_bool(obj, "didDelete"):
            didDelete = didDelete_json
        else:
            didDelete = None
        if willDelete_json := json_get_optional_bool(obj, "willDelete"):
            willDelete = willDelete_json
        else:
            willDelete = None
        return cls(dynamicRegistration=dynamicRegistration, didCreate=didCreate, willCreate=willCreate, didRename=didRename, willRename=willRename, didDelete=didDelete, willDelete=willDelete)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.dynamicRegistration is not None:
            out["dynamicRegistration"] = self.dynamicRegistration
        if self.didCreate is not None:
            out["didCreate"] = self.didCreate
        if self.willCreate is not None:
            out["willCreate"] = self.willCreate
        if self.didRename is not None:
            out["didRename"] = self.didRename
        if self.willRename is not None:
            out["willRename"] = self.willRename
        if self.didDelete is not None:
            out["didDelete"] = self.didDelete
        if self.willDelete is not None:
            out["willDelete"] = self.willDelete
        return out


@dataclass
class InlineValueWorkspaceClientCapabilities():
    """
    Client workspace capabilities specific to inline values.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # Whether the client implementation supports a refresh request sent from the
    # server to the client.
    # 
    # Note that this event is global and will force the client to refresh all
    # inline values currently shown. It should be used with absolute care and is
    # useful for situation where a server for example detects a project wide
    # change that requires such a calculation.
    refreshSupport: Optional[bool]

    def __init__(self, *, refreshSupport: Optional[bool] = None) -> None:
        """
        - refreshSupport: Whether the client implementation supports a refresh request sent from the
            server to the client.
            
            Note that this event is global and will force the client to refresh all
            inline values currently shown. It should be used with absolute care and is
            useful for situation where a server for example detects a project wide
            change that requires such a calculation.
        """
        self.refreshSupport = refreshSupport

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "InlineValueWorkspaceClientCapabilities":
        if refreshSupport_json := json_get_optional_bool(obj, "refreshSupport"):
            refreshSupport = refreshSupport_json
        else:
            refreshSupport = None
        return cls(refreshSupport=refreshSupport)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.refreshSupport is not None:
            out["refreshSupport"] = self.refreshSupport
        return out


@dataclass
class InlayHintWorkspaceClientCapabilities():
    """
    Client workspace capabilities specific to inlay hints.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # Whether the client implementation supports a refresh request sent from
    # the server to the client.
    # 
    # Note that this event is global and will force the client to refresh all
    # inlay hints currently shown. It should be used with absolute care and
    # is useful for situation where a server for example detects a project wide
    # change that requires such a calculation.
    refreshSupport: Optional[bool]

    def __init__(self, *, refreshSupport: Optional[bool] = None) -> None:
        """
        - refreshSupport: Whether the client implementation supports a refresh request sent from
            the server to the client.
            
            Note that this event is global and will force the client to refresh all
            inlay hints currently shown. It should be used with absolute care and
            is useful for situation where a server for example detects a project wide
            change that requires such a calculation.
        """
        self.refreshSupport = refreshSupport

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "InlayHintWorkspaceClientCapabilities":
        if refreshSupport_json := json_get_optional_bool(obj, "refreshSupport"):
            refreshSupport = refreshSupport_json
        else:
            refreshSupport = None
        return cls(refreshSupport=refreshSupport)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.refreshSupport is not None:
            out["refreshSupport"] = self.refreshSupport
        return out


@dataclass
class DiagnosticWorkspaceClientCapabilities():
    """
    Workspace client capabilities specific to diagnostic pull requests.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # Whether the client implementation supports a refresh request sent from
    # the server to the client.
    # 
    # Note that this event is global and will force the client to refresh all
    # pulled diagnostics currently shown. It should be used with absolute care and
    # is useful for situation where a server for example detects a project wide
    # change that requires such a calculation.
    refreshSupport: Optional[bool]

    def __init__(self, *, refreshSupport: Optional[bool] = None) -> None:
        """
        - refreshSupport: Whether the client implementation supports a refresh request sent from
            the server to the client.
            
            Note that this event is global and will force the client to refresh all
            pulled diagnostics currently shown. It should be used with absolute care and
            is useful for situation where a server for example detects a project wide
            change that requires such a calculation.
        """
        self.refreshSupport = refreshSupport

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DiagnosticWorkspaceClientCapabilities":
        if refreshSupport_json := json_get_optional_bool(obj, "refreshSupport"):
            refreshSupport = refreshSupport_json
        else:
            refreshSupport = None
        return cls(refreshSupport=refreshSupport)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.refreshSupport is not None:
            out["refreshSupport"] = self.refreshSupport
        return out


@dataclass
class WorkspaceClientCapabilities():
    """
    Workspace specific client capabilities.

    *Generated from the TypeScript documentation*
    """

    # The client supports applying batch edits
    # to the workspace by supporting the request
    # 'workspace/applyEdit'
    applyEdit: Optional[bool]
    
    # Capabilities specific to `WorkspaceEdit`s.
    workspaceEdit: Optional["WorkspaceEditClientCapabilities"]
    
    # Capabilities specific to the `workspace/didChangeConfiguration` notification.
    didChangeConfiguration: Optional["DidChangeConfigurationClientCapabilities"]
    
    # Capabilities specific to the `workspace/didChangeWatchedFiles` notification.
    didChangeWatchedFiles: Optional["DidChangeWatchedFilesClientCapabilities"]
    
    # Capabilities specific to the `workspace/symbol` request.
    symbol: Optional["WorkspaceSymbolClientCapabilities"]
    
    # Capabilities specific to the `workspace/executeCommand` request.
    executeCommand: Optional["ExecuteCommandClientCapabilities"]
    
    # The client has support for workspace folders.
    # 
    # @since 3.6.0
    workspaceFolders: Optional[bool]
    
    # The client supports `workspace/configuration` requests.
    # 
    # @since 3.6.0
    configuration: Optional[bool]
    
    # Capabilities specific to the semantic token requests scoped to the
    # workspace.
    # 
    # @since 3.16.0.
    semanticTokens: Optional["SemanticTokensWorkspaceClientCapabilities"]
    
    # Capabilities specific to the code lens requests scoped to the
    # workspace.
    # 
    # @since 3.16.0.
    codeLens: Optional["CodeLensWorkspaceClientCapabilities"]
    
    # The client has support for file notifications/requests for user operations on files.
    # 
    # Since 3.16.0
    fileOperations: Optional["FileOperationClientCapabilities"]
    
    # Capabilities specific to the inline values requests scoped to the
    # workspace.
    # 
    # @since 3.17.0.
    inlineValue: Optional["InlineValueWorkspaceClientCapabilities"]
    
    # Capabilities specific to the inlay hint requests scoped to the
    # workspace.
    # 
    # @since 3.17.0.
    inlayHint: Optional["InlayHintWorkspaceClientCapabilities"]
    
    # Capabilities specific to the diagnostic requests scoped to the
    # workspace.
    # 
    # @since 3.17.0.
    diagnostics: Optional["DiagnosticWorkspaceClientCapabilities"]

    def __init__(self, *, applyEdit: Optional[bool] = None, workspaceEdit: Optional["WorkspaceEditClientCapabilities"] = None, didChangeConfiguration: Optional["DidChangeConfigurationClientCapabilities"] = None, didChangeWatchedFiles: Optional["DidChangeWatchedFilesClientCapabilities"] = None, symbol: Optional["WorkspaceSymbolClientCapabilities"] = None, executeCommand: Optional["ExecuteCommandClientCapabilities"] = None, workspaceFolders: Optional[bool] = None, configuration: Optional[bool] = None, semanticTokens: Optional["SemanticTokensWorkspaceClientCapabilities"] = None, codeLens: Optional["CodeLensWorkspaceClientCapabilities"] = None, fileOperations: Optional["FileOperationClientCapabilities"] = None, inlineValue: Optional["InlineValueWorkspaceClientCapabilities"] = None, inlayHint: Optional["InlayHintWorkspaceClientCapabilities"] = None, diagnostics: Optional["DiagnosticWorkspaceClientCapabilities"] = None) -> None:
        """
        - applyEdit: The client supports applying batch edits
            to the workspace by supporting the request
            'workspace/applyEdit'
        - workspaceEdit: Capabilities specific to `WorkspaceEdit`s.
        - didChangeConfiguration: Capabilities specific to the `workspace/didChangeConfiguration` notification.
        - didChangeWatchedFiles: Capabilities specific to the `workspace/didChangeWatchedFiles` notification.
        - symbol: Capabilities specific to the `workspace/symbol` request.
        - executeCommand: Capabilities specific to the `workspace/executeCommand` request.
        - workspaceFolders: The client has support for workspace folders.
            
            @since 3.6.0
        - configuration: The client supports `workspace/configuration` requests.
            
            @since 3.6.0
        - semanticTokens: Capabilities specific to the semantic token requests scoped to the
            workspace.
            
            @since 3.16.0.
        - codeLens: Capabilities specific to the code lens requests scoped to the
            workspace.
            
            @since 3.16.0.
        - fileOperations: The client has support for file notifications/requests for user operations on files.
            
            Since 3.16.0
        - inlineValue: Capabilities specific to the inline values requests scoped to the
            workspace.
            
            @since 3.17.0.
        - inlayHint: Capabilities specific to the inlay hint requests scoped to the
            workspace.
            
            @since 3.17.0.
        - diagnostics: Capabilities specific to the diagnostic requests scoped to the
            workspace.
            
            @since 3.17.0.
        """
        self.applyEdit = applyEdit
        self.workspaceEdit = workspaceEdit
        self.didChangeConfiguration = didChangeConfiguration
        self.didChangeWatchedFiles = didChangeWatchedFiles
        self.symbol = symbol
        self.executeCommand = executeCommand
        self.workspaceFolders = workspaceFolders
        self.configuration = configuration
        self.semanticTokens = semanticTokens
        self.codeLens = codeLens
        self.fileOperations = fileOperations
        self.inlineValue = inlineValue
        self.inlayHint = inlayHint
        self.diagnostics = diagnostics

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "WorkspaceClientCapabilities":
        if applyEdit_json := json_get_optional_bool(obj, "applyEdit"):
            applyEdit = applyEdit_json
        else:
            applyEdit = None
        if workspaceEdit_json := json_get_optional_object(obj, "workspaceEdit"):
            workspaceEdit = WorkspaceEditClientCapabilities.from_json(workspaceEdit_json)
        else:
            workspaceEdit = None
        if didChangeConfiguration_json := json_get_optional_object(obj, "didChangeConfiguration"):
            didChangeConfiguration = DidChangeConfigurationClientCapabilities.from_json(didChangeConfiguration_json)
        else:
            didChangeConfiguration = None
        if didChangeWatchedFiles_json := json_get_optional_object(obj, "didChangeWatchedFiles"):
            didChangeWatchedFiles = DidChangeWatchedFilesClientCapabilities.from_json(didChangeWatchedFiles_json)
        else:
            didChangeWatchedFiles = None
        if symbol_json := json_get_optional_object(obj, "symbol"):
            symbol = WorkspaceSymbolClientCapabilities.from_json(symbol_json)
        else:
            symbol = None
        if executeCommand_json := json_get_optional_object(obj, "executeCommand"):
            executeCommand = ExecuteCommandClientCapabilities.from_json(executeCommand_json)
        else:
            executeCommand = None
        if workspaceFolders_json := json_get_optional_bool(obj, "workspaceFolders"):
            workspaceFolders = workspaceFolders_json
        else:
            workspaceFolders = None
        if configuration_json := json_get_optional_bool(obj, "configuration"):
            configuration = configuration_json
        else:
            configuration = None
        if semanticTokens_json := json_get_optional_object(obj, "semanticTokens"):
            semanticTokens = SemanticTokensWorkspaceClientCapabilities.from_json(semanticTokens_json)
        else:
            semanticTokens = None
        if codeLens_json := json_get_optional_object(obj, "codeLens"):
            codeLens = CodeLensWorkspaceClientCapabilities.from_json(codeLens_json)
        else:
            codeLens = None
        if fileOperations_json := json_get_optional_object(obj, "fileOperations"):
            fileOperations = FileOperationClientCapabilities.from_json(fileOperations_json)
        else:
            fileOperations = None
        if inlineValue_json := json_get_optional_object(obj, "inlineValue"):
            inlineValue = InlineValueWorkspaceClientCapabilities.from_json(inlineValue_json)
        else:
            inlineValue = None
        if inlayHint_json := json_get_optional_object(obj, "inlayHint"):
            inlayHint = InlayHintWorkspaceClientCapabilities.from_json(inlayHint_json)
        else:
            inlayHint = None
        if diagnostics_json := json_get_optional_object(obj, "diagnostics"):
            diagnostics = DiagnosticWorkspaceClientCapabilities.from_json(diagnostics_json)
        else:
            diagnostics = None
        return cls(applyEdit=applyEdit, workspaceEdit=workspaceEdit, didChangeConfiguration=didChangeConfiguration, didChangeWatchedFiles=didChangeWatchedFiles, symbol=symbol, executeCommand=executeCommand, workspaceFolders=workspaceFolders, configuration=configuration, semanticTokens=semanticTokens, codeLens=codeLens, fileOperations=fileOperations, inlineValue=inlineValue, inlayHint=inlayHint, diagnostics=diagnostics)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.applyEdit is not None:
            out["applyEdit"] = self.applyEdit
        if self.workspaceEdit is not None:
            out["workspaceEdit"] = self.workspaceEdit.to_json()
        if self.didChangeConfiguration is not None:
            out["didChangeConfiguration"] = self.didChangeConfiguration.to_json()
        if self.didChangeWatchedFiles is not None:
            out["didChangeWatchedFiles"] = self.didChangeWatchedFiles.to_json()
        if self.symbol is not None:
            out["symbol"] = self.symbol.to_json()
        if self.executeCommand is not None:
            out["executeCommand"] = self.executeCommand.to_json()
        if self.workspaceFolders is not None:
            out["workspaceFolders"] = self.workspaceFolders
        if self.configuration is not None:
            out["configuration"] = self.configuration
        if self.semanticTokens is not None:
            out["semanticTokens"] = self.semanticTokens.to_json()
        if self.codeLens is not None:
            out["codeLens"] = self.codeLens.to_json()
        if self.fileOperations is not None:
            out["fileOperations"] = self.fileOperations.to_json()
        if self.inlineValue is not None:
            out["inlineValue"] = self.inlineValue.to_json()
        if self.inlayHint is not None:
            out["inlayHint"] = self.inlayHint.to_json()
        if self.diagnostics is not None:
            out["diagnostics"] = self.diagnostics.to_json()
        return out


@dataclass
class TextDocumentSyncClientCapabilities():
    """


    *Generated from the TypeScript documentation*
    """

    # Whether text document synchronization supports dynamic registration.
    dynamicRegistration: Optional[bool]
    
    # The client supports sending will save notifications.
    willSave: Optional[bool]
    
    # The client supports sending a will save request and
    # waits for a response providing text edits which will
    # be applied to the document before it is saved.
    willSaveWaitUntil: Optional[bool]
    
    # The client supports did save notifications.
    didSave: Optional[bool]

    def __init__(self, *, dynamicRegistration: Optional[bool] = None, willSave: Optional[bool] = None, willSaveWaitUntil: Optional[bool] = None, didSave: Optional[bool] = None) -> None:
        """
        - dynamicRegistration: Whether text document synchronization supports dynamic registration.
        - willSave: The client supports sending will save notifications.
        - willSaveWaitUntil: The client supports sending a will save request and
            waits for a response providing text edits which will
            be applied to the document before it is saved.
        - didSave: The client supports did save notifications.
        """
        self.dynamicRegistration = dynamicRegistration
        self.willSave = willSave
        self.willSaveWaitUntil = willSaveWaitUntil
        self.didSave = didSave

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "TextDocumentSyncClientCapabilities":
        if dynamicRegistration_json := json_get_optional_bool(obj, "dynamicRegistration"):
            dynamicRegistration = dynamicRegistration_json
        else:
            dynamicRegistration = None
        if willSave_json := json_get_optional_bool(obj, "willSave"):
            willSave = willSave_json
        else:
            willSave = None
        if willSaveWaitUntil_json := json_get_optional_bool(obj, "willSaveWaitUntil"):
            willSaveWaitUntil = willSaveWaitUntil_json
        else:
            willSaveWaitUntil = None
        if didSave_json := json_get_optional_bool(obj, "didSave"):
            didSave = didSave_json
        else:
            didSave = None
        return cls(dynamicRegistration=dynamicRegistration, willSave=willSave, willSaveWaitUntil=willSaveWaitUntil, didSave=didSave)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.dynamicRegistration is not None:
            out["dynamicRegistration"] = self.dynamicRegistration
        if self.willSave is not None:
            out["willSave"] = self.willSave
        if self.willSaveWaitUntil is not None:
            out["willSaveWaitUntil"] = self.willSaveWaitUntil
        if self.didSave is not None:
            out["didSave"] = self.didSave
        return out


AnonymousStructure21Keys = Literal["valueSet"]

def parse_AnonymousStructure21(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure21Keys, Any]:
    out: Dict[AnonymousStructure21Keys, Any] = {}
    out["valueSet"] = [CompletionItemTag(json_assert_type_int(i)) for i in json_get_array(obj, "valueSet")]
    return out

def write_AnonymousStructure21(obj: Dict[AnonymousStructure21Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    out["valueSet"] = [i.value for i in obj["valueSet"]]
    return out


AnonymousStructure22Keys = Literal["properties"]

def parse_AnonymousStructure22(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure22Keys, Any]:
    out: Dict[AnonymousStructure22Keys, Any] = {}
    out["properties"] = [json_assert_type_string(i) for i in json_get_array(obj, "properties")]
    return out

def write_AnonymousStructure22(obj: Dict[AnonymousStructure22Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    out["properties"] = [i for i in obj["properties"]]
    return out


AnonymousStructure23Keys = Literal["valueSet"]

def parse_AnonymousStructure23(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure23Keys, Any]:
    out: Dict[AnonymousStructure23Keys, Any] = {}
    out["valueSet"] = [InsertTextMode(json_assert_type_int(i)) for i in json_get_array(obj, "valueSet")]
    return out

def write_AnonymousStructure23(obj: Dict[AnonymousStructure23Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    out["valueSet"] = [i.value for i in obj["valueSet"]]
    return out


AnonymousStructure24Keys = Literal["snippetSupport","commitCharactersSupport","documentationFormat","deprecatedSupport","preselectSupport","tagSupport","insertReplaceSupport","resolveSupport","insertTextModeSupport","labelDetailsSupport"]

def parse_AnonymousStructure24(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure24Keys, Any]:
    out: Dict[AnonymousStructure24Keys, Any] = {}
    if snippetSupport_json := json_get_optional_bool(obj, "snippetSupport"):
        out["snippetSupport"] = snippetSupport_json
    else:
        out["snippetSupport"] = None
    if commitCharactersSupport_json := json_get_optional_bool(obj, "commitCharactersSupport"):
        out["commitCharactersSupport"] = commitCharactersSupport_json
    else:
        out["commitCharactersSupport"] = None
    if documentationFormat_json := json_get_optional_array(obj, "documentationFormat"):
        out["documentationFormat"] = [MarkupKind(json_assert_type_string(i)) for i in documentationFormat_json]
    else:
        out["documentationFormat"] = None
    if deprecatedSupport_json := json_get_optional_bool(obj, "deprecatedSupport"):
        out["deprecatedSupport"] = deprecatedSupport_json
    else:
        out["deprecatedSupport"] = None
    if preselectSupport_json := json_get_optional_bool(obj, "preselectSupport"):
        out["preselectSupport"] = preselectSupport_json
    else:
        out["preselectSupport"] = None
    if tagSupport_json := json_get_optional_object(obj, "tagSupport"):
        out["tagSupport"] = parse_AnonymousStructure21(tagSupport_json)
    else:
        out["tagSupport"] = None
    if insertReplaceSupport_json := json_get_optional_bool(obj, "insertReplaceSupport"):
        out["insertReplaceSupport"] = insertReplaceSupport_json
    else:
        out["insertReplaceSupport"] = None
    if resolveSupport_json := json_get_optional_object(obj, "resolveSupport"):
        out["resolveSupport"] = parse_AnonymousStructure22(resolveSupport_json)
    else:
        out["resolveSupport"] = None
    if insertTextModeSupport_json := json_get_optional_object(obj, "insertTextModeSupport"):
        out["insertTextModeSupport"] = parse_AnonymousStructure23(insertTextModeSupport_json)
    else:
        out["insertTextModeSupport"] = None
    if labelDetailsSupport_json := json_get_optional_bool(obj, "labelDetailsSupport"):
        out["labelDetailsSupport"] = labelDetailsSupport_json
    else:
        out["labelDetailsSupport"] = None
    return out

def write_AnonymousStructure24(obj: Dict[AnonymousStructure24Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    if obj.get("snippetSupport") is not None:
        out["snippetSupport"] = obj.get("snippetSupport")
    if obj.get("commitCharactersSupport") is not None:
        out["commitCharactersSupport"] = obj.get("commitCharactersSupport")
    if obj.get("documentationFormat") is not None:
        out["documentationFormat"] = [i.value for i in obj.get("documentationFormat")]
    if obj.get("deprecatedSupport") is not None:
        out["deprecatedSupport"] = obj.get("deprecatedSupport")
    if obj.get("preselectSupport") is not None:
        out["preselectSupport"] = obj.get("preselectSupport")
    if obj.get("tagSupport") is not None:
        out["tagSupport"] = write_AnonymousStructure21(obj.get("tagSupport"))
    if obj.get("insertReplaceSupport") is not None:
        out["insertReplaceSupport"] = obj.get("insertReplaceSupport")
    if obj.get("resolveSupport") is not None:
        out["resolveSupport"] = write_AnonymousStructure22(obj.get("resolveSupport"))
    if obj.get("insertTextModeSupport") is not None:
        out["insertTextModeSupport"] = write_AnonymousStructure23(obj.get("insertTextModeSupport"))
    if obj.get("labelDetailsSupport") is not None:
        out["labelDetailsSupport"] = obj.get("labelDetailsSupport")
    return out


AnonymousStructure25Keys = Literal["valueSet"]

def parse_AnonymousStructure25(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure25Keys, Any]:
    out: Dict[AnonymousStructure25Keys, Any] = {}
    if valueSet_json := json_get_optional_array(obj, "valueSet"):
        out["valueSet"] = [CompletionItemKind(json_assert_type_int(i)) for i in valueSet_json]
    else:
        out["valueSet"] = None
    return out

def write_AnonymousStructure25(obj: Dict[AnonymousStructure25Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    if obj.get("valueSet") is not None:
        out["valueSet"] = [i.value for i in obj.get("valueSet")]
    return out


AnonymousStructure26Keys = Literal["itemDefaults"]

def parse_AnonymousStructure26(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure26Keys, Any]:
    out: Dict[AnonymousStructure26Keys, Any] = {}
    if itemDefaults_json := json_get_optional_array(obj, "itemDefaults"):
        out["itemDefaults"] = [json_assert_type_string(i) for i in itemDefaults_json]
    else:
        out["itemDefaults"] = None
    return out

def write_AnonymousStructure26(obj: Dict[AnonymousStructure26Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    if obj.get("itemDefaults") is not None:
        out["itemDefaults"] = [i for i in obj.get("itemDefaults")]
    return out


@dataclass
class CompletionClientCapabilities():
    """
    Completion client capabilities

    *Generated from the TypeScript documentation*
    """

    # Whether completion supports dynamic registration.
    dynamicRegistration: Optional[bool]
    
    # The client supports the following `CompletionItem` specific
    # capabilities.
    completionItem: Optional[Dict[AnonymousStructure24Keys, Any]]
    
    completionItemKind: Optional[Dict[AnonymousStructure25Keys, Any]]
    
    # Defines how the client handles whitespace and indentation
    # when accepting a completion item that uses multi line
    # text in either `insertText` or `textEdit`.
    # 
    # @since 3.17.0
    insertTextMode: Optional["InsertTextMode"]
    
    # The client supports to send additional context information for a
    # `textDocument/completion` request.
    contextSupport: Optional[bool]
    
    # The client supports the following `CompletionList` specific
    # capabilities.
    # 
    # @since 3.17.0
    completionList: Optional[Dict[AnonymousStructure26Keys, Any]]

    def __init__(self, *, dynamicRegistration: Optional[bool] = None, completionItem: Optional[Dict[AnonymousStructure24Keys, Any]] = None, completionItemKind: Optional[Dict[AnonymousStructure25Keys, Any]] = None, insertTextMode: Optional["InsertTextMode"] = None, contextSupport: Optional[bool] = None, completionList: Optional[Dict[AnonymousStructure26Keys, Any]] = None) -> None:
        """
        - dynamicRegistration: Whether completion supports dynamic registration.
        - completionItem: The client supports the following `CompletionItem` specific
            capabilities.
        - insertTextMode: Defines how the client handles whitespace and indentation
            when accepting a completion item that uses multi line
            text in either `insertText` or `textEdit`.
            
            @since 3.17.0
        - contextSupport: The client supports to send additional context information for a
            `textDocument/completion` request.
        - completionList: The client supports the following `CompletionList` specific
            capabilities.
            
            @since 3.17.0
        """
        self.dynamicRegistration = dynamicRegistration
        self.completionItem = completionItem
        self.completionItemKind = completionItemKind
        self.insertTextMode = insertTextMode
        self.contextSupport = contextSupport
        self.completionList = completionList

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "CompletionClientCapabilities":
        if dynamicRegistration_json := json_get_optional_bool(obj, "dynamicRegistration"):
            dynamicRegistration = dynamicRegistration_json
        else:
            dynamicRegistration = None
        if completionItem_json := json_get_optional_object(obj, "completionItem"):
            completionItem = parse_AnonymousStructure24(completionItem_json)
        else:
            completionItem = None
        if completionItemKind_json := json_get_optional_object(obj, "completionItemKind"):
            completionItemKind = parse_AnonymousStructure25(completionItemKind_json)
        else:
            completionItemKind = None
        if insertTextMode_json := json_get_optional_int(obj, "insertTextMode"):
            insertTextMode = InsertTextMode(insertTextMode_json)
        else:
            insertTextMode = None
        if contextSupport_json := json_get_optional_bool(obj, "contextSupport"):
            contextSupport = contextSupport_json
        else:
            contextSupport = None
        if completionList_json := json_get_optional_object(obj, "completionList"):
            completionList = parse_AnonymousStructure26(completionList_json)
        else:
            completionList = None
        return cls(dynamicRegistration=dynamicRegistration, completionItem=completionItem, completionItemKind=completionItemKind, insertTextMode=insertTextMode, contextSupport=contextSupport, completionList=completionList)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.dynamicRegistration is not None:
            out["dynamicRegistration"] = self.dynamicRegistration
        if self.completionItem is not None:
            out["completionItem"] = write_AnonymousStructure24(self.completionItem)
        if self.completionItemKind is not None:
            out["completionItemKind"] = write_AnonymousStructure25(self.completionItemKind)
        if self.insertTextMode is not None:
            out["insertTextMode"] = self.insertTextMode.value
        if self.contextSupport is not None:
            out["contextSupport"] = self.contextSupport
        if self.completionList is not None:
            out["completionList"] = write_AnonymousStructure26(self.completionList)
        return out


@dataclass
class HoverClientCapabilities():
    """


    *Generated from the TypeScript documentation*
    """

    # Whether hover supports dynamic registration.
    dynamicRegistration: Optional[bool]
    
    # Client supports the following content formats for the content
    # property. The order describes the preferred format of the client.
    contentFormat: Optional[List["MarkupKind"]]

    def __init__(self, *, dynamicRegistration: Optional[bool] = None, contentFormat: Optional[List["MarkupKind"]] = None) -> None:
        """
        - dynamicRegistration: Whether hover supports dynamic registration.
        - contentFormat: Client supports the following content formats for the content
            property. The order describes the preferred format of the client.
        """
        self.dynamicRegistration = dynamicRegistration
        self.contentFormat = contentFormat

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "HoverClientCapabilities":
        if dynamicRegistration_json := json_get_optional_bool(obj, "dynamicRegistration"):
            dynamicRegistration = dynamicRegistration_json
        else:
            dynamicRegistration = None
        if contentFormat_json := json_get_optional_array(obj, "contentFormat"):
            contentFormat = [MarkupKind(json_assert_type_string(i)) for i in contentFormat_json]
        else:
            contentFormat = None
        return cls(dynamicRegistration=dynamicRegistration, contentFormat=contentFormat)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.dynamicRegistration is not None:
            out["dynamicRegistration"] = self.dynamicRegistration
        if self.contentFormat is not None:
            out["contentFormat"] = [i.value for i in self.contentFormat]
        return out


AnonymousStructure27Keys = Literal["labelOffsetSupport"]

def parse_AnonymousStructure27(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure27Keys, Any]:
    out: Dict[AnonymousStructure27Keys, Any] = {}
    if labelOffsetSupport_json := json_get_optional_bool(obj, "labelOffsetSupport"):
        out["labelOffsetSupport"] = labelOffsetSupport_json
    else:
        out["labelOffsetSupport"] = None
    return out

def write_AnonymousStructure27(obj: Dict[AnonymousStructure27Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    if obj.get("labelOffsetSupport") is not None:
        out["labelOffsetSupport"] = obj.get("labelOffsetSupport")
    return out


AnonymousStructure28Keys = Literal["documentationFormat","parameterInformation","activeParameterSupport"]

def parse_AnonymousStructure28(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure28Keys, Any]:
    out: Dict[AnonymousStructure28Keys, Any] = {}
    if documentationFormat_json := json_get_optional_array(obj, "documentationFormat"):
        out["documentationFormat"] = [MarkupKind(json_assert_type_string(i)) for i in documentationFormat_json]
    else:
        out["documentationFormat"] = None
    if parameterInformation_json := json_get_optional_object(obj, "parameterInformation"):
        out["parameterInformation"] = parse_AnonymousStructure27(parameterInformation_json)
    else:
        out["parameterInformation"] = None
    if activeParameterSupport_json := json_get_optional_bool(obj, "activeParameterSupport"):
        out["activeParameterSupport"] = activeParameterSupport_json
    else:
        out["activeParameterSupport"] = None
    return out

def write_AnonymousStructure28(obj: Dict[AnonymousStructure28Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    if obj.get("documentationFormat") is not None:
        out["documentationFormat"] = [i.value for i in obj.get("documentationFormat")]
    if obj.get("parameterInformation") is not None:
        out["parameterInformation"] = write_AnonymousStructure27(obj.get("parameterInformation"))
    if obj.get("activeParameterSupport") is not None:
        out["activeParameterSupport"] = obj.get("activeParameterSupport")
    return out


@dataclass
class SignatureHelpClientCapabilities():
    """
    Client Capabilities for a [SignatureHelpRequest](#SignatureHelpRequest).

    *Generated from the TypeScript documentation*
    """

    # Whether signature help supports dynamic registration.
    dynamicRegistration: Optional[bool]
    
    # The client supports the following `SignatureInformation`
    # specific properties.
    signatureInformation: Optional[Dict[AnonymousStructure28Keys, Any]]
    
    # The client supports to send additional context information for a
    # `textDocument/signatureHelp` request. A client that opts into
    # contextSupport will also support the `retriggerCharacters` on
    # `SignatureHelpOptions`.
    # 
    # @since 3.15.0
    contextSupport: Optional[bool]

    def __init__(self, *, dynamicRegistration: Optional[bool] = None, signatureInformation: Optional[Dict[AnonymousStructure28Keys, Any]] = None, contextSupport: Optional[bool] = None) -> None:
        """
        - dynamicRegistration: Whether signature help supports dynamic registration.
        - signatureInformation: The client supports the following `SignatureInformation`
            specific properties.
        - contextSupport: The client supports to send additional context information for a
            `textDocument/signatureHelp` request. A client that opts into
            contextSupport will also support the `retriggerCharacters` on
            `SignatureHelpOptions`.
            
            @since 3.15.0
        """
        self.dynamicRegistration = dynamicRegistration
        self.signatureInformation = signatureInformation
        self.contextSupport = contextSupport

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "SignatureHelpClientCapabilities":
        if dynamicRegistration_json := json_get_optional_bool(obj, "dynamicRegistration"):
            dynamicRegistration = dynamicRegistration_json
        else:
            dynamicRegistration = None
        if signatureInformation_json := json_get_optional_object(obj, "signatureInformation"):
            signatureInformation = parse_AnonymousStructure28(signatureInformation_json)
        else:
            signatureInformation = None
        if contextSupport_json := json_get_optional_bool(obj, "contextSupport"):
            contextSupport = contextSupport_json
        else:
            contextSupport = None
        return cls(dynamicRegistration=dynamicRegistration, signatureInformation=signatureInformation, contextSupport=contextSupport)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.dynamicRegistration is not None:
            out["dynamicRegistration"] = self.dynamicRegistration
        if self.signatureInformation is not None:
            out["signatureInformation"] = write_AnonymousStructure28(self.signatureInformation)
        if self.contextSupport is not None:
            out["contextSupport"] = self.contextSupport
        return out


@dataclass
class DeclarationClientCapabilities():
    """
    @since 3.14.0

    *Generated from the TypeScript documentation*
    """

    # Whether declaration supports dynamic registration. If this is set to `true`
    # the client supports the new `DeclarationRegistrationOptions` return value
    # for the corresponding server capability as well.
    dynamicRegistration: Optional[bool]
    
    # The client supports additional metadata in the form of declaration links.
    linkSupport: Optional[bool]

    def __init__(self, *, dynamicRegistration: Optional[bool] = None, linkSupport: Optional[bool] = None) -> None:
        """
        - dynamicRegistration: Whether declaration supports dynamic registration. If this is set to `true`
            the client supports the new `DeclarationRegistrationOptions` return value
            for the corresponding server capability as well.
        - linkSupport: The client supports additional metadata in the form of declaration links.
        """
        self.dynamicRegistration = dynamicRegistration
        self.linkSupport = linkSupport

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DeclarationClientCapabilities":
        if dynamicRegistration_json := json_get_optional_bool(obj, "dynamicRegistration"):
            dynamicRegistration = dynamicRegistration_json
        else:
            dynamicRegistration = None
        if linkSupport_json := json_get_optional_bool(obj, "linkSupport"):
            linkSupport = linkSupport_json
        else:
            linkSupport = None
        return cls(dynamicRegistration=dynamicRegistration, linkSupport=linkSupport)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.dynamicRegistration is not None:
            out["dynamicRegistration"] = self.dynamicRegistration
        if self.linkSupport is not None:
            out["linkSupport"] = self.linkSupport
        return out


@dataclass
class DefinitionClientCapabilities():
    """
    Client Capabilities for a [DefinitionRequest](#DefinitionRequest).

    *Generated from the TypeScript documentation*
    """

    # Whether definition supports dynamic registration.
    dynamicRegistration: Optional[bool]
    
    # The client supports additional metadata in the form of definition links.
    # 
    # @since 3.14.0
    linkSupport: Optional[bool]

    def __init__(self, *, dynamicRegistration: Optional[bool] = None, linkSupport: Optional[bool] = None) -> None:
        """
        - dynamicRegistration: Whether definition supports dynamic registration.
        - linkSupport: The client supports additional metadata in the form of definition links.
            
            @since 3.14.0
        """
        self.dynamicRegistration = dynamicRegistration
        self.linkSupport = linkSupport

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DefinitionClientCapabilities":
        if dynamicRegistration_json := json_get_optional_bool(obj, "dynamicRegistration"):
            dynamicRegistration = dynamicRegistration_json
        else:
            dynamicRegistration = None
        if linkSupport_json := json_get_optional_bool(obj, "linkSupport"):
            linkSupport = linkSupport_json
        else:
            linkSupport = None
        return cls(dynamicRegistration=dynamicRegistration, linkSupport=linkSupport)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.dynamicRegistration is not None:
            out["dynamicRegistration"] = self.dynamicRegistration
        if self.linkSupport is not None:
            out["linkSupport"] = self.linkSupport
        return out


@dataclass
class TypeDefinitionClientCapabilities():
    """
    Since 3.6.0

    *Generated from the TypeScript documentation*
    """

    # Whether implementation supports dynamic registration. If this is set to `true`
    # the client supports the new `TypeDefinitionRegistrationOptions` return value
    # for the corresponding server capability as well.
    dynamicRegistration: Optional[bool]
    
    # The client supports additional metadata in the form of definition links.
    # 
    # Since 3.14.0
    linkSupport: Optional[bool]

    def __init__(self, *, dynamicRegistration: Optional[bool] = None, linkSupport: Optional[bool] = None) -> None:
        """
        - dynamicRegistration: Whether implementation supports dynamic registration. If this is set to `true`
            the client supports the new `TypeDefinitionRegistrationOptions` return value
            for the corresponding server capability as well.
        - linkSupport: The client supports additional metadata in the form of definition links.
            
            Since 3.14.0
        """
        self.dynamicRegistration = dynamicRegistration
        self.linkSupport = linkSupport

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "TypeDefinitionClientCapabilities":
        if dynamicRegistration_json := json_get_optional_bool(obj, "dynamicRegistration"):
            dynamicRegistration = dynamicRegistration_json
        else:
            dynamicRegistration = None
        if linkSupport_json := json_get_optional_bool(obj, "linkSupport"):
            linkSupport = linkSupport_json
        else:
            linkSupport = None
        return cls(dynamicRegistration=dynamicRegistration, linkSupport=linkSupport)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.dynamicRegistration is not None:
            out["dynamicRegistration"] = self.dynamicRegistration
        if self.linkSupport is not None:
            out["linkSupport"] = self.linkSupport
        return out


@dataclass
class ImplementationClientCapabilities():
    """
    @since 3.6.0

    *Generated from the TypeScript documentation*
    """

    # Whether implementation supports dynamic registration. If this is set to `true`
    # the client supports the new `ImplementationRegistrationOptions` return value
    # for the corresponding server capability as well.
    dynamicRegistration: Optional[bool]
    
    # The client supports additional metadata in the form of definition links.
    # 
    # @since 3.14.0
    linkSupport: Optional[bool]

    def __init__(self, *, dynamicRegistration: Optional[bool] = None, linkSupport: Optional[bool] = None) -> None:
        """
        - dynamicRegistration: Whether implementation supports dynamic registration. If this is set to `true`
            the client supports the new `ImplementationRegistrationOptions` return value
            for the corresponding server capability as well.
        - linkSupport: The client supports additional metadata in the form of definition links.
            
            @since 3.14.0
        """
        self.dynamicRegistration = dynamicRegistration
        self.linkSupport = linkSupport

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "ImplementationClientCapabilities":
        if dynamicRegistration_json := json_get_optional_bool(obj, "dynamicRegistration"):
            dynamicRegistration = dynamicRegistration_json
        else:
            dynamicRegistration = None
        if linkSupport_json := json_get_optional_bool(obj, "linkSupport"):
            linkSupport = linkSupport_json
        else:
            linkSupport = None
        return cls(dynamicRegistration=dynamicRegistration, linkSupport=linkSupport)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.dynamicRegistration is not None:
            out["dynamicRegistration"] = self.dynamicRegistration
        if self.linkSupport is not None:
            out["linkSupport"] = self.linkSupport
        return out


@dataclass
class ReferenceClientCapabilities():
    """
    Client Capabilities for a [ReferencesRequest](#ReferencesRequest).

    *Generated from the TypeScript documentation*
    """

    # Whether references supports dynamic registration.
    dynamicRegistration: Optional[bool]

    def __init__(self, *, dynamicRegistration: Optional[bool] = None) -> None:
        """
        - dynamicRegistration: Whether references supports dynamic registration.
        """
        self.dynamicRegistration = dynamicRegistration

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "ReferenceClientCapabilities":
        if dynamicRegistration_json := json_get_optional_bool(obj, "dynamicRegistration"):
            dynamicRegistration = dynamicRegistration_json
        else:
            dynamicRegistration = None
        return cls(dynamicRegistration=dynamicRegistration)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.dynamicRegistration is not None:
            out["dynamicRegistration"] = self.dynamicRegistration
        return out


@dataclass
class DocumentHighlightClientCapabilities():
    """
    Client Capabilities for a [DocumentHighlightRequest](#DocumentHighlightRequest).

    *Generated from the TypeScript documentation*
    """

    # Whether document highlight supports dynamic registration.
    dynamicRegistration: Optional[bool]

    def __init__(self, *, dynamicRegistration: Optional[bool] = None) -> None:
        """
        - dynamicRegistration: Whether document highlight supports dynamic registration.
        """
        self.dynamicRegistration = dynamicRegistration

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DocumentHighlightClientCapabilities":
        if dynamicRegistration_json := json_get_optional_bool(obj, "dynamicRegistration"):
            dynamicRegistration = dynamicRegistration_json
        else:
            dynamicRegistration = None
        return cls(dynamicRegistration=dynamicRegistration)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.dynamicRegistration is not None:
            out["dynamicRegistration"] = self.dynamicRegistration
        return out


@dataclass
class DocumentSymbolClientCapabilities():
    """
    Client Capabilities for a [DocumentSymbolRequest](#DocumentSymbolRequest).

    *Generated from the TypeScript documentation*
    """

    # Whether document symbol supports dynamic registration.
    dynamicRegistration: Optional[bool]
    
    # Specific capabilities for the `SymbolKind` in the
    # `textDocument/documentSymbol` request.
    symbolKind: Optional[Dict[AnonymousStructure18Keys, Any]]
    
    # The client supports hierarchical document symbols.
    hierarchicalDocumentSymbolSupport: Optional[bool]
    
    # The client supports tags on `SymbolInformation`. Tags are supported on
    # `DocumentSymbol` if `hierarchicalDocumentSymbolSupport` is set to true.
    # Clients supporting tags have to handle unknown tags gracefully.
    # 
    # @since 3.16.0
    tagSupport: Optional[Dict[AnonymousStructure19Keys, Any]]
    
    # The client supports an additional label presented in the UI when
    # registering a document symbol provider.
    # 
    # @since 3.16.0
    labelSupport: Optional[bool]

    def __init__(self, *, dynamicRegistration: Optional[bool] = None, symbolKind: Optional[Dict[AnonymousStructure18Keys, Any]] = None, hierarchicalDocumentSymbolSupport: Optional[bool] = None, tagSupport: Optional[Dict[AnonymousStructure19Keys, Any]] = None, labelSupport: Optional[bool] = None) -> None:
        """
        - dynamicRegistration: Whether document symbol supports dynamic registration.
        - symbolKind: Specific capabilities for the `SymbolKind` in the
            `textDocument/documentSymbol` request.
        - hierarchicalDocumentSymbolSupport: The client supports hierarchical document symbols.
        - tagSupport: The client supports tags on `SymbolInformation`. Tags are supported on
            `DocumentSymbol` if `hierarchicalDocumentSymbolSupport` is set to true.
            Clients supporting tags have to handle unknown tags gracefully.
            
            @since 3.16.0
        - labelSupport: The client supports an additional label presented in the UI when
            registering a document symbol provider.
            
            @since 3.16.0
        """
        self.dynamicRegistration = dynamicRegistration
        self.symbolKind = symbolKind
        self.hierarchicalDocumentSymbolSupport = hierarchicalDocumentSymbolSupport
        self.tagSupport = tagSupport
        self.labelSupport = labelSupport

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DocumentSymbolClientCapabilities":
        if dynamicRegistration_json := json_get_optional_bool(obj, "dynamicRegistration"):
            dynamicRegistration = dynamicRegistration_json
        else:
            dynamicRegistration = None
        if symbolKind_json := json_get_optional_object(obj, "symbolKind"):
            symbolKind = parse_AnonymousStructure18(symbolKind_json)
        else:
            symbolKind = None
        if hierarchicalDocumentSymbolSupport_json := json_get_optional_bool(obj, "hierarchicalDocumentSymbolSupport"):
            hierarchicalDocumentSymbolSupport = hierarchicalDocumentSymbolSupport_json
        else:
            hierarchicalDocumentSymbolSupport = None
        if tagSupport_json := json_get_optional_object(obj, "tagSupport"):
            tagSupport = parse_AnonymousStructure19(tagSupport_json)
        else:
            tagSupport = None
        if labelSupport_json := json_get_optional_bool(obj, "labelSupport"):
            labelSupport = labelSupport_json
        else:
            labelSupport = None
        return cls(dynamicRegistration=dynamicRegistration, symbolKind=symbolKind, hierarchicalDocumentSymbolSupport=hierarchicalDocumentSymbolSupport, tagSupport=tagSupport, labelSupport=labelSupport)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.dynamicRegistration is not None:
            out["dynamicRegistration"] = self.dynamicRegistration
        if self.symbolKind is not None:
            out["symbolKind"] = write_AnonymousStructure18(self.symbolKind)
        if self.hierarchicalDocumentSymbolSupport is not None:
            out["hierarchicalDocumentSymbolSupport"] = self.hierarchicalDocumentSymbolSupport
        if self.tagSupport is not None:
            out["tagSupport"] = write_AnonymousStructure19(self.tagSupport)
        if self.labelSupport is not None:
            out["labelSupport"] = self.labelSupport
        return out


AnonymousStructure29Keys = Literal["valueSet"]

def parse_AnonymousStructure29(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure29Keys, Any]:
    out: Dict[AnonymousStructure29Keys, Any] = {}
    out["valueSet"] = [CodeActionKind(json_assert_type_string(i)) for i in json_get_array(obj, "valueSet")]
    return out

def write_AnonymousStructure29(obj: Dict[AnonymousStructure29Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    out["valueSet"] = [i.value for i in obj["valueSet"]]
    return out


AnonymousStructure30Keys = Literal["codeActionKind"]

def parse_AnonymousStructure30(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure30Keys, Any]:
    out: Dict[AnonymousStructure30Keys, Any] = {}
    out["codeActionKind"] = parse_AnonymousStructure29(json_get_object(obj, "codeActionKind"))
    return out

def write_AnonymousStructure30(obj: Dict[AnonymousStructure30Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    out["codeActionKind"] = write_AnonymousStructure29(obj["codeActionKind"])
    return out


@dataclass
class CodeActionClientCapabilities():
    """
    The Client Capabilities of a [CodeActionRequest](#CodeActionRequest).

    *Generated from the TypeScript documentation*
    """

    # Whether code action supports dynamic registration.
    dynamicRegistration: Optional[bool]
    
    # The client support code action literals of type `CodeAction` as a valid
    # response of the `textDocument/codeAction` request. If the property is not
    # set the request can only return `Command` literals.
    # 
    # @since 3.8.0
    codeActionLiteralSupport: Optional[Dict[AnonymousStructure30Keys, Any]]
    
    # Whether code action supports the `isPreferred` property.
    # 
    # @since 3.15.0
    isPreferredSupport: Optional[bool]
    
    # Whether code action supports the `disabled` property.
    # 
    # @since 3.16.0
    disabledSupport: Optional[bool]
    
    # Whether code action supports the `data` property which is
    # preserved between a `textDocument/codeAction` and a
    # `codeAction/resolve` request.
    # 
    # @since 3.16.0
    dataSupport: Optional[bool]
    
    # Whether the client supports resolving additional code action
    # properties via a separate `codeAction/resolve` request.
    # 
    # @since 3.16.0
    resolveSupport: Optional[Dict[AnonymousStructure22Keys, Any]]
    
    # Whether the client honors the change annotations in
    # text edits and resource operations returned via the
    # `CodeAction#edit` property by for example presenting
    # the workspace edit in the user interface and asking
    # for confirmation.
    # 
    # @since 3.16.0
    honorsChangeAnnotations: Optional[bool]

    def __init__(self, *, dynamicRegistration: Optional[bool] = None, codeActionLiteralSupport: Optional[Dict[AnonymousStructure30Keys, Any]] = None, isPreferredSupport: Optional[bool] = None, disabledSupport: Optional[bool] = None, dataSupport: Optional[bool] = None, resolveSupport: Optional[Dict[AnonymousStructure22Keys, Any]] = None, honorsChangeAnnotations: Optional[bool] = None) -> None:
        """
        - dynamicRegistration: Whether code action supports dynamic registration.
        - codeActionLiteralSupport: The client support code action literals of type `CodeAction` as a valid
            response of the `textDocument/codeAction` request. If the property is not
            set the request can only return `Command` literals.
            
            @since 3.8.0
        - isPreferredSupport: Whether code action supports the `isPreferred` property.
            
            @since 3.15.0
        - disabledSupport: Whether code action supports the `disabled` property.
            
            @since 3.16.0
        - dataSupport: Whether code action supports the `data` property which is
            preserved between a `textDocument/codeAction` and a
            `codeAction/resolve` request.
            
            @since 3.16.0
        - resolveSupport: Whether the client supports resolving additional code action
            properties via a separate `codeAction/resolve` request.
            
            @since 3.16.0
        - honorsChangeAnnotations: Whether the client honors the change annotations in
            text edits and resource operations returned via the
            `CodeAction#edit` property by for example presenting
            the workspace edit in the user interface and asking
            for confirmation.
            
            @since 3.16.0
        """
        self.dynamicRegistration = dynamicRegistration
        self.codeActionLiteralSupport = codeActionLiteralSupport
        self.isPreferredSupport = isPreferredSupport
        self.disabledSupport = disabledSupport
        self.dataSupport = dataSupport
        self.resolveSupport = resolveSupport
        self.honorsChangeAnnotations = honorsChangeAnnotations

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "CodeActionClientCapabilities":
        if dynamicRegistration_json := json_get_optional_bool(obj, "dynamicRegistration"):
            dynamicRegistration = dynamicRegistration_json
        else:
            dynamicRegistration = None
        if codeActionLiteralSupport_json := json_get_optional_object(obj, "codeActionLiteralSupport"):
            codeActionLiteralSupport = parse_AnonymousStructure30(codeActionLiteralSupport_json)
        else:
            codeActionLiteralSupport = None
        if isPreferredSupport_json := json_get_optional_bool(obj, "isPreferredSupport"):
            isPreferredSupport = isPreferredSupport_json
        else:
            isPreferredSupport = None
        if disabledSupport_json := json_get_optional_bool(obj, "disabledSupport"):
            disabledSupport = disabledSupport_json
        else:
            disabledSupport = None
        if dataSupport_json := json_get_optional_bool(obj, "dataSupport"):
            dataSupport = dataSupport_json
        else:
            dataSupport = None
        if resolveSupport_json := json_get_optional_object(obj, "resolveSupport"):
            resolveSupport = parse_AnonymousStructure22(resolveSupport_json)
        else:
            resolveSupport = None
        if honorsChangeAnnotations_json := json_get_optional_bool(obj, "honorsChangeAnnotations"):
            honorsChangeAnnotations = honorsChangeAnnotations_json
        else:
            honorsChangeAnnotations = None
        return cls(dynamicRegistration=dynamicRegistration, codeActionLiteralSupport=codeActionLiteralSupport, isPreferredSupport=isPreferredSupport, disabledSupport=disabledSupport, dataSupport=dataSupport, resolveSupport=resolveSupport, honorsChangeAnnotations=honorsChangeAnnotations)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.dynamicRegistration is not None:
            out["dynamicRegistration"] = self.dynamicRegistration
        if self.codeActionLiteralSupport is not None:
            out["codeActionLiteralSupport"] = write_AnonymousStructure30(self.codeActionLiteralSupport)
        if self.isPreferredSupport is not None:
            out["isPreferredSupport"] = self.isPreferredSupport
        if self.disabledSupport is not None:
            out["disabledSupport"] = self.disabledSupport
        if self.dataSupport is not None:
            out["dataSupport"] = self.dataSupport
        if self.resolveSupport is not None:
            out["resolveSupport"] = write_AnonymousStructure22(self.resolveSupport)
        if self.honorsChangeAnnotations is not None:
            out["honorsChangeAnnotations"] = self.honorsChangeAnnotations
        return out


@dataclass
class CodeLensClientCapabilities():
    """
    The client capabilities  of a [CodeLensRequest](#CodeLensRequest).

    *Generated from the TypeScript documentation*
    """

    # Whether code lens supports dynamic registration.
    dynamicRegistration: Optional[bool]

    def __init__(self, *, dynamicRegistration: Optional[bool] = None) -> None:
        """
        - dynamicRegistration: Whether code lens supports dynamic registration.
        """
        self.dynamicRegistration = dynamicRegistration

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "CodeLensClientCapabilities":
        if dynamicRegistration_json := json_get_optional_bool(obj, "dynamicRegistration"):
            dynamicRegistration = dynamicRegistration_json
        else:
            dynamicRegistration = None
        return cls(dynamicRegistration=dynamicRegistration)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.dynamicRegistration is not None:
            out["dynamicRegistration"] = self.dynamicRegistration
        return out


@dataclass
class DocumentLinkClientCapabilities():
    """
    The client capabilities of a [DocumentLinkRequest](#DocumentLinkRequest).

    *Generated from the TypeScript documentation*
    """

    # Whether document link supports dynamic registration.
    dynamicRegistration: Optional[bool]
    
    # Whether the client supports the `tooltip` property on `DocumentLink`.
    # 
    # @since 3.15.0
    tooltipSupport: Optional[bool]

    def __init__(self, *, dynamicRegistration: Optional[bool] = None, tooltipSupport: Optional[bool] = None) -> None:
        """
        - dynamicRegistration: Whether document link supports dynamic registration.
        - tooltipSupport: Whether the client supports the `tooltip` property on `DocumentLink`.
            
            @since 3.15.0
        """
        self.dynamicRegistration = dynamicRegistration
        self.tooltipSupport = tooltipSupport

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DocumentLinkClientCapabilities":
        if dynamicRegistration_json := json_get_optional_bool(obj, "dynamicRegistration"):
            dynamicRegistration = dynamicRegistration_json
        else:
            dynamicRegistration = None
        if tooltipSupport_json := json_get_optional_bool(obj, "tooltipSupport"):
            tooltipSupport = tooltipSupport_json
        else:
            tooltipSupport = None
        return cls(dynamicRegistration=dynamicRegistration, tooltipSupport=tooltipSupport)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.dynamicRegistration is not None:
            out["dynamicRegistration"] = self.dynamicRegistration
        if self.tooltipSupport is not None:
            out["tooltipSupport"] = self.tooltipSupport
        return out


@dataclass
class DocumentColorClientCapabilities():
    """


    *Generated from the TypeScript documentation*
    """

    # Whether implementation supports dynamic registration. If this is set to `true`
    # the client supports the new `DocumentColorRegistrationOptions` return value
    # for the corresponding server capability as well.
    dynamicRegistration: Optional[bool]

    def __init__(self, *, dynamicRegistration: Optional[bool] = None) -> None:
        """
        - dynamicRegistration: Whether implementation supports dynamic registration. If this is set to `true`
            the client supports the new `DocumentColorRegistrationOptions` return value
            for the corresponding server capability as well.
        """
        self.dynamicRegistration = dynamicRegistration

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DocumentColorClientCapabilities":
        if dynamicRegistration_json := json_get_optional_bool(obj, "dynamicRegistration"):
            dynamicRegistration = dynamicRegistration_json
        else:
            dynamicRegistration = None
        return cls(dynamicRegistration=dynamicRegistration)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.dynamicRegistration is not None:
            out["dynamicRegistration"] = self.dynamicRegistration
        return out


@dataclass
class DocumentFormattingClientCapabilities():
    """
    Client capabilities of a [DocumentFormattingRequest](#DocumentFormattingRequest).

    *Generated from the TypeScript documentation*
    """

    # Whether formatting supports dynamic registration.
    dynamicRegistration: Optional[bool]

    def __init__(self, *, dynamicRegistration: Optional[bool] = None) -> None:
        """
        - dynamicRegistration: Whether formatting supports dynamic registration.
        """
        self.dynamicRegistration = dynamicRegistration

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DocumentFormattingClientCapabilities":
        if dynamicRegistration_json := json_get_optional_bool(obj, "dynamicRegistration"):
            dynamicRegistration = dynamicRegistration_json
        else:
            dynamicRegistration = None
        return cls(dynamicRegistration=dynamicRegistration)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.dynamicRegistration is not None:
            out["dynamicRegistration"] = self.dynamicRegistration
        return out


@dataclass
class DocumentRangeFormattingClientCapabilities():
    """
    Client capabilities of a [DocumentRangeFormattingRequest](#DocumentRangeFormattingRequest).

    *Generated from the TypeScript documentation*
    """

    # Whether range formatting supports dynamic registration.
    dynamicRegistration: Optional[bool]

    def __init__(self, *, dynamicRegistration: Optional[bool] = None) -> None:
        """
        - dynamicRegistration: Whether range formatting supports dynamic registration.
        """
        self.dynamicRegistration = dynamicRegistration

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DocumentRangeFormattingClientCapabilities":
        if dynamicRegistration_json := json_get_optional_bool(obj, "dynamicRegistration"):
            dynamicRegistration = dynamicRegistration_json
        else:
            dynamicRegistration = None
        return cls(dynamicRegistration=dynamicRegistration)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.dynamicRegistration is not None:
            out["dynamicRegistration"] = self.dynamicRegistration
        return out


@dataclass
class DocumentOnTypeFormattingClientCapabilities():
    """
    Client capabilities of a [DocumentOnTypeFormattingRequest](#DocumentOnTypeFormattingRequest).

    *Generated from the TypeScript documentation*
    """

    # Whether on type formatting supports dynamic registration.
    dynamicRegistration: Optional[bool]

    def __init__(self, *, dynamicRegistration: Optional[bool] = None) -> None:
        """
        - dynamicRegistration: Whether on type formatting supports dynamic registration.
        """
        self.dynamicRegistration = dynamicRegistration

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DocumentOnTypeFormattingClientCapabilities":
        if dynamicRegistration_json := json_get_optional_bool(obj, "dynamicRegistration"):
            dynamicRegistration = dynamicRegistration_json
        else:
            dynamicRegistration = None
        return cls(dynamicRegistration=dynamicRegistration)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.dynamicRegistration is not None:
            out["dynamicRegistration"] = self.dynamicRegistration
        return out


@dataclass
class RenameClientCapabilities():
    """


    *Generated from the TypeScript documentation*
    """

    # Whether rename supports dynamic registration.
    dynamicRegistration: Optional[bool]
    
    # Client supports testing for validity of rename operations
    # before execution.
    # 
    # @since 3.12.0
    prepareSupport: Optional[bool]
    
    # Client supports the default behavior result.
    # 
    # The value indicates the default behavior used by the
    # client.
    # 
    # @since 3.16.0
    prepareSupportDefaultBehavior: Optional["PrepareSupportDefaultBehavior"]
    
    # Whether the client honors the change annotations in
    # text edits and resource operations returned via the
    # rename request's workspace edit by for example presenting
    # the workspace edit in the user interface and asking
    # for confirmation.
    # 
    # @since 3.16.0
    honorsChangeAnnotations: Optional[bool]

    def __init__(self, *, dynamicRegistration: Optional[bool] = None, prepareSupport: Optional[bool] = None, prepareSupportDefaultBehavior: Optional["PrepareSupportDefaultBehavior"] = None, honorsChangeAnnotations: Optional[bool] = None) -> None:
        """
        - dynamicRegistration: Whether rename supports dynamic registration.
        - prepareSupport: Client supports testing for validity of rename operations
            before execution.
            
            @since 3.12.0
        - prepareSupportDefaultBehavior: Client supports the default behavior result.
            
            The value indicates the default behavior used by the
            client.
            
            @since 3.16.0
        - honorsChangeAnnotations: Whether the client honors the change annotations in
            text edits and resource operations returned via the
            rename request's workspace edit by for example presenting
            the workspace edit in the user interface and asking
            for confirmation.
            
            @since 3.16.0
        """
        self.dynamicRegistration = dynamicRegistration
        self.prepareSupport = prepareSupport
        self.prepareSupportDefaultBehavior = prepareSupportDefaultBehavior
        self.honorsChangeAnnotations = honorsChangeAnnotations

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "RenameClientCapabilities":
        if dynamicRegistration_json := json_get_optional_bool(obj, "dynamicRegistration"):
            dynamicRegistration = dynamicRegistration_json
        else:
            dynamicRegistration = None
        if prepareSupport_json := json_get_optional_bool(obj, "prepareSupport"):
            prepareSupport = prepareSupport_json
        else:
            prepareSupport = None
        if prepareSupportDefaultBehavior_json := json_get_optional_int(obj, "prepareSupportDefaultBehavior"):
            prepareSupportDefaultBehavior = PrepareSupportDefaultBehavior(prepareSupportDefaultBehavior_json)
        else:
            prepareSupportDefaultBehavior = None
        if honorsChangeAnnotations_json := json_get_optional_bool(obj, "honorsChangeAnnotations"):
            honorsChangeAnnotations = honorsChangeAnnotations_json
        else:
            honorsChangeAnnotations = None
        return cls(dynamicRegistration=dynamicRegistration, prepareSupport=prepareSupport, prepareSupportDefaultBehavior=prepareSupportDefaultBehavior, honorsChangeAnnotations=honorsChangeAnnotations)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.dynamicRegistration is not None:
            out["dynamicRegistration"] = self.dynamicRegistration
        if self.prepareSupport is not None:
            out["prepareSupport"] = self.prepareSupport
        if self.prepareSupportDefaultBehavior is not None:
            out["prepareSupportDefaultBehavior"] = self.prepareSupportDefaultBehavior.value
        if self.honorsChangeAnnotations is not None:
            out["honorsChangeAnnotations"] = self.honorsChangeAnnotations
        return out


AnonymousStructure31Keys = Literal["valueSet"]

def parse_AnonymousStructure31(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure31Keys, Any]:
    out: Dict[AnonymousStructure31Keys, Any] = {}
    if valueSet_json := json_get_optional_array(obj, "valueSet"):
        out["valueSet"] = [FoldingRangeKind(json_assert_type_string(i)) for i in valueSet_json]
    else:
        out["valueSet"] = None
    return out

def write_AnonymousStructure31(obj: Dict[AnonymousStructure31Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    if obj.get("valueSet") is not None:
        out["valueSet"] = [i.value for i in obj.get("valueSet")]
    return out


AnonymousStructure32Keys = Literal["collapsedText"]

def parse_AnonymousStructure32(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure32Keys, Any]:
    out: Dict[AnonymousStructure32Keys, Any] = {}
    if collapsedText_json := json_get_optional_bool(obj, "collapsedText"):
        out["collapsedText"] = collapsedText_json
    else:
        out["collapsedText"] = None
    return out

def write_AnonymousStructure32(obj: Dict[AnonymousStructure32Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    if obj.get("collapsedText") is not None:
        out["collapsedText"] = obj.get("collapsedText")
    return out


@dataclass
class FoldingRangeClientCapabilities():
    """


    *Generated from the TypeScript documentation*
    """

    # Whether implementation supports dynamic registration for folding range
    # providers. If this is set to `true` the client supports the new
    # `FoldingRangeRegistrationOptions` return value for the corresponding
    # server capability as well.
    dynamicRegistration: Optional[bool]
    
    # The maximum number of folding ranges that the client prefers to receive
    # per document. The value serves as a hint, servers are free to follow the
    # limit.
    rangeLimit: Optional[int]
    
    # If set, the client signals that it only supports folding complete lines.
    # If set, client will ignore specified `startCharacter` and `endCharacter`
    # properties in a FoldingRange.
    lineFoldingOnly: Optional[bool]
    
    # Specific options for the folding range kind.
    # 
    # @since 3.17.0
    foldingRangeKind: Optional[Dict[AnonymousStructure31Keys, Any]]
    
    # Specific options for the folding range.
    # 
    # @since 3.17.0
    foldingRange: Optional[Dict[AnonymousStructure32Keys, Any]]

    def __init__(self, *, dynamicRegistration: Optional[bool] = None, rangeLimit: Optional[int] = None, lineFoldingOnly: Optional[bool] = None, foldingRangeKind: Optional[Dict[AnonymousStructure31Keys, Any]] = None, foldingRange: Optional[Dict[AnonymousStructure32Keys, Any]] = None) -> None:
        """
        - dynamicRegistration: Whether implementation supports dynamic registration for folding range
            providers. If this is set to `true` the client supports the new
            `FoldingRangeRegistrationOptions` return value for the corresponding
            server capability as well.
        - rangeLimit: The maximum number of folding ranges that the client prefers to receive
            per document. The value serves as a hint, servers are free to follow the
            limit.
        - lineFoldingOnly: If set, the client signals that it only supports folding complete lines.
            If set, client will ignore specified `startCharacter` and `endCharacter`
            properties in a FoldingRange.
        - foldingRangeKind: Specific options for the folding range kind.
            
            @since 3.17.0
        - foldingRange: Specific options for the folding range.
            
            @since 3.17.0
        """
        self.dynamicRegistration = dynamicRegistration
        self.rangeLimit = rangeLimit
        self.lineFoldingOnly = lineFoldingOnly
        self.foldingRangeKind = foldingRangeKind
        self.foldingRange = foldingRange

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "FoldingRangeClientCapabilities":
        if dynamicRegistration_json := json_get_optional_bool(obj, "dynamicRegistration"):
            dynamicRegistration = dynamicRegistration_json
        else:
            dynamicRegistration = None
        if rangeLimit_json := json_get_optional_int(obj, "rangeLimit"):
            rangeLimit = rangeLimit_json
        else:
            rangeLimit = None
        if lineFoldingOnly_json := json_get_optional_bool(obj, "lineFoldingOnly"):
            lineFoldingOnly = lineFoldingOnly_json
        else:
            lineFoldingOnly = None
        if foldingRangeKind_json := json_get_optional_object(obj, "foldingRangeKind"):
            foldingRangeKind = parse_AnonymousStructure31(foldingRangeKind_json)
        else:
            foldingRangeKind = None
        if foldingRange_json := json_get_optional_object(obj, "foldingRange"):
            foldingRange = parse_AnonymousStructure32(foldingRange_json)
        else:
            foldingRange = None
        return cls(dynamicRegistration=dynamicRegistration, rangeLimit=rangeLimit, lineFoldingOnly=lineFoldingOnly, foldingRangeKind=foldingRangeKind, foldingRange=foldingRange)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.dynamicRegistration is not None:
            out["dynamicRegistration"] = self.dynamicRegistration
        if self.rangeLimit is not None:
            out["rangeLimit"] = self.rangeLimit
        if self.lineFoldingOnly is not None:
            out["lineFoldingOnly"] = self.lineFoldingOnly
        if self.foldingRangeKind is not None:
            out["foldingRangeKind"] = write_AnonymousStructure31(self.foldingRangeKind)
        if self.foldingRange is not None:
            out["foldingRange"] = write_AnonymousStructure32(self.foldingRange)
        return out


@dataclass
class SelectionRangeClientCapabilities():
    """


    *Generated from the TypeScript documentation*
    """

    # Whether implementation supports dynamic registration for selection range providers. If this is set to `true`
    # the client supports the new `SelectionRangeRegistrationOptions` return value for the corresponding server
    # capability as well.
    dynamicRegistration: Optional[bool]

    def __init__(self, *, dynamicRegistration: Optional[bool] = None) -> None:
        """
        - dynamicRegistration: Whether implementation supports dynamic registration for selection range providers. If this is set to `true`
            the client supports the new `SelectionRangeRegistrationOptions` return value for the corresponding server
            capability as well.
        """
        self.dynamicRegistration = dynamicRegistration

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "SelectionRangeClientCapabilities":
        if dynamicRegistration_json := json_get_optional_bool(obj, "dynamicRegistration"):
            dynamicRegistration = dynamicRegistration_json
        else:
            dynamicRegistration = None
        return cls(dynamicRegistration=dynamicRegistration)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.dynamicRegistration is not None:
            out["dynamicRegistration"] = self.dynamicRegistration
        return out


AnonymousStructure33Keys = Literal["valueSet"]

def parse_AnonymousStructure33(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure33Keys, Any]:
    out: Dict[AnonymousStructure33Keys, Any] = {}
    out["valueSet"] = [DiagnosticTag(json_assert_type_int(i)) for i in json_get_array(obj, "valueSet")]
    return out

def write_AnonymousStructure33(obj: Dict[AnonymousStructure33Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    out["valueSet"] = [i.value for i in obj["valueSet"]]
    return out


@dataclass
class PublishDiagnosticsClientCapabilities():
    """
    The publish diagnostic client capabilities.

    *Generated from the TypeScript documentation*
    """

    # Whether the clients accepts diagnostics with related information.
    relatedInformation: Optional[bool]
    
    # Client supports the tag property to provide meta data about a diagnostic.
    # Clients supporting tags have to handle unknown tags gracefully.
    # 
    # @since 3.15.0
    tagSupport: Optional[Dict[AnonymousStructure33Keys, Any]]
    
    # Whether the client interprets the version property of the
    # `textDocument/publishDiagnostics` notification's parameter.
    # 
    # @since 3.15.0
    versionSupport: Optional[bool]
    
    # Client supports a codeDescription property
    # 
    # @since 3.16.0
    codeDescriptionSupport: Optional[bool]
    
    # Whether code action supports the `data` property which is
    # preserved between a `textDocument/publishDiagnostics` and
    # `textDocument/codeAction` request.
    # 
    # @since 3.16.0
    dataSupport: Optional[bool]

    def __init__(self, *, relatedInformation: Optional[bool] = None, tagSupport: Optional[Dict[AnonymousStructure33Keys, Any]] = None, versionSupport: Optional[bool] = None, codeDescriptionSupport: Optional[bool] = None, dataSupport: Optional[bool] = None) -> None:
        """
        - relatedInformation: Whether the clients accepts diagnostics with related information.
        - tagSupport: Client supports the tag property to provide meta data about a diagnostic.
            Clients supporting tags have to handle unknown tags gracefully.
            
            @since 3.15.0
        - versionSupport: Whether the client interprets the version property of the
            `textDocument/publishDiagnostics` notification's parameter.
            
            @since 3.15.0
        - codeDescriptionSupport: Client supports a codeDescription property
            
            @since 3.16.0
        - dataSupport: Whether code action supports the `data` property which is
            preserved between a `textDocument/publishDiagnostics` and
            `textDocument/codeAction` request.
            
            @since 3.16.0
        """
        self.relatedInformation = relatedInformation
        self.tagSupport = tagSupport
        self.versionSupport = versionSupport
        self.codeDescriptionSupport = codeDescriptionSupport
        self.dataSupport = dataSupport

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "PublishDiagnosticsClientCapabilities":
        if relatedInformation_json := json_get_optional_bool(obj, "relatedInformation"):
            relatedInformation = relatedInformation_json
        else:
            relatedInformation = None
        if tagSupport_json := json_get_optional_object(obj, "tagSupport"):
            tagSupport = parse_AnonymousStructure33(tagSupport_json)
        else:
            tagSupport = None
        if versionSupport_json := json_get_optional_bool(obj, "versionSupport"):
            versionSupport = versionSupport_json
        else:
            versionSupport = None
        if codeDescriptionSupport_json := json_get_optional_bool(obj, "codeDescriptionSupport"):
            codeDescriptionSupport = codeDescriptionSupport_json
        else:
            codeDescriptionSupport = None
        if dataSupport_json := json_get_optional_bool(obj, "dataSupport"):
            dataSupport = dataSupport_json
        else:
            dataSupport = None
        return cls(relatedInformation=relatedInformation, tagSupport=tagSupport, versionSupport=versionSupport, codeDescriptionSupport=codeDescriptionSupport, dataSupport=dataSupport)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.relatedInformation is not None:
            out["relatedInformation"] = self.relatedInformation
        if self.tagSupport is not None:
            out["tagSupport"] = write_AnonymousStructure33(self.tagSupport)
        if self.versionSupport is not None:
            out["versionSupport"] = self.versionSupport
        if self.codeDescriptionSupport is not None:
            out["codeDescriptionSupport"] = self.codeDescriptionSupport
        if self.dataSupport is not None:
            out["dataSupport"] = self.dataSupport
        return out


@dataclass
class CallHierarchyClientCapabilities():
    """
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # Whether implementation supports dynamic registration. If this is set to `true`
    # the client supports the new `(TextDocumentRegistrationOptions & StaticRegistrationOptions)`
    # return value for the corresponding server capability as well.
    dynamicRegistration: Optional[bool]

    def __init__(self, *, dynamicRegistration: Optional[bool] = None) -> None:
        """
        - dynamicRegistration: Whether implementation supports dynamic registration. If this is set to `true`
            the client supports the new `(TextDocumentRegistrationOptions & StaticRegistrationOptions)`
            return value for the corresponding server capability as well.
        """
        self.dynamicRegistration = dynamicRegistration

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "CallHierarchyClientCapabilities":
        if dynamicRegistration_json := json_get_optional_bool(obj, "dynamicRegistration"):
            dynamicRegistration = dynamicRegistration_json
        else:
            dynamicRegistration = None
        return cls(dynamicRegistration=dynamicRegistration)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.dynamicRegistration is not None:
            out["dynamicRegistration"] = self.dynamicRegistration
        return out


AnonymousStructure34Keys = Literal["delta"]

def parse_AnonymousStructure34(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure34Keys, Any]:
    out: Dict[AnonymousStructure34Keys, Any] = {}
    if delta_json := json_get_optional_bool(obj, "delta"):
        out["delta"] = delta_json
    else:
        out["delta"] = None
    return out

def write_AnonymousStructure34(obj: Dict[AnonymousStructure34Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    if obj.get("delta") is not None:
        out["delta"] = obj.get("delta")
    return out


AnonymousStructure35Keys = Literal["range","full"]

def parse_AnonymousStructure35(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure35Keys, Any]:
    out: Dict[AnonymousStructure35Keys, Any] = {}
    if range_json := obj.get("range"):
        out["range"] = parse_or_type(range_json, (lambda v: json_assert_type_bool(v), lambda v: parse_AnonymousStructure5(json_assert_type_object(v))))
    else:
        out["range"] = None
    if full_json := obj.get("full"):
        out["full"] = parse_or_type(full_json, (lambda v: json_assert_type_bool(v), lambda v: parse_AnonymousStructure34(json_assert_type_object(v))))
    else:
        out["full"] = None
    return out

def write_AnonymousStructure35(obj: Dict[AnonymousStructure35Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    if obj.get("range") is not None:
        out["range"] = write_or_type(obj.get("range"), (lambda i: isinstance(i, bool), lambda i: isinstance(i, Dict)), (lambda i: i, lambda i: write_AnonymousStructure5(i)))
    if obj.get("full") is not None:
        out["full"] = write_or_type(obj.get("full"), (lambda i: isinstance(i, bool), lambda i: isinstance(i, Dict)), (lambda i: i, lambda i: write_AnonymousStructure34(i)))
    return out


@dataclass
class SemanticTokensClientCapabilities():
    """
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # Whether implementation supports dynamic registration. If this is set to `true`
    # the client supports the new `(TextDocumentRegistrationOptions & StaticRegistrationOptions)`
    # return value for the corresponding server capability as well.
    dynamicRegistration: Optional[bool]
    
    # Which requests the client supports and might send to the server
    # depending on the server's capability. Please note that clients might not
    # show semantic tokens or degrade some of the user experience if a range
    # or full request is advertised by the client but not provided by the
    # server. If for example the client capability `requests.full` and
    # `request.range` are both set to true but the server only provides a
    # range provider the client might not render a minimap correctly or might
    # even decide to not show any semantic tokens at all.
    requests: Dict[AnonymousStructure35Keys, Any]
    
    # The token types that the client supports.
    tokenTypes: List[str]
    
    # The token modifiers that the client supports.
    tokenModifiers: List[str]
    
    # The token formats the clients supports.
    formats: List["TokenFormat"]
    
    # Whether the client supports tokens that can overlap each other.
    overlappingTokenSupport: Optional[bool]
    
    # Whether the client supports tokens that can span multiple lines.
    multilineTokenSupport: Optional[bool]
    
    # Whether the client allows the server to actively cancel a
    # semantic token request, e.g. supports returning
    # LSPErrorCodes.ServerCancelled. If a server does the client
    # needs to retrigger the request.
    # 
    # @since 3.17.0
    serverCancelSupport: Optional[bool]
    
    # Whether the client uses semantic tokens to augment existing
    # syntax tokens. If set to `true` client side created syntax
    # tokens and semantic tokens are both used for colorization. If
    # set to `false` the client only uses the returned semantic tokens
    # for colorization.
    # 
    # If the value is `undefined` then the client behavior is not
    # specified.
    # 
    # @since 3.17.0
    augmentsSyntaxTokens: Optional[bool]

    def __init__(self, *, dynamicRegistration: Optional[bool] = None, requests: Dict[AnonymousStructure35Keys, Any], tokenTypes: List[str], tokenModifiers: List[str], formats: List["TokenFormat"], overlappingTokenSupport: Optional[bool] = None, multilineTokenSupport: Optional[bool] = None, serverCancelSupport: Optional[bool] = None, augmentsSyntaxTokens: Optional[bool] = None) -> None:
        """
        - dynamicRegistration: Whether implementation supports dynamic registration. If this is set to `true`
            the client supports the new `(TextDocumentRegistrationOptions & StaticRegistrationOptions)`
            return value for the corresponding server capability as well.
        - requests: Which requests the client supports and might send to the server
            depending on the server's capability. Please note that clients might not
            show semantic tokens or degrade some of the user experience if a range
            or full request is advertised by the client but not provided by the
            server. If for example the client capability `requests.full` and
            `request.range` are both set to true but the server only provides a
            range provider the client might not render a minimap correctly or might
            even decide to not show any semantic tokens at all.
        - tokenTypes: The token types that the client supports.
        - tokenModifiers: The token modifiers that the client supports.
        - formats: The token formats the clients supports.
        - overlappingTokenSupport: Whether the client supports tokens that can overlap each other.
        - multilineTokenSupport: Whether the client supports tokens that can span multiple lines.
        - serverCancelSupport: Whether the client allows the server to actively cancel a
            semantic token request, e.g. supports returning
            LSPErrorCodes.ServerCancelled. If a server does the client
            needs to retrigger the request.
            
            @since 3.17.0
        - augmentsSyntaxTokens: Whether the client uses semantic tokens to augment existing
            syntax tokens. If set to `true` client side created syntax
            tokens and semantic tokens are both used for colorization. If
            set to `false` the client only uses the returned semantic tokens
            for colorization.
            
            If the value is `undefined` then the client behavior is not
            specified.
            
            @since 3.17.0
        """
        self.dynamicRegistration = dynamicRegistration
        self.requests = requests
        self.tokenTypes = tokenTypes
        self.tokenModifiers = tokenModifiers
        self.formats = formats
        self.overlappingTokenSupport = overlappingTokenSupport
        self.multilineTokenSupport = multilineTokenSupport
        self.serverCancelSupport = serverCancelSupport
        self.augmentsSyntaxTokens = augmentsSyntaxTokens

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "SemanticTokensClientCapabilities":
        if dynamicRegistration_json := json_get_optional_bool(obj, "dynamicRegistration"):
            dynamicRegistration = dynamicRegistration_json
        else:
            dynamicRegistration = None
        requests = parse_AnonymousStructure35(json_get_object(obj, "requests"))
        tokenTypes = [json_assert_type_string(i) for i in json_get_array(obj, "tokenTypes")]
        tokenModifiers = [json_assert_type_string(i) for i in json_get_array(obj, "tokenModifiers")]
        formats = [TokenFormat(json_assert_type_string(i)) for i in json_get_array(obj, "formats")]
        if overlappingTokenSupport_json := json_get_optional_bool(obj, "overlappingTokenSupport"):
            overlappingTokenSupport = overlappingTokenSupport_json
        else:
            overlappingTokenSupport = None
        if multilineTokenSupport_json := json_get_optional_bool(obj, "multilineTokenSupport"):
            multilineTokenSupport = multilineTokenSupport_json
        else:
            multilineTokenSupport = None
        if serverCancelSupport_json := json_get_optional_bool(obj, "serverCancelSupport"):
            serverCancelSupport = serverCancelSupport_json
        else:
            serverCancelSupport = None
        if augmentsSyntaxTokens_json := json_get_optional_bool(obj, "augmentsSyntaxTokens"):
            augmentsSyntaxTokens = augmentsSyntaxTokens_json
        else:
            augmentsSyntaxTokens = None
        return cls(dynamicRegistration=dynamicRegistration, requests=requests, tokenTypes=tokenTypes, tokenModifiers=tokenModifiers, formats=formats, overlappingTokenSupport=overlappingTokenSupport, multilineTokenSupport=multilineTokenSupport, serverCancelSupport=serverCancelSupport, augmentsSyntaxTokens=augmentsSyntaxTokens)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.dynamicRegistration is not None:
            out["dynamicRegistration"] = self.dynamicRegistration
        out["requests"] = write_AnonymousStructure35(self.requests)
        out["tokenTypes"] = [i for i in self.tokenTypes]
        out["tokenModifiers"] = [i for i in self.tokenModifiers]
        out["formats"] = [i.value for i in self.formats]
        if self.overlappingTokenSupport is not None:
            out["overlappingTokenSupport"] = self.overlappingTokenSupport
        if self.multilineTokenSupport is not None:
            out["multilineTokenSupport"] = self.multilineTokenSupport
        if self.serverCancelSupport is not None:
            out["serverCancelSupport"] = self.serverCancelSupport
        if self.augmentsSyntaxTokens is not None:
            out["augmentsSyntaxTokens"] = self.augmentsSyntaxTokens
        return out


@dataclass
class LinkedEditingRangeClientCapabilities():
    """
    Client capabilities for the linked editing range request.
    
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # Whether implementation supports dynamic registration. If this is set to `true`
    # the client supports the new `(TextDocumentRegistrationOptions & StaticRegistrationOptions)`
    # return value for the corresponding server capability as well.
    dynamicRegistration: Optional[bool]

    def __init__(self, *, dynamicRegistration: Optional[bool] = None) -> None:
        """
        - dynamicRegistration: Whether implementation supports dynamic registration. If this is set to `true`
            the client supports the new `(TextDocumentRegistrationOptions & StaticRegistrationOptions)`
            return value for the corresponding server capability as well.
        """
        self.dynamicRegistration = dynamicRegistration

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "LinkedEditingRangeClientCapabilities":
        if dynamicRegistration_json := json_get_optional_bool(obj, "dynamicRegistration"):
            dynamicRegistration = dynamicRegistration_json
        else:
            dynamicRegistration = None
        return cls(dynamicRegistration=dynamicRegistration)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.dynamicRegistration is not None:
            out["dynamicRegistration"] = self.dynamicRegistration
        return out


@dataclass
class MonikerClientCapabilities():
    """
    Client capabilities specific to the moniker request.
    
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # Whether moniker supports dynamic registration. If this is set to `true`
    # the client supports the new `MonikerRegistrationOptions` return value
    # for the corresponding server capability as well.
    dynamicRegistration: Optional[bool]

    def __init__(self, *, dynamicRegistration: Optional[bool] = None) -> None:
        """
        - dynamicRegistration: Whether moniker supports dynamic registration. If this is set to `true`
            the client supports the new `MonikerRegistrationOptions` return value
            for the corresponding server capability as well.
        """
        self.dynamicRegistration = dynamicRegistration

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "MonikerClientCapabilities":
        if dynamicRegistration_json := json_get_optional_bool(obj, "dynamicRegistration"):
            dynamicRegistration = dynamicRegistration_json
        else:
            dynamicRegistration = None
        return cls(dynamicRegistration=dynamicRegistration)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.dynamicRegistration is not None:
            out["dynamicRegistration"] = self.dynamicRegistration
        return out


@dataclass
class TypeHierarchyClientCapabilities():
    """
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # Whether implementation supports dynamic registration. If this is set to `true`
    # the client supports the new `(TextDocumentRegistrationOptions & StaticRegistrationOptions)`
    # return value for the corresponding server capability as well.
    dynamicRegistration: Optional[bool]

    def __init__(self, *, dynamicRegistration: Optional[bool] = None) -> None:
        """
        - dynamicRegistration: Whether implementation supports dynamic registration. If this is set to `true`
            the client supports the new `(TextDocumentRegistrationOptions & StaticRegistrationOptions)`
            return value for the corresponding server capability as well.
        """
        self.dynamicRegistration = dynamicRegistration

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "TypeHierarchyClientCapabilities":
        if dynamicRegistration_json := json_get_optional_bool(obj, "dynamicRegistration"):
            dynamicRegistration = dynamicRegistration_json
        else:
            dynamicRegistration = None
        return cls(dynamicRegistration=dynamicRegistration)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.dynamicRegistration is not None:
            out["dynamicRegistration"] = self.dynamicRegistration
        return out


@dataclass
class InlineValueClientCapabilities():
    """
    Client capabilities specific to inline values.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # Whether implementation supports dynamic registration for inline value providers.
    dynamicRegistration: Optional[bool]

    def __init__(self, *, dynamicRegistration: Optional[bool] = None) -> None:
        """
        - dynamicRegistration: Whether implementation supports dynamic registration for inline value providers.
        """
        self.dynamicRegistration = dynamicRegistration

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "InlineValueClientCapabilities":
        if dynamicRegistration_json := json_get_optional_bool(obj, "dynamicRegistration"):
            dynamicRegistration = dynamicRegistration_json
        else:
            dynamicRegistration = None
        return cls(dynamicRegistration=dynamicRegistration)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.dynamicRegistration is not None:
            out["dynamicRegistration"] = self.dynamicRegistration
        return out


@dataclass
class InlayHintClientCapabilities():
    """
    Inlay hint client capabilities.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # Whether inlay hints support dynamic registration.
    dynamicRegistration: Optional[bool]
    
    # Indicates which properties a client can resolve lazily on an inlay
    # hint.
    resolveSupport: Optional[Dict[AnonymousStructure22Keys, Any]]

    def __init__(self, *, dynamicRegistration: Optional[bool] = None, resolveSupport: Optional[Dict[AnonymousStructure22Keys, Any]] = None) -> None:
        """
        - dynamicRegistration: Whether inlay hints support dynamic registration.
        - resolveSupport: Indicates which properties a client can resolve lazily on an inlay
            hint.
        """
        self.dynamicRegistration = dynamicRegistration
        self.resolveSupport = resolveSupport

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "InlayHintClientCapabilities":
        if dynamicRegistration_json := json_get_optional_bool(obj, "dynamicRegistration"):
            dynamicRegistration = dynamicRegistration_json
        else:
            dynamicRegistration = None
        if resolveSupport_json := json_get_optional_object(obj, "resolveSupport"):
            resolveSupport = parse_AnonymousStructure22(resolveSupport_json)
        else:
            resolveSupport = None
        return cls(dynamicRegistration=dynamicRegistration, resolveSupport=resolveSupport)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.dynamicRegistration is not None:
            out["dynamicRegistration"] = self.dynamicRegistration
        if self.resolveSupport is not None:
            out["resolveSupport"] = write_AnonymousStructure22(self.resolveSupport)
        return out


@dataclass
class DiagnosticClientCapabilities():
    """
    Client capabilities specific to diagnostic pull requests.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # Whether implementation supports dynamic registration. If this is set to `true`
    # the client supports the new `(TextDocumentRegistrationOptions & StaticRegistrationOptions)`
    # return value for the corresponding server capability as well.
    dynamicRegistration: Optional[bool]
    
    # Whether the clients supports related documents for document diagnostic pulls.
    relatedDocumentSupport: Optional[bool]

    def __init__(self, *, dynamicRegistration: Optional[bool] = None, relatedDocumentSupport: Optional[bool] = None) -> None:
        """
        - dynamicRegistration: Whether implementation supports dynamic registration. If this is set to `true`
            the client supports the new `(TextDocumentRegistrationOptions & StaticRegistrationOptions)`
            return value for the corresponding server capability as well.
        - relatedDocumentSupport: Whether the clients supports related documents for document diagnostic pulls.
        """
        self.dynamicRegistration = dynamicRegistration
        self.relatedDocumentSupport = relatedDocumentSupport

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DiagnosticClientCapabilities":
        if dynamicRegistration_json := json_get_optional_bool(obj, "dynamicRegistration"):
            dynamicRegistration = dynamicRegistration_json
        else:
            dynamicRegistration = None
        if relatedDocumentSupport_json := json_get_optional_bool(obj, "relatedDocumentSupport"):
            relatedDocumentSupport = relatedDocumentSupport_json
        else:
            relatedDocumentSupport = None
        return cls(dynamicRegistration=dynamicRegistration, relatedDocumentSupport=relatedDocumentSupport)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.dynamicRegistration is not None:
            out["dynamicRegistration"] = self.dynamicRegistration
        if self.relatedDocumentSupport is not None:
            out["relatedDocumentSupport"] = self.relatedDocumentSupport
        return out


@dataclass
class TextDocumentClientCapabilities():
    """
    Text document specific client capabilities.

    *Generated from the TypeScript documentation*
    """

    # Defines which synchronization capabilities the client supports.
    synchronization: Optional["TextDocumentSyncClientCapabilities"]
    
    # Capabilities specific to the `textDocument/completion` request.
    completion: Optional["CompletionClientCapabilities"]
    
    # Capabilities specific to the `textDocument/hover` request.
    hover: Optional["HoverClientCapabilities"]
    
    # Capabilities specific to the `textDocument/signatureHelp` request.
    signatureHelp: Optional["SignatureHelpClientCapabilities"]
    
    # Capabilities specific to the `textDocument/declaration` request.
    # 
    # @since 3.14.0
    declaration: Optional["DeclarationClientCapabilities"]
    
    # Capabilities specific to the `textDocument/definition` request.
    definition: Optional["DefinitionClientCapabilities"]
    
    # Capabilities specific to the `textDocument/typeDefinition` request.
    # 
    # @since 3.6.0
    typeDefinition: Optional["TypeDefinitionClientCapabilities"]
    
    # Capabilities specific to the `textDocument/implementation` request.
    # 
    # @since 3.6.0
    implementation: Optional["ImplementationClientCapabilities"]
    
    # Capabilities specific to the `textDocument/references` request.
    references: Optional["ReferenceClientCapabilities"]
    
    # Capabilities specific to the `textDocument/documentHighlight` request.
    documentHighlight: Optional["DocumentHighlightClientCapabilities"]
    
    # Capabilities specific to the `textDocument/documentSymbol` request.
    documentSymbol: Optional["DocumentSymbolClientCapabilities"]
    
    # Capabilities specific to the `textDocument/codeAction` request.
    codeAction: Optional["CodeActionClientCapabilities"]
    
    # Capabilities specific to the `textDocument/codeLens` request.
    codeLens: Optional["CodeLensClientCapabilities"]
    
    # Capabilities specific to the `textDocument/documentLink` request.
    documentLink: Optional["DocumentLinkClientCapabilities"]
    
    # Capabilities specific to the `textDocument/documentColor` and the
    # `textDocument/colorPresentation` request.
    # 
    # @since 3.6.0
    colorProvider: Optional["DocumentColorClientCapabilities"]
    
    # Capabilities specific to the `textDocument/formatting` request.
    formatting: Optional["DocumentFormattingClientCapabilities"]
    
    # Capabilities specific to the `textDocument/rangeFormatting` request.
    rangeFormatting: Optional["DocumentRangeFormattingClientCapabilities"]
    
    # Capabilities specific to the `textDocument/onTypeFormatting` request.
    onTypeFormatting: Optional["DocumentOnTypeFormattingClientCapabilities"]
    
    # Capabilities specific to the `textDocument/rename` request.
    rename: Optional["RenameClientCapabilities"]
    
    # Capabilities specific to the `textDocument/foldingRange` request.
    # 
    # @since 3.10.0
    foldingRange: Optional["FoldingRangeClientCapabilities"]
    
    # Capabilities specific to the `textDocument/selectionRange` request.
    # 
    # @since 3.15.0
    selectionRange: Optional["SelectionRangeClientCapabilities"]
    
    # Capabilities specific to the `textDocument/publishDiagnostics` notification.
    publishDiagnostics: Optional["PublishDiagnosticsClientCapabilities"]
    
    # Capabilities specific to the various call hierarchy requests.
    # 
    # @since 3.16.0
    callHierarchy: Optional["CallHierarchyClientCapabilities"]
    
    # Capabilities specific to the various semantic token request.
    # 
    # @since 3.16.0
    semanticTokens: Optional["SemanticTokensClientCapabilities"]
    
    # Capabilities specific to the `textDocument/linkedEditingRange` request.
    # 
    # @since 3.16.0
    linkedEditingRange: Optional["LinkedEditingRangeClientCapabilities"]
    
    # Client capabilities specific to the `textDocument/moniker` request.
    # 
    # @since 3.16.0
    moniker: Optional["MonikerClientCapabilities"]
    
    # Capabilities specific to the various type hierarchy requests.
    # 
    # @since 3.17.0
    typeHierarchy: Optional["TypeHierarchyClientCapabilities"]
    
    # Capabilities specific to the `textDocument/inlineValue` request.
    # 
    # @since 3.17.0
    inlineValue: Optional["InlineValueClientCapabilities"]
    
    # Capabilities specific to the `textDocument/inlayHint` request.
    # 
    # @since 3.17.0
    inlayHint: Optional["InlayHintClientCapabilities"]
    
    # Capabilities specific to the diagnostic pull model.
    # 
    # @since 3.17.0
    diagnostic: Optional["DiagnosticClientCapabilities"]

    def __init__(self, *, synchronization: Optional["TextDocumentSyncClientCapabilities"] = None, completion: Optional["CompletionClientCapabilities"] = None, hover: Optional["HoverClientCapabilities"] = None, signatureHelp: Optional["SignatureHelpClientCapabilities"] = None, declaration: Optional["DeclarationClientCapabilities"] = None, definition: Optional["DefinitionClientCapabilities"] = None, typeDefinition: Optional["TypeDefinitionClientCapabilities"] = None, implementation: Optional["ImplementationClientCapabilities"] = None, references: Optional["ReferenceClientCapabilities"] = None, documentHighlight: Optional["DocumentHighlightClientCapabilities"] = None, documentSymbol: Optional["DocumentSymbolClientCapabilities"] = None, codeAction: Optional["CodeActionClientCapabilities"] = None, codeLens: Optional["CodeLensClientCapabilities"] = None, documentLink: Optional["DocumentLinkClientCapabilities"] = None, colorProvider: Optional["DocumentColorClientCapabilities"] = None, formatting: Optional["DocumentFormattingClientCapabilities"] = None, rangeFormatting: Optional["DocumentRangeFormattingClientCapabilities"] = None, onTypeFormatting: Optional["DocumentOnTypeFormattingClientCapabilities"] = None, rename: Optional["RenameClientCapabilities"] = None, foldingRange: Optional["FoldingRangeClientCapabilities"] = None, selectionRange: Optional["SelectionRangeClientCapabilities"] = None, publishDiagnostics: Optional["PublishDiagnosticsClientCapabilities"] = None, callHierarchy: Optional["CallHierarchyClientCapabilities"] = None, semanticTokens: Optional["SemanticTokensClientCapabilities"] = None, linkedEditingRange: Optional["LinkedEditingRangeClientCapabilities"] = None, moniker: Optional["MonikerClientCapabilities"] = None, typeHierarchy: Optional["TypeHierarchyClientCapabilities"] = None, inlineValue: Optional["InlineValueClientCapabilities"] = None, inlayHint: Optional["InlayHintClientCapabilities"] = None, diagnostic: Optional["DiagnosticClientCapabilities"] = None) -> None:
        """
        - synchronization: Defines which synchronization capabilities the client supports.
        - completion: Capabilities specific to the `textDocument/completion` request.
        - hover: Capabilities specific to the `textDocument/hover` request.
        - signatureHelp: Capabilities specific to the `textDocument/signatureHelp` request.
        - declaration: Capabilities specific to the `textDocument/declaration` request.
            
            @since 3.14.0
        - definition: Capabilities specific to the `textDocument/definition` request.
        - typeDefinition: Capabilities specific to the `textDocument/typeDefinition` request.
            
            @since 3.6.0
        - implementation: Capabilities specific to the `textDocument/implementation` request.
            
            @since 3.6.0
        - references: Capabilities specific to the `textDocument/references` request.
        - documentHighlight: Capabilities specific to the `textDocument/documentHighlight` request.
        - documentSymbol: Capabilities specific to the `textDocument/documentSymbol` request.
        - codeAction: Capabilities specific to the `textDocument/codeAction` request.
        - codeLens: Capabilities specific to the `textDocument/codeLens` request.
        - documentLink: Capabilities specific to the `textDocument/documentLink` request.
        - colorProvider: Capabilities specific to the `textDocument/documentColor` and the
            `textDocument/colorPresentation` request.
            
            @since 3.6.0
        - formatting: Capabilities specific to the `textDocument/formatting` request.
        - rangeFormatting: Capabilities specific to the `textDocument/rangeFormatting` request.
        - onTypeFormatting: Capabilities specific to the `textDocument/onTypeFormatting` request.
        - rename: Capabilities specific to the `textDocument/rename` request.
        - foldingRange: Capabilities specific to the `textDocument/foldingRange` request.
            
            @since 3.10.0
        - selectionRange: Capabilities specific to the `textDocument/selectionRange` request.
            
            @since 3.15.0
        - publishDiagnostics: Capabilities specific to the `textDocument/publishDiagnostics` notification.
        - callHierarchy: Capabilities specific to the various call hierarchy requests.
            
            @since 3.16.0
        - semanticTokens: Capabilities specific to the various semantic token request.
            
            @since 3.16.0
        - linkedEditingRange: Capabilities specific to the `textDocument/linkedEditingRange` request.
            
            @since 3.16.0
        - moniker: Client capabilities specific to the `textDocument/moniker` request.
            
            @since 3.16.0
        - typeHierarchy: Capabilities specific to the various type hierarchy requests.
            
            @since 3.17.0
        - inlineValue: Capabilities specific to the `textDocument/inlineValue` request.
            
            @since 3.17.0
        - inlayHint: Capabilities specific to the `textDocument/inlayHint` request.
            
            @since 3.17.0
        - diagnostic: Capabilities specific to the diagnostic pull model.
            
            @since 3.17.0
        """
        self.synchronization = synchronization
        self.completion = completion
        self.hover = hover
        self.signatureHelp = signatureHelp
        self.declaration = declaration
        self.definition = definition
        self.typeDefinition = typeDefinition
        self.implementation = implementation
        self.references = references
        self.documentHighlight = documentHighlight
        self.documentSymbol = documentSymbol
        self.codeAction = codeAction
        self.codeLens = codeLens
        self.documentLink = documentLink
        self.colorProvider = colorProvider
        self.formatting = formatting
        self.rangeFormatting = rangeFormatting
        self.onTypeFormatting = onTypeFormatting
        self.rename = rename
        self.foldingRange = foldingRange
        self.selectionRange = selectionRange
        self.publishDiagnostics = publishDiagnostics
        self.callHierarchy = callHierarchy
        self.semanticTokens = semanticTokens
        self.linkedEditingRange = linkedEditingRange
        self.moniker = moniker
        self.typeHierarchy = typeHierarchy
        self.inlineValue = inlineValue
        self.inlayHint = inlayHint
        self.diagnostic = diagnostic

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "TextDocumentClientCapabilities":
        if synchronization_json := json_get_optional_object(obj, "synchronization"):
            synchronization = TextDocumentSyncClientCapabilities.from_json(synchronization_json)
        else:
            synchronization = None
        if completion_json := json_get_optional_object(obj, "completion"):
            completion = CompletionClientCapabilities.from_json(completion_json)
        else:
            completion = None
        if hover_json := json_get_optional_object(obj, "hover"):
            hover = HoverClientCapabilities.from_json(hover_json)
        else:
            hover = None
        if signatureHelp_json := json_get_optional_object(obj, "signatureHelp"):
            signatureHelp = SignatureHelpClientCapabilities.from_json(signatureHelp_json)
        else:
            signatureHelp = None
        if declaration_json := json_get_optional_object(obj, "declaration"):
            declaration = DeclarationClientCapabilities.from_json(declaration_json)
        else:
            declaration = None
        if definition_json := json_get_optional_object(obj, "definition"):
            definition = DefinitionClientCapabilities.from_json(definition_json)
        else:
            definition = None
        if typeDefinition_json := json_get_optional_object(obj, "typeDefinition"):
            typeDefinition = TypeDefinitionClientCapabilities.from_json(typeDefinition_json)
        else:
            typeDefinition = None
        if implementation_json := json_get_optional_object(obj, "implementation"):
            implementation = ImplementationClientCapabilities.from_json(implementation_json)
        else:
            implementation = None
        if references_json := json_get_optional_object(obj, "references"):
            references = ReferenceClientCapabilities.from_json(references_json)
        else:
            references = None
        if documentHighlight_json := json_get_optional_object(obj, "documentHighlight"):
            documentHighlight = DocumentHighlightClientCapabilities.from_json(documentHighlight_json)
        else:
            documentHighlight = None
        if documentSymbol_json := json_get_optional_object(obj, "documentSymbol"):
            documentSymbol = DocumentSymbolClientCapabilities.from_json(documentSymbol_json)
        else:
            documentSymbol = None
        if codeAction_json := json_get_optional_object(obj, "codeAction"):
            codeAction = CodeActionClientCapabilities.from_json(codeAction_json)
        else:
            codeAction = None
        if codeLens_json := json_get_optional_object(obj, "codeLens"):
            codeLens = CodeLensClientCapabilities.from_json(codeLens_json)
        else:
            codeLens = None
        if documentLink_json := json_get_optional_object(obj, "documentLink"):
            documentLink = DocumentLinkClientCapabilities.from_json(documentLink_json)
        else:
            documentLink = None
        if colorProvider_json := json_get_optional_object(obj, "colorProvider"):
            colorProvider = DocumentColorClientCapabilities.from_json(colorProvider_json)
        else:
            colorProvider = None
        if formatting_json := json_get_optional_object(obj, "formatting"):
            formatting = DocumentFormattingClientCapabilities.from_json(formatting_json)
        else:
            formatting = None
        if rangeFormatting_json := json_get_optional_object(obj, "rangeFormatting"):
            rangeFormatting = DocumentRangeFormattingClientCapabilities.from_json(rangeFormatting_json)
        else:
            rangeFormatting = None
        if onTypeFormatting_json := json_get_optional_object(obj, "onTypeFormatting"):
            onTypeFormatting = DocumentOnTypeFormattingClientCapabilities.from_json(onTypeFormatting_json)
        else:
            onTypeFormatting = None
        if rename_json := json_get_optional_object(obj, "rename"):
            rename = RenameClientCapabilities.from_json(rename_json)
        else:
            rename = None
        if foldingRange_json := json_get_optional_object(obj, "foldingRange"):
            foldingRange = FoldingRangeClientCapabilities.from_json(foldingRange_json)
        else:
            foldingRange = None
        if selectionRange_json := json_get_optional_object(obj, "selectionRange"):
            selectionRange = SelectionRangeClientCapabilities.from_json(selectionRange_json)
        else:
            selectionRange = None
        if publishDiagnostics_json := json_get_optional_object(obj, "publishDiagnostics"):
            publishDiagnostics = PublishDiagnosticsClientCapabilities.from_json(publishDiagnostics_json)
        else:
            publishDiagnostics = None
        if callHierarchy_json := json_get_optional_object(obj, "callHierarchy"):
            callHierarchy = CallHierarchyClientCapabilities.from_json(callHierarchy_json)
        else:
            callHierarchy = None
        if semanticTokens_json := json_get_optional_object(obj, "semanticTokens"):
            semanticTokens = SemanticTokensClientCapabilities.from_json(semanticTokens_json)
        else:
            semanticTokens = None
        if linkedEditingRange_json := json_get_optional_object(obj, "linkedEditingRange"):
            linkedEditingRange = LinkedEditingRangeClientCapabilities.from_json(linkedEditingRange_json)
        else:
            linkedEditingRange = None
        if moniker_json := json_get_optional_object(obj, "moniker"):
            moniker = MonikerClientCapabilities.from_json(moniker_json)
        else:
            moniker = None
        if typeHierarchy_json := json_get_optional_object(obj, "typeHierarchy"):
            typeHierarchy = TypeHierarchyClientCapabilities.from_json(typeHierarchy_json)
        else:
            typeHierarchy = None
        if inlineValue_json := json_get_optional_object(obj, "inlineValue"):
            inlineValue = InlineValueClientCapabilities.from_json(inlineValue_json)
        else:
            inlineValue = None
        if inlayHint_json := json_get_optional_object(obj, "inlayHint"):
            inlayHint = InlayHintClientCapabilities.from_json(inlayHint_json)
        else:
            inlayHint = None
        if diagnostic_json := json_get_optional_object(obj, "diagnostic"):
            diagnostic = DiagnosticClientCapabilities.from_json(diagnostic_json)
        else:
            diagnostic = None
        return cls(synchronization=synchronization, completion=completion, hover=hover, signatureHelp=signatureHelp, declaration=declaration, definition=definition, typeDefinition=typeDefinition, implementation=implementation, references=references, documentHighlight=documentHighlight, documentSymbol=documentSymbol, codeAction=codeAction, codeLens=codeLens, documentLink=documentLink, colorProvider=colorProvider, formatting=formatting, rangeFormatting=rangeFormatting, onTypeFormatting=onTypeFormatting, rename=rename, foldingRange=foldingRange, selectionRange=selectionRange, publishDiagnostics=publishDiagnostics, callHierarchy=callHierarchy, semanticTokens=semanticTokens, linkedEditingRange=linkedEditingRange, moniker=moniker, typeHierarchy=typeHierarchy, inlineValue=inlineValue, inlayHint=inlayHint, diagnostic=diagnostic)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.synchronization is not None:
            out["synchronization"] = self.synchronization.to_json()
        if self.completion is not None:
            out["completion"] = self.completion.to_json()
        if self.hover is not None:
            out["hover"] = self.hover.to_json()
        if self.signatureHelp is not None:
            out["signatureHelp"] = self.signatureHelp.to_json()
        if self.declaration is not None:
            out["declaration"] = self.declaration.to_json()
        if self.definition is not None:
            out["definition"] = self.definition.to_json()
        if self.typeDefinition is not None:
            out["typeDefinition"] = self.typeDefinition.to_json()
        if self.implementation is not None:
            out["implementation"] = self.implementation.to_json()
        if self.references is not None:
            out["references"] = self.references.to_json()
        if self.documentHighlight is not None:
            out["documentHighlight"] = self.documentHighlight.to_json()
        if self.documentSymbol is not None:
            out["documentSymbol"] = self.documentSymbol.to_json()
        if self.codeAction is not None:
            out["codeAction"] = self.codeAction.to_json()
        if self.codeLens is not None:
            out["codeLens"] = self.codeLens.to_json()
        if self.documentLink is not None:
            out["documentLink"] = self.documentLink.to_json()
        if self.colorProvider is not None:
            out["colorProvider"] = self.colorProvider.to_json()
        if self.formatting is not None:
            out["formatting"] = self.formatting.to_json()
        if self.rangeFormatting is not None:
            out["rangeFormatting"] = self.rangeFormatting.to_json()
        if self.onTypeFormatting is not None:
            out["onTypeFormatting"] = self.onTypeFormatting.to_json()
        if self.rename is not None:
            out["rename"] = self.rename.to_json()
        if self.foldingRange is not None:
            out["foldingRange"] = self.foldingRange.to_json()
        if self.selectionRange is not None:
            out["selectionRange"] = self.selectionRange.to_json()
        if self.publishDiagnostics is not None:
            out["publishDiagnostics"] = self.publishDiagnostics.to_json()
        if self.callHierarchy is not None:
            out["callHierarchy"] = self.callHierarchy.to_json()
        if self.semanticTokens is not None:
            out["semanticTokens"] = self.semanticTokens.to_json()
        if self.linkedEditingRange is not None:
            out["linkedEditingRange"] = self.linkedEditingRange.to_json()
        if self.moniker is not None:
            out["moniker"] = self.moniker.to_json()
        if self.typeHierarchy is not None:
            out["typeHierarchy"] = self.typeHierarchy.to_json()
        if self.inlineValue is not None:
            out["inlineValue"] = self.inlineValue.to_json()
        if self.inlayHint is not None:
            out["inlayHint"] = self.inlayHint.to_json()
        if self.diagnostic is not None:
            out["diagnostic"] = self.diagnostic.to_json()
        return out


@dataclass
class NotebookDocumentSyncClientCapabilities():
    """
    Notebook specific client capabilities.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # Whether implementation supports dynamic registration. If this is
    # set to `true` the client supports the new
    # `(TextDocumentRegistrationOptions & StaticRegistrationOptions)`
    # return value for the corresponding server capability as well.
    dynamicRegistration: Optional[bool]
    
    # The client supports sending execution summary data per cell.
    executionSummarySupport: Optional[bool]

    def __init__(self, *, dynamicRegistration: Optional[bool] = None, executionSummarySupport: Optional[bool] = None) -> None:
        """
        - dynamicRegistration: Whether implementation supports dynamic registration. If this is
            set to `true` the client supports the new
            `(TextDocumentRegistrationOptions & StaticRegistrationOptions)`
            return value for the corresponding server capability as well.
        - executionSummarySupport: The client supports sending execution summary data per cell.
        """
        self.dynamicRegistration = dynamicRegistration
        self.executionSummarySupport = executionSummarySupport

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "NotebookDocumentSyncClientCapabilities":
        if dynamicRegistration_json := json_get_optional_bool(obj, "dynamicRegistration"):
            dynamicRegistration = dynamicRegistration_json
        else:
            dynamicRegistration = None
        if executionSummarySupport_json := json_get_optional_bool(obj, "executionSummarySupport"):
            executionSummarySupport = executionSummarySupport_json
        else:
            executionSummarySupport = None
        return cls(dynamicRegistration=dynamicRegistration, executionSummarySupport=executionSummarySupport)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.dynamicRegistration is not None:
            out["dynamicRegistration"] = self.dynamicRegistration
        if self.executionSummarySupport is not None:
            out["executionSummarySupport"] = self.executionSummarySupport
        return out


@dataclass
class NotebookDocumentClientCapabilities():
    """
    Capabilities specific to the notebook document support.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # Capabilities specific to notebook document synchronization
    # 
    # @since 3.17.0
    synchronization: "NotebookDocumentSyncClientCapabilities"

    def __init__(self, *, synchronization: "NotebookDocumentSyncClientCapabilities") -> None:
        """
        - synchronization: Capabilities specific to notebook document synchronization
            
            @since 3.17.0
        """
        self.synchronization = synchronization

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "NotebookDocumentClientCapabilities":
        synchronization = NotebookDocumentSyncClientCapabilities.from_json(json_get_object(obj, "synchronization"))
        return cls(synchronization=synchronization)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["synchronization"] = self.synchronization.to_json()
        return out


AnonymousStructure36Keys = Literal["additionalPropertiesSupport"]

def parse_AnonymousStructure36(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure36Keys, Any]:
    out: Dict[AnonymousStructure36Keys, Any] = {}
    if additionalPropertiesSupport_json := json_get_optional_bool(obj, "additionalPropertiesSupport"):
        out["additionalPropertiesSupport"] = additionalPropertiesSupport_json
    else:
        out["additionalPropertiesSupport"] = None
    return out

def write_AnonymousStructure36(obj: Dict[AnonymousStructure36Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    if obj.get("additionalPropertiesSupport") is not None:
        out["additionalPropertiesSupport"] = obj.get("additionalPropertiesSupport")
    return out


@dataclass
class ShowMessageRequestClientCapabilities():
    """
    Show message request client capabilities

    *Generated from the TypeScript documentation*
    """

    # Capabilities specific to the `MessageActionItem` type.
    messageActionItem: Optional[Dict[AnonymousStructure36Keys, Any]]

    def __init__(self, *, messageActionItem: Optional[Dict[AnonymousStructure36Keys, Any]] = None) -> None:
        """
        - messageActionItem: Capabilities specific to the `MessageActionItem` type.
        """
        self.messageActionItem = messageActionItem

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "ShowMessageRequestClientCapabilities":
        if messageActionItem_json := json_get_optional_object(obj, "messageActionItem"):
            messageActionItem = parse_AnonymousStructure36(messageActionItem_json)
        else:
            messageActionItem = None
        return cls(messageActionItem=messageActionItem)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.messageActionItem is not None:
            out["messageActionItem"] = write_AnonymousStructure36(self.messageActionItem)
        return out


@dataclass
class ShowDocumentClientCapabilities():
    """
    Client capabilities for the showDocument request.
    
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # The client has support for the showDocument
    # request.
    support: bool

    def __init__(self, *, support: bool) -> None:
        """
        - support: The client has support for the showDocument
            request.
        """
        self.support = support

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "ShowDocumentClientCapabilities":
        support = json_get_bool(obj, "support")
        return cls(support=support)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["support"] = self.support
        return out


@dataclass
class WindowClientCapabilities():
    """


    *Generated from the TypeScript documentation*
    """

    # It indicates whether the client supports server initiated
    # progress using the `window/workDoneProgress/create` request.
    # 
    # The capability also controls Whether client supports handling
    # of progress notifications. If set servers are allowed to report a
    # `workDoneProgress` property in the request specific server
    # capabilities.
    # 
    # @since 3.15.0
    workDoneProgress: Optional[bool]
    
    # Capabilities specific to the showMessage request.
    # 
    # @since 3.16.0
    showMessage: Optional["ShowMessageRequestClientCapabilities"]
    
    # Capabilities specific to the showDocument request.
    # 
    # @since 3.16.0
    showDocument: Optional["ShowDocumentClientCapabilities"]

    def __init__(self, *, workDoneProgress: Optional[bool] = None, showMessage: Optional["ShowMessageRequestClientCapabilities"] = None, showDocument: Optional["ShowDocumentClientCapabilities"] = None) -> None:
        """
        - workDoneProgress: It indicates whether the client supports server initiated
            progress using the `window/workDoneProgress/create` request.
            
            The capability also controls Whether client supports handling
            of progress notifications. If set servers are allowed to report a
            `workDoneProgress` property in the request specific server
            capabilities.
            
            @since 3.15.0
        - showMessage: Capabilities specific to the showMessage request.
            
            @since 3.16.0
        - showDocument: Capabilities specific to the showDocument request.
            
            @since 3.16.0
        """
        self.workDoneProgress = workDoneProgress
        self.showMessage = showMessage
        self.showDocument = showDocument

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "WindowClientCapabilities":
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        if showMessage_json := json_get_optional_object(obj, "showMessage"):
            showMessage = ShowMessageRequestClientCapabilities.from_json(showMessage_json)
        else:
            showMessage = None
        if showDocument_json := json_get_optional_object(obj, "showDocument"):
            showDocument = ShowDocumentClientCapabilities.from_json(showDocument_json)
        else:
            showDocument = None
        return cls(workDoneProgress=workDoneProgress, showMessage=showMessage, showDocument=showDocument)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        if self.showMessage is not None:
            out["showMessage"] = self.showMessage.to_json()
        if self.showDocument is not None:
            out["showDocument"] = self.showDocument.to_json()
        return out


AnonymousStructure16Keys = Literal["cancel","retryOnContentModified"]

def parse_AnonymousStructure16(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure16Keys, Any]:
    out: Dict[AnonymousStructure16Keys, Any] = {}
    out["cancel"] = json_get_bool(obj, "cancel")
    out["retryOnContentModified"] = [json_assert_type_string(i) for i in json_get_array(obj, "retryOnContentModified")]
    return out

def write_AnonymousStructure16(obj: Dict[AnonymousStructure16Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    out["cancel"] = obj["cancel"]
    out["retryOnContentModified"] = [i for i in obj["retryOnContentModified"]]
    return out


@dataclass
class RegularExpressionsClientCapabilities():
    """
    Client capabilities specific to regular expressions.
    
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # The engine's name.
    engine: str
    
    # The engine's version.
    version: Optional[str]

    def __init__(self, *, engine: str, version: Optional[str] = None) -> None:
        """
        - engine: The engine's name.
        - version: The engine's version.
        """
        self.engine = engine
        self.version = version

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "RegularExpressionsClientCapabilities":
        engine = json_get_string(obj, "engine")
        if version_json := json_get_optional_string(obj, "version"):
            version = version_json
        else:
            version = None
        return cls(engine=engine, version=version)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["engine"] = self.engine
        if self.version is not None:
            out["version"] = self.version
        return out


@dataclass
class MarkdownClientCapabilities():
    """
    Client capabilities specific to the used markdown parser.
    
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # The name of the parser.
    parser: str
    
    # The version of the parser.
    version: Optional[str]
    
    # A list of HTML tags that the client allows / supports in
    # Markdown.
    # 
    # @since 3.17.0
    allowedTags: Optional[List[str]]

    def __init__(self, *, parser: str, version: Optional[str] = None, allowedTags: Optional[List[str]] = None) -> None:
        """
        - parser: The name of the parser.
        - version: The version of the parser.
        - allowedTags: A list of HTML tags that the client allows / supports in
            Markdown.
            
            @since 3.17.0
        """
        self.parser = parser
        self.version = version
        self.allowedTags = allowedTags

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "MarkdownClientCapabilities":
        parser = json_get_string(obj, "parser")
        if version_json := json_get_optional_string(obj, "version"):
            version = version_json
        else:
            version = None
        if allowedTags_json := json_get_optional_array(obj, "allowedTags"):
            allowedTags = [json_assert_type_string(i) for i in allowedTags_json]
        else:
            allowedTags = None
        return cls(parser=parser, version=version, allowedTags=allowedTags)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["parser"] = self.parser
        if self.version is not None:
            out["version"] = self.version
        if self.allowedTags is not None:
            out["allowedTags"] = [i for i in self.allowedTags]
        return out


@dataclass
class GeneralClientCapabilities():
    """
    General client capabilities.
    
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # Client capability that signals how the client
    # handles stale requests (e.g. a request
    # for which the client will not process the response
    # anymore since the information is outdated).
    # 
    # @since 3.17.0
    staleRequestSupport: Optional[Dict[AnonymousStructure16Keys, Any]]
    
    # Client capabilities specific to regular expressions.
    # 
    # @since 3.16.0
    regularExpressions: Optional["RegularExpressionsClientCapabilities"]
    
    # Client capabilities specific to the client's markdown parser.
    # 
    # @since 3.16.0
    markdown: Optional["MarkdownClientCapabilities"]
    
    # The position encodings supported by the client. Client and server
    # have to agree on the same position encoding to ensure that offsets
    # (e.g. character position in a line) are interpreted the same on both
    # sides.
    # 
    # To keep the protocol backwards compatible the following applies: if
    # the value 'utf-16' is missing from the array of position encodings
    # servers can assume that the client supports UTF-16. UTF-16 is
    # therefore a mandatory encoding.
    # 
    # If omitted it defaults to ['utf-16'].
    # 
    # Implementation considerations: since the conversion from one encoding
    # into another requires the content of the file / line the conversion
    # is best done where the file is read which is usually on the server
    # side.
    # 
    # @since 3.17.0
    positionEncodings: Optional[List["PositionEncodingKind"]]

    def __init__(self, *, staleRequestSupport: Optional[Dict[AnonymousStructure16Keys, Any]] = None, regularExpressions: Optional["RegularExpressionsClientCapabilities"] = None, markdown: Optional["MarkdownClientCapabilities"] = None, positionEncodings: Optional[List["PositionEncodingKind"]] = None) -> None:
        """
        - staleRequestSupport: Client capability that signals how the client
            handles stale requests (e.g. a request
            for which the client will not process the response
            anymore since the information is outdated).
            
            @since 3.17.0
        - regularExpressions: Client capabilities specific to regular expressions.
            
            @since 3.16.0
        - markdown: Client capabilities specific to the client's markdown parser.
            
            @since 3.16.0
        - positionEncodings: The position encodings supported by the client. Client and server
            have to agree on the same position encoding to ensure that offsets
            (e.g. character position in a line) are interpreted the same on both
            sides.
            
            To keep the protocol backwards compatible the following applies: if
            the value 'utf-16' is missing from the array of position encodings
            servers can assume that the client supports UTF-16. UTF-16 is
            therefore a mandatory encoding.
            
            If omitted it defaults to ['utf-16'].
            
            Implementation considerations: since the conversion from one encoding
            into another requires the content of the file / line the conversion
            is best done where the file is read which is usually on the server
            side.
            
            @since 3.17.0
        """
        self.staleRequestSupport = staleRequestSupport
        self.regularExpressions = regularExpressions
        self.markdown = markdown
        self.positionEncodings = positionEncodings

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "GeneralClientCapabilities":
        if staleRequestSupport_json := json_get_optional_object(obj, "staleRequestSupport"):
            staleRequestSupport = parse_AnonymousStructure16(staleRequestSupport_json)
        else:
            staleRequestSupport = None
        if regularExpressions_json := json_get_optional_object(obj, "regularExpressions"):
            regularExpressions = RegularExpressionsClientCapabilities.from_json(regularExpressions_json)
        else:
            regularExpressions = None
        if markdown_json := json_get_optional_object(obj, "markdown"):
            markdown = MarkdownClientCapabilities.from_json(markdown_json)
        else:
            markdown = None
        if positionEncodings_json := json_get_optional_array(obj, "positionEncodings"):
            positionEncodings = [PositionEncodingKind(json_assert_type_string(i)) for i in positionEncodings_json]
        else:
            positionEncodings = None
        return cls(staleRequestSupport=staleRequestSupport, regularExpressions=regularExpressions, markdown=markdown, positionEncodings=positionEncodings)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.staleRequestSupport is not None:
            out["staleRequestSupport"] = write_AnonymousStructure16(self.staleRequestSupport)
        if self.regularExpressions is not None:
            out["regularExpressions"] = self.regularExpressions.to_json()
        if self.markdown is not None:
            out["markdown"] = self.markdown.to_json()
        if self.positionEncodings is not None:
            out["positionEncodings"] = [i.value for i in self.positionEncodings]
        return out


@dataclass
class ClientCapabilities():
    """
    Defines the capabilities provided by the client.

    *Generated from the TypeScript documentation*
    """

    # Workspace specific client capabilities.
    workspace: Optional["WorkspaceClientCapabilities"]
    
    # Text document specific client capabilities.
    textDocument: Optional["TextDocumentClientCapabilities"]
    
    # Capabilities specific to the notebook document support.
    # 
    # @since 3.17.0
    notebookDocument: Optional["NotebookDocumentClientCapabilities"]
    
    # Window specific client capabilities.
    window: Optional["WindowClientCapabilities"]
    
    # General client capabilities.
    # 
    # @since 3.16.0
    general: Optional["GeneralClientCapabilities"]
    
    # Experimental client capabilities.
    experimental: Optional["LSPAny"]

    def __init__(self, *, workspace: Optional["WorkspaceClientCapabilities"] = None, textDocument: Optional["TextDocumentClientCapabilities"] = None, notebookDocument: Optional["NotebookDocumentClientCapabilities"] = None, window: Optional["WindowClientCapabilities"] = None, general: Optional["GeneralClientCapabilities"] = None, experimental: Optional["LSPAny"] = None) -> None:
        """
        - workspace: Workspace specific client capabilities.
        - textDocument: Text document specific client capabilities.
        - notebookDocument: Capabilities specific to the notebook document support.
            
            @since 3.17.0
        - window: Window specific client capabilities.
        - general: General client capabilities.
            
            @since 3.16.0
        - experimental: Experimental client capabilities.
        """
        self.workspace = workspace
        self.textDocument = textDocument
        self.notebookDocument = notebookDocument
        self.window = window
        self.general = general
        self.experimental = experimental

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "ClientCapabilities":
        if workspace_json := json_get_optional_object(obj, "workspace"):
            workspace = WorkspaceClientCapabilities.from_json(workspace_json)
        else:
            workspace = None
        if textDocument_json := json_get_optional_object(obj, "textDocument"):
            textDocument = TextDocumentClientCapabilities.from_json(textDocument_json)
        else:
            textDocument = None
        if notebookDocument_json := json_get_optional_object(obj, "notebookDocument"):
            notebookDocument = NotebookDocumentClientCapabilities.from_json(notebookDocument_json)
        else:
            notebookDocument = None
        if window_json := json_get_optional_object(obj, "window"):
            window = WindowClientCapabilities.from_json(window_json)
        else:
            window = None
        if general_json := json_get_optional_object(obj, "general"):
            general = GeneralClientCapabilities.from_json(general_json)
        else:
            general = None
        if experimental_json := obj.get("experimental"):
            experimental = parse_LSPAny(experimental_json)
        else:
            experimental = None
        return cls(workspace=workspace, textDocument=textDocument, notebookDocument=notebookDocument, window=window, general=general, experimental=experimental)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workspace is not None:
            out["workspace"] = self.workspace.to_json()
        if self.textDocument is not None:
            out["textDocument"] = self.textDocument.to_json()
        if self.notebookDocument is not None:
            out["notebookDocument"] = self.notebookDocument.to_json()
        if self.window is not None:
            out["window"] = self.window.to_json()
        if self.general is not None:
            out["general"] = self.general.to_json()
        if self.experimental is not None:
            out["experimental"] = write_LSPAny(self.experimental)
        return out


@dataclass
class _InitializeParams():
    """
    The initialize parameters

    *Generated from the TypeScript documentation*
    """

    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]
    
    # The process Id of the parent process that started
    # the server.
    # 
    # Is `null` if the process has not been started by another process.
    # If the parent process is not alive then the server should exit.
    processId: Union[int, None]
    
    # Information about the client
    # 
    # @since 3.15.0
    clientInfo: Optional[Dict[AnonymousStructure10Keys, Any]]
    
    # The locale the client is currently showing the user interface
    # in. This must not necessarily be the locale of the operating
    # system.
    # 
    # Uses IETF language tags as the value's syntax
    # (See https://en.wikipedia.org/wiki/IETF_language_tag)
    # 
    # @since 3.16.0
    locale: Optional[str]
    
    # The rootPath of the workspace. Is null
    # if no folder is open.
    # 
    # @deprecated in favour of rootUri.
    rootPath: Optional[Union[str, None]]
    
    # The rootUri of the workspace. Is null if no
    # folder is open. If both `rootPath` and `rootUri` are set
    # `rootUri` wins.
    # 
    # @deprecated in favour of workspaceFolders.
    rootUri: Union[str, None]
    
    # The capabilities provided by the client (editor or tool)
    capabilities: "ClientCapabilities"
    
    # User provided initialization options.
    initializationOptions: Optional["LSPAny"]
    
    # The initial trace setting. If omitted trace is disabled ('off').
    trace: Optional[Union[str, str, str, str]]

    def __init__(self, *, workDoneToken: Optional["ProgressToken"] = None, processId: Union[int, None], clientInfo: Optional[Dict[AnonymousStructure10Keys, Any]] = None, locale: Optional[str] = None, rootPath: Optional[Union[str, None]] = None, rootUri: Union[str, None], capabilities: "ClientCapabilities", initializationOptions: Optional["LSPAny"] = None, trace: Optional[Union[str, str, str, str]] = None) -> None:
        """
        - workDoneToken: An optional token that a server can use to report work done progress.
        - processId: The process Id of the parent process that started
            the server.
            
            Is `null` if the process has not been started by another process.
            If the parent process is not alive then the server should exit.
        - clientInfo: Information about the client
            
            @since 3.15.0
        - locale: The locale the client is currently showing the user interface
            in. This must not necessarily be the locale of the operating
            system.
            
            Uses IETF language tags as the value's syntax
            (See https://en.wikipedia.org/wiki/IETF_language_tag)
            
            @since 3.16.0
        - rootPath: The rootPath of the workspace. Is null
            if no folder is open.
            
            @deprecated in favour of rootUri.
        - rootUri: The rootUri of the workspace. Is null if no
            folder is open. If both `rootPath` and `rootUri` are set
            `rootUri` wins.
            
            @deprecated in favour of workspaceFolders.
        - capabilities: The capabilities provided by the client (editor or tool)
        - initializationOptions: User provided initialization options.
        - trace: The initial trace setting. If omitted trace is disabled ('off').
        """
        self.workDoneToken = workDoneToken
        self.processId = processId
        self.clientInfo = clientInfo
        self.locale = locale
        self.rootPath = rootPath
        self.rootUri = rootUri
        self.capabilities = capabilities
        self.initializationOptions = initializationOptions
        self.trace = trace

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "_InitializeParams":
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        processId = parse_or_type(obj["processId"], (lambda v: json_assert_type_int(v), lambda v: json_assert_type_null(v)))
        if clientInfo_json := json_get_optional_object(obj, "clientInfo"):
            clientInfo = parse_AnonymousStructure10(clientInfo_json)
        else:
            clientInfo = None
        if locale_json := json_get_optional_string(obj, "locale"):
            locale = locale_json
        else:
            locale = None
        if rootPath_json := obj.get("rootPath"):
            rootPath = parse_or_type(rootPath_json, (lambda v: json_assert_type_string(v), lambda v: json_assert_type_null(v)))
        else:
            rootPath = None
        rootUri = parse_or_type(obj["rootUri"], (lambda v: json_assert_type_string(v), lambda v: json_assert_type_null(v)))
        capabilities = ClientCapabilities.from_json(json_get_object(obj, "capabilities"))
        if initializationOptions_json := obj.get("initializationOptions"):
            initializationOptions = parse_LSPAny(initializationOptions_json)
        else:
            initializationOptions = None
        if trace_json := obj.get("trace"):
            trace = parse_or_type(trace_json, (lambda v: match_string(json_assert_type_string(v), "off"), lambda v: match_string(json_assert_type_string(v), "messages"), lambda v: match_string(json_assert_type_string(v), "compact"), lambda v: match_string(json_assert_type_string(v), "verbose")))
        else:
            trace = None
        return cls(workDoneToken=workDoneToken, processId=processId, clientInfo=clientInfo, locale=locale, rootPath=rootPath, rootUri=rootUri, capabilities=capabilities, initializationOptions=initializationOptions, trace=trace)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        out["processId"] = write_or_type(self.processId, (lambda i: isinstance(i, int), lambda i: i is None), (lambda i: i, lambda i: i))
        if self.clientInfo is not None:
            out["clientInfo"] = write_AnonymousStructure10(self.clientInfo)
        if self.locale is not None:
            out["locale"] = self.locale
        if self.rootPath is not None:
            out["rootPath"] = write_or_type(self.rootPath, (lambda i: isinstance(i, str), lambda i: i is None), (lambda i: i, lambda i: i))
        out["rootUri"] = write_or_type(self.rootUri, (lambda i: isinstance(i, str), lambda i: i is None), (lambda i: i, lambda i: i))
        out["capabilities"] = self.capabilities.to_json()
        if self.initializationOptions is not None:
            out["initializationOptions"] = write_LSPAny(self.initializationOptions)
        if self.trace is not None:
            out["trace"] = write_or_type(self.trace, (lambda i: i == "off", lambda i: i == "messages", lambda i: i == "compact", lambda i: i == "verbose"), (lambda i: "off", lambda i: "messages", lambda i: "compact", lambda i: "verbose"))
        return out


@dataclass
class WorkspaceFoldersInitializeParams():
    """


    *Generated from the TypeScript documentation*
    """

    # The workspace folders configured in the client when the server starts.
    # 
    # This property is only available if the client supports workspace folders.
    # It can be `null` if the client supports workspace folders but none are
    # configured.
    # 
    # @since 3.6.0
    workspaceFolders: Optional[Union[List["WorkspaceFolder"], None]]

    def __init__(self, *, workspaceFolders: Optional[Union[List["WorkspaceFolder"], None]] = None) -> None:
        """
        - workspaceFolders: The workspace folders configured in the client when the server starts.
            
            This property is only available if the client supports workspace folders.
            It can be `null` if the client supports workspace folders but none are
            configured.
            
            @since 3.6.0
        """
        self.workspaceFolders = workspaceFolders

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "WorkspaceFoldersInitializeParams":
        if workspaceFolders_json := obj.get("workspaceFolders"):
            workspaceFolders = parse_or_type(workspaceFolders_json, (lambda v: [WorkspaceFolder.from_json(json_assert_type_object(i)) for i in json_assert_type_array(v)], lambda v: json_assert_type_null(v)))
        else:
            workspaceFolders = None
        return cls(workspaceFolders=workspaceFolders)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workspaceFolders is not None:
            out["workspaceFolders"] = write_or_type(self.workspaceFolders, (lambda i: isinstance(i, List) and (len(i) == 0 or (isinstance(i[0], WorkspaceFolder))), lambda i: i is None), (lambda i: [i.to_json() for i in i], lambda i: i))
        return out


@dataclass
class InitializeParams(_InitializeParams, WorkspaceFoldersInitializeParams):
    """


    *Generated from the TypeScript documentation*
    """

    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]
    
    # The process Id of the parent process that started
    # the server.
    # 
    # Is `null` if the process has not been started by another process.
    # If the parent process is not alive then the server should exit.
    processId: Union[int, None]
    
    # Information about the client
    # 
    # @since 3.15.0
    clientInfo: Optional[Dict[AnonymousStructure10Keys, Any]]
    
    # The locale the client is currently showing the user interface
    # in. This must not necessarily be the locale of the operating
    # system.
    # 
    # Uses IETF language tags as the value's syntax
    # (See https://en.wikipedia.org/wiki/IETF_language_tag)
    # 
    # @since 3.16.0
    locale: Optional[str]
    
    # The rootPath of the workspace. Is null
    # if no folder is open.
    # 
    # @deprecated in favour of rootUri.
    rootPath: Optional[Union[str, None]]
    
    # The rootUri of the workspace. Is null if no
    # folder is open. If both `rootPath` and `rootUri` are set
    # `rootUri` wins.
    # 
    # @deprecated in favour of workspaceFolders.
    rootUri: Union[str, None]
    
    # The capabilities provided by the client (editor or tool)
    capabilities: "ClientCapabilities"
    
    # User provided initialization options.
    initializationOptions: Optional["LSPAny"]
    
    # The initial trace setting. If omitted trace is disabled ('off').
    trace: Optional[Union[str, str, str, str]]
    
    # The workspace folders configured in the client when the server starts.
    # 
    # This property is only available if the client supports workspace folders.
    # It can be `null` if the client supports workspace folders but none are
    # configured.
    # 
    # @since 3.6.0
    workspaceFolders: Optional[Union[List["WorkspaceFolder"], None]]

    def __init__(self, *, workDoneToken: Optional["ProgressToken"] = None, processId: Union[int, None], clientInfo: Optional[Dict[AnonymousStructure10Keys, Any]] = None, locale: Optional[str] = None, rootPath: Optional[Union[str, None]] = None, rootUri: Union[str, None], capabilities: "ClientCapabilities", initializationOptions: Optional["LSPAny"] = None, trace: Optional[Union[str, str, str, str]] = None, workspaceFolders: Optional[Union[List["WorkspaceFolder"], None]] = None) -> None:
        """
        - workDoneToken: An optional token that a server can use to report work done progress.
        - processId: The process Id of the parent process that started
            the server.
            
            Is `null` if the process has not been started by another process.
            If the parent process is not alive then the server should exit.
        - clientInfo: Information about the client
            
            @since 3.15.0
        - locale: The locale the client is currently showing the user interface
            in. This must not necessarily be the locale of the operating
            system.
            
            Uses IETF language tags as the value's syntax
            (See https://en.wikipedia.org/wiki/IETF_language_tag)
            
            @since 3.16.0
        - rootPath: The rootPath of the workspace. Is null
            if no folder is open.
            
            @deprecated in favour of rootUri.
        - rootUri: The rootUri of the workspace. Is null if no
            folder is open. If both `rootPath` and `rootUri` are set
            `rootUri` wins.
            
            @deprecated in favour of workspaceFolders.
        - capabilities: The capabilities provided by the client (editor or tool)
        - initializationOptions: User provided initialization options.
        - trace: The initial trace setting. If omitted trace is disabled ('off').
        - workspaceFolders: The workspace folders configured in the client when the server starts.
            
            This property is only available if the client supports workspace folders.
            It can be `null` if the client supports workspace folders but none are
            configured.
            
            @since 3.6.0
        """
        self.workDoneToken = workDoneToken
        self.processId = processId
        self.clientInfo = clientInfo
        self.locale = locale
        self.rootPath = rootPath
        self.rootUri = rootUri
        self.capabilities = capabilities
        self.initializationOptions = initializationOptions
        self.trace = trace
        self.workspaceFolders = workspaceFolders

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "InitializeParams":
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        processId = parse_or_type(obj["processId"], (lambda v: json_assert_type_int(v), lambda v: json_assert_type_null(v)))
        if clientInfo_json := json_get_optional_object(obj, "clientInfo"):
            clientInfo = parse_AnonymousStructure10(clientInfo_json)
        else:
            clientInfo = None
        if locale_json := json_get_optional_string(obj, "locale"):
            locale = locale_json
        else:
            locale = None
        if rootPath_json := obj.get("rootPath"):
            rootPath = parse_or_type(rootPath_json, (lambda v: json_assert_type_string(v), lambda v: json_assert_type_null(v)))
        else:
            rootPath = None
        rootUri = parse_or_type(obj["rootUri"], (lambda v: json_assert_type_string(v), lambda v: json_assert_type_null(v)))
        capabilities = ClientCapabilities.from_json(json_get_object(obj, "capabilities"))
        if initializationOptions_json := obj.get("initializationOptions"):
            initializationOptions = parse_LSPAny(initializationOptions_json)
        else:
            initializationOptions = None
        if trace_json := obj.get("trace"):
            trace = parse_or_type(trace_json, (lambda v: match_string(json_assert_type_string(v), "off"), lambda v: match_string(json_assert_type_string(v), "messages"), lambda v: match_string(json_assert_type_string(v), "compact"), lambda v: match_string(json_assert_type_string(v), "verbose")))
        else:
            trace = None
        if workspaceFolders_json := obj.get("workspaceFolders"):
            workspaceFolders = parse_or_type(workspaceFolders_json, (lambda v: [WorkspaceFolder.from_json(json_assert_type_object(i)) for i in json_assert_type_array(v)], lambda v: json_assert_type_null(v)))
        else:
            workspaceFolders = None
        return cls(workDoneToken=workDoneToken, processId=processId, clientInfo=clientInfo, locale=locale, rootPath=rootPath, rootUri=rootUri, capabilities=capabilities, initializationOptions=initializationOptions, trace=trace, workspaceFolders=workspaceFolders)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        out["processId"] = write_or_type(self.processId, (lambda i: isinstance(i, int), lambda i: i is None), (lambda i: i, lambda i: i))
        if self.clientInfo is not None:
            out["clientInfo"] = write_AnonymousStructure10(self.clientInfo)
        if self.locale is not None:
            out["locale"] = self.locale
        if self.rootPath is not None:
            out["rootPath"] = write_or_type(self.rootPath, (lambda i: isinstance(i, str), lambda i: i is None), (lambda i: i, lambda i: i))
        out["rootUri"] = write_or_type(self.rootUri, (lambda i: isinstance(i, str), lambda i: i is None), (lambda i: i, lambda i: i))
        out["capabilities"] = self.capabilities.to_json()
        if self.initializationOptions is not None:
            out["initializationOptions"] = write_LSPAny(self.initializationOptions)
        if self.trace is not None:
            out["trace"] = write_or_type(self.trace, (lambda i: i == "off", lambda i: i == "messages", lambda i: i == "compact", lambda i: i == "verbose"), (lambda i: "off", lambda i: "messages", lambda i: "compact", lambda i: "verbose"))
        if self.workspaceFolders is not None:
            out["workspaceFolders"] = write_or_type(self.workspaceFolders, (lambda i: isinstance(i, List) and (len(i) == 0 or (isinstance(i[0], WorkspaceFolder))), lambda i: i is None), (lambda i: [i.to_json() for i in i], lambda i: i))
        return out


@dataclass
class SaveOptions():
    """
    Save options.

    *Generated from the TypeScript documentation*
    """

    # The client is supposed to include the content on save.
    includeText: Optional[bool]

    def __init__(self, *, includeText: Optional[bool] = None) -> None:
        """
        - includeText: The client is supposed to include the content on save.
        """
        self.includeText = includeText

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "SaveOptions":
        if includeText_json := json_get_optional_bool(obj, "includeText"):
            includeText = includeText_json
        else:
            includeText = None
        return cls(includeText=includeText)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.includeText is not None:
            out["includeText"] = self.includeText
        return out


@dataclass
class TextDocumentSyncOptions():
    """


    *Generated from the TypeScript documentation*
    """

    # Open and close notifications are sent to the server. If omitted open close notification should not
    # be sent.
    openClose: Optional[bool]
    
    # Change notifications are sent to the server. See TextDocumentSyncKind.None, TextDocumentSyncKind.Full
    # and TextDocumentSyncKind.Incremental. If omitted it defaults to TextDocumentSyncKind.None.
    change: Optional["TextDocumentSyncKind"]
    
    # If present will save notifications are sent to the server. If omitted the notification should not be
    # sent.
    willSave: Optional[bool]
    
    # If present will save wait until requests are sent to the server. If omitted the request should not be
    # sent.
    willSaveWaitUntil: Optional[bool]
    
    # If present save notifications are sent to the server. If omitted the notification should not be
    # sent.
    save: Optional[Union[bool, "SaveOptions"]]

    def __init__(self, *, openClose: Optional[bool] = None, change: Optional["TextDocumentSyncKind"] = None, willSave: Optional[bool] = None, willSaveWaitUntil: Optional[bool] = None, save: Optional[Union[bool, "SaveOptions"]] = None) -> None:
        """
        - openClose: Open and close notifications are sent to the server. If omitted open close notification should not
            be sent.
        - change: Change notifications are sent to the server. See TextDocumentSyncKind.None, TextDocumentSyncKind.Full
            and TextDocumentSyncKind.Incremental. If omitted it defaults to TextDocumentSyncKind.None.
        - willSave: If present will save notifications are sent to the server. If omitted the notification should not be
            sent.
        - willSaveWaitUntil: If present will save wait until requests are sent to the server. If omitted the request should not be
            sent.
        - save: If present save notifications are sent to the server. If omitted the notification should not be
            sent.
        """
        self.openClose = openClose
        self.change = change
        self.willSave = willSave
        self.willSaveWaitUntil = willSaveWaitUntil
        self.save = save

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "TextDocumentSyncOptions":
        if openClose_json := json_get_optional_bool(obj, "openClose"):
            openClose = openClose_json
        else:
            openClose = None
        if change_json := json_get_optional_int(obj, "change"):
            change = TextDocumentSyncKind(change_json)
        else:
            change = None
        if willSave_json := json_get_optional_bool(obj, "willSave"):
            willSave = willSave_json
        else:
            willSave = None
        if willSaveWaitUntil_json := json_get_optional_bool(obj, "willSaveWaitUntil"):
            willSaveWaitUntil = willSaveWaitUntil_json
        else:
            willSaveWaitUntil = None
        if save_json := obj.get("save"):
            save = parse_or_type(save_json, (lambda v: json_assert_type_bool(v), lambda v: SaveOptions.from_json(json_assert_type_object(v))))
        else:
            save = None
        return cls(openClose=openClose, change=change, willSave=willSave, willSaveWaitUntil=willSaveWaitUntil, save=save)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.openClose is not None:
            out["openClose"] = self.openClose
        if self.change is not None:
            out["change"] = self.change.value
        if self.willSave is not None:
            out["willSave"] = self.willSave
        if self.willSaveWaitUntil is not None:
            out["willSaveWaitUntil"] = self.willSaveWaitUntil
        if self.save is not None:
            out["save"] = write_or_type(self.save, (lambda i: isinstance(i, bool), lambda i: isinstance(i, SaveOptions)), (lambda i: i, lambda i: i.to_json()))
        return out


AnonymousStructure13Keys = Literal["language"]

def parse_AnonymousStructure13(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure13Keys, Any]:
    out: Dict[AnonymousStructure13Keys, Any] = {}
    out["language"] = json_get_string(obj, "language")
    return out

def write_AnonymousStructure13(obj: Dict[AnonymousStructure13Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    out["language"] = obj["language"]
    return out


AnonymousStructure14Keys = Literal["notebook","cells"]

def parse_AnonymousStructure14(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure14Keys, Any]:
    out: Dict[AnonymousStructure14Keys, Any] = {}
    out["notebook"] = parse_or_type(obj["notebook"], (lambda v: json_assert_type_string(v), lambda v: parse_NotebookDocumentFilter((v))))
    if cells_json := json_get_optional_array(obj, "cells"):
        out["cells"] = [parse_AnonymousStructure13(json_assert_type_object(i)) for i in cells_json]
    else:
        out["cells"] = None
    return out

def write_AnonymousStructure14(obj: Dict[AnonymousStructure14Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    out["notebook"] = write_or_type(obj["notebook"], (lambda i: isinstance(i, str), lambda i: (isinstance(i, Dict) and "notebookType" in i.keys()) or (isinstance(i, Dict) and "scheme" in i.keys()) or (isinstance(i, Dict) and "pattern" in i.keys())), (lambda i: i, lambda i: write_NotebookDocumentFilter(i)))
    if obj.get("cells") is not None:
        out["cells"] = [write_AnonymousStructure13(i) for i in obj.get("cells")]
    return out


AnonymousStructure15Keys = Literal["notebook","cells"]

def parse_AnonymousStructure15(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure15Keys, Any]:
    out: Dict[AnonymousStructure15Keys, Any] = {}
    if notebook_json := obj.get("notebook"):
        out["notebook"] = parse_or_type(notebook_json, (lambda v: json_assert_type_string(v), lambda v: parse_NotebookDocumentFilter((v))))
    else:
        out["notebook"] = None
    out["cells"] = [parse_AnonymousStructure13(json_assert_type_object(i)) for i in json_get_array(obj, "cells")]
    return out

def write_AnonymousStructure15(obj: Dict[AnonymousStructure15Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    if obj.get("notebook") is not None:
        out["notebook"] = write_or_type(obj.get("notebook"), (lambda i: isinstance(i, str), lambda i: (isinstance(i, Dict) and "notebookType" in i.keys()) or (isinstance(i, Dict) and "scheme" in i.keys()) or (isinstance(i, Dict) and "pattern" in i.keys())), (lambda i: i, lambda i: write_NotebookDocumentFilter(i)))
    out["cells"] = [write_AnonymousStructure13(i) for i in obj["cells"]]
    return out


@dataclass
class NotebookDocumentSyncOptions():
    """
    Options specific to a notebook plus its cells
    to be synced to the server.
    
    If a selector provides a notebook document
    filter but no cell selector all cells of a
    matching notebook document will be synced.
    
    If a selector provides no notebook document
    filter but only a cell selector all notebook
    document that contain at least one matching
    cell will be synced.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # The notebooks to be synced
    notebookSelector: List[Union[Dict[AnonymousStructure14Keys, Any], Dict[AnonymousStructure15Keys, Any]]]
    
    # Whether save notification should be forwarded to
    # the server. Will only be honored if mode === `notebook`.
    save: Optional[bool]

    def __init__(self, *, notebookSelector: List[Union[Dict[AnonymousStructure14Keys, Any], Dict[AnonymousStructure15Keys, Any]]], save: Optional[bool] = None) -> None:
        """
        - notebookSelector: The notebooks to be synced
        - save: Whether save notification should be forwarded to
            the server. Will only be honored if mode === `notebook`.
        """
        self.notebookSelector = notebookSelector
        self.save = save

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "NotebookDocumentSyncOptions":
        notebookSelector = [parse_or_type((i), (lambda v: parse_AnonymousStructure14(json_assert_type_object(v)), lambda v: parse_AnonymousStructure15(json_assert_type_object(v)))) for i in json_get_array(obj, "notebookSelector")]
        if save_json := json_get_optional_bool(obj, "save"):
            save = save_json
        else:
            save = None
        return cls(notebookSelector=notebookSelector, save=save)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["notebookSelector"] = [write_or_type(i, (lambda i: isinstance(i, Dict) and "notebook" in i.keys(), lambda i: isinstance(i, Dict) and "cells" in i.keys()), (lambda i: write_AnonymousStructure14(i), lambda i: write_AnonymousStructure15(i))) for i in self.notebookSelector]
        if self.save is not None:
            out["save"] = self.save
        return out


@dataclass
class NotebookDocumentSyncRegistrationOptions(NotebookDocumentSyncOptions):
    """
    Registration options specific to a notebook.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # The notebooks to be synced
    notebookSelector: List[Union[Dict[AnonymousStructure14Keys, Any], Dict[AnonymousStructure15Keys, Any]]]
    
    # Whether save notification should be forwarded to
    # the server. Will only be honored if mode === `notebook`.
    save: Optional[bool]
    
    # The id used to register the request. The id can be used to deregister
    # the request again. See also Registration#id.
    id: Optional[str]

    def __init__(self, *, notebookSelector: List[Union[Dict[AnonymousStructure14Keys, Any], Dict[AnonymousStructure15Keys, Any]]], save: Optional[bool] = None, id: Optional[str] = None) -> None:
        """
        - notebookSelector: The notebooks to be synced
        - save: Whether save notification should be forwarded to
            the server. Will only be honored if mode === `notebook`.
        - id: The id used to register the request. The id can be used to deregister
            the request again. See also Registration#id.
        """
        self.notebookSelector = notebookSelector
        self.save = save
        self.id = id

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "NotebookDocumentSyncRegistrationOptions":
        notebookSelector = [parse_or_type((i), (lambda v: parse_AnonymousStructure14(json_assert_type_object(v)), lambda v: parse_AnonymousStructure15(json_assert_type_object(v)))) for i in json_get_array(obj, "notebookSelector")]
        if save_json := json_get_optional_bool(obj, "save"):
            save = save_json
        else:
            save = None
        if id_json := json_get_optional_string(obj, "id"):
            id = id_json
        else:
            id = None
        return cls(notebookSelector=notebookSelector, save=save, id=id)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["notebookSelector"] = [write_or_type(i, (lambda i: isinstance(i, Dict) and "notebook" in i.keys(), lambda i: isinstance(i, Dict) and "cells" in i.keys()), (lambda i: write_AnonymousStructure14(i), lambda i: write_AnonymousStructure15(i))) for i in self.notebookSelector]
        if self.save is not None:
            out["save"] = self.save
        if self.id is not None:
            out["id"] = self.id
        return out


AnonymousStructure12Keys = Literal["labelDetailsSupport"]

def parse_AnonymousStructure12(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure12Keys, Any]:
    out: Dict[AnonymousStructure12Keys, Any] = {}
    if labelDetailsSupport_json := json_get_optional_bool(obj, "labelDetailsSupport"):
        out["labelDetailsSupport"] = labelDetailsSupport_json
    else:
        out["labelDetailsSupport"] = None
    return out

def write_AnonymousStructure12(obj: Dict[AnonymousStructure12Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    if obj.get("labelDetailsSupport") is not None:
        out["labelDetailsSupport"] = obj.get("labelDetailsSupport")
    return out


@dataclass
class CompletionOptions():
    """
    Completion options.

    *Generated from the TypeScript documentation*
    """

    workDoneProgress: Optional[bool]
    
    # Most tools trigger completion request automatically without explicitly requesting
    # it using a keyboard shortcut (e.g. Ctrl+Space). Typically they do so when the user
    # starts to type an identifier. For example if the user types `c` in a JavaScript file
    # code complete will automatically pop up present `console` besides others as a
    # completion item. Characters that make up identifiers don't need to be listed here.
    # 
    # If code complete should automatically be trigger on characters not being valid inside
    # an identifier (for example `.` in JavaScript) list them in `triggerCharacters`.
    triggerCharacters: Optional[List[str]]
    
    # The list of all possible characters that commit a completion. This field can be used
    # if clients don't support individual commit characters per completion item. See
    # `ClientCapabilities.textDocument.completion.completionItem.commitCharactersSupport`
    # 
    # If a server provides both `allCommitCharacters` and commit characters on an individual
    # completion item the ones on the completion item win.
    # 
    # @since 3.2.0
    allCommitCharacters: Optional[List[str]]
    
    # The server provides support to resolve additional
    # information for a completion item.
    resolveProvider: Optional[bool]
    
    # The server supports the following `CompletionItem` specific
    # capabilities.
    # 
    # @since 3.17.0
    completionItem: Optional[Dict[AnonymousStructure12Keys, Any]]

    def __init__(self, *, workDoneProgress: Optional[bool] = None, triggerCharacters: Optional[List[str]] = None, allCommitCharacters: Optional[List[str]] = None, resolveProvider: Optional[bool] = None, completionItem: Optional[Dict[AnonymousStructure12Keys, Any]] = None) -> None:
        """
        - triggerCharacters: Most tools trigger completion request automatically without explicitly requesting
            it using a keyboard shortcut (e.g. Ctrl+Space). Typically they do so when the user
            starts to type an identifier. For example if the user types `c` in a JavaScript file
            code complete will automatically pop up present `console` besides others as a
            completion item. Characters that make up identifiers don't need to be listed here.
            
            If code complete should automatically be trigger on characters not being valid inside
            an identifier (for example `.` in JavaScript) list them in `triggerCharacters`.
        - allCommitCharacters: The list of all possible characters that commit a completion. This field can be used
            if clients don't support individual commit characters per completion item. See
            `ClientCapabilities.textDocument.completion.completionItem.commitCharactersSupport`
            
            If a server provides both `allCommitCharacters` and commit characters on an individual
            completion item the ones on the completion item win.
            
            @since 3.2.0
        - resolveProvider: The server provides support to resolve additional
            information for a completion item.
        - completionItem: The server supports the following `CompletionItem` specific
            capabilities.
            
            @since 3.17.0
        """
        self.workDoneProgress = workDoneProgress
        self.triggerCharacters = triggerCharacters
        self.allCommitCharacters = allCommitCharacters
        self.resolveProvider = resolveProvider
        self.completionItem = completionItem

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "CompletionOptions":
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        if triggerCharacters_json := json_get_optional_array(obj, "triggerCharacters"):
            triggerCharacters = [json_assert_type_string(i) for i in triggerCharacters_json]
        else:
            triggerCharacters = None
        if allCommitCharacters_json := json_get_optional_array(obj, "allCommitCharacters"):
            allCommitCharacters = [json_assert_type_string(i) for i in allCommitCharacters_json]
        else:
            allCommitCharacters = None
        if resolveProvider_json := json_get_optional_bool(obj, "resolveProvider"):
            resolveProvider = resolveProvider_json
        else:
            resolveProvider = None
        if completionItem_json := json_get_optional_object(obj, "completionItem"):
            completionItem = parse_AnonymousStructure12(completionItem_json)
        else:
            completionItem = None
        return cls(workDoneProgress=workDoneProgress, triggerCharacters=triggerCharacters, allCommitCharacters=allCommitCharacters, resolveProvider=resolveProvider, completionItem=completionItem)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        if self.triggerCharacters is not None:
            out["triggerCharacters"] = [i for i in self.triggerCharacters]
        if self.allCommitCharacters is not None:
            out["allCommitCharacters"] = [i for i in self.allCommitCharacters]
        if self.resolveProvider is not None:
            out["resolveProvider"] = self.resolveProvider
        if self.completionItem is not None:
            out["completionItem"] = write_AnonymousStructure12(self.completionItem)
        return out


@dataclass
class HoverOptions():
    """
    Hover options.

    *Generated from the TypeScript documentation*
    """

    workDoneProgress: Optional[bool]

    def __init__(self, *, workDoneProgress: Optional[bool] = None) -> None:
        """
    
        """
        self.workDoneProgress = workDoneProgress

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "HoverOptions":
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        return cls(workDoneProgress=workDoneProgress)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        return out


@dataclass
class SignatureHelpOptions():
    """
    Server Capabilities for a [SignatureHelpRequest](#SignatureHelpRequest).

    *Generated from the TypeScript documentation*
    """

    workDoneProgress: Optional[bool]
    
    # List of characters that trigger signature help automatically.
    triggerCharacters: Optional[List[str]]
    
    # List of characters that re-trigger signature help.
    # 
    # These trigger characters are only active when signature help is already showing. All trigger characters
    # are also counted as re-trigger characters.
    # 
    # @since 3.15.0
    retriggerCharacters: Optional[List[str]]

    def __init__(self, *, workDoneProgress: Optional[bool] = None, triggerCharacters: Optional[List[str]] = None, retriggerCharacters: Optional[List[str]] = None) -> None:
        """
        - triggerCharacters: List of characters that trigger signature help automatically.
        - retriggerCharacters: List of characters that re-trigger signature help.
            
            These trigger characters are only active when signature help is already showing. All trigger characters
            are also counted as re-trigger characters.
            
            @since 3.15.0
        """
        self.workDoneProgress = workDoneProgress
        self.triggerCharacters = triggerCharacters
        self.retriggerCharacters = retriggerCharacters

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "SignatureHelpOptions":
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        if triggerCharacters_json := json_get_optional_array(obj, "triggerCharacters"):
            triggerCharacters = [json_assert_type_string(i) for i in triggerCharacters_json]
        else:
            triggerCharacters = None
        if retriggerCharacters_json := json_get_optional_array(obj, "retriggerCharacters"):
            retriggerCharacters = [json_assert_type_string(i) for i in retriggerCharacters_json]
        else:
            retriggerCharacters = None
        return cls(workDoneProgress=workDoneProgress, triggerCharacters=triggerCharacters, retriggerCharacters=retriggerCharacters)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        if self.triggerCharacters is not None:
            out["triggerCharacters"] = [i for i in self.triggerCharacters]
        if self.retriggerCharacters is not None:
            out["retriggerCharacters"] = [i for i in self.retriggerCharacters]
        return out


@dataclass
class DefinitionOptions():
    """
    Server Capabilities for a [DefinitionRequest](#DefinitionRequest).

    *Generated from the TypeScript documentation*
    """

    workDoneProgress: Optional[bool]

    def __init__(self, *, workDoneProgress: Optional[bool] = None) -> None:
        """
    
        """
        self.workDoneProgress = workDoneProgress

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DefinitionOptions":
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        return cls(workDoneProgress=workDoneProgress)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        return out


@dataclass
class ReferenceOptions():
    """
    Reference options.

    *Generated from the TypeScript documentation*
    """

    workDoneProgress: Optional[bool]

    def __init__(self, *, workDoneProgress: Optional[bool] = None) -> None:
        """
    
        """
        self.workDoneProgress = workDoneProgress

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "ReferenceOptions":
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        return cls(workDoneProgress=workDoneProgress)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        return out


@dataclass
class DocumentHighlightOptions():
    """
    Provider options for a [DocumentHighlightRequest](#DocumentHighlightRequest).

    *Generated from the TypeScript documentation*
    """

    workDoneProgress: Optional[bool]

    def __init__(self, *, workDoneProgress: Optional[bool] = None) -> None:
        """
    
        """
        self.workDoneProgress = workDoneProgress

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DocumentHighlightOptions":
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        return cls(workDoneProgress=workDoneProgress)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        return out


@dataclass
class DocumentSymbolOptions():
    """
    Provider options for a [DocumentSymbolRequest](#DocumentSymbolRequest).

    *Generated from the TypeScript documentation*
    """

    workDoneProgress: Optional[bool]
    
    # A human-readable string that is shown when multiple outlines trees
    # are shown for the same document.
    # 
    # @since 3.16.0
    label: Optional[str]

    def __init__(self, *, workDoneProgress: Optional[bool] = None, label: Optional[str] = None) -> None:
        """
        - label: A human-readable string that is shown when multiple outlines trees
            are shown for the same document.
            
            @since 3.16.0
        """
        self.workDoneProgress = workDoneProgress
        self.label = label

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DocumentSymbolOptions":
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        if label_json := json_get_optional_string(obj, "label"):
            label = label_json
        else:
            label = None
        return cls(workDoneProgress=workDoneProgress, label=label)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        if self.label is not None:
            out["label"] = self.label
        return out


@dataclass
class CodeActionOptions():
    """
    Provider options for a [CodeActionRequest](#CodeActionRequest).

    *Generated from the TypeScript documentation*
    """

    workDoneProgress: Optional[bool]
    
    # CodeActionKinds that this server may return.
    # 
    # The list of kinds may be generic, such as `CodeActionKind.Refactor`, or the server
    # may list out every specific kind they provide.
    codeActionKinds: Optional[List["CodeActionKind"]]
    
    # The server provides support to resolve additional
    # information for a code action.
    # 
    # @since 3.16.0
    resolveProvider: Optional[bool]

    def __init__(self, *, workDoneProgress: Optional[bool] = None, codeActionKinds: Optional[List["CodeActionKind"]] = None, resolveProvider: Optional[bool] = None) -> None:
        """
        - codeActionKinds: CodeActionKinds that this server may return.
            
            The list of kinds may be generic, such as `CodeActionKind.Refactor`, or the server
            may list out every specific kind they provide.
        - resolveProvider: The server provides support to resolve additional
            information for a code action.
            
            @since 3.16.0
        """
        self.workDoneProgress = workDoneProgress
        self.codeActionKinds = codeActionKinds
        self.resolveProvider = resolveProvider

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "CodeActionOptions":
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        if codeActionKinds_json := json_get_optional_array(obj, "codeActionKinds"):
            codeActionKinds = [CodeActionKind(json_assert_type_string(i)) for i in codeActionKinds_json]
        else:
            codeActionKinds = None
        if resolveProvider_json := json_get_optional_bool(obj, "resolveProvider"):
            resolveProvider = resolveProvider_json
        else:
            resolveProvider = None
        return cls(workDoneProgress=workDoneProgress, codeActionKinds=codeActionKinds, resolveProvider=resolveProvider)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        if self.codeActionKinds is not None:
            out["codeActionKinds"] = [i.value for i in self.codeActionKinds]
        if self.resolveProvider is not None:
            out["resolveProvider"] = self.resolveProvider
        return out


@dataclass
class CodeLensOptions():
    """
    Code Lens provider options of a [CodeLensRequest](#CodeLensRequest).

    *Generated from the TypeScript documentation*
    """

    workDoneProgress: Optional[bool]
    
    # Code lens has a resolve provider as well.
    resolveProvider: Optional[bool]

    def __init__(self, *, workDoneProgress: Optional[bool] = None, resolveProvider: Optional[bool] = None) -> None:
        """
        - resolveProvider: Code lens has a resolve provider as well.
        """
        self.workDoneProgress = workDoneProgress
        self.resolveProvider = resolveProvider

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "CodeLensOptions":
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        if resolveProvider_json := json_get_optional_bool(obj, "resolveProvider"):
            resolveProvider = resolveProvider_json
        else:
            resolveProvider = None
        return cls(workDoneProgress=workDoneProgress, resolveProvider=resolveProvider)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        if self.resolveProvider is not None:
            out["resolveProvider"] = self.resolveProvider
        return out


@dataclass
class DocumentLinkOptions():
    """
    Provider options for a [DocumentLinkRequest](#DocumentLinkRequest).

    *Generated from the TypeScript documentation*
    """

    workDoneProgress: Optional[bool]
    
    # Document links have a resolve provider as well.
    resolveProvider: Optional[bool]

    def __init__(self, *, workDoneProgress: Optional[bool] = None, resolveProvider: Optional[bool] = None) -> None:
        """
        - resolveProvider: Document links have a resolve provider as well.
        """
        self.workDoneProgress = workDoneProgress
        self.resolveProvider = resolveProvider

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DocumentLinkOptions":
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        if resolveProvider_json := json_get_optional_bool(obj, "resolveProvider"):
            resolveProvider = resolveProvider_json
        else:
            resolveProvider = None
        return cls(workDoneProgress=workDoneProgress, resolveProvider=resolveProvider)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        if self.resolveProvider is not None:
            out["resolveProvider"] = self.resolveProvider
        return out


@dataclass
class WorkspaceSymbolOptions():
    """
    Server capabilities for a [WorkspaceSymbolRequest](#WorkspaceSymbolRequest).

    *Generated from the TypeScript documentation*
    """

    workDoneProgress: Optional[bool]
    
    # The server provides support to resolve additional
    # information for a workspace symbol.
    # 
    # @since 3.17.0
    resolveProvider: Optional[bool]

    def __init__(self, *, workDoneProgress: Optional[bool] = None, resolveProvider: Optional[bool] = None) -> None:
        """
        - resolveProvider: The server provides support to resolve additional
            information for a workspace symbol.
            
            @since 3.17.0
        """
        self.workDoneProgress = workDoneProgress
        self.resolveProvider = resolveProvider

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "WorkspaceSymbolOptions":
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        if resolveProvider_json := json_get_optional_bool(obj, "resolveProvider"):
            resolveProvider = resolveProvider_json
        else:
            resolveProvider = None
        return cls(workDoneProgress=workDoneProgress, resolveProvider=resolveProvider)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        if self.resolveProvider is not None:
            out["resolveProvider"] = self.resolveProvider
        return out


@dataclass
class DocumentFormattingOptions():
    """
    Provider options for a [DocumentFormattingRequest](#DocumentFormattingRequest).

    *Generated from the TypeScript documentation*
    """

    workDoneProgress: Optional[bool]

    def __init__(self, *, workDoneProgress: Optional[bool] = None) -> None:
        """
    
        """
        self.workDoneProgress = workDoneProgress

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DocumentFormattingOptions":
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        return cls(workDoneProgress=workDoneProgress)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        return out


@dataclass
class DocumentRangeFormattingOptions():
    """
    Provider options for a [DocumentRangeFormattingRequest](#DocumentRangeFormattingRequest).

    *Generated from the TypeScript documentation*
    """

    workDoneProgress: Optional[bool]

    def __init__(self, *, workDoneProgress: Optional[bool] = None) -> None:
        """
    
        """
        self.workDoneProgress = workDoneProgress

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DocumentRangeFormattingOptions":
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        return cls(workDoneProgress=workDoneProgress)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        return out


@dataclass
class DocumentOnTypeFormattingOptions():
    """
    Provider options for a [DocumentOnTypeFormattingRequest](#DocumentOnTypeFormattingRequest).

    *Generated from the TypeScript documentation*
    """

    # A character on which formatting should be triggered, like `{`.
    firstTriggerCharacter: str
    
    # More trigger characters.
    moreTriggerCharacter: Optional[List[str]]

    def __init__(self, *, firstTriggerCharacter: str, moreTriggerCharacter: Optional[List[str]] = None) -> None:
        """
        - firstTriggerCharacter: A character on which formatting should be triggered, like `{`.
        - moreTriggerCharacter: More trigger characters.
        """
        self.firstTriggerCharacter = firstTriggerCharacter
        self.moreTriggerCharacter = moreTriggerCharacter

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DocumentOnTypeFormattingOptions":
        firstTriggerCharacter = json_get_string(obj, "firstTriggerCharacter")
        if moreTriggerCharacter_json := json_get_optional_array(obj, "moreTriggerCharacter"):
            moreTriggerCharacter = [json_assert_type_string(i) for i in moreTriggerCharacter_json]
        else:
            moreTriggerCharacter = None
        return cls(firstTriggerCharacter=firstTriggerCharacter, moreTriggerCharacter=moreTriggerCharacter)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["firstTriggerCharacter"] = self.firstTriggerCharacter
        if self.moreTriggerCharacter is not None:
            out["moreTriggerCharacter"] = [i for i in self.moreTriggerCharacter]
        return out


@dataclass
class RenameOptions():
    """
    Provider options for a [RenameRequest](#RenameRequest).

    *Generated from the TypeScript documentation*
    """

    workDoneProgress: Optional[bool]
    
    # Renames should be checked and tested before being executed.
    # 
    # @since version 3.12.0
    prepareProvider: Optional[bool]

    def __init__(self, *, workDoneProgress: Optional[bool] = None, prepareProvider: Optional[bool] = None) -> None:
        """
        - prepareProvider: Renames should be checked and tested before being executed.
            
            @since version 3.12.0
        """
        self.workDoneProgress = workDoneProgress
        self.prepareProvider = prepareProvider

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "RenameOptions":
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        if prepareProvider_json := json_get_optional_bool(obj, "prepareProvider"):
            prepareProvider = prepareProvider_json
        else:
            prepareProvider = None
        return cls(workDoneProgress=workDoneProgress, prepareProvider=prepareProvider)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        if self.prepareProvider is not None:
            out["prepareProvider"] = self.prepareProvider
        return out


@dataclass
class ExecuteCommandOptions():
    """
    The server capabilities of a [ExecuteCommandRequest](#ExecuteCommandRequest).

    *Generated from the TypeScript documentation*
    """

    workDoneProgress: Optional[bool]
    
    # The commands to be executed on the server
    commands: List[str]

    def __init__(self, *, workDoneProgress: Optional[bool] = None, commands: List[str]) -> None:
        """
        - commands: The commands to be executed on the server
        """
        self.workDoneProgress = workDoneProgress
        self.commands = commands

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "ExecuteCommandOptions":
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        commands = [json_assert_type_string(i) for i in json_get_array(obj, "commands")]
        return cls(workDoneProgress=workDoneProgress, commands=commands)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        out["commands"] = [i for i in self.commands]
        return out


@dataclass
class WorkspaceFoldersServerCapabilities():
    """


    *Generated from the TypeScript documentation*
    """

    # The server has support for workspace folders
    supported: Optional[bool]
    
    # Whether the server wants to receive workspace folder
    # change notifications.
    # 
    # If a string is provided the string is treated as an ID
    # under which the notification is registered on the client
    # side. The ID can be used to unregister for these events
    # using the `client/unregisterCapability` request.
    changeNotifications: Optional[Union[str, bool]]

    def __init__(self, *, supported: Optional[bool] = None, changeNotifications: Optional[Union[str, bool]] = None) -> None:
        """
        - supported: The server has support for workspace folders
        - changeNotifications: Whether the server wants to receive workspace folder
            change notifications.
            
            If a string is provided the string is treated as an ID
            under which the notification is registered on the client
            side. The ID can be used to unregister for these events
            using the `client/unregisterCapability` request.
        """
        self.supported = supported
        self.changeNotifications = changeNotifications

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "WorkspaceFoldersServerCapabilities":
        if supported_json := json_get_optional_bool(obj, "supported"):
            supported = supported_json
        else:
            supported = None
        if changeNotifications_json := obj.get("changeNotifications"):
            changeNotifications = parse_or_type(changeNotifications_json, (lambda v: json_assert_type_string(v), lambda v: json_assert_type_bool(v)))
        else:
            changeNotifications = None
        return cls(supported=supported, changeNotifications=changeNotifications)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.supported is not None:
            out["supported"] = self.supported
        if self.changeNotifications is not None:
            out["changeNotifications"] = write_or_type(self.changeNotifications, (lambda i: isinstance(i, str), lambda i: isinstance(i, bool)), (lambda i: i, lambda i: i))
        return out


@dataclass
class FileOperationOptions():
    """
    Options for notifications/requests for user operations on files.
    
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # The server is interested in receiving didCreateFiles notifications.
    didCreate: Optional["FileOperationRegistrationOptions"]
    
    # The server is interested in receiving willCreateFiles requests.
    willCreate: Optional["FileOperationRegistrationOptions"]
    
    # The server is interested in receiving didRenameFiles notifications.
    didRename: Optional["FileOperationRegistrationOptions"]
    
    # The server is interested in receiving willRenameFiles requests.
    willRename: Optional["FileOperationRegistrationOptions"]
    
    # The server is interested in receiving didDeleteFiles file notifications.
    didDelete: Optional["FileOperationRegistrationOptions"]
    
    # The server is interested in receiving willDeleteFiles file requests.
    willDelete: Optional["FileOperationRegistrationOptions"]

    def __init__(self, *, didCreate: Optional["FileOperationRegistrationOptions"] = None, willCreate: Optional["FileOperationRegistrationOptions"] = None, didRename: Optional["FileOperationRegistrationOptions"] = None, willRename: Optional["FileOperationRegistrationOptions"] = None, didDelete: Optional["FileOperationRegistrationOptions"] = None, willDelete: Optional["FileOperationRegistrationOptions"] = None) -> None:
        """
        - didCreate: The server is interested in receiving didCreateFiles notifications.
        - willCreate: The server is interested in receiving willCreateFiles requests.
        - didRename: The server is interested in receiving didRenameFiles notifications.
        - willRename: The server is interested in receiving willRenameFiles requests.
        - didDelete: The server is interested in receiving didDeleteFiles file notifications.
        - willDelete: The server is interested in receiving willDeleteFiles file requests.
        """
        self.didCreate = didCreate
        self.willCreate = willCreate
        self.didRename = didRename
        self.willRename = willRename
        self.didDelete = didDelete
        self.willDelete = willDelete

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "FileOperationOptions":
        if didCreate_json := json_get_optional_object(obj, "didCreate"):
            didCreate = FileOperationRegistrationOptions.from_json(didCreate_json)
        else:
            didCreate = None
        if willCreate_json := json_get_optional_object(obj, "willCreate"):
            willCreate = FileOperationRegistrationOptions.from_json(willCreate_json)
        else:
            willCreate = None
        if didRename_json := json_get_optional_object(obj, "didRename"):
            didRename = FileOperationRegistrationOptions.from_json(didRename_json)
        else:
            didRename = None
        if willRename_json := json_get_optional_object(obj, "willRename"):
            willRename = FileOperationRegistrationOptions.from_json(willRename_json)
        else:
            willRename = None
        if didDelete_json := json_get_optional_object(obj, "didDelete"):
            didDelete = FileOperationRegistrationOptions.from_json(didDelete_json)
        else:
            didDelete = None
        if willDelete_json := json_get_optional_object(obj, "willDelete"):
            willDelete = FileOperationRegistrationOptions.from_json(willDelete_json)
        else:
            willDelete = None
        return cls(didCreate=didCreate, willCreate=willCreate, didRename=didRename, willRename=willRename, didDelete=didDelete, willDelete=willDelete)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.didCreate is not None:
            out["didCreate"] = self.didCreate.to_json()
        if self.willCreate is not None:
            out["willCreate"] = self.willCreate.to_json()
        if self.didRename is not None:
            out["didRename"] = self.didRename.to_json()
        if self.willRename is not None:
            out["willRename"] = self.willRename.to_json()
        if self.didDelete is not None:
            out["didDelete"] = self.didDelete.to_json()
        if self.willDelete is not None:
            out["willDelete"] = self.willDelete.to_json()
        return out


AnonymousStructure11Keys = Literal["workspaceFolders","fileOperations"]

def parse_AnonymousStructure11(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure11Keys, Any]:
    out: Dict[AnonymousStructure11Keys, Any] = {}
    if workspaceFolders_json := json_get_optional_object(obj, "workspaceFolders"):
        out["workspaceFolders"] = WorkspaceFoldersServerCapabilities.from_json(workspaceFolders_json)
    else:
        out["workspaceFolders"] = None
    if fileOperations_json := json_get_optional_object(obj, "fileOperations"):
        out["fileOperations"] = FileOperationOptions.from_json(fileOperations_json)
    else:
        out["fileOperations"] = None
    return out

def write_AnonymousStructure11(obj: Dict[AnonymousStructure11Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    if obj.get("workspaceFolders") is not None:
        out["workspaceFolders"] = obj.get("workspaceFolders").to_json()
    if obj.get("fileOperations") is not None:
        out["fileOperations"] = obj.get("fileOperations").to_json()
    return out


@dataclass
class ServerCapabilities():
    """
    Defines the capabilities provided by a language
    server.

    *Generated from the TypeScript documentation*
    """

    # The position encoding the server picked from the encodings offered
    # by the client via the client capability `general.positionEncodings`.
    # 
    # If the client didn't provide any position encodings the only valid
    # value that a server can return is 'utf-16'.
    # 
    # If omitted it defaults to 'utf-16'.
    # 
    # @since 3.17.0
    positionEncoding: Optional["PositionEncodingKind"]
    
    # Defines how text documents are synced. Is either a detailed structure
    # defining each notification or for backwards compatibility the
    # TextDocumentSyncKind number.
    textDocumentSync: Optional[Union["TextDocumentSyncOptions", "TextDocumentSyncKind"]]
    
    # Defines how notebook documents are synced.
    # 
    # @since 3.17.0
    notebookDocumentSync: Optional[Union["NotebookDocumentSyncOptions", "NotebookDocumentSyncRegistrationOptions"]]
    
    # The server provides completion support.
    completionProvider: Optional["CompletionOptions"]
    
    # The server provides hover support.
    hoverProvider: Optional[Union[bool, "HoverOptions"]]
    
    # The server provides signature help support.
    signatureHelpProvider: Optional["SignatureHelpOptions"]
    
    # The server provides Goto Declaration support.
    declarationProvider: Optional[Union[bool, "DeclarationOptions", "DeclarationRegistrationOptions"]]
    
    # The server provides goto definition support.
    definitionProvider: Optional[Union[bool, "DefinitionOptions"]]
    
    # The server provides Goto Type Definition support.
    typeDefinitionProvider: Optional[Union[bool, "TypeDefinitionOptions", "TypeDefinitionRegistrationOptions"]]
    
    # The server provides Goto Implementation support.
    implementationProvider: Optional[Union[bool, "ImplementationOptions", "ImplementationRegistrationOptions"]]
    
    # The server provides find references support.
    referencesProvider: Optional[Union[bool, "ReferenceOptions"]]
    
    # The server provides document highlight support.
    documentHighlightProvider: Optional[Union[bool, "DocumentHighlightOptions"]]
    
    # The server provides document symbol support.
    documentSymbolProvider: Optional[Union[bool, "DocumentSymbolOptions"]]
    
    # The server provides code actions. CodeActionOptions may only be
    # specified if the client states that it supports
    # `codeActionLiteralSupport` in its initial `initialize` request.
    codeActionProvider: Optional[Union[bool, "CodeActionOptions"]]
    
    # The server provides code lens.
    codeLensProvider: Optional["CodeLensOptions"]
    
    # The server provides document link support.
    documentLinkProvider: Optional["DocumentLinkOptions"]
    
    # The server provides color provider support.
    colorProvider: Optional[Union[bool, "DocumentColorOptions", "DocumentColorRegistrationOptions"]]
    
    # The server provides workspace symbol support.
    workspaceSymbolProvider: Optional[Union[bool, "WorkspaceSymbolOptions"]]
    
    # The server provides document formatting.
    documentFormattingProvider: Optional[Union[bool, "DocumentFormattingOptions"]]
    
    # The server provides document range formatting.
    documentRangeFormattingProvider: Optional[Union[bool, "DocumentRangeFormattingOptions"]]
    
    # The server provides document formatting on typing.
    documentOnTypeFormattingProvider: Optional["DocumentOnTypeFormattingOptions"]
    
    # The server provides rename support. RenameOptions may only be
    # specified if the client states that it supports
    # `prepareSupport` in its initial `initialize` request.
    renameProvider: Optional[Union[bool, "RenameOptions"]]
    
    # The server provides folding provider support.
    foldingRangeProvider: Optional[Union[bool, "FoldingRangeOptions", "FoldingRangeRegistrationOptions"]]
    
    # The server provides selection range support.
    selectionRangeProvider: Optional[Union[bool, "SelectionRangeOptions", "SelectionRangeRegistrationOptions"]]
    
    # The server provides execute command support.
    executeCommandProvider: Optional["ExecuteCommandOptions"]
    
    # The server provides call hierarchy support.
    # 
    # @since 3.16.0
    callHierarchyProvider: Optional[Union[bool, "CallHierarchyOptions", "CallHierarchyRegistrationOptions"]]
    
    # The server provides linked editing range support.
    # 
    # @since 3.16.0
    linkedEditingRangeProvider: Optional[Union[bool, "LinkedEditingRangeOptions", "LinkedEditingRangeRegistrationOptions"]]
    
    # The server provides semantic tokens support.
    # 
    # @since 3.16.0
    semanticTokensProvider: Optional[Union["SemanticTokensOptions", "SemanticTokensRegistrationOptions"]]
    
    # The server provides moniker support.
    # 
    # @since 3.16.0
    monikerProvider: Optional[Union[bool, "MonikerOptions", "MonikerRegistrationOptions"]]
    
    # The server provides type hierarchy support.
    # 
    # @since 3.17.0
    typeHierarchyProvider: Optional[Union[bool, "TypeHierarchyOptions", "TypeHierarchyRegistrationOptions"]]
    
    # The server provides inline values.
    # 
    # @since 3.17.0
    inlineValueProvider: Optional[Union[bool, "InlineValueOptions", "InlineValueRegistrationOptions"]]
    
    # The server provides inlay hints.
    # 
    # @since 3.17.0
    inlayHintProvider: Optional[Union[bool, "InlayHintOptions", "InlayHintRegistrationOptions"]]
    
    # The server has support for pull model diagnostics.
    # 
    # @since 3.17.0
    diagnosticProvider: Optional[Union["DiagnosticOptions", "DiagnosticRegistrationOptions"]]
    
    # Workspace specific server capabilities.
    workspace: Optional[Dict[AnonymousStructure11Keys, Any]]
    
    # Experimental server capabilities.
    experimental: Optional["LSPAny"]

    def __init__(self, *, positionEncoding: Optional["PositionEncodingKind"] = None, textDocumentSync: Optional[Union["TextDocumentSyncOptions", "TextDocumentSyncKind"]] = None, notebookDocumentSync: Optional[Union["NotebookDocumentSyncOptions", "NotebookDocumentSyncRegistrationOptions"]] = None, completionProvider: Optional["CompletionOptions"] = None, hoverProvider: Optional[Union[bool, "HoverOptions"]] = None, signatureHelpProvider: Optional["SignatureHelpOptions"] = None, declarationProvider: Optional[Union[bool, "DeclarationOptions", "DeclarationRegistrationOptions"]] = None, definitionProvider: Optional[Union[bool, "DefinitionOptions"]] = None, typeDefinitionProvider: Optional[Union[bool, "TypeDefinitionOptions", "TypeDefinitionRegistrationOptions"]] = None, implementationProvider: Optional[Union[bool, "ImplementationOptions", "ImplementationRegistrationOptions"]] = None, referencesProvider: Optional[Union[bool, "ReferenceOptions"]] = None, documentHighlightProvider: Optional[Union[bool, "DocumentHighlightOptions"]] = None, documentSymbolProvider: Optional[Union[bool, "DocumentSymbolOptions"]] = None, codeActionProvider: Optional[Union[bool, "CodeActionOptions"]] = None, codeLensProvider: Optional["CodeLensOptions"] = None, documentLinkProvider: Optional["DocumentLinkOptions"] = None, colorProvider: Optional[Union[bool, "DocumentColorOptions", "DocumentColorRegistrationOptions"]] = None, workspaceSymbolProvider: Optional[Union[bool, "WorkspaceSymbolOptions"]] = None, documentFormattingProvider: Optional[Union[bool, "DocumentFormattingOptions"]] = None, documentRangeFormattingProvider: Optional[Union[bool, "DocumentRangeFormattingOptions"]] = None, documentOnTypeFormattingProvider: Optional["DocumentOnTypeFormattingOptions"] = None, renameProvider: Optional[Union[bool, "RenameOptions"]] = None, foldingRangeProvider: Optional[Union[bool, "FoldingRangeOptions", "FoldingRangeRegistrationOptions"]] = None, selectionRangeProvider: Optional[Union[bool, "SelectionRangeOptions", "SelectionRangeRegistrationOptions"]] = None, executeCommandProvider: Optional["ExecuteCommandOptions"] = None, callHierarchyProvider: Optional[Union[bool, "CallHierarchyOptions", "CallHierarchyRegistrationOptions"]] = None, linkedEditingRangeProvider: Optional[Union[bool, "LinkedEditingRangeOptions", "LinkedEditingRangeRegistrationOptions"]] = None, semanticTokensProvider: Optional[Union["SemanticTokensOptions", "SemanticTokensRegistrationOptions"]] = None, monikerProvider: Optional[Union[bool, "MonikerOptions", "MonikerRegistrationOptions"]] = None, typeHierarchyProvider: Optional[Union[bool, "TypeHierarchyOptions", "TypeHierarchyRegistrationOptions"]] = None, inlineValueProvider: Optional[Union[bool, "InlineValueOptions", "InlineValueRegistrationOptions"]] = None, inlayHintProvider: Optional[Union[bool, "InlayHintOptions", "InlayHintRegistrationOptions"]] = None, diagnosticProvider: Optional[Union["DiagnosticOptions", "DiagnosticRegistrationOptions"]] = None, workspace: Optional[Dict[AnonymousStructure11Keys, Any]] = None, experimental: Optional["LSPAny"] = None) -> None:
        """
        - positionEncoding: The position encoding the server picked from the encodings offered
            by the client via the client capability `general.positionEncodings`.
            
            If the client didn't provide any position encodings the only valid
            value that a server can return is 'utf-16'.
            
            If omitted it defaults to 'utf-16'.
            
            @since 3.17.0
        - textDocumentSync: Defines how text documents are synced. Is either a detailed structure
            defining each notification or for backwards compatibility the
            TextDocumentSyncKind number.
        - notebookDocumentSync: Defines how notebook documents are synced.
            
            @since 3.17.0
        - completionProvider: The server provides completion support.
        - hoverProvider: The server provides hover support.
        - signatureHelpProvider: The server provides signature help support.
        - declarationProvider: The server provides Goto Declaration support.
        - definitionProvider: The server provides goto definition support.
        - typeDefinitionProvider: The server provides Goto Type Definition support.
        - implementationProvider: The server provides Goto Implementation support.
        - referencesProvider: The server provides find references support.
        - documentHighlightProvider: The server provides document highlight support.
        - documentSymbolProvider: The server provides document symbol support.
        - codeActionProvider: The server provides code actions. CodeActionOptions may only be
            specified if the client states that it supports
            `codeActionLiteralSupport` in its initial `initialize` request.
        - codeLensProvider: The server provides code lens.
        - documentLinkProvider: The server provides document link support.
        - colorProvider: The server provides color provider support.
        - workspaceSymbolProvider: The server provides workspace symbol support.
        - documentFormattingProvider: The server provides document formatting.
        - documentRangeFormattingProvider: The server provides document range formatting.
        - documentOnTypeFormattingProvider: The server provides document formatting on typing.
        - renameProvider: The server provides rename support. RenameOptions may only be
            specified if the client states that it supports
            `prepareSupport` in its initial `initialize` request.
        - foldingRangeProvider: The server provides folding provider support.
        - selectionRangeProvider: The server provides selection range support.
        - executeCommandProvider: The server provides execute command support.
        - callHierarchyProvider: The server provides call hierarchy support.
            
            @since 3.16.0
        - linkedEditingRangeProvider: The server provides linked editing range support.
            
            @since 3.16.0
        - semanticTokensProvider: The server provides semantic tokens support.
            
            @since 3.16.0
        - monikerProvider: The server provides moniker support.
            
            @since 3.16.0
        - typeHierarchyProvider: The server provides type hierarchy support.
            
            @since 3.17.0
        - inlineValueProvider: The server provides inline values.
            
            @since 3.17.0
        - inlayHintProvider: The server provides inlay hints.
            
            @since 3.17.0
        - diagnosticProvider: The server has support for pull model diagnostics.
            
            @since 3.17.0
        - workspace: Workspace specific server capabilities.
        - experimental: Experimental server capabilities.
        """
        self.positionEncoding = positionEncoding
        self.textDocumentSync = textDocumentSync
        self.notebookDocumentSync = notebookDocumentSync
        self.completionProvider = completionProvider
        self.hoverProvider = hoverProvider
        self.signatureHelpProvider = signatureHelpProvider
        self.declarationProvider = declarationProvider
        self.definitionProvider = definitionProvider
        self.typeDefinitionProvider = typeDefinitionProvider
        self.implementationProvider = implementationProvider
        self.referencesProvider = referencesProvider
        self.documentHighlightProvider = documentHighlightProvider
        self.documentSymbolProvider = documentSymbolProvider
        self.codeActionProvider = codeActionProvider
        self.codeLensProvider = codeLensProvider
        self.documentLinkProvider = documentLinkProvider
        self.colorProvider = colorProvider
        self.workspaceSymbolProvider = workspaceSymbolProvider
        self.documentFormattingProvider = documentFormattingProvider
        self.documentRangeFormattingProvider = documentRangeFormattingProvider
        self.documentOnTypeFormattingProvider = documentOnTypeFormattingProvider
        self.renameProvider = renameProvider
        self.foldingRangeProvider = foldingRangeProvider
        self.selectionRangeProvider = selectionRangeProvider
        self.executeCommandProvider = executeCommandProvider
        self.callHierarchyProvider = callHierarchyProvider
        self.linkedEditingRangeProvider = linkedEditingRangeProvider
        self.semanticTokensProvider = semanticTokensProvider
        self.monikerProvider = monikerProvider
        self.typeHierarchyProvider = typeHierarchyProvider
        self.inlineValueProvider = inlineValueProvider
        self.inlayHintProvider = inlayHintProvider
        self.diagnosticProvider = diagnosticProvider
        self.workspace = workspace
        self.experimental = experimental

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "ServerCapabilities":
        if positionEncoding_json := json_get_optional_string(obj, "positionEncoding"):
            positionEncoding = PositionEncodingKind(positionEncoding_json)
        else:
            positionEncoding = None
        if textDocumentSync_json := obj.get("textDocumentSync"):
            textDocumentSync = parse_or_type(textDocumentSync_json, (lambda v: TextDocumentSyncOptions.from_json(json_assert_type_object(v)), lambda v: TextDocumentSyncKind(json_assert_type_int(v))))
        else:
            textDocumentSync = None
        if notebookDocumentSync_json := obj.get("notebookDocumentSync"):
            notebookDocumentSync = parse_or_type(notebookDocumentSync_json, (lambda v: NotebookDocumentSyncOptions.from_json(json_assert_type_object(v)), lambda v: NotebookDocumentSyncRegistrationOptions.from_json(json_assert_type_object(v))))
        else:
            notebookDocumentSync = None
        if completionProvider_json := json_get_optional_object(obj, "completionProvider"):
            completionProvider = CompletionOptions.from_json(completionProvider_json)
        else:
            completionProvider = None
        if hoverProvider_json := obj.get("hoverProvider"):
            hoverProvider = parse_or_type(hoverProvider_json, (lambda v: json_assert_type_bool(v), lambda v: HoverOptions.from_json(json_assert_type_object(v))))
        else:
            hoverProvider = None
        if signatureHelpProvider_json := json_get_optional_object(obj, "signatureHelpProvider"):
            signatureHelpProvider = SignatureHelpOptions.from_json(signatureHelpProvider_json)
        else:
            signatureHelpProvider = None
        if declarationProvider_json := obj.get("declarationProvider"):
            declarationProvider = parse_or_type(declarationProvider_json, (lambda v: json_assert_type_bool(v), lambda v: DeclarationOptions.from_json(json_assert_type_object(v)), lambda v: DeclarationRegistrationOptions.from_json(json_assert_type_object(v))))
        else:
            declarationProvider = None
        if definitionProvider_json := obj.get("definitionProvider"):
            definitionProvider = parse_or_type(definitionProvider_json, (lambda v: json_assert_type_bool(v), lambda v: DefinitionOptions.from_json(json_assert_type_object(v))))
        else:
            definitionProvider = None
        if typeDefinitionProvider_json := obj.get("typeDefinitionProvider"):
            typeDefinitionProvider = parse_or_type(typeDefinitionProvider_json, (lambda v: json_assert_type_bool(v), lambda v: TypeDefinitionOptions.from_json(json_assert_type_object(v)), lambda v: TypeDefinitionRegistrationOptions.from_json(json_assert_type_object(v))))
        else:
            typeDefinitionProvider = None
        if implementationProvider_json := obj.get("implementationProvider"):
            implementationProvider = parse_or_type(implementationProvider_json, (lambda v: json_assert_type_bool(v), lambda v: ImplementationOptions.from_json(json_assert_type_object(v)), lambda v: ImplementationRegistrationOptions.from_json(json_assert_type_object(v))))
        else:
            implementationProvider = None
        if referencesProvider_json := obj.get("referencesProvider"):
            referencesProvider = parse_or_type(referencesProvider_json, (lambda v: json_assert_type_bool(v), lambda v: ReferenceOptions.from_json(json_assert_type_object(v))))
        else:
            referencesProvider = None
        if documentHighlightProvider_json := obj.get("documentHighlightProvider"):
            documentHighlightProvider = parse_or_type(documentHighlightProvider_json, (lambda v: json_assert_type_bool(v), lambda v: DocumentHighlightOptions.from_json(json_assert_type_object(v))))
        else:
            documentHighlightProvider = None
        if documentSymbolProvider_json := obj.get("documentSymbolProvider"):
            documentSymbolProvider = parse_or_type(documentSymbolProvider_json, (lambda v: json_assert_type_bool(v), lambda v: DocumentSymbolOptions.from_json(json_assert_type_object(v))))
        else:
            documentSymbolProvider = None
        if codeActionProvider_json := obj.get("codeActionProvider"):
            codeActionProvider = parse_or_type(codeActionProvider_json, (lambda v: json_assert_type_bool(v), lambda v: CodeActionOptions.from_json(json_assert_type_object(v))))
        else:
            codeActionProvider = None
        if codeLensProvider_json := json_get_optional_object(obj, "codeLensProvider"):
            codeLensProvider = CodeLensOptions.from_json(codeLensProvider_json)
        else:
            codeLensProvider = None
        if documentLinkProvider_json := json_get_optional_object(obj, "documentLinkProvider"):
            documentLinkProvider = DocumentLinkOptions.from_json(documentLinkProvider_json)
        else:
            documentLinkProvider = None
        if colorProvider_json := obj.get("colorProvider"):
            colorProvider = parse_or_type(colorProvider_json, (lambda v: json_assert_type_bool(v), lambda v: DocumentColorOptions.from_json(json_assert_type_object(v)), lambda v: DocumentColorRegistrationOptions.from_json(json_assert_type_object(v))))
        else:
            colorProvider = None
        if workspaceSymbolProvider_json := obj.get("workspaceSymbolProvider"):
            workspaceSymbolProvider = parse_or_type(workspaceSymbolProvider_json, (lambda v: json_assert_type_bool(v), lambda v: WorkspaceSymbolOptions.from_json(json_assert_type_object(v))))
        else:
            workspaceSymbolProvider = None
        if documentFormattingProvider_json := obj.get("documentFormattingProvider"):
            documentFormattingProvider = parse_or_type(documentFormattingProvider_json, (lambda v: json_assert_type_bool(v), lambda v: DocumentFormattingOptions.from_json(json_assert_type_object(v))))
        else:
            documentFormattingProvider = None
        if documentRangeFormattingProvider_json := obj.get("documentRangeFormattingProvider"):
            documentRangeFormattingProvider = parse_or_type(documentRangeFormattingProvider_json, (lambda v: json_assert_type_bool(v), lambda v: DocumentRangeFormattingOptions.from_json(json_assert_type_object(v))))
        else:
            documentRangeFormattingProvider = None
        if documentOnTypeFormattingProvider_json := json_get_optional_object(obj, "documentOnTypeFormattingProvider"):
            documentOnTypeFormattingProvider = DocumentOnTypeFormattingOptions.from_json(documentOnTypeFormattingProvider_json)
        else:
            documentOnTypeFormattingProvider = None
        if renameProvider_json := obj.get("renameProvider"):
            renameProvider = parse_or_type(renameProvider_json, (lambda v: json_assert_type_bool(v), lambda v: RenameOptions.from_json(json_assert_type_object(v))))
        else:
            renameProvider = None
        if foldingRangeProvider_json := obj.get("foldingRangeProvider"):
            foldingRangeProvider = parse_or_type(foldingRangeProvider_json, (lambda v: json_assert_type_bool(v), lambda v: FoldingRangeOptions.from_json(json_assert_type_object(v)), lambda v: FoldingRangeRegistrationOptions.from_json(json_assert_type_object(v))))
        else:
            foldingRangeProvider = None
        if selectionRangeProvider_json := obj.get("selectionRangeProvider"):
            selectionRangeProvider = parse_or_type(selectionRangeProvider_json, (lambda v: json_assert_type_bool(v), lambda v: SelectionRangeOptions.from_json(json_assert_type_object(v)), lambda v: SelectionRangeRegistrationOptions.from_json(json_assert_type_object(v))))
        else:
            selectionRangeProvider = None
        if executeCommandProvider_json := json_get_optional_object(obj, "executeCommandProvider"):
            executeCommandProvider = ExecuteCommandOptions.from_json(executeCommandProvider_json)
        else:
            executeCommandProvider = None
        if callHierarchyProvider_json := obj.get("callHierarchyProvider"):
            callHierarchyProvider = parse_or_type(callHierarchyProvider_json, (lambda v: json_assert_type_bool(v), lambda v: CallHierarchyOptions.from_json(json_assert_type_object(v)), lambda v: CallHierarchyRegistrationOptions.from_json(json_assert_type_object(v))))
        else:
            callHierarchyProvider = None
        if linkedEditingRangeProvider_json := obj.get("linkedEditingRangeProvider"):
            linkedEditingRangeProvider = parse_or_type(linkedEditingRangeProvider_json, (lambda v: json_assert_type_bool(v), lambda v: LinkedEditingRangeOptions.from_json(json_assert_type_object(v)), lambda v: LinkedEditingRangeRegistrationOptions.from_json(json_assert_type_object(v))))
        else:
            linkedEditingRangeProvider = None
        if semanticTokensProvider_json := obj.get("semanticTokensProvider"):
            semanticTokensProvider = parse_or_type(semanticTokensProvider_json, (lambda v: SemanticTokensOptions.from_json(json_assert_type_object(v)), lambda v: SemanticTokensRegistrationOptions.from_json(json_assert_type_object(v))))
        else:
            semanticTokensProvider = None
        if monikerProvider_json := obj.get("monikerProvider"):
            monikerProvider = parse_or_type(monikerProvider_json, (lambda v: json_assert_type_bool(v), lambda v: MonikerOptions.from_json(json_assert_type_object(v)), lambda v: MonikerRegistrationOptions.from_json(json_assert_type_object(v))))
        else:
            monikerProvider = None
        if typeHierarchyProvider_json := obj.get("typeHierarchyProvider"):
            typeHierarchyProvider = parse_or_type(typeHierarchyProvider_json, (lambda v: json_assert_type_bool(v), lambda v: TypeHierarchyOptions.from_json(json_assert_type_object(v)), lambda v: TypeHierarchyRegistrationOptions.from_json(json_assert_type_object(v))))
        else:
            typeHierarchyProvider = None
        if inlineValueProvider_json := obj.get("inlineValueProvider"):
            inlineValueProvider = parse_or_type(inlineValueProvider_json, (lambda v: json_assert_type_bool(v), lambda v: InlineValueOptions.from_json(json_assert_type_object(v)), lambda v: InlineValueRegistrationOptions.from_json(json_assert_type_object(v))))
        else:
            inlineValueProvider = None
        if inlayHintProvider_json := obj.get("inlayHintProvider"):
            inlayHintProvider = parse_or_type(inlayHintProvider_json, (lambda v: json_assert_type_bool(v), lambda v: InlayHintOptions.from_json(json_assert_type_object(v)), lambda v: InlayHintRegistrationOptions.from_json(json_assert_type_object(v))))
        else:
            inlayHintProvider = None
        if diagnosticProvider_json := obj.get("diagnosticProvider"):
            diagnosticProvider = parse_or_type(diagnosticProvider_json, (lambda v: DiagnosticOptions.from_json(json_assert_type_object(v)), lambda v: DiagnosticRegistrationOptions.from_json(json_assert_type_object(v))))
        else:
            diagnosticProvider = None
        if workspace_json := json_get_optional_object(obj, "workspace"):
            workspace = parse_AnonymousStructure11(workspace_json)
        else:
            workspace = None
        if experimental_json := obj.get("experimental"):
            experimental = parse_LSPAny(experimental_json)
        else:
            experimental = None
        return cls(positionEncoding=positionEncoding, textDocumentSync=textDocumentSync, notebookDocumentSync=notebookDocumentSync, completionProvider=completionProvider, hoverProvider=hoverProvider, signatureHelpProvider=signatureHelpProvider, declarationProvider=declarationProvider, definitionProvider=definitionProvider, typeDefinitionProvider=typeDefinitionProvider, implementationProvider=implementationProvider, referencesProvider=referencesProvider, documentHighlightProvider=documentHighlightProvider, documentSymbolProvider=documentSymbolProvider, codeActionProvider=codeActionProvider, codeLensProvider=codeLensProvider, documentLinkProvider=documentLinkProvider, colorProvider=colorProvider, workspaceSymbolProvider=workspaceSymbolProvider, documentFormattingProvider=documentFormattingProvider, documentRangeFormattingProvider=documentRangeFormattingProvider, documentOnTypeFormattingProvider=documentOnTypeFormattingProvider, renameProvider=renameProvider, foldingRangeProvider=foldingRangeProvider, selectionRangeProvider=selectionRangeProvider, executeCommandProvider=executeCommandProvider, callHierarchyProvider=callHierarchyProvider, linkedEditingRangeProvider=linkedEditingRangeProvider, semanticTokensProvider=semanticTokensProvider, monikerProvider=monikerProvider, typeHierarchyProvider=typeHierarchyProvider, inlineValueProvider=inlineValueProvider, inlayHintProvider=inlayHintProvider, diagnosticProvider=diagnosticProvider, workspace=workspace, experimental=experimental)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.positionEncoding is not None:
            out["positionEncoding"] = self.positionEncoding.value
        if self.textDocumentSync is not None:
            out["textDocumentSync"] = write_or_type(self.textDocumentSync, (lambda i: isinstance(i, TextDocumentSyncOptions), lambda i: isinstance(i, TextDocumentSyncKind)), (lambda i: i.to_json(), lambda i: i.value))
        if self.notebookDocumentSync is not None:
            out["notebookDocumentSync"] = write_or_type(self.notebookDocumentSync, (lambda i: isinstance(i, NotebookDocumentSyncOptions), lambda i: isinstance(i, NotebookDocumentSyncRegistrationOptions)), (lambda i: i.to_json(), lambda i: i.to_json()))
        if self.completionProvider is not None:
            out["completionProvider"] = self.completionProvider.to_json()
        if self.hoverProvider is not None:
            out["hoverProvider"] = write_or_type(self.hoverProvider, (lambda i: isinstance(i, bool), lambda i: isinstance(i, HoverOptions)), (lambda i: i, lambda i: i.to_json()))
        if self.signatureHelpProvider is not None:
            out["signatureHelpProvider"] = self.signatureHelpProvider.to_json()
        if self.declarationProvider is not None:
            out["declarationProvider"] = write_or_type(self.declarationProvider, (lambda i: isinstance(i, bool), lambda i: isinstance(i, DeclarationOptions), lambda i: isinstance(i, DeclarationRegistrationOptions)), (lambda i: i, lambda i: i.to_json(), lambda i: i.to_json()))
        if self.definitionProvider is not None:
            out["definitionProvider"] = write_or_type(self.definitionProvider, (lambda i: isinstance(i, bool), lambda i: isinstance(i, DefinitionOptions)), (lambda i: i, lambda i: i.to_json()))
        if self.typeDefinitionProvider is not None:
            out["typeDefinitionProvider"] = write_or_type(self.typeDefinitionProvider, (lambda i: isinstance(i, bool), lambda i: isinstance(i, TypeDefinitionOptions), lambda i: isinstance(i, TypeDefinitionRegistrationOptions)), (lambda i: i, lambda i: i.to_json(), lambda i: i.to_json()))
        if self.implementationProvider is not None:
            out["implementationProvider"] = write_or_type(self.implementationProvider, (lambda i: isinstance(i, bool), lambda i: isinstance(i, ImplementationOptions), lambda i: isinstance(i, ImplementationRegistrationOptions)), (lambda i: i, lambda i: i.to_json(), lambda i: i.to_json()))
        if self.referencesProvider is not None:
            out["referencesProvider"] = write_or_type(self.referencesProvider, (lambda i: isinstance(i, bool), lambda i: isinstance(i, ReferenceOptions)), (lambda i: i, lambda i: i.to_json()))
        if self.documentHighlightProvider is not None:
            out["documentHighlightProvider"] = write_or_type(self.documentHighlightProvider, (lambda i: isinstance(i, bool), lambda i: isinstance(i, DocumentHighlightOptions)), (lambda i: i, lambda i: i.to_json()))
        if self.documentSymbolProvider is not None:
            out["documentSymbolProvider"] = write_or_type(self.documentSymbolProvider, (lambda i: isinstance(i, bool), lambda i: isinstance(i, DocumentSymbolOptions)), (lambda i: i, lambda i: i.to_json()))
        if self.codeActionProvider is not None:
            out["codeActionProvider"] = write_or_type(self.codeActionProvider, (lambda i: isinstance(i, bool), lambda i: isinstance(i, CodeActionOptions)), (lambda i: i, lambda i: i.to_json()))
        if self.codeLensProvider is not None:
            out["codeLensProvider"] = self.codeLensProvider.to_json()
        if self.documentLinkProvider is not None:
            out["documentLinkProvider"] = self.documentLinkProvider.to_json()
        if self.colorProvider is not None:
            out["colorProvider"] = write_or_type(self.colorProvider, (lambda i: isinstance(i, bool), lambda i: isinstance(i, DocumentColorOptions), lambda i: isinstance(i, DocumentColorRegistrationOptions)), (lambda i: i, lambda i: i.to_json(), lambda i: i.to_json()))
        if self.workspaceSymbolProvider is not None:
            out["workspaceSymbolProvider"] = write_or_type(self.workspaceSymbolProvider, (lambda i: isinstance(i, bool), lambda i: isinstance(i, WorkspaceSymbolOptions)), (lambda i: i, lambda i: i.to_json()))
        if self.documentFormattingProvider is not None:
            out["documentFormattingProvider"] = write_or_type(self.documentFormattingProvider, (lambda i: isinstance(i, bool), lambda i: isinstance(i, DocumentFormattingOptions)), (lambda i: i, lambda i: i.to_json()))
        if self.documentRangeFormattingProvider is not None:
            out["documentRangeFormattingProvider"] = write_or_type(self.documentRangeFormattingProvider, (lambda i: isinstance(i, bool), lambda i: isinstance(i, DocumentRangeFormattingOptions)), (lambda i: i, lambda i: i.to_json()))
        if self.documentOnTypeFormattingProvider is not None:
            out["documentOnTypeFormattingProvider"] = self.documentOnTypeFormattingProvider.to_json()
        if self.renameProvider is not None:
            out["renameProvider"] = write_or_type(self.renameProvider, (lambda i: isinstance(i, bool), lambda i: isinstance(i, RenameOptions)), (lambda i: i, lambda i: i.to_json()))
        if self.foldingRangeProvider is not None:
            out["foldingRangeProvider"] = write_or_type(self.foldingRangeProvider, (lambda i: isinstance(i, bool), lambda i: isinstance(i, FoldingRangeOptions), lambda i: isinstance(i, FoldingRangeRegistrationOptions)), (lambda i: i, lambda i: i.to_json(), lambda i: i.to_json()))
        if self.selectionRangeProvider is not None:
            out["selectionRangeProvider"] = write_or_type(self.selectionRangeProvider, (lambda i: isinstance(i, bool), lambda i: isinstance(i, SelectionRangeOptions), lambda i: isinstance(i, SelectionRangeRegistrationOptions)), (lambda i: i, lambda i: i.to_json(), lambda i: i.to_json()))
        if self.executeCommandProvider is not None:
            out["executeCommandProvider"] = self.executeCommandProvider.to_json()
        if self.callHierarchyProvider is not None:
            out["callHierarchyProvider"] = write_or_type(self.callHierarchyProvider, (lambda i: isinstance(i, bool), lambda i: isinstance(i, CallHierarchyOptions), lambda i: isinstance(i, CallHierarchyRegistrationOptions)), (lambda i: i, lambda i: i.to_json(), lambda i: i.to_json()))
        if self.linkedEditingRangeProvider is not None:
            out["linkedEditingRangeProvider"] = write_or_type(self.linkedEditingRangeProvider, (lambda i: isinstance(i, bool), lambda i: isinstance(i, LinkedEditingRangeOptions), lambda i: isinstance(i, LinkedEditingRangeRegistrationOptions)), (lambda i: i, lambda i: i.to_json(), lambda i: i.to_json()))
        if self.semanticTokensProvider is not None:
            out["semanticTokensProvider"] = write_or_type(self.semanticTokensProvider, (lambda i: isinstance(i, SemanticTokensOptions), lambda i: isinstance(i, SemanticTokensRegistrationOptions)), (lambda i: i.to_json(), lambda i: i.to_json()))
        if self.monikerProvider is not None:
            out["monikerProvider"] = write_or_type(self.monikerProvider, (lambda i: isinstance(i, bool), lambda i: isinstance(i, MonikerOptions), lambda i: isinstance(i, MonikerRegistrationOptions)), (lambda i: i, lambda i: i.to_json(), lambda i: i.to_json()))
        if self.typeHierarchyProvider is not None:
            out["typeHierarchyProvider"] = write_or_type(self.typeHierarchyProvider, (lambda i: isinstance(i, bool), lambda i: isinstance(i, TypeHierarchyOptions), lambda i: isinstance(i, TypeHierarchyRegistrationOptions)), (lambda i: i, lambda i: i.to_json(), lambda i: i.to_json()))
        if self.inlineValueProvider is not None:
            out["inlineValueProvider"] = write_or_type(self.inlineValueProvider, (lambda i: isinstance(i, bool), lambda i: isinstance(i, InlineValueOptions), lambda i: isinstance(i, InlineValueRegistrationOptions)), (lambda i: i, lambda i: i.to_json(), lambda i: i.to_json()))
        if self.inlayHintProvider is not None:
            out["inlayHintProvider"] = write_or_type(self.inlayHintProvider, (lambda i: isinstance(i, bool), lambda i: isinstance(i, InlayHintOptions), lambda i: isinstance(i, InlayHintRegistrationOptions)), (lambda i: i, lambda i: i.to_json(), lambda i: i.to_json()))
        if self.diagnosticProvider is not None:
            out["diagnosticProvider"] = write_or_type(self.diagnosticProvider, (lambda i: isinstance(i, DiagnosticOptions), lambda i: isinstance(i, DiagnosticRegistrationOptions)), (lambda i: i.to_json(), lambda i: i.to_json()))
        if self.workspace is not None:
            out["workspace"] = write_AnonymousStructure11(self.workspace)
        if self.experimental is not None:
            out["experimental"] = write_LSPAny(self.experimental)
        return out


AnonymousStructure0Keys = Literal["name","version"]

def parse_AnonymousStructure0(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure0Keys, Any]:
    out: Dict[AnonymousStructure0Keys, Any] = {}
    out["name"] = json_get_string(obj, "name")
    if version_json := json_get_optional_string(obj, "version"):
        out["version"] = version_json
    else:
        out["version"] = None
    return out

def write_AnonymousStructure0(obj: Dict[AnonymousStructure0Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    out["name"] = obj["name"]
    if obj.get("version") is not None:
        out["version"] = obj.get("version")
    return out


@dataclass
class InitializeResult():
    """
    The result returned from an initialize request.

    *Generated from the TypeScript documentation*
    """

    # The capabilities the language server provides.
    capabilities: "ServerCapabilities"
    
    # Information about the server.
    # 
    # @since 3.15.0
    serverInfo: Optional[Dict[AnonymousStructure0Keys, Any]]

    def __init__(self, *, capabilities: "ServerCapabilities", serverInfo: Optional[Dict[AnonymousStructure0Keys, Any]] = None) -> None:
        """
        - capabilities: The capabilities the language server provides.
        - serverInfo: Information about the server.
            
            @since 3.15.0
        """
        self.capabilities = capabilities
        self.serverInfo = serverInfo

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "InitializeResult":
        capabilities = ServerCapabilities.from_json(json_get_object(obj, "capabilities"))
        if serverInfo_json := json_get_optional_object(obj, "serverInfo"):
            serverInfo = parse_AnonymousStructure0(serverInfo_json)
        else:
            serverInfo = None
        return cls(capabilities=capabilities, serverInfo=serverInfo)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["capabilities"] = self.capabilities.to_json()
        if self.serverInfo is not None:
            out["serverInfo"] = write_AnonymousStructure0(self.serverInfo)
        return out


@dataclass
class InitializeError():
    """
    The data type of the ResponseError if the
    initialize request fails.

    *Generated from the TypeScript documentation*
    """

    # Indicates whether the client execute the following retry logic:
    # (1) show the message provided by the ResponseError to the user
    # (2) user selects retry or cancel
    # (3) if user selected retry the initialize method is sent again.
    retry: bool

    def __init__(self, *, retry: bool) -> None:
        """
        - retry: Indicates whether the client execute the following retry logic:
            (1) show the message provided by the ResponseError to the user
            (2) user selects retry or cancel
            (3) if user selected retry the initialize method is sent again.
        """
        self.retry = retry

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "InitializeError":
        retry = json_get_bool(obj, "retry")
        return cls(retry=retry)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["retry"] = self.retry
        return out


@dataclass
class InitializedParams():
    """


    *Generated from the TypeScript documentation*
    """





    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "InitializedParams":
    
        return cls()

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
    
        return out


@dataclass
class DidChangeConfigurationParams():
    """
    The parameters of a change configuration notification.

    *Generated from the TypeScript documentation*
    """

    # The actual changed settings
    settings: "LSPAny"

    def __init__(self, *, settings: "LSPAny") -> None:
        """
        - settings: The actual changed settings
        """
        self.settings = settings

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DidChangeConfigurationParams":
        settings = parse_LSPAny(obj["settings"])
        return cls(settings=settings)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["settings"] = write_LSPAny(self.settings)
        return out


@dataclass
class DidChangeConfigurationRegistrationOptions():
    """


    *Generated from the TypeScript documentation*
    """

    section: Optional[Union[str, List[str]]]

    def __init__(self, *, section: Optional[Union[str, List[str]]] = None) -> None:
        """
    
        """
        self.section = section

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DidChangeConfigurationRegistrationOptions":
        if section_json := obj.get("section"):
            section = parse_or_type(section_json, (lambda v: json_assert_type_string(v), lambda v: [json_assert_type_string(i) for i in json_assert_type_array(v)]))
        else:
            section = None
        return cls(section=section)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.section is not None:
            out["section"] = write_or_type(self.section, (lambda i: isinstance(i, str), lambda i: isinstance(i, List) and (len(i) == 0 or (isinstance(i[0], str)))), (lambda i: i, lambda i: [i for i in i]))
        return out


@dataclass
class ShowMessageParams():
    """
    The parameters of a notification message.

    *Generated from the TypeScript documentation*
    """

    # The message type. See {@link MessageType}
    type: "MessageType"
    
    # The actual message.
    message: str

    def __init__(self, *, type: "MessageType", message: str) -> None:
        """
        - type: The message type. See {@link MessageType}
        - message: The actual message.
        """
        self.type = type
        self.message = message

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "ShowMessageParams":
        type = MessageType(json_get_int(obj, "type"))
        message = json_get_string(obj, "message")
        return cls(type=type, message=message)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["type"] = self.type.value
        out["message"] = self.message
        return out


@dataclass
class MessageActionItem():
    """


    *Generated from the TypeScript documentation*
    """

    # A short title like 'Retry', 'Open Log' etc.
    title: str

    def __init__(self, *, title: str) -> None:
        """
        - title: A short title like 'Retry', 'Open Log' etc.
        """
        self.title = title

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "MessageActionItem":
        title = json_get_string(obj, "title")
        return cls(title=title)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["title"] = self.title
        return out


@dataclass
class ShowMessageRequestParams():
    """


    *Generated from the TypeScript documentation*
    """

    # The message type. See {@link MessageType}
    type: "MessageType"
    
    # The actual message.
    message: str
    
    # The message action items to present.
    actions: Optional[List["MessageActionItem"]]

    def __init__(self, *, type: "MessageType", message: str, actions: Optional[List["MessageActionItem"]] = None) -> None:
        """
        - type: The message type. See {@link MessageType}
        - message: The actual message.
        - actions: The message action items to present.
        """
        self.type = type
        self.message = message
        self.actions = actions

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "ShowMessageRequestParams":
        type = MessageType(json_get_int(obj, "type"))
        message = json_get_string(obj, "message")
        if actions_json := json_get_optional_array(obj, "actions"):
            actions = [MessageActionItem.from_json(json_assert_type_object(i)) for i in actions_json]
        else:
            actions = None
        return cls(type=type, message=message, actions=actions)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["type"] = self.type.value
        out["message"] = self.message
        if self.actions is not None:
            out["actions"] = [i.to_json() for i in self.actions]
        return out


@dataclass
class LogMessageParams():
    """
    The log message parameters.

    *Generated from the TypeScript documentation*
    """

    # The message type. See {@link MessageType}
    type: "MessageType"
    
    # The actual message.
    message: str

    def __init__(self, *, type: "MessageType", message: str) -> None:
        """
        - type: The message type. See {@link MessageType}
        - message: The actual message.
        """
        self.type = type
        self.message = message

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "LogMessageParams":
        type = MessageType(json_get_int(obj, "type"))
        message = json_get_string(obj, "message")
        return cls(type=type, message=message)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["type"] = self.type.value
        out["message"] = self.message
        return out


@dataclass
class DidOpenTextDocumentParams():
    """
    The parameters sent in an open text document notification

    *Generated from the TypeScript documentation*
    """

    # The document that was opened.
    textDocument: "TextDocumentItem"

    def __init__(self, *, textDocument: "TextDocumentItem") -> None:
        """
        - textDocument: The document that was opened.
        """
        self.textDocument = textDocument

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DidOpenTextDocumentParams":
        textDocument = TextDocumentItem.from_json(json_get_object(obj, "textDocument"))
        return cls(textDocument=textDocument)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["textDocument"] = self.textDocument.to_json()
        return out


@dataclass
class DidChangeTextDocumentParams():
    """
    The change text document notification's parameters.

    *Generated from the TypeScript documentation*
    """

    # The document that did change. The version number points
    # to the version after all provided content changes have
    # been applied.
    textDocument: "VersionedTextDocumentIdentifier"
    
    # The actual content changes. The content changes describe single state changes
    # to the document. So if there are two content changes c1 (at array index 0) and
    # c2 (at array index 1) for a document in state S then c1 moves the document from
    # S to S' and c2 from S' to S''. So c1 is computed on the state S and c2 is computed
    # on the state S'.
    # 
    # To mirror the content of a document using change events use the following approach:
    # - start with the same initial content
    # - apply the 'textDocument/didChange' notifications in the order you receive them.
    # - apply the `TextDocumentContentChangeEvent`s in a single notification in the order
    #   you receive them.
    contentChanges: List["TextDocumentContentChangeEvent"]

    def __init__(self, *, textDocument: "VersionedTextDocumentIdentifier", contentChanges: List["TextDocumentContentChangeEvent"]) -> None:
        """
        - textDocument: The document that did change. The version number points
            to the version after all provided content changes have
            been applied.
        - contentChanges: The actual content changes. The content changes describe single state changes
            to the document. So if there are two content changes c1 (at array index 0) and
            c2 (at array index 1) for a document in state S then c1 moves the document from
            S to S' and c2 from S' to S''. So c1 is computed on the state S and c2 is computed
            on the state S'.
            
            To mirror the content of a document using change events use the following approach:
            - start with the same initial content
            - apply the 'textDocument/didChange' notifications in the order you receive them.
            - apply the `TextDocumentContentChangeEvent`s in a single notification in the order
              you receive them.
        """
        self.textDocument = textDocument
        self.contentChanges = contentChanges

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DidChangeTextDocumentParams":
        textDocument = VersionedTextDocumentIdentifier.from_json(json_get_object(obj, "textDocument"))
        contentChanges = [parse_TextDocumentContentChangeEvent((i)) for i in json_get_array(obj, "contentChanges")]
        return cls(textDocument=textDocument, contentChanges=contentChanges)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["textDocument"] = self.textDocument.to_json()
        out["contentChanges"] = [write_TextDocumentContentChangeEvent(i) for i in self.contentChanges]
        return out


@dataclass
class TextDocumentChangeRegistrationOptions(TextDocumentRegistrationOptions):
    """
    Describe options to be used when registered for text document change events.

    *Generated from the TypeScript documentation*
    """

    # A document selector to identify the scope of the registration. If set to null
    # the document selector provided on the client side will be used.
    documentSelector: Union["DocumentSelector", None]
    
    # How documents are synced to the server.
    syncKind: "TextDocumentSyncKind"

    def __init__(self, *, documentSelector: Union["DocumentSelector", None], syncKind: "TextDocumentSyncKind") -> None:
        """
        - documentSelector: A document selector to identify the scope of the registration. If set to null
            the document selector provided on the client side will be used.
        - syncKind: How documents are synced to the server.
        """
        self.documentSelector = documentSelector
        self.syncKind = syncKind

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "TextDocumentChangeRegistrationOptions":
        documentSelector = parse_or_type(obj["documentSelector"], (lambda v: parse_DocumentSelector(json_assert_type_array(v)), lambda v: json_assert_type_null(v)))
        syncKind = TextDocumentSyncKind(json_get_int(obj, "syncKind"))
        return cls(documentSelector=documentSelector, syncKind=syncKind)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["documentSelector"] = write_or_type(self.documentSelector, (lambda i: isinstance(i, List) and (len(i) == 0 or (((isinstance(i[0], Dict) and "language" in i[0].keys()) or (isinstance(i[0], Dict) and "scheme" in i[0].keys()) or (isinstance(i[0], Dict) and "pattern" in i[0].keys())) or (isinstance(i[0], NotebookCellTextDocumentFilter)))), lambda i: i is None), (lambda i: write_DocumentSelector(i), lambda i: i))
        out["syncKind"] = self.syncKind.value
        return out


@dataclass
class DidCloseTextDocumentParams():
    """
    The parameters sent in a close text document notification

    *Generated from the TypeScript documentation*
    """

    # The document that was closed.
    textDocument: "TextDocumentIdentifier"

    def __init__(self, *, textDocument: "TextDocumentIdentifier") -> None:
        """
        - textDocument: The document that was closed.
        """
        self.textDocument = textDocument

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DidCloseTextDocumentParams":
        textDocument = TextDocumentIdentifier.from_json(json_get_object(obj, "textDocument"))
        return cls(textDocument=textDocument)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["textDocument"] = self.textDocument.to_json()
        return out


@dataclass
class DidSaveTextDocumentParams():
    """
    The parameters sent in a save text document notification

    *Generated from the TypeScript documentation*
    """

    # The document that was saved.
    textDocument: "TextDocumentIdentifier"
    
    # Optional the content when saved. Depends on the includeText value
    # when the save notification was requested.
    text: Optional[str]

    def __init__(self, *, textDocument: "TextDocumentIdentifier", text: Optional[str] = None) -> None:
        """
        - textDocument: The document that was saved.
        - text: Optional the content when saved. Depends on the includeText value
            when the save notification was requested.
        """
        self.textDocument = textDocument
        self.text = text

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DidSaveTextDocumentParams":
        textDocument = TextDocumentIdentifier.from_json(json_get_object(obj, "textDocument"))
        if text_json := json_get_optional_string(obj, "text"):
            text = text_json
        else:
            text = None
        return cls(textDocument=textDocument, text=text)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["textDocument"] = self.textDocument.to_json()
        if self.text is not None:
            out["text"] = self.text
        return out


@dataclass
class TextDocumentSaveRegistrationOptions(TextDocumentRegistrationOptions, SaveOptions):
    """
    Save registration options.

    *Generated from the TypeScript documentation*
    """

    # A document selector to identify the scope of the registration. If set to null
    # the document selector provided on the client side will be used.
    documentSelector: Union["DocumentSelector", None]
    
    # The client is supposed to include the content on save.
    includeText: Optional[bool]

    def __init__(self, *, documentSelector: Union["DocumentSelector", None], includeText: Optional[bool] = None) -> None:
        """
        - documentSelector: A document selector to identify the scope of the registration. If set to null
            the document selector provided on the client side will be used.
        - includeText: The client is supposed to include the content on save.
        """
        self.documentSelector = documentSelector
        self.includeText = includeText

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "TextDocumentSaveRegistrationOptions":
        documentSelector = parse_or_type(obj["documentSelector"], (lambda v: parse_DocumentSelector(json_assert_type_array(v)), lambda v: json_assert_type_null(v)))
        if includeText_json := json_get_optional_bool(obj, "includeText"):
            includeText = includeText_json
        else:
            includeText = None
        return cls(documentSelector=documentSelector, includeText=includeText)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["documentSelector"] = write_or_type(self.documentSelector, (lambda i: isinstance(i, List) and (len(i) == 0 or (((isinstance(i[0], Dict) and "language" in i[0].keys()) or (isinstance(i[0], Dict) and "scheme" in i[0].keys()) or (isinstance(i[0], Dict) and "pattern" in i[0].keys())) or (isinstance(i[0], NotebookCellTextDocumentFilter)))), lambda i: i is None), (lambda i: write_DocumentSelector(i), lambda i: i))
        if self.includeText is not None:
            out["includeText"] = self.includeText
        return out


@dataclass
class WillSaveTextDocumentParams():
    """
    The parameters sent in a will save text document notification.

    *Generated from the TypeScript documentation*
    """

    # The document that will be saved.
    textDocument: "TextDocumentIdentifier"
    
    # The 'TextDocumentSaveReason'.
    reason: "TextDocumentSaveReason"

    def __init__(self, *, textDocument: "TextDocumentIdentifier", reason: "TextDocumentSaveReason") -> None:
        """
        - textDocument: The document that will be saved.
        - reason: The 'TextDocumentSaveReason'.
        """
        self.textDocument = textDocument
        self.reason = reason

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "WillSaveTextDocumentParams":
        textDocument = TextDocumentIdentifier.from_json(json_get_object(obj, "textDocument"))
        reason = TextDocumentSaveReason(json_get_int(obj, "reason"))
        return cls(textDocument=textDocument, reason=reason)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["textDocument"] = self.textDocument.to_json()
        out["reason"] = self.reason.value
        return out


@dataclass
class FileEvent():
    """
    An event describing a file change.

    *Generated from the TypeScript documentation*
    """

    # The file's uri.
    uri: str
    
    # The change type.
    type: "FileChangeType"

    def __init__(self, *, uri: str, type: "FileChangeType") -> None:
        """
        - uri: The file's uri.
        - type: The change type.
        """
        self.uri = uri
        self.type = type

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "FileEvent":
        uri = json_get_string(obj, "uri")
        type = FileChangeType(json_get_int(obj, "type"))
        return cls(uri=uri, type=type)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["uri"] = self.uri
        out["type"] = self.type.value
        return out


@dataclass
class DidChangeWatchedFilesParams():
    """
    The watched files change notification's parameters.

    *Generated from the TypeScript documentation*
    """

    # The actual file events.
    changes: List["FileEvent"]

    def __init__(self, *, changes: List["FileEvent"]) -> None:
        """
        - changes: The actual file events.
        """
        self.changes = changes

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DidChangeWatchedFilesParams":
        changes = [FileEvent.from_json(json_assert_type_object(i)) for i in json_get_array(obj, "changes")]
        return cls(changes=changes)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["changes"] = [i.to_json() for i in self.changes]
        return out


# The glob pattern to watch relative to the base path. Glob patterns can have the following syntax:
# - `*` to match one or more characters in a path segment
# - `?` to match on one character in a path segment
# - `**` to match any number of path segments, including none
# - `{}` to group conditions (e.g. `**​/*.{ts,js}` matches all TypeScript and JavaScript files)
# - `[]` to declare a range of characters to match in a path segment (e.g., `example.[0-9]` to match on `example.0`, `example.1`, …)
# - `[!...]` to negate a range of characters to match in a path segment (e.g., `example.[!0-9]` to match on `example.a`, `example.b`, but not `example.0`)
# 
# @since 3.17.0
Pattern = str

def parse_Pattern(arg: JSON_VALUE) -> Pattern:
    return json_assert_type_string(arg)

def write_Pattern(arg: Pattern) -> JSON_VALUE:
    return arg


@dataclass
class RelativePattern():
    """
    A relative pattern is a helper to construct glob patterns that are matched
    relatively to a base URI. The common value for a `baseUri` is a workspace
    folder root, but it can be another absolute URI as well.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # A workspace folder or a base URI to which this pattern will be matched
    # against relatively.
    baseUri: Union["WorkspaceFolder", str]
    
    # The actual glob pattern;
    pattern: "Pattern"

    def __init__(self, *, baseUri: Union["WorkspaceFolder", str], pattern: "Pattern") -> None:
        """
        - baseUri: A workspace folder or a base URI to which this pattern will be matched
            against relatively.
        - pattern: The actual glob pattern;
        """
        self.baseUri = baseUri
        self.pattern = pattern

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "RelativePattern":
        baseUri = parse_or_type(obj["baseUri"], (lambda v: WorkspaceFolder.from_json(json_assert_type_object(v)), lambda v: json_assert_type_string(v)))
        pattern = parse_Pattern(json_get_string(obj, "pattern"))
        return cls(baseUri=baseUri, pattern=pattern)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["baseUri"] = write_or_type(self.baseUri, (lambda i: isinstance(i, WorkspaceFolder), lambda i: isinstance(i, str)), (lambda i: i.to_json(), lambda i: i))
        out["pattern"] = write_Pattern(self.pattern)
        return out


# The glob pattern. Either a string pattern or a relative pattern.
# 
# @since 3.17.0
GlobPattern = Union["Pattern", "RelativePattern"]

def parse_GlobPattern(arg: JSON_VALUE) -> GlobPattern:
    return parse_or_type((arg), (lambda v: parse_Pattern(json_assert_type_string(v)), lambda v: RelativePattern.from_json(json_assert_type_object(v))))

def write_GlobPattern(arg: GlobPattern) -> JSON_VALUE:
    return write_or_type(arg, (lambda i: isinstance(i, str), lambda i: isinstance(i, RelativePattern)), (lambda i: write_Pattern(i), lambda i: i.to_json()))


@dataclass
class FileSystemWatcher():
    """


    *Generated from the TypeScript documentation*
    """

    # The glob pattern to watch. See {@link GlobPattern glob pattern} for more detail.
    # 
    # @since 3.17.0 support for relative patterns.
    globPattern: "GlobPattern"
    
    # The kind of events of interest. If omitted it defaults
    # to WatchKind.Create | WatchKind.Change | WatchKind.Delete
    # which is 7.
    kind: Optional["WatchKind"]

    def __init__(self, *, globPattern: "GlobPattern", kind: Optional["WatchKind"] = None) -> None:
        """
        - globPattern: The glob pattern to watch. See {@link GlobPattern glob pattern} for more detail.
            
            @since 3.17.0 support for relative patterns.
        - kind: The kind of events of interest. If omitted it defaults
            to WatchKind.Create | WatchKind.Change | WatchKind.Delete
            which is 7.
        """
        self.globPattern = globPattern
        self.kind = kind

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "FileSystemWatcher":
        globPattern = parse_GlobPattern(obj["globPattern"])
        if kind_json := json_get_optional_int(obj, "kind"):
            kind = WatchKind(kind_json)
        else:
            kind = None
        return cls(globPattern=globPattern, kind=kind)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["globPattern"] = write_GlobPattern(self.globPattern)
        if self.kind is not None:
            out["kind"] = self.kind.value
        return out


@dataclass
class DidChangeWatchedFilesRegistrationOptions():
    """
    Describe options to be used when registered for text document change events.

    *Generated from the TypeScript documentation*
    """

    # The watchers to register.
    watchers: List["FileSystemWatcher"]

    def __init__(self, *, watchers: List["FileSystemWatcher"]) -> None:
        """
        - watchers: The watchers to register.
        """
        self.watchers = watchers

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DidChangeWatchedFilesRegistrationOptions":
        watchers = [FileSystemWatcher.from_json(json_assert_type_object(i)) for i in json_get_array(obj, "watchers")]
        return cls(watchers=watchers)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["watchers"] = [i.to_json() for i in self.watchers]
        return out


@dataclass
class PublishDiagnosticsParams():
    """
    The publish diagnostic notification's parameters.

    *Generated from the TypeScript documentation*
    """

    # The URI for which diagnostic information is reported.
    uri: str
    
    # Optional the version number of the document the diagnostics are published for.
    # 
    # @since 3.15.0
    version: Optional[int]
    
    # An array of diagnostic information items.
    diagnostics: List["Diagnostic"]

    def __init__(self, *, uri: str, version: Optional[int] = None, diagnostics: List["Diagnostic"]) -> None:
        """
        - uri: The URI for which diagnostic information is reported.
        - version: Optional the version number of the document the diagnostics are published for.
            
            @since 3.15.0
        - diagnostics: An array of diagnostic information items.
        """
        self.uri = uri
        self.version = version
        self.diagnostics = diagnostics

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "PublishDiagnosticsParams":
        uri = json_get_string(obj, "uri")
        if version_json := json_get_optional_int(obj, "version"):
            version = version_json
        else:
            version = None
        diagnostics = [Diagnostic.from_json(json_assert_type_object(i)) for i in json_get_array(obj, "diagnostics")]
        return cls(uri=uri, version=version, diagnostics=diagnostics)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["uri"] = self.uri
        if self.version is not None:
            out["version"] = self.version
        out["diagnostics"] = [i.to_json() for i in self.diagnostics]
        return out


@dataclass
class CompletionContext():
    """
    Contains additional information about the context in which a completion request is triggered.

    *Generated from the TypeScript documentation*
    """

    # How the completion was triggered.
    triggerKind: "CompletionTriggerKind"
    
    # The trigger character (a single character) that has trigger code complete.
    # Is undefined if `triggerKind !== CompletionTriggerKind.TriggerCharacter`
    triggerCharacter: Optional[str]

    def __init__(self, *, triggerKind: "CompletionTriggerKind", triggerCharacter: Optional[str] = None) -> None:
        """
        - triggerKind: How the completion was triggered.
        - triggerCharacter: The trigger character (a single character) that has trigger code complete.
            Is undefined if `triggerKind !== CompletionTriggerKind.TriggerCharacter`
        """
        self.triggerKind = triggerKind
        self.triggerCharacter = triggerCharacter

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "CompletionContext":
        triggerKind = CompletionTriggerKind(json_get_int(obj, "triggerKind"))
        if triggerCharacter_json := json_get_optional_string(obj, "triggerCharacter"):
            triggerCharacter = triggerCharacter_json
        else:
            triggerCharacter = None
        return cls(triggerKind=triggerKind, triggerCharacter=triggerCharacter)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["triggerKind"] = self.triggerKind.value
        if self.triggerCharacter is not None:
            out["triggerCharacter"] = self.triggerCharacter
        return out


@dataclass
class CompletionParams(TextDocumentPositionParams):
    """
    Completion parameters

    *Generated from the TypeScript documentation*
    """

    # The text document.
    textDocument: "TextDocumentIdentifier"
    
    # The position inside the text document.
    position: "Position"
    
    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]
    
    # An optional token that a server can use to report partial results (e.g. streaming) to
    # the client.
    partialResultToken: Optional["ProgressToken"]
    
    # The completion context. This is only available it the client specifies
    # to send this using the client capability `textDocument.completion.contextSupport === true`
    context: Optional["CompletionContext"]

    def __init__(self, *, textDocument: "TextDocumentIdentifier", position: "Position", workDoneToken: Optional["ProgressToken"] = None, partialResultToken: Optional["ProgressToken"] = None, context: Optional["CompletionContext"] = None) -> None:
        """
        - textDocument: The text document.
        - position: The position inside the text document.
        - workDoneToken: An optional token that a server can use to report work done progress.
        - partialResultToken: An optional token that a server can use to report partial results (e.g. streaming) to
            the client.
        - context: The completion context. This is only available it the client specifies
            to send this using the client capability `textDocument.completion.contextSupport === true`
        """
        self.textDocument = textDocument
        self.position = position
        self.workDoneToken = workDoneToken
        self.partialResultToken = partialResultToken
        self.context = context

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "CompletionParams":
        textDocument = TextDocumentIdentifier.from_json(json_get_object(obj, "textDocument"))
        position = Position.from_json(json_get_object(obj, "position"))
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        if partialResultToken_json := obj.get("partialResultToken"):
            partialResultToken = parse_ProgressToken(partialResultToken_json)
        else:
            partialResultToken = None
        if context_json := json_get_optional_object(obj, "context"):
            context = CompletionContext.from_json(context_json)
        else:
            context = None
        return cls(textDocument=textDocument, position=position, workDoneToken=workDoneToken, partialResultToken=partialResultToken, context=context)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["textDocument"] = self.textDocument.to_json()
        out["position"] = self.position.to_json()
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        if self.partialResultToken is not None:
            out["partialResultToken"] = write_ProgressToken(self.partialResultToken)
        if self.context is not None:
            out["context"] = self.context.to_json()
        return out


@dataclass
class CompletionItemLabelDetails():
    """
    Additional details for a completion item label.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # An optional string which is rendered less prominently directly after {@link CompletionItem.label label},
    # without any spacing. Should be used for function signatures and type annotations.
    detail: Optional[str]
    
    # An optional string which is rendered less prominently after {@link CompletionItem.detail}. Should be used
    # for fully qualified names and file paths.
    description: Optional[str]

    def __init__(self, *, detail: Optional[str] = None, description: Optional[str] = None) -> None:
        """
        - detail: An optional string which is rendered less prominently directly after {@link CompletionItem.label label},
            without any spacing. Should be used for function signatures and type annotations.
        - description: An optional string which is rendered less prominently after {@link CompletionItem.detail}. Should be used
            for fully qualified names and file paths.
        """
        self.detail = detail
        self.description = description

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "CompletionItemLabelDetails":
        if detail_json := json_get_optional_string(obj, "detail"):
            detail = detail_json
        else:
            detail = None
        if description_json := json_get_optional_string(obj, "description"):
            description = description_json
        else:
            description = None
        return cls(detail=detail, description=description)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.detail is not None:
            out["detail"] = self.detail
        if self.description is not None:
            out["description"] = self.description
        return out


@dataclass
class InsertReplaceEdit():
    """
    A special text edit to provide an insert and a replace operation.
    
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # The string to be inserted.
    newText: str
    
    # The range if the insert is requested
    insert: "Range"
    
    # The range if the replace is requested.
    replace: "Range"

    def __init__(self, *, newText: str, insert: "Range", replace: "Range") -> None:
        """
        - newText: The string to be inserted.
        - insert: The range if the insert is requested
        - replace: The range if the replace is requested.
        """
        self.newText = newText
        self.insert = insert
        self.replace = replace

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "InsertReplaceEdit":
        newText = json_get_string(obj, "newText")
        insert = Range.from_json(json_get_object(obj, "insert"))
        replace = Range.from_json(json_get_object(obj, "replace"))
        return cls(newText=newText, insert=insert, replace=replace)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["newText"] = self.newText
        out["insert"] = self.insert.to_json()
        out["replace"] = self.replace.to_json()
        return out


@dataclass
class CompletionItem():
    """
    A completion item represents a text snippet that is
    proposed to complete text that is being typed.

    *Generated from the TypeScript documentation*
    """

    # The label of this completion item.
    # 
    # The label property is also by default the text that
    # is inserted when selecting this completion.
    # 
    # If label details are provided the label itself should
    # be an unqualified name of the completion item.
    label: str
    
    # Additional details for the label
    # 
    # @since 3.17.0
    labelDetails: Optional["CompletionItemLabelDetails"]
    
    # The kind of this completion item. Based of the kind
    # an icon is chosen by the editor.
    kind: Optional["CompletionItemKind"]
    
    # Tags for this completion item.
    # 
    # @since 3.15.0
    tags: Optional[List["CompletionItemTag"]]
    
    # A human-readable string with additional information
    # about this item, like type or symbol information.
    detail: Optional[str]
    
    # A human-readable string that represents a doc-comment.
    documentation: Optional[Union[str, "MarkupContent"]]
    
    # Indicates if this item is deprecated.
    # @deprecated Use `tags` instead.
    deprecated: Optional[bool]
    
    # Select this item when showing.
    # 
    # *Note* that only one completion item can be selected and that the
    # tool / client decides which item that is. The rule is that the *first*
    # item of those that match best is selected.
    preselect: Optional[bool]
    
    # A string that should be used when comparing this item
    # with other items. When `falsy` the [label](#CompletionItem.label)
    # is used.
    sortText: Optional[str]
    
    # A string that should be used when filtering a set of
    # completion items. When `falsy` the [label](#CompletionItem.label)
    # is used.
    filterText: Optional[str]
    
    # A string that should be inserted into a document when selecting
    # this completion. When `falsy` the [label](#CompletionItem.label)
    # is used.
    # 
    # The `insertText` is subject to interpretation by the client side.
    # Some tools might not take the string literally. For example
    # VS Code when code complete is requested in this example
    # `con<cursor position>` and a completion item with an `insertText` of
    # `console` is provided it will only insert `sole`. Therefore it is
    # recommended to use `textEdit` instead since it avoids additional client
    # side interpretation.
    insertText: Optional[str]
    
    # The format of the insert text. The format applies to both the
    # `insertText` property and the `newText` property of a provided
    # `textEdit`. If omitted defaults to `InsertTextFormat.PlainText`.
    # 
    # Please note that the insertTextFormat doesn't apply to
    # `additionalTextEdits`.
    insertTextFormat: Optional["InsertTextFormat"]
    
    # How whitespace and indentation is handled during completion
    # item insertion. If not provided the clients default value depends on
    # the `textDocument.completion.insertTextMode` client capability.
    # 
    # @since 3.16.0
    insertTextMode: Optional["InsertTextMode"]
    
    # An [edit](#TextEdit) which is applied to a document when selecting
    # this completion. When an edit is provided the value of
    # [insertText](#CompletionItem.insertText) is ignored.
    # 
    # Most editors support two different operations when accepting a completion
    # item. One is to insert a completion text and the other is to replace an
    # existing text with a completion text. Since this can usually not be
    # predetermined by a server it can report both ranges. Clients need to
    # signal support for `InsertReplaceEdits` via the
    # `textDocument.completion.insertReplaceSupport` client capability
    # property.
    # 
    # *Note 1:* The text edit's range as well as both ranges from an insert
    # replace edit must be a [single line] and they must contain the position
    # at which completion has been requested.
    # *Note 2:* If an `InsertReplaceEdit` is returned the edit's insert range
    # must be a prefix of the edit's replace range, that means it must be
    # contained and starting at the same position.
    # 
    # @since 3.16.0 additional type `InsertReplaceEdit`
    textEdit: Optional[Union["TextEdit", "InsertReplaceEdit"]]
    
    # The edit text used if the completion item is part of a CompletionList and
    # CompletionList defines an item default for the text edit range.
    # 
    # Clients will only honor this property if they opt into completion list
    # item defaults using the capability `completionList.itemDefaults`.
    # 
    # If not provided and a list's default range is provided the label
    # property is used as a text.
    # 
    # @since 3.17.0
    textEditText: Optional[str]
    
    # An optional array of additional [text edits](#TextEdit) that are applied when
    # selecting this completion. Edits must not overlap (including the same insert position)
    # with the main [edit](#CompletionItem.textEdit) nor with themselves.
    # 
    # Additional text edits should be used to change text unrelated to the current cursor position
    # (for example adding an import statement at the top of the file if the completion item will
    # insert an unqualified type).
    additionalTextEdits: Optional[List["TextEdit"]]
    
    # An optional set of characters that when pressed while this completion is active will accept it first and
    # then type that character. *Note* that all commit characters should have `length=1` and that superfluous
    # characters will be ignored.
    commitCharacters: Optional[List[str]]
    
    # An optional [command](#Command) that is executed *after* inserting this completion. *Note* that
    # additional modifications to the current document should be described with the
    # [additionalTextEdits](#CompletionItem.additionalTextEdits)-property.
    command: Optional["Command"]
    
    # A data entry field that is preserved on a completion item between a
    # [CompletionRequest](#CompletionRequest) and a [CompletionResolveRequest](#CompletionResolveRequest).
    data: Optional["LSPAny"]

    def __init__(self, *, label: str, labelDetails: Optional["CompletionItemLabelDetails"] = None, kind: Optional["CompletionItemKind"] = None, tags: Optional[List["CompletionItemTag"]] = None, detail: Optional[str] = None, documentation: Optional[Union[str, "MarkupContent"]] = None, deprecated: Optional[bool] = None, preselect: Optional[bool] = None, sortText: Optional[str] = None, filterText: Optional[str] = None, insertText: Optional[str] = None, insertTextFormat: Optional["InsertTextFormat"] = None, insertTextMode: Optional["InsertTextMode"] = None, textEdit: Optional[Union["TextEdit", "InsertReplaceEdit"]] = None, textEditText: Optional[str] = None, additionalTextEdits: Optional[List["TextEdit"]] = None, commitCharacters: Optional[List[str]] = None, command: Optional["Command"] = None, data: Optional["LSPAny"] = None) -> None:
        """
        - label: The label of this completion item.
            
            The label property is also by default the text that
            is inserted when selecting this completion.
            
            If label details are provided the label itself should
            be an unqualified name of the completion item.
        - labelDetails: Additional details for the label
            
            @since 3.17.0
        - kind: The kind of this completion item. Based of the kind
            an icon is chosen by the editor.
        - tags: Tags for this completion item.
            
            @since 3.15.0
        - detail: A human-readable string with additional information
            about this item, like type or symbol information.
        - documentation: A human-readable string that represents a doc-comment.
        - deprecated: Indicates if this item is deprecated.
            @deprecated Use `tags` instead.
        - preselect: Select this item when showing.
            
            *Note* that only one completion item can be selected and that the
            tool / client decides which item that is. The rule is that the *first*
            item of those that match best is selected.
        - sortText: A string that should be used when comparing this item
            with other items. When `falsy` the [label](#CompletionItem.label)
            is used.
        - filterText: A string that should be used when filtering a set of
            completion items. When `falsy` the [label](#CompletionItem.label)
            is used.
        - insertText: A string that should be inserted into a document when selecting
            this completion. When `falsy` the [label](#CompletionItem.label)
            is used.
            
            The `insertText` is subject to interpretation by the client side.
            Some tools might not take the string literally. For example
            VS Code when code complete is requested in this example
            `con<cursor position>` and a completion item with an `insertText` of
            `console` is provided it will only insert `sole`. Therefore it is
            recommended to use `textEdit` instead since it avoids additional client
            side interpretation.
        - insertTextFormat: The format of the insert text. The format applies to both the
            `insertText` property and the `newText` property of a provided
            `textEdit`. If omitted defaults to `InsertTextFormat.PlainText`.
            
            Please note that the insertTextFormat doesn't apply to
            `additionalTextEdits`.
        - insertTextMode: How whitespace and indentation is handled during completion
            item insertion. If not provided the clients default value depends on
            the `textDocument.completion.insertTextMode` client capability.
            
            @since 3.16.0
        - textEdit: An [edit](#TextEdit) which is applied to a document when selecting
            this completion. When an edit is provided the value of
            [insertText](#CompletionItem.insertText) is ignored.
            
            Most editors support two different operations when accepting a completion
            item. One is to insert a completion text and the other is to replace an
            existing text with a completion text. Since this can usually not be
            predetermined by a server it can report both ranges. Clients need to
            signal support for `InsertReplaceEdits` via the
            `textDocument.completion.insertReplaceSupport` client capability
            property.
            
            *Note 1:* The text edit's range as well as both ranges from an insert
            replace edit must be a [single line] and they must contain the position
            at which completion has been requested.
            *Note 2:* If an `InsertReplaceEdit` is returned the edit's insert range
            must be a prefix of the edit's replace range, that means it must be
            contained and starting at the same position.
            
            @since 3.16.0 additional type `InsertReplaceEdit`
        - textEditText: The edit text used if the completion item is part of a CompletionList and
            CompletionList defines an item default for the text edit range.
            
            Clients will only honor this property if they opt into completion list
            item defaults using the capability `completionList.itemDefaults`.
            
            If not provided and a list's default range is provided the label
            property is used as a text.
            
            @since 3.17.0
        - additionalTextEdits: An optional array of additional [text edits](#TextEdit) that are applied when
            selecting this completion. Edits must not overlap (including the same insert position)
            with the main [edit](#CompletionItem.textEdit) nor with themselves.
            
            Additional text edits should be used to change text unrelated to the current cursor position
            (for example adding an import statement at the top of the file if the completion item will
            insert an unqualified type).
        - commitCharacters: An optional set of characters that when pressed while this completion is active will accept it first and
            then type that character. *Note* that all commit characters should have `length=1` and that superfluous
            characters will be ignored.
        - command: An optional [command](#Command) that is executed *after* inserting this completion. *Note* that
            additional modifications to the current document should be described with the
            [additionalTextEdits](#CompletionItem.additionalTextEdits)-property.
        - data: A data entry field that is preserved on a completion item between a
            [CompletionRequest](#CompletionRequest) and a [CompletionResolveRequest](#CompletionResolveRequest).
        """
        self.label = label
        self.labelDetails = labelDetails
        self.kind = kind
        self.tags = tags
        self.detail = detail
        self.documentation = documentation
        self.deprecated = deprecated
        self.preselect = preselect
        self.sortText = sortText
        self.filterText = filterText
        self.insertText = insertText
        self.insertTextFormat = insertTextFormat
        self.insertTextMode = insertTextMode
        self.textEdit = textEdit
        self.textEditText = textEditText
        self.additionalTextEdits = additionalTextEdits
        self.commitCharacters = commitCharacters
        self.command = command
        self.data = data

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "CompletionItem":
        label = json_get_string(obj, "label")
        if labelDetails_json := json_get_optional_object(obj, "labelDetails"):
            labelDetails = CompletionItemLabelDetails.from_json(labelDetails_json)
        else:
            labelDetails = None
        if kind_json := json_get_optional_int(obj, "kind"):
            kind = CompletionItemKind(kind_json)
        else:
            kind = None
        if tags_json := json_get_optional_array(obj, "tags"):
            tags = [CompletionItemTag(json_assert_type_int(i)) for i in tags_json]
        else:
            tags = None
        if detail_json := json_get_optional_string(obj, "detail"):
            detail = detail_json
        else:
            detail = None
        if documentation_json := obj.get("documentation"):
            documentation = parse_or_type(documentation_json, (lambda v: json_assert_type_string(v), lambda v: MarkupContent.from_json(json_assert_type_object(v))))
        else:
            documentation = None
        if deprecated_json := json_get_optional_bool(obj, "deprecated"):
            deprecated = deprecated_json
        else:
            deprecated = None
        if preselect_json := json_get_optional_bool(obj, "preselect"):
            preselect = preselect_json
        else:
            preselect = None
        if sortText_json := json_get_optional_string(obj, "sortText"):
            sortText = sortText_json
        else:
            sortText = None
        if filterText_json := json_get_optional_string(obj, "filterText"):
            filterText = filterText_json
        else:
            filterText = None
        if insertText_json := json_get_optional_string(obj, "insertText"):
            insertText = insertText_json
        else:
            insertText = None
        if insertTextFormat_json := json_get_optional_int(obj, "insertTextFormat"):
            insertTextFormat = InsertTextFormat(insertTextFormat_json)
        else:
            insertTextFormat = None
        if insertTextMode_json := json_get_optional_int(obj, "insertTextMode"):
            insertTextMode = InsertTextMode(insertTextMode_json)
        else:
            insertTextMode = None
        if textEdit_json := obj.get("textEdit"):
            textEdit = parse_or_type(textEdit_json, (lambda v: TextEdit.from_json(json_assert_type_object(v)), lambda v: InsertReplaceEdit.from_json(json_assert_type_object(v))))
        else:
            textEdit = None
        if textEditText_json := json_get_optional_string(obj, "textEditText"):
            textEditText = textEditText_json
        else:
            textEditText = None
        if additionalTextEdits_json := json_get_optional_array(obj, "additionalTextEdits"):
            additionalTextEdits = [TextEdit.from_json(json_assert_type_object(i)) for i in additionalTextEdits_json]
        else:
            additionalTextEdits = None
        if commitCharacters_json := json_get_optional_array(obj, "commitCharacters"):
            commitCharacters = [json_assert_type_string(i) for i in commitCharacters_json]
        else:
            commitCharacters = None
        if command_json := json_get_optional_object(obj, "command"):
            command = Command.from_json(command_json)
        else:
            command = None
        if data_json := obj.get("data"):
            data = parse_LSPAny(data_json)
        else:
            data = None
        return cls(label=label, labelDetails=labelDetails, kind=kind, tags=tags, detail=detail, documentation=documentation, deprecated=deprecated, preselect=preselect, sortText=sortText, filterText=filterText, insertText=insertText, insertTextFormat=insertTextFormat, insertTextMode=insertTextMode, textEdit=textEdit, textEditText=textEditText, additionalTextEdits=additionalTextEdits, commitCharacters=commitCharacters, command=command, data=data)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["label"] = self.label
        if self.labelDetails is not None:
            out["labelDetails"] = self.labelDetails.to_json()
        if self.kind is not None:
            out["kind"] = self.kind.value
        if self.tags is not None:
            out["tags"] = [i.value for i in self.tags]
        if self.detail is not None:
            out["detail"] = self.detail
        if self.documentation is not None:
            out["documentation"] = write_or_type(self.documentation, (lambda i: isinstance(i, str), lambda i: isinstance(i, MarkupContent)), (lambda i: i, lambda i: i.to_json()))
        if self.deprecated is not None:
            out["deprecated"] = self.deprecated
        if self.preselect is not None:
            out["preselect"] = self.preselect
        if self.sortText is not None:
            out["sortText"] = self.sortText
        if self.filterText is not None:
            out["filterText"] = self.filterText
        if self.insertText is not None:
            out["insertText"] = self.insertText
        if self.insertTextFormat is not None:
            out["insertTextFormat"] = self.insertTextFormat.value
        if self.insertTextMode is not None:
            out["insertTextMode"] = self.insertTextMode.value
        if self.textEdit is not None:
            out["textEdit"] = write_or_type(self.textEdit, (lambda i: isinstance(i, TextEdit), lambda i: isinstance(i, InsertReplaceEdit)), (lambda i: i.to_json(), lambda i: i.to_json()))
        if self.textEditText is not None:
            out["textEditText"] = self.textEditText
        if self.additionalTextEdits is not None:
            out["additionalTextEdits"] = [i.to_json() for i in self.additionalTextEdits]
        if self.commitCharacters is not None:
            out["commitCharacters"] = [i for i in self.commitCharacters]
        if self.command is not None:
            out["command"] = self.command.to_json()
        if self.data is not None:
            out["data"] = write_LSPAny(self.data)
        return out


AnonymousStructure1Keys = Literal["insert","replace"]

def parse_AnonymousStructure1(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure1Keys, Any]:
    out: Dict[AnonymousStructure1Keys, Any] = {}
    out["insert"] = Range.from_json(json_get_object(obj, "insert"))
    out["replace"] = Range.from_json(json_get_object(obj, "replace"))
    return out

def write_AnonymousStructure1(obj: Dict[AnonymousStructure1Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    out["insert"] = obj["insert"].to_json()
    out["replace"] = obj["replace"].to_json()
    return out


AnonymousStructure2Keys = Literal["commitCharacters","editRange","insertTextFormat","insertTextMode","data"]

def parse_AnonymousStructure2(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure2Keys, Any]:
    out: Dict[AnonymousStructure2Keys, Any] = {}
    if commitCharacters_json := json_get_optional_array(obj, "commitCharacters"):
        out["commitCharacters"] = [json_assert_type_string(i) for i in commitCharacters_json]
    else:
        out["commitCharacters"] = None
    if editRange_json := obj.get("editRange"):
        out["editRange"] = parse_or_type(editRange_json, (lambda v: Range.from_json(json_assert_type_object(v)), lambda v: parse_AnonymousStructure1(json_assert_type_object(v))))
    else:
        out["editRange"] = None
    if insertTextFormat_json := json_get_optional_int(obj, "insertTextFormat"):
        out["insertTextFormat"] = InsertTextFormat(insertTextFormat_json)
    else:
        out["insertTextFormat"] = None
    if insertTextMode_json := json_get_optional_int(obj, "insertTextMode"):
        out["insertTextMode"] = InsertTextMode(insertTextMode_json)
    else:
        out["insertTextMode"] = None
    if data_json := obj.get("data"):
        out["data"] = parse_LSPAny(data_json)
    else:
        out["data"] = None
    return out

def write_AnonymousStructure2(obj: Dict[AnonymousStructure2Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    if obj.get("commitCharacters") is not None:
        out["commitCharacters"] = [i for i in obj.get("commitCharacters")]
    if obj.get("editRange") is not None:
        out["editRange"] = write_or_type(obj.get("editRange"), (lambda i: isinstance(i, Range), lambda i: isinstance(i, Dict) and "insert" in i.keys() and "replace" in i.keys()), (lambda i: i.to_json(), lambda i: write_AnonymousStructure1(i)))
    if obj.get("insertTextFormat") is not None:
        out["insertTextFormat"] = obj.get("insertTextFormat").value
    if obj.get("insertTextMode") is not None:
        out["insertTextMode"] = obj.get("insertTextMode").value
    if obj.get("data") is not None:
        out["data"] = write_LSPAny(obj.get("data"))
    return out


@dataclass
class CompletionList():
    """
    Represents a collection of [completion items](#CompletionItem) to be presented
    in the editor.

    *Generated from the TypeScript documentation*
    """

    # This list it not complete. Further typing results in recomputing this list.
    # 
    # Recomputed lists have all their items replaced (not appended) in the
    # incomplete completion sessions.
    isIncomplete: bool
    
    # In many cases the items of an actual completion result share the same
    # value for properties like `commitCharacters` or the range of a text
    # edit. A completion list can therefore define item defaults which will
    # be used if a completion item itself doesn't specify the value.
    # 
    # If a completion list specifies a default value and a completion item
    # also specifies a corresponding value the one from the item is used.
    # 
    # Servers are only allowed to return default values if the client
    # signals support for this via the `completionList.itemDefaults`
    # capability.
    # 
    # @since 3.17.0
    itemDefaults: Optional[Dict[AnonymousStructure2Keys, Any]]
    
    # The completion items.
    items: List["CompletionItem"]

    def __init__(self, *, isIncomplete: bool, itemDefaults: Optional[Dict[AnonymousStructure2Keys, Any]] = None, items: List["CompletionItem"]) -> None:
        """
        - isIncomplete: This list it not complete. Further typing results in recomputing this list.
            
            Recomputed lists have all their items replaced (not appended) in the
            incomplete completion sessions.
        - itemDefaults: In many cases the items of an actual completion result share the same
            value for properties like `commitCharacters` or the range of a text
            edit. A completion list can therefore define item defaults which will
            be used if a completion item itself doesn't specify the value.
            
            If a completion list specifies a default value and a completion item
            also specifies a corresponding value the one from the item is used.
            
            Servers are only allowed to return default values if the client
            signals support for this via the `completionList.itemDefaults`
            capability.
            
            @since 3.17.0
        - items: The completion items.
        """
        self.isIncomplete = isIncomplete
        self.itemDefaults = itemDefaults
        self.items = items

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "CompletionList":
        isIncomplete = json_get_bool(obj, "isIncomplete")
        if itemDefaults_json := json_get_optional_object(obj, "itemDefaults"):
            itemDefaults = parse_AnonymousStructure2(itemDefaults_json)
        else:
            itemDefaults = None
        items = [CompletionItem.from_json(json_assert_type_object(i)) for i in json_get_array(obj, "items")]
        return cls(isIncomplete=isIncomplete, itemDefaults=itemDefaults, items=items)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["isIncomplete"] = self.isIncomplete
        if self.itemDefaults is not None:
            out["itemDefaults"] = write_AnonymousStructure2(self.itemDefaults)
        out["items"] = [i.to_json() for i in self.items]
        return out


@dataclass
class CompletionRegistrationOptions(TextDocumentRegistrationOptions, CompletionOptions):
    """
    Registration options for a [CompletionRequest](#CompletionRequest).

    *Generated from the TypeScript documentation*
    """

    # A document selector to identify the scope of the registration. If set to null
    # the document selector provided on the client side will be used.
    documentSelector: Union["DocumentSelector", None]
    
    workDoneProgress: Optional[bool]
    
    # Most tools trigger completion request automatically without explicitly requesting
    # it using a keyboard shortcut (e.g. Ctrl+Space). Typically they do so when the user
    # starts to type an identifier. For example if the user types `c` in a JavaScript file
    # code complete will automatically pop up present `console` besides others as a
    # completion item. Characters that make up identifiers don't need to be listed here.
    # 
    # If code complete should automatically be trigger on characters not being valid inside
    # an identifier (for example `.` in JavaScript) list them in `triggerCharacters`.
    triggerCharacters: Optional[List[str]]
    
    # The list of all possible characters that commit a completion. This field can be used
    # if clients don't support individual commit characters per completion item. See
    # `ClientCapabilities.textDocument.completion.completionItem.commitCharactersSupport`
    # 
    # If a server provides both `allCommitCharacters` and commit characters on an individual
    # completion item the ones on the completion item win.
    # 
    # @since 3.2.0
    allCommitCharacters: Optional[List[str]]
    
    # The server provides support to resolve additional
    # information for a completion item.
    resolveProvider: Optional[bool]
    
    # The server supports the following `CompletionItem` specific
    # capabilities.
    # 
    # @since 3.17.0
    completionItem: Optional[Dict[AnonymousStructure12Keys, Any]]

    def __init__(self, *, documentSelector: Union["DocumentSelector", None], workDoneProgress: Optional[bool] = None, triggerCharacters: Optional[List[str]] = None, allCommitCharacters: Optional[List[str]] = None, resolveProvider: Optional[bool] = None, completionItem: Optional[Dict[AnonymousStructure12Keys, Any]] = None) -> None:
        """
        - documentSelector: A document selector to identify the scope of the registration. If set to null
            the document selector provided on the client side will be used.
        - triggerCharacters: Most tools trigger completion request automatically without explicitly requesting
            it using a keyboard shortcut (e.g. Ctrl+Space). Typically they do so when the user
            starts to type an identifier. For example if the user types `c` in a JavaScript file
            code complete will automatically pop up present `console` besides others as a
            completion item. Characters that make up identifiers don't need to be listed here.
            
            If code complete should automatically be trigger on characters not being valid inside
            an identifier (for example `.` in JavaScript) list them in `triggerCharacters`.
        - allCommitCharacters: The list of all possible characters that commit a completion. This field can be used
            if clients don't support individual commit characters per completion item. See
            `ClientCapabilities.textDocument.completion.completionItem.commitCharactersSupport`
            
            If a server provides both `allCommitCharacters` and commit characters on an individual
            completion item the ones on the completion item win.
            
            @since 3.2.0
        - resolveProvider: The server provides support to resolve additional
            information for a completion item.
        - completionItem: The server supports the following `CompletionItem` specific
            capabilities.
            
            @since 3.17.0
        """
        self.documentSelector = documentSelector
        self.workDoneProgress = workDoneProgress
        self.triggerCharacters = triggerCharacters
        self.allCommitCharacters = allCommitCharacters
        self.resolveProvider = resolveProvider
        self.completionItem = completionItem

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "CompletionRegistrationOptions":
        documentSelector = parse_or_type(obj["documentSelector"], (lambda v: parse_DocumentSelector(json_assert_type_array(v)), lambda v: json_assert_type_null(v)))
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        if triggerCharacters_json := json_get_optional_array(obj, "triggerCharacters"):
            triggerCharacters = [json_assert_type_string(i) for i in triggerCharacters_json]
        else:
            triggerCharacters = None
        if allCommitCharacters_json := json_get_optional_array(obj, "allCommitCharacters"):
            allCommitCharacters = [json_assert_type_string(i) for i in allCommitCharacters_json]
        else:
            allCommitCharacters = None
        if resolveProvider_json := json_get_optional_bool(obj, "resolveProvider"):
            resolveProvider = resolveProvider_json
        else:
            resolveProvider = None
        if completionItem_json := json_get_optional_object(obj, "completionItem"):
            completionItem = parse_AnonymousStructure12(completionItem_json)
        else:
            completionItem = None
        return cls(documentSelector=documentSelector, workDoneProgress=workDoneProgress, triggerCharacters=triggerCharacters, allCommitCharacters=allCommitCharacters, resolveProvider=resolveProvider, completionItem=completionItem)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["documentSelector"] = write_or_type(self.documentSelector, (lambda i: isinstance(i, List) and (len(i) == 0 or (((isinstance(i[0], Dict) and "language" in i[0].keys()) or (isinstance(i[0], Dict) and "scheme" in i[0].keys()) or (isinstance(i[0], Dict) and "pattern" in i[0].keys())) or (isinstance(i[0], NotebookCellTextDocumentFilter)))), lambda i: i is None), (lambda i: write_DocumentSelector(i), lambda i: i))
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        if self.triggerCharacters is not None:
            out["triggerCharacters"] = [i for i in self.triggerCharacters]
        if self.allCommitCharacters is not None:
            out["allCommitCharacters"] = [i for i in self.allCommitCharacters]
        if self.resolveProvider is not None:
            out["resolveProvider"] = self.resolveProvider
        if self.completionItem is not None:
            out["completionItem"] = write_AnonymousStructure12(self.completionItem)
        return out


@dataclass
class HoverParams(TextDocumentPositionParams):
    """
    Parameters for a [HoverRequest](#HoverRequest).

    *Generated from the TypeScript documentation*
    """

    # The text document.
    textDocument: "TextDocumentIdentifier"
    
    # The position inside the text document.
    position: "Position"
    
    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]

    def __init__(self, *, textDocument: "TextDocumentIdentifier", position: "Position", workDoneToken: Optional["ProgressToken"] = None) -> None:
        """
        - textDocument: The text document.
        - position: The position inside the text document.
        - workDoneToken: An optional token that a server can use to report work done progress.
        """
        self.textDocument = textDocument
        self.position = position
        self.workDoneToken = workDoneToken

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "HoverParams":
        textDocument = TextDocumentIdentifier.from_json(json_get_object(obj, "textDocument"))
        position = Position.from_json(json_get_object(obj, "position"))
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        return cls(textDocument=textDocument, position=position, workDoneToken=workDoneToken)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["textDocument"] = self.textDocument.to_json()
        out["position"] = self.position.to_json()
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        return out


AnonymousStructure41Keys = Literal["language","value"]

def parse_AnonymousStructure41(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure41Keys, Any]:
    out: Dict[AnonymousStructure41Keys, Any] = {}
    out["language"] = json_get_string(obj, "language")
    out["value"] = json_get_string(obj, "value")
    return out

def write_AnonymousStructure41(obj: Dict[AnonymousStructure41Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    out["language"] = obj["language"]
    out["value"] = obj["value"]
    return out


# MarkedString can be used to render human readable text. It is either a markdown string
# or a code-block that provides a language and a code snippet. The language identifier
# is semantically equal to the optional language identifier in fenced code blocks in GitHub
# issues. See https://help.github.com/articles/creating-and-highlighting-code-blocks/#syntax-highlighting
# 
# The pair of a language and a value is an equivalent to markdown:
# ```${language}
# ${value}
# ```
# 
# Note that markdown strings will be sanitized - that means html will be escaped.
# @deprecated use MarkupContent instead.
MarkedString = Union[str, Dict[AnonymousStructure41Keys, Any]]

def parse_MarkedString(arg: JSON_VALUE) -> MarkedString:
    return parse_or_type((arg), (lambda v: json_assert_type_string(v), lambda v: parse_AnonymousStructure41(json_assert_type_object(v))))

def write_MarkedString(arg: MarkedString) -> JSON_VALUE:
    return write_or_type(arg, (lambda i: isinstance(i, str), lambda i: isinstance(i, Dict) and "language" in i.keys() and "value" in i.keys()), (lambda i: i, lambda i: write_AnonymousStructure41(i)))


@dataclass
class Hover():
    """
    The result of a hover request.

    *Generated from the TypeScript documentation*
    """

    # The hover's content
    contents: Union["MarkupContent", "MarkedString", List["MarkedString"]]
    
    # An optional range inside the text document that is used to
    # visualize the hover, e.g. by changing the background color.
    range: Optional["Range"]

    def __init__(self, *, contents: Union["MarkupContent", "MarkedString", List["MarkedString"]], range: Optional["Range"] = None) -> None:
        """
        - contents: The hover's content
        - range: An optional range inside the text document that is used to
            visualize the hover, e.g. by changing the background color.
        """
        self.contents = contents
        self.range = range

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "Hover":
        contents = parse_or_type(obj["contents"], (lambda v: MarkupContent.from_json(json_assert_type_object(v)), lambda v: parse_MarkedString((v)), lambda v: [parse_MarkedString((i)) for i in json_assert_type_array(v)]))
        if range_json := json_get_optional_object(obj, "range"):
            range = Range.from_json(range_json)
        else:
            range = None
        return cls(contents=contents, range=range)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["contents"] = write_or_type(self.contents, (lambda i: isinstance(i, MarkupContent), lambda i: (isinstance(i, str)) or (isinstance(i, Dict) and "language" in i.keys() and "value" in i.keys()), lambda i: isinstance(i, List) and (len(i) == 0 or ((isinstance(i[0], str)) or (isinstance(i[0], Dict) and "language" in i[0].keys() and "value" in i[0].keys())))), (lambda i: i.to_json(), lambda i: write_MarkedString(i), lambda i: [write_MarkedString(i) for i in i]))
        if self.range is not None:
            out["range"] = self.range.to_json()
        return out


@dataclass
class HoverRegistrationOptions(TextDocumentRegistrationOptions, HoverOptions):
    """
    Registration options for a [HoverRequest](#HoverRequest).

    *Generated from the TypeScript documentation*
    """

    # A document selector to identify the scope of the registration. If set to null
    # the document selector provided on the client side will be used.
    documentSelector: Union["DocumentSelector", None]
    
    workDoneProgress: Optional[bool]

    def __init__(self, *, documentSelector: Union["DocumentSelector", None], workDoneProgress: Optional[bool] = None) -> None:
        """
        - documentSelector: A document selector to identify the scope of the registration. If set to null
            the document selector provided on the client side will be used.
        """
        self.documentSelector = documentSelector
        self.workDoneProgress = workDoneProgress

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "HoverRegistrationOptions":
        documentSelector = parse_or_type(obj["documentSelector"], (lambda v: parse_DocumentSelector(json_assert_type_array(v)), lambda v: json_assert_type_null(v)))
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        return cls(documentSelector=documentSelector, workDoneProgress=workDoneProgress)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["documentSelector"] = write_or_type(self.documentSelector, (lambda i: isinstance(i, List) and (len(i) == 0 or (((isinstance(i[0], Dict) and "language" in i[0].keys()) or (isinstance(i[0], Dict) and "scheme" in i[0].keys()) or (isinstance(i[0], Dict) and "pattern" in i[0].keys())) or (isinstance(i[0], NotebookCellTextDocumentFilter)))), lambda i: i is None), (lambda i: write_DocumentSelector(i), lambda i: i))
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        return out


@dataclass
class ParameterInformation():
    """
    Represents a parameter of a callable-signature. A parameter can
    have a label and a doc-comment.

    *Generated from the TypeScript documentation*
    """

    # The label of this parameter information.
    # 
    # Either a string or an inclusive start and exclusive end offsets within its containing
    # signature label. (see SignatureInformation.label). The offsets are based on a UTF-16
    # string representation as `Position` and `Range` does.
    # 
    # *Note*: a label of type string should be a substring of its containing signature label.
    # Its intended use case is to highlight the parameter label part in the `SignatureInformation.label`.
    label: Union[str, Tuple[int, int]]
    
    # The human-readable doc-comment of this parameter. Will be shown
    # in the UI but can be omitted.
    documentation: Optional[Union[str, "MarkupContent"]]

    def __init__(self, *, label: Union[str, Tuple[int, int]], documentation: Optional[Union[str, "MarkupContent"]] = None) -> None:
        """
        - label: The label of this parameter information.
            
            Either a string or an inclusive start and exclusive end offsets within its containing
            signature label. (see SignatureInformation.label). The offsets are based on a UTF-16
            string representation as `Position` and `Range` does.
            
            *Note*: a label of type string should be a substring of its containing signature label.
            Its intended use case is to highlight the parameter label part in the `SignatureInformation.label`.
        - documentation: The human-readable doc-comment of this parameter. Will be shown
            in the UI but can be omitted.
        """
        self.label = label
        self.documentation = documentation

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "ParameterInformation":
        label = parse_or_type(obj["label"], (lambda v: json_assert_type_string(v), lambda v: (json_assert_type_int(json_assert_type_array(v)[0]), json_assert_type_int(json_assert_type_array(v)[1]))))
        if documentation_json := obj.get("documentation"):
            documentation = parse_or_type(documentation_json, (lambda v: json_assert_type_string(v), lambda v: MarkupContent.from_json(json_assert_type_object(v))))
        else:
            documentation = None
        return cls(label=label, documentation=documentation)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["label"] = write_or_type(self.label, (lambda i: isinstance(i, str), lambda i: isinstance(i, Tuple)), (lambda i: i, lambda i: list(i)))
        if self.documentation is not None:
            out["documentation"] = write_or_type(self.documentation, (lambda i: isinstance(i, str), lambda i: isinstance(i, MarkupContent)), (lambda i: i, lambda i: i.to_json()))
        return out


@dataclass
class SignatureInformation():
    """
    Represents the signature of something callable. A signature
    can have a label, like a function-name, a doc-comment, and
    a set of parameters.

    *Generated from the TypeScript documentation*
    """

    # The label of this signature. Will be shown in
    # the UI.
    label: str
    
    # The human-readable doc-comment of this signature. Will be shown
    # in the UI but can be omitted.
    documentation: Optional[Union[str, "MarkupContent"]]
    
    # The parameters of this signature.
    parameters: Optional[List["ParameterInformation"]]
    
    # The index of the active parameter.
    # 
    # If provided, this is used in place of `SignatureHelp.activeParameter`.
    # 
    # @since 3.16.0
    activeParameter: Optional[int]

    def __init__(self, *, label: str, documentation: Optional[Union[str, "MarkupContent"]] = None, parameters: Optional[List["ParameterInformation"]] = None, activeParameter: Optional[int] = None) -> None:
        """
        - label: The label of this signature. Will be shown in
            the UI.
        - documentation: The human-readable doc-comment of this signature. Will be shown
            in the UI but can be omitted.
        - parameters: The parameters of this signature.
        - activeParameter: The index of the active parameter.
            
            If provided, this is used in place of `SignatureHelp.activeParameter`.
            
            @since 3.16.0
        """
        self.label = label
        self.documentation = documentation
        self.parameters = parameters
        self.activeParameter = activeParameter

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "SignatureInformation":
        label = json_get_string(obj, "label")
        if documentation_json := obj.get("documentation"):
            documentation = parse_or_type(documentation_json, (lambda v: json_assert_type_string(v), lambda v: MarkupContent.from_json(json_assert_type_object(v))))
        else:
            documentation = None
        if parameters_json := json_get_optional_array(obj, "parameters"):
            parameters = [ParameterInformation.from_json(json_assert_type_object(i)) for i in parameters_json]
        else:
            parameters = None
        if activeParameter_json := json_get_optional_int(obj, "activeParameter"):
            activeParameter = activeParameter_json
        else:
            activeParameter = None
        return cls(label=label, documentation=documentation, parameters=parameters, activeParameter=activeParameter)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["label"] = self.label
        if self.documentation is not None:
            out["documentation"] = write_or_type(self.documentation, (lambda i: isinstance(i, str), lambda i: isinstance(i, MarkupContent)), (lambda i: i, lambda i: i.to_json()))
        if self.parameters is not None:
            out["parameters"] = [i.to_json() for i in self.parameters]
        if self.activeParameter is not None:
            out["activeParameter"] = self.activeParameter
        return out


@dataclass
class SignatureHelp():
    """
    Signature help represents the signature of something
    callable. There can be multiple signature but only one
    active and only one active parameter.

    *Generated from the TypeScript documentation*
    """

    # One or more signatures.
    signatures: List["SignatureInformation"]
    
    # The active signature. If omitted or the value lies outside the
    # range of `signatures` the value defaults to zero or is ignored if
    # the `SignatureHelp` has no signatures.
    # 
    # Whenever possible implementors should make an active decision about
    # the active signature and shouldn't rely on a default value.
    # 
    # In future version of the protocol this property might become
    # mandatory to better express this.
    activeSignature: Optional[int]
    
    # The active parameter of the active signature. If omitted or the value
    # lies outside the range of `signatures[activeSignature].parameters`
    # defaults to 0 if the active signature has parameters. If
    # the active signature has no parameters it is ignored.
    # In future version of the protocol this property might become
    # mandatory to better express the active parameter if the
    # active signature does have any.
    activeParameter: Optional[int]

    def __init__(self, *, signatures: List["SignatureInformation"], activeSignature: Optional[int] = None, activeParameter: Optional[int] = None) -> None:
        """
        - signatures: One or more signatures.
        - activeSignature: The active signature. If omitted or the value lies outside the
            range of `signatures` the value defaults to zero or is ignored if
            the `SignatureHelp` has no signatures.
            
            Whenever possible implementors should make an active decision about
            the active signature and shouldn't rely on a default value.
            
            In future version of the protocol this property might become
            mandatory to better express this.
        - activeParameter: The active parameter of the active signature. If omitted or the value
            lies outside the range of `signatures[activeSignature].parameters`
            defaults to 0 if the active signature has parameters. If
            the active signature has no parameters it is ignored.
            In future version of the protocol this property might become
            mandatory to better express the active parameter if the
            active signature does have any.
        """
        self.signatures = signatures
        self.activeSignature = activeSignature
        self.activeParameter = activeParameter

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "SignatureHelp":
        signatures = [SignatureInformation.from_json(json_assert_type_object(i)) for i in json_get_array(obj, "signatures")]
        if activeSignature_json := json_get_optional_int(obj, "activeSignature"):
            activeSignature = activeSignature_json
        else:
            activeSignature = None
        if activeParameter_json := json_get_optional_int(obj, "activeParameter"):
            activeParameter = activeParameter_json
        else:
            activeParameter = None
        return cls(signatures=signatures, activeSignature=activeSignature, activeParameter=activeParameter)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["signatures"] = [i.to_json() for i in self.signatures]
        if self.activeSignature is not None:
            out["activeSignature"] = self.activeSignature
        if self.activeParameter is not None:
            out["activeParameter"] = self.activeParameter
        return out


@dataclass
class SignatureHelpContext():
    """
    Additional information about the context in which a signature help request was triggered.
    
    @since 3.15.0

    *Generated from the TypeScript documentation*
    """

    # Action that caused signature help to be triggered.
    triggerKind: "SignatureHelpTriggerKind"
    
    # Character that caused signature help to be triggered.
    # 
    # This is undefined when `triggerKind !== SignatureHelpTriggerKind.TriggerCharacter`
    triggerCharacter: Optional[str]
    
    # `true` if signature help was already showing when it was triggered.
    # 
    # Retriggers occurs when the signature help is already active and can be caused by actions such as
    # typing a trigger character, a cursor move, or document content changes.
    isRetrigger: bool
    
    # The currently active `SignatureHelp`.
    # 
    # The `activeSignatureHelp` has its `SignatureHelp.activeSignature` field updated based on
    # the user navigating through available signatures.
    activeSignatureHelp: Optional["SignatureHelp"]

    def __init__(self, *, triggerKind: "SignatureHelpTriggerKind", triggerCharacter: Optional[str] = None, isRetrigger: bool, activeSignatureHelp: Optional["SignatureHelp"] = None) -> None:
        """
        - triggerKind: Action that caused signature help to be triggered.
        - triggerCharacter: Character that caused signature help to be triggered.
            
            This is undefined when `triggerKind !== SignatureHelpTriggerKind.TriggerCharacter`
        - isRetrigger: `true` if signature help was already showing when it was triggered.
            
            Retriggers occurs when the signature help is already active and can be caused by actions such as
            typing a trigger character, a cursor move, or document content changes.
        - activeSignatureHelp: The currently active `SignatureHelp`.
            
            The `activeSignatureHelp` has its `SignatureHelp.activeSignature` field updated based on
            the user navigating through available signatures.
        """
        self.triggerKind = triggerKind
        self.triggerCharacter = triggerCharacter
        self.isRetrigger = isRetrigger
        self.activeSignatureHelp = activeSignatureHelp

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "SignatureHelpContext":
        triggerKind = SignatureHelpTriggerKind(json_get_int(obj, "triggerKind"))
        if triggerCharacter_json := json_get_optional_string(obj, "triggerCharacter"):
            triggerCharacter = triggerCharacter_json
        else:
            triggerCharacter = None
        isRetrigger = json_get_bool(obj, "isRetrigger")
        if activeSignatureHelp_json := json_get_optional_object(obj, "activeSignatureHelp"):
            activeSignatureHelp = SignatureHelp.from_json(activeSignatureHelp_json)
        else:
            activeSignatureHelp = None
        return cls(triggerKind=triggerKind, triggerCharacter=triggerCharacter, isRetrigger=isRetrigger, activeSignatureHelp=activeSignatureHelp)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["triggerKind"] = self.triggerKind.value
        if self.triggerCharacter is not None:
            out["triggerCharacter"] = self.triggerCharacter
        out["isRetrigger"] = self.isRetrigger
        if self.activeSignatureHelp is not None:
            out["activeSignatureHelp"] = self.activeSignatureHelp.to_json()
        return out


@dataclass
class SignatureHelpParams(TextDocumentPositionParams):
    """
    Parameters for a [SignatureHelpRequest](#SignatureHelpRequest).

    *Generated from the TypeScript documentation*
    """

    # The text document.
    textDocument: "TextDocumentIdentifier"
    
    # The position inside the text document.
    position: "Position"
    
    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]
    
    # The signature help context. This is only available if the client specifies
    # to send this using the client capability `textDocument.signatureHelp.contextSupport === true`
    # 
    # @since 3.15.0
    context: Optional["SignatureHelpContext"]

    def __init__(self, *, textDocument: "TextDocumentIdentifier", position: "Position", workDoneToken: Optional["ProgressToken"] = None, context: Optional["SignatureHelpContext"] = None) -> None:
        """
        - textDocument: The text document.
        - position: The position inside the text document.
        - workDoneToken: An optional token that a server can use to report work done progress.
        - context: The signature help context. This is only available if the client specifies
            to send this using the client capability `textDocument.signatureHelp.contextSupport === true`
            
            @since 3.15.0
        """
        self.textDocument = textDocument
        self.position = position
        self.workDoneToken = workDoneToken
        self.context = context

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "SignatureHelpParams":
        textDocument = TextDocumentIdentifier.from_json(json_get_object(obj, "textDocument"))
        position = Position.from_json(json_get_object(obj, "position"))
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        if context_json := json_get_optional_object(obj, "context"):
            context = SignatureHelpContext.from_json(context_json)
        else:
            context = None
        return cls(textDocument=textDocument, position=position, workDoneToken=workDoneToken, context=context)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["textDocument"] = self.textDocument.to_json()
        out["position"] = self.position.to_json()
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        if self.context is not None:
            out["context"] = self.context.to_json()
        return out


@dataclass
class SignatureHelpRegistrationOptions(TextDocumentRegistrationOptions, SignatureHelpOptions):
    """
    Registration options for a [SignatureHelpRequest](#SignatureHelpRequest).

    *Generated from the TypeScript documentation*
    """

    # A document selector to identify the scope of the registration. If set to null
    # the document selector provided on the client side will be used.
    documentSelector: Union["DocumentSelector", None]
    
    workDoneProgress: Optional[bool]
    
    # List of characters that trigger signature help automatically.
    triggerCharacters: Optional[List[str]]
    
    # List of characters that re-trigger signature help.
    # 
    # These trigger characters are only active when signature help is already showing. All trigger characters
    # are also counted as re-trigger characters.
    # 
    # @since 3.15.0
    retriggerCharacters: Optional[List[str]]

    def __init__(self, *, documentSelector: Union["DocumentSelector", None], workDoneProgress: Optional[bool] = None, triggerCharacters: Optional[List[str]] = None, retriggerCharacters: Optional[List[str]] = None) -> None:
        """
        - documentSelector: A document selector to identify the scope of the registration. If set to null
            the document selector provided on the client side will be used.
        - triggerCharacters: List of characters that trigger signature help automatically.
        - retriggerCharacters: List of characters that re-trigger signature help.
            
            These trigger characters are only active when signature help is already showing. All trigger characters
            are also counted as re-trigger characters.
            
            @since 3.15.0
        """
        self.documentSelector = documentSelector
        self.workDoneProgress = workDoneProgress
        self.triggerCharacters = triggerCharacters
        self.retriggerCharacters = retriggerCharacters

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "SignatureHelpRegistrationOptions":
        documentSelector = parse_or_type(obj["documentSelector"], (lambda v: parse_DocumentSelector(json_assert_type_array(v)), lambda v: json_assert_type_null(v)))
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        if triggerCharacters_json := json_get_optional_array(obj, "triggerCharacters"):
            triggerCharacters = [json_assert_type_string(i) for i in triggerCharacters_json]
        else:
            triggerCharacters = None
        if retriggerCharacters_json := json_get_optional_array(obj, "retriggerCharacters"):
            retriggerCharacters = [json_assert_type_string(i) for i in retriggerCharacters_json]
        else:
            retriggerCharacters = None
        return cls(documentSelector=documentSelector, workDoneProgress=workDoneProgress, triggerCharacters=triggerCharacters, retriggerCharacters=retriggerCharacters)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["documentSelector"] = write_or_type(self.documentSelector, (lambda i: isinstance(i, List) and (len(i) == 0 or (((isinstance(i[0], Dict) and "language" in i[0].keys()) or (isinstance(i[0], Dict) and "scheme" in i[0].keys()) or (isinstance(i[0], Dict) and "pattern" in i[0].keys())) or (isinstance(i[0], NotebookCellTextDocumentFilter)))), lambda i: i is None), (lambda i: write_DocumentSelector(i), lambda i: i))
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        if self.triggerCharacters is not None:
            out["triggerCharacters"] = [i for i in self.triggerCharacters]
        if self.retriggerCharacters is not None:
            out["retriggerCharacters"] = [i for i in self.retriggerCharacters]
        return out


@dataclass
class DefinitionParams(TextDocumentPositionParams):
    """
    Parameters for a [DefinitionRequest](#DefinitionRequest).

    *Generated from the TypeScript documentation*
    """

    # The text document.
    textDocument: "TextDocumentIdentifier"
    
    # The position inside the text document.
    position: "Position"
    
    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]
    
    # An optional token that a server can use to report partial results (e.g. streaming) to
    # the client.
    partialResultToken: Optional["ProgressToken"]

    def __init__(self, *, textDocument: "TextDocumentIdentifier", position: "Position", workDoneToken: Optional["ProgressToken"] = None, partialResultToken: Optional["ProgressToken"] = None) -> None:
        """
        - textDocument: The text document.
        - position: The position inside the text document.
        - workDoneToken: An optional token that a server can use to report work done progress.
        - partialResultToken: An optional token that a server can use to report partial results (e.g. streaming) to
            the client.
        """
        self.textDocument = textDocument
        self.position = position
        self.workDoneToken = workDoneToken
        self.partialResultToken = partialResultToken

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DefinitionParams":
        textDocument = TextDocumentIdentifier.from_json(json_get_object(obj, "textDocument"))
        position = Position.from_json(json_get_object(obj, "position"))
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        if partialResultToken_json := obj.get("partialResultToken"):
            partialResultToken = parse_ProgressToken(partialResultToken_json)
        else:
            partialResultToken = None
        return cls(textDocument=textDocument, position=position, workDoneToken=workDoneToken, partialResultToken=partialResultToken)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["textDocument"] = self.textDocument.to_json()
        out["position"] = self.position.to_json()
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        if self.partialResultToken is not None:
            out["partialResultToken"] = write_ProgressToken(self.partialResultToken)
        return out


@dataclass
class DefinitionRegistrationOptions(TextDocumentRegistrationOptions, DefinitionOptions):
    """
    Registration options for a [DefinitionRequest](#DefinitionRequest).

    *Generated from the TypeScript documentation*
    """

    # A document selector to identify the scope of the registration. If set to null
    # the document selector provided on the client side will be used.
    documentSelector: Union["DocumentSelector", None]
    
    workDoneProgress: Optional[bool]

    def __init__(self, *, documentSelector: Union["DocumentSelector", None], workDoneProgress: Optional[bool] = None) -> None:
        """
        - documentSelector: A document selector to identify the scope of the registration. If set to null
            the document selector provided on the client side will be used.
        """
        self.documentSelector = documentSelector
        self.workDoneProgress = workDoneProgress

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DefinitionRegistrationOptions":
        documentSelector = parse_or_type(obj["documentSelector"], (lambda v: parse_DocumentSelector(json_assert_type_array(v)), lambda v: json_assert_type_null(v)))
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        return cls(documentSelector=documentSelector, workDoneProgress=workDoneProgress)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["documentSelector"] = write_or_type(self.documentSelector, (lambda i: isinstance(i, List) and (len(i) == 0 or (((isinstance(i[0], Dict) and "language" in i[0].keys()) or (isinstance(i[0], Dict) and "scheme" in i[0].keys()) or (isinstance(i[0], Dict) and "pattern" in i[0].keys())) or (isinstance(i[0], NotebookCellTextDocumentFilter)))), lambda i: i is None), (lambda i: write_DocumentSelector(i), lambda i: i))
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        return out


@dataclass
class ReferenceContext():
    """
    Value-object that contains additional information when
    requesting references.

    *Generated from the TypeScript documentation*
    """

    # Include the declaration of the current symbol.
    includeDeclaration: bool

    def __init__(self, *, includeDeclaration: bool) -> None:
        """
        - includeDeclaration: Include the declaration of the current symbol.
        """
        self.includeDeclaration = includeDeclaration

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "ReferenceContext":
        includeDeclaration = json_get_bool(obj, "includeDeclaration")
        return cls(includeDeclaration=includeDeclaration)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["includeDeclaration"] = self.includeDeclaration
        return out


@dataclass
class ReferenceParams(TextDocumentPositionParams):
    """
    Parameters for a [ReferencesRequest](#ReferencesRequest).

    *Generated from the TypeScript documentation*
    """

    # The text document.
    textDocument: "TextDocumentIdentifier"
    
    # The position inside the text document.
    position: "Position"
    
    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]
    
    # An optional token that a server can use to report partial results (e.g. streaming) to
    # the client.
    partialResultToken: Optional["ProgressToken"]
    
    context: "ReferenceContext"

    def __init__(self, *, textDocument: "TextDocumentIdentifier", position: "Position", workDoneToken: Optional["ProgressToken"] = None, partialResultToken: Optional["ProgressToken"] = None, context: "ReferenceContext") -> None:
        """
        - textDocument: The text document.
        - position: The position inside the text document.
        - workDoneToken: An optional token that a server can use to report work done progress.
        - partialResultToken: An optional token that a server can use to report partial results (e.g. streaming) to
            the client.
        """
        self.textDocument = textDocument
        self.position = position
        self.workDoneToken = workDoneToken
        self.partialResultToken = partialResultToken
        self.context = context

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "ReferenceParams":
        textDocument = TextDocumentIdentifier.from_json(json_get_object(obj, "textDocument"))
        position = Position.from_json(json_get_object(obj, "position"))
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        if partialResultToken_json := obj.get("partialResultToken"):
            partialResultToken = parse_ProgressToken(partialResultToken_json)
        else:
            partialResultToken = None
        context = ReferenceContext.from_json(json_get_object(obj, "context"))
        return cls(textDocument=textDocument, position=position, workDoneToken=workDoneToken, partialResultToken=partialResultToken, context=context)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["textDocument"] = self.textDocument.to_json()
        out["position"] = self.position.to_json()
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        if self.partialResultToken is not None:
            out["partialResultToken"] = write_ProgressToken(self.partialResultToken)
        out["context"] = self.context.to_json()
        return out


@dataclass
class ReferenceRegistrationOptions(TextDocumentRegistrationOptions, ReferenceOptions):
    """
    Registration options for a [ReferencesRequest](#ReferencesRequest).

    *Generated from the TypeScript documentation*
    """

    # A document selector to identify the scope of the registration. If set to null
    # the document selector provided on the client side will be used.
    documentSelector: Union["DocumentSelector", None]
    
    workDoneProgress: Optional[bool]

    def __init__(self, *, documentSelector: Union["DocumentSelector", None], workDoneProgress: Optional[bool] = None) -> None:
        """
        - documentSelector: A document selector to identify the scope of the registration. If set to null
            the document selector provided on the client side will be used.
        """
        self.documentSelector = documentSelector
        self.workDoneProgress = workDoneProgress

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "ReferenceRegistrationOptions":
        documentSelector = parse_or_type(obj["documentSelector"], (lambda v: parse_DocumentSelector(json_assert_type_array(v)), lambda v: json_assert_type_null(v)))
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        return cls(documentSelector=documentSelector, workDoneProgress=workDoneProgress)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["documentSelector"] = write_or_type(self.documentSelector, (lambda i: isinstance(i, List) and (len(i) == 0 or (((isinstance(i[0], Dict) and "language" in i[0].keys()) or (isinstance(i[0], Dict) and "scheme" in i[0].keys()) or (isinstance(i[0], Dict) and "pattern" in i[0].keys())) or (isinstance(i[0], NotebookCellTextDocumentFilter)))), lambda i: i is None), (lambda i: write_DocumentSelector(i), lambda i: i))
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        return out


@dataclass
class DocumentHighlightParams(TextDocumentPositionParams):
    """
    Parameters for a [DocumentHighlightRequest](#DocumentHighlightRequest).

    *Generated from the TypeScript documentation*
    """

    # The text document.
    textDocument: "TextDocumentIdentifier"
    
    # The position inside the text document.
    position: "Position"
    
    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]
    
    # An optional token that a server can use to report partial results (e.g. streaming) to
    # the client.
    partialResultToken: Optional["ProgressToken"]

    def __init__(self, *, textDocument: "TextDocumentIdentifier", position: "Position", workDoneToken: Optional["ProgressToken"] = None, partialResultToken: Optional["ProgressToken"] = None) -> None:
        """
        - textDocument: The text document.
        - position: The position inside the text document.
        - workDoneToken: An optional token that a server can use to report work done progress.
        - partialResultToken: An optional token that a server can use to report partial results (e.g. streaming) to
            the client.
        """
        self.textDocument = textDocument
        self.position = position
        self.workDoneToken = workDoneToken
        self.partialResultToken = partialResultToken

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DocumentHighlightParams":
        textDocument = TextDocumentIdentifier.from_json(json_get_object(obj, "textDocument"))
        position = Position.from_json(json_get_object(obj, "position"))
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        if partialResultToken_json := obj.get("partialResultToken"):
            partialResultToken = parse_ProgressToken(partialResultToken_json)
        else:
            partialResultToken = None
        return cls(textDocument=textDocument, position=position, workDoneToken=workDoneToken, partialResultToken=partialResultToken)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["textDocument"] = self.textDocument.to_json()
        out["position"] = self.position.to_json()
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        if self.partialResultToken is not None:
            out["partialResultToken"] = write_ProgressToken(self.partialResultToken)
        return out


@dataclass
class DocumentHighlight():
    """
    A document highlight is a range inside a text document which deserves
    special attention. Usually a document highlight is visualized by changing
    the background color of its range.

    *Generated from the TypeScript documentation*
    """

    # The range this highlight applies to.
    range: "Range"
    
    # The highlight kind, default is [text](#DocumentHighlightKind.Text).
    kind: Optional["DocumentHighlightKind"]

    def __init__(self, *, range: "Range", kind: Optional["DocumentHighlightKind"] = None) -> None:
        """
        - range: The range this highlight applies to.
        - kind: The highlight kind, default is [text](#DocumentHighlightKind.Text).
        """
        self.range = range
        self.kind = kind

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DocumentHighlight":
        range = Range.from_json(json_get_object(obj, "range"))
        if kind_json := json_get_optional_int(obj, "kind"):
            kind = DocumentHighlightKind(kind_json)
        else:
            kind = None
        return cls(range=range, kind=kind)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["range"] = self.range.to_json()
        if self.kind is not None:
            out["kind"] = self.kind.value
        return out


@dataclass
class DocumentHighlightRegistrationOptions(TextDocumentRegistrationOptions, DocumentHighlightOptions):
    """
    Registration options for a [DocumentHighlightRequest](#DocumentHighlightRequest).

    *Generated from the TypeScript documentation*
    """

    # A document selector to identify the scope of the registration. If set to null
    # the document selector provided on the client side will be used.
    documentSelector: Union["DocumentSelector", None]
    
    workDoneProgress: Optional[bool]

    def __init__(self, *, documentSelector: Union["DocumentSelector", None], workDoneProgress: Optional[bool] = None) -> None:
        """
        - documentSelector: A document selector to identify the scope of the registration. If set to null
            the document selector provided on the client side will be used.
        """
        self.documentSelector = documentSelector
        self.workDoneProgress = workDoneProgress

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DocumentHighlightRegistrationOptions":
        documentSelector = parse_or_type(obj["documentSelector"], (lambda v: parse_DocumentSelector(json_assert_type_array(v)), lambda v: json_assert_type_null(v)))
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        return cls(documentSelector=documentSelector, workDoneProgress=workDoneProgress)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["documentSelector"] = write_or_type(self.documentSelector, (lambda i: isinstance(i, List) and (len(i) == 0 or (((isinstance(i[0], Dict) and "language" in i[0].keys()) or (isinstance(i[0], Dict) and "scheme" in i[0].keys()) or (isinstance(i[0], Dict) and "pattern" in i[0].keys())) or (isinstance(i[0], NotebookCellTextDocumentFilter)))), lambda i: i is None), (lambda i: write_DocumentSelector(i), lambda i: i))
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        return out


@dataclass
class DocumentSymbolParams():
    """
    Parameters for a [DocumentSymbolRequest](#DocumentSymbolRequest).

    *Generated from the TypeScript documentation*
    """

    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]
    
    # An optional token that a server can use to report partial results (e.g. streaming) to
    # the client.
    partialResultToken: Optional["ProgressToken"]
    
    # The text document.
    textDocument: "TextDocumentIdentifier"

    def __init__(self, *, workDoneToken: Optional["ProgressToken"] = None, partialResultToken: Optional["ProgressToken"] = None, textDocument: "TextDocumentIdentifier") -> None:
        """
        - workDoneToken: An optional token that a server can use to report work done progress.
        - partialResultToken: An optional token that a server can use to report partial results (e.g. streaming) to
            the client.
        - textDocument: The text document.
        """
        self.workDoneToken = workDoneToken
        self.partialResultToken = partialResultToken
        self.textDocument = textDocument

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DocumentSymbolParams":
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        if partialResultToken_json := obj.get("partialResultToken"):
            partialResultToken = parse_ProgressToken(partialResultToken_json)
        else:
            partialResultToken = None
        textDocument = TextDocumentIdentifier.from_json(json_get_object(obj, "textDocument"))
        return cls(workDoneToken=workDoneToken, partialResultToken=partialResultToken, textDocument=textDocument)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        if self.partialResultToken is not None:
            out["partialResultToken"] = write_ProgressToken(self.partialResultToken)
        out["textDocument"] = self.textDocument.to_json()
        return out


@dataclass
class BaseSymbolInformation():
    """
    A base for all symbol information.

    *Generated from the TypeScript documentation*
    """

    # The name of this symbol.
    name: str
    
    # The kind of this symbol.
    kind: "SymbolKind"
    
    # Tags for this symbol.
    # 
    # @since 3.16.0
    tags: Optional[List["SymbolTag"]]
    
    # The name of the symbol containing this symbol. This information is for
    # user interface purposes (e.g. to render a qualifier in the user interface
    # if necessary). It can't be used to re-infer a hierarchy for the document
    # symbols.
    containerName: Optional[str]

    def __init__(self, *, name: str, kind: "SymbolKind", tags: Optional[List["SymbolTag"]] = None, containerName: Optional[str] = None) -> None:
        """
        - name: The name of this symbol.
        - kind: The kind of this symbol.
        - tags: Tags for this symbol.
            
            @since 3.16.0
        - containerName: The name of the symbol containing this symbol. This information is for
            user interface purposes (e.g. to render a qualifier in the user interface
            if necessary). It can't be used to re-infer a hierarchy for the document
            symbols.
        """
        self.name = name
        self.kind = kind
        self.tags = tags
        self.containerName = containerName

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "BaseSymbolInformation":
        name = json_get_string(obj, "name")
        kind = SymbolKind(json_get_int(obj, "kind"))
        if tags_json := json_get_optional_array(obj, "tags"):
            tags = [SymbolTag(json_assert_type_int(i)) for i in tags_json]
        else:
            tags = None
        if containerName_json := json_get_optional_string(obj, "containerName"):
            containerName = containerName_json
        else:
            containerName = None
        return cls(name=name, kind=kind, tags=tags, containerName=containerName)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["name"] = self.name
        out["kind"] = self.kind.value
        if self.tags is not None:
            out["tags"] = [i.value for i in self.tags]
        if self.containerName is not None:
            out["containerName"] = self.containerName
        return out


@dataclass
class SymbolInformation(BaseSymbolInformation):
    """
    Represents information about programming constructs like variables, classes,
    interfaces etc.

    *Generated from the TypeScript documentation*
    """

    # The name of this symbol.
    name: str
    
    # The kind of this symbol.
    kind: "SymbolKind"
    
    # Tags for this symbol.
    # 
    # @since 3.16.0
    tags: Optional[List["SymbolTag"]]
    
    # The name of the symbol containing this symbol. This information is for
    # user interface purposes (e.g. to render a qualifier in the user interface
    # if necessary). It can't be used to re-infer a hierarchy for the document
    # symbols.
    containerName: Optional[str]
    
    # Indicates if this symbol is deprecated.
    # 
    # @deprecated Use tags instead
    deprecated: Optional[bool]
    
    # The location of this symbol. The location's range is used by a tool
    # to reveal the location in the editor. If the symbol is selected in the
    # tool the range's start information is used to position the cursor. So
    # the range usually spans more than the actual symbol's name and does
    # normally include things like visibility modifiers.
    # 
    # The range doesn't have to denote a node range in the sense of an abstract
    # syntax tree. It can therefore not be used to re-construct a hierarchy of
    # the symbols.
    location: "Location"

    def __init__(self, *, name: str, kind: "SymbolKind", tags: Optional[List["SymbolTag"]] = None, containerName: Optional[str] = None, deprecated: Optional[bool] = None, location: "Location") -> None:
        """
        - name: The name of this symbol.
        - kind: The kind of this symbol.
        - tags: Tags for this symbol.
            
            @since 3.16.0
        - containerName: The name of the symbol containing this symbol. This information is for
            user interface purposes (e.g. to render a qualifier in the user interface
            if necessary). It can't be used to re-infer a hierarchy for the document
            symbols.
        - deprecated: Indicates if this symbol is deprecated.
            
            @deprecated Use tags instead
        - location: The location of this symbol. The location's range is used by a tool
            to reveal the location in the editor. If the symbol is selected in the
            tool the range's start information is used to position the cursor. So
            the range usually spans more than the actual symbol's name and does
            normally include things like visibility modifiers.
            
            The range doesn't have to denote a node range in the sense of an abstract
            syntax tree. It can therefore not be used to re-construct a hierarchy of
            the symbols.
        """
        self.name = name
        self.kind = kind
        self.tags = tags
        self.containerName = containerName
        self.deprecated = deprecated
        self.location = location

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "SymbolInformation":
        name = json_get_string(obj, "name")
        kind = SymbolKind(json_get_int(obj, "kind"))
        if tags_json := json_get_optional_array(obj, "tags"):
            tags = [SymbolTag(json_assert_type_int(i)) for i in tags_json]
        else:
            tags = None
        if containerName_json := json_get_optional_string(obj, "containerName"):
            containerName = containerName_json
        else:
            containerName = None
        if deprecated_json := json_get_optional_bool(obj, "deprecated"):
            deprecated = deprecated_json
        else:
            deprecated = None
        location = Location.from_json(json_get_object(obj, "location"))
        return cls(name=name, kind=kind, tags=tags, containerName=containerName, deprecated=deprecated, location=location)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["name"] = self.name
        out["kind"] = self.kind.value
        if self.tags is not None:
            out["tags"] = [i.value for i in self.tags]
        if self.containerName is not None:
            out["containerName"] = self.containerName
        if self.deprecated is not None:
            out["deprecated"] = self.deprecated
        out["location"] = self.location.to_json()
        return out


@dataclass
class DocumentSymbol():
    """
    Represents programming constructs like variables, classes, interfaces etc.
    that appear in a document. Document symbols can be hierarchical and they
    have two ranges: one that encloses its definition and one that points to
    its most interesting range, e.g. the range of an identifier.

    *Generated from the TypeScript documentation*
    """

    # The name of this symbol. Will be displayed in the user interface and therefore must not be
    # an empty string or a string only consisting of white spaces.
    name: str
    
    # More detail for this symbol, e.g the signature of a function.
    detail: Optional[str]
    
    # The kind of this symbol.
    kind: "SymbolKind"
    
    # Tags for this document symbol.
    # 
    # @since 3.16.0
    tags: Optional[List["SymbolTag"]]
    
    # Indicates if this symbol is deprecated.
    # 
    # @deprecated Use tags instead
    deprecated: Optional[bool]
    
    # The range enclosing this symbol not including leading/trailing whitespace but everything else
    # like comments. This information is typically used to determine if the clients cursor is
    # inside the symbol to reveal in the symbol in the UI.
    range: "Range"
    
    # The range that should be selected and revealed when this symbol is being picked, e.g the name of a function.
    # Must be contained by the `range`.
    selectionRange: "Range"
    
    # Children of this symbol, e.g. properties of a class.
    children: Optional[List["DocumentSymbol"]]

    def __init__(self, *, name: str, detail: Optional[str] = None, kind: "SymbolKind", tags: Optional[List["SymbolTag"]] = None, deprecated: Optional[bool] = None, range: "Range", selectionRange: "Range", children: Optional[List["DocumentSymbol"]] = None) -> None:
        """
        - name: The name of this symbol. Will be displayed in the user interface and therefore must not be
            an empty string or a string only consisting of white spaces.
        - detail: More detail for this symbol, e.g the signature of a function.
        - kind: The kind of this symbol.
        - tags: Tags for this document symbol.
            
            @since 3.16.0
        - deprecated: Indicates if this symbol is deprecated.
            
            @deprecated Use tags instead
        - range: The range enclosing this symbol not including leading/trailing whitespace but everything else
            like comments. This information is typically used to determine if the clients cursor is
            inside the symbol to reveal in the symbol in the UI.
        - selectionRange: The range that should be selected and revealed when this symbol is being picked, e.g the name of a function.
            Must be contained by the `range`.
        - children: Children of this symbol, e.g. properties of a class.
        """
        self.name = name
        self.detail = detail
        self.kind = kind
        self.tags = tags
        self.deprecated = deprecated
        self.range = range
        self.selectionRange = selectionRange
        self.children = children

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DocumentSymbol":
        name = json_get_string(obj, "name")
        if detail_json := json_get_optional_string(obj, "detail"):
            detail = detail_json
        else:
            detail = None
        kind = SymbolKind(json_get_int(obj, "kind"))
        if tags_json := json_get_optional_array(obj, "tags"):
            tags = [SymbolTag(json_assert_type_int(i)) for i in tags_json]
        else:
            tags = None
        if deprecated_json := json_get_optional_bool(obj, "deprecated"):
            deprecated = deprecated_json
        else:
            deprecated = None
        range = Range.from_json(json_get_object(obj, "range"))
        selectionRange = Range.from_json(json_get_object(obj, "selectionRange"))
        if children_json := json_get_optional_array(obj, "children"):
            children = [DocumentSymbol.from_json(json_assert_type_object(i)) for i in children_json]
        else:
            children = None
        return cls(name=name, detail=detail, kind=kind, tags=tags, deprecated=deprecated, range=range, selectionRange=selectionRange, children=children)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["name"] = self.name
        if self.detail is not None:
            out["detail"] = self.detail
        out["kind"] = self.kind.value
        if self.tags is not None:
            out["tags"] = [i.value for i in self.tags]
        if self.deprecated is not None:
            out["deprecated"] = self.deprecated
        out["range"] = self.range.to_json()
        out["selectionRange"] = self.selectionRange.to_json()
        if self.children is not None:
            out["children"] = [i.to_json() for i in self.children]
        return out


@dataclass
class DocumentSymbolRegistrationOptions(TextDocumentRegistrationOptions, DocumentSymbolOptions):
    """
    Registration options for a [DocumentSymbolRequest](#DocumentSymbolRequest).

    *Generated from the TypeScript documentation*
    """

    # A document selector to identify the scope of the registration. If set to null
    # the document selector provided on the client side will be used.
    documentSelector: Union["DocumentSelector", None]
    
    workDoneProgress: Optional[bool]
    
    # A human-readable string that is shown when multiple outlines trees
    # are shown for the same document.
    # 
    # @since 3.16.0
    label: Optional[str]

    def __init__(self, *, documentSelector: Union["DocumentSelector", None], workDoneProgress: Optional[bool] = None, label: Optional[str] = None) -> None:
        """
        - documentSelector: A document selector to identify the scope of the registration. If set to null
            the document selector provided on the client side will be used.
        - label: A human-readable string that is shown when multiple outlines trees
            are shown for the same document.
            
            @since 3.16.0
        """
        self.documentSelector = documentSelector
        self.workDoneProgress = workDoneProgress
        self.label = label

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DocumentSymbolRegistrationOptions":
        documentSelector = parse_or_type(obj["documentSelector"], (lambda v: parse_DocumentSelector(json_assert_type_array(v)), lambda v: json_assert_type_null(v)))
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        if label_json := json_get_optional_string(obj, "label"):
            label = label_json
        else:
            label = None
        return cls(documentSelector=documentSelector, workDoneProgress=workDoneProgress, label=label)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["documentSelector"] = write_or_type(self.documentSelector, (lambda i: isinstance(i, List) and (len(i) == 0 or (((isinstance(i[0], Dict) and "language" in i[0].keys()) or (isinstance(i[0], Dict) and "scheme" in i[0].keys()) or (isinstance(i[0], Dict) and "pattern" in i[0].keys())) or (isinstance(i[0], NotebookCellTextDocumentFilter)))), lambda i: i is None), (lambda i: write_DocumentSelector(i), lambda i: i))
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        if self.label is not None:
            out["label"] = self.label
        return out


@dataclass
class CodeActionContext():
    """
    Contains additional diagnostic information about the context in which
    a [code action](#CodeActionProvider.provideCodeActions) is run.

    *Generated from the TypeScript documentation*
    """

    # An array of diagnostics known on the client side overlapping the range provided to the
    # `textDocument/codeAction` request. They are provided so that the server knows which
    # errors are currently presented to the user for the given range. There is no guarantee
    # that these accurately reflect the error state of the resource. The primary parameter
    # to compute code actions is the provided range.
    diagnostics: List["Diagnostic"]
    
    # Requested kind of actions to return.
    # 
    # Actions not of this kind are filtered out by the client before being shown. So servers
    # can omit computing them.
    only: Optional[List["CodeActionKind"]]
    
    # The reason why code actions were requested.
    # 
    # @since 3.17.0
    triggerKind: Optional["CodeActionTriggerKind"]

    def __init__(self, *, diagnostics: List["Diagnostic"], only: Optional[List["CodeActionKind"]] = None, triggerKind: Optional["CodeActionTriggerKind"] = None) -> None:
        """
        - diagnostics: An array of diagnostics known on the client side overlapping the range provided to the
            `textDocument/codeAction` request. They are provided so that the server knows which
            errors are currently presented to the user for the given range. There is no guarantee
            that these accurately reflect the error state of the resource. The primary parameter
            to compute code actions is the provided range.
        - only: Requested kind of actions to return.
            
            Actions not of this kind are filtered out by the client before being shown. So servers
            can omit computing them.
        - triggerKind: The reason why code actions were requested.
            
            @since 3.17.0
        """
        self.diagnostics = diagnostics
        self.only = only
        self.triggerKind = triggerKind

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "CodeActionContext":
        diagnostics = [Diagnostic.from_json(json_assert_type_object(i)) for i in json_get_array(obj, "diagnostics")]
        if only_json := json_get_optional_array(obj, "only"):
            only = [CodeActionKind(json_assert_type_string(i)) for i in only_json]
        else:
            only = None
        if triggerKind_json := json_get_optional_int(obj, "triggerKind"):
            triggerKind = CodeActionTriggerKind(triggerKind_json)
        else:
            triggerKind = None
        return cls(diagnostics=diagnostics, only=only, triggerKind=triggerKind)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["diagnostics"] = [i.to_json() for i in self.diagnostics]
        if self.only is not None:
            out["only"] = [i.value for i in self.only]
        if self.triggerKind is not None:
            out["triggerKind"] = self.triggerKind.value
        return out


@dataclass
class CodeActionParams():
    """
    The parameters of a [CodeActionRequest](#CodeActionRequest).

    *Generated from the TypeScript documentation*
    """

    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]
    
    # An optional token that a server can use to report partial results (e.g. streaming) to
    # the client.
    partialResultToken: Optional["ProgressToken"]
    
    # The document in which the command was invoked.
    textDocument: "TextDocumentIdentifier"
    
    # The range for which the command was invoked.
    range: "Range"
    
    # Context carrying additional information.
    context: "CodeActionContext"

    def __init__(self, *, workDoneToken: Optional["ProgressToken"] = None, partialResultToken: Optional["ProgressToken"] = None, textDocument: "TextDocumentIdentifier", range: "Range", context: "CodeActionContext") -> None:
        """
        - workDoneToken: An optional token that a server can use to report work done progress.
        - partialResultToken: An optional token that a server can use to report partial results (e.g. streaming) to
            the client.
        - textDocument: The document in which the command was invoked.
        - range: The range for which the command was invoked.
        - context: Context carrying additional information.
        """
        self.workDoneToken = workDoneToken
        self.partialResultToken = partialResultToken
        self.textDocument = textDocument
        self.range = range
        self.context = context

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "CodeActionParams":
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        if partialResultToken_json := obj.get("partialResultToken"):
            partialResultToken = parse_ProgressToken(partialResultToken_json)
        else:
            partialResultToken = None
        textDocument = TextDocumentIdentifier.from_json(json_get_object(obj, "textDocument"))
        range = Range.from_json(json_get_object(obj, "range"))
        context = CodeActionContext.from_json(json_get_object(obj, "context"))
        return cls(workDoneToken=workDoneToken, partialResultToken=partialResultToken, textDocument=textDocument, range=range, context=context)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        if self.partialResultToken is not None:
            out["partialResultToken"] = write_ProgressToken(self.partialResultToken)
        out["textDocument"] = self.textDocument.to_json()
        out["range"] = self.range.to_json()
        out["context"] = self.context.to_json()
        return out


AnonymousStructure3Keys = Literal["reason"]

def parse_AnonymousStructure3(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure3Keys, Any]:
    out: Dict[AnonymousStructure3Keys, Any] = {}
    out["reason"] = json_get_string(obj, "reason")
    return out

def write_AnonymousStructure3(obj: Dict[AnonymousStructure3Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    out["reason"] = obj["reason"]
    return out


@dataclass
class CodeAction():
    """
    A code action represents a change that can be performed in code, e.g. to fix a problem or
    to refactor code.
    
    A CodeAction must set either `edit` and/or a `command`. If both are supplied, the `edit` is applied first, then the `command` is executed.

    *Generated from the TypeScript documentation*
    """

    # A short, human-readable, title for this code action.
    title: str
    
    # The kind of the code action.
    # 
    # Used to filter code actions.
    kind: Optional["CodeActionKind"]
    
    # The diagnostics that this code action resolves.
    diagnostics: Optional[List["Diagnostic"]]
    
    # Marks this as a preferred action. Preferred actions are used by the `auto fix` command and can be targeted
    # by keybindings.
    # 
    # A quick fix should be marked preferred if it properly addresses the underlying error.
    # A refactoring should be marked preferred if it is the most reasonable choice of actions to take.
    # 
    # @since 3.15.0
    isPreferred: Optional[bool]
    
    # Marks that the code action cannot currently be applied.
    # 
    # Clients should follow the following guidelines regarding disabled code actions:
    # 
    #   - Disabled code actions are not shown in automatic [lightbulbs](https://code.visualstudio.com/docs/editor/editingevolved#_code-action)
    #     code action menus.
    # 
    #   - Disabled actions are shown as faded out in the code action menu when the user requests a more specific type
    #     of code action, such as refactorings.
    # 
    #   - If the user has a [keybinding](https://code.visualstudio.com/docs/editor/refactoring#_keybindings-for-code-actions)
    #     that auto applies a code action and only disabled code actions are returned, the client should show the user an
    #     error message with `reason` in the editor.
    # 
    # @since 3.16.0
    disabled: Optional[Dict[AnonymousStructure3Keys, Any]]
    
    # The workspace edit this code action performs.
    edit: Optional["WorkspaceEdit"]
    
    # A command this code action executes. If a code action
    # provides an edit and a command, first the edit is
    # executed and then the command.
    command: Optional["Command"]
    
    # A data entry field that is preserved on a code action between
    # a `textDocument/codeAction` and a `codeAction/resolve` request.
    # 
    # @since 3.16.0
    data: Optional["LSPAny"]

    def __init__(self, *, title: str, kind: Optional["CodeActionKind"] = None, diagnostics: Optional[List["Diagnostic"]] = None, isPreferred: Optional[bool] = None, disabled: Optional[Dict[AnonymousStructure3Keys, Any]] = None, edit: Optional["WorkspaceEdit"] = None, command: Optional["Command"] = None, data: Optional["LSPAny"] = None) -> None:
        """
        - title: A short, human-readable, title for this code action.
        - kind: The kind of the code action.
            
            Used to filter code actions.
        - diagnostics: The diagnostics that this code action resolves.
        - isPreferred: Marks this as a preferred action. Preferred actions are used by the `auto fix` command and can be targeted
            by keybindings.
            
            A quick fix should be marked preferred if it properly addresses the underlying error.
            A refactoring should be marked preferred if it is the most reasonable choice of actions to take.
            
            @since 3.15.0
        - disabled: Marks that the code action cannot currently be applied.
            
            Clients should follow the following guidelines regarding disabled code actions:
            
              - Disabled code actions are not shown in automatic [lightbulbs](https://code.visualstudio.com/docs/editor/editingevolved#_code-action)
                code action menus.
            
              - Disabled actions are shown as faded out in the code action menu when the user requests a more specific type
                of code action, such as refactorings.
            
              - If the user has a [keybinding](https://code.visualstudio.com/docs/editor/refactoring#_keybindings-for-code-actions)
                that auto applies a code action and only disabled code actions are returned, the client should show the user an
                error message with `reason` in the editor.
            
            @since 3.16.0
        - edit: The workspace edit this code action performs.
        - command: A command this code action executes. If a code action
            provides an edit and a command, first the edit is
            executed and then the command.
        - data: A data entry field that is preserved on a code action between
            a `textDocument/codeAction` and a `codeAction/resolve` request.
            
            @since 3.16.0
        """
        self.title = title
        self.kind = kind
        self.diagnostics = diagnostics
        self.isPreferred = isPreferred
        self.disabled = disabled
        self.edit = edit
        self.command = command
        self.data = data

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "CodeAction":
        title = json_get_string(obj, "title")
        if kind_json := json_get_optional_string(obj, "kind"):
            kind = CodeActionKind(kind_json)
        else:
            kind = None
        if diagnostics_json := json_get_optional_array(obj, "diagnostics"):
            diagnostics = [Diagnostic.from_json(json_assert_type_object(i)) for i in diagnostics_json]
        else:
            diagnostics = None
        if isPreferred_json := json_get_optional_bool(obj, "isPreferred"):
            isPreferred = isPreferred_json
        else:
            isPreferred = None
        if disabled_json := json_get_optional_object(obj, "disabled"):
            disabled = parse_AnonymousStructure3(disabled_json)
        else:
            disabled = None
        if edit_json := json_get_optional_object(obj, "edit"):
            edit = WorkspaceEdit.from_json(edit_json)
        else:
            edit = None
        if command_json := json_get_optional_object(obj, "command"):
            command = Command.from_json(command_json)
        else:
            command = None
        if data_json := obj.get("data"):
            data = parse_LSPAny(data_json)
        else:
            data = None
        return cls(title=title, kind=kind, diagnostics=diagnostics, isPreferred=isPreferred, disabled=disabled, edit=edit, command=command, data=data)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["title"] = self.title
        if self.kind is not None:
            out["kind"] = self.kind.value
        if self.diagnostics is not None:
            out["diagnostics"] = [i.to_json() for i in self.diagnostics]
        if self.isPreferred is not None:
            out["isPreferred"] = self.isPreferred
        if self.disabled is not None:
            out["disabled"] = write_AnonymousStructure3(self.disabled)
        if self.edit is not None:
            out["edit"] = self.edit.to_json()
        if self.command is not None:
            out["command"] = self.command.to_json()
        if self.data is not None:
            out["data"] = write_LSPAny(self.data)
        return out


@dataclass
class CodeActionRegistrationOptions(TextDocumentRegistrationOptions, CodeActionOptions):
    """
    Registration options for a [CodeActionRequest](#CodeActionRequest).

    *Generated from the TypeScript documentation*
    """

    # A document selector to identify the scope of the registration. If set to null
    # the document selector provided on the client side will be used.
    documentSelector: Union["DocumentSelector", None]
    
    workDoneProgress: Optional[bool]
    
    # CodeActionKinds that this server may return.
    # 
    # The list of kinds may be generic, such as `CodeActionKind.Refactor`, or the server
    # may list out every specific kind they provide.
    codeActionKinds: Optional[List["CodeActionKind"]]
    
    # The server provides support to resolve additional
    # information for a code action.
    # 
    # @since 3.16.0
    resolveProvider: Optional[bool]

    def __init__(self, *, documentSelector: Union["DocumentSelector", None], workDoneProgress: Optional[bool] = None, codeActionKinds: Optional[List["CodeActionKind"]] = None, resolveProvider: Optional[bool] = None) -> None:
        """
        - documentSelector: A document selector to identify the scope of the registration. If set to null
            the document selector provided on the client side will be used.
        - codeActionKinds: CodeActionKinds that this server may return.
            
            The list of kinds may be generic, such as `CodeActionKind.Refactor`, or the server
            may list out every specific kind they provide.
        - resolveProvider: The server provides support to resolve additional
            information for a code action.
            
            @since 3.16.0
        """
        self.documentSelector = documentSelector
        self.workDoneProgress = workDoneProgress
        self.codeActionKinds = codeActionKinds
        self.resolveProvider = resolveProvider

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "CodeActionRegistrationOptions":
        documentSelector = parse_or_type(obj["documentSelector"], (lambda v: parse_DocumentSelector(json_assert_type_array(v)), lambda v: json_assert_type_null(v)))
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        if codeActionKinds_json := json_get_optional_array(obj, "codeActionKinds"):
            codeActionKinds = [CodeActionKind(json_assert_type_string(i)) for i in codeActionKinds_json]
        else:
            codeActionKinds = None
        if resolveProvider_json := json_get_optional_bool(obj, "resolveProvider"):
            resolveProvider = resolveProvider_json
        else:
            resolveProvider = None
        return cls(documentSelector=documentSelector, workDoneProgress=workDoneProgress, codeActionKinds=codeActionKinds, resolveProvider=resolveProvider)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["documentSelector"] = write_or_type(self.documentSelector, (lambda i: isinstance(i, List) and (len(i) == 0 or (((isinstance(i[0], Dict) and "language" in i[0].keys()) or (isinstance(i[0], Dict) and "scheme" in i[0].keys()) or (isinstance(i[0], Dict) and "pattern" in i[0].keys())) or (isinstance(i[0], NotebookCellTextDocumentFilter)))), lambda i: i is None), (lambda i: write_DocumentSelector(i), lambda i: i))
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        if self.codeActionKinds is not None:
            out["codeActionKinds"] = [i.value for i in self.codeActionKinds]
        if self.resolveProvider is not None:
            out["resolveProvider"] = self.resolveProvider
        return out


@dataclass
class WorkspaceSymbolParams():
    """
    The parameters of a [WorkspaceSymbolRequest](#WorkspaceSymbolRequest).

    *Generated from the TypeScript documentation*
    """

    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]
    
    # An optional token that a server can use to report partial results (e.g. streaming) to
    # the client.
    partialResultToken: Optional["ProgressToken"]
    
    # A query string to filter symbols by. Clients may send an empty
    # string here to request all symbols.
    query: str

    def __init__(self, *, workDoneToken: Optional["ProgressToken"] = None, partialResultToken: Optional["ProgressToken"] = None, query: str) -> None:
        """
        - workDoneToken: An optional token that a server can use to report work done progress.
        - partialResultToken: An optional token that a server can use to report partial results (e.g. streaming) to
            the client.
        - query: A query string to filter symbols by. Clients may send an empty
            string here to request all symbols.
        """
        self.workDoneToken = workDoneToken
        self.partialResultToken = partialResultToken
        self.query = query

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "WorkspaceSymbolParams":
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        if partialResultToken_json := obj.get("partialResultToken"):
            partialResultToken = parse_ProgressToken(partialResultToken_json)
        else:
            partialResultToken = None
        query = json_get_string(obj, "query")
        return cls(workDoneToken=workDoneToken, partialResultToken=partialResultToken, query=query)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        if self.partialResultToken is not None:
            out["partialResultToken"] = write_ProgressToken(self.partialResultToken)
        out["query"] = self.query
        return out


AnonymousStructure4Keys = Literal["uri"]

def parse_AnonymousStructure4(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure4Keys, Any]:
    out: Dict[AnonymousStructure4Keys, Any] = {}
    out["uri"] = json_get_string(obj, "uri")
    return out

def write_AnonymousStructure4(obj: Dict[AnonymousStructure4Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    out["uri"] = obj["uri"]
    return out


@dataclass
class WorkspaceSymbol(BaseSymbolInformation):
    """
    A special workspace symbol that supports locations without a range.
    
    See also SymbolInformation.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # The name of this symbol.
    name: str
    
    # The kind of this symbol.
    kind: "SymbolKind"
    
    # Tags for this symbol.
    # 
    # @since 3.16.0
    tags: Optional[List["SymbolTag"]]
    
    # The name of the symbol containing this symbol. This information is for
    # user interface purposes (e.g. to render a qualifier in the user interface
    # if necessary). It can't be used to re-infer a hierarchy for the document
    # symbols.
    containerName: Optional[str]
    
    # The location of the symbol. Whether a server is allowed to
    # return a location without a range depends on the client
    # capability `workspace.symbol.resolveSupport`.
    # 
    # See SymbolInformation#location for more details.
    location: Union["Location", Dict[AnonymousStructure4Keys, Any]]
    
    # A data entry field that is preserved on a workspace symbol between a
    # workspace symbol request and a workspace symbol resolve request.
    data: Optional["LSPAny"]

    def __init__(self, *, name: str, kind: "SymbolKind", tags: Optional[List["SymbolTag"]] = None, containerName: Optional[str] = None, location: Union["Location", Dict[AnonymousStructure4Keys, Any]], data: Optional["LSPAny"] = None) -> None:
        """
        - name: The name of this symbol.
        - kind: The kind of this symbol.
        - tags: Tags for this symbol.
            
            @since 3.16.0
        - containerName: The name of the symbol containing this symbol. This information is for
            user interface purposes (e.g. to render a qualifier in the user interface
            if necessary). It can't be used to re-infer a hierarchy for the document
            symbols.
        - location: The location of the symbol. Whether a server is allowed to
            return a location without a range depends on the client
            capability `workspace.symbol.resolveSupport`.
            
            See SymbolInformation#location for more details.
        - data: A data entry field that is preserved on a workspace symbol between a
            workspace symbol request and a workspace symbol resolve request.
        """
        self.name = name
        self.kind = kind
        self.tags = tags
        self.containerName = containerName
        self.location = location
        self.data = data

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "WorkspaceSymbol":
        name = json_get_string(obj, "name")
        kind = SymbolKind(json_get_int(obj, "kind"))
        if tags_json := json_get_optional_array(obj, "tags"):
            tags = [SymbolTag(json_assert_type_int(i)) for i in tags_json]
        else:
            tags = None
        if containerName_json := json_get_optional_string(obj, "containerName"):
            containerName = containerName_json
        else:
            containerName = None
        location = parse_or_type(obj["location"], (lambda v: Location.from_json(json_assert_type_object(v)), lambda v: parse_AnonymousStructure4(json_assert_type_object(v))))
        if data_json := obj.get("data"):
            data = parse_LSPAny(data_json)
        else:
            data = None
        return cls(name=name, kind=kind, tags=tags, containerName=containerName, location=location, data=data)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["name"] = self.name
        out["kind"] = self.kind.value
        if self.tags is not None:
            out["tags"] = [i.value for i in self.tags]
        if self.containerName is not None:
            out["containerName"] = self.containerName
        out["location"] = write_or_type(self.location, (lambda i: isinstance(i, Location), lambda i: isinstance(i, Dict) and "uri" in i.keys()), (lambda i: i.to_json(), lambda i: write_AnonymousStructure4(i)))
        if self.data is not None:
            out["data"] = write_LSPAny(self.data)
        return out


@dataclass
class WorkspaceSymbolRegistrationOptions(WorkspaceSymbolOptions):
    """
    Registration options for a [WorkspaceSymbolRequest](#WorkspaceSymbolRequest).

    *Generated from the TypeScript documentation*
    """

    workDoneProgress: Optional[bool]
    
    # The server provides support to resolve additional
    # information for a workspace symbol.
    # 
    # @since 3.17.0
    resolveProvider: Optional[bool]

    def __init__(self, *, workDoneProgress: Optional[bool] = None, resolveProvider: Optional[bool] = None) -> None:
        """
        - resolveProvider: The server provides support to resolve additional
            information for a workspace symbol.
            
            @since 3.17.0
        """
        self.workDoneProgress = workDoneProgress
        self.resolveProvider = resolveProvider

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "WorkspaceSymbolRegistrationOptions":
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        if resolveProvider_json := json_get_optional_bool(obj, "resolveProvider"):
            resolveProvider = resolveProvider_json
        else:
            resolveProvider = None
        return cls(workDoneProgress=workDoneProgress, resolveProvider=resolveProvider)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        if self.resolveProvider is not None:
            out["resolveProvider"] = self.resolveProvider
        return out


@dataclass
class CodeLensParams():
    """
    The parameters of a [CodeLensRequest](#CodeLensRequest).

    *Generated from the TypeScript documentation*
    """

    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]
    
    # An optional token that a server can use to report partial results (e.g. streaming) to
    # the client.
    partialResultToken: Optional["ProgressToken"]
    
    # The document to request code lens for.
    textDocument: "TextDocumentIdentifier"

    def __init__(self, *, workDoneToken: Optional["ProgressToken"] = None, partialResultToken: Optional["ProgressToken"] = None, textDocument: "TextDocumentIdentifier") -> None:
        """
        - workDoneToken: An optional token that a server can use to report work done progress.
        - partialResultToken: An optional token that a server can use to report partial results (e.g. streaming) to
            the client.
        - textDocument: The document to request code lens for.
        """
        self.workDoneToken = workDoneToken
        self.partialResultToken = partialResultToken
        self.textDocument = textDocument

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "CodeLensParams":
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        if partialResultToken_json := obj.get("partialResultToken"):
            partialResultToken = parse_ProgressToken(partialResultToken_json)
        else:
            partialResultToken = None
        textDocument = TextDocumentIdentifier.from_json(json_get_object(obj, "textDocument"))
        return cls(workDoneToken=workDoneToken, partialResultToken=partialResultToken, textDocument=textDocument)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        if self.partialResultToken is not None:
            out["partialResultToken"] = write_ProgressToken(self.partialResultToken)
        out["textDocument"] = self.textDocument.to_json()
        return out


@dataclass
class CodeLens():
    """
    A code lens represents a [command](#Command) that should be shown along with
    source text, like the number of references, a way to run tests, etc.
    
    A code lens is _unresolved_ when no command is associated to it. For performance
    reasons the creation of a code lens and resolving should be done in two stages.

    *Generated from the TypeScript documentation*
    """

    # The range in which this code lens is valid. Should only span a single line.
    range: "Range"
    
    # The command this code lens represents.
    command: Optional["Command"]
    
    # A data entry field that is preserved on a code lens item between
    # a [CodeLensRequest](#CodeLensRequest) and a [CodeLensResolveRequest]
    # (#CodeLensResolveRequest)
    data: Optional["LSPAny"]

    def __init__(self, *, range: "Range", command: Optional["Command"] = None, data: Optional["LSPAny"] = None) -> None:
        """
        - range: The range in which this code lens is valid. Should only span a single line.
        - command: The command this code lens represents.
        - data: A data entry field that is preserved on a code lens item between
            a [CodeLensRequest](#CodeLensRequest) and a [CodeLensResolveRequest]
            (#CodeLensResolveRequest)
        """
        self.range = range
        self.command = command
        self.data = data

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "CodeLens":
        range = Range.from_json(json_get_object(obj, "range"))
        if command_json := json_get_optional_object(obj, "command"):
            command = Command.from_json(command_json)
        else:
            command = None
        if data_json := obj.get("data"):
            data = parse_LSPAny(data_json)
        else:
            data = None
        return cls(range=range, command=command, data=data)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["range"] = self.range.to_json()
        if self.command is not None:
            out["command"] = self.command.to_json()
        if self.data is not None:
            out["data"] = write_LSPAny(self.data)
        return out


@dataclass
class CodeLensRegistrationOptions(TextDocumentRegistrationOptions, CodeLensOptions):
    """
    Registration options for a [CodeLensRequest](#CodeLensRequest).

    *Generated from the TypeScript documentation*
    """

    # A document selector to identify the scope of the registration. If set to null
    # the document selector provided on the client side will be used.
    documentSelector: Union["DocumentSelector", None]
    
    workDoneProgress: Optional[bool]
    
    # Code lens has a resolve provider as well.
    resolveProvider: Optional[bool]

    def __init__(self, *, documentSelector: Union["DocumentSelector", None], workDoneProgress: Optional[bool] = None, resolveProvider: Optional[bool] = None) -> None:
        """
        - documentSelector: A document selector to identify the scope of the registration. If set to null
            the document selector provided on the client side will be used.
        - resolveProvider: Code lens has a resolve provider as well.
        """
        self.documentSelector = documentSelector
        self.workDoneProgress = workDoneProgress
        self.resolveProvider = resolveProvider

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "CodeLensRegistrationOptions":
        documentSelector = parse_or_type(obj["documentSelector"], (lambda v: parse_DocumentSelector(json_assert_type_array(v)), lambda v: json_assert_type_null(v)))
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        if resolveProvider_json := json_get_optional_bool(obj, "resolveProvider"):
            resolveProvider = resolveProvider_json
        else:
            resolveProvider = None
        return cls(documentSelector=documentSelector, workDoneProgress=workDoneProgress, resolveProvider=resolveProvider)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["documentSelector"] = write_or_type(self.documentSelector, (lambda i: isinstance(i, List) and (len(i) == 0 or (((isinstance(i[0], Dict) and "language" in i[0].keys()) or (isinstance(i[0], Dict) and "scheme" in i[0].keys()) or (isinstance(i[0], Dict) and "pattern" in i[0].keys())) or (isinstance(i[0], NotebookCellTextDocumentFilter)))), lambda i: i is None), (lambda i: write_DocumentSelector(i), lambda i: i))
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        if self.resolveProvider is not None:
            out["resolveProvider"] = self.resolveProvider
        return out


@dataclass
class DocumentLinkParams():
    """
    The parameters of a [DocumentLinkRequest](#DocumentLinkRequest).

    *Generated from the TypeScript documentation*
    """

    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]
    
    # An optional token that a server can use to report partial results (e.g. streaming) to
    # the client.
    partialResultToken: Optional["ProgressToken"]
    
    # The document to provide document links for.
    textDocument: "TextDocumentIdentifier"

    def __init__(self, *, workDoneToken: Optional["ProgressToken"] = None, partialResultToken: Optional["ProgressToken"] = None, textDocument: "TextDocumentIdentifier") -> None:
        """
        - workDoneToken: An optional token that a server can use to report work done progress.
        - partialResultToken: An optional token that a server can use to report partial results (e.g. streaming) to
            the client.
        - textDocument: The document to provide document links for.
        """
        self.workDoneToken = workDoneToken
        self.partialResultToken = partialResultToken
        self.textDocument = textDocument

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DocumentLinkParams":
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        if partialResultToken_json := obj.get("partialResultToken"):
            partialResultToken = parse_ProgressToken(partialResultToken_json)
        else:
            partialResultToken = None
        textDocument = TextDocumentIdentifier.from_json(json_get_object(obj, "textDocument"))
        return cls(workDoneToken=workDoneToken, partialResultToken=partialResultToken, textDocument=textDocument)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        if self.partialResultToken is not None:
            out["partialResultToken"] = write_ProgressToken(self.partialResultToken)
        out["textDocument"] = self.textDocument.to_json()
        return out


@dataclass
class DocumentLink():
    """
    A document link is a range in a text document that links to an internal or external resource, like another
    text document or a web site.

    *Generated from the TypeScript documentation*
    """

    # The range this link applies to.
    range: "Range"
    
    # The uri this link points to. If missing a resolve request is sent later.
    target: Optional[str]
    
    # The tooltip text when you hover over this link.
    # 
    # If a tooltip is provided, is will be displayed in a string that includes instructions on how to
    # trigger the link, such as `{0} (ctrl + click)`. The specific instructions vary depending on OS,
    # user settings, and localization.
    # 
    # @since 3.15.0
    tooltip: Optional[str]
    
    # A data entry field that is preserved on a document link between a
    # DocumentLinkRequest and a DocumentLinkResolveRequest.
    data: Optional["LSPAny"]

    def __init__(self, *, range: "Range", target: Optional[str] = None, tooltip: Optional[str] = None, data: Optional["LSPAny"] = None) -> None:
        """
        - range: The range this link applies to.
        - target: The uri this link points to. If missing a resolve request is sent later.
        - tooltip: The tooltip text when you hover over this link.
            
            If a tooltip is provided, is will be displayed in a string that includes instructions on how to
            trigger the link, such as `{0} (ctrl + click)`. The specific instructions vary depending on OS,
            user settings, and localization.
            
            @since 3.15.0
        - data: A data entry field that is preserved on a document link between a
            DocumentLinkRequest and a DocumentLinkResolveRequest.
        """
        self.range = range
        self.target = target
        self.tooltip = tooltip
        self.data = data

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DocumentLink":
        range = Range.from_json(json_get_object(obj, "range"))
        if target_json := json_get_optional_string(obj, "target"):
            target = target_json
        else:
            target = None
        if tooltip_json := json_get_optional_string(obj, "tooltip"):
            tooltip = tooltip_json
        else:
            tooltip = None
        if data_json := obj.get("data"):
            data = parse_LSPAny(data_json)
        else:
            data = None
        return cls(range=range, target=target, tooltip=tooltip, data=data)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["range"] = self.range.to_json()
        if self.target is not None:
            out["target"] = self.target
        if self.tooltip is not None:
            out["tooltip"] = self.tooltip
        if self.data is not None:
            out["data"] = write_LSPAny(self.data)
        return out


@dataclass
class DocumentLinkRegistrationOptions(TextDocumentRegistrationOptions, DocumentLinkOptions):
    """
    Registration options for a [DocumentLinkRequest](#DocumentLinkRequest).

    *Generated from the TypeScript documentation*
    """

    # A document selector to identify the scope of the registration. If set to null
    # the document selector provided on the client side will be used.
    documentSelector: Union["DocumentSelector", None]
    
    workDoneProgress: Optional[bool]
    
    # Document links have a resolve provider as well.
    resolveProvider: Optional[bool]

    def __init__(self, *, documentSelector: Union["DocumentSelector", None], workDoneProgress: Optional[bool] = None, resolveProvider: Optional[bool] = None) -> None:
        """
        - documentSelector: A document selector to identify the scope of the registration. If set to null
            the document selector provided on the client side will be used.
        - resolveProvider: Document links have a resolve provider as well.
        """
        self.documentSelector = documentSelector
        self.workDoneProgress = workDoneProgress
        self.resolveProvider = resolveProvider

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DocumentLinkRegistrationOptions":
        documentSelector = parse_or_type(obj["documentSelector"], (lambda v: parse_DocumentSelector(json_assert_type_array(v)), lambda v: json_assert_type_null(v)))
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        if resolveProvider_json := json_get_optional_bool(obj, "resolveProvider"):
            resolveProvider = resolveProvider_json
        else:
            resolveProvider = None
        return cls(documentSelector=documentSelector, workDoneProgress=workDoneProgress, resolveProvider=resolveProvider)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["documentSelector"] = write_or_type(self.documentSelector, (lambda i: isinstance(i, List) and (len(i) == 0 or (((isinstance(i[0], Dict) and "language" in i[0].keys()) or (isinstance(i[0], Dict) and "scheme" in i[0].keys()) or (isinstance(i[0], Dict) and "pattern" in i[0].keys())) or (isinstance(i[0], NotebookCellTextDocumentFilter)))), lambda i: i is None), (lambda i: write_DocumentSelector(i), lambda i: i))
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        if self.resolveProvider is not None:
            out["resolveProvider"] = self.resolveProvider
        return out


@dataclass
class FormattingOptions():
    """
    Value-object describing what options formatting should use.

    *Generated from the TypeScript documentation*
    """

    # Size of a tab in spaces.
    tabSize: int
    
    # Prefer spaces over tabs.
    insertSpaces: bool
    
    # Trim trailing whitespace on a line.
    # 
    # @since 3.15.0
    trimTrailingWhitespace: Optional[bool]
    
    # Insert a newline character at the end of the file if one does not exist.
    # 
    # @since 3.15.0
    insertFinalNewline: Optional[bool]
    
    # Trim all newlines after the final newline at the end of the file.
    # 
    # @since 3.15.0
    trimFinalNewlines: Optional[bool]

    def __init__(self, *, tabSize: int, insertSpaces: bool, trimTrailingWhitespace: Optional[bool] = None, insertFinalNewline: Optional[bool] = None, trimFinalNewlines: Optional[bool] = None) -> None:
        """
        - tabSize: Size of a tab in spaces.
        - insertSpaces: Prefer spaces over tabs.
        - trimTrailingWhitespace: Trim trailing whitespace on a line.
            
            @since 3.15.0
        - insertFinalNewline: Insert a newline character at the end of the file if one does not exist.
            
            @since 3.15.0
        - trimFinalNewlines: Trim all newlines after the final newline at the end of the file.
            
            @since 3.15.0
        """
        self.tabSize = tabSize
        self.insertSpaces = insertSpaces
        self.trimTrailingWhitespace = trimTrailingWhitespace
        self.insertFinalNewline = insertFinalNewline
        self.trimFinalNewlines = trimFinalNewlines

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "FormattingOptions":
        tabSize = json_get_int(obj, "tabSize")
        insertSpaces = json_get_bool(obj, "insertSpaces")
        if trimTrailingWhitespace_json := json_get_optional_bool(obj, "trimTrailingWhitespace"):
            trimTrailingWhitespace = trimTrailingWhitespace_json
        else:
            trimTrailingWhitespace = None
        if insertFinalNewline_json := json_get_optional_bool(obj, "insertFinalNewline"):
            insertFinalNewline = insertFinalNewline_json
        else:
            insertFinalNewline = None
        if trimFinalNewlines_json := json_get_optional_bool(obj, "trimFinalNewlines"):
            trimFinalNewlines = trimFinalNewlines_json
        else:
            trimFinalNewlines = None
        return cls(tabSize=tabSize, insertSpaces=insertSpaces, trimTrailingWhitespace=trimTrailingWhitespace, insertFinalNewline=insertFinalNewline, trimFinalNewlines=trimFinalNewlines)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["tabSize"] = self.tabSize
        out["insertSpaces"] = self.insertSpaces
        if self.trimTrailingWhitespace is not None:
            out["trimTrailingWhitespace"] = self.trimTrailingWhitespace
        if self.insertFinalNewline is not None:
            out["insertFinalNewline"] = self.insertFinalNewline
        if self.trimFinalNewlines is not None:
            out["trimFinalNewlines"] = self.trimFinalNewlines
        return out


@dataclass
class DocumentFormattingParams():
    """
    The parameters of a [DocumentFormattingRequest](#DocumentFormattingRequest).

    *Generated from the TypeScript documentation*
    """

    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]
    
    # The document to format.
    textDocument: "TextDocumentIdentifier"
    
    # The format options.
    options: "FormattingOptions"

    def __init__(self, *, workDoneToken: Optional["ProgressToken"] = None, textDocument: "TextDocumentIdentifier", options: "FormattingOptions") -> None:
        """
        - workDoneToken: An optional token that a server can use to report work done progress.
        - textDocument: The document to format.
        - options: The format options.
        """
        self.workDoneToken = workDoneToken
        self.textDocument = textDocument
        self.options = options

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DocumentFormattingParams":
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        textDocument = TextDocumentIdentifier.from_json(json_get_object(obj, "textDocument"))
        options = FormattingOptions.from_json(json_get_object(obj, "options"))
        return cls(workDoneToken=workDoneToken, textDocument=textDocument, options=options)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        out["textDocument"] = self.textDocument.to_json()
        out["options"] = self.options.to_json()
        return out


@dataclass
class DocumentFormattingRegistrationOptions(TextDocumentRegistrationOptions, DocumentFormattingOptions):
    """
    Registration options for a [DocumentFormattingRequest](#DocumentFormattingRequest).

    *Generated from the TypeScript documentation*
    """

    # A document selector to identify the scope of the registration. If set to null
    # the document selector provided on the client side will be used.
    documentSelector: Union["DocumentSelector", None]
    
    workDoneProgress: Optional[bool]

    def __init__(self, *, documentSelector: Union["DocumentSelector", None], workDoneProgress: Optional[bool] = None) -> None:
        """
        - documentSelector: A document selector to identify the scope of the registration. If set to null
            the document selector provided on the client side will be used.
        """
        self.documentSelector = documentSelector
        self.workDoneProgress = workDoneProgress

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DocumentFormattingRegistrationOptions":
        documentSelector = parse_or_type(obj["documentSelector"], (lambda v: parse_DocumentSelector(json_assert_type_array(v)), lambda v: json_assert_type_null(v)))
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        return cls(documentSelector=documentSelector, workDoneProgress=workDoneProgress)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["documentSelector"] = write_or_type(self.documentSelector, (lambda i: isinstance(i, List) and (len(i) == 0 or (((isinstance(i[0], Dict) and "language" in i[0].keys()) or (isinstance(i[0], Dict) and "scheme" in i[0].keys()) or (isinstance(i[0], Dict) and "pattern" in i[0].keys())) or (isinstance(i[0], NotebookCellTextDocumentFilter)))), lambda i: i is None), (lambda i: write_DocumentSelector(i), lambda i: i))
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        return out


@dataclass
class DocumentRangeFormattingParams():
    """
    The parameters of a [DocumentRangeFormattingRequest](#DocumentRangeFormattingRequest).

    *Generated from the TypeScript documentation*
    """

    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]
    
    # The document to format.
    textDocument: "TextDocumentIdentifier"
    
    # The range to format
    range: "Range"
    
    # The format options
    options: "FormattingOptions"

    def __init__(self, *, workDoneToken: Optional["ProgressToken"] = None, textDocument: "TextDocumentIdentifier", range: "Range", options: "FormattingOptions") -> None:
        """
        - workDoneToken: An optional token that a server can use to report work done progress.
        - textDocument: The document to format.
        - range: The range to format
        - options: The format options
        """
        self.workDoneToken = workDoneToken
        self.textDocument = textDocument
        self.range = range
        self.options = options

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DocumentRangeFormattingParams":
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        textDocument = TextDocumentIdentifier.from_json(json_get_object(obj, "textDocument"))
        range = Range.from_json(json_get_object(obj, "range"))
        options = FormattingOptions.from_json(json_get_object(obj, "options"))
        return cls(workDoneToken=workDoneToken, textDocument=textDocument, range=range, options=options)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        out["textDocument"] = self.textDocument.to_json()
        out["range"] = self.range.to_json()
        out["options"] = self.options.to_json()
        return out


@dataclass
class DocumentRangeFormattingRegistrationOptions(TextDocumentRegistrationOptions, DocumentRangeFormattingOptions):
    """
    Registration options for a [DocumentRangeFormattingRequest](#DocumentRangeFormattingRequest).

    *Generated from the TypeScript documentation*
    """

    # A document selector to identify the scope of the registration. If set to null
    # the document selector provided on the client side will be used.
    documentSelector: Union["DocumentSelector", None]
    
    workDoneProgress: Optional[bool]

    def __init__(self, *, documentSelector: Union["DocumentSelector", None], workDoneProgress: Optional[bool] = None) -> None:
        """
        - documentSelector: A document selector to identify the scope of the registration. If set to null
            the document selector provided on the client side will be used.
        """
        self.documentSelector = documentSelector
        self.workDoneProgress = workDoneProgress

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DocumentRangeFormattingRegistrationOptions":
        documentSelector = parse_or_type(obj["documentSelector"], (lambda v: parse_DocumentSelector(json_assert_type_array(v)), lambda v: json_assert_type_null(v)))
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        return cls(documentSelector=documentSelector, workDoneProgress=workDoneProgress)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["documentSelector"] = write_or_type(self.documentSelector, (lambda i: isinstance(i, List) and (len(i) == 0 or (((isinstance(i[0], Dict) and "language" in i[0].keys()) or (isinstance(i[0], Dict) and "scheme" in i[0].keys()) or (isinstance(i[0], Dict) and "pattern" in i[0].keys())) or (isinstance(i[0], NotebookCellTextDocumentFilter)))), lambda i: i is None), (lambda i: write_DocumentSelector(i), lambda i: i))
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        return out


@dataclass
class DocumentOnTypeFormattingParams():
    """
    The parameters of a [DocumentOnTypeFormattingRequest](#DocumentOnTypeFormattingRequest).

    *Generated from the TypeScript documentation*
    """

    # The document to format.
    textDocument: "TextDocumentIdentifier"
    
    # The position around which the on type formatting should happen.
    # This is not necessarily the exact position where the character denoted
    # by the property `ch` got typed.
    position: "Position"
    
    # The character that has been typed that triggered the formatting
    # on type request. That is not necessarily the last character that
    # got inserted into the document since the client could auto insert
    # characters as well (e.g. like automatic brace completion).
    ch: str
    
    # The formatting options.
    options: "FormattingOptions"

    def __init__(self, *, textDocument: "TextDocumentIdentifier", position: "Position", ch: str, options: "FormattingOptions") -> None:
        """
        - textDocument: The document to format.
        - position: The position around which the on type formatting should happen.
            This is not necessarily the exact position where the character denoted
            by the property `ch` got typed.
        - ch: The character that has been typed that triggered the formatting
            on type request. That is not necessarily the last character that
            got inserted into the document since the client could auto insert
            characters as well (e.g. like automatic brace completion).
        - options: The formatting options.
        """
        self.textDocument = textDocument
        self.position = position
        self.ch = ch
        self.options = options

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DocumentOnTypeFormattingParams":
        textDocument = TextDocumentIdentifier.from_json(json_get_object(obj, "textDocument"))
        position = Position.from_json(json_get_object(obj, "position"))
        ch = json_get_string(obj, "ch")
        options = FormattingOptions.from_json(json_get_object(obj, "options"))
        return cls(textDocument=textDocument, position=position, ch=ch, options=options)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["textDocument"] = self.textDocument.to_json()
        out["position"] = self.position.to_json()
        out["ch"] = self.ch
        out["options"] = self.options.to_json()
        return out


@dataclass
class DocumentOnTypeFormattingRegistrationOptions(TextDocumentRegistrationOptions, DocumentOnTypeFormattingOptions):
    """
    Registration options for a [DocumentOnTypeFormattingRequest](#DocumentOnTypeFormattingRequest).

    *Generated from the TypeScript documentation*
    """

    # A document selector to identify the scope of the registration. If set to null
    # the document selector provided on the client side will be used.
    documentSelector: Union["DocumentSelector", None]
    
    # A character on which formatting should be triggered, like `{`.
    firstTriggerCharacter: str
    
    # More trigger characters.
    moreTriggerCharacter: Optional[List[str]]

    def __init__(self, *, documentSelector: Union["DocumentSelector", None], firstTriggerCharacter: str, moreTriggerCharacter: Optional[List[str]] = None) -> None:
        """
        - documentSelector: A document selector to identify the scope of the registration. If set to null
            the document selector provided on the client side will be used.
        - firstTriggerCharacter: A character on which formatting should be triggered, like `{`.
        - moreTriggerCharacter: More trigger characters.
        """
        self.documentSelector = documentSelector
        self.firstTriggerCharacter = firstTriggerCharacter
        self.moreTriggerCharacter = moreTriggerCharacter

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "DocumentOnTypeFormattingRegistrationOptions":
        documentSelector = parse_or_type(obj["documentSelector"], (lambda v: parse_DocumentSelector(json_assert_type_array(v)), lambda v: json_assert_type_null(v)))
        firstTriggerCharacter = json_get_string(obj, "firstTriggerCharacter")
        if moreTriggerCharacter_json := json_get_optional_array(obj, "moreTriggerCharacter"):
            moreTriggerCharacter = [json_assert_type_string(i) for i in moreTriggerCharacter_json]
        else:
            moreTriggerCharacter = None
        return cls(documentSelector=documentSelector, firstTriggerCharacter=firstTriggerCharacter, moreTriggerCharacter=moreTriggerCharacter)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["documentSelector"] = write_or_type(self.documentSelector, (lambda i: isinstance(i, List) and (len(i) == 0 or (((isinstance(i[0], Dict) and "language" in i[0].keys()) or (isinstance(i[0], Dict) and "scheme" in i[0].keys()) or (isinstance(i[0], Dict) and "pattern" in i[0].keys())) or (isinstance(i[0], NotebookCellTextDocumentFilter)))), lambda i: i is None), (lambda i: write_DocumentSelector(i), lambda i: i))
        out["firstTriggerCharacter"] = self.firstTriggerCharacter
        if self.moreTriggerCharacter is not None:
            out["moreTriggerCharacter"] = [i for i in self.moreTriggerCharacter]
        return out


@dataclass
class RenameParams():
    """
    The parameters of a [RenameRequest](#RenameRequest).

    *Generated from the TypeScript documentation*
    """

    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]
    
    # The document to rename.
    textDocument: "TextDocumentIdentifier"
    
    # The position at which this request was sent.
    position: "Position"
    
    # The new name of the symbol. If the given name is not valid the
    # request must return a [ResponseError](#ResponseError) with an
    # appropriate message set.
    newName: str

    def __init__(self, *, workDoneToken: Optional["ProgressToken"] = None, textDocument: "TextDocumentIdentifier", position: "Position", newName: str) -> None:
        """
        - workDoneToken: An optional token that a server can use to report work done progress.
        - textDocument: The document to rename.
        - position: The position at which this request was sent.
        - newName: The new name of the symbol. If the given name is not valid the
            request must return a [ResponseError](#ResponseError) with an
            appropriate message set.
        """
        self.workDoneToken = workDoneToken
        self.textDocument = textDocument
        self.position = position
        self.newName = newName

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "RenameParams":
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        textDocument = TextDocumentIdentifier.from_json(json_get_object(obj, "textDocument"))
        position = Position.from_json(json_get_object(obj, "position"))
        newName = json_get_string(obj, "newName")
        return cls(workDoneToken=workDoneToken, textDocument=textDocument, position=position, newName=newName)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        out["textDocument"] = self.textDocument.to_json()
        out["position"] = self.position.to_json()
        out["newName"] = self.newName
        return out


@dataclass
class RenameRegistrationOptions(TextDocumentRegistrationOptions, RenameOptions):
    """
    Registration options for a [RenameRequest](#RenameRequest).

    *Generated from the TypeScript documentation*
    """

    # A document selector to identify the scope of the registration. If set to null
    # the document selector provided on the client side will be used.
    documentSelector: Union["DocumentSelector", None]
    
    workDoneProgress: Optional[bool]
    
    # Renames should be checked and tested before being executed.
    # 
    # @since version 3.12.0
    prepareProvider: Optional[bool]

    def __init__(self, *, documentSelector: Union["DocumentSelector", None], workDoneProgress: Optional[bool] = None, prepareProvider: Optional[bool] = None) -> None:
        """
        - documentSelector: A document selector to identify the scope of the registration. If set to null
            the document selector provided on the client side will be used.
        - prepareProvider: Renames should be checked and tested before being executed.
            
            @since version 3.12.0
        """
        self.documentSelector = documentSelector
        self.workDoneProgress = workDoneProgress
        self.prepareProvider = prepareProvider

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "RenameRegistrationOptions":
        documentSelector = parse_or_type(obj["documentSelector"], (lambda v: parse_DocumentSelector(json_assert_type_array(v)), lambda v: json_assert_type_null(v)))
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        if prepareProvider_json := json_get_optional_bool(obj, "prepareProvider"):
            prepareProvider = prepareProvider_json
        else:
            prepareProvider = None
        return cls(documentSelector=documentSelector, workDoneProgress=workDoneProgress, prepareProvider=prepareProvider)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["documentSelector"] = write_or_type(self.documentSelector, (lambda i: isinstance(i, List) and (len(i) == 0 or (((isinstance(i[0], Dict) and "language" in i[0].keys()) or (isinstance(i[0], Dict) and "scheme" in i[0].keys()) or (isinstance(i[0], Dict) and "pattern" in i[0].keys())) or (isinstance(i[0], NotebookCellTextDocumentFilter)))), lambda i: i is None), (lambda i: write_DocumentSelector(i), lambda i: i))
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        if self.prepareProvider is not None:
            out["prepareProvider"] = self.prepareProvider
        return out


@dataclass
class PrepareRenameParams(TextDocumentPositionParams):
    """


    *Generated from the TypeScript documentation*
    """

    # The text document.
    textDocument: "TextDocumentIdentifier"
    
    # The position inside the text document.
    position: "Position"
    
    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]

    def __init__(self, *, textDocument: "TextDocumentIdentifier", position: "Position", workDoneToken: Optional["ProgressToken"] = None) -> None:
        """
        - textDocument: The text document.
        - position: The position inside the text document.
        - workDoneToken: An optional token that a server can use to report work done progress.
        """
        self.textDocument = textDocument
        self.position = position
        self.workDoneToken = workDoneToken

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "PrepareRenameParams":
        textDocument = TextDocumentIdentifier.from_json(json_get_object(obj, "textDocument"))
        position = Position.from_json(json_get_object(obj, "position"))
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        return cls(textDocument=textDocument, position=position, workDoneToken=workDoneToken)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["textDocument"] = self.textDocument.to_json()
        out["position"] = self.position.to_json()
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        return out


@dataclass
class ExecuteCommandParams():
    """
    The parameters of a [ExecuteCommandRequest](#ExecuteCommandRequest).

    *Generated from the TypeScript documentation*
    """

    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]
    
    # The identifier of the actual command handler.
    command: str
    
    # Arguments that the command should be invoked with.
    arguments: Optional[List["LSPAny"]]

    def __init__(self, *, workDoneToken: Optional["ProgressToken"] = None, command: str, arguments: Optional[List["LSPAny"]] = None) -> None:
        """
        - workDoneToken: An optional token that a server can use to report work done progress.
        - command: The identifier of the actual command handler.
        - arguments: Arguments that the command should be invoked with.
        """
        self.workDoneToken = workDoneToken
        self.command = command
        self.arguments = arguments

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "ExecuteCommandParams":
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        command = json_get_string(obj, "command")
        if arguments_json := json_get_optional_array(obj, "arguments"):
            arguments = [parse_LSPAny((i)) for i in arguments_json]
        else:
            arguments = None
        return cls(workDoneToken=workDoneToken, command=command, arguments=arguments)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        out["command"] = self.command
        if self.arguments is not None:
            out["arguments"] = [write_LSPAny(i) for i in self.arguments]
        return out


@dataclass
class ExecuteCommandRegistrationOptions(ExecuteCommandOptions):
    """
    Registration options for a [ExecuteCommandRequest](#ExecuteCommandRequest).

    *Generated from the TypeScript documentation*
    """

    workDoneProgress: Optional[bool]
    
    # The commands to be executed on the server
    commands: List[str]

    def __init__(self, *, workDoneProgress: Optional[bool] = None, commands: List[str]) -> None:
        """
        - commands: The commands to be executed on the server
        """
        self.workDoneProgress = workDoneProgress
        self.commands = commands

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "ExecuteCommandRegistrationOptions":
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        commands = [json_assert_type_string(i) for i in json_get_array(obj, "commands")]
        return cls(workDoneProgress=workDoneProgress, commands=commands)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        out["commands"] = [i for i in self.commands]
        return out


@dataclass
class ApplyWorkspaceEditParams():
    """
    The parameters passed via a apply workspace edit request.

    *Generated from the TypeScript documentation*
    """

    # An optional label of the workspace edit. This label is
    # presented in the user interface for example on an undo
    # stack to undo the workspace edit.
    label: Optional[str]
    
    # The edits to apply.
    edit: "WorkspaceEdit"

    def __init__(self, *, label: Optional[str] = None, edit: "WorkspaceEdit") -> None:
        """
        - label: An optional label of the workspace edit. This label is
            presented in the user interface for example on an undo
            stack to undo the workspace edit.
        - edit: The edits to apply.
        """
        self.label = label
        self.edit = edit

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "ApplyWorkspaceEditParams":
        if label_json := json_get_optional_string(obj, "label"):
            label = label_json
        else:
            label = None
        edit = WorkspaceEdit.from_json(json_get_object(obj, "edit"))
        return cls(label=label, edit=edit)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.label is not None:
            out["label"] = self.label
        out["edit"] = self.edit.to_json()
        return out


@dataclass
class ApplyWorkspaceEditResult():
    """
    The result returned from the apply workspace edit request.
    
    @since 3.17 renamed from ApplyWorkspaceEditResponse

    *Generated from the TypeScript documentation*
    """

    # Indicates whether the edit was applied or not.
    applied: bool
    
    # An optional textual description for why the edit was not applied.
    # This may be used by the server for diagnostic logging or to provide
    # a suitable error for a request that triggered the edit.
    failureReason: Optional[str]
    
    # Depending on the client's failure handling strategy `failedChange` might
    # contain the index of the change that failed. This property is only available
    # if the client signals a `failureHandlingStrategy` in its client capabilities.
    failedChange: Optional[int]

    def __init__(self, *, applied: bool, failureReason: Optional[str] = None, failedChange: Optional[int] = None) -> None:
        """
        - applied: Indicates whether the edit was applied or not.
        - failureReason: An optional textual description for why the edit was not applied.
            This may be used by the server for diagnostic logging or to provide
            a suitable error for a request that triggered the edit.
        - failedChange: Depending on the client's failure handling strategy `failedChange` might
            contain the index of the change that failed. This property is only available
            if the client signals a `failureHandlingStrategy` in its client capabilities.
        """
        self.applied = applied
        self.failureReason = failureReason
        self.failedChange = failedChange

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "ApplyWorkspaceEditResult":
        applied = json_get_bool(obj, "applied")
        if failureReason_json := json_get_optional_string(obj, "failureReason"):
            failureReason = failureReason_json
        else:
            failureReason = None
        if failedChange_json := json_get_optional_int(obj, "failedChange"):
            failedChange = failedChange_json
        else:
            failedChange = None
        return cls(applied=applied, failureReason=failureReason, failedChange=failedChange)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["applied"] = self.applied
        if self.failureReason is not None:
            out["failureReason"] = self.failureReason
        if self.failedChange is not None:
            out["failedChange"] = self.failedChange
        return out


@dataclass
class WorkDoneProgressBegin():
    """


    *Generated from the TypeScript documentation*
    """

    kind: str
    
    # Mandatory title of the progress operation. Used to briefly inform about
    # the kind of operation being performed.
    # 
    # Examples: "Indexing" or "Linking dependencies".
    title: str
    
    # Controls if a cancel button should show to allow the user to cancel the
    # long running operation. Clients that don't support cancellation are allowed
    # to ignore the setting.
    cancellable: Optional[bool]
    
    # Optional, more detailed associated progress message. Contains
    # complementary information to the `title`.
    # 
    # Examples: "3/25 files", "project/src/module2", "node_modules/some_dep".
    # If unset, the previous progress message (if any) is still valid.
    message: Optional[str]
    
    # Optional progress percentage to display (value 100 is considered 100%).
    # If not provided infinite progress is assumed and clients are allowed
    # to ignore the `percentage` value in subsequent in report notifications.
    # 
    # The value should be steadily rising. Clients are free to ignore values
    # that are not following this rule. The value range is [0, 100].
    percentage: Optional[int]

    def __init__(self, *, kind: str, title: str, cancellable: Optional[bool] = None, message: Optional[str] = None, percentage: Optional[int] = None) -> None:
        """
        - title: Mandatory title of the progress operation. Used to briefly inform about
            the kind of operation being performed.
            
            Examples: "Indexing" or "Linking dependencies".
        - cancellable: Controls if a cancel button should show to allow the user to cancel the
            long running operation. Clients that don't support cancellation are allowed
            to ignore the setting.
        - message: Optional, more detailed associated progress message. Contains
            complementary information to the `title`.
            
            Examples: "3/25 files", "project/src/module2", "node_modules/some_dep".
            If unset, the previous progress message (if any) is still valid.
        - percentage: Optional progress percentage to display (value 100 is considered 100%).
            If not provided infinite progress is assumed and clients are allowed
            to ignore the `percentage` value in subsequent in report notifications.
            
            The value should be steadily rising. Clients are free to ignore values
            that are not following this rule. The value range is [0, 100].
        """
        self.kind = kind
        self.title = title
        self.cancellable = cancellable
        self.message = message
        self.percentage = percentage

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "WorkDoneProgressBegin":
        kind = match_string(json_get_string(obj, "kind"), "begin")
        title = json_get_string(obj, "title")
        if cancellable_json := json_get_optional_bool(obj, "cancellable"):
            cancellable = cancellable_json
        else:
            cancellable = None
        if message_json := json_get_optional_string(obj, "message"):
            message = message_json
        else:
            message = None
        if percentage_json := json_get_optional_int(obj, "percentage"):
            percentage = percentage_json
        else:
            percentage = None
        return cls(kind=kind, title=title, cancellable=cancellable, message=message, percentage=percentage)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["kind"] = "begin"
        out["title"] = self.title
        if self.cancellable is not None:
            out["cancellable"] = self.cancellable
        if self.message is not None:
            out["message"] = self.message
        if self.percentage is not None:
            out["percentage"] = self.percentage
        return out


@dataclass
class WorkDoneProgressReport():
    """


    *Generated from the TypeScript documentation*
    """

    kind: str
    
    # Controls enablement state of a cancel button.
    # 
    # Clients that don't support cancellation or don't support controlling the button's
    # enablement state are allowed to ignore the property.
    cancellable: Optional[bool]
    
    # Optional, more detailed associated progress message. Contains
    # complementary information to the `title`.
    # 
    # Examples: "3/25 files", "project/src/module2", "node_modules/some_dep".
    # If unset, the previous progress message (if any) is still valid.
    message: Optional[str]
    
    # Optional progress percentage to display (value 100 is considered 100%).
    # If not provided infinite progress is assumed and clients are allowed
    # to ignore the `percentage` value in subsequent in report notifications.
    # 
    # The value should be steadily rising. Clients are free to ignore values
    # that are not following this rule. The value range is [0, 100]
    percentage: Optional[int]

    def __init__(self, *, kind: str, cancellable: Optional[bool] = None, message: Optional[str] = None, percentage: Optional[int] = None) -> None:
        """
        - cancellable: Controls enablement state of a cancel button.
            
            Clients that don't support cancellation or don't support controlling the button's
            enablement state are allowed to ignore the property.
        - message: Optional, more detailed associated progress message. Contains
            complementary information to the `title`.
            
            Examples: "3/25 files", "project/src/module2", "node_modules/some_dep".
            If unset, the previous progress message (if any) is still valid.
        - percentage: Optional progress percentage to display (value 100 is considered 100%).
            If not provided infinite progress is assumed and clients are allowed
            to ignore the `percentage` value in subsequent in report notifications.
            
            The value should be steadily rising. Clients are free to ignore values
            that are not following this rule. The value range is [0, 100]
        """
        self.kind = kind
        self.cancellable = cancellable
        self.message = message
        self.percentage = percentage

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "WorkDoneProgressReport":
        kind = match_string(json_get_string(obj, "kind"), "report")
        if cancellable_json := json_get_optional_bool(obj, "cancellable"):
            cancellable = cancellable_json
        else:
            cancellable = None
        if message_json := json_get_optional_string(obj, "message"):
            message = message_json
        else:
            message = None
        if percentage_json := json_get_optional_int(obj, "percentage"):
            percentage = percentage_json
        else:
            percentage = None
        return cls(kind=kind, cancellable=cancellable, message=message, percentage=percentage)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["kind"] = "report"
        if self.cancellable is not None:
            out["cancellable"] = self.cancellable
        if self.message is not None:
            out["message"] = self.message
        if self.percentage is not None:
            out["percentage"] = self.percentage
        return out


@dataclass
class WorkDoneProgressEnd():
    """


    *Generated from the TypeScript documentation*
    """

    kind: str
    
    # Optional, a final message indicating to for example indicate the outcome
    # of the operation.
    message: Optional[str]

    def __init__(self, *, kind: str, message: Optional[str] = None) -> None:
        """
        - message: Optional, a final message indicating to for example indicate the outcome
            of the operation.
        """
        self.kind = kind
        self.message = message

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "WorkDoneProgressEnd":
        kind = match_string(json_get_string(obj, "kind"), "end")
        if message_json := json_get_optional_string(obj, "message"):
            message = message_json
        else:
            message = None
        return cls(kind=kind, message=message)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["kind"] = "end"
        if self.message is not None:
            out["message"] = self.message
        return out


@dataclass
class SetTraceParams():
    """


    *Generated from the TypeScript documentation*
    """

    value: "TraceValues"

    def __init__(self, *, value: "TraceValues") -> None:
        """
    
        """
        self.value = value

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "SetTraceParams":
        value = TraceValues(json_get_string(obj, "value"))
        return cls(value=value)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["value"] = self.value.value
        return out


@dataclass
class LogTraceParams():
    """


    *Generated from the TypeScript documentation*
    """

    message: str
    
    verbose: Optional[str]

    def __init__(self, *, message: str, verbose: Optional[str] = None) -> None:
        """
    
        """
        self.message = message
        self.verbose = verbose

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "LogTraceParams":
        message = json_get_string(obj, "message")
        if verbose_json := json_get_optional_string(obj, "verbose"):
            verbose = verbose_json
        else:
            verbose = None
        return cls(message=message, verbose=verbose)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["message"] = self.message
        if self.verbose is not None:
            out["verbose"] = self.verbose
        return out


@dataclass
class CancelParams():
    """


    *Generated from the TypeScript documentation*
    """

    # The request id to cancel.
    id: Union[int, str]

    def __init__(self, *, id: Union[int, str]) -> None:
        """
        - id: The request id to cancel.
        """
        self.id = id

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "CancelParams":
        id = parse_or_type(obj["id"], (lambda v: json_assert_type_int(v), lambda v: json_assert_type_string(v)))
        return cls(id=id)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["id"] = write_or_type(self.id, (lambda i: isinstance(i, int), lambda i: isinstance(i, str)), (lambda i: i, lambda i: i))
        return out


@dataclass
class ProgressParams():
    """


    *Generated from the TypeScript documentation*
    """

    # The progress token provided by the client or server.
    token: "ProgressToken"
    
    # The progress data.
    value: "LSPAny"

    def __init__(self, *, token: "ProgressToken", value: "LSPAny") -> None:
        """
        - token: The progress token provided by the client or server.
        - value: The progress data.
        """
        self.token = token
        self.value = value

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "ProgressParams":
        token = parse_ProgressToken(obj["token"])
        value = parse_LSPAny(obj["value"])
        return cls(token=token, value=value)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["token"] = write_ProgressToken(self.token)
        out["value"] = write_LSPAny(self.value)
        return out


@dataclass
class WorkDoneProgressParams():
    """


    *Generated from the TypeScript documentation*
    """

    # An optional token that a server can use to report work done progress.
    workDoneToken: Optional["ProgressToken"]

    def __init__(self, *, workDoneToken: Optional["ProgressToken"] = None) -> None:
        """
        - workDoneToken: An optional token that a server can use to report work done progress.
        """
        self.workDoneToken = workDoneToken

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "WorkDoneProgressParams":
        if workDoneToken_json := obj.get("workDoneToken"):
            workDoneToken = parse_ProgressToken(workDoneToken_json)
        else:
            workDoneToken = None
        return cls(workDoneToken=workDoneToken)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneToken is not None:
            out["workDoneToken"] = write_ProgressToken(self.workDoneToken)
        return out


@dataclass
class LocationLink():
    """
    Represents the connection of two locations. Provides additional metadata over normal [locations](#Location),
    including an origin range.

    *Generated from the TypeScript documentation*
    """

    # Span of the origin of this link.
    # 
    # Used as the underlined span for mouse interaction. Defaults to the word range at
    # the definition position.
    originSelectionRange: Optional["Range"]
    
    # The target resource identifier of this link.
    targetUri: str
    
    # The full target range of this link. If the target for example is a symbol then target range is the
    # range enclosing this symbol not including leading/trailing whitespace but everything else
    # like comments. This information is typically used to highlight the range in the editor.
    targetRange: "Range"
    
    # The range that should be selected and revealed when this link is being followed, e.g the name of a function.
    # Must be contained by the `targetRange`. See also `DocumentSymbol#range`
    targetSelectionRange: "Range"

    def __init__(self, *, originSelectionRange: Optional["Range"] = None, targetUri: str, targetRange: "Range", targetSelectionRange: "Range") -> None:
        """
        - originSelectionRange: Span of the origin of this link.
            
            Used as the underlined span for mouse interaction. Defaults to the word range at
            the definition position.
        - targetUri: The target resource identifier of this link.
        - targetRange: The full target range of this link. If the target for example is a symbol then target range is the
            range enclosing this symbol not including leading/trailing whitespace but everything else
            like comments. This information is typically used to highlight the range in the editor.
        - targetSelectionRange: The range that should be selected and revealed when this link is being followed, e.g the name of a function.
            Must be contained by the `targetRange`. See also `DocumentSymbol#range`
        """
        self.originSelectionRange = originSelectionRange
        self.targetUri = targetUri
        self.targetRange = targetRange
        self.targetSelectionRange = targetSelectionRange

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "LocationLink":
        if originSelectionRange_json := json_get_optional_object(obj, "originSelectionRange"):
            originSelectionRange = Range.from_json(originSelectionRange_json)
        else:
            originSelectionRange = None
        targetUri = json_get_string(obj, "targetUri")
        targetRange = Range.from_json(json_get_object(obj, "targetRange"))
        targetSelectionRange = Range.from_json(json_get_object(obj, "targetSelectionRange"))
        return cls(originSelectionRange=originSelectionRange, targetUri=targetUri, targetRange=targetRange, targetSelectionRange=targetSelectionRange)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.originSelectionRange is not None:
            out["originSelectionRange"] = self.originSelectionRange.to_json()
        out["targetUri"] = self.targetUri
        out["targetRange"] = self.targetRange.to_json()
        out["targetSelectionRange"] = self.targetSelectionRange.to_json()
        return out


@dataclass
class StaticRegistrationOptions():
    """
    Static registration options to be returned in the initialize
    request.

    *Generated from the TypeScript documentation*
    """

    # The id used to register the request. The id can be used to deregister
    # the request again. See also Registration#id.
    id: Optional[str]

    def __init__(self, *, id: Optional[str] = None) -> None:
        """
        - id: The id used to register the request. The id can be used to deregister
            the request again. See also Registration#id.
        """
        self.id = id

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "StaticRegistrationOptions":
        if id_json := json_get_optional_string(obj, "id"):
            id = id_json
        else:
            id = None
        return cls(id=id)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.id is not None:
            out["id"] = self.id
        return out


@dataclass
class InlineValueText():
    """
    Provide inline value as text.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # The document range for which the inline value applies.
    range: "Range"
    
    # The text of the inline value.
    text: str

    def __init__(self, *, range: "Range", text: str) -> None:
        """
        - range: The document range for which the inline value applies.
        - text: The text of the inline value.
        """
        self.range = range
        self.text = text

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "InlineValueText":
        range = Range.from_json(json_get_object(obj, "range"))
        text = json_get_string(obj, "text")
        return cls(range=range, text=text)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["range"] = self.range.to_json()
        out["text"] = self.text
        return out


@dataclass
class InlineValueVariableLookup():
    """
    Provide inline value through a variable lookup.
    If only a range is specified, the variable name will be extracted from the underlying document.
    An optional variable name can be used to override the extracted name.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # The document range for which the inline value applies.
    # The range is used to extract the variable name from the underlying document.
    range: "Range"
    
    # If specified the name of the variable to look up.
    variableName: Optional[str]
    
    # How to perform the lookup.
    caseSensitiveLookup: bool

    def __init__(self, *, range: "Range", variableName: Optional[str] = None, caseSensitiveLookup: bool) -> None:
        """
        - range: The document range for which the inline value applies.
            The range is used to extract the variable name from the underlying document.
        - variableName: If specified the name of the variable to look up.
        - caseSensitiveLookup: How to perform the lookup.
        """
        self.range = range
        self.variableName = variableName
        self.caseSensitiveLookup = caseSensitiveLookup

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "InlineValueVariableLookup":
        range = Range.from_json(json_get_object(obj, "range"))
        if variableName_json := json_get_optional_string(obj, "variableName"):
            variableName = variableName_json
        else:
            variableName = None
        caseSensitiveLookup = json_get_bool(obj, "caseSensitiveLookup")
        return cls(range=range, variableName=variableName, caseSensitiveLookup=caseSensitiveLookup)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["range"] = self.range.to_json()
        if self.variableName is not None:
            out["variableName"] = self.variableName
        out["caseSensitiveLookup"] = self.caseSensitiveLookup
        return out


@dataclass
class InlineValueEvaluatableExpression():
    """
    Provide an inline value through an expression evaluation.
    If only a range is specified, the expression will be extracted from the underlying document.
    An optional expression can be used to override the extracted expression.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # The document range for which the inline value applies.
    # The range is used to extract the evaluatable expression from the underlying document.
    range: "Range"
    
    # If specified the expression overrides the extracted expression.
    expression: Optional[str]

    def __init__(self, *, range: "Range", expression: Optional[str] = None) -> None:
        """
        - range: The document range for which the inline value applies.
            The range is used to extract the evaluatable expression from the underlying document.
        - expression: If specified the expression overrides the extracted expression.
        """
        self.range = range
        self.expression = expression

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "InlineValueEvaluatableExpression":
        range = Range.from_json(json_get_object(obj, "range"))
        if expression_json := json_get_optional_string(obj, "expression"):
            expression = expression_json
        else:
            expression = None
        return cls(range=range, expression=expression)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["range"] = self.range.to_json()
        if self.expression is not None:
            out["expression"] = self.expression
        return out


@dataclass
class RelatedFullDocumentDiagnosticReport(FullDocumentDiagnosticReport):
    """
    A full diagnostic report with a set of related documents.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # A full document diagnostic report.
    kind: str
    
    # An optional result id. If provided it will
    # be sent on the next diagnostic request for the
    # same document.
    resultId: Optional[str]
    
    # The actual items.
    items: List["Diagnostic"]
    
    # Diagnostics of related documents. This information is useful
    # in programming languages where code in a file A can generate
    # diagnostics in a file B which A depends on. An example of
    # such a language is C/C++ where marco definitions in a file
    # a.cpp and result in errors in a header file b.hpp.
    # 
    # @since 3.17.0
    relatedDocuments: Optional[Dict[str, Union["FullDocumentDiagnosticReport", "UnchangedDocumentDiagnosticReport"]]]

    def __init__(self, *, kind: str, resultId: Optional[str] = None, items: List["Diagnostic"], relatedDocuments: Optional[Dict[str, Union["FullDocumentDiagnosticReport", "UnchangedDocumentDiagnosticReport"]]] = None) -> None:
        """
        - kind: A full document diagnostic report.
        - resultId: An optional result id. If provided it will
            be sent on the next diagnostic request for the
            same document.
        - items: The actual items.
        - relatedDocuments: Diagnostics of related documents. This information is useful
            in programming languages where code in a file A can generate
            diagnostics in a file B which A depends on. An example of
            such a language is C/C++ where marco definitions in a file
            a.cpp and result in errors in a header file b.hpp.
            
            @since 3.17.0
        """
        self.kind = kind
        self.resultId = resultId
        self.items = items
        self.relatedDocuments = relatedDocuments

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "RelatedFullDocumentDiagnosticReport":
        kind = match_string(json_get_string(obj, "kind"), "full")
        if resultId_json := json_get_optional_string(obj, "resultId"):
            resultId = resultId_json
        else:
            resultId = None
        items = [Diagnostic.from_json(json_assert_type_object(i)) for i in json_get_array(obj, "items")]
        if relatedDocuments_json := json_get_optional_object(obj, "relatedDocuments"):
            relatedDocuments = { json_assert_type_string(key): parse_or_type((value), (lambda v: FullDocumentDiagnosticReport.from_json(json_assert_type_object(v)), lambda v: UnchangedDocumentDiagnosticReport.from_json(json_assert_type_object(v)))) for key, value in relatedDocuments_json.items()}
        else:
            relatedDocuments = None
        return cls(kind=kind, resultId=resultId, items=items, relatedDocuments=relatedDocuments)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["kind"] = "full"
        if self.resultId is not None:
            out["resultId"] = self.resultId
        out["items"] = [i.to_json() for i in self.items]
        if self.relatedDocuments is not None:
            out["relatedDocuments"] = { key: write_or_type(val, (lambda i: isinstance(i, FullDocumentDiagnosticReport), lambda i: isinstance(i, UnchangedDocumentDiagnosticReport)), (lambda i: i.to_json(), lambda i: i.to_json())) for key, val in self.relatedDocuments.items() }
        return out


@dataclass
class RelatedUnchangedDocumentDiagnosticReport(UnchangedDocumentDiagnosticReport):
    """
    An unchanged diagnostic report with a set of related documents.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # A document diagnostic report indicating
    # no changes to the last result. A server can
    # only return `unchanged` if result ids are
    # provided.
    kind: str
    
    # A result id which will be sent on the next
    # diagnostic request for the same document.
    resultId: str
    
    # Diagnostics of related documents. This information is useful
    # in programming languages where code in a file A can generate
    # diagnostics in a file B which A depends on. An example of
    # such a language is C/C++ where marco definitions in a file
    # a.cpp and result in errors in a header file b.hpp.
    # 
    # @since 3.17.0
    relatedDocuments: Optional[Dict[str, Union["FullDocumentDiagnosticReport", "UnchangedDocumentDiagnosticReport"]]]

    def __init__(self, *, kind: str, resultId: str, relatedDocuments: Optional[Dict[str, Union["FullDocumentDiagnosticReport", "UnchangedDocumentDiagnosticReport"]]] = None) -> None:
        """
        - kind: A document diagnostic report indicating
            no changes to the last result. A server can
            only return `unchanged` if result ids are
            provided.
        - resultId: A result id which will be sent on the next
            diagnostic request for the same document.
        - relatedDocuments: Diagnostics of related documents. This information is useful
            in programming languages where code in a file A can generate
            diagnostics in a file B which A depends on. An example of
            such a language is C/C++ where marco definitions in a file
            a.cpp and result in errors in a header file b.hpp.
            
            @since 3.17.0
        """
        self.kind = kind
        self.resultId = resultId
        self.relatedDocuments = relatedDocuments

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "RelatedUnchangedDocumentDiagnosticReport":
        kind = match_string(json_get_string(obj, "kind"), "unchanged")
        resultId = json_get_string(obj, "resultId")
        if relatedDocuments_json := json_get_optional_object(obj, "relatedDocuments"):
            relatedDocuments = { json_assert_type_string(key): parse_or_type((value), (lambda v: FullDocumentDiagnosticReport.from_json(json_assert_type_object(v)), lambda v: UnchangedDocumentDiagnosticReport.from_json(json_assert_type_object(v)))) for key, value in relatedDocuments_json.items()}
        else:
            relatedDocuments = None
        return cls(kind=kind, resultId=resultId, relatedDocuments=relatedDocuments)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["kind"] = "unchanged"
        out["resultId"] = self.resultId
        if self.relatedDocuments is not None:
            out["relatedDocuments"] = { key: write_or_type(val, (lambda i: isinstance(i, FullDocumentDiagnosticReport), lambda i: isinstance(i, UnchangedDocumentDiagnosticReport)), (lambda i: i.to_json(), lambda i: i.to_json())) for key, val in self.relatedDocuments.items() }
        return out


# The definition of a symbol represented as one or many [locations](#Location).
# For most programming languages there is only one location at which a symbol is
# defined.
# 
# Servers should prefer returning `DefinitionLink` over `Definition` if supported
# by the client.
Definition = Union["Location", List["Location"]]

def parse_Definition(arg: JSON_VALUE) -> Definition:
    return parse_or_type((arg), (lambda v: Location.from_json(json_assert_type_object(v)), lambda v: [Location.from_json(json_assert_type_object(i)) for i in json_assert_type_array(v)]))

def write_Definition(arg: Definition) -> JSON_VALUE:
    return write_or_type(arg, (lambda i: isinstance(i, Location), lambda i: isinstance(i, List) and (len(i) == 0 or (isinstance(i[0], Location)))), (lambda i: i.to_json(), lambda i: [i.to_json() for i in i]))


# Information about where a symbol is defined.
# 
# Provides additional metadata over normal [location](#Location) definitions, including the range of
# the defining symbol
DefinitionLink = LocationLink

def parse_DefinitionLink(arg: JSON_VALUE) -> DefinitionLink:
    return LocationLink.from_json(json_assert_type_object(arg))

def write_DefinitionLink(arg: DefinitionLink) -> JSON_VALUE:
    return arg.to_json()


# The declaration of a symbol representation as one or many [locations](#Location).
Declaration = Union["Location", List["Location"]]

def parse_Declaration(arg: JSON_VALUE) -> Declaration:
    return parse_or_type((arg), (lambda v: Location.from_json(json_assert_type_object(v)), lambda v: [Location.from_json(json_assert_type_object(i)) for i in json_assert_type_array(v)]))

def write_Declaration(arg: Declaration) -> JSON_VALUE:
    return write_or_type(arg, (lambda i: isinstance(i, Location), lambda i: isinstance(i, List) and (len(i) == 0 or (isinstance(i[0], Location)))), (lambda i: i.to_json(), lambda i: [i.to_json() for i in i]))


# Information about where a symbol is declared.
# 
# Provides additional metadata over normal [location](#Location) declarations, including the range of
# the declaring symbol.
# 
# Servers should prefer returning `DeclarationLink` over `Declaration` if supported
# by the client.
DeclarationLink = LocationLink

def parse_DeclarationLink(arg: JSON_VALUE) -> DeclarationLink:
    return LocationLink.from_json(json_assert_type_object(arg))

def write_DeclarationLink(arg: DeclarationLink) -> JSON_VALUE:
    return arg.to_json()


# Inline value information can be provided by different means:
# - directly as a text value (class InlineValueText).
# - as a name to use for a variable lookup (class InlineValueVariableLookup)
# - as an evaluatable expression (class InlineValueEvaluatableExpression)
# The InlineValue types combines all inline value types into one type.
# 
# @since 3.17.0
InlineValue = Union["InlineValueText", "InlineValueVariableLookup", "InlineValueEvaluatableExpression"]

def parse_InlineValue(arg: JSON_VALUE) -> InlineValue:
    return parse_or_type((arg), (lambda v: InlineValueText.from_json(json_assert_type_object(v)), lambda v: InlineValueVariableLookup.from_json(json_assert_type_object(v)), lambda v: InlineValueEvaluatableExpression.from_json(json_assert_type_object(v))))

def write_InlineValue(arg: InlineValue) -> JSON_VALUE:
    return write_or_type(arg, (lambda i: isinstance(i, InlineValueText), lambda i: isinstance(i, InlineValueVariableLookup), lambda i: isinstance(i, InlineValueEvaluatableExpression)), (lambda i: i.to_json(), lambda i: i.to_json(), lambda i: i.to_json()))


# The result of a document diagnostic pull request. A report can
# either be a full report containing all diagnostics for the
# requested document or an unchanged report indicating that nothing
# has changed in terms of diagnostics in comparison to the last
# pull request.
# 
# @since 3.17.0
DocumentDiagnosticReport = Union["RelatedFullDocumentDiagnosticReport", "RelatedUnchangedDocumentDiagnosticReport"]

def parse_DocumentDiagnosticReport(arg: JSON_VALUE) -> DocumentDiagnosticReport:
    return parse_or_type((arg), (lambda v: RelatedFullDocumentDiagnosticReport.from_json(json_assert_type_object(v)), lambda v: RelatedUnchangedDocumentDiagnosticReport.from_json(json_assert_type_object(v))))

def write_DocumentDiagnosticReport(arg: DocumentDiagnosticReport) -> JSON_VALUE:
    return write_or_type(arg, (lambda i: isinstance(i, RelatedFullDocumentDiagnosticReport), lambda i: isinstance(i, RelatedUnchangedDocumentDiagnosticReport)), (lambda i: i.to_json(), lambda i: i.to_json()))


AnonymousStructure37Keys = Literal["range","placeholder"]

def parse_AnonymousStructure37(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure37Keys, Any]:
    out: Dict[AnonymousStructure37Keys, Any] = {}
    out["range"] = Range.from_json(json_get_object(obj, "range"))
    out["placeholder"] = json_get_string(obj, "placeholder")
    return out

def write_AnonymousStructure37(obj: Dict[AnonymousStructure37Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    out["range"] = obj["range"].to_json()
    out["placeholder"] = obj["placeholder"]
    return out


AnonymousStructure38Keys = Literal["defaultBehavior"]

def parse_AnonymousStructure38(obj: Mapping[str, JSON_VALUE]) -> Dict[AnonymousStructure38Keys, Any]:
    out: Dict[AnonymousStructure38Keys, Any] = {}
    out["defaultBehavior"] = json_get_bool(obj, "defaultBehavior")
    return out

def write_AnonymousStructure38(obj: Dict[AnonymousStructure38Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {}
    out["defaultBehavior"] = obj["defaultBehavior"]
    return out


PrepareRenameResult = Union["Range", Dict[AnonymousStructure37Keys, Any], Dict[AnonymousStructure38Keys, Any]]

def parse_PrepareRenameResult(arg: JSON_VALUE) -> PrepareRenameResult:
    return parse_or_type((arg), (lambda v: Range.from_json(json_assert_type_object(v)), lambda v: parse_AnonymousStructure37(json_assert_type_object(v)), lambda v: parse_AnonymousStructure38(json_assert_type_object(v))))

def write_PrepareRenameResult(arg: PrepareRenameResult) -> JSON_VALUE:
    return write_or_type(arg, (lambda i: isinstance(i, Range), lambda i: isinstance(i, Dict) and "range" in i.keys() and "placeholder" in i.keys(), lambda i: isinstance(i, Dict) and "defaultBehavior" in i.keys()), (lambda i: i.to_json(), lambda i: write_AnonymousStructure37(i), lambda i: write_AnonymousStructure38(i)))


@dataclass
class ConfigurationParamsAndPartialResultParams():
    """


    *Generated from the TypeScript documentation*
    """

    items: List["ConfigurationItem"]
    
    # An optional token that a server can use to report partial results (e.g. streaming) to
    # the client.
    partialResultToken: Optional["ProgressToken"]

    def __init__(self, *, items: List["ConfigurationItem"], partialResultToken: Optional["ProgressToken"] = None) -> None:
        """
        - partialResultToken: An optional token that a server can use to report partial results (e.g. streaming) to
            the client.
        """
        self.items = items
        self.partialResultToken = partialResultToken

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "ConfigurationParamsAndPartialResultParams":
        items = [ConfigurationItem.from_json(json_assert_type_object(i)) for i in json_get_array(obj, "items")]
        if partialResultToken_json := obj.get("partialResultToken"):
            partialResultToken = parse_ProgressToken(partialResultToken_json)
        else:
            partialResultToken = None
        return cls(items=items, partialResultToken=partialResultToken)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        out["items"] = [i.to_json() for i in self.items]
        if self.partialResultToken is not None:
            out["partialResultToken"] = write_ProgressToken(self.partialResultToken)
        return out


@dataclass
class TextDocumentRegistrationOptionsAndWorkDoneProgressOptions():
    """


    *Generated from the TypeScript documentation*
    """

    workDoneProgress: Optional[bool]
    
    # A document selector to identify the scope of the registration. If set to null
    # the document selector provided on the client side will be used.
    documentSelector: Union["DocumentSelector", None]

    def __init__(self, *, workDoneProgress: Optional[bool] = None, documentSelector: Union["DocumentSelector", None]) -> None:
        """
        - documentSelector: A document selector to identify the scope of the registration. If set to null
            the document selector provided on the client side will be used.
        """
        self.workDoneProgress = workDoneProgress
        self.documentSelector = documentSelector

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "TextDocumentRegistrationOptionsAndWorkDoneProgressOptions":
        if workDoneProgress_json := json_get_optional_bool(obj, "workDoneProgress"):
            workDoneProgress = workDoneProgress_json
        else:
            workDoneProgress = None
        documentSelector = parse_or_type(obj["documentSelector"], (lambda v: parse_DocumentSelector(json_assert_type_array(v)), lambda v: json_assert_type_null(v)))
        return cls(workDoneProgress=workDoneProgress, documentSelector=documentSelector)

    def to_json(self) -> Dict[str, JSON_VALUE]:
        out: Dict[str, JSON_VALUE] = {}
        if self.workDoneProgress is not None:
            out["workDoneProgress"] = self.workDoneProgress
        out["documentSelector"] = write_or_type(self.documentSelector, (lambda i: isinstance(i, List) and (len(i) == 0 or (((isinstance(i[0], Dict) and "language" in i[0].keys()) or (isinstance(i[0], Dict) and "scheme" in i[0].keys()) or (isinstance(i[0], Dict) and "pattern" in i[0].keys())) or (isinstance(i[0], NotebookCellTextDocumentFilter)))), lambda i: i is None), (lambda i: write_DocumentSelector(i), lambda i: i))
        return out
