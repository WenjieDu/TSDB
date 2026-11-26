"""
Config functions for TSDB.
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: BSD-3-Clause

import os
import stat
import tempfile
from configparser import ConfigParser
from pathlib import Path

from .logging import logger

USER_HOME = Path(os.path.expanduser("~"))
PYPOTS_ECOSYSTEM_HOME_PATH = USER_HOME / ".pypots"
PYPOTS_ECOSYSTEM_CONFIG_PATH = PYPOTS_ECOSYSTEM_HOME_PATH / "config.ini"

TSDB_INSTALL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_TEMPLATE_PATH = os.path.join(TSDB_INSTALL_PATH, "config_template.ini")
LEGACY_CONFIG_ENCODING_ENV = "TSDB_LEGACY_CONFIG_ENCODING"


def read_configs(config_path: str = PYPOTS_ECOSYSTEM_CONFIG_PATH):
    """Read an ecosystem INI file as UTF-8 (also accepting a UTF-8 BOM)."""
    config_parser = ConfigParser()
    config_parser.read(config_path, encoding="utf-8-sig")
    return config_parser


def _atomic_write(path, writer):
    """Write beside the destination, then replace only after a successful write."""
    path = Path(path).resolve()
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            dir=path.parent,
            prefix=f".{path.name}.",
            delete=False,
        ) as f:
            temp_path = Path(f.name)
            writer(f)
            f.flush()
            os.fsync(f.fileno())
        if path.exists():
            os.chmod(temp_path, stat.S_IMODE(path.stat().st_mode))
        os.replace(temp_path, path)
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()


def _backup_config(path, original):
    """Keep the exact original bytes under a unique name before recovery/migration."""
    path = Path(path).resolve()
    with tempfile.NamedTemporaryFile(
        mode="wb", dir=path.parent, prefix=f"{path.name}.", suffix=".bak", delete=False
    ) as f:
        f.write(original)
        f.flush()
        os.fsync(f.fileno())
        return Path(f.name)


def _validate_config(text, path):
    parser = ConfigParser()
    parser.read_string(text, source=str(path))
    if not parser.has_option("path", "tsdb_home") or not parser.get("path", "tsdb_home").strip():
        raise ValueError(f"Missing [path] tsdb_home in {path}. Restore or edit your configuration. It was not changed.")
    return parser


def write_configs(config_parser, key_value_set):
    for section in key_value_set:
        for key in key_value_set[section]:
            value = key_value_set[section][key]
            config_parser.set(section, key, value)

    _atomic_write(PYPOTS_ECOSYSTEM_CONFIG_PATH, config_parser.write)

    logger.info("Wrote new configs to config.ini successfully.")


def _initialize_config():
    path = PYPOTS_ECOSYSTEM_CONFIG_PATH
    if path.exists():
        original = path.read_bytes()
        try:
            text = original.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            # Never guess the encoding of a legacy file. An explicit, one-time
            # opt-in is used only if the bytes are not already valid UTF-8.
            encoding = os.environ.get(LEGACY_CONFIG_ENCODING_ENV)
            if not encoding:
                raise ValueError(
                    f"{path} is not valid UTF-8. Set {LEGACY_CONFIG_ENCODING_ENV} to its known original encoding "
                    "for one configuration import, or convert it to UTF-8 after backing it up. The file was not changed."
                ) from exc
            try:
                text = original.decode(encoding)
            except (LookupError, UnicodeError) as legacy_exc:
                raise ValueError(f"Cannot decode {path} using {encoding!r}. The file was not changed.") from legacy_exc
            _validate_config(text, path)
            backup = _backup_config(path, original)
            _atomic_write(path, lambda f: f.write(text))
            logger.info(f"💫 Migrated ecosystem config to UTF-8. Original bytes saved to {backup}")
            return

        # Recover only the empty/section-only file left by an interrupted old
        # initialization. Never reset a config containing other user settings.
        if text.strip() not in ("", "[path]"):
            _validate_config(text, path)
            return
        backup = _backup_config(path, original)
        logger.warning(f"‼️ Recovering incomplete ecosystem config. Original bytes saved to {backup}")
    else:
        logger.warning("‼️ PyPOTS Ecosystem configuration file does not exist.")

    path.parent.mkdir(parents=True, exist_ok=True)
    configer = read_configs(CONFIG_TEMPLATE_PATH)
    write_configs(configer, {"path": {"tsdb_home": str(path.parent / "tsdb")}})
    logger.info(f"💫 Initialized PyPOTS Ecosystem configuration file {path} successfully.")


_initialize_config()
