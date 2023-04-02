from pathlib import Path

from lspscript.tokens import Grammar, Token, lexeme, tokenize
from lspscript.util import install_language


async def test_tokenization_no_whitespace() -> None:
    grammar = Grammar.load_from_file(Path("test/mock_grammar.json"))
    install_language(language_id="mock", extensions=[".mock"], grammar=grammar, allow_override=True)
    text = """\
function test begin
    a = b + c
end
"""
    tokens = await tokenize(text, "mock")

    assert len(tokens) == 9
    assert tokens[0] == Token("function", set(["source.mock", "meta.function", "storage.type.function"]), 0)
    assert tokens[1] == Token("test", set(["source.mock", "meta.function", "entity.name.function"]), 9)
    assert tokens[2] == Token("begin", set(["source.mock", "meta.function", "keyword.other.begin"]), 14)
    assert tokens[3] == Token("a", set(["source.mock", "meta.function", "variable.other"]), 24)
    assert tokens[4] == Token("=", set(["source.mock", "meta.function", "keyword.operator.assignment"]), 26)
    assert tokens[5] == Token("b", set(["source.mock", "meta.function", "variable.other"]), 28)
    assert tokens[6] == Token("+", set(["source.mock", "meta.function", "keyword.operator.arithmetic"]), 30)
    assert tokens[7] == Token("c", set(["source.mock", "meta.function", "variable.other"]), 32)
    assert tokens[8] == Token("end", set(["source.mock", "meta.function", "keyword.other.end"]), 34)


async def test_tokenization_whitespace() -> None:
    grammar = Grammar.load_from_file(Path("test/mock_grammar.json"))
    install_language(language_id="mock", extensions=[".mock"], grammar=grammar, allow_override=True)
    text = """\
function test begin
    a = b + c
end
"""
    tokens = await tokenize(text, "mock", include_whitespace=True)

    assert len(tokens) == 19
    assert tokens[0] == Token("function", set(["source.mock", "meta.function", "storage.type.function"]), 0)
    assert tokens[1] == Token(" ", set(["source.mock", "meta.function"]), 8)
    assert tokens[2] == Token("test", set(["source.mock", "meta.function", "entity.name.function"]), 9)
    assert tokens[3] == Token(" ", set(["source.mock", "meta.function"]), 13)
    assert tokens[4] == Token("begin", set(["source.mock", "meta.function", "keyword.other.begin"]), 14)
    assert tokens[5] == Token("\n", set(["source.mock"]), 19)
    assert tokens[6] == Token("    ", set(["source.mock", "meta.function"]), 20)
    assert tokens[7] == Token("a", set(["source.mock", "meta.function", "variable.other"]), 24)
    assert tokens[8] == Token(" ", set(["source.mock", "meta.function"]), 25)
    assert tokens[9] == Token("=", set(["source.mock", "meta.function", "keyword.operator.assignment"]), 26)
    assert tokens[10] == Token(" ", set(["source.mock", "meta.function"]), 27)
    assert tokens[11] == Token("b", set(["source.mock", "meta.function", "variable.other"]), 28)
    assert tokens[12] == Token(" ", set(["source.mock", "meta.function"]), 29)
    assert tokens[13] == Token("+", set(["source.mock", "meta.function", "keyword.operator.arithmetic"]), 30)
    assert tokens[14] == Token(" ", set(["source.mock", "meta.function"]), 31)
    assert tokens[15] == Token("c", set(["source.mock", "meta.function", "variable.other"]), 32)
    assert tokens[16] == Token("\n", set(["source.mock"]), 33)
    assert tokens[17] == Token("end", set(["source.mock", "meta.function", "keyword.other.end"]), 34)
    assert tokens[18] == Token("\n", set(["source.mock"]), 37)


async def test_tokenization_line_breaks_lf() -> None:
    grammar = Grammar.load_from_file(Path("test/mock_grammar.json"))
    install_language(language_id="mock", extensions=[".mock"], grammar=grammar, allow_override=True)
    text = "function test begin\n    a = b + c\nend\n"
    tokens = await tokenize(text, "mock", include_whitespace=True)

    assert len(tokens) == 19
    assert tokens[5] % lexeme("\n")
    assert tokens[16] % lexeme("\n")
    assert tokens[18] % lexeme("\n")


async def test_tokenization_line_breaks_cr() -> None:
    grammar = Grammar.load_from_file(Path("test/mock_grammar.json"))
    install_language(language_id="mock", extensions=[".mock"], grammar=grammar, allow_override=True)
    text = "function test begin\r    a = b + c\rend\r"
    tokens = await tokenize(text, "mock", include_whitespace=True)

    assert len(tokens) == 19
    assert tokens[5] % lexeme("\r")
    assert tokens[16] % lexeme("\r")
    assert tokens[18] % lexeme("\r")


async def test_tokenization_line_breaks_crlf() -> None:
    grammar = Grammar.load_from_file(Path("test/mock_grammar.json"))
    install_language(language_id="mock", extensions=[".mock"], grammar=grammar, allow_override=True)
    text = "function test begin\r\n    a = b + c\r\nend\r\n"
    tokens = await tokenize(text, "mock", include_whitespace=True)

    assert len(tokens) == 19
    assert tokens[5] % lexeme("\r\n")
    assert tokens[16] % lexeme("\r\n")
    assert tokens[18] % lexeme("\r\n")
