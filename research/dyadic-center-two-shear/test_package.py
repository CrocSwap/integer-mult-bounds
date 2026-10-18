#!/usr/bin/env python3
"""Reproduction and proof-evidence failure controls for the research package."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='two shear minimal ')
        cls.root = Path(cls.temp.name)/'checkout without git'
        cls.package = cls.root/'research/dyadic-center-two-shear'
        cls.package.mkdir(parents=True)
        for source in HERE.iterdir():
            if source.is_file():
                shutil.copy2(source, cls.package/source.name)
        pins = json.loads((HERE/'SOURCES.json').read_text())
        for name in pins['sha256']:
            target = cls.root/name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT/name, target)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def call(self, name='verify.py', optimized=False):
        return subprocess.run([sys.executable,'-I','-B',*(['-O'] if optimized else []),
                               str(self.package/name)], cwd=self.temp.name,
                              text=True, capture_output=True, timeout=180)

    def test_01_minimal_relocation_optimized_public_replay(self):
        self.assertFalse((self.root/'.git').exists())
        # Selection can advance without invalidating a historical circuit.
        pointer = self.root/'certificates/selected-result.json'
        pointer.parent.mkdir(parents=True, exist_ok=True)
        pointer.write_text('{"decimal":"a later unrelated selection"}\n')
        result = self.call(optimized=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('saved=112797360000 no_new_kappa',result.stdout)

    def test_02_source_corruption_rejected_without_receipt_overwrite(self):
        path = self.root/'scripts/experiments/complex_centers.py'
        original = path.read_bytes()
        receipt = (self.package/'EXPECTED.json').read_bytes()
        try:
            path.write_bytes(original+b'\n# deliberate source corruption\n')
            result = self.call()
            self.assertNotEqual(result.returncode,0)
            self.assertIn('source mismatch: scripts/experiments/complex_centers.py',result.stderr)
            self.assertEqual((self.package/'EXPECTED.json').read_bytes(),receipt)
        finally:
            path.write_bytes(original)

    def test_03_underpriced_receipt_rejected_after_fresh_full_replay(self):
        path = self.package/'EXPECTED.json'
        original = path.read_bytes()
        bad = json.loads(original)
        bad['scalar_invoice']['after'] -= 1
        damaged = (json.dumps(bad,indent=2,sort_keys=True)+'\n').encode()
        try:
            path.write_bytes(damaged)
            result = self.call()
            self.assertNotEqual(result.returncode,0)
            self.assertIn('receipt mismatch', result.stderr)
            self.assertEqual(path.read_bytes(), damaged)
        finally:
            path.write_bytes(original)

    def test_04_corrupted_base_selection_snapshot_rejected(self):
        path = self.package/'BASE-SELECTED.json'
        original = path.read_bytes()
        try:
            path.write_bytes(original+b' ')
            result = self.call()
            self.assertNotEqual(result.returncode,0)
            self.assertIn('base selection snapshot mismatch',result.stderr)
        finally:
            path.write_bytes(original)

    def test_05_independent_optimized_without_sources(self):
        isolated = Path(self.temp.name)/'independent only.py'
        shutil.copy2(HERE/'independent.py',isolated)
        result = subprocess.run([sys.executable,'-I','-O','-B',str(isolated)],
                                cwd=self.temp.name,text=True,capture_output=True,timeout=180)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('PASS_INDEPENDENT_TWO_SHEAR',result.stdout)


if __name__ == '__main__':
    unittest.main()
