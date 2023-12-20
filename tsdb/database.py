"""
List available datasets and their official download links.
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: BSD-3-Clause

import os
from configparser import ConfigParser

from .utils.logging import logger

config = ConfigParser()
tsdb_config_path = os.path.join(os.path.dirname(__file__), "config.ini")
config.read(tsdb_config_path)

old_cached_dataset_dir = os.path.join(os.path.expanduser("~"), ".tsdb_cached_datasets")
CACHED_DATASET_DIR = os.path.join(
    os.path.expanduser("~"), config.get("path", "data_home")
)
if os.path.exists(old_cached_dataset_dir):
    logger.warning(
        "‼️ Detected the home dir of the old version TSDB. "
        "Since v0.3, TSDB has changed the default cache dir to '~/.tsdb'. "
        "You can migrate downloaded datasets by invoking the new function "
        f"tsdb.migrate(old='~/.tsdb_cached_datasets', new={CACHED_DATASET_DIR})"
    )
    CACHED_DATASET_DIR = old_cached_dataset_dir


_DATABASE = {
    # http://www.physionet.org/challenge/2012
    # https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/physionet_2012
    "physionet_2012": [
        "https://www.physionet.org/files/challenge-2012/1.0.0/set-a.tar.gz",
        "https://www.physionet.org/files/challenge-2012/1.0.0/set-b.tar.gz",
        "https://www.physionet.org/files/challenge-2012/1.0.0/set-c.tar.gz",
        "https://www.physionet.org/files/challenge-2012/1.0.0/Outcomes-a.txt",
        "https://www.physionet.org/files/challenge-2012/1.0.0/Outcomes-b.txt",
        "https://www.physionet.org/files/challenge-2012/1.0.0/Outcomes-c.txt",
    ],
    # http://www.physionet.org/challenge/2019
    # https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/physionet_2019
    "physionet_2019": [
        "https://archive.physionet.org/users/shared/challenge-2019/training_setA.zip",
        "https://archive.physionet.org/users/shared/challenge-2019/training_setB.zip",
    ],
    #
    # https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/electricity_load_diagrams
    "electricity_load_diagrams": "https://archive.ics.uci.edu/ml/machine-learning-databases/00321/LD2011_2014.txt.zip",
    #
    # https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/beijing_multisite_air_quality
    "beijing_multisite_air_quality": "https://archive.ics.uci.edu/ml/machine-learning-databases/00501/"
    "PRSA2017_Data_20130301-20170228.zip",
    #
    # https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/vessel_ais
    "vessel_ais": "https://zenodo.org/record/8064564/files/parquets.zip",
    #
    # https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/electricity_transformer_temperature
    "electricity_transformer_temperature": [
        "https://raw.githubusercontent.com/zhouhaoyi/ETDataset/main/ETT-small/ETTm1.csv",
        "https://raw.githubusercontent.com/zhouhaoyi/ETDataset/main/ETT-small/ETTm2.csv",
        "https://raw.githubusercontent.com/zhouhaoyi/ETDataset/main/ETT-small/ETTh1.csv",
        "https://raw.githubusercontent.com/zhouhaoyi/ETDataset/main/ETT-small/ETTh2.csv",
    ],
}


# https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/ucr_uea_datasets
# 128 UCR + 33 UEA + 2 old removed (NonInvasiveFatalECGThorax1 and 2) = 163
_ucr_uea_datasets = [
    "ACSF1",
    "Adiac",
    "AllGestureWiimoteX",
    "AllGestureWiimoteY",
    "AllGestureWiimoteZ",
    "ArrowHead",
    "Beef",
    "BeetleFly",
    "BirdChicken",
    "BME",
    "Car",
    "CBF",
    "Chinatown",
    "ChlorineConcentration",
    "CinCECGTorso",
    "Coffee",
    "Computers",
    "CricketX",
    "CricketY",
    "CricketZ",
    "Crop",
    "DiatomSizeReduction",
    "DistalPhalanxOutlineCorrect",
    "DistalPhalanxOutlineAgeGroup",
    "DistalPhalanxTW",
    "DodgerLoopDay",
    "DodgerLoopGame",
    "DodgerLoopWeekend",
    "Earthquakes",
    "ECG200",
    "ECG5000",
    "ECGFiveDays",
    "ElectricDevices",
    "EOGHorizontalSignal",
    "EOGVerticalSignal",
    "EthanolLevel",
    "FaceAll",
    "FaceFour",
    "FacesUCR",
    "FiftyWords",
    "Fish",
    "FordA",
    "FordB",
    "FreezerRegularTrain",
    "FreezerSmallTrain",
    "Fungi",
    "GestureMidAirD1",
    "GestureMidAirD2",
    "GestureMidAirD3",
    "GesturePebbleZ1",
    "GesturePebbleZ2",
    "GunPoint",
    "GunPointAgeSpan",
    "GunPointMaleVersusFemale",
    "GunPointOldVersusYoung",
    "Ham",
    "HandOutlines",
    "Haptics",
    "Herring",
    "HouseTwenty",
    "InlineSkate",
    "InsectEPGRegularTrain",
    "InsectEPGSmallTrain",
    "InsectWingbeatSound",
    "ItalyPowerDemand",
    "LargeKitchenAppliances",
    "Lightning2",
    "Lightning7",
    "Mallat",
    "Meat",
    "MedicalImages",
    "MelbournePedestrian",
    "MiddlePhalanxOutlineCorrect",
    "MiddlePhalanxOutlineAgeGroup",
    "MiddlePhalanxTW",
    "MixedShapesRegularTrain",
    "MixedShapesSmallTrain",
    "MoteStrain",
    "NonInvasiveFetalECGThorax1",
    "NonInvasiveFetalECGThorax2",
    "OliveOil",
    "OSULeaf",
    "PhalangesOutlinesCorrect",
    "Phoneme",
    "PickupGestureWiimoteZ",
    "PigAirwayPressure",
    "PigArtPressure",
    "PigCVP",
    "PLAID",
    "Plane",
    "PowerCons",
    "ProximalPhalanxOutlineCorrect",
    "ProximalPhalanxOutlineAgeGroup",
    "ProximalPhalanxTW",
    "RefrigerationDevices",
    "Rock",
    "ScreenType",
    "SemgHandGenderCh2",
    "SemgHandMovementCh2",
    "SemgHandSubjectCh2",
    "ShakeGestureWiimoteZ",
    "ShapeletSim",
    "ShapesAll",
    "SmallKitchenAppliances",
    "SmoothSubspace",
    "SonyAIBORobotSurface1",
    "SonyAIBORobotSurface2",
    "StarLightCurves",
    "Strawberry",
    "SwedishLeaf",
    "Symbols",
    "SyntheticControl",
    "ToeSegmentation1",
    "ToeSegmentation2",
    "Trace",
    "TwoLeadECG",
    "TwoPatterns",
    "UMD",
    "UWaveGestureLibraryAll",
    "UWaveGestureLibraryX",
    "UWaveGestureLibraryY",
    "UWaveGestureLibraryZ",
    "Wafer",
    "Wine",
    "WordSynonyms",
    "Worms",
    "WormsTwoClass",
    "Yoga",
    "ArticularyWordRecognition",
    "AsphaltObstaclesCoordinates",
    "AsphaltPavementTypeCoordinates",
    "AsphaltRegularityCoordinates",
    "AtrialFibrillation",
    "BasicMotions",
    "CharacterTrajectories",
    "Cricket",
    "DuckDuckGeese",
    "EigenWorms",
    "Epilepsy",
    "EthanolConcentration",
    "ERing",
    "FaceDetection",
    "FingerMovements",
    "HandMovementDirection",
    "Handwriting",
    "Heartbeat",
    "InsectWingbeat",
    "JapaneseVowels",
    "Libras",
    "LSST",
    "MotorImagery",
    "NATOPS",
    "PenDigits",
    "PEMS-SF",
    "PhonemeSpectra",
    "RacketSports",
    "SelfRegulationSCP1",
    "SelfRegulationSCP2",
    "SpokenArabicDigits",
    "StandWalkJump",
    "UWaveGestureLibrary",
    "NonInvasiveFatalECGThorax1",
    "NonInvasiveFatalECGThorax2",
]

UCR_UEA_DATASETS = {}
for i in _ucr_uea_datasets:
    UCR_UEA_DATASETS[
        "ucr_uea_" + i
    ] = f"https://www.timeseriesclassification.com/aeon-toolkit/{i}.zip"

DATABASE = {**_DATABASE, **UCR_UEA_DATASETS}
AVAILABLE_DATASETS = list(DATABASE.keys())
