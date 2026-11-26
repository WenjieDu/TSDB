"""Native subprocess acceptance tests for configuration and cache transactions."""

# License: BSD-3-Clause

import os
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path

import pytest
import tomlkit

ROOT = Path(__file__).resolve().parents[1]
NAME = "electricity_load_diagrams"
RAW = ";meter\n2011-01-01 00:00:00;1,5\n"


@contextmanager
def _workers(tmp_path):
    processes = []

    def start(code, home, *args):
        env = os.environ.copy()
        env.update(PYPOTS_HOME=str(home), PYTHONPATH=str(ROOT))
        env.pop("TSDB_CACHE_DIR", None)
        process = subprocess.Popen(
            [sys.executable, "-c", code, *map(str, args)],
            cwd=tmp_path,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        processes.append(process)
        return process

    try:
        yield start
    finally:
        for process in processes:
            if process.poll() is None:
                process.kill()
            process.communicate(timeout=15)


def _finish(process):
    stdout, stderr = process.communicate(timeout=60)
    assert process.returncode == 0, (stdout.decode(errors="replace"), stderr.decode(errors="replace"))


def _wait_for(path, process=None):
    deadline = time.monotonic() + 30
    while not path.exists() and time.monotonic() < deadline:
        if process is not None and process.poll() is not None:
            _finish(process)
            break
        time.sleep(0.025)
    assert path.exists(), f"Worker did not reach checkpoint: {path.name}"


@pytest.mark.parametrize("legacy", [False, True])
def test_eight_concurrent_initializers_and_namespace_updates(tmp_path, legacy):
    home = tmp_path / "ecosystem"
    home.mkdir()
    original = b"[path]\ntsdb_home = original-cache\n[custom]\nkeep = yes\n"
    if legacy:
        (home / "config.ini").write_bytes(original)
    code = """
import sys, time
from pathlib import Path
from tsdb.utils.config import read_configs, write_configs
ready, go, key = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
ready.touch()
deadline = time.monotonic() + 30
while not go.exists() and time.monotonic() < deadline:
    time.sleep(.02)
assert go.exists()
assert read_configs()['schema_version'] == 1
for i in range(5):
    write_configs({key: {f'value_{i}': i}, 'shared': {f'{key}_{i}': i}})
"""
    go = tmp_path / "go"
    with _workers(tmp_path) as start:
        workers = [start(code, home, tmp_path / f"ready-{i}", go, f"component_{i}") for i in range(8)]
        for i, process in enumerate(workers):
            _wait_for(tmp_path / f"ready-{i}", process)
        assert not (home / "config.toml").exists()
        go.touch()
        for process in workers:
            _finish(process)
    document = tomlkit.parse((home / "config.toml").read_text(encoding="utf-8"))
    assert document["schema_version"] == 1
    for i in range(8):
        assert document[f"component_{i}"] == {f"value_{j}": j for j in range(5)}
    assert document["shared"] == {f"component_{i}_{j}": j for i in range(8) for j in range(5)}
    backups = list(home.glob("config.ini.*.bak"))
    if legacy:
        assert document["tsdb"]["cache_dir"] == "original-cache"
        assert document["legacy_ini"]["custom"]["keep"] == "yes"
        assert len(backups) == 1 and backups[0].read_bytes() == original
        assert (home / "config.ini").read_bytes() == original
    else:
        assert Path(document["tsdb"]["cache_dir"]) == home / "tsdb"
        assert not backups


@pytest.mark.parametrize("legacy", [False, True])
@pytest.mark.parametrize("after_replace", [False, True])
def test_terminated_config_publication_recovers(tmp_path, legacy, after_replace):
    home = tmp_path / "ecosystem"
    home.mkdir()
    config = home / "config.toml"
    ini = home / "config.ini"
    original = b"[path]\ntsdb_home = original-cache\n[custom]\nkeep = yes\n"
    if legacy:
        ini.write_bytes(original)
    else:
        original = b'# keep comment\nschema_version = 1\n[tsdb]\ncache_dir = "old"\n[pypots]\nkeep = true\n'
        config.write_bytes(original)
    ready = tmp_path / "ready"
    code = """
import sys, time
from pathlib import Path
from tsdb.utils import config
replace = config.os.replace
def pause(source, destination):
    if sys.argv[2] == 'after':
        replace(source, destination)
    Path(sys.argv[1]).touch()
    time.sleep(120)
config.os.replace = pause
if sys.argv[3] == 'legacy':
    config.read_configs()
else:
    config.write_configs({'pypots': {'updated': 7}})
"""
    with _workers(tmp_path) as start:
        process = start(code, home, ready, "after" if after_replace else "before", "legacy" if legacy else "toml")
        _wait_for(ready, process)
        process.kill()
        process.communicate(timeout=15)
        if legacy:
            assert ini.read_bytes() == original
            backups = list(home.glob("config.ini.*.bak"))
            assert len(backups) == 1 and backups[0].read_bytes() == original
            assert config.exists() == after_replace
        elif not after_replace:
            assert config.read_bytes() == original
        else:
            assert tomlkit.parse(config.read_text(encoding="utf-8"))["pypots"]["updated"] == 7
        # Recovery is through the real configuration API, not a repaired fixture.
        _finish(start("from tsdb.utils.config import write_configs; write_configs({'recovered': {'ok': True}})", home))
    document = tomlkit.parse(config.read_text(encoding="utf-8"))
    assert document["recovered"]["ok"] is True
    if legacy:
        assert document["tsdb"]["cache_dir"] == "original-cache"
        assert document["legacy_ini"]["custom"]["keep"] == "yes"
        assert ini.read_bytes() == original
    else:
        assert document["pypots"]["keep"] is True
        assert ("updated" in document["pypots"]) == after_replace
        assert "# keep comment" in config.read_text(encoding="utf-8")


@pytest.mark.parametrize("operation", ["load", "delete"])
@pytest.mark.parametrize("different_home", [False, True])
def test_cache_migration_serializes_public_operations(tmp_path, operation, different_home):
    home = tmp_path / "ecosystem"
    home.mkdir()
    source = tmp_path / "source-cache"
    destination = tmp_path / "destination-cache"
    raw = source / NAME
    raw.mkdir(parents=True)
    (raw / "LD2011_2014.txt").write_text(RAW, encoding="utf-8")
    (source / "sentinel").write_bytes(b"preserve")
    (home / "config.toml").write_text(
        tomlkit.dumps({"schema_version": 1, "tsdb": {"cache_dir": str(source)}}), encoding="utf-8"
    )
    copying, release, contended, done = [tmp_path / key for key in ("copying", "release", "contended", "done")]
    migrate_code = """
import sys, time
from pathlib import Path
import tsdb
from tsdb.utils import file
copytree = file.shutil.copytree
def pause(*args, **kwargs):
    if Path(args[0]) == Path(sys.argv[1]):
        Path(sys.argv[3]).touch()
        deadline = time.monotonic() + 30
        while not Path(sys.argv[4]).exists() and time.monotonic() < deadline:
            time.sleep(.02)
        assert Path(sys.argv[4]).exists()
    return copytree(*args, **kwargs)
file.shutil.copytree = pause
tsdb.migrate_cache(sys.argv[2])
"""
    operation_code = """
import sys
from pathlib import Path
import tsdb
from tsdb import data_processing
from tsdb.utils import cache_lock
# Observe an actual retry after the nonblocking native lock attempt failed.
original = cache_lock.time.sleep
def observe(seconds):
    Path(sys.argv[3]).touch()
    original(seconds)
cache_lock.time.sleep = observe
# A missing dataset must never trigger an external request in this test.
def no_network(*args, **kwargs):
    raise AssertionError('Unexpected download')
data_processing.download_and_extract = no_network
kwargs = {'cache_dir': sys.argv[2]} if sys.argv[2] else {}
if sys.argv[1] == 'load':
    assert tsdb.load('electricity_load_diagrams', **kwargs)['X']['meter'].tolist() == [1.5]
else:
    tsdb.delete_cache('electricity_load_diagrams', **kwargs)
Path(sys.argv[4]).touch()
"""
    # A lexical alias must resolve to the same physical destination lock.
    anchor = tmp_path / "alias-anchor"
    anchor.mkdir()
    alias = anchor / ".." / destination.name
    with _workers(tmp_path) as start:
        migration = start(migrate_code, home, source, destination, copying, release)
        _wait_for(copying, migration)
        competing = start(
            operation_code,
            tmp_path / "other-home" if different_home else home,
            operation,
            alias if different_home else "",
            contended,
            done,
        )
        _wait_for(contended, competing)
        # A failed native lock attempt proves real contention, not just scheduling.
        assert not done.exists()
        assert source.is_dir() and not destination.exists()
        release.touch()
        _finish(migration)
        _finish(competing)
    assert done.exists() and not source.exists()
    assert (destination / "sentinel").read_bytes() == b"preserve"
    document = tomlkit.parse((home / "config.toml").read_text(encoding="utf-8"))
    assert Path(document["tsdb"]["cache_dir"]) == destination
    if operation == "load":
        assert (destination / NAME / f"{NAME}_cache.pkl").is_file()
    else:
        assert not (destination / NAME).exists()
    if different_home:
        assert not (tmp_path / "other-home").exists()
