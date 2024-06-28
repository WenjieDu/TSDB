"""
Functions manipulating files.
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: BSD-3-Clause


import os
import pickle
import shutil
from typing import Optional

from .config import read_configs, write_configs
from .logging import logger


def check_path(path: str) -> str:
    """Check the given path and return the absolute path.

    Parameters
    ----------
    path :
        The path to be checked.

    Returns
    -------
    checked_path:
        The absolute path of the given path.
    """
    # expand the home dir if the path starts with "~"
    if path.startswith("~"):
        checked_path = path.replace("~", os.path.expanduser("~"))
    else:
        checked_path = path

    checked_path = os.path.abspath(checked_path)
    return checked_path


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
            logger.info(f"Successfully deleted {path}")
        else:
            cached_dataset_dir = determine_data_home()
            raise FileExistsError(
                f"Deleting operation failed. {cached_dataset_dir} still exists."
            )
    except shutil.Error:
        raise shutil.Error("Operation failed.")


def determine_data_home():
    # read data_home from the config file
    config = read_configs()
    data_home_path = config.get("path", "data_home")
    # replace '~' with the absolute path if existing in the path
    data_home_path = data_home_path.replace("~", os.path.expanduser("~"))

    # old cached dataset dir path used in TSDB v0.2
    old_cached_dataset_dir_02 = os.path.join(
        os.path.expanduser("~"), ".tsdb_cached_datasets"
    )
    # old cached dataset dir path used in TSDB v0.4
    old_cached_dataset_dir_04 = os.path.join(os.path.expanduser("~"), ".tsdb")

    if os.path.exists(old_cached_dataset_dir_02) or os.path.exists(
        old_cached_dataset_dir_04
    ):
        logger.warning(
            "‼️ Detected the home dir of the old version TSDB. Auto migrating... Please wait."
        )
        cached_dataset_dir = data_home_path
        if os.path.exists(old_cached_dataset_dir_02):
            migrate(old_cached_dataset_dir_02, cached_dataset_dir)
        else:
            migrate(old_cached_dataset_dir_04, cached_dataset_dir)
        logger.info("🌟 Migrating finished.")
    elif os.path.exists(data_home_path):
        # use the path directly, may be in a portable disk
        cached_dataset_dir = data_home_path
    else:
        # use the default path for initialization,
        # e.g. `data_home_path` in a portable disk but the disk is not connected
        default_path = os.path.join(os.path.expanduser("~"), ".pypots", "tsdb")
        cached_dataset_dir = default_path
        if os.path.abspath(data_home_path) != os.path.abspath(default_path):
            logger.warning(
                f"‼️ The preset data_home path '{data_home_path}' doesn't exist. "
                f"Using the default path '{default_path}'"
            )
    return cached_dataset_dir


def migrate(old_path: str, new_path: str) -> None:
    """Migrate files in a directory from old_path to new_path.

    Parameters
    ----------
    old_path:
        The old path of the dataset.

    new_path:
        The new path of the dataset.

    """
    if not os.path.exists(old_path):
        raise FileNotFoundError(f"Given old_path {old_path} does not exist.")

    if not os.path.exists(new_path):
        # if new_path does not exist, just rename the old_path into it
        new_parent_dir = os.path.abspath(os.path.join(new_path, ".."))
        if not os.path.exists(new_parent_dir):
            os.makedirs(new_parent_dir, exist_ok=True)

    logger.warning(f"‼️ Please note that new_path {new_path} already exists.")
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

    logger.info(
        f"Successfully migrated {old_path} to {new_path}, and deleted {old_path}"
    )


def migrate_cache(target_path: str) -> None:
    """Migrate datasets from old_path to new_path.

    Parameters
    ----------
    target_path:
        The new path for TSDB to store cached datasets.

    """
    cached_dataset_dir = determine_data_home()
    migrate(cached_dataset_dir, target_path)
    config_parser = read_configs()
    write_configs(config_parser, {"path": {"data_home": target_path}})
    logger.info(f"Have set {target_path} as the default cache dir.")
