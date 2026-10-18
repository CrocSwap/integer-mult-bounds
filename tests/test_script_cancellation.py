"""Real direct-script cancellation controls. Adapted from credited PR2625 tests.

Prepared for ywz65 with OpenAI Codex assistance. Apache-2.0.
"""
import concurrent.futures
import contextlib
import io
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
spec = importlib.util.spec_from_file_location("script_cancel_runner", ROOT / "scripts/run_parallel.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

BLOCK = """import os, subprocess, sys, time
from pathlib import Path
root = Path(__file__).resolve().parent
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
(Path(__file__).resolve().parent/'queued-started').touch()
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
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root/"block.py").write_text(BLOCK)
            (root/"queued.py").write_text(QUEUED)
            (root/"solver.py").write_text(SOLVER)
            error = failure("fixture cancellation")
            interrupted_at = []

            def interrupted_results(futures):
                if not wait_for((root/"ready").exists):
                    raise RuntimeError("real script/solver did not start")
                for name in ("module", "solver"):
                    observers.append(ProcessObserver(int((root/(name+".pid")).read_text())))
                if not all(item.alive() for item in observers):
                    raise RuntimeError("fixture processes not alive")
                nonlocal timer
                timer = threading.Timer(5, (root/"release").touch)
                timer.start()
                interrupted_at.append(time.monotonic())
                raise error

            try:
                with patch.object(runner, "as_completed", interrupted_results), patch.object(runner, "jobs", return_value=1):
                    with self.assertRaises(failure) as caught:
                        runner.run_all([(name, [sys.executable, str(root/(name+".py"))])
                                        for name in ("block", "queued")], cwd=root)
                elapsed = time.monotonic()-interrupted_at[0]
                self.assertIs(caught.exception, error, "preserve the controlling exception")
                self.assertFalse((root/"release").exists(),
                                 f"cancellation waited for forced fixture release ({elapsed:.3f}s)")
                self.assertFalse((root/"queued-started").exists(), "queued module started after cancellation")
                if cleanup_failure:
                    self.assertTrue(any(item.alive() for item in observers),
                                    "injected cleanup denial must remain observable")
                    self.assertIn("Parallel script cleanup failed",
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
        with patch.object(runner, "stop_script", parent_only):
            with self.assertRaisesRegex(AssertionError, "forced fixture release|survived cancellation"):
                self.exercise()

    def test_cleanup_failure_does_not_mask_or_block_cancellation(self):
        with patch.object(runner, "stop_script", side_effect=PermissionError("injected denial")):
            self.exercise(cleanup_failure=True)

    def test_taskkill_timeout_uses_bounded_parent_fallback(self):
        process = Mock(pid=12345)
        process.poll.return_value = None
        with patch.object(runner.os, "name", "nt"), \
                patch.object(runner.subprocess, "run",
                             side_effect=subprocess.TimeoutExpired("taskkill", 5)) as native:
            with self.assertRaisesRegex(RuntimeError, "script 12345"):
                runner.stop_script(process)
        self.assertEqual(native.call_args.kwargs["timeout"], 5)
        process.kill.assert_called_once_with()
        process.wait.assert_called_once_with(timeout=2)

    def test_complete_output_blocks_and_failure_labels_survive_polling(self):
        output=io.StringIO()
        code="import sys,time;sys.stdout.write('L'*100000);sys.stdout.flush();time.sleep(.6);sys.stdout.write('R'*100000);sys.stdout.flush()"
        with contextlib.redirect_stdout(output), patch.object(runner,"jobs",return_value=1):
            failed=runner.run_all([('good',[sys.executable,'-c',code]),
                                   ('bad',[sys.executable,'-c',"print('bad-output');raise SystemExit(7)"])])
        self.assertEqual(failed,['bad'])
        text=output.getvalue()
        self.assertIn('L'*100000+'R'*100000+'\n',text)
        self.assertLess(text.index('Checked good'),text.index('FAIL bad'))
        self.assertTrue(text.endswith('bad-output\n'))

    def exercise_start_failure(self, during_iteration, communication=False):
        """A real running solver must stop if command production/launch fails."""
        observers, timers, replaced_communicators = [], [], []
        real_popen = subprocess.Popen
        error = FileNotFoundError('injected unavailable command')
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root/'block.py').write_text(BLOCK)
            (root/'solver.py').write_text(SOLVER)

            def ready_then_fail():
                if not wait_for((root/'ready').exists):
                    raise RuntimeError('active script did not start')
                for name in ('module', 'solver'):
                    observers.append(ProcessObserver(int((root/(name+'.pid')).read_text())))
                timer = threading.Timer(5, (root/'release').touch)
                timers.append(timer)
                timer.start()
                raise error

            def commands():
                yield 'block', [sys.executable, str(root/'block.py')]
                if communication:
                    return
                if during_iteration:
                    ready_then_fail()
                yield 'missing', ['nonexistent-fixture-command']

            def launch(argv, *args, **kwargs):
                if argv == ['nonexistent-fixture-command']:
                    ready_then_fail()
                process = real_popen(argv, *args, **kwargs)
                if communication and str(root/'block.py') in argv:
                    replaced_communicators.append(process)
                    process.communicate = lambda *a, **kw: ready_then_fail()
                return process

            try:
                with patch.object(runner, 'jobs', return_value=2), \
                        patch.object(runner.subprocess, 'Popen', side_effect=launch):
                    with self.assertRaises(FileNotFoundError) as caught:
                        runner.run_all(commands(), cwd=root)
                self.assertIs(caught.exception, error)
                self.assertFalse((root/'release').exists(), 'waited for fixture rescue')
                self.assertTrue(wait_for(lambda: not any(o.alive() for o in observers), 1),
                                'active tree survived command failure')
            finally:
                for timer in timers:
                    timer.cancel()
                    timer.join()
                (root/'release').touch()
                self.assertTrue(wait_for(lambda: not any(o.alive() for o in observers), 20))
                for observer in observers:
                    observer.close()
                # This fixture replaced communicate before it could install
                # its reader/pipe cleanup, so release that fixture-owned pipe.
                for process in replaced_communicators:
                    process.wait(timeout=2)
                    process.stdout.close()

    def test_command_iteration_failure_stops_already_submitted_script(self):
        self.exercise_start_failure(during_iteration=True)

    def test_worker_launch_failure_stops_other_active_tree(self):
        self.exercise_start_failure(during_iteration=False)

    def test_output_failure_keeps_live_script_registered_for_cleanup(self):
        self.exercise_start_failure(during_iteration=False, communication=True)


if __name__ == "__main__":
    unittest.main()
