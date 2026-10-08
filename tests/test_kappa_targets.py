"""Check optimistic bounds independently against the complete rank counts."""
from fractions import Fraction as Q
from math import comb
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_kappa_targets import (optimistic_eta, family_ceiling,
                                 data_floor_kappa_upper, excluded_arity_threshold)
from aligned_bit_network import KAPPA, ROLES, counts_from


class TargetBounds(unittest.TestCase):
    def test_counts_and_discarded_costs(self):
        for h in (39, 40, 50, 61, 199):
            v = comb(h, 3)
            N, m = v**3, h**3
            deficit = N-6*v*v*h*(h-1)
            self.assertEqual(optimistic_eta(h), Q(deficit, 2*N*m))
            W = 2*N+2*v*v*(3*v+h)
            self.assertEqual(optimistic_eta(h, True), Q(deficit, W*m))
            self.assertLess(optimistic_eta(h, True), optimistic_eta(h))
        actual = counts_from(ROLES)
        self.assertLess(actual['eta'], optimistic_eta(50, True))
        self.assertEqual(optimistic_eta(50), Q(1, 10**6))

    def test_exact_all_h_ceiling(self):
        for keep, factor in ((False, 27), (True, 7)):
            cert = family_ceiling(keep)
            self.assertEqual(cert['optimistic_best_h'], 50)
            self.assertLess(cert['tail_bit_saving_upper'], cert['bit_saving_lower'])
            self.assertLess(cert['kappa_upper'], factor*KAPPA)

    def test_necessary_target_boundaries(self):
        previous = None
        for factor in (10, 100, 1000, 10000):
            target = factor*KAPPA
            threshold = excluded_arity_threshold(target)['first_excluded_m']
            self.assertLessEqual(data_floor_kappa_upper(threshold), target)
            self.assertGreater(data_floor_kappa_upper(threshold-1), target)
            if previous is not None:
                self.assertLess(threshold, previous)
            previous = threshold

    def test_reject_nonpositive_deficit(self):
        with self.assertRaises(ValueError):
            optimistic_eta(38)


if __name__ == '__main__':
    unittest.main()
