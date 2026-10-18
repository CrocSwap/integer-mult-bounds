# SPDX-License-Identifier: Apache-2.0
"""Behavioral checks of formal grids, extrema, chronology and source bindings."""

import copy
import itertools
import json
import tempfile
import unittest
from fractions import Fraction as Q
from pathlib import Path

from check_integer import check as integer_check
from rows import (
    combine,
    depth,
    endpoint_check,
    interval,
    prefixes,
    scalar,
    signed_width,
    warp,
)
from verify import PACKAGE, authenticate, decode, evaluate


class Formats(unittest.TestCase):
    def test_integer_replay_intermediate_grid(self):
        excursion = [
            ["scalar", ["add", ["L", 0], ["L", 1], sign, 16], 0] for sign in (1, -1)
        ]
        endpoint = [
            ["scalar", ["add", ["L", r], ["L", r - 112], 1, 1], 0]
            for r in range(112, 224)
        ]
        checked = integer_check(excursion + endpoint, 4)
        self.assertEqual((checked["fractional_bits"], checked["ADDs"]), (4, 114))
        with self.assertRaisesRegex(ValueError, "exact fixed-grid divisibility"):
            integer_check(excursion + endpoint, 3)

    def test_exact_signed_extrema(self):
        # Direct enumeration supplies an independent check of the endpoint formula.
        for precision in (2, 3):
            limit = 1 << (precision - 1)
            for coefficients in itertools.product(range(-2, 3), repeat=3):
                row = {(i, ()): Q(q) for i, q in enumerate(coefficients) if q}
                values = [
                    sum(a * b for a, b in zip(coefficients, values, strict=True))
                    for values in itertools.product(range(-limit, limit), repeat=3)
                ]
                low, high = interval(row, precision)
                self.assertEqual((low, high), (min(values), max(values)))
                width = signed_width(low, high)
                self.assertTrue(-(1 << (width - 1)) <= low <= high < 1 << (width - 1))
                if width > 1:
                    self.assertFalse(
                        -(1 << (width - 2)) <= low <= high < 1 << (width - 2)
                    )

    def test_negative_signed_edge(self):
        row = {(0, ()): Q(-1)}
        self.assertEqual(interval(row, 3), (-3, 4))
        self.assertEqual(signed_width(*interval(row, 3)), 4)

    def test_phase_identification_uses_symmetric_box(self):
        # A signed monomial atom need not stay in the asymmetric input box.
        row = {(0, (1,)): Q(1)}
        minimum_input = -4
        phase_value = -minimum_input
        self.assertGreater(phase_value, interval(row, 3)[1])
        self.assertLessEqual(abs(phase_value), 4 * sum(map(abs, row.values())))

    def test_cancellation_and_divisibility(self):
        source = {(0, ()): Q(1, 8)}
        row = combine({(0, ()): Q(-1, 16)}, source, Q(1, 2))
        self.assertEqual(row, {})
        self.assertEqual(depth(source), 3)
        self.assertEqual(depth({(0, ()): Q(1, 16)}), 4)
        self.assertEqual(Q(1, 16) * 2**4, 1)
        self.assertNotEqual((Q(1, 16) * 2**3).denominator, 1)

    def test_warp_order_and_inverse(self):
        original = {(0, ()): Q(3), (1, (2,)): Q(-1, 2)}
        self.assertEqual(warp(warp(original, 3), -3), original)
        self.assertNotEqual(warp(warp(original, 3), 2), warp(warp(original, 2), 3))
        self.assertEqual(depth(warp(original, 9)), 1)

    def test_zero_buffer_return(self):
        good = [["zero_buffer", "alloc", 1], ["zero_buffer", "free", 1]]
        self.assertEqual(len(list(prefixes(good, 1))), 1)
        bad = [good[0], ["scalar", ["add", ["Z", 1], ["L", 0], 1, 1], 0], good[1]]
        with self.assertRaisesRegex(ValueError, "zero return"):
            list(prefixes(bad, 1))

    def test_unknown_native_event(self):
        with self.assertRaisesRegex(ValueError, "known non-scalar"):
            list(prefixes([["silently_assumed_transform"]], 1))

    def test_all_prefixes_not_only_final(self):
        events = [
            ["scalar", ["add", ["L", 0], ["L", 1], sign, 16], 0] for sign in (1, -1)
        ]
        rows = list(prefixes(events, 2))
        self.assertEqual(depth(rows[0][2]), 4)
        self.assertEqual(depth(rows[-1][2]["L", 0]), 0)

    def test_actual_receipt_witnesses(self):
        receipt = json.loads((PACKAGE / "RESULT.json").read_text())
        for directions in receipt["providers"].values():
            for direction, record in directions.items():
                summary = record["exact"]
                self.assertEqual(summary["signed_width"], 77)
                self.assertEqual(
                    summary["fractional_bits"], 4 if direction == "forward" else 5
                )
                row = decode(summary["witnesses"]["depth"]["row"])
                self.assertEqual(depth(row), summary["fractional_bits"])
                for side in ("low", "high"):
                    witness = decode(summary["witnesses"][side]["row"])
                    self.assertEqual(
                        str(interval(witness, 64)[side == "high"]), summary[side]
                    )
                self.assertGreater(summary["ignored_events"]["climb"], 0)

    def test_semantic_endpoint_mutations(self):
        events = [
            ["scalar", ["add", ["L", r], ["L", r - 112], 1, 1], 0]
            for r in range(112, 224)
        ]
        state = list(prefixes(events))[-1][2]
        endpoint_check(state, 632, False)
        mutant = copy.deepcopy(events)
        mutant[0][1][3] = -1
        with self.assertRaisesRegex(ValueError, "literal scalar endpoint"):
            endpoint_check(list(prefixes(mutant))[-1][2], 632, False)
        warped = copy.deepcopy(state)
        warped["L", 0] = warp(warped["L", 0], 1)
        with self.assertRaisesRegex(ValueError, "literal scalar endpoint"):
            endpoint_check(warped, 632, False)

    def test_invalid_boundaries(self):
        for row in ({(0, ()): Q(1, 3)},):
            with self.assertRaisesRegex(ValueError, "dyadic row"):
                depth(row)
        with self.assertRaisesRegex(ValueError, "input precision"):
            interval({}, 129)
        with self.assertRaisesRegex(ValueError, "bounded emitted"):
            list(prefixes([["phase"]] * 30_001))
        with self.assertRaisesRegex(ValueError, "nonzero warp"):
            warp({}, 0)
        with self.assertRaisesRegex(ValueError, "distinct ADD"):
            scalar({("L", 0): {}}, ["add", ["L", 0], ["L", 0], 1, 1])
        self.assertEqual(evaluate({(0, ()): Q(2)}, {(0, ()): -3}), -6)

    def test_source_corruption(self):
        self.assertEqual(authenticate(), 19)
        with tempfile.TemporaryDirectory(prefix="grid-source-control-") as directory:
            target = Path(directory)
            (target / "vendor").mkdir()
            records = json.loads((PACKAGE / "VENDOR.json").read_text())
            for record in records["files"]:
                destination = target / record["path"]
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes((PACKAGE / record["path"]).read_bytes())
            (target / "VENDOR.json").write_text(json.dumps(records))
            (target / "vendor/bitadder.py").write_bytes(b"corrupted source\n")
            with self.assertRaisesRegex(ValueError, "frozen source bytes"):
                authenticate(target)


if __name__ == "__main__":
    unittest.main()
