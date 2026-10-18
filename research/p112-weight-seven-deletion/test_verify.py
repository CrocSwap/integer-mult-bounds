"""Behavioral, source-binding and losing-bound controls for the obstruction."""

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path
from unittest.mock import patch

import verify
from geometry import root_data
from obstruction import (RETAINED, TARGET, application, coordinate_bound,
                         intersection_after_deletion, original_survivor,
                         prior_cover_audit)


class ObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.roots, cls.points, cls.labels, _ = root_data()

    def test_actual_profile_and_dimension_ledger(self):
        result = application()
        self.assertEqual(result["target"], list(TARGET))
        self.assertEqual(result["retained_weights"], list(RETAINED))
        self.assertEqual(result["retained_intersection_lower"], 5)
        self.assertEqual(result["retained_quotient_dimension"], 4)
        self.assertEqual(result["new_profile_exclusions"], 1)
        self.assertEqual(result["margin"], 11)

    def test_intersection_loss_is_sharp_not_free(self):
        # Coordinate subspaces give literal sharp cases for every dimension.
        for dimension in range(1, 10):
            for code_dimension in range(dimension + 1):
                for removed in range(dimension + 1):
                    retained = set(range(removed, dimension))
                    code = set(range(code_dimension))
                    actual = len(retained & code)
                    self.assertEqual(actual, intersection_after_deletion(
                        dimension, code_dimension, removed))
        self.assertEqual(intersection_after_deletion(9, 6, 2), 4)
        self.assertNotEqual(intersection_after_deletion(9, 6, 1), 6)

    def test_invalid_dimension_inputs(self):
        for values in ((9, 10, 1), (9, 6, -1), (9, 6, 10),
                       (17, 6, 1), (9, True, 1), (9, 6, 1.0)):
            with self.subTest(values=values), self.assertRaises(ValueError):
                intersection_after_deletion(*values)

    def test_quotient_normalization_on_exact_linear_fixture(self):
        # This is a linear-algebra fixture, not an impossible P112 realization.
        images = [(1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0)]
        images += [(i, i * i, i ** 3, i + 1) for i in range(6)]
        circuits = []
        for i in range(1, 6):
            row = [Fraction(0)] * 9
            row[i + 3], row[3] = Fraction(1, i + 1), -1
            row[0], row[1] = -Fraction(i, i + 1), -Fraction(i * i, i + 1)
            row[2] = -Fraction(i ** 3, i + 1)
            image = tuple(sum(row[j] * images[j][k] for j in range(9))
                          for k in range(4))
            self.assertEqual(image, (0, 0, 0, 0))
            circuits.append(row)
        # A diagonal five-by-five minor certifies all five circuits independent.
        for i, row in enumerate(circuits):
            for j in range(5):
                self.assertEqual(row[j + 4], Fraction(1, i + 2) if i == j else 0)

    def test_new_bound_and_losing_old_bound(self):
        row = coordinate_bound(24, [20] * 6)
        self.assertEqual(row["quotient_support_cap"], 44)
        self.assertEqual(row["edge_support_cap"], 64)
        self.assertEqual(row["coordinate_incidence_upper"], 784)
        self.assertEqual(row["old_incidence_upper"], 816)
        self.assertEqual(row["old_margin"], -21)

    def test_support_boundary_must_not_be_excluded(self):
        self.assertEqual(coordinate_bound(25, [20] * 6)["margin"], 3)
        row = coordinate_bound(26, [20] * 6)
        self.assertEqual(row["margin"], -5)
        self.assertFalse(row["excluded"])

    def test_quotient_and_root_cutoffs_are_strict(self):
        for small, caps in ((33, [20] * 6), (30, [20] * 6),
                            (24, [36] + [20] * 5)):
            with self.subTest(small=small, caps=caps), self.assertRaises(ValueError):
                coordinate_bound(small, caps)

    def test_invalid_support_inputs(self):
        for small, caps in ((-1, [20] * 6), (True, [20] * 6),
                            (24, [20] * 5), (24, [20] * 5 + [-1]),
                            (24, [20] * 5 + [20.0])):
            with self.subTest(small=small, caps=caps), self.assertRaises(ValueError):
                coordinate_bound(small, caps)

    def test_original_profile_is_a_strict_budget_survivor(self):
        self.assertTrue(original_survivor(TARGET))
        self.assertEqual(sum(w - 2 for w in TARGET), 35)
        self.assertFalse(original_survivor((6,) * 9))  # excess 36 is not strict
        for weights in (TARGET[::-1], TARGET[:-1] + (8,), (2,) * 11):
            with self.assertRaises(ValueError):
                original_survivor(weights)

    def test_unmodified_predecessor_count(self):
        result = subprocess.run(
            [sys.executable, "-B", str(verify.PACKAGE / "vendor/bk2b.py")],
            check=True, capture_output=True, text=True, timeout=30)
        rows = [tuple(map(int, line.split())) for line in result.stdout.splitlines()]
        self.assertEqual(len(rows), 24)
        self.assertEqual([row for row in rows if row[:2] == (6, 4)], [(6, 4, 69, 1)])
        self.assertEqual(result.stderr, "")

    def test_all_prior_covers_with_a_separate_subset_oracle(self):
        rows = prior_cover_audit()
        self.assertEqual([row["basis"] for row in rows], [[4, 4, 4, 6]])
        cap = {4: 8, 6: 20}
        for row in rows:
            weights = row["basis"]
            candidates = []
            for paid in product((False, True), repeat=len(weights)):
                remaining = [w for w, cut in zip(weights, paid, strict=True) if not cut]
                for left in product((False, True), repeat=len(remaining)):
                    left_sum = sum(w for w, side in
                                   zip(remaining, left, strict=True) if side)
                    right_sum = sum(w for w, side in
                                    zip(remaining, left, strict=True) if not side)
                    if left_sum <= 6 and right_sum <= 6:
                        candidates.append(sum(cap[w] for w, cut in
                                              zip(weights, paid, strict=True) if cut))
            self.assertEqual(min(candidates), row["minimum_two_flat_cuts"])
            self.assertFalse(row["rank_four_anchor"])

    def test_endpoint_patterns_and_literal_root_fixture(self):
        self.assertEqual(verify.endpoint_controls()["value_assignments"], 7 ** 6)
        fixture = verify.simplex_control(self.roots, self.points)
        self.assertEqual(max(map(int, fixture["live_edge_histogram"])), 9)
        self.assertEqual(sum(fixture["live_edge_histogram"].values()), 112)
        # A six-value endpoint pattern can have fifteen unequal pairs. The
        # nine-incidence assertion needs the root-simplex hypothesis.
        self.assertEqual(sum(a != b for a, b in combinations(range(6), 2)), 15)

    def test_retained_source_mutation_is_rejected(self):
        self.assertEqual(len(verify.bound_sources()), 4)
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory)
            shutil.copyfile(verify.PACKAGE / "SOURCES.json", package / "SOURCES.json")
            for name in verify.RETAINED_PATHS:
                target = package / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(verify.PACKAGE / name, target)
            with (package / "geometry.py").open("a", encoding="utf-8") as stream:
                stream.write("\n# mutation\n")
            with patch.object(verify, "PACKAGE", package), self.assertRaisesRegex(
                    ValueError, "changed retained source"):
                verify.bound_sources()

    def test_input_bytes_and_semantic_binding_are_both_checked(self):
        source = verify.ROOT / verify.DATA
        self.assertEqual(len(verify.bind_data(source, self.points, self.labels)), 64)
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory)
            raw = source.read_bytes() + b"\n"
            changed = package / "changed.txt"
            changed.write_bytes(raw)
            with self.assertRaisesRegex(ValueError, "changed P112 input"):
                verify.bind_data(changed, self.points, self.labels)
            pins = json.loads((verify.PACKAGE / "SOURCES.json").read_text())
            for row in pins["files"]:
                if row["usage"] == "input":
                    row["sha256"] = hashlib.sha256(raw).hexdigest()
            (package / "SOURCES.json").write_text(json.dumps(pins))
            wrong_labels = (0,) + self.labels[1:]
            with patch.object(verify, "PACKAGE", package), self.assertRaisesRegex(
                    ValueError, "P112 label binding"):
                verify.bind_data(changed, self.points, wrong_labels)

    def test_receipt_outputs_are_external_and_exclusive(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "receipt.json"
            verify.publish_receipt({"control": True}, output)
            self.assertEqual(json.loads(output.read_text()), {"control": True})
            with self.assertRaises(FileExistsError):
                verify.publish_receipt({}, output)
        with self.assertRaisesRegex(ValueError, "outside checkout"):
            verify.publish_receipt({}, verify.PACKAGE / "forbidden-output.json")


if __name__ == "__main__":
    unittest.main()
