"""Isolate test initialization and cache writes from the user's real HOME."""

# License: BSD-3-Clause

import tempfile

import pytest


def pytest_configure(config):
    home = tempfile.TemporaryDirectory(prefix="tsdb-test-home-")
    patch = pytest.MonkeyPatch()
    patch.setenv("HOME", home.name)
    patch.setenv("USERPROFILE", home.name)
    for key in ("TSDB_LEGACY_CONFIG_ENCODING", "PYPOTS_HOME", "TSDB_CACHE_DIR"):
        patch.delenv(key, raising=False)
    config.add_cleanup(home.cleanup)
    config.add_cleanup(patch.undo)
