"""
Functions to load specific datasets.
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: BSD-3-Clause

from .beijing_multisite_air_quality import load_beijing_air_quality
from .electricity_load_diagrams import load_electricity
from .electricity_transformer_temperature import load_ett
from .italy_air_quality import load_italy_air_quality
from .physionet_2012 import load_physionet2012
from .physionet_2019 import load_physionet2019
from .ucr_uea_datasets import load_ucr_uea_dataset
from .vessel_ais import load_ais
from .pems_traffic import load_pems_traffic
from .solar_alabama import load_solar_alabama

__all__ = [
    "load_beijing_air_quality",
    "load_electricity",
    "load_physionet2012",
    "load_physionet2019",
    "load_ucr_uea_dataset",
    "load_ais",
    "load_ett",
    "load_italy_air_quality",
    "load_pems_traffic",
    "load_solar_alabama",
]
