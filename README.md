<a href='https://github.com/WenjieDu/TSDB'><img src="https://pypots.com/figs/pypots_logos/TSDB/logo_FFBG.svg" align='right' width='200'/></a>

<h3 align="center">Welcome to TSDB</h3>

*<p align='center'>load 173 public time-series datasets with a single line of code ;-)</p>*

<p align='center'>
    <a href='https://github.com/WenjieDu/TSDB'>
        <img alt='Python version' src='https://img.shields.io/badge/python-v3-E97040?logo=python&logoColor=white'>
    </a>
    <a href="https://github.com/WenjieDu/TSDB/releases">
        <img alt="the latest release version" src="https://img.shields.io/github/v/release/wenjiedu/tsdb?color=EE781F&include_prereleases&label=Release&logo=github&logoColor=white">
    </a>
    <a href="https://github.com/WenjieDu/TSDB/blob/main/LICENSE">
        <img alt="BSD-3 license" src="https://img.shields.io/badge/License-BSD--3-E9BB41?logo=opensourceinitiative&logoColor=white">
    </a>
    <a href="https://github.com/WenjieDu/PyPOTS/blob/main/README.md#-community">
        <img alt="Community" src="https://img.shields.io/badge/join_us-community!-C8A062">
    </a>
    <a href="https://github.com/WenjieDu/TSDB/graphs/contributors">
        <img alt="GitHub contributors" src="https://img.shields.io/github/contributors/wenjiedu/tsdb?color=D8E699&label=Contributors&logo=GitHub">
    </a>
    <a href="https://star-history.com/#wenjiedu/tsdb">
        <img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/wenjiedu/tsdb?logo=None&color=6BB392&label=%E2%98%85%20Stars">
    </a>
    <a href="https://github.com/WenjieDu/TSDB/network/members">
        <img alt="GitHub Repo forks" src="https://img.shields.io/github/forks/wenjiedu/tsdb?logo=forgejo&logoColor=black&label=Forks">
    </a>
    <a href="https://sonarcloud.io/component_measures?id=WenjieDu_TSDB&metric=sqale_rating&view=list">
        <img alt="maintainability" src="https://sonarcloud.io/api/project_badges/measure?project=WenjieDu_TSDB&metric=sqale_rating">
    </a>
    <a href='https://coveralls.io/github/WenjieDu/TSDB'>
        <img alt='Coveralls report' src='https://img.shields.io/coverallsCoverage/github/WenjieDu/TSDB?branch=main&logo=coveralls&color=75C1C4&label=Coverage'>
    </a>
    <a  href='https://github.com/WenjieDu/TSDB/actions/workflows/testing_ci.yml'>
        <img alt='GitHub Testing' src='https://img.shields.io/github/actions/workflow/status/wenjiedu/tsdb/testing_ci.yml?logo=github&color=C8D8E1&label=CI'>
    </a>
    <a href="https://arxiv.org/abs/2305.18811">
        <img alt="arXiv DOI" src="https://img.shields.io/badge/DOI-10.48550/arXiv.2305.18811-F8F7F0">
    </a>
    <a href="https://anaconda.org/conda-forge/tsdb">
        <img alt="Conda downloads" src="https://pypots.com/figs/downloads_badges/conda_tsdb_downloads.svg">
    </a>
    <a href="https://pepy.tech/project/tsdb">
        <img alt="PyPI downloads" src="https://pypots.com/figs/downloads_badges/pypi_tsdb_downloads.svg">
    </a>
</p>

<a href='https://github.com/WenjieDu/PyPOTS'><img src='https://pypots.com/figs/pypots_logos/PyPOTS/logo_FFBG.svg' width='160' align='left' /></a>
TSDB is a part of
<a href="https://github.com/WenjieDu/PyPOTS">
PyPOTS <img align="center" src="https://img.shields.io/github/stars/WenjieDu/PyPOTS?style=social">
</a>
(a Python toolbox for data mining on Partially-Observed Time Series), and was separated from PyPOTS for decoupling datasets from learning algorithms.

TSDB is created to help researchers and engineers get rid of data collecting and downloading, and focus back on data processing details. TSDB provides all-in-one-stop convenience for downloading and loading open-source time-series datasets (available datasets listed [below](https://github.com/WenjieDu/TSDB#-list-of-available-datasets)).

❗️Please note that due to people have very different requirements for data processing, data-loading functions in TSDB only contain the most general steps (e.g. removing invalid samples) and won't process the data (not even normalize it). So, no worries, TSDB won't affect your data preprocessing. If you only want the raw datasets, TSDB can help you download and save raw datasets as well (take a look at [Usage Examples](https://github.com/WenjieDu/TSDB#-usage-examples) below).

🤝 If you need TSDB to integrate an open-source dataset or want to add it into TSDB yourself, please feel free to request for it by creating an issue or make a PR to merge your code.

🤗 **Please** star this repo to help others notice TSDB if you think it is a useful toolkit.
**Please** properly [cite TSDB and PyPOTS](https://github.com/WenjieDu/TSDB#-citing-tsdbpypots) in your publications
if it helps with your research. This really means a lot to our open-source research. Thank you!


## ❖ Usage Examples
> [!IMPORTANT]
> TSDB is available on both <a alt='PyPI' href='https://pypi.python.org/pypi/tsdb'><img align='center' src='https://img.shields.io/badge/PyPI--lightgreen?style=social&logo=pypi'></a>
> and <a alt='Anaconda' href='https://anaconda.org/conda-forge/tsdb'><img align='center' src='https://img.shields.io/badge/Anaconda--lightgreen?style=social&logo=anaconda'></a>❗️
>
> Install via pip:
> > pip install tsdb
>
> or install from source code:
> > pip install `https://github.com/WenjieDu/TSDB/archive/main.zip`
>
> or install via conda:
> > conda install tsdb -c conda-forge


```python
import tsdb

# list all available datasets in TSDB
tsdb.list()
# ['physionet_2012',
#  'physionet_2019',
#  'electricity_load_diagrams',
#  'beijing_multisite_air_quality',
#  'italy_air_quality',
#  'vessel_ais',
#  'electricity_transformer_temperature',
#  'pems_traffic',
#  'solar_alabama',
#  'ucr_uea_ACSF1',
#  'ucr_uea_Adiac',
#  ...

# select the dataset you need and load it, TSDB will download, extract, and process it automatically
data = tsdb.load('physionet_2012')
# if you need the raw data, use download_and_extract()
tsdb.download_and_extract('physionet_2012', './save_it_here')
# datasets you once loaded are cached, and you can check them with list_cached_data()
tsdb.list_cache()
# you can delete only one specific dataset's pickled cache
tsdb.delete_cache(dataset_name='physionet_2012', only_pickle=True)
# you can delete only one specific dataset raw files and preserve others
tsdb.delete_cache(dataset_name='physionet_2012')
# or you can delete all cache with delete_cached_data() to free disk space
tsdb.delete_cache()

# The default cache directory is ~/.pypots/tsdb under the user's home directory.
# To avoid taking up too much space if downloading many datasets ,
# TSDB cache directory can be migrated to an external disk
tsdb.migrate_cache("/mnt/external_disk/TSDB_cache")
```

That's all. Simple and efficient. Enjoy it! 😃

### Python support and optional dependencies

TSDB v1.0 requires Python 3.10 or newer. Python 3.8 and 3.9 users can continue
using TSDB 0.8. For TSQA, install the optional dependencies with
`pip install "tsdb[tsqa]"`. Other datasets retain their existing dependencies.

Importing TSDB or its shared logger, and listing dataset names, do not initialize
the ecosystem configuration or migrate caches. The configuration is initialized
when the configuration or data access modules are first used.

### Reliable downloads and raw data

`tsdb.download_and_extract(name, destination)` downloads all required raw files
before publishing a new destination directory. Existing destinations are not
overwritten. For TSQA it downloads the actual Hugging Face dataset files; install
`tsdb[tsqa]` first. To download a CSV/TXT file or supported archive from a URL,
use `tsdb.download_url(url, destination)`. ZIP, TAR (including gzip, bzip2 and xz
compression), and single CSV/TXT gzip files are supported. The destination must
not exist. Unsafe archive paths, links, special files and conflicting file
members are rejected. `tsdb.load(name, use_cache=False)` retains the old cache
until the replacement has been downloaded, parsed and cached successfully.
Parsed caches are trusted local pickle files: never install or load an untrusted
pickle. Unreadable parsed caches are rebuilt from local raw data when possible.
Cache operations sharing one ecosystem configuration are serialized by an OS
lock. External writers and distinct ecosystem homes sharing a cache are not
covered. Cache migration requires a new or empty non-overlapping destination;
configuration is switched only after copying succeeds. A failed configuration
write retains the original and the complete destination copy for recovery.
Invalid dataset names raise ValueError. Pickle utility failures raise CacheError
instead of returning None. Cache deletion preserves unrelated files and backups.

### Unicode configuration and logs

TSDB stores the shared ecosystem configuration (`~/.pypots/config.ini`) and new
file logs in UTF-8 on all platforms. Console logs retain Unicode and emoji when
the output stream supports them, and escape unsupported characters otherwise.
TSDB does not change your application's standard streams or global encoding settings.

Existing valid UTF-8 configurations (including ASCII and UTF-8 with BOM) are
read unchanged. If a configuration from an older release is not valid UTF-8,
set `TSDB_LEGACY_CONFIG_ENCODING` to its **known original encoding** (e.g.
`cp1252` or `gbk`) for one `from tsdb.utils import config`, then unset it. TSDB validates the
configuration, saves its original bytes in a uniquely named `config.ini.*.bak`
file beside it, and atomically converts the original to UTF-8. Do not guess the
encoding: some legacy byte sequences are also valid UTF-8 and cannot be reliably
distinguished. If you know such a file was written in a different encoding,
back it up and explicitly reopen/convert it in a text editor before importing TSDB.
An empty or section-only `[path]` file left by interrupted initialization is
backed up and recovered; other invalid configurations are not silently reset.

Appending to an existing non-UTF-8 log is refused to avoid mixing encodings.
Choose a new log filename, or back up and convert the old log to UTF-8 before
appending. An explicitly requested overwrite (`mode="w"`) still replaces the log.


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
| [TSQA](dataset_profiles/tsqa)                                                                     | LLM training                            |
| [UCR & UEA Datasets](dataset_profiles/ucr_uea_datasets) (all 163 datasets)                        | Classification                          |


## ❖ Citing TSDB/PyPOTS
The paper introducing PyPOTS is available [on arXiv](https://arxiv.org/abs/2305.18811),
A short version of it is accepted by the 9th SIGKDD international workshop on Mining and Learning from Time Series ([MiLeTS'23](https://kdd-milets.github.io/milets2023/))).
**Additionally**, PyPOTS has been included as a [PyTorch Ecosystem](https://pytorch.org/ecosystem/) project.
We are pursuing to publish it in prestigious academic venues, e.g. JMLR (track for
[Machine Learning Open Source Software](https://www.jmlr.org/mloss/)). If you use PyPOTS in your work,
please cite it as below and 🌟star this repository to make others notice this library. 🤗

There are scientific research projects using PyPOTS and referencing in their papers.
Here is [an incomplete list of them](https://scholar.google.com/scholar?as_ylo=2022&q=%E2%80%9CPyPOTS%E2%80%9D&hl=en).

<p align="center">
<a href="https://github.com/WenjieDu/PyPOTS">
    <img src="https://pypots.com/figs/pypots_logos/Ecosystem/PyPOTS_Ecosystem_Pipeline.png" width="95%"/>
</a>
</p>

```bibtex
@article{du2023pypots,
title = {{PyPOTS: A Python Toolkit for Data Mining on Partially-Observed Time Series}},
author = {Wenjie Du},
journal = {SIGKDD MiLeTS Workshop},
year = {2023},
}
```

```bibtex
@article{du2025pypots,
title = {{PyPOTS v1: A Python Toolkit for Machine Learning on Partially-Observed Time Series}},
author = {Wenjie Du, Yiyuan Yang, Linglong Qian, Jun Wang, and Qingsong Wen},
year = {2025},
}
```

### Dataset return contracts

UCR/UEA TXT data retains `(samples, timepoints, features)`; ARFF data retains
its historical `(samples, channels, timepoints)` layout. This difference is
intentional compatibility preservation in v1.0; do not assume a unified axis
order across formats. ARFF takes precedence when both complete pairs exist.
Single-row TXT inputs are supported; malformed/empty pairs raise errors.
PhysioNet and Beijing raw files are enumerated in sorted order; existing local
parsed caches retain their earlier order until explicitly rebuilt. AIS elapsed
time is computed in seconds independent of pandas timestamp resolution.

### Coverage and release validation

PR CI measures deterministic offline coverage. Daily Testing additionally runs
`python scripts/coverage_suite.py --output /path/to/new/report-directory` with
pytest-cov and the TSQA extra installed. The runner executes offline and live
suites separately on the same checkout, combines their coverage databases,
and records the exact revision, each exit status, and line counts. External
source errors fail the job; partial coverage never implies a passing suite.
The designated Coveralls upload remains offline-only for a comparable trend.
