"""Observe real isolated-module descendants after successful and failed CLI exits."""
import json
import os
import select
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path


class ProcessHandle:
    def __init__(self, pid):
        self.queue = select.kqueue()
        self.exited = False
        try:
            self.queue.control([select.kevent(pid, filter=select.KQ_FILTER_PROC,
                flags=select.KQ_EV_ADD | select.KQ_EV_ENABLE | select.KQ_EV_ONESHOT,
                fflags=select.KQ_NOTE_EXIT)], 0, 0)
        except BaseException:
            self.queue.close()
            raise
    def ready(self):
        self.exited = self.exited or bool(self.queue.control([], 1, 0))
        return self.exited
    def close(self):
        self.queue.close()
def open_process(pid):
    return ProcessHandle(pid)
def process_select(handles, write, error, timeout):
    import time
    deadline = time.monotonic() + timeout
    while True:
        ready = [h for h in handles if h.ready()]
        if ready or time.monotonic() >= deadline:
            return ready, [], []
        time.sleep(.005)

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/run_isolated_tests.py"

# Every fixture has a 30-second emergency lifetime. The assertions run before
# release, using retained pidfds rather than PID existence or eventual self-exit.
SOLVER = '''import os, subprocess, sys, time
from pathlib import Path
root = Path(sys.argv[1])
if sys.argv[2] == "child":
    grand = subprocess.Popen([sys.executable, __file__, str(root), "grand"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    (root / "grand.pid").write_text(str(grand.pid))
    (root / "child-ready").touch()
else:
    (root / "grand-ready").touch()
for _ in range(3000):
    if (root / "solver-release").exists():
        break
    time.sleep(.01)
if sys.argv[2] == "child":
    grand.wait(timeout=5)
'''
MODULE = '''import json, os, subprocess, sys, time, unittest
from pathlib import Path

class ProcessHandle:
    def __init__(self, pid):
        self.queue = select.kqueue()
        self.exited = False
        try:
            self.queue.control([select.kevent(pid, filter=select.KQ_FILTER_PROC,
                flags=select.KQ_EV_ADD | select.KQ_EV_ENABLE | select.KQ_EV_ONESHOT,
                fflags=select.KQ_NOTE_EXIT)], 0, 0)
        except BaseException:
            self.queue.close()
            raise
    def ready(self):
        self.exited = self.exited or bool(self.queue.control([], 1, 0))
        return self.exited
    def close(self):
        self.queue.close()
def open_process(pid):
    return ProcessHandle(pid)
def process_select(handles, write, error, timeout):
    import time
    deadline = time.monotonic() + timeout
    while True:
        ready = [h for h in handles if h.ready()]
        if ready or time.monotonic() >= deadline:
            return ready, [], []
        time.sleep(.005)

class T(unittest.TestCase):
    def test_solver(self):
        root = Path(__file__).resolve().parent.parent
        child = subprocess.Popen([sys.executable, str(root / "solver.py"), str(root), "child"],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(2000):
            if (root / "grand-ready").exists() and (root / "child-ready").exists():
                break
            time.sleep(.01)
        else:
            self.fail("grandchild readiness timeout")
        pids = [os.getpid(), child.pid, int((root / "grand.pid").read_text())]
        (root / "ready.tmp").write_text(json.dumps(pids))
        (root / "ready.tmp").rename(root / "ready.json")
        for _ in range(2000):
            if (root / "module-release").exists():
                break
            time.sleep(.01)
        else:
            self.fail("module release timeout")
        if (root / "join").exists():
            (root / "solver-release").touch()
            child.wait(timeout=5)
        print("literal module output", flush=True)
        if (root / "fail").exists():
            self.fail("literal module failure")
'''


def await_file(path):
    for _ in range(1000):
        if path.exists():
            return
        time.sleep(.01)
    raise AssertionError("fixture readiness timeout: " + str(path))


def terminated(handles, timeout=2):
    """pidfds become readable at exit, including unreaped orphan zombies."""
    pending = set(handles)
    for _ in range(len(handles)):
        readable, _, _ = process_select(list(pending), [], [], timeout)
        pending.difference_update(readable)
        if not pending:
            return True
    return not pending


@unittest.skipUnless(sys.platform == "darwin" and hasattr(select, "kqueue"),
                     "macOS retained kqueue process-exit events required")
class ExitCleanupTests(unittest.TestCase):
    def exercise(self, failed=False, joined=False, replacement=None, following=False):
        with tempfile.TemporaryDirectory(prefix="isolated-exit-") as temporary:
            root = Path(temporary)
            (root / "scripts").mkdir()
            (root / "tests").mkdir()
            script = root / "scripts/run_isolated_tests.py"
            shutil.copyfile(RUNNER, script)
            if replacement:
                text = script.read_text()
                marker = "\ndef run_modules("
                self.assertEqual(text.count(marker), 1)
                script.write_text(text.replace(marker, replacement + marker))
            (root / "solver.py").write_text(SOLVER)
            (root / "tests/test_fixture.py").write_text(MODULE)
            if following:
                (root / "tests/test_z_follow.py").write_text('''import json, os, select, unittest
from pathlib import Path

class ProcessHandle:
    def __init__(self, pid):
        self.queue = select.kqueue()
        self.exited = False
        try:
            self.queue.control([select.kevent(pid, filter=select.KQ_FILTER_PROC,
                flags=select.KQ_EV_ADD | select.KQ_EV_ENABLE | select.KQ_EV_ONESHOT,
                fflags=select.KQ_NOTE_EXIT)], 0, 0)
        except BaseException:
            self.queue.close()
            raise
    def ready(self):
        self.exited = self.exited or bool(self.queue.control([], 1, 0))
        return self.exited
    def close(self):
        self.queue.close()
def open_process(pid):
    return ProcessHandle(pid)
def process_select(handles, write, error, timeout):
    import time
    deadline = time.monotonic() + timeout
    while True:
        ready = [h for h in handles if h.ready()]
        if ready or time.monotonic() >= deadline:
            return ready, [], []
        time.sleep(.005)

class T(unittest.TestCase):
    def test_previous_solver_stopped(self):
        root = Path(__file__).resolve().parent.parent
        pids = json.loads((root / "ready.json").read_bytes())[1:]
        for pid in pids:
            try:
                handle = open_process(pid)
            except ProcessLookupError:
                continue
            try:
                self.assertEqual(process_select([handle], [], [], 0)[0], [handle])
            finally:
                handle.close()
''')
            for flag, enabled in (("fail", failed), ("join", joined)):
                if enabled:
                    (root / flag).touch()
            process = subprocess.Popen([sys.executable, "-B", str(script), "--workers", "1"],
                                       cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       start_new_session=True)
            handles, pids = [], []
            try:
                await_file(root / "ready.json")
                pids = json.loads((root / "ready.json").read_bytes())
                for pid in pids:
                    handles.append(open_process(pid))
                self.assertEqual([os.getpgid(pid) for pid in pids], [pids[0]] * 3)
                self.assertEqual(process_select(handles, [], [], 0)[0], [])
                (root / "module-release").touch()
                out, err = process.communicate(timeout=10)
                return process.returncode, out, err, terminated(handles)
            finally:
                self.cleanup(root, process, pids, handles)

    def cleanup(self, root, process, pids, handles):
        (root / "module-release").touch()
        (root / "solver-release").touch()
        # Target only this fixture's known sessions. Never trust the runner's
        # cleanup for a mutation control or a failing regression.
        try:
            for group in (pids[:1] + [process.pid]):
                try:
                    os.killpg(group, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            process.communicate(timeout=5)
            if handles:
                self.assertTrue(terminated(handles, 5), "fixture cleanup failed")
        finally:
            for handle in handles:
                handle.close()

    def assert_result(self, failed=False, joined=False, replacement=None):
        code, out, err, quiet = self.exercise(failed, joined, replacement)
        self.assertEqual(code, 1 if failed else 0, err.decode())
        self.assertIn(b"literal module output\n", out)
        if failed:
            self.assertIn(b"literal module failure", err)
            self.assertIn(b"Failed modules: test_fixture.py", err)
            self.assertNotIn(b"PASS all", out)
        else:
            self.assertIn(b"PASS all 1 test modules in isolated interpreters", out)
        self.assertTrue(quiet, "ordinary solver survived module completion")

    def test_success_stops_exited_leaders_child_and_grandchild(self):
        self.assert_result()

    def test_failure_stops_exited_leaders_child_and_grandchild(self):
        self.assert_result(failed=True)

    def test_joined_completion_retains_success_and_output(self):
        self.assert_result(joined=True)

    def test_cleanup_finishes_before_next_queued_module(self):
        code, out, err, quiet = self.exercise(following=True)
        self.assertEqual(code, 0, err.decode())
        self.assertIn(b"PASS all 2 test modules in isolated interpreters", out)
        self.assertTrue(quiet)

    def test_parent_only_cleanup_is_detected(self):
        replacement = '''
def stop_module(process):
    if process.poll() is None:
        process.kill()
    process.wait(timeout=2)
'''
        with self.assertRaisesRegex(AssertionError, "ordinary solver survived"):
            self.assert_result(replacement=replacement)

    def test_cleanup_denial_cannot_report_success(self):
        replacement = '''
def stop_module(process):
    raise PermissionError("injected exit cleanup denial")
'''
        code, out, err, quiet = self.exercise(replacement=replacement)
        self.assertNotEqual(code, 0)
        self.assertIn(b"injected exit cleanup denial", err)
        self.assertNotIn(b"PASS all", out)
        self.assertFalse(quiet, "denied cleanup must leave the fault observable")


if __name__ == "__main__":
    unittest.main()
