from dataclasses import dataclass
from typing import List, Literal, Mapping, MutableSequence, Optional, Union

from .anytype import *
from .util import *

MessageDirection = Literal["clientToServer", "serverToClient", "both"]


@dataclass(frozen=True)
class EnumerationEntry:
    """Defines an enumeration entry"""

    documentation: Optional[str]
    name: str
    proposed: Optional[bool]
    since: Optional[str]
    value: Union[str, int]

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "EnumerationEntry":
        documentation = json_get_optional_string(obj, "documentation")
        name = json_get_string(obj, "name")
        proposed = json_get_optional_bool(obj, "proposed")
        since = json_get_optional_string(obj, "since")
        value = obj.get("value", None)
        if value is None:
            raise LSPKeyNotFoundException("name")
        if type(value) is not int and type(value) is not str:
            raise LSPMetaModelException("string or integer expected")
        return cls(documentation, name, proposed, since, value)


@dataclass(frozen=True)
class EnumerationType:
    """The type of an enumeration"""

    name: Literal["string", "integer", "uinteger"]

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "EnumerationType":
        name = json_get_string(obj, "name")
        if name == "string":
            return cls("string")
        elif name == "integer":
            return cls("integer")
        elif name == "uinteger":
            return cls("uinteger")
        else:
            raise LSPMetaModelException(
                f'Expected "name" to be one of "string", "integer" or "uinteger", found {name}')


@dataclass(frozen=True)
class Enumeration:
    """Defines an enumeration"""

    documentation: Optional[str]
    name: str
    proposed: Optional[bool]
    since: Optional[str]
    supports_custom_values: Optional[bool]
    type: EnumerationType
    values: Tuple[EnumerationEntry, ...]

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "Enumeration":
        documentation = json_get_optional_string(obj, "documentation")
        name = json_get_string(obj, "name")
        proposed = json_get_optional_bool(obj, "proposed")
        since = json_get_optional_string(obj, "since")
        supports_custom_values = json_get_optional_bool(
            obj, "supportsCustomValues")
        type_json = json_get_object(obj, "type")
        values_json = json_get_array_of_objects(obj, "values")

        type = EnumerationType.from_json(type_json)
        values = tuple(EnumerationEntry.from_json(v) for v in values_json)
        return cls(documentation, name, proposed, since, supports_custom_values, type, values)


@dataclass(frozen=True)
class Notification:
    """Represents an LSP notification"""

    documentation: Optional[str]
    message_direction: MessageDirection
    method: str
    params: Optional[Union[AnyType, Tuple[AnyType, ...]]]
    proposed: Optional[bool]
    registration_options: Optional[AnyType]
    since: Optional[str]

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "Notification":
        documentation = json_get_optional_string(obj, "documentation")
        message_direction_json = json_get_string(obj, "messageDirection")
        if message_direction_json == "clientToServer":
            message_direction = "clientToServer"
        elif message_direction_json == "serverToClient":
            message_direction = "serverToClient"
        elif message_direction_json == "both":
            message_direction = "both"
        else:
            raise LSPMetaModelException(
                "Invalid value for messageDirection: " + message_direction_json)
        method = json_get_string(obj, "method")
        proposed = json_get_optional_bool(obj, "proposed")
        registration_options_json = json_get_optional_object(
            obj, "registrationOptions")
        since = json_get_optional_string(obj, "since")

        params_json: Optional[Union[JSON_VALUE,
                                    List[JSON_VALUE]]] = obj.get("params", None)
        params: Optional[Union[AnyType, Tuple[AnyType, ...]]] = None
        if params_json is not None:
            if isinstance(params_json, MutableSequence):
                params = tuple([AnyType.from_json(p)  # type: ignore # TODO
                               for p in params_json])
            elif isinstance(params_json, Mapping):
                params = AnyType.from_json(params_json)
            else:
                raise LSPMetaModelException(
                    "Expected object or array of objects")

        registration_options = AnyType.from_json(
            registration_options_json) if registration_options_json else None

        return cls(documentation, message_direction, method, params, proposed, registration_options, since)


@dataclass(frozen=True)
class Request:
    """Represents a LSP request"""

    documentation: Optional[str]
    error_data: Optional[AnyType]
    message_direction: MessageDirection
    method: str
    params: Optional[Union[AnyType, Tuple[AnyType, ...]]]
    partial_result: Optional[AnyType]
    proposed: Optional[bool]
    registration_options: Optional[AnyType]
    registration_method: Optional[str]
    result: AnyType
    since: Optional[str]

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "Request":
        documentation = json_get_optional_string(obj, "documentation")
        message_direction_json = json_get_string(obj, "messageDirection")
        error_data_json = json_get_optional_object(obj, "errorData")
        if message_direction_json == "clientToServer":
            message_direction = "clientToServer"
        elif message_direction_json == "serverToClient":
            message_direction = "serverToClient"
        elif message_direction_json == "both":
            message_direction = "both"
        else:
            raise LSPMetaModelException(
                "Invalid value for messageDirection: " + message_direction_json)
        method = json_get_string(obj, "method")
        partial_result_json = json_get_optional_object(obj, "partialResult")
        proposed = json_get_optional_bool(obj, "proposed")
        registration_options_json = json_get_optional_object(
            obj, "registrationOptions")
        registration_method_json = json_get_optional_string(
            obj, "registrationMethod")
        result_json = json_get_object(obj, "result")
        since = json_get_optional_string(obj, "since")

        params_json: Optional[Union[JSON_VALUE,
                                    List[JSON_VALUE]]] = obj.get("params", None)
        params: Optional[Union[AnyType, Tuple[AnyType, ...]]] = None
        if params_json is not None:
            if isinstance(params_json, MutableSequence):
                params = tuple([AnyType.from_json(p)  # type: ignore # TODO
                               for p in params_json])
            elif isinstance(params_json, Mapping):
                params = AnyType.from_json(params_json)
            else:
                raise LSPMetaModelException(
                    "Expected object or array of objects")

        error_data = AnyType.from_json(
            error_data_json) if error_data_json else None
        partial_result = AnyType.from_json(
            partial_result_json) if partial_result_json else None
        registration_options = AnyType.from_json(
            registration_options_json) if registration_options_json else None
        registration_method = registration_method_json if registration_method_json else None
        results = AnyType.from_json(result_json)

        return cls(documentation, error_data, message_direction, method, params, partial_result, proposed, registration_options, registration_method, results, since)


@dataclass(frozen=True)
class Structure:
    """Defines the structure of an object literal."""

    documentation: Optional[str]
    extends: Optional[Tuple[AnyType, ...]]
    mixins: Optional[Tuple[AnyType, ...]]
    name: str
    properties: Tuple[Property, ...]
    proposed: Optional[bool]
    since: Optional[str]

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "Structure":
        documentation = json_get_optional_string(obj, "documentation")

        if "extends" in obj:
            extends_json = json_get_array_of_objects(obj, "extends")
            extends = tuple(AnyType.from_json(e) for e in extends_json)
        else:
            extends = None

        if "mixins" in obj:
            mixins_json = json_get_array_of_objects(obj, "mixins")
            mixins = tuple(AnyType.from_json(m) for m in mixins_json)
        else:
            mixins = None

        name = json_get_string(obj, "name")

        properties_json = json_get_array_of_objects(obj, "properties")
        properties = tuple(Property.from_json(p) for p in properties_json)

        proposed = json_get_optional_bool(obj, "proposed")
        since = json_get_optional_string(obj, "since")

        return cls(documentation, extends, mixins, name, properties, proposed, since)


@dataclass(frozen=True)
class TypeAlias:
    """Defines a type alias. (e.g. `type Definition = Location | LocationLink`)"""

    documentation: Optional[str]
    name: str
    proposed: Optional[bool]
    since: Optional[str]
    type: AnyType

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "TypeAlias":
        documentation = json_get_optional_string(obj, "documentation")
        name = json_get_string(obj, "name")
        proposed = json_get_optional_bool(obj, "proposed")
        since = json_get_optional_string(obj, "since")
        typename = AnyType.from_json(json_get_object(obj, "type"))
        return cls(documentation, name, proposed, since, typename)


@dataclass(frozen=True)
class MetaModel:
    """The actual meta model"""

    enumerations: Tuple[Enumeration, ...]
    notifications: Tuple[Notification, ...]
    requests: Tuple[Request, ...]
    structures: Tuple[Structure, ...]
    type_aliases: Tuple[TypeAlias, ...]

    @classmethod
    def from_json(cls, obj: Mapping[str, JSON_VALUE]) -> "MetaModel":
        enumerations_json = json_get_array_of_objects(obj, "enumerations")
        notifications_json = json_get_array_of_objects(obj, "notifications")
        requests_json = json_get_array_of_objects(obj, "requests")
        structures_json = json_get_array_of_objects(obj, "structures")
        type_aliases_json = json_get_array_of_objects(obj, "typeAliases")

        enumerations = tuple(Enumeration.from_json(i)
                             for i in enumerations_json)
        notifcations = tuple(Notification.from_json(i)
                             for i in notifications_json)
        requests = tuple(Request.from_json(i) for i in requests_json)
        structures = tuple(Structure.from_json(i) for i in structures_json)
        type_aliases = tuple(TypeAlias.from_json(i) for i in type_aliases_json)

        return cls(enumerations, notifcations, requests, structures, type_aliases)
