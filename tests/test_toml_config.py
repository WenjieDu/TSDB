"""Versioned configuration, migration conflicts, and isolated cache overrides."""

# License: BSD-3-Clause

import os
import subprocess
import sys
from pathlib import Path

import pytest
import tomlkit

import tsdb
from tsdb.utils import config

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def config_path(tmp_path, monkeypatch):
    path = tmp_path / "config.toml"
    monkeypatch.setattr(config, "PYPOTS_ECOSYSTEM_CONFIG_PATH", path)
    return path


def test_preserve_toml_comments_types_and_other_tables(config_path):
    original = '# user comment\nschema_version = 1\n\n[tsdb]\ncache_dir = "old" # path comment\n\n[pypots]\nenabled = true\nworkers = 3\nlabels = ["温度", "café"]\n'
    config_path.write_text(original, encoding="utf-8")
    config.write_configs({"tsdb": {"cache_dir": "new/🚀"}})
    text = config_path.read_text(encoding="utf-8")
    assert "# user comment" in text and "# path comment" in text
    document = config.read_configs()
    assert document["tsdb"]["cache_dir"] == "new/🚀"
    assert document["pypots"] == {"enabled": True, "workers": 3, "labels": ["温度", "café"]}


@pytest.mark.parametrize(
    "original",
    [
        b"",
        b"schema_version = 2\n[tsdb]\ncache_dir = 'old'\n",
        b"schema_version = true\n[tsdb]\ncache_dir = 'old'\n",
        b"schema_version = 1\n[tsdb]\ncache_dir = 123\n",
        b"schema_version = 1\n[tsdb\n",
    ],
)
def test_invalid_toml_is_never_reset_or_downgraded(config_path, original):
    config_path.write_bytes(original)
    legacy = config_path.with_suffix(".ini")
    legacy.write_bytes(b"[path]\ntsdb_home = old\n")
    with pytest.raises(ValueError):
        config.read_configs()
    assert config_path.read_bytes() == original
    assert legacy.read_bytes() == b"[path]\ntsdb_home = old\n"
    assert not list(config_path.parent.glob("*.bak"))


def test_legacy_drift_fails_closed(config_path):
    legacy = config_path.with_suffix(".ini")
    legacy.write_text("[path]\ntsdb_home = old\n", encoding="utf-8")
    config.read_configs()
    original = config_path.read_bytes()
    legacy.write_text("[path]\ntsdb_home = changed\n", encoding="utf-8")
    with pytest.raises(ValueError, match="changed or appeared"):
        config.read_configs()
    assert config_path.read_bytes() == original
    assert legacy.read_text(encoding="utf-8").endswith("changed\n")


def test_ini_appearing_after_fresh_initialization_is_not_ignored(config_path):
    config.read_configs()
    config_path.with_suffix(".ini").write_text("[path]\ntsdb_home = old\n", encoding="utf-8")
    with pytest.raises(ValueError, match="changed or appeared"):
        config.read_configs()


def test_relocation_requires_retiring_legacy_ini(config_path):
    root = config_path.parent / "old-cache"
    root.mkdir()
    (root / "sentinel").write_text("preserve", encoding="utf-8")
    legacy = config_path.with_suffix(".ini")
    legacy.write_text(f"[path]\ntsdb_home = {root}\n", encoding="utf-8")
    assert Path(tsdb.CACHED_DATASET_DIR) == root
    target = config_path.parent / "new-cache"
    with pytest.raises(ValueError, match="archive config.ini"):
        tsdb.migrate_cache(target)
    assert root.exists() and not target.exists()
    legacy.rename(config_path.parent / "retired.ini.bak")
    tsdb.migrate_cache(target)
    assert Path(tsdb.CACHED_DATASET_DIR) == target
    assert (target / "sentinel").read_text(encoding="utf-8") == "preserve"


def test_manual_toml_path_divergence_is_detected(config_path):
    legacy = config_path.with_suffix(".ini")
    legacy.write_text("[path]\ntsdb_home = old\n", encoding="utf-8")
    document = config.read_configs()
    document["tsdb"]["cache_dir"] = "different"
    config_path.write_text(tomlkit.dumps(document), encoding="utf-8")
    with pytest.raises(ValueError, match="differs from the migrated INI"):
        config.read_configs()


def test_override_does_not_rewrite_persistent_config(config_path, monkeypatch):
    document = config.read_configs()
    before = config_path.read_bytes()
    target = config_path.parent / "temporary-cache"
    monkeypatch.setenv("TSDB_CACHE_DIR", str(target))
    assert Path(tsdb.CACHED_DATASET_DIR) == target
    assert tsdb.list_cache() == [] and target.is_dir()
    with pytest.raises(ValueError, match="Unset TSDB_CACHE_DIR"):
        tsdb.migrate_cache(config_path.parent / "new")
    assert config_path.read_bytes() == before
    monkeypatch.delenv("TSDB_CACHE_DIR")
    assert tsdb.CACHED_DATASET_DIR == document["tsdb"]["cache_dir"]
    monkeypatch.setenv("TSDB_CACHE_DIR", " ")
    with pytest.raises(ValueError, match="must not be empty"):
        _ = tsdb.CACHED_DATASET_DIR


def test_custom_home_and_config_are_lazy(tmp_path):
    home = tmp_path / "user-home"
    home.mkdir()
    legacy = home / ".tsdb"
    legacy.mkdir()
    (legacy / "sentinel").write_text("keep", encoding="utf-8")
    ecosystem = tmp_path / "custom-温度"
    env = os.environ.copy()
    env.update(HOME=str(home), USERPROFILE=str(home), PYPOTS_HOME=str(ecosystem), PYTHONPATH=str(ROOT))
    code = """
import os
from pathlib import Path
import tsdb
from tsdb.utils import config
home = Path(os.environ['PYPOTS_HOME'])
assert not home.exists()
assert Path(tsdb.CACHED_DATASET_DIR) == home / 'tsdb'
assert config.read_configs()['tsdb']['cache_dir'] == str(home / 'tsdb')
assert (home / 'config.toml').exists()
assert not (Path.home() / '.pypots').exists()
assert (Path.home() / '.tsdb' / 'sentinel').exists()
"""
    result = subprocess.run(
        [sys.executable, "-c", code], env=env, cwd=tmp_path, capture_output=True, timeout=60, check=False
    )
    assert result.returncode == 0, result.stderr.decode(errors="replace")


def test_concurrent_migration_and_updates_preserve_both_writers(tmp_path):
    ecosystem = tmp_path / "shared"
    ecosystem.mkdir()
    legacy = ecosystem / "config.ini"
    legacy.write_text("[path]\ntsdb_home = old\n[custom]\nkeep = yes\n", encoding="utf-8")
    env = os.environ.copy()
    env.update(PYPOTS_HOME=str(ecosystem), PYTHONPATH=str(ROOT))
    code = """
import sys
from tsdb.utils.config import write_configs
write_configs({'pypots': {sys.argv[1]: True}})
"""
    args = [sys.executable, "-c", code]
    with (
        subprocess.Popen([*args, "first"], env=env, cwd=tmp_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as a,
        subprocess.Popen([*args, "second"], env=env, cwd=tmp_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as b,
    ):
        for process in (a, b):
            stdout, stderr = process.communicate(timeout=60)
            assert process.returncode == 0, (stdout.decode(errors="replace"), stderr.decode(errors="replace"))
    document = tomlkit.parse((ecosystem / "config.toml").read_text(encoding="utf-8"))
    assert document["pypots"] == {"first": True, "second": True}
    assert document["legacy_ini"]["custom"]["keep"] == "yes"
    backups = list(ecosystem.glob("config.ini.*.bak"))
    assert len(backups) == 1 and backups[0].read_bytes() == legacy.read_bytes()


def test_missing_configured_cache_does_not_fall_back(config_path):
    missing = config_path.parent / "unmounted-cache"
    config.write_configs({"tsdb": {"cache_dir": str(missing)}})
    with pytest.raises(FileNotFoundError, match="Configured TSDB cache"):
        tsdb.list_cache()
    assert not missing.exists()
    assert not (config_path.parent / "tsdb").exists()


def test_explicit_override_precedence_and_isolation(config_path, monkeypatch):
    configured = config_path.parent / "configured"
    configured.mkdir()
    config.write_configs({"tsdb": {"cache_dir": str(configured)}})
    before = config_path.read_bytes()
    env_root = config_path.parent / "environment"
    explicit = config_path.parent / "explicit"
    monkeypatch.setenv("TSDB_CACHE_DIR", str(env_root))
    assert tsdb.get_cache_dir() == str(env_root)
    assert tsdb.get_cache_dir(cache_dir=explicit) == str(explicit)
    assert not explicit.exists()
    name = "electricity_load_diagrams"
    raw = explicit / name
    raw.mkdir(parents=True)
    (raw / "LD2011_2014.txt").write_text(";meter\n2011-01-01 00:00:00;1,5\n", encoding="utf-8")
    assert tsdb.load(name, cache_dir=explicit)["X"]["meter"].tolist() == [1.5]
    assert tsdb.list_cache(cache_dir=explicit) == [name]
    tsdb.delete_cache(name, only_pickle=True, cache_dir=explicit)
    assert not list(raw.glob("*.pkl"))
    tsdb.delete_cache(name, cache_dir=explicit)
    assert not raw.exists() and not env_root.exists()
    assert config_path.read_bytes() == before
    monkeypatch.delenv("TSDB_CACHE_DIR")
    assert tsdb.get_cache_dir() == str(configured)
    with pytest.raises(ValueError, match="nonempty"):
        tsdb.get_cache_dir(cache_dir=" ")


def test_explicit_override_does_not_initialize_config(config_path):
    assert not config_path.exists()
    assert tsdb.list_cache(cache_dir=config_path.parent / "temporary") == []
    assert not config_path.exists()
    assert not config_path.with_suffix(".cache.lock").exists()
