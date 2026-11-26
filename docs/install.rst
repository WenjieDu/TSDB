Installation
============

TSDB v1.0 requires Python 3.10 or later. For Python 3.8 or 3.9, remain on TSDB 0.8.

Choose one installation method:

.. code-block:: bash

   pip install tsdb
   # To upgrade: pip install tsdb --upgrade

.. code-block:: bash

   conda install conda-forge::tsdb

Conda package availability depends on the channel's published versions.
To install the latest source on main (which may include unreleased changes):

.. code-block:: bash

   pip install https://github.com/WenjieDu/TSDB/archive/main.zip

Optional dependencies
---------------------

The default runtime dependencies are NumPy, pandas, PyArrow, requests, and tqdm.
TSQA requires the optional Hugging Face client:

.. code-block:: bash

   pip install "tsdb[tsqa]"

No SciPy or scikit-learn installation is required by TSDB itself.
For the behavior of existing caches and configuration, see :doc:`migration`.
