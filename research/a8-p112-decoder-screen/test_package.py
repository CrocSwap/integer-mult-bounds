#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Relocation, optimized execution, and receipt rejection controls."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


class PackageControls(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='a8-p112-')
        self.root = Path(self.temporary.name)
        self.package = self.root / 'package'
        self.package.mkdir()
        for name in ('verify.py', 'independent.py', 'CERTIFICATE.json'):
            shutil.copyfile(HERE / name, self.package / name)

    def tearDown(self):
        self.temporary.cleanup()

    def run_script(self, script='verify.py'):
        return subprocess.run([sys.executable, '-I', '-O', '-B', str(self.package / script)],
                              cwd=self.root, capture_output=True, text=True, timeout=120)

    def change_receipt(self, change):
        path = self.package / 'CERTIFICATE.json'
        value = json.loads(path.read_text())
        change(value)
        path.write_text(json.dumps(value) + '\n')

    def test_primary_optimized_relocated_read_only(self):
        paths = list(self.package.iterdir())
        before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
        for path in paths:
            path.chmod(0o444)
        self.package.chmod(0o555)
        try:
            result = self.run_script()
        finally:
            self.package.chmod(0o755)
            for path in paths:
                path.chmod(0o644)
        self.assertEqual(result.returncode, 0, result.stderr[-1000:])
        self.assertIn('PASS_A8_P112_DECODER_FLOOR', result.stdout)
        self.assertEqual(before, {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in self.package.iterdir()})

    def test_separate_checker_without_primary(self):
        (self.package / 'verify.py').unlink()
        result = self.run_script('independent.py')
        self.assertEqual(result.returncode, 0, result.stderr[-1000:])
        self.assertIn('PASS_A8_P112_INDEPENDENT', result.stdout)

    def test_changed_claim_rejected(self):
        self.change_receipt(lambda value: value.update(sharp_copy_cost=70))
        result = self.run_script()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('certificate differs from exact replay', result.stderr)

    def test_missing_anchor_rejected(self):
        self.change_receipt(lambda value: value['anchors'].pop(4))
        result = self.run_script()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('certificate differs from exact replay', result.stderr)

    def test_missing_receipt_rejected(self):
        (self.package / 'CERTIFICATE.json').unlink()
        result = self.run_script()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('FileNotFoundError', result.stderr)

    def test_truncated_receipt_rejected(self):
        (self.package / 'CERTIFICATE.json').write_text('{"anchors": [')
        result = self.run_script()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('JSONDecodeError', result.stderr)


if __name__ == '__main__':
    unittest.main()
