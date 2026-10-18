"""Behavioral and boundary controls for the mixed-edge support theorem."""

import copy
import json
import random
import shutil
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import independent
import mixed
import verify
from vendor.geometry import dot, frame_lines, root_lines


class MixedEdgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.roots = root_lines()
        cls.points = tuple(r for r in cls.roots if r not in frame_lines())
        cls.directions, cls.normals, _ = mixed.alphabet(cls.roots, cls.points)
        cls.vertices = mixed.intersections(cls.directions)
        cls.adjacency = mixed.compatibility(cls.vertices, cls.directions)
        cls.expected = json.loads(verify.read_bytes(verify.PACKAGE / "RESULT.json"))

    def test_01_changed_alphabet_is_necessary(self):
        root_directions = {mixed.projective(r) for r in self.roots}
        self.assertNotIn(mixed.ANCHOR, root_directions)
        self.assertEqual(sum(dot(p, mixed.ANCHOR) != 0 for p in self.points), 70)
        self.assertEqual(len(self.directions), 248)

    def test_02_anchor_symmetries_preserve_the_actual_frame(self):
        self.assertEqual(
            mixed.anchor_orbit(self.roots, frame_lines(), self.normals), 128
        )

    def test_03_incomplete_root_inventory_fails(self):
        with self.assertRaises(ValueError):
            mixed.alphabet(self.roots[:-1], self.points)

    def test_04_missing_or_duplicated_direction_fails(self):
        with self.assertRaises(ValueError):
            mixed.intersections(self.directions[:-1])
        with self.assertRaises(ValueError):
            mixed.intersections(self.directions[:-1] + self.directions[:1])

    def test_05_every_candidate_has_both_legal_incident_edges(self):
        allowed = set(self.directions)
        anchor = tuple(2 * x for x in mixed.ANCHOR)
        for vertex in self.vertices:
            self.assertIn(mixed.projective(vertex), allowed)
            difference = tuple(x - y for x, y in zip(vertex, anchor, strict=True))
            self.assertIn(mixed.projective(difference), allowed)
        self.assertEqual(
            independent.gram_vertices(independent.direction_inventory()), self.vertices
        )

    def test_06_graph_is_separately_reconstructed(self):
        self.assertEqual(
            independent.graph(self.vertices, self.directions), self.adjacency
        )
        self.assertEqual(sum(row.bit_count() for row in self.adjacency) // 2, 595)
        for i, neighbors in enumerate(self.adjacency):
            self.assertFalse(neighbors >> i & 1)
            for j in range(58):
                self.assertEqual(neighbors >> j & 1, self.adjacency[j] >> i & 1)

    def test_07_clique_boundary_and_complete_coverage(self):
        self.assertEqual(list(mixed.cliques(self.adjacency, 0)), [()])
        self.assertEqual(sum(1 for _ in mixed.cliques(self.adjacency, 7)), 10520)
        for size in (-1, 8):
            with self.assertRaises(ValueError):
                list(mixed.cliques(self.adjacency, size))
        with self.assertRaises(ValueError):
            list(mixed.cliques(self.adjacency[:-1], 7))

    def test_08_two_exact_rank_methods_and_dependent_controls(self):
        identity = tuple(tuple(int(i == j) for j in range(8)) for i in range(8))
        self.assertEqual(mixed.rational_rank(identity), 8)
        self.assertEqual(independent.integer_rank(identity), 8)
        self.assertEqual(mixed.rational_rank(identity[:-1] + identity[:1]), 7)
        randomizer = random.Random(3156)
        for _ in range(64):
            rows = tuple(
                tuple(randomizer.randrange(-4, 5) for _ in range(8)) for _ in range(8)
            )
            self.assertEqual(mixed.rational_rank(rows), independent.integer_rank(rows))
        with self.assertRaises(ValueError):
            mixed.rational_rank(())

    def test_09_positive_witness_and_one_extra_cut_boundary(self):
        rows = self.expected["mixed"]["witness"]["vertices_doubled"]
        self.assertEqual(mixed.rational_rank(rows), 8)
        values = [(0, *(dot(p, row) for row in rows)) for p in self.points]
        self.assertEqual(mixed.surviving_support(values, 32)[0], 182)
        self.assertEqual(mixed.surviving_support(values, 33)[0], 179)
        for i in range(8):
            self.assertIn(mixed.projective(rows[i]), self.directions)
            for j in range(i):
                difference = tuple(x - y for x, y in zip(rows[i], rows[j], strict=True))
                self.assertIn(mixed.projective(difference), self.directions)

    def test_10_support_quantifiers_and_invalid_budgets(self):
        identical = [(Fraction(7),) * 9] * 112
        distinct = [tuple(range(9))] * 112
        self.assertEqual(mixed.surviving_support(identical, 0)[0], 0)
        self.assertEqual(mixed.surviving_support(distinct, 112)[0], 0)
        self.assertEqual(mixed.surviving_support(distinct, 32)[0], 640)
        for budget in (-1, 113, True):
            with self.assertRaises(ValueError):
                mixed.surviving_support(distinct, budget)
        with self.assertRaises(ValueError):
            mixed.surviving_support(distinct[:-1], 32)

    def test_11_all_root_branch_and_both_rank_seven_extensions(self):
        result = mixed.all_root_census(self.roots)
        self.assertEqual(result["minimum_after_40_cuts"], 204)
        final = [row["orbit_sizes"] for row in result["steps"] if row["rank"] == 7]
        self.assertEqual(final, [[1], []])

    def test_12_actual_profile_and_losing_prior_cover(self):
        result = mixed.application()
        self.assertEqual(result["original_survivors"], 251)
        self.assertEqual(result["margin"], 2)
        self.assertEqual(result["edge_support_cap"], 72)
        self.assertEqual(result["weight_only_two_six_flat_cut_allowance"], 20)

    def test_13_changed_receipt_cannot_pass(self):
        for section, key in (
            ("mixed", "minimum_after_32_cuts"),
            ("application", "margin"),
            ("graph", "edges"),
        ):
            changed = copy.deepcopy(self.expected)
            changed[section][key] -= 1
            with self.assertRaises(ValueError):
                verify.check_receipt(changed, self.expected)

    def test_14_changed_frozen_source_cannot_pass(self):
        with tempfile.TemporaryDirectory(prefix="p112-source-control-") as directory:
            package = Path(directory)
            shutil.copyfile(verify.PACKAGE / "SOURCES.json", package / "SOURCES.json")
            shutil.copytree(verify.PACKAGE / "vendor", package / "vendor")
            verify.bind_sources(package)
            (package / "vendor").chmod(0o700)
            mutant = package / "vendor/geometry.py"
            mutant.chmod(
                0o600
            )  # Change only this test-owned copy, even from a read-only export.
            mutant.write_bytes(b"# changed source\n")
            with self.assertRaises(ValueError):
                verify.bind_sources(package)

    def test_15_bad_projective_vector_and_changed_live_input(self):
        for row in ((0,) * 8, (1, 0)):
            with self.assertRaises(ValueError):
                mixed.projective(row)
        with tempfile.TemporaryDirectory(prefix="p112-live-control-") as directory:
            path = Path(directory) / "bad-data.txt"
            path.write_bytes(b"truncated input\n")
            with self.assertRaises(ValueError):
                verify.bind_data(path, (), (), verify.bind_sources())


if __name__ == "__main__":
    unittest.main()
