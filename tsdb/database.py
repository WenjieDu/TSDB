"""
List available datasets and their official download links.
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: GLP-v3

_DATABASE = {
    # https://github.com/WenjieDu/Time_Series_Database/tree/main/datasets/PhysioNet-2012
    'physionet_2012': [
        'https://www.physionet.org/files/challenge-2012/1.0.0/set-a.tar.gz',
        'https://www.physionet.org/files/challenge-2012/1.0.0/set-b.tar.gz',
        'https://www.physionet.org/files/challenge-2012/1.0.0/set-c.tar.gz',
        'https://www.physionet.org/files/challenge-2012/1.0.0/Outcomes-a.txt',
        'https://www.physionet.org/files/challenge-2012/1.0.0/Outcomes-b.txt',
        'https://www.physionet.org/files/challenge-2012/1.0.0/Outcomes-c.txt',
    ],

    # https://github.com/WenjieDu/Time_Series_Database/tree/main/datasets/PhysioNet-2019
    'physionet_2019': [
        'https://archive.physionet.org/users/shared/challenge-2019/training_setA.zip',
        'https://archive.physionet.org/users/shared/challenge-2019/training_setB.zip',
    ],

    # https://github.com/WenjieDu/Time_Series_Database/tree/main/datasets/ElectricityLoadDiagrams
    'electricity_load_diagrams':
        'https://archive.ics.uci.edu/ml/machine-learning-databases/00321/LD2011_2014.txt.zip',

    # https://github.com/WenjieDu/Time_Series_Database/tree/main/datasets/BeijingMultiSiteAirQuality
    'beijing_multisite_air_quality':
        'https://archive.ics.uci.edu/ml/machine-learning-databases/00501/PRSA2017_Data_20130301-20170228.zip',
}

_UCR_UEA_datasets = [
    'Adiac',
    'ArrowHead',
    'Beef',
    'BeetleFly',
    'BirdChicken',
    'Car',
    'CBF',
    'ChlorineConcentration',
    'CinCECGTorso',
    'Coffee',
    'Computers',
    'CricketX',
    'CricketY',
    'CricketZ',
    'DiatomSizeReduction',
    'DistalPhalanxOutlineCorrect',
    'DistalPhalanxOutlineAgeGroup',
    'DistalPhalanxTW',
    'Earthquakes',
    'ECG200',
    'ECG5000',
    'ECGFiveDays',
    'ElectricDevices',
    'FaceAll',
    'FaceFour',
    'FacesUCR',
    'FiftyWords',
    'Fish',
    'FordA',
    'FordB',
    'GunPoint',
    'Ham',
    'HandOutlines',
    'Haptics',
    'Herring',
    'InlineSkate',
    'InsectWingbeatSound',
    'ItalyPowerDemand',
    'LargeKitchenAppliances',
    'Lightning2',
    'Lightning7',
    'Mallat',
    'Meat',
    'MedicalImages',
    'MiddlePhalanxOutlineCorrect',
    'MiddlePhalanxOutlineAgeGroup',
    'MiddlePhalanxTW',
    'MoteStrain',
    'NonInvasiveFatalECGThorax1',
    'NonInvasiveFatalECGThorax2',
    'OliveOil',
    'OSULeaf',
    'PhalangesOutlinesCorrect',
    'Phoneme',
    'Plane',
    'ProximalPhalanxOutlineCorrect',
    'ProximalPhalanxOutlineAgeGroup',
    'ProximalPhalanxTW',
    'RefrigerationDevices',
    'ScreenType',
    'ShapeletSim',
    'ShapesAll',
    'SmallKitchenAppliances',
    'SonyAIBORobotSurface1',
    'SonyAIBORobotSurface2',
    'StarLightCurves',
    'Strawberry',
    'SwedishLeaf',
    'Symbols',
    'SyntheticControl',
    'ToeSegmentation1',
    'ToeSegmentation2',
    'Trace',
    'TwoLeadECG',
    'TwoPatterns',
    'UWaveGestureLibraryX',
    'UWaveGestureLibraryY',
    'UWaveGestureLibraryZ',
    'UWaveGestureLibraryAll',
    'Wafer',
    'Wine',
    'WordSynonyms',
    'Worms',
    'WormsTwoClass',
    'Yoga',
    'ArticularyWordRecognition',
    'AtrialFibrillation',
    'BasicMotions',
    'CharacterTrajectories',
    'Cricket',
    'DuckDuckGeese',
    'EigenWorms',
    'Epilepsy',
    'EthanolConcentration',
    'ERing',
    'FaceDetection',
    'FingerMovements',
    'HandMovementDirection',
    'Handwriting',
    'Heartbeat',
    'InsectWingbeat',
    'JapaneseVowels',
    'Libras',
    'LSST',
    'MotorImagery',
    'NATOPS',
    'PenDigits',
    'PEMS-SF',
    'Phoneme',
    'RacketSports',
    'SelfRegulationSCP1',
    'SelfRegulationSCP2',
    'SpokenArabicDigits',
    'StandWalkJump',
    'UWaveGestureLibrary'
]

UCR_UEA_datasets = {}
for i in _UCR_UEA_datasets:
    UCR_UEA_datasets['UCR_UEA_' + i] = f'https://www.timeseriesclassification.com/Downloads/{i}.zip'

DATABASE = {**_DATABASE, **UCR_UEA_datasets}
AVAILABLE_DATASETS = list(DATABASE.keys())


def list_database():
    """ List the database.

    Returns
    -------
    DATABASE : dict
        A dict contains all datasets' names and download links.

    """
    return DATABASE


def list_available_datasets():
    """ List all available datasets.

    Returns
    -------
    AVAILABLE_DATASETS : list
        A list contains all datasets' names.

    """
    return AVAILABLE_DATASETS
