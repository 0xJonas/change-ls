from typing import Any, Dict
from gen.schema.anytype import AnyType
from gen.schema.types import MetaModel, ReferenceType
from gen.generator import Generator, LSPGeneratorException, ReferenceResolver
import pytest

from gen.static.util import LSPLiteralException, LSPTypeException


def test_reference_resolver_resolves_reference() -> None:
    model = MetaModel.from_json({
        "enumerations": [
            {
                "name": "Enumeration1",
                "type": {
                    "kind": "base",
                    "name": "integer"
                },
                "values": [
                    {
                        "name": "value1",
                        "value": 1
                    },
                    {
                        "name": "value2",
                        "value": 2
                    }
                ]
            }
        ],
        "notifications": [],
        "requests": [],
        "structures": [
            {
                "name": "Structure1",
                "properties": []
            }
        ],
        "typeAliases": [],
    })

    resolver = ReferenceResolver(model)

    res1 = resolver.resolve_reference(ReferenceType("Structure1"))
    assert res1 is model.structures[0]

    res2 = resolver.resolve_reference(ReferenceType("Enumeration1"))
    assert res2 is model.enumerations[0]

    res3 = resolver.resolve_reference(ReferenceType("DoesNotExist"))
    assert res3 == None


def test_reference_resolver_resolves_typealias() -> None:
    model = MetaModel.from_json({
        "enumerations": [],
        "notifications": [],
        "requests": [],
        "structures": [
            {
                "name": "Structure1",
                "properties": []
            }
        ],
        "typeAliases": [
            {
                "name": "TypeAlias1",
                "type": {
                    "kind": "reference",
                    "name": "Structure1"
                }
            }
        ],
    })

    resolver = ReferenceResolver(model)

    res1 = resolver.resolve_reference(ReferenceType("TypeAlias1"))
    assert res1 is model.structures[0]


def test_reference_resolver_detects_circular_references() -> None:
    model = MetaModel.from_json({
        "enumerations": [],
        "notifications": [],
        "requests": [],
        "structures": [],
        "typeAliases": [
            {
                "name": "TypeAlias1",
                "type": {
                    "kind": "reference",
                    "name": "TypeAlias2"
                }
            },
            {
                "name": "TypeAlias2",
                "type": {
                    "kind": "reference",
                    "name": "TypeAlias1"
                }
            }
        ],
    })

    resolver = ReferenceResolver(model)

    with pytest.raises(LSPGeneratorException):
        resolver.resolve_reference(ReferenceType("TypeAlias1"))


def get_empty_meta_model() -> MetaModel:
    return MetaModel.from_json({
        "enumerations": [],
        "notifications": [],
        "requests": [],
        "structures": [],
        "typeAliases": []
    })


def get_test_default_names() -> Dict[str, Any]:
    import gen.static.util as util
    names = util.__dict__.copy()
    exec("""\
from dataclasses import dataclass
from typing import Dict, List, Tuple, Union
    """, names)

    return names


def test_generator_generate_parse_expression_anytype_or() -> None:
    model = get_empty_meta_model()
    generator = Generator(model)

    anytype = AnyType.from_json({
        "kind": "or",
        "items": [
            {
                "kind": "base",
                "name": "integer"
            },
            {
                "kind": "array",
                "element": {
                    "kind": "base",
                    "name": "integer"
                }
            }
        ]
    })

    import gen.static.util as util

    expr1 = generator.generate_parse_expression(anytype, '5')
    res1 = eval(expr1, util.__dict__)
    assert res1 == 5

    expr2 = generator.generate_parse_expression(anytype, '[1, 2, 3, 4]')
    res2 = eval(expr2, util.__dict__)
    assert res2 == [1, 2, 3, 4]

    with pytest.raises(LSPTypeException):
        expr3 = generator.generate_parse_expression(anytype, '"Hello"')
        eval(expr3, util.__dict__)


@pytest.mark.skip()
def test_generator_generate_parse_expression_anytype_literal() -> None:
    model = MetaModel.from_json({
        "enumerations": (),
        "notifications": (),
        "requests": (),
        "structures": (),
        "typeAliases": (
            {
                "name": "Test",
                "type": {
                    "kind": "literal",
                    "value": {
                        "properties": (
                            {
                                "name": "test1",
                                "type": {
                                    "kind": "base",
                                    "name": "string"
                                }
                            },
                        )
                    }
                }
            },
        )
    })
    literal = model.type_aliases[0].type
    generator = Generator(model)

    generator.generate_anonymus_structure_definitions()

    expr = generator.generate_parse_expression(literal, '{ "test1": "Hello" }')

    import gen.static.util as util
    from dataclasses import dataclass
    names = util.__dict__.copy()
    names["dataclass"] = dataclass

    # Process class definition
    exec(generator._anonymus_structures[0], names)

    # Parse expression using class definition
    res = eval(expr, names)

    assert res.test1 == "Hello"


def test_generator_parse_anytypes() -> None:
    model = MetaModel.from_json({
        "enumerations": [],
        "notifications": [],
        "requests": [],
        "structures": [
            {
                "name": "TestBaseString",
                "properties": [
                    {
                        "name": "test",
                        "type": {
                            "kind": "base",
                            "name": "string"
                        }
                    }
                ]
            },
            {
                "name": "TestBaseInteger",
                "properties": [
                    {
                        "name": "test",
                        "type": {
                            "kind": "base",
                            "name": "integer"
                        }
                    }
                ]
            },
            {
                "name": "TestBaseBoolean",
                "properties": [
                    {
                        "name": "test",
                        "type": {
                            "kind": "base",
                            "name": "boolean"
                        }
                    }
                ]
            },
            {
                "name": "TestArray",
                "properties": [
                    {
                        "name": "test",
                        "type": {
                            "kind": "array",
                            "element": {
                                "kind": "base",
                                "name": "integer"
                            }
                        }
                    }
                ]
            },
            {
                "name": "TestMap",
                "properties": [
                    {
                        "name": "test",
                        "type": {
                            "kind": "map",
                            "key": {
                                "kind": "base",
                                "name": "string"
                            },
                            "value": {
                                "kind": "base",
                                "name": "boolean"
                            }
                        }
                    }
                ]
            },
            {
                "name": "TestTuple",
                "properties": [
                    {
                        "name": "test",
                        "type": {
                            "kind": "tuple",
                            "items": [
                                {
                                    "kind": "base",
                                    "name": "string"
                                },
                                {
                                    "kind": "array",
                                    "element": {
                                        "kind": "base",
                                        "name": "integer"
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        ],
        "typeAliases": []
    })

    generator = Generator(model)

    names = get_test_default_names()

    exec(generator.generate_structure_definition(model.structures[0]), names)
    exec(generator.generate_structure_definition(model.structures[1]), names)
    exec(generator.generate_structure_definition(model.structures[2]), names)
    exec(generator.generate_structure_definition(model.structures[3]), names)
    exec(generator.generate_structure_definition(model.structures[4]), names)
    exec(generator.generate_structure_definition(model.structures[5]), names)

    res1 = eval("TestBaseString.from_json({ 'test': 'test' })", names)
    assert res1.test == "test"

    res2 = eval("TestBaseInteger.from_json({ 'test': 15 })", names)
    assert res2.test == 15

    res3 = eval("TestBaseBoolean.from_json({ 'test': True })", names)
    assert res3.test == True

    res4 = eval("TestArray.from_json({ 'test': [2, 4, 6, 8, 10] })", names)
    assert res4.test == [2, 4, 6, 8, 10]

    res5 = eval("TestMap.from_json({ 'test': { 'test1': True, 'test2': False }})", names)
    assert res5.test == { "test1": True, "test2": False }

    res5 = eval("TestTuple.from_json({ 'test': ['test', [5, 10]] })", names)
    assert res5.test == ("test", [5, 10])

    with pytest.raises(LSPTypeException):
        eval("TestBaseString.from_json({ 'test': 5 })", names)

    with pytest.raises(LSPTypeException):
        eval("TestBaseInteger.from_json({ 'test': None })", names)

    with pytest.raises(LSPTypeException):
        eval("TestBaseBoolean.from_json({ 'test': 'hello' })", names)

    with pytest.raises(LSPTypeException):
        eval("TestArray.from_json({ 'test': ['a', 'b', 'c'] })", names)

    with pytest.raises(LSPTypeException):
        eval("TestMap.from_json({ 'test': { 'test1': 1, 'test2': 0 }})", names)

    with pytest.raises(LSPTypeException):
        eval("TestTuple.from_json({ 'test': ['test', 7] })", names)


def test_generator_parse_anytypes_matching() -> None:
    model = MetaModel.from_json({
        "enumerations": [],
        "notifications": [],
        "requests": [],
        "structures": [
             {
                "name": "TestStringLiteral",
                "properties": [
                    {
                        "name": "test",
                        "type": {
                            "kind": "stringLiteral",
                            "value": "test123"
                        }
                    }
                ]
             },
             {
                "name": "TestIntegerLiteral",
                "properties": [
                    {
                        "name": "test",
                        "type": {
                            "kind": "integerLiteral",
                            "value": 4096
                        }
                    }
                ]
             },
             {
                "name": "TestBooleanLiteral",
                "properties": [
                    {
                        "name": "test",
                        "type": {
                            "kind": "booleanLiteral",
                            "value": True
                        }
                    }
                ]
             }
        ],
        "typeAliases": [],
    })
    generator = Generator(model)

    names = get_test_default_names()

    exec(generator.generate_structure_definition(model.structures[0]), names)
    exec(generator.generate_structure_definition(model.structures[1]), names)
    exec(generator.generate_structure_definition(model.structures[2]), names)

    res1 = eval("TestStringLiteral.from_json({ 'test': 'test123' })", names)
    assert res1.test == "test123"

    res2 = eval("TestIntegerLiteral.from_json({ 'test': 4096 })", names)
    assert res2.test == 4096

    res3 = eval("TestBooleanLiteral.from_json({ 'test': True })", names)
    assert res3.test == True

    with pytest.raises(LSPLiteralException):
        eval("TestStringLiteral.from_json({ 'test': 'wrong' })", names)

    with pytest.raises(LSPLiteralException):
        eval("TestIntegerLiteral.from_json({ 'test': 10 })", names)

    with pytest.raises(LSPLiteralException):
        eval("TestBooleanLiteral.from_json({ 'test': False })", names)


def test_generator_generate_structure_definition() -> None:
    model = MetaModel.from_json({
        "enumerations": [],
        "notifications": [],
        "requests": [],
        "structures": [
            {
                "name": "Test1",
                "extends": [
                    {
                        "kind": "reference",
                        "name": "Test2"
                    }
                ],
                "mixins": [
                    {
                        "kind": "reference",
                        "name": "Test3"
                    }
                ],
                "properties": [
                    {
                        "name": "test1",
                        "type": {
                            "kind": "base",
                            "name": "string"
                        }
                    }
                ]
            },
            {
                "name": "Test2",
                "properties": [
                    {
                        "name": "test2",
                        "type": {
                            "kind": "base",
                            "name": "integer"
                        }
                    }
                ]
            },
            {
                "name": "Test3",
                "properties": [
                    {
                        "name": "test3",
                        "type": {
                            "kind": "base",
                            "name": "boolean"
                        }
                    }
                ]
            }
        ],
        "typeAliases": []
    })

    generator = Generator(model)

    import gen.static.util as util
    from dataclasses import dataclass
    names = util.__dict__.copy()
    names["dataclass"] = dataclass

    # Process class definition
    exec(generator.generate_structure_definition(model.structures[2]), names)
    exec(generator.generate_structure_definition(model.structures[1]), names)
    exec(generator.generate_structure_definition(model.structures[0]), names)

    assert eval("issubclass(Test1, Test2)", names)

    res = eval("Test1.from_json({ 'test1': 'Hello', 'test2': 10, 'test3': True })", names)
    assert res.test1 == 'Hello'
    assert res.test2 == 10
    assert res.test3 == True


def test_generator_get_referenced_definition_anytype() -> None:
    model = MetaModel.from_json({
        "enumerations": [],
        "notifications": [],
        "requests": [],
        "structures": [
            {
                "name": "Root",
                "properties": [
                    {
                        "name": "testReference",
                        "type": {
                            "kind": "reference",
                            "name": "Test1"
                        }
                    },
                    {
                        "name": "testArray",
                        "type": {
                            "kind": "array",
                            "element": {
                                "kind": "reference",
                                "name": "Test2"
                            }
                        }
                    },
                    {
                        "name": "testMap",
                        "type": {
                            "kind": "map",
                            "key": {
                                "kind": "reference",
                                "name": "TestTypeAlias"
                            },
                            "value": {
                                "kind": "reference",
                                "name": "Test3"
                            }
                        }
                    },
                    {
                        "name": "testOr",
                        "type": {
                            "kind": "or",
                            "items": [
                                {
                                    "kind": "reference",
                                    "name": "Test4"
                                }
                            ]
                        }
                    },
                    {
                        "name": "testTuple",
                        "type": {
                            "kind": "tuple",
                            "items": [
                                {
                                    "kind": "reference",
                                    "name": "Test5"
                                }
                            ]
                        }
                    },
                ]
            },
            {
                "name": "Test1",
                "properties": []
            },
            {
                "name": "Test2",
                "properties": []
            },
            {
                "name": "Test3",
                "properties": []
            },
            {
                "name": "Test4",
                "properties": []
            },
            {
                "name": "Test5",
                "properties": []
            },
            {
                "name": "ShouldNotShowUp",
                "properties": []
            },
        ],
        "typeAliases": [
            {
                "name": "TestTypeAlias",
                "type": {
                    "kind": "base",
                    "name": "string"
                }
            }
        ]
    })
    generator = Generator(model)

    res = generator.get_referenced_definitions(model.structures[0])
    assert "Test1" in res
    assert "Test2" in res
    assert "Test3" in res
    assert "Test4" in res
    assert "Test5" in res
    assert "TestTypeAlias" in res
    assert "ShouldNotShowUp" not in res
