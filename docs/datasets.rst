Dataset Guide
=============

TSDB registers 173 identifiers: 10 standalone datasets and 163 UCR/UEA datasets.
The maintained dataset profiles provide original sources, citation information,
and dataset-specific details. Tasks below are examples, not restrictions or
verified license declarations.

.. list-table::
   :header-rows: 1
   :widths: 40 30 30

   * - Dataset profile
     - Identifier
     - Example tasks
   * - `PhysioNet Challenge 2012 <https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/physionet_2012>`_ :cite:`silva2012physionet`
     - ``physionet_2012``
     - Forecasting, imputation, classification
   * - `PhysioNet Challenge 2019 <https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/physionet_2019>`_ :cite:`reyna2019physionet`
     - ``physionet_2019``
     - Forecasting, imputation, classification
   * - `Beijing Multi-Site Air Quality <https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/beijing_multisite_air_quality>`_ :cite:`zhang2017airquality`
     - ``beijing_multisite_air_quality``
     - Forecasting, imputation
   * - `Italy Air Quality <https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/italy_air_quality>`_ :cite:`vito2016air`
     - ``italy_air_quality``
     - Forecasting, imputation
   * - `Electricity Load Diagrams <https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/electricity_load_diagrams>`_ :cite:`trindade2015electricity`
     - ``electricity_load_diagrams``
     - Forecasting, imputation
   * - `Electricity Transformer Temperature (ETT) <https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/electricity_transformer_temperature>`_ :cite:`zhou2021informer`
     - ``electricity_transformer_temperature``
     - Forecasting, imputation
   * - `Vessel AIS <https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/vessel_ais>`_ :cite:`grgicevic2023ais`
     - ``vessel_ais``
     - Forecasting, imputation, classification
   * - `PeMS Traffic <https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/pems_traffic>`_
     - ``pems_traffic``
     - Forecasting, imputation
   * - `Solar Alabama <https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/solar_alabama>`_
     - ``solar_alabama``
     - Forecasting, imputation
   * - `TSQA <https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/tsqa>`_ :cite:`kong2025timemqa`
     - ``tsqa``
     - Time series question answering
   * - `UCR/UEA (163 datasets) <https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/ucr_uea_datasets>`_ :cite:`dau2018ucr,bagnall2018uea`
     - ``ucr_uea_*``
     - Classification

.. doctest::

   >>> import tsdb
   >>> sum(name.startswith("ucr_uea_") for name in tsdb.list())
   163
   >>> "ucr_uea_Wine" in tsdb.list()
   True

Dataset return contracts
------------------------

``tsdb.load`` returns a dictionary with dataset-specific keys and shapes.
UCR/UEA TXT data retains ``(samples, timepoints, features)``; ARFF data retains
its historical ``(samples, channels, timepoints)`` layout. Do not assume a
unified axis order across formats. ARFF takes precedence when both complete
pairs exist. Single-row TXT inputs are supported; malformed or empty pairs
raise errors. PhysioNet and Beijing raw files are enumerated in sorted order.
AIS elapsed time uses seconds independently of pandas timestamp resolution.
The original Zenodo AIS archive contains extensionless files named
``parquets/2020-2_group_*``. TSDB accepts these original names and conventional
``.parquet`` names, without renaming or changing the raw data.

Dataset-specific basic parsing is not a standardized learning pipeline. For
standardized model-ready preprocessing, see
`BenchPOTS <https://github.com/WenjieDu/BenchPOTS>`_. Always consult and cite the
original source for its license and any use restrictions.
