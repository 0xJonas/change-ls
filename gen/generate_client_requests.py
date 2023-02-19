from textwrap import dedent
from typing import Any, Dict, List, Sequence, Tuple

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
    assert not isinstance(request.params, Tuple)  # TODO implement
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

    assert not isinstance(notification.params, Tuple)  # TODO implement
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


def generate_client_requests_mixin(gen: Generator) -> str:
    client_requests = filter(lambda r: r.message_direction ==
                             "clientToServer" or r.message_direction == "both",  gen.get_meta_model().requests)
    client_notifications = filter(lambda n: n.message_direction ==
                                  "clientToServer" or n.message_direction == "both",  gen.get_meta_model().notifications)

    request_methods = map(lambda r: _generate_send_request_method(gen, r), client_requests)
    notification_methods = map(lambda n: _generate_send_notification_method(gen, n), client_notifications)

    template = dedent_ignore_empty("""\
        class ClientRequestsMixin(ABC):

            @abstractmethod
            async def send_request(self, method: str, params: JSON_VALUE, **kwargs: Any) -> JSON_VALUE:
                pass

            @abstractmethod
            async def send_notification(self, method: str, params: JSON_VALUE) -> None:
                pass

        {request_methods}

        {notification_methods}""")

    return template.format(
        request_methods=indent("\n\n".join(request_methods)),
        notification_methods=indent("\n\n".join(notification_methods)))


def _generate_server_request_method(gen: Generator, request: Request) -> str:
    name = request.method.translate(_message_translation_table)

    assert not isinstance(request.params, Tuple)  # TODO implement
    if request.params is None:
        param_type = None
        template = dedent_ignore_empty('''\
            @abstractmethod
            def on_{name}(self) -> {return_type}:
                """
            {documentation}

                *Generated from the TypeScript documentation*
                """
                return NotImplemented''')
    else:
        param_type = gen.generate_type_annotation(request.params)
        template = dedent_ignore_empty('''\
            @abstractmethod
            def on_{name}(self, params: {param_type}) -> {return_type}:
                """
            {documentation}

                *Generated from the TypeScript documentation*
                """
                return NotImplemented''')

    return template.format(
        name=name,
        return_type=gen.generate_type_annotation(request.result),
        documentation=indent(request.documentation if request.documentation else ""),
        param_type=param_type)


def _generate_server_request_branches(gen: Generator, requests: Sequence[Request], send_method_name: str) -> List[str]:
    branches: List[str] = []
    for r in requests:
        assert not isinstance(r.params, Tuple)  # TODO implement
        if r.params is None:
            params = ""
        else:
            expected_json_type = gen.get_expected_json_type(r.params)
            if expected_json_type:
                json_type_assert_fun = json_type_to_assert_function[expected_json_type]
            else:
                json_type_assert_fun = ""
            params = gen.generate_parse_expression(r.params, f"{json_type_assert_fun}(params)")
        branches.append(dedent(f"""\
            elif method == "{r.method}":
                result = self.on_{r.method.translate(_message_translation_table)}({params})
                return {gen.generate_write_expression(r.result, "result")}"""))

    return branches


def _generate_server_notification_method(gen: Generator, notification: Notification) -> str:
    name = notification.method.translate(_message_translation_table)

    assert not isinstance(notification.params, Tuple)  # TODO implement
    if notification.params is None:
        param_type = None
        template = dedent_ignore_empty('''\
            @abstractmethod
            def on_{name}(self) -> None:
                """
            {documentation}

                *Generated from the TypeScript documentation*
                """
                return NotImplemented''')
    else:
        param_type = gen.generate_type_annotation(notification.params)
        template = dedent_ignore_empty('''\
            @abstractmethod
            def on_{name}(self, params: {param_type}) -> None:
                """
            {documentation}

                *Generated from the TypeScript documentation*
                """
                return NotImplemented''')

    return template.format(
        name=name,
        documentation=indent(notification.documentation if notification.documentation else ""),
        param_type=param_type)


def _generate_server_notification_branches(gen: Generator, notifications: Sequence[Notification]) -> List[str]:
    branches: List[str] = []
    for n in notifications:
        assert not isinstance(n.params, Tuple)  # TODO implement
        if n.params is None:
            params = ""
        else:
            expected_json_type = gen.get_expected_json_type(n.params)
            if expected_json_type:
                json_type_assert_fun = json_type_to_assert_function[expected_json_type]
            else:
                json_type_assert_fun = ""
            params = gen.generate_parse_expression(n.params, f"{json_type_assert_fun}(params)")
        branches.append(dedent(f"""\
            elif method == "{n.method}":
                self.on_{n.method.translate(_message_translation_table)}({params})"""))

    return branches


def generate_server_requests_mixin(gen: Generator) -> str:
    server_requests = [r for r in gen.get_meta_model().requests if r.message_direction ==
                       "serverToClient" or r.message_direction == "both"]
    server_notifications = [n for n in gen.get_meta_model().notifications if n.message_direction ==
                            "serverToClient" or n.message_direction == "both"]

    request_methods = map(lambda r: _generate_server_request_method(gen, r), server_requests)
    notification_methods = map(lambda n: _generate_server_notification_method(gen, n), server_notifications)

    request_branches = _generate_server_request_branches(gen, server_requests, "send_result")
    notification_branches = _generate_server_notification_branches(gen, server_notifications)

    template = dedent_ignore_empty("""\
        class ServerRequestsMixin(ABC):

        {request_methods}

        {notification_methods}

            def dispatch_request(self, method: str, params: JSON_VALUE) -> JSON_VALUE:
                if False:
                    pass
        {request_branches}

            def dispatch_notification(self, method: str, params: JSON_VALUE) -> None:
                if False:
                    pass
        {notification_branches}""")
    return template.format(
        request_methods=indent("\n\n".join(request_methods)),
        notification_methods=indent("\n\n".join(notification_methods)),
        request_branches=indent(indent("\n".join(request_branches))),
        notification_branches=indent(indent("\n".join(notification_branches))))


def generate_client_requests_py(gen: Generator) -> str:
    client_requests_mixin = generate_client_requests_mixin(gen)
    server_requests_mixin = generate_server_requests_mixin(gen)

    template = dedent_ignore_empty("""\
        from .util import *
        from .enumerations import *
        from .structures import *

        from abc import ABC, abstractmethod
        from typing import Any


        {client_requests_mixin}


        {server_requests_mixin}
        """)
    return template.format(
        client_requests_mixin=client_requests_mixin,
        server_requests_mixin=server_requests_mixin)
