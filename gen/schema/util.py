from typing import Callable, List, Literal, Mapping, Optional, Sequence, Type, TypeVar, Union

JSON_VALUE = Union[int, float, bool, str, Sequence["JSON_VALUE"], Mapping[str, "JSON_VALUE"], None]
JSON_TYPE_NAME = Literal[
    "number (int)", "number (real)", "bool", "string", "array", "object", "null"
]


class LSPKeyNotFoundException(Exception):
    def __init__(self, key: str) -> None:
        self.key = key

    def __str__(self) -> str:
        return f"Expected key {self.key}"


class LSPTypeException(Exception):
    def __init__(self, key: str, expected_type: JSON_TYPE_NAME) -> None:
        self.key = key
        self.expected_type = expected_type

    def __str__(self) -> str:
        return f"Key {self.key} is expected to be of type {self.expected_type}"


class LSPMetaModelException(Exception):
    message: str

    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return "Error reading the meta model " + self.message


T = TypeVar("T", bound=JSON_VALUE)
R = TypeVar("R", bound=JSON_VALUE)


def _create_get_function(
    check_type: Type[T], json_type_name: JSON_TYPE_NAME, return_type: Type[R]
) -> Callable[[Mapping[str, JSON_VALUE], str], R]:
    """Creates a function which returns the value of a field with type check_type.
    If the field is missing or the extracted value has the wrong type, an
    exception is raised."""

    def json_get(obj: Mapping[str, JSON_VALUE], key: str) -> return_type:
        try:
            val = obj[key]
            if not isinstance(val, check_type):
                raise LSPTypeException(key, json_type_name)
            return val  # type: ignore
        except KeyError as e:
            raise LSPKeyNotFoundException(key) from e

    return json_get


def _create_get_optional_function(
    check_type: Type[T], json_type_name: JSON_TYPE_NAME, return_type: Type[R]
) -> Callable[[Mapping[str, JSON_VALUE], str], Optional[R]]:
    """Creates a function which returns the value of a field with type check_type.
    If the field is missing, None is returned. If the field exists but its value has
    the wrong type, an exception is raised."""

    def json_get_optional(obj: Mapping[str, JSON_VALUE], key: str) -> Optional[return_type]:
        val = obj.get(key, None)
        if val is not None and not isinstance(val, check_type):
            raise LSPTypeException(key, json_type_name)
        return val  # type: ignore

    return json_get_optional


def json_get_array_of_objects(
    obj: Mapping[str, JSON_VALUE], key: str
) -> List[Mapping[str, JSON_VALUE]]:
    l = json_get_array(obj, key)
    out: List[Mapping[str, JSON_VALUE]] = []
    for i in l:
        if not isinstance(i, Mapping):
            raise LSPMetaModelException("Expected object")
        out.append(i)
    return out


json_get_int = _create_get_function(int, "number (int)", int)
json_get_float = _create_get_function(float, "number (real)", float)
json_get_bool = _create_get_function(bool, "bool", bool)
json_get_string = _create_get_function(str, "string", str)
json_get_array = _create_get_function(Sequence, "array", Sequence[JSON_VALUE])
json_get_object = _create_get_function(Mapping, "object", Mapping[str, JSON_VALUE])
json_get_none = _create_get_function(type(None), "null", type(None))

json_get_optional_int = _create_get_optional_function(int, "number (int)", int)
json_get_optional_float = _create_get_optional_function(float, "number (real)", float)
json_get_optional_bool = _create_get_optional_function(bool, "bool", bool)
json_get_optional_string = _create_get_optional_function(str, "string", str)
json_get_optional_array = _create_get_optional_function(Sequence, "array", Sequence[JSON_VALUE])
json_get_optional_object = _create_get_optional_function(
    Mapping, "object", Mapping[str, JSON_VALUE]
)
json_get_optional_none = _create_get_optional_function(type(None), "null", type(None))
