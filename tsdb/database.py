"""
List available datasets and their official download links.
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: BSD-3-Clause

from dataclasses import asdict, dataclass

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
        "https://physionet-open.s3.amazonaws.com/challenge-2019/1.0.0/training/training_setA/",
        "https://physionet-open.s3.amazonaws.com/challenge-2019/1.0.0/training/training_setB/",
    ],
    #
    # https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/electricity_load_diagrams
    "electricity_load_diagrams": "https://archive.ics.uci.edu/ml/machine-learning-databases/00321/LD2011_2014.txt.zip",
    #
    # https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/beijing_multisite_air_quality
    "beijing_multisite_air_quality": "https://archive.ics.uci.edu/ml/machine-learning-databases/00501/"
    "PRSA2017_Data_20130301-20170228.zip",
    # https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/italy_air_quality
    "italy_air_quality": "https://archive.ics.uci.edu/static/public/360/air+quality.zip",
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
    # https://pems.dot.ca.gov, https://github.com/laiguokun/multivariate-time-series-data
    "pems_traffic": "https://raw.githubusercontent.com/laiguokun/multivariate-time-series-data/master/"
    "traffic/traffic.txt.gz",
    # https://www.nrel.gov/grid/solar-power-data.html, https://github.com/laiguokun/multivariate-time-series-data
    "solar_alabama": "https://raw.githubusercontent.com/laiguokun/multivariate-time-series-data/master/"
    "solar-energy/solar_AL.txt.gz",
    # https://huggingface.co/datasets/Time-MQA/TSQA
    # https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/tsqa
    "tsqa": "hf://Time-MQA/TSQA",
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
    UCR_UEA_DATASETS["ucr_uea_" + i] = f"https://www.timeseriesclassification.com/aeon-toolkit/{i}.zip"

DATABASE = {**_DATABASE, **UCR_UEA_DATASETS}
AVAILABLE_DATASETS = list(DATABASE.keys())


@dataclass(frozen=True)
class DatasetSpec:
    """Lightweight descriptor; no loader or download dependency imports."""

    name: str
    sources: tuple[str, ...]
    loader: str
    download_strategy: str = "http"
    profile: str = ""
    loader_arg: str | None = None
    required_files: tuple[str, ...] = ()
    required_directories: tuple[tuple[str, str], ...] = ()
    optional_dependencies: tuple[str, ...] = ()
    revision: str | None = None
    license: str | None = None
    tasks: tuple[str, ...] | None = None


# Keep source URLs and legacy DATABASE/list ordering unchanged. A family defines
# dispatch and required layout together; UCR/UEA uses one family for all names.
_FAMILIES = {
    "physionet_2012": {
        "loader": "load_physionet2012",
        "required_files": ("Outcomes-a.txt", "Outcomes-b.txt", "Outcomes-c.txt"),
        "required_directories": (("set-a", "*.txt"), ("set-b", "*.txt"), ("set-c", "*.txt")),
        "revision": "1.0.0",
    },
    "physionet_2019": {"loader": "load_physionet2019", "download_strategy": "physionet_2019", "revision": "1.0.0"},
    "electricity_load_diagrams": {"loader": "load_electricity", "required_files": ("LD2011_2014.txt",)},
    "electricity_transformer_temperature": {
        "loader": "load_ett",
        "required_files": ("ETTm1.csv", "ETTm2.csv", "ETTh1.csv", "ETTh2.csv"),
    },
    "beijing_multisite_air_quality": {
        "loader": "load_beijing_air_quality",
        "required_directories": (("PRSA_Data_20130301-20170228", "*.csv"),),
    },
    "italy_air_quality": {"loader": "load_italy_air_quality", "required_files": ("AirQualityUCI.csv",)},
    "vessel_ais": {"loader": "load_ais", "required_directories": (("parquets", "*"),)},
    "pems_traffic": {"loader": "load_pems_traffic", "required_files": ("traffic.txt",)},
    "solar_alabama": {"loader": "load_solar_alabama", "required_files": ("solar_AL.txt",)},
    "tsqa": {"loader": "load_tsqa", "download_strategy": "huggingface", "optional_dependencies": ("huggingface_hub",)},
}


def dataset_spec(name: str) -> DatasetSpec:
    if name not in DATABASE:
        raise ValueError(f"{name!r} is not available in TSDB. See tsdb.list().")
    value = DATABASE[name]
    sources = (value,) if isinstance(value, str) else tuple(value)
    if name.startswith("ucr_uea_"):
        return DatasetSpec(
            name, sources, "load_ucr_uea_dataset", profile="ucr_uea_datasets", loader_arg=name.removeprefix("ucr_uea_")
        )
    return DatasetSpec(name, sources, profile=name, **_FAMILIES[name])


def info(name: str) -> dict:
    """Return dataset metadata without downloading, parsing or touching caches.

    Unknown source license, task or revision metadata is represented by None.
    The dataset profile links to the maintained source/citation information.
    """
    spec = dataset_spec(name)
    result = asdict(spec)
    result["profile_url"] = f"https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/{spec.profile}"
    return result
