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


def check_path(
    path: str,
    check_exists: bool = False,
) -> str:
    """Check the given path and return the absolute path.

    Parameters
    ----------
    path :
        The path to be checked.

    check_exists :
        If True, check if the path exists, and will raise an AssertionError if the path does not exist.

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

    if check_exists:
        assert os.path.exists(
            checked_path
        ), f"The given path {checked_path} does not exists"

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
    # check the given path
    path = check_path(path)

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
    # check the given path
    path = check_path(path, check_exists=True)
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
    # check the given path, no need to check if the path exists because ignore_errors is set
    path = check_path(path)

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
    # default path
    default_path = check_path("~/.pypots/tsdb")

    # read data_home from the config file
    # data_home may be changed by users, hence not necessarily equal to the default path
    config = read_configs()
    data_home_path = config.get("path", "data_home")
    data_home_path = check_path(data_home_path)

    # old cached dataset dir path used in TSDB v0.2
    old_cached_dataset_dir_02 = check_path("~/.tsdb_cached_datasets")
    # old cached dataset dir path used in TSDB v0.4
    old_cached_dataset_dir_04 = check_path("~/.tsdb")

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
        # if the preset data_home path does not exist,
        # e.g. `data_home_path` is in a portable disk that is not connected
        # then use the default path
        if check_path(data_home_path) != check_path(default_path):
            logger.warning(
                f"❗️ The preset data_home {data_home_path} doesn't exist. "
                f"This may be caused by the portable disk not connected."
            )
            logger.warning(f"‼️ Using the default path {default_path} for now")

        cached_dataset_dir = default_path

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
    # check both old_path and new_path
    old_path = check_path(old_path, check_exists=True)
    new_path = check_path(new_path)

    # create new_path if not exists
    if not os.path.exists(new_path):
        os.makedirs(new_path, exist_ok=True)
    else:
        logger.warning(f"‼️ Note that new_path {new_path} already exists.")

    all_old_files = os.listdir(old_path)
    for f in all_old_files:
        old_f_path = os.path.join(old_path, f)

        if os.path.isdir(old_f_path):
            new_f_path = os.path.join(new_path, f)
            shutil.copytree(old_f_path, new_f_path)
        else:
            shutil.move(old_f_path, new_path)
    shutil.rmtree(old_path, ignore_errors=True)

    logger.info(f"Successfully migrated {old_path} to {new_path}")
    logger.info(f"Purged the old path {old_path}")


def migrate_cache(target_path: str) -> None:
    """Migrate datasets from old_path to new_path.

    Parameters
    ----------
    target_path:
        The new path for TSDB to store cached datasets.

    """
    # check the target path
    target_path = check_path(target_path)

    cached_dataset_dir = determine_data_home()
    migrate(cached_dataset_dir, target_path)
    config_parser = read_configs()
    write_configs(config_parser, {"path": {"data_home": target_path}})
    logger.info(f"Have set {target_path} as the default cache dir.")
