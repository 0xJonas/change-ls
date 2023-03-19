import json
import plistlib
from abc import ABC, abstractmethod
from http.client import HTTPResponse
from pathlib import Path
from typing import Optional
from urllib.request import Request, urlopen


def _extract_scope_name(raw: str, is_json: bool) -> str:
    if is_json:
        grammar = json.loads(raw)
        return grammar["scopeName"]
    else:
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
        scope_name = _extract_scope_name(content, url.endswith(".json"))
        return _UserGrammar(scope_name, content)

    @staticmethod
    def load_from_file(path: Path) -> "_UserGrammar":
        with path.open() as file:
            content = file.read()

        scope_name = _extract_scope_name(content, path.suffix == ".json")
        return _UserGrammar(scope_name, content)

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


class _UserGrammar(Grammar):
    _content: str

    def __init__(self, scope_name: str, content: str) -> None:
        super().__init__(scope_name)
        self._content = content

    def get_content(self) -> str:
        return self._content


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
