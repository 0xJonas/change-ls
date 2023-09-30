import atexit
import re
import shutil
import subprocess
from asyncio import (AbstractEventLoop, Event, Future, get_running_loop,
                     new_event_loop, run_coroutine_threadsafe, set_event_loop,
                     wrap_future)
from dataclasses import dataclass
from logging import Logger, getLogger
from pathlib import Path
from threading import Lock, Thread
from typing import List, Mapping, Optional, Tuple

import change_ls._languages as languages
from change_ls._protocol import LSSubprocessProtocol
from change_ls.tokens._token_list import SyntacticToken, TokenList
from change_ls.types._util import (JSON_VALUE, json_assert_type_array,
                                   json_assert_type_int,
                                   json_assert_type_object,
                                   json_assert_type_string, json_get_array,
                                   json_get_string)

version_pattern = re.compile(r"^v(\d+)\.(\d+)\.(\d+)\s*$")

MIN_NODE_VERSION_MAJOR = 14
MIN_NODE_VERSION_MINOR = 0
MIN_NODE_VERSION_PATCH = 0


def check_node_version(path: str) -> bool:
    result = subprocess.run([path, "-v"], capture_output=True, encoding="utf-8")
    version_match = version_pattern.fullmatch(result.stdout)

    if not version_match:
        return False

    major, minor, patch = version_match.group(1, 2, 3)
    return int(major) >= MIN_NODE_VERSION_MAJOR and int(minor) >= MIN_NODE_VERSION_MINOR and int(patch) >= MIN_NODE_VERSION_PATCH


def get_token_server_path() -> Path:
    return Path(__file__).parent.parent / "token_server"


class TokenClientException(Exception):
    pass


@dataclass
class TextDocumentTokenizeParams:
    scope_name: str
    text: str

    @classmethod
    def from_json(cls, json: Mapping[str, JSON_VALUE]) -> "TextDocumentTokenizeParams":
        scope_name = json_get_string(json, "scopeName")
        text = json_get_string(json, "text")
        return cls(scope_name, text)

    def to_json(self) -> JSON_VALUE:
        return {
            "scopeName": self.scope_name,
            "text": self.text
        }


@dataclass
class TextDocumentTokenizeResult:
    scopes: List[str]
    tokens: List[List[int]]

    @classmethod
    def from_json(cls, json: Mapping[str, JSON_VALUE]) -> "TextDocumentTokenizeResult":
        scopes = [json_assert_type_string(s) for s in json_get_array(json, "scopes")]
        tokens = [[json_assert_type_int(s) for s in json_assert_type_array(a)]
                  for a in json_get_array(json, "tokens")]
        return cls(scopes, tokens)

    def to_json(self) -> JSON_VALUE:
        return {
            "scopes": self.scopes,
            "tokens": self.tokens
        }


class _TokenClient:

    _protocol: LSSubprocessProtocol
    _logger: Logger

    def __init__(self) -> None:
        self._logger = getLogger("lspscript.tokens")

    async def launch(self) -> None:
        node_path = shutil.which("node")
        if not node_path or not check_node_version(node_path):
            raise TokenClientException(
                f"node with at least version {MIN_NODE_VERSION_MAJOR}.{MIN_NODE_VERSION_MINOR}.{MIN_NODE_VERSION_PATCH} must be on PATH.")

        token_server_path = get_token_server_path()
        (_, self._protocol) = await get_running_loop().subprocess_exec(
            lambda: LSSubprocessProtocol(self.dispatch_request, self.dispatch_notification, self._logger),
            node_path, str(token_server_path / "main.js"),
            cwd=str(token_server_path))

    async def send_request(self, method: str, params: JSON_VALUE) -> JSON_VALUE:
        future: Future[JSON_VALUE] = get_running_loop().create_future()
        self._logger.info("Sending request (%s)", method)
        self._protocol.send_request(method, params, future)

        await future

        assert not future.cancelled()
        if exception := future.exception():
            self._logger.info("Request failed (%s)", method)
            raise exception
        else:
            return future.result()

    async def initialize(self) -> None:
        await self.send_request("initialize", None)

    async def exit(self) -> None:
        self._logger.info("Stopping token server")
        self._protocol.send_notification("exit", None)
        await self._protocol.wait_for_disconnect()
        self._logger.info("Token server stopped")

    def dispatch_request(self, method: str, params: JSON_VALUE) -> JSON_VALUE:
        if method == "grammar/requestRaw":
            return self.grammar_request_raw(params)
        pass

    def dispatch_notification(self, method: str, params: JSON_VALUE) -> None:
        pass

    def grammar_request_raw(self, params: JSON_VALUE) -> JSON_VALUE:
        scope_name = json_get_string(json_assert_type_object(params), "scopeName")
        self._logger.info("Token Server requested grammar %s", scope_name)

        if grammar := languages.scope_to_grammar.get(scope_name):
            return {
                "rawGrammar": grammar.get_content(),
                "format": grammar.get_format()
            }
        else:
            self._logger.warning("Grammar %s not found", scope_name)
            # raise LSPException(LSPErrorCodes.RequestFailed.value, f"Grammar {scope_name} not found", scope_name)
            return None

    async def send_text_document_tokenize_request(self, params: TextDocumentTokenizeParams) -> TextDocumentTokenizeResult:
        res_json = await self.send_request("textDocument/tokenize", params.to_json())
        res = json_assert_type_object(res_json)
        return TextDocumentTokenizeResult.from_json(res)


_token_client_instance: Optional[_TokenClient] = None
_token_client_event_loop: AbstractEventLoop
_token_client_lock = Lock()


async def _start_token_client() -> None:
    token_client_ready = Event()
    main_event_loop = get_running_loop()

    def start_token_client_internal() -> None:
        global _token_client_event_loop, _token_client_instance
        nonlocal token_client_ready, main_event_loop

        _token_client_event_loop = new_event_loop()
        set_event_loop(_token_client_event_loop)

        _token_client_instance = _TokenClient()
        _token_client_event_loop.run_until_complete(_token_client_instance.launch())
        _token_client_event_loop.run_until_complete(_token_client_instance.initialize())
        _token_client_event_loop.call_soon(
            lambda: main_event_loop.call_soon_threadsafe(lambda: token_client_ready.set()))
        _token_client_event_loop.run_forever()

    async def shutdown_token_client_internal() -> None:
        global _token_client_instance
        assert _token_client_instance
        await _token_client_instance.exit()
        get_running_loop().stop()

    def shutdown_token_client() -> None:
        global _token_client_event_loop
        nonlocal token_client_thread
        run_coroutine_threadsafe(shutdown_token_client_internal(), _token_client_event_loop)
        token_client_thread.join(timeout=10.0)
        if token_client_thread.is_alive():
            raise Exception("Unable to stop token_client thread")

    token_client_thread = Thread(target=start_token_client_internal, name="token_client", daemon=True)
    atexit.register(shutdown_token_client)
    token_client_thread.start()
    await token_client_ready.wait()


async def _get_token_client() -> _TokenClient:
    global _token_client_instance

    with _token_client_lock:
        if not _token_client_instance:
            await _start_token_client()
            assert _token_client_instance

        return _token_client_instance


def _find_line_break(text: str, offset: int) -> Tuple[int, str]:
    for i in range(offset, len(text)):
        if text[i:i+2] == "\r\n":
            return i, text[i:i+2]
        elif text[i] in ["\n", "\r"]:
            return i, text[i]
    return len(text), ""


async def tokenize(text: str, language_id: str, *, include_whitespace: bool = False) -> TokenList[SyntacticToken]:
    scope_name = languages.language_id_to_scope[language_id]
    params = TextDocumentTokenizeParams(scope_name, text)
    instance = await _get_token_client()
    result = await wrap_future(run_coroutine_threadsafe(
        instance.send_text_document_tokenize_request(params), _token_client_event_loop))

    offset = 0
    tokens: List[SyntacticToken] = []
    for (delta_line, delta_col, length), scopes_indices in zip(result.tokens[::2], result.tokens[1::2]):
        for _ in range(delta_line):
            line_break_index, line_break_str = _find_line_break(text, offset)

            # Because vscode-textmate does weird stuff with newlines, they are
            # skipped in the token server and synthesized here instead.
            if include_whitespace:
                tokens.append(SyntacticToken(line_break_str, line_break_index, {scope_name}))

            offset = line_break_index + len(line_break_str)

        offset += delta_col

        lexeme = text[offset:offset + length]

        if not include_whitespace and lexeme.isspace():
            continue

        scopes = set(result.scopes[i] for i in scopes_indices)

        tokens.append(SyntacticToken(lexeme, offset, scopes))

    # Include potential trailing newline
    line_break_index, line_break_str = _find_line_break(text, offset)
    if line_break_str and include_whitespace:
        tokens.append(SyntacticToken(line_break_str, line_break_index, {scope_name}))

    return TokenList(tokens)