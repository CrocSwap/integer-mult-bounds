#!/usr/bin/env python3
"""Failure-detection and portable offline replay tests for the radix-9 audit."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction as F

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('radix9_audit', ROOT / 'verify.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class TestAudit(unittest.TestCase):
    def test_nonprimitive_embeddings_rejected(self):
        for k in (0, 3, 6, 9, -1):
            with self.subTest(k=k), self.assertRaisesRegex(audit.AuditError, 'nonprimitive'):
                audit.coefficients(k)

    def test_root_enclosures_nest_and_select_positive_chart(self):
        coarse, fine = audit.algebraic_root(32), audit.algebraic_root(256)
        for outer, inner in zip(coarse, fine):
            self.assertLessEqual(outer[0], inner[0])
            self.assertLessEqual(inner[1], outer[1])
        self.assertGreater(fine[0][0], F(3, 4))
        self.assertGreater(fine[1][0], 0)

    def test_overlap_alone_is_rejected(self):
        inner = [((F(1), F(2)), (F(0), F(0)))] * 9
        outer = [((F(3, 2), F(3)), (F(0), F(0)))] * 9
        with self.assertRaisesRegex(audit.AuditError, 'coefficient enclosure'):
            audit.require_contained(inner, outer)

    def test_upward_power_bounds_at_boundaries(self):
        for exponent in (-2048, -128, -1, 0, 1, 64):
            value = audit.power2(exponent)
            self.assertEqual(audit.upper_power2(value), exponent)
            self.assertEqual(audit.upper_power2(value * F(15, 16)), exponent)
            self.assertEqual(audit.upper_power2(value * F(17, 16)), exponent + 1)

    def test_modified_subject_and_factor_file_rejected(self):
        for name in ('interval_kernel.py', 'FACTORS.json'):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp) / 'audit'
                shutil.copytree(ROOT, target)
                path = target / 'vendor' / name
                path.write_bytes(path.read_bytes() + b'\n')
                with self.assertRaisesRegex(audit.AuditError, 'source drift'):
                    audit.verify_sources(target)

    def test_manifest_cannot_read_outside_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'audit'
            shutil.copytree(ROOT, target)
            manifest = json.loads((target / 'SOURCE.json').read_text())
            manifest['files']['../outside'] = {'sha256': 'irrelevant'}
            (target / 'SOURCE.json').write_bytes(json.dumps(manifest).encode())
            with self.assertRaisesRegex(audit.AuditError, 'source path containment'):
                audit.verify_sources(target)

    def test_offline_relocation_optimized_and_output_protection(self):
        with tempfile.TemporaryDirectory(prefix='radix9 audit ') as tmp:
            location = Path(tmp)
            package = location / 'copied package'
            shutil.copytree(ROOT, package)
            output = location / 'result.json'
            command = [sys.executable, '-B', '-I', '-O', str(package / 'verify.py')]
            result = subprocess.run(command + ['--output', str(output)], cwd=location,
                                    capture_output=True, text=True, timeout=60)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(output.read_bytes(), (ROOT / 'EXPECTED.json').read_bytes())
            original = output.read_bytes()
            result = subprocess.run(command + ['--output', str(output)], cwd=location,
                                    capture_output=True, text=True, timeout=60)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('output already exists', result.stderr)
            self.assertEqual(output.read_bytes(), original)

    def test_forged_expected_receipt_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'forged.json'
            target.write_bytes(b'{"status":"PASS"}\n')
            result = subprocess.run([sys.executable, '-B', '-I', '-O', str(ROOT / 'verify.py'),
                                     '--check', str(target)], cwd=tmp,
                                    capture_output=True, text=True, timeout=60)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('expected evidence differs', result.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
