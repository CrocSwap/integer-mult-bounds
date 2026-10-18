"""Portable replay and rejection tests; standard-library unittest.

Jonathan Lam, with substantial OpenAI Codex assistance; Apache-2.0.
"""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RELATIVE = HERE.relative_to(ROOT)


class ReplayPackagingTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='eisenstein-replay-test-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / 'minimal-checkout'
        self.package = self.root / RELATIVE
        shutil.copytree(HERE, self.package, ignore=shutil.ignore_patterns('__pycache__'))
        self.inputs = json.loads((HERE / 'SOURCES.json').read_text())['local_inputs']
        for item in self.inputs:
            target = self.root / item['path']
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / item['path'], target)
        self.output = Path(self.temporary.name) / 'receipt.json'
        self.output.write_text('preserve this output on failure\n')

    def run_replay(self):
        return subprocess.run(
            [sys.executable, '-O', '-B', str(self.package / 'verify.py'),
             '--write', str(self.output)],
            cwd=self.temporary.name, text=True, capture_output=True, timeout=180,
            check=False)

    def test_relocated_optimized_replay_and_export(self):
        result = self.run_replay()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('clique-method optimum 22', result.stdout)
        self.assertEqual(json.loads(self.output.read_text()),
                         json.loads((HERE / 'certificate.json').read_text()))
        self.assertFalse(list(self.root.rglob('__pycache__')))

    def test_corrupt_certificate_rejected_before_export(self):
        path = self.package / 'certificate.json'
        data = json.loads(path.read_text())
        data['dual']['flat_pairs'].pop()
        path.write_text(json.dumps(data))
        result = self.run_replay()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('committed certificate differs', result.stderr)
        self.assertEqual(self.output.read_text(), 'preserve this output on failure\n')

    def test_changed_source_rejected_before_export(self):
        path = self.root / self.inputs[0]['path']
        path.write_bytes(path.read_bytes() + b'\n# tampered source\n')
        result = self.run_replay()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('source hash mismatch', result.stderr)
        self.assertEqual(self.output.read_text(), 'preserve this output on failure\n')


if __name__ == '__main__':
    unittest.main()
