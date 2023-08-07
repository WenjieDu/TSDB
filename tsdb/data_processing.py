"""
Functions for loading datasets.
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: GPL-v3

import os
import shutil
import sys
import warnings

import numpy

from tsdb.database import DATABASE, AVAILABLE_DATASETS, CACHED_DATASET_DIR
from tsdb.loading_funcs import (
    load_physionet2012,
    load_physionet2019,
    load_electricity,
    load_beijing_air_quality,
    load_ucr_uea_dataset,
    load_ais,
)
from tsdb.utils.downloading import download_and_extract
from tsdb.utils.file import purge_given_path, pickle_load, pickle_dump
from tsdb.utils.logging import logger


def list_database():
    """List the database.

    Returns
    -------
    DATABASE : dict
        A dict contains all datasets' names and download links.

    """
    return DATABASE


def list_available_datasets():
    """List all available datasets.

    Returns
    -------
    AVAILABLE_DATASETS : list
        A list contains all datasets' names.

    """
    return AVAILABLE_DATASETS


def window_truncate(feature_vectors, seq_len):
    """Generate time series samples, truncating windows from time-series data with a given sequence length.

    Parameters
    ----------
    feature_vectors : array, shape of [total_length, feature_num]
        Time-series data.
    seq_len : int,
        Sequence length.

    Returns
    -------
    array,
        Truncated time series with given sequence length.
    """
    start_indices = numpy.asarray(range(feature_vectors.shape[0] // seq_len)) * seq_len
    sample_collector = []
    for idx in start_indices:
        sample_collector.append(feature_vectors[idx : idx + seq_len])

    return numpy.asarray(sample_collector).astype("float32")


def list_cached_data():
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


def delete_cached_data(dataset_name=None):
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
    purge_given_path(dir_to_delete)


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
    pandas.DataFrame,
        Loaded dataset.
    """
    assert dataset_name in AVAILABLE_DATASETS, (
        f'The given dataset name "{dataset_name}" is not in the database. '
        f"Please fetch the full list of the available dataset_profiles with tsdb.list_available_datasets()"
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
            elif dataset_name == "beijing_multisite_air_quality":
                result = load_beijing_air_quality(dataset_saving_path)
            elif dataset_name == "vessel_ais":
                result = load_ais(dataset_saving_path)
            elif "ucr_uea_" in dataset_name:
                actual_dataset_name = dataset_name.replace(
                    "ucr_uea_", ""
                )  # delete 'ucr_uea_' in the name
                result = load_ucr_uea_dataset(dataset_saving_path, actual_dataset_name)

        except FileExistsError:
            shutil.rmtree(dataset_saving_path, ignore_errors=True)
            warnings.warn(
                "Dataset corrupted, already deleted. Please rerun load_specific_dataset() to re-download the raw data."
            )
        pickle_dump(result, cache_path)

    logger.info("Loaded successfully!")
    return result
