.. TSDB documentation master file, created by
   sphinx-quickstart on Wed Mar 15 15:23:52 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to TSDB documentation!
================================
.. image:: https://raw.githubusercontent.com/WenjieDu/TSDB/main/docs/_static/figs/TSDB_logo.svg?sanitize=true
   :height: 160
   :align: right
   :target: https://github.com/WenjieDu/TSDB
   :alt: TSDB logo

.. centered:: A Python Toolbox Helping Load Time-Series Datasets Easily

.. image:: https://img.shields.io/badge/python-v3-E97040?logo=python&logoColor=white
   :alt: Python version
.. image:: https://img.shields.io/pypi/v/tsdb?color=green&label=PyPI&logo=pypi&logoColor=white
   :alt: PyPI version
   :target: https://pypi.org/project/tsdb
.. image:: https://img.shields.io/badge/License-GPL--v3-E9BB41
   :alt: License
.. image:: https://img.shields.io/github/actions/workflow/status/wenjiedu/tsdb/testing_ci.yml?logo=github&color=C8D8E1&label=CI
   :alt: GitHub Testing
   :target: https://github.com/WenjieDu/TSDB/actions/workflows/testing_ci.yml
.. image:: https://img.shields.io/codeclimate/maintainability-percentage/WenjieDu/TSDB?color=3C7699&label=Maintainability&logo=codeclimate
   :alt: Code Climate maintainability
   :target: https://codeclimate.com/github/WenjieDu/TSDB
.. image:: https://img.shields.io/coverallsCoverage/github/WenjieDu/TSDB?branch=main&logo=coveralls&color=75C1C4&label=Coverage
   :alt: Coveralls report
   :target: https://coveralls.io/github/WenjieDu/TSDB
.. image:: https://img.shields.io/conda/dn/conda-forge/tsdb?label=Conda%20Downloads&color=AED0ED&logo=anaconda&logoColor=white
   :alt: Conda downloads
   :target: https://anaconda.org/conda-forge/pypots
.. image:: https://static.pepy.tech/personalized-badge/tsdb?period=total&units=international_system&left_color=grey&right_color=blue&left_text=PyPI%20Downloads
   :alt: PyPI downloads
   :target: https://pypi.org/project/tsdb
.. image:: https://img.shields.io/badge/Contributor%20Covenant-v2.1-4baaaa.svg
   :alt: CODE of CONDUCT
.. image:: https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FWenjieDu%2FTime_Series_Database&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=Visits+since+April+2022&edge_flat=false
   :alt: Visit num


📣 TSDB now supports a total of 1️⃣6️⃣5️⃣ time-series datasets ‼️

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

or install from PyPI:

   pip install tsdb

or install from source code:

   pip install `https://github.com/WenjieDu/TSDB/archive/main.zip`

.. code-block:: python
   :linenos:

   import tsdb

   tsdb.list_available_datasets()  # list all available datasets in TSDB
   data = tsdb.load_dataset('physionet_2012')  # select the dataset you need and load it, TSDB will download, extract, and process it automatically
   tsdb.download_and_extract('physionet_2012', './save_it_here')  # if you need the raw data, use download_and_extract()
   tsdb.list_cached_data()  # datasets you once loaded are cached, and you can check them with list_cached_data()
   tsdb.delete_cached_data()  # you can delete all cache with delete_cached_data() to free disk space
   tsdb.delete_cached_data(dataset_name='physionet_2012')  # or you can delete only one specific dataset and preserve others


That's all. Simple and efficient. Enjoy it! 😃


❖ List of Available Datasets
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
=============================================================================================================================== ==========================================
 Name                                                                                                                            Main Tasks
=============================================================================================================================== ==========================================
 `PhysioNet Challenge 2012 <https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/physionet_2012>`_                       Classification, Forecasting, Imputation
 `PhysioNet Challenge 2019 <https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/physionet_2019>`_                       Classification, Imputation
 `Beijing Multi-Site Air-Quality <https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/beijing_multisite_air_quality>`_  Forecasting, Imputation
 `Electricity Load Diagrams <https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/electricity_load_diagrams>`_           Forecasting, Imputation
 `UCR & UEA Datasets <https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/ucr_uea_datasets>`_ (all 160 datasets)         Classification
 `Vessel AIS data <https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/vessel_ais>`_                                    Imputation, Forecasting, Classification
=============================================================================================================================== ==========================================

❖ Citing TSDB/PyPOTS
^^^^^^^^^^^^^^^^^^^^^

.. image:: https://raw.githubusercontent.com/WenjieDu/PyPOTS/main/docs/_static/figs/PyPOTS_logo.svg?sanitize=true
   :height: 160
   :align: left
   :target: https://github.com/WenjieDu/PyPOTS
   :alt: PyPOTS logo

TSDB is a part of `PyPOTS project <https://github.com/WenjieDu/PyPOTS>`_ (a Python toolbox for data mining on Partially-Observed Time Series), and was separated from PyPOTS for decoupling datasets from learning algorithms.

The paper introducing PyPOTS is available on arXiv at `this URL <https://arxiv.org/abs/2305.18811>`_.,
and we are pursuing to publish it in prestigious academic venues, e.g. JMLR (track for
`Machine Learning Open Source Software <https://www.jmlr.org/mloss/>`_). If you use PyPOTS in your work,
please cite it as below and 🌟star `PyPOTS repository <https://github.com/WenjieDu/PyPOTS>`_ to make others notice this library. 🤗

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
