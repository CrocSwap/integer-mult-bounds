# SPDX-License-Identifier: Apache-2.0
"""Fast checks of the code-disjoint interval arithmetic.

Run: python3 -B -m unittest discover -s research/t37-endpoints-independent -p test_package.py -v
"""
import math
import sys
import unittest
from fractions import Fraction as Q
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import endpoints as E  # noqa: E402


class ArithmeticTests(unittest.TestCase):
    def test_logarithms_bracket_floats(self):
        for k in (2, 3, 4, 5, 6, 7, 8, 42, 48, 64, 73):
            iv = E.ln_int(k)
            self.assertLess(float(iv.hi - iv.lo), 1e-80)
            self.assertAlmostEqual(float(iv.lo), math.log(k), places=14)

    def test_exponential_brackets(self):
        for y in (Q(0), Q(1, 1000), Q(7, 1000), Q(9, 1000)):
            iv = E.exp_small(E.I(y))
            self.assertLessEqual(iv.lo, iv.hi)
            self.assertAlmostEqual(float(iv.lo), math.exp(float(y)), places=14)
            self.assertLess(float(iv.hi - iv.lo), 1e-40)

    def test_exponential_lower_bound_is_rigorous(self):
        y = Q(1, 200)
        iv = E.exp_small(E.I(y))
        partial = sum(y ** k / math.factorial(k) for k in range(30))
        self.assertTrue(iv.lo <= partial <= iv.hi)

    def test_unsupported_prime(self):
        with self.assertRaises(ValueError):
            E.ln_int(11)

    def test_kappa_reduction_matches_record(self):
        k, margin = E.kappa_from(Q('416181814685169713943/250000000000000000000000'),
                                 Q('1733427039589844234749/1000000000000000000000000'))
        self.assertEqual(str(k), '1661960547713947/1000000000000000000')
        self.assertTrue(k < margin <= k + Q(1, 10 ** 18))


if __name__ == '__main__':
    unittest.main()
