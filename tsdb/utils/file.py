"""

"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: GLP-v3


import os
import shutil

from tsdb.utils.logging import logger
from tsdb.database import CACHED_DATASET_DIR


def purge_given_path(path):
    """Delete the given path.
    It will be deleted if a file is given. Itself and all its contents will be purged will a fold is given.

    Parameters
    ----------
    path: str,
        It could be a file or a fold.

    """
    assert os.path.exists(
        path
    ), f"The given path {path} does not exists. Operation aborted."

    try:
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
        else:
            os.remove(path)
        # check if succeed
        if not os.path.exists(path):
            logger.info(f"Successfully deleted {path}.")
        else:
            raise FileExistsError(
                f"Deleting operation failed. {CACHED_DATASET_DIR} still exists."
            )
    except shutil.Error:
        raise shutil.Error("Operation failed.")
