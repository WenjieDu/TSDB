import numpy as np
import pandas as pd
import time
import os

def load_AIS(local_path):
    """ Load dataset AIS data, which is a time-series imputation and classification dataset.
    Parameters
    ----------
    local_path : str,
        The local path of dir saving the raw data of AIS data.
    Returns
    -------
    data : dict
        A dictionary contains X and y:
            X : pandas.DataFrame,
                Time-series feature vectors.
            y : pandas.Series,
                Classification labels.
    Notes
    -----
    All samples (vessels) contain 6000 time steps each. Raw data is filtered by speed over ground > 0.2 to
    make sure moving vessels are taken into account only.
    This could also be done usong navigational status number. To make sure data is regulary sampled each vessel
    sequence is sliced on 2000 samples and resampled with 3S buckets. The mean value is taken inside.
    Course and heading are wrapped to {-180,180}, so "cog" and "true_heading" are turned into "course" and "heading" respectively.
    Column "date_time_utc" is converted to float and index is set as timeindex starting
    from 0 for each vessel. Imputation could be made in lat,lon,sog and cog column and classification could
    be to find vessel length class based on observed positional and velocity data. 
    Other features such as "nav_status", "message_nr" and "imo_nr" are removed.
    """

    start_time = time.time()
    print('Please wait for 3-4 min')
    path_to_parquets = local_path

    filenames= os.listdir (path_to_parquets)

    mmsis = list()
    s = list()
    a = list()
    data = dict()

    for p in filenames:
        
        path =os.path.join(path_to_parquets, p)
        df = pd.read_parquet(path, engine='pyarrow')
        
        print(f'Reading {path}, data shape {df.shape}')
        
        vessels = list(df["mmsi"].unique())

        for k in vessels:

             g = df.groupby(by = "mmsi").get_group(k)
             g = g.loc[g['sog'] > 0.2 ].iloc[0:2000]

             if len(g) == 2000:

                 datetime_series = pd.to_datetime(g["date_time_utc"])
                 datetime_index = pd.DatetimeIndex(datetime_series.values)
                 g = g.set_index(datetime_index)
                 values = datetime_series.values.astype(float)
                 t = np.amin(values)
                 g["time"] = ( values - t ) / 10 ** 9

                 g = g.resample('3S').mean(numeric_only=True).iloc[0:6000]

             if len(g) == 6000:

                 g.loc[:,['mmsi']] = g.loc[:,['mmsi']].ffill()
                 g['mmsi'] =  g['mmsi'].values.astype(int)
                 g.loc[:,['length']] = g.loc[:,['length']].ffill()

                 g = g.assign(heading = lambda x: np.mod(x["true_heading"] - 180.0, 360.0) - 180.0)
                 g = g.assign(course = lambda x: np.mod(x["cog"] - 180.0, 360.0) - 180.0)

                 m = g["mmsi"][0]

                 if m not in mmsis:
                     s.append(g.reset_index(drop=True).drop(columns = ["nav_status", "message_nr","imo_nr", "true_heading","cog"]))
                     a.append(pd.DataFrame({"Length":[g["length"][0]], "MMSI": [g["mmsi"][0]]}))

                     mmsis.append(m)

    data['X'] = pd.concat(s)
    data['y'] = pd.concat(a)
    data['y'].set_index("MMSI", inplace=True)

    print("--- %s seconds ---" % (time.time() - start_time))
    print (f'Number of unique vessel trajectories for training is {len(mmsis)}')

    return data
