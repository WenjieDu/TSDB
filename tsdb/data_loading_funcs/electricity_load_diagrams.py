"""
Scripts related to dataset Electricity Load Diagrams.

For more information please refer to:
https://github.com/WenjieDu/Time_Series_Database/tree/main/datasets/ElectricityLoadDiagrams

"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: GLP-v3

import os

import pandas as pd


def load_electricity(local_path):
    """ Load dataset Electricity Load Diagrams.

    Parameters
    ----------
    local_path : str,
        The local path of dir saving the raw data of Electricity Load Diagrams.

    Returns
    -------
    data : dict
        A dictionary contains X:
            X : pandas.DataFrame
                The time-series data of Electricity Load Diagrams.
    """
    file_path = os.path.join(local_path, 'LD2011_2014.txt')
    df = pd.read_csv(file_path, index_col=0, sep=';', decimal=',')
    df.index = pd.to_datetime(df.index)
    # feature_names = df.columns.tolist()
    # feature_num = len(feature_names)
    df['datetime'] = pd.to_datetime(df.index)
    data = {
        'X': df,
    }
    return data
