"""
TSDB (Time Series Data Beans): a Python toolbox to ease loading public time-series datasets.
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: BSD-3-Clause

# TSDB version
#
# PEP0440 compatible formatted version, see:
# https://www.python.org/dev/peps/pep-0440/
# Generic release markers:
# X.Y
# X.Y.Z # For bugfix releases
#
# Admissible pre-release markers:
# X.YaN # Alpha release
# X.YbN # Beta release
# X.YrcN # Release Candidate
# X.Y # Final release
#
# Dev branch marker is: 'X.Y.dev' or 'X.Y.devN' where N is an integer.
# 'X.Y.dev0' is the canonical version of 'X.Y.dev'
__version__ = "0.2.1"


from .data_processing import (
    list,
    load,
    download_and_extract,
    list_cache,
    delete_cache,
    purge_path,
    CACHED_DATASET_DIR,
    pickle_dump,
    pickle_load,
    # below are deprecated functions, import for now, will be removed in v0.2
    list_database,
    list_available_datasets,
    list_cached_data,
    load_dataset,
    delete_cached_data,
)

__all__ = [
    "__version__",
    "list",
    "load",
    "download_and_extract",
    "list_cache",
    "delete_cache",
    "purge_path",
    "CACHED_DATASET_DIR",
    "pickle_dump",
    "pickle_load",
    # below are deprecated functions, import for now, will be removed in v0.2
    "list_database",
    "list_available_datasets",
    "list_cached_data",
    "load_dataset",
    "delete_cached_data",
]
