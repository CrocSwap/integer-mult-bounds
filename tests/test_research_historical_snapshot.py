"""Fresh historical replay and rejecting controls for the PR7257 repair.

Credit Clear1nsight's pinned-checkout repair and unpaidmoon's PR6292 audit.
Apache-2.0.
"""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'research/historical-selected-replay-gap'
spec = importlib.util.spec_from_file_location('historical_snapshot_checks', PACKAGE / 'verify.py')
AUDIT = importlib.util.module_from_spec(spec)
spec.loader.exec_module(AUDIT)


class HistoricalSnapshotTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='historical-snapshot-control-')
        self.addCleanup(temporary.cleanup)
        self.snapshot = Path(temporary.name) / 'snapshot'
        self.sources = json.loads((PACKAGE / 'SOURCES.json').read_bytes())
        self.runner = AUDIT.load_module(ROOT / 'scripts/research_package.py')
        self.env = self.runner.git_source_env()

    def checkout(self, sources=None):
        AUDIT.checkout_snapshot(self.snapshot, sources or self.sources, self.runner, self.env)

    def test_fresh_checkout_preserves_pins_and_complete_consumer(self):
        self.checkout()
        head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=self.snapshot,
                                       env=self.env, timeout=30).decode().strip()
        self.assertEqual(head, AUDIT.INSPECTED)
        for row in self.sources['files']:
            with self.subTest(path=row['path']):
                actual = (self.snapshot / row['path']).read_bytes()
                self.assertEqual(hashlib.sha256(actual).hexdigest(), row['sha256'])
        # Includes all 19 rejections, the nine-package plan and empty-diff case.
        AUDIT.check_snapshot(self.snapshot, self.env)

    def test_checkout_rejects_a_forged_historical_digest(self):
        sources = copy.deepcopy(self.sources)
        sources['files'][0]['sha256'] = '0' * 64
        with self.assertRaisesRegex(SystemExit, 'historical checkout source digest changed: Makefile'):
            self.checkout(sources)

    def test_consumer_rejects_changed_selected_checker(self):
        self.checkout()
        path = self.snapshot / AUDIT.SELECTED_PATH
        path.write_bytes(path.read_bytes() + b'\n')
        with self.assertRaisesRegex(SystemExit, 'live selected checker digest changed'):
            AUDIT.check_snapshot(self.snapshot, self.env)

    def test_optimized_cli_still_rejects_disabled_assertions(self):
        result = subprocess.run([sys.executable, '-O', '-B', str(PACKAGE / 'verify.py')],
                                cwd=ROOT, capture_output=True, timeout=30)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b'assertions must stay enabled', result.stderr)
        self.assertNotIn(b'PASS_HISTORICAL_SELECTED_REPLAY_GAP', result.stdout)


if __name__ == '__main__':
    unittest.main()
