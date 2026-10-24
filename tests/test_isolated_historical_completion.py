"""Real skip-clones wrapper completion, authentication, and mutation controls.

Maintainer integration of ywz65's PR2579, with OpenAI Codex assistance.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('completion_history', ROOT/'scripts/replay_historical_check.py')
history = importlib.util.module_from_spec(spec)
spec.loader.exec_module(history)


class HistoricalCompletionTests(unittest.TestCase):
    def run_case(self, body, *, corrupt=False, fake_wrapper=False, route="skip-clones-tests"):
        pattern = "test_skip_clones.py" if route == "skip-clones-tests" else "test_" + route.removeprefix("legacy-test-").replace("-", "_") + ".py"
        config = history.CONFIG[route]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            names = ['scripts/run_isolated_tests.py', 'scripts/research_package.py', 'scripts/replay_historical_check.py',
                     'research/skip-clones/SOURCE.json']
            for entry in [config, *config.get('additional_inputs', [])]:
                names.extend([entry['path'], entry['manifest'], entry['input'] if entry.get('input_from_root') else 'scripts/historical-ci-inputs/' + entry['input']])
            names = list(dict.fromkeys(names))
            for name in names:
                target = root/name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT/name, target)
            (root/'tests').mkdir()
            (root/'tests'/pattern).write_text(body, encoding='utf-8')
            if corrupt:
                with (root/config['input']).open('ab') as f:
                    f.write(b'\n# invalidated historical baseline\n')
            if fake_wrapper:
                (root/'scripts/replay_historical_check.py').write_text('raise SystemExit(0)\n')
            subprocess.run(['git','init','-q'], cwd=root, check=True)
            subprocess.run(['git','add','.'], cwd=root, check=True)
            tracked = subprocess.check_output(['git','ls-files','-z'], cwd=root).decode().split('\0')[:-1]
            before = {name: (root/name).read_bytes() for name in tracked}
            result = subprocess.run([sys.executable, '-I', '-O', '-B',
                str(root/'scripts/run_isolated_tests.py'), '--workers', '1'], cwd=root,
                capture_output=True, timeout=30)
            self.assertEqual(before, {name: (root/name).read_bytes() for name in tracked})
            return result

    def test_completed_historical_module_uses_exact_overlay(self):
        config = history.CONFIG['skip-clones-tests']
        body = ('import hashlib, unittest\nfrom pathlib import Path\n'
                'class T(unittest.TestCase):\n'
                ' def test_overlay(self):\n'
                f'  self.assertEqual(hashlib.sha256(Path({config["path"]!r}).read_bytes()).hexdigest(), {config["sha256"]!r})\n')
        r = self.run_case(body)
        self.assertEqual(r.returncode, 0, r.stderr.decode())
        self.assertIn(b'PASS_HISTORICAL_CHECK skip-clones-tests', r.stdout)
        self.assertIn(b'PASS all 1 test modules', r.stdout)

    def test_historical_discovery_zero_exit_rejects(self):
        r = self.run_case('def load_tests(loader, tests, pattern):\n raise SystemExit(0)\n')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn(b'Incomplete unittest run', r.stderr)
        self.assertNotIn(b'PASS_HISTORICAL_CHECK', r.stdout)
        self.assertNotIn(b'PASS all', r.stdout)

    def test_historical_execution_zero_exit_rejects(self):
        r = self.run_case('import unittest, os\nclass T(unittest.TestCase):\n def test_exit(self):\n  os._exit(0)\n')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn(b'Incomplete unittest run', r.stderr)
        self.assertNotIn(b'PASS all', r.stdout)

    def test_baseline_authentication_still_precedes_execution(self):
        r = self.run_case('raise RuntimeError("must not run")\n', corrupt=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn(b'Changed historical input', r.stderr)
        self.assertNotIn(b'RuntimeError: must not run', r.stderr)

    def test_completed_test_cannot_hide_overlay_mutation(self):
        r = self.run_case('import unittest\nfrom pathlib import Path\nclass T(unittest.TestCase):\n'
                         ' def test_mutate(self):\n  Path("scripts/exclusion_circuit.py").write_text("changed")\n')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn(b'Replay changed tracked artifact', r.stderr)
        self.assertNotIn(b'PASS all', r.stdout)

    def test_all_new_routes_require_actual_test_completion(self):
        for slug in ('copied-fixed', 'copied-fixed-reversed', 'skip-strips',
                     'skip-suffix', 'pair-assembly', 'split-skip'):
            route = 'legacy-test-' + slug
            with self.subTest(route=route, outcome='complete'):
                r = self.run_case('import unittest\n', route=route)
                self.assertEqual(r.returncode, 0, r.stderr.decode())
                self.assertIn(('PASS_HISTORICAL_CHECK ' + route).encode(), r.stdout)
            with self.subTest(route=route, outcome='early-exit'):
                r = self.run_case('def load_tests(loader, tests, pattern):\n raise SystemExit(0)\n', route=route)
                self.assertNotEqual(r.returncode, 0)
                self.assertIn(b'Incomplete unittest run', r.stderr)
                self.assertNotIn(b'PASS all', r.stdout)

    def test_wrapper_zero_exit_without_child_receipt_rejects(self):
        r = self.run_case('import unittest\n', fake_wrapper=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn(b'Incomplete unittest run', r.stderr)
        self.assertNotIn(b'PASS all', r.stdout)


if __name__ == '__main__':
    unittest.main()
