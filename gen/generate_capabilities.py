from dataclasses import dataclass
from json import load
from pathlib import Path
from textwrap import dedent
from typing import Dict, List, Optional, Union

from gen.gen_util import dedent_ignore_empty, indent
from gen.generator import Generator
from gen.schema.anytype import (ReferenceType, StructureLiteral,
                                StructureLiteralType)
from gen.schema.types import Structure
from gen.schema.util import (JSON_VALUE, LSPMetaModelException,
                             json_get_optional_string)


@dataclass
class FeatureInfo:
    server_capability: Optional[str]

    @classmethod
    def from_json(cls, obj: Dict[str, JSON_VALUE]) -> "FeatureInfo":
        server_capability = json_get_optional_string(obj, "serverCapability")
        return cls(server_capability)


def _get_access_modes(gen: Generator, root: Union[Structure, StructureLiteral], path: List[str]) -> List[str]:
    if len(path) == 0:
        return []

    mode = "subscript" if isinstance(root, StructureLiteral) else "member"

    segment = path[0]
    property = None
    for p in root.properties:
        if p.name == segment:
            property = p
    if not property:
        raise LSPMetaModelException("Invalid server capability: " + ".".join(path))

    if isinstance(property.type.content, ReferenceType):
        next = gen.resolve_reference(property.type.content)
        assert isinstance(next, Structure)
    elif isinstance(property.type.content, StructureLiteralType):
        next = property.type.content.value
    else:
        return [mode]

    return [mode] + _get_access_modes(gen, next, path[1:])


def _generate_capability_check(root: str, path: List[str], access_modes: List[str]) -> str:
    access_expressions: List[str] = [root]
    for segment, mode in zip(path, access_modes):
        if mode == "subscript":
            expr = f'.get("{segment}")'
        else:
            expr = '.' + segment
        access_expressions.append(access_expressions[-1] + expr)

    # The last check will be the actual capability. We need to
    # check for None and False explicitly here, since these are the values
    # that indicate that the capability is not supported. Other values,
    # especially {} will register the capability.
    return " and ".join(access_expressions) + " not in [None, False]"


def _generate_capability_access(root: str, path: List[str], access_modes: List[str]) -> str:
    subexpressions: List[str] = [root]
    for segment, mode in zip(path, access_modes):
        if mode == "subscript":
            expr = f'["{segment}"]'
        else:
            expr = '.' + segment
        subexpressions.append(expr)

    return "".join(subexpressions)


def parse_capabilities(path: Path) -> Dict[str, FeatureInfo]:
    with path.open("r") as file:
        json_data = load(file)

    out: Dict[str, FeatureInfo] = {}
    for method in json_data:
        out[method] = FeatureInfo.from_json(json_data[method])
    return out


def generate_server_capabilities_to_feature_registrations(gen: Generator, feature_infos: Dict[str, FeatureInfo], server_capabilities: Structure) -> str:
    checks: List[str] = []

    for m, f in feature_infos.items():
        if not f.server_capability:
            continue

        path = f.server_capability.split('.')
        access_modes = _get_access_modes(gen, server_capabilities, path)

        checks.append(dedent(f"""\
            if {_generate_capability_check("capabilities", path, access_modes)}:
                out.append(_capability_to_feature_registration({_generate_capability_access("capabilities", path, access_modes)}, "{m}"))"""))

    template = dedent_ignore_empty("""\
        def _capability_to_feature_registration(capability: Any, method: str) -> FeatureRegistration:
            if isinstance(capability, TextDocumentRegistrationOptions):
                document_selector = capability.documentSelector
            else:
                document_selector = None
            if isinstance(capability, StaticRegistrationOptions):
                id = capability.id
            else:
                id = None
            return FeatureRegistration(id, method, document_selector, capability)


        def server_capabilities_to_feature_registrations(capabilities: {name}) -> List[FeatureRegistration]:
            out: List[FeatureRegistration] = []
        {checks}
            return out""")
    return template.format(name=server_capabilities.name, checks=indent("\n".join(checks)))


def generate_registration_to_feature_registration(gen: Generator) -> str:
    meta_model = gen.get_meta_model()

    registration_option_mapping: Dict[str, str] = {}

    for r in meta_model.requests:
        if not r.registration_options:
            continue
        method = r.registration_method if r.registration_method else r.method
        if method in registration_option_mapping:
            continue
        if not isinstance(r.registration_options.content, ReferenceType):
            print(r.method)
        assert isinstance(r.registration_options.content, ReferenceType)
        registration_option_mapping[method] = r.registration_options.content.name

    for n in meta_model.notifications:
        if not n.registration_options:
            continue
        method = n.registration_method if n.registration_method else n.method
        if method in registration_option_mapping:
            continue
        if not isinstance(n.registration_options.content, ReferenceType):
            print(n.method)
        assert isinstance(n.registration_options.content, ReferenceType)
        registration_option_mapping[method] = n.registration_options.content.name

    template = dedent_ignore_empty("""\
        _method_to_options_mapping = {{
        {mapping}
        }}


        def registration_to_feature_registration(registration: Registration) -> FeatureRegistration:
            cls = _method_to_options_mapping[registration.method]
            options = cls.from_json(registration.registerOptions)
            if isinstance(options, TextDocumentRegistrationOptions):
                document_selector = options.documentSelector
            else:
                document_selector = None
            if isinstance(options, StaticRegistrationOptions):
                id = options.id
            else:
                id = registration.id
            return FeatureRegistration(id, registration.method, document_selector, options)""")

    return template.format(mapping=indent(",\n".join('"' + m + '": ' + o for m, o in registration_option_mapping.items())))


def generate_capabilities_py(gen: Generator, feature_infos: Dict[str, FeatureInfo]) -> str:
    server_capabilities = gen.resolve_reference(ReferenceType("ServerCapabilities"))
    assert isinstance(server_capabilities, Structure)

    server_capabilities_to_feature_registrations = generate_server_capabilities_to_feature_registrations(
        gen, feature_infos, server_capabilities)

    registration_to_feature_registration = generate_registration_to_feature_registration(gen)

    template = dedent_ignore_empty("""\
        from typing import List, Optional
        from dataclasses import dataclass
        from .structures import *


        @dataclass
        class FeatureRegistration:
            id: Optional[str]
            method: str
            document_selector: Optional[DocumentSelector]
            options: Any


        {server_capabilities_to_feature_registrations}


        {registration_to_feature_registration}""")

    return template.format(
        server_capabilities_to_feature_registrations=server_capabilities_to_feature_registrations,
        registration_to_feature_registration=registration_to_feature_registration)
