#!/usr/bin/env python3
"""Packaging and corruption controls. Hanson Sun with OpenAI Codex. Apache-2.0."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='observable-connector-')
        self.root = Path(self.temp.name)
        self.pkg = self.root / 'research' / HERE.name
        shutil.copytree(HERE, self.pkg, ignore=shutil.ignore_patterns('__pycache__'))
        sources = json.loads((HERE / 'SOURCES.json').read_text())
        for row in sources['files']:
            if row['usage'] == 'input':
                dst = self.root / row['path']
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / row['path'], dst)

    def tearDown(self):
        for path in self.root.rglob('*'):
            if path.is_dir():
                path.chmod(0o755)
            else:
                path.chmod(0o644)
        self.temp.cleanup()

    def run_verifier(self, *args):
        return subprocess.run([sys.executable, '-I', '-O', '-B', str(self.pkg / 'verify.py'), *args],
                              cwd=self.root, text=True, capture_output=True, timeout=40)

    def test_read_only_relocation_and_exact_export(self):
        for path in self.root.rglob('*'):
            path.chmod(0o555 if path.is_dir() else 0o444)
        result = self.run_verifier()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('PASS_OBSERVABLE_CONNECTOR', result.stdout)
        export = self.root / 'recomputed.json'
        result = self.run_verifier('--write', str(export))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(export.read_bytes(), (self.pkg / 'CERTIFICATE.json').read_bytes())
        duplicate = self.run_verifier('--write', str(export))
        self.assertNotEqual(duplicate.returncode, 0)
        self.assertIn('File exists', duplicate.stderr)

    def test_false_optimum_certificate_rejected(self):
        path = self.pkg / 'CERTIFICATE.json'
        doc = json.loads(path.read_text())
        doc['optimality']['mixed']['minimum'] = 2
        path.write_text(json.dumps(doc))
        result = self.run_verifier()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('certificate mismatch', result.stderr)

    def test_retained_source_corruption_rejected(self):
        path = self.pkg / 'references' / 'PR1439-README.md'
        path.write_text(path.read_text() + '\nmutated source\n')
        result = self.run_verifier()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('predecessor SHA256 mismatch', result.stderr)

    def test_live_source_corruption_rejected(self):
        path = self.root / 'research/universal-connector-boundary/README.md'
        path.write_text(path.read_text() + '\nmutated source\n')
        result = self.run_verifier()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('live source drift', result.stderr)

    def test_missing_certificate_rejected(self):
        (self.pkg / 'CERTIFICATE.json').unlink()
        result = self.run_verifier()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('CERTIFICATE.json', result.stderr)


if __name__ == '__main__':
    unittest.main()
