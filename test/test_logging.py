from logging import DEBUG, Handler, Logger, LogRecord, getLogger
from typing import Any, Generator, List

import pytest

from change_ls.logging import Operation, OperationLoggerAdapter, operation


class OperationRecorder(Handler):
    records: List[LogRecord]

    def __init__(self) -> None:
        super().__init__()
        self.records = []

    def emit(self, record: LogRecord) -> None:
        self.records.append(record)


@pytest.fixture
def test_handler() -> Generator[OperationRecorder, None, None]:
    logger = getLogger("change-ls.test")
    logger.setLevel(DEBUG)
    logger.propagate = False
    handler = OperationRecorder()
    logger.addHandler(handler)
    yield handler
    logger.removeHandler(handler)


async def test_operation_decorator(test_handler: OperationRecorder) -> None:
    logger = OperationLoggerAdapter(getLogger("change-ls.test"))
    logger.info("No Operation")

    @operation(logger_name="change-ls.test", start_message="Starting test_fn1", end_message="Finished test_fn1")
    async def test_fn1() -> None:
        test_fn2()

    @operation(logger_name="change-ls.test", start_message="Starting test_fn2", end_message="Finished test_fn2")
    def test_fn2() -> None:
        logger.info("Test")

    await test_fn1()

    assert len(test_handler.records) == 6
    records = test_handler.records

    assert records[0].msg == "No Operation"
    assert records[0].cls_operation_stack_names is None  # type: ignore
    assert records[0].cls_current_operation_name is None  # type: ignore

    assert records[1].msg == "Starting test_fn1"
    assert records[1].cls_operation_stack_names == "test_fn1"  # type: ignore
    assert records[1].cls_current_operation_name == "test_fn1"  # type: ignore

    assert records[2].msg == "Starting test_fn2"
    assert records[2].cls_operation_stack_names == "test_fn1.test_fn2"  # type: ignore
    assert records[2].cls_current_operation_name == "test_fn2"  # type: ignore

    assert records[3].msg == "Test"
    assert records[3].cls_operation_stack_names == "test_fn1.test_fn2"  # type: ignore
    assert records[3].cls_current_operation_name == "test_fn2"  # type: ignore

    assert records[4].msg == "Finished test_fn2"
    assert records[4].cls_operation_stack_names == "test_fn1.test_fn2"  # type: ignore
    assert records[4].cls_current_operation_name == "test_fn2"  # type: ignore

    assert records[5].msg == "Finished test_fn1"
    assert records[5].cls_operation_stack_names == "test_fn1"  # type: ignore
    assert records[5].cls_current_operation_name == "test_fn1"  # type: ignore


def test_operation_context_manager(test_handler: OperationRecorder) -> None:
    logger = OperationLoggerAdapter(getLogger("change-ls.test"))
    logger.info("No Operation")

    with Operation("test_fn1", logger, "Starting test_fn1", "Finished test_fn1"):
        with Operation("test_fn2", logger, "Starting test_fn2", "Finished test_fn2"):
            logger.info("Test")

    assert len(test_handler.records) == 6
    records = test_handler.records

    assert records[0].msg == "No Operation"
    assert records[0].cls_operation_stack_names is None  # type: ignore
    assert records[0].cls_current_operation_name is None  # type: ignore

    assert records[1].msg == "Starting test_fn1"
    assert records[1].cls_operation_stack_names == "test_fn1"  # type: ignore
    assert records[1].cls_current_operation_name == "test_fn1"  # type: ignore

    assert records[2].msg == "Starting test_fn2"
    assert records[2].cls_operation_stack_names == "test_fn1.test_fn2"  # type: ignore
    assert records[2].cls_current_operation_name == "test_fn2"  # type: ignore

    assert records[3].msg == "Test"
    assert records[3].cls_operation_stack_names == "test_fn1.test_fn2"  # type: ignore
    assert records[3].cls_current_operation_name == "test_fn2"  # type: ignore

    assert records[4].msg == "Finished test_fn2"
    assert records[4].cls_operation_stack_names == "test_fn1.test_fn2"  # type: ignore
    assert records[4].cls_current_operation_name == "test_fn2"  # type: ignore

    assert records[5].msg == "Finished test_fn1"
    assert records[5].cls_operation_stack_names == "test_fn1"  # type: ignore
    assert records[5].cls_current_operation_name == "test_fn1"  # type: ignore


class OperationContext:
    _logger: Logger

    def __init__(self) -> None:
        self._logger = getLogger("change-ls.test")

    @operation(start_message="test_fn", get_logger_from_context=lambda self, *_1, **_2: self._logger)  # type: ignore
    def test_fn(self, param1: Any, param2: Any) -> None:
        pass


def test_operation_get_logger_from_context(test_handler: OperationRecorder) -> None:
    context = OperationContext()

    context.test_fn(1, param2=2)

    assert len(test_handler.records) == 1
    records = test_handler.records
    assert records[0].msg == "test_fn"
    assert records[0].cls_operation_stack_names == "test_fn"  # type: ignore
    assert records[0].cls_current_operation_name == "test_fn"  # type: ignore


def test_operation_message_formatting(test_handler: OperationRecorder) -> None:
    @operation(logger_name="change-ls.test", start_message="test_fn1 {a} {b} {c}")
    def test_fn1(a: int, b: int, c: int) -> None:
        pass

    @operation(logger_name="change-ls.test", start_message="test_fn2 {a} {b} {c}")
    def test_fn2(a: int, *b: int, **c: int) -> None:
        pass

    @operation(logger_name="change-ls.test", start_message="test_fn3 {a} {b}")
    def test_fn3(a: int = 1, *, b: int = 2) -> None:
        pass

    test_fn1(1, 2, 3)
    test_fn1(1, c=3, b=2)
    test_fn2(1, 2, 3, d=4, e=5)
    test_fn2(1, d=4, e=5)
    test_fn3()

    assert len(test_handler.records) == 5
    records = test_handler.records

    assert records[0].msg == "test_fn1 1 2 3"
    assert records[1].msg == "test_fn1 1 2 3"
    assert records[2].msg in ["test_fn2 1 (2, 3) {'d': 4, 'e': 5}", "test_fn2 1 (2, 3) {'e': 5, 'd': 4}"]
    assert records[3].msg in ["test_fn2 1 () {'d': 4, 'e': 5}", "test_fn2 1 () {'e': 5, 'd': 4}"]
    assert records[4].msg == "test_fn3 1 2"
