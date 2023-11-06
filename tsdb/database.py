"""
List available datasets and their official download links.
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: BSD-3-Clause

import os

CACHED_DATASET_DIR = os.path.join(os.path.expanduser("~"), ".tsdb_cached_datasets")

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
}


# The list of raw data files to be downloaded
MATR_LINKS = (
    (
        "https://data.matr.io/1/api/v1/file/5c86c0b5fa2ede00015ddf66/download",
        "2017-05-12_batchdata_updated_struct_errorcorrect.mat",
    ),
    (
        "https://data.matr.io/1/api/v1/file/5c86bf13fa2ede00015ddd82/download",
        "2017-06-30_batchdata_updated_struct_errorcorrect.mat",
    ),
    (
        "https://data.matr.io/1/api/v1/file/5c86bd64fa2ede00015ddbb2/download",
        "2018-04-12_batchdata_updated_struct_errorcorrect.mat",
    ),
    (
        "https://data.matr.io/1/api/v1/file/5dcef152110002c7215b2c90/download",
        "2019-01-24_batchdata_updated_struct_errorcorrect.mat",
    ),
)

HUST_LINKS = (
    (
        "https://data.mendeley.com/public-files/datasets/nsc7hnsg4s/"
        "files/5ca0ac3e-d598-4d07-8dcb-879aa047e98b/file_downloaded",
        "hust_data.zip",
    ),
)

CALCE_LINKS = (
    ("https://web.calce.umd.edu/batteries/data/CS2_33.zip", "CS2_33.zip"),
    ("https://web.calce.umd.edu/batteries/data/CS2_34.zip", "CS2_34.zip"),
    ("https://web.calce.umd.edu/batteries/data/CS2_35.zip", "CS2_35.zip"),
    ("https://web.calce.umd.edu/batteries/data/CS2_36.zip", "CS2_36.zip"),
    ("https://web.calce.umd.edu/batteries/data/CS2_37.zip", "CS2_37.zip"),
    ("https://web.calce.umd.edu/batteries/data/CS2_38.zip", "CS2_38.zip"),
    ("https://web.calce.umd.edu/batteries/data/CX2_16.zip", "CX2_16.zip"),
    ("https://web.calce.umd.edu/batteries/data/CX2_33.zip", "CX2_33.zip"),
    ("https://web.calce.umd.edu/batteries/data/CX2_35.zip", "CX2_35.zip"),
    ("https://web.calce.umd.edu/batteries/data/CX2_34.zip", "CX2_34.zip"),
    ("https://web.calce.umd.edu/batteries/data/CX2_36.zip", "CX2_36.zip"),
    ("https://web.calce.umd.edu/batteries/data/CX2_37.zip", "CX2_37.zip"),
    ("https://web.calce.umd.edu/batteries/data/CX2_38.zip", "CX2_38.zip"),
)


RWTH_LINKS = (
    ("https://publications.rwth-aachen.de/record/818642/files/Rawdata.zip", "raw.zip"),
)

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
