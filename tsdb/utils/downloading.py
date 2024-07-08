"""
Downloading functions.
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: BSD-3-Clause

import gzip
import os
import shutil
import tempfile
import warnings
from typing import Optional

import requests
from tqdm import tqdm

from .logging import logger
from ..database import DATABASE


def _download_and_extract(url: str, saving_path: str) -> Optional[str]:
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
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            chunk_size = 8192
            try:
                size = int(r.headers["Content-Length"])
            except KeyError:
                size = None

            with tqdm(
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                miniters=1,
                desc=f"Downloading {file_name}",
                total=size,
            ) as pbar:
                with open(raw_data_saving_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        f.write(chunk)
                        pbar.update(len(chunk))

    except Exception as e:
        shutil.rmtree(saving_path, ignore_errors=True)
        shutil.rmtree(raw_data_saving_path, ignore_errors=True)
        raise RuntimeError(f"Exception: {e}\n" f"Download failed. Aborting.")
    except KeyboardInterrupt:
        shutil.rmtree(saving_path, ignore_errors=True)
        shutil.rmtree(raw_data_saving_path, ignore_errors=True)
        raise KeyboardInterrupt("Download cancelled by the user.")

    logger.info(f"Successfully downloaded data to {raw_data_saving_path}")

    # if the file is compressed, then unpack it
    if suffix in supported_compression_format:
        try:
            os.makedirs(saving_path, exist_ok=True)
            if ".txt.gz" in file_name:
                new_name = file_name.split(".txt.gz")[0]
                new_name = new_name + ".txt"
                saving_path = os.path.join(saving_path, new_name)
                with open(raw_data_saving_path, "rb") as f, open(
                    saving_path, "wb"
                ) as wf:
                    wf.write(gzip.decompress(f.read()))
            else:
                shutil.unpack_archive(raw_data_saving_path, saving_path)
            logger.info(f"Successfully extracted data to {saving_path}")
        except Exception as e:
            shutil.rmtree(saving_path, ignore_errors=True)
            raise RuntimeError(f"❌ {e}")
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    return saving_path


def download_and_extract(dataset_name: str, dataset_saving_path: str) -> None:
    """Wrapper of _download_and_extract.

    Parameters
    ----------
    dataset_name : str,
        The name of a dataset available in tsdb.

    dataset_saving_path : str,
        The local path for dataset saving.

    """
    logger.info("Start downloading...")
    os.makedirs(dataset_saving_path)
    if isinstance(DATABASE[dataset_name], list):
        for link in DATABASE[dataset_name]:
            _download_and_extract(link, dataset_saving_path)
    else:
        _download_and_extract(DATABASE[dataset_name], dataset_saving_path)
