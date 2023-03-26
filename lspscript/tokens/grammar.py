import json
import plistlib
from abc import ABC, abstractmethod
from http.client import HTTPResponse
from pathlib import Path
from typing import Literal, Optional
from urllib.request import Request, urlopen

GrammarFormat = Literal["json", "plist"]


def _extract_scope_name(raw: str, format: GrammarFormat) -> str:
    if format == "json":
        grammar = json.loads(raw)
        return grammar["scopeName"]
    elif format == "plist":
        grammar = plistlib.loads(raw.encode())
        return grammar["scopeName"]


def _fetch_text_from_url(url: str) -> str:
    request = Request(url, method="GET")
    with urlopen(request) as response:
        if not isinstance(response, HTTPResponse):
            raise ValueError("Expected HTTP/HTTPS URL")
        if response.status < 200 or response.status > 299:
            raise Exception(f"Request failed: status {response.status} {response.reason}")

        return response.read().decode()


class Grammar(ABC):
    """
    Opaque object representing a TextMate grammar.
    """
    _scope_name: str

    def __init__(self, scope_name: str) -> None:
        self._scope_name = scope_name

    @staticmethod
    def load_from_url(url: str) -> "_UserGrammar":
        content = _fetch_text_from_url(url)
        format = "json" if url.endswith(".json") else "plist"
        scope_name = _extract_scope_name(content, format)
        return _UserGrammar(scope_name, content, format)

    @staticmethod
    def load_from_file(path: Path) -> "_UserGrammar":
        with path.open() as file:
            content = file.read()

        format = "json" if path.suffix == ".json" else "plist"
        scope_name = _extract_scope_name(content, format)
        return _UserGrammar(scope_name, content, format)

    def get_scope_name(self) -> str:
        """
        Returns the initial scope name for the `Grammar`.
        """
        return self._scope_name

    @abstractmethod
    def get_content(self) -> str:
        """
        Returns the raw content of the `Grammar`.
        """
        pass

    @abstractmethod
    def get_format(self) -> GrammarFormat:
        """
        Returns the format of the Grammar's raw content, e.g. "json" or "plist".
        """
        pass


class _UserGrammar(Grammar):
    _content: str
    _format: GrammarFormat

    def __init__(self, scope_name: str, content: str, format: GrammarFormat) -> None:
        super().__init__(scope_name)
        self._content = content
        self._format = format

    def get_content(self) -> str:
        return self._content

    def get_format(self) -> GrammarFormat:
        return self._format


class BuiltInGrammar(Grammar):
    _content: Optional[str]
    _url: str

    def __init__(self, scope_name: str, url: str) -> None:
        super().__init__(scope_name)
        self._url = url

    def get_content(self) -> str:
        if self._content is None:
            self._content = _fetch_text_from_url(self._url)

        return self._content

    def get_format(self) -> GrammarFormat:
        if self._url.endswith(".json"):
            return "json"
        else:
            return "plist"
