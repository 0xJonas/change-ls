import pytest

from lspscript.tokens import *


def test_token_list_is_read_only() -> None:
    token_list = TokenList([
        SyntacticToken("test1", 0, {"source.test", "scope.1"}),
        SyntacticToken("test2", 5, {"source.test", "scope.2"})
    ])

    with pytest.raises(NotImplementedError):
        token_list[0] = SyntacticToken("new", 0, {"source.test", "scope.1"})


def test_token_matching() -> None:
    token = SyntacticToken("test1", 0, {"source.test", "scope.1"})
    assert token % lexeme("test1")
    assert token % scope("scope.1")
    assert not token % lexeme("test2")
    assert not token % scope("scope.2")


def test_and_token_matcher() -> None:
    token = SyntacticToken("test1", 0, {"source.test", "scope.1"})
    assert token % (lexeme("test1") & scope("source.test"))
    assert not token % (lexeme("test2") & scope("source.test"))
    assert not token % (lexeme("test1") & scope("source.fail"))
    assert not token % (lexeme("test2") & scope("source.fail"))


def test_or_token_matcher() -> None:
    token = SyntacticToken("test1", 0, {"source.test", "scope.1"})
    assert token % (lexeme("test1") | scope("source.test"))
    assert token % (lexeme("test2") | scope("source.test"))
    assert token % (lexeme("test1") | scope("source.fail"))
    assert not token % (lexeme("test2") | scope("source.fail"))


def test_not_token_matcher() -> None:
    token = SyntacticToken("test1", 0, {"source.test", "scope.1"})
    assert token % ~lexeme("test2")
    assert not token % ~lexeme("test1")


def test_token_list_matching() -> None:
    token_list = TokenList([
        SyntacticToken("test1", 0, {"source.test", "scope.1"}),
        SyntacticToken("test2", 5, {"source.test", "scope.2"})
    ])

    assert not token_list % []
    assert token_list % [scope("scope.1"), scope("scope.2")]
    assert not token_list % [scope("scope.1"), scope("scope.1")]
