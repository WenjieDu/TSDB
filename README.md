# TSDB <a href="https://github.com/WenjieDu/TSDB"><img src="https://pypots.com/figs/pypots_logos/TSDB/logo_FFBG.svg" width="200" align="right" alt="TSDB logo"></a>

> A Python Toolbox for Loading Public Time Series Datasets

<p>
    <a href="https://tsdb.readthedocs.io/en/latest/install.html">
       <img alt="Python version" src="https://img.shields.io/badge/Python-v3.10+-F8C6B5?logo=python&logoColor=white">
    </a>
    <a href="https://github.com/WenjieDu/TSDB/releases">
        <img alt="the latest release version" src="https://img.shields.io/github/v/release/wenjiedu/tsdb?color=EE781F&include_prereleases&label=Release&logo=github&logoColor=white">
    </a>
    <a href="https://tsdb.readthedocs.io/en/latest/">
        <img alt="Docs building" src="https://img.shields.io/readthedocs/tsdb?logo=readthedocs&label=Docs&logoColor=white&color=395260">
    </a>
    <a href="https://pepy.tech/project/tsdb">
        <img alt="PyPI downloads" src="https://pypots.com/figs/downloads_badges/pypi_tsdb_downloads.svg">
    </a>
    <a href="https://anaconda.org/conda-forge/tsdb">
        <img alt="Conda downloads" src="https://pypots.com/figs/downloads_badges/conda_tsdb_downloads.svg">
    </a>
    <a href="https://github.com/WenjieDu/TSDB/blob/main/LICENSE">
        <img alt="BSD-3 license" src="https://img.shields.io/badge/License-BSD--3-E9BB41?logo=opensourceinitiative&logoColor=white">
    </a>
    <a href="https://github.com/WenjieDu/PyPOTS#-community">
        <img alt="Community" src="https://img.shields.io/badge/join_us-community!-C8A062">
    </a>
    <a href="https://star-history.com/#wenjiedu/tsdb">
        <img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/wenjiedu/tsdb?logo=None&color=6BB392&label=%E2%98%85%20Stars">
    </a>
    <a href="https://github.com/WenjieDu/TSDB/network/members">
        <img alt="GitHub Repo forks" src="https://img.shields.io/github/forks/wenjiedu/tsdb?logo=forgejo&logoColor=black&label=Forks">
    </a>
    <a href="https://github.com/WenjieDu/TSDB/graphs/contributors">
        <img alt="GitHub contributors" src="https://img.shields.io/github/contributors/wenjiedu/tsdb?color=D8E699&label=Contributors&logo=GitHub">
    </a>
    <a href="https://github.com/WenjieDu/TSDB/actions/workflows/testing_ci.yml">
        <img alt="GitHub Testing" src="https://img.shields.io/github/actions/workflow/status/wenjiedu/tsdb/testing_ci.yml?logo=circleci&color=C8D8E1&label=CI">
    </a>
    <a href="https://coveralls.io/github/WenjieDu/TSDB?branch=main">
        <img alt="Coveralls coverage" src="https://img.shields.io/coverallsCoverage/github/WenjieDu/TSDB?branch=main&logo=coveralls&color=75C1C4&label=Coverage">
    </a>
    <a href="https://sonarcloud.io/component_measures?id=WenjieDu_TSDB&metric=sqale_rating&view=list">
        <img alt="maintainability" src="https://sonarcloud.io/api/project_badges/measure?project=WenjieDu_TSDB&metric=sqale_rating">
    </a>
    <a href="https://github.com/astral-sh/ruff">
        <img alt="Code Style" src="https://img.shields.io/badge/Code_Style-Ruff-D7FF64?logo=ruff">
    </a>
    <a href="https://github.com/WenjieDu/TSDB?tab=coc-ov-file">
        <img alt="Code of Conduct" src="https://img.shields.io/badge/Contributor_Covenant-2.1-4baaaa">
    </a>
    <a href="https://arxiv.org/abs/2305.18811">
        <img alt="arXiv DOI" src="https://img.shields.io/badge/DOI-10.48550/arXiv.2305.18811-F8F7F0">
    </a>
</p>

TSDB (Time Series Data Beans) is an open-source Python toolbox that makes **173 public time series datasets available through unified APIs** for machine learning research and engineering. It is the dataset access layer of the [PyPOTS ecosystem](https://pypots.com/ecosystem/), separating data acquisition from learning algorithms.

TSDB handles dataset discovery, downloading, extraction, loading, and local caching so researchers can focus on data analysis. Loaders perform dataset-specific basic preparation, not task-specific normalization or missing-value imputation. For experiments requiring original files, TSDB also supports raw downloads.

[Website](https://pypots.com) · [Documentation](https://tsdb.readthedocs.io/en/latest/) · [Tutorials](https://github.com/WenjieDu/BrewPOTS) · [Community](https://github.com/WenjieDu/PyPOTS#-community)

[**Key Features**](#-key-features) · [**Installation**](#-installation) · [**Usage**](#-usage) · [**List of Available Datasets**](#-list-of-available-datasets) · [**PyPOTS Ecosystem**](#-pypots-ecosystem) · [**Citing TSDB/PyPOTS**](#-citing-tsdbpypots) · [**Contribution**](#-contribution)

## ❖ Key Features

- **Rich dataset collection:** 173 datasets from healthcare, energy, weather, traffic, and other domains, including UCR/UEA classification datasets and TSQA.
- **Unified APIs:** Discover datasets, load them into Python, or download their original files through consistent interfaces.
- **Metadata discovery:** Inspect available source URLs, known revisions, loader information, and dataset profiles without downloading data.
- **Local caching:** Reuse downloaded files and parsed results, refresh datasets explicitly, or migrate caches to a different drive.
- **Reliable downloads:** Staged downloads, safe archive extraction, and recovery from incomplete operations.
- **Reproducible research:** Preserve dataset-specific return contracts and link to upstream sources and citations.

## ❖ Installation

TSDB v1.0 requires Python 3.10 or later and is available on [PyPI](https://pypi.org/project/tsdb/) and [Anaconda](https://anaconda.org/conda-forge/tsdb). See the [installation guide](https://tsdb.readthedocs.io/en/latest/install.html) for optional dependencies and compatibility.

Choose **one** of the following installation methods according to your environment.

**Option 1: pip (recommended)**

```bash
pip install tsdb
# To upgrade: pip install tsdb --upgrade
```

**Option 2: Conda**

```bash
conda install conda-forge::tsdb
# To upgrade: conda update conda-forge::tsdb
```

**Option 3: Latest source code on main (may include unreleased changes)**

```bash
pip install https://github.com/WenjieDu/TSDB/archive/main.zip
```

For the TSQA dataset, install the optional dependency with `pip install "tsdb[tsqa]"`.

## ❖ Usage

### Quick Start

```python
import tsdb

# Discover available datasets without downloading anything
print(tsdb.list())
print(tsdb.info("physionet_2012"))

# Download, extract, parse and cache a dataset automatically
# The first load requires network access.
data = tsdb.load("physionet_2012")

# Reuse the locally cached dataset
print(tsdb.list_cache())
```

### Download Raw Data

```python
# Choose a new destination directory
tsdb.download_and_extract("physionet_2012", "./physionet_2012_raw")
```

See the [usage guide](https://tsdb.readthedocs.io/en/latest/usage.html), [API reference](https://tsdb.readthedocs.io/en/latest/tsdb.html), and [migration guide](https://tsdb.readthedocs.io/en/latest/migration.html) for detailed examples, cache management, and compatibility notes.

## ❖ List of Available Datasets

| Name                                                                                              | Main Tasks                              |
|---------------------------------------------------------------------------------------------------|-----------------------------------------|
| [PhysioNet Challenge 2012](dataset_profiles/physionet_2012)                                       | Forecasting, Imputation, Classification |
| [PhysioNet Challenge 2019](dataset_profiles/physionet_2019)                                       | Forecasting, Imputation, Classification |
| [Beijing Multi-Site Air-Quality](dataset_profiles/beijing_multisite_air_quality)                  | Forecasting, Imputation                 |
| [Italy Air Quality](dataset_profiles/italy_air_quality)                                           | Forecasting, Imputation                 |
| [Electricity Load Diagrams](dataset_profiles/electricity_load_diagrams)                           | Forecasting, Imputation                 |
| [Electricity Transformer Temperature (ETT)](dataset_profiles/electricity_transformer_temperature) | Forecasting, Imputation                 |
| [Vessel AIS](dataset_profiles/vessel_ais)                                                         | Forecasting, Imputation, Classification |
| [PeMS Traffic](dataset_profiles/pems_traffic)                                                     | Forecasting, Imputation                 |
| [Solar Alabama](dataset_profiles/solar_alabama)                                                   | Forecasting, Imputation                 |
| [TSQA](dataset_profiles/tsqa)                                                                     | Time series question answering                            |
| [UCR & UEA Datasets](dataset_profiles/ucr_uea_datasets) (all 163 datasets)                        | Classification                          |

Use `tsdb.list()` for the complete list of identifiers. See the [dataset guide](https://tsdb.readthedocs.io/en/latest/datasets.html) for source and return-format details.

## ❖ PyPOTS Ecosystem

Time series datasets are our coffee beans. TSDB makes them accessible; [PyGrinder](https://github.com/WenjieDu/PyGrinder) simulates missingness, [BenchPOTS](https://github.com/WenjieDu/BenchPOTS) provides standardized preprocessing, [PyPOTS](https://github.com/WenjieDu/PyPOTS) provides unified time series modeling, and [BrewPOTS](https://github.com/WenjieDu/BrewPOTS) offers tutorials.

<p align="center">
<a href="https://pypots.com/ecosystem/">
    <img src="https://pypots.com/figs/pypots_logos/Ecosystem/PyPOTS_Ecosystem_Pipeline.png" width="95%" alt="PyPOTS ecosystem pipeline"/>
</a>
<br>
<b> ☕️ Welcome to the universe of PyPOTS. Enjoy it and have fun!</b>
</p>

## ❖ Citing TSDB/PyPOTS

If TSDB helps your research, please cite the original datasets using their linked profiles and the [PyPOTS toolkit paper](https://arxiv.org/abs/2305.18811v2).

```bibtex
@article{du2023pypots,
title = {{PyPOTS: A Python Toolkit for Data Mining on Partially-Observed Time Series}},
author = {Wenjie Du},
journal = {SIGKDD MiLeTS Workshop},
url = {https://arxiv.org/abs/2305.18811v1},
year = {2023},
}
```

```bibtex
@article{du2025pypots,
title = {{PyPOTS: A Python Toolkit for Machine Learning on Partially-Observed Time Series}},
author = {Wenjie Du and Yiyuan Yang and Linglong Qian and Jun Wang and Qingsong Wen},
journal = {arXiv preprint arXiv:2305.18811v2},
url = {https://arxiv.org/abs/2305.18811v2},
year = {2025},
}
```

## ❖ Contribution

We welcome new dataset integrations, bug fixes, documentation, and regression tests. Report reproducible problems or propose improvements through [GitHub Issues](https://github.com/WenjieDu/TSDB/issues). See the [maintainer guide](https://tsdb.readthedocs.io/en/latest/maintenance.html) for testing and release procedures.

Before submitting a pull request, enable pre-commit in your local clone and run `pre-commit run --all-files`. Please include upstream source and citation information for new datasets.
