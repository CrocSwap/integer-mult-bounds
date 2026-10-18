# SPDX-License-Identifier: Apache-2.0
"""Behavioral and publication-boundary controls for the endpoint certificate."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction as Q
from pathlib import Path

import geometry
import verify


class CertificateTests(unittest.TestCase):
    def test_affine_cover_and_missing_hypothesis(self):
        points = {1 << k for k in range(8)}
        row = geometry.plane_cover(points, 256)
        self.assertEqual((row['demand'], row['capacity']), (8, 7))
        self.assertEqual(geometry.pair_oracle(points, 256), (7, 8))
        # 1+2+3=0 prevents a functional taking value one on all three.
        with self.assertRaisesRegex(ValueError, 'odd affine section'):
            geometry.plane_cover(points | {3}, 256)
        with self.assertRaisesRegex(ValueError, 'endpoint containment'):
            geometry.plane_cover(points | {256}, 256)

    def test_price_and_domain(self):
        verify.sources()
        module = verify.interval_module()
        lo, hi = verify.moment(module, 0, 208, verify.SELECTED)
        self.assertTrue(Q('0.9988962438816701') < lo <= hi < Q('0.9988962438816703'))
        self.assertGreater(verify.moment(module, 12, 207, verify.SELECTED)[0], hi)
        for cheap, units in ((-1, 208), (0, 483), (0, 208.0)):
            with self.assertRaises(ValueError):
                verify.moment(module, cheap, units, verify.SELECTED)

    def test_duplicate_input_and_frame_rejection(self):
        with self.assertRaisesRegex(ValueError, 'duplicate JSON key'):
            json.loads('{"x":1,"x":2}', object_pairs_hook=verify.unique)
        with self.assertRaisesRegex(ValueError, 'independent binary basis'):
            geometry.span([1, 2, 3])

    def test_optimized_git_free_export_and_corruption(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / 'research/p104-endpoint-geometric-budget'
            shutil.copytree(verify.PACKAGE, package, ignore=shutil.ignore_patterns('__pycache__'))
            manifest = verify.read_json(verify.PACKAGE / 'SOURCES.json')
            for entry in manifest['files']:
                if entry['usage'] == 'input':
                    target = root / entry['path']
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(verify.ROOT / entry['path'], target)
            env = dict(os.environ, PYTHONPYCACHEPREFIX=str(root / 'cache'))
            command = [sys.executable, '-O', '-Werror', '-B', str(package / 'verify.py')]
            good = subprocess.run(command, check=False, cwd=root, env=env, text=True,
                                  capture_output=True, timeout=60)
            self.assertEqual(good.returncode, 0, good.stderr)
            self.assertIn('endpoints=208 units=208', good.stdout)
            result_path = package / 'RESULT.json'
            original = result_path.read_bytes()
            receipt = json.loads(original)
            receipt['price']['units'] = 208.0
            result_path.write_text(json.dumps(receipt), encoding='utf-8')
            bad = subprocess.run(command, check=False, cwd=root, env=env, text=True,
                                 capture_output=True, timeout=60)
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn('complete typed receipt', bad.stderr)
            result_path.write_bytes(original)
            source = root / 'research/complex-local-word-ceiling/ceiling.py'
            source.write_text('raise RuntimeError("MUST_NOT_IMPORT")\n', encoding='utf-8')
            bad = subprocess.run(command, check=False, cwd=root, env=env, text=True,
                                 capture_output=True, timeout=60)
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn('input hash', bad.stderr)
            self.assertNotIn('RuntimeError: MUST_NOT_IMPORT', bad.stderr)


if __name__ == '__main__':
    unittest.main()
