Usage
=====

Discover datasets
-----------------

.. doctest::

   >>> import tsdb
   >>> len(tsdb.list())
   173
   >>> spec = tsdb.info("physionet_2019")
   >>> spec["name"], spec["revision"], spec["download_strategy"]
   ('physionet_2019', '1.0.0', 'physionet_2019')
   >>> spec["license"] is None
   True

``info`` returns a fresh dictionary with source URLs, loader name and argument,
strategy, profile and profile URL, required file/directory layout, optional
dependencies, and known revision, license, and tasks. Unknown metadata is
``None``; consult the source and profile for authoritative terms and citations.
Neither discovery operation requires network access, scientific dependency
imports, configuration initialization, or cache migration.

Load and download
-----------------

.. code-block:: python

   data = tsdb.load("physionet_2012")
   print(data.keys())
   tsdb.download_and_extract("physionet_2012", "./raw_physionet_2012")

The first load downloads and parses the dataset into a dictionary. Keys and
shapes depend on the dataset; see :doc:`datasets`. Subsequent loads use local
caches. Raw downloads publish a new directory only after all required sources
have succeeded. The destination must not already exist. TSQA downloads actual
Hugging Face dataset files; install the extra described in :doc:`install`.

Use ``tsdb.download_url(url, destination)`` to download an arbitrary supported
CSV/TXT or archive into a new directory. ZIP, TAR (including gzip, bzip2 and xz),
and single CSV/TXT gzip files are supported. Unsafe archive paths, links,
special files and conflicting members are rejected. The return value is an
absolute path to the output directory or decompressed single gzip file.

Cache management
----------------

The default cache is ``~/.pypots/tsdb``. Inspect, rebuild or refresh a dataset:

.. code-block:: python

   print(tsdb.CACHED_DATASET_DIR)
   print(tsdb.list_cache())
   tsdb.delete_cache("physionet_2012", only_pickle=True)
   data = tsdb.load("physionet_2012")  # reparse existing raw files
   data = tsdb.load("physionet_2012", use_cache=False)  # fresh download

Deleting only the pickle preserves raw files. Unreadable parsed caches are
rebuilt from local raw data when possible. A fresh download retains the old
cache until its replacement has been downloaded, parsed and cached successfully.
Parsed caches are trusted local pickle files; never load an untrusted pickle.

.. code-block:: python

   tsdb.delete_cache("physionet_2012")  # remove this dataset's local files
   # tsdb.delete_cache()  # remove all registered dataset caches
   tsdb.migrate_cache("/mnt/external_disk/TSDB_cache")

Deletion preserves unrelated files and recovery backups. Invalid dataset names
raise ``ValueError``. Pickle utility failures raise ``CacheError`` instead of
returning ``None``. Cache operations sharing one ecosystem configuration are
serialized by an OS lock; external writers and distinct ecosystem homes sharing
a cache are not covered. Migration requires a new or empty non-overlapping
destination. Configuration switches only after copying succeeds. A failed
configuration write retains the original and complete destination copy for recovery.

Ecosystem configuration
-----------------------

TSDB reads and updates a versioned UTF-8 TOML file using tomlkit. With the
default ecosystem home it is ``~/.pypots/config.toml``:

.. code-block:: toml

   schema_version = 1

   [tsdb]
   cache_dir = "~/.pypots/tsdb"

Additional tables, comments and typed values are preserved when TSDB updates
its own cache setting. Other ecosystem-specific tables are reserved for future
use; their presence does not enable features in TSDB.

Set ``PYPOTS_HOME`` before importing the configuration/data-access modules to
select another ecosystem home. Its default cache is ``$PYPOTS_HOME/tsdb``;
its configuration and lock are stored in that home. ``TSDB_CACHE_DIR`` is a
process-environment override read at each cache operation and takes precedence
over the persistent cache setting. For example:

.. code-block:: bash

   export PYPOTS_HOME=/path/to/isolated/pypots
   export TSDB_CACHE_DIR=/path/to/temporary/cache

An override does not change the TOML file or migrate the old cache. Unset it
before calling ``tsdb.migrate_cache``. A new temporary cache can be created
on first use. A nondefault persistent directory must already exist (or be
created by ``migrate_cache``); an absent external drive is not silently
replaced with the default cache. Keep the same ecosystem home when sharing
one cache across processes. The original default ``~/.pypots/tsdb`` is unchanged.

Configuration is initialized only when first read, not by importing TSDB,
the shared logger, or inspecting dataset metadata. Legacy INI is migrated
without changing data paths; read :doc:`migration` before relocating a cache
that was used by older TSDB environments.

Shared logging
--------------

.. code-block:: python

   from tsdb.utils.logging import Logger

   log = Logger(name="my-experiment", logging_level="info")
   log.set_saving_path("./logs", "experiment.log")
   log.logger.info("Training started")

The shared configuration and file logs use UTF-8. Console logging retains
Unicode when supported and escapes unsupported characters without changing
application standard streams or global encoding settings. See :doc:`migration`
for legacy configuration and log-file compatibility.

Named logger lifecycle
----------------------

``Logger`` wrappers with the same name share one TSDB-owned console handler
and at most one TSDB-owned UTF-8 file handler. Constructing another wrapper
with the same name applies its level and format to the existing handlers,
preserving any configured file and console stream. Use ``set_level``,
``set_logging_format`` and ``set_saving_path`` to change the shared settings.
The ``logging_level``, ``formatter``, ``stream_handler`` and ``file_handler``
attributes expose the current shared state; ``stream_handler.setStream``
remains available for a custom console stream. Invalid levels raise
``ValueError``.

Replacing the file destination detaches and closes the previous TSDB file
handler. If opening or validating the new file fails, the previous handler
remains active. TSDB does not remove or reconfigure independently attached
application handlers. Configuration calls through TSDB are serialized within
a process; concurrent emission during reconfiguration and external handler
changes are not a transactional logging operation.
