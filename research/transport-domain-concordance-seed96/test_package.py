"""Subprocess integrity and relocation checks for the small concordance package.

Hanson Sun with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REL = HERE.relative_to(ROOT)
WORD = Path('research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz')


class PackageIntegrity(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='transport concordance ')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.package = self.root / REL
        shutil.copytree(HERE, self.package, ignore=shutil.ignore_patterns('__pycache__'))
        (self.root / WORD).parent.mkdir(parents=True)
        shutil.copyfile(ROOT / WORD, self.root / WORD)

    def invoke(self):
        return subprocess.run([sys.executable, '-I', '-O', '-B', str(self.package / 'verify.py')],
                              cwd=self.root, text=True, capture_output=True, timeout=60)

    def test_relocated_optimized_replay_is_read_only(self):
        def inventory():
            return {str(p.relative_to(self.root)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in self.root.rglob('*') if p.is_file()}
        before = inventory()
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('PASS_TRANSPORT_CONCORDANCE', result.stdout)
        self.assertEqual(inventory(), before)

    def test_vendor_source_mutation_rejects_before_execution(self):
        path = self.package / 'vendor/pr933/search.py'
        path.write_bytes(path.read_bytes() + b'\nraise RuntimeError("must not execute")\n')
        result = self.invoke()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('source SHA256 mismatch', result.stderr)
        self.assertNotIn('RuntimeError: must not execute', result.stderr)

    def test_corrupt_and_type_confused_receipts_reject(self):
        path = self.package / 'CERTIFICATE.json'
        original = json.loads(path.read_text())
        for value in (102, True):
            candidate = json.loads(json.dumps(original))
            candidate['synthetic']['source_observation']['pairs'] = value
            path.write_text(json.dumps(candidate))
            before = path.read_bytes()
            result = self.invoke()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('certificate does not match', result.stderr)
            self.assertEqual(path.read_bytes(), before)

    def test_fixture_mutation_rejects(self):
        path = self.package / 'fixtures/five-gate.json'
        word = json.loads(path.read_text())
        word['B'][1][2] = [18]  # Remove x's dependency on y.
        path.write_text(json.dumps(word))
        receipt = (self.package / 'CERTIFICATE.json').read_bytes()
        result = self.invoke()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.package / 'CERTIFICATE.json').read_bytes(), receipt)


if __name__ == '__main__':
    unittest.main()
