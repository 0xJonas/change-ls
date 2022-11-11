from keyword import iskeyword
from gen.schema.anytype import AndType, AnyType, ArrayType, BaseType, BooleanLiteralType, IntegerLiteralType, MapKeyType, MapType, OrType, Property, StringLiteralType, StructureLiteral, StructureLiteralType, TupleType
from gen.schema.types import Enumeration, MetaModel, Notification, ReferenceType, Request, Structure, TypeAlias

from typing import Any, ClassVar, Dict, List, Optional, Tuple, Union

from gen.schema.util import JSON_TYPE_NAME


class LSPGeneratorException(Exception):
    message: str

    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


def indent(text: str) -> str:
    return "\n".join(["    " + l for l in text.splitlines()])


def _generate_documentation_comment(documentation: str) -> str:
    out: List[str] = []
    for l in documentation.splitlines():
        l = l.replace("\\", "\\\\")
        l = "# " + l
        out.append(l)
    return "\n".join(out) + "\n"


def _escape_keyword(name: str) -> str:
    if iskeyword(name):
        return name + '_'
    else:
        return name


ref_target = Union[Enumeration, Structure, TypeAlias]

class ReferenceResolver:
    _enumeration_index: Dict[str, Enumeration]
    _structure_index: Dict[str, Structure]
    _type_alias_index: Dict[str, TypeAlias]

    def __init__(self, meta_model: MetaModel) -> None:
        self._enumeration_index = { e.name: e for e in meta_model.enumerations }
        self._structure_index = { s.name: s for s in meta_model.structures }
        self._type_alias_index = { t.name: t for t in meta_model.type_aliases }

    def _resolve_reference_internal(self, name: str, stack: List[str], resolve_typealiases: bool) -> Optional[ref_target]:
        if name in stack:
            raise LSPGeneratorException(f"Circular references: {stack + [name]}")
        if name in self._enumeration_index:
            return self._enumeration_index[name]
        elif name in self._structure_index:
            return self._structure_index[name]
        elif name in self._type_alias_index:
            type_alias = self._type_alias_index[name]
            if type_alias.type.kind == "reference" and resolve_typealiases:
                reference = type_alias.type.content
                assert isinstance(reference, ReferenceType)
                return self._resolve_reference_internal(reference.name, stack + [name], resolve_typealiases)
            else:
                return type_alias
        else:
            return None

    def resolve_reference(self, reference: ReferenceType, resolve_typealiases: bool=True) -> Optional[ref_target]:
        """Resolves a ReferenceType to its reference type in the MetaModel of this ReferenceResolver.

        This method will transparently resolve intermediate TypeAliases.
        Raises an LSPGeneratorException if circular references are detected. This is possible if a TypeAlias
        aliases a References which, either directly or indirectly points back to the same TypeAlias.

        Returns None if the referenced type was not found."""
        return self._resolve_reference_internal(reference.name, [], resolve_typealiases)


# All the types which end up in structures.py
structures_py_type = Union[Structure, StructureLiteral, TypeAlias, AndType]

class Generator:
    _meta_model: MetaModel
    _reference_resolver: ReferenceResolver

    _anonymous_structure_names: Dict[StructureLiteral, str]
    _anonymous_andtype_names: Dict[AndType, str]

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
        self._anonymous_structure_names = {}
        self._anonymous_andtype_names = {}


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
        elif val.kind == "reference":
            assert isinstance(val.content, ReferenceType)
            target = self._reference_resolver.resolve_reference(val.content)
            if isinstance(target, TypeAlias):
                return self._get_expected_json_type(target.type)
            elif isinstance(target, Enumeration):
                return "string" if target.type.name == "string" else "number (int)"
            else:
                return "object"
        elif val.kind in ["map", "and", "literal"]:
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

    # --------------------------------------------
    #              Parse Expressions
    # --------------------------------------------

    def _generate_parse_expression_base(self, base: BaseType, arg: str) -> str:
        # TODO validate URIs
        return arg


    def _generate_parse_expression_reference(self, reference: ReferenceType, arg: str) -> str:
        target = self._reference_resolver.resolve_reference(reference, resolve_typealiases=False)
        if isinstance(target, TypeAlias):
            return f"parse_{target.name}({arg})"
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
            if not isinstance(target, TypeAlias):
                print(target)
                raise LSPGeneratorException("A Reference in a map key must point to an AnyType.")
            json_expected_type = self._get_expected_json_type(target.type)
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
        return f"parse_or_type({arg}, ({', '.join(parse_functions)}))"


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
            assert isinstance(val.content, AndType)
            return f"{self._anonymous_andtype_names[val.content]}.from_json({arg})"
        elif val.kind == "or":
            assert isinstance(val.content, OrType)
            return self._generate_parse_expression_or(val.content, arg)
        elif val.kind == "tuple":
            assert isinstance(val.content, TupleType)
            return self._generate_parse_expression_tuple(val.content, arg)
        elif val.kind == "literal":
            assert isinstance(val.content, StructureLiteralType)
            return f"parse_{self._anonymous_structure_names[val.content.value]}({arg})"
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


    # --------------------------------------------
    #              Write Expressions
    # --------------------------------------------

    def generate_write_expression_reference(self, reference: ReferenceType, name: str) -> str:
        target = self._reference_resolver.resolve_reference(reference, resolve_typealiases=False)
        if isinstance(target, Enumeration):
            return name + ".value"
        elif isinstance(target, Structure):
            return name + ".to_json()"
        elif isinstance(target, TypeAlias):
            return f"write_{target.name}({name})"
        else:
            raise LSPGeneratorException("Reference pointing to an unsupported type.")


    def _generate_type_test(self, val: AnyType, name: str) -> str:
        if val.kind == "base":
            assert isinstance(val.content, BaseType)
            if val.content.name in ["URI", "DocumentUri", "RegExp", "string"]:
                return f"isinstance({name}, str)"
            elif val.content.name in ["integer", "uinteger"]:
                return f"isinstance({name}, int)"
            elif val.content.name == "decimal":
                return f"isinstance({name}, float)"
            elif val.content.name == "boolean":
                return f"isinstance({name}, bool)"
            else: # null
                return f"{name} is None"
        elif val.kind == "reference":
            assert isinstance(val.content, ReferenceType)
            target = self._reference_resolver.resolve_reference(val.content, resolve_typealiases=False)
            if isinstance(target, (Structure, Enumeration)):
                return f"isinstance({name}, {target.name})"
            elif isinstance(target, TypeAlias):
                if target.name == "LSPAny":
                    # Special case, because this type is mutually recursive with
                    # LSPArray and would cause infinite recursion in other parts.
                    return "True"
                else:
                    return self._generate_type_test(target.type, name)
            else:
                assert False
        elif val.kind == "array":
            assert isinstance(val.content, ArrayType)
            element_type_test = self._generate_type_test(val.content.element, name + "[0]")
            return f"isinstance({name}, List) and (len({name}) == 0 or ({element_type_test}))"
            # return f"isinstance({name}, List)"
        elif val.kind == "map":
            return f"isinstance({name}, Dict)"
        elif val.kind == "and":
            assert isinstance(val.content, AndType)
            structure_name = self._anonymous_andtype_names[val.content]
            return f"isinstance({name}, {structure_name})"
        elif val.kind == "or":
            assert isinstance(val.content, OrType)
            tests = ["(" + self._generate_type_test(i, name) + ")" for i in val.content.items]
            return " or ".join(tests)
        elif val.kind == "tuple":
            return f"isinstance({name}, Tuple)"
        elif val.kind == "literal":
            assert isinstance(val.content, StructureLiteralType)
            required_keys = [p.name for p in val.content.value.properties if not p.optional]
            key_checks = [f'"{key}" in {name}.keys()' for key in required_keys]
            return " and ".join([f"isinstance({name}, Dict)"] + key_checks)
        elif val.kind == "stringLiteral":
            assert isinstance(val.content, StringLiteralType)
            return f'{name} == "{val.content.value}"'
        elif val.kind == "integerLiteral":
            assert isinstance(val.content, IntegerLiteralType)
            return f"{name} == {val.content.value}"
        elif val.kind == "booleanLiteral":
            assert isinstance(val.content, BooleanLiteralType)
            return f"{name} == {val.content.value}"
        else:
            assert False # Broken AnyType


    def _generate_write_expression_or(self, val: OrType, name: str) -> str:
        kinds = [i.kind for i in val.items]

        # Currently we cannot check generic type parameters, so if this
        # is ever required to disambiguate, assert here.
        # if not kinds.count("array") <= 1:
        #     print(val)
        # assert kinds.count("array") <= 1
        assert kinds.count("map") <= 1
        assert kinds.count("tuple") <= 1

        type_tests = [f"lambda i: {self._generate_type_test(i, 'i')}" for i in val.items]
        writers = [f"lambda i: {self.generate_write_expression(i, 'i')}" for i in val.items]

        return f"write_or_type({name}, ({', '.join(type_tests)}), ({', '.join(writers)}))"


    def generate_write_expression(self, val: AnyType, name: str) -> str:
        if val.kind == "base":
            return name
        elif val.kind == "reference":
            assert isinstance(val.content, ReferenceType)
            return self.generate_write_expression_reference(val.content, name)
        elif val.kind == "array":
            assert isinstance(val.content, ArrayType)
            return f"[{self.generate_write_expression(val.content.element, 'i')} for i in {name}]"
        elif val.kind == "map":
            assert isinstance(val.content, MapType)
            if isinstance(val.content.key, MapKeyType):
                write_key_expression = "key" # Whatever the actual type is, all valid MapKeyTypes can be written directly.
            else:
                write_key_expression = self.generate_write_expression_reference(val.content.key, "key")
            write_value_expression = self.generate_write_expression(val.content.value, "val")
            return f"{{ {write_key_expression}: {write_value_expression} for key, val in {name}.items() }}"
        elif val.kind == "and":
            assert isinstance(val.content, AndType)
            return f"{name}.to_json()"
        elif val.kind == "or":
            assert isinstance(val.content, OrType)
            return self._generate_write_expression_or(val.content, name)
        elif val.kind == "tuple":
            assert isinstance(val.content, TupleType)
            return f"list({name})"
        elif val.kind == "literal":
            assert isinstance(val.content, StructureLiteralType)
            return f"write_{self._anonymous_structure_names[val.content.value]}({name})"
        elif val.kind == "stringLiteral":
            assert isinstance(val.content, StringLiteralType)
            return '"' + val.content.value + '"'
        elif val.kind == "integerLiteral":
            assert isinstance(val.content, IntegerLiteralType)
            return str(val.content.value)
        elif val.kind == "booleanLiteral":
            assert isinstance(val.content, BooleanLiteralType)
            return str(val.content.value)
        else:
            assert False # Broken AnyType


    # --------------------------------------------
    #              Type Annotations
    # --------------------------------------------

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
            # Some types are mutually recursive,
            # so we need to use a string literal type annotation
            return '"' + val.content.name + '"'
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
            return self._anonymous_andtype_names[val.content]
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
            return f"Dict[{self._anonymous_structure_names[val.content.value]}Keys, Any]"
        elif val.kind == "stringLiteral":
            return "str"
        elif val.kind == "integerLiteral":
            return "int"
        elif val.kind == "booleanLiteral":
            return "bool"
        else:
            assert False # Broken AnyType


    # --------------------------------------------
    #             Definition Ordering
    # --------------------------------------------

    def get_referenced_definitions_anytype(self, val: AnyType) -> List[Union[ref_target, StructureLiteral, AndType]]:
        if val.kind == "reference":
            assert isinstance(val.content, ReferenceType)
            target = self._reference_resolver.resolve_reference(val.content, resolve_typealiases=False)
            assert target != None
            return [target]
        elif val.kind == "array":
            assert isinstance(val.content, ArrayType)
            return self.get_referenced_definitions_anytype(val.content.element)
        elif val.kind == "map":
            assert isinstance(val.content, MapType)
            out: List[Any] = []
            if isinstance(val.content.key, ReferenceType):
                out.append(self._reference_resolver.resolve_reference(val.content.key, resolve_typealiases=False))
            if isinstance(val.content.value.content, ReferenceType):
                out.append(self._reference_resolver.resolve_reference(val.content.value.content, resolve_typealiases=False))
            return out
        elif val.kind == "and":
            assert isinstance(val.content, AndType)
            return [val.content]
        elif val.kind == "or":
            assert isinstance(val.content, OrType)
            out: List[Any] = []
            for i in val.content.items:
                out += self.get_referenced_definitions_anytype(i)
            return out
        elif val.kind == "tuple":
            assert isinstance(val.content, TupleType)
            out: List[Any] = []
            for i in val.content.items:
                out += self.get_referenced_definitions_anytype(i)
            return out
        elif val.kind == "literal":
            assert isinstance(val.content, StructureLiteralType)
            return [val.content.value]
        elif val.kind in ["base", "stringLiteral", "integerLiteral", "booleanLiteral"]:
            return []
        else:
            assert False # Broken AnyType


    def get_referenced_definitions(self, obj: Union[Notification, Request, Structure, TypeAlias, StructureLiteral, AndType]) -> List[Union[ref_target, StructureLiteral, AndType]]:
        if isinstance(obj, Enumeration):
            return []
        elif isinstance(obj, Notification):
            out: List[Union[ref_target, StructureLiteral, AndType]] = []

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
            out: List[Union[ref_target, StructureLiteral, AndType]] = []

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
            out: List[Union[ref_target, StructureLiteral, AndType]] = []

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
            out: List[Union[ref_target, StructureLiteral, AndType]] = []
            for p in obj.properties:
                out += self.get_referenced_definitions_anytype(p.type)
            return out
        else: # isinstance(obj, AndType)
            out: List[Union[ref_target, StructureLiteral, AndType]] = []
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

            self.sort_structures_and_typealiases_rec(r, status, list)

        list.append(obj)
        status[obj] = "visited"


    def sort_structures_and_typealiases(self) -> List[structures_py_type]:
        """Topologically sorts Structures and TypeAliases, so that the definitions can
        be generated in a valid order."""
        status: Dict[structures_py_type, str] = {}
        list: List[structures_py_type] = []

        for s in self._meta_model.structures:
            self.sort_structures_and_typealiases_rec(s, status, list)

        for t in self._meta_model.type_aliases:
            self.sort_structures_and_typealiases_rec(t, status, list)

        for s in self._anonymous_structure_names.keys():
            self.sort_structures_and_typealiases_rec(s, status, list)

        for a in self._anonymous_andtype_names.keys():
            self.sort_structures_and_typealiases_rec(a, status, list)

        return list

    # --------------------------------------------
    #            Structure Definitions
    # --------------------------------------------

    def _generate_property_declaration(self, prop: Property) -> str:
        """Generates declaration code for a `Property`."""
        type_annotation = self._generate_type_annotation(prop.type)
        if prop.optional:
            type_annotation = f"Optional[{type_annotation}]"

        if prop.documentation:
            documentation = _generate_documentation_comment(prop.documentation)
        else:
            documentation = ""


        return f"{documentation}{_escape_keyword(prop.name)}: {type_annotation}"


    def _generate_property_read_statement(self, prop: Property, obj_name: str, anonymous_struct: bool = False, dest_name: str = "") -> str:
        """Generates a statement that reads the given `Property` from the JSON object `obj_name`."""
        if anonymous_struct:
            dest = f'{dest_name}["{prop.name}"]'
        else:
            dest = _escape_keyword(prop.name)

        if prop.optional:
            if expected_json_type := self._get_expected_json_type(prop.type):
                get_json_expr = self._json_type_to_get_optional_function[expected_json_type] + f'({obj_name}, "{prop.name}")'
            else:
                get_json_expr = f'{obj_name}.get("{prop.name}")'

            parse_expression = self.generate_parse_expression(prop.type, f"{prop.name}_json")
            return f"""\
if {prop.name}_json := {get_json_expr}:
    {dest} = {parse_expression}
else:
    {dest} = None"""

        else:
            if expected_json_type := self._get_expected_json_type(prop.type):
                get_json_expr = self._json_type_to_get_function[expected_json_type] + f'({obj_name}, "{prop.name}")'
            else:
                get_json_expr = f'{obj_name}["{prop.name}"]'

            parse_expression = self.generate_parse_expression(prop.type, get_json_expr)
            return f"{dest} = {parse_expression}"


    def _generate_property_write_statement(self, prop: Property, obj_name: str, anonymous_structure: bool = False, source_name: str = "") -> str:
        if anonymous_structure:
            if prop.optional:
                source = f'{source_name}.get("{prop.name}")'
            else:
                source = f'{source_name}["{prop.name}"]'
        else:
            source = "self." + _escape_keyword(prop.name)

        write_statement = f'{obj_name}["{prop.name}"] = {self.generate_write_expression(prop.type, source)}'
        if prop.optional:
            write_statement = f"if {source} is not None:\n    " + write_statement
        return write_statement


    def _generate_structure_init_method_documentation(self, properties: Tuple[Property, ...]) -> str:
        docstring_lines: List[str] = []
        for p in properties:
            if not p.documentation:
                continue
            lines = p.documentation.splitlines()
            docstring_lines.append(f"- {p.name}: {lines[0]}")
            docstring_lines += ["    " + l for l in lines[1:]]
        return "\n".join(docstring_lines)


    def _generate_structure_init_method(self, properties: Tuple[Property, ...]) -> str:
        if len(properties) == 0:
            return ""

        documentation = self._generate_structure_init_method_documentation(properties)

        parameters: List[str] = []
        for p in properties:
            if p.optional:
                parameters.append(f"{_escape_keyword(p.name)}: Optional[{self._generate_type_annotation(p.type)}] = None")
            else:
                parameters.append(f"{_escape_keyword(p.name)}: {self._generate_type_annotation(p.type)}")

        names = [_escape_keyword(p.name) for p in properties]
        assignments = [f"self.{n} = {n}" for n in names]
        sep = "\n"
        return f'''\
def __init__(self, *, {", ".join(parameters)}) -> None:
    """
{indent(documentation)}
    """
{indent(sep.join(assignments))}'''


    def _generate_structure_from_json_method(self, class_name: str, properties: Tuple[Property]) -> str:
        property_read_statements = "\n".join([self._generate_property_read_statement(p, "obj") for p in properties])
        property_names = ", ".join([_escape_keyword(p.name) + "=" + _escape_keyword(p.name) for p in properties])
        return f"""\
@classmethod
def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "{class_name}":
{indent(property_read_statements)}
    return cls({property_names})"""


    def _generate_structure_to_json_method(self, properties: Tuple[Property]) -> str:
        property_write_statements = "\n".join([self._generate_property_write_statement(p, "out") for p in properties])
        return f"""\
def to_json(self) -> Dict[str, JSON_VALUE]:
    out: Dict[str, JSON_VALUE] = {{}}
{indent(property_write_statements)}
    return out"""


    def _generate_structure_definition_generic(self, class_name: str, documentation: Optional[str], properties: Tuple[Property], superclasses: Tuple[str, ...]) -> str:
        doc = documentation if documentation else ""
        property_declarations = "\n\n".join([self._generate_property_declaration(p) for p in properties])

        return f'''\
@dataclass
class {class_name}({", ".join(superclasses)}):
    """{doc}"""

{indent(property_declarations)}

{indent(self._generate_structure_init_method(properties))}

{indent(self._generate_structure_from_json_method(class_name, properties))}

{indent(self._generate_structure_to_json_method(properties))}'''


    def _generate_and_type_name(self, val: AndType) -> str:
        item_names: List[str] = []
        for i in val.items:
            assert isinstance(i.content, ReferenceType)
            item_names.append(i.content.name)
        item_names.sort()
        return "And".join(item_names)


    def _add_anonymous_definitions_from_anytype(self, val: AnyType) -> None:
        """Adds a definition to the list of anonymous definitions for the given anytype.
        If `val` is an aggregate type, definitions are created recursively for all
        encountered anonymous types (literal, and). Recursion stops if a type is not an
        anonymous structure."""

        if val.kind in ["base", "reference", "stringLiteral", "integerLiteral", "booleanLiteral"]:
            return
        elif val.kind == "array":
            assert isinstance(val.content, ArrayType)
            self._add_anonymous_definitions_from_anytype(val.content.element)
        elif val.kind == "map":
            assert isinstance(val.content, MapType)
            self._add_anonymous_definitions_from_anytype(val.content.value)
        elif val.kind == "and":
            assert isinstance(val.content, AndType)
            for i in val.content.items:
                self._add_anonymous_definitions_from_anytype(i)

            self._anonymous_andtype_names[val.content] = self._generate_and_type_name(val.content)
        elif val.kind == "or":
            assert isinstance(val.content, OrType)
            for i in val.content.items:
                self._add_anonymous_definitions_from_anytype(i)
        elif val.kind == "tuple":
            assert isinstance(val.content, TupleType)
            for i in val.content.items:
                self._add_anonymous_definitions_from_anytype(i)
        elif val.kind == "literal":
            assert isinstance(val.content, StructureLiteralType)
            for i in val.content.value.properties:
                self._add_anonymous_definitions_from_anytype(i.type)

            if val.content.value in self._anonymous_structure_names:
                # The code below is expected to always add a new name
                # to the _anonymus_structure_names dict. However, because
                # the metamodel defines several empty structures which
                # hash to the same value, this is not always the case.
                # If we encounter an already existing structure, we can
                # simply return here.
                return

            class_name = "AnonymousStructure" + str(len(self._anonymous_structure_names))
            self._anonymous_structure_names[val.content.value] = class_name


    def generate_anonymous_structure_names(self) -> None:
        """Traverses the `MetaModel` and generates definitions for all
        anonymus types used"""

        for n in self._meta_model.notifications:
            if n.params:
                if isinstance(n.params, Tuple):
                    for p in n.params:
                        self._add_anonymous_definitions_from_anytype(p)
                else:
                    self._add_anonymous_definitions_from_anytype(n.params)

            if n.registration_options:
                self._add_anonymous_definitions_from_anytype(n.registration_options)

        for r in self._meta_model.requests:
            if r.error_data:
                self._add_anonymous_definitions_from_anytype(r.error_data)

            if r.params:
                if isinstance(r.params, Tuple):
                    for p in r.params:
                        self._add_anonymous_definitions_from_anytype(p)
                else:
                    self._add_anonymous_definitions_from_anytype(r.params)

            if r.partial_result:
                self._add_anonymous_definitions_from_anytype(r.partial_result)

            if r.registration_options:
                self._add_anonymous_definitions_from_anytype(r.registration_options)

            self._add_anonymous_definitions_from_anytype(r.result)

        for s in self._meta_model.structures:
            if s.extends:
                for p in s.extends:
                    self._add_anonymous_definitions_from_anytype(p)

            if s.mixins:
                for p in s.mixins:
                    self._add_anonymous_definitions_from_anytype(p)

            for p in s.properties:
                self._add_anonymous_definitions_from_anytype(p.type)

        for t in self._meta_model.type_aliases:
            self._add_anonymous_definitions_from_anytype(t.type)


    def collect_structure_properties(self, struct: Structure) -> List[Property]:
        # Use a dict instead of a List, so that the properties from
        # derived classes can override those from the base classes
        props: Dict[str, Property] = {}

        if struct.extends:
            for m in struct.extends:
                if not isinstance(m.content, ReferenceType):
                    raise LSPGeneratorException("Non-reference 'extends' values are not supported.")
                target = self._reference_resolver.resolve_reference(m.content)
                if not isinstance(target, Structure):
                    raise LSPGeneratorException("Non-Structure references in 'extends' are not supported")
                props.update({ p.name: p for p in self.collect_structure_properties(target)})

        if struct.mixins:
            for m in struct.mixins:
                if not isinstance(m.content, ReferenceType):
                    raise LSPGeneratorException("Non-reference 'mixins' values are not supported.")
                target = self._reference_resolver.resolve_reference(m.content)
                if not isinstance(target, Structure):
                    raise LSPGeneratorException("Non-Structure references in 'mixins' are not supported")
                props.update({ p.name: p for p in target.properties})

        props.update({ p.name: p for p in struct.properties})

        return list(props.values())


    def generate_andtype_definition(self, val: AndType) -> str:
        name = self._anonymous_andtype_names[val]
        properties: List[Property] = []
        for i in val.items:
            if not isinstance(i.content, ReferenceType):
                raise LSPGeneratorException("AndType items must be references")
            target = self._reference_resolver.resolve_reference(i.content)
            if isinstance(target, Structure):
                properties += self.collect_structure_properties(target)
            elif isinstance(target, StructureLiteral):
                properties += target.properties
            else:
                raise LSPGeneratorException("AndType items must refer to structures")
        return self._generate_structure_definition_generic(name, None, tuple(properties), ())


    def _generate_anonymous_structure_key_type_alias(self, val: StructureLiteral) -> str:
        name = f"{self._anonymous_structure_names[val]}Keys"
        if len(val.properties) == 0:
            return name + " = Literal[None]"

        type_names = ['"' + p.name + '"' for p in val.properties]
        return f"{name} = Literal[{','.join(type_names)}]"


    def _generate_anonymous_structure_read_fun(self, val: StructureLiteral) -> str:
        name = self._anonymous_structure_names[val]
        read_statements = [self._generate_property_read_statement(p, "obj", True, "out") for p in val.properties]
        sep = "\n"
        return f"""\
def parse_{name}(obj: Mapping[str, JSON_VALUE]) -> Dict[{name}Keys, Any]:
    out: Dict[{name}Keys, Any] = {{}}
{indent(sep.join(read_statements))}
    return out"""


    def _generate_anonymous_structure_write_fun(self, val: StructureLiteral) -> str:
        name = self._anonymous_structure_names[val]
        write_statements = [self._generate_property_write_statement(p, "out", True, "obj") for p in val.properties]
        sep = "\n"
        return f"""\
def write_{name}(obj: Dict[{name}Keys, Any]) -> JSON_VALUE:
    out: JSON_VALUE = {{}}
{indent(sep.join(write_statements))}
    return out"""


    def generate_anonymous_structure_definition(self, val: StructureLiteral) -> str:
        return f"""\
{self._generate_anonymous_structure_key_type_alias(val)}

{self._generate_anonymous_structure_read_fun(val)}

{self._generate_anonymous_structure_write_fun(val)}"""



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
                documentation = _generate_documentation_comment(e.documentation)
            else:
                documentation = ""

            value = '\"' + str(e.value) + '\"' if enum.type.name == "string" else str(e.value)

            entry_definitions.append(f"{documentation}{_escape_keyword(e.name)}: ClassVar[\"{enum.name}\"] = {value} # type: ignore")

        body = "\n\n".join(entry_definitions)

        return f'''\
class {enum.name}({", ".join(superclasses)}):
    """{enum.documentation if enum.documentation else ""}"""

{indent(body)}'''


    def generate_typealias_definition(self, typealias: TypeAlias) -> str:
        documentation = _generate_documentation_comment(typealias.documentation) if typealias.documentation else ""

        annotation = self._generate_type_annotation(typealias.type)
        if annotation[0] == '"' and annotation[-1] == '"':
            # If the type annotation is quoted, the generated code will look like
            #   typealias = "type"
            # which is interpreted as setting a string variable. So we un-quote the annotation
            # here and hope that it does not cause problems with forward declarations.
            annotation = annotation[1: -1]

        definition = f"{documentation}{typealias.name} = {annotation}"
        expected_json_type = self._get_expected_json_type(typealias.type)
        if expected_json_type:
            assert_fun = self._json_type_to_assert_function[expected_json_type]
        else:
            assert_fun = ""
        parse_fun = f"""\
def parse_{typealias.name}(arg: JSON_VALUE) -> {typealias.name}:
    return {self.generate_parse_expression(typealias.type, f"{assert_fun}(arg)")}"""

        write_fun = f"""\
def write_{typealias.name}(arg: {typealias.name}) -> JSON_VALUE:
    return {self.generate_write_expression(typealias.type, "arg")}"""

        return definition + "\n\n" + parse_fun + "\n\n" + write_fun


    def generate_enumerations_py(self) -> str:
        definitions: List[str] = [self.generate_enumeration_definition(e) for e in self._meta_model.enumerations]
        imports = """\
from typing import ClassVar
from .lsp_enum import AllowCustomValues, TypedLSPEnum


"""
        return imports + "\n\n\n".join(definitions)


    def generate_structures_py(self) -> str:
        self.generate_anonymous_structure_names()
        sorted_types = self.sort_structures_and_typealiases()

        definitions: List[str] = []

        for t in sorted_types:
            if isinstance(t, TypeAlias):
                definitions.append(self.generate_typealias_definition(t))
            elif isinstance(t, Structure):
                definitions.append(self.generate_structure_definition(t))
            elif isinstance(t, StructureLiteral):
                definitions.append(self.generate_anonymous_structure_definition(t))
            else: # isinstance(t, AndType)
                definitions.append(self.generate_andtype_definition(t))

        sep = "\n\n\n"
        return f"""\
from .util import *
from .enumerations import *

from dataclasses import dataclass
from typing import Dict, List, Literal, Mapping, Optional, Tuple, Union


{sep.join(definitions)}
"""


    def _generate_parse_lambda(self, val: AnyType) -> str:
        expected_json_type = self._get_expected_json_type(val)
        if expected_json_type:
            assert_fun = self._json_type_to_assert_function[expected_json_type]
        else:
            assert_fun = ""
        return f'lambda p: {self.generate_parse_expression(val, f"{assert_fun}(p)")}'


    def generate_dispatch_py(self) -> str:
        parse_request_params: List[str] = []
        parse_request_result: List[str] = []
        parse_request_partial_result: List[str] = []
        write_request_params: List[str] = []
        write_request_result: List[str] = []
        write_request_partial_result: List[str] = []

        for r in self._meta_model.requests:
            # print(r)
            if r.params:
                assert not isinstance(r.params, Tuple)  # TODO implement
                parse_request_params.append(f'"{r.method}": {self._generate_parse_lambda(r.params)}')
                write_request_params.append(f'"{r.method}": lambda p: {self.generate_write_expression(r.params, "p")}')

            parse_request_result.append(f'"{r.method}": {self._generate_parse_lambda(r.result)}')
            write_request_result.append(f'"{r.method}": lambda p: {self.generate_write_expression(r.result, "p")}')

            if r.partial_result:
                parse_request_partial_result.append(f'"{r.method}": {self._generate_parse_lambda(r.partial_result)}')
                write_request_partial_result.append(f'"{r.method}": lambda p: {self.generate_write_expression(r.partial_result, "p")}')

        parse_notification_params: List[str] = []
        write_notification_params: List[str] = []

        for n in self._meta_model.notifications:
            if n.params:
                assert not isinstance(n.params, Tuple)  # TODO implement
                parse_notification_params.append(f'"{n.method}": {self._generate_parse_lambda(n.params)}')
                write_notification_params.append(f'"{n.method}": lambda p: {self.generate_write_expression(n.params, "p")}')

        sep = ",\n"
        return f"""\
from .util import *
from .enumerations import *
from .structures import *


parse_request_params: Dict[str, Callable[[JSON_VALUE], Any]] = {{
{indent(sep.join(parse_request_params))}
}}

write_request_params: Dict[str, Callable[[Any], JSON_VALUE]] = {{
{indent(sep.join(write_request_params))}
}}


parse_request_result: Dict[str, Callable[[JSON_VALUE], Any]] = {{
{indent(sep.join(parse_request_result))}
}}

write_request_result: Dict[str, Callable[[Any], JSON_VALUE]] = {{
{indent(sep.join(write_request_result))}
}}


parse_request_partial_result: Dict[str, Callable[[JSON_VALUE], Any]] = {{
{indent(sep.join(parse_request_partial_result))}
}}

write_request_partial_result: Dict[str, Callable[[Any], JSON_VALUE]] = {{
{indent(sep.join(write_request_partial_result))}
}}


parse_notification_params: Dict[str, Callable[[JSON_VALUE], Any]] = {{
{indent(sep.join(parse_notification_params))}
}}

write_notification_params: Dict[str, Callable[[Any], JSON_VALUE]] = {{
{indent(sep.join(write_notification_params))}
}}
"""
