"""Behavioral controls for the shortening certificate. Apache-2.0."""

import copy
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import independent
import model


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads((model.PACKAGE / "RESULT.json").read_bytes())
        cls.roots, cls.labels = independent.lattice()
        cls.values = independent.root_values(cls.roots)

    def test_all_frame_types_and_endpoint_counts_are_excluded(self):
        for row in self.receipt["punctures"]:
            for u in range(5):
                lower, upper = model.defect_bounds(
                    29, row["cost"], row["singletons"], u
                )
                self.assertGreater(lower, upper)
        self.assertEqual(sum(r["count"] for r in self.receipt["punctures"]), 2025)

    def test_support_thirty_is_an_open_budget_and_literal_witness(self):
        self.assertEqual(model.defect_bounds(30, 12, 0, 0), (64, 64))
        self.assertEqual(
            independent.check_witness(
                self.receipt["witness30"], self.roots, self.labels, self.values
            ),
            [(34, 39), (34, 39)],
        )

    def test_support_domain_is_enforced(self):
        for bad in (-1, 31, 29.0, True):
            with self.assertRaises(ValueError):
                model.defect_bounds(bad, 12, 0, 0)

    def test_puncture_domain_is_enforced(self):
        for f, t in ((12, 4), (10, 0), (8, 12), (16, 0)):
            with self.assertRaises(ValueError):
                model.defect_bounds(29, f, t, 0)

    def test_endpoint_count_is_enforced(self):
        for u in (-1, 5, 2.0, True):
            with self.assertRaises(ValueError):
                model.defect_bounds(29, 12, 0, u)

    def test_label_domain_is_enforced(self):
        for labels in ((0,), (512,), (-1,), (True,), (1.0,), tuple([1] * 121)):
            with self.assertRaises(ValueError):
                model.span(labels)

    def test_missing_singleton_breaks_full_closure_contract(self):
        groups = [row["indices"][:] for row in self.receipt["singleton_facts"]]
        groups[0].pop()
        with self.assertRaisesRegex(ValueError, "closure"):
            model.singleton_facts(self.labels, groups)

    def test_ten_labels_really_can_fail_to_pin_rank_six(self):
        for row in self.receipt["singleton_facts"]:
            group = row["indices"]
            hyperplane = next(
                [i for i in group if (n & self.labels[i]).bit_count() % 2 == 0]
                for n in range(512)
                if sum((n & self.labels[i]).bit_count() % 2 == 0 for i in group) == 10
            )
            self.assertEqual(
                independent.binary_rank([self.labels[i] for i in hyperplane]), 5
            )

    def test_code_coefficient_mutation_preserving_support_is_rejected(self):
        witness = copy.deepcopy(self.receipt["witness30"])
        index = next(j for j, x in enumerate(witness["endpoints"][0]) if x)
        witness["endpoints"][0][index] *= 2
        with self.assertRaisesRegex(ValueError, "code identities"):
            independent.check_witness(witness, self.roots, self.labels, self.values)

    def test_witness_support_receipt_mutation_is_rejected(self):
        witness = copy.deepcopy(self.receipt["witness30"])
        witness["endpoint_supports"][0].pop()
        with self.assertRaisesRegex(ValueError, "support binding"):
            independent.check_witness(witness, self.roots, self.labels, self.values)

    def test_duplicate_witness_frame_is_rejected(self):
        witness = copy.deepcopy(self.receipt["witness30"])
        witness["frame"][0] = witness["frame"][1]
        with self.assertRaisesRegex(ValueError, "frame indices"):
            independent.check_witness(witness, self.roots, self.labels, self.values)

    def test_lost_small_piece_is_rejected(self):
        witness = copy.deepcopy(self.receipt["witness30"])
        witness["common"].pop()
        with self.assertRaisesRegex(ValueError, "common support"):
            independent.check_witness(witness, self.roots, self.labels, self.values)

    def test_witness_claimed_intersection_mutation_is_rejected(self):
        witness = copy.deepcopy(self.receipt["witness30"])
        witness["intersection_dimension"] = 2
        with self.assertRaisesRegex(ValueError, "modular ranks"):
            independent.check_witness(witness, self.roots, self.labels, self.values)

    def test_changed_geometry_is_rejected_before_import(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as temp:
            root = Path(temp)
            package = root / "research/test-package"
            source = root / "research/p112-ten-piece-simplex/geometry.py"
            package.mkdir(parents=True)
            source.parent.mkdir(parents=True)
            (package / "SOURCES.json").write_bytes(
                (model.PACKAGE / "SOURCES.json").read_bytes()
            )
            source.write_bytes(
                (
                    model.REPO / "research/p112-ten-piece-simplex/geometry.py"
                ).read_bytes()
                + b"\nraise RuntimeError('must not execute')\n"
            )
            with (
                patch.object(model, "REPO", root),
                patch.object(model, "PACKAGE", package),
                self.assertRaisesRegex(ValueError, "source hash"),
            ):
                model.geometry()


if __name__ == "__main__":
    unittest.main(verbosity=2)
