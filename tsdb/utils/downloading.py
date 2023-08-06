"""
Downloading functions.
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: GLP-v3


import os
import shutil
import tempfile
import urllib.request
import warnings

from tsdb.database import DATABASE
from tsdb.utils.logging import logger


def _download_and_extract(url, saving_path):
    """Download dataset from the given url and extract to the given saving path.

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
    no_need_decompression_format = ["csv", "txt"]
    supported_compression_format = ["zip", "tar", "gz", "bz", "xz"]

    # truncate the file name from url
    file_name = os.path.basename(url)
    suffix = file_name.split(".")[-1]

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
            category=RuntimeWarning,
        )
        return None

    # download and save the raw dataset
    try:
        urllib.request.urlretrieve(url, raw_data_saving_path)
    except Exception as e:
        shutil.rmtree(saving_path, ignore_errors=True)
        shutil.rmtree(raw_data_saving_path, ignore_errors=True)
        logger.info(f"Exception: {e}\n" f"Download failed. Aborting.")
        raise
    except KeyboardInterrupt:
        shutil.rmtree(saving_path, ignore_errors=True)
        shutil.rmtree(raw_data_saving_path, ignore_errors=True)
        logger.info("Download cancelled by the user.")
        raise

    logger.info(f"Successfully downloaded data to {raw_data_saving_path}.")

    if (
        suffix in supported_compression_format
    ):  # if the file is compressed, then unpack it
        try:
            os.makedirs(saving_path, exist_ok=True)
            shutil.unpack_archive(raw_data_saving_path, saving_path)
            logger.info(f"Successfully extracted data to {saving_path}")
        except shutil.Error:
            warnings.warn(
                "The compressed file is corrupted, aborting.", category=RuntimeWarning
            )
            return None
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    return saving_path


def download_and_extract(dataset_name, dataset_saving_path):
    """Wrapper of _download_and_extract.

    Parameters
    ----------
    dataset_name : str,
        The name of a dataset available in tsdb.

    dataset_saving_path : str,
        The local path for dataset saving.

    Returns
    -------

    """
    logger.info("Start downloading...")
    os.makedirs(dataset_saving_path)
    if isinstance(DATABASE[dataset_name], list):
        for link in DATABASE[dataset_name]:
            _download_and_extract(link, dataset_saving_path)
    else:
        _download_and_extract(DATABASE[dataset_name], dataset_saving_path)
