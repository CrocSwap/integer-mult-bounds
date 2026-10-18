#!/usr/bin/env python3
"""Behavioral controls for exact maps, invoices and interpreter boundaries."""

import copy
import importlib.util
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("window_audit", Path(__file__).with_name("verify.py"))
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)


class WindowAuditTests(unittest.TestCase):
    def test_literal_expected_invoices(self):
        pivot = (0, 1, 2, 0, 1)
        self.assertEqual(V.gap_dp(pivot), 40)
        self.assertEqual(V.gap_dp(pivot + pivot), 132)
        self.assertEqual(V.fusion_saving(pivot, pivot), -56)
        self.assertEqual(V.fusion_saving((0,), (0,)), -24)
        self.assertEqual(V.fusion_saving((0,), (1,)), 0)

    def test_all_single_octet_phases(self):
        for octet in range(3):
            for phase in range(4):
                columns = V.replay(V.octet_power(octet, phase))
                self.assertEqual(len(V.octet_power(octet, phase)), (0, 20, 16, 20)[phase])
                for column, values in enumerate(columns):
                    expected = [int(row == column) for row in range(56)]
                    if 32 + 8 * octet <= column < 40 + 8 * octet:
                        expected[column] = 0
                        local = column - 32 - 8 * octet
                        expected[32 + 8 * octet + V.rotated_row(local, -phase)] = 1
                    self.assertEqual(values, expected)

    def test_wrong_erase_and_missing_erase(self):
        word = V.schedule((0,))
        erase = next(
            i
            for i, (kind, target, source, sign) in enumerate(word)
            if kind == "ADD" and target >= 32 and source in range(8, 32) and sign == -1
        )
        bad = word.copy()
        kind, target, source, sign = bad[erase]
        bad[erase] = kind, target, 8, sign
        with self.assertRaisesRegex(ValueError, "dirty map"):
            V.check_map(bad, (0,))
        with self.assertRaisesRegex(ValueError, "dirty map"):
            V.check_map(word[:erase] + word[erase + 8 :], (0,))

    def test_deferral_does_not_deliver_at_first_call_boundary(self):
        joint = V.schedule((0, 1))
        # Sixteen copied rows, then the first complete 68-record child.
        with self.assertRaisesRegex(ValueError, "dirty map"):
            V.check_map(joint[:84], (0,))
        V.check_map(V.schedule((0,)), (0,))

    def test_phase_indexed_reader_mutation(self):
        word = V.schedule((0, 1), phase_indexed=True)
        bad = word.copy()
        index = next(i for i, gate in enumerate(bad) if gate == ("ADD", 3, 40, 1))
        bad[index] = "ADD", 0, 40, 1
        with self.assertRaisesRegex(ValueError, "dirty map"):
            V.check_map(bad, (0, 1))

    def test_corrupt_reported_invoice_is_rejected(self):
        source = copy.deepcopy(V.read_source())
        source["pivot_k5k10"]["price"]["pivot_joint10_typed_fixed"]["primitives"] = 1568
        with self.assertRaisesRegex(ValueError, "source invoice"):
            V.verify_programs(source)

    def test_boundaries_and_capacity(self):
        with self.assertRaisesRegex(ValueError, "not supported"):
            V.schedule((0,), literal=True, phase_indexed=True)
        for blocks in ((), (3,), (True,), (0,) * 65):
            with self.assertRaises(ValueError):
                V.schedule(blocks)
        for gate in (
            ("OTHER", 0, None, 0),
            ("ADD", 0, 0, 1),
            ("ADD", 56, 1, 1),
            ("ADD", 0, 56, 1),
            ("ADD", 0, 1, 2),
        ):
            with self.assertRaises(ValueError):
                V.replay([gate])
        with self.assertRaisesRegex(ValueError, "capacity"):
            V.replay([("NEG", 0, None, 0)] * 40001)
        self.assertEqual(V.gap_dp((0,) * 64), 1260)


if __name__ == "__main__":
    unittest.main()
