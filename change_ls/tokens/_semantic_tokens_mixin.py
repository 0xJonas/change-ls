from abc import abstractmethod, abstractproperty
from logging import DEBUG, Logger, LoggerAdapter, getLogger
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

from change_ls._change_ls_error import ChangeLSError
from change_ls._client import Client
from change_ls._util import TextDocumentInfo
from change_ls.logging import OperationLoggerAdapter, operation
from change_ls.tokens._token_list import SemanticToken, SyntacticToken, TokenList
from change_ls.types import (
    Position,
    SemanticTokens,
    SemanticTokensDelta,
    SemanticTokensDeltaParams,
    SemanticTokensLegend,
    SemanticTokensParams,
    TextDocumentIdentifier,
)

if TYPE_CHECKING:
    _LoggerAdapter = LoggerAdapter[Any]
else:
    _LoggerAdapter = LoggerAdapter


def _get_semantic_tokens_in_range(
    semantic_tokens: TokenList[SemanticToken], start: int, end: int, start_index: int = 0
) -> Tuple[List[SemanticToken], int]:
    # Adjust starting index to include all overlapping tokens
    while start_index < len(semantic_tokens) and semantic_tokens[start_index].end_offset < start:
        start_index += 1

    index = start_index
    semantic_tokens_len = len(semantic_tokens)
    out: List[SemanticToken] = []
    while index < semantic_tokens_len and semantic_tokens[index].start_offset < end:
        if semantic_tokens[index].end_offset >= start:
            out.append(semantic_tokens[index])
        index += 1

    return (out, start_index)


def _sort_candidate_semantic_tokens(
    candidates: List[SemanticToken], syn_token_start: int, syn_token_end: int
) -> None:
    def sort_key(sem_token: SemanticToken) -> Tuple[int, int]:
        sem_token_len = len(sem_token.lexeme)
        overlap_start = max(syn_token_start, sem_token.start_offset)
        overlap_end = min(syn_token_end, sem_token.end_offset)
        # semantic token length is negative, so if a longer semantic token
        # completely overlaps a shorter semantic token and both are overlapping the
        # same amount of the syntactic token, then the shorter token is preferred.
        return (overlap_end - overlap_start, -sem_token_len)

    candidates.sort(key=sort_key, reverse=True)


def enrich_syntactic_tokens(
    syntactic_tokens: TokenList[SyntacticToken],
    semantic_tokens: TokenList[SemanticToken],
    *,
    _logger: Optional[Union[Logger, _LoggerAdapter]] = None,
) -> None:
    """
    Enriches the given :class:`SyntacticTokens <SyntacticToken>` with semantic information
    from the given :class:`SemanticTokens <SemanticToken>`.

    This is similar to calling :meth:`TextDocument.load_tokens()` with ``mode="enrich"``.

    :param syntactic_tokens: The syntactic tokens to enrich.
    :param semantic_tokens: The semantic information to enrich the syntactic tokens by.
    """
    if _logger is None:
        _logger = OperationLoggerAdapter(getLogger("change-ls.workspace"))

    _logger.info("Enriching syntactic tokens with semantic information.")

    search_start_index = 0
    for index, syn_token in enumerate(syntactic_tokens):
        syn_token_start = syn_token.offset
        syn_token_end = syn_token_start + len(syn_token.lexeme)
        overlapping_semantic_tokens, search_start_index = _get_semantic_tokens_in_range(
            semantic_tokens, syn_token_start, syn_token_end, search_start_index
        )

        if len(overlapping_semantic_tokens) == 0:
            _logger.debug(
                f"No semantic token overlapping syntactic_tokens[{index}] = {syn_token!r}, clearing semantic data."
            )
            syn_token.sem_type = None
            syn_token.sem_modifiers = set()
            continue

        _sort_candidate_semantic_tokens(
            overlapping_semantic_tokens, syn_token.start_offset, syn_token.end_offset
        )

        semantic_token = overlapping_semantic_tokens[0]
        _logger.debug(
            f"Using first of semantic token candidates {overlapping_semantic_tokens!r} for syntactic_tokens[{index}] = {syn_token!r}."
        )
        syn_token.sem_type = semantic_token.sem_type
        syn_token.sem_modifiers = semantic_token.sem_modifiers


def _get_set_bits(bits: int) -> List[int]:
    bit = 0
    out: List[int] = []
    while bits > 0:
        if bit & 1 == 1:
            out.append(bit)
        bits >>= 1
        bit += 1
    return out


def _apply_semantic_token_delta(base: SemanticTokens, delta: SemanticTokensDelta) -> SemanticTokens:
    edits = list(delta.edits)
    edits.sort(key=lambda e: e.start)

    data_offset = 0
    new_data: List[int] = []
    for edit in edits:
        if data_offset < edit.start:
            new_data += base.data[data_offset : edit.start]
        if edit.data:
            new_data += edit.data
        data_offset = edit.start + edit.deleteCount
    if data_offset < len(base.data):
        new_data += base.data[data_offset:]

    return SemanticTokens(resultId=delta.resultId, data=new_data)


def _get_semantic_tokens_legend(client: Client) -> SemanticTokensLegend:
    server_capabilities = client._server_capabilities  # type: ignore
    assert server_capabilities is not None
    assert server_capabilities.semanticTokensProvider is not None
    return server_capabilities.semanticTokensProvider.legend


class SemanticTokensMixin:
    _cached_results: Dict[Client, SemanticTokens]
    _loaded_semantic_tokens: Dict[Client, TokenList[SemanticToken]]

    def __init__(self) -> None:
        self._cached_results = {}
        self._loaded_semantic_tokens = {}

    @abstractmethod
    def _resolve_client_parameter(self, client: Optional[Client]) -> Client:
        ...

    @abstractmethod
    def position_to_offset(self, position: Position, client: Optional[Client] = None) -> int:
        ...

    @abstractmethod
    def get_text_document_identifier(self) -> TextDocumentIdentifier:
        ...

    @abstractproperty
    def text(self) -> str:
        ...

    @abstractproperty
    def uri(self) -> str:
        ...

    @abstractproperty
    def language_id(self) -> str:
        ...

    @abstractproperty
    def logger(self) -> _LoggerAdapter:
        ...

    def _get_logger_from_context(self, *args: Any, **kwargs: Any) -> _LoggerAdapter:
        return self.logger

    def _parse_semantic_tokens_relative(
        self, data: List[int], legend: SemanticTokensLegend, client: Client
    ) -> TokenList[SemanticToken]:
        self.logger.info("Parsing raw token data in relative format.")
        if self.logger.getEffectiveLevel() <= DEBUG:
            self.logger.debug("Raw data: " + str(data))
        data_length = len(data)
        text = self.text

        current_line = 0
        current_start = 0
        tokens: List[SemanticToken] = []
        for i in range(0, data_length, 5):
            delta_line, delta_start, length, token_type_idx, token_modifiers_bits = data[i : i + 5]

            if delta_line != 0:
                current_line += delta_line
                current_start = delta_start
            else:
                current_start += delta_start

            offset = self.position_to_offset(
                Position(line=current_line, character=current_start), client
            )

            try:
                lexeme = text[offset : offset + length]
            except IndexError as e:
                raise ChangeLSError("Invalid semantic token data: Token is out of bounds") from e

            try:
                token_type = legend.tokenTypes[token_type_idx]
            except IndexError as e:
                raise ChangeLSError("Invalid semantic token data: Invalid token type") from e

            try:
                token_modifiers = {
                    legend.tokenModifiers[i] for i in _get_set_bits(token_modifiers_bits)
                }
            except IndexError as e:
                raise ChangeLSError("Invalid semantic token data: Invalid token modifier") from e

            tokens.append(SemanticToken(lexeme, offset, token_type, token_modifiers))

        if self.logger.getEffectiveLevel() <= DEBUG:
            self.logger.debug("Semantic tokens: " + repr(tokens))
        return TokenList(tokens)

    def _cache_result(self, result: SemanticTokens, client: Client) -> None:
        self.logger.info(f"Saving result '{result.resultId}' for Client '{client}'.")
        self._cached_results[client] = result

    async def _load_semantic_tokens_full(self, client: Client) -> TokenList[SemanticToken]:
        self.logger.info("Loading full semantic token list for Client '{client}'.")
        params = SemanticTokensParams(textDocument=self.get_text_document_identifier())
        result = await client.send_text_document_semantic_tokens_full(params)
        if result is None:
            self.logger.warning(
                f"Language server {client.server_info} did not send semantic tokens, no semantic information available."
            )
            return TokenList([])

        if result.resultId is not None:
            # Only cache results with a known resultId, since without a resultId
            # we cannot use this result for textDocument/semanticTokens/full/delta requests.
            self._cache_result(result, client)

        return self._parse_semantic_tokens_relative(
            result.data, _get_semantic_tokens_legend(client), client
        )

    async def _load_semantic_tokens_delta(self, client: Client) -> TokenList[SemanticToken]:
        self.logger.info(f"Loading semantic token delta for Client '{client}'.")
        previous_result = self._cached_results[client]
        assert previous_result.resultId is not None
        params = SemanticTokensDeltaParams(
            textDocument=self.get_text_document_identifier(),
            previousResultId=previous_result.resultId,
        )
        delta = await client.send_text_document_semantic_tokens_full_delta(params)

        if delta is None:
            self.logger.warning(
                f"Language server {client.server_info} did not send semantic tokens, using previous response's data."
            )
            return self._parse_semantic_tokens_relative(
                previous_result.data, _get_semantic_tokens_legend(client), client
            )

        if isinstance(delta, SemanticTokensDelta):
            self.logger.info(
                f"Applying semantic token delta to result '{previous_result.resultId}'."
            )
            result = _apply_semantic_token_delta(previous_result, delta)
        else:
            result = delta

        if result.resultId is not None:
            # Only cache results with a known resultId, since without a resultId
            # we cannot use this result for textDocument/semanticTokens/full/delta requests.
            self._cache_result(result, client)

        return self._parse_semantic_tokens_relative(
            result.data, _get_semantic_tokens_legend(client), client
        )

    @operation(
        start_message="Loading semantic tokens using Client {client}...",
        get_logger_from_context=_get_logger_from_context,
    )
    async def _load_semantic_tokens(self, client: Optional[Client] = None) -> None:
        client = self._resolve_client_parameter(client)

        if client in self._cached_results and client.check_feature(
            "textDocument/semanticTokens",
            semantic_tokens=["full/delta"],
            text_document=TextDocumentInfo(self.uri, self.language_id),
        ):
            self._loaded_semantic_tokens[client] = await self._load_semantic_tokens_delta(client)
        elif client.check_feature(
            "textDocument/semanticTokens",
            sematic_tokens=["full"],
            text_document=TextDocumentInfo(self.uri, self.language_id),
        ):
            self._loaded_semantic_tokens[client] = await self._load_semantic_tokens_full(client)
        else:
            raise ChangeLSError(f"Client {client} does not support semantic tokens.")

    @property
    def sem_tokens(self) -> TokenList[SemanticToken]:
        """
        The semantic tokens for this document. This property is only valid when exactly one
        :class:`Client` is running in the current :class:`Workspace` and semantic tokens have
        been loaded for that client.
        """
        return self.get_loaded_semantic_tokens()

    def get_loaded_semantic_tokens(
        self, client: Optional[Client] = None
    ) -> TokenList[SemanticToken]:
        """
        Returns semantic tokens previously loaded with :meth:`TextDocument.load_tokens()` using
        either ``mode="enrich"`` or ``mode="semantic"``.

        :param client: The :class:`Client` which was used to load the semantic tokens.
            If only one client is running in the current :class:`Workspace` this parameter is optional.
        """
        out = self._loaded_semantic_tokens.get(self._resolve_client_parameter(client))

        if out is None:
            raise ChangeLSError(f"No semantic tokens are loaded for client {client}")
        return out
