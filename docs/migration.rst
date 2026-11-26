Migrating from TSDB 0.8 to v1.0
===============================

Python and API compatibility
----------------------------

* Python 3.10 or newer is required. Python 3.8 and 3.9 users can remain on 0.8.
* Existing dataset identifiers and basic return contracts are preserved.
* Use the new public ``tsdb.download_url`` instead of the private
  ``tsdb.utils.downloading._download_and_extract`` wrapper. The public API
  returns an absolute path and refuses existing destinations.
* Invalid dataset names now raise ``ValueError``; malformed dataset inputs and
  pickle failures are reported explicitly instead of being silently ignored.
* TSQA requires ``tsdb[tsqa]``. Importing TSDB, listing datasets and inspecting
  metadata no longer initialize the shared configuration or migrate caches.

Existing dataset caches
-----------------------

No blanket cache deletion or redownload is required. PhysioNet and Beijing
raw files are now enumerated in sorted order; previously parsed caches retain
their earlier order until rebuilt. AIS elapsed time is computed in seconds
independent of pandas timestamp resolution. To use current parsing logic with
existing raw files, call ``tsdb.delete_cache(name, only_pickle=True)`` before
loading again. See :doc:`datasets` for the preserved UCR/UEA axis conventions.

Unicode configuration and logs
------------------------------

TSDB stores the shared ecosystem configuration (``~/.pypots/config.ini``) and
new file logs in UTF-8. Existing valid UTF-8 configurations (including ASCII
and UTF-8 with BOM) are read without conversion. If an old file is not valid
UTF-8, set ``TSDB_LEGACY_CONFIG_ENCODING`` to its **known original encoding**
(e.g. ``cp1252`` or ``gbk``) for one ``from tsdb.utils import config``, then unset it.
TSDB validates the configuration, saves its original bytes in a uniquely named
``config.ini.*.bak`` beside it, and atomically converts the original to UTF-8.
Do not guess the encoding. Some legacy byte sequences are also valid UTF-8;
if you know a file was written in another encoding, back it up and explicitly
convert it in a text editor before importing TSDB.

An empty or section-only ``[path]`` file left by interrupted initialization is
backed up and recovered; other invalid configurations are not silently reset.
Appending to a non-UTF-8 log is refused. Choose a new filename, or back up and
convert the old log before appending. An explicitly requested overwrite
(``mode="w"``) still replaces the log.
