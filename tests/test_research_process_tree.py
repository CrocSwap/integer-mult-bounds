"""Linux process-tree failure controls for bounded research-package replay.

Paul Romeo, with substantial OpenAI Codex assistance. Apache-2.0.
Leader-exit and interruption controls by yssite, with OpenAI Codex assistance.
"""
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import research_package as package
sys.path.pop(0)

KILL_GROUP = getattr(os, "killpg", None)
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
if len(sys.argv) == 4:
    while not (root / "ready").exists():
        time.sleep(0.01)
    sys.exit(int(sys.argv[3]))
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


def alive(pid):
    try:
        # A killed orphan can remain a zombie until the system reaps it.
        state = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[0]
        return state not in ("Z", "X")
    except (FileNotFoundError, ProcessLookupError):
        return False


@unittest.skipUnless(sys.platform == "linux", "requires Linux /proc process states")
class ProcessTreeTests(unittest.TestCase):
    def exercise_tree(self, complete=False, leader_exit=None, interrupt=False):
        process, owned_group, pids = None, False, []
        real_popen = subprocess.Popen
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script = root / "tree.py"
            script.write_text(TREE)

            def started(*args, **kwargs):
                nonlocal process, owned_group, pids
                process = real_popen(*args, **kwargs)
                owned_group = os.getpgid(process.pid) == process.pid
                self.assertTrue(owned_group, "fixture must own its process group")
                self.assertTrue(wait_for((root / "ready").exists, timeout=30), "tree never became ready")
                pids = [int((root / f"{depth}.pid").read_text()) for depth in range(3)]
                self.assertEqual(pids[2], process.pid)
                for pid in pids:
                    if pid != process.pid or leader_exit is None:
                        self.assertTrue(alive(pid))
                    self.assertEqual(os.getpgid(pid), process.pid)
                    self.assertEqual(os.getsid(pid), process.pid)
                if complete:
                    (root / "release").touch()
                if interrupt:
                    real_wait = process.wait

                    def interrupted_wait(*args, **kwargs):
                        # One interruption after readiness; cleanup must still
                        # reap the real leader using its ordinary wait method.
                        process.wait = real_wait
                        raise KeyboardInterrupt

                    process.wait = interrupted_wait
                return process

            try:
                # Start the timeout clock only after both descendants exist.
                with patch.object(package.subprocess, "Popen", side_effect=started):
                    argv = [sys.executable, str(script), str(root), "2"]
                    if leader_exit is not None:
                        argv.append(str(leader_exit))
                        if leader_exit:
                            with self.assertRaisesRegex(ValueError, f"exited {leader_exit}"):
                                package.run_command(argv, root, 5)
                        else:
                            package.run_command(argv, root, 5)
                    elif interrupt:
                        with self.assertRaises(KeyboardInterrupt):
                            package.run_command(argv, root, 5)
                    elif complete:
                        package.run_command(argv, root, 5)
                    else:
                        with self.assertRaisesRegex(ValueError, "verification timed out"):
                            package.run_command(argv, root, 0.05)
                wait_for(lambda: not any(alive(pid) for pid in pids), timeout=1)
                self.assertFalse([pid for pid in pids if alive(pid)], "live descendants after replay")
            finally:
                (root / "release").touch()
                if process is not None:
                    try:
                        if owned_group:
                            KILL_GROUP(process.pid, signal.SIGKILL)
                        else:
                            process.kill()
                    except ProcessLookupError:
                        pass
                    process.wait(timeout=5)
                    self.assertTrue(wait_for(lambda: not any(alive(pid) for pid in pids)),
                                    "fixture cleanup failed")

    def test_successful_tree_completion(self):
        self.exercise_tree(complete=True)

    def test_timeout_terminates_descendants(self):
        self.exercise_tree()

    def test_successful_leader_exit_terminates_descendants(self):
        self.exercise_tree(leader_exit=0)

    def test_failed_leader_exit_terminates_descendants(self):
        self.exercise_tree(leader_exit=7)

    def test_interruption_terminates_descendants(self):
        self.exercise_tree(interrupt=True)

    def test_leader_only_cleanup_is_detected_after_exit(self):
        for code in (0, 7):
            with self.subTest(code=code), patch.object(package.os, "killpg", os.kill):
                with self.assertRaisesRegex(AssertionError, "live descendants after replay"):
                    self.exercise_tree(leader_exit=code)

    def test_parent_only_cleanup_is_detected(self):
        with patch.object(package.os, "killpg", os.kill):
            with self.assertRaisesRegex(AssertionError, "live descendants after replay"):
                self.exercise_tree()


if __name__ == "__main__":
    unittest.main()
