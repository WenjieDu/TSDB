"""Identify the original and conventional Vessel AIS Parquet filenames."""

# License: BSD-3-Clause

import re
from pathlib import Path

_ORIGINAL_NAME = re.compile(r"2020-2_group_[0-9]+")


def ais_parquet_files(root):
    """Return AIS Parquet paths in filesystem order; reject malformed candidates."""
    directory = Path(root) / "parquets"
    files = []
    if directory.is_dir():
        for path in directory.iterdir():
            if not (path.suffix == ".parquet" or _ORIGINAL_NAME.fullmatch(path.name)):
                continue
            if not path.is_file() or path.stat().st_size < 12:
                raise ValueError(f"Invalid AIS Parquet file: {path.name}")
            with path.open("rb") as stream:
                header = stream.read(4)
                stream.seek(-4, 2)
                footer = stream.read(4)
            if header != b"PAR1" or footer != b"PAR1":
                raise ValueError(f"Invalid AIS Parquet file: {path.name}")
            files.append(path)
    if not files:
        raise ValueError("Missing AIS Parquet files in parquets/")
    return files
