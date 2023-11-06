"""
Scripts related to dataset vessel_AIS.

For more information please refer to:
https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/vessel_ais
"""

# Created by Grgičević Luka <luka.grgicevic@ntnu.no>
# Modified by Wenjie Du <wenjay.du@gmail.com>
# License: BSD-3-Clause

import os
import time

import numpy as np
import pandas as pd
from pandas.errors import UnsupportedFunctionCall

from ..utils.logging import logger


def load_ais(local_path):
    """Load dataset AIS data, which is a time-series imputation and classification dataset.

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
    This could also be done using a navigational status number. To make sure data is regularly sampled each vessel
    sequence is sliced on 2000 samples and resampled with 3S buckets. The mean value is taken inside.
    Course and heading are wrapped to {-180,180}, so "cog" and "true_heading" are turned into "course" and "heading"
    respectively. Column "date_time_utc" is converted to float and the index is set as timeindex starting
    from 0 for each vessel. Imputation could be made in lat,long, sog and cog column and classification could
    be to find vessel length class based on observed positional and velocity data.
    Other features such as "nav_status", "message_nr" and "imo_nr" are removed.
    """

    start_time = time.time()
    logger.info("Please wait...")
    path_to_parquets = os.path.join(local_path, "parquets")

    filenames = os.listdir(path_to_parquets)

    mmsis = list()
    s = list()
    a = list()
    data = dict()
    i = 0

    """
    There are 40 parquet files with around 200 vessels per file, with unknown trajectory length and possible duplicates
    of vessels (car ferries)
    """
    for p in filenames:

        path = os.path.join(path_to_parquets, p)
        df = pd.read_parquet(path, engine="pyarrow")
        logger.info(
            f"Reading group of vessel trajectories {i}/40 from {path}, data shape {df.shape}"
        )
        i += 1

        # Making a list of unique vessel identifiers
        vessels = list(df["mmsi"].unique())

        for k in vessels:

            # Grouping time series by MMSI and filtering only moving vessels by "sog"

            g = df.groupby(by="mmsi").get_group(k)
            g = g.loc[g["sog"] > 0.2].iloc[0:2000]

            # Length of 2000 is taken provisionally, increasing to 3000 will reduce the number of vessels,
            # but the data would be better
            if len(g) == 2000:

                # Making an index made of date time, so we can use resample method
                # and leaving "date_time_utc" column in a float type

                datetime_series = pd.to_datetime(g["date_time_utc"])
                datetime_index = pd.DatetimeIndex(datetime_series.values)
                g = g.set_index(datetime_index)
                values = datetime_series.values.astype(float)

                # Here we shift time for every vessel, so it starts from 0, it can be removed
                t = np.amin(values)
                g["time"] = (values - t) / 10**9

                # Now we slice the time series to be all equal.
                # It is reasonable to expect that the series would be at least double in size,
                # so should slice it on at least 4000.
                # Navigational status tells what should be the sampling time (how often vessel sends an AIS message)
                # for a particular mode of operation (for example speed less than 25 knots, at anchor etc).
                try:
                    g = g.resample("3S").mean(numeric_only=True).iloc[0:6000]
                except UnsupportedFunctionCall:
                    # Refer to https://github.com/WenjieDu/TSDB/pull/13#issuecomment-1618798165
                    # This error may be caused by pandas lower versions like 1.4.4.
                    # Can be directly solved by upgrading pandas to 1.5.3.
                    g = g.resample("3S").mean().iloc[0:6000]

            # Maybe there are some time series shorter then 6000
            if len(g) == 6000:

                # Fill in the missing information regarding MMSI and length caused by resampling

                g.loc[:, ["mmsi"]] = g.loc[:, ["mmsi"]].ffill()
                g["mmsi"] = g["mmsi"].values.astype(int)
                g.loc[:, ["length"]] = g.loc[:, ["length"]].ffill()

                # Wrapping the angles to [-pi/2, pi/2] to prepare for scaling

                g = g.assign(
                    heading=lambda x: np.mod(x["true_heading"] - 180.0, 360.0) - 180.0
                )
                g = g.assign(course=lambda x: np.mod(x["cog"] - 180.0, 360.0) - 180.0)

                m = g["mmsi"][0]

                # Taking only unique MMSIs and dropping unnecessary columns

                if m not in mmsis:
                    # X data
                    s.append(
                        g.reset_index(drop=True).drop(
                            columns=[
                                "nav_status",
                                "message_nr",
                                "imo_nr",
                                "true_heading",
                                "cog",
                            ]
                        )
                    )
                    # y data, classes are length integer for possible classification
                    a.append(
                        pd.DataFrame(
                            {"Length": [g["length"][0]], "MMSI": [g["mmsi"][0]]}
                        )
                    )

                    # Vessels included in training stored in list of MMSIs
                    mmsis.append(m)

    data["X"] = pd.concat(s)
    data["y"] = pd.concat(a)
    data["y"].set_index("MMSI", inplace=True)

    logger.info(f"--- {(time.time() - start_time)} seconds ---")
    logger.info(f"Number of unique vessel trajectories for training is {len(mmsis)}")

    return data
