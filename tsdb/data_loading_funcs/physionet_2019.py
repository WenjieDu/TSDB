"""
Scripts related to dataset PhysioNet Challenge 2019.

"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: GLP-v3

import os

import pandas as pd


def load_physionet2019(local_path):
    time_series_measurements_dir = ['training', 'training_setB']
    label_feature = 'SepsisLabel'  # feature SepsisLabel contains labels indicating whether patients get sepsis
    time_feature = 'ICULOS'  # ICU length-of-stay (hours since ICU admit)

    df_collector = []
    for m_ in time_series_measurements_dir:
        raw_data_dir = os.path.join(local_path, m_)
        for filename in os.listdir(raw_data_dir):
            recordID = filename.split('.psv')[0]
            with open(os.path.join(raw_data_dir, filename), 'r') as f:
                df_temp = pd.read_csv(f, sep='|', header=0)
            df_temp['RecordID'] = recordID
            df_collector.append(df_temp)

    df = pd.concat(df_collector, sort=True)
    df = df.reset_index(drop=True)
    y = df[['RecordID', time_feature, label_feature]]
    X = df.drop(label_feature, axis=1)

    data = {
        'X': X,
        'y': y,
        'static_features': ['Age', 'Gender', 'HospAdmTime']
    }
    return data
