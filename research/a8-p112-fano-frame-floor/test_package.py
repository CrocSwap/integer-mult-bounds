#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Failure controls for source bindings and the public receipt-checking command."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('frame_floor_verifier', HERE / 'verify.py')
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


class PackageControls(unittest.TestCase):
    def test_changed_predecessor_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'changed.py'
            path.write_bytes((HERE / 'vendor/pr1304_verify.py').read_bytes() + b'\n')
            with self.assertRaisesRegex(ValueError, 'source bytes changed'):
                verifier.predecessor(path)

    def test_missing_predecessor_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError):
                verifier.predecessor(Path(directory) / 'absent.py')

    def rejected_receipt(self, text, expected_error):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'receipt.json'
            if text is not None:
                path.write_text(text)
            result = subprocess.run(
                [sys.executable, '-I', '-O', '-B', str(HERE / 'verify.py'),
                 '--certificate', str(path)], cwd=directory, capture_output=True,
                text=True, timeout=120)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(expected_error, result.stderr)
            self.assertNotIn('PASS_A8_P112', result.stdout)
            if text is not None:
                self.assertEqual(path.read_text(), text)

    def test_false_cost_rejected_by_cli(self):
        receipt = json.loads((HERE / 'CERTIFICATE.json').read_text())
        receipt['sharp_copy_cost'] = 70
        self.rejected_receipt(json.dumps(receipt), 'certificate differs')

    def test_omitted_anchor_rejected_by_cli(self):
        receipt = json.loads((HERE / 'CERTIFICATE.json').read_text())
        receipt['orbits'][1]['anchors'].pop()
        self.rejected_receipt(json.dumps(receipt), 'certificate differs')

    def test_missing_receipt_rejected_by_cli(self):
        self.rejected_receipt(None, 'FileNotFoundError')

    def test_malformed_receipt_rejected_by_cli(self):
        self.rejected_receipt('{broken', 'JSONDecodeError')


if __name__ == '__main__':
    unittest.main()
