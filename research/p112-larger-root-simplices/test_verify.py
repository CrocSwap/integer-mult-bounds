"""Behavioral controls and independent small exact checks."""

import copy
import json
import tempfile
import unittest
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

from simplex import (
    CAP,
    TARGETS,
    basis_killed,
    cover_audit,
    feasible,
    incidence_bound,
    simplex_fixture,
    survivor_rows,
    target_bound,
)
from vendor.geometry import root_data
from verify import DATA, PACKAGE, ROOT, bind_data, bind_sources, check_receipt


def rational_rank(rows):
    matrix = [[Fraction(x) for x in row] for row in rows]
    rank = 0
    for column in range(8):
        pivot = next((i for i in range(rank, len(matrix)) if matrix[i][column]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        scale = matrix[rank][column]
        matrix[rank] = [x / scale for x in matrix[rank]]
        for i in range(rank + 1, len(matrix)):
            scale = matrix[i][column]
            matrix[i] = [x - scale * y for x, y in zip(matrix[i], matrix[rank], strict=True)]
        rank += 1
    return rank


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.roots, cls.points, cls.labels, _ = root_data()
        cls.sources = bind_sources()

    def test_exact_new_margins(self):
        self.assertEqual([target_bound(b)["margin"] for b in TARGETS], [9, 4, 12])
        self.assertTrue(all(target_bound(b)["excluded"] for b in TARGETS))

    def test_original_six_vertex_control(self):
        self.assertEqual(incidence_bound(5, 26, [12] + [20] * 5)["margin"], 1)
        self.assertEqual(incidence_bound(5, 20, [20] * 6)["margin"], 15)

    def test_one_more_small_coordinate_loses_each_exclusion(self):
        for b in TARGETS:
            self.assertFalse(incidence_bound(b, 27, [12] + [20] * b)["excluded"])

    def test_one_more_large_coordinate_boundary(self):
        self.assertEqual(incidence_bound(7, 26, [13] + [20] * 7)["margin"], -3)

    def test_strict_quotient_boundary(self):
        with self.assertRaisesRegex(ValueError, "quotient basis"):
            incidence_bound(6, 33, [20] * 7)

    def test_strict_root_boundary(self):
        with self.assertRaisesRegex(ValueError, "edge directions"):
            incidence_bound(6, 30, [20] * 7)

    def test_invalid_shapes(self):
        for b, small, caps in ((4, 26, [20] * 5), (6, -1, [20] * 7),
                               (6, 26, [20] * 6), (6, 26, [True] * 7)):
            with self.assertRaises(ValueError):
                incidence_bound(b, small, caps)
        with self.assertRaises(ValueError):
            target_bound(True)

    def test_all_two_level_incidence_assignments(self):
        for n in (6, 7, 8, 9):
            maximum = 0
            for tail in product((0, 1), repeat=n - 1):
                values = (0,) + tail
                count = sum(x != y for x, y in combinations(values, 2))
                maximum = max(maximum, count)
            self.assertEqual(maximum, n * n // 4)
            self.assertLessEqual(2 * n - 3, maximum)

    def test_literal_simplex_ranks_and_incidence(self):
        maxima = []
        for b in TARGETS:
            fixture = simplex_fixture(self.roots, self.points, b)
            self.assertEqual(rational_rank(fixture["vertices"]), b)
            self.assertEqual(sum(fixture["incidence_histogram"].values()), 112)
            maxima.append(fixture["maximum"])
        self.assertEqual(maxima, [12, 16, 18])

    def test_actual_survivors(self):
        for b, expected in ((6, 69), (7, 154), (8, 251)):
            rows = survivor_rows(b)
            self.assertEqual(len(rows), expected)
            self.assertIn(TARGETS[b], rows)
            self.assertTrue(feasible(TARGETS[b], b))
            self.assertFalse(basis_killed(TARGETS[b], b))

    def test_independent_target_prefix_and_packing_checks(self):
        thresholds = [53, 78, 92, 100, 106, 109, 111, 112]
        for b, weights in TARGETS.items():
            # Direct prefix checks for these targets, which contain no sevens.
            for level in range(1, b + 1):
                self.assertGreaterEqual(sum(CAP[w] for w in weights[:4 + level]),
                                        thresholds[level - 1])
            self.assertEqual(sum(weights[:4]), 17)
            self.assertEqual(sum(CAP[w] for w in weights[:4]), 38)
            self.assertGreater(sum(weights[:4]), 12)
            self.assertLess(sum(w - 2 for w in weights), 6 * b)

    def test_cover_and_anchor_overlap_controls(self):
        for weights in TARGETS.values():
            result = cover_audit(weights)
            self.assertEqual(result["minimum_separate_deletion_budget"], 14)
            self.assertIsNone(result["rank_four_anchor_minimum_budget"])
        with self.assertRaises(ValueError):
            cover_audit((2, 5, 5, 6))

    def test_input_binding_and_label_mutant(self):
        self.assertEqual(bind_data(ROOT / DATA, self.points, self.labels, self.sources),
                         self.sources["files"][2]["sha256"])
        with self.assertRaisesRegex(ValueError, "label binding"):
            bind_data(ROOT / DATA, self.points, self.labels[::-1], self.sources)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "data.txt"
            path.write_bytes((ROOT / DATA).read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "changed P112 input"):
                bind_data(path, self.points, self.labels, self.sources)

    def test_source_binding_and_path_mutants(self):
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory)
            (package / "vendor").mkdir()
            for row in self.sources["retained_files"]:
                path = row["local_path"]
                (package / path).write_bytes((PACKAGE / path).read_bytes())
            manifest = package / "SOURCES.json"
            manifest.write_text(json.dumps(self.sources))
            self.assertEqual(bind_sources(package), self.sources)
            path = package / self.sources["retained_files"][0]["local_path"]
            path.write_bytes(path.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "changed retained source"):
                bind_sources(package)
            mutant = copy.deepcopy(self.sources)
            mutant["retained_files"][0]["local_path"] = "../outside"
            manifest.write_text(json.dumps(mutant))
            with self.assertRaisesRegex(ValueError, "invalid retained-source path"):
                bind_sources(package)

    def test_receipt_mutant(self):
        expected = json.loads((PACKAGE / "RESULT.json").read_text())
        check_receipt(expected, copy.deepcopy(expected))
        mutant = copy.deepcopy(expected)
        mutant["exclusions"][0]["coordinate_cap"] = 11
        with self.assertRaisesRegex(ValueError, "receipt differs"):
            check_receipt(mutant, expected)


if __name__ == "__main__":
    unittest.main()
