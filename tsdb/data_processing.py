"""
Functions for loading datasets.
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: BSD-3-Clause

import os
import shutil
import warnings

from .database import AVAILABLE_DATASETS
from .loading_funcs import (
    load_physionet2012,
    load_physionet2019,
    load_electricity,
    load_ett,
    load_beijing_air_quality,
    load_ucr_uea_dataset,
    load_ais,
    load_italy_air_quality,
    load_pems_traffic,
    load_solar_alabama,
)
from .utils.downloading import download_and_extract
from .utils.file import purge_path, pickle_load, pickle_dump, determine_tsdb_home
from .utils.logging import logger

CACHED_DATASET_DIR = determine_tsdb_home()


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
            elif dataset_name == "italy_air_quality":
                result = load_italy_air_quality(dataset_saving_path)
            elif dataset_name == "vessel_ais":
                result = load_ais(dataset_saving_path)
            elif dataset_name == "pems_traffic":
                result = load_pems_traffic(dataset_saving_path)
            elif dataset_name == "solar_alabama":
                result = load_solar_alabama(dataset_saving_path)
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


def delete_cache(dataset_name: str = None, only_pickle: bool = False) -> None:
    """Delete CACHED_DATASET_DIR if exists.

    Parameters
    ----------
    dataset_name : str, optional
        The name of the specific dataset in database.DATABASE.
        If dataset is not cached, then abort.
        Delete all cached datasets if dataset_name is left as None.

    only_pickle : bool,
        Whether to delete only the cached pickle file.
        When the preprocessing pipeline TSDB is changed, users may want to only delete the cached pickle file which is
        generated by the old pipeline but keep the downloaded raw data. This option is designed for this purpose.

    """
    # if CACHED_DATASET_DIR does not exist, abort
    if not os.path.exists(CACHED_DATASET_DIR):
        logger.error("❌ No cached data. Operation aborted.")
    else:
        # if CACHED_DATASET_DIR exists, then execute purging procedure
        if dataset_name is None:  # if dataset_name is not given, then purge all
            logger.info(
                f"`dataset_name` not given. Purging all cached data under {CACHED_DATASET_DIR}..."
            )
            if only_pickle:
                for cached_dataset in os.listdir(CACHED_DATASET_DIR):
                    for file in os.listdir(
                        os.path.join(CACHED_DATASET_DIR, cached_dataset)
                    ):
                        if file.endswith(".pkl"):
                            purge_path(
                                os.path.join(CACHED_DATASET_DIR, cached_dataset, file)
                            )
            else:
                purge_path(CACHED_DATASET_DIR)
                os.makedirs(CACHED_DATASET_DIR)
        else:
            assert (
                dataset_name in AVAILABLE_DATASETS
            ), f"{dataset_name} is not available in TSDB, so it has no cache. Please check your dataset name."
            if only_pickle:
                for file in os.listdir(os.path.join(CACHED_DATASET_DIR, dataset_name)):
                    if file.endswith(".pkl"):
                        purge_path(os.path.join(CACHED_DATASET_DIR, dataset_name, file))
            else:
                dir_to_delete = os.path.join(CACHED_DATASET_DIR, dataset_name)
                if not os.path.exists(dir_to_delete):
                    logger.error(
                        f"❌ Dataset {dataset_name} is not cached. Operation aborted."
                    )
                    return
                else:
                    logger.info(
                        f"Purging cached dataset {dataset_name} under {dir_to_delete}..."
                    )
                    purge_path(dir_to_delete)
