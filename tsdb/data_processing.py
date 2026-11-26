"""
Functions for loading datasets.
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: BSD-3-Clause

import os
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path

from . import loading_funcs
from .database import AVAILABLE_DATASETS, dataset_spec
from .utils import config
from .utils.cache_lock import cache_lock, dataset_cache_lock
from .utils.config import cache_dir_override
from .utils.downloading import download_and_extract, refresh_raw_dataset
from .utils.file import CacheError, determine_tsdb_home, normalize_cache_dir, pickle_dump, pickle_load
from .utils.logging import logger


def _cache_home(cache_dir=None):
    if cache_dir is not None:
        return normalize_cache_dir(cache_dir)
    override = cache_dir_override()
    if override is not None:
        return normalize_cache_dir(override)
    # Retain the internal module override for existing integrations/tests.
    return globals().get("CACHED_DATASET_DIR") or determine_tsdb_home()


def get_cache_dir(*, cache_dir: str | os.PathLike | None = None) -> str:
    """Return the effective absolute cache directory (explicit, env, config, default)."""
    if cache_dir is not None or cache_dir_override() is not None:
        return _cache_home(cache_dir)
    with cache_lock():
        return _cache_home()


@contextmanager
def _cache_operation(cache_dir=None):
    # Keep config resolution and cache operations serialized against persistent
    # migration in this ecosystem; overrides need only the physical cache lock.
    if cache_dir is not None or cache_dir_override() is not None:
        root = Path(_cache_home(cache_dir))
        with dataset_cache_lock(root):
            yield root
    else:
        with cache_lock():
            root = Path(_cache_home())
            default = Path(config.PYPOTS_ECOSYSTEM_CONFIG_PATH).parent / "tsdb"
            must_exist = root.exists() or (root != default and "CACHED_DATASET_DIR" not in globals())
            with dataset_cache_lock(root):
                # Another ecosystem may have relocated the shared root while
                # we waited. Do not recreate a missing persistent cache.
                if must_exist and not root.is_dir():
                    raise FileNotFoundError(f"Configured TSDB cache {root} is no longer available")
                yield root


def __getattr__(name):
    if name == "CACHED_DATASET_DIR":
        return get_cache_dir()
    raise AttributeError(name)


def list() -> list:
    """Return registered dataset names."""
    return AVAILABLE_DATASETS.copy()


def _validate_name(dataset_name):
    if dataset_name not in AVAILABLE_DATASETS:
        raise ValueError(f"{dataset_name!r} is not available in TSDB. See tsdb.list().")


def _parse(dataset_name, path):
    spec = dataset_spec(dataset_name)
    loader = getattr(loading_funcs, spec.loader)
    result = loader(path, spec.loader_arg) if spec.loader_arg is not None else loader(path)
    if not isinstance(result, dict) or not result:
        raise CacheError(f"Dataset {dataset_name} did not produce valid data")
    pickle_dump(result, Path(path) / f"{dataset_name}_cache.pkl")
    return result


def _load_cached(name, target):
    cache = target / f"{name}_cache.pkl"
    if cache.is_symlink():
        raise CacheError(f"Refusing linked parsed cache: {cache}")
    if cache.is_file():
        try:
            result = pickle_load(cache)
            if isinstance(result, dict) and result:
                return result
        except CacheError:
            logger.warning(f"Rebuilding unreadable parsed cache {cache} from local raw data")
    return _parse(name, str(target))


def load(dataset_name: str, use_cache: bool = True, *, cache_dir: str | os.PathLike | None = None) -> dict:
    """Load a dataset; cache_dir temporarily overrides the resolved cache.

    use_cache=False stages and validates a fresh replacement.
    """
    _validate_name(dataset_name)
    profile = dataset_spec(dataset_name).profile
    logger.info(f"Please cite {dataset_name}: https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/{profile}")
    with _cache_operation(cache_dir) as root:
        target = root / dataset_name
        if target.is_symlink() or (target.exists() and not target.is_dir()):
            raise CacheError(f"Invalid dataset cache path: {target}")
        if target.exists():
            if use_cache:
                result = _load_cached(dataset_name, target)
            else:
                result = refresh_raw_dataset(
                    dataset_name, str(target), prepare=lambda path: _parse(dataset_name, str(path))
                )
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(prefix=".tsdb-load-", dir=target.parent) as staging:
                raw = Path(staging) / "data"
                download_and_extract(dataset_name, str(raw))
                result = _parse(dataset_name, str(raw))
                if os.path.lexists(target):
                    raise FileExistsError(str(target))
                os.rename(raw, target)
    logger.info("Loaded successfully!")
    return result


def list_cache(*, cache_dir: str | os.PathLike | None = None) -> list:
    """List registered cached datasets in the resolved or explicitly supplied cache."""
    with _cache_operation(cache_dir) as root:
        root.mkdir(parents=True, exist_ok=True)
        return sorted(
            p.name for p in root.iterdir() if p.name in AVAILABLE_DATASETS and p.is_dir() and not p.is_symlink()
        )


def _delete_dataset(path, only_pickle):
    if path.is_symlink():
        raise CacheError(f"Refusing to delete linked cache directory: {path}")
    if not path.exists():
        if only_pickle:
            raise FileNotFoundError(str(path))
        return
    if not path.is_dir():
        raise CacheError(f"Not a dataset directory: {path}")
    if only_pickle:
        for file in path.glob("*.pkl"):
            file.unlink()
    else:
        shutil.rmtree(path)


def delete_cache(
    dataset_name: str | None = None, only_pickle: bool = False, *, cache_dir: str | os.PathLike | None = None
) -> None:
    """Delete registered caches in the resolved or explicit cache, preserving unrelated files."""
    if dataset_name is not None:
        _validate_name(dataset_name)
    with _cache_operation(cache_dir) as root:
        if not root.exists():
            return
        if dataset_name is None:
            for path in root.iterdir():
                if path.name in AVAILABLE_DATASETS:
                    _delete_dataset(path, only_pickle)
        else:
            _delete_dataset(root / dataset_name, only_pickle)
