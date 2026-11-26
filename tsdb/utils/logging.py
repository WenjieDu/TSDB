"""
Configure logging here.
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: BSD-3

import logging
import os

LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
}


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
    """Use UTF-8 even on Python 3.8, where FileHandler has no errors parameter."""

    def _open(self):
        open_file = getattr(self, "_builtin_open", open)
        return open_file(self.baseFilename, self.mode, encoding="utf-8", errors="backslashreplace")


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
    """Logging class for TSDB logger initialization and control."""

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
            The logging level of the logger, should be debug/info/warning/error.

        logging_format :
            Logging format of the logger.

        """

        assert logging_level in LEVELS, f"logging_level should be {list(LEVELS.keys())}, but got {logging_level}"

        self.logger = logging.getLogger(name)
        self.logging_level = LEVELS[logging_level]

        self.stream_handler = _UnicodeStreamHandler()
        self.formatter = None
        self.file_handler = None

        self.set_level(logging_level)
        self.set_logging_format(logging_format)
        self.logger.propagate = False

    def set_logging_format(self, logging_format: str) -> None:
        self.formatter = logging.Formatter(logging_format, datefmt="%Y-%m-%d %H:%M:%S")
        self.stream_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.stream_handler)
        if self.file_handler is not None:
            self.file_handler.setFormatter(self.formatter)
            self.logger.addHandler(self.file_handler)

    def set_saving_path(self, saving_dir: str, name: str, mode: str = "a") -> None:
        """Set the logger's saving path. This function will enable saving logs to the specified path.

        Parameters
        ----------
        saving_dir :
            The path to the directory for logging file saving.

        name :
            The name of the logging file to be saved.

        mode :
            Logging file writing mode.

        """
        if not os.path.exists(saving_dir):
            self.logger.warning(f"{saving_dir} does not exist. Creating it now...")
            os.makedirs(saving_dir)
        path = os.path.join(saving_dir, name)
        if "a" in mode:
            _check_append_encoding(path)
        handler = _UTF8FileHandler(path, mode=mode, encoding="utf-8")
        handler.setLevel(self.logging_level)
        handler.setFormatter(self.formatter)
        if self.file_handler is not None:
            self.logger.removeHandler(self.file_handler)
            self.file_handler.close()
        self.file_handler = handler
        self.logger.addHandler(handler)
        self.logger.info(f"Log will be saved to {path}")

    def set_level(self, level: str) -> None:
        """Set the logger's logging level.

        Parameters
        ----------
        level :
            The logging level of the logger, should be debug/info/warning/error.

        """
        self.logging_level = LEVELS[level]
        self.logger.setLevel(self.logging_level)
        if self.stream_handler is not None:
            self.stream_handler.setLevel(self.logging_level)
        if self.file_handler is not None:
            self.file_handler.setLevel(self.logging_level)


# initialize a logger for TSDB logging
logger_creator = Logger()
logger = logger_creator.logger
