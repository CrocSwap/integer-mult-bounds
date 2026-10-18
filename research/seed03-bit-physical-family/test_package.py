#!/usr/bin/env python3
"""Focused tests for the selected PR589 physical-family operator check."""
from __future__ import annotations

import gzip
import importlib.util
import json
from fractions import Fraction as Q
from pathlib import Path
import unittest

VERIFY_PATH = Path(__file__).with_name("verify.py")
SPEC = importlib.util.spec_from_file_location("seed03_verify", VERIFY_PATH)
verify = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify)


ROOT = Path(__file__).resolve().parents[2]


class PhysicalFamilyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = verify.verify()

    def test_exact_family_receipt_and_two_idle_intervals(self):
        family = self.result["family"]
        self.assertEqual((family["pair"], family["copy"], family["child_ids"]),
                         (1, 0, [0, 7]))
        self.assertEqual(len(family["roles"]), 4)
        self.assertTrue(all(x["equal"] and x["columns_checked"] == 128
                            for x in self.result["interval_results"].values()))

    def test_q_perp_projection_is_exact_rank_seven(self):
        word = json.loads(gzip.decompress((ROOT / verify.WORD).read_bytes()))
        q = tuple(word["lines"][0])
        K = verify.q_perp(q)
        self.assertEqual(sum(K[i][i] for i in range(8)), 7)
        self.assertTrue(all(sum(K[i][k] * K[k][j] for k in range(8)) == K[i][j]
                            for i in range(8) for j in range(8)))
        self.assertTrue(all(sum(K[i][j] * q[j] for j in range(8)) == 0
                            for i in range(8)))

    def test_address_operator_is_an_involution_on_every_basis_column(self):
        word = json.loads(gzip.decompress((ROOT / verify.WORD).read_bytes()))
        p = verify.make_projector(tuple(range(1, 9)), tuple(word["lines"][0]), "test")
        for index in range(128):
            state = [Q(0)] * 128
            state[index] = Q(1)
            state = tuple(state)
            self.assertEqual(verify.apply_D(p, verify.apply_D(p, state)), state)

    def test_fault_controls_reject_wrong_or_missing_operations(self):
        controls = self.result["summary"]["rejected_controls"]
        self.assertEqual(controls, ["omitted_helper", "equal_rank_wrong_axis",
                                    "duplicate_helper", "wrong_source_port"])

    def test_positive_order_control_covers_all_six_orders(self):
        self.assertEqual(self.result["summary"]["helper_order_permutations_checked"], 6)


if __name__ == "__main__":
    unittest.main(verbosity=2)
