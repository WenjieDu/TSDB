# <p align='center'> Welcome to Time-Series Database (TSDB) </p>
#### <p align='center'> A Python Toolbox for Easily Loading Open-Source Time-Series Datasets </p>
<p align='center'>
	<!-- PyPI download number -->
    <a alt='PyPI download number' href='https://pypi.org/project/tsdb'>
        <img src='https://static.pepy.tech/personalized-badge/tsdb?period=total&units=international_system&left_color=gray&right_color=blue&left_text=Total%20Downloads'>
    </a>
	<!-- Hits number -->
    <img src='https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FWenjieDu%2FTime_Series_Database&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false'>

</p>


## ❖ Usage Example
Install from PyPI: 
> pip install tsdb

or install from source code: 
> pip install `https://github.com/WenjieDu/Time_Series_Database/archive/master.zip`


```python
import tsdb
tsdb.list_available_datasets()  # list all available datasets in TSDB
data = tsdb.load_specific_dataset('physionet_2012')  # select the dataset you need and load it, TSDB will download, extract, and process it automatically
tsdb.download_and_extract('physionet_2012', 'save it here')  # if you only need the raw data, use download_and_extract() 
tsdb.list_cached_data()  # datasets you loaded are cached. You can check them with list_cached_data().
tsdb.delete_cached_data()  # and you can delete all cache with delete_cached_data()
```

That's all. Simple and efficient. Enjoy it! 😃

## ❖ List of Available Datasets

| Name                                                                  | Main Tasks                              |
|-----------------------------------------------------------------------|-----------------------------------------|
| [PhysioNet Challenge 2012](datasets/PhysioNet-2012)                   | Classification, Forecasting, Imputation |
| [Beijing Multi-Site Air-Quality](datasets/BeijingMultiSiteAirQuality) | Forecasting, Imputation                 |
| [Electricity Load Diagrams](datasets/ElectricityLoadDiagrams)         | Forecasting, Imputation                 |
| [All UCR & UEA Datasets](datasets/UCR_UEA_Datasets)                   | Classification                          |
