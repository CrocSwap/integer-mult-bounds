"""Real active-child and queued-module controls for cancellation of test discovery."""
import concurrent.futures
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import Mock, patch


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("isolated_cancel_runner", ROOT / "scripts/run_isolated_tests.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

BLOCK = """import os, subprocess, sys, time, unittest
from pathlib import Path
class T(unittest.TestCase):
    def test_wait(self):
        root = Path(__file__).resolve().parent.parent
        (root/'module.pid').write_text(str(os.getpid()))
        child = subprocess.Popen([sys.executable, str(root/'solver.py'), str(root)])
        deadline = time.monotonic()+15
        while not (root/'release').exists() and time.monotonic()<deadline:
            time.sleep(.01)
        child.wait(timeout=5)
"""
SOLVER = """import os,sys,time
from pathlib import Path
root=Path(sys.argv[1])
(root/'solver.pid').write_text(str(os.getpid()))
(root/'ready').touch()
deadline=time.monotonic()+15
while not (root/'release').exists() and time.monotonic()<deadline:
    time.sleep(.01)
"""
QUEUED = """from pathlib import Path
import unittest
class T(unittest.TestCase):
    def test_started(self):
        (Path(__file__).resolve().parent.parent/'queued-started').touch()
"""


def wait_for(predicate, timeout=10):
    deadline = time.monotonic()+timeout
    while not predicate():
        if time.monotonic() >= deadline:
            return False
        time.sleep(.01)
    return True


class ProcessObserver:
    """Retain native handles on Windows; distinguish Linux zombies from live work."""
    def __init__(self, pid):
        self.pid = pid
        self.handle = None
        if os.name == "nt":
            import ctypes
            from ctypes import wintypes
            self.api = ctypes.WinDLL("kernel32", use_last_error=True)
            self.api.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
            self.api.OpenProcess.restype = wintypes.HANDLE
            self.api.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
            self.api.WaitForSingleObject.restype = wintypes.DWORD
            self.api.CloseHandle.argtypes = [wintypes.HANDLE]
            self.api.CloseHandle.restype = wintypes.BOOL
            self.handle = self.api.OpenProcess(0x00100000, False, pid)  # SYNCHRONIZE
            if not self.handle:
                raise ctypes.WinError(ctypes.get_last_error())

    def alive(self):
        if self.handle:
            state = self.api.WaitForSingleObject(self.handle, 0)
            if state not in (0, 258):
                raise RuntimeError("process observer wait failed")
            return state == 258
        try:
            state = Path(f"/proc/{self.pid}/stat").read_text().rsplit(")", 1)[1].split()[0]
            return state not in ("Z", "X")
        except FileNotFoundError:
            return False

    def close(self):
        if self.handle:
            self.api.CloseHandle(self.handle)
            self.handle = None


@unittest.skipUnless(os.name == "nt" or sys.platform == "linux", "native Windows or Linux lifetime observer")
class CancellationTests(unittest.TestCase):
    def exercise(self, failure=KeyboardInterrupt, cleanup_failure=False):
        observers, timer = [], None
        real_pool = concurrent.futures.ThreadPoolExecutor
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tests = root/"tests"
            tests.mkdir()
            (tests/"test_a_block.py").write_text(BLOCK)
            (tests/"test_b_queued.py").write_text(QUEUED)
            (root/"solver.py").write_text(SOLVER)
            error = failure("fixture cancellation")
            interrupted_at = []

            class InterruptedPool(real_pool):
                def map(self, fn, iterable, *args, **kwargs):
                    # Start real workers, then inject the controlling thread's exception.
                    result = super().map(fn, iterable, *args, **kwargs)
                    if not wait_for((root/"ready").exists):
                        raise RuntimeError("real module/solver did not start")
                    for name in ("module", "solver"):
                        observers.append(ProcessObserver(int((root/(name+".pid")).read_text())))
                    if not all(item.alive() for item in observers):
                        raise RuntimeError("fixture processes not alive")
                    nonlocal timer
                    # Bound the old runner's broken shutdown so a failing control cannot leak.
                    timer = threading.Timer(5, (root/"release").touch)
                    timer.start()
                    interrupted_at.append(time.monotonic())
                    raise error

            try:
                with patch.object(runner, "ThreadPoolExecutor", InterruptedPool):
                    with self.assertRaises(failure) as caught:
                        runner.run_modules(sorted(tests.glob("test*.py")), tests_dir=tests,
                                           cwd=root, workers=1)
                elapsed = time.monotonic()-interrupted_at[0]
                self.assertIs(caught.exception, error, "preserve the controlling exception")
                self.assertFalse((root/"release").exists(),
                                 f"cancellation waited for forced fixture release ({elapsed:.3f}s)")
                self.assertFalse((root/"queued-started").exists(), "queued module started after cancellation")
                if cleanup_failure:
                    self.assertTrue(any(item.alive() for item in observers),
                                    "injected cleanup denial must remain observable")
                    self.assertIn("Isolated test cleanup failed",
                                  "\n".join(getattr(error, "__notes__", [])))
                else:
                    self.assertTrue(wait_for(lambda: not any(item.alive() for item in observers), 1),
                                    "active module or solver survived cancellation")
            finally:
                if timer is not None:
                    timer.cancel()
                    timer.join()
                (root/"release").touch()
                if observers:
                    self.assertTrue(wait_for(lambda: not any(item.alive() for item in observers), 20),
                                    "fixture cleanup failed")
                for item in observers:
                    item.close()

    def test_keyboard_interrupt_stops_active_tree_and_queued_module(self):
        self.exercise()

    def test_other_controlling_exception_is_preserved(self):
        self.exercise(RuntimeError)

    def test_parent_only_cleanup_is_detected(self):
        def parent_only(process):
            process.kill()
            process.wait()
        with patch.object(runner, "stop_module", parent_only):
            with self.assertRaisesRegex(AssertionError, "forced fixture release|survived cancellation"):
                self.exercise()

    def test_cleanup_failure_does_not_mask_or_block_cancellation(self):
        with patch.object(runner, "stop_module", side_effect=PermissionError("injected denial")):
            self.exercise(cleanup_failure=True)

    def test_taskkill_timeout_uses_bounded_parent_fallback(self):
        process = Mock(pid=12345)
        process.poll.return_value = None
        with patch.object(runner.os, "name", "nt"), \
                patch.object(runner.subprocess, "run",
                             side_effect=subprocess.TimeoutExpired("taskkill", 5)) as native:
            with self.assertRaisesRegex(RuntimeError, "module 12345"):
                runner.stop_module(process)
        self.assertEqual(native.call_args.kwargs["timeout"], 5)
        process.kill.assert_called_once_with()
        process.wait.assert_called_once_with(timeout=2)

    def test_worker_communicate_error_keeps_live_tree_registered(self):
        observers = []
        real_popen = subprocess.Popen
        children = []
        error = OSError("injected worker pipe failure")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tests = root/"tests"
            tests.mkdir()
            module = tests/"test_a_block.py"
            module.write_text(BLOCK)
            (root/"solver.py").write_text(SOLVER)

            class FailingCommunicate(real_popen):
                def communicate(self, *args, **kwargs):
                    if "unittest" in self.args:
                        children.append(self)
                        if not wait_for((root/"ready").exists):
                            raise RuntimeError("real module/solver did not start")
                        for name in ("module", "solver"):
                            observers.append(ProcessObserver(int((root/(name+".pid")).read_text())))
                        if not all(item.alive() for item in observers):
                            raise RuntimeError("fixture processes not alive")
                        raise error
                    return super().communicate(*args, **kwargs)

            try:
                with patch.object(runner.subprocess, "Popen", FailingCommunicate):
                    with self.assertRaises(OSError) as caught:
                        runner.run_modules([module], tests_dir=tests, cwd=root, workers=1)
                self.assertIs(caught.exception, error)
                self.assertTrue(wait_for(lambda: not any(item.alive() for item in observers), 1),
                                "worker failure removed the live tree before cleanup")
                self.assertFalse((root/"release").exists())
            finally:
                (root/"release").touch()
                if observers:
                    self.assertTrue(wait_for(lambda: not any(item.alive() for item in observers), 20))
                for item in observers:
                    item.close()
                for child in children:
                    for stream in (child.stdout, child.stderr):
                        stream.close()

    def test_output_bytes_survive_multiple_communicate_timeouts(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tests = root/"tests"
            tests.mkdir()
            module = tests/"test_output.py"
            module.write_text("import sys,time,unittest\n"
                              "class T(unittest.TestCase):\n"
                              " def test_output(self):\n"
                              "  sys.stdout.buffer.write(b'L'*100000);sys.stdout.flush()\n"
                              "  time.sleep(.6)\n"
                              "  sys.stdout.buffer.write(b'R'*100000);sys.stdout.flush()\n")
            rows = runner.run_modules([module], tests_dir=tests, cwd=root, workers=1)
            self.assertEqual(rows[0][1], 0, rows[0][3])
            self.assertEqual(rows[0][2], b"L"*100000+b"R"*100000)


if __name__ == "__main__":
    unittest.main()
