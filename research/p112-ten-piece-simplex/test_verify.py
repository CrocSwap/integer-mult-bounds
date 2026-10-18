"""Behavioral and mathematical controls; safe under Python optimization."""

from itertools import combinations, product
from pathlib import Path
import tempfile
import unittest

from beta import (CAP, NEW_SHAPES, beta_receipt, incidence,
                  original_survivor, prior_cover_audit, ten_piece_obstruction,
                  two_flat_cuts)
from geometry import canonical, dot, require, root_data, root_plane_receipt
from verify import DATA, ROOT, bind_data, simplex_control


def subset_cut_oracle(weights):
    """Independent cover formulation by disjoint subsets, no ternary assignment."""
    best = sum(CAP[w] for w in weights)
    for left in range(1 << len(weights)):
        if sum(w for i, w in enumerate(weights) if left >> i & 1) > 6:
            continue
        for right in range(1 << len(weights)):
            if left & right or sum(w for i, w in enumerate(weights) if right >> i & 1) > 6:
                continue
            uncovered = sum(CAP[w] for i, w in enumerate(weights)
                            if not (left | right) >> i & 1)
            best = min(best, uncovered)
    return best


class MathematicalControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.roots, cls.points, cls.labels, _ = root_data()

    def test_five_new_shapes(self):
        for shape, margin in zip(NEW_SHAPES, (11, 11, 27, 27, 27), strict=True):
            self.assertTrue(original_survivor(shape))
            row = ten_piece_obstruction(shape)
            self.assertEqual(row["margin"], margin)
            self.assertTrue(row["excluded"])

    def test_small_support_boundary_loses_the_contradiction(self):
        self.assertEqual(incidence(25, [20]*6)["margin"], 3)
        row = incidence(26, [20]*6)
        self.assertEqual(row["margin"], -5)
        self.assertFalse(row["excluded"])

    def test_large_support_boundary_loses_the_contradiction(self):
        self.assertEqual(incidence(26, [18, 20, 20, 20, 20, 20])["margin"], 3)
        row = incidence(26, [19, 20, 20, 20, 20, 20])
        self.assertEqual(row["margin"], -1)
        self.assertFalse(row["excluded"])

    def test_original_count_does_not_prove_three_of_the_exclusions(self):
        margins = [ten_piece_obstruction(shape)["original_margin"] for shape in NEW_SHAPES]
        self.assertEqual(margins, [-21, -17, -3, 1, 1])

    def test_quotient_and_root_thresholds_are_strict(self):
        with self.assertRaisesRegex(ValueError, "quotient"):
            incidence(33, [20] * 6)
        with self.assertRaisesRegex(ValueError, "root-edge"):
            incidence(30, [20] * 6)

    def test_invalid_support_inputs(self):
        for small, large in ((-1, [20]*6), (True, [20]*6), (26, [20]*5),
                             (26, [20]*5 + [False]), (26, [113]*6)):
            with self.assertRaises(ValueError):
                incidence(small, large)

    def test_invalid_weights(self):
        for weights in ((2, 3), (7,)*11, (6, 5, 4, 3, 2), (2, 3, 4, 5, 8)):
            with self.assertRaises(ValueError):
                original_survivor(weights)
        with self.assertRaises(ValueError):
            ten_piece_obstruction((2, 3, 4, 5, 6))

    def test_original_residue_and_overlap_control(self):
        result = beta_receipt()
        self.assertEqual(len(result["pinned_survivors"]), 38)
        self.assertEqual(result["overlap_control"]["minimum_anchor_cuts"], 12)
        self.assertIn("PR3167:H4-p12", result["overlap_control"]["prior_exclusions"])

    def test_all_alternative_quotient_bases(self):
        for shape, minimum, anchor_minimum in zip(NEW_SHAPES, (12, 16, 12, 14, 16),
                                                (None, None, None, 18, 18), strict=True):
            answer = prior_cover_audit(shape)
            self.assertEqual(answer["minimum_cuts"], minimum)
            self.assertEqual(answer["minimum_anchor_cuts"], anchor_minimum)
            self.assertEqual(answer["prior_exclusions"], [])
            independent, anchor = 113, 113
            for indices in combinations(range(10), 5):
                basis = tuple(shape[i] for i in indices)
                if sum(CAP[w] for w in basis) >= 53:
                    continue
                cuts = subset_cut_oracle(basis)
                independent = min(independent, cuts)
                if any(w <= 4 for i, w in enumerate(shape) if i not in indices):
                    anchor = min(anchor, cuts)
            self.assertEqual((independent, None if anchor == 113 else anchor),
                             (minimum, anchor_minimum))

    def test_cover_oracle_matches_independent_subsets(self):
        for weights in product((2, 3, 4, 5, 6), repeat=3):
            self.assertEqual(two_flat_cuts(weights), subset_cut_oracle(weights))

    def test_two_level_and_edge_coordinate_incidence(self):
        maximum = 0
        for values in product((0, 1), repeat=6):
            count = sum(a != b for a, b in combinations(values, 2))
            maximum = max(maximum, count)
            self.assertLessEqual(count, 9)
        self.assertEqual(maximum, 9)
        self.assertEqual(sum(a != b for a, b in combinations((-1, 1, 0, 0, 0, 0), 2)), 9)

    def test_outside_charge_for_arbitrary_endpoint_values(self):
        for values in product((-1, 0, 1, 2), repeat=6):
            unequal = sum(a != b for a, b in combinations(values, 2))
            nonzero = sum(v != 0 for v in values)
            self.assertLessEqual(unequal, 5 * nonzero)
            self.assertLessEqual(unequal, 4 * nonzero + 1)

    def test_charge_bound_for_all_zero_and_equality_patterns(self):
        # Every possible equality relation among six endpoint values is
        # represented using zero and at most six distinct nonzero values.
        for values in product(range(7), repeat=6):
            unequal = sum(a != b for a, b in combinations(values, 2))
            self.assertLessEqual(unequal, 4 * sum(v != 0 for v in values) + 1)

    def test_sharp_root_simplex(self):
        result = simplex_control(self.roots, self.points)
        self.assertGreater(result["histogram"][9], 0)
        changed = list(self.roots)
        changed[0] = changed[1]
        with self.assertRaises(ValueError):
            root_plane_receipt(changed)

    def test_bound_input_and_byte_mutation(self):
        path = ROOT / DATA
        self.assertEqual(len(bind_data(path, self.points, self.labels)), 64)
        with tempfile.TemporaryDirectory() as temporary:
            changed = Path(temporary) / "changed.txt"
            changed.write_bytes(path.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "changed P112"):
                bind_data(changed, self.points, self.labels)

    def test_root_evaluation_span_and_distance(self):
        self.assertEqual({sum(dot(root, point) != 0 for point in self.points)
                          for root in self.roots}, {53, 56})
        self.assertEqual(len({canonical(row) for row in self.roots}), 120)
        with self.assertRaises(ValueError):
            require(False, "optimized Python must retain this guard")


if __name__ == "__main__":
    unittest.main()
