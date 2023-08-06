"""
tsdb package
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: GLP-v3

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
__version__ = "0.1"


try:
    from tsdb.data_processing import (
        list_database,
        list_available_datasets,
        window_truncate,
        download_and_extract,
        load_dataset,
        delete_cached_data,
        purge_given_path,
        list_cached_data,
        CACHED_DATASET_DIR,
        pickle_dump,
        pickle_load,
    )

except Exception as e:
    print(e)

__all__ = [
    "__version__",
    "list_database",
    "list_available_datasets",
    "window_truncate",
    "download_and_extract",
    "load_dataset",
    "delete_cached_data",
    "purge_given_path",
    "list_cached_data",
    "CACHED_DATASET_DIR",
    "pickle_dump",
    "pickle_load",
]
