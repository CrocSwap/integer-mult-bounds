"""Native Windows timeout-tree controls for registered research replay.

ywz65, with substantial OpenAI Codex assistance. Apache-2.0.
Complements Paul Romeo's Linux controls in test_research_process_tree.py.
Only ordinary descendants of a live leader are in scope; this is not containment.
"""
import ctypes
from ctypes import wintypes
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
import importlib.util
# Historical taskkill baseline; current Job Object coverage is in test_research_windows_job.py.
_spec = importlib.util.spec_from_file_location("historical_taskkill_runner", ROOT / "tests/historical/windows-taskkill-runner.py")
package = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(package)

TREE = """\
import os
from pathlib import Path
import subprocess
import sys
import time

root, depth = Path(sys.argv[1]), int(sys.argv[2])
(root / f"{depth}.pid").write_text(str(os.getpid()))
child = (subprocess.Popen([sys.executable, __file__, str(root), str(depth - 1)])
         if depth else None)
if depth == 0:
    (root / "ready").touch()
deadline = time.monotonic() + 60
while not (root / "release").exists() and time.monotonic() < deadline:
    time.sleep(0.01)
if child is not None:
    child.wait(timeout=5)
"""


def wait_for(predicate, timeout=5):
    deadline = time.monotonic() + timeout
    while not predicate():
        if time.monotonic() >= deadline:
            return False
        time.sleep(0.01)
    return True


class ProcessHandle:
    """Retain one fixture process object, so later PID reuse cannot fool a check."""

    def __init__(self, pid):
        self.api = ctypes.WinDLL("kernel32", use_last_error=True)
        self.api.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        self.api.OpenProcess.restype = wintypes.HANDLE
        self.api.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        self.api.WaitForSingleObject.restype = wintypes.DWORD
        self.api.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
        self.api.TerminateProcess.restype = wintypes.BOOL
        self.api.CloseHandle.argtypes = [wintypes.HANDLE]
        self.api.CloseHandle.restype = wintypes.BOOL
        self.pid = pid
        # SYNCHRONIZE for observation; PROCESS_TERMINATE only for fixture teardown.
        self.handle = self.api.OpenProcess(0x00100000 | 0x0001, False, pid)
        if not self.handle:
            raise ctypes.WinError(ctypes.get_last_error())

    def alive(self):
        result = self.api.WaitForSingleObject(self.handle, 0)
        if result == 0:  # WAIT_OBJECT_0: the process terminated.
            return False
        if result == 258:  # WAIT_TIMEOUT: the process is still running.
            return True
        raise ctypes.WinError(ctypes.get_last_error())

    def stop(self):
        if self.alive() and not self.api.TerminateProcess(self.handle, 1):
            if self.alive():
                raise ctypes.WinError(ctypes.get_last_error())
        if self.api.WaitForSingleObject(self.handle, 5000) != 0:
            raise RuntimeError(f"fixture process {self.pid} did not stop")

    def close(self):
        if self.handle:
            if not self.api.CloseHandle(self.handle):
                raise ctypes.WinError(ctypes.get_last_error())
            self.handle = None


@unittest.skipUnless(sys.platform == "win32", "requires native Windows process handles")
class WindowsProcessTreeTests(unittest.TestCase):
    def exercise_tree(self, complete=False, leader_only=False):
        process = None
        cleanup_at = None
        handles = []
        real_popen, real_run = subprocess.Popen, subprocess.run
        with tempfile.TemporaryDirectory(prefix="replay tree ") as tmp:
            root = Path(tmp)
            script = root / "tree.py"
            script.write_text(TREE, encoding="utf-8")

            def started(argv, **kwargs):
                nonlocal process
                candidate = real_popen(argv, **kwargs)
                if str(script) not in argv:
                    return candidate  # taskkill is not part of the fixture tree.
                process = candidate
                self.assertTrue(wait_for((root / "ready").exists, 30), "tree never became ready")
                pids = [int((root / f"{depth}.pid").read_text()) for depth in range(3)]
                self.assertEqual(pids[2], process.pid)
                self.assertEqual(len(set(pids)), 3)
                for pid in pids:
                    handles.append(ProcessHandle(pid))
                self.assertTrue(all(handle.alive() for handle in handles))
                if complete:
                    (root / "release").touch()
                return candidate

            def run(argv, **kwargs):
                nonlocal cleanup_at
                is_cleanup = argv[:4] == ["taskkill", "/F", "/T", "/PID"]
                if is_cleanup:
                    cleanup_at = time.monotonic()
                if leader_only and is_cleanup:
                    self.assertEqual(argv[4], str(process.pid))
                    process.kill()
                    return subprocess.CompletedProcess(argv, 0, b"", b"")
                result = real_run(argv, **kwargs)
                if is_cleanup:
                    # Do not mistake the fixture's eventual self-exit for a kill.
                    self.assertEqual(result.returncode, 0, result.stderr)
                return result

            try:
                # All three handles are retained before the launcher's timeout begins.
                with patch.object(package.subprocess, "Popen", side_effect=started), \
                        patch.object(package.subprocess, "run", side_effect=run):
                    argv = [sys.executable, str(script), str(root), "2"]
                    if complete:
                        package.run_command(argv, root, 5)
                    else:
                        with self.assertRaisesRegex(ValueError, "verification timed out"):
                            package.run_command(argv, root, 0.05)
                if not complete:
                    self.assertIsNotNone(cleanup_at, "timeout did not invoke tree cleanup")
                    self.assertLess(time.monotonic() - cleanup_at, 10,
                                    "cleanup waited for the fixture's 60-second self-exit")
                wait_for(lambda: not any(handle.alive() for handle in handles), 1)
                self.assertFalse([h.pid for h in handles if h.alive()], "live descendants after replay")
            finally:
                (root / "release").touch()
                try:
                    # Only retained handles belonging to this fixture are terminated.
                    for handle in handles:
                        handle.stop()
                    if process is not None:
                        if process.poll() is None:
                            process.kill()
                        process.wait(timeout=5)
                finally:
                    for handle in handles:
                        handle.close()

    def test_successful_tree_completion(self):
        self.exercise_tree(complete=True)

    def test_timeout_terminates_descendants(self):
        self.exercise_tree()

    def test_parent_only_cleanup_is_detected(self):
        with self.assertRaisesRegex(AssertionError, "live descendants after replay"):
            self.exercise_tree(leader_only=True)


if __name__ == "__main__":
    unittest.main()
