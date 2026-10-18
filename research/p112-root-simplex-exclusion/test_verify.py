"""Behavioral controls for the root-simplex proof's delicate implications."""

import json
import tempfile
import unittest
from itertools import product
from pathlib import Path

from geometry import (SIMPLE, canonical, chamber_receipt, dot, flat_capacity,
                      primitive, root_data, root_plane_receipt, solve)
from simplex import SHAPES, incidence_bound, obstruction, simplex_receipt, unequal_edges
from verify import DATA, PACKAGE, ROOT, bind_data


class ProofControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.roots, cls.points, cls.labels, cls.coordinates = root_data()

    def test_source_and_label_reconstruction(self):
        digest = bind_data(ROOT / DATA, self.points, self.labels)
        self.assertEqual(digest, "ac4a48851b922f2a433684b60c74768ae3bb4fc5e8990ffe63e3942bb3c2ea34")
        self.assertEqual(len(set(self.labels)), 112)
        self.assertTrue(all(x & 1 for x in self.labels))

    def test_changed_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "changed.txt"
            path.write_bytes((ROOT / DATA).read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "changed P112"):
                bind_data(path, self.points, self.labels)

    def test_changed_labels_and_roots_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "label binding"):
            bind_data(ROOT / DATA, self.points, self.labels[::-1])
        with self.assertRaisesRegex(ValueError, "root binding"):
            bind_data(ROOT / DATA, self.points[::-1], self.labels)

    def test_root_support_distance_and_chamber(self):
        result = chamber_receipt(self.roots, self.points, self.coordinates)
        self.assertEqual(result["root_support_histogram"], {"53": 112, "56": 8})
        self.assertEqual(max(result["rank_six_parabolic_counts"]), 36)
        self.assertEqual(result["ray_zero_counts"], [42, 28, 22, 14, 16, 23, 37, 63])

    def test_chamber_mutation_is_rejected(self):
        changed = list(self.coordinates)
        changed[0] = (1, -1, 0, 0, 0, 0, 0, 0)
        with self.assertRaisesRegex(ValueError, "positivity"):
            chamber_receipt(self.roots, self.points, changed)

    def test_complete_root_plane_check(self):
        self.assertEqual(root_plane_receipt(self.roots), {"2": 3780, "3": 3360})
        with self.assertRaisesRegex(ValueError, "root-plane input"):
            root_plane_receipt(self.roots[:-1])

    def test_orthogonal_roots_have_no_third_line(self):
        a, b = (2, -2, 0, 0, 0, 0, 0, 0), (0, 0, 2, -2, 0, 0, 0, 0)
        self.assertEqual(dot(a, b), 0)
        self.assertNotIn(canonical(tuple(x - y for x, y in zip(a, b, strict=True))), self.roots)

    def test_a2_common_scale_control(self):
        a, b = (-2, 2, 0, 0, 0, 0, 0, 0), (-2, 0, 2, 0, 0, 0, 0, 0)
        root_directions = {primitive(r) for r in self.roots}
        good = primitive(tuple(x - y for x, y in zip(a, b, strict=True)))
        bad = primitive(tuple(x - 2*y for x, y in zip(a, b, strict=True)))
        self.assertIn(good, root_directions)
        self.assertNotIn(bad, root_directions)

    def test_literal_simplex_is_sharp(self):
        result = simplex_receipt(self.roots, self.points)
        self.assertEqual(result["maximum"], 9)
        self.assertEqual(result["incidence_histogram"], {"0": 2, "5": 36, "8": 42, "9": 32})
        self.assertEqual(unequal_edges((0, 1, -1, 0, 0, 0)), 9)
        self.assertEqual(unequal_edges((0, 0, 0, 1, 1, 1)), 9)

    def test_root_hypothesis_cannot_be_dropped(self):
        self.assertEqual(unequal_edges((0, 0, 1, 1, 2, 2)), 12)
        self.assertEqual(unequal_edges((0, 1, 2, 3, 4, 5)), 15)

    def test_six_value_support_charge_exhaustively(self):
        for values in product(range(4), repeat=6):
            self.assertLessEqual(unequal_edges(values), 5 * sum(x != 0 for x in values))

    def test_both_literal_exclusions(self):
        first, second = [obstruction(*shape) for shape in SHAPES]
        self.assertEqual((first["outside_edge_lower"], first["outside_edge_upper"]), (615, 600))
        self.assertEqual((second["outside_edge_lower"], second["outside_edge_upper"]), (561, 560))
        self.assertTrue(first["excluded"] and second["excluded"])

    def test_one_extra_line_loses_the_one_incidence_margin(self):
        result = incidence_bound(27, [12, 20, 20, 20, 20, 20])
        self.assertEqual(result["contradiction_margin"], -8)
        self.assertFalse(result["excluded"])

    def test_quotient_and_root_threshold_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "quotient basis"):
            incidence_bound(33, [20] * 6)
        with self.assertRaisesRegex(ValueError, "edge directions"):
            incidence_bound(30, [20] * 6)
        with self.assertRaisesRegex(ValueError, "support bounds"):
            incidence_bound(True, [20] * 6)
        with self.assertRaisesRegex(ValueError, "bounded pieces"):
            obstruction((2, 5, 5), (7,) * 6)

    def test_flat_inputs_and_dimension_are_bounded(self):
        with self.assertRaisesRegex(ValueError, "five/six"):
            flat_capacity(self.labels, 7)
        with self.assertRaisesRegex(ValueError, "invalid P112"):
            flat_capacity(self.labels[:-1], 5)

    def test_singular_coordinates_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "singular"):
            solve([(0,) * 8] * 8, (0,) * 8)
        for j in range(8):
            ray = solve(SIMPLE, [int(i == j) for i in range(8)])
            self.assertEqual([dot(r, ray) for r in SIMPLE], [int(i == j) for i in range(8)])

    def test_receipt_retains_exact_census_totals(self):
        result = json.loads((PACKAGE / "RESULT.json").read_text())
        self.assertEqual([row["subspaces"] for row in result["flat_capacities"]], [3309747, 788035])
        self.assertEqual([row["maximum"] for row in result["flat_capacities"]], [12, 20])
        self.assertEqual([row["contradiction_margin"] for row in result["exclusions"]], [15, 1])


if __name__ == "__main__":
    unittest.main()
