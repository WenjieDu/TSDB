"""Run offline and live tests once each and report their coverage union."""

# License: BSD-3-Clause

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def run_suite(output, scope, selector, hf_token=None):
    """Record an independent coverage database and actual pytest exit status."""
    env = os.environ.copy()
    env.pop("HF_TOKEN", None)
    if scope == "live" and hf_token:
        env["HF_TOKEN"] = hf_token
    env["COVERAGE_FILE"] = str(output / f".coverage.{scope}")
    env["TSDB_CI_DATASET_REPORT"] = str(output / "dataset-modes")
    if scope == "offline":
        env.pop("TSDB_CI_RAW_CACHE", None)
    command = [
        sys.executable,
        "-m",
        "pytest",
        "-rA",
        "-m",
        selector,
        "tests",
        "--cov=tsdb",
        "--cov-report=term",
        f"--cov-report=json:{output / (scope + '.json')}",
        f"--cov-report=xml:{output / (scope + '.xml')}",
        f"--junitxml={output / (scope + '-pytest.xml')}",
    ]
    return subprocess.run(command, env=env, check=False).returncode


def combine(output):
    env = os.environ.copy()
    env.pop("HF_TOKEN", None)
    env["COVERAGE_FILE"] = str(output / ".coverage")
    subprocess.run([sys.executable, "-m", "coverage", "combine", "--keep", str(output)], env=env, check=True)
    for kind, name in (("json", "combined.json"), ("xml", "combined.xml"), ("lcov", "combined.lcov")):
        subprocess.run([sys.executable, "-m", "coverage", kind, "-o", str(output / name)], env=env, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    # Retain the credential only for the live test subprocess, not git, offline tests or reporting.
    hf_token = os.environ.pop("HF_TOKEN", None)
    output = args.output.resolve()
    if subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], text=True).strip():
        parser.error("Coverage requires a clean tracked source checkout")
    output.mkdir(parents=True, exist_ok=False)
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    results = {"revision": revision, "python": sys.version, "scopes": {}}
    for scope, selector in (("offline", "not network"), ("live", "network")):
        status = run_suite(output, scope, selector, hf_token)
        results["scopes"][scope] = {"exit_code": status}
    if (
        subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip() != revision
        or subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], text=True).strip()
    ):
        raise RuntimeError("Source revision changed during coverage execution")
    if all((output / f".coverage.{scope}").is_file() for scope in ("offline", "live")):
        combine(output)
    for scope in ("offline", "live", "combined"):
        report = output / f"{scope}.json"
        if report.is_file():
            totals = json.loads(report.read_text(encoding="utf-8"))["totals"]
            results["scopes"].setdefault(scope, {}).update(
                {key: totals[key] for key in ("covered_lines", "num_statements", "percent_covered")}
            )
    results["dataset_modes"] = [
        json.loads(path.read_text(encoding="utf-8")) for path in sorted((output / "dataset-modes").glob("*.json"))
    ]
    results["live_data_mode"] = "cache-enabled" if os.environ.get("TSDB_CI_RAW_CACHE") else "cold-only"
    (output / "summary.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2))
    if any(results["scopes"][scope]["exit_code"] != 0 for scope in ("offline", "live")):
        return 1
    return 0 if "combined" in results["scopes"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
