from abc import ABC, abstractmethod
from asyncio import (BaseTransport, Event, Future, Protocol,
                     SubprocessProtocol, SubprocessTransport, Transport,
                     WriteTransport)
from dataclasses import dataclass
from json import JSONDecodeError, dumps, loads
from logging import DEBUG
from sys import getdefaultencoding
from typing import (Any, Callable, Dict, List, Mapping, Optional, Sequence,
                    Tuple, Union)

from change_ls.logging import _get_change_ls_default_logger  # type: ignore
from change_ls.logging import OperationLoggerAdapter
from change_ls.types import JSON_VALUE, ErrorCodes, LSPErrorCodes


class LSPException(Exception):
    error_code: Union[ErrorCodes, LSPErrorCodes, int]
    message: str
    data: Any

    def __init__(self, error_code: int, message: str, data: Any = None) -> None:
        if error_code >= -32099 and error_code <= -32000:
            self.error_code = ErrorCodes(error_code)
        elif error_code >= -32899 and error_code <= -32800:
            self.error_code = LSPErrorCodes(error_code)
        else:
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
            value = str(line[colon + 1:], encoding="ascii").strip()

            if field == "Content-Length":
                content_length = int(value)
            elif field == "Content-Type":
                content_type = value

    def to_bytes(self) -> bytes:
        return f"Content-Length: {self.content_length}\r\nContent-Type: {self.content_type}\r\n\r\n".encode(encoding="ascii")

    def get_encoding(self) -> str:
        "Returns the content encoding, according to the Content-Type."

        for param in self.content_type.split(';'):
            if "=" not in param:
                continue
            [field, value] = param.split('=', 1)
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


_RequestHandler = Callable[[str, Union[Sequence[JSON_VALUE], Mapping[str, JSON_VALUE], None]], JSON_VALUE]
_NotificationHandler = Callable[[str, Union[Sequence[JSON_VALUE], Mapping[str, JSON_VALUE], None]], None]


class LSProtocol(ABC):

    # Maps the ids of currently active requests to their corresponding
    # Future objects provided by the client.
    _active_requests: Dict[Union[int, str], "Future[JSON_VALUE]"]

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

    def __init__(self, request_handler: _RequestHandler, notification_handler: _NotificationHandler) -> None:
        self._active_requests = {}
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

    def _set_loggers(self, _logger_client: OperationLoggerAdapter, _logger_server: OperationLoggerAdapter, _logger_messages: OperationLoggerAdapter) -> None:
        self._logger_client = _logger_client
        self._logger_server = _logger_server
        self._logger_messages = _logger_messages

    def reject_active_requests(self, exc: Exception) -> None:
        if len(self._active_requests) > 0:
            _ = self._logger_client and self._logger_client.warning(
                "Dropping %d currently active requests", len(self._active_requests))
        for f in self._active_requests.values():
            f.set_exception(exc)

    def _send_error_response(self, id: Union[str, int, None], code: Union[ErrorCodes, LSPErrorCodes, int], message: str, data: Optional[JSON_VALUE] = None) -> None:
        if not isinstance(code, int):
            error_code = code.value
        else:
            error_code = code
        message_json = {
            "jsonrpc": "2.0",
            "id": id,
            "error": {
                "code": error_code,
                "message": message,
                "data": data
            }
        }
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
        content = str(self._read_buffer[content_from:content_to],
                      encoding=self._pending_header.get_encoding())
        if self._logger_messages and self._logger_messages.getEffectiveLevel() <= DEBUG:
            self._logger_messages.debug("Received:\n%s", str(
                self._read_buffer[:content_to], encoding=self._pending_header.get_encoding()))

        self._read_buffer = self._read_buffer[self._content_offset +
                                              self._pending_header.content_length:]
        self._pending_header = None

        try:
            return loads(content)
        except JSONDecodeError as e:
            self._send_error_response(None, ErrorCodes.ParseError, e.msg)
            return None

    def _process_request(self, id: Union[int, str], method: str, params: Union[Sequence[JSON_VALUE], Mapping[str, JSON_VALUE], None]) -> None:
        try:
            result = self._request_handler(method, params)
        except LSPException as e:
            self._send_error_response(id, e.error_code, e.message, e.data)
            return None

        request_content: Dict[str, JSON_VALUE] = {
            "jsonrpc": "2.0",
            "id": id,
            "result": result
        }

        self._write_data(_json_to_packet(request_content))

    def _process_response(self, id: Union[int, str], result: JSON_VALUE) -> None:
        future = self._active_requests.get(id)
        if not future:
            _ = self._logger_client and self._logger_client.warning(f"Received response for unknown request id {id}.")
            return
        future.set_result(result)
        del self._active_requests[id]

    def _process_notification(self, method: str, params: Union[List[JSON_VALUE], Mapping[str, JSON_VALUE], None]) -> None:
        self._notification_handler(method, params)

    def _process_error(self, id: Union[int, str, None], error: Mapping[str, JSON_VALUE]) -> None:
        code = error.get("code")
        message = error.get("message")
        data = error.get("data")
        if not code and not message:
            self._send_error_response(None, ErrorCodes.InvalidRequest,
                                      "Error object must contain members 'code' and 'message'")
            return
        if type(code) is not int:
            self._send_error_response(None, ErrorCodes.InvalidRequest, "'code' must be of type number")
            return
        if type(message) is not str:
            self._send_error_response(None, ErrorCodes.InvalidRequest, "'message' must be of type string")
            return

        if id is not None:
            future = self._active_requests.get(id)
            if not future:
                _ = self._logger_client and self._logger_client.warning(f"Received error for unknown request id {id}.")
                return
            future.set_exception(LSPException(code, message, data))
            del self._active_requests[id]
        else:
            raise LSPException(code, message, data)

    def _process_message(self, json_data: Mapping[str, JSON_VALUE]) -> None:
        method = json_data.get("method")
        id = json_data.get("id")

        if id is not None and (type(id) is not str and type(id) is not int):
            self._send_error_response(None, ErrorCodes.InvalidRequest, "'id' must be of type number or string")
            return

        # Determine whether the message is a request, notification, response or error
        if method is not None:
            # Use ellipsis for undefined to differentiate from null
            params = json_data.get("params", ...)

            if id is not None:
                if type(method) is not str:
                    self._send_error_response(id, ErrorCodes.InvalidRequest, "'method' must be of type string")
                    return

                if not isinstance(params, List) and not isinstance(params, Mapping) and params is not ...:
                    self._send_error_response(id, ErrorCodes.InvalidRequest, "'params' must be of type array or object")
                    return

                if params == ...:
                    params = None
                self._process_request(id, method, params)
            else:
                # No error responses for notifications
                if type(method) is not str:
                    return

                if not isinstance(params, List) and not isinstance(params, Mapping) and params is not ...:
                    return

                if params == ...:
                    params = None
                self._process_notification(method, params)

        else:
            error = json_data.get("error", ...)
            has_result = "result" in json_data

            if error is not ... and has_result:
                self._send_error_response(None, ErrorCodes.InvalidRequest,
                                          "Only one of 'result' or 'error' may be included")
                return

            if error is not ...:
                if not isinstance(error, Mapping):
                    self._send_error_response(None, ErrorCodes.InvalidRequest, "'error' must be of type object.")
                    return
                self._process_error(id, error)

            elif id is not None:
                if not has_result:
                    self._send_error_response(id, ErrorCodes.InvalidRequest, "Expected either 'method' or 'result'.")
                    return

                self._process_response(id, json_data["result"])

            else:
                self._send_error_response(None, ErrorCodes.InvalidRequest,
                                          "At least one of 'id' or 'method' must exist.")
                return

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

    def send_request(self, method: str, params: JSON_VALUE, future: "Future[JSON_VALUE]") -> None:
        """
        Sends a request to the language server, using the given `method` and `params`.
        This function should only run on the LSProtocol's thread.
        """
        if not self._connected:
            future.set_exception(LSPClientException("No connection to server"))
            return

        request_id = self._request_counter
        self._request_counter += 1

        message_json: Dict[str, JSON_VALUE] = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method
        }
        if params is not None:
            message_json["params"] = params

        self._active_requests[request_id] = future
        self._write_data(_json_to_packet(message_json))

    def send_notification(self, method: str, params: JSON_VALUE) -> None:
        """
        Sends a notification to the language server, using the given `method` and `params`.
        This function should only run on the LSProtocol's thread.
        """
        message_json: Dict[str, JSON_VALUE] = {
            "jsonrpc": "2.0",
            "method": method
        }
        if params is not None:
            message_json["params"] = params

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

    def __init__(self, request_handler: _RequestHandler, notification_handler: _NotificationHandler) -> None:
        super().__init__(request_handler, notification_handler)

    def connection_made(self, transport: BaseTransport) -> None:
        assert isinstance(transport, Transport)
        self._transport = transport
        self._connected = True

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

    def __init__(self, request_handler: _RequestHandler, notification_handler: _NotificationHandler) -> None:
        super().__init__(request_handler, notification_handler)

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
                "Server stderr: %s", str(data, encoding=getdefaultencoding()))

    def _write_data(self, data: bytes) -> None:
        self._write_transport.write(data)
        if self._logger_messages and self._logger_messages.getEffectiveLevel() <= DEBUG:
            self._logger_messages.debug("Sent:\n%s", str(data, encoding="utf-8"))
