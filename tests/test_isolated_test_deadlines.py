"""Real hung-module and queued-module deadline controls, without expensive research replays."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('deadline_runner', ROOT/'scripts/run_isolated_tests.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

# Windows launches the lifetime supervisor and ownership gate before discovery.
# Keep a healthy fixture comfortably within its budget; the hung fixture still
# exhausts the entire same budget before a queued module receives a fresh one.
SHORT_BUDGET = 3 if os.name == 'nt' else 1


class DeadlineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.tests = self.root/'tests'
        self.tests.mkdir()

    def module(self, name, body):
        path = self.tests/name
        path.write_text(body)
        return path

    def run_modules(self, files, **kwargs):
        return runner.run_modules(files, tests_dir=self.tests, cwd=self.root, **kwargs)

    def test_hung_module_fails_and_other_module_finishes_with_output(self):
        hung = self.module('test_a.py', 'import time\nprint("before hang", flush=True)\ntime.sleep(60)\n')
        passed = self.module('test_b.py', 'import unittest\nclass Test(unittest.TestCase):\n def test_ok(self): print("ran other", flush=True)\n')
        start = time.monotonic()
        rows = self.run_modules([hung, passed], workers=2, module_timeout=SHORT_BUDGET)
        self.assertLess(time.monotonic()-start, SHORT_BUDGET + 7)
        self.assertEqual([r[1] for r in rows], [124, 0])
        self.assertIn(b'before hang', rows[0][2])
        self.assertIn(f'Module timeout after {SHORT_BUDGET}s'.encode(), rows[0][3])
        self.assertIn(b'ran other', rows[1][2])

    def test_queue_wait_does_not_consume_next_modules_budget(self):
        # First module exhausts its entire budget before the next is launched.
        hung = self.module('test_a.py', 'import time\ntime.sleep(60)\n')
        passed = self.module('test_b.py', 'import time, unittest\ntime.sleep(.2)\nclass Test(unittest.TestCase):\n def test_ok(self): pass\n')
        rows = self.run_modules([hung, passed], workers=1, module_timeout=SHORT_BUDGET)
        self.assertEqual([r[1] for r in rows], [124, 0])

    def test_success_failure_and_early_exit_keep_their_meaning(self):
        files = [self.module('test_ok.py', 'import unittest\nclass T(unittest.TestCase):\n def test_ok(self): pass\n'),
                 self.module('test_fail.py', 'import unittest\nclass T(unittest.TestCase):\n def test_fail(self): self.fail("expected")\n'),
                 self.module('test_exit.py', 'import os\nos._exit(0)\n')]
        rows = self.run_modules(files, workers=2, module_timeout=5)
        self.assertEqual([r[1] for r in rows], [0, 1, 1])
        self.assertIn(b'Incomplete unittest run', rows[2][3])

    def test_invalid_budgets_rejected_before_launch(self):
        for value in [0, -1, float('nan'), float('inf'), '-inf']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.run_modules([], module_timeout=value)

    @unittest.skipUnless(os.name == 'posix', 'POSIX cleanup after leader exit')
    def test_completed_receipt_with_open_child_pipe_is_cleaned_before_deadline(self):
        path = self.module('test_pipe.py',
            'import subprocess, sys, unittest\n'
            'subprocess.Popen([sys.executable,"-c","import time; time.sleep(60)"])\n'
            'class T(unittest.TestCase):\n def test_ok(self): pass\n')
        rows = self.run_modules([path], workers=1, module_timeout=3)
        self.assertEqual(rows[0][1], 0)
        self.assertIn(b'OK', rows[0][3])
        self.assertNotIn(b'Module timeout', rows[0][3])

    @unittest.skipUnless(sys.platform == 'linux', 'Linux process state observation')
    def test_ordinary_child_is_stopped_on_timeout(self):
        # A PID marker lets the parent check that the ordinary child stopped.
        body = ('import subprocess,sys,time\nfrom pathlib import Path\n'
                'p=subprocess.Popen([sys.executable,"-c","import time; time.sleep(60)"],'
                'stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)\n'
                'Path("child.pid").write_text(str(p.pid))\ntime.sleep(60)\n')
        path = self.module('test_child.py', body)
        rows = self.run_modules([path], workers=1, module_timeout=1)
        self.assertEqual(rows[0][1], 124)
        pid = int((self.root/'child.pid').read_text())
        status = Path('/proc')/str(pid)/'stat'
        if status.exists():
            self.assertEqual(status.read_text().split()[2], 'Z')

    def test_cli_reports_timeout_and_nonzero_exit(self):
        scripts = self.root/'scripts'; scripts.mkdir()
        (scripts/'run_isolated_tests.py').write_bytes((ROOT/'scripts/run_isolated_tests.py').read_bytes())
        (scripts/'research_package.py').write_bytes((ROOT/'scripts/research_package.py').read_bytes())
        self.module('test_hang.py', 'import time\nprint("diagnostic", flush=True)\ntime.sleep(60)\n')
        result = subprocess.run([sys.executable, str(scripts/'run_isolated_tests.py'),
                                 '--workers', '1', '--module-timeout', str(SHORT_BUDGET)],
                                capture_output=True, timeout=SHORT_BUDGET + 9)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b'diagnostic', result.stdout)
        self.assertIn(b'Module timeout', result.stderr)
        self.assertIn(b'Failed modules: test_hang.py', result.stderr)


if __name__ == '__main__':
    unittest.main()
