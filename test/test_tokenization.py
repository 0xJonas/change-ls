from pathlib import Path

from change_ls import install_language
from change_ls.tokens import Grammar, SyntacticToken, lexeme, tokenize


async def test_tokenization_no_whitespace() -> None:
    grammar = Grammar.load_from_file(Path("test/mock_grammar.json"))
    install_language(language_id="mock", extensions=[".mock"], grammar=grammar, allow_overwrite=True)
    text = """\
function test begin
    a = b + c
end
"""
    tokens = await tokenize(text, "mock")

    assert len(tokens) == 9
    assert tokens[0] == SyntacticToken("function", 0, {"source.mock", "meta.function", "storage.type.function"})
    assert tokens[1] == SyntacticToken("test", 9, {"source.mock", "meta.function", "entity.name.function"})
    assert tokens[2] == SyntacticToken("begin", 14, {"source.mock", "meta.function", "keyword.other.begin"})
    assert tokens[3] == SyntacticToken("a", 24, {"source.mock", "meta.function", "variable.other"},)
    assert tokens[4] == SyntacticToken("=", 26, {"source.mock", "meta.function", "keyword.operator.assignment"})
    assert tokens[5] == SyntacticToken("b", 28, {"source.mock", "meta.function", "variable.other"},)
    assert tokens[6] == SyntacticToken("+", 30, {"source.mock", "meta.function", "keyword.operator.arithmetic"})
    assert tokens[7] == SyntacticToken("c", 32, {"source.mock", "meta.function", "variable.other"},)
    assert tokens[8] == SyntacticToken("end", 34, {"source.mock", "meta.function", "keyword.other.end"})


async def test_tokenization_whitespace() -> None:
    grammar = Grammar.load_from_file(Path("test/mock_grammar.json"))
    install_language(language_id="mock", extensions=[".mock"], grammar=grammar, allow_overwrite=True)
    text = """\
function test begin
    a = b + c
end
"""
    tokens = await tokenize(text, "mock", include_whitespace=True)

    assert len(tokens) == 19
    assert tokens[0] == SyntacticToken("function", 0, {"source.mock", "meta.function", "storage.type.function"})
    assert tokens[1] == SyntacticToken(" ", 8, {"source.mock", "meta.function"})
    assert tokens[2] == SyntacticToken("test", 9, {"source.mock", "meta.function", "entity.name.function"})
    assert tokens[3] == SyntacticToken(" ", 13, {"source.mock", "meta.function"})
    assert tokens[4] == SyntacticToken("begin", 14, {"source.mock", "meta.function", "keyword.other.begin"})
    assert tokens[5] == SyntacticToken("\n", 19, {"source.mock"})
    assert tokens[6] == SyntacticToken("    ", 20, {"source.mock", "meta.function"})
    assert tokens[7] == SyntacticToken("a", 24, {"source.mock", "meta.function", "variable.other"})
    assert tokens[8] == SyntacticToken(" ", 25, {"source.mock", "meta.function"})
    assert tokens[9] == SyntacticToken("=", 26, {"source.mock", "meta.function", "keyword.operator.assignment"})
    assert tokens[10] == SyntacticToken(" ", 27, {"source.mock", "meta.function"})
    assert tokens[11] == SyntacticToken("b", 28, {"source.mock", "meta.function", "variable.other"})
    assert tokens[12] == SyntacticToken(" ", 29, {"source.mock", "meta.function"})
    assert tokens[13] == SyntacticToken("+", 30, {"source.mock", "meta.function", "keyword.operator.arithmetic"})
    assert tokens[14] == SyntacticToken(" ", 31, {"source.mock", "meta.function"})
    assert tokens[15] == SyntacticToken("c", 32, {"source.mock", "meta.function", "variable.other"})
    assert tokens[16] == SyntacticToken("\n", 33, {"source.mock"})
    assert tokens[17] == SyntacticToken("end", 34, {"source.mock", "meta.function", "keyword.other.end"})
    assert tokens[18] == SyntacticToken("\n", 37, {"source.mock"})


async def test_tokenization_line_breaks_lf() -> None:
    grammar = Grammar.load_from_file(Path("test/mock_grammar.json"))
    install_language(language_id="mock", extensions=[".mock"], grammar=grammar, allow_overwrite=True)
    text = "function test begin\n    a = b + c\nend\n"
    tokens = await tokenize(text, "mock", include_whitespace=True)

    assert len(tokens) == 19
    assert tokens[5] % lexeme("\n")
    assert tokens[16] % lexeme("\n")
    assert tokens[18] % lexeme("\n")


async def test_tokenization_line_breaks_cr() -> None:
    grammar = Grammar.load_from_file(Path("test/mock_grammar.json"))
    install_language(language_id="mock", extensions=[".mock"], grammar=grammar, allow_overwrite=True)
    text = "function test begin\r    a = b + c\rend\r"
    tokens = await tokenize(text, "mock", include_whitespace=True)

    assert len(tokens) == 19
    assert tokens[5] % lexeme("\r")
    assert tokens[16] % lexeme("\r")
    assert tokens[18] % lexeme("\r")


async def test_tokenization_line_breaks_crlf() -> None:
    grammar = Grammar.load_from_file(Path("test/mock_grammar.json"))
    install_language(language_id="mock", extensions=[".mock"], grammar=grammar, allow_overwrite=True)
    text = "function test begin\r\n    a = b + c\r\nend\r\n"
    tokens = await tokenize(text, "mock", include_whitespace=True)

    assert len(tokens) == 19
    assert tokens[5] % lexeme("\r\n")
    assert tokens[16] % lexeme("\r\n")
    assert tokens[18] % lexeme("\r\n")
