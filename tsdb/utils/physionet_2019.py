"""Download the versioned PhysioNet 2019 training sets from its official AWS mirror."""

# License: BSD-3-Clause

import os
import re
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree

import requests
from requests.adapters import HTTPAdapter
from tqdm import tqdm
from urllib3.util.retry import Retry

from .logging import logger

_S3_ROOT = "https://physionet-open.s3.amazonaws.com/"
# The XML namespace is an identifier, not a network endpoint. Its literal URI
# must match the S3 response exactly. All actual requests use HTTPS (S5332 false positive).
_NS = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}  # NOSONAR
# The official release contains 20,336 subjects in A and 20,000 in B.
_SPLITS = (("training", 20336), ("training_setB", 20000))
_TIMEOUT = (10, 60)
_WORKERS = 16
_CHUNK_SIZE = 32


def _session():
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=0.5, status_forcelist=(429, 500, 502, 503, 504))
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def _parse_records(root, prefix, records):
    """Validate the objects on one listing page and accumulate unique records."""
    for entry in root.findall("s3:Contents", _NS):
        key = entry.findtext("s3:Key", namespaces=_NS)
        if key == prefix:  # optional S3 directory marker
            continue
        if not key or not key.startswith(prefix):
            raise RuntimeError(f"Unexpected object in PhysioNet listing: {key!r}")
        name = key[len(prefix) :]
        if not re.fullmatch(r"p\d+\.psv", name, flags=re.ASCII) or name in records:
            raise RuntimeError(f"Unexpected or duplicate PhysioNet record: {name!r}")
        size = int(entry.findtext("s3:Size", namespaces=_NS))
        if size <= 0:
            raise RuntimeError(f"Empty PhysioNet record: {name}")
        records[name] = size


def _get_next_token(root, seen_tokens):
    """Return the next continuation token, or None for the final page."""
    truncated = root.findtext("s3:IsTruncated", namespaces=_NS)
    if truncated == "false":
        return None
    token = root.findtext("s3:NextContinuationToken", namespaces=_NS)
    if truncated != "true" or not token or token in seen_tokens:
        raise RuntimeError("Invalid PhysioNet S3 pagination")
    seen_tokens.add(token)
    return token


def _list_records(url, expected_count):
    """Validate every page before downloading any patient records."""
    prefix = urlsplit(url).path.lstrip("/")
    records = {}
    token = None
    seen_tokens = set()
    with _session() as session:
        while True:
            params = {"list-type": "2", "prefix": prefix, "max-keys": 1000}
            if token is not None:
                params["continuation-token"] = token
            response = session.get(_S3_ROOT, params=params, timeout=_TIMEOUT)
            response.raise_for_status()
            root = ElementTree.fromstring(response.content)
            _parse_records(root, prefix, records)
            token = _get_next_token(root, seen_tokens)
            if token is None:
                break
    if len(records) != expected_count:
        raise RuntimeError(f"Expected {expected_count} PhysioNet records at {url}, found {len(records)}")
    return sorted(records.items())


def _download_chunk(url, directory, records):
    with _session() as session:
        for name, size in records:
            response = session.get(url + name, timeout=_TIMEOUT)
            response.raise_for_status()
            if len(response.content) != size:
                raise RuntimeError(f"Incomplete PhysioNet record: {name}")
            (directory / name).write_bytes(response.content)
    return len(records)


def _download_split(url, directory, records):
    directory.mkdir()
    chunks = [records[i : i + _CHUNK_SIZE] for i in range(0, len(records), _CHUNK_SIZE)]
    with (
        ThreadPoolExecutor(max_workers=_WORKERS) as executor,
        tqdm(
            total=len(records),
            desc=f"Downloading PhysioNet 2019 {directory.name}",
            unit="record",
            ascii=True,
        ) as progress,
    ):
        # Bound the queued work so a failed request cannot enqueue the entire dataset.
        for offset in range(0, len(chunks), _WORKERS):
            pending = [
                executor.submit(_download_chunk, url, directory, chunk) for chunk in chunks[offset : offset + _WORKERS]
            ]
            for future in pending:
                progress.update(future.result())


def download_physionet2019(urls, saving_path):
    """Publish both complete splits together, retaining the legacy cache layout."""
    if len(urls) != len(_SPLITS):
        raise RuntimeError("Both PhysioNet 2019 training splits are required")
    destination = Path(saving_path).absolute()
    if destination.exists():
        raise FileExistsError(str(destination))
    destination.parent.mkdir(parents=True, exist_ok=True)
    listings = [_list_records(url, count) for url, (_, count) in zip(urls, _SPLITS)]
    # Do not leave a partial dataset at the path that tsdb.load treats as cached.
    with tempfile.TemporaryDirectory(prefix=".physionet2019-", dir=destination.parent) as staging:
        data = Path(staging) / "data"
        data.mkdir()
        for url, (directory, _), records in zip(urls, _SPLITS, listings):
            _download_split(url, data / directory, records)
        if destination.exists():
            raise FileExistsError(str(destination))
        os.rename(data, destination)
    logger.info(f"Successfully downloaded PhysioNet 2019 data to {destination}")
