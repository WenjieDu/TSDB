TSDB
====

.. only:: html and not epub

   .. image:: https://pypots.com/figs/pypots_logos/TSDB/logo_FFBG.svg
      :width: 180
      :align: right
      :target: https://github.com/WenjieDu/TSDB
      :alt: TSDB logo

**A Python Toolbox for Loading Public Time Series Datasets**

TSDB (Time Series Data Beans) provides unified access to 173 public time series datasets.
It handles discovery, downloading, extraction, loading, and caching as the dataset access layer of the
`PyPOTS ecosystem <https://pypots.com/ecosystem/>`_. Loaders apply basic dataset-specific preparation,
not task-specific normalization or missing-value imputation. Users may also download original files.

.. note::
   This documentation describes the v1.0 development API. Use the documentation matching your installed version.

Quick start
-----------

.. code-block:: bash

   pip install tsdb

.. code-block:: python

   import tsdb

   print(tsdb.list())
   print(tsdb.info("physionet_2012"))
   data = tsdb.load("physionet_2012")  # first load requires network access

See :doc:`install` and :doc:`usage` for prerequisites and detailed examples.

`GitHub <https://github.com/WenjieDu/TSDB>`_ · `PyPI <https://pypi.org/project/tsdb/>`_ ·
`Community <https://github.com/WenjieDu/PyPOTS#-community>`_ · `Tutorials <https://github.com/WenjieDu/BrewPOTS>`_

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   install
   usage
   datasets
   migration

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   tsdb

.. toctree::
   :maxdepth: 2
   :caption: Project Development

   maintenance
   references
