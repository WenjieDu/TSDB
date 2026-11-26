"""Offline regression coverage for the official PhysioNet 2019 object download."""

# License: BSD-3-Clause

import xml.etree.ElementTree as ET

import pytest

import tsdb
from tsdb import data_processing, download_and_extract
from tsdb.database import DATABASE
from tsdb.loading_funcs.physionet_2019 import load_physionet2019
from tsdb.utils import physionet_2019 as source


def _page(prefix, records, token=None):
    root = ET.Element("ListBucketResult", xmlns=source._NS["s3"])
    ET.SubElement(root, "IsTruncated").text = "true" if token else "false"
    if token:
        ET.SubElement(root, "NextContinuationToken").text = token
    for name, size in records:
        entry = ET.SubElement(root, "Contents")
        ET.SubElement(entry, "Key").text = prefix + name
        ET.SubElement(entry, "Size").text = str(size)
    return ET.tostring(root)


class Response:
    def __init__(self, content):
        self.content = content

    def raise_for_status(self):
        pass


@pytest.fixture
def simulated_source(monkeypatch):
    payload = b"Age|Gender|Unit1|Unit2|HospAdmTime|ICULOS|SepsisLabel\n65|1|0|1|-1|1|0\n"
    urls = DATABASE["physionet_2019"]
    names = [["p000001.psv", "p000002.psv"], ["p100001.psv"]]
    prefixes = [url[len(source._S3_ROOT) :] for url in urls]
    monkeypatch.setattr(source, "_SPLITS", (("training", 2), ("training_setB", 1)))
    requests = []
    files = {url + name: payload for url, split in zip(urls, names) for name in split}

    class Session:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def get(self, url, params=None, timeout=None):
            assert timeout == source._TIMEOUT
            requests.append((url, params))
            if params is None:
                return Response(files[url])
            index = prefixes.index(params["prefix"])
            records = [(name, len(payload)) for name in names[index]]
            if index == 0:
                if "continuation-token" not in params:
                    return Response(_page(prefixes[index], records[:1], "page-two"))
                assert params["continuation-token"] == "page-two"
                records = records[1:]
            return Response(_page(prefixes[index], records))

    monkeypatch.setattr(source, "_session", Session)
    return files, requests


def test_download_both_splits_preserves_loader_contract(tmp_path, simulated_source):
    files, requests = simulated_source
    destination = tmp_path / "cache" / "physionet_2019"
    download_and_extract("physionet_2019", str(destination))
    assert sorted(p.name for p in (destination / "training").iterdir()) == [
        "p000001.psv",
        "p000002.psv",
    ]
    assert sorted(p.name for p in (destination / "training_setB").iterdir()) == ["p100001.psv"]
    loaded = load_physionet2019(str(destination))
    assert set(loaded) == {"training_setA", "training_setB", "static_features"}
    assert set(loaded["training_setA"].RecordID) == {"p000001", "p000002"}
    assert set(loaded["training_setB"].RecordID) == {"p100001"}
    assert loaded["training_setA"].SepsisLabel.tolist() == [0, 0]
    assert len([params for _, params in requests if params]) == 3
    assert len([url for url, params in requests if params is None]) == len(files)
    assert list(destination.parent.iterdir()) == [destination]


def test_incomplete_download_never_publishes_cache(tmp_path, simulated_source):
    files, _ = simulated_source
    files[DATABASE["physionet_2019"][1] + "p100001.psv"] = b"truncated"
    destination = tmp_path / "physionet_2019"
    with pytest.raises(RuntimeError, match="Incomplete PhysioNet record"):
        download_and_extract("physionet_2019", str(destination))
    assert not destination.exists()
    assert not list(tmp_path.iterdir())


def test_reject_missing_records_before_download(tmp_path, simulated_source, monkeypatch):
    _, requests = simulated_source
    monkeypatch.setattr(source, "_SPLITS", (("training", 3), ("training_setB", 1)))
    with pytest.raises(RuntimeError, match="Expected 3 PhysioNet records"):
        download_and_extract("physionet_2019", str(tmp_path / "cache"))
    assert all(params for _, params in requests)
    assert not list(tmp_path.iterdir())


def test_existing_cache_is_not_overwritten(tmp_path, simulated_source):
    _, requests = simulated_source
    path = tmp_path / "existing"
    path.mkdir()
    (path / "marker").write_bytes(b"keep")
    with pytest.raises(FileExistsError):
        download_and_extract("physionet_2019", str(path))
    assert (path / "marker").read_bytes() == b"keep"
    assert not requests


def test_public_load_and_cached_reads(tmp_path, simulated_source, monkeypatch):
    _, requests = simulated_source
    monkeypatch.setattr(data_processing, "CACHED_DATASET_DIR", str(tmp_path))
    first = tsdb.load("physionet_2019")
    assert first["training_setA"].RecordID.nunique() == 2
    assert first["training_setB"].RecordID.nunique() == 1
    assert (tmp_path / "physionet_2019" / "physionet_2019_cache.pkl").is_file()
    requests.clear()
    again = tsdb.load("physionet_2019")
    assert again["training_setA"].equals(first["training_setA"])
    assert again["training_setB"].equals(first["training_setB"])
    tsdb.delete_cache("physionet_2019", only_pickle=True)
    assert tsdb.load("physionet_2019")["training_setB"].equals(first["training_setB"])
    assert not requests
