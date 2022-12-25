from gen.schema.anytype import *
from gen.schema.types import *


def test_parse_enumeration() -> None:
    test_json1 = {
        "documentation": "A test Enumeration",
        "name": "Test",
        "proposed": False,
        "since": "0.1.0",
        "supportsCustomValues": False,
        "type": {
            "kind": "base",
            "name": "string"
        },
        "values": [
            {
                "documentation": "A test EnumerationEntry",
                "name": "Test1",
                "proposed": True,
                "since": "0.1.1",
                "value": "value1"
            },
            {
                "name": "Test2",
                "value": "value2"
            }
        ]
    }

    res1 = Enumeration.from_json(test_json1)
    assert res1 == Enumeration(
        "A test Enumeration",
        "Test",
        False,
        "0.1.0",
        False,
        EnumerationType("string"),
        (
            EnumerationEntry("A test EnumerationEntry", "Test1", True, "0.1.1", "value1"),
            EnumerationEntry(None, "Test2", None, None, "value2")
        )
    )

    test_json2 = {
        "name": "Test2",
        "type": {
            "kind": "base",
            "name": "integer"
        },
        "values": [
            {
                "name": "Test2_1",
                "value": 1
            }
        ]
    }

    res2 = Enumeration.from_json(test_json2)
    assert res2 == Enumeration(
        None, "Test2", None, None, None, EnumerationType("integer"), (EnumerationEntry(None, "Test2_1", None, None, 1),)
    )


def test_parse_notification() -> None:
    test_json1 = {
        "documentation": "A test Notification",
        "messageDirection": "clientToServer",
        "method": "test/test",
        "params": {
            "kind": "base",
            "name": "string"
        },
        "proposed": True,
        "registrationOptions": {
            "kind": "base",
            "name": "integer"
        },
        "since": "0.1.0"
    }

    res1 = Notification.from_json(test_json1)
    assert res1 == Notification(
        "A test Notification",
        "clientToServer",
        "test/test",
        AnyType("base", BaseType("string")),
        True,
        AnyType("base", BaseType("integer")),
        "0.1.0"
    )

    test_json2 = {
        "method": "test/test",
        "messageDirection": "serverToClient"
    }
    res2 = Notification.from_json(test_json2)
    assert res2 == Notification(None, "serverToClient", "test/test", None, None, None, None)

    test_json3 = {
        "method": "test/test",
        "messageDirection": "both",
        "params": [
            {
                "kind": "base",
                "name": "string"
            },
            {
                "kind": "base",
                "name": "integer"
            }
        ]
    }

    res3 = Notification.from_json(test_json3)
    assert res3 == Notification(None, "both", "test/test", (AnyType("base", BaseType("string")),
                                AnyType("base", BaseType("integer"))), None, None, None)


def test_parse_request() -> None:
    test_json1 = {
        "documentation": "A test Request",
        "errorData": {
            "kind": "base",
            "name": "string"
        },
        "messageDirection": "clientToServer",
        "method": "test/test",
        "params": {
            "kind": "base",
            "name": "string"
        },
        "partialResult": {
            "kind": "base",
            "name": "integer",
        },
        "proposed": False,
        "registrationOptions": {
            "kind": "base",
            "name": "boolean"
        },
        "registrationMethod": "testing",
        "result": {
            "kind": "base",
            "name": "URI"
        },
        "since": "0.1.0"
    }

    res1 = Request.from_json(test_json1)
    assert res1 == Request(
        "A test Request",
        AnyType("base", BaseType("string")),
        "clientToServer",
        "test/test",
        AnyType("base", BaseType("string")),
        AnyType("base", BaseType("integer")),
        False,
        AnyType("base", BaseType("boolean")),
        "testing",
        AnyType("base", BaseType("URI")),
        "0.1.0"
    )

    test_json2 = {
        "method": "test/test",
        "messageDirection": "serverToClient",
        "result": {
            "kind": "base",
            "name": "boolean"
        }
    }

    res2 = Request.from_json(test_json2)
    assert res2 == Request(None, None, "serverToClient", "test/test", None, None,
                           None, None, None, AnyType("base", BaseType("boolean")), None)

    test_json3 = {
        "method": "test/test",
        "messageDirection": "both",
        "params": [
            {
                "kind": "base",
                "name": "string"
            },
            {
                "kind": "base",
                "name": "integer"
            }
        ],
        "result": {
            "kind": "base",
            "name": "DocumentUri"
        }
    }

    res3 = Request.from_json(test_json3)
    assert res3 == Request(
        None,
        None,
        "both",
        "test/test",
        (AnyType("base", BaseType("string")), AnyType("base", BaseType("integer"))),
        None,
        None,
        None,
        None,
        AnyType("base", BaseType("DocumentUri")),
        None
    )


def test_parse_structure() -> None:
    test_json1 = {
        "documentation": "A test Structure",
        "extends": [
            {
                "kind": "base",
                "name": "string"
            }
        ],
        "mixins": [
            {
                "kind": "base",
                "name": "integer"
            }
        ],
        "name": "Test",
        "properties": [
            {
                "name": "test",
                "type": {
                    "kind": "base",
                    "name": "boolean"
                }
            }
        ],
        "proposed": True,
        "since": "0.1.0"
    }

    res1 = Structure.from_json(test_json1)
    assert res1 == Structure(
        "A test Structure",
        (AnyType("base", BaseType("string")),),
        (AnyType("base", BaseType("integer")),),
        "Test",
        (Property(None, "test", None, None, None, AnyType("base", BaseType("boolean"))),),
        True,
        "0.1.0"
    )

    test_json2 = {
        "name": "Test2",
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

    res2 = Structure.from_json(test_json2)
    assert res2 == Structure(
        None,
        None,
        None,
        "Test2",
        (Property(None, "test", None, None, None, AnyType("base", BaseType("boolean"))),),
        None,
        None
    )


def test_parse_typealias() -> None:
    test_json1 = {
        "documentation": "A test TypeAlias",
        "name": "Test",
        "proposed": False,
        "since": "0.1.0",
        "type": {
            "kind": "base",
            "name": "URI"
        }
    }

    res1 = TypeAlias.from_json(test_json1)
    assert res1 == TypeAlias(
        "A test TypeAlias",
        "Test",
        False,
        "0.1.0",
        AnyType("base", BaseType("URI"))
    )

    test_json2 = {
        "name": "Test2",
        "type": {
            "kind": "base",
            "name": "integer"
        }
    }

    res2 = TypeAlias.from_json(test_json2)
    assert res2 == TypeAlias(
        None,
        "Test2",
        None,
        None,
        AnyType("base", BaseType("integer"))
    )
