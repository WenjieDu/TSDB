"""
TSDB (Time Series Data Beans): a Python toolbox loads hundreds of public time-series datasets for machine/deep learning
with a single line of code.
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: BSD-3-Clause

from .data_processing import (
    CACHED_DATASET_DIR,
    delete_cache,
    download_and_extract,
    list,
    list_cache,
    load,
)
from .utils.file import (
    migrate,
    migrate_cache,
    pickle_dump,
    pickle_load,
    purge_path,
)
from .version import __version__

__all__ = [
    "CACHED_DATASET_DIR",
    "__version__",
    "delete_cache",
    "download_and_extract",
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
