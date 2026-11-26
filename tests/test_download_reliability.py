"""Deterministic checks for download staging, validation and archive safety."""

# License: BSD-3-Clause

import gzip
import io
import stat
import tarfile
import zipfile
from pathlib import Path

import pytest
import requests

import tsdb
from tsdb import data_processing
from tsdb.database import DATABASE
from tsdb.loading_funcs.tsqa import load_tsqa
from tsdb.utils import downloading, tsqa


def _zip(*members):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        for member, content in members:
            archive.writestr(member, content)
    return stream.getvalue()


def _tar(member, content=b"payload"):
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode="w:gz") as archive:
        if member.isfile():
            member.size = len(content)
            archive.addfile(member, io.BytesIO(content))
        else:
            archive.addfile(member)
    return stream.getvalue()


def _response(content=b"value\n1\n", status=200, length=None):
    response = requests.Response()
    response.status_code = status
    response._content = content
    response._content_consumed = True
    response.headers["Content-Length"] = str(len(content) if length is None else length)
    return response


@pytest.fixture
def serve(monkeypatch):
    calls = []
    responses = {}

    def get(url, **kwargs):
        calls.append(url)
        assert kwargs["timeout"] == (10, 60)
        assert kwargs["stream"] is True
        assert kwargs["headers"]["Accept-Encoding"] == "identity"
        item = responses[url].pop(0)
        if isinstance(item, BaseException):
            raise item
        return item

    monkeypatch.setattr(requests, "get", get)
    monkeypatch.setattr(downloading.time, "sleep", lambda _: None)
    return responses, calls


def test_multifile_download_publishes_only_complete_dataset(tmp_path, serve):
    responses, calls = serve
    name = "electricity_transformer_temperature"
    for url in DATABASE[name]:
        responses[url] = [_response()]
    destination = tmp_path / "dataset"
    tsdb.download_and_extract(name, destination)
    assert sorted(p.name for p in destination.iterdir()) == ["ETTh1.csv", "ETTh2.csv", "ETTm1.csv", "ETTm2.csv"]
    assert calls == DATABASE[name]
    assert list(tmp_path.iterdir()) == [destination]


@pytest.mark.parametrize("failure", ["404", "timeout", "truncated", "interrupted"])
def test_failed_multifile_download_leaves_no_partial_data(tmp_path, serve, failure):
    responses, calls = serve
    urls = DATABASE["electricity_transformer_temperature"]
    responses[urls[0]] = [_response()]
    failure_items = {
        "404": ([_response(status=404)], downloading.DownloadError),
        "timeout": ([requests.Timeout("timed out")] * 4, downloading.DownloadError),
        "truncated": ([_response(length=500) for _ in range(4)], downloading.DownloadError),
        "interrupted": ([KeyboardInterrupt()], KeyboardInterrupt),
    }
    responses[urls[1]], exception = failure_items[failure]
    attempts = len(responses[urls[1]])
    with pytest.raises(exception):
        tsdb.download_and_extract("electricity_transformer_temperature", tmp_path / "dataset")
    assert len(calls) == attempts + 1
    assert not list(tmp_path.iterdir())


def test_retry_transient_http_and_truncated_body(tmp_path, serve):
    responses, calls = serve
    url = "https://example.test/data.csv?revision=1"
    responses[url] = [_response(status=503), _response(length=100), _response(b"complete")]
    destination = tmp_path / "data"
    assert tsdb.download_url(url, destination) == str(destination)
    assert (destination / "data.csv").read_bytes() == b"complete"
    assert calls == [url] * 3


def test_existing_destination_preserved(tmp_path, serve):
    _, calls = serve
    destination = tmp_path / "existing"
    destination.mkdir()
    (destination / "sentinel").write_bytes(b"keep")
    with pytest.raises(FileExistsError):
        tsdb.download_url("https://example.test/data.zip", destination)
    assert (destination / "sentinel").read_bytes() == b"keep"
    assert not calls


def test_unsupported_format_fails_before_network(tmp_path, serve):
    _, calls = serve
    with pytest.raises(ValueError, match="Unsupported download format"):
        tsdb.download_url("https://example.test/data.exe", tmp_path / "data")
    assert not calls
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize(
    "member",
    [
        "../escape.txt",
        "/escape.txt",
        "C:/escape.txt",
        "..\\escape.txt",
        "nested/../../escape.txt",
        "NUL.txt",
        "a:stream",
    ],
)
def test_zip_rejects_unsafe_paths(tmp_path, serve, member):
    responses, _ = serve
    url = "https://example.test/data.zip"
    responses[url] = [_response(_zip(("valid.txt", b"valid"), (member, b"bad")))]
    with pytest.raises(ValueError, match="Unsafe archive path"):
        tsdb.download_url(url, tmp_path / "data")
    assert not list(tmp_path.iterdir())


def test_zip_rejects_symlink(tmp_path, serve):
    responses, _ = serve
    url = "https://example.test/data.zip"
    link = zipfile.ZipInfo("linked")
    link.create_system = 3
    link.external_attr = (stat.S_IFLNK | 0o777) << 16
    responses[url] = [_response(_zip((link, b"../escape")))]
    with pytest.raises(ValueError, match="Unsupported ZIP member type"):
        tsdb.download_url(url, tmp_path / "data")
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("kind", [tarfile.SYMTYPE, tarfile.LNKTYPE, tarfile.FIFOTYPE, tarfile.CHRTYPE])
def test_tar_rejects_links_and_special_members(tmp_path, serve, kind):
    responses, _ = serve
    url = "https://example.test/data.tar.gz"
    member = tarfile.TarInfo("unsafe")
    member.type = kind
    member.linkname = "../escape"
    responses[url] = [_response(_tar(member))]
    with pytest.raises(ValueError, match="Unsupported TAR member type"):
        tsdb.download_url(url, tmp_path / "data")
    assert not list(tmp_path.iterdir())


def test_tar_rejects_traversal(tmp_path, serve):
    responses, _ = serve
    url = "https://example.test/data.tar.gz"
    responses[url] = [_response(_tar(tarfile.TarInfo("../escape.txt")))]
    with pytest.raises(ValueError, match="Unsafe archive path"):
        tsdb.download_url(url, tmp_path / "data")
    assert not list(tmp_path.iterdir())


def test_regular_tar_and_gzip(tmp_path, serve):
    responses, _ = serve
    tar_url = "https://example.test/data.tar.gz"
    responses[tar_url] = [_response(_tar(tarfile.TarInfo("./nested/file.txt")))]
    assert tsdb.download_url(tar_url, tmp_path / "tar") == str(tmp_path / "tar")
    assert (tmp_path / "tar/nested/file.txt").read_bytes() == b"payload"
    gzip_url = "https://example.test/traffic.txt.gz"
    responses[gzip_url] = [_response(gzip.compress(b"data"))]
    assert tsdb.download_url(gzip_url, tmp_path / "gzip") == str(tmp_path / "gzip/traffic.txt")
    assert (tmp_path / "gzip/traffic.txt").read_bytes() == b"data"


def test_reject_missing_required_dataset_files(tmp_path, serve):
    responses, _ = serve
    name = "electricity_load_diagrams"
    responses[DATABASE[name]] = [_response(_zip(("wrong.txt", b"data")))]
    with pytest.raises(downloading.DownloadError, match="Missing or empty required file"):
        tsdb.download_and_extract(name, tmp_path / "data")
    assert not list(tmp_path.iterdir())


def test_failed_refresh_preserves_existing_raw_and_parsed_cache(tmp_path, serve, monkeypatch):
    responses, _ = serve
    name = "electricity_load_diagrams"
    monkeypatch.setitem(vars(data_processing), "CACHED_DATASET_DIR", str(tmp_path))
    destination = tmp_path / name
    destination.mkdir()
    (destination / "LD2011_2014.txt").write_bytes(b"existing raw")
    (destination / f"{name}_cache.pkl").write_bytes(b"existing parsed")
    responses[DATABASE[name]] = [_response(status=404)]
    with pytest.raises(downloading.DownloadError):
        tsdb.load(name, use_cache=False)
    assert (destination / "LD2011_2014.txt").read_bytes() == b"existing raw"
    assert (destination / f"{name}_cache.pkl").read_bytes() == b"existing parsed"
    assert list(tmp_path.iterdir()) == [destination]


def test_successful_refresh_replaces_raw_data(tmp_path, serve, monkeypatch):
    responses, _ = serve
    name = "electricity_load_diagrams"
    monkeypatch.setitem(vars(data_processing), "CACHED_DATASET_DIR", str(tmp_path))
    url = DATABASE[name]
    first = b";MT_001\n2011-01-01 00:00:00;1,5\n"
    second = b";MT_001\n2011-01-01 00:00:00;9,5\n"
    responses[url] = [_response(_zip(("LD2011_2014.txt", first))), _response(_zip(("LD2011_2014.txt", second)))]
    assert tsdb.load(name)["X"]["MT_001"].tolist() == [1.5]
    assert tsdb.load(name, use_cache=False)["X"]["MT_001"].tolist() == [9.5]
    assert tsdb.load(name)["X"]["MT_001"].tolist() == [9.5]
    assert list(tmp_path.iterdir()) == [tmp_path / name]


def test_tsqa_raw_download_and_local_loading(tmp_path, monkeypatch):
    calls = []

    def snapshot(**kwargs):
        calls.append(kwargs)
        root = Path(kwargs["local_dir"])
        for name in tsqa.TSQA_CSV_FILES.values():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("value\n1\n", encoding="utf-8")
        return str(root)

    monkeypatch.setattr(tsqa, "snapshot_download", snapshot)
    destination = tmp_path / "tsqa"
    tsdb.download_and_extract("tsqa", destination)
    assert tsqa.has_tsqa_files(destination)
    assert set(load_tsqa(destination)) == set(tsqa.TSQA_CSV_FILES)
    assert len(calls) == 1
    assert calls[0]["repo_id"] == "Time-MQA/TSQA"
    assert list(tmp_path.iterdir()) == [destination]


def test_tsqa_incomplete_snapshot_is_not_published(tmp_path, monkeypatch):
    monkeypatch.setattr(tsqa, "snapshot_download", lambda **_: None)
    with pytest.raises(RuntimeError, match="missing required CSV files"):
        tsdb.download_and_extract("tsqa", tmp_path / "tsqa")
    assert not list(tmp_path.iterdir())


def test_refresh_publication_failure_restores_previous_data(tmp_path, serve, monkeypatch):
    responses, _ = serve
    name = "electricity_load_diagrams"
    target = tmp_path / name
    target.mkdir()
    (target / "sentinel").write_bytes(b"keep")
    responses[DATABASE[name]] = [_response(_zip(("LD2011_2014.txt", b"new")))]
    rename = downloading.os.rename

    def fail_publication(source, destination):
        if Path(destination) == target and Path(source).parent.name.startswith(".tsdb-refresh-"):
            raise OSError("simulated publication failure")
        return rename(source, destination)

    monkeypatch.setattr(downloading.os, "rename", fail_publication)
    with pytest.raises(OSError, match="simulated publication failure"):
        downloading.refresh_raw_dataset(name, target)
    assert (target / "sentinel").read_bytes() == b"keep"
    assert list(tmp_path.iterdir()) == [target]


def test_refresh_failed_rollback_retains_backup(tmp_path, serve, monkeypatch):
    responses, _ = serve
    name = "electricity_load_diagrams"
    target = tmp_path / name
    target.mkdir()
    (target / "sentinel").write_bytes(b"keep")
    responses[DATABASE[name]] = [_response(_zip(("LD2011_2014.txt", b"new")))]
    rename = downloading.os.rename

    def fail_rename(source, destination):
        if Path(destination) == target:
            raise OSError("simulated rename failure")
        return rename(source, destination)

    monkeypatch.setattr(downloading.os, "rename", fail_rename)
    with pytest.raises(OSError, match="simulated rename failure"):
        downloading.refresh_raw_dataset(name, target)
    backups = list(tmp_path.glob(".tsdb-backup-*/data/sentinel"))
    assert len(backups) == 1
    assert backups[0].read_bytes() == b"keep"
    assert not target.exists()
    assert not list(tmp_path.glob(".tsdb-refresh-*"))


def test_stream_interruption_retries_without_appending(tmp_path, serve):
    responses, calls = serve
    url = "https://example.test/data.csv"
    interrupted = _response(b"old")

    def broken_stream(**_):
        yield b"partial"
        raise requests.exceptions.ChunkedEncodingError("lost connection")

    interrupted.iter_content = broken_stream
    responses[url] = [interrupted, _response(b"replacement")]
    tsdb.download_url(url, tmp_path / "data")
    assert (tmp_path / "data/data.csv").read_bytes() == b"replacement"
    assert calls == [url, url]
