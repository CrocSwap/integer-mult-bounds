"""Native Windows controls for the isolated runner's exited-module handoff.

Mihir Srivastava, with substantial OpenAI Codex assistance. Apache-2.0.
Reuses the readiness fixtures from Nick Petalas's POSIX exit-cleanup tests.
"""
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from test_isolated_test_exit_cleanup import MODULE, SOLVER, await_file

ROOT = Path(__file__).resolve().parents[1]


class ProcessHandles:
    """Hold process identities through exit; never infer death from PID lookup."""

    def __init__(self):
        self.api = ctypes.WinDLL("kernel32", use_last_error=True)
        self.api.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        self.api.OpenProcess.restype = wintypes.HANDLE
        self.api.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        self.api.WaitForSingleObject.restype = wintypes.DWORD
        self.api.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
        self.api.TerminateProcess.restype = wintypes.BOOL
        self.api.CloseHandle.argtypes = [wintypes.HANDLE]
        self.api.CloseHandle.restype = wintypes.BOOL
        self.handles = []

    def observe(self, pid):
        handle = self.api.OpenProcess(0x00100001, False, pid)  # SYNCHRONIZE | TERMINATE
        if not handle:
            raise ctypes.WinError(ctypes.get_last_error())
        self.handles.append(handle)
        if self.api.WaitForSingleObject(handle, 0) != 258:
            raise AssertionError("fixture process was not alive at readiness")

    def all_stopped(self):
        states = [self.api.WaitForSingleObject(handle, 0) for handle in self.handles]
        if any(state not in (0, 258) for state in states):
            raise AssertionError("native process observation failed")
        return all(state == 0 for state in states)

    def close(self):
        # Independently stop only retained fixture processes, including mutants.
        try:
            for handle in self.handles:
                if self.api.WaitForSingleObject(handle, 0) == 258:
                    if not self.api.TerminateProcess(handle, 1):
                        if self.api.WaitForSingleObject(handle, 5000) != 0:
                            raise ctypes.WinError(ctypes.get_last_error())
                if self.api.WaitForSingleObject(handle, 5000) != 0:
                    raise AssertionError("fixture process cleanup failed")
        finally:
            for handle in self.handles:
                self.api.CloseHandle(handle)


@unittest.skipUnless(os.name == "nt", "requires native Windows process handles")
class WindowsExitCleanupTests(unittest.TestCase):
    def exercise(self, failed=False, joined=False, capture=False, mutant=False, timeout=False):
        with tempfile.TemporaryDirectory(prefix="isolated windows exit ") as temporary:
            root = Path(temporary)
            scripts, tests = root / "scripts", root / "tests"
            scripts.mkdir()
            tests.mkdir()
            for name in ("run_isolated_tests.py", "research_package.py"):
                shutil.copyfile(ROOT / "scripts" / name, scripts / name)
            script = scripts / "run_isolated_tests.py"
            if mutant:
                source = script.read_text(encoding="utf-8")
                marker = "\ndef run_modules("
                self.assertEqual(source.count(marker), 1)
                source = source.replace(marker, "\ndef windows_module_command(command, python, cache):\n"
                                        "    return command\n" + marker)
                script.write_text(source, encoding="utf-8")
            solver, module = SOLVER, MODULE
            if capture:
                # Retain both capture pipes even after unittest completes.
                solver = solver.replace("stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL",
                                        "stdout=None, stderr=None")
                module = module.replace("stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL",
                                        "stdout=None, stderr=None")
            (root / "solver.py").write_text(solver, encoding="utf-8")
            (tests / "test_fixture.py").write_text(module, encoding="utf-8")
            for flag, enabled in (("fail", failed), ("join", joined)):
                if enabled:
                    (root / flag).touch()
            process = subprocess.Popen(
                [sys.executable, "-B", str(script), "--workers", "1", "--module-timeout", "5"],
                cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            observer = ProcessHandles()
            try:
                await_file(root / "ready.json")
                pids = json.loads((root / "ready.json").read_bytes())
                self.assertEqual(len(set(pids)), 3)
                for pid in pids:
                    observer.observe(pid)
                if not timeout:
                    (root / "module-release").touch()
                out, err = process.communicate(timeout=15)
                return process.returncode, out, err, observer.all_stopped()
            finally:
                (root / "module-release").touch()
                (root / "solver-release").touch()
                try:
                    observer.close()
                finally:
                    if process.poll() is None:
                        process.kill()
                    process.communicate(timeout=10)

    def assert_result(self, **kwargs):
        code, out, err, quiet = self.exercise(**kwargs)
        failed = kwargs.get("failed", False)
        self.assertEqual(code, 1 if failed else 0, err.decode())
        self.assertIn(b"literal module output", out)
        if failed:
            self.assertIn(b"literal module failure", err)
            self.assertIn(b"Failed modules: test_fixture.py", err)
            self.assertNotIn(b"PASS all", out)
        else:
            self.assertIn(b"PASS all 1 test modules in isolated interpreters", out)
        self.assertTrue(quiet, "ordinary solver survived module completion")

    def test_success_stops_exited_modules_child_and_grandchild(self):
        self.assert_result()

    def test_failure_stops_exited_modules_child_and_grandchild(self):
        self.assert_result(failed=True)

    def test_joined_completion_preserves_success_and_output(self):
        self.assert_result(joined=True)

    def test_inherited_capture_pipes_do_not_turn_success_into_timeout(self):
        self.assert_result(capture=True)

    def test_ungated_launch_mutant_is_detected(self):
        for failed in (False, True):
            with self.subTest(failed=failed):
                with self.assertRaisesRegex(AssertionError, "ordinary solver survived"):
                    self.assert_result(failed=failed, mutant=True)

    def test_timeout_stops_the_owned_tree_and_keeps_failure(self):
        code, out, err, quiet = self.exercise(timeout=True)
        self.assertNotEqual(code, 0)
        self.assertIn(b"Module timeout after 5s", err)
        self.assertNotIn(b"PASS all", out)
        self.assertTrue(quiet, "ordinary solver survived module timeout")


if __name__ == "__main__":
    unittest.main()
