from abc import ABC, abstractmethod
from asyncio import (
    BaseTransport,
    Event,
    Future,
    Protocol,
    SubprocessProtocol,
    SubprocessTransport,
    Transport,
    WriteTransport,
)
from dataclasses import dataclass
from json import JSONDecodeError, dumps, loads
from logging import DEBUG
from sys import getdefaultencoding
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple, Union

import cattrs
import lsprotocol.types as lsp

from change_ls.logging import OperationLoggerAdapter
from change_ls.types import JSON_VALUE


class LSPException(Exception):
    error_code: int
    message: str
    data: Any

    def __init__(self, error_code: int, message: str, data: Any = None) -> None:
        self.error_code = error_code
        self.message = message
        self.data = data

    def __str__(self) -> str:
        return f"Received error {str(self.error_code)}: {self.message}"


class LSPClientException(Exception):
    pass


@dataclass
class _LSPHeader:
    content_length: int
    content_type: str = "application/vscode-jsonrpc; charset=utf-8"

    @classmethod
    def try_from_bytes(cls, data: bytes) -> Optional[Tuple["_LSPHeader", int]]:
        content_length = -1
        content_type = "application/vscode-jsonrpc; charset=utf-8"

        cursor = 0
        while True:
            line_end = data.find(b"\r\n", cursor)
            if line_end < 0:
                # Incomplete header, wait for more data
                return None

            line = data[cursor:line_end]
            cursor = line_end + 2

            if len(line) == 0:
                out = cls(content_length, content_type)
                return (out, cursor)

            colon = line.index(b":")
            field = str(line[:colon], encoding="ascii").strip()
            value = str(line[colon + 1 :], encoding="ascii").strip()

            if field == "Content-Length":
                content_length = int(value)
            elif field == "Content-Type":
                content_type = value

    def to_bytes(self) -> bytes:
        return f"Content-Length: {self.content_length}\r\nContent-Type: {self.content_type}\r\n\r\n".encode(
            encoding="ascii"
        )

    def get_encoding(self) -> str:
        "Returns the content encoding, according to the Content-Type."

        for param in self.content_type.split(";"):
            if "=" not in param:
                continue
            [field, value] = param.split("=", 1)
            if field.strip() == "charset":
                out = value.strip()
                if out == "utf8":
                    return "utf-8"
                else:
                    return out
        return "utf-8"


def _json_to_packet(data: JSON_VALUE) -> bytes:
    content = dumps(data, ensure_ascii=False).encode(encoding="utf-8")
    header = _LSPHeader(len(content))
    return header.to_bytes() + content


def _is_request(instance: Any) -> bool:
    return hasattr(instance, "id") and hasattr(instance, "method") and hasattr(instance, "jsonrpc")


def _is_notification(instance: Any) -> bool:
    return hasattr(instance, "method") and hasattr(instance, "jsonrpc")


def _extract_id(json_data: Mapping[str, JSON_VALUE]) -> Union[int, str]:
    id = json_data["id"]
    if not isinstance(id, str) and not isinstance(id, int):
        raise LSPException(lsp.ErrorCodes.InvalidRequest, "'id' must be of type number or string")
    return id


def _extract_method(json_data: Mapping[str, JSON_VALUE]) -> str:
    method = json_data["method"]
    if not isinstance(method, str):
        raise LSPException(lsp.ErrorCodes.InvalidRequest, "'method' must be of type string")
    return method


def _extract_params(
    json_data: Mapping[str, JSON_VALUE]
) -> Optional[Union[Sequence[JSON_VALUE], Dict[str, JSON_VALUE]]]:
    if "params" in json_data:
        params_json = json_data["params"]
        if not isinstance(params_json, Sequence) and not isinstance(params_json, Dict):
            raise LSPException(
                lsp.ErrorCodes.InvalidParams,
                "params field must be a dictionary or a sequence",
                params_json,
            )
        return params_json
    else:
        return None


_RequestHandler = Callable[[str, Any], Any]
_NotificationHandler = Callable[[str, Any], None]


class LSProtocol(ABC):
    # Maps the ids of currently active requests to their corresponding
    # Future objects provided by the client.
    _active_requests: Dict[Union[int, str], Tuple[str, "Future[Any]"]]

    _converter: cattrs.Converter
    _request_handler: _RequestHandler
    _notification_handler: _NotificationHandler

    _logger_client: Optional[OperationLoggerAdapter]
    _logger_server: Optional[OperationLoggerAdapter]
    _logger_messages: Optional[OperationLoggerAdapter]

    _read_buffer: bytes
    _pending_header: Optional[_LSPHeader]
    _content_offset: int
    _request_counter: int
    _connected: bool
    _disconnect_event: Event

    def __init__(
        self,
        converter: cattrs.Converter,
        request_handler: _RequestHandler,
        notification_handler: _NotificationHandler,
    ) -> None:
        self._active_requests = {}
        self._converter = converter
        self._request_handler = request_handler
        self._notification_handler = notification_handler
        self._logger_client = None
        self._logger_server = None
        self._logger_messages = None
        self._read_buffer = b""
        self._pending_header = None
        self._content_offset = 0
        self._request_counter = 0
        self._connected = False
        self._disconnect_event = Event()

    def _set_loggers(
        self,
        _logger_client: OperationLoggerAdapter,
        _logger_server: OperationLoggerAdapter,
        _logger_messages: OperationLoggerAdapter,
    ) -> None:
        self._logger_client = _logger_client
        self._logger_server = _logger_server
        self._logger_messages = _logger_messages

    def reject_active_requests(self, exc: Exception) -> None:
        if len(self._active_requests) > 0:
            _ = self._logger_client and self._logger_client.warning(
                "Dropping %d currently active requests", len(self._active_requests)
            )
        for f in self._active_requests.values():
            f[1].set_exception(exc)
        self._active_requests = {}

    def _send_error_response(
        self,
        id: Union[str, int, None],
        code: int,
        message: str,
        data: Optional[JSON_VALUE] = None,
    ) -> None:
        message_json = self._converter.unstructure(
            lsp.ResponseErrorMessage(id=id, error=lsp.ResponseError(code, message, data))
        )
        self._write_data(_json_to_packet(message_json))

    def _try_read_message(self) -> Optional[Dict[str, JSON_VALUE]]:
        if not self._pending_header:
            maybe_header = _LSPHeader.try_from_bytes(self._read_buffer)
            if not maybe_header:
                return None
            (self._pending_header, self._content_offset) = maybe_header

        if len(self._read_buffer) - self._content_offset < self._pending_header.content_length:
            # Content has not yet been fully received, wait for more data.
            return None

        content_from = self._content_offset
        content_to = content_from + self._pending_header.content_length
        content = str(
            self._read_buffer[content_from:content_to], encoding=self._pending_header.get_encoding()
        )
        if self._logger_messages and self._logger_messages.getEffectiveLevel() <= DEBUG:
            self._logger_messages.debug(
                "Received:\n%s",
                str(self._read_buffer[:content_to], encoding=self._pending_header.get_encoding()),
            )

        self._read_buffer = self._read_buffer[
            self._content_offset + self._pending_header.content_length :
        ]
        self._pending_header = None

        try:
            return loads(content)
        except JSONDecodeError as e:
            self._send_error_response(None, lsp.ErrorCodes.ParseError, e.msg)
            return None

    def _process_request(self, json_data: Mapping[str, JSON_VALUE]) -> None:
        id = None
        try:
            id = _extract_id(json_data)
            method = _extract_method(json_data)
            params_json = _extract_params(json_data)

            if method in lsp.METHOD_TO_TYPES:
                _, response_type, param_type, _ = lsp.METHOD_TO_TYPES[method]
                try:
                    params = self._converter.structure(params_json, param_type)
                except Exception as e:  # pylint: disable=broad-exception-caught
                    raise LSPException(lsp.ErrorCodes.InvalidParams, str(e), None) from e
            else:
                # For unknown methods, pass the json data through as-is, so any
                # dispatch method on the other end can handle it.
                param_type = None
                response_type = None
                params = params_json

            result = self._request_handler(method, params)
        except LSPException as e:
            self._send_error_response(id, e.error_code, e.message, e.data)
            return

        if response_type is not None:
            # TODO: This is technically not guaranteed to work
            response = response_type(id=id, result=result)  # type: ignore
            response_json = self._converter.unstructure(response)
        else:
            response_json = {"id": id, "result": result, "jsonrpc": "2.0"}

        self._write_data(_json_to_packet(response_json))

    def _process_notification(self, json_data: Mapping[str, JSON_VALUE]) -> None:
        method = json_data["method"]
        if not isinstance(method, str):
            # No error response for notifications
            return

        if method in lsp.METHOD_TO_TYPES:
            notification = self._converter.structure(json_data, lsp.METHOD_TO_TYPES[method][0])
            self._notification_handler(method, notification.params)
        elif "params" not in json_data:
            self._notification_handler(method, None)
        else:
            self._notification_handler(method, json_data["params"])

    def _process_response(self, json_data: Mapping[str, JSON_VALUE]) -> None:
        id = json_data["id"]
        if not isinstance(id, str) and not isinstance(id, int):
            _ = self._logger_client and self._logger_client.warning(
                "id field in LSP must be an int or string."
            )
            return

        pending_request = self._active_requests.get(id)
        if not pending_request:
            _ = self._logger_client and self._logger_client.warning(
                f"Received response for unknown request id {id}."
            )
            return

        method = pending_request[0]
        if method in lsp.METHOD_TO_TYPES:
            response_msg = self._converter.structure(
                json_data, lsp.METHOD_TO_TYPES[pending_request[0]][1]
            )
            pending_request[1].set_result(response_msg.result)
        else:
            pending_request[1].set_result(json_data["result"])

        del self._active_requests[id]

    def _process_error(self, json_data: Mapping[str, JSON_VALUE]) -> None:
        error_msg = self._converter.structure(json_data, lsp.ResponseErrorMessage)
        assert error_msg.error is not None
        if error_msg.id is not None:
            pending_request = self._active_requests.get(error_msg.id)
            if not pending_request:
                _ = self._logger_client and self._logger_client.warning(
                    f"Received error for unknown request id {error_msg.id}."
                )
                return
            pending_request[1].set_exception(
                LSPException(error_msg.error.code, error_msg.error.message, error_msg.error.data)
            )
            del self._active_requests[error_msg.id]
        else:
            raise LSPException(error_msg.error.code, error_msg.error.message, error_msg.error.data)

    def _process_message(self, json_data: Mapping[str, JSON_VALUE]) -> None:
        if "method" in json_data and "id" in json_data:
            self._process_request(json_data)
        elif "method" in json_data and "id" not in json_data:
            self._process_notification(json_data)
        elif "result" in json_data:
            self._process_response(json_data)
        elif "error" in json_data:
            self._process_error(json_data)
        else:
            _ = self._logger_client and self._logger_client.warning(
                f"Received malformed data: {json_data}"
            )

    def _on_data(self, data: bytes) -> None:
        "Called by subclasses when new data has been received."

        self._read_buffer += data
        json_data = self._try_read_message()
        while json_data is not None:
            self._process_message(json_data)
            json_data = self._try_read_message()

    @abstractmethod
    def _write_data(self, data: bytes) -> None:
        pass

    def send_request(self, request: Any, future: "Future[JSON_VALUE]") -> None:
        """
        Sends a request to the language server, using the given `method` and `params`.
        This function should only run on the LSProtocol's thread.
        """
        if not self._connected:
            future.set_exception(LSPClientException("No connection to server"))
            return

        if not _is_request(request):
            raise TypeError("Argument must be a request object.")

        self._active_requests[request.id] = (request.method, future)

        message_json = self._converter.unstructure(request)
        self._write_data(_json_to_packet(message_json))

    def send_notification(self, notification: Any) -> None:
        """
        Sends a notification to the language server, using the given `method` and `params`.
        This function should only run on the LSProtocol's thread.
        """
        if not _is_notification(notification):
            raise TypeError("Argument must be a notification object.")
        message_json = self._converter.unstructure(notification)
        self._write_data(_json_to_packet(message_json))

    def _on_connection_lost(self) -> None:
        _ = self._logger_client and self._logger_client.info("Server terminated connection.")
        self._connected = False
        self._disconnect_event.set()
        self.reject_active_requests(LSPClientException("Server has stopped."))

    async def wait_for_disconnect(self) -> None:
        await self._disconnect_event.wait()


class LSStreamingProtocol(Protocol, LSProtocol):
    _transport: Transport
    _server: Any
    _connection_event: Event

    def __init__(
        self,
        converter: cattrs.Converter,
        request_handler: _RequestHandler,
        notification_handler: _NotificationHandler,
    ) -> None:
        super().__init__(converter, request_handler, notification_handler)
        self._connection_event = Event()

    def set_server(self, server: Any) -> None:
        self._server = server

    def connection_made(self, transport: BaseTransport) -> None:
        assert isinstance(transport, Transport)
        self._transport = transport
        self._connected = True
        self._connection_event.set()

    async def wait_for_connection(self) -> None:
        await self._connection_event.wait()

    def connection_lost(self, exc: Optional[Exception]) -> None:
        self._on_connection_lost()
        if exc:
            raise exc

    def data_received(self, data: bytes) -> None:
        super()._on_data(data)

    def _write_data(self, data: bytes) -> None:
        self._transport.write(data)
        if self._logger_messages and self._logger_messages.getEffectiveLevel() <= DEBUG:
            self._logger_messages.debug("Sent:\n%s", str(data, encoding="utf-8"))


class LSSubprocessProtocol(LSProtocol, SubprocessProtocol):
    _transport: SubprocessTransport
    _write_transport: WriteTransport

    def connection_made(self, transport: BaseTransport) -> None:
        assert isinstance(transport, SubprocessTransport)
        self._transport = transport

        temp = transport.get_pipe_transport(0)
        assert isinstance(temp, WriteTransport)
        self._write_transport = temp
        self._connected = True

    def connection_lost(self, exc: Optional[Exception]) -> None:
        self._on_connection_lost()
        if exc:
            raise exc

    def pipe_data_received(self, fd: int, data: bytes) -> None:
        if fd == 1:
            super()._on_data(data)
        elif fd == 2:
            _ = self._logger_server and self._logger_server.warning(
                "Server stderr: %s", str(data, encoding=getdefaultencoding())
            )

    def _write_data(self, data: bytes) -> None:
        self._write_transport.write(data)
        if self._logger_messages and self._logger_messages.getEffectiveLevel() <= DEBUG:
            self._logger_messages.debug("Sent:\n%s", str(data, encoding="utf-8"))
