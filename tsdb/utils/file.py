"""
Functions manipulating files.
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: GLP-v3


import os
import pickle
import shutil

from tsdb.database import CACHED_DATASET_DIR
from tsdb.utils.logging import logger


def pickle_dump(data, path):
    """Pickle the given object.

    Parameters
    ----------
    data : object
        The object to be pickled.

    path : string,
        Saving path.

    Returns
    -------
    `path` if succeed else None

    """
    try:
        with open(path, "wb") as f:
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
    except pickle.PicklingError:
        logger.info("Pickling failed. No cache will be saved.")
        return None
    logger.info(f"Successfully saved to {path}")
    return path


def pickle_load(path):
    """Load pickled object from file.

    Parameters
    ----------
    path : string,
        Local path of the pickled object.

    Returns
    -------
    Object
        Pickled object.

    """
    try:
        with open(path, "rb") as f:
            data = pickle.load(f)
    except pickle.UnpicklingError as e:
        logger.info("Cached data corrupted. Aborting...\n" f"{e}")
    return data


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
