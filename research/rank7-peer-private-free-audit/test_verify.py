#!/usr/bin/env python3
"""Normative algebra/dataflow fixtures, independent of the large source receipts.

SPDX-License-Identifier: Apache-2.0
"""
from fractions import Fraction
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit_io as io
import checks
import lifetimes as life


def scalar(op):
    return ["scalar", op, ()]


class PrivateFreeTests(unittest.TestCase):
    def test_noncommuting_operator_order(self):
        events = [["zero_buffer", "alloc", "Z0"],
                  ["warp", "L0", 1, (), ()], ["warp", "L0", 2, (), ()],
                  scalar(["add", "Z0", "L0", 1, 1]),
                  ["warp", "L0", -2, (), ()], ["warp", "L0", -1, (), ()],
                  scalar(["add", "Z0", "L0", -1, 1]), ["zero_buffer", "free", "Z0"]]
        value = life.values(events, ["L0"], strict=False)["frees"][0]["value"]
        self.assertEqual(value, [["L0", [], "-1"], ["L0", [2, 1], "1"]])
        dual = life.values(events, ["L0"], backward=True, strict=False)["frees"][0]["value"]
        self.assertEqual(dual, [["L0", [], "-1"], ["L0", [1000002, 1000001], "1"]])

    def test_arbitrary_dirty_columns_and_fractional_cancel(self):
        events = [["zero_buffer", "alloc", "Z0"],
                  scalar(["add", "Z0", "L0", 1, 2]),
                  scalar(["add", "Z0", "L1", 7, 3]),
                  scalar(["add", "Z0", "L0", -1, 2]),
                  scalar(["add", "Z0", "L1", -7, 3]),
                  ["zero_buffer", "free", "Z0"]]
        self.assertEqual(life.values(events, ["L0", "L1"])["frees"][0]["value"], [])
        bad = events[:3] + events[4:]
        self.assertRaisesRegex(ValueError, "nonzero private", life.values, bad, ["L0", "L1"])
        self.assertEqual(life.provenance(events, ["L0", "L1"])["all_frees"]["event_indices"], list(range(6)))

    def test_clear_kills_values_but_keeps_lifetime(self):
        events = [scalar(["add", "L0", "L1", 1, 1]),
                  scalar(["copy", "L0", "L1"]), ["zero_buffer", "alloc", "Z0"],
                  scalar(["add", "Z0", "L0", 1, 1]), scalar(["clear", "Z0"]),
                  ["zero_buffer", "free", "Z0"]]
        self.assertEqual(life.values(events, ["L0", "L1"])["frees"][0]["value"], [])
        cone = life.provenance(events, ["L0", "L1"])["all_frees"]
        self.assertEqual(cone["event_indices"], [2, 4, 5])
        self.assertEqual(cone["boundary_inputs"], [])

    def test_copy_preserves_chart_dependency(self):
        events = [scalar(["add", "L0", "L1", 1, 1]),
                  ["climb", "A", "L0", (), (1,), 1],
                  scalar(["copy", "L0", "L1"]), ["zero_buffer", "alloc", "Z0"],
                  scalar(["add", "Z0", "L0", 1, 1]), ["zero_buffer", "free", "Z0"]]
        cone = life.provenance(events, ["L0", "L1"])["all_frees"]
        self.assertEqual(cone["event_indices"], [1, 2, 3, 4, 5])
        self.assertNotIn("v:L0", cone["boundary_inputs"])
        self.assertIn("c:L0", cone["boundary_inputs"])
        self.assertIn("v:L1", cone["boundary_inputs"])

    def test_private_lifetime_guards(self):
        alloc = ["zero_buffer", "alloc", "Z0"]
        free = ["zero_buffer", "free", "Z0"]
        for events, message in (([free], "live allocation"), ([alloc, alloc], "fresh"),
                                ([alloc], "closed"), ([alloc, free, scalar(["clear", "Z0"])], "outside lifetime")):
            self.assertRaisesRegex(ValueError, message, life.values, events, ["L0"])
        self.assertRaisesRegex(ValueError, "private lifetime", life.provenance,
                               [alloc, free, scalar(["add", "L0", "Z0", 1, 1])], ["L0"])

    def test_zero_root_not_inferred_from_another_root(self):
        events = [["zero_buffer", "alloc", "Z249"], ["zero_buffer", "alloc", "Z395"],
                  scalar(["add", "Z395", "L0", 1, 1]),
                  ["zero_buffer", "free", "Z249"], ["zero_buffer", "free", "Z395"],
                  ["residual_adapter", "post", "L249", (), (1,)]]
        cone = life.provenance(events, ["L0", "L249"])
        self.assertEqual(cone["old_pair"]["event_indices"], [0, 3, 5])
        self.assertEqual(cone["expanded"]["event_indices"], list(range(6)))
        self.assertRaisesRegex(ValueError, "nonzero private free Z395", life.values, events, ["L0", "L249"])

    def test_source_and_invoice_negative_controls(self):
        self.assertRaisesRegex(ValueError, "duplicate JSON", io.unique, [("x", 1), ("x", 2)])
        blobs = io.inputs()
        self.assertEqual(checks.invoice(blobs, 91)["source_declared_physical_families"], 66813)
        self.assertRaisesRegex(ValueError, "charged private", checks.invoice, blobs, 90)
        self.assertEqual(life.warp({("x", (-7,)): Fraction(3)}, 7), {("x", ()): Fraction(3)})

    def test_complete_event_range_encoding(self):
        events = [["phase", str(i)] for i in range(10)]
        indices = [0, 1, 3, 5, 6, 7, 9]
        summary = life.summary(events, {"event_indices": indices, "boundary_inputs": []})
        self.assertEqual(summary["event_ranges_half_open"], [[0, 2], [3, 4], [5, 8], [9, 10]])
        self.assertEqual([i for a, b in summary["event_ranges_half_open"] for i in range(a, b)], indices)


if __name__ == "__main__":
    unittest.main()
