#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Relocation, optimized execution, and rejection tests for the exact package."""
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
RELATIVE = HERE.relative_to(ROOT)


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='p112-masked-')
        cls.root = Path(cls.temp.name)
        cls.package = cls.root / RELATIVE
        cls.package.mkdir(parents=True)
        for name in ('verify.py', 'independent.py', 'SOURCES.json', 'CERTIFICATE.json'):
            shutil.copyfile(HERE / name, cls.package / name)
        cls.sources = json.loads((HERE / 'SOURCES.json').read_text())['local_files']
        for name in cls.sources:
            path = cls.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, path)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def run_check(self, name):
        return subprocess.run([sys.executable, '-I', '-O', '-B', str(self.package / name)],
                              cwd=self.root, text=True, capture_output=True, timeout=90)

    def test_01_optimized_relocated_replay_is_read_only(self):
        def hashes():
            return {p.relative_to(self.root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in self.root.rglob('*') if p.is_file()}
        before = hashes()
        for name, marker in [('verify.py', 'PASS_P112_MASKED_COMPONENT'),
                             ('independent.py', 'PASS_P112_MASKED_TANGENT_INDEPENDENT')]:
            result = self.run_check(name)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(marker, result.stdout)
        self.assertEqual(before, hashes())

    def test_02_corrupted_rank_receipt_is_rejected(self):
        path = self.package / 'CERTIFICATE.json'
        original = path.read_bytes()
        try:
            data = json.loads(original)
            data['jacobian_rank'] -= 1
            path.write_text(json.dumps(data, indent=2) + '\n')
            result = self.run_check('verify.py')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('certificate differs', result.stderr)
        finally:
            path.write_bytes(original)

    def test_03_changed_predecessor_proof_is_rejected(self):
        path = self.root / next(iter(self.sources))
        original = path.read_bytes()
        try:
            path.write_bytes(original + b'\nmodified premise\n')
            result = self.run_check('verify.py')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('source bytes changed', result.stderr)
        finally:
            path.write_bytes(original)

    def test_04_missing_predecessor_proof_is_rejected(self):
        path = self.root / next(iter(self.sources))
        original = path.read_bytes()
        try:
            path.unlink()
            result = self.run_check('verify.py')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('FileNotFoundError', result.stderr)
        finally:
            path.write_bytes(original)

    def test_05_omitted_source_pin_is_rejected(self):
        path = self.package / 'SOURCES.json'
        original = path.read_bytes()
        try:
            data = json.loads(original)
            data['local_files'].pop(next(iter(data['local_files'])))
            path.write_text(json.dumps(data))
            result = self.run_check('verify.py')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('source inventory changed', result.stderr)
        finally:
            path.write_bytes(original)


if __name__ == '__main__':
    unittest.main(verbosity=2)
