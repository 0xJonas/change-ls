from http.client import HTTPResponse
from urllib.request import Request, urlopen

import pytest

import lspscript.languages as languages
import lspscript.tokens as tokens


def check_url(url: str) -> bool:
    request = Request(url, method="HEAD")
    with urlopen(request) as response:
        if not isinstance(response, HTTPResponse):
            raise ValueError("Expected HTTP/HTTPS URL")
        return response.status >= 200 and response.status <= 299


@pytest.mark.uses_external_resources
@pytest.mark.slow
def test_grammar_uris_are_accessible() -> None:
    for grammar in languages.scope_to_grammar.values():
        if isinstance(grammar, tokens.grammar.BuiltInGrammar):
            # Reach into the object for the URL so we can send the requests asynchronously.
            # grammar.get_content() would be synchronous.
            assert check_url(grammar._url)  # type: ignore


@pytest.mark.uses_external_resources
@pytest.mark.slow
async def test_grammar_completeness() -> None:
    """
    Run with `pytest --log-cli-level=INFO ./test/test_languages.py::test_grammar_completeness`.

    This test should always pass, its purpose is to see which grammars are loaded for each language id.
    Grammars which are not found will log a warning.
    """
    for language_id in languages.language_id_to_scope.keys():
        await tokens.tokenize("\n", language_id)
