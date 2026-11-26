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

The default runtime dependencies are NumPy, pandas, PyArrow, requests, tqdm,
and tomlkit (TOML configuration read/write).
TSQA requires the optional Hugging Face client:

.. code-block:: bash

   pip install "tsdb[tsqa]"

TSQA is a gated dataset on Hugging Face. Sign in and obtain access at
`Time-MQA/TSQA <https://huggingface.co/datasets/Time-MQA/TSQA>`_. Then authenticate
with ``hf auth login`` or provide ``HF_TOKEN`` in your environment using an
authorized read-only Hugging Face access token. Never put the token in source
code or logs. Existing local TSQA raw data can be parsed without authentication.

No SciPy or scikit-learn installation is required by TSDB itself.
For the behavior of existing caches and configuration, see :doc:`migration`.
