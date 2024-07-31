"""
TSDB (Time Series Data Beans): a Python toolbox loads hundreds of public time-series datasets for machine/deep learning
with a single line of code.
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: BSD-3-Clause

from .data_processing import (
    CACHED_DATASET_DIR,
    list,
    load,
    download_and_extract,
    list_cache,
    delete_cache,
)
from .utils.file import (
    purge_path,
    pickle_dump,
    pickle_load,
    migrate,
    migrate_cache,
)
from .version import __version__

__all__ = [
    "__version__",
    "list",
    "load",
    "download_and_extract",
    "list_cache",
    "delete_cache",
    "CACHED_DATASET_DIR",
    # file
    "purge_path",
    "pickle_dump",
    "pickle_load",
    "migrate",
    "migrate_cache",
]
