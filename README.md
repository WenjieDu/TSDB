<a href='https://github.com/WenjieDu/TSDB'><img src="https://raw.githubusercontent.com/WenjieDu/TSDB/main/docs/_static/figs/TSDB_logo.svg?sanitize=true" align='right' width='235'/></a>

# <p align='center'>Welcome to TSDB</p>
**<p align='center'>A Python Toolbox to Ease Loading Open-Source Time-Series Datasets</p>**

<p align='center'>
    <!-- Python version -->
    <img src='https://img.shields.io/badge/python-v3-yellowgreen'>
    <!-- PyPI version -->
    <img alt="PyPI" src="https://img.shields.io/pypi/v/tsdb?color=green&label=PyPI&logo=pypi">
    <!-- on Anaconda -->
    <a alt='on anaconda' href='https://anaconda.org/conda-forge/tsdb'>
        <img alt="on anaconda" src="https://img.shields.io/badge/Conda-TSDB-lightgreen?style=social&logo=anaconda" />
    </a>
    <!-- GitHub Testing -->
    <a alt='GitHub Testing' href='https://github.com/WenjieDu/TSDB/actions/workflows/testing.yml'> 
        <img src='https://github.com/WenjieDu/TSDB/actions/workflows/testing.yml/badge.svg'>
    </a>
    <!-- Coveralls report -->
    <a alt='Coveralls report' href='https://coveralls.io/github/WenjieDu/TSDB'> 
        <img src='https://img.shields.io/coverallsCoverage/github/WenjieDu/TSDB?branch=main&logo=coveralls'>
    </a>
    <!-- PyPI download number -->
    <a alt='PyPI download number' href='https://pypi.org/project/tsdb'>
        <img src='https://static.pepy.tech/personalized-badge/tsdb?period=total&units=international_system&left_color=gray&right_color=blue&left_text=Downloads'>
    </a>
    <!-- Code of Conduct -->
    <a alt='CODE_OF_CONDUCT' href='CODE_OF_CONDUCT.md'> 
        <img src='https://img.shields.io/badge/Contributor%20Covenant-v2.1-4baaaa.svg'>
    </a>
</p>

> 📣 TSDB now supports a total of 1️⃣1️⃣9️⃣ time-series datasets ‼️

<a href='https://github.com/WenjieDu/PyPOTS'><img src='https://raw.githubusercontent.com/WenjieDu/PyPOTS/main/docs/_static/figs/PyPOTS_logo.svg?sanitize=true' width='160' align='left' /></a>
TSDB is a part of [PyPOTS project](https://github.com/WenjieDu/PyPOTS) (a Python toolbox for data mining on Partially-Observed Time Series), and was separated from PyPOTS for decoupling datasets from learning algorithms.

TSDB is created to help researchers and engineers get rid of data collecting and downloading, and focus back on data processing details. TSDB provides all-in-one-stop convenience for downloading and loading open-source time-series datasets (available datasets listed [below](https://github.com/WenjieDu/TSDB#-list-of-available-datasets)).

❗️Please note that due to people have very different requirements for data processing, data-loading functions in TSDB only contain the most general steps (e.g. removing invalid samples) and won't process the data (not even normalize it). So, no worries, TSDB won't affect your data preprocessing. If you only want the raw datasets, TSDB can help you download and save raw datasets as well (take a look at [Usage Examples](https://github.com/WenjieDu/TSDB#-usage-example) below).

🤝 If you need TSDB to integrate an open-source dataset or want to add it into TSDB yourself, please feel free to request for it by creating an issue or make a PR to merge your code.


## ❖ Usage Examples
TSDB now is available on <a alt='Anaconda' href='https://anaconda.org/conda-forge/tsdb'><img align='center' src='https://img.shields.io/badge/Anaconda--lightgreen?style=social&logo=anaconda'></a>❗️ 

Install it with `conda install tsdb`, you may need to specify the channel with option `-c conda-forge`

or install from PyPI:
> pip install tsdb

or install from source code:
> pip install `https://github.com/WenjieDu/TSDB/archive/main.zip`

```python
import tsdb

tsdb.list_available_datasets()  # list all available datasets in TSDB
data = tsdb.load_dataset('physionet_2012')  # select the dataset you need and load it, TSDB will download, extract, and process it automatically
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
| [Vessel AIS data](datasets/AIS)                                       | Imputation, Forecasting, Classification |
| [Beijing Multi-Site Air-Quality](datasets/BeijingMultiSiteAirQuality) | Forecasting, Imputation                 |
| [Electricity Load Diagrams](datasets/ElectricityLoadDiagrams)         | Forecasting, Imputation                 |
| [UCR & UEA Datasets](datasets/UCR_UEA_Datasets) (all 115 datasets)    | Classification                          |


## ❖ Citing TSDB
The paper introducing PyPOTS project is available on arXiv at [this URL](https://arxiv.org/abs/2305.18811),
and we are pursuing to publish it in prestigious academic venues, e.g. JMLR (track for
[Machine Learning Open Source Software](https://www.jmlr.org/mloss/)). If you use TSDB in your work,
please cite PyPOTS project as below and 🌟star this repository to make others notice this library. 🤗 Thank you!

``` bibtex
@article{du2023PyPOTS,
title={{PyPOTS: A Python Toolbox for Data Mining on Partially-Observed Time Series}},
author={Wenjie Du},
year={2023},
eprint={2305.18811},
archivePrefix={arXiv},
primaryClass={cs.LG},
url={https://arxiv.org/abs/2305.18811},
doi={10.48550/arXiv.2305.18811},
}
```

or

> Wenjie Du. (2023).
> PyPOTS: A Python Toolbox for Data Mining on Partially-Observed Time Series.
> arXiv, abs/2305.18811. https://doi.org/10.48550/arXiv.2305.18811


<details>
<summary>🏠 Visits</summary>
<img align='left' src='https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FWenjieDu%2FTime_Series_Database&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=Visits+since+April+2022&edge_flat=false'>
</details>
