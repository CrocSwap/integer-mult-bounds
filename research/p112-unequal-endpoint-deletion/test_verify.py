"""Independent finite controls and failure cases for the two applications."""

# Copyright 2026 Nick Petalas

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
from ledger import (
    CAP,
    TARGETS,
    application,
    coordinate_invoice,
    historical_inventory,
    historical_survivor,
    prior_cover_rows,
    surviving_dimension,
)


class DeletionTests(unittest.TestCase):
    def test_both_actual_profiles(self):
        inventory = historical_inventory()
        self.assertEqual(inventory["survivor_count"], 69)
        for weights in TARGETS:
            row = application(weights)
            self.assertEqual(row["intersection_after_lower"], 5)
            self.assertEqual(row["quotient_dimension"], 4)
            self.assertEqual(row["small_support_cap"], 28)
            self.assertEqual(row["endpoint_caps"], [12, 20, 20, 20, 20, 20])
            self.assertEqual(row["coordinate_incidence_upper"], 784)
            self.assertEqual(row["margin"], 11)
            self.assertTrue(historical_survivor(weights))
            self.assertEqual(sum(w - 2 for w in weights), 35)

    def test_sharp_dimension_loss(self):
        for dimension in range(1, 11):
            for code in range(dimension + 1):
                for removed in range(dimension + 1):
                    actual = len(set(range(code)) & set(range(removed, dimension)))
                    self.assertEqual(actual, surviving_dimension(dimension, code, removed))
        self.assertEqual(surviving_dimension(10, 6, 2), 4)
        self.assertNotEqual(surviving_dimension(10, 6, 1), 6)

    def test_invalid_dimension_ledger(self):
        for values in ((10, 11, 1), (10, 6, -1), (10, 6, 11),
                       (17, 6, 1), (10, True, 1), (10, 6, 1.0)):
            with self.subTest(values=values), self.assertRaises(ValueError):
                surviving_dimension(*values)

    def test_nonuniform_endpoint_is_essential_for_this_invoice(self):
        row = coordinate_invoice(28, (12,) + (20,) * 5)
        self.assertEqual(row["old_incidence_upper"], 812)
        self.assertGreaterEqual(row["old_incidence_upper"], 795)
        uniform = coordinate_invoice(28, (20,) * 6)
        self.assertEqual(uniform["coordinate_incidence_upper"], 816)
        self.assertFalse(uniform["excluded"])
        self.assertFalse(coordinate_invoice(30, (19,) * 6)["excluded"])

    def test_strict_support_cutoffs(self):
        # First fails 53, second hits 70 while keeping quotient support below 53.
        for small, caps in ((33, (20,) * 6), (30, (20,) * 6),
                            (28, (36,) + (20,) * 5)):
            with self.subTest(small=small, caps=caps), self.assertRaises(ValueError):
                coordinate_invoice(small, caps)

    def test_invalid_support_and_weight_inputs(self):
        for small, caps in ((-1, (20,) * 6), (True, (20,) * 6),
                            (28, (20,) * 5), (28, (20,) * 5 + (-1,)),
                            (28, (20,) * 5 + (20.0,))):
            with self.subTest(small=small, caps=caps), self.assertRaises(ValueError):
                coordinate_invoice(small, caps)
        for weights in (TARGETS[0][::-1], (*TARGETS[0][:-1], 8), (2,) * 11):
            with self.assertRaises(ValueError):
                historical_survivor(weights)
        self.assertFalse(historical_survivor((6,) * 9))
        with self.assertRaises(ValueError):
            application((4, 4, 4, 6, 6, 6, 6, 6, 6, 7))

    def test_quotient_normalization_and_independent_codewords(self):
        images = [(1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0)]
        images += [(i, i * i, i ** 3, i + 1) for i in range(6)]
        circuits = []
        for i in range(1, 6):
            row = [Fraction(0)] * 9
            row[i + 3], row[3] = Fraction(1, i + 1), -1
            for j in range(3):
                row[j] = -Fraction(i ** (j + 1), i + 1)
            self.assertEqual(tuple(sum(row[j] * images[j][k] for j in range(9))
                                   for k in range(4)), (0, 0, 0, 0))
            circuits.append(row)
        for i, row in enumerate(circuits):
            self.assertEqual(row[4:], [Fraction(1, i + 2) if i == j else 0
                                       for j in range(5)])

    def test_independent_two_flat_subset_oracle(self):
        expected = [2, 3]
        for weights, count in zip(TARGETS, expected, strict=True):
            rows = prior_cover_rows(weights)
            self.assertEqual(len(rows), count)
            for row in rows:
                basis = row["basis"]
                costs = []
                for paid in product((False, True), repeat=4):
                    unpaid = [w for w, p in zip(basis, paid, strict=True) if not p]
                    for left in product((False, True), repeat=len(unpaid)):
                        totals = [sum(w for w, side in zip(unpaid, left, strict=True)
                                      if side == value) for value in (False, True)]
                        if max(totals) <= 6:
                            costs.append(sum(CAP[w] for w, p in
                                             zip(basis, paid, strict=True) if p))
                self.assertEqual(min(costs), row["minimum_two_flat_cuts"])
                self.assertGreater(min(costs), 14)
            self.assertEqual(min(row["minimum_two_flat_cuts"] for row in rows), 16)

    def test_unmodified_historical_checker(self):
        verify.bound_inputs()
        command = [sys.executable, "-B", str(verify.ROOT / verify.INPUTS[3])]
        result = subprocess.run(command, check=True, capture_output=True,
                                text=True, timeout=30)
        rows = [tuple(map(int, line.split())) for line in result.stdout.splitlines()]
        self.assertEqual(len(rows), 24)
        self.assertIn((6, 4, 69, 1), rows)
        self.assertEqual(result.stderr, "")

    def test_endpoint_patterns_and_root_hypothesis_control(self):
        self.assertEqual(verify.endpoint_receipt()["equality_assignments"], 7 ** 6)
        # Arbitrary six values can have 15 unequal pairs. Nine is root-specific.
        self.assertEqual(sum(a != b for a, b in combinations(range(6), 2)), 15)
        # Independent arithmetic checks all possible nonzero endpoint counts.
        for k in range(7):
            self.assertLessEqual(k * (6 - k) + k * (k - 1) // 2, 4 * k + 1)

    def test_every_input_is_authenticated(self):
        self.assertEqual(set(verify.bound_inputs()), set(verify.INPUTS))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in verify.INPUTS:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(verify.ROOT / name, target)
            for name in verify.INPUTS:
                target = root / name
                raw = target.read_bytes()
                target.write_bytes(raw + b"\n")
                with patch.object(verify, "ROOT", root), self.assertRaisesRegex(
                        ValueError, "input hash differs"):
                    verify.bound_inputs()
                target.write_bytes(raw)

    def test_external_exclusive_output_and_receipt_comparison(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "receipt.json"
            verify.publish({"control": True}, output)
            self.assertEqual(json.loads(output.read_text()), {"control": True})
            with self.assertRaises(FileExistsError):
                verify.publish({}, output)
            (root / "RESULT.json").write_text('{"expected": true}\n')
            with patch.object(verify, "PACKAGE", root), self.assertRaisesRegex(
                    ValueError, "committed receipt differs"):
                verify.publish({}, None)
        with self.assertRaisesRegex(ValueError, "outside checkout"):
            verify.publish({}, verify.PACKAGE / "forbidden.json")
        with self.assertRaisesRegex(ValueError, "absolute"):
            verify.publish({}, Path("relative.json"))


if __name__ == "__main__":
    unittest.main()
