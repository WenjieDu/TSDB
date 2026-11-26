"""Versioned TOML configuration for the PyPOTS ecosystem."""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: BSD-3-Clause

import hashlib
import os
import stat
import tempfile
from configparser import ConfigParser
from pathlib import Path

import tomlkit

from .cache_lock import config_lock
from .logging import logger

USER_HOME = Path(os.path.expanduser("~"))
PYPOTS_ECOSYSTEM_HOME_PATH = Path(os.environ.get("PYPOTS_HOME") or USER_HOME / ".pypots").expanduser().absolute()
PYPOTS_ECOSYSTEM_CONFIG_PATH = PYPOTS_ECOSYSTEM_HOME_PATH / "config.toml"
TSDB_INSTALL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_TEMPLATE_PATH = os.path.join(TSDB_INSTALL_PATH, "config_template.toml")
LEGACY_CONFIG_ENCODING_ENV = "TSDB_LEGACY_CONFIG_ENCODING"
CACHE_DIR_ENV = "TSDB_CACHE_DIR"
SCHEMA_VERSION = 1


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


def _validate(document, path):
    version = document.get("schema_version")
    if isinstance(version, bool) or not isinstance(version, int) or version != SCHEMA_VERSION:
        raise ValueError(f"Unsupported configuration schema_version in {path}; expected {SCHEMA_VERSION}.")
    settings = document.get("tsdb")
    if (
        not isinstance(settings, dict)
        or not isinstance(settings.get("cache_dir"), str)
        or not settings["cache_dir"].strip()
    ):
        raise ValueError(f"Missing or invalid [tsdb] cache_dir in {path}. The file was not changed.")
    return document


def _read_toml(path):
    return _validate(tomlkit.parse(Path(path).read_text(encoding="utf-8")), path)


def _legacy_text(path, original):
    try:
        return original.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        encoding = os.environ.get(LEGACY_CONFIG_ENCODING_ENV)
        if not encoding:
            raise ValueError(
                f"{path} is not valid UTF-8. Set {LEGACY_CONFIG_ENCODING_ENV} to its known original encoding. The file was not changed."
            ) from exc
        try:
            return original.decode(encoding)
        except (LookupError, UnicodeError) as legacy_exc:
            raise ValueError(f"Cannot decode {path} using {encoding!r}. The file was not changed.") from legacy_exc


def _new_document(path):
    document = _read_toml(CONFIG_TEMPLATE_PATH)
    document["tsdb"]["cache_dir"] = str(path.parent / "tsdb")
    return document


def _migrate_ini(path, legacy):
    original = legacy.read_bytes()
    text = _legacy_text(legacy, original)
    document = _new_document(path)
    if text.strip() not in ("", "[path]"):
        parser = ConfigParser()
        parser.read_string(text, source=str(legacy))
        if not parser.has_option("path", "tsdb_home") or not parser.get("path", "tsdb_home").strip():
            raise ValueError(f"Missing [path] tsdb_home in {legacy}. The file was not changed.")
        document["tsdb"]["cache_dir"] = parser.get("path", "tsdb_home")
        # Preserve legacy sections and raw string values without guessing their types.
        # The original bytes also retain comments, case, and interpolation syntax.
        archived = {section: dict(parser.items(section, raw=True)) for section in parser.sections()}
        if parser.defaults():
            archived["DEFAULT"] = dict(parser.defaults())
        document["legacy_ini"] = archived
    document["legacy_ini_sha256"] = hashlib.sha256(original).hexdigest()
    document["legacy_cache_dir"] = str(document["tsdb"]["cache_dir"])
    _validate(document, path)
    backup = _backup_config(legacy, original)
    _atomic_write(path, lambda f: f.write(tomlkit.dumps(document)))
    logger.warning(
        f"Migrated legacy INI to {path}; original retained at {legacy}, backup at {backup}. Upgrade old TSDB environments before relocating caches."
    )
    return document


def _load_or_initialize(path):
    legacy = path.with_suffix(".ini")
    if path.exists():
        document = _read_toml(path)
        if legacy.exists() and hashlib.sha256(legacy.read_bytes()).hexdigest() != document.get("legacy_ini_sha256"):
            raise ValueError(
                f"Legacy configuration {legacy} changed or appeared after TOML initialization. Reconcile it manually and archive the INI before using {path}; neither file was changed."
            )
        if legacy.exists() and document["tsdb"]["cache_dir"] != document.get("legacy_cache_dir"):
            raise ValueError(
                f"TOML cache_dir differs from the migrated INI at {legacy}. Upgrade older TSDB environments and archive the INI before changing the persistent cache path."
            )
        return document
    if legacy.exists():
        return _migrate_ini(path, legacy)
    document = _new_document(path)
    _atomic_write(path, lambda f: f.write(tomlkit.dumps(document)))
    return document


def read_configs(config_path=None):
    """Read a TOML document; initialize/migrate only the active configuration."""
    path = Path(PYPOTS_ECOSYSTEM_CONFIG_PATH)
    if config_path is not None and Path(config_path) != path:
        return _read_toml(config_path)
    with config_lock(path):
        path.parent.mkdir(parents=True, exist_ok=True)
        return _load_or_initialize(path)


def write_configs(key_value_set):
    """Read the latest document under lock, merge updates, and atomically replace it."""
    path = Path(PYPOTS_ECOSYSTEM_CONFIG_PATH)
    with config_lock(path):
        document = read_configs()
        for section, values in key_value_set.items():
            if section not in document:
                document[section] = tomlkit.table()
            for key, value in values.items():
                document[section][key] = value
        _validate(document, path)
        if path.with_suffix(".ini").exists() and document["tsdb"]["cache_dir"] != document.get("legacy_cache_dir"):
            raise ValueError(
                "Upgrade older TSDB environments and archive config.ini before changing the persistent cache path."
            )
        _atomic_write(path, lambda f: f.write(tomlkit.dumps(document)))


def _initialize_config():
    """Explicit initialization, also used by migration regression tests."""
    return read_configs()


def cache_dir_override():
    value = os.environ.get(CACHE_DIR_ENV)
    if value is not None and not value.strip():
        raise ValueError(f"{CACHE_DIR_ENV} must not be empty.")
    return value


def require_legacy_retired_for_relocation():
    """Prevent a persistent move while an old release can still read the INI."""
    if Path(PYPOTS_ECOSYSTEM_CONFIG_PATH).with_suffix(".ini").exists():
        raise ValueError(
            "Upgrade older TSDB environments and archive config.ini before migrating the persistent cache."
        )
