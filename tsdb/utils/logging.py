"""
Configure logging here.
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: GPL-v3

import logging
import os

LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
}


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

        assert (
            logging_level in LEVELS.keys()
        ), f"logging_level should be {list(LEVELS.keys())}, but got {logging_level}"

        self.logger = logging.getLogger(name)
        self.logging_level = LEVELS[logging_level]

        self.stream_handler = logging.StreamHandler()
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
        self.file_handler = logging.FileHandler(path, mode=mode)
        self.file_handler.setLevel(self.logging_level)
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)
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
