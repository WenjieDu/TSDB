"""Validate an immutable stable release checkout and its distribution artifacts."""

# License: BSD-3-Clause

import argparse
import ast
import re
import subprocess
import tarfile
import zipfile
from email.parser import BytesParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STABLE_TAG = re.compile(r"v(?:0|[1-9]\d*)(?:\.(?:0|[1-9]\d*)){1,2}", flags=re.ASCII)


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def source_version():
    tree = ast.parse((ROOT / "tsdb/version.py").read_text(encoding="utf-8"))
    for statement in tree.body:
        if isinstance(statement, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "__version__" for target in statement.targets
        ):
            return ast.literal_eval(statement.value)
    raise ValueError("Could not find the literal package version")


def validate_checkout(tag, event_sha):
    if not STABLE_TAG.fullmatch(tag):
        raise ValueError(f"Expected a stable vX.Y or vX.Y.Z release tag, got {tag!r}")
    head = git("rev-parse", "HEAD")
    tagged = git("rev-parse", "--verify", f"refs/tags/{tag}^{{commit}}")
    if head != tagged or (event_sha and head != event_sha):
        raise ValueError("Checkout, release tag and release event must identify the same commit")
    subprocess.run(["git", "merge-base", "--is-ancestor", head, "refs/remotes/origin/main"], cwd=ROOT, check=True)
    version = source_version()
    if tag != f"v{version}":
        raise ValueError(f"Release tag {tag!r} does not match package version {version!r}")
    print(f"PASS: {tag} -> {head}, package version {version}, reachable from main", flush=True)
    return version, head


def distribution_metadata(dist):
    files = sorted(dist.iterdir())
    wheels = list(dist.glob("*.whl"))
    sdists = list(dist.glob("*.tar.gz"))
    if len(files) != 2 or len(wheels) != 1 or len(sdists) != 1 or not all(path.is_file() for path in files):
        raise ValueError("Expected exactly one wheel and one source distribution")
    with zipfile.ZipFile(wheels[0]) as archive:
        (name,) = (name for name in archive.namelist() if name.endswith(".dist-info/METADATA"))
        wheel_metadata = BytesParser().parsebytes(archive.read(name))
    with tarfile.open(sdists[0]) as archive:
        (member,) = (
            member
            for member in archive.getmembers()
            if member.name.count("/") == 1 and member.name.endswith("/PKG-INFO")
        )
        stream = archive.extractfile(member)
        if stream is None:
            raise ValueError("Missing source distribution metadata")
        with stream:
            source_metadata = BytesParser().parsebytes(stream.read())
    return wheel_metadata, source_metadata


def validate_distributions(dist, version):
    for metadata in distribution_metadata(dist):
        if metadata["Name"] != "tsdb" or metadata["Version"] != version or metadata["Requires-Python"] != ">=3.10":
            raise ValueError("Distribution metadata does not match the TSDB release")
    from packaging.requirements import Requirement

    expected_deps = {
        Requirement(line)
        for line in (ROOT / "requirements/requirements.txt").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    }
    expected_deps.add(Requirement('huggingface_hub; extra == "tsqa"'))
    for metadata in distribution_metadata(dist):
        if {Requirement(value) for value in metadata.get_all("Requires-Dist", [])} != expected_deps:
            raise ValueError("Distribution runtime dependencies differ from the declared requirements")
        if metadata.get_all("Provides-Extra", []) != ["tsqa"]:
            raise ValueError("Distribution TSQA extra is missing or unexpected")
    license_bytes = (ROOT / "LICENSE").read_bytes()
    wheel = next(dist.glob("*.whl"))
    expected = {path.relative_to(ROOT).as_posix() for path in (ROOT / "tsdb").rglob("*.py")}
    expected.add("tsdb/config_template.toml")
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        if not any(
            archive.read(name) == license_bytes
            for name in names
            if name.startswith(f"tsdb-{version}.dist-info/") and name.endswith("/LICENSE")
        ):
            raise ValueError("Wheel license differs from repository license")
        if "tsdb/config_template.toml" not in names or not all(
            name.startswith(("tsdb/", f"tsdb-{version}.dist-info/")) for name in names
        ):
            raise ValueError("Unexpected wheel contents or missing configuration template")
        if {name for name in names if name.startswith("tsdb/")} != expected:
            raise ValueError("Wheel source members differ from package source tree")
        if not any(name.endswith("/METADATA") for name in names):
            raise ValueError("Missing wheel metadata")
    with tarfile.open(next(dist.glob("*.tar.gz"))) as archive:
        licenses = [
            member
            for member in archive.getmembers()
            if member.name.count("/") == 1 and member.name.endswith("/LICENSE")
        ]
        if len(licenses) != 1 or archive.extractfile(licenses[0]).read() != license_bytes:
            raise ValueError("Sdist license differs from repository license")
        members = {member.name.split("/", 1)[-1] for member in archive.getmembers() if member.isfile()}
        if not expected.issubset(members) or any(name.startswith(("build/", "dist/", "tests/")) for name in members):
            raise ValueError("Unexpected sdist contents or missing package sources")
    print(f"PASS: both distribution versions match {version}; Python floor and package contents valid", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", default="")
    parser.add_argument("--event-sha", default="")
    parser.add_argument("--dist", type=Path)
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args()
    if args.tag:
        version, head = validate_checkout(args.tag, args.event_sha)
    else:
        if args.event_sha:
            raise ValueError("Release event requires an explicit tag")
        version, head = source_version(), git("rev-parse", "HEAD")
    if args.dist is not None:
        validate_distributions(args.dist, version)
    if args.github_output is not None:
        with args.github_output.open("a", encoding="utf-8") as output:
            output.write(f"version={version}\ncommit={head}\n")


if __name__ == "__main__":
    main()
