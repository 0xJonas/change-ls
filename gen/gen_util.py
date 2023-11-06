from keyword import iskeyword
from typing import Dict, List, Union

from gen.schema.types import Enumeration, Structure, TypeAlias
from gen.schema.util import JSON_TYPE_NAME


class LSPGeneratorException(Exception):
    message: str

    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


def indent(text: str) -> str:
    return "\n".join(["    " + l for l in text.splitlines()])


def dedent_ignore_empty(text: str) -> str:
    min_indentation = 1 << 31
    lines = text.splitlines(keepends=False)
    for line in lines:
        if len(line) == 0:
            continue
        for i, c in enumerate(line):
            if c != " ":
                min_indentation = min(min_indentation, i)
                break

    return "\n".join(
        (
            line[min_indentation:] if len(line) >= min_indentation else line
            for line in text.splitlines()
        )
    )


def generate_documentation_comment(documentation: str) -> str:
    out: List[str] = []
    for l in documentation.splitlines():
        l = l.replace("\\", "\\\\")
        l = "# " + l
        out.append(l)
    return "\n".join(out) + "\n"


def escape_keyword(name: str) -> str:
    if iskeyword(name):
        return name + "_"
    else:
        return name


json_type_to_get_function: Dict[JSON_TYPE_NAME, str] = {
    "number (int)": "json_get_int",
    "number (real)": "json_get_float",
    "bool": "json_get_bool",
    "string": "json_get_string",
    "array": "json_get_array",
    "object": "json_get_object",
    "null": "json_get_null",
}

json_type_to_get_optional_function: Dict[JSON_TYPE_NAME, str] = {
    "number (int)": "json_get_optional_int",
    "number (real)": "json_get_optional_float",
    "bool": "json_get_optional_bool",
    "string": "json_get_optional_string",
    "array": "json_get_optional_array",
    "object": "json_get_optional_object",
    "null": "json_get_optional_null",
}

# Maps JSON types to their corresponding json_assert_type_* function in static.util
json_type_to_assert_function: Dict[JSON_TYPE_NAME, str] = {
    "number (int)": "json_assert_type_int",
    "number (real)": "json_assert_type_float",
    "bool": "json_assert_type_bool",
    "string": "json_assert_type_string",
    "array": "json_assert_type_array",
    "object": "json_assert_type_object",
    "null": "json_assert_type_null",
}


ref_target = Union[Enumeration, Structure, TypeAlias]
