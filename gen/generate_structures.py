from textwrap import dedent
from typing import Any, Dict, List, Optional, Tuple, Union

from gen.gen_util import (LSPGeneratorException, dedent_ignore_empty,
                          escape_keyword, generate_documentation_comment,
                          indent, json_type_to_assert_function,
                          json_type_to_get_function,
                          json_type_to_get_optional_function, ref_target)
from gen.generator import Generator, LSPGeneratorException
from gen.schema.anytype import (AndType, AnyType, ArrayType, MapType, OrType,
                                Property, ReferenceType, StructureLiteral,
                                StructureLiteralType, TupleType)
from gen.schema.types import (Enumeration, Notification, Request, Structure,
                              TypeAlias)


def _generate_property_read_statement(gen: Generator, prop: Property, obj_name: str, anonymous_struct: bool = False, dest_name: str = "") -> str:
    """Generates a statement that reads the given `Property` from the JSON object `obj_name`."""
    if anonymous_struct:
        dest = f'{dest_name}["{prop.name}"]'
    else:
        dest = escape_keyword(prop.name)

    if prop.optional:
        if expected_json_type := gen.get_expected_json_type(prop.type):
            get_json_expr = json_type_to_get_optional_function[expected_json_type] + f'({obj_name}, "{prop.name}")'
        else:
            get_json_expr = f'{obj_name}.get("{prop.name}")'

        parse_expression = gen.generate_parse_expression(prop.type, f"{prop.name}_json")

        return dedent(f"""\
            if ({prop.name}_json := {get_json_expr}) is not None:
                {dest} = {parse_expression}
            else:
                {dest} = None""")

    else:
        if expected_json_type := gen.get_expected_json_type(prop.type):
            get_json_expr = json_type_to_get_function[expected_json_type] + f'({obj_name}, "{prop.name}")'
        else:
            get_json_expr = f'{obj_name}["{prop.name}"]'

        parse_expression = gen.generate_parse_expression(prop.type, get_json_expr)
        return f"{dest} = {parse_expression}"


def _generate_property_write_statement(gen: Generator, prop: Property, obj_name: str, anonymous_structure: bool = False, source_name: str = "") -> str:
    if anonymous_structure:
        if prop.optional:
            source = f'{source_name}.get("{prop.name}")'
        else:
            source = f'{source_name}["{prop.name}"]'
    else:
        source = "self." + escape_keyword(prop.name)

    write_statement = f'{obj_name}["{prop.name}"] = {gen.generate_write_expression(prop.type, source)}'
    if prop.optional:
        write_statement = f"if {source} is not None:\n    " + write_statement
    return write_statement


def _generate_anonymous_structure_read_fun(gen: Generator, val: StructureLiteral) -> str:
    read_statements = [_generate_property_read_statement(gen, p, "obj", True, "out") for p in val.properties]
    template = dedent("""\
        def _parse_{name}(obj: Mapping[str, JSON_VALUE]) -> {type}:
            out: {type} = {{}}
        {statements}
            return out""")
    return template.format(
        name=gen.get_anonymous_type_name(val),
        type=gen.generate_type_annotation(AnyType("literal", StructureLiteralType(val))),
        statements=indent("\n".join(read_statements)))


def _generate_anonymous_structure_write_fun(gen: Generator, val: StructureLiteral) -> str:
    write_statements = [_generate_property_write_statement(gen, p, "out", True, "obj") for p in val.properties]

    template = dedent("""\
        def _write_{name}(obj: {type}) -> JSON_VALUE:
            out: JSON_VALUE = {{}}
        {statements}
            return out""")

    return template.format(
        name=gen.get_anonymous_type_name(val),
        type=gen.generate_type_annotation(AnyType("literal", StructureLiteralType(val))),
        statements=indent("\n".join(write_statements)))


def generate_anonymous_structure_definition(gen: Generator, val: StructureLiteral) -> str:
    template = dedent_ignore_empty("""\
        {read_fun}

        {write_fun}""")
    return template.format(
        read_fun=_generate_anonymous_structure_read_fun(gen, val),
        write_fun=_generate_anonymous_structure_write_fun(gen, val))


def _generate_property_declaration(gen: Generator, prop: Property) -> str:
    """Generates declaration code for a `Property`."""
    type_annotation = gen.generate_type_annotation(prop.type)
    if prop.optional:
        type_annotation = f"Optional[{type_annotation}]"

    if prop.documentation:
        documentation = generate_documentation_comment(prop.documentation)
    else:
        documentation = ""

    return f"{documentation}{escape_keyword(prop.name)}: {type_annotation}"


def _build_documentation_with_prefix(prefix: str, documentation: str) -> str:
    if len(documentation) == 0:
        return ""

    lines = documentation.splitlines()
    first_line = prefix + lines[0]
    return first_line + "\n" + "\n".join("    " + l for l in lines[1:])


def _generate_anonymous_structure_documentation(gen: Generator, val: StructureLiteral) -> str:
    docstring_parts: List[str] = ["`dict` with the following keys:\n"]
    for p in val.properties:
        prefix = f"* `'{p.name}'` (type `{gen.generate_type_annotation(p.type)}`): "

        if not p.documentation:
            docstring_parts.append(prefix)
        else:
            docstring_parts.append(_build_documentation_with_prefix(prefix, p.documentation))
    return "\n\n".join(docstring_parts)


def _generate_property_documentation(gen: Generator, property: Property) -> str:
    documentation = ""
    if property.documentation:
        documentation += property.documentation
    if isinstance(property.type.content, StructureLiteralType):
        documentation += "\n\n" + _generate_anonymous_structure_documentation(gen, property.type.content.value)
    return _build_documentation_with_prefix(f":param {property.name}: ", documentation)


def _generate_structure_init_method(gen: Generator, properties: Tuple[Property, ...]) -> str:
    if len(properties) == 0:
        return ""

    parameters: List[str] = []
    for p in properties:
        if p.optional:
            parameters.append(f"{escape_keyword(p.name)}: Optional[{gen.generate_type_annotation(p.type)}] = None")
        else:
            parameters.append(f"{escape_keyword(p.name)}: {gen.generate_type_annotation(p.type)}")

    names = [escape_keyword(p.name) for p in properties]
    assignments = [f"self.{n} = {n}" for n in names]

    template = dedent('''\
        def __init__(self, *, {parameters}) -> None:
        {assignments}''')

    return template.format(
        parameters=", ".join(parameters),
        assignments=indent("\n".join(assignments)))


def _generate_structure_from_json_method(gen: Generator, class_name: str, properties: Tuple[Property]) -> str:
    property_read_statements = "\n".join([_generate_property_read_statement(gen, p, "obj") for p in properties])
    property_assignments = ", ".join([escape_keyword(p.name) + "=" + escape_keyword(p.name) for p in properties])

    template = dedent("""\
        @classmethod
        def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "{class_name}":
        {read_statements}
            return cls({property_assignments})""")
    return template.format(
        class_name=class_name,
        read_statements=indent(property_read_statements),
        property_assignments=property_assignments)


def _generate_structure_to_json_method(gen: Generator, properties: Tuple[Property]) -> str:
    property_write_statements = "\n".join([_generate_property_write_statement(gen, p, "out") for p in properties])

    template = dedent("""\
        def to_json(self) -> Dict[str, JSON_VALUE]:
            out: Dict[str, JSON_VALUE] = {{}}
        {write_statments}
            return out""")
    return template.format(write_statments=indent(property_write_statements))


def _generate_structure_definition_generic(gen: Generator, class_name: str, documentation: Optional[str], properties: Tuple[Property], superclasses: Tuple[str, ...]) -> str:
    property_declarations = "\n\n".join([_generate_property_declaration(gen, p) for p in properties])

    template = dedent_ignore_empty('''\
        @dataclass
        class {class_name}({superclasses}):
            """
        {documentation}

            *Generated from the TypeScript documentation*
            """

        {property_declarations}

        {init}

        {from_json}

        {to_json}''')

    return template.format(
        class_name=class_name,
        superclasses=", ".join(superclasses),
        documentation=indent(documentation if documentation else ""),
        property_declarations=indent(property_declarations),
        init=indent(_generate_structure_init_method(gen, properties)),
        from_json=indent(_generate_structure_from_json_method(gen, class_name, properties)),
        to_json=indent(_generate_structure_to_json_method(gen, properties)))


def generate_structure_definition(gen: Generator, struct: Structure) -> str:
    superclasses: List[str] = []
    if struct.extends:
        for m in struct.extends:
            if not isinstance(m.content, ReferenceType):
                raise LSPGeneratorException("Non-reference 'extends' values are not supported.")
            superclasses.append(m.content.name)

    properties = tuple(gen.collect_structure_properties(struct))

    property_documentations = "\n".join(_generate_property_documentation(gen, p) for p in properties)
    if struct.documentation:
        documentation = struct.documentation + "\n\n" + property_documentations
    else:
        documentation = property_documentations
    return _generate_structure_definition_generic(gen, struct.name, documentation, properties, tuple(superclasses))


def generate_andtype_definition(gen: Generator, val: AndType) -> str:
    name = gen.get_anonymous_type_name(val)
    properties: List[Property] = []
    for i in val.items:
        if not isinstance(i.content, ReferenceType):
            raise LSPGeneratorException("AndType items must be references")
        target = gen.resolve_reference(i.content)
        if isinstance(target, Structure):
            properties += gen.collect_structure_properties(target)
        elif isinstance(target, StructureLiteral):
            properties += target.properties
        else:
            raise LSPGeneratorException("AndType items must refer to structures")
    return _generate_structure_definition_generic(gen, name, None, tuple(properties), ())


def generate_typealias_definition(gen: Generator, typealias: TypeAlias) -> str:
    annotation = gen.generate_type_annotation(typealias.type)
    if annotation[0] == '"' and annotation[-1] == '"':
        # If the type annotation is quoted, the generated code will look like
        #   typealias = "type"
        # which is interpreted as setting a string variable. So we un-quote the annotation
        # here and hope that it does not cause problems with forward declarations.
        annotation = annotation[1: -1]

    expected_json_type = gen.get_expected_json_type(typealias.type)
    if expected_json_type:
        assert_fun = json_type_to_assert_function[expected_json_type]
    else:
        assert_fun = ""

    template = dedent_ignore_empty("""\
        {documentation}{name} = {annotation}

        def parse_{name}(arg: JSON_VALUE) -> {name}:
            return {parse_expression}

        def write_{name}(arg: {name}) -> JSON_VALUE:
            return {write_expression}""")

    return template.format(
        name=typealias.name,
        documentation=generate_documentation_comment(typealias.documentation) if typealias.documentation else "",
        annotation=annotation,
        parse_expression=gen.generate_parse_expression(typealias.type, f"{assert_fun}(arg)"),
        write_expression=gen.generate_write_expression(typealias.type, "arg"))


def get_referenced_definitions_anytype(gen: Generator, val: AnyType) -> List[Union[ref_target, StructureLiteral, AndType]]:
    if val.kind == "reference":
        assert isinstance(val.content, ReferenceType)
        target = gen.resolve_reference(val.content, resolve_typealiases=False)
        assert target != None
        return [target]
    elif val.kind == "array":
        assert isinstance(val.content, ArrayType)
        return get_referenced_definitions_anytype(gen, val.content.element)
    elif val.kind == "map":
        assert isinstance(val.content, MapType)
        out: List[Any] = []
        if isinstance(val.content.key, ReferenceType):
            out.append(gen.resolve_reference(val.content.key, resolve_typealiases=False))
        if isinstance(val.content.value.content, ReferenceType):
            out.append(gen.resolve_reference(val.content.value.content, resolve_typealiases=False))
        return out
    elif val.kind == "and":
        assert isinstance(val.content, AndType)
        return [val.content]
    elif val.kind == "or":
        assert isinstance(val.content, OrType)
        out: List[Any] = []
        for i in val.content.items:
            out += get_referenced_definitions_anytype(gen, i)
        return out
    elif val.kind == "tuple":
        assert isinstance(val.content, TupleType)
        out: List[Any] = []
        for i in val.content.items:
            out += get_referenced_definitions_anytype(gen, i)
        return out
    elif val.kind == "literal":
        assert isinstance(val.content, StructureLiteralType)
        return [val.content.value]
    elif val.kind in ["base", "stringLiteral", "integerLiteral", "booleanLiteral"]:
        return []
    else:
        assert False  # Broken AnyType


def _get_referenced_definitions(gen: Generator, obj: Union[Notification, Request, Structure, TypeAlias, StructureLiteral, AndType]) -> List[Union[ref_target, StructureLiteral, AndType]]:
    if isinstance(obj, Enumeration):
        return []
    elif isinstance(obj, Notification):
        out: List[Union[ref_target, StructureLiteral, AndType]] = []

        if obj.params:
            if isinstance(obj.params, Tuple):
                for p in obj.params:
                    out += get_referenced_definitions_anytype(gen, p)
            else:
                out += get_referenced_definitions_anytype(gen, obj.params)

        if obj.registration_options:
            out += get_referenced_definitions_anytype(gen, obj.registration_options)

        return out
    elif isinstance(obj, Request):
        out: List[Union[ref_target, StructureLiteral, AndType]] = []

        if obj.error_data:
            out += get_referenced_definitions_anytype(gen, obj.error_data)

        if obj.params:
            if isinstance(obj.params, Tuple):
                for p in obj.params:
                    out += get_referenced_definitions_anytype(gen, p)
            else:
                out += get_referenced_definitions_anytype(gen, obj.params)

        if obj.partial_result:
            out += get_referenced_definitions_anytype(gen, obj.partial_result)

        if obj.registration_options:
            out += get_referenced_definitions_anytype(gen, obj.registration_options)

        out += get_referenced_definitions_anytype(gen, obj.result)

        return out
    elif isinstance(obj, Structure):
        out: List[Union[ref_target, StructureLiteral, AndType]] = []

        if obj.extends:
            for p in obj.extends:
                out += get_referenced_definitions_anytype(gen, p)

        if obj.mixins:
            # mixins are copied into the structure, so there is no type relation
            # between a structure and its mixins. Therefore, any types referenced
            # by a mixin are also referenced by the structure.
            for p in obj.mixins:
                if p.kind != "reference":
                    raise LSPGeneratorException("Non-reference mixins are not supported")
                assert isinstance(p.content, ReferenceType)
                target = gen.resolve_reference(p.content)
                if not isinstance(target, Structure):
                    raise LSPGeneratorException("References to non-structure values are not supported in mixins")
                out += _get_referenced_definitions(gen, target)

        for p in obj.properties:
            out += get_referenced_definitions_anytype(gen, p.type)

        return out
    elif isinstance(obj, TypeAlias):
        return get_referenced_definitions_anytype(gen, obj.type)
    elif isinstance(obj, StructureLiteral):
        out: List[Union[ref_target, StructureLiteral, AndType]] = []
        for p in obj.properties:
            out += get_referenced_definitions_anytype(gen, p.type)
        return out
    else:  # isinstance(obj, AndType)
        out: List[Union[ref_target, StructureLiteral, AndType]] = []
        for i in obj.items:
            if i.kind != "reference":
                raise LSPGeneratorException("Non-reference AndType items are not supported")
            assert isinstance(i.content, ReferenceType)
            target = gen.resolve_reference(i.content)
            if not isinstance(target, Structure):
                raise LSPGeneratorException("References to non-structure values are not supported in AndType items")
            out += _get_referenced_definitions(gen, target)
        return out


# All the types which end up in structures.py
structures_py_type = Union[Structure, StructureLiteral, TypeAlias, AndType]


def _sort_structures_and_typealiases_rec(gen: Generator, obj: structures_py_type, status: Dict[structures_py_type, str], list: List[structures_py_type]) -> None:
    if status.get(obj) in ["pending", "visited"]:
        return

    status[obj] = "pending"

    for r in _get_referenced_definitions(gen, obj):
        if isinstance(r, Enumeration):
            # Enumerations only ever reference AnyTypes
            continue

        _sort_structures_and_typealiases_rec(gen, r, status, list)

    list.append(obj)
    status[obj] = "visited"


def _sort_structures_and_typealiases(gen: Generator) -> List[structures_py_type]:
    """Topologically sorts Structures and TypeAliases, so that the definitions can
    be generated in a valid order."""
    status: Dict[structures_py_type, str] = {}
    list: List[structures_py_type] = []

    for s in gen.get_meta_model().structures:
        _sort_structures_and_typealiases_rec(gen, s, status, list)

    for t in gen.get_meta_model().type_aliases:
        _sort_structures_and_typealiases_rec(gen, t, status, list)

    for t in gen.get_anonymous_types():
        _sort_structures_and_typealiases_rec(gen, t, status, list)

    return list


def generate_structures_py(gen: Generator) -> str:
    sorted_types = _sort_structures_and_typealiases(gen)

    definitions: List[str] = []

    for t in sorted_types:
        if isinstance(t, TypeAlias):
            definitions.append(generate_typealias_definition(gen, t))
        elif isinstance(t, Structure):
            definitions.append(generate_structure_definition(gen, t))
        elif isinstance(t, StructureLiteral):
            definitions.append(generate_anonymous_structure_definition(gen, t))
        else:  # isinstance(t, AndType)
            definitions.append(generate_andtype_definition(gen, t))

    template = dedent_ignore_empty("""\
        # DO NOT EDIT THIS FILE DIRECTLY!
        #
        # This file was automatically generated, so any edits to it will get overwritten.
        # To change the content of this file, make changes to the generator.

        from ._util import *
        from ._enumerations import *

        from dataclasses import dataclass
        from typing import Dict, List, Literal, Mapping, Optional, Tuple, Union


        {definitions}
        """)

    return template.format(definitions="\n\n\n".join(definitions))
