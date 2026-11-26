"""Serialize configuration updates and operations on the same physical cache."""

# License: BSD-3-Clause

import hashlib
import os
import time
import unicodedata
from contextlib import ExitStack, contextmanager
from pathlib import Path
from threading import local

_LOCK_STATE = local()


@contextmanager
def _os_lock(path):
    """Use an OS-owned lock, automatically released on process termination.

    The lock is outside the dataset tree so deletion/migration cannot replace
    its inode. Only cooperating TSDB processes are covered.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as handle:
        if os.name == "nt":
            import msvcrt

            # Windows can lock bytes beyond EOF. Do not write a sentinel before
            # acquiring the lock: another process may already hold that byte.
            deadline = time.monotonic() + 120
            while True:
                handle.seek(0)
                try:
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                    break
                except OSError as exc:
                    if time.monotonic() >= deadline:
                        raise TimeoutError("Timed out waiting for TSDB cache lock") from exc
                    time.sleep(0.1)
            try:
                yield
            finally:
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            deadline = time.monotonic() + 120
            while True:
                try:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError as exc:
                    if time.monotonic() >= deadline:
                        raise TimeoutError("Timed out waiting for TSDB cache lock") from exc
                    time.sleep(0.1)
            try:
                yield
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


@contextmanager
def _shared_lock(path):
    """Allow nested calls in one thread while keeping the same cross-process lock."""
    path = Path(path).resolve()
    held = getattr(_LOCK_STATE, "paths", None)
    if held is None:
        held = _LOCK_STATE.paths = set()
    if path in held:
        yield
        return
    with _os_lock(path):
        held.add(path)
        try:
            yield
        finally:
            held.remove(path)


@contextmanager
def config_lock(config_path):
    """Protect one ecosystem configuration using its stable legacy lock name."""
    with _shared_lock(Path(config_path).with_suffix(".cache.lock")):
        yield


def _dataset_lock_path(root):
    root = Path(root).expanduser().resolve()
    # A sibling lock survives removal/relocation of the root. Case folding also
    # coalesces aliases on case-insensitive filesystems (harmless over-locking
    # on a case-sensitive filesystem). Do not place a lock inside the cache.
    name = hashlib.sha256(unicodedata.normalize("NFC", root.name).casefold().encode("utf-8")).hexdigest()
    return root.parent / f".tsdb-cache-{name}.lock"


@contextmanager
def dataset_cache_lock(*roots):
    """Lock source/destination roots in deterministic order across config homes."""
    paths = sorted({_dataset_lock_path(root) for root in roots}, key=lambda p: (str(p).casefold(), str(p)))
    with ExitStack() as stack:
        for path in paths:
            stack.enter_context(_shared_lock(path))
        yield


@contextmanager
def cache_lock():
    from . import config

    with config_lock(config.PYPOTS_ECOSYSTEM_CONFIG_PATH):
        yield
