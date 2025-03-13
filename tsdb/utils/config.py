"""
Config functions for TSDB.
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: BSD-3-Clause

import os
import shutil
from configparser import ConfigParser
from pathlib import Path

from .logging import logger

USER_HOME = Path(os.path.expanduser("~"))
PYPOTS_ECOSYSTEM_HOME_PATH = USER_HOME / ".pypots"
PYPOTS_ECOSYSTEM_CONFIG_PATH = PYPOTS_ECOSYSTEM_HOME_PATH / "config.ini"

TSDB_INSTALL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_TEMPLATE_PATH = os.path.join(TSDB_INSTALL_PATH, "config_template.ini")


def read_configs(config_path: str = PYPOTS_ECOSYSTEM_CONFIG_PATH):
    config_parser = ConfigParser()
    config_parser.read(config_path)
    return config_parser


def write_configs(config_parser, key_value_set):
    for section in key_value_set.keys():
        for key in key_value_set[section].keys():
            value = key_value_set[section][key]
            config_parser.set(section, key, value)

    with open(PYPOTS_ECOSYSTEM_CONFIG_PATH, "w") as f:
        config_parser.write(f)

    logger.info("Wrote new configs to config.ini successfully.")


# if the pypots ecosystem home directory does not exist
if not os.path.exists(PYPOTS_ECOSYSTEM_CONFIG_PATH):
    logger.warning("‼️ PyPOTS Ecosystem configuration file does not exist.")
    # create the pypots ecosystem home directory
    os.makedirs(PYPOTS_ECOSYSTEM_HOME_PATH, exist_ok=True)

    # move the config template to pypots home to initialize the config
    shutil.copy(CONFIG_TEMPLATE_PATH, PYPOTS_ECOSYSTEM_CONFIG_PATH)
    configer = read_configs()
    write_configs(
        configer, {"path": {"tsdb_home": str(PYPOTS_ECOSYSTEM_HOME_PATH / "tsdb")}}
    )

    logger.info(
        f"💫 Initialized PyPOTS Ecosystem configuration file {PYPOTS_ECOSYSTEM_CONFIG_PATH} successfully."
    )
