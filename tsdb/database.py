"""

"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: GLP-v3

DATABASE = {
    # github.com/WenjieDu/Time_Series_Database/tree/main/datasets/PhysioNet-2012
    'physionet_2012': [
        'https://www.physionet.org/files/challenge-2012/1.0.0/set-a.tar.gz',
        'https://www.physionet.org/files/challenge-2012/1.0.0/set-b.tar.gz',
        'https://www.physionet.org/files/challenge-2012/1.0.0/set-c.tar.gz',
        'https://www.physionet.org/files/challenge-2012/1.0.0/Outcomes-a.txt',
        'https://www.physionet.org/files/challenge-2012/1.0.0/Outcomes-b.txt',
        'https://www.physionet.org/files/challenge-2012/1.0.0/Outcomes-c.txt',
    ],

    # github.com/WenjieDu/Time_Series_Database/tree/main/datasets/ElectricityLoadDiagrams
    'electricity_load_diagrams':
        'https://archive.ics.uci.edu/ml/machine-learning-databases/00321/LD2011_2014.txt.zip',

    # github.com/WenjieDu/Time_Series_Database/tree/main/datasets/BeijingMultiSiteAirQuality
    'beijing_multisite_air_quality':
        'https://archive.ics.uci.edu/ml/machine-learning-databases/00501/PRSA2017_Data_20130301-20170228.zip',

}

AVAILABLE_DATASETS = list(DATABASE.keys())
