#!/usr/bin/env python3
"""Boundary and admission tests that remain meaningful under optimized Python."""
from fractions import Fraction as F
from pathlib import Path
import importlib.util
import json
import sys
import tempfile
import unittest
import copy

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('fourier_transfer_verifier', HERE/'verify.py')
v = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = v
spec.loader.exec_module(v)


class Contracts(unittest.TestCase):
    def test_log_ceiling_against_integer_loop(self):
        # Independent small-domain implementation, including fractions <1.
        for n in range(1, 32):
            for d in range(1, 32):
                x = F(n, d)
                k, power = 0, F(1)
                while power < x:
                    k, power = k+1, power*2
                while power/2 >= x:
                    k, power = k-1, power/2
                self.assertEqual(v.ceil_log2(x), k)

    def test_square_root_ceiling_at_boundaries(self):
        for k in range(-25, 26):
            pivot = v.power2(2*k)
            for q, expected in [(pivot, k), (pivot*F(1001,1000), k+1),
                                (pivot*F(999,1000), k)]:
                self.assertEqual((v.ceil_log2(q)+1)//2, expected)

    def test_comparison_threshold(self):
        for t in [F(0), F(1,100), F(1,2), F(4,7), F(3,5), F(1), F(10)]:
            for delta in [F(1,10), F(1), F(7,3)]:
                m = t*delta
                diff = v.inherited_bound(delta,m)**2-v.squared_bound(delta,m)
                self.assertEqual(diff, 4*t*(t-F(4,7))/delta**2)
                if 0 < t < F(4,7):
                    self.assertLess(diff, 0)  # Catch a universal-improvement claim.

    def test_invalid_inputs(self):
        for delta, derivative in [(0,1), (-1,1), (1,-1)]:
            with self.assertRaises(ValueError):
                v.squared_bound(delta, derivative)
        for x in [0,-1]:
            with self.assertRaises(ValueError):
                v.ceil_log2(x)

    def test_constant_mode_is_not_dropped(self):
        self.assertTrue(v.sequence_check({0:F(3,7)}))
        self.assertFalse(v.sequence_check({0:F(3,7)},include_constant=False))
        self.assertEqual(v.squared_bound(F(3,2), 0), F(4,9))

    def test_prime_power_scope(self):
        for r in (2,3,4,8,9,16,25,27,49,64):
            self.assertTrue(v.prime_power(r))
        for r in (0,1,6,10,12,15,18,True):
            self.assertFalse(v.prime_power(r))

    def test_source_drift_rejected(self):
        manifest = json.loads((HERE/'SOURCE.json').read_text())
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in manifest['files']:
                dest = root/name
                dest.parent.mkdir(parents=True,exist_ok=True)
                dest.write_bytes(b'intentional corruption')
            with self.assertRaisesRegex(ValueError,'pinned source changed'):
                v.check_sources(root)

    def test_corrupted_receipt_rejected(self):
        receipt = json.loads((HERE/'EXPECTED.json').read_text())
        bad = copy.deepcopy(receipt)
        bad['finite_inverse_oracle']['sample_count'] -= 1
        with self.assertRaisesRegex(ValueError,'committed evidence differs'):
            v.check_receipt(receipt, bad)
        with self.assertRaisesRegex(ValueError,'committed evidence differs'):
            v.check_receipt({'count':1}, {'count':True})


if __name__ == '__main__':
    unittest.main()
