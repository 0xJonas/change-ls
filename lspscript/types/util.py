from typing import Any, Callable, List, Literal, Mapping, MutableSequence, Optional, Sequence, Tuple, Type, TypeVar, Union

JSON_VALUE = Union[int, float, bool, str, Sequence['JSON_VALUE'], Mapping[str, 'JSON_VALUE'], None]
JSON_TYPE_NAME = Literal["number (int)", "number (real)", "bool", "string", "array", "object", "null"]


class LSPKeyNotFoundException(Exception):
    key: str

    def __init__(self, key: str) -> None:
        self.key = key

    def __str__(self) -> str:
        return f"Expected key {self.key}"


class LSPTypeException(Exception):
    expected_type: JSON_TYPE_NAME
    key: Optional[str]

    def __init__(self, expected_type: JSON_TYPE_NAME, key: Optional[str] = None) -> None:
        self.expected_type = expected_type
        self.key = key

    def __str__(self) -> str:
        if self.key:
            return f"Key {self.key} is expected to be of type {self.expected_type}"
        else:
            return f"Expected type {self.expected_type}"


class LSPLiteralException(Exception):
    val: JSON_VALUE
    expected: JSON_VALUE

    def __init__(self, val: JSON_VALUE, expected: JSON_VALUE) -> None:
        self.val = val
        self.expected = expected

    def __str__(self) -> str:
        return f"Expected {self.expected}, found {self.val}"


T = TypeVar("T", bound=JSON_VALUE)


def _create_get_function(check_type: Type[T], json_type_name: JSON_TYPE_NAME, return_type: Type[T]) -> Callable[[Mapping[str, JSON_VALUE], str], T]:
    """Creates a function which returns the value of a field with type check_type.
    If the field is missing or the extracted value has the wrong type, an
    exception is raised."""
    def json_get(obj: Mapping[str, JSON_VALUE], key: str) -> return_type:
        try:
            val = obj[key]
            if not isinstance(val, check_type):
                raise LSPTypeException(json_type_name, key)
            return val
        except KeyError as e:
            raise LSPKeyNotFoundException(key) from e

    return json_get

def _create_get_optional_function(check_type: Type[T], json_type_name: JSON_TYPE_NAME, return_type: Type[T]) -> Callable[[Mapping[str, JSON_VALUE], str], Optional[T]]:
    """Creates a function which returns the value of a field with type check_type.
    If the field is missing, None is returned. If the field exists but its value has
    the wrong type, an exception is raised."""
    def json_get_optional(obj: Mapping[str, JSON_VALUE], key: str) -> Optional[return_type]:
        val = obj.get(key, None)
        if val is not None and not isinstance(val, check_type):
            raise LSPTypeException(json_type_name, key)
        return val

    return json_get_optional


def _create_assert_type_function(check_type: Type[T], json_type_name: JSON_TYPE_NAME, return_type: Type[T]) -> Callable[[JSON_VALUE], T]:
    def json_assert_type(val: JSON_VALUE) -> return_type:
        if not isinstance(val, check_type):
            raise LSPTypeException(json_type_name)
        else:
            return val

    return json_assert_type


json_get_int = _create_get_function(int, "number (int)", int)
json_get_float = _create_get_function(float, "number (real)", float)
json_get_bool = _create_get_function(bool, "bool", bool)
json_get_string = _create_get_function(str, "string", str)
json_get_array = _create_get_function(MutableSequence, "array", Sequence[JSON_VALUE]) # use MutableSequence so that a str is not classified as an array
json_get_object = _create_get_function(Mapping, "object", Mapping[str, JSON_VALUE])
json_get_null = _create_get_function(type(None), "null", type(None))

json_get_optional_int = _create_get_optional_function(int, "number (int)", int)
json_get_optional_float = _create_get_optional_function(float, "number (real)", float)
json_get_optional_bool = _create_get_optional_function(bool, "bool", bool)
json_get_optional_string = _create_get_optional_function(str, "string", str)
json_get_optional_array = _create_get_optional_function(MutableSequence, "array", Sequence[JSON_VALUE]) # use MutableSequence so that a str is not classified as an array
json_get_optional_object = _create_get_optional_function(Mapping, "object", Mapping[str, JSON_VALUE])
json_get_optional_null = _create_get_optional_function(type(None), "null", type(None))

json_assert_type_int = _create_assert_type_function(int, "number (int)", int)
json_assert_type_float = _create_assert_type_function(float, "number (real)", float)
json_assert_type_bool = _create_assert_type_function(bool, "bool", bool)
json_assert_type_string = _create_assert_type_function(str, "string", str)
json_assert_type_array = _create_assert_type_function(MutableSequence, "array", Sequence[JSON_VALUE]) # use MutableSequence so that a str is not classified as an array
json_assert_type_object = _create_assert_type_function(Mapping, "object", Mapping[str, JSON_VALUE])
json_assert_type_null = _create_assert_type_function(type(None), "null", type(None))


def match_string(val: str, expected: str) -> str:
    if val == expected:
        return val
    else:
        raise LSPLiteralException(val, expected)


def match_integer(val: int, expected: int) -> int:
    if val == expected:
        return val
    else:
        raise LSPLiteralException(val, expected)


def match_bool(val: bool, expected: bool) -> bool:
    if val == expected:
        return val
    else:
        raise LSPLiteralException(val, expected)


def parse_or_type(val: JSON_VALUE, variant_parsers: Tuple[Callable[[JSON_VALUE], Any], ...]) -> Any:
    errors: List[Exception] = []
    for parse in variant_parsers:
        try:
            res = parse(val)
            return res
        except Exception as e:
            errors.append(e)
    # All parsers raised an exception
    raise errors[0] # TODO other exception?


def write_or_type(val: Any, type_tests: Tuple[Callable[[Any], bool], ...], variant_writers: Tuple[Callable[[Any], JSON_VALUE], ...]) -> JSON_VALUE:
    for t, w in zip(type_tests, variant_writers):
        if t(val):
            return w(val)
    assert False # TODO exception
