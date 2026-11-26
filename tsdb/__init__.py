"""
TSDB (Time Series Data Beans): a Python toolbox loads hundreds of public time-series datasets for machine/deep learning
with a single line of code.
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: BSD-3-Clause

from importlib import import_module

from .database import AVAILABLE_DATASETS, info
from .version import __version__


def list() -> list:
    """Return the registered dataset names without importing data loaders."""
    return AVAILABLE_DATASETS.copy()


_LAZY_EXPORTS = {
    "CACHED_DATASET_DIR": ".data_processing",
    "delete_cache": ".data_processing",
    "list_cache": ".data_processing",
    "load": ".data_processing",
    "download_and_extract": ".utils.downloading",
    "download_url": ".utils.downloading",
    "migrate": ".utils.file",
    "migrate_cache": ".utils.file",
    "pickle_dump": ".utils.file",
    "pickle_load": ".utils.file",
    "purge_path": ".utils.file",
}


def __getattr__(name):
    module = _LAZY_EXPORTS.get(name)
    if module is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    # Do not memoize the cache path: migration can change it during a process.
    return getattr(import_module(module, __name__), name)


def __dir__():
    return sorted(set(globals()) | set(__all__))


__all__ = [
    "CACHED_DATASET_DIR",
    "__version__",
    "delete_cache",
    "download_and_extract",
    "download_url",
    "info",
    "list",
    "list_cache",
    "load",
    "migrate",
    "migrate_cache",
    "pickle_dump",
    "pickle_load",
    # file
    "purge_path",
]
