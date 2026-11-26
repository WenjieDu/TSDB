API Reference
=============

Dataset discovery
-----------------

.. autofunction:: tsdb.list
.. autofunction:: tsdb.info

Dataset access
--------------

.. autofunction:: tsdb.load
.. autofunction:: tsdb.download_and_extract
.. autofunction:: tsdb.download_url

Cache management
----------------

.. autofunction:: tsdb.get_cache_dir
.. autofunction:: tsdb.list_cache
.. autofunction:: tsdb.delete_cache
.. autofunction:: tsdb.migrate_cache

``tsdb.CACHED_DATASET_DIR`` resolves the current configured cache directory on
access. Unlike discovery APIs, reading it can initialize configuration and
perform legacy cache migration.

File utilities
--------------

.. autofunction:: tsdb.migrate
.. autofunction:: tsdb.pickle_dump
.. autofunction:: tsdb.pickle_load
.. autofunction:: tsdb.purge_path
.. autoexception:: tsdb.utils.file.CacheError

Shared logging
--------------

.. autoclass:: tsdb.utils.logging.Logger
   :members: set_level, set_logging_format, set_saving_path, stream_handler, file_handler, logging_level, formatter

``tsdb.utils.logging.logger`` is the shared standard-library logger.

See :doc:`usage` for examples and :doc:`migration` for changed error behavior.
