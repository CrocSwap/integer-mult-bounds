# SPDX-License-Identifier: Apache-2.0
"""Focused checks for the frozen two-coordinate composition receipt."""
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("pair_verify", HERE / "verify.py")
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)
RESULT = json.loads((HERE / "RESULT.json").read_bytes())


class TemporalGaugePairTests(unittest.TestCase):
    def test_exact_combined_invoices_and_endpoints(self):
        self.assertEqual(RESULT["status"], "PASS_COMPLEX_L248_L253_TEMPORAL_COMPOSITION")
        for orientation, expected in (("forward", 135730), ("backward", 135746)):
            row = RESULT["orientations"][orientation]
            self.assertEqual(row["combined_invoice"]["complex_primitives"], expected)
            self.assertEqual(row["formal_endpoint"]["formal_input_columns"], 712)
            self.assertTrue(row["formal_endpoint"]["all_restored"])

    def test_disjoint_support_is_recorded_both_directions(self):
        for row in RESULT["orientations"].values():
            self.assertEqual(row["shared_add_ids"], 0)
            self.assertEqual(row["combined_schedule_ids"], 167)
            self.assertEqual(row["L248_incident_adds"], 71)
            self.assertEqual(row["L253_incident_adds"], 96)

    def test_paid_profile_and_selected_kappa_are_fixed(self):
        self.assertEqual(RESULT["selected_kappa"], "836330098538459/500000000000000000")
        for row in RESULT["orientations"].values():
            self.assertEqual(row["combined_invoice"]["paid_profile"],
                             {"1": 2412, "2": 418, "3": 432, "4": 142, "5": 82, "8": 8})
            self.assertEqual(row["combined_invoice"]["charged_payload_bits"], 192)

    def test_overlap_mutation_is_rejected(self):
        with self.assertRaises(ValueError):
            VERIFY.require_disjoint({10: 1}, {10: -1})

    def test_duplicate_and_missing_add_mutations_are_rejected(self):
        with self.assertRaises(ValueError):
            VERIFY.indexed_schedule([[10, 0], [10, 1]], {10}, "test")
        with self.assertRaises(ValueError):
            VERIFY.indexed_schedule([[10, 0]], {10, 11}, "test")

    def test_wrong_invoice_mutation_is_rejected(self):
        with self.assertRaises(ValueError):
            VERIFY.check_invoice(135731, 135730, "test")


if __name__ == "__main__":
    unittest.main(verbosity=2)
