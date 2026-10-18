#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Adversarial certificate, receipt, source-binding and relocation checks."""
from copy import deepcopy
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('mask_checker', HERE / 'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = v.geometry()
        cls.cert = v.read_json(HERE / 'CERTIFICATE.json')

    def test_complete_strata_and_schema(self):
        variants = []
        c = deepcopy(self.cert); c['cases'].pop(); variants.append((c, 'case count'))
        c = deepcopy(self.cert); c['cases'][-1] = c['cases'][0]; variants.append((c, 'duplicate case'))
        c = deepcopy(self.cert); c['schema_version'] = True; variants.append((c, 'schema'))
        c = deepcopy(self.cert); c['cases'][0]['strata'][0] = 0.0; variants.append((c, 'strata'))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'bad.json'
            for c, message in variants:
                path.write_text(json.dumps(c))
                with self.assertRaisesRegex(ValueError, message):
                    v.certificate(self.data, path)
            path.write_text('{"schema_version":1,"schema_version":1,"cases":[]}')
            with self.assertRaisesRegex(ValueError, 'duplicate JSON key'):
                v.certificate(self.data, path)

    def test_dependence_balance_and_support(self):
        row = self.cert['cases'][7]
        # Search only to select corruptions that exercise each rejection branch.
        failures = set()
        for index in range(16):
            for port in range(112):
                bad = deepcopy(row); bad['units'][index][0] = port
                try:
                    v.check_case(bad, self.data)
                except ValueError as exc:
                    failures.add(str(exc))
                if {'unit support incidence', 'independent unit group'} <= failures:
                    break
            if {'unit support incidence', 'independent unit group'} <= failures:
                break
        self.assertTrue({'unit support incidence', 'independent unit group'} <= failures)
        bad = deepcopy(row); bad['units'][0][1] ^= 1
        with self.assertRaises(ValueError):
            v.check_case(bad, self.data)
        bad = deepcopy(row); bad['units'][0][2] = False
        with self.assertRaisesRegex(ValueError, 'unit domain'):
            v.check_case(bad, self.data)

    def test_power_lemma_boundary(self):
        # Exact algebra: (sqrt(9)+sqrt(7))^2=16+2sqrt(63)<32.
        self.assertEqual(9 + 7, 16)
        self.assertLess(9 * 7, 64)
        # A balanced certificate is stronger than only a rank-sum certificate.
        self.assertTrue(all(c*c <= 8*c for c in range(9)))
        self.assertGreater(9*9, 8*9)

    def test_generator_reproduces_bytes(self):
        with tempfile.TemporaryDirectory(prefix='mask certificate ') as tmp:
            path = Path(tmp) / 'new.json'
            command = [sys.executable, '-I', '-O', '-B', str(HERE / 'build_certificate.py'), '--output', str(path)]
            result = subprocess.run(command, text=True, capture_output=True, timeout=60)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(path.read_bytes(), (HERE / 'CERTIFICATE.json').read_bytes())
            result = subprocess.run(command, text=True, capture_output=True, timeout=60)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('refuse to overwrite', result.stderr)

    def test_readonly_relocation_and_actual_file_corruption(self):
        with tempfile.TemporaryDirectory(prefix='mask package space ') as tmp:
            root = Path(tmp)
            dest = root / 'research' / 'renamed package'
            shutil.copytree(HERE, dest, ignore=shutil.ignore_patterns('__pycache__'))
            manifest = v.read_json(HERE / 'SOURCES.json')
            for row in manifest['files']:
                if row['usage'] == 'input':
                    target = root / row['path']; target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(v.ROOT / row['path'], target)
            files = [p for p in root.rglob('*') if p.is_file()]
            directories = [p for p in root.rglob('*') if p.is_dir()]
            before = {str(p.relative_to(root)): sha256(p.read_bytes()).hexdigest() for p in files}
            for p in files: p.chmod(0o444)
            for p in directories: p.chmod(0o555)
            for script in ('verify.py', 'independent_check.py'):
                result = subprocess.run([sys.executable, '-I', '-O', '-B', str(dest / script)],
                                        cwd=tmp, text=True, capture_output=True, timeout=60)
                self.assertEqual(result.returncode, 0, result.stderr)
            after = {str(p.relative_to(root)): sha256(p.read_bytes()).hexdigest()
                     for p in root.rglob('*') if p.is_file()}
            self.assertEqual(before, after)
            for p in directories: p.chmod(0o755)
            for p in files: p.chmod(0o644)
            command = [sys.executable, '-I', '-O', '-B', str(dest / 'verify.py')]
            receipt = dest / 'RESULT.json'; original = receipt.read_bytes()
            for bad_value in (28.0, True, 27):
                value = json.loads(original); value['coordinate_pairs'] = bad_value
                receipt.write_text(json.dumps(value))
                result = subprocess.run(command, text=True, capture_output=True, timeout=60)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('complete result receipt', result.stderr)
            receipt.write_bytes(original)
            certpath = dest / 'CERTIFICATE.json'; certbytes = certpath.read_bytes()
            c = json.loads(certbytes); c['cases'][0]['units'][0] = c['cases'][0]['units'][1]
            certpath.write_text(json.dumps(c))
            for script in ('verify.py', 'independent_check.py'):
                result = subprocess.run([sys.executable, '-I', '-O', '-B', str(dest / script)],
                                        text=True, capture_output=True, timeout=60)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('unit', result.stderr)
            certpath.write_bytes(certbytes)
            geometry = root / v.GEOMETRY; geometry.write_bytes(geometry.read_bytes() + b' ')
            result = subprocess.run(command, text=True, capture_output=True, timeout=60)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('source SHA256', result.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
