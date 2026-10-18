#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Rejection, relocation and optimization checks for the scoped package."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('floor_check', HERE / 'verify.py')
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


class PackageTests(unittest.TestCase):
    def run_package(self, mutate=None, script='verify.py'):
        with tempfile.TemporaryDirectory(prefix='a8-floor-test-') as directory:
            package = Path(directory) / 'relocated-package'
            shutil.copytree(HERE, package)
            if mutate:
                mutate(package)
            before = {str(p.relative_to(package)): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in package.rglob('*') if p.is_file()}
            for p in package.rglob('*'):
                if p.is_file():
                    p.chmod(0o444)
            completed = subprocess.run([sys.executable, '-I', '-O', '-B', str(package / script)],
                                       cwd=directory, capture_output=True, text=True, timeout=120)
            after = {str(p.relative_to(package)): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in package.rglob('*') if p.is_file()}
            self.assertEqual(before, after, 'replay modified package files')
            for p in package.rglob('*'):
                if p.is_file():
                    p.chmod(0o644)
            return completed

    def test_optimized_relocated_readonly(self):
        result = self.run_package()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('PASS_A8_SIMPLEX_DECODER_FLOOR', result.stdout)

    def test_changed_receipt(self):
        def mutate(p):
            f = p / 'CERTIFICATE.json'
            x = json.loads(f.read_text()); x['sharp_cost'] = 71
            f.write_text(json.dumps(x))
        result = self.run_package(mutate)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('certificate differs', result.stderr)

    def test_missing_receipt(self):
        result = self.run_package(lambda p: (p / 'CERTIFICATE.json').unlink())
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('CERTIFICATE.json', result.stderr)

    def test_incomplete_plane_receipt(self):
        def mutate(p):
            f = p / 'CERTIFICATE.json'; x = json.loads(f.read_text())
            x['all_eight_cases'].pop(); f.write_text(json.dumps(x))
        result = self.run_package(mutate)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('certificate differs', result.stderr)

    def test_mutated_predecessor_frame(self):
        def mutate(p):
            f = p / 'FRAME.json'; x = json.loads(f.read_text())
            x['six_times_normals'][0][0] += 1; f.write_text(json.dumps(x))
        result = self.run_package(mutate, 'independent.py')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('exact predecessor frame pin', result.stderr)

    def test_punctured_domain_rejected(self):
        with self.assertRaisesRegex(ValueError, '120 distinct labels'):
            V.model_checks(V.model()[:-1])

    def test_rank_deficient_column_rejected(self):
        rows = V.model()
        altered = [(u, tuple(0 if k == 0 else x for k, x in enumerate(v))) for u, v in rows]
        with self.assertRaises(ValueError):
            V.model_checks(altered)

    def test_all_nine_terms_active(self):
        rows = V.model()
        C, costs = V.witness(rows, True)
        self.assertEqual(costs, [1, 8, 9, 9, 9, 9, 9, 9, 9])
        self.assertTrue(all(any(row[k] != 0 for row in C) for k in range(9)))


if __name__ == '__main__':
    unittest.main(verbosity=2)
