"""Extract regular files and directories only, within a private staging tree."""

# License: BSD-3-Clause

import gzip
import shutil
import stat
import tarfile
import zipfile
from pathlib import Path

_RESERVED = {"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"} | {
    f"{prefix}{digit}" for prefix in ("COM", "LPT") for digit in "123456789¹²³"
}


def member_path(root: Path, name: str) -> Path:
    """Reject unsafe and non-portable archive paths before touching the filesystem."""
    if not name or name.startswith("/") or "\\" in name or "\x00" in name or ":" in name:
        raise ValueError(f"Unsafe archive path: {name!r}")
    parts = [part for part in name.split("/") if part not in ("", ".")]
    for part in parts:
        if (
            part == ".."
            or part.endswith((" ", "."))
            or part.split(".", 1)[0].rstrip().upper() in _RESERVED
            or any(ord(char) < 32 or char in '<>"|?*' for char in part)
        ):
            raise ValueError(f"Unsafe archive path: {name!r}")
    return root.joinpath(*parts)


def _write_file(source, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    # No overwriting, including collisions across different source archives.
    with target.open("xb") as output:
        shutil.copyfileobj(source, output, length=1024 * 1024)


def _extract_zip(archive: Path, root: Path) -> None:
    with zipfile.ZipFile(archive) as zf:
        for member in zf.infolist():
            target = member_path(root, member.orig_filename)
            kind = stat.S_IFMT(member.external_attr >> 16)
            if kind not in (0, stat.S_IFREG, stat.S_IFDIR):
                raise ValueError(f"Unsupported ZIP member type: {member.filename!r}")
            if member.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                if kind == stat.S_IFDIR or target == root:
                    raise ValueError(f"Invalid ZIP file member: {member.filename!r}")
                with zf.open(member) as source:
                    _write_file(source, target)


def _extract_tar(archive: Path, root: Path) -> None:
    with tarfile.open(archive, mode="r:*") as tf:
        for member in tf:
            target = member_path(root, member.name)
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            elif member.isfile() and target != root:
                with tf.extractfile(member) as source:
                    _write_file(source, target)
            else:
                raise ValueError(f"Unsupported TAR member type: {member.name!r}")


def archive_format(name: str) -> str:
    lower = name.lower()
    if lower.endswith((".txt", ".csv")):
        return "raw"
    if lower.endswith(".zip"):
        return "zip"
    if lower.endswith((".tar", ".tar.gz", ".tgz", ".tar.bz2", ".tbz2", ".tar.xz", ".txz")):
        return "tar"
    if lower.endswith((".txt.gz", ".csv.gz")):
        return "gzip"
    raise ValueError(f"Unsupported download format: {name!r}")


def extract(archive: Path, root: Path, name: str, kind: str) -> None:
    if kind == "zip":
        _extract_zip(archive, root)
    elif kind == "tar":
        _extract_tar(archive, root)
    elif kind == "gzip":
        with gzip.open(archive, "rb") as source:
            _write_file(source, member_path(root, name[:-3]))
    else:
        with archive.open("rb") as source:
            _write_file(source, member_path(root, name))
