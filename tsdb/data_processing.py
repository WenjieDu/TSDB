"""
Functions for loading datasets.
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: BSD-3-Clause

import os
import shutil
import sys
import warnings

from .database import AVAILABLE_DATASETS, CACHED_DATASET_DIR
from .loading_funcs import (
    load_physionet2012,
    load_physionet2019,
    load_electricity,
    load_ett,
    load_beijing_air_quality,
    load_ucr_uea_dataset,
    load_ais,
)
from .utils.downloading import download_and_extract
from .utils.file import purge_path, pickle_load, pickle_dump
from .utils.logging import logger


def list() -> list:
    """List the database.

    Returns
    -------
    DATABASE : dict
        A dict contains all datasets' names and download links.

    """
    return AVAILABLE_DATASETS


def load(dataset_name: str, use_cache: bool = True) -> dict:
    """Load dataset with given name.

    Parameters
    ----------
    dataset_name : str,
        The name of the specific dataset in database.DATABASE.

    use_cache : bool,
        Whether to use cache (including data downloading and processing)

    Returns
    -------
    result:
        Loaded dataset in a Python dict.
    """
    assert dataset_name in AVAILABLE_DATASETS, (
        f'The given dataset name "{dataset_name}" is not in the database. '
        f"Please fetch the full list of the available dataset_profiles with tsdb.list()"
    )

    profile_dir = dataset_name if "ucr_uea_" not in dataset_name else "ucr_uea_datasets"
    logger.info(
        f"You're using dataset {dataset_name}, please cite it properly in your work. "
        f"You can find its reference information at the below link: \n"
        f"https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/{profile_dir}"
    )

    dataset_saving_path = os.path.join(CACHED_DATASET_DIR, dataset_name)
    if not os.path.exists(
        dataset_saving_path
    ):  # if the dataset is not cached, then download it
        download_and_extract(dataset_name, dataset_saving_path)
    else:
        if use_cache:
            logger.info(
                f"Dataset {dataset_name} has already been downloaded. Processing directly..."
            )
        else:
            # if not use cache, then delete the downloaded data dir (including processing cache)
            shutil.rmtree(dataset_saving_path, ignore_errors=True)
            download_and_extract(dataset_name, dataset_saving_path)

    # if cached, then load directly
    cache_path = os.path.join(dataset_saving_path, dataset_name + "_cache.pkl")
    if os.path.exists(cache_path):
        logger.info(
            f"Dataset {dataset_name} has already been cached. Loading from cache directly..."
        )
        result = pickle_load(cache_path)
    else:
        try:
            if dataset_name == "physionet_2012":
                result = load_physionet2012(dataset_saving_path)
            elif dataset_name == "physionet_2019":
                result = load_physionet2019(dataset_saving_path)
            elif dataset_name == "electricity_load_diagrams":
                result = load_electricity(dataset_saving_path)
            elif dataset_name == "electricity_transformer_temperature":
                result = load_ett(dataset_saving_path)
            elif dataset_name == "beijing_multisite_air_quality":
                result = load_beijing_air_quality(dataset_saving_path)
            elif dataset_name == "vessel_ais":
                result = load_ais(dataset_saving_path)
            elif "ucr_uea_" in dataset_name:
                actual_dataset_name = dataset_name.replace(
                    "ucr_uea_", ""
                )  # delete 'ucr_uea_' in the name
                result = load_ucr_uea_dataset(dataset_saving_path, actual_dataset_name)
            else:
                raise NotImplementedError(
                    f"Dataset {dataset_name} is not supported yet. "
                    f"Please check the dataset name or contribute it to TSDB https://github.com/WenjieDu/TSDB/."
                )

        except FileExistsError:
            shutil.rmtree(dataset_saving_path, ignore_errors=True)
            warnings.warn(
                "Dataset corrupted. Just deleted it. "
                "Please rerun the function tsdb.load(dataset_name) to re-download the raw data."
            )
        pickle_dump(result, cache_path)

    logger.info("Loaded successfully!")
    return result


def list_cache() -> list:
    """List names of all cached datasets.

    Returns
    -------
    list,
        A list contains all cached datasets' names.

    """
    if not os.path.exists(CACHED_DATASET_DIR):
        os.makedirs(CACHED_DATASET_DIR)
        return []
    else:
        dir_content = os.listdir(CACHED_DATASET_DIR)

        # remove unrelated content
        if ".DS_Store" in dir_content:
            dir_content.remove(".DS_Store")

        return dir_content


def delete_cache(dataset_name=None) -> None:
    """Delete CACHED_DATASET_DIR if exists."""
    # if CACHED_DATASET_DIR does not exist, abort
    if not os.path.exists(CACHED_DATASET_DIR):
        logger.info("No cached data. Operation aborted.")
        sys.exit()
    # if CACHED_DATASET_DIR exists, then purge
    if dataset_name is not None:
        assert (
            dataset_name in AVAILABLE_DATASETS
        ), f"{dataset_name} is not available in TSDB, so it has no cache. Please check your dataset name."
        dir_to_delete = os.path.join(CACHED_DATASET_DIR, dataset_name)
        if not os.path.exists(dir_to_delete):
            logger.info(f"Dataset {dataset_name} is not cached. Operation aborted.")
            sys.exit()
        logger.info(f"Purging cached dataset {dataset_name} under {dir_to_delete}...")
    else:
        dir_to_delete = CACHED_DATASET_DIR
        logger.info(f"Purging all cached data under {CACHED_DATASET_DIR}...")
    purge_path(dir_to_delete)


# deprecated functions below


def list_available_datasets():
    """List all available datasets.

    Returns
    -------
    AVAILABLE_DATASETS : list
        A list contains all datasets' names.

    Warnings
    --------
    The method list_available_datasets is deprecated. Please use ``list()`` instead.

    """
    logger.warning(
        "🚨DeprecationWarning: The method list_available_datasets is deprecated. Please use `list()` instead."
    )
    return list()


def list_database():
    """List the database.

    Returns
    -------
    DATABASE : dict
        A dict contains all datasets' names and download links.

    Warnings
    --------
    The method list_available_datasets is deprecated. Please use `list()` instead.

    """
    logger.warning(
        "🚨DeprecationWarning: The method list_available_datasets is deprecated. Please use `list()` instead."
    )
    return list()


def list_cached_data():
    """List names of all cached datasets.

    Returns
    -------
    list,
        A list contains all cached datasets' names.

    Warnings
    --------
    The method list_cached_data is deprecated. Please use `list_cache()` instead.

    """
    logger.warning(
        "🚨DeprecationWarning: The method list_cached_data is deprecated. Please use `list_cache()` instead."
    )
    return list_cache()


def load_dataset(dataset_name, use_cache=True):
    """Load dataset with given name.

    Parameters
    ----------
    dataset_name : str,
        The name of the specific dataset in database.DATABASE.

    use_cache : bool,
        Whether to use cache (including data downloading and processing)

    Returns
    -------
    result:
        Loaded dataset in a Python dict.

    Warnings
    --------
    The method load_dataset is deprecated. Please use `load()` instead.
    """
    logger.warning(
        "🚨DeprecationWarning: The method load_dataset is deprecated. Please use `load()` instead."
    )
    return load(dataset_name, use_cache)


def delete_cached_data(dataset_name=None):
    """Delete CACHED_DATASET_DIR if exists.

    Warnings
    --------
    The method delete_cached_data is deprecated. Please use `delete_cache()` instead.
    """
    logger.warning(
        "🚨DeprecationWarning: The method delete_cached_data is deprecated. Please use `delete_cache()` instead."
    )
    delete_cache(dataset_name)
