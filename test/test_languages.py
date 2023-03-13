import asyncio
from typing import Any, Coroutine, List

import aiohttp
import pytest

from lspscript.languages import scope_to_grammar


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
    for url in scope_to_grammar.values():
        requests.append(check_url(client_session, url))

    asyncio.gather(*requests)
