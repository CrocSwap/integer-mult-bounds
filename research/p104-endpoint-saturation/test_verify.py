# SPDX-License-Identifier: Apache-2.0
"""Behavioral controls for allocation, source binding and published CLI checks."""

import itertools
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import verify

PACKAGE = Path(__file__).resolve().parent


class AllocationTests(unittest.TestCase):
    def test_exhaustive_small_allocations(self):
        options = [(2, 1), (3, 2), (4, 2), (5, 3), (6, 3)]
        cases = 0
        for size in range(1, 5):
            for endpoints in itertools.product(options, repeat=size):
                expected = [10**6] * (2 * size + 1)
                for assigned in itertools.product(range(3), repeat=size):
                    cheap = sum(max(0, d - c * u) for u, (d, c) in
                                zip(assigned, endpoints, strict=True))
                    expected[sum(assigned)] = min(expected[sum(assigned)], cheap)
                _, coverage = verify.marginal_certificate(endpoints)
                self.assertEqual([sum(d for d, _ in endpoints) - x for x in coverage],
                                 expected)
                self.assertEqual(verify.dynamic_minimum_cheap(endpoints), expected)
                cases += 1
        self.assertEqual(cases, 780)

    def test_exact_threshold_assignment_and_rejection(self):
        result = verify.calculate()
        for row in result.values():
            self.assertEqual(row['profile_253_147'],
                             {'maximum_coverage': 3972, 'deficit': 684})
            self.assertEqual(row['minimum_cheap_by_units'][191:193], [219, 204])
            assigned = row['relaxed_assignment_at_threshold']
            self.assertEqual(sum(u for u, _ in assigned), 192)
            self.assertEqual(sum(c for _, c in assigned), 204)
            self.assertEqual(sum(u + c for u, c in assigned), 396)

    def test_invalid_allocation_boundaries(self):
        for endpoints in [[], [(0, 0)], [(5, 2)], [(2, 2)], [(31, 31)], [(3.0, 2)]]:
            with self.subTest(endpoints=endpoints), self.assertRaises(ValueError):
                verify.marginal_certificate(endpoints)
        with self.assertRaises(ValueError):
            verify.marginal_certificate([(2, 1)] * 105)

    def test_semantic_unsaturated_mutant(self):
        # Without truncating a second helper's useful contribution at its endpoint,
        # the credited 253/147 aggregate erroneously passes.
        original = (PACKAGE / 'verify.py').read_text()
        old = 'value = costs[used] + max(0, demand - added * capacity)'
        new = 'value = costs[used] + demand - added * capacity'
        self.assertEqual(original.count(old), 1)
        with tempfile.TemporaryDirectory() as directory:
            root, package = export(Path(directory))
            (package / 'verify.py').write_text(original.replace(old, new))
            run = cli(root, package, '-O')
            self.assertNotEqual(run.returncode, 0)
            self.assertIn('DP endpoint cases', run.stderr)

    def test_export_and_integrity_failures(self):
        with tempfile.TemporaryDirectory() as directory:
            root, package = export(Path(directory))
            for option in (None, '-O'):
                run = cli(root, package, option)
                self.assertEqual(run.returncode, 0, run.stderr)
                self.assertIn('deficit=684 minimum_units_at_400=192', run.stdout)
            source = root / 'research/p104-native-channel/inputs/LOWRANK-WITNESS.json'
            original = source.read_bytes()
            source.write_bytes(original + b' ')
            rejected = cli(root, package)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn('source SHA256 mismatch', rejected.stderr)
            source.write_bytes(original)
            receipt = json.loads((package / 'RESULT.json').read_text())
            receipt['arrival']['minimum_units_at_400'] = 192.0
            (package / 'RESULT.json').write_text(json.dumps(receipt))
            rejected = cli(root, package, '-O')
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn('typed receipt equality', rejected.stderr)


def export(root):
    package = root / 'research/p104-endpoint-saturation'
    shutil.copytree(PACKAGE, package, ignore=shutil.ignore_patterns('__pycache__'))
    for name in ('LOWRANK-WITNESS.json', 'P104-FIXTURE.json'):
        relative = Path('research/p104-native-channel/inputs') / name
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(verify.ROOT / relative, target)
    return root, package


def cli(root, package, option=None):
    arguments = [sys.executable, '-B', '-Werror']
    if option:
        arguments.append(option)
    arguments.append(str(package / 'verify.py'))
    return subprocess.run(arguments, cwd=root, capture_output=True, text=True,
                          timeout=30, check=False)


if __name__ == '__main__':
    unittest.main()
