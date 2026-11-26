"""Isolate test initialization and cache writes from the user's real HOME."""

# License: BSD-3-Clause

import tempfile

import pytest


def pytest_configure(config):
    home = tempfile.TemporaryDirectory(prefix="tsdb-test-home-")
    patch = pytest.MonkeyPatch()
    patch.setenv("HOME", home.name)
    patch.setenv("USERPROFILE", home.name)
    patch.delenv("TSDB_LEGACY_CONFIG_ENCODING", raising=False)
    config.add_cleanup(home.cleanup)
    config.add_cleanup(patch.undo)
