"""Import boundaries are part of the shared TSDB infrastructure contract."""

# License: BSD-3-Clause

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_logger_and_registry_are_independent_of_data_infrastructure(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    legacy = home / ".tsdb"
    legacy.mkdir()
    (legacy / "sentinel.txt").write_text("preserve", encoding="utf-8")
    env = os.environ.copy()
    env.update(HOME=str(home), USERPROFILE=str(home), PYTHONPATH=str(ROOT))
    code = """
import logging
import sys
import tsdb
from tsdb.utils.logging import Logger, logger
assert callable(Logger)
assert isinstance(logger, logging.Logger)
names = tsdb.list()
assert "physionet_2019" in names
original = tuple(names)
names.clear()
assert tuple(tsdb.list()) == original
assert 'load' in dir(tsdb)
assert 'CACHED_DATASET_DIR' in dir(tsdb)
for name in ('numpy', 'pandas', 'sklearn', 'scipy', 'requests', 'pyarrow', 'tsdb.data_processing', 'tsdb.utils.config'):
    assert name not in sys.modules, name
"""
    result = subprocess.run(
        [sys.executable, "-S", "-c", code], cwd=tmp_path, env=env, capture_output=True, timeout=60, check=False
    )
    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    assert not (home / ".pypots").exists()
    assert (legacy / "sentinel.txt").read_text(encoding="utf-8") == "preserve"


def test_public_exports_are_preserved():
    import tsdb

    expected = {
        "CACHED_DATASET_DIR",
        "__version__",
        "delete_cache",
        "download_and_extract",
        "download_url",
        "list",
        "list_cache",
        "load",
        "migrate",
        "migrate_cache",
        "pickle_dump",
        "pickle_load",
        "purge_path",
    }
    assert set(tsdb.__all__) == expected
    for name in expected:
        assert getattr(tsdb, name) is not None
