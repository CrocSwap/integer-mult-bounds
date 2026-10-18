"""Behavioral controls for the literal witness and arbitrary-shift inequality."""

import copy
import importlib.util
import json
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("rank6_controls", PACKAGE / "verify.py")
verify = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify)


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g = verify.source_geometry()
        _, cls.points, cls.labels, _ = cls.g.root_data()
        cls.result = json.loads((PACKAGE / "RESULT.json").read_text())

    def test_actual_boundary(self):
        got = verify.validate_witness(
            self.g, self.points, self.labels, self.result["witness30"]
        )
        self.assertEqual(got["intersection_dimension"], 2)
        self.assertEqual(got["rational_ranks_code_pieces_join"], [8, 3, 9])

    def test_coefficient_corruption(self):
        witness = copy.deepcopy(self.result["witness30"])
        witness["piece_coefficients"][0][0] *= -1
        with self.assertRaisesRegex(ValueError, "code identity"):
            verify.validate_witness(self.g, self.points, self.labels, witness)

    def test_one_fewer_cut_is_not_witness(self):
        witness = copy.deepcopy(self.result["witness30"])
        witness["common_cut_indices"].pop()
        with self.assertRaisesRegex(ValueError, "thirty"):
            verify.validate_witness(self.g, self.points, self.labels, witness)

    def test_duplicate_or_zero_support(self):
        for mutant in ("duplicate", "zero"):
            witness = copy.deepcopy(self.result["witness30"])
            if mutant == "duplicate":
                witness["piece_support_indices"][0][0] = witness[
                    "piece_support_indices"
                ][0][1]
            else:
                witness["piece_coefficients"][0][0] = 0
            with self.assertRaisesRegex(ValueError, "malformed"):
                verify.validate_witness(self.g, self.points, self.labels, witness)

    def test_nonmodal_shift_pointwise_bound(self):
        count = 0
        for singleton in range(3):
            for value in (-8, -4, 4, 8):
                unshifted = [0, 0, 0]
                unshifted[singleton] = value
                for shift in range(-12, 13):
                    bits = [int(v + shift != 0) for v in unshifted]
                    self.assertGreaterEqual(sum(bits), 2 - bits[singleton])
                    count += 1
        self.assertEqual(count, 300)
        for shift in range(-12, 13):
            self.assertGreaterEqual(sum(v + shift != 0 for v in (-4, 0, 4)), 2)

    def test_losing_relaxations(self):
        self.assertGreater(2 * (78 - 29), 3 * 32)
        self.assertLessEqual(2 * (78 - 29), 3 * (20 + 16))
        self.assertLessEqual(2 * (76 - 29), 3 * 32)
        self.assertEqual(2 * (78 - 30), 3 * 32)

    def test_binary_bounds_and_dependency(self):
        for invalid in ((512,), (-1,), (True,)):
            with self.assertRaises(ValueError):
                verify.binary_basis(invalid)
        self.assertEqual(verify.binary_basis((3, 5, 6)), verify.binary_basis((3, 5)))
        with self.assertRaisesRegex(ValueError, "dependent"):
            verify.coordinate_map((3, 3))


if __name__ == "__main__":
    unittest.main()
