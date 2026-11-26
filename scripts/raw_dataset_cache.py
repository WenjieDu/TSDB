"""Opt-in, raw-only CI cache for explicitly reviewed public dataset sources."""

# License: BSD-3-Clause

import hashlib
import json
import os
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

from tsdb.database import DATABASE

# Only cache sources whose public redistribution terms have been reviewed.
# The suffix allowlist deliberately excludes serialized Python objects.
POLICY = {
    "physionet_2019": ("https://physionet.org/content/challenge-2019/1.0.0/", (".psv",)),
    "electricity_load_diagrams": ("https://archive.ics.uci.edu/dataset/321/electricityloaddiagrams20112014", (".txt",)),
    "beijing_multisite_air_quality": (
        "https://archive.ics.uci.edu/dataset/501/beijing+multi+site+air+quality",
        (".csv",),
    ),
    "italy_air_quality": ("https://archive.ics.uci.edu/dataset/360/air+quality", (".csv", ".xlsx")),
}
# Match the reviewed upstream URLs exactly; a source change requires a fresh license review.
REVIEWED_SOURCES = {
    "physionet_2019": [
        "https://physionet-open.s3.amazonaws.com/challenge-2019/1.0.0/training/training_setA/",
        "https://physionet-open.s3.amazonaws.com/challenge-2019/1.0.0/training/training_setB/",
    ],
    "electricity_load_diagrams": "https://archive.ics.uci.edu/ml/machine-learning-databases/00321/LD2011_2014.txt.zip",
    "beijing_multisite_air_quality": "https://archive.ics.uci.edu/ml/machine-learning-databases/00501/PRSA2017_Data_20130301-20170228.zip",
    "italy_air_quality": "https://archive.ics.uci.edu/static/public/360/air+quality.zip",
}
MAX_DATASET_BYTES = 1024**3
MAX_CACHE_BYTES = 2 * 1024**3


def cache_key(now=None):
    """Rotate each Sunday UTC; invalidate on source or cache-policy changes."""
    today = (now or datetime.now(timezone.utc)).date()
    sunday = today - timedelta(days=(today.weekday() + 1) % 7)
    sources = {name: DATABASE[name] for name in POLICY}
    if sources != REVIEWED_SOURCES:
        raise ValueError("Raw cache source changed; review its redistribution terms before caching")
    identity = json.dumps(sources, sort_keys=True).encode()
    digest = hashlib.sha256(identity + Path(__file__).read_bytes()).hexdigest()[:24]
    return f"tsdb-public-raw-v1-{sunday.isoformat()}-{digest}"


def inventory(root, name):
    """Reject links, non-data files and oversized or empty snapshots; hash raw bytes."""
    if DATABASE[name] != REVIEWED_SOURCES[name]:
        raise ValueError("Raw cache source changed; review its redistribution terms")
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Invalid raw cache directory")
    files = {}
    size = 0
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError("Linked raw cache entry")
        if path.is_dir():
            continue
        if not path.is_file() or path.suffix.lower() not in POLICY[name][1]:
            raise ValueError(f"Unexpected raw cache member: {path.name}")
        count = path.stat().st_size
        size += count
        if size > MAX_DATASET_BYTES:
            raise ValueError("Raw dataset exceeds cache budget")
        with path.open("rb") as stream:
            digest = hashlib.sha256()
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        files[path.relative_to(root).as_posix()] = [count, digest.hexdigest()]
    if not files or not size:
        raise ValueError("Empty raw cache snapshot")
    return {
        "source": DATABASE[name],
        "attribution": POLICY[name][0],
        "license": "CC BY 4.0",
        "bytes": size,
        "files": files,
    }


def restore(root, name, target):
    """Restore only verified raw data into a private test directory."""
    entry = root / name
    if not os.path.lexists(entry):
        return False
    if entry.is_symlink() or not entry.is_dir() or {p.name for p in entry.iterdir()} != {"raw", "manifest.json"}:
        raise ValueError("Invalid dataset cache entry")
    manifest = entry / "manifest.json"
    if manifest.is_symlink() or not manifest.is_file():
        raise ValueError("Invalid cache manifest")
    actual = inventory(entry / "raw", name)
    if actual != json.loads(manifest.read_text(encoding="utf-8")):
        raise ValueError("Raw cache integrity or source identity mismatch")
    shutil.copytree(entry / "raw", target)
    print(f"RAW CACHE HIT {name}: {actual['bytes']} bytes, {len(actual['files'])} files", flush=True)
    return True


def store(root, name, target):
    """Snapshot raw data only after a successful cold load and cache readback."""
    root.mkdir(parents=True, exist_ok=True)
    entry = root / name
    if os.path.lexists(entry):
        raise ValueError("Refusing to replace existing raw cache entry")
    manifest = inventory(target, name)
    entry.mkdir()
    shutil.copytree(target, entry / "raw")
    (entry / "manifest.json").write_text(json.dumps(manifest, sort_keys=True), encoding="utf-8")
    print(f"RAW CACHE SEED {name}: {manifest['bytes']} bytes, {len(manifest['files'])} files", flush=True)


def verify(root):
    """Validate the complete cache allowlist, integrity and uncompressed budget before upload."""
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Invalid raw cache root")
    total = 0
    for entry in root.iterdir():
        if entry.name not in POLICY or entry.is_symlink() or not entry.is_dir():
            raise ValueError("Unexpected raw cache entry")
        if {p.name for p in entry.iterdir()} != {"raw", "manifest.json"}:
            raise ValueError("Unexpected raw cache members")
        manifest = entry / "manifest.json"
        if manifest.is_symlink() or not manifest.is_file():
            raise ValueError("Invalid manifest")
        actual = inventory(entry / "raw", entry.name)
        if actual != json.loads(manifest.read_text(encoding="utf-8")):
            raise ValueError("Raw cache integrity mismatch")
        total += actual["bytes"]
    if {entry.name for entry in root.iterdir()} != set(POLICY) or total > MAX_CACHE_BYTES:
        raise ValueError("Incomplete cache or total size exceeds 2 GiB")
    print(f"RAW CACHE VERIFIED {total} uncompressed bytes", flush=True)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.verify:
        verify(args.verify)
    else:
        print(cache_key())
