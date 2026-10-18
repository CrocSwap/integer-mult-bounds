"""Behavioral controls for the exact proof quantities and their failure modes."""

import json
import unittest
from collections import Counter
from fractions import Fraction
from itertools import combinations
from unittest.mock import patch

import independent
import verify
from vendor.geometry import dot, require, root_data
from vendor.mixed import ANCHOR, cliques, projective, rational_rank


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads(verify.read_bytes(verify.PACKAGE / "RESULT.json"))
        cls.roots, cls.points, cls.labels, _ = root_data()
        cls.vertices = tuple(tuple(v) for v in cls.receipt["vertices_doubled"])
        cls.adjacency = cls.receipt["adjacency"]

    def test_original_profile(self):
        result = verify.application()
        self.assertEqual(result["endpoint_allowance"], 108)
        self.assertEqual(result["minimum_weight_only_two_flat_cuts"], 20)

    def test_complete_clique_set(self):
        primary = set(cliques(self.adjacency, 4))
        edges = independent.edges(self.vertices, independent.inventory())
        self.assertEqual(primary, set(independent.pair_join(edges)))
        self.assertEqual(len(primary), 4459)

    def test_rank_oracles(self):
        anchor = tuple(2 * x for x in ANCHOR)
        for chosen in cliques(self.adjacency, 4):
            rows = (anchor, *(self.vertices[i] for i in chosen))
            self.assertEqual(rational_rank(rows), independent.integer_rank(rows))

    def test_singular_fixture(self):
        rows = [(1, 0, 0, 0, 0, 0, 0, 0)] * 5
        self.assertEqual(independent.integer_rank(rows), 1)
        self.assertEqual(rational_rank(rows), 1)

    def test_shift_cost(self):
        for values in ((0, 1, 2, 3, 4, 5), (0, 0, 1, 1, 2, 2), (2,) * 6):
            expected = 6 - max(Counter(values).values())
            actual = min(
                sum(x + shift != 0 for x in values)
                for shift in (*(-x for x in values), Fraction(1, 2))
            )
            self.assertEqual(actual, expected)

    def test_mixed_attaining_witness(self):
        witness = self.receipt["mixed"]["witness"]
        rows = tuple(tuple(v) for v in witness["vertices_doubled"])
        self.assertEqual(rational_rank(rows), 5)
        costs = verify.support_costs(rows, self.points)
        cuts = set(witness["cuts"])
        self.assertEqual(len(cuts), 30)
        self.assertEqual(sum(c for i, c in enumerate(costs) if i not in cuts), 121)
        directions = set(independent.inventory())
        endpoints = ((0,) * 8, *rows)
        for a, b in combinations(endpoints, 2):
            self.assertIn(
                projective(tuple(x - y for x, y in zip(a, b, strict=True))), directions
            )

    def test_mixed_cut_boundary(self):
        rows = self.receipt["mixed"]["witness"]["vertices_doubled"]
        costs = sorted(verify.support_costs(rows, self.points))
        self.assertLess(sum(costs[:81]), sum(costs[:82]))

    def test_common_shift_scaling(self):
        rows = self.receipt["mixed"]["witness"]["vertices_doubled"]
        for point in self.points:
            values = (0, *(dot(point, row) for row in rows))
            self.assertEqual(
                max(Counter(values).values()),
                max(Counter(7 - 3 * x for x in values).values()),
            )

    def test_root_attainment_relaxation(self):
        self.assertEqual(independent.root_spectrum(), 120)
        result = verify.root_census(self.roots)
        self.assertEqual(result["minimum_after_38_full_root_cuts"], 120)

    def test_data_mutant(self):
        sources = verify.bind_sources()
        with patch.object(verify, "read_bytes", return_value=b"mutant"):
            with self.assertRaisesRegex(ValueError, "P112 data hash"):
                verify.bind_data(
                    verify.PACKAGE / "x", self.points, self.labels, sources
                )

    def test_source_mutant(self):
        original = verify.read_bytes

        def changed(path):
            raw = original(path)
            return raw + b"# mutation" if path.name == "mixed.py" else raw

        with patch.object(verify, "read_bytes", side_effect=changed):
            with self.assertRaisesRegex(ValueError, "retained hash"):
                verify.bind_sources()

    def test_graph_mutant(self):
        changed = list(self.adjacency)
        i, j = next(
            (i, j) for i, j in combinations(range(58), 2) if changed[i] >> j & 1
        )
        changed[i] ^= 1 << j
        changed[j] ^= 1 << i
        self.assertNotEqual(set(cliques(changed, 4)), set(cliques(self.adjacency, 4)))

    def test_invalid_dimensions(self):
        with self.assertRaisesRegex(ValueError, "six-vertex dimensions"):
            verify.support_costs([], self.points)
        with self.assertRaisesRegex(ValueError, "rank shape"):
            independent.integer_rank([])

    def test_rejection_stays_on_under_optimization(self):
        with self.assertRaisesRegex(ValueError, "control"):
            require(False, "control")


if __name__ == "__main__":
    unittest.main()
