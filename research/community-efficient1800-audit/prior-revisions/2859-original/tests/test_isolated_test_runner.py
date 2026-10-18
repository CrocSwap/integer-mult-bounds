"""Behavior tests for scripts/run_isolated_tests.py.

The runner executes every test module in a fresh interpreter. These tests
exercise the runner end to end in a sandbox (a copied runner plus a tiny
tests/ directory) so the real suite is never re-run inside a test.

They guard three obligations:
1. Coverage and failure detection: every discovered module runs in its own
   process and every failing module is reported.
2. Concurrency: modules are scheduled concurrently (the reason the change
   exists), with the exact same per-module command.
3. Receipt stability: stdout blocks stay contiguous per module in sorted
   module order and the summary lines are unchanged.
"""
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / 'scripts' / 'run_isolated_tests.py'

PASS_MODULE = '''import unittest

class T(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(2 + 2, 4)
'''

FAIL_MODULE = '''import unittest

class T(unittest.TestCase):
    def test_fail(self):
        self.fail('deliberate negative control')
'''

BARRIER_MODULE = '''import os
import time
import unittest
from pathlib import Path

class T(unittest.TestCase):
    def test_arrive(self):
        d = Path(os.environ['ARRIVE_DIR'])
        d.mkdir(exist_ok=True)
        (d / Path(__file__).stem).write_text('x')
        deadline = time.time() + 8
        while time.time() < deadline:
            if len(list(d.iterdir())) >= 3:
                return
            time.sleep(0.05)
        self.fail('barrier timeout: test modules did not run concurrently')
'''


class Sandbox:
    def __init__(self, tmp, modules):
        scripts = tmp / 'scripts'
        scripts.mkdir()
        shutil.copyfile(RUNNER, scripts / 'run_isolated_tests.py')
        tests = tmp / 'tests'
        tests.mkdir()
        for name, body in modules.items():
            (tests / name).write_text(body, encoding='utf-8')
        self.tmp = tmp

    def run(self, *args, env=None, timeout=180):
        merged = dict(os.environ)
        if env:
            merged.update(env)
        return subprocess.run(
            [sys.executable, '-B', str(self.tmp / 'scripts' / 'run_isolated_tests.py'), *args],
            cwd=self.tmp, capture_output=True, timeout=timeout, env=merged)


class IsolatedRunnerTest(unittest.TestCase):
    def setUp(self):
        import tempfile
        self._td = tempfile.TemporaryDirectory()
        self.tmp = Path(self._td.name)

    def tearDown(self):
        self._td.cleanup()

    def sandbox(self, modules):
        return Sandbox(self.tmp, modules)

    def test_every_module_runs_and_every_failure_is_reported(self):
        box = self.sandbox({
            'test_a_pass.py': PASS_MODULE,
            'test_b_pass.py': PASS_MODULE,
            'test_c_fail.py': FAIL_MODULE,
        })
        result = box.run('--workers', '3')
        self.assertNotEqual(result.returncode, 0)
        out = result.stdout.decode()
        err = result.stderr.decode()
        names = ['test_a_pass.py', 'test_b_pass.py', 'test_c_fail.py']
        positions = [out.index('Checking ' + n) for n in names]
        self.assertEqual(positions, sorted(positions))
        self.assertIn('Failed modules: test_c_fail.py', err)
        self.assertIn('deliberate negative control', err)

    def test_modules_are_scheduled_concurrently(self):
        box = self.sandbox({
            'test_arrive_1.py': BARRIER_MODULE,
            'test_arrive_2.py': BARRIER_MODULE,
            'test_arrive_3.py': BARRIER_MODULE,
        })
        arrive = self.tmp / 'arrive'
        result = box.run('--workers', '3', env={'ARRIVE_DIR': str(arrive)}, timeout=120)
        self.assertEqual(
            result.returncode, 0,
            'concurrent scheduling broken (or --workers rejected): '
            + result.stderr.decode()[-500:])
        self.assertIn('PASS all 3 test modules in isolated interpreters',
                      result.stdout.decode())

    def test_default_invocation_keeps_receipt_and_summary(self):
        box = self.sandbox({
            'test_a_pass.py': PASS_MODULE,
            'test_b_fail.py': FAIL_MODULE,
        })
        result = box.run()
        self.assertEqual(result.returncode, 1)
        lines = result.stdout.decode().splitlines()
        self.assertEqual(lines[0], 'Checking test_a_pass.py')
        self.assertIn('Checking test_b_fail.py', lines)
        self.assertFalse(any(line.startswith('PASS all') for line in lines))
        self.assertIn('Failed modules: test_b_fail.py', result.stderr.decode())

    def test_same_named_synthetic_clone_test_still_fails(self):
        # A name alone must not trigger the production historical overlay.
        box = self.sandbox({'test_skip_clones.py': FAIL_MODULE})
        result = box.run('--workers', '1')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('deliberate negative control', result.stderr.decode())
        self.assertIn('Failed modules: test_skip_clones.py', result.stderr.decode())

    def test_frozen_family_routing_preserves_failure_reporting(self):
        box = self.sandbox({'test_split_skip.py': FAIL_MODULE,
                            'test_regular.py': PASS_MODULE})
        manifest = self.tmp / 'research/skip-clones/SOURCE.json'
        manifest.parent.mkdir(parents=True)
        manifest.write_text('{}')
        (self.tmp / 'scripts/replay_historical_check.py').write_text(
            "import sys\nprint('historical route: ' + sys.argv[1])\n"
            "raise SystemExit(7)\n")
        result = box.run('--workers', '2')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('historical route: legacy-test-split-skip', result.stdout.decode())
        self.assertIn('Failed modules: test_split_skip.py', result.stderr.decode())
        self.assertNotIn('deliberate negative control', result.stderr.decode())
        self.assertIn('Ran 1 test', result.stderr.decode())

    def test_inherited_optimization_cannot_hide_verifier_assertions(self):
        # Research tests call verifiers that still use Python assert. The
        # outer runner itself may be optimized, but its checks must not be.
        box = self.sandbox({'test_assertion.py': '''import os
import unittest

class T(unittest.TestCase):
    def test_verifier(self):
        self.assertEqual(os.environ.get('REPLAY_SENTINEL'), 'preserved')
        assert False, 'deliberate mathematical assertion'
'''})
        for level in ('1', '2'):
            with self.subTest(level=level):
                result = box.run('--workers', '1', env={
                    'PYTHONOPTIMIZE': level, 'REPLAY_SENTINEL': 'preserved'})
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('deliberate mathematical assertion', result.stderr.decode())
                self.assertIn('Failed modules: test_assertion.py', result.stderr.decode())


if __name__ == '__main__':
    unittest.main()
