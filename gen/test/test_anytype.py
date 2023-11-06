from gen.schema.anytype import *
from pytest import raises


def test_parse_basetype() -> None:
    test_json1 = {"kind": "base", "name": "string"}
    res = AnyType.from_json(test_json1)
    assert res == AnyType("base", BaseType("string"))

    test_json2 = {"kind": "base", "name": "thing"}
    with raises(LSPMetaModelException):
        AnyType.from_json(test_json2)


def test_parse_referencetype() -> None:
    test_json = {"kind": "reference", "name": "test_ref"}
    res = AnyType.from_json(test_json)
    assert res == AnyType("reference", ReferenceType("test_ref"))


def test_parse_arraytype() -> None:
    test_json = {"kind": "array", "element": {"kind": "base", "name": "string"}}
    res = AnyType.from_json(test_json)
    assert res == AnyType("array", ArrayType(AnyType("base", BaseType("string"))))


def test_parse_maptype() -> None:
    test_json1 = {
        "kind": "map",
        "key": {"kind": "base", "name": "string"},
        "value": {"kind": "base", "name": "integer"},
    }
    res = AnyType.from_json(test_json1)
    assert res == AnyType(
        "map", MapType(MapKeyType("string"), AnyType("base", BaseType("integer")))
    )

    test_json2 = {
        "kind": "map",
        "key": {"kind": "base", "name": "thing"},  # wrong literal type here
        "value": {"kind": "base", "name": "integer"},
    }
    with raises(LSPMetaModelException):
        AnyType.from_json(test_json2)

    test_json3 = {
        "kind": "map",
        "key": {"kind": "reference", "name": "test_ref"},
        "value": {"kind": "base", "name": "integer"},
    }
    res = AnyType.from_json(test_json3)
    assert res == AnyType(
        "map", MapType(ReferenceType("test_ref"), AnyType("base", BaseType("integer")))
    )

    test_json4 = {
        "kind": "map",
        "key": {"kind": "stringLiteral", "value": "test"},
        "value": {"kind": "base", "name": "integer"},
    }
    with raises(LSPMetaModelException):
        AnyType.from_json(test_json4)


def test_parse_andtype() -> None:
    test_json = {
        "kind": "and",
        "items": [
            {"kind": "base", "name": "URI"},
            {"kind": "array", "element": {"kind": "base", "name": "string"}},
        ],
    }

    res = AnyType.from_json(test_json)
    assert res == AnyType(
        "and",
        AndType(
            (
                AnyType("base", BaseType("URI")),
                AnyType("array", ArrayType(AnyType("base", BaseType("string")))),
            )
        ),
    )


def test_parse_ortype() -> None:
    test_json = {
        "kind": "or",
        "items": [
            {"kind": "base", "name": "string"},
            {"kind": "array", "element": {"kind": "base", "name": "string"}},
        ],
    }

    res = AnyType.from_json(test_json)
    assert res == AnyType(
        "or",
        OrType(
            (
                AnyType("base", BaseType("string")),
                AnyType("array", ArrayType(AnyType("base", BaseType("string")))),
            )
        ),
    )


def test_parse_tupletype() -> None:
    test_json = {
        "kind": "tuple",
        "items": [
            {"kind": "base", "name": "string"},
            {"kind": "array", "element": {"kind": "base", "name": "string"}},
        ],
    }

    res = AnyType.from_json(test_json)
    assert res == AnyType(
        "tuple",
        TupleType(
            (
                AnyType("base", BaseType("string")),
                AnyType("array", ArrayType(AnyType("base", BaseType("string")))),
            )
        ),
    )


def test_parse_structureliteraltype() -> None:
    test_json1 = {
        "kind": "literal",
        "value": {
            "documentation": "A test StructureLiteral",
            "properties": [
                {
                    "documentation": "A test Property",
                    "name": "test",
                    "optional": False,
                    "proposed": False,
                    "since": "0.1.1",
                    "type": {"kind": "base", "name": "boolean"},
                }
            ],
            "proposed": True,
            "since": "0.1.0",
        },
    }

    res1 = AnyType.from_json(test_json1)
    assert res1 == AnyType(
        "literal",
        StructureLiteralType(
            StructureLiteral(
                "A test StructureLiteral",
                (
                    Property(
                        "A test Property",
                        "test",
                        False,
                        False,
                        "0.1.1",
                        AnyType("base", BaseType("boolean")),
                    ),
                ),
                True,
                "0.1.0",
            )
        ),
    )

    test_json2 = {
        "kind": "literal",
        "value": {"properties": [{"name": "test2", "type": {"kind": "base", "name": "boolean"}}]},
    }

    res2 = AnyType.from_json(test_json2)
    assert res2 == AnyType(
        "literal",
        StructureLiteralType(
            StructureLiteral(
                None,
                (Property(None, "test2", None, None, None, AnyType("base", BaseType("boolean"))),),
                None,
                None,
            )
        ),
    )


def test_parse_stringliteraltype() -> None:
    test_json = {"kind": "stringLiteral", "value": "test"}

    res = AnyType.from_json(test_json)
    assert res == AnyType("stringLiteral", StringLiteralType("test"))


def test_parse_integerliteraltype() -> None:
    test_json = {"kind": "integerLiteral", "value": 4096}

    res = AnyType.from_json(test_json)
    assert res == AnyType("integerLiteral", IntegerLiteralType(4096))


def test_parse_booleanliteraltype() -> None:
    test_json = {"kind": "booleanLiteral", "value": True}

    res = AnyType.from_json(test_json)
    assert res == AnyType("booleanLiteral", BooleanLiteralType(True))
