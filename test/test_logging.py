from logging import DEBUG, Handler, LogRecord, getLogger
from typing import Generator, List

import pytest

from change_ls.logging import Operation, OperationLoggerAdapter, operation


class TestHandler(Handler):
    records: List[LogRecord]

    def __init__(self) -> None:
        super().__init__()
        self.records = []

    def emit(self, record: LogRecord) -> None:
        self.records.append(record)


@pytest.fixture
def test_handler() -> Generator[TestHandler, None, None]:
    logger = getLogger("change-ls.test")
    logger.setLevel(DEBUG)
    logger.propagate = False
    handler = TestHandler()
    logger.addHandler(handler)
    yield handler
    logger.removeHandler(handler)


def test_operation_decorator(test_handler: TestHandler) -> None:
    logger = OperationLoggerAdapter(getLogger("change-ls.test"))
    logger.info("No Operation")

    @operation(logger_name="change-ls.test", start_message="Starting test_fn1", end_message="Finished test_fn1")
    def test_fn1() -> None:
        test_fn2()

    @operation(logger_name="change-ls.test", start_message="Starting test_fn2", end_message="Finished test_fn2")
    def test_fn2() -> None:
        logger.info("Test")

    test_fn1()

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


def test_operation_context_manager(test_handler: TestHandler) -> None:
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
