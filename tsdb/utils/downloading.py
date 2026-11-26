"""Download and safely publish datasets without exposing partial destinations."""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: BSD-3-Clause

import os
import shutil
import tempfile
import time
from pathlib import Path
from urllib.parse import unquote, urlsplit

import requests
from tqdm import tqdm

from ..database import dataset_spec
from .archive import archive_format, extract, member_path
from .logging import logger
from .physionet_2019 import download_physionet2019
from .tsqa import download_tsqa
from .vessel_ais import ais_parquet_files

_TIMEOUT = (10, 60)
_ATTEMPTS = 4
_RETRY_STATUS = {429, 500, 502, 503, 504}


class DownloadError(RuntimeError):
    """A source could not be downloaded or validated."""


class _IncompleteDownload(DownloadError):
    """The response did not contain the expected bytes."""


def _download_once(url: str, path: Path, name: str) -> None:
    with requests.get(url, stream=True, timeout=_TIMEOUT, headers={"Accept-Encoding": "identity"}) as response:
        response.raise_for_status()
        length = response.headers.get("Content-Length")
        # Requests transparently decodes Content-Encoding; only compare like-for-like bytes.
        size = (
            int(length)
            if length is not None and response.headers.get("Content-Encoding", "identity") == "identity"
            else None
        )
        written = 0
        with (
            path.open("wb") as output,
            tqdm(
                total=size, unit="B", unit_scale=True, unit_divisor=1024, desc=f"Downloading {name}", ascii=True
            ) as progress,
        ):
            for chunk in response.iter_content(chunk_size=64 * 1024):
                written += output.write(chunk)
                progress.update(len(chunk))
        if written == 0 or (size is not None and written != size):
            raise _IncompleteDownload(f"Incomplete download for {name}: expected {size}, received {written} bytes")


def _download(url: str, path: Path, name: str) -> None:
    for attempt in range(_ATTEMPTS):
        try:
            _download_once(url, path, name)
        except requests.HTTPError as exc:
            if exc.response is None or exc.response.status_code not in _RETRY_STATUS or attempt == _ATTEMPTS - 1:
                raise DownloadError(f"Download failed for {name}: {exc}") from exc
        except (
            requests.ConnectionError,
            requests.Timeout,
            requests.exceptions.ChunkedEncodingError,
            _IncompleteDownload,
        ) as exc:
            if attempt == _ATTEMPTS - 1:
                raise DownloadError(f"Download failed for {name}: {exc}") from exc
        except requests.RequestException as exc:
            raise DownloadError(f"Download failed for {name}: {exc}") from exc
        else:
            return
        time.sleep(0.5 * 2**attempt)


def _fetch(url: str, root: Path, work: Path) -> str:
    parts = urlsplit(url)
    name = unquote(parts.path.rsplit("/", 1)[-1])
    if parts.scheme not in ("http", "https") or not parts.netloc or member_path(root, name).parent != root:
        raise ValueError(f"Invalid download URL: {url!r}")
    kind = archive_format(name)
    archive = work / "download"
    _download(url, archive, name)
    extract(archive, root, name, kind)
    archive.unlink()
    return name[:-3] if kind == "gzip" else ""


def _check_destination(destination: Path) -> None:
    if os.path.lexists(destination):
        raise FileExistsError(f"Download destination already exists: {destination}")


def _validate_dataset(name: str, root: Path) -> None:
    spec = dataset_spec(name)
    if spec.loader_arg is not None:
        dataset = spec.loader_arg
        if not any(
            all(_nonempty(root / f"{dataset}_{split}.{ext}") for split in ("TRAIN", "TEST")) for ext in ("arff", "txt")
        ):
            raise DownloadError(f"Missing train/test files for {name}")
    for filename in spec.required_files:
        if not _nonempty(root / filename):
            raise DownloadError(f"Missing or empty required file: {filename}")
    if name == "vessel_ais":
        # The source archive contains extensionless Parquet files.
        try:
            ais_parquet_files(root)
        except ValueError as exc:
            raise DownloadError(str(exc)) from exc
    for directory, pattern in spec.required_directories:
        if not any(_nonempty(path) for path in (root / directory).glob(pattern)):
            raise DownloadError(f"Missing required dataset files: {directory}/{pattern}")


def _nonempty(path: Path) -> bool:
    return path.is_file() and path.stat().st_size > 0


def _publish(destination: Path, urls: tuple[str, ...], dataset_name: str | None = None) -> str:
    _check_destination(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".tsdb-download-", dir=destination.parent) as staging:
        work = Path(staging)
        root = work / "data"
        root.mkdir()
        result = ""
        if dataset_name is not None and dataset_spec(dataset_name).download_strategy == "huggingface":
            download_tsqa(urls[0].removeprefix("hf://"), root)
        else:
            for url in urls:
                result = _fetch(url, root, work)
        if not any(path.is_file() for path in root.rglob("*")):
            raise DownloadError("Download produced no files")
        if dataset_name is not None:
            _validate_dataset(dataset_name, root)
        _check_destination(destination)
        os.rename(root, destination)
    logger.info(f"Successfully downloaded data to {destination}")
    return str(destination / result)


def download_url(url: str, saving_path: str) -> str:
    """Download a CSV/TXT or supported archive into a new destination directory.

    The destination must not exist. Failed or interrupted downloads leave no
    partial destination. Return the directory (or decompressed .txt/.csv path
    for a single gzip file). TLS verification is not disabled.
    """
    return _publish(Path(saving_path).absolute(), (url,))


def _download_and_extract(url: str, saving_path: str) -> str:
    """Compatibility wrapper for the legacy generic URL helper."""
    result = download_url(url, saving_path)
    # Preserve the old helper's relative-path return convention.
    relative = Path(result).relative_to(Path(saving_path).absolute())
    return str(Path(saving_path) / relative)


def download_and_extract(dataset_name: str, dataset_saving_path: str) -> None:
    """Download a registered dataset's raw files into a new directory.

    All required sources must succeed before publication. An existing
    destination is never overwritten by this function.
    """
    spec = dataset_spec(dataset_name)
    destination = Path(dataset_saving_path).absolute()
    _check_destination(destination)
    if spec.download_strategy == "physionet_2019":
        download_physionet2019(spec.sources, str(destination))
        return
    _publish(destination, spec.sources, dataset_name)


def refresh_raw_dataset(dataset_name: str, destination: str, prepare=None):
    """Keep the old raw/cache directory until a replacement download is complete.

    An optional prepare callback validates and parses staged data before
    publication. If rollback fails, preserve the backup.
    """
    target = Path(destination).absolute()
    if target.is_symlink() or not target.is_dir():
        raise ValueError(f"Cannot refresh non-directory or linked cache: {target}")
    with tempfile.TemporaryDirectory(prefix=".tsdb-refresh-", dir=target.parent) as staging:
        replacement = Path(staging) / "data"
        download_and_extract(dataset_name, str(replacement))
        result = prepare(replacement) if prepare is not None else None
        backup_dir = Path(tempfile.mkdtemp(prefix=".tsdb-backup-", dir=target.parent))
        backup = backup_dir / "data"
        try:
            os.rename(target, backup)
            try:
                os.rename(replacement, target)
            except BaseException:
                # Never delete the old data if restoring it fails.
                if not os.path.lexists(target):
                    os.rename(backup, target)
                raise
        except BaseException:
            if backup.exists():
                logger.error(f"Original dataset retained at {backup}; restore it manually if needed.")
            else:
                backup_dir.rmdir()
            raise
        else:
            shutil.rmtree(backup_dir)
        return result
