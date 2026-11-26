"""Offline regression tests for ecosystem configuration and shared logging."""

# License: BSD-3-Clause

import io
import logging
import os
import subprocess
import sys
import uuid
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MESSAGE = "🚀 Training: café 温度"


@pytest.fixture
def config_module(tmp_path, monkeypatch):
    # The import initializes configuration; isolate it even when run alone.
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))
    from tsdb.utils import config

    path = home / ".pypots" / "config.ini"
    path.parent.mkdir(exist_ok=True)
    monkeypatch.setattr(config, "PYPOTS_ECOSYSTEM_CONFIG_PATH", path)
    monkeypatch.delenv(config.LEGACY_CONFIG_ENCODING_ENV, raising=False)
    return config, path


def _config_text(value):
    return f"[path]\ntsdb_home = {value}\n\n[custom]\nkeep = yes\n"


def test_utf8_config_roundtrip(config_module):
    config, path = config_module
    value = "cache/温度/café/🚀"
    original = _config_text(value).encode("utf-8-sig")
    path.write_bytes(original)
    config._initialize_config()
    assert path.read_bytes() == original
    parser = config.read_configs(path)
    assert parser.get("path", "tsdb_home") == value
    config.write_configs(parser, {"path": {"tsdb_home": value + "/new"}})
    assert path.read_bytes().decode("utf-8")
    parser = config.read_configs(path)
    assert parser.get("path", "tsdb_home") == value + "/new"
    assert parser.get("custom", "keep") == "yes"
    assert not list(path.parent.glob("*.bak"))


@pytest.mark.parametrize("encoding,value", [("cp1252", "café"), ("gbk", "温度")])
def test_legacy_config_explicit_migration(config_module, monkeypatch, encoding, value):
    config, path = config_module
    legacy_text = _config_text(value).replace("\n", "\r\n")
    original = legacy_text.encode(encoding)
    path.write_bytes(original)
    with pytest.raises(ValueError, match="TSDB_LEGACY_CONFIG_ENCODING"):
        config._initialize_config()
    assert path.read_bytes() == original
    assert not list(path.parent.glob("*.bak"))
    monkeypatch.setenv(config.LEGACY_CONFIG_ENCODING_ENV, encoding)
    config._initialize_config()
    assert path.read_bytes() == legacy_text.encode("utf-8")
    backups = list(path.parent.glob("*.bak"))
    assert len(backups) == 1
    assert backups[0].read_bytes() == original
    # Leaving the migration option set must not re-decode valid UTF-8.
    config._initialize_config()
    assert list(path.parent.glob("*.bak")) == backups
    assert config.read_configs(path).get("path", "tsdb_home") == value


@pytest.mark.parametrize("original", [b"", b"[path]\n", b"[path]\r\n"])
def test_recover_incomplete_config(config_module, original):
    config, path = config_module
    path.write_bytes(original)
    config._initialize_config()
    assert config.read_configs(path).get("path", "tsdb_home") == str(path.parent / "tsdb")
    backups = list(path.parent.glob("*.bak"))
    assert len(backups) == 1
    assert backups[0].read_bytes() == original


@pytest.mark.parametrize("original", [b"[path]\n[custom]\nkeep = yes\n", b"[path]\ntsdb_home =\n"])
def test_do_not_overwrite_other_invalid_configs(config_module, original):
    config, path = config_module
    path.write_bytes(original)
    with pytest.raises(ValueError, match="tsdb_home"):
        config._initialize_config()
    assert path.read_bytes() == original
    assert not list(path.parent.glob("*.bak"))


def test_wrong_legacy_encoding_is_not_guessed(config_module, monkeypatch):
    config, path = config_module
    original = _config_text("café").encode("cp1252")
    path.write_bytes(original)
    monkeypatch.setenv(config.LEGACY_CONFIG_ENCODING_ENV, "ascii")
    with pytest.raises(ValueError, match="Cannot decode"):
        config._initialize_config()
    assert path.read_bytes() == original
    assert not list(path.parent.glob("*.bak"))


@pytest.mark.parametrize("failure", ["write", "replace"])
def test_atomic_config_failure(config_module, monkeypatch, failure):
    config, path = config_module
    original = _config_text("original").encode("utf-8")
    path.write_bytes(original)
    parser = config.read_configs(path)

    def fail(*args):
        if failure == "write":
            args[0].write("[path]\n")
        raise OSError("simulated failure")

    if failure == "write":
        monkeypatch.setattr(parser, "write", fail)
    else:
        monkeypatch.setattr(config.os, "replace", fail)
    with pytest.raises(OSError, match="simulated failure"):
        config.write_configs(parser, {"path": {"tsdb_home": "new/🚀"}})
    assert path.read_bytes() == original
    assert list(path.parent.iterdir()) == [path]


def test_failed_migration_preserves_original(config_module, monkeypatch):
    config, path = config_module
    original = _config_text("café").encode("cp1252")
    path.write_bytes(original)
    monkeypatch.setenv(config.LEGACY_CONFIG_ENCODING_ENV, "cp1252")

    def fail(*args):
        raise OSError("simulated failure")

    monkeypatch.setattr(config.os, "replace", fail)
    with pytest.raises(OSError, match="simulated failure"):
        config._initialize_config()
    assert path.read_bytes() == original
    backups = list(path.parent.glob("*.bak"))
    assert len(backups) == 1
    assert backups[0].read_bytes() == original


@pytest.fixture
def log_creator(tmp_path, monkeypatch):
    # Keep the real HOME untouched, even for an isolated logging test.
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))
    from tsdb.utils.logging import Logger

    creator = Logger(name=f"unicode-io-{uuid.uuid4()}")
    yield creator
    for handler in list(creator.logger.handlers):
        creator.logger.removeHandler(handler)
        handler.close()


@pytest.mark.parametrize("encoding", ["utf-8", "cp1252", "gbk", "ascii"])
def test_unicode_logging_stream_and_file(log_creator, tmp_path, encoding):
    creator = log_creator
    buffer = io.BytesIO()
    stream = io.TextIOWrapper(buffer, encoding=encoding, errors="strict", write_through=True)
    creator.stream_handler.setStream(stream)
    creator.set_saving_path(str(tmp_path), "utf8.log")
    creator.logger.warning("%s", MESSAGE)
    creator.logger.info("ASCII marker")
    creator.file_handler.flush()
    expected = MESSAGE.encode(encoding, errors="backslashreplace").decode(encoding)
    assert expected in buffer.getvalue().decode(encoding)
    assert "ASCII marker" in buffer.getvalue().decode(encoding)
    file_text = (tmp_path / "utf8.log").read_text(encoding="utf-8")
    assert MESSAGE in file_text
    assert "ASCII marker" in file_text
    assert stream.encoding == encoding
    assert stream.errors == "strict"


def test_custom_stream_without_encoding(log_creator):
    class StrictStream:
        def __init__(self):
            self.output = b""

        def write(self, text):
            self.output += text.encode("cp1252")

        def flush(self):
            pass

    stream = StrictStream()
    log_creator.stream_handler.setStream(stream)
    log_creator.logger.warning(MESSAGE)
    assert MESSAGE.encode("cp1252", errors="backslashreplace") in stream.output


def test_logging_append_preserves_utf8_and_refuses_legacy(log_creator, tmp_path):
    path = tmp_path / "existing.log"
    path.write_bytes(b"old caf\xe9\n")
    with pytest.raises(ValueError, match="not UTF-8"):
        log_creator.set_saving_path(str(tmp_path), path.name)
    assert path.read_bytes() == b"old caf\xe9\n"
    assert log_creator.file_handler is None
    path.write_text("old café\n", encoding="utf-8")
    log_creator.set_saving_path(str(tmp_path), path.name)
    log_creator.logger.warning(MESSAGE)
    log_creator.set_saving_path(str(tmp_path), path.name)
    log_creator.logger.warning("one marker")
    text = path.read_text(encoding="utf-8")
    assert "old café" in text
    assert MESSAGE in text
    assert text.count("one marker") == 1
    assert sum(isinstance(h, logging.FileHandler) for h in log_creator.logger.handlers) == 1


def test_logging_append_validates_beyond_first_chunk(log_creator, tmp_path):
    path = tmp_path / "large.log"
    original = b"a" * 131072 + b"\xff"
    path.write_bytes(original)
    with pytest.raises(ValueError, match="not UTF-8"):
        log_creator.set_saving_path(str(tmp_path), path.name)
    assert path.read_bytes() == original
    assert log_creator.file_handler is None


@pytest.mark.parametrize("encoding", ["utf-8", "cp1252", "gbk"])
def test_fresh_import_with_unicode_home(tmp_path, encoding):
    home = tmp_path / "home-温度-🚀"
    home.mkdir()
    env = os.environ.copy()
    env.update(
        HOME=str(home),
        USERPROFILE=str(home),
        PYTHONPATH=str(ROOT),
        PYTHONIOENCODING=encoding,
        PYTHONUTF8="0",
        PYTHONDONTWRITEBYTECODE="1",
    )
    env.pop("TSDB_LEGACY_CONFIG_ENCODING", None)
    command = [
        sys.executable,
        "-c",
        (
            "import sys, os; streams=(sys.stdout,sys.stderr); settings=(sys.stdout.encoding,sys.stderr.encoding); "
            "before=dict(os.environ); import tsdb; "
            "assert streams==(sys.stdout,sys.stderr); assert settings==(sys.stdout.encoding,sys.stderr.encoding); "
            "assert all(os.environ.get(k)==before.get(k) for k in ('PYTHONUTF8','PYTHONIOENCODING')); "
            "print('IMPORT_OK')"
        ),
    ]
    for _ in range(2):
        result = subprocess.run(command, env=env, cwd=tmp_path, capture_output=True, timeout=60, check=False)
        assert result.returncode == 0, result.stderr.decode(encoding, errors="backslashreplace")
        assert b"IMPORT_OK" in result.stdout
        assert b"Logging error" not in result.stderr
    config_file = home / ".pypots" / "config.ini"
    assert str(home / ".pypots" / "tsdb") in config_file.read_text(encoding="utf-8")
    assert not list(config_file.parent.glob("*.bak"))
