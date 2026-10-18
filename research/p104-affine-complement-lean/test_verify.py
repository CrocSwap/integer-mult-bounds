#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Behavioral controls for finite premises; formal controls are in check_lean.py."""

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
spec = importlib.util.spec_from_file_location('affine_premises', PACKAGE / 'verify.py')
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


class PremiseTests(unittest.TestCase):
    def test_source_bound_result(self):
        self.assertEqual(verify.calculate(), verify.load(PACKAGE / 'RESULT.json'))

    def test_necessary_hypotheses(self):
        # An eight-dimensional odd section in the low eight bits.
        points = {v for v in range(256) if v & 1}
        points = set(sorted(points)[:47]) | {129}
        self.assertEqual(verify.rank(points), 8)
        first, second = verify.check_cover(points, 256, 1, 2)
        self.assertEqual(first + second, 48)
        for q, f, error in [(0, 2, 'form bounds'), (2, 2, 'odd-section'),
                            (1, 256, 'nontrivial split')]:
            with self.assertRaisesRegex(ValueError, error):
                verify.check_cover(points, 256, q, f)
        with self.assertRaisesRegex(ValueError, 'duplicate JSON'):
            json.loads('{"a": 1, "a": 2}', object_pairs_hook=verify.unique)

    def test_git_free_and_corruptions(self):
        with tempfile.TemporaryDirectory(prefix='p104-affine-test-') as tmp:
            root = Path(tmp)
            package = root / 'research' / PACKAGE.name
            shutil.copytree(PACKAGE, package, ignore=shutil.ignore_patterns('__pycache__', '.lake'))
            for row in verify.load(PACKAGE / 'SOURCES.json')['files']:
                if row['usage'] == 'input':
                    path = root / row['path']
                    path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(ROOT / row['path'], path)
            command = [sys.executable, '-I', '-O', '-Werror', '-B', str(package / 'verify.py')]
            result = subprocess.run(command, check=False, capture_output=True, text=True, timeout=60)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('PASS_P104_AFFINE_PREMISES', result.stdout)
            receipt = verify.load(package / 'RESULT.json')
            receipt['endpoints'] = True
            (package / 'RESULT.json').write_text(json.dumps(receipt))
            result = subprocess.run(command, check=False, capture_output=True, text=True, timeout=60)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('typed receipt', result.stderr)
            source = root / verify.INPUT / 'LOWRANK-WITNESS.json'
            source.write_bytes(source.read_bytes() + b' ')
            result = subprocess.run(command, check=False, capture_output=True, text=True, timeout=60)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('source hash', result.stderr)


if __name__ == '__main__':
    unittest.main()
