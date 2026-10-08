"""Exact screens, bank sharing, and composition with the new depth guard."""
from dataclasses import replace
from fractions import Fraction as Q
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from experiments import ternary_direction as td


class PrimeFamilyScreens(unittest.TestCase):
    def test_binomial_scalar_identity_for_each_screened_prime(self):
        for p in (3, 5, 7, 11, 13):
            for intersection in range(2*p):
                got = (td.comb(intersection, p-1)-int(intersection == p-1)) % p
                self.assertEqual(got, int(intersection == 2*p-1))

    def test_positive_deficit_boundary(self):
        self.assertIsNone(td.prime_case(3, 22, False))
        self.assertIsNotNone(td.prime_case(3, 23, False))
        row = td.prime_case(3, 28, True)
        self.assertEqual(row['role_floor'], 983178)
        self.assertEqual(row['center_dimension'], 26)
        self.assertEqual(row['eta'], Q(39312, 2*28**3*(98280+983178)))

    def test_global_maxima_and_infinite_tails(self):
        for p, best_h in ((3, 28), (5, 29), (7, 33)):
            free = td.prime_family(p, False)
            outputs = td.prime_family(p, True)
            self.assertEqual(free['h'], best_h)
            self.assertEqual(outputs['h'], best_h)
            self.assertLess(outputs['kappa_upper'], free['kappa_upper'])
            self.assertLess(free['tail_bit_saving_upper'], free['bit_saving_lower'])
            self.assertLess(outputs['tail_bit_saving_upper'], outputs['bit_saving_lower'])
        self.assertLess(td.prime_family(3, True)['kappa_upper'], 12*td.PR7_KAPPA)
        self.assertLess(td.larger_prime_output_tail()['kappa_strict_upper'], Q(718, 10**14))

    def test_role_budget_needed_for_orders_of_magnitude(self):
        rows = td.fixed_h28_role_targets()['targets']
        self.assertEqual(rows['10']['necessary_roles_at_most'], 2659452)
        self.assertEqual(rows['100']['necessary_roles_at_most'], 177493)
        self.assertEqual(rows['100']['necessary_additions_at_most_with_direct_outputs'], 78835)
        self.assertTrue(rows['1000']['impossible_even_with_free_roles'])


class GuardComposition(unittest.TestCase):
    def test_paired_producer_and_monotone_shared_bank(self):
        row = td.paired_guard_control(8)
        self.assertEqual(row['three_stage_path_rank_upper'], 560)
        self.assertEqual(row['shared_bank_join']['permutation_size'], 56)
        for invocation in row['invocations']:
            self.assertEqual(invocation['maximum_path_descent'], 8)
            self.assertEqual(invocation['decreasing_edges'], 9)

    def test_pr7_exponent_and_all_assembly_margins_survive(self):
        row = td.combined_witness()
        self.assertEqual(row['parameters']['kappa'], td.PR7_KAPPA)
        self.assertEqual(row['guard']['C1'], Q(1001099, 10**6))
        self.assertEqual(row['guard']['path_branching'], 22120)
        self.assertEqual(row['complex_leaf_saving'], Q(38961, 10**12))
        self.assertGreater(row['leaf_saving_over_current_bit'], 5)
        self.assertTrue(all(x > 0 for x in row['constraint_slacks'].values()))
        self.assertGreater(min(row['margins'].values()), td.PR7_KAPPA)
        bad = replace(td.parameters(), beta=Q(1, 1000))
        with self.assertRaises(ValueError):
            td.dg.research_witness(n=td.complex_counts(), parameters=bad)


if __name__ == '__main__':
    unittest.main()
