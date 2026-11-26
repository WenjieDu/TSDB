"""Regression tests for POSIX fork inheritance of native TSDB lock handles."""

# License: BSD-3-Clause

import os
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(not hasattr(os, "fork"), reason="POSIX fork is unavailable on Windows")
ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("kind", ["config", "dataset"])
def test_fork_child_acquires_independent_lock_after_parent_release(tmp_path, kind):
    code = """
import os, signal, sys, time
from pathlib import Path
from tsdb.utils import cache_lock as locks
root = Path(sys.argv[1])
lock = locks.config_lock if sys.argv[2] == 'config' else locks.dataset_cache_lock
contended, entered = root / 'contended', root / 'entered'
path = root / 'cache'

def wait(marker):
    deadline = time.monotonic() + 8
    while not marker.exists() and time.monotonic() < deadline:
        time.sleep(.02)
    assert marker.exists(), marker

with lock(path):
    # Preserve ordinary reentrancy before testing the inherited state.
    with lock(path):
        pid = os.fork()
        if pid == 0:
            signal.alarm(12)
            try:
                original = locks.time.sleep
                def observe(seconds):
                    contended.touch()
                    original(seconds)
                locks.time.sleep = observe
                with lock(path):
                    entered.touch()
                os._exit(0)
            except BaseException:
                import traceback
                traceback.print_exc()
                os._exit(1)
        try:
            wait(contended)  # native nonblocking lock actually failed
            assert not entered.exists(), 'child bypassed parent lock'
        except BaseException:
            os.kill(pid, signal.SIGKILL)
            os.waitpid(pid, 0)
            raise
    assert not entered.exists(), 'nested exit released the outer lock'
# Parent releases; the child must now successfully acquire and release its own lock.
_, status = os.waitpid(pid, 0)
assert os.WIFEXITED(status) and os.WEXITSTATUS(status) == 0, status
assert entered.exists()
with lock(path):
    pass
"""
    _run(tmp_path, code, kind)


@pytest.mark.parametrize("other_thread", [False, True])
def test_fork_child_does_not_keep_dead_parent_lock_alive(tmp_path, other_thread):
    code = """
import fcntl, os, signal, sys, threading, time
from pathlib import Path
from tsdb.utils import cache_lock as locks
root = Path(sys.argv[1])
path = root / 'cache'
ready, release, done = root / 'ready', root / 'release', root / 'done'

def wait(marker):
    deadline = time.monotonic() + 8
    while not marker.exists() and time.monotonic() < deadline:
        time.sleep(.02)
    assert marker.exists(), marker

def fork_child():
    pid = os.fork()
    if pid == 0:
        signal.alarm(12)
        try:
            ready.touch()
            wait(release)
            with locks.dataset_cache_lock(path):
                done.touch()
            os._exit(0)
        except BaseException:
            import traceback
            traceback.print_exc()
            os._exit(1)
    wait(ready)
    # Exit without unwinding the lock context. The child is still alive.
    os._exit(0)

holder = os.fork()
if holder == 0:
    signal.alarm(12)
    if sys.argv[2] == 'True':
        acquired = threading.Event()
        def hold():
            with locks.dataset_cache_lock(path):
                acquired.set()
                time.sleep(30)
        thread = threading.Thread(target=hold, daemon=True)
        thread.start()
        assert acquired.wait(8)
        fork_child()
    else:
        with locks.dataset_cache_lock(path):
            fork_child()
    os._exit(1)
_, status = os.waitpid(holder, 0)
assert os.WIFEXITED(status) and os.WEXITSTATUS(status) == 0, status
assert ready.exists() and not done.exists()
try:
    # An independent open-file description must be able to lock immediately,
    # although the forked child is alive and has not entered its own operation.
    with locks._dataset_lock_path(path).open('a+b') as probe:
        fcntl.flock(probe.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.flock(probe.fileno(), fcntl.LOCK_UN)
finally:
    release.touch()
wait(done)
"""
    _run(tmp_path, code, str(other_thread))


def _run(tmp_path, code, parameter):
    env = os.environ.copy()
    env.update(PYTHONPATH=str(ROOT), PYPOTS_HOME=str(tmp_path / "home"))
    result = subprocess.run(
        [sys.executable, "-c", code, str(tmp_path), parameter],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        timeout=45,
        check=False,
    )
    assert result.returncode == 0, (result.stdout.decode(errors="replace"), result.stderr.decode(errors="replace"))
