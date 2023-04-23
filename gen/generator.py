from typing import Dict, List, Optional, Tuple, Union

from gen.gen_util import (LSPGeneratorException, dedent_ignore_empty, indent,
                          json_type_to_assert_function, ref_target)
from gen.schema.anytype import (AndType, AnyType, ArrayType, BaseType,
                                BooleanLiteralType, IntegerLiteralType,
                                MapKeyType, MapType, OrType, Property,
                                StringLiteralType, StructureLiteral,
                                StructureLiteralType, TupleType)
from gen.schema.types import (Enumeration, MetaModel, ReferenceType, Structure,
                              TypeAlias)
from gen.schema.util import JSON_TYPE_NAME


class ReferenceResolver:
    _enumeration_index: Dict[str, Enumeration]
    _structure_index: Dict[str, Structure]
    _type_alias_index: Dict[str, TypeAlias]

    def __init__(self, meta_model: MetaModel) -> None:
        self._enumeration_index = {e.name: e for e in meta_model.enumerations}
        self._structure_index = {s.name: s for s in meta_model.structures}
        self._type_alias_index = {t.name: t for t in meta_model.type_aliases}

    def resolve_reference(self, name: str, resolve_typealiases: bool, stack: List[str] = []) -> Optional[ref_target]:
        if name in stack:
            raise LSPGeneratorException(
                f"Circular references: {stack + [name]}")
        if name in self._enumeration_index:
            return self._enumeration_index[name]
        elif name in self._structure_index:
            return self._structure_index[name]
        elif name in self._type_alias_index:
            type_alias = self._type_alias_index[name]
            if type_alias.type.kind == "reference" and resolve_typealiases:
                reference = type_alias.type.content
                assert isinstance(reference, ReferenceType)
                return self.resolve_reference(reference.name, resolve_typealiases, stack + [name])
            else:
                return type_alias
        else:
            return None


class Generator:
    _meta_model: MetaModel
    _reference_resolver: ReferenceResolver

    _anonymous_structure_names: Dict[StructureLiteral, str]
    _anonymous_andtype_names: Dict[AndType, str]

    def __init__(self, meta_model: MetaModel) -> None:
        self._meta_model = meta_model
        self._reference_resolver = ReferenceResolver(meta_model)
        self._anonymous_structure_names = {}
        self._anonymous_andtype_names = {}
        self._generate_anonymous_structure_names()

    def get_meta_model(self) -> MetaModel:
        return self._meta_model

    def resolve_reference(self, reference: ReferenceType, resolve_typealiases: bool = True) -> Optional[ref_target]:
        """
        Resolves a ReferenceType to its reference type in the MetaModel of this Generator.

        This method will transparently resolve intermediate TypeAliases.
        Raises an LSPGeneratorException if circular references are detected. This is possible if a TypeAlias
        aliases a References which, either directly or indirectly points back to the same TypeAlias.

        Returns None if the referenced type was not found.
        """
        return self._reference_resolver.resolve_reference(reference.name, resolve_typealiases)

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
            assert False  # Broken BaseType

    def _get_expected_json_type_mapkey(self, key: MapKeyType) -> JSON_TYPE_NAME:
        """Returns the variant `JSON_VALUE` which values of the given `MapKeyType` are expected to have."""
        if key.name in ["URI", "DocumentUri", "string"]:
            return "string"
        elif key.name == "integer":
            return "number (int)"
        else:
            assert False  # Broken MapKeyType

    def get_expected_json_type(self, val: AnyType) -> Optional[JSON_TYPE_NAME]:
        """Returns the variant of `JSON_VALUE` which values of the given `AnyType` are expected to have."""
        if val.kind == "base":
            assert isinstance(val.content, BaseType)
            return self._get_expected_json_type_base(val.content)
        elif val.kind == "reference":
            assert isinstance(val.content, ReferenceType)
            target = self.resolve_reference(val.content)
            if isinstance(target, TypeAlias):
                return self.get_expected_json_type(target.type)
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
            assert False  # Broken AnyType

    # --------------------------------------------
    #              Parse Expressions
    # --------------------------------------------

    def _generate_parse_expression_base(self, base: BaseType, arg: str) -> str:
        # TODO validate URIs
        return arg

    def _generate_parse_expression_reference(self, reference: ReferenceType, arg: str) -> str:
        target = self.resolve_reference(reference, resolve_typealiases=False)
        if isinstance(target, TypeAlias):
            return f"parse_{target.name}({arg})"
        elif isinstance(target, Structure):
            return f"{reference.name}.from_json({arg})"
        elif isinstance(target, Enumeration):
            return f"{reference.name}({arg})"
        else:
            raise LSPGeneratorException(
                "Reference pointing to an unsupported type.")

    def _generate_parse_expression_mapping(self, map: MapType, arg: str) -> str:
        """
        Generates an expression that parses the given `MapType` from the given `arg`.
        The expression evaluates to a Python dict, which maps arbitrary instances of the
        map's key type to instances of the map's value type.
        """
        if isinstance(map.key, MapKeyType):
            assert_type_func_key = json_type_to_assert_function[self._get_expected_json_type_mapkey(
                map.key)]
        else:
            target = self.resolve_reference(map.key)
            if not isinstance(target, TypeAlias):
                print(target)
                raise LSPGeneratorException(
                    "A Reference in a map key must point to an AnyType.")
            json_expected_type = self.get_expected_json_type(target.type)
            if not json_expected_type:
                raise LSPGeneratorException("Weird AnyType in a map key.")
            assert_type_func_key = json_type_to_assert_function[json_expected_type]

        if expected_json_type_value := self.get_expected_json_type(map.value):
            assert_type_func_value = json_type_to_assert_function[expected_json_type_value]
        else:
            assert_type_func_value = ""

        parse_expression_arg = f"{assert_type_func_value}(value)"
        return f"{{ {assert_type_func_key}(key): {self.generate_parse_expression(map.value, parse_expression_arg)} for key, value in {arg}.items()}}"

    def _get_or_item_priority(self, item: AnyType) -> int:
        """
        Computes a priority for an item of an OrType.

        These priorities control in which order the parses for
        the items are attempted. The first item which successfully
        parses is returned. No subsequent items are attempted, even
        if they would parse successfully as well.
        """
        if not isinstance(item.content, ReferenceType):
            return 0

        target = self.resolve_reference(item.content)
        if not target:
            return 0

        if isinstance(target, Structure):
            return len(self.collect_structure_properties(target))
        else:
            return 0

    def _sort_or_items(self, items: Tuple[AnyType, ...]) -> List[AnyType]:
        """
        Returns the given list of items sorted by priority.

        See `_get_or_item_priority` for how priorities are used with OrTypes.
        """
        out = list(items)
        out.sort(key=lambda i: self._get_or_item_priority(i), reverse=True)
        return out

    def _generate_parse_expression_or(self, or_val: OrType, arg: str) -> str:
        """
        Generate an expression that parses the given `OrType` which is contained
        in a variable with the name given in `arg`.
        """
        parse_functions: List[str] = []
        items = self._sort_or_items(or_val.items)
        for i in items:
            if expected_json_type := self.get_expected_json_type(i):
                assert_type_func = json_type_to_assert_function[expected_json_type]
            else:
                assert_type_func = ""
            parse_func_arg = f"{assert_type_func}(v)"
            parse_functions.append(
                f"lambda v: {self.generate_parse_expression(i, parse_func_arg)}")
        return f"parse_or_type({arg}, ({', '.join(parse_functions)}))"

    def _generate_parse_expression_tuple(self, tuple: TupleType, arg: str) -> str:
        """
        Generates an expression that parses the given `TupleType` from the given `arg`.
        The returned expression evaluates to a Python tuple which contains the types defined in the `TupleType`
        """
        parse_expressions: List[str] = []
        for i, t in enumerate(tuple.items):
            json_type = self.get_expected_json_type(t)
            assert_fun = json_type_to_assert_function[json_type] if json_type else ""
            parse_expressions.append(self.generate_parse_expression(
                t, f"{assert_fun}({arg}[{i}])"))
        return "(" + ", ".join(parse_expressions) + ")"

    def generate_parse_expression(self, val: AnyType, arg: str) -> str:
        """
        Generate an expression that will parse the value in `arg` into the type denoted by `val`.
        `arg` should be an expression that evaluates to a `JSON_VALUE`.
        """
        if val.kind == "base":
            assert isinstance(val.content, BaseType)
            return self._generate_parse_expression_base(val.content, arg)
        elif val.kind == "reference":
            assert isinstance(val.content, ReferenceType)
            return self._generate_parse_expression_reference(val.content, arg)
        elif val.kind == "array":
            assert isinstance(val.content, ArrayType)
            json_type = self.get_expected_json_type(val.content.element)
            assert_fun = json_type_to_assert_function[json_type] if json_type else ""
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
            return f"_parse_{self._anonymous_structure_names[val.content.value]}({arg})"
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
            assert False  # Broken AnyType

    # --------------------------------------------
    #              Write Expressions
    # --------------------------------------------

    def _generate_write_expression_reference(self, reference: ReferenceType, name: str) -> str:
        """
        Generates an expression which creates a `JSON_VALUE` representing the given `reference`.

        The expression will be different depending on what the `reference` points to.
        """
        target = self.resolve_reference(reference, resolve_typealiases=False)
        if isinstance(target, Enumeration):
            return name + ".value"
        elif isinstance(target, Structure):
            return name + ".to_json()"
        elif isinstance(target, TypeAlias):
            return f"write_{target.name}({name})"
        else:
            raise LSPGeneratorException(
                "Reference pointing to an unsupported type.")

    def _generate_type_test(self, val: AnyType, name: str) -> str:
        """
        Generates an expression which tests if the variable with the name given in `name`
        has the type given in `val`.

        Type tests are used when creating `JSON_VALUEs` for `OrTypes`.
        """
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
            else:  # null
                return f"{name} is None"
        elif val.kind == "reference":
            assert isinstance(val.content, ReferenceType)
            target = self.resolve_reference(
                val.content, resolve_typealiases=False)
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
            element_type_test = self._generate_type_test(
                val.content.element, name + "[0]")
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
            tests = ["(" + self._generate_type_test(i, name) +
                     ")" for i in val.content.items]
            return " or ".join(tests)
        elif val.kind == "tuple":
            return f"isinstance({name}, Tuple)"
        elif val.kind == "literal":
            assert isinstance(val.content, StructureLiteralType)
            required_keys = [
                p.name for p in val.content.value.properties if not p.optional]
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
            assert False  # Broken AnyType

    def _generate_write_expression_or(self, val: OrType, name: str) -> str:
        """
        Generates an expression which creates a `JSON_VALUE` from a variable with a name given in `name`,
        using the items from the `OrType` in `val`.
        """
        kinds = [i.kind for i in val.items]

        # Currently we cannot check generic type parameters, so if this
        # is ever required to disambiguate, assert here.
        # if not kinds.count("array") <= 1:
        #     print(val)
        # assert kinds.count("array") <= 1
        assert kinds.count("map") <= 1
        assert kinds.count("tuple") <= 1

        type_tests = [
            f"lambda i: {self._generate_type_test(i, 'i')}" for i in val.items]
        writers = [
            f"lambda i: {self.generate_write_expression(i, 'i')}" for i in val.items]

        return f"write_or_type({name}, ({', '.join(type_tests)}), ({', '.join(writers)}))"

    def generate_write_expression(self, val: AnyType, name: str) -> str:
        """
        Generates an expression which creates a `JSON_VALUE` from the variable in `name` of the type
        given in `val`.
        """
        if val.kind == "base":
            return name
        elif val.kind == "reference":
            assert isinstance(val.content, ReferenceType)
            return self._generate_write_expression_reference(val.content, name)
        elif val.kind == "array":
            assert isinstance(val.content, ArrayType)
            return f"[{self.generate_write_expression(val.content.element, 'i')} for i in {name}]"
        elif val.kind == "map":
            assert isinstance(val.content, MapType)
            if isinstance(val.content.key, MapKeyType):
                # Whatever the actual type is, all valid MapKeyTypes can be written directly.
                write_key_expression = "key"
            else:
                write_key_expression = self._generate_write_expression_reference(
                    val.content.key, "key")
            write_value_expression = self.generate_write_expression(
                val.content.value, "val")
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
            return f"_write_{self._anonymous_structure_names[val.content.value]}({name})"
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
            assert False  # Broken AnyType

    # --------------------------------------------
    #              Type Annotations
    # --------------------------------------------

    def _generate_type_annotation_base(self, base: BaseType) -> str:
        """Generates a type annotation for the `BaseType` given in `base`."""

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
            assert False  # Broken BaseType

    def _generate_type_annotation_mapkey(self, key: MapKeyType) -> str:
        """Returns the variant `JSON_VALUE` which values of the given `MapKeyType` are expected to have."""

        if key.name in ["URI", "DocumentUri", "string"]:
            return "str"
        elif key.name == "integer":
            return "int"
        else:
            assert False  # Broken MapKeyType

    def _generate_type_annotation_literal(self, literal: StructureLiteralType) -> str:
        if len(literal.value.properties) == 0:
            property_names = None
        else:
            property_names = ",".join('"' + p.name + '"' for p in literal.value.properties)
        return f"Dict[Literal[{property_names}], Any]"

    def generate_type_annotation(self, val: AnyType) -> str:
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
            return f"List[{self.generate_type_annotation(val.content.element)}]"
        elif val.kind == "map":
            assert isinstance(val.content, MapType)
            if isinstance(val.content.key, MapKeyType):
                key_annotation = self._generate_type_annotation_mapkey(
                    val.content.key)
            else:
                key_annotation = val.content.key.name
            return f"Dict[{key_annotation}, {self.generate_type_annotation(val.content.value)}]"
        elif val.kind == "and":
            assert isinstance(val.content, AndType)
            return self._anonymous_andtype_names[val.content]
        elif val.kind == "or":
            assert isinstance(val.content, OrType)
            item_annotations = [self.generate_type_annotation(
                v) for v in val.content.items]
            return f"Union[{', '.join(item_annotations)}]"
        elif val.kind == "tuple":
            assert isinstance(val.content, TupleType)
            item_annotations = [self.generate_type_annotation(
                v) for v in val.content.items]
            return f"Tuple[{', '.join(item_annotations)}]"
        elif val.kind == "literal":
            assert isinstance(val.content, StructureLiteralType)
            return self._generate_type_annotation_literal(val.content)
        elif val.kind == "stringLiteral":
            return "str"
        elif val.kind == "integerLiteral":
            return "int"
        elif val.kind == "booleanLiteral":
            return "bool"
        else:
            assert False  # Broken AnyType

    # --------------------------------------------
    #            Anonymous Structures
    # --------------------------------------------

    def _generate_and_type_name(self, val: AndType) -> str:
        """Generates a name for an `AndType` from its items."""

        item_names: List[str] = []
        for i in val.items:
            assert isinstance(i.content, ReferenceType)
            item_names.append(i.content.name)
        item_names.sort()
        return "And".join(item_names)

    def _add_anonymous_definitions_from_anytype(self, val: AnyType) -> None:
        """
        Adds a definition to the list of anonymous definitions for the given anytype.
        If `val` is an aggregate type, definitions are created recursively for all
        encountered anonymous types (literal, and). Recursion stops if a type is not an
        anonymous structure.
        """

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

            self._anonymous_andtype_names[val.content] = self._generate_and_type_name(
                val.content)
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

            class_name = "AnonymousStructure" + \
                str(len(self._anonymous_structure_names))
            self._anonymous_structure_names[val.content.value] = class_name

    def _generate_anonymous_structure_names(self) -> None:
        """
        Traverses the `MetaModel` and generates definitions for all anonymus types used.
        """

        for n in self._meta_model.notifications:
            if n.params:
                if isinstance(n.params, Tuple):
                    for p in n.params:
                        self._add_anonymous_definitions_from_anytype(p)
                else:
                    self._add_anonymous_definitions_from_anytype(n.params)

            if n.registration_options:
                self._add_anonymous_definitions_from_anytype(
                    n.registration_options)

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
                self._add_anonymous_definitions_from_anytype(
                    r.registration_options)

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
        """
        Returns the complete list of properties which the given `Structure` has,
        including properties from mixins and superclasses.
        """
        # Use a dict instead of a List, so that the properties from
        # derived classes can override those from the base classes
        props: Dict[str, Property] = {}

        if struct.extends:
            for m in struct.extends:
                if not isinstance(m.content, ReferenceType):
                    raise LSPGeneratorException("Non-reference 'extends' values are not supported.")
                target = self.resolve_reference(m.content)
                if not isinstance(target, Structure):
                    raise LSPGeneratorException("Non-Structure references in 'extends' are not supported")
                props.update({p.name: p for p in self.collect_structure_properties(target)})

        if struct.mixins:
            for m in struct.mixins:
                if not isinstance(m.content, ReferenceType):
                    raise LSPGeneratorException("Non-reference 'mixins' values are not supported.")
                target = self.resolve_reference(m.content)
                if not isinstance(target, Structure):
                    raise LSPGeneratorException("Non-Structure references in 'mixins' are not supported")
                props.update({p.name: p for p in target.properties})

        props.update({p.name: p for p in struct.properties})

        return list(props.values())

    def get_anonymous_type_name(self, type: Union[StructureLiteral, AndType]) -> str:
        """
        Returns the name generated for the given anonymous type.

        Currently, anonymous types include `StructureLiterals` ("kind": "literal") and `AndTypes` ("kind": "and").
        """
        if isinstance(type, StructureLiteral):
            return self._anonymous_structure_names[type]
        else:
            return self._anonymous_andtype_names[type]

    def get_anonymous_types(self) -> List[Union[StructureLiteral, AndType]]:
        """
        Returns a list of all anonymous types in the metaModel.
        """
        return list(self._anonymous_structure_names.keys()) + list(self._anonymous_andtype_names.keys())

    def generate_init_py(self) -> str:
        structures = [
            '"' + s.name + '"' for s in self._meta_model.structures if s.name[0] != '_']
        enumerations = ['"' + e.name + '"'
                        for e in self._meta_model.enumerations]
        type_aliases = ['"' + t.name + '"'
                        for t in self._meta_model.type_aliases]
        and_types = ['"' + a + '"'
                     for a in self._anonymous_andtype_names.values()]

        template = dedent_ignore_empty("""\
            from .structures import *
            from .enumerations import *


            __all__ = (
            {exports}
            )
            """)

        return template.format(exports=indent(",\n".join(structures + enumerations + type_aliases + and_types)))
