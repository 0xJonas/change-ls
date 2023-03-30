from pathlib import Path
from types import TracebackType
from typing import Dict, List, Optional, Type

from lspscript.client import Client
from lspscript.lsp_exception import LSPScriptException
from lspscript.tokens import TokenList
from lspscript.types import (DidCloseTextDocumentParams,
                             OptionalVersionedTextDocumentIdentifier,
                             TextDocumentItem, VersionedTextDocumentIdentifier)
from lspscript.util import TextDocumentInfo, guess_language_id


class TextDocument(TextDocumentInfo, VersionedTextDocumentIdentifier, OptionalVersionedTextDocumentIdentifier, TextDocumentItem):
    _path: Path
    _encoding: str
    _clients: Dict[str, Client]
    _tokens: Optional[TokenList]

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

        uri = path.as_uri()
        TextDocumentInfo.__init__(self, uri, language_id)
        VersionedTextDocumentIdentifier.__init__(self, uri=uri, version=version)
        OptionalVersionedTextDocumentIdentifier.__init__(self, uri=uri, version=version)
        TextDocumentItem.__init__(self, uri=uri, languageId=language_id, version=version, text=text)

    def close(self, client_names: Optional[List[str]] = None) -> None:
        if client_names is None:
            client_names = list(self._clients.keys())

        for name in client_names:
            params = DidCloseTextDocumentParams(textDocument=self)
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

        #
        # text_document.close()
        # text_document.__aexit()__
        # - textDocument/didClose
        #
        # commit_edits()
        # - textDocument/didChange
        #
        # save()
        # - textDocument/willSave
        # - textDocument/willSaveWaitUntil
