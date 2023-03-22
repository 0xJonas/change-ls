import pytest

from lspscript.tokens import *


def test_token_list_is_read_only() -> None:
    token_list = TokenList([
        Token("test1", ["source.test", "scope.1"], 0),
        Token("test2", ["source.test", "scope.2"], 5)
    ])

    with pytest.raises(NotImplementedError):
        token_list[0] = Token("new", ["source.test", "scope.1"], 0)


def test_token_matching() -> None:
    token = Token("test1", ["source.test", "scope.1"], 0)
    assert token % lexeme("test1")
    assert token % scope("scope.1")
    assert not token % lexeme("test2")
    assert not token % scope("scope.2")


def test_and_token_matcher() -> None:
    token = Token("test1", ["source.test", "scope.1"], 0)
    assert token % (lexeme("test1") & scope("source.test"))
    assert not token % (lexeme("test2") & scope("source.test"))
    assert not token % (lexeme("test1") & scope("source.fail"))
    assert not token % (lexeme("test2") & scope("source.fail"))


def test_or_token_matcher() -> None:
    token = Token("test1", ["source.test", "scope.1"], 0)
    assert token % (lexeme("test1") | scope("source.test"))
    assert token % (lexeme("test2") | scope("source.test"))
    assert token % (lexeme("test1") | scope("source.fail"))
    assert not token % (lexeme("test2") | scope("source.fail"))


def test_not_token_matcher() -> None:
    token = Token("test1", ["source.test", "scope.1"], 0)
    assert token % ~lexeme("test2")
    assert not token % ~lexeme("test1")


def test_token_list_matching() -> None:
    token_list = TokenList([
        Token("test1", ["source.test", "scope.1"], 0),
        Token("test2", ["source.test", "scope.2"], 5)
    ])

    assert not token_list % []
    assert token_list % [scope("scope.1"), scope("scope.2")]
    assert not token_list % [scope("scope.1"), scope("scope.1")]
