#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Isolated replay and actual on-disk corruption controls, including optimized Python."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


class PackageControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix='r439 terminal audit ')
        cls.root = Path(cls.temporary.name)
        cls.package = cls.root / 'research' / HERE.name
        cls.package.mkdir(parents=True)
        for path in HERE.iterdir():
            if path.is_file():
                shutil.copy2(path, cls.package / path.name)
        pins = json.loads((HERE / 'SOURCES.json').read_bytes())
        for entry in pins['files']:
            if entry['usage'] == 'input':
                destination = cls.root / entry['path']
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / entry['path'], destination)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def invoke(self, expected_failure=None):
        result = subprocess.run([sys.executable, '-I', '-O', '-B', str(self.package / 'verify.py')],
                                cwd=self.root, capture_output=True, text=True, timeout=120,
                                env=dict(os.environ, PYTHONUTF8='1'))
        if expected_failure is None:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('PASS_R439_TERMINAL_STAR_RESTORATION', result.stdout)
        else:
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(expected_failure, result.stderr)

    def mutate_and_reject(self, path, replacement, message):
        original = path.read_bytes()
        try:
            path.write_bytes(replacement)
            self.invoke(message)
        finally:
            path.write_bytes(original)

    def test_optimized_minimal_relocation_is_read_only(self):
        def inventory():
            return {str(p.relative_to(self.root)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in self.root.rglob('*') if p.is_file()}
        before = inventory()
        self.invoke()
        self.assertEqual(before, inventory())

    def test_consumed_source_corruption(self):
        path = self.root / 'research/r439-helper-stars-seed19/candidate.json.gz'
        original = path.read_bytes()
        self.mutate_and_reject(path, bytes([original[0] ^ 1]) + original[1:], 'source SHA256')

    def test_omitted_input_pin(self):
        path = self.package / 'SOURCES.json'
        data = json.loads(path.read_bytes())
        data['files'] = [entry for entry in data['files'] if entry['path'] != 'research/r439-helper-stars-seed19/candidate.json.gz']
        self.mutate_and_reject(path, json.dumps(data).encode(), 'exact input pin inventory')

    def test_false_certificate_and_type_confusion(self):
        path = self.package / 'CERTIFICATE.json'
        data = json.loads(path.read_bytes())
        data['words'][0]['eligible_nonempty_subsets'] = False
        self.mutate_and_reject(path, json.dumps(data).encode(), 'certificate mismatch')

    def test_missing_certificate_is_not_regenerated(self):
        path = self.package / 'CERTIFICATE.json'
        original = path.read_bytes()
        try:
            path.unlink()
            self.invoke('FileNotFoundError')
            self.assertFalse(path.exists())
        finally:
            path.write_bytes(original)

    def test_duplicate_source_keys(self):
        path = self.package / 'SOURCES.json'
        self.mutate_and_reject(path, b'{"files":[],"files":[]}', 'duplicate JSON key')


if __name__ == '__main__':
    unittest.main()
