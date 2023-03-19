import asyncio
from typing import Any, Coroutine, List

import aiohttp
import pytest

import lspscript.languages as languages
from lspscript.tokens.grammar import BuiltInGrammar


@pytest.fixture
async def client_session():
    async with aiohttp.ClientSession() as client:
        yield client
        await asyncio.sleep(0.3)


async def check_url(client_session: aiohttp.ClientSession, url: str) -> None:
    async with client_session.get(url) as response:
        assert response.status == 200


async def test_grammar_uris_are_accessible(client_session: aiohttp.ClientSession) -> None:
    requests: List[Coroutine[Any, Any, None]] = []
    for grammar in languages.scope_to_grammar.values():
        if isinstance(grammar, BuiltInGrammar):
            # Reach into the object for the URL so we can send the requests asynchronously.
            # grammar.get_content() would be synchronous.
            requests.append(check_url(client_session, grammar._url))  # type: ignore

    asyncio.gather(*requests)

# TODO: grammar completeness
