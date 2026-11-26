"""Small raw-data fixtures for the supported loader families and shape contracts."""

# License: BSD-3-Clause

import numpy as np
import pandas as pd
import pytest

from tsdb.loading_funcs import (
    load_ais,
    load_beijing_air_quality,
    load_electricity,
    load_ett,
    load_italy_air_quality,
    load_pems_traffic,
    load_physionet2012,
    load_physionet2019,
    load_solar_alabama,
    load_ucr_uea_dataset,
)
from tsdb.loading_funcs.ucr_uea_datasets import to_time_series_dataset, ts_size


def _write(root, name, text):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_electricity_and_ett_contract(tmp_path):
    _write(tmp_path, "LD2011_2014.txt", ";meter\n2011-01-01 00:00:00;1,5\n2011-01-01 00:15:00;2,5\n")
    data = load_electricity(tmp_path)["X"]
    assert data["meter"].tolist() == [1.5, 2.5]
    assert isinstance(data.index, pd.DatetimeIndex)
    for name in ("ETTm1", "ETTm2", "ETTh1", "ETTh2"):
        _write(tmp_path, f"{name}.csv", "date,OT\n2020-01-01,3.5\n")
    data = load_ett(tmp_path)
    assert set(data) == {"ETTm1", "ETTm2", "ETTh1", "ETTh2"}
    for frame in data.values():
        assert frame["OT"].tolist() == [3.5]
        assert frame.index[0] == pd.Timestamp("2020-01-01")


def test_beijing_filters_unrelated_files_and_orders_sources(tmp_path):
    prefix = "PRSA_Data_20130301-20170228/"
    _write(tmp_path, prefix + "b.csv", "station,PM2.5\nb,2\n")
    _write(tmp_path, prefix + "a.csv", "station,PM2.5\na,1\n")
    _write(tmp_path, prefix + "README.txt", "not data")
    frame = load_beijing_air_quality(tmp_path)["X"]
    assert frame["station"].tolist() == ["a", "b"]
    assert frame["PM2.5"].tolist() == [1, 2]


def test_italy_preserves_missing_sentinel_and_correlated_columns(tmp_path):
    names = ["Date", "Time", "C6H6(GT)", "PT08.S2(NMHC)", *[f"f{i}" for i in range(11)]]
    _write(
        tmp_path,
        "AirQualityUCI.csv",
        ";".join(names)
        + ";;\n"
        + ";".join(["10/03/2004", "18.00.00", "-200", "1046", *["1"] * 11])
        + ";;\n"
        + ";" * 16
        + "\n",
    )
    frame = load_italy_air_quality(tmp_path)["X"]
    assert list(frame.columns) == names
    assert frame["C6H6(GT)"].tolist() == [-200]
    assert frame["PT08.S2(NMHC)"].tolist() == [1046]


@pytest.mark.parametrize(
    "name,filename,columns,rows,start,end,loader",
    [
        ("traffic", "traffic.txt", 862, 17544, "2015-01-01", "2016-12-31 23:00:00", load_pems_traffic),
        ("solar", "solar_AL.txt", 137, 52560, "2006-01-01", "2006-12-31 23:50:00", load_solar_alabama),
    ],
)
def test_fixed_frequency_datasets(tmp_path, name, filename, columns, rows, start, end, loader):
    line = ",".join(["1"] * columns) + "\n"
    _write(tmp_path, filename, line * rows)
    frame = loader(tmp_path)["X"]
    assert frame.shape == (rows, columns + 1), name
    assert frame["date"].iloc[0] == pd.Timestamp(start)
    assert frame["date"].iloc[-1] == pd.Timestamp(end)
    assert frame["0"].iloc[-1] == 1


def test_physionet2012_static_features_labels_and_filtering(tmp_path):
    for i, split in enumerate("abc", 1):
        rid = 100000 + i
        _write(tmp_path, f"Outcomes-{split}.txt", f"RecordID,In-hospital_death\n{rid},1\n")
        _write(
            tmp_path,
            f"set-{split}/{rid}.txt",
            "Time,Parameter,Value\n00:00,Age,50\n00:00,Height,170\n00:00,Gender,1\n00:00,ICUType,2\n00:30,HR,70\n01:00,HR,80\n",
        )
        _write(tmp_path, f"set-{split}/notes.md", "ignored")
    data = load_physionet2012(tmp_path)
    assert data["static_features"] == ["Age", "Gender", "ICUType", "Height"]
    for i, split in enumerate("abc", 1):
        rid = 100000 + i
        frame = data[f"set-{split}"]
        assert frame["RecordID"].tolist() == [rid, rid]
        assert frame["Age"].tolist() == [50, 50]
        assert frame["HR"].tolist() == [70, 80]
        assert data[f"outcomes-{split}"].loc[rid, "In-hospital_death"] == 1


def test_physionet2019_split_and_order(tmp_path):
    for split in ("training", "training_setB"):
        for rid in ("p000002", "p000001"):
            _write(tmp_path, f"{split}/{rid}.psv", "HR|Age|SepsisLabel\n70|50|0\n80|50|1\n")
        _write(tmp_path, f"{split}/README.txt", "ignored")
    data = load_physionet2019(tmp_path)
    for key in ("training_setA", "training_setB"):
        assert data[key].RecordID.tolist() == ["p000001", "p000001", "p000002", "p000002"]
        assert data[key].SepsisLabel.tolist() == [0, 1, 0, 1]


def test_ucr_single_row_txt_and_dtype(tmp_path):
    for split in ("TRAIN", "TEST"):
        _write(tmp_path, f"Tiny_{split}.txt", "2 1 3 4\n")
    data = load_ucr_uea_dataset(tmp_path, "Tiny")
    assert data["X_train"].shape == (1, 3, 1)
    np.testing.assert_array_equal(data["X_train"][0, :, 0], [1, 3, 4])
    np.testing.assert_array_equal(data["y_test"], [2])
    assert to_time_series_dataset(pd.DataFrame([[1, 2]]), dtype=np.float32).dtype == np.float32
    assert ts_size([1, np.nan]) == 1
    assert to_time_series_dataset([[1, 2], [3]]).shape == (2, 2, 1)
    assert np.isnan(to_time_series_dataset([[1, 2], [3]])[1, 1, 0])
    assert to_time_series_dataset([]).shape == (0, 0, 0)


def test_uea_arff_preserves_historical_axes_and_labels(tmp_path):
    arff = "@relation Tiny\n@attribute series relational\n@attribute t1 numeric\n@attribute t2 numeric\n@attribute t3 numeric\n@end series\n@attribute class {a,b}\n@data\n% comment\n'1,2,3\\n4,?,6',a\n'7,8,9\\n10,11,12',b\n"
    for split in ("TRAIN", "TEST"):
        _write(tmp_path, f"Tiny_{split}.arff", arff)
        _write(tmp_path, f"Tiny_{split}.txt", "2 1 3 4\n")
    data = load_ucr_uea_dataset(tmp_path, "Tiny")
    assert data["X_train"].shape == (2, 2, 3)
    np.testing.assert_array_equal(data["y_train"], ["a", "b"])
    assert np.isnan(data["X_train"][0, 1, 1])
    np.testing.assert_array_equal(data["X_train"][1, 1], [10, 11, 12])


@pytest.mark.parametrize("content", ["@data\n", "@data\n1,2,a\n3,b\n"])
def test_uea_rejects_empty_or_inconsistent_arff(tmp_path, content):
    for split in ("TRAIN", "TEST"):
        _write(tmp_path, f"Tiny_{split}.arff", content)
    with pytest.raises(ValueError):
        load_ucr_uea_dataset(tmp_path, "Tiny")


def test_uea_missing_pair(tmp_path):
    _write(tmp_path, "Tiny_TRAIN.txt", "1 2 3\n")
    with pytest.raises(FileNotFoundError):
        load_ucr_uea_dataset(tmp_path, "Tiny")


def test_ais_real_parquet_elapsed_seconds_and_labels(tmp_path):
    folder = tmp_path / "parquets"
    folder.mkdir()
    n = 2000
    frame = pd.DataFrame(
        {
            "mmsi": [123] * n,
            "sog": [1.0] * n,
            "length": [20.0] * n,
            "date_time_utc": pd.date_range("2020-01-01", periods=n, freq="9s").as_unit("us"),
            "true_heading": [270.0] * n,
            "cog": [45.0] * n,
            "lat": [1.0] * n,
            "long": [2.0] * n,
            "nav_status": [0] * n,
            "message_nr": [1] * n,
            "imo_nr": [0] * n,
        }
    )
    # The last sample must reach the 6000th resampling bucket.
    frame.loc[n - 1, "date_time_utc"] = pd.Timestamp("2020-01-01") + pd.Timedelta(seconds=17997)
    frame.to_parquet(folder / "vessels.parquet", index=False)
    (folder / "README.txt").write_text("ignored", encoding="utf-8")
    data = load_ais(tmp_path)
    assert len(data["X"]) == 6000
    assert data["X"]["time"].iloc[3] == 9.0
    assert data["X"]["heading"].iloc[0] == -90.0
    assert data["X"]["course"].iloc[0] == 45.0
    assert data["y"].loc[123, "Length"] == 20.0
