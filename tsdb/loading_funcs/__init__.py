"""
Functions to load specific datasets.
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: GLP-v3

from tsdb.loading_funcs.beijing_multisite_air_quality import (
    load_beijing_air_quality,
)
from tsdb.loading_funcs.electricity_load_diagrams import load_electricity
from tsdb.loading_funcs.physionet_2012 import load_physionet2012
from tsdb.loading_funcs.physionet_2019 import load_physionet2019
from tsdb.loading_funcs.ucr_uea_datasets import load_ucr_uea_dataset
from tsdb.loading_funcs.vessel_ais import load_ais

__all__ = [
    "load_beijing_air_quality",
    "load_electricity",
    "load_physionet2012",
    "load_physionet2019",
    "load_ucr_uea_dataset",
    "load_ais",
]
