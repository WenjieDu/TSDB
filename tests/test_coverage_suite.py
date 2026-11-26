"""Ensure the optional gated-dataset credential is scoped to live testing."""

# License: BSD-3-Clause

from types import SimpleNamespace

from scripts import coverage_suite


def test_hf_token_is_not_passed_to_offline_or_reporting(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setenv("HF_TOKEN", "synthetic-test-token")
    monkeypatch.setenv("TSDB_CI_RAW_CACHE", "raw-cache")

    def run(command, *, env, check):
        calls.append((command, env, check))
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(coverage_suite.subprocess, "run", run)
    assert coverage_suite.run_suite(tmp_path, "offline", "not network", "synthetic-test-token") == 0
    assert coverage_suite.run_suite(tmp_path, "live", "network", "synthetic-test-token") == 0
    coverage_suite.combine(tmp_path)
    assert "HF_TOKEN" not in calls[0][1]
    assert "TSDB_CI_RAW_CACHE" not in calls[0][1]
    assert calls[1][1]["HF_TOKEN"] == "synthetic-test-token"
    assert all("HF_TOKEN" not in env for _, env, _ in calls[2:])
    assert all("synthetic-test-token" not in command for command, _, _ in calls)


def test_live_suite_without_token_does_not_invent_credentials(tmp_path, monkeypatch):
    monkeypatch.delenv("HF_TOKEN", raising=False)

    def run(command, *, env, check):
        assert "HF_TOKEN" not in env
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(coverage_suite.subprocess, "run", run)
    assert coverage_suite.run_suite(tmp_path, "live", "network") == 0
