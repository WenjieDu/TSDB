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

Versioned TOML configuration
----------------------------

TSDB v1.0 uses ``~/.pypots/config.toml`` (schema version 1) instead of INI.
The first configuration read automatically imports the old
``config.ini`` and maps ``[path] tsdb_home`` to ``[tsdb] cache_dir``. Existing
cache paths are preserved; no dataset is moved or downloaded by this conversion.
Legacy sections and raw string values are retained under ``legacy_ini``;
no numeric or boolean types are inferred. The original INI remains unchanged
and a uniquely named ``config.ini.*.bak`` preserves its exact bytes, including
comments and original encoding. A SHA-256 fingerprint and the original cache
path detect conflicting legacy edits or divergent cache paths.

Valid UTF-8 (including ASCII and UTF-8 with BOM) is accepted. For other legacy
encodings set ``TSDB_LEGACY_CONFIG_ENCODING`` to the **known original encoding**
(e.g. ``cp1252`` or ``gbk``) before the first configuration read, then unset it.
Do not guess the encoding. An empty or section-only ``[path]`` INI left by
interrupted initialization is backed up and recovered; other invalid files
and unknown TOML schema versions are not silently reset.

TOML is the authoritative configuration for v1.0. Old TSDB versions still
read INI, so they can reuse the unchanged migrated cache location, but
cross-version concurrent cache mutations are not supported. Do not edit
both formats. Before relocating or manually changing the persistent cache
path, upgrade all TSDB environments that share it and archive the old
``config.ini`` (rename it, for example, to ``config.ini.retired``). TSDB
refuses a persistent relocation while the INI remains active; if an older
version later modifies or recreates the INI, v1.0 detects conflicting state
and asks you to reconcile and archive it. There is no non-atomic dual-format
write or automatic downgrade. Keep the original configuration and its backup
for recovery. A missing nondefault cache directory now raises
``FileNotFoundError`` instead of silently using another cache; reconnect the
external disk, create the intended directory, or use a temporary override.

The internal ``tsdb.utils.config.read_configs()`` now returns a TOML document
and ``write_configs(updates)`` merges nested table updates under the lock.
Applications should prefer the public cache APIs rather than private INI
helpers. See :doc:`usage` for configuration locations and overrides.

Unicode logs
------------

New file logs use UTF-8. Appending to a non-UTF-8 log is refused. Choose a new
filename, or back up and convert the old log before appending. An explicitly
requested overwrite (``mode="w"``) still replaces the log.

Logger wrappers now share the handlers of their named logger. Repeated
construction does not duplicate TSDB output; changes made by one wrapper
are visible to other wrappers with the same name. Use the configuration
methods rather than directly assigning handler/formatter/level attributes.
See :doc:`usage` for the lifecycle contract.
