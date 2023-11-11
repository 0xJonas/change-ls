from dataclasses import dataclass
from typing import Literal, Mapping, Optional, Tuple, Union

from gen.schema.util import (
    JSON_VALUE,
    LSPMetaModelException,
    json_get_array_of_objects,
    json_get_bool,
    json_get_int,
    json_get_object,
    json_get_optional_bool,
    json_get_optional_string,
    json_get_string,
)


@dataclass(frozen=True)
class BaseType:
    """Represents a base type like `string` or `DocumentUri`."""

    name: Literal[
        "URI",
        "DocumentUri",
        "integer",
        "uinteger",
        "decimal",
        "RegExp",
        "string",
        "boolean",
        "null",
    ]

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "BaseType":
        name_json = json_get_string(obj, "name")
        if name_json == "URI":
            return BaseType("URI")
        elif name_json == "DocumentUri":
            return cls("DocumentUri")
        elif name_json == "integer":
            return cls("integer")
        elif name_json == "uinteger":
            return cls("uinteger")
        elif name_json == "decimal":
            return cls("decimal")
        elif name_json == "RegExp":
            return cls("RegExp")
        elif name_json == "string":
            return cls("string")
        elif name_json == "boolean":
            return cls("boolean")
        elif name_json == "null":
            return cls("null")
        else:
            raise LSPMetaModelException(
                f'Expected "name" to be one of "URI", "DocumentUri", "integer", "uinteger", "decimal", "RegExp", "string", "boolean" or "null", found {name_json}'
            )


@dataclass(frozen=True)
class ReferenceType:
    """Represents a reference to another type (e.g. `TextDocument`). This is either a `Structure`, a `Enumeration` or a `TypeAlias` in the same meta model."""

    name: str

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "ReferenceType":
        return cls(json_get_string(obj, "name"))


@dataclass(frozen=True)
class ArrayType:
    """Represents an array type (e.g. `TextDocument[]`)."""

    element: "AnyType"

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "ArrayType":
        element_json = json_get_object(obj, "element")
        return cls(AnyType.from_json(element_json))


@dataclass(frozen=True)
class MapKeyType:
    """Represents a type that can be used as a key in a map type."""

    name: Literal["URI", "DocumentUri", "string", "integer"]

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "MapKeyType":
        name_json = json_get_string(obj, "name")
        if name_json == "URI":
            return cls("URI")
        elif name_json == "DocumentUri":
            return cls("DocumentUri")
        elif name_json == "string":
            return cls("string")
        elif name_json == "integer":
            return cls("integer")
        else:
            raise LSPMetaModelException(
                f'Expected "name" to be one of "URI", "DocumentUri", "string" or "integer", found {name_json}'
            )


@dataclass(frozen=True)
class MapType:
    """Represents a JSON object map (e.g. `interface Map<K extends string | integer, V> { [key: K] => V; }`)."""

    key: Union[MapKeyType, ReferenceType]
    value: "AnyType"

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "MapType":
        key_json = json_get_object(obj, "key")
        key_kind = json_get_string(key_json, "kind")
        if key_kind == "base":
            key = MapKeyType.from_json(key_json)
        elif key_kind == "reference":
            key = ReferenceType.from_json(key_json)
        else:
            raise LSPMetaModelException(
                f'Expected "kind" to be one of "base" or "reference, found {key_kind}'
            )

        value_json = json_get_object(obj, "value")
        return cls(key, AnyType.from_json(value_json))


@dataclass(frozen=True)
class AndType:
    """Represents an `and`type (e.g. TextDocumentParams & WorkDoneProgressParams`)."""

    items: Tuple["AnyType", ...]

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "AndType":
        items_json = json_get_array_of_objects(obj, "items")
        items = tuple(AnyType.from_json(i) for i in items_json)
        return cls(items)


@dataclass(frozen=True)
class OrType:
    """Represents an `or` type (e.g. `Location | LocationLink`)."""

    items: Tuple["AnyType", ...]

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "OrType":
        items_json = json_get_array_of_objects(obj, "items")
        items = tuple(AnyType.from_json(i) for i in items_json)
        return cls(items)


@dataclass(frozen=True)
class TupleType:
    """Represents a `tuple` type (e.g. `[integer, integer]`)."""

    items: Tuple["AnyType", ...]

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "TupleType":
        items_json = json_get_array_of_objects(obj, "items")
        items = tuple(AnyType.from_json(i) for i in items_json)
        return cls(items)


@dataclass(frozen=True)
class Property:
    """Represents an object property."""

    documentation: Optional[str]
    name: str
    optional: Optional[bool]
    proposed: Optional[bool]
    since: Optional[str]
    type: "AnyType"

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "Property":
        documentation = json_get_optional_string(obj, "documentation")
        name = json_get_string(obj, "name")
        optional = json_get_optional_bool(obj, "optional")
        proposed = json_get_optional_bool(obj, "proposed")
        since = json_get_optional_string(obj, "since")
        type = AnyType.from_json(json_get_object(obj, "type"))
        return cls(documentation, name, optional, proposed, since, type)


@dataclass(frozen=True)
class StructureLiteral:
    """Defines an unnamed structure of an object literal."""

    documentation: Optional[str]
    properties: Tuple[Property, ...]
    proposed: Optional[bool]
    since: Optional[str]

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "StructureLiteral":
        documentation = json_get_optional_string(obj, "documentation")
        proposed = json_get_optional_bool(obj, "proposed")
        since = json_get_optional_string(obj, "since")

        properties_json = json_get_array_of_objects(obj, "properties")
        properties = tuple(Property.from_json(p) for p in properties_json)

        return cls(documentation, properties, proposed, since)


@dataclass(frozen=True)
class StructureLiteralType:
    """Represents a literal structure (e.g. `property: { start: uinteger; end: uinteger; }`)."""

    value: StructureLiteral

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "StructureLiteralType":
        value_json = json_get_object(obj, "value")
        return cls(StructureLiteral.from_json(value_json))


@dataclass(frozen=True)
class StringLiteralType:
    """Represents a string literal type (e.g. `kind: 'rename'`)."""

    value: str

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "StringLiteralType":
        return cls(json_get_string(obj, "value"))

    def generate_read(self, source: str) -> str:
        return f"""if json_get_string(obj, "{source}") != {self.value}:
    raise LSPException("stringLiteral does not match")
"""


@dataclass(frozen=True)
class IntegerLiteralType:
    """Represents an integer literal type (e.g. `kind: 1`)."""

    value: int

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "IntegerLiteralType":
        return cls(json_get_int(obj, "value"))

    def generate_read(self, source: str) -> str:
        return f"""if json_get_number(obj, "{source}") != {self.value}:
    raise LSPException("integerLiteral does not match")
"""


@dataclass(frozen=True)
class BooleanLiteralType:
    """Represents a boolean literal type (e.g. `kind: true`)."""

    value: bool

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "BooleanLiteralType":
        return cls(json_get_bool(obj, "value"))

    def generate_read(self, source: str) -> str:
        return f"""if json_get_boolean(obj, "{source}") != {self.value}:
    raise LSPException("booleanLiteral does not match")
"""


AnyTypeKind = Literal[
    "base",
    "reference",
    "array",
    "map",
    "and",
    "or",
    "tuple",
    "literal",
    "stringLiteral",
    "integerLiteral",
    "booleanLiteral",
]


@dataclass(frozen=True)
class AnyType:
    kind: AnyTypeKind
    content: Union[
        BaseType,
        ReferenceType,
        ArrayType,
        MapType,
        AndType,
        OrType,
        TupleType,
        StructureLiteralType,
        StringLiteralType,
        IntegerLiteralType,
        BooleanLiteralType,
    ]

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "AnyType":
        kind_json = json_get_string(obj, "kind")
        if kind_json == "base":
            return AnyType("base", BaseType.from_json(obj))
        elif kind_json == "reference":
            return AnyType("reference", ReferenceType.from_json(obj))
        elif kind_json == "array":
            return AnyType("array", ArrayType.from_json(obj))
        elif kind_json == "map":
            return AnyType("map", MapType.from_json(obj))
        elif kind_json == "and":
            return AnyType("and", AndType.from_json(obj))
        elif kind_json == "or":
            return AnyType("or", OrType.from_json(obj))
        elif kind_json == "tuple":
            return AnyType("tuple", TupleType.from_json(obj))
        elif kind_json == "literal":
            return AnyType("literal", StructureLiteralType.from_json(obj))
        elif kind_json == "stringLiteral":
            return AnyType("stringLiteral", StringLiteralType.from_json(obj))
        elif kind_json == "integerLiteral":
            return AnyType("integerLiteral", IntegerLiteralType.from_json(obj))
        elif kind_json == "booleanLiteral":
            return AnyType("booleanLiteral", BooleanLiteralType.from_json(obj))
        else:
            raise LSPMetaModelException(
                f'Expected "kind" to be one of "base", "reference", "array", "map", "and", "or", "tuple", "literal", "stringLiteral", "integerLiteral" or "booleanLiteral", found {kind_json}'
            )
