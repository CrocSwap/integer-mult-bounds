# SPDX-License-Identifier: Apache-2.0
"""Fast checks. Run: python3 -B -m unittest discover -s research/pending-claims-independent-pricing -p test_package.py -v"""
import json
import math
import sys
import unittest
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import arith  # noqa: E402


class Tests(unittest.TestCase):
    def test_prime_logarithms(self):
        for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 37, 47, 73):
            iv = arith.ln_int(p)
            self.assertLess(float(iv.hi - iv.lo), 1e-90)
            self.assertAlmostEqual(float(iv.lo), math.log(p), places=14)
        self.assertAlmostEqual(float(arith.ln_int(44).lo), math.log(44), places=14)

    def test_reduction_reproduces_selected(self):
        k, margin, binding = arith.kappa_from(Q('416181814685169713943/250000000000000000000000'),
                                              Q('1733427039589844234749/1000000000000000000000000'))
        self.assertEqual((str(k), binding), ('1661960547713947/1000000000000000000', 'complex'))

    def test_snapshot_provenance_shape(self):
        snap = json.loads((HERE / 'SNAPSHOT.json').read_text())
        self.assertEqual(len(snap), 16)
        for c in snap:
            self.assertEqual(len(c['head']), 40)
            for path, blob in c['sources'].values():
                self.assertEqual(len(blob), 40)


if __name__ == '__main__':
    unittest.main()
