"""
Configure logging here.
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: BSD-3

import logging
import os
from threading import RLock

LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
}


_CONFIGURATION_LOCK = RLock()


class _UnicodeStreamHandler(logging.StreamHandler):
    """Retain Unicode when possible; escape only characters the stream cannot encode."""

    def emit(self, record):
        try:
            message = self.format(record) + self.terminator
            encoding = getattr(self.stream, "encoding", None)
            if encoding:
                message = message.encode(encoding, errors="backslashreplace").decode(encoding)
            try:
                self.stream.write(message)
            except UnicodeEncodeError as exc:
                # Some custom streams do not advertise their encoding.
                self.stream.write(message.encode(exc.encoding, errors="backslashreplace").decode(exc.encoding))
            self.flush()
        except RecursionError:
            raise
        except Exception:  # noqa: BLE001 - Preserve the existing error-handling contract.
            self.handleError(record)


class _UTF8FileHandler(logging.FileHandler):
    """Identify file handlers owned by TSDB, not application handlers."""


def _check_append_encoding(path):
    """Refuse to mix UTF-8 with an existing non-UTF-8 log."""
    try:
        with open(path, encoding="utf-8") as f:
            for _ in iter(lambda: f.read(65536), ""):
                # Reading each chunk validates its UTF-8 encoding.
                continue
    except FileNotFoundError:
        pass
    except UnicodeDecodeError as exc:
        raise ValueError(
            f"Cannot append UTF-8 logs to {path}: existing content is not UTF-8. "
            "Choose a new filename or back up and convert the existing log before appending."
        ) from exc


class Logger:
    """Configure a named logger with one TSDB-owned stream and optional file handler.

    Instances with the same name share handler configuration. The most recent
    constructor or configuration call sets the level and format for that name.
    Application-owned handlers are not removed or reconfigured.
    """

    def __init__(
        self,
        name: str = "TSDB running log",
        logging_level: str = "debug",
        logging_format: str = "%(asctime)s [%(levelname)s]: %(message)s",
    ):
        """
        Parameters
        ----------
        name :
            The name for the logger to be initialized.
        logging_level :
            The logging level, one of debug/info/warning/error.
        logging_format :
            Logging format of the logger.
        """
        level = self._resolve_level(logging_level)
        formatter = logging.Formatter(logging_format, datefmt="%Y-%m-%d %H:%M:%S")
        self.logger = logging.getLogger(name)
        with _CONFIGURATION_LOCK:
            self._configure_stream(formatter, level)
            self._apply_level(level)
            self.logger.propagate = False

    def _handler(self, handler_type):
        return next((handler for handler in self.logger.handlers if isinstance(handler, handler_type)), None)

    @property
    def stream_handler(self):
        """The current TSDB-owned console handler for this logger name."""
        return self._handler(_UnicodeStreamHandler)

    @property
    def file_handler(self):
        """The current TSDB-owned file handler, or None if not configured."""
        return self._handler(_UTF8FileHandler)

    @property
    def logging_level(self):
        """Current numeric level shared by wrappers of this logger."""
        return self.logger.level

    @property
    def formatter(self):
        """Current console formatter shared by wrappers of this logger."""
        stream = self.stream_handler
        return stream.formatter if stream is not None else None

    @staticmethod
    def _resolve_level(level):
        if level not in LEVELS:
            raise ValueError(f"logging_level should be {list(LEVELS)}, but got {level}")
        return LEVELS[level]

    def _configure_stream(self, formatter, level):
        stream = self.stream_handler
        if stream is None:
            stream = _UnicodeStreamHandler()
            stream.setLevel(level)
            stream.setFormatter(formatter)
            self.logger.addHandler(stream)
        else:
            stream.setFormatter(formatter)
        file_handler = self.file_handler
        if file_handler is not None:
            file_handler.setFormatter(formatter)

    def _apply_level(self, level):
        self.logger.setLevel(level)
        for handler in (self.stream_handler, self.file_handler):
            if handler is not None:
                handler.setLevel(level)

    def set_logging_format(self, logging_format: str) -> None:
        """Set the format for the shared TSDB-owned handlers."""
        formatter = logging.Formatter(logging_format, datefmt="%Y-%m-%d %H:%M:%S")
        with _CONFIGURATION_LOCK:
            self._configure_stream(formatter, self.logging_level)

    def set_saving_path(self, saving_dir: str, name: str, mode: str = "a") -> None:
        """Enable UTF-8 file logging, replacing the previous TSDB-owned file handler.

        Parameters
        ----------
        saving_dir :
            The directory for logging file saving.
        name :
            The name of the logging file.
        mode :
            Logging file writing mode.
        """
        with _CONFIGURATION_LOCK:
            if not os.path.exists(saving_dir):
                self.logger.warning(f"{saving_dir} does not exist. Creating it now...")
                os.makedirs(saving_dir, exist_ok=True)
            path = os.path.join(saving_dir, name)
            if "a" in mode:
                _check_append_encoding(path)
            # Open and configure the new handler before retiring the old one.
            handler = _UTF8FileHandler(path, mode=mode, encoding="utf-8", errors="backslashreplace")
            handler.setLevel(self.logging_level)
            handler.setFormatter(self.formatter)
            previous = self.file_handler
            if previous is not None:
                self.logger.removeHandler(previous)
            self.logger.addHandler(handler)
            if previous is not None:
                previous.close()
            self.logger.info(f"Log will be saved to {path}")

    def set_level(self, level: str) -> None:
        """Set the shared logging level (debug/info/warning/error)."""
        value = self._resolve_level(level)
        with _CONFIGURATION_LOCK:
            self._apply_level(value)


# initialize a logger for TSDB logging
logger_creator = Logger()
logger = logger_creator.logger
