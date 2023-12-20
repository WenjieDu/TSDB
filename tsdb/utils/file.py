"""
Functions manipulating files.
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: BSD-3-Clause


import os
import pickle
import shutil
from typing import Optional
from configparser import ConfigParser


from .logging import logger
from ..database import CACHED_DATASET_DIR


def pickle_dump(data: object, path: str) -> Optional[str]:
    """Pickle the given object.

    Parameters
    ----------
    data:
        The object to be pickled.

    path:
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


def pickle_load(path: str) -> object:
    """Load pickled object from file.

    Parameters
    ----------
    path :
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


def purge_path(path: str, ignore_errors: bool = True) -> None:
    """Delete the given path.
    It will be deleted if a file is given. Itself and all its contents will be purged will a fold is given.

    Parameters
    ----------
    path:
        It could be a file or a fold.

    ignore_errors:
        Errors are ignored if ignore_errors is set.

    """
    assert os.path.exists(
        path
    ), f"The given path {path} does not exists. Operation aborted."

    try:
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=ignore_errors)
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


def migrate(old_path: str, new_path: str) -> None:
    """Migrate datasets from old_path to new_path.

    Parameters
    ----------
    old_path:
        The old path of the dataset.

    new_path:
        The new path of the dataset.

    """
    if not os.path.exists(old_path):
        raise FileNotFoundError(f"Given old_path {old_path} does not exist.")

    if os.path.exists(new_path):
        logger.warning(f"Please note that new_path {new_path} already exists.")
        # if new_path exists, we have to move everything from old_path into it
        all_old_files = os.listdir(old_path)
        for f in all_old_files:
            old_f_path = os.path.join(old_path, f)
            if os.path.isdir(old_f_path):
                new_f_path = os.path.join(new_path, f)
                shutil.copytree(old_f_path, new_f_path)
            else:
                shutil.move(old_f_path, new_path)
        shutil.rmtree(old_path, ignore_errors=True)
    else:
        # if new_path does not exist, just rename the old_path into it
        new_parent_dir = os.path.abspath(os.path.join(new_path, ".."))
        if not os.path.exists(new_parent_dir):
            os.makedirs(new_parent_dir, exist_ok=True)
        os.rename(old_path, new_path)

    config = ConfigParser()
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    tsdb_config_path = os.path.join(parent_dir, "config.ini")
    config.read(tsdb_config_path)

    if os.path.abspath(old_path) == os.path.abspath(CACHED_DATASET_DIR):
        config.set("path", "data_home", new_path)
        with open(tsdb_config_path, "w") as f:
            config.write(f)

        logger.info(
            f"Found the given old_path is the current TSDB dataset cache directory. "
            f"Have already set the new cache directory to {new_path}."
        )

    logger.info(
        f"Successfully migrated {old_path} to {new_path}, and deleted {old_path}"
    )
