from .schema.anytype import AndType, AnyType, ArrayType, BaseType, BooleanLiteralType, IntegerLiteralType, MapKeyType, MapType, OrType, Property, StringLiteralType, StructureLiteral, StructureLiteralType, TupleType
from .schema.types import Enumeration, MetaModel, Notification, ReferenceType, Request, Structure, TypeAlias

from typing import ClassVar, Dict, List, Optional, Tuple, Union

from .schema.util import JSON_TYPE_NAME


class LSPGeneratorException(Exception):
    message: str

    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


def indent(text: str) -> str:
    return "\n".join(["    " + l for l in text.splitlines()])


class ReferenceResolver:
    _enumeration_index: Dict[str, Enumeration]
    _structure_index: Dict[str, Structure]
    _type_alias_index: Dict[str, TypeAlias]

    def __init__(self, meta_model: MetaModel) -> None:
        self._enumeration_index = { e.name: e for e in meta_model.enumerations }
        self._structure_index = { s.name: s for s in meta_model.structures }
        self._type_alias_index = { t.name: t for t in meta_model.type_aliases }

    def _resolve_reference_internal(self, name: str, stack: List[str]) -> Optional[Union[Structure, Enumeration, TypeAlias]]:
        if name in stack:
            raise LSPGeneratorException(f"Circular references: {stack + [name]}")
        if name in self._enumeration_index:
            return self._enumeration_index[name]
        elif name in self._structure_index:
            return self._structure_index[name]
        elif name in self._type_alias_index:
            type_alias = self._type_alias_index[name]
            if type_alias.type.kind == "reference":
                reference = type_alias.type.content
                assert isinstance(reference, ReferenceType)
                return self._resolve_reference_internal(reference.name, stack + [name])
        else:
            return None

    def resolve_reference(self, reference: ReferenceType) -> Optional[Union[Structure, Enumeration, TypeAlias]]:
        """Resolves a ReferenceType to its reference type in the MetaModel of this ReferenceResolver.

        This method will transparently resolve intermediate TypeAliases.
        Raises an LSPGeneratorException if circular references are detected. This is possible if a TypeAlias
        aliases a References which, either directly or indirectly points back to the same TypeAlias.

        Returns None if the referenced type was not found."""
        return self._resolve_reference_internal(reference.name, [])


# All the types which end up in structures.py
structures_py_type = Union[Structure, StructureLiteral, TypeAlias, AndType]

class Generator:
    _meta_model: MetaModel
    _reference_resolver: ReferenceResolver

    _anonymus_structure_names: Dict[StructureLiteral, str]
    _anonymus_andtype_names: Dict[AndType, str]

    _json_type_to_get_function: ClassVar[Dict[JSON_TYPE_NAME, str]] = {
        "number (int)": "json_get_int",
        "number (real)": "json_get_float",
        "bool": "json_get_bool",
        "string": "json_get_string",
        "array": "json_get_array",
        "object": "json_get_object",
        "null": "json_get_null",
    }

    _json_type_to_get_optional_function: ClassVar[Dict[JSON_TYPE_NAME, str]] = {
        "number (int)": "json_get_optional_int",
        "number (real)": "json_get_optional_float",
        "bool": "json_get_optional_bool",
        "string": "json_get_optional_string",
        "array": "json_get_optional_array",
        "object": "json_get_optional_object",
        "null": "json_get_optional_null",
    }

    # Maps JSON types to their corresponding json_assert_type_* function in static.util
    _json_type_to_assert_function: ClassVar[Dict[JSON_TYPE_NAME, str]] = {
        "number (int)": "json_assert_type_int",
        "number (real)": "json_assert_type_float",
        "bool": "json_assert_type_bool",
        "string": "json_assert_type_string",
        "array": "json_assert_type_array",
        "object": "json_assert_type_object",
        "null": "json_assert_type_null",
    }


    def __init__(self, meta_model: MetaModel) -> None:
        self._meta_model = meta_model
        self._reference_resolver = ReferenceResolver(meta_model)
        self._anonymus_structures = []
        self._anonymus_structure_names = {}


    def _get_expected_json_type_base(self, base: BaseType) -> JSON_TYPE_NAME:
        """Returns the variant of `JSON_VALUE` that is expected when parsing the given `BaseType`."""
        if base.name in ["URI", "DocumentUri", "RegExp", "string"]:
            return "string"
        elif base.name in ["integer", "uinteger"]:
            return "number (int)"
        elif base.name == "decimal":
            return "number (real)"
        elif base.name == "boolean":
            return "bool"
        elif base.name == "null":
            return "null"
        else:
            assert False # Broken BaseType


    def _get_expected_json_type_mapkey(self, key: MapKeyType) -> JSON_TYPE_NAME:
        """Returns the variant `JSON_VALUE` which values of the given `MapKeyType` are expected to have."""
        if key.name in ["URI", "DocumentUri", "string"]:
            return "string"
        elif key.name == "integer":
            return "number (int)"
        else:
            assert False # Broken MapKeyType


    def _get_expected_json_type(self, val: AnyType) -> Optional[JSON_TYPE_NAME]:
        """Returns the variant of `JSON_VALUE` which values of the given `AnyType` are expected to have."""
        if val.kind == "base":
            assert isinstance(val.content, BaseType)
            return self._get_expected_json_type_base(val.content)
        elif val.kind in ["reference", "map", "and", "literal"]:
            return "object"
        elif val.kind in ["array", "tuple"]:
            return "array"
        elif val.kind == "stringLiteral":
            return "string"
        elif val.kind == "integerLiteral":
            return "number (int)"
        elif val.kind == "booleanLiteral":
            return "bool"
        elif val.kind == "or":
            return None
        else:
            assert False # Broken AnyType


    def _generate_parse_expression_base(self, base: BaseType, arg: str) -> str:
        # TODO validate URIs
        return arg


    def _generate_parse_expression_reference(self, reference: ReferenceType, arg: str) -> str:
        target = self._reference_resolver.resolve_reference(reference)
        if isinstance(target, AnyType):
            # typeAlias pointing to an AnyType
            return self.generate_parse_expression(target, arg)
        elif isinstance(target, Structure):
            return f"{reference.name}.from_json({arg})"
        elif isinstance(target, Enumeration):
            return f"{reference.name}({arg})"
        else:
            raise LSPGeneratorException("Reference pointing to an unsupported type.")


    def _generate_parse_expression_mapping(self, map: MapType, arg: str) -> str:
        """Generates an expression that parses the given `MapType` from the given `arg`.
        The expression evaluates to a Python dict, which maps arbitrary instances of the
        map's key type to instances of the map's value type."""
        if isinstance(map.key, MapKeyType):
            assert_type_func_key = self._json_type_to_assert_function[self._get_expected_json_type_mapkey(map.key)]
        else:
            target = self._reference_resolver.resolve_reference(map.key)
            if not isinstance(target, AnyType):
                raise LSPGeneratorException("A Reference in a map key must point to an AnyType.")
            json_expected_type = self._get_expected_json_type(target)
            if not json_expected_type:
                raise LSPGeneratorException("Weird AnyType in a map key.")
            assert_type_func_key = self._json_type_to_assert_function[json_expected_type]

        if expected_json_type_value := self._get_expected_json_type(map.value):
            assert_type_func_value = self._json_type_to_assert_function[expected_json_type_value]
        else:
            assert_type_func_value = ""

        parse_expression_arg = f"{assert_type_func_value}(value)"
        return f"{{ {assert_type_func_key}(key): {self.generate_parse_expression(map.value, parse_expression_arg)} for key, value in {arg}.items()}}"


    def _generate_parse_expression_or(self, or_val: OrType, arg: str) -> str:
        parse_functions: List[str] = []
        for i in or_val.items:
            if expected_json_type := self._get_expected_json_type(i):
                assert_type_func = self._json_type_to_assert_function[expected_json_type]
            else:
                assert_type_func = ""
            parse_func_arg = f"{assert_type_func}(v)"
            parse_functions.append(f"lambda v: {self.generate_parse_expression(i, parse_func_arg)}")
        return f"parse_or_type({arg}, [{', '.join(parse_functions)}])"


    def _generate_parse_expression_tuple(self, tuple: TupleType, arg: str) -> str:
        """Generates an expression that parses the given `TupleType` from the given `arg`.
        The returned expression evaluates to a Python tuple which contains the types defined in the `TupleType`"""
        parse_expressions: List[str] = []
        for i, t in enumerate(tuple.items):
            json_type = self._get_expected_json_type(t)
            assert_fun = self._json_type_to_assert_function[json_type] if json_type else ""
            parse_expressions.append(self.generate_parse_expression(t, f"{assert_fun}({arg}[{i}])"))
        return "(" + ", ".join(parse_expressions) + ")"


    def generate_parse_expression(self, val: AnyType, arg: str) -> str:
        """Generate an expression that will parse the value in `arg` into the type denoted by `val`.
        `arg` should be an expression that evaluates to a `JSON_VALUE`."""
        if val.kind == "base":
            assert isinstance(val.content, BaseType)
            return self._generate_parse_expression_base(val.content, arg)
        elif val.kind == "reference":
            assert isinstance(val.content, ReferenceType)
            return self._generate_parse_expression_reference(val.content, arg)
        elif val.kind == "array":
            assert isinstance(val.content, ArrayType)
            json_type = self._get_expected_json_type(val.content.element)
            assert_fun = self._json_type_to_assert_function[json_type] if json_type else ""
            return f'[{self.generate_parse_expression(val.content.element, f"{assert_fun}(i)")} for i in {arg}]'
        elif val.kind == "map":
            assert isinstance(val.content, MapType)
            return self._generate_parse_expression_mapping(val.content, arg)
        elif val.kind == "and":
            return "" # TODO
        elif val.kind == "or":
            assert isinstance(val.content, OrType)
            return self._generate_parse_expression_or(val.content, arg)
        elif val.kind == "tuple":
            assert isinstance(val.content, TupleType)
            return self._generate_parse_expression_tuple(val.content, arg)
        elif val.kind == "literal":
            assert isinstance(val.content, StructureLiteralType)
            return f"{self._anonymus_structure_names[val.content.value]}.from_json({arg})"
        elif val.kind == "stringLiteral":
            assert isinstance(val.content, StringLiteralType)
            return f'match_string({arg}, "{val.content.value}")'
        elif val.kind == "integerLiteral":
            assert isinstance(val.content, IntegerLiteralType)
            return f'match_integer({arg}, {val.content.value})'
        elif val.kind == "booleanLiteral":
            assert isinstance(val.content, BooleanLiteralType)
            return f'match_bool({arg}, {val.content.value})'
        else:
            assert False # Broken AnyType


    def _generate_type_annotation_base(self, base: BaseType) -> str:
        if base.name in ["URI", "DocumentUri", "RegExp", "string"]:
            return "str"
        elif base.name in ["integer", "uinteger"]:
            return "int"
        elif base.name == "decimal":
            return "float"
        elif base.name == "boolean":
            return "bool"
        elif base.name == "null":
            return "None"
        else:
            assert False # Broken BaseType


    def _generate_type_annotation_mapkey(self, key: MapKeyType) -> str:
        """Returns the variant `JSON_VALUE` which values of the given `MapKeyType` are expected to have."""
        if key.name in ["URI", "DocumentUri", "string"]:
            return "str"
        elif key.name == "integer":
            return "int"
        else:
            assert False # Broken MapKeyType


    def _generate_type_annotation(self, val: AnyType) -> str:
        """Generates a type annotation for the given `AnyType`."""
        if val.kind == "base":
            assert isinstance(val.content, BaseType)
            return self._generate_type_annotation_base(val.content)
        elif val.kind == "reference":
            assert isinstance(val.content, ReferenceType)
            return val.content.name
        elif val.kind == "array":
            assert isinstance(val.content, ArrayType)
            return f"List[{self._generate_type_annotation(val.content.element)}]"
        elif val.kind == "map":
            assert isinstance(val.content, MapType)
            if isinstance(val.content.key, MapKeyType):
                key_annotation = self._generate_type_annotation_mapkey(val.content.key)
            else:
                key_annotation = val.content.key.name
            return f"Dict[{key_annotation}, {self._generate_type_annotation(val.content.value)}]"
        elif val.kind == "and":
            assert isinstance(val.content, AndType)
            return self._anonymus_andtype_names[val.content]
        elif val.kind == "or":
            assert isinstance(val.content, OrType)
            item_annotations = [self._generate_type_annotation(v) for v in val.content.items]
            return f"Union[{', '.join(item_annotations)}]"
        elif val.kind == "tuple":
            assert isinstance(val.content, TupleType)
            item_annotations = [self._generate_type_annotation(v) for v in val.content.items]
            return f"Tuple[{', '.join(item_annotations)}]"
        elif val.kind == "literal":
            assert isinstance(val.content, StructureLiteralType)
            return self._anonymus_structure_names[val.content.value]
        elif val.kind == "stringLiteral":
            return "str"
        elif val.kind == "integerLiteral":
            return "int"
        elif val.kind == "booleanLiteral":
            return "bool"
        else:
            assert False # Broken AnyType


    def get_referenced_definitions_anytype(self, val: AnyType) -> List[str]:
        if val.kind == "reference":
            assert isinstance(val.content, ReferenceType)
            return [val.content.name]
        elif val.kind == "array":
            assert isinstance(val.content, ArrayType)
            return self.get_referenced_definitions_anytype(val.content.element)
        elif val.kind == "map":
            assert isinstance(val.content, MapType)
            out: List[str] = []
            if isinstance(val.content.key, ReferenceType):
                out.append(val.content.key.name)
            if isinstance(val.content.value.content, ReferenceType):
                out.append(val.content.value.content.name)
            return out
        elif val.kind == "and":
            assert isinstance(val.content, AndType)
            return [self._anonymus_andtype_names[val.content]]
        elif val.kind == "or":
            assert isinstance(val.content, OrType)
            out: List[str] = []
            for i in val.content.items:
                out += self.get_referenced_definitions_anytype(i)
            return out
        elif val.kind == "tuple":
            assert isinstance(val.content, TupleType)
            out: List[str] = []
            for i in val.content.items:
                out += self.get_referenced_definitions_anytype(i)
            return out
        elif val.kind == "literal":
            assert isinstance(val.content, StructureLiteralType)
            return [self._anonymus_structure_names[val.content.value]]
        elif val.kind in ["base", "stringLiteral", "integerLiteral", "booleanLiteral"]:
            return []
        else:
            assert False # Broken AnyType


    def get_referenced_definitions(self, obj: Union[Notification, Request, Structure, TypeAlias, StructureLiteral, AndType]) -> List[str]:
        if isinstance(obj, Enumeration):
            return []
        elif isinstance(obj, Notification):
            out: List[str] = []

            if obj.params:
                if isinstance(obj.params, Tuple):
                    for p in obj.params:
                        out += self.get_referenced_definitions_anytype(p)
                else:
                    out += self.get_referenced_definitions_anytype(obj.params)

            if obj.registration_options:
                out += self.get_referenced_definitions_anytype(obj.registration_options)

            return out
        elif isinstance(obj, Request):
            out: List[str] = []

            if obj.error_data:
                out += self.get_referenced_definitions_anytype(obj.error_data)

            if obj.params:
                if isinstance(obj.params, Tuple):
                    for p in obj.params:
                        out += self.get_referenced_definitions_anytype(p)
                else:
                    out += self.get_referenced_definitions_anytype(obj.params)

            if obj.partial_result:
                out += self.get_referenced_definitions_anytype(obj.partial_result)

            if obj.registration_options:
                out += self.get_referenced_definitions_anytype(obj.registration_options)

            out += self.get_referenced_definitions_anytype(obj.result)

            return out
        elif isinstance(obj, Structure):
            out: List[str] = []

            if obj.extends:
                for p in obj.extends:
                    out += self.get_referenced_definitions_anytype(p)

            if obj.mixins:
                # mixins are copied into the structure, so there is no type relation
                # between a structure and its mixins. Therefore, any types referenced
                # by a mixin are also referenced by the structure.
                for p in obj.mixins:
                    if p.kind != "reference":
                        raise LSPGeneratorException("Non-reference mixins are not supported")
                    assert isinstance(p.content, ReferenceType)
                    target = self._reference_resolver.resolve_reference(p.content)
                    if not isinstance(target, Structure):
                        raise LSPGeneratorException("References to non-structure values are not supported in mixins")
                    out += self.get_referenced_definitions(target)

            for p in obj.properties:
                out += self.get_referenced_definitions_anytype(p.type)

            return out
        elif isinstance(obj, TypeAlias):
            return self.get_referenced_definitions_anytype(obj.type)
        elif isinstance(obj, StructureLiteral):
            out: List[str] = []
            for p in obj.properties:
                out += self.get_referenced_definitions_anytype(p.type)
            return out
        else: # isinstance(obj, AndType)
            out: List[str] = []
            for i in obj.items:
                if i.kind != "reference":
                    raise LSPGeneratorException("Non-reference AndType items are not supported")
                assert isinstance(i.content, ReferenceType)
                target = self._reference_resolver.resolve_reference(i.content)
                if not isinstance(target, Structure):
                    raise LSPGeneratorException("References to non-structure values are not supported in AndType items")
                out += self.get_referenced_definitions(target)
            return out


    def sort_structures_and_typealiases_rec(self, obj: structures_py_type, status: Dict[structures_py_type, str], list: List[structures_py_type]) -> None:
        if status.get(obj) in ["pending", "visited"]:
            return

        status[obj] = "pending"

        for r in self.get_referenced_definitions(obj):
            if isinstance(r, Enumeration):
                # Enumerations only ever reference AnyTypes
                continue

            if not isinstance(r, (Structure, TypeAlias, StructureLiteral, AndType)):
                raise LSPGeneratorException("Structure or TypeAlias is referencing an unsupported type.")

            self.sort_structures_and_typealiases_rec(r, status, list)

        list.append(obj)
        status[obj] = "visited"


    def sort_structures_and_typealiases(self) -> List[structures_py_type]:
        """Topologically sorts Structures and TypeAliases, so that the definition can
        be generated in a valid order."""
        status: Dict[structures_py_type, str] = {}
        list: List[structures_py_type] = []

        for s in self._meta_model.structures:
            self.sort_structures_and_typealiases_rec(s, status, list)

        for t in self._meta_model.type_aliases:
            self.sort_structures_and_typealiases_rec(t, status, list)

        return list


    def _generate_documentation_comment(self, documentation: str) -> str:
        out = '\n'.join(["# " + l for l in documentation.splitlines()])
        out += '\n'
        return out


    def _generate_property_declaration(self, prop: Property) -> str:
        """Generates declaration code for a `Property`."""
        type_annotation = self._generate_type_annotation(prop.type)
        if prop.optional:
            type_annotation = f"Optional[{type_annotation}]"

        if prop.documentation:
            documentation = self._generate_documentation_comment(prop.documentation)
        else:
            documentation = ""


        return f"{documentation}{prop.name}: {type_annotation}"


    def _generate_property_read_statement(self, prop: Property, obj_name: str) -> str:
        """Generates a statement that reads the given `Property` from the JSON object `obj_name`."""
        if prop.optional:
            if expected_json_type := self._get_expected_json_type(prop.type):
                get_json_expr = self._json_type_to_get_optional_function[expected_json_type] + f'({obj_name}, "{prop.name}")'
            else:
                get_json_expr = f'{obj_name}.get("{prop.name}")'

            parse_expression = self.generate_parse_expression(prop.type, f"{prop.name}_json")
            return f"""\
if {prop.name}_json := {get_json_expr}:
    {prop.name} = {parse_expression}
else:
    {prop.name} = None"""

        else:
            if expected_json_type := self._get_expected_json_type(prop.type):
                get_json_expr = self._json_type_to_get_function[expected_json_type] + f'({obj_name}, "{prop.name}")'
            else:
                get_json_expr = f'{obj_name}["{prop.name}"]'

            parse_expression = self.generate_parse_expression(prop.type, get_json_expr)
            return f"{prop.name} = {parse_expression}"


    def _generate_structure_from_json_method(self, class_name: str, properties: Tuple[Property]) -> str:
        property_read_statements = "\n".join([self._generate_property_read_statement(p, "obj") for p in properties])
        property_names = ", ".join([p.name + "=" + p.name for p in properties])
        return f"""\
@classmethod
def from_json(cls, obj: JSON_VALUE) -> "{class_name}":
{indent(property_read_statements)}
    return cls({property_names})"""


    def _generate_structure_definition_generic(self, class_name: str, documentation: Optional[str], properties: Tuple[Property], superclasses: Tuple[str, ...]) -> str:
        doc = documentation if documentation else ""
        property_declarations = "\n\n".join([self._generate_property_declaration(p) for p in properties])

        return f'''\
@dataclass
class {class_name}({", ".join(superclasses)}):
    """{doc}"""

{indent(property_declarations)}

{indent(self._generate_structure_from_json_method(class_name, properties))}'''


    def _add_anonymus_definitions_from_anytype(self, val: AnyType) -> None:
        """Adds a definition to the list of anonymus definitions for the given anytype.
        If `val` is an aggregate type, definitions are created recursively for all
        encountered anonymus types (literal, and). Recursion stops if a type is not an
        anonymus structure."""

        if val.kind in ["base", "reference", "stringLiteral", "integerLiteral", "booleanLiteral"]:
            return
        elif val.kind == "array":
            assert isinstance(val.content, ArrayType)
            self._add_anonymus_definitions_from_anytype(val.content.element)
        elif val.kind == "map":
            assert isinstance(val.content, MapType)
            self._add_anonymus_definitions_from_anytype(val.content.value)
        elif val.kind == "and":
            assert isinstance(val.content, AndType)
            for i in val.content.items:
                self._add_anonymus_definitions_from_anytype(i)

            class_name = "AnonymusAndType" + str(len(self._anonymus_andtype_names))
            self._anonymus_andtype_names[val.content] = class_name
        elif val.kind == "or":
            assert isinstance(val.content, OrType)
            for i in val.content.items:
                self._add_anonymus_definitions_from_anytype(i)
        elif val.kind == "tuple":
            assert isinstance(val.content, TupleType)
            for i in val.content.items:
                self._add_anonymus_definitions_from_anytype(i)
        elif val.kind == "literal":
            assert isinstance(val.content, StructureLiteralType)
            for i in val.content.value.properties:
                self._add_anonymus_definitions_from_anytype(i.type)

            class_name = "AnonymusStructure" + str(len(self._anonymus_structure_names))
            self._anonymus_structure_names[val.content.value] = class_name
            # self._anonymus_structures.append(self._generate_structure_definition_generic(class_name, val.content.value.documentation, val.content.value.properties, ()))


    def generate_anonymus_structure_definitions(self) -> None:
        """Traverses the `MetaModel` and generates definitions for all
        anonymus types used"""

        for n in self._meta_model.notifications:
            if n.params:
                if isinstance(n.params, Tuple):
                    for p in n.params:
                        self._add_anonymus_definitions_from_anytype(p)
                else:
                    self._add_anonymus_definitions_from_anytype(n.params)

            if n.registration_options:
                self._add_anonymus_definitions_from_anytype(n.registration_options)

        for r in self._meta_model.requests:
            if r.error_data:
                self._add_anonymus_definitions_from_anytype(r.error_data)

            if r.params:
                if isinstance(r.params, Tuple):
                    for p in r.params:
                        self._add_anonymus_definitions_from_anytype(p)
                else:
                    self._add_anonymus_definitions_from_anytype(r.params)

            if r.partial_result:
                self._add_anonymus_definitions_from_anytype(r.partial_result)

            if r.registration_options:
                self._add_anonymus_definitions_from_anytype(r.registration_options)

            self._add_anonymus_definitions_from_anytype(r.result)

        for s in self._meta_model.structures:
            if s.extends:
                for p in s.extends:
                    self._add_anonymus_definitions_from_anytype(p)

            if s.mixins:
                for p in s.mixins:
                    self._add_anonymus_definitions_from_anytype(p)

            for p in s.properties:
                self._add_anonymus_definitions_from_anytype(p.type)

        for t in self._meta_model.type_aliases:
            self._add_anonymus_definitions_from_anytype(t.type)


    def collect_structure_properties(self, struct: Structure) -> List[Property]:
        props: List[Property] = []

        if struct.extends:
            for m in struct.extends:
                if not isinstance(m.content, ReferenceType):
                    raise LSPGeneratorException("Non-reference 'extends' values are not supported.")
                target = self._reference_resolver.resolve_reference(m.content)
                if not isinstance(target, Structure):
                    raise LSPGeneratorException("Non-Structure references in 'extends' are not supported")
                props += self.collect_structure_properties(target)

        if struct.mixins:
            for m in struct.mixins:
                if not isinstance(m.content, ReferenceType):
                    raise LSPGeneratorException("Non-reference 'mixins' values are not supported.")
                target = self._reference_resolver.resolve_reference(m.content)
                if not isinstance(target, Structure):
                    raise LSPGeneratorException("Non-Structure references in 'mixins' are not supported")
                props += target.properties

        props += struct.properties

        return props


    def generate_structure_definition(self, struct: Structure) -> str:
        superclasses: List[str] = []
        if struct.extends:
            for m in struct.extends:
                if not isinstance(m.content, ReferenceType):
                    raise LSPGeneratorException("Non-reference 'extends' values are not supported.")
                superclasses.append(m.content.name)

        properties = tuple(self.collect_structure_properties(struct))

        return self._generate_structure_definition_generic(struct.name, struct.documentation, properties, tuple(superclasses))


    def generate_enumeration_definition(self, enum: Enumeration) -> str:
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
                documentation = self._generate_documentation_comment(e.documentation)
            else:
                documentation = ""

            value = '\"' + str(e.value) + '\"' if enum.type.name == "string" else str(e.value)

            entry_definitions.append(f"{documentation}{e.name}: ClassVar[\"{enum.name}\"] = {value} # type: ignore")

        body = "\n\n".join(entry_definitions)

        return f'''\
class {enum.name}({", ".join(superclasses)}):
    """{enum.documentation if enum.documentation else ""}"""

{indent(body)}'''
