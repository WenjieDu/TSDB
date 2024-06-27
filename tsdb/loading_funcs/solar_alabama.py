"""
Scripts related to dataset Solar Alabama. It contains the solar power production records in the year 2006,
which are sampled every 10 minutes from 137 PV plants in Alabama State.
https://www.nrel.gov/grid/solar-power-data.html

For more information please refer to:
https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/solar_alabama
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: BSD-3-Clause

import os

import pandas as pd


def load_solar_alabama(local_path):
    """Load dataset Solar Alabama.

    Parameters
    ----------
    local_path : str,
        The local path of dir saving the raw data of Solar Alabama.

    Returns
    -------
    data : dict
        A dictionary contains X:
            X : pandas.DataFrame
                The time-series data of Solar Alabama.
    """
    dir_path = os.path.join(local_path, "solar_AL.txt")

    # make columns names
    col_names = [str(i) for i in range(137)]
    df = pd.read_csv(dir_path, index_col=None, names=col_names)
    date = pd.date_range(
        start="2006-01-01 00:00:00",
        end="2006-12-31 23:50:00",
        freq="10min",
    )
    df["date"] = date
    col_names.insert(0, "date")
    df = df[col_names]

    data = {
        "X": df,
    }
    return data
