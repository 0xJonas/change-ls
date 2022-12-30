from typing import List

from gen.gen_util import (dedent_ignore_empty, escape_keyword,
                          generate_documentation_comment, indent)
from gen.generator import Generator
from gen.schema.types import Enumeration


def generate_enumeration_definition(gen: Generator, enum: Enumeration) -> str:
    superclasses: List[str] = []
    if enum.type.name == "string":
        superclasses.append("TypedLSPEnum[str]")
    elif enum.type.name in ["integer", "uinteger"]:
        superclasses.append("TypedLSPEnum[int]")
    else:
        assert False # Broken Enumeration

    if enum.supports_custom_values:
        superclasses.append("AllowCustomValues")

    entry_definitions: List[str] = []
    for e in enum.values:
        if e.documentation:
            documentation = generate_documentation_comment(e.documentation)
        else:
            documentation = ""

        value = '\"' + str(e.value) + '\"' if enum.type.name == "string" else str(e.value)

        entry_definitions.append(f"{documentation}{escape_keyword(e.name)}: ClassVar[\"{enum.name}\"] = {value} # type: ignore")

    template = dedent_ignore_empty('''\
        class {name}({superclasses}):
            """
        {documentation}

            *Generated from the TypeScript documentation*
            """

        {body}''')

    return template.format(
            name=enum.name,
            superclasses=", ".join(superclasses),
            documentation=indent(enum.documentation if enum.documentation else ""),
            body=indent("\n\n".join(entry_definitions)))


def generate_enumerations_py(gen: Generator) -> str:
    template = dedent_ignore_empty("""\
        from typing import ClassVar
        from .lsp_enum import AllowCustomValues, TypedLSPEnum


        {definitions}
        """)

    return template.format(definitions="\n\n\n".join(generate_enumeration_definition(gen, e) for e in gen.get_meta_model().enumerations))