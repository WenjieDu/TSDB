"""Serialize TSDB cache operations sharing one ecosystem configuration."""

# License: BSD-3-Clause

import os
import time
from contextlib import contextmanager
from pathlib import Path
from threading import local

_LOCK_STATE = local()


@contextmanager
def _os_lock(path):
    """Use an OS-owned lock, automatically released on process termination.

    The lock is outside the dataset tree so deletion/migration cannot replace
    its inode. Different ecosystem homes and external writers are not covered.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as handle:
        if os.name == "nt":
            import msvcrt

            handle.seek(0, os.SEEK_END)
            if handle.tell() == 0:
                handle.write(b"\0")
                handle.flush()
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
def config_lock(config_path):
    """Allow nested calls in one thread while keeping the same cross-process lock."""
    path = Path(config_path).with_suffix(".cache.lock").resolve()
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
def cache_lock():
    from . import config

    with config_lock(config.PYPOTS_ECOSYSTEM_CONFIG_PATH):
        yield
