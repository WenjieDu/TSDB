"""Build, install and validate exact TSDB release distributions."""

# License: BSD-3-Clause

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args, cwd=ROOT, env=None):
    print("+", *args, flush=True)
    subprocess.run(args, cwd=cwd, env=env, check=True)


def pip(*args):
    run(sys.executable, "-m", "pip", *args)


def smoke(output, name):
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    home = output / name
    home.mkdir()
    env.update(HOME=str(home), USERPROFILE=str(home))
    run(sys.executable, "-I", str(ROOT / "scripts/smoke_release.py"), cwd=output, env=env)


def install(output):
    output.mkdir(parents=True, exist_ok=True)
    dist = output / "dist"
    dist.mkdir()  # refuse stale artifacts
    # Build backend and all third-party dependencies were installed from the
    # hash-checked release requirements. Do not resolve anything again.
    run(sys.executable, "-m", "build", "--no-isolation", "--outdir", str(dist))
    (wheel,) = dist.glob("*.whl")
    (sdist,) = dist.glob("*.tar.gz")
    run(sys.executable, "-m", "twine", "check", "--strict", str(wheel), str(sdist))
    pip("install", "--no-deps", "--no-index", str(wheel))
    pip("check")
    smoke(output, "wheel-home")


def package(output):
    # Exercise the sdist independently without fetching another build backend.
    (sdist,) = (output / "dist").glob("*.tar.gz")
    pip("install", "--force-reinstall", "--no-deps", "--no-index", "--no-build-isolation", str(sdist))
    pip("check")
    smoke(output, "sdist-home")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("install", "package"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    {"install": install, "package": package}[args.command](args.output.resolve())


if __name__ == "__main__":
    main()
