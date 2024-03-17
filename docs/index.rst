.. PyPOTS documentation index page
   Created by Wenjie Du <wenjay.du@gmail.com>
   License: BSD-3-Clause

Welcome to TSDB documentation!
================================
.. image:: https://pypots.com/figs/pypots_logos/TSDB/logo_FFBG.svg
   :height: 180
   :align: right
   :target: https://github.com/WenjieDu/TSDB
   :alt: TSDB logo

**A Python Toolbox to Ease Loading Public Time-Series Datasets**

.. image:: https://img.shields.io/badge/python-v3-E97040?logo=python&logoColor=white
   :alt: Python version

.. image:: https://img.shields.io/github/v/release/wenjiedu/tsdb?color=EE781F&include_prereleases&label=Release&logo=github&logoColor=white
   :alt: the latest release version
   :target: https://img.shields.io/github/v/release/wenjiedu/tsdb?color=EE781F&include_prereleases&label=Release&logo=github&logoColor=white

.. image:: https://img.shields.io/badge/License-BSD--3-E9BB41?logo=opensourceinitiative&logoColor=white
   :alt: License
   :target: https://github.com/WenjieDu/TSDB/blob/main/LICENSE

.. image:: https://img.shields.io/github/actions/workflow/status/wenjiedu/tsdb/testing_ci.yml?logo=github&color=C8D8E1&label=CI
   :alt: GitHub Testing
   :target: https://github.com/WenjieDu/TSDB/actions/workflows/testing_ci.yml

.. image:: https://img.shields.io/codeclimate/maintainability-percentage/WenjieDu/TSDB?color=3C7699&label=Maintainability&logo=codeclimate
   :alt: Code Climate maintainability
   :target: https://codeclimate.com/github/WenjieDu/TSDB

.. image:: https://img.shields.io/coverallsCoverage/github/WenjieDu/TSDB?branch=main&logo=coveralls&color=75C1C4&label=Coverage
   :alt: Coveralls report
   :target: https://coveralls.io/github/WenjieDu/TSDB

.. image:: https://img.shields.io/endpoint?url=https://pypots.com/figs/downloads_badges/conda_tsdb_downloads.json
   :alt: Conda downloads
   :target: https://anaconda.org/conda-forge/pypots

.. image:: https://img.shields.io/endpoint?url=https://pypots.com/figs/downloads_badges/pypi_tsdb_downloads.json
   :alt: PyPI downloads
   :target: https://pepy.tech/project/tsdb

.. image:: https://img.shields.io/badge/Contributor%20Covenant-v2.1-4baaaa.svg
   :alt: CODE of CONDUCT

.. image:: https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FWenjieDu%2FTime_Series_Database&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=Visits+since+April+2022&edge_flat=false
   :alt: Visit num

📣 TSDB now supports a total of 1️⃣6️⃣9️⃣ time-series datasets ‼️

.. image:: https://pypots.com/figs/pypots_logos/PyPOTS/logo_FFBG.svg
   :width: 120
   :align: left
   :target: https://github.com/WenjieDu/PyPOTS
   :alt: PyPOTS logo

TSDB is a part of `PyPOTS project <https://github.com/WenjieDu/PyPOTS>`_ (a Python toolbox for data mining on Partially-Observed Time Series), and was separated from PyPOTS for decoupling datasets from learning algorithms.

TSDB is created to help researchers and engineers get rid of data collecting and downloading, and focus back on data processing details.
TSDB provides all-in-one-stop convenience for downloading and loading open-source time-series datasets (available datasets listed `below <https://github.com/WenjieDu/TSDB#-list-of-available-datasets>`_).

❗️Please note that due to people have very different requirements for data processing, data-loading functions in TSDB only contain the most general steps (e.g. removing invalid samples)
and won't process the data (not even normalize it). So, no worries, TSDB won't affect your data preprocessing. If you only want the raw datasets,
TSDB can help you download and save raw datasets as well (take a look at `Usage Examples <https://github.com/WenjieDu/TSDB#-usage-example>`_ below).

🤝 If you need TSDB to integrate an open-source dataset or want to add it into TSDB yourself, please feel free to request for it by creating an issue or make a PR to merge your code.

🤗 **Please** star this repo to help others notice TSDB if you think it is a useful toolkit.
**Please** properly `cite TSDB <https://github.com/WenjieDu/TSDB#-citing-tsdbpypots>`_ in your publications
if it helps with your research. This really means a lot to our open-source research. Thank you!


❖ Usage Examples
^^^^^^^^^^^^^^^^^
TSDB is available on both `PyPI <https://pypi.python.org/pypi/tsdb>`_ and `Anaconda <https://anaconda.org/conda-forge/tsdb>`_.

Install it with `conda install tsdb`, you may need to specify the channel with option `-c conda-forge`

or install via PyPI:

   pip install tsdb

or install from source code:

   pip install `https://github.com/WenjieDu/TSDB/archive/main.zip`

.. code-block:: python
   :linenos:

   import tsdb

   # list all available datasets in TSDB
   tsdb.list()
   # select the dataset you need and load it, TSDB will download, extract, and process it automatically
   data = tsdb.load('physionet_2012')
   # if you need the raw data, use download_and_extract()
   tsdb.download_and_extract('physionet_2012', './save_it_here')
   # datasets you once loaded are cached, and you can check them with list_cached_data()
   tsdb.list_cache()
   # you can delete only one specific dataset and preserve others
   tsdb.delete_cache(dataset_name='physionet_2012')
   # or you can delete all cache with delete_cached_data() to free disk space
   tsdb.delete_cache()

   # to avoid taking up too much space if downloading many datasets,
   # TSDB cache directory can be migrated to an external disk
   tsdb.migrate_cache("/mnt/external_disk/TSDB_cache")


That's all. Simple and efficient. Enjoy it! 😃


❖ List of Available Datasets
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
========================================================================================================================================================================== ==========================================
 Name                                                                                                                                                                      Main Tasks
========================================================================================================================================================================== ==========================================
 `PhysioNet Challenge 2012 <https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/physionet_2012>`_  :cite:`silva2012physionet`                                      Forecasting, Imputation, Classification
 `PhysioNet Challenge 2019 <https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/physionet_2019>`_  :cite:`reyna2019physionet`                                      Forecasting, Imputation, Classification
 `Beijing Multi-Site Air-Quality <https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/beijing_multisite_air_quality>`_  :cite:`zhang2017airquality`                Forecasting, Imputation
 `Electricity Load Diagrams <https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/electricity_load_diagrams>`_  :cite:`trindade2015electricity`                     Forecasting, Imputation
 `Electricity Transformer Temperature (ETT) <https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/electricity_transformer_temperature>`_  :cite:`zhou2021informer`  Forecasting, Imputation
 `Vessel AIS data <https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/vessel_ais>`_  :cite:`grgicevic2023ais`                                                     Forecasting, Imputation, Classification
 `UCR & UEA Datasets <https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/ucr_uea_datasets>`_ (all 163 datasets)  :cite:`bagnall2018uea` :cite:`dau2018ucr`        Classification
========================================================================================================================================================================== ==========================================

❖ Citing TSDB/PyPOTS
^^^^^^^^^^^^^^^^^^^^^
The paper introducing PyPOTS is available on arXiv at `this URL <https://arxiv.org/abs/2305.18811>`_.,
and we are pursuing to publish it in prestigious academic venues, e.g. JMLR (track for
`Machine Learning Open Source Software <https://www.jmlr.org/mloss/>`_). If you use PyPOTS in your work,
please cite it as below and 🌟star `PyPOTS repository <https://github.com/WenjieDu/PyPOTS>`_ to make others notice this library. 🤗


.. image:: https://pypots.com/figs/pypots_logos/Ecosystem/PyPOTS_Ecosystem_Pipeline.png
   :height: 300
   :align: center
   :target: https://pypots.com/ecosystem/
   :alt: PyPOTS Ecosystem Pipeline


.. code-block:: bibtex
   :linenos:

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

or

   Wenjie Du. (2023).
   PyPOTS: A Python Toolbox for Data Mining on Partially-Observed Time Series.
   arXiv, abs/2305.18811. https://doi.org/10.48550/arXiv.2305.18811


.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Code Documentation

   tsdb

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Additional Information

   references
