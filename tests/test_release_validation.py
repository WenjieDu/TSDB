"""Regression tests for release-tag policy."""

# License: BSD-3-Clause

import pytest

from scripts.check_release import RELEASE_TAG


@pytest.mark.parametrize(
    "tag",
    [
        "v1.0.0",
        "v1.0.0rc1",
        "v1.0.0rc2",
        "v0.8.0",
        "v10.20.30",
    ],
)
def test_release_tag_accepts_stable_and_rc(tag):
    assert RELEASE_TAG.fullmatch(tag)


@pytest.mark.parametrize(
    "tag",
    [
        "v1.0",
        "v1.0.0rc",
        "v1.0.0rc01",
        "v1.0.0a1",
        "v1.0.0b1",
        "v1.0.0.dev1",
        "v1.0.0.post1",
        "1.0.0rc1",
        "release-v1.0.0rc1",
    ],
)
def test_release_tag_rejects_unsupported_versions(tag):
    assert RELEASE_TAG.fullmatch(tag) is None
