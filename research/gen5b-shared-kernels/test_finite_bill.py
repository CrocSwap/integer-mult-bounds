from fractions import Fraction as F
import unittest

import finite_bill


class FiniteBillTests(unittest.TestCase):
    def test_explicit_cutoff_inequalities(self):
        for delta in (F(1), F(1, 100), F(1, 10 ** 20)):
            for coefficient in (1, 90386288803484701):
                cutoff = finite_bill.cutoff(delta, coefficient)
                self.assertGreaterEqual(F(cutoff) * delta ** 2, 36)
                self.assertGreaterEqual(F(cutoff) * delta,
                                        2 * (4 + (coefficient - 1).bit_length()))

    def test_invalid_gap_rejected(self):
        for delta in (F(0), F(-1), F(2)):
            with self.assertRaises(AssertionError):
                finite_bill.cutoff(delta, 1)


if __name__ == '__main__':
    unittest.main()
