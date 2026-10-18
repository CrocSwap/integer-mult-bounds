#!/usr/bin/env python3
"""Behavioral tests and deliberate failure controls for verify.py."""

import importlib.util
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "verify", Path(__file__).with_name("verify.py"))
verify = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify)


class Q8RegularCellRankBoundTests(unittest.TestCase):
    def test_full_receipt(self):
        result = verify.build_receipt()
        self.assertEqual(result["status"], "PASS_Q8_REGULAR_CELL_RANK_BOUND")
        self.assertEqual(result["finite_checks"]["rank_couplings_by_r"],
                         {"1": 1, "2": 6, "3": 28})
        self.assertEqual(result["finite_checks"]["coupled_matrix_fixtures"], 560)

    def test_non_idempotent_coupling_rejected(self):
        with self.assertRaises(ValueError):
            verify.validate_idempotent(1, 2, 2)

    def test_q8_order_four_positive_control(self):
        table = verify.group_table()
        self.assertEqual(table[1][1], 4)
        self.assertEqual(table[2][2], 4)
        self.assertEqual(table[3][3], 4)

    def test_missing_order_four_action_fails_rank_target(self):
        rows = verify.identity(8)
        rank = verify.gf2_rank(verify.xor_rows(rows, verify.identity(8)))
        self.assertNotEqual(rank, 6)


if __name__ == "__main__":
    unittest.main()
