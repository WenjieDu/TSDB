"""
Scripts related to dataset Electricity Transformer Temperature.

For more information please refer to:
https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/electricity_transformer_temperature

"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: BSD-3-Clause

import os

import pandas as pd


def load_ett(local_path):
    """Load dataset Electricity Transformer Temperature.

    Parameters
    ----------
    local_path : str,
        The local path of dir saving the raw data of Electricity Transformer Temperature.

    Returns
    -------
    data : dict
        A dictionary contains all four sub datasets:
            ETTm1 : pandas.DataFrame
                The time-series data of ETTm1
            ETTm2 : pandas.DataFrame
                The time-series data of ETTm2
            ETTh1 : pandas.DataFrame
                The time-series data of ETTh1
            ETTh2 : pandas.DataFrame
                The time-series data of ETTh2

    """
    sub_datasets = [
        "ETTm1.csv",
        "ETTm2.csv",
        "ETTh1.csv",
        "ETTh2.csv",
    ]

    data = {}
    for sub_set in sub_datasets:
        file_path = os.path.join(local_path, sub_set)
        df = pd.read_csv(file_path, index_col="date")
        df.index = pd.to_datetime(df.index)
        df_name = sub_set.split(".csv")[0]
        data[df_name] = df

    return data
