#!/usr/bin/env python3
"""Focused admission/provenance controls; Python 3.10+, standard library."""
import copy
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('nonlinear_floor_driver', HERE / 'verify.py')
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


class PackageChecks(unittest.TestCase):
    def test_demands_and_concentration(self):
        verify.check_sources()
        geometry, _ = verify.load_vendor()
        cliques = geometry.maximal_cliques(geometry.nonorthogonality(geometry.gaussian_lines()))
        for size in (7, 8, 10, 11, 12):
            q = next(c for c in cliques if c.bit_count() == size)
            demand = [3 * ((q >> i) & 1) for i in range(60)]
            self.assertEqual(verify.demand_floor(demand, cliques), 3 * size)
        self.assertEqual(verify.demand_floor([0] * 60, cliques), 0)
        self.assertEqual(verify.demand_floor([2] * 60, cliques), 80)
        for demand in ([1] * 59, [-1] + [0] * 59, [True] + [0] * 59, [0.5] + [0] * 59):
            with self.assertRaises(ValueError):
                verify.demand_floor(demand, cliques)

    def test_certificate_mutations(self):
        actual = json.loads((HERE / 'CERTIFICATE.json').read_text())
        verify.compare_receipt(actual, copy.deepcopy(actual))
        for field in ('uniform_gaussian_floor_per_bit', 'demand_coefficient', 'concentrated_twelve_port_floor', 'assignment_seed'):
            bad = copy.deepcopy(actual)
            bad[field] = 'wrong'
            with self.assertRaises(ValueError):
                verify.compare_receipt(actual, bad)
        bad = copy.deepcopy(actual)
        bad['geometric_premise']['unordered_nonempty_flat_pairs'] -= 1
        with self.assertRaises(ValueError):
            verify.compare_receipt(actual, bad)

    def test_relocated_source_corruption_and_optimization(self):
        manifest = json.loads((HERE / 'SOURCES.json').read_text())
        with tempfile.TemporaryDirectory(prefix='gaussian nonlinear ') as tmp:
            root = Path(tmp)
            package = root / 'research' / HERE.name
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
            for local in manifest['base_sources']:
                target = root / local
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(verify.ROOT / local, target)
            command = [sys.executable, '-I', '-B', str(package / 'verify.py'), '--check-sources']
            def run():
                return subprocess.run(command, cwd=tmp, text=True, capture_output=True)
            result = run()
            self.assertEqual(result.returncode, 0, result.stderr)
            vendor = package / 'vendor/pr738/geometry.py'
            saved = vendor.read_bytes()
            vendor.write_bytes(saved + b'\n# mutation\n')
            self.assertNotEqual(run().returncode, 0)
            vendor.write_bytes(saved)
            manifest_path = package / 'SOURCES.json'
            saved_manifest = manifest_path.read_bytes()
            bad_manifest = json.loads(saved_manifest)
            del bad_manifest['vendor']['vendor/pr738/verify.py']
            manifest_path.write_text(json.dumps(bad_manifest))
            self.assertNotEqual(run().returncode, 0)
            manifest_path.write_bytes(saved_manifest)
            vendor.unlink()
            self.assertNotEqual(run().returncode, 0)
            vendor.write_bytes(saved)
            selected = root / 'certificates/selected-result.json'
            saved_selected = selected.read_bytes()
            selected.write_bytes(saved_selected + b'\n')
            self.assertNotEqual(run().returncode, 0)
            selected.write_bytes(saved_selected)
            result = subprocess.run([sys.executable, '-I', '-O', '-B', str(package / 'verify.py')], cwd=tmp, text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('optimized Python is unsupported', result.stderr)
            sentinel = package / 'kept-output.json'
            sentinel.write_text('existing receipt\n')
            result = subprocess.run([sys.executable, '-I', '-B', str(package / 'verify.py'),
                                     '--output', str(sentinel)], cwd=tmp, text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('output path already exists', result.stderr)
            self.assertEqual(sentinel.read_text(), 'existing receipt\n')


if __name__ == '__main__':
    unittest.main(verbosity=2)
