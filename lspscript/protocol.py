from abc import ABC, abstractmethod
from asyncio import (BaseTransport, Future, Protocol, SubprocessProtocol,
                     SubprocessTransport, Transport, WriteTransport,
                     get_running_loop)
from dataclasses import dataclass
from json import JSONDecoder, JSONEncoder
from logging import DEBUG, Logger
from sys import getdefaultencoding
from typing import Any, Callable, Dict, Optional, Tuple, Union

from lspscript.types import ErrorCodes, LSPErrorCodes
from lspscript.types.util import JSON_VALUE


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
    def from_bytes(cls, data: bytes) -> Optional[Tuple["_LSPHeader", int]]:
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


# Signature of a function which takes a str (method), a JSON_VALUE (params) and a function to send a JSON_VALUE back (send_data)
_ServerMessageCallback = Callable[[
    str, JSON_VALUE, Callable[[JSON_VALUE], None]], None]


class LSProtocol(ABC):

    # Maps the ids of currently active requests to their corresponding
    # Future objects provided by the client. These Future objects come from
    # a different thread than the LSProtocol, so they must be resolved using
    # future.get_loop().call_soon_threadsafe(lambda: future.set_result(...))
    _active_requests: Dict[Union[int, str], "Future[JSON_VALUE]"]

    # Function which is called when data is received with an unknown request id,
    # i.e. when the Language Server sends requests/notifications of its own.
    # This callable is run on the same thread as the LSProtocol, so it is up to
    # the callable's provider to ensure thread-safety.
    _server_message_callback: _ServerMessageCallback

    _logger: Logger

    _encoder: JSONEncoder
    _decoder: JSONDecoder
    _read_buffer: bytes
    _pending_header: Optional[_LSPHeader]
    _content_offset: int
    _request_counter: int
    _connected: bool

    def __init__(self, server_message_callback: _ServerMessageCallback, logger: Logger) -> None:
        self._active_requests = {}
        self._server_message_callback = server_message_callback
        self._logger = logger
        self._encoder = JSONEncoder(ensure_ascii=False)
        self._decoder = JSONDecoder()
        self._read_buffer = b""
        self._pending_header = None
        self._content_offset = 0
        self._request_counter = 0
        self._connected = False

    def reject_active_requests(self, exc: Exception) -> None:
        if len(self._active_requests) > 0:
            self._logger.warning(
                "Dropping %d currently active requests", len(self._active_requests))
        for f in self._active_requests.values():
            f.get_loop().call_soon_threadsafe(lambda: f.set_exception(exc))

    def on_data(self, data: bytes) -> None:
        "Called by subclasses when new data has been received."

        self._read_buffer += data

        if not self._pending_header:
            maybe_header = _LSPHeader.from_bytes(self._read_buffer)
            if not maybe_header:
                return
            (self._pending_header, self._content_offset) = maybe_header

        if len(self._read_buffer) - self._content_offset < self._pending_header.content_length:
            # Content has not yet been fully received, wait for more data.
            return

        content_from = self._content_offset
        content_to = content_from + self._pending_header.content_length
        content = str(self._read_buffer[content_from:content_to],
                      encoding=self._pending_header.get_encoding())
        logger = self._logger.getChild("data")
        if logger.getEffectiveLevel() <= DEBUG:
            logger.getChild("data").debug("Received:\n%s", str(
                self._read_buffer[:content_to], encoding=self._pending_header.get_encoding()))

        self._read_buffer = self._read_buffer[self._content_offset +
                                              self._pending_header.content_length:]
        self._pending_header = None

        json_data = self._decoder.decode(content)
        request_id = json_data.get("id")
        if (request_id is not None) and (future := self._active_requests.get(request_id)):
            # A result for an active request was received.
            if error := json_data.get("error"):
                exception = LSPException(
                    error["code"], error["message"], error.get("data"))
                future.get_loop().call_soon_threadsafe(lambda: future.set_exception(exception))
            # No := here, because json_data["result"] can be present but None
            elif "result" in json_data:
                future.get_loop().call_soon_threadsafe(
                    lambda: future.set_result(json_data["result"]))
            del self._active_requests[request_id]

        else:
            # The data does not correspond to an active request. This means the server
            # is sending a request/notification of its own.
            client_loop = get_running_loop()

            def send_result(result: JSON_VALUE) -> None:
                # send_result should only be to send results for requests,
                # which means a request_id is required.
                assert request_id is not None
                data = self._create_result_message(request_id, result)

                # The send_result function runs on the main thread, so any interactions
                # with the client thread must go through call_soon_threadsafe. The client thread's
                # event loop is saved in the closure.
                client_loop.call_soon_threadsafe(lambda: self.write_data(data))

            self._server_message_callback(
                json_data["method"], json_data.get("params"), send_result)

    @abstractmethod
    def write_data(self, data: bytes) -> None:
        pass

    def _create_message(self, method: str, id: Optional[Union[str, int]] = None, *, params: JSON_VALUE = None, result: JSON_VALUE = None) -> bytes:
        request_content: Dict[str, JSON_VALUE] = {
            "jsonrpc": "2.0",
            "method": method
        }
        if id is not None:
            request_content["id"] = id
        if params is not None:
            request_content["params"] = params
        if result is not None:
            request_content["result"] = result

        content = self._encoder.encode(request_content).encode("utf-8")
        header = _LSPHeader(len(content))

        return header.to_bytes() + content

    def _create_result_message(self, id: Union[str, int], result: JSON_VALUE = None) -> bytes:
        request_content: Dict[str, JSON_VALUE] = {
            "jsonrpc": "2.0",
            "id": id,
            "result": result
        }

        content = self._encoder.encode(request_content).encode("utf-8")
        header = _LSPHeader(len(content))

        return header.to_bytes() + content

    def send_request(self, method: str, params: JSON_VALUE, future: "Future[JSON_VALUE]") -> None:
        """
        Sends a request to the language server, using the given `method` and `params`.
        This function should only run on the LSProtocol's thread.
        """
        if not self._connected:
            future.get_loop().call_soon_threadsafe(lambda: future.set_exception(
                LSPClientException("No connection to server")))
            return

        request_id = self._request_counter
        self._request_counter += 1

        data = self._create_message(method, request_id, params=params)

        self._active_requests[request_id] = future
        self.write_data(data)

    def send_notification(self, method: str, params: JSON_VALUE) -> None:
        """
        Sends a notification to the language server, using the given `method` and `params`.
        This function should only run on the LSProtocol's thread.
        """
        data = self._create_message(method, params=params)
        self.write_data(data)

    def on_connection_lost(self) -> None:
        # Stop the event_loop so the thread in Client terminates
        get_running_loop().stop()
        self.reject_active_requests(LSPClientException("Server has stopped."))


class LSStreamingProtocol(Protocol, LSProtocol):

    _transport: Transport

    def __init__(self, server_message_callback: _ServerMessageCallback, logger: Logger) -> None:
        super().__init__(server_message_callback, logger)

    def connection_made(self, transport: BaseTransport) -> None:
        assert isinstance(transport, Transport)
        self._transport = transport
        self._connected = True

    def connection_lost(self, exc: Optional[Exception]) -> None:
        self.on_connection_lost()
        if exc:
            raise exc

    def data_received(self, data: bytes) -> None:
        super().on_data(data)

    def write_data(self, data: bytes) -> None:
        self._transport.write(data)
        logger = self._logger.getChild("data")
        if logger.getEffectiveLevel() <= DEBUG:
            logger.debug("Sent %s", str(data, encoding="utf-8"))


class LSSubprocessProtocol(LSProtocol, SubprocessProtocol):

    _transport: SubprocessTransport
    _write_transport: WriteTransport

    def __init__(self, server_message_callback: _ServerMessageCallback, logger: Logger) -> None:
        super().__init__(server_message_callback, logger)

    def connection_made(self, transport: BaseTransport) -> None:
        assert isinstance(transport, SubprocessTransport)
        self._transport = transport

        temp = transport.get_pipe_transport(0)
        assert isinstance(temp, WriteTransport)
        self._write_transport = temp
        self._connected = True

    def connection_lost(self, exc: Optional[Exception]) -> None:
        self.on_connection_lost()
        if exc:
            raise exc

    def pipe_data_received(self, fd: int, data: bytes) -> None:
        if fd == 1:
            super().on_data(data)
        elif fd == 2:
            self._logger.getChild("server").warning(
                "Server stderr: %s", str(data, encoding=getdefaultencoding()))

    def write_data(self, data: bytes) -> None:
        self._write_transport.write(data)
        logger = self._logger.getChild("data")
        if logger.getEffectiveLevel() <= DEBUG:
            logger.debug("Sent:\n%s", str(data, encoding="utf-8"))
