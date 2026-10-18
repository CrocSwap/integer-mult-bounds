# SPDX-License-Identifier: Apache-2.0
"""Small independent checks of the exact certificate mechanisms."""
from collections import Counter, defaultdict
from fractions import Fraction as Q
import itertools
import unittest

import verify as audit


class Certificates(unittest.TestCase):
    def test_all_small_equal_mass_multisets(self):
        groups = defaultdict(list)
        for length in range(1, 5):
            for values in itertools.combinations_with_replacement(range(1, 7), length):
                groups[sum(values)].append(values)
        checked = 0
        for group in groups.values():
            for old, new in itertools.combinations(group, 2):
                size = max(len(old), len(new))
                x = sorted(new, reverse=True) + [0] * (size - len(new))
                y = sorted(old, reverse=True) + [0] * (size - len(old))
                forward = all(sum(x[:k]) >= sum(y[:k]) for k in range(size + 1))
                reverse = all(sum(y[:k]) >= sum(x[:k]) for k in range(size + 1))
                status = audit.compare(dict(Counter(new)), dict(Counter(old)))["status"]
                expected = ("new_strictly_better_all_a" if forward else
                            "old_strictly_better_all_a" if reverse else "majorization_inconclusive")
                self.assertEqual(status, expected)
                checked += 1
        self.assertEqual(checked, 1191)

    def test_exact_power_enclosures(self):
        for q in range(2, 9):
            for p in range(1, q):
                for rank in range(1, 17):
                    lo, hi = audit.rank_power_interval(rank, Q(p, q), bits=12)
                    # Exact rational cross-check, separate from scaled radicand construction.
                    self.assertLessEqual(lo ** q, Q(rank) ** (q - p))
                    self.assertGreaterEqual(hi ** q, Q(rank) ** (q - p))
                    self.assertLessEqual(hi - lo, Q(1, 4096))

    def test_real_crossing_is_not_dominance(self):
        d = {1: 7, 3: -3, 7: -2, 16: 1}
        self.assertIsNone(audit.single_positive_tangent(d))
        self.assertEqual(audit.sign_witness(d, Q(1, 650))["sign"], "negative")
        self.assertEqual(audit.sign_witness(d, Q(1, 2))["sign"], "positive")

    def test_nonmajorization_tangent_certificate(self):
        old, new = {1: 7, 3: 4, 16: 1}, {7: 5}
        self.assertEqual(audit.compare(new, old)["status"], "majorization_inconclusive")
        receipt = audit.single_positive_tangent(audit.delta(new, old))
        self.assertEqual(int(receipt["derivative_log_numerator_product"]), 7 ** 35)
        self.assertEqual(int(receipt["derivative_log_denominator_product"]), 3 ** 12 * 16 ** 16)
        self.assertGreater(7 ** 35, 3 ** 12 * 16 ** 16)

    def test_wrong_derivative_has_opposite_signs(self):
        d = {1: -14, 2: 15, 4: -4}
        self.assertIsNone(audit.single_positive_tangent(d))
        self.assertEqual(audit.sign_witness(d, Q(1, 650))["sign"], "positive")
        self.assertEqual(audit.sign_witness(d, Q(1, 2))["sign"], "negative")


if __name__ == "__main__":
    unittest.main()
