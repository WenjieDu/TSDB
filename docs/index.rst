.. TSDB documentation master file, created by
   sphinx-quickstart on Wed Mar 15 15:23:52 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to TSDB's documentation!
================================
.. image:: https://raw.githubusercontent.com/WenjieDu/TSDB/main/docs/figs/TSDB%20logo.svg?sanitize=true
   :height: 235
   :align: right
   :target: https://github.com/WenjieDu/TSDB
   :alt: TSDB logo

.. centered:: A Python Toolbox to Ease Loading Open-Source Time-Series Datasets

.. image:: https://img.shields.io/badge/python-v3-yellowgreen
   :alt: Python version
.. image:: https://img.shields.io/pypi/v/tsdb?color=green&label=PyPI
   :alt: PyPI version
   :target: https://pypi.org/project/tsdb
.. image:: https://github.com/WenjieDu/TSDB/actions/workflows/testing.yml/badge.svg
   :alt: GitHub Testing
   :target: https://github.com/WenjieDu/TSDB/actions/workflows/testing.yml
.. image:: https://coveralls.io/repos/github/WenjieDu/Time_Series_Database/badge.svg
   :alt: Coveralls report
   :target: https://coveralls.io/github/WenjieDu/Time_Series_Database
.. image:: https://static.pepy.tech/personalized-badge/tsdb?period=total&units=none&left_color=gray&right_color=blue&left_text=Downloads
   :alt: PyPI download number
   :target: https://pypi.org/project/tsdb
.. image:: https://img.shields.io/badge/Contributor%20Covenant-v2.1-4baaaa.svg
   :alt: CODE of CONDUCT


📣 TSDB now supports a total of 1️⃣1️⃣9️⃣ time-series datasets ‼️

Project TSDB is created to help researchers and engineers get rid of data collecting and downloading, and focus back on data processing details. TSDB provides all-in-one-stop convenience for downloading and loading open-source time-series datasets (available datasets listed `below <https://github.com/WenjieDu/TSDB#-list-of-available-datasets>`_).

❗️Please note that due to people have very different requirements for data processing, data-loading functions in TSDB only contain the most general steps (e.g. removing invalid samples) and won't process the data (not even normalize it). So, no worries, TSDB won't affect your data preprocessing. If you only want the raw datasets, TSDB can help you download and save raw datasets as well (take a look at `Usage Examples <https://github.com/WenjieDu/TSDB#-usage-example>`_ below).

🤝 If you need TSDB to integrate an open-source dataset or want to add it into TSDB yourself, please feel free to request for it by creating an issue or make a PR to merge your code.

❖ Usage Examples
^^^^^^^^^^^^^^^^^
Install from PyPI:
   pip install tsdb

or install from source code:
   pip install https://github.com/WenjieDu/TSDB/archive/main.zip

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
======================================================================== ==========================================
 Name                                                                    Main Tasks
======================================================================== ==========================================
 [PhysioNet Challenge 2012](datasets/PhysioNet-2012)                     Classification, Forecasting, Imputation
 [PhysioNet Challenge 2019](datasets/PhysioNet-2019)                     Classification, Imputation
 [Beijing Multi-Site Air-Quality](datasets/BeijingMultiSiteAirQuality)   Forecasting, Imputation
 [Electricity Load Diagrams](datasets/ElectricityLoadDiagrams)           Forecasting, Imputation
 [UCR & UEA Datasets](datasets/UCR_UEA_Datasets) (all 115 datasets)      Classification
======================================================================== ==========================================

❖ License
^^^^^^^^^^
Please note that TSDB is open source under `license GPL-3.0 <https://en.wikipedia.org/wiki/GNU_General_Public_License#Version_3>`_.

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   install
   examples

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Code Documentation

   tsdb

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Additional Information

   faq
   about_us


References
""""""""""
.. bibliography::