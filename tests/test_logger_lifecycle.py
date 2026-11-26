"""Regression tests for shared named logger configuration and handler ownership."""

# License: BSD-3-Clause

import io
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor

import pytest

from tsdb.utils.logging import Logger


@pytest.fixture
def logger_name():
    name = f"logger-lifecycle-{uuid.uuid4()}"
    yield name
    logger = logging.getLogger(name)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()


def test_same_name_reuses_stream_and_current_configuration(logger_name):
    first = Logger(logger_name)
    stream = io.StringIO()
    first.stream_handler.setStream(stream)
    second = Logger(logger_name, logging_level="warning", logging_format="%(levelname)s: %(message)s")
    assert first.logger is second.logger
    assert first.stream_handler is second.stream_handler
    assert first.stream_handler.stream is stream
    assert first.formatter is second.formatter
    assert first.logging_level == second.logging_level == logging.WARNING
    assert len(first.logger.handlers) == 1
    first.logger.info("hidden")
    first.logger.warning("one marker")
    assert stream.getvalue() == "WARNING: one marker\n"
    first.set_level("info")
    second.set_logging_format("%(message)s")
    first.logger.info("new format")
    assert stream.getvalue().endswith("new format\n")
    assert first.logging_level == second.logging_level == logging.INFO
    assert first.formatter is second.formatter


def test_file_handler_shared_replacement_and_external_ownership(logger_name, tmp_path):
    named = logging.getLogger(logger_name)
    external_stream = logging.StreamHandler(io.StringIO())
    external_stream.setLevel(logging.ERROR)
    external_formatter = logging.Formatter("external:%(message)s")
    external_stream.setFormatter(external_formatter)
    external_file = logging.FileHandler(tmp_path / "external.log", encoding="utf-8")
    named.addHandler(external_stream)
    named.addHandler(external_file)
    first = Logger(logger_name, logging_format="%(message)s")
    first.set_saving_path(str(tmp_path), "first.log")
    old = first.file_handler
    second = Logger(logger_name, logging_level="info", logging_format="new:%(message)s")
    assert second.file_handler is old
    assert old.level == logging.INFO
    assert old.formatter is second.formatter
    first.logger.info("before replacement")
    second.set_saving_path(str(tmp_path), "second.log")
    assert first.file_handler is second.file_handler
    assert old not in named.handlers
    assert old.stream is None
    first.set_logging_format("updated:%(message)s")
    second.set_level("warning")
    first.logger.warning("after replacement")
    assert "after replacement" not in (tmp_path / "first.log").read_text(encoding="utf-8")
    assert (tmp_path / "second.log").read_text(encoding="utf-8").count("updated:after replacement") == 1
    assert external_stream in named.handlers and external_file in named.handlers
    assert external_stream.level == logging.ERROR
    assert external_stream.formatter is external_formatter
    assert external_file.stream is not None
    assert len(named.handlers) == 4


def test_failed_file_replacement_keeps_active_handler(logger_name, tmp_path):
    first = Logger(logger_name)
    first.set_saving_path(str(tmp_path), "valid.log")
    old = first.file_handler
    second = Logger(logger_name)
    invalid = tmp_path / "legacy.log"
    invalid.write_bytes(b"invalid \xff")
    with pytest.raises(ValueError, match="not UTF-8"):
        second.set_saving_path(str(tmp_path), invalid.name)
    with pytest.raises(OSError):
        second.set_saving_path(str(tmp_path), ".", mode="w")
    assert second.file_handler is first.file_handler is old
    assert old.stream is not None
    first.logger.warning("still active")
    assert "still active" in (tmp_path / "valid.log").read_text(encoding="utf-8")
    assert invalid.read_bytes() == b"invalid \xff"


def test_invalid_configuration_does_not_change_active_logger(logger_name):
    first = Logger(logger_name, logging_level="info")
    formatter = first.formatter
    with pytest.raises(ValueError, match="logging_level"):
        Logger(logger_name, logging_level="invalid")
    with pytest.raises(ValueError, match="logging_level"):
        first.set_level("invalid")
    with pytest.raises(ValueError):
        Logger(logger_name, logging_format="invalid format")
    assert first.logging_level == logging.INFO
    assert first.formatter is formatter
    assert len(first.logger.handlers) == 1


def test_concurrent_configuration_reuses_one_owned_handler(logger_name, tmp_path):
    def configure(index):
        wrapper = Logger(logger_name)
        wrapper.set_saving_path(str(tmp_path), f"{index}.log")
        return wrapper

    with ThreadPoolExecutor(max_workers=8) as executor:
        wrappers = list(executor.map(configure, range(16)))
    first = wrappers[0]
    assert len(first.logger.handlers) == 2
    assert all(w.stream_handler is first.stream_handler and w.file_handler is first.file_handler for w in wrappers)
    first.logger.warning("final marker")
    assert sum(p.read_text(encoding="utf-8").count("final marker") for p in tmp_path.glob("*.log")) == 1


def test_distinct_names_remain_independent(logger_name):
    first = Logger(logger_name, logging_level="warning")
    second = Logger(logger_name + "-other", logging_level="debug")
    try:
        assert first.logger is not second.logger
        assert first.stream_handler is not second.stream_handler
        assert first.logging_level == logging.WARNING
        assert second.logging_level == logging.DEBUG
    finally:
        second.logger.removeHandler(second.stream_handler)
