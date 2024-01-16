"""
Config functions for TSDB.
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: BSD-3-Clause

import os
from configparser import ConfigParser

from .logging import logger

TSDB_BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TSDB_CONFIG_FILE = os.path.join(TSDB_BASE_PATH, "config.ini")


def read_configs():
    config_parser = ConfigParser()
    config_parser.read(TSDB_CONFIG_FILE)
    return config_parser


def write_configs(config_parser, key_value_set):
    for section in key_value_set.keys():
        for key in key_value_set[section].keys():
            value = key_value_set[section][key]
            config_parser.set(section, key, value)

    with open(TSDB_CONFIG_FILE, "w") as f:
        config_parser.write(f)

    logger.info("Wrote new configs to config.ini successfully.")
