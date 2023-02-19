from typing import Any, Dict

import pytest

from gen.generate_capabilities import FeatureInfo, generate_capabilities_py
from gen.generate_client_requests import generate_client_requests_py
from gen.generate_enumerations import generate_enumeration_definition
from gen.generate_structures import _get_referenced_definitions  # type: ignore
from gen.generate_structures import generate_structures_py
from gen.generator import Generator, LSPGeneratorException
from gen.schema.anytype import AnyType
from gen.schema.types import MetaModel, ReferenceType
from gen.schema.util import JSON_VALUE
from gen.static.lsp_enum import LSPEnumException
from gen.static.util import (LSPKeyNotFoundException, LSPLiteralException,
                             LSPTypeException)


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

    generator = Generator(model)

    res1 = generator.resolve_reference(ReferenceType("Structure1"))
    assert res1 is model.structures[0]

    res2 = generator.resolve_reference(ReferenceType("Enumeration1"))
    assert res2 is model.enumerations[0]

    res3 = generator.resolve_reference(ReferenceType("DoesNotExist"))
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

    generator = Generator(model)

    res1 = generator.resolve_reference(ReferenceType("TypeAlias1"))
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

    generator = Generator(model)

    with pytest.raises(LSPGeneratorException):
        generator.resolve_reference(ReferenceType("TypeAlias1"))


def get_empty_meta_model() -> MetaModel:
    return MetaModel.from_json({
        "enumerations": [],
        "notifications": [],
        "requests": [],
        "structures": [],
        "typeAliases": []
    })


def get_test_default_names() -> Dict[str, Any]:
    import gen.static.lsp_enum as lsp_enum
    import gen.static.util as util
    names = util.__dict__.copy()
    names.update(lsp_enum.__dict__)
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


def get_anytype_test_model() -> Dict[str, JSON_VALUE]:
    return {
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
                "name": "Part1",
                "properties": [
                    {
                        "name": "part1",
                        "type": {
                            "kind": "base",
                            "name": "integer"
                        }
                    }
                ]
            },
            {
                "name": "Part2",
                "properties": [
                    {
                        "name": "part2",
                        "type": {
                            "kind": "base",
                            "name": "boolean"
                        }
                    }
                ]
            },
            {
                "name": "TestAnd",
                "properties": [
                    {
                        "name": "test",
                        "type": {
                            "kind": "and",
                            "items": [
                                {
                                    "kind": "reference",
                                    "name": "Part1"
                                },
                                {
                                    "kind": "reference",
                                    "name": "Part2"
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "name": "TestOr",
                "properties": [
                    {
                        "name": "test",
                        "type": {
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
            },
            {
                "name": "TestLiteral",
                "properties": [
                    {
                        "name": "test",
                        "type": {
                            "kind": "literal",
                            "value": {
                                "properties": [
                                    {
                                        "name": "sub",
                                        "type": {
                                            "kind": "base",
                                            "name": "string"
                                        }
                                    }
                                ]
                            }
                        }
                    }
                ]
            },
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
        "typeAliases": []
    }


def test_generator_parse_anytypes() -> None:
    model = MetaModel.from_json(get_anytype_test_model())

    generator = Generator(model)

    names = get_test_default_names()

    structures_py = generate_structures_py(generator)
    # Skip imports, because they don't work inside the test
    exec(structures_py[structures_py.index("@dataclass"):], names)

    res1 = eval("TestBaseString.from_json({ 'test': 'test' })", names)
    assert res1.test == "test"
    assert res1.to_json() == {'test': 'test'}

    res2 = eval("TestBaseInteger.from_json({ 'test': 15 })", names)
    assert res2.test == 15
    assert res2.to_json() == {'test': 15}

    res3 = eval("TestBaseBoolean.from_json({ 'test': True })", names)
    assert res3.test == True
    assert res3.to_json() == {'test': True}

    res4 = eval("TestArray.from_json({ 'test': [2, 4, 6, 8, 10] })", names)
    assert res4.test == [2, 4, 6, 8, 10]
    assert res4.to_json() == {'test': [2, 4, 6, 8, 10]}

    res5 = eval("TestMap.from_json({ 'test': { 'test1': True, 'test2': False }})", names)
    assert res5.test == {"test1": True, "test2": False}
    assert res5.to_json() == {'test': {'test1': True, 'test2': False}}

    res6 = eval("TestAnd.from_json({ 'test': { 'part1': 3, 'part2': True } })", names)
    assert res6.test.part1 == 3
    assert res6.test.part2 == True
    assert res6.to_json() == {'test': {'part1': 3, 'part2': True}}

    res7 = eval("TestOr.from_json({ 'test': 16 })", names)
    assert res7.test == 16
    assert res7.to_json() == {'test': 16}
    res7 = eval("TestOr.from_json({ 'test': [2, 4, 8, 16] })", names)
    assert res7.test == [2, 4, 8, 16]
    assert res7.to_json() == {'test': [2, 4, 8, 16]}

    res8 = eval("TestTuple.from_json({ 'test': ['test', [5, 10]] })", names)
    assert res8.test == ("test", [5, 10])
    assert res8.to_json() == {'test': ['test', [5, 10]]}

    res9 = eval("TestLiteral.from_json({ 'test': { 'sub': 'Nested struct' } })", names)
    assert res9.test["sub"] == 'Nested struct'
    assert res9.to_json() == {'test': {'sub': 'Nested struct'}}

    res10 = eval("TestStringLiteral.from_json({ 'test': 'test123' })", names)
    assert res10.test == "test123"
    assert res10.to_json() == {'test': 'test123'}

    res11 = eval("TestIntegerLiteral.from_json({ 'test': 4096 })", names)
    assert res11.test == 4096
    assert res11.to_json() == {'test': 4096}

    res12 = eval("TestBooleanLiteral.from_json({ 'test': True })", names)
    assert res12.test == True
    assert res12.to_json() == {'test': True}

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

    with pytest.raises(LSPKeyNotFoundException):
        eval("TestAnd.from_json({ 'test': { 'part1': 0 } })", names)

    with pytest.raises(LSPTypeException):
        eval("TestOr.from_json({ 'test': { 'test': 'wrong' } })", names)

    with pytest.raises(LSPTypeException):
        eval("TestTuple.from_json({ 'test': ['a', 'b', 'c'] })", names)

    with pytest.raises(LSPTypeException):
        eval("TestTuple.from_json({ 'test': ['test', 7] })", names)

    with pytest.raises(LSPKeyNotFoundException):
        eval("TestLiteral.from_json({ 'test': { 'wrong': 'error' } })", names)

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
                    },
                    {
                        "name": "testopt",
                        "type": {
                            "kind": "base",
                            "name": "string"
                        },
                        "optional": True
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
            },
            {
                "name": "Test4",
                "properties": [
                    {
                        "name": "test4",
                        "type": {
                            "kind": "literal",
                            "value": {
                                "properties": []
                            }
                        },
                        "optional": True
                    }
                ]
            }
        ],
        "typeAliases": []
    })

    generator = Generator(model)

    names = get_test_default_names()

    structures_py = generate_structures_py(generator)
    # Skip imports, because they don't work inside the test
    exec(structures_py[structures_py.index("@dataclass"):], names)

    assert eval("issubclass(Test1, Test2)", names)

    res1 = eval("Test1.from_json({ 'test1': 'Hello', 'test2': 10, 'test3': True })", names)
    assert res1.test1 == 'Hello'
    assert res1.testopt is None
    assert res1.test2 == 10
    assert res1.test3 == True
    assert res1.to_json() == {'test1': 'Hello', 'test2': 10, 'test3': True}

    res2 = eval("Test1(test1='Hello', test2=10, test3=True)", names)
    assert res2.test1 == 'Hello'
    assert res2.testopt is None
    assert res2.test2 == 10
    assert res2.test3 == True

    res3 = eval("Test1(test1='Hello', test2=10, test3=True, testopt='Optional')", names)
    assert res3.testopt == "Optional"

    res4 = eval("Test4.from_json({ 'test4': {} })", names)
    assert res4.test4 == {}


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

    res = _get_referenced_definitions(generator, model.structures[0])
    assert model.structures[1] in res
    assert model.structures[2] in res
    assert model.structures[3] in res
    assert model.structures[4] in res
    assert model.structures[5] in res
    assert model.type_aliases[0] in res
    assert model.structures[6] not in res


def test_generator_generate_enum_definition() -> None:
    model = MetaModel.from_json({
        "enumerations": [
            {
                "name": "TestEnum1",
                "type": {
                    "kind": "base",
                    "name": "string"
                },
                "values": [
                    {
                        "name": "testStr1",
                        "value": "Hello"
                    },
                    {
                        "name": "testStr2",
                        "value": "World"
                    }
                ]
            },
            {
                "name": "TestEnum2",
                "type": {
                    "kind": "base",
                    "name": "integer"
                },
                "supportsCustomValues": True,
                "values": [
                    {
                        "name": "testInt1",
                        "value": 11
                    },
                    {
                        "name": "testInt2",
                        "value": 22
                    }
                ]
            }
        ],
        "notifications": [],
        "requests": [],
        "structures": [],
        "typeAliases": [],
    })
    generator = Generator(model)

    names = get_test_default_names()

    exec(generate_enumeration_definition(generator, model.enumerations[0]), names)
    exec(generate_enumeration_definition(generator, model.enumerations[1]), names)

    assert eval("TestEnum1.testStr1.value", names) == "Hello"
    assert eval("TestEnum1.testStr2.value", names) == "World"
    assert eval("TestEnum1('Hello') is TestEnum1.testStr1", names)
    assert eval("TestEnum2.testInt1.value", names) == 11
    assert eval("TestEnum2.testInt2.value", names) == 22
    assert eval("TestEnum2(33).value", names) == 33
    assert eval("TestEnum2(44) is TestEnum2(44)", names)

    with pytest.raises(LSPEnumException):
        eval("TestEnum1('Error')", names)


async def test_generator_client_requests() -> None:
    model = MetaModel.from_json({
        "enumerations": [],
        "notifications": [
            {
                "method": "test/clientNotification",
                "messageDirection": "clientToServer",
                "params": {
                    "kind": "base",
                    "name": "string"
                }
            },
            {
                "method": "test/serverNotification",
                "messageDirection": "serverToClient",
                "params": {
                    "kind": "base",
                    "name": "string"
                }
            },
            {
                "method": "test/bidirectionalNotification",
                "messageDirection": "both",
                "params": {
                    "kind": "base",
                    "name": "string"
                }
            }
        ],
        "requests": [
            {
                "method": "test/clientRequest",
                "messageDirection": "clientToServer",
                "params": {
                    "kind": "base",
                    "name": "string"
                },
                "result": {
                    "kind": "base",
                    "name": "string"
                }
            },
            {
                "method": "test/serverRequest",
                "messageDirection": "serverToClient",
                "params": {
                    "kind": "base",
                    "name": "string"
                },
                "result": {
                    "kind": "base",
                    "name": "string"
                }
            },
            {
                "method": "test/bidirectionalRequest",
                "messageDirection": "both",
                "params": {
                    "kind": "base",
                    "name": "string"
                },
                "result": {
                    "kind": "base",
                    "name": "string"
                }
            }
        ],
        "structures": [],
        "typeAliases": []
    })
    generator = Generator(model)

    names = get_test_default_names()

    client_requests_py = generate_client_requests_py(generator)
    client_requests_py = client_requests_py[client_requests_py.index("class"):]  # Skip imports

    exec("from abc import ABC, abstractmethod", names)
    exec(client_requests_py, names)
    exec("""\

class TestClient(ClientRequestsMixin, ServerRequestsMixin):

    async def send_request(self, method, params):
        return "send_request " + params

    async def send_notification(self, method, params):
        self.sentinel = "send_notification " + params

    def on_test_server_request(self, params: str) -> str:
        return "on_test_server_request " + params

    def on_test_bidirectional_request(self, params: str) -> str:
        return "on_test_bidirectional_request " + params

    def on_test_server_notification(self, params: str) -> None:
        self.sentinel = "on_test_server_notification " + params

    def on_test_bidirectional_notification(self, params: str) -> None:
        self.sentinel = "on_test_bidirectional_notification " + params
""", names)

    test_client = names["TestClient"]()
    assert "send_test_client_request" in dir(test_client)
    # server requests should not generate methods in the client.
    assert "send_test_server_request" not in dir(test_client)
    assert "send_test_bidirectional_request" in dir(test_client)

    res1 = await test_client.send_test_client_request("Hello1")
    assert res1 == "send_request Hello1"
    res2 = await test_client.send_test_bidirectional_request("Hello2")
    assert res2 == "send_request Hello2"

    await test_client.send_test_client_notification("Hello1")
    assert test_client.sentinel == "send_notification Hello1"
    await test_client.send_test_bidirectional_notification("Hello2")
    assert test_client.sentinel == "send_notification Hello2"

    response = test_client.dispatch_request("test/serverRequest", "Bye1")
    assert response == "on_test_server_request Bye1"
    response = test_client.dispatch_request("test/bidirectionalRequest", "Bye2")
    assert response == "on_test_bidirectional_request Bye2"

    test_client.dispatch_notification("test/serverNotification", "Bye1")
    assert test_client.sentinel == "on_test_server_notification Bye1"
    test_client.dispatch_notification("test/bidirectionalNotification", "Bye2")
    assert test_client.sentinel == "on_test_bidirectional_notification Bye2"


def test_generator_server_capabilities() -> None:
    model = MetaModel.from_json({
        "requests": [],
        "structures": [
            {
                "name": "DocumentSelector",
                "properties": []
            },
            {
                "name": "Registration",
                "properties": []
            },
            {
                "name": "TextDocumentRegistrationOptions",
                "properties": [
                    {
                        "name": "documentSelector",
                        "type": {
                            "kind": "reference",
                            "name": "DocumentSelector"
                        }
                    }
                ]
            },
            {
                "name": "StaticRegistrationOptions",
                "properties": [
                    {
                        "name": "id",
                        "type": {
                            "kind": "base",
                            "name": "string"
                        }
                    }
                ]
            },
            {
                "name": "ServerCapabilities",
                "properties": [
                    {
                        "name": "capability1",
                        "type": {
                            "kind": "reference",
                            "name": "TextDocumentRegistrationOptions"
                        }
                    },
                    {
                        "name": "capability2",
                        "type": {
                            "kind": "reference",
                            "name": "StaticRegistrationOptions"
                        }
                    },
                    {
                        "name": "capability3",
                        "type": {
                            "kind": "literal",
                            "value": {
                                "properties": [
                                    {
                                        "name": "test",
                                        "type": {
                                            "kind": "base",
                                            "name": "boolean"
                                        }
                                    }
                                ]
                            }
                        }
                    }
                ]
            }
        ],
        "enumerations": [],
        "notifications": [],
        "typeAliases": []
    })

    feature_infos = {
        "test/1": FeatureInfo("capability1"),
        "test/2": FeatureInfo("capability2"),
        "test/3": FeatureInfo("capability3.test"),
    }

    generator = Generator(model)

    names = get_test_default_names()

    structures_py = generate_structures_py(generator)
    # Skip imports, because they don't work inside the test
    exec(structures_py[structures_py.index("@dataclass"):], names)

    capabilities_py = generate_capabilities_py(generator, feature_infos)
    exec(capabilities_py[capabilities_py.index("@dataclass"):], names)

    server_capabilities = names["ServerCapabilities"].from_json({
        "capability1": {
            "documentSelector": {}
        },
        "capability2": {
            "id": "test_id"
        },
        "capability3": {
            "test": True
        }
    })
    registrations = names["server_capabilities_to_feature_registrations"](server_capabilities)

    assert len(registrations) == 3

    assert registrations[0].id is None
    assert registrations[0].method == "test/1"
    assert registrations[0].document_selector is not None

    assert registrations[1].id == "test_id"
    assert registrations[1].method == "test/2"
    assert registrations[1].document_selector is None

    assert registrations[2].id is None
    assert registrations[2].method == "test/3"
    assert registrations[2].document_selector is None


def test_generator_feature_registration() -> None:
    model = MetaModel.from_json({
        "requests": [
            {
                "method": "test/1",
                "params": [],
                "messageDirection": "clientToServer",
                "registrationOptions": {
                    "kind": "reference",
                    "name": "TextDocumentRegistrationOptions"
                },
                "result": {
                    "kind": "base",
                    "name": "null"
                }
            },
            {
                "method": "test/2",
                "params": [],
                "messageDirection": "clientToServer",
                "registrationOptions": {
                    "kind": "reference",
                    "name": "StaticRegistrationOptions"
                },
                "registrationMethod": "test",
                "result": {
                    "kind": "base",
                    "name": "null"
                }
            }
        ],
        "structures": [
            {
                "name": "DocumentSelector",
                "properties": []
            },
            {
                "name": "TextDocumentRegistrationOptions",
                "properties": [
                    {
                        "name": "documentSelector",
                        "type": {
                            "kind": "reference",
                            "name": "DocumentSelector"
                        }
                    }
                ]
            },
            {
                "name": "StaticRegistrationOptions",
                "properties": [
                    {
                        "name": "id",
                        "type": {
                            "kind": "base",
                            "name": "string"
                        }
                    }
                ]
            },
            {
                "name": "Registration",
                "properties": [
                    {
                        "name": "id",
                        "type": {
                            "kind": "base",
                            "name": "string"
                        },
                    },
                    {
                        "name": "method",
                        "type": {
                            "kind": "base",
                            "name": "string"
                        },
                    },
                    {
                        "name": "registerOptions",
                        "type": {
                            "kind": "reference",
                            "name": "LSPAny"
                        }
                    }
                ]
            },
            {
                "name": "ServerCapabilities",
                "properties": []
            }
        ],
        "typeAliases": [
            {
                "name": "LSPAny",
                "type": {
                    "kind": "or",
                    "items": [
                        {
                            "kind": "reference",
                            "name": "LSPObject"
                        },
                        {
                            "kind": "reference",
                            "name": "LSPArray"
                        },
                        {
                            "kind": "base",
                            "name": "string"
                        },
                        {
                            "kind": "base",
                            "name": "integer"
                        },
                        {
                            "kind": "base",
                            "name": "uinteger"
                        },
                        {
                            "kind": "base",
                            "name": "decimal"
                        },
                        {
                            "kind": "base",
                            "name": "boolean"
                        },
                        {
                            "kind": "base",
                            "name": "null"
                        }
                    ]
                }
            },
            {
                "name": "LSPArray",
                "type": {
                    "kind": "array",
                    "element": {
                        "kind": "reference",
                        "name": "LSPAny"
                    }
                }
            },
            {
                "name": "LSPObject",
                "type": {
                    "kind": "map",
                    "key": {
                        "kind": "base",
                        "name": "string"
                    },
                    "value": {
                        "kind": "reference",
                        "name": "LSPAny"
                    }
                }
            },
        ],
        "enumerations": [],
        "notifications": []
    })

    generator = Generator(model)

    names = get_test_default_names()

    structures_py = generate_structures_py(generator)
    # Skip imports, because they don't work inside the test
    exec(structures_py[structures_py.index("@dataclass"):], names)

    capabilities_py = generate_capabilities_py(generator, {})
    exec(capabilities_py[capabilities_py.index("@dataclass"):], names)

    registration1 = eval(
        "Registration(id='test_id/1', method='test/1', registerOptions={'documentSelector': {}})",
        names)
    res1 = names["registration_to_feature_registration"](registration1)
    assert res1.id == "test_id/1"
    assert res1.method == "test/1"
    assert res1.document_selector is not None

    registration2 = eval(
        "Registration(id='test_id/2', method='test', registerOptions={'id': 'test_id/3'})",
        names)
    res2 = names["registration_to_feature_registration"](registration2)
    assert res2.id == "test_id/3"  # !
    assert res2.method == "test"
    assert res2.document_selector is None
