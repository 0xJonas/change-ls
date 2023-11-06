from asyncio import get_running_loop
from typing import Callable, Mapping, Sequence, Union

from pytest import raises

from change_ls._protocol import LSPException, LSProtocol
from change_ls.types import JSON_VALUE, ErrorCodes

_ParamType = Union[Sequence[JSON_VALUE], Mapping[str, JSON_VALUE], None]
_RequestHandler = Callable[[str, _ParamType], JSON_VALUE]
_NotificationHandler = Callable[[str, _ParamType], None]


class MockLSProtocol(LSProtocol):
    _output_buffer: bytes

    def __init__(
        self, request_handler: _RequestHandler, notification_handler: _NotificationHandler
    ) -> None:
        super().__init__(request_handler, notification_handler)
        self._output_buffer = b""
        self._connected = True

    def _write_data(self, data: bytes) -> None:
        self._output_buffer += data

    def push_input(self, data: bytes) -> None:
        self._on_data(data)

    def pull_output(self) -> bytes:
        out = self._output_buffer
        self._output_buffer = b""
        return out


def _empty_request_handler(
    method: str, params: Union[Sequence[JSON_VALUE], Mapping[str, JSON_VALUE], None]
) -> JSON_VALUE:
    return None


def _empty_notification_handler(
    method: str, params: Union[Sequence[JSON_VALUE], Mapping[str, JSON_VALUE], None]
) -> None:
    return None


async def test_send_request_receive_response() -> None:
    client = MockLSProtocol(_empty_request_handler, _empty_notification_handler)
    server = MockLSProtocol(lambda m, _: 5 if m == "test" else 10, _empty_notification_handler)

    future = get_running_loop().create_future()
    client.send_request("test", None, future)

    server.push_input(client.pull_output())
    client.push_input(server.pull_output())

    res = await future
    assert res == 5


async def test_send_request_receive_error() -> None:
    def server_request_handler(method: str, params: _ParamType) -> None:
        raise LSPException(ErrorCodes.MethodNotFound.value, "method not found")

    client = MockLSProtocol(_empty_request_handler, _empty_notification_handler)
    server = MockLSProtocol(server_request_handler, _empty_notification_handler)

    future = get_running_loop().create_future()
    client.send_request("test", None, future)

    server.push_input(client.pull_output())
    client.push_input(server.pull_output())

    with raises(LSPException):
        await future


async def test_send_notification() -> None:
    future = get_running_loop().create_future()

    def server_notification_handler(method: str, params: _ParamType) -> None:
        future.set_result(True)

    client = MockLSProtocol(_empty_request_handler, _empty_notification_handler)
    server = MockLSProtocol(_empty_request_handler, server_notification_handler)

    client.send_notification("test", None)

    server.push_input(client.pull_output())
    client.push_input(server.pull_output())

    assert await future


async def test_send_invalid_json() -> None:
    client = MockLSProtocol(_empty_request_handler, _empty_notification_handler)
    server = MockLSProtocol(_empty_request_handler, _empty_notification_handler)

    invalid = b"Content-Length: 11\r\n\r\n<not-json/>"
    client.push_input(invalid)

    with raises(LSPException):
        server.push_input(client.pull_output())


async def test_send_invalid_lsp() -> None:
    client = MockLSProtocol(_empty_request_handler, _empty_notification_handler)
    server = MockLSProtocol(_empty_request_handler, _empty_notification_handler)

    invalid = b"Content-Length: 11\r\n\r\n{'test': 5}"
    client.push_input(invalid)

    with raises(LSPException):
        server.push_input(client.pull_output())


async def test_send_invalid_param_type() -> None:
    client = MockLSProtocol(_empty_request_handler, _empty_notification_handler)
    server = MockLSProtocol(_empty_request_handler, _empty_notification_handler)

    future = get_running_loop().create_future()
    # Set up a request id, but do not actually send the output to the server.
    client.send_request("test", None, future)

    invalid = (
        b'Content-Length: 61\r\n\r\n{"jsonrpc": "2.0", "id": 0, "method": "test", "params": null}'
    )
    server.push_input(invalid)
    client.push_input(server.pull_output())

    with raises(LSPException):
        await future


async def test_send_request_non_ascii() -> None:
    client = MockLSProtocol(_empty_request_handler, _empty_notification_handler)
    server = MockLSProtocol(lambda m, _: "🙂" if m == "test" else "🙁", _empty_notification_handler)

    future = get_running_loop().create_future()
    client.send_request("test", None, future)

    server.push_input(client.pull_output())
    client.push_input(server.pull_output())

    res = await future
    assert res == "🙂"
