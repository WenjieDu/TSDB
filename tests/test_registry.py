"""Check every registry entry without downloading data."""

# License: BSD-3-Clause

import json
from pathlib import Path
from urllib.parse import urlsplit

import pytest

import tsdb
from tsdb import loading_funcs
from tsdb.database import AVAILABLE_DATASETS, DATABASE, dataset_spec
from tsdb.utils.archive import archive_format


def test_every_registered_dataset_has_a_supported_source_and_loader():
    assert tsdb.list() == AVAILABLE_DATASETS
    assert len(AVAILABLE_DATASETS) == len(set(AVAILABLE_DATASETS))
    assert list(DATABASE) == AVAILABLE_DATASETS
    root = Path(__file__).resolve().parents[1]
    for name in AVAILABLE_DATASETS:
        spec = dataset_spec(name)
        expected = DATABASE[name]
        assert spec.sources == ((expected,) if isinstance(expected, str) else tuple(expected))
        assert callable(getattr(loading_funcs, spec.loader))
        assert (root / "dataset_profiles" / spec.profile / "README.md").is_file()
        assert spec.sources
        for url in spec.sources:
            if spec.download_strategy == "http":
                assert urlsplit(url).scheme == "https"
                assert archive_format(urlsplit(url).path.rsplit("/", 1)[-1])
            elif spec.download_strategy == "physionet_2019":
                assert url.startswith("https://physionet-open.s3.amazonaws.com/")
            else:
                assert spec.download_strategy == "huggingface"
                assert url.startswith("hf://")
        assert json.loads(json.dumps(tsdb.info(name)))["name"] == name


def test_info_unknown_metadata_and_copy():
    info = tsdb.info("ucr_uea_Wine")
    assert info["license"] is None
    assert info["revision"] is None
    assert info["loader_arg"] == "Wine"
    info["name"] = "changed"
    assert tsdb.info("ucr_uea_Wine")["name"] == "ucr_uea_Wine"
    assert tsdb.info("tsqa")["optional_dependencies"] == ("huggingface_hub",)
    with pytest.raises(ValueError, match="not available in TSDB"):
        tsdb.info("unknown")
