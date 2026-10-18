#!/usr/bin/env python3
"""Focused edge, arithmetic, source-binding and cycle tests (Apache-2.0)."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

P = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('stride_check', P / 'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class FocusedTests(unittest.TestCase):
    def test_scalar_all_strides(self):
        tau = v.UNITS[2]
        for s in (-17, 0, 1, 9):
            for rho in v.ROOTS:
                self.assertEqual(v.resolvent([tau], s, rho),
                                 [[v.quotient(v.ONE, v.minus(tau, rho))]])

    def test_zero_root_direct_inverse(self):
        phases = list(v.UNITS[:6])
        inverse = v.resolvent(phases, 2, v.ZERO)
        for i, row in enumerate(inverse):
            for j, value in enumerate(row):
                expected = v.quotient(v.ONE, phases[(i+2) % 6]) if j == (i+2) % 6 else v.ZERO
                self.assertEqual(value, expected)

    def test_partition_and_adjacency(self):
        for n in range(1, 32):
            for s in range(-n, n+1):
                cc = v.cycles(n, s)
                self.assertEqual(sorted(i for c in cc for i in c), list(range(n)))
                for c in cc:
                    for j, i in enumerate(c):
                        self.assertEqual(c[(j+1) % len(c)], (i+s) % n)

    def test_asymmetric_closure_example(self):
        phases = list(v.UNITS[:6])
        h = [v.product([phases[i] for i in c]) for c in v.cycles(6, 2)]
        self.assertEqual(h, [(v.F(-3, 5), v.F(-4, 5)), (v.F(-5, 13), v.F(12, 13))])
        self.assertEqual(v.product(phases), (v.F(63, 65), v.F(-16, 65)))
        with self.assertRaisesRegex(ValueError, 'inverse identity'):
            v.check_inverse(v.operator(phases, 2, v.ROOTS[0]),
                            v.resolvent(phases, 2, v.ROOTS[0], 'global_holonomy'))

    def test_one_singular_cycle_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'singular cycle closure'):
            v.resolvent([v.ONE, v.UNITS[1], v.ONE, v.UNITS[1]], 2, v.ONE)

    def test_dual_phase_is_shifted_not_conjugated(self):
        phases = list(v.UNITS[:6])
        a = v.operator(phases, 2, v.ROOTS[0])
        self.assertEqual(v.operator(v.dual_phases(phases, 2), -2, v.ROOTS[0]), v.transpose(a))

    def test_corrupted_source_manifest_fails_before_execution(self):
        source = json.loads((P / 'SOURCE.json').read_text())
        source['files']['weighted.py'] = '0' * 64
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, 'source hash: weighted.py'):
                v.load_source(P.parents[1], source, Path(tmp))

    def test_missing_source_commit_fails_closed(self):
        source = json.loads((P / 'SOURCE.json').read_text())
        source['commit'] = '0' * 40
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, 'Missing pinned PR628 git object'):
                v.load_source(P.parents[1], source, Path(tmp))


if __name__ == '__main__':
    unittest.main(verbosity=2)
