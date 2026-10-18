"""Native Windows replay lifetime controls; ywz65 / OpenAI Codex, Apache-2.0."""
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import research_package as package
sys.path.pop(0)

TREE = r"""
from pathlib import Path
import os, subprocess, sys, time
root, depth, mode = Path(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
(root / f'{depth}.pid').write_text(str(os.getpid()))
child = (subprocess.Popen([sys.executable, __file__, str(root), str(depth-1), mode])
         if depth else None)
if depth == 0:
    (root / 'ready').touch()
deadline = time.monotonic() + 60
while not (root / 'observed').exists() and time.monotonic() < deadline:
    time.sleep(.01)
if depth == 2 and mode in ('0', '7'):
    raise SystemExit(int(mode))
while not (root / 'release').exists() and time.monotonic() < deadline:
    time.sleep(.01)
if child is not None:
    child.wait(timeout=5)
"""


def wait_for(predicate, seconds=10):
    deadline = time.monotonic() + seconds
    while not predicate():
        if time.monotonic() >= deadline:
            raise AssertionError("fixture readiness timed out")
        time.sleep(.01)


@unittest.skipUnless(sys.platform == "win32", "requires native Windows Job Objects")
class WindowsJobTests(unittest.TestCase):
    def fixture(self, mode="0", interrupt=False, mutate=False):
        api = ctypes.WinDLL("kernel32", use_last_error=True)
        api.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        api.OpenProcess.restype = wintypes.HANDLE
        api.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        api.WaitForSingleObject.restype = wintypes.DWORD
        api.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
        api.TerminateProcess.restype = wintypes.BOOL
        api.CloseHandle.argtypes = [wintypes.HANDLE]
        api.CloseHandle.restype = wintypes.BOOL
        handles, failures = [], []
        real_popen = subprocess.Popen

        def alive(handle):
            status = api.WaitForSingleObject(handle, 0)
            self.assertIn(status, (0, 258), "native process observer failed")
            return status == 258

        with tempfile.TemporaryDirectory(prefix="job tree ") as tmp:
            root = Path(tmp)
            script = root / "tree.py"
            script.write_text(TREE, encoding="utf-8")

            def observe():
                try:
                    wait_for((root / "ready").exists)
                    pids = [int((root / f"{depth}.pid").read_text()) for depth in range(3)]
                    self.assertEqual(len(set(pids)), 3)
                    for pid in pids:
                        handle = api.OpenProcess(0x00100001, False, pid)
                        if not handle:
                            raise ctypes.WinError(ctypes.get_last_error())
                        handles.append(handle)
                        self.assertTrue(alive(handle))
                    (root / "observed").touch()
                    if mode == "joined":
                        (root / "release").touch()
                except BaseException as exc:
                    failures.append(exc)

            def launch(*args, **kwargs):
                process = real_popen(*args, **kwargs)
                real_wait = process.wait

                def ready_wait(timeout=None):
                    process.wait = real_wait
                    wait_for(lambda: (root / "observed").exists() or failures)
                    if failures:
                        raise failures[0]
                    if interrupt:
                        raise KeyboardInterrupt("controlled interruption after readiness")
                    return real_wait(timeout=timeout)

                process.wait = ready_wait
                return process

            def leader_only(argv, cwd, timeout, env):
                process = subprocess.Popen(argv, cwd=cwd, env=env)
                try:
                    return process.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    raise ValueError("verification timed out") from None
                finally:
                    if process.poll() is None:
                        process.kill()
                    process.wait(timeout=5)

            observer = threading.Thread(target=observe)
            observer.start()
            try:
                implementation = leader_only if mutate else package.run_windows_command
                with patch.object(package.subprocess, "Popen", side_effect=launch), \
                        patch.object(package, "run_windows_command", side_effect=implementation):
                    argv = [sys.executable, str(script), str(root), "2", mode]
                    if interrupt:
                        with self.assertRaises(KeyboardInterrupt):
                            package.run_command(argv, root, 5)
                    elif mode == "timeout":
                        with self.assertRaisesRegex(ValueError, "verification timed out"):
                            package.run_command(argv, root, .05)
                    elif mode == "7":
                        with self.assertRaisesRegex(ValueError, "verification command exited 7"):
                            package.run_command(argv, root, 5)
                    else:
                        package.run_command(argv, root, 5)
                observer.join(timeout=15)
                self.assertFalse(observer.is_alive())
                self.assertFalse(failures, failures)
                self.assertEqual(len(handles), 3)
                # Native termination can precede the retained process object's
                # final signaled state; observe that completion with a bound.
                deadline = time.monotonic() + 1
                while any(alive(h) for h in handles) and time.monotonic() < deadline:
                    time.sleep(.01)
                self.assertFalse([h for h in handles if alive(h)], "live owned descendants after return")
            finally:
                (root / "release").touch()
                observer.join(timeout=15)
                for handle in handles:
                    try:
                        if alive(handle):
                            stopped = api.TerminateProcess(handle, 1)
                            if not stopped:
                                # It may have completed between observation and stop.
                                self.assertEqual(api.WaitForSingleObject(handle, 5000), 0)
                        self.assertEqual(api.WaitForSingleObject(handle, 5000), 0)
                    finally:
                        api.CloseHandle(handle)

    def test_normal_leader_exit_terminates_descendants(self):
        self.fixture("0")

    def test_failed_leader_exit_preserves_code_and_stops_descendants(self):
        self.fixture("7")

    def test_timeout_stops_complete_tree(self):
        self.fixture("timeout")

    def test_interrupted_wait_stops_complete_tree(self):
        self.fixture("timeout", interrupt=True)

    def test_fully_joined_command_is_a_positive_control(self):
        self.fixture("joined")

    def test_parent_only_mutant_is_detected_at_every_exit_boundary(self):
        for mode in ("0", "7", "timeout"):
            with self.subTest(mode=mode), self.assertRaisesRegex(AssertionError, "live owned descendants"):
                self.fixture(mode, mutate=True)

    def test_assignment_failure_never_starts_verification(self):
        real_dll = ctypes.WinDLL
        real_popen = subprocess.Popen
        started = []

        def launch(*args, **kwargs):
            process = real_popen(*args, **kwargs)
            started.append(process)
            return process

        def denied(*args):
            ctypes.set_last_error(5)
            return 0

        class Proxy:
            def __init__(self, *args, **kwargs):
                self.api = real_dll(*args, **kwargs)

            def __getattr__(self, name):
                return denied if name == "AssignProcessToJobObject" else getattr(self.api, name)

        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / "command-ran"
            command = [sys.executable, "-c", "from pathlib import Path; import sys; Path(sys.argv[1]).touch()", str(marker)]
            with patch.object(ctypes, "WinDLL", Proxy), \
                    patch.object(package.subprocess, "Popen", side_effect=launch):
                with self.assertRaises(OSError):
                    package.run_command(command, tmp, 5)
            self.assertEqual(len(started), 1)
            self.assertIsNotNone(started[0].poll(), "unassigned gated launcher survived")
            self.assertFalse(marker.exists(), "command started before job ownership")

    def test_gate_ignores_startup_hooks_but_verifier_keeps_environment(self):
        """A scheduler-delayed assignment must not expose Python startup hooks."""
        real_dll = ctypes.WinDLL
        real_popen = subprocess.Popen
        api = real_dll("kernel32", use_last_error=True)
        api.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        api.AssignProcessToJobObject.restype = wintypes.BOOL
        api.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        api.OpenProcess.restype = wintypes.HANDLE
        api.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        api.WaitForSingleObject.restype = wintypes.DWORD
        api.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
        api.TerminateProcess.restype = wintypes.BOOL
        api.CloseHandle.argtypes = [wintypes.HANDLE]
        api.CloseHandle.restype = wintypes.BOOL

        def exercise(mutate):
            with tempfile.TemporaryDirectory(prefix="gate startup ") as tmp:
                root = Path(tmp)
                pidfile = root / "startup-child.pid"
                hook = root / "sitecustomize.py"
                hook.write_text(r'''
import os, subprocess, sys
from pathlib import Path
root = Path(os.environ["RESEARCH_GATE_TEST_ROOT"])
if len(sys.argv) > 1 and sys.argv[0] == "-c" and sys.argv[1].startswith("Local\\research-replay-"):
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    child = subprocess.Popen([sys.executable, "-I", "-S", "-c", "import time; time.sleep(30)"],
                             env=env, creationflags=0x08000000)
    pending = root / "startup-child.pid.pending"
    pending.write_text(str(child.pid))
    pending.replace(root / "startup-child.pid")
else:
    (root / "verifier-hook").write_text(os.environ["RESEARCH_GATE_TEST_VALUE"])
''', encoding="utf-8")
                script = root / "verifier.py"
                script.write_text("import json, os, sys\nfrom pathlib import Path\n"
                                  "Path('verifier-result.json').write_text(json.dumps([sys.argv[1], "
                                  "os.environ['RESEARCH_GATE_TEST_VALUE']]))\n", encoding="utf-8")
                env = dict(os.environ)
                env.update(PYTHONPATH=str(root), RESEARCH_GATE_TEST_ROOT=str(root),
                           RESEARCH_GATE_TEST_VALUE="environment survives")
                handles = []

                def delayed_assign(*args):
                    # Force the unisolated mutant's pre-assignment startup order.
                    deadline = time.monotonic() + (10 if mutate else 1)
                    while not pidfile.exists() and time.monotonic() < deadline:
                        time.sleep(.01)
                    if pidfile.exists():
                        handle = api.OpenProcess(0x00100001, False, int(pidfile.read_text()))
                        if not handle:
                            raise ctypes.WinError(ctypes.get_last_error())
                        handles.append(handle)
                    return api.AssignProcessToJobObject(*args)

                class Proxy:
                    def __init__(self, *args, **kwargs):
                        self.real = real_dll(*args, **kwargs)

                    def __getattr__(self, name):
                        return delayed_assign if name == "AssignProcessToJobObject" else getattr(self.real, name)

                def launch(argv, *args, **kwargs):
                    if mutate:
                        self.assertEqual(argv[1:3], ["-I", "-S"])
                        argv = [argv[0], *argv[3:]]
                    return real_popen(argv, *args, **kwargs)

                try:
                    with patch.object(ctypes, "WinDLL", Proxy), \
                            patch.object(package.subprocess, "Popen", side_effect=launch):
                        code = package.run_windows_command(
                            [sys.executable, str(script), "argument with spaces"], root, 5, env)
                    self.assertEqual(code, 0)
                    self.assertEqual((root / "verifier-hook").read_text(), "environment survives")
                    self.assertEqual(json.loads((root / "verifier-result.json").read_text()),
                                     ["argument with spaces", "environment survives"])
                    if mutate:
                        self.assertEqual(len(handles), 1, "startup mutant did not exercise the race")
                    self.assertFalse([h for h in handles if api.WaitForSingleObject(h, 0) == 258],
                                     "unowned startup child survived gate cleanup")
                    self.assertFalse(pidfile.exists(), "gate executed environment startup hook")
                finally:
                    for handle in handles:
                        try:
                            if api.WaitForSingleObject(handle, 0) == 258:
                                self.assertTrue(api.TerminateProcess(handle, 1))
                            self.assertEqual(api.WaitForSingleObject(handle, 5000), 0)
                        finally:
                            self.assertTrue(api.CloseHandle(handle))

        exercise(False)
        with self.assertRaisesRegex(AssertionError, "unowned startup child"):
            exercise(True)


if __name__ == "__main__":
    unittest.main()
