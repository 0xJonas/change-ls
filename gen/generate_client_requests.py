from typing import Any, Dict, Tuple

from gen.gen_util import (dedent_ignore_empty, indent,
                          json_type_to_assert_function)
from gen.generator import Generator
from gen.schema.types import Notification, Request


def _create_message_translation_table() -> Any:
    table: Dict[str, str] = {}
    for i in range(ord("A"), ord("Z") + 1):
        table[chr(i)] = "_" + chr(i + 32)
    table["/"] = "_"
    table["$"] = "s"
    return str.maketrans(table)

_message_translation_table = _create_message_translation_table()


def _generate_send_request_method(gen: Generator, request: Request) -> str:
    assert not isinstance(request.params, Tuple) # TODO implement
    result_json_type = gen.get_expected_json_type(request.result)
    if result_json_type:
        result_type_assert = json_type_to_assert_function[result_json_type]
    else:
        result_type_assert = ""

    return_expression = gen.generate_parse_expression(request.result, f"{result_type_assert}(result_json)")

    param_type = None
    param_write_expression = None

    if request.params is None:
        template = dedent_ignore_empty('''\
            async def {name}(self, **kwargs: Any) -> {return_type}:
                """
            {documentation}

                *Generated from the TypeScript documentation*
                """
                result_json = await self.send_request("{method}", None, **kwargs)
                return {return_expression}''')
    else:
        param_type = gen.generate_type_annotation(request.params)
        param_write_expression = gen.generate_write_expression(request.params, "params")
        template = dedent_ignore_empty('''\
            async def {name}(self, params: {param_type}, **kwargs: Any) -> {return_type}:
                """
            {documentation}

                *Generated from the TypeScript documentation*
                """
                params_json = {param_write_expression}
                result_json = await self.send_request("{method}", params_json, **kwargs)
                return {return_expression}''')

    return template.format(
        name="send_" + request.method.translate(_message_translation_table),
        return_type=gen.generate_type_annotation(request.result),
        documentation=indent(request.documentation if request.documentation else ""),
        return_expression=return_expression,
        method=request.method,
        param_type=param_type,
        param_write_expression=param_write_expression)


def _generate_send_notification_method(gen: Generator, notification: Notification) -> str:
    param_type = None
    param_write_expression = None

    assert not isinstance(notification.params, Tuple) # TODO implement
    if notification.params is None:
        template = dedent_ignore_empty('''\
            async def {name}(self) -> None:
                """
            {documentation}

                *Generated from the TypeScript documentation*
                """
                await self.send_notification("{method}", None)''')
    else:
        param_type = gen.generate_type_annotation(notification.params)
        param_write_expression = gen.generate_write_expression(notification.params, "params")

        template = dedent_ignore_empty('''\
            async def {name}(self, params: {param_type}) -> None:
                """
            {documentation}

                *Generated from the TypeScript documentation*
                """
                params_json = {param_write_expression}
                await self.send_notification("{method}", params_json)''')

    return template.format(
        name="send_" + notification.method.translate(_message_translation_table),
        documentation=indent(notification.documentation if notification.documentation else ""),
        method=notification.method,
        param_type=param_type,
        param_write_expression=param_write_expression)


def generate_client_requests_py(gen: Generator) -> str:
    client_requests = filter(lambda r: r.message_direction == "clientToServer" or r.message_direction == "both",  gen.get_meta_model().requests)
    client_notifications = filter(lambda n: n.message_direction == "clientToServer" or n.message_direction == "both",  gen.get_meta_model().notifications)

    request_methods = map(lambda r: _generate_send_request_method(gen, r), client_requests)
    notification_methods = map(lambda n: _generate_send_notification_method(gen, n), client_notifications)

    template = dedent_ignore_empty("""\
        from .util import *
        from .enumerations import *
        from .structures import *

        from abc import ABC, abstractmethod
        from typing import Any

        class ClientRequestsMixin(ABC):

            @abstractmethod
            async def send_request(self, method: str, params: JSON_VALUE, **kwargs: Any) -> JSON_VALUE:
                pass

            @abstractmethod
            async def send_notification(self, method: str, params: JSON_VALUE) -> None:
                pass

        {request_methods}

        {notification_methods}
        """)

    return template.format(
        request_methods=indent("\n\n".join(request_methods)),
        notification_methods=indent("\n\n".join(notification_methods)))
