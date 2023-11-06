"""
Scripts related to dataset Beijing Multi-site Air Quality.

For more information please refer to:
https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/beijing_multisite_air_quality
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: BSD-3-Clause

import os

import pandas as pd

from ..utils.logging import logger


def load_beijing_air_quality(local_path):
    """Load dataset Beijing Multi-site Air Quality.

    Parameters
    ----------
    local_path : str,
        The local path of dir saving the raw data of Beijing Multi-site Air Quality.

    Returns
    -------
    data : dict
        A dictionary contains X:
            X : pandas.DataFrame
                The time-series data of Beijing Multi-site Air Quality.
    """
    dir_path = os.path.join(local_path, "PRSA_Data_20130301-20170228")
    df_collector = []
    file_list = os.listdir(dir_path)
    for filename in file_list:
        file_path = os.path.join(dir_path, filename)
        current_df = pd.read_csv(file_path)
        df_collector.append(current_df)
        logger.info(f"Reading {file_path}, data shape {current_df.shape}")
    df = pd.concat(df_collector, axis=0)
    data = {
        "X": df,
    }
    return data
