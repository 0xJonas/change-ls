from typing import ClassVar
from .lsp_enum import AllowCustomValues, TypedLSPEnum


class SemanticTokenTypes(TypedLSPEnum[str], AllowCustomValues):
    """
    A set of predefined token types. This set is not fixed
    an clients can specify additional token types via the
    corresponding client capabilities.
    
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    namespace: ClassVar["SemanticTokenTypes"] = "namespace" # type: ignore
    
    # Represents a generic type. Acts as a fallback for types which can't be mapped to
    # a specific type like class or enum.
    type: ClassVar["SemanticTokenTypes"] = "type" # type: ignore
    
    class_: ClassVar["SemanticTokenTypes"] = "class" # type: ignore
    
    enum: ClassVar["SemanticTokenTypes"] = "enum" # type: ignore
    
    interface: ClassVar["SemanticTokenTypes"] = "interface" # type: ignore
    
    struct: ClassVar["SemanticTokenTypes"] = "struct" # type: ignore
    
    typeParameter: ClassVar["SemanticTokenTypes"] = "typeParameter" # type: ignore
    
    parameter: ClassVar["SemanticTokenTypes"] = "parameter" # type: ignore
    
    variable: ClassVar["SemanticTokenTypes"] = "variable" # type: ignore
    
    property: ClassVar["SemanticTokenTypes"] = "property" # type: ignore
    
    enumMember: ClassVar["SemanticTokenTypes"] = "enumMember" # type: ignore
    
    event: ClassVar["SemanticTokenTypes"] = "event" # type: ignore
    
    function: ClassVar["SemanticTokenTypes"] = "function" # type: ignore
    
    method: ClassVar["SemanticTokenTypes"] = "method" # type: ignore
    
    macro: ClassVar["SemanticTokenTypes"] = "macro" # type: ignore
    
    keyword: ClassVar["SemanticTokenTypes"] = "keyword" # type: ignore
    
    modifier: ClassVar["SemanticTokenTypes"] = "modifier" # type: ignore
    
    comment: ClassVar["SemanticTokenTypes"] = "comment" # type: ignore
    
    string: ClassVar["SemanticTokenTypes"] = "string" # type: ignore
    
    number: ClassVar["SemanticTokenTypes"] = "number" # type: ignore
    
    regexp: ClassVar["SemanticTokenTypes"] = "regexp" # type: ignore
    
    operator: ClassVar["SemanticTokenTypes"] = "operator" # type: ignore
    
    # @since 3.17.0
    decorator: ClassVar["SemanticTokenTypes"] = "decorator" # type: ignore


class SemanticTokenModifiers(TypedLSPEnum[str], AllowCustomValues):
    """
    A set of predefined token modifiers. This set is not fixed
    an clients can specify additional token types via the
    corresponding client capabilities.
    
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    declaration: ClassVar["SemanticTokenModifiers"] = "declaration" # type: ignore
    
    definition: ClassVar["SemanticTokenModifiers"] = "definition" # type: ignore
    
    readonly: ClassVar["SemanticTokenModifiers"] = "readonly" # type: ignore
    
    static: ClassVar["SemanticTokenModifiers"] = "static" # type: ignore
    
    deprecated: ClassVar["SemanticTokenModifiers"] = "deprecated" # type: ignore
    
    abstract: ClassVar["SemanticTokenModifiers"] = "abstract" # type: ignore
    
    async_: ClassVar["SemanticTokenModifiers"] = "async" # type: ignore
    
    modification: ClassVar["SemanticTokenModifiers"] = "modification" # type: ignore
    
    documentation: ClassVar["SemanticTokenModifiers"] = "documentation" # type: ignore
    
    defaultLibrary: ClassVar["SemanticTokenModifiers"] = "defaultLibrary" # type: ignore


class DocumentDiagnosticReportKind(TypedLSPEnum[str]):
    """
    The document diagnostic report kinds.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # A diagnostic report with a full
    # set of problems.
    Full: ClassVar["DocumentDiagnosticReportKind"] = "full" # type: ignore
    
    # A report indicating that the last
    # returned report is still accurate.
    Unchanged: ClassVar["DocumentDiagnosticReportKind"] = "unchanged" # type: ignore


class ErrorCodes(TypedLSPEnum[int], AllowCustomValues):
    """
    Predefined error codes.

    *Generated from the TypeScript documentation*
    """

    ParseError: ClassVar["ErrorCodes"] = -32700 # type: ignore
    
    InvalidRequest: ClassVar["ErrorCodes"] = -32600 # type: ignore
    
    MethodNotFound: ClassVar["ErrorCodes"] = -32601 # type: ignore
    
    InvalidParams: ClassVar["ErrorCodes"] = -32602 # type: ignore
    
    InternalError: ClassVar["ErrorCodes"] = -32603 # type: ignore
    
    # Error code indicating that a server received a notification or
    # request before the server has received the `initialize` request.
    ServerNotInitialized: ClassVar["ErrorCodes"] = -32002 # type: ignore
    
    UnknownErrorCode: ClassVar["ErrorCodes"] = -32001 # type: ignore


class LSPErrorCodes(TypedLSPEnum[int], AllowCustomValues):
    """


    *Generated from the TypeScript documentation*
    """

    # A request failed but it was syntactically correct, e.g the
    # method name was known and the parameters were valid. The error
    # message should contain human readable information about why
    # the request failed.
    # 
    # @since 3.17.0
    RequestFailed: ClassVar["LSPErrorCodes"] = -32803 # type: ignore
    
    # The server cancelled the request. This error code should
    # only be used for requests that explicitly support being
    # server cancellable.
    # 
    # @since 3.17.0
    ServerCancelled: ClassVar["LSPErrorCodes"] = -32802 # type: ignore
    
    # The server detected that the content of a document got
    # modified outside normal conditions. A server should
    # NOT send this error code if it detects a content change
    # in it unprocessed messages. The result even computed
    # on an older state might still be useful for the client.
    # 
    # If a client decides that a result is not of any use anymore
    # the client should cancel the request.
    ContentModified: ClassVar["LSPErrorCodes"] = -32801 # type: ignore
    
    # The client has canceled a request and a server as detected
    # the cancel.
    RequestCancelled: ClassVar["LSPErrorCodes"] = -32800 # type: ignore


class FoldingRangeKind(TypedLSPEnum[str], AllowCustomValues):
    """
    A set of predefined range kinds.

    *Generated from the TypeScript documentation*
    """

    # Folding range for a comment
    Comment: ClassVar["FoldingRangeKind"] = "comment" # type: ignore
    
    # Folding range for an import or include
    Imports: ClassVar["FoldingRangeKind"] = "imports" # type: ignore
    
    # Folding range for a region (e.g. `#region`)
    Region: ClassVar["FoldingRangeKind"] = "region" # type: ignore


class SymbolKind(TypedLSPEnum[int]):
    """
    A symbol kind.

    *Generated from the TypeScript documentation*
    """

    File: ClassVar["SymbolKind"] = 1 # type: ignore
    
    Module: ClassVar["SymbolKind"] = 2 # type: ignore
    
    Namespace: ClassVar["SymbolKind"] = 3 # type: ignore
    
    Package: ClassVar["SymbolKind"] = 4 # type: ignore
    
    Class: ClassVar["SymbolKind"] = 5 # type: ignore
    
    Method: ClassVar["SymbolKind"] = 6 # type: ignore
    
    Property: ClassVar["SymbolKind"] = 7 # type: ignore
    
    Field: ClassVar["SymbolKind"] = 8 # type: ignore
    
    Constructor: ClassVar["SymbolKind"] = 9 # type: ignore
    
    Enum: ClassVar["SymbolKind"] = 10 # type: ignore
    
    Interface: ClassVar["SymbolKind"] = 11 # type: ignore
    
    Function: ClassVar["SymbolKind"] = 12 # type: ignore
    
    Variable: ClassVar["SymbolKind"] = 13 # type: ignore
    
    Constant: ClassVar["SymbolKind"] = 14 # type: ignore
    
    String: ClassVar["SymbolKind"] = 15 # type: ignore
    
    Number: ClassVar["SymbolKind"] = 16 # type: ignore
    
    Boolean: ClassVar["SymbolKind"] = 17 # type: ignore
    
    Array: ClassVar["SymbolKind"] = 18 # type: ignore
    
    Object: ClassVar["SymbolKind"] = 19 # type: ignore
    
    Key: ClassVar["SymbolKind"] = 20 # type: ignore
    
    Null: ClassVar["SymbolKind"] = 21 # type: ignore
    
    EnumMember: ClassVar["SymbolKind"] = 22 # type: ignore
    
    Struct: ClassVar["SymbolKind"] = 23 # type: ignore
    
    Event: ClassVar["SymbolKind"] = 24 # type: ignore
    
    Operator: ClassVar["SymbolKind"] = 25 # type: ignore
    
    TypeParameter: ClassVar["SymbolKind"] = 26 # type: ignore


class SymbolTag(TypedLSPEnum[int]):
    """
    Symbol tags are extra annotations that tweak the rendering of a symbol.
    
    @since 3.16

    *Generated from the TypeScript documentation*
    """

    # Render a symbol as obsolete, usually using a strike-out.
    Deprecated: ClassVar["SymbolTag"] = 1 # type: ignore


class UniquenessLevel(TypedLSPEnum[str]):
    """
    Moniker uniqueness level to define scope of the moniker.
    
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # The moniker is only unique inside a document
    document: ClassVar["UniquenessLevel"] = "document" # type: ignore
    
    # The moniker is unique inside a project for which a dump got created
    project: ClassVar["UniquenessLevel"] = "project" # type: ignore
    
    # The moniker is unique inside the group to which a project belongs
    group: ClassVar["UniquenessLevel"] = "group" # type: ignore
    
    # The moniker is unique inside the moniker scheme.
    scheme: ClassVar["UniquenessLevel"] = "scheme" # type: ignore
    
    # The moniker is globally unique
    global_: ClassVar["UniquenessLevel"] = "global" # type: ignore


class MonikerKind(TypedLSPEnum[str]):
    """
    The moniker kind.
    
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # The moniker represent a symbol that is imported into a project
    import_: ClassVar["MonikerKind"] = "import" # type: ignore
    
    # The moniker represents a symbol that is exported from a project
    export: ClassVar["MonikerKind"] = "export" # type: ignore
    
    # The moniker represents a symbol that is local to a project (e.g. a local
    # variable of a function, a class not visible outside the project, ...)
    local: ClassVar["MonikerKind"] = "local" # type: ignore


class InlayHintKind(TypedLSPEnum[int]):
    """
    Inlay hint kinds.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # An inlay hint that for a type annotation.
    Type: ClassVar["InlayHintKind"] = 1 # type: ignore
    
    # An inlay hint that is for a parameter.
    Parameter: ClassVar["InlayHintKind"] = 2 # type: ignore


class MessageType(TypedLSPEnum[int]):
    """
    The message type

    *Generated from the TypeScript documentation*
    """

    # An error message.
    Error: ClassVar["MessageType"] = 1 # type: ignore
    
    # A warning message.
    Warning: ClassVar["MessageType"] = 2 # type: ignore
    
    # An information message.
    Info: ClassVar["MessageType"] = 3 # type: ignore
    
    # A log message.
    Log: ClassVar["MessageType"] = 4 # type: ignore


class TextDocumentSyncKind(TypedLSPEnum[int]):
    """
    Defines how the host (editor) should sync
    document changes to the language server.

    *Generated from the TypeScript documentation*
    """

    # Documents should not be synced at all.
    None_: ClassVar["TextDocumentSyncKind"] = 0 # type: ignore
    
    # Documents are synced by always sending the full content
    # of the document.
    Full: ClassVar["TextDocumentSyncKind"] = 1 # type: ignore
    
    # Documents are synced by sending the full content on open.
    # After that only incremental updates to the document are
    # send.
    Incremental: ClassVar["TextDocumentSyncKind"] = 2 # type: ignore


class TextDocumentSaveReason(TypedLSPEnum[int]):
    """
    Represents reasons why a text document is saved.

    *Generated from the TypeScript documentation*
    """

    # Manually triggered, e.g. by the user pressing save, by starting debugging,
    # or by an API call.
    Manual: ClassVar["TextDocumentSaveReason"] = 1 # type: ignore
    
    # Automatic after a delay.
    AfterDelay: ClassVar["TextDocumentSaveReason"] = 2 # type: ignore
    
    # When the editor lost focus.
    FocusOut: ClassVar["TextDocumentSaveReason"] = 3 # type: ignore


class CompletionItemKind(TypedLSPEnum[int]):
    """
    The kind of a completion entry.

    *Generated from the TypeScript documentation*
    """

    Text: ClassVar["CompletionItemKind"] = 1 # type: ignore
    
    Method: ClassVar["CompletionItemKind"] = 2 # type: ignore
    
    Function: ClassVar["CompletionItemKind"] = 3 # type: ignore
    
    Constructor: ClassVar["CompletionItemKind"] = 4 # type: ignore
    
    Field: ClassVar["CompletionItemKind"] = 5 # type: ignore
    
    Variable: ClassVar["CompletionItemKind"] = 6 # type: ignore
    
    Class: ClassVar["CompletionItemKind"] = 7 # type: ignore
    
    Interface: ClassVar["CompletionItemKind"] = 8 # type: ignore
    
    Module: ClassVar["CompletionItemKind"] = 9 # type: ignore
    
    Property: ClassVar["CompletionItemKind"] = 10 # type: ignore
    
    Unit: ClassVar["CompletionItemKind"] = 11 # type: ignore
    
    Value: ClassVar["CompletionItemKind"] = 12 # type: ignore
    
    Enum: ClassVar["CompletionItemKind"] = 13 # type: ignore
    
    Keyword: ClassVar["CompletionItemKind"] = 14 # type: ignore
    
    Snippet: ClassVar["CompletionItemKind"] = 15 # type: ignore
    
    Color: ClassVar["CompletionItemKind"] = 16 # type: ignore
    
    File: ClassVar["CompletionItemKind"] = 17 # type: ignore
    
    Reference: ClassVar["CompletionItemKind"] = 18 # type: ignore
    
    Folder: ClassVar["CompletionItemKind"] = 19 # type: ignore
    
    EnumMember: ClassVar["CompletionItemKind"] = 20 # type: ignore
    
    Constant: ClassVar["CompletionItemKind"] = 21 # type: ignore
    
    Struct: ClassVar["CompletionItemKind"] = 22 # type: ignore
    
    Event: ClassVar["CompletionItemKind"] = 23 # type: ignore
    
    Operator: ClassVar["CompletionItemKind"] = 24 # type: ignore
    
    TypeParameter: ClassVar["CompletionItemKind"] = 25 # type: ignore


class CompletionItemTag(TypedLSPEnum[int]):
    """
    Completion item tags are extra annotations that tweak the rendering of a completion
    item.
    
    @since 3.15.0

    *Generated from the TypeScript documentation*
    """

    # Render a completion as obsolete, usually using a strike-out.
    Deprecated: ClassVar["CompletionItemTag"] = 1 # type: ignore


class InsertTextFormat(TypedLSPEnum[int]):
    """
    Defines whether the insert text in a completion item should be interpreted as
    plain text or a snippet.

    *Generated from the TypeScript documentation*
    """

    # The primary text to be inserted is treated as a plain string.
    PlainText: ClassVar["InsertTextFormat"] = 1 # type: ignore
    
    # The primary text to be inserted is treated as a snippet.
    # 
    # A snippet can define tab stops and placeholders with `$1`, `$2`
    # and `${3:foo}`. `$0` defines the final tab stop, it defaults to
    # the end of the snippet. Placeholders with equal identifiers are linked,
    # that is typing in one will update others too.
    # 
    # See also: https://microsoft.github.io/language-server-protocol/specifications/specification-current/#snippet_syntax
    Snippet: ClassVar["InsertTextFormat"] = 2 # type: ignore


class InsertTextMode(TypedLSPEnum[int]):
    """
    How whitespace and indentation is handled during completion
    item insertion.
    
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # The insertion or replace strings is taken as it is. If the
    # value is multi line the lines below the cursor will be
    # inserted using the indentation defined in the string value.
    # The client will not apply any kind of adjustments to the
    # string.
    asIs: ClassVar["InsertTextMode"] = 1 # type: ignore
    
    # The editor adjusts leading whitespace of new lines so that
    # they match the indentation up to the cursor of the line for
    # which the item is accepted.
    # 
    # Consider a line like this: <2tabs><cursor><3tabs>foo. Accepting a
    # multi line completion item is indented using 2 tabs and all
    # following lines inserted will be indented using 2 tabs as well.
    adjustIndentation: ClassVar["InsertTextMode"] = 2 # type: ignore


class DocumentHighlightKind(TypedLSPEnum[int]):
    """
    A document highlight kind.

    *Generated from the TypeScript documentation*
    """

    # A textual occurrence.
    Text: ClassVar["DocumentHighlightKind"] = 1 # type: ignore
    
    # Read-access of a symbol, like reading a variable.
    Read: ClassVar["DocumentHighlightKind"] = 2 # type: ignore
    
    # Write-access of a symbol, like writing to a variable.
    Write: ClassVar["DocumentHighlightKind"] = 3 # type: ignore


class CodeActionKind(TypedLSPEnum[str], AllowCustomValues):
    """
    A set of predefined code action kinds

    *Generated from the TypeScript documentation*
    """

    # Empty kind.
    Empty: ClassVar["CodeActionKind"] = "" # type: ignore
    
    # Base kind for quickfix actions: 'quickfix'
    QuickFix: ClassVar["CodeActionKind"] = "quickfix" # type: ignore
    
    # Base kind for refactoring actions: 'refactor'
    Refactor: ClassVar["CodeActionKind"] = "refactor" # type: ignore
    
    # Base kind for refactoring extraction actions: 'refactor.extract'
    # 
    # Example extract actions:
    # 
    # - Extract method
    # - Extract function
    # - Extract variable
    # - Extract interface from class
    # - ...
    RefactorExtract: ClassVar["CodeActionKind"] = "refactor.extract" # type: ignore
    
    # Base kind for refactoring inline actions: 'refactor.inline'
    # 
    # Example inline actions:
    # 
    # - Inline function
    # - Inline variable
    # - Inline constant
    # - ...
    RefactorInline: ClassVar["CodeActionKind"] = "refactor.inline" # type: ignore
    
    # Base kind for refactoring rewrite actions: 'refactor.rewrite'
    # 
    # Example rewrite actions:
    # 
    # - Convert JavaScript function to class
    # - Add or remove parameter
    # - Encapsulate field
    # - Make method static
    # - Move method to base class
    # - ...
    RefactorRewrite: ClassVar["CodeActionKind"] = "refactor.rewrite" # type: ignore
    
    # Base kind for source actions: `source`
    # 
    # Source code actions apply to the entire file.
    Source: ClassVar["CodeActionKind"] = "source" # type: ignore
    
    # Base kind for an organize imports source action: `source.organizeImports`
    SourceOrganizeImports: ClassVar["CodeActionKind"] = "source.organizeImports" # type: ignore
    
    # Base kind for auto-fix source actions: `source.fixAll`.
    # 
    # Fix all actions automatically fix errors that have a clear fix that do not require user input.
    # They should not suppress errors or perform unsafe fixes such as generating new types or classes.
    # 
    # @since 3.15.0
    SourceFixAll: ClassVar["CodeActionKind"] = "source.fixAll" # type: ignore


class TraceValues(TypedLSPEnum[str]):
    """


    *Generated from the TypeScript documentation*
    """

    # Turn tracing off.
    Off: ClassVar["TraceValues"] = "off" # type: ignore
    
    # Trace messages only.
    Messages: ClassVar["TraceValues"] = "messages" # type: ignore
    
    # Verbose message tracing.
    Verbose: ClassVar["TraceValues"] = "verbose" # type: ignore


class MarkupKind(TypedLSPEnum[str]):
    """
    Describes the content type that a client supports in various
    result literals like `Hover`, `ParameterInfo` or `CompletionItem`.
    
    Please note that `MarkupKinds` must not start with a `$`. This kinds
    are reserved for internal usage.

    *Generated from the TypeScript documentation*
    """

    # Plain text is supported as a content format
    PlainText: ClassVar["MarkupKind"] = "plaintext" # type: ignore
    
    # Markdown is supported as a content format
    Markdown: ClassVar["MarkupKind"] = "markdown" # type: ignore


class PositionEncodingKind(TypedLSPEnum[str], AllowCustomValues):
    """
    A set of predefined position encoding kinds.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # Character offsets count UTF-8 code units.
    UTF8: ClassVar["PositionEncodingKind"] = "utf-8" # type: ignore
    
    # Character offsets count UTF-16 code units.
    # 
    # This is the default and must always be supported
    # by servers
    UTF16: ClassVar["PositionEncodingKind"] = "utf-16" # type: ignore
    
    # Character offsets count UTF-32 code units.
    # 
    # Implementation note: these are the same as Unicode code points,
    # so this `PositionEncodingKind` may also be used for an
    # encoding-agnostic representation of character offsets.
    UTF32: ClassVar["PositionEncodingKind"] = "utf-32" # type: ignore


class FileChangeType(TypedLSPEnum[int]):
    """
    The file event type

    *Generated from the TypeScript documentation*
    """

    # The file got created.
    Created: ClassVar["FileChangeType"] = 1 # type: ignore
    
    # The file got changed.
    Changed: ClassVar["FileChangeType"] = 2 # type: ignore
    
    # The file got deleted.
    Deleted: ClassVar["FileChangeType"] = 3 # type: ignore


class WatchKind(TypedLSPEnum[int], AllowCustomValues):
    """


    *Generated from the TypeScript documentation*
    """

    # Interested in create events.
    Create: ClassVar["WatchKind"] = 1 # type: ignore
    
    # Interested in change events
    Change: ClassVar["WatchKind"] = 2 # type: ignore
    
    # Interested in delete events
    Delete: ClassVar["WatchKind"] = 4 # type: ignore


class DiagnosticSeverity(TypedLSPEnum[int]):
    """
    The diagnostic's severity.

    *Generated from the TypeScript documentation*
    """

    # Reports an error.
    Error: ClassVar["DiagnosticSeverity"] = 1 # type: ignore
    
    # Reports a warning.
    Warning: ClassVar["DiagnosticSeverity"] = 2 # type: ignore
    
    # Reports an information.
    Information: ClassVar["DiagnosticSeverity"] = 3 # type: ignore
    
    # Reports a hint.
    Hint: ClassVar["DiagnosticSeverity"] = 4 # type: ignore


class DiagnosticTag(TypedLSPEnum[int]):
    """
    The diagnostic tags.
    
    @since 3.15.0

    *Generated from the TypeScript documentation*
    """

    # Unused or unnecessary code.
    # 
    # Clients are allowed to render diagnostics with this tag faded out instead of having
    # an error squiggle.
    Unnecessary: ClassVar["DiagnosticTag"] = 1 # type: ignore
    
    # Deprecated or obsolete code.
    # 
    # Clients are allowed to rendered diagnostics with this tag strike through.
    Deprecated: ClassVar["DiagnosticTag"] = 2 # type: ignore


class CompletionTriggerKind(TypedLSPEnum[int]):
    """
    How a completion was triggered

    *Generated from the TypeScript documentation*
    """

    # Completion was triggered by typing an identifier (24x7 code
    # complete), manual invocation (e.g Ctrl+Space) or via API.
    Invoked: ClassVar["CompletionTriggerKind"] = 1 # type: ignore
    
    # Completion was triggered by a trigger character specified by
    # the `triggerCharacters` properties of the `CompletionRegistrationOptions`.
    TriggerCharacter: ClassVar["CompletionTriggerKind"] = 2 # type: ignore
    
    # Completion was re-triggered as current completion list is incomplete
    TriggerForIncompleteCompletions: ClassVar["CompletionTriggerKind"] = 3 # type: ignore


class SignatureHelpTriggerKind(TypedLSPEnum[int]):
    """
    How a signature help was triggered.
    
    @since 3.15.0

    *Generated from the TypeScript documentation*
    """

    # Signature help was invoked manually by the user or by a command.
    Invoked: ClassVar["SignatureHelpTriggerKind"] = 1 # type: ignore
    
    # Signature help was triggered by a trigger character.
    TriggerCharacter: ClassVar["SignatureHelpTriggerKind"] = 2 # type: ignore
    
    # Signature help was triggered by the cursor moving or by the document content changing.
    ContentChange: ClassVar["SignatureHelpTriggerKind"] = 3 # type: ignore


class CodeActionTriggerKind(TypedLSPEnum[int]):
    """
    The reason why code actions were requested.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # Code actions were explicitly requested by the user or by an extension.
    Invoked: ClassVar["CodeActionTriggerKind"] = 1 # type: ignore
    
    # Code actions were requested automatically.
    # 
    # This typically happens when current selection in a file changes, but can
    # also be triggered when file content changes.
    Automatic: ClassVar["CodeActionTriggerKind"] = 2 # type: ignore


class FileOperationPatternKind(TypedLSPEnum[str]):
    """
    A pattern kind describing if a glob pattern matches a file a folder or
    both.
    
    @since 3.16.0

    *Generated from the TypeScript documentation*
    """

    # The pattern matches a file only.
    file: ClassVar["FileOperationPatternKind"] = "file" # type: ignore
    
    # The pattern matches a folder only.
    folder: ClassVar["FileOperationPatternKind"] = "folder" # type: ignore


class NotebookCellKind(TypedLSPEnum[int]):
    """
    A notebook cell kind.
    
    @since 3.17.0

    *Generated from the TypeScript documentation*
    """

    # A markup-cell is formatted source that is used for display.
    Markup: ClassVar["NotebookCellKind"] = 1 # type: ignore
    
    # A code-cell is source code.
    Code: ClassVar["NotebookCellKind"] = 2 # type: ignore


class ResourceOperationKind(TypedLSPEnum[str]):
    """


    *Generated from the TypeScript documentation*
    """

    # Supports creating new files and folders.
    Create: ClassVar["ResourceOperationKind"] = "create" # type: ignore
    
    # Supports renaming existing files and folders.
    Rename: ClassVar["ResourceOperationKind"] = "rename" # type: ignore
    
    # Supports deleting existing files and folders.
    Delete: ClassVar["ResourceOperationKind"] = "delete" # type: ignore


class FailureHandlingKind(TypedLSPEnum[str]):
    """


    *Generated from the TypeScript documentation*
    """

    # Applying the workspace change is simply aborted if one of the changes provided
    # fails. All operations executed before the failing operation stay executed.
    Abort: ClassVar["FailureHandlingKind"] = "abort" # type: ignore
    
    # All operations are executed transactional. That means they either all
    # succeed or no changes at all are applied to the workspace.
    Transactional: ClassVar["FailureHandlingKind"] = "transactional" # type: ignore
    
    # If the workspace edit contains only textual file changes they are executed transactional.
    # If resource changes (create, rename or delete file) are part of the change the failure
    # handling strategy is abort.
    TextOnlyTransactional: ClassVar["FailureHandlingKind"] = "textOnlyTransactional" # type: ignore
    
    # The client tries to undo the operations already executed. But there is no
    # guarantee that this is succeeding.
    Undo: ClassVar["FailureHandlingKind"] = "undo" # type: ignore


class PrepareSupportDefaultBehavior(TypedLSPEnum[int]):
    """


    *Generated from the TypeScript documentation*
    """

    # The client's default behavior is to select the identifier
    # according the to language's syntax rule.
    Identifier: ClassVar["PrepareSupportDefaultBehavior"] = 1 # type: ignore


class TokenFormat(TypedLSPEnum[str]):
    """


    *Generated from the TypeScript documentation*
    """

    Relative: ClassVar["TokenFormat"] = "relative" # type: ignore
