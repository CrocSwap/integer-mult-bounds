"""Behavioral controls for the exact A4 threshold and literal counterexample."""

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import independent
import model
import verify
from algebra import parse_witness, rank
from geometry import root_data


class ThresholdTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = verify.read_json(verify.PACKAGE / "WITNESS.json")
        cls.roots, cls.points, cls.labels, _ = root_data()

    def test_complete_primary_receipt(self):
        verify.check_receipt(
            verify.build(), verify.read_json(verify.PACKAGE / "RESULT.json")
        )

    def test_frame_bound_and_losing_control(self):
        self.assertEqual(model.frame_bound((1, 1, 6)), 13)

    def test_impossible_frame_is_rejected(self):
        for signature in ((0, 0, 8), (0, 3, 5), (1, 0, 7), (1, 1, 5), (True, 1, 6)):
            with self.subTest(signature=signature), self.assertRaises(ValueError):
                model.frame_bound(signature)

    def test_complete_independent_receipt(self):
        self.assertEqual(
            independent.build(), verify.read_json(verify.PACKAGE / "INDEPENDENT.json")
        )

    def test_endpoint_coefficient_change_is_rejected(self):
        raw = copy.deepcopy(self.raw)
        raw["endpoints_sparse"][0][0][1] *= -1
        with self.assertRaisesRegex(ValueError, "literal endpoint"):
            model.witness_receipt(self.roots, self.points, self.labels, raw)

    def test_duplicate_or_out_of_range_cut_is_rejected(self):
        for replacement in (self.raw["cuts"][1], 112, True):
            raw = copy.deepcopy(self.raw)
            raw["cuts"][0] = replacement
            with self.subTest(replacement=replacement), self.assertRaises(ValueError):
                parse_witness(raw)

    def test_sparse_shape_and_coefficients_are_checked(self):
        for pair in ([0, 0], [112, 1], [True, 1], [0, 3], [0]):
            raw = copy.deepcopy(self.raw)
            raw["endpoints_sparse"][0][0] = pair
            with self.subTest(pair=pair), self.assertRaises(ValueError):
                parse_witness(raw)

    def test_non_A4_directions_are_rejected(self):
        raw = copy.deepcopy(self.raw)
        raw["directions_doubled"][0] = raw["directions_doubled"][1][:]
        with self.assertRaisesRegex(ValueError, "A4 Gram"):
            model.witness_receipt(self.roots, self.points, self.labels, raw)

    def test_incomplete_roots_are_rejected(self):
        with self.assertRaises(ValueError):
            model.orbit_receipt(self.roots[:-1])

    def test_rational_rank_does_not_use_modular_zero(self):
        self.assertEqual(rank(((1, 2, 3), (2, 4, 6))), (0,))
        _, cuts, endpoints = parse_witness(self.raw)
        bad = [list(row) for row in endpoints]
        t = next(i for i in range(112) if i not in cuts)
        bad[1][t] += 101
        self.assertEqual(independent.rank_mod(bad), independent.rank_mod(endpoints))
        with self.assertRaisesRegex(ValueError, "literal inclusion"):
            independent.witness_relations(
                self.points, self.raw["directions_doubled"], cuts, bad
            )

    def test_geometry_source_mutation_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory)
            (package / "SOURCES.json").write_bytes(
                (verify.PACKAGE / "SOURCES.json").read_bytes()
            )
            (package / "geometry.py").write_bytes(
                (verify.PACKAGE / "geometry.py").read_bytes() + b"\n"
            )
            with (
                patch.object(verify, "PACKAGE", package),
                self.assertRaisesRegex(ValueError, "geometry hash"),
            ):
                verify.bind_sources()

    def test_changed_receipt_is_rejected(self):
        raw = verify.read_json(verify.PACKAGE / "RESULT.json")
        altered = json.loads(json.dumps(raw))
        altered["shortening_threshold"] = 29
        with self.assertRaisesRegex(ValueError, "receipt differs"):
            verify.check_receipt(raw, altered)

    def test_rank_capacity_is_enforced(self):
        for rows in ((), ((1,),) * 18, ((1, 2), (3,)), ((9,),)):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                rank(rows)


if __name__ == "__main__":
    unittest.main()
