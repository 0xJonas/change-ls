import atexit
import re
import shutil
import subprocess
from asyncio import (
    AbstractEventLoop,
    Event,
    Future,
    get_running_loop,
    new_event_loop,
    run_coroutine_threadsafe,
    set_event_loop,
    wrap_future,
)
from pathlib import Path
from threading import Lock, Thread
from typing import Any, List, Mapping, Optional, Sequence, Tuple, Union

import attrs
import cattrs

import change_ls._client as cls_client
import change_ls._languages as languages
from change_ls._protocol import LSSubprocessProtocol
from change_ls.logging import get_change_ls_default_logger  # type: ignore
from change_ls.logging import OperationLoggerAdapter
from change_ls.tokens._token_list import SyntacticToken, TokenList

version_pattern = re.compile(r"^v(\d+)\.(\d+)\.(\d+)\s*$")

MIN_NODE_VERSION = (14, 0, 0)


def check_node_version(path: Optional[str] = None) -> bool:
    """
    Checks whether a sufficient version of node is installed to run the token server.

    :param path: Check the node version at this path. If this is not given,
        the path returned by ``shutil.which("node")`` is used.
    """
    if not path:
        path = shutil.which("node")
    if not path:
        return False

    result = subprocess.run([path, "-v"], capture_output=True, encoding="utf-8", check=False)
    if result.returncode != 0:
        return False

    version_match = version_pattern.fullmatch(result.stdout)

    if not version_match:
        return False

    found_version = tuple(int(v) for v in version_match.group(1, 2, 3))
    return found_version >= MIN_NODE_VERSION


def get_token_server_path() -> Path:
    return Path(__file__).parent.parent / "token_server"


class TokenClientException(Exception):
    pass


@attrs.define
class TextDocumentTokenizeParams:
    scope_name: str
    text: str


@attrs.define
class TextDocumentTokenizeResult:
    scopes: List[str]
    tokens: List[List[int]]


JSON_VALUE = Union[int, float, bool, str, Sequence["JSON_VALUE"], Mapping[str, "JSON_VALUE"], None]


class _TokenClient:
    _protocol: LSSubprocessProtocol
    _logger: OperationLoggerAdapter
    _event_loop: AbstractEventLoop
    _converter: cattrs.Converter
    _request_counter: int

    def __init__(self, event_loop: AbstractEventLoop) -> None:
        self._logger = get_change_ls_default_logger("change-ls.tokens")
        self._event_loop = event_loop
        self._converter = cls_client._get_change_ls_converter()
        self._request_counter = 0

    def generate_request_id(self) -> str:
        self._request_counter += 1
        return "change-ls::tokens::" + str(self._request_counter)

    async def launch(self) -> None:
        node_path = shutil.which("node")
        if not node_path or not check_node_version(node_path):
            raise TokenClientException(
                "node with at least version "
                f"v{MIN_NODE_VERSION[0]}.{MIN_NODE_VERSION[1]}.{MIN_NODE_VERSION[2]} "
                "must be on PATH."
            )

        token_server_path = get_token_server_path()
        (_, self._protocol) = await get_running_loop().subprocess_exec(
            lambda: LSSubprocessProtocol(
                self._converter, self.dispatch_request, self.dispatch_notification
            ),
            node_path,
            str(token_server_path / "main.js"),
            cwd=str(token_server_path),
        )
        self._protocol._set_loggers(self._logger, self._logger, self._logger)  # type: ignore

    async def _send_request_internal(self, request: Any) -> Any:
        future: "Future[JSON_VALUE]" = self._event_loop.create_future()
        self._logger.info("Sending request (%s)", request.method)
        self._protocol.send_request(request, future)

        await future

        assert not future.cancelled()
        if exception := future.exception():
            self._logger.info("Request failed (%s)", request.method)
            raise exception
        else:
            return future.result()

    async def send_request(self, request: Any) -> Any:
        return await wrap_future(
            run_coroutine_threadsafe(self._send_request_internal(request), self._event_loop)
        )

    async def initialize(self) -> None:
        await self.send_request(
            cls_client.CustomRequest(self.generate_request_id(), "tokenServer/initialize")
        )

    async def _exit_internal(self) -> None:
        # This must be called from the TokenClient's thread.
        self._logger.info("Stopping token server...")
        self._protocol.send_notification(cls_client.CustomNotification("tokenServer/exit", None))
        await self._protocol.wait_for_disconnect()
        self._logger.info("Token server stopped!")

    def dispatch_request(self, method: str, params: JSON_VALUE) -> JSON_VALUE:
        if method == "grammar/requestRaw":
            return self.grammar_request_raw(params)

    def dispatch_notification(self, method: str, params: JSON_VALUE) -> None:
        pass

    def grammar_request_raw(self, params: JSON_VALUE) -> JSON_VALUE:
        assert isinstance(params, Mapping)
        assert "scopeName" in params
        scope_name = params["scopeName"]
        assert isinstance(scope_name, str)
        self._logger.info("Token Server requested grammar %s", scope_name)

        if grammar := languages.scope_to_grammar.get(scope_name):
            return {"rawGrammar": grammar.get_content(), "format": grammar.get_format()}
        else:
            self._logger.warning("Grammar %s not found", scope_name)
            # raise LSPException(LSPErrorCodes.RequestFailed.value, f"Grammar {scope_name} not found", scope_name)
            return None

    async def send_text_document_tokenize_request(
        self, params: TextDocumentTokenizeParams
    ) -> TextDocumentTokenizeResult:
        res_json = await self.send_request(
            cls_client.CustomRequest(
                self.generate_request_id(),
                "textDocument/tokenize",
                self._converter.unstructure(params),
            )
        )
        return self._converter.structure(res_json, TextDocumentTokenizeResult)


_token_client_instance: Optional[_TokenClient] = None
_token_client_lock = Lock()


async def _launch_token_client() -> _TokenClient:
    token_client: Optional[_TokenClient] = None
    token_client_ready = Event()
    main_event_loop = get_running_loop()

    def start_token_client_internal() -> None:
        # Runs on the token client's thread
        nonlocal token_client, token_client_ready, main_event_loop

        _token_client_event_loop = new_event_loop()
        set_event_loop(_token_client_event_loop)

        token_client = _TokenClient(_token_client_event_loop)
        _token_client_event_loop.run_until_complete(token_client.launch())
        _token_client_event_loop.run_until_complete(token_client.initialize())
        _token_client_event_loop.call_soon(
            lambda: main_event_loop.call_soon_threadsafe(token_client_ready.set)
        )
        _token_client_event_loop.run_forever()

    async def shutdown_token_client_internal() -> None:
        # Runs on the token client's thread
        assert token_client
        await token_client._exit_internal()
        get_running_loop().stop()

    def shutdown_token_client() -> None:
        # Does not run on the token client's thread
        nonlocal token_client_thread, token_client
        assert token_client
        run_coroutine_threadsafe(shutdown_token_client_internal(), token_client._event_loop)
        token_client_thread.join(timeout=10.0)
        if token_client_thread.is_alive():
            raise TokenClientException("Unable to stop token_client thread")

    # The TokenClient needs to run in its own thread, because it has to manage its own
    # event loop. If the main thread's event loop is stopped while the token server
    # is still running, the TokenClient is unable to properly shut down the server,
    # causing exceptions when the user's script exits.
    # The thread needs to be a daemon thread so it does not otherwise prevent
    # the Python interpreter from exiting when the script is done.
    token_client_thread = Thread(
        target=start_token_client_internal, name="token_client", daemon=True
    )
    atexit.register(shutdown_token_client)
    token_client_thread.start()
    await token_client_ready.wait()
    assert token_client
    return token_client


async def _get_token_client() -> _TokenClient:
    global _token_client_instance  # pylint: disable=global-statement

    with _token_client_lock:
        if not _token_client_instance:
            _token_client_instance = await _launch_token_client()

        assert _token_client_instance
        return _token_client_instance


def _find_line_break(text: str, offset: int) -> Tuple[int, str]:
    for i in range(offset, len(text)):
        if text[i : i + 2] == "\r\n":
            return i, text[i : i + 2]
        elif text[i] in ["\n", "\r"]:
            return i, text[i]
    return len(text), ""


async def tokenize(
    text: str, language_id: str, *, include_whitespace: bool = False
) -> TokenList[SyntacticToken]:
    scope_name = languages.language_id_to_scope[language_id]
    params = TextDocumentTokenizeParams(scope_name, text)
    instance = await _get_token_client()
    result = await instance.send_text_document_tokenize_request(params)

    offset = 0
    tokens: List[SyntacticToken] = []
    for (delta_line, delta_col, length), scopes_indices in zip(
        result.tokens[::2], result.tokens[1::2]
    ):
        for _ in range(delta_line):
            line_break_index, line_break_str = _find_line_break(text, offset)

            # Because vscode-textmate does weird stuff with newlines, they are
            # skipped in the token server and synthesized here instead.
            if include_whitespace:
                tokens.append(SyntacticToken(line_break_str, line_break_index, {scope_name}))

            offset = line_break_index + len(line_break_str)

        offset += delta_col

        lexeme = text[offset : offset + length]

        if not include_whitespace and lexeme.isspace():
            continue

        scopes = set(result.scopes[i] for i in scopes_indices)

        tokens.append(SyntacticToken(lexeme, offset, scopes))

    # Include potential trailing newline
    line_break_index, line_break_str = _find_line_break(text, offset)
    if line_break_str and include_whitespace:
        tokens.append(SyntacticToken(line_break_str, line_break_index, {scope_name}))

    return TokenList(tokens)
