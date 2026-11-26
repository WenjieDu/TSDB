"""Regression tests for cache transactions, migration and process coordination."""

# License: BSD-3-Clause

import os
import subprocess
import sys
from pathlib import Path

import pytest

import tsdb
from tsdb import data_processing
from tsdb.utils import config, file

NAME = "electricity_load_diagrams"
RAW = ";MT_001\n2011-01-01 00:00:00;1,5\n"


@pytest.fixture
def cache_root(tmp_path, monkeypatch):
    root = tmp_path / "cache"
    root.mkdir()
    config_path = tmp_path / "config.ini"
    config_path.write_text(f"[path]\ntsdb_home = {root}\n", encoding="utf-8")
    monkeypatch.setattr(config, "PYPOTS_ECOSYSTEM_CONFIG_PATH", config_path)
    return root


def _local_dataset(root):
    target = root / NAME
    target.mkdir()
    (target / "LD2011_2014.txt").write_text(RAW, encoding="utf-8")
    return target


def test_corrupt_parsed_cache_rebuilds_without_network(cache_root, monkeypatch):
    target = _local_dataset(cache_root)
    cache = target / f"{NAME}_cache.pkl"
    cache.write_bytes(b"not a pickle")
    monkeypatch.setattr(data_processing, "download_and_extract", lambda *_: pytest.fail("unexpected download"))
    assert tsdb.load(NAME)["X"]["MT_001"].tolist() == [1.5]
    assert tsdb.pickle_load(cache)["X"]["MT_001"].tolist() == [1.5]


def test_atomic_pickle_failure_preserves_previous_file(tmp_path, monkeypatch):
    path = tmp_path / "cache.pkl"
    tsdb.pickle_dump({"old": 1}, path)
    original = path.read_bytes()

    def fail(*_):
        raise OSError("simulated replace failure")

    monkeypatch.setattr(file.os, "replace", fail)
    with pytest.raises(file.CacheError, match="Cannot write local cache"):
        tsdb.pickle_dump({"new": 2}, path)
    assert path.read_bytes() == original
    assert list(tmp_path.iterdir()) == [path]


def test_cold_parse_failure_does_not_publish_cache(cache_root, monkeypatch):
    def download(_, path):
        Path(path).mkdir()

    monkeypatch.setattr(data_processing, "download_and_extract", download)
    with pytest.raises(FileNotFoundError):
        tsdb.load(NAME)
    assert not list(cache_root.iterdir())


def test_refresh_parse_failure_preserves_parsed_and_raw_cache(cache_root, monkeypatch):
    from tsdb.utils import downloading

    target = _local_dataset(cache_root)
    tsdb.load(NAME)
    original = {p.name: p.read_bytes() for p in target.iterdir()}
    monkeypatch.setattr(downloading, "download_and_extract", lambda _, path: Path(path).mkdir())
    with pytest.raises(FileNotFoundError):
        tsdb.load(NAME, use_cache=False)
    assert {p.name: p.read_bytes() for p in target.iterdir()} == original
    assert list(cache_root.iterdir()) == [target]


def test_migrate_cache_switches_live_path(cache_root, monkeypatch):
    _local_dataset(cache_root)
    tsdb.load(NAME)
    target = cache_root.parent / "新-cache"
    tsdb.migrate_cache(target)
    assert Path(tsdb.CACHED_DATASET_DIR) == target
    assert not cache_root.exists()
    monkeypatch.setattr(data_processing, "download_and_extract", lambda *_: pytest.fail("unexpected download"))
    assert tsdb.list_cache() == [NAME]
    assert tsdb.load(NAME)["X"]["MT_001"].tolist() == [1.5]
    tsdb.delete_cache(NAME)
    assert not list(target.iterdir())


def test_migration_preflights_conflict_and_overlap(cache_root):
    _local_dataset(cache_root)
    destination = cache_root.parent / "other"
    destination.mkdir()
    (destination / "sentinel").write_bytes(b"keep")
    with pytest.raises(FileExistsError, match="not empty"):
        tsdb.migrate_cache(destination)
    with pytest.raises(ValueError, match="must not overlap"):
        tsdb.migrate_cache(cache_root / "child")
    assert (destination / "sentinel").read_bytes() == b"keep"
    assert (cache_root / NAME / "LD2011_2014.txt").is_file()


def test_migration_config_failure_retains_original(cache_root, monkeypatch):
    _local_dataset(cache_root)
    destination = cache_root.parent / "new"

    def fail(*_):
        raise OSError("config failed")

    monkeypatch.setattr(file, "write_configs", fail)
    with pytest.raises(OSError, match="config failed"):
        tsdb.migrate_cache(destination)
    assert Path(tsdb.CACHED_DATASET_DIR) == cache_root
    assert (cache_root / NAME / "LD2011_2014.txt").is_file()
    assert (destination / NAME / "LD2011_2014.txt").is_file()


def test_delete_preserves_unrelated_and_recovery_data(cache_root):
    _local_dataset(cache_root)
    (cache_root / "notes.txt").write_bytes(b"keep")
    backup = cache_root / ".tsdb-backup-example"
    backup.mkdir()
    assert tsdb.list_cache() == [NAME]
    tsdb.delete_cache()
    assert {p.name for p in cache_root.iterdir()} == {"notes.txt", backup.name}


def test_invalid_dataset_names_under_optimized_python(tmp_path):
    env = os.environ.copy()
    env.update(HOME=str(tmp_path), USERPROFILE=str(tmp_path), PYTHONPATH=str(Path(__file__).resolve().parents[1]))
    code = """
import tsdb
for f in (tsdb.load, tsdb.delete_cache):
    try: f('../invalid')
    except ValueError: pass
    else: raise RuntimeError('invalid dataset accepted')
"""
    result = subprocess.run(
        [sys.executable, "-O", "-c", code], env=env, cwd=tmp_path, capture_output=True, timeout=60, check=False
    )
    assert result.returncode == 0, result.stderr.decode(errors="replace")


def test_two_processes_share_cache_lock(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    env = os.environ.copy()
    env.update(HOME=str(home), USERPROFILE=str(home), PYTHONPATH=str(Path(__file__).resolve().parents[1]))
    code = """
from tsdb.utils.cache_lock import cache_lock
from pathlib import Path
import time, sys
p = Path(sys.argv[1])
with cache_lock():
    with p.open('a') as f: f.write('start\\n')
    time.sleep(.2)
    with p.open('a') as f: f.write('end\\n')
"""
    marker = tmp_path / "trace"
    args = [sys.executable, "-c", code, str(marker)]
    with (
        subprocess.Popen(args, env=env, cwd=tmp_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) as a,
        subprocess.Popen(args, env=env, cwd=tmp_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) as b,
    ):
        assert a.wait(timeout=60) == 0
        assert b.wait(timeout=60) == 0
    assert marker.read_text().splitlines() == ["start", "end", "start", "end"]
