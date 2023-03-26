from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Sequence, Set, SupportsIndex, Tuple, Union, overload


class TokenMatcher(ABC):

    @abstractmethod
    def matches_token(self, token: "Token") -> bool:
        pass

    def __and__(self, other: "TokenMatcher") -> "AndTokenMatcher":
        return AndTokenMatcher(self, other)

    def __or__(self, other: "TokenMatcher") -> "OrTokenMatcher":
        return OrTokenMatcher(self, other)

    def __invert__(self) -> "NotTokenMatcher":
        return NotTokenMatcher(self)


class LexemeTokenMatcher(TokenMatcher):
    lexeme: str

    def __init__(self, lexeme: str) -> None:
        super().__init__()
        self.lexeme = lexeme

    def matches_token(self, token: "Token") -> bool:
        return self.lexeme == token.lexeme


class ScopeTokenMatcher(TokenMatcher):
    scope: str

    def __init__(self, scope: str) -> None:
        super().__init__()
        self.scope = scope

    def matches_token(self, token: "Token") -> bool:
        return self.scope in token.scopes


class AndTokenMatcher(TokenMatcher):
    left: TokenMatcher
    right: TokenMatcher

    def __init__(self, left: TokenMatcher, right: TokenMatcher) -> None:
        super().__init__()
        self.left = left
        self.right = right

    def matches_token(self, token: "Token") -> bool:
        return self.left.matches_token(token) and self.right.matches_token(token)


class OrTokenMatcher(TokenMatcher):
    left: TokenMatcher
    right: TokenMatcher

    def __init__(self, left: TokenMatcher, right: TokenMatcher) -> None:
        super().__init__()
        self.left = left
        self.right = right

    def matches_token(self, token: "Token") -> bool:
        return self.left.matches_token(token) or self.right.matches_token(token)


class NotTokenMatcher(TokenMatcher):
    matcher: TokenMatcher

    def __init__(self, matcher: TokenMatcher) -> None:
        super().__init__()
        self.matcher = matcher

    def matches_token(self, token: "Token") -> bool:
        return not self.matcher.matches_token(token)


class AnyTokenMatcher(TokenMatcher):

    def matches_token(self, _: "Token") -> bool:
        return True


@dataclass
class Token(TokenMatcher):
    lexeme: str
    scopes: Set[str]
    offset: int

    __slots__ = ["lexeme", "scopes", "offset"]

    def __mod__(self, other: TokenMatcher) -> bool:
        return other.matches_token(self)

    def matches_token(self, other: "Token") -> bool:
        return self.lexeme == other.lexeme \
            and len(self.scopes) == len(other.scopes) \
            and self.scopes == other.scopes


class TokenList(Tuple[Token, ...]):

    def __setitem__(self, index: Any, value: Any) -> None:
        raise NotImplementedError("TokenLists are read-only.")

    @overload
    def __getitem__(self, index: SupportsIndex) -> Token: ...
    @overload
    def __getitem__(self, index: slice) -> "TokenList": ...

    def __getitem__(self, index: Union[SupportsIndex, slice]) -> Union["TokenList", Token]:
        if isinstance(index, slice):
            return TokenList(super().__getitem__(index))
        else:
            return super().__getitem__(index)

    def __mod__(self, other: Sequence[TokenMatcher]) -> bool:
        if len(self) != len(other):
            return False
        return all(matcher.matches_token(token) for token, matcher in zip(self, other))


def lexeme(lexeme: str) -> LexemeTokenMatcher:
    return LexemeTokenMatcher(lexeme)


def scope(scope: str) -> ScopeTokenMatcher:
    return ScopeTokenMatcher(scope)


def any() -> AnyTokenMatcher:
    return AnyTokenMatcher()
