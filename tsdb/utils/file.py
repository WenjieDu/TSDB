"""
Functions manipulating files.
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: BSD-3-Clause

import os
import pickle
import shutil
import tempfile
from pathlib import Path

import pandas as pd

from . import config
from .cache_lock import cache_lock, dataset_cache_lock
from .config import cache_dir_override, read_configs, require_legacy_retired_for_relocation, write_configs
from .logging import logger


def check_path(
    path: str,
    check_exists: bool = False,
) -> str:
    """Check the given path and return the absolute path.

    Parameters
    ----------
    path :
        The path to be checked.

    check_exists :
        If True, check if the path exists, and will raise an AssertionError if the path does not exist.

    Returns
    -------
    checked_path:
        The absolute path of the given path.

    """
    checked_path = os.path.abspath(os.path.expanduser(path))

    if check_exists:
        assert os.path.exists(checked_path), f"The given path {checked_path} does not exists"

    return checked_path


def extract_parent_dir(path: str) -> str:
    """Extract the given path's parent directory.

    Parameters
    ----------
    path :
        The path for extracting.

    Returns
    -------
    parent_dir :
        The path to the parent dir of the given path.

    """
    parent_dir = os.path.abspath(os.path.join(path, ".."))
    return parent_dir


def create_dir_if_not_exist(path: str, is_dir: bool = True) -> None:
    """Create the given directory if it doesn't exist.

    Parameters
    ----------
    path :
        The path for check.

    is_dir :
        Whether the given path is to a directory. If `is_dir` is False, the given path is to a file or an object,
        then this file's parent directory will be checked.

    """
    path = extract_parent_dir(path) if not is_dir else path
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        logger.info(f"Successfully created the given path {path}")


class CacheError(RuntimeError):
    """A trusted local cache could not be read or written."""


def pickle_dump(data: object, path: str) -> None:
    """Atomically write a trusted local pickle; preserve an earlier file on failure."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", dir=destination.parent, prefix=".tsdb-pickle-", delete=False) as f:
            temporary = Path(f.name)
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temporary, destination)
    except Exception as exc:
        raise CacheError(f"Cannot write local cache {destination}") from exc
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def pickle_load(path: str) -> object:
    """Read a trusted local pickle. Never load a pickle from an untrusted source."""
    try:
        return pd.read_pickle(path)
    except Exception as exc:
        raise CacheError(f"Cannot read local cache {path}") from exc


def purge_path(path: str, ignore_errors: bool = True) -> None:
    """Delete the given path.
    It will be deleted if a file is given. Itself and all its contents will be purged will a fold is given.

    Parameters
    ----------
    path:
        It could be a file or a fold.

    ignore_errors:
        Errors are ignored if ignore_errors is set.

    """
    # check the given path, no need to check if the path exists because ignore_errors is set
    path = check_path(path)

    try:
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=ignore_errors)
        else:
            os.remove(path)
        # check if succeed
        if not os.path.exists(path):
            logger.info(f"Successfully deleted {path}")
        else:
            cached_dataset_dir = determine_tsdb_home()
            raise FileExistsError(f"Deleting operation failed. {cached_dataset_dir} still exists.")
    except shutil.Error:
        raise shutil.Error("Operation failed.")


def normalize_cache_dir(path):
    """Validate a cache override without touching the filesystem."""
    value = os.fspath(path)
    if not isinstance(value, str) or not value.strip() or "\0" in value:
        raise ValueError("cache_dir must be a nonempty filesystem path")
    return str(Path(value).expanduser().resolve())


def determine_tsdb_home():
    # default path
    override = cache_dir_override()
    if override is not None:
        return check_path(override)
    default_path = str(Path(config.PYPOTS_ECOSYSTEM_CONFIG_PATH).parent / "tsdb")

    # read tsdb_home from the current config file
    # tsdb_home may be changed by users, hence not necessarily equal to the default path
    document = read_configs()
    tsdb_home_path = document["tsdb"]["cache_dir"]
    tsdb_home_path = check_path(tsdb_home_path)

    # old cached dataset dir path used in TSDB v0.2
    old_cached_dataset_dir_02 = check_path("~/.tsdb_cached_datasets")
    # old cached dataset dir path used in TSDB v0.4
    old_cached_dataset_dir_04 = check_path("~/.tsdb")

    if Path(config.PYPOTS_ECOSYSTEM_CONFIG_PATH).parent == config.USER_HOME / ".pypots" and (
        os.path.exists(old_cached_dataset_dir_02) or os.path.exists(old_cached_dataset_dir_04)
    ):
        logger.warning("‼️ Detected the home dir of the old version TSDB. Auto migrating... Please wait.")
        cached_dataset_dir = tsdb_home_path
        if os.path.exists(old_cached_dataset_dir_02):
            migrate(old_cached_dataset_dir_02, cached_dataset_dir)
        else:
            migrate(old_cached_dataset_dir_04, cached_dataset_dir)
        logger.info("🌟 Migrating finished.")
    elif os.path.exists(tsdb_home_path) or tsdb_home_path == default_path:
        cached_dataset_dir = tsdb_home_path
    else:
        # Do not silently redirect a configured external disk to another cache.
        raise FileNotFoundError(
            f"Configured TSDB cache {tsdb_home_path} does not exist. Mount or create that directory, "
            "or set TSDB_CACHE_DIR for a temporary override."
        )

    return cached_dataset_dir


def _migration_paths(old_path, new_path):
    source = Path(old_path).expanduser().absolute()
    destination = Path(new_path).expanduser().absolute()
    if source.is_symlink() or not source.is_dir():
        raise ValueError(f"Migration source must be a real directory: {source}")
    if destination.is_symlink() or (destination.exists() and not destination.is_dir()):
        raise ValueError(f"Migration destination must be a real directory: {destination}")
    source = source.resolve()
    destination = destination.resolve()
    if source == destination or source in destination.parents or destination in source.parents:
        raise ValueError("Migration source and destination must not overlap")
    if destination.exists() and any(destination.iterdir()):
        raise FileExistsError(f"Migration destination is not empty: {destination}")
    return source, destination


def _migrate(old_path, new_path, symlink=False, on_publish=None):
    source, destination = _migration_paths(old_path, new_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    existed = destination.exists()
    with tempfile.TemporaryDirectory(prefix=".tsdb-migration-", dir=destination.parent) as work:
        staged = Path(work) / "data"
        # Preserve relative symlinks in legacy Hugging Face caches.
        shutil.copytree(source, staged, symlinks=True)
        if existed:
            destination.rmdir()  # refuses a concurrent non-empty destination
        try:
            if os.path.lexists(destination):
                raise FileExistsError(str(destination))
            os.rename(staged, destination)
        except BaseException:
            if existed and not os.path.lexists(destination):
                destination.mkdir()
            raise
        # Until config publication succeeds, the original remains intact.
        if on_publish is not None:
            on_publish(destination)
    shutil.rmtree(source)
    if symlink:
        os.symlink(destination, source, target_is_directory=True)
    logger.info(f"Successfully migrated {source} to {destination}")


def migrate(old_path: str, new_path: str, symlink: bool = False) -> None:
    """Safely migrate to a new or empty directory; refuse overlaps and conflicts.

    If publication or configuration fails, retain the source. A complete
    destination copy may remain for manual recovery. Do not run with external
    writers changing either tree.
    """
    source, destination = _migration_paths(old_path, new_path)
    with dataset_cache_lock(source, destination):
        _migrate(source, destination, symlink)


def migrate_cache(target_path: str) -> None:
    """Migrate the configured cache and switch paths after successful copying."""
    from .. import data_processing

    with cache_lock():
        if cache_dir_override() is not None:
            raise ValueError("Unset TSDB_CACHE_DIR before migrating the persistent cache.")
        read_configs()
        require_legacy_retired_for_relocation()
        source = data_processing._cache_home()

        def update(destination):
            write_configs({"tsdb": {"cache_dir": str(destination)}})
            if "CACHED_DATASET_DIR" in vars(data_processing):
                data_processing.CACHED_DATASET_DIR = str(destination)

        source, destination = _migration_paths(source, target_path)
        home = Path(config.PYPOTS_ECOSYSTEM_CONFIG_PATH).parent.resolve()
        if any(root == home or root in home.parents for root in (source, destination)):
            raise ValueError("Cache migration must not move or replace the ecosystem configuration directory")
        with dataset_cache_lock(source, destination):
            _migrate(source, destination, on_publish=update)
