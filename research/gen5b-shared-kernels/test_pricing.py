from fractions import Fraction as F
import unittest

import baseline_arithmetic as baseline
import packing
import reprice


class PricingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = reprice.reprice({1: 18, 2: -12}, {2: 12, 3: -18, 4: 6})

    def test_profile_and_packing(self):
        x = self.result
        self.assertEqual((x['calls'], x['rank_mass'], x['literal_stock']),
                         (482665, 2455070, 1229735))
        self.assertEqual(x['deficit'], 4400)
        self.assertEqual(x['packing']['feasible_bins'], 161467)
        self.assertTrue(x['packing']['optimal'])
        self.assertEqual(x['packing']['unused_coordinate_capacity'], 0)

    def test_adjacent_moment_bounds(self):
        x = self.result
        self.assertEqual(x['root_bracket'],
                         [F(750469712644613, 10 ** 18), F(750469712644614, 10 ** 18)])
        self.assertLess(x['moment_interval'][1], 1)
        self.assertGreater(x['adjacent_moment_interval'][0], 1)

    def test_outer_constraints_and_scope(self):
        x = self.result
        self.assertEqual(x['kappa'], F(749906929903449, 10 ** 18))
        self.assertEqual(len(x['assembly']['strict_constraints']), 47)
        self.assertTrue(all(v > 0 for v in x['assembly']['strict_constraints'].values()))
        self.assertEqual(x['assembly']['adjacent_grid_rejected'], ['g3_above_kappa'])
        self.assertFalse(x['physical_admission'])

    def test_missing_bank_is_rejected(self):
        x = self.result['packing']
        patterns = [dict(widths=row['widths'][:], count=row['count']) for row in x['patterns']]
        patterns[0]['count'] -= 1
        with self.assertRaises(AssertionError):
            packing.verify(120, x['demand'], patterns)

    def test_float_delta_is_rejected(self):
        with self.assertRaises(ValueError):
            reprice.reprice({1: 18.0}, {})


if __name__ == '__main__':
    unittest.main()
