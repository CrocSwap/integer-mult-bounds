#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Proof-relevant receipt/source corruption and relocation checks."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


class PackageChecks(unittest.TestCase):
    def invoke(self, script, *arguments, cwd=None):
        return subprocess.run([sys.executable, '-I', '-O', '-B', str(script), *map(str, arguments)],
                              cwd=cwd, text=True, capture_output=True)

    def test_changed_mathematical_receipt_is_rejected_without_output(self):
        with tempfile.TemporaryDirectory() as folder:
            tmp = Path(folder)
            receipt = json.loads((HERE / 'CERTIFICATE.json').read_text())
            # Underprice the paired-path exception by one deleted port.
            exceptional = next(r for r in receipt['cases'][0]['orbits']
                               if r['classification'] == 'two-pair path')
            exceptional['minimum_deletions'] -= 1
            bad = tmp / 'wrong.json'
            bad.write_text(json.dumps(receipt))
            result = self.invoke(HERE / 'verify.py', '--certificate', bad,
                                 '--output', tmp / 'output.json')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('certificate mismatch', result.stderr)
            self.assertFalse((tmp / 'output.json').exists())

    def test_relocated_optimized_replay_and_overwrite_protection(self):
        with tempfile.TemporaryDirectory(prefix='star research ') as folder:
            tmp = Path(folder)
            package = tmp / 'package with spaces'
            shutil.copytree(HERE, package)
            output = tmp / 'verified.json'
            result = self.invoke(package / 'verify.py', '--output', output, cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(output.read_bytes(), (HERE / 'CERTIFICATE.json').read_bytes())
            result = self.invoke(package / 'verify.py', '--output', output, cwd=tmp)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('refusing to overwrite', result.stderr)
            self.assertEqual(output.read_bytes(), (HERE / 'CERTIFICATE.json').read_bytes())

    def test_changed_predecessor_bytes_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            package = Path(folder) / 'package'
            shutil.copytree(HERE, package)
            source = package / 'reference' / 'HIGHER-GRAPH.md'
            source.write_bytes(source.read_bytes() + b'\nchanged source\n')
            result = self.invoke(package / 'verify.py')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('source SHA256 mismatch', result.stderr)


if __name__ == '__main__':
    unittest.main()
