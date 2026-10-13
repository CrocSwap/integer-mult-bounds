"""Focused independent controls for architectural rejection certificates."""
from fractions import Fraction as Q
import unittest
from audit import (composition_screen, cube_screen, identity, join_control,
                   moment, multiply, rank, subtract, tensor)


class ArchitectureControls(unittest.TestCase):
    def test_join_with_independent_dense_oblique_labels(self):
        # P=u*v with v*u=1. These do not use the audit's sparse examples.
        u, v = [Q(1), Q(2), Q(-1)], [Q(1,2), Q(1,2), Q(1,2)]
        P = [[x*y for y in v] for x in u]
        u, v = [Q(1), Q(3)], [Q(-2), Q(1)]
        R = [[x*y for y in v] for x in u]
        result = join_control(P, R)
        self.assertEqual(result['joined_rank'], 3)
        self.assertEqual(result['rank_saved'], 4)
        self.assertEqual(rank(tensor(P, R)), 1)

    def test_wrong_label_contract_rejected(self):
        with self.assertRaises(ValueError):
            join_control([[Q(2), Q(0)], [Q(0), Q(0)]], identity(2))
        with self.assertRaises(ValueError):
            join_control(identity(2), identity(2))

    def test_rank_subadditivity_does_not_allow_full_m_credit(self):
        P = [[Q(1), Q(0)], [Q(0), Q(0)]]
        E = tensor(identity(2), P)
        D = tensor(subtract(identity(2), P), identity(2))
        self.assertEqual(rank(subtract(D, E)), 2)
        self.assertEqual(rank(subtract(identity(4), E))+rank(D), 4)
        self.assertNotEqual(4-rank(subtract(D, E)), 4)

    def test_affine_residual_rejects_partial_and_full_sharing(self):
        data = composition_screen()
        for x in (Q(0), Q(1,7), Q(1,2), Q(1)):
            rows = {528: 2, 1: 1, 22: 2, 24: 2, 23: 1, 25: 1,
                    552: 1-x, 550: 1-x, 529: x}
            bounds = moment(rows, 575, 4-x)
            self.assertGreater(bounds[0], 1)
            expected_lo = (4*data['unshared_floor_moment'][0]-4
                           +x*data['numerator_minus_role_volume_slope_per_join'][0])
            # Independently evaluated intervals must overlap.
            actual_hi = (4-x)*(bounds[1]-1)
            self.assertLessEqual(expected_lo, actual_hi)

    def test_cube_budget_is_more_favorable_than_source_floor(self):
        data = cube_screen()
        self.assertGreater(data['zero_auxiliary_zero_central_loss_moment'][0], 1)
        self.assertGreater(data['zero_central_loss_one_source_per_label_moment'][0],
                           data['zero_auxiliary_zero_central_loss_moment'][1])
        self.assertEqual(sum(t*n for t, n in data['lower_bound_rows'].items()), 2047)
        self.assertEqual(data['labels'], 2147483648)
        self.assertEqual(data['supplied_binary_factor_size'], 7144448)


if __name__ == '__main__':
    unittest.main()
