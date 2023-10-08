from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import (Any, Generic, Optional, Sequence, Set, SupportsIndex,
                    Tuple, TypeVar, Union, overload)


class TokenMatcher(ABC):

    @abstractmethod
    def matches_token(self, token: "_BaseToken") -> bool:
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

    def matches_token(self, token: "_BaseToken") -> bool:
        return self.lexeme == token.lexeme


class ScopeTokenMatcher(TokenMatcher):
    scope: str

    def __init__(self, scope: str) -> None:
        super().__init__()
        self.scope = scope

    def matches_token(self, token: "_BaseToken") -> bool:
        if not isinstance(token, SyntacticToken):
            return False
        return self.scope in token.scopes


class SemanticTypeTokenMatcher(TokenMatcher):
    sem_type: str

    def __init__(self, sem_type: str) -> None:
        super().__init__()
        self.sem_type = sem_type

    def matches_token(self, token: "_BaseToken") -> bool:
        if not isinstance(token, _BaseSemanticToken):
            return False
        return self.sem_type == token.sem_type


class SemanticModifierTokenMatcher(TokenMatcher):
    sem_modifier: str

    def __init__(self, sem_modifier: str) -> None:
        super().__init__()
        self.sem_modifier = sem_modifier

    def matches_token(self, token: "_BaseToken") -> bool:
        if not isinstance(token, _BaseSemanticToken):
            return False
        return self.sem_modifier in token.sem_modifiers


class AndTokenMatcher(TokenMatcher):
    left: TokenMatcher
    right: TokenMatcher

    def __init__(self, left: TokenMatcher, right: TokenMatcher) -> None:
        super().__init__()
        self.left = left
        self.right = right

    def matches_token(self, token: "_BaseToken") -> bool:
        return self.left.matches_token(token) and self.right.matches_token(token)


class OrTokenMatcher(TokenMatcher):
    left: TokenMatcher
    right: TokenMatcher

    def __init__(self, left: TokenMatcher, right: TokenMatcher) -> None:
        super().__init__()
        self.left = left
        self.right = right

    def matches_token(self, token: "_BaseToken") -> bool:
        return self.left.matches_token(token) or self.right.matches_token(token)


class NotTokenMatcher(TokenMatcher):
    matcher: TokenMatcher

    def __init__(self, matcher: TokenMatcher) -> None:
        super().__init__()
        self.matcher = matcher

    def matches_token(self, token: "_BaseToken") -> bool:
        return not self.matcher.matches_token(token)


class AnyTokenMatcher(TokenMatcher):

    def matches_token(self, token: "_BaseToken") -> bool:
        return True


@dataclass
class _BaseToken(TokenMatcher):
    lexeme: str
    offset: int

    __slots__ = ["lexeme", "offset"]

    def __mod__(self, other: TokenMatcher) -> bool:
        return other.matches_token(self)

    @property
    def start_offset(self) -> int:
        return self.offset

    @property
    def end_offset(self) -> int:
        return self.offset + len(self.lexeme)

    def matches_token(self, token: "_BaseToken") -> bool:
        return self.lexeme == token.lexeme

    def __str__(self) -> str:
        return self.lexeme


@dataclass
class _BaseSemanticToken(_BaseToken):
    sem_type: Optional[str]
    sem_modifiers: Set[str]

    __slots__ = ["sem_type", "sem_modifiers"]

    def matches_token(self, token: "_BaseToken") -> bool:
        if not isinstance(token, _BaseSemanticToken):
            return False
        return (super().matches_token(token)
                and self.sem_type == token.sem_type
                and self.sem_modifiers == token.sem_modifiers)


@dataclass
class SemanticToken(_BaseSemanticToken):

    def __repr__(self) -> str:
        return f'SemanticToken({self.lexeme=!r}, {self.offset=!r}, {self.sem_type=!r}, {self.sem_modifiers=!r})'


@dataclass
class SyntacticToken(_BaseSemanticToken, TokenMatcher):
    scopes: Set[str]

    __slots__ = ["scopes"]

    def __init__(self, lexeme: str, offset: int, scopes: Set[str], sem_type: Optional[str] = None, sem_modifiers: Set[str] = set()) -> None:
        self.lexeme = lexeme
        self.offset = offset
        self.scopes = scopes
        self.sem_type = sem_type
        self.sem_modifiers = set(sem_modifiers)

    def matches_token(self, token: "_BaseToken") -> bool:
        if not isinstance(token, SyntacticToken):
            return False
        return (self.lexeme == token.lexeme
                and len(self.scopes) == len(token.scopes)
                and self.scopes == token.scopes)

    def __repr__(self) -> str:
        return f'SyntacticToken({self.lexeme=!r}, {self.offset=!r}, {self.sem_type=!r}, {self.sem_modifiers=!r}, {self.scopes=!r})'


_TokenType = TypeVar("_TokenType", bound=_BaseToken)


class TokenList(Generic[_TokenType], Tuple[_TokenType, ...]):

    def __setitem__(self, index: Any, value: Any) -> None:
        raise NotImplementedError("TokenLists are read-only.")

    @overload
    def __getitem__(self, index: SupportsIndex) -> _TokenType: ...
    @overload
    def __getitem__(self, index: slice) -> "TokenList[_TokenType]": ...

    def __getitem__(self, index: Union[SupportsIndex, slice]) -> Union["TokenList[_TokenType]", _TokenType]:
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


def sem_type(sem_type: str) -> SemanticTypeTokenMatcher:
    return SemanticTypeTokenMatcher(sem_type)


def sem_modifier(sem_modifier: str) -> SemanticModifierTokenMatcher:
    return SemanticModifierTokenMatcher(sem_modifier)


def any() -> AnyTokenMatcher:
    return AnyTokenMatcher()
