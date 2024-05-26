"""
Scripts related to dataset Italy Air Quality.

For more information please refer to:
https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/italy_air_quality
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: BSD-3-Clause

import os

import pandas as pd


def load_italy_air_quality(local_path):
    """Load dataset Italy Air Quality.

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
    file_path = os.path.join(local_path, "AirQualityUCI.csv")
    df = pd.read_csv(file_path, sep=";", decimal=",")
    # remove empty columns
    df.drop(columns=["Unnamed: 15", "Unnamed: 16"], inplace=True)
    # remove rows with all NaN, i.e. Date is NaN
    df = df[~df["Date"].isna()]

    data = {
        "X": df,
    }
    return data
