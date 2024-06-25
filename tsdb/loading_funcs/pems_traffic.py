"""
Scripts related to dataset PeMS Traffic.

For more information please refer to:
https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/pems_traffic
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: BSD-3-Clause

import os

import pandas as pd


def load_pems_traffic(local_path):
    """Load dataset PeMS Traffic.

    Parameters
    ----------
    local_path : str,
        The local path of dir saving the raw data of PeMS Traffic.

    Returns
    -------
    data : dict
        A dictionary contains X:
            X : pandas.DataFrame
                The time-series data of PeMS Traffic.
    """
    dir_path = os.path.join(local_path, "traffic.txt")

    # make columns names
    col_names = [str(i) for i in range(862)]
    df = pd.read_csv(dir_path, index_col=None, names=col_names)
    date = pd.date_range(
        start="2015-01-01 00:00:00",
        end="2016-12-31 23:00:00",
        freq="H",
    )
    df["date"] = date
    col_names.insert(0, "date")
    df = df[col_names]

    data = {
        "X": df,
    }
    return data
