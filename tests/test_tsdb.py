"""Deterministic TSDB regression tests and independent live dataset checks."""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: BSD-3-Clause

import io
import json
import os
import uuid
import zipfile
from pathlib import Path

import pandas as pd
import pytest
import requests
import tomlkit

import tsdb
from scripts.raw_dataset_cache import POLICY, restore, store
from tsdb import data_processing
from tsdb.database import DATABASE
from tsdb.utils import config, file
from tsdb.utils.logging import Logger

DATASETS_TO_TEST = [
    "physionet_2012",
    "physionet_2019",
    "beijing_multisite_air_quality",
    "italy_air_quality",
    "electricity_load_diagrams",
    "electricity_transformer_temperature",
    "vessel_ais",
    "tsqa",
    "pems_traffic",
    "solar_alabama",
    "ucr_uea_Wine",
    "ucr_uea_FingerMovements",
]


@pytest.fixture
def cache(tmp_path, monkeypatch):
    root = tmp_path / "cache"
    root.mkdir()
    config_path = tmp_path / "config.toml"
    config_path.write_text(tomlkit.dumps({"schema_version": 1, "tsdb": {"cache_dir": str(root)}}), encoding="utf-8")
    monkeypatch.setitem(vars(data_processing), "CACHED_DATASET_DIR", str(root))
    monkeypatch.setattr(config, "PYPOTS_ECOSYSTEM_CONFIG_PATH", config_path)

    def read_local_configs(path=config_path):
        return config.read_configs(path)

    monkeypatch.setattr(file, "read_configs", read_local_configs)
    return root


@pytest.fixture
def archive(monkeypatch):
    """Serve a tiny deterministic ZIP without any network calls."""
    payload = io.BytesIO()
    with zipfile.ZipFile(payload, "w") as archive:
        archive.writestr("LD2011_2014.txt", ";MT_001\n2011-01-01 00:00:00;1,5\n2011-01-01 00:15:00;2,5\n")
    calls = []

    def get(url, **kwargs):
        assert url == DATABASE["electricity_load_diagrams"]
        assert kwargs["stream"]
        calls.append(url)
        response = requests.Response()
        response.status_code = 200
        response._content = payload.getvalue()
        response._content_consumed = True
        response.headers["Content-Length"] = str(len(response.content))
        return response

    monkeypatch.setattr(requests, "get", get)
    return calls


def test_available_datasets():
    available = tsdb.list()
    assert available
    assert set(available) == set(DATABASE)


def test_download_and_extract(tmp_path, archive):
    destination = tmp_path / "download"
    tsdb.download_and_extract("electricity_load_diagrams", str(destination))
    assert (destination / "LD2011_2014.txt").is_file()
    assert len(archive) == 1
    tsdb.purge_path(str(destination))
    assert not destination.exists()


def test_load_cache_and_purge(cache, archive):
    name = "electricity_load_diagrams"
    data = tsdb.load(name)
    frame = data["X"]
    assert frame["MT_001"].tolist() == [1.5, 2.5]
    assert isinstance(frame.index, pd.DatetimeIndex)
    path = cache / name
    pickle_path = path / (name + "_cache.pkl")
    assert pickle_path.is_file()
    assert tsdb.list_cache() == [name]
    pd.testing.assert_frame_equal(tsdb.load(name)["X"], frame)
    assert len(archive) == 1
    tsdb.delete_cache(name, only_pickle=True)
    assert not pickle_path.exists()
    assert (path / "LD2011_2014.txt").is_file()
    pd.testing.assert_frame_equal(tsdb.load(name)["X"], frame)
    assert len(archive) == 1
    tsdb.delete_cache(name)
    assert tsdb.list_cache() == []
    pd.testing.assert_frame_equal(tsdb.load(name)["X"], frame)
    assert len(archive) == 2
    tsdb.delete_cache(only_pickle=True)
    assert not pickle_path.exists()
    tsdb.delete_cache()
    assert tsdb.list_cache() == []


def test_delete_cache_missing_root(cache):
    cache.rmdir()
    tsdb.delete_cache()
    assert not cache.exists()


def test_delete_cache_invalid_dataset(cache):
    with pytest.raises(ValueError, match="not available in TSDB"):
        tsdb.delete_cache("unknown_dataset")
    assert cache.is_dir()


def test_delete_cache_missing_dataset(cache):
    tsdb.delete_cache("physionet_2019")
    assert cache.is_dir()
    with pytest.raises(FileNotFoundError):
        tsdb.delete_cache("physionet_2019", only_pickle=True)


def test_delete_cache_preserves_other_datasets_and_raw_files(cache):
    first = cache / "physionet_2019"
    second = cache / "physionet_2012"
    for directory in (first, second):
        directory.mkdir()
        (directory / "cached.pkl").write_bytes(b"cache")
        (directory / "raw.txt").write_bytes(b"raw")
    tsdb.delete_cache("physionet_2019", only_pickle=True)
    assert not (first / "cached.pkl").exists()
    assert (first / "raw.txt").read_bytes() == b"raw"
    assert (second / "cached.pkl").is_file()
    tsdb.delete_cache(only_pickle=True)
    assert not (second / "cached.pkl").exists()
    assert (second / "raw.txt").read_bytes() == b"raw"
    tsdb.delete_cache("physionet_2019")
    assert not first.exists()
    assert second.is_dir()
    tsdb.delete_cache()
    assert cache.is_dir()
    assert not list(cache.iterdir())


def test_migrate(tmp_path, cache):
    original = tmp_path / "original"
    original.mkdir()
    (original / "test.txt").write_text("hello world", encoding="utf-8")
    destination = tmp_path / "new" / "dir"
    tsdb.migrate(str(original), str(destination))
    assert not original.exists()
    assert (destination / "test.txt").read_text(encoding="utf-8") == "hello world"
    (cache / "test.txt").write_text("cached", encoding="utf-8")
    new_cache = tmp_path / "new_cache"
    tsdb.migrate_cache(str(new_cache))
    assert not cache.exists()
    assert (new_cache / "test.txt").read_text(encoding="utf-8") == "cached"
    assert config.read_configs(config.PYPOTS_ECOSYSTEM_CONFIG_PATH)["tsdb"]["cache_dir"] == str(new_cache)


def test_logging(tmp_path):
    creator = Logger(name=f"test-log-{uuid.uuid4()}", logging_level="debug")
    try:
        creator.logger.debug("debug")
        creator.logger.info("info")
        creator.logger.warning("warning")
        creator.logger.error("error")
        for level, expected in [("info", 20), ("warning", 30), ("error", 40), ("debug", 10)]:
            creator.set_level(level)
            assert creator.logger.level == expected
        creator.set_saving_path(str(tmp_path), "testing.log")
        creator.logger.info("file marker")
        assert "file marker" in (tmp_path / "testing.log").read_text(encoding="utf-8")
    finally:
        for handler in list(creator.logger.handlers):
            creator.logger.removeHandler(handler)
            handler.close()


def test_config(cache):
    configs = config.read_configs(config.PYPOTS_ECOSYSTEM_CONFIG_PATH)
    assert configs["tsdb"]["cache_dir"] == str(cache)


@pytest.mark.network
@pytest.mark.parametrize("dataset", DATASETS_TO_TEST)
def test_live_dataset_loading(cache, dataset):
    raw_root = os.environ.get("TSDB_CI_RAW_CACHE")
    raw_cache = Path(raw_root) if raw_root and dataset in POLICY else None
    target = cache / dataset
    hit = raw_cache is not None and restore(raw_cache, dataset, target)
    # Cover the public download API without downloading Wine twice.
    if dataset == "ucr_uea_Wine":
        tsdb.download_and_extract(dataset, str(target))
    result = tsdb.load(dataset)
    assert isinstance(result, dict), f"Failed to load {dataset}"
    assert result, f"Empty dataset {dataset}"
    if dataset == "physionet_2019":
        assert result["training_setA"].RecordID.nunique() == 20336
        assert result["training_setB"].RecordID.nunique() == 20000
    if dataset == "vessel_ais":
        from tsdb.utils.vessel_ais import ais_parquet_files

        assert len(ais_parquet_files(target)) == 40
        assert not result["y"].empty and result["y"].index.is_unique
        assert len(result["X"]) == 6000 * len(result["y"])
        assert result["X"]["mmsi"].nunique() == len(result["y"])
    if dataset == "tsqa":
        from tsdb.utils.tsqa import TSQA_CSV_FILES

        assert set(result) == set(TSQA_CSV_FILES)
        assert all(not frame.empty for frame in result.values())
    # Exercise cached reads without a second download.
    assert isinstance(tsdb.load(dataset), dict)

    if raw_cache is not None and not hit:
        tsdb.delete_cache(dataset, only_pickle=True)
        store(raw_cache, dataset, target)
    mode = "raw-cache-hit" if hit else "cold-download"
    print(f"DATASET MODE {dataset}: {mode}", flush=True)
    report_dir = os.environ.get("TSDB_CI_DATASET_REPORT")
    if report_dir:
        report = Path(report_dir)
        report.mkdir(parents=True, exist_ok=True)
        (report / f"{dataset}.json").write_text(json.dumps({"dataset": dataset, "mode": mode}), encoding="utf-8")


def test_real_dataset_raw_cache_reparse(cache, archive, monkeypatch, tmp_path):
    name = "electricity_load_diagrams"
    shared = tmp_path / "shared-raw"
    report = tmp_path / "report"
    monkeypatch.setenv("TSDB_CI_RAW_CACHE", str(shared))
    monkeypatch.setenv("TSDB_CI_DATASET_REPORT", str(report))
    test_live_dataset_loading(cache, name)
    assert len(archive) == 1
    assert not list(shared.rglob("*.pkl"))
    assert json.loads((report / f"{name}.json").read_text())["mode"] == "cold-download"
    tsdb.delete_cache(name)
    calls = []
    parse = data_processing._parse

    def tracked_parse(*args):
        calls.append(args[0])
        return parse(*args)

    monkeypatch.setattr(data_processing, "_parse", tracked_parse)
    test_live_dataset_loading(cache, name)
    assert len(archive) == 1
    assert calls == [name]
    assert (cache / name / f"{name}_cache.pkl").is_file()
    assert json.loads((report / f"{name}.json").read_text())["mode"] == "raw-cache-hit"
