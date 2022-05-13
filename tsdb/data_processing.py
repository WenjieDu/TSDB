"""
Utilities for loading specific datasets.
"""
# Created by Wenjie Du <wenjay.du@gmail.com>
# License: GPL-v3

import os
import pickle
import shutil
import tempfile
import warnings
from sys import exit
from urllib.request import urlretrieve

import numpy as np

from tsdb.data_loading_funcs import *
from tsdb.database import DATABASE, AVAILABLE_DATASETS

CACHED_DATASET_DIR = os.path.join(os.path.expanduser('~'), ".tsdb_cached_datasets")


def window_truncate(feature_vectors, seq_len):
    """ Generate time series samples, truncating windows from time-series data with a given sequence length.

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
    start_indices = np.asarray(range(feature_vectors.shape[0] // seq_len)) * seq_len
    sample_collector = []
    for idx in start_indices:
        sample_collector.append(feature_vectors[idx: idx + seq_len])

    return np.asarray(sample_collector).astype('float32')


def _download_and_extract(url, saving_path):
    """ Download dataset from the given url and extract to the given saving path.

    Parameters
    ----------
    url : str,
        URL of the dataset to be downloaded.
    saving_path : str,
        Path to save extracted dataset.

    Returns
    -------
    saving_path if successful else None
    """
    no_need_decompression_format = ['csv', 'txt']
    supported_compression_format = ["zip", "tar", "gz", "bz", "xz"]

    # truncate the file name from url
    file_name = os.path.basename(url)
    suffix = file_name.split('.')[-1]

    if suffix in no_need_decompression_format:
        raw_data_saving_path = os.path.join(saving_path, file_name)
    elif suffix in supported_compression_format:
        # create temp dir for raw data saving
        tmp_dir = tempfile.mkdtemp()
        raw_data_saving_path = os.path.join(tmp_dir, file_name)
    else:
        warnings.warn(
            "The compression format is not supported, aborting. "
            "If necessary, please create a pull request to add according supports.",
            category=RuntimeWarning
        )
        return None

    # download and save the raw dataset
    try:
        urlretrieve(url, raw_data_saving_path)
    # except Exception as e:
    except Exception as e:
        shutil.rmtree(saving_path, ignore_errors=True)
        print(f"Exception: {e}\n"
              f"Download failed. Aborting.")
        exit()
    print(f"Successfully downloaded data to {raw_data_saving_path}.")

    if suffix in supported_compression_format:  # if the file is compressed, then unpack it
        try:
            os.makedirs(saving_path, exist_ok=True)
            shutil.unpack_archive(raw_data_saving_path, saving_path)
            print(f"Successfully extracted data to {saving_path}")
        except shutil.Error:
            warnings.warn("The compressed file is corrupted, aborting.", category=RuntimeWarning)
            return None
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    return saving_path


def download_and_extract(dataset_name, dataset_saving_path):
    """ Wrapper of _download_and_extract.

    Parameters
    ----------
    dataset_name : str,
        The name of a dataset available in tsdb.

    dataset_saving_path : str,
        The local path for dataset saving.

    Returns
    -------

    """
    print('Start downloading...')
    os.makedirs(dataset_saving_path)
    if isinstance(DATABASE[dataset_name], list):
        for link in DATABASE[dataset_name]:
            _download_and_extract(link, dataset_saving_path)
    else:
        _download_and_extract(DATABASE[dataset_name], dataset_saving_path)


def list_cached_data():
    """ List names of all cached datasets.

    Returns
    -------
    list,
        A list contains all cached datasets' names.

    """
    if not os.path.exists(CACHED_DATASET_DIR):
        os.makedirs(CACHED_DATASET_DIR)
        return []
    else:
        return os.listdir(CACHED_DATASET_DIR)


def delete_cached_data(dataset_name=None):
    """ Delete CACHED_DATASET_DIR if exists.
    """
    # if CACHED_DATASET_DIR does not exist, abort
    if not os.path.exists(CACHED_DATASET_DIR):
        print('No cached data. Operation aborted.')
        exit()
    # if CACHED_DATASET_DIR exists, then purge
    try:
        if dataset_name is not None:
            assert dataset_name in AVAILABLE_DATASETS, \
                f'{dataset_name} is not available in TSDB, so it has no cache. Please check your dataset name.'
            dir_to_delete = os.path.join(CACHED_DATASET_DIR, dataset_name)
            if not os.path.exists(dir_to_delete):
                print(f'Dataset {dataset_name} is not cached. Operation aborted.')
                exit()
            print(f'Purging cached dataset {dataset_name} under {dir_to_delete}...')
        else:
            dir_to_delete = CACHED_DATASET_DIR
            print(f'Purging all cached data under {CACHED_DATASET_DIR}...')
        shutil.rmtree(dir_to_delete, ignore_errors=True)
        # check if succeed
        if not os.path.exists(dir_to_delete):
            print('Purged successfully!')
        else:
            raise FileExistsError(f'Deleting operation failed. {CACHED_DATASET_DIR} still exists.')
    except shutil.Error:
        raise shutil.Error('Operation failed.')


def pickle_dump(data, path):
    """ Pickle the given object.

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
        with open(path, 'wb') as f:
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
    except pickle.PicklingError:
        print('Pickling failed. No cache will be saved.')
        return None
    return path


def pickle_load(path):
    """ Load pickled object from file.

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
        with open(path, 'rb') as f:
            data = pickle.load(f)
    except pickle.UnpicklingError:
        print('Cached data corrupted. Aborting...\n'
              'Please rerun func load_specific_dataset with option use_cache=False')
    return data


def load_dataset(dataset_name, use_cache=True):
    """ Load dataset with given name.

    Parameters
    ----------
    dataset_name : str,
        The name of the specific dataset in DATABASE.

    use_cache : bool,
        Whether to use cache (including data downloading and processing)

    Returns
    -------
    pandas.DataFrame,
        Loaded dataset.
    """
    assert dataset_name in AVAILABLE_DATASETS, f'Input dataset name "{dataset_name}" is not in the database {AVAILABLE_DATASETS}.'
    dataset_saving_path = os.path.join(CACHED_DATASET_DIR, dataset_name)
    if not os.path.exists(dataset_saving_path):  # if the dataset is not cached, then download it
        download_and_extract(dataset_name, dataset_saving_path)
    else:
        if use_cache:
            print(f'Dataset {dataset_name} has already been downloaded. Processing directly...')
        else:
            # if not use cache, then delete the downloaded data dir (including processing cache)
            shutil.rmtree(dataset_saving_path, ignore_errors=True)
            download_and_extract(dataset_name, dataset_saving_path)

    # if cached, then load directly
    cache_path = os.path.join(dataset_saving_path, dataset_name + '_cache.pkl')
    if os.path.exists(cache_path):
        print(f'Dataset {dataset_name} has already been cached. Loading from cache directly...')
        result = pickle_load(cache_path)
    else:
        try:
            if dataset_name == 'physionet_2012':
                result = load_physionet2012(dataset_saving_path)
            if dataset_name == 'physionet_2019':
                result = load_physionet2019(dataset_saving_path)
            elif dataset_name == 'electricity_load_diagrams':
                result = load_electricity(dataset_saving_path)
            elif dataset_name == 'beijing_multisite_air_quality':
                result = load_beijing_air_quality(dataset_saving_path)
            elif 'UCR_UEA_' in dataset_name:
                actual_dataset_name = dataset_name.replace('UCR_UEA_', '')  # delete 'UCR_UEA_' in the name
                result = load_ucr_uea_dataset(dataset_saving_path, actual_dataset_name)

        except FileExistsError:
            shutil.rmtree(dataset_saving_path, ignore_errors=True)
            warnings.warn(
                'Dataset corrupted, already deleted. Please rerun load_specific_dataset() to re-download the raw data.'
            )
        pickle_dump(result, cache_path)

    print('Loaded successfully!')
    return result
