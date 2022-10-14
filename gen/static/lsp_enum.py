from typing import Any, ClassVar, Dict, Generic, Tuple, Type, TypeVar


# The next two functions are copied from cpython/enum.py

def _is_dunder(name: str) -> bool:
    """Returns True if a __dunder__ name, False otherwise."""
    return (
        len(name) > 4 and
        name[:2] == name[-2:] == '__' and
        name[2] != '_' and
        name[-3] != '_'
    )

def _is_descriptor(obj: Any) -> bool:
    """Returns True if obj is a descriptor, False otherwise."""
    return (
        hasattr(obj, '__get__') or
        hasattr(obj, '__set__') or
        hasattr(obj, '__delete__')
    )


class LSPEnumException(Exception):
    value: str

    def __init__(self, value: str) -> None:
        self.value = value

    def __str__(self) -> str:
        return f"Enum does not contain an entry with value {self.value} and does not support custom values."


class _LSPEnumProtoMember:
    """This class is a temporary representation of an LSPEnum member.
    When the final LSPEnum class is created, it replaces the value with
    an instance of that LSPEnum class. This cannot be done in the metaclass
    because the Enum class does not exist at that point."""
    value: Any

    def __init__(self, value: Any) -> None:
        self.value = value

    def __set_name__(self, owner: Type["_LSPEnum"], name: str) -> None:
        full_member = owner._create_member(self.value)
        setattr(owner, name, full_member)


class AllowCustomValues:
    """Marker class to indicate to _LSPEnumMeta that custom values are allowed."""
    pass

class _LSPEnumMeta(type):

    def __new__(cls, name: str, bases: Tuple[type, ...], classdict: Dict[str, Any]) -> type:
        value_to_member = {}

        for (key, value) in classdict.items():
            if _is_dunder(key) or _is_descriptor(value):
                continue
            classdict[key] = _LSPEnumProtoMember(value)

        classdict["_value_to_member"] = value_to_member
        classdict["_allow_custom_values"] = AllowCustomValues in bases

        return super().__new__(cls, name, bases, classdict)


T = TypeVar("T", bound="_LSPEnum")

class _LSPEnum(metaclass=_LSPEnumMeta):
    value: Any
    _initialized: ClassVar[bool]

    def __new__(cls: Type[T], value: Any) -> T:
        if out := cls._value_to_member.get(value):
            return out
        elif cls._allow_custom_values:
            return cls._create_member(value)
        else:
            raise LSPEnumException(value)


    @classmethod
    def _create_member(cls: Type[T], value: Any) -> T:
        new_member = super().__new__(cls)
        new_member.__init__(value)
        cls._value_to_member[value] = new_member
        return new_member


    def __init__(self, value: Any) -> None:
        self.value = value


U = TypeVar("U")

# This needs to be a seperate class, because a type bound cannot
# contain generic type arguments.
class TypedLSPEnum(Generic[U], _LSPEnum):
    value: U

    def __new__(cls: Type[T], value: U) -> T:
        return super().__new__(cls, value)

    def __init__(self, value: U) -> None:
        self.value = value
