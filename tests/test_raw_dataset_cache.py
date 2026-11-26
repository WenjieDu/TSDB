"""Offline checks for weekly cache identity and raw-only integrity."""

# License: BSD-3-Clause

from datetime import datetime, timezone

import pytest

from scripts import raw_dataset_cache as raw


def test_cache_week_and_reviewed_source(monkeypatch):
    sunday = datetime(2026, 11, 22, tzinfo=timezone.utc)
    saturday = datetime(2026, 11, 28, tzinfo=timezone.utc)
    next_sunday = datetime(2026, 11, 29, tzinfo=timezone.utc)
    assert raw.cache_key(sunday) == raw.cache_key(saturday)
    assert raw.cache_key(sunday) != raw.cache_key(next_sunday)
    monkeypatch.setitem(raw.DATABASE, "italy_air_quality", "https://example.invalid/unreviewed.zip")
    with pytest.raises(ValueError, match="source changed"):
        raw.cache_key(sunday)


def test_manifest_integrity_and_budget(tmp_path, monkeypatch):
    root = tmp_path / "shared"
    for name, (_, suffixes) in raw.POLICY.items():
        source = tmp_path / name
        source.mkdir()
        (source / f"data{suffixes[0]}").write_bytes(b"raw-data")
        raw.store(root, name, source)
    raw.verify(root)
    assert not raw.restore(tmp_path / "missing", "physionet_2019", tmp_path / "not-created")
    monkeypatch.setattr(raw, "MAX_CACHE_BYTES", 1)
    with pytest.raises(ValueError, match="total size"):
        raw.verify(root)
    (root / "physionet_2019" / "raw" / "data.psv").write_bytes(b"tampered")
    with pytest.raises(ValueError, match="integrity"):
        raw.restore(root, "physionet_2019", tmp_path / "restored")
    assert not (tmp_path / "restored").exists()


def test_reject_pickle_and_symlink(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "parsed.pkl").write_bytes(b"not a pickle")
    with pytest.raises(ValueError, match="Unexpected raw cache member"):
        raw.store(tmp_path / "shared", "physionet_2019", source)
    assert not (tmp_path / "shared" / "physionet_2019").exists()
    (source / "parsed.pkl").unlink()
    outside = tmp_path / "outside.psv"
    outside.write_bytes(b"outside")
    try:
        (source / "linked.psv").symlink_to(outside)
    except OSError:
        pytest.skip("Platform does not permit symlinks")
    with pytest.raises(ValueError, match="Linked"):
        raw.store(tmp_path / "shared", "physionet_2019", source)
