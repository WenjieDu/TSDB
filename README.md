<img src="https://github.com/WenjieDu/Time_Series_Database/blob/f3a838e2d4a4640d32754e5729a8969269eaf9d0/docs/figs/TSDB%20logo.svg?sanitize=true" align='right' width='230'/>

# <p align='center'>Welcome to TSDB</p>
### <p align='center'>A Python Toolbox Helping Load Open-Source Time-Series Datasets</p>
<p align='center'>
	<!-- Python version -->
    <img src='https://img.shields.io/badge/python-v3-yellowgreen'>
    <!-- GitHub Testing -->
    <a alt='GitHub Testing' href='https://github.com/WenjieDu/TSDB/actions/workflows/testing.yml'> 
        <img src='https://github.com/WenjieDu/TSDB/actions/workflows/testing.yml/badge.svg'>
    </a>
	<!-- PyPI download number -->
    <a alt='PyPI download number' href='https://pypi.org/project/tsdb'>
        <img src='https://static.pepy.tech/personalized-badge/tsdb?period=total&units=international_system&left_color=gray&right_color=blue&left_text=Total%20Downloads'>
    </a>
	<!-- Visit number -->
    <img src='https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FWenjieDu%2FTime_Series_Database&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=Visits&edge_flat=false'>
</p>

Project TSDB is created to help researchers and engineers get rid of data collecting and downloading, and focus back on data processing details. TSDB provides all-in-one-stop convenience for downloading and loading open-source time-series datasets (available datasets listed [below](https://github.com/WenjieDu/TSDB#-list-of-available-datasets)). **Note that** due to people have very different requirements for data processing, data-loading functions in TSDB only contain the most general steps (e.g. removing invalid samples) and won't process the data (not even normalize it). So, no worries. If you only need raw datasets, TSDB allows you to download datasets only as well (take a look at [Usage Examples](https://github.com/WenjieDu/TSDB#-usage-example)).

## ❖ Usage Examples
Install from PyPI: 
> pip install tsdb

or install from source code: 
> pip install `https://github.com/WenjieDu/TSDB/archive/main.zip`

```python
import tsdb
tsdb.list_available_datasets()  # list all available datasets in TSDB
data = tsdb.load_specific_dataset('physionet_2012')  # select the dataset you need and load it, TSDB will download, extract, and process it automatically
tsdb.download_and_extract('physionet_2012', './save_it_here')  # if you need the raw data, use download_and_extract()
tsdb.list_cached_data()  # datasets you once loaded are cached, and you can check them with list_cached_data()
tsdb.delete_cached_data()  # you can delete all cache with delete_cached_data() to free disk space
tsdb.delete_cached_data(dataset_name='physionet_2012')  # or you can delete only one specific dataset and preserve others
```

That's all. Simple and efficient. Enjoy it! 😃

## ❖ List of Available Datasets

| Name                                                                  | Main Tasks                              |
|-----------------------------------------------------------------------|-----------------------------------------|
| [PhysioNet Challenge 2012](datasets/PhysioNet-2012)                   | Classification, Forecasting, Imputation |
| [PhysioNet Challenge 2019](datasets/PhysioNet-2019)                   | Classification, Imputation              |
| [Beijing Multi-Site Air-Quality](datasets/BeijingMultiSiteAirQuality) | Forecasting, Imputation                 |
| [Electricity Load Diagrams](datasets/ElectricityLoadDiagrams)         | Forecasting, Imputation                 |
| [All UCR & UEA Datasets](datasets/UCR_UEA_Datasets)                   | Classification                          |

## ❖ License
Please note that TSDB is open source under [license GPL-3.0](https://en.wikipedia.org/wiki/GNU_General_Public_License#Version_3).