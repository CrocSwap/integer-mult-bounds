#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 thakrarsagar. Developed with substantial OpenAI Codex assistance.
"""Controls at the actual high-cube setup, cost and ownership boundary."""

from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import runtime
import verify


class SetupControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loaded = runtime.load()
        cls.identity = runtime.run_case(cls.loaded, kind="identity")

    @classmethod
    def tearDownClass(cls):
        runtime.close(cls.loaded)

    def test_input_word_width_and_bank_size_have_real_cost(self):
        baseline = self.identity
        extra_role = runtime.run_case(self.loaded, kind="identity", capacity=65)
        for row in (baseline, extra_role):
            verify.check_case(row)
            self.assertEqual(row["volume"], 81)
            self.assertEqual(row["high_modulus"], 3)
            self.assertEqual(row["tolls"], [])
        self.assertEqual(extra_role["traffic"] - baseline["traffic"], 10)
        self.assertEqual(extra_role["setup_traffic"] - baseline["setup_traffic"], 10)
        # Both legal constructors give Q=V=1, but the enclosing moduli 3 and 5
        # require different physical word widths. No noncanonical padding or
        # bypass of Ring's required one-high-zero representation is used.
        narrow = runtime.run_case(self.loaded, kind="identity", q=3, width=1)
        wider = runtime.run_case(self.loaded, kind="identity", q=5, width=1)
        for row in (narrow, wider):
            verify.check_case(row)
            self.assertEqual((row["high_modulus"], row["volume"]), (1, 1))
        self.assertEqual(wider["input_digits"] - narrow["input_digits"], 1)
        self.assertEqual(wider["traffic"] - narrow["traffic"], 27)
        self.assertEqual(wider["setup_traffic"] - narrow["setup_traffic"], 27)

    def test_unit_high_modulus_skips_nontrivial_word_and_bank(self):
        # The compiler still supplies a nonempty word, but Q=1 has one high
        # address. Neither its factors nor any high-bank marker is executed.
        ordinary = runtime.run_case(self.loaded, kind="mixed", width=1)
        larger_bank = runtime.run_case(self.loaded, kind="mixed", width=1, capacity=80)
        for row in (ordinary, larger_bank):
            verify.check_case(row)
            self.assertEqual(row["high_modulus"], 1)
            self.assertTrue(row["operations"])
            self.assertEqual(row["tolls"], [])
            self.assertEqual(row["native_intervals"], [])
            self.assertEqual(row["extents"], [])
            self.assertEqual(row["intermediate_clears"], [])
            self.assertEqual(row["output_payload_peak"], 1)
        self.assertEqual(ordinary["traffic"], larger_bank["traffic"])

    def test_reversed_add_pays_both_swaps_and_retains_three_outputs(self):
        ordered = runtime.run_case(self.loaded, kind="ordered")
        reversed_add = runtime.run_case(self.loaded, kind="reversed")
        for row in (ordered, reversed_add):
            verify.check_case(row)
        # A 2x2 route has one ADD per row. These adjacent fields also exercise
        # zero exponents in before/middle/after extent construction.
        self.assertEqual(ordered["operations"], [["add", 1, 0, 1], ["add", 3, 2, 1]])
        self.assertEqual(reversed_add["operations"], [["add", 0, 1, 1], ["add", 2, 3, 1]])
        self.assertEqual(ordered["output_payload_peak"], 2)
        self.assertEqual(reversed_add["output_payload_peak"], 3)
        self.assertEqual(len(ordered["native_intervals"]), 0)
        self.assertEqual(len(reversed_add["native_intervals"]), 4)
        self.assertEqual([t["kind"] for t in reversed_add["tolls"]],
                         ["swap", "added", "swap", "swap", "added", "swap"])
        self.assertEqual(len(ordered["intermediate_clears"]), 2)
        self.assertEqual(len(reversed_add["intermediate_clears"]), 6)

    def test_endpoint_preserving_extra_setup_read_fails_invoice(self):
        high = sys.modules["high_route"]
        original = high.execute

        def extra_read(source, *args, **kwargs):
            result = original(source, *args, **kwargs)
            source.read()
            return result

        with patch.object(high, "execute", extra_read):
            changed = runtime.run_case(self.loaded, kind="identity")
        # run_case has already checked the unchanged independent endpoint,
        # borrowed bytes/heads and ownership; only the physical bill changed.
        self.assertEqual(changed["traffic"], self.identity["traffic"] + 1)
        self.assertEqual(changed["setup_traffic"], self.identity["setup_traffic"] + 1)
        with self.assertRaisesRegex(ValueError, "exact encoded setup invoice"):
            verify.check_case(changed)

    def test_omitted_high_bank_erasure_fails_return_boundary(self):
        state = runtime.prepare(self.loaded, kind="identity")
        bank = state.adapter.high_bank
        arena = type(bank)
        original = arena.erase_owned

        def omit_target(current):
            if current is not bank:
                return original(current)
            return None

        try:
            with patch.object(arena, "erase_owned", omit_target):
                with self.assertRaisesRegex(ValueError, "complete high-bank teardown"):
                    runtime.execute(state)
        finally:
            if bank.initialized:
                original(bank)
            runtime.cleanup(state)

    def test_missing_first_swap_fails_independent_affine_endpoint(self):
        state = runtime.prepare(self.loaded, kind="reversed")
        # A single high address separates the first two fields. The generic
        # periodic fixture can be invariant under this particular transposition.
        state.initial = bytes(int(i == 27) for i in range(state.bits))
        state.source.cells[1:state.bits + 1] = state.initial
        original = state.adapter.swap
        calls = 0

        def first_swap_is_copy(source, *args, **kwargs):
            nonlocal calls
            calls += 1
            if calls != 1:
                return original(source, *args, **kwargs)
            # Return a genuine fresh owned output, with correct extent and
            # restored heads, but omit this permutation's mathematical action.
            output = state.scope.acquire()
            source.rewind()
            state.runtime.routes.copy_rows(source, output, state.context.highs, state.fibre)
            source.rewind()
            output.rewind()
            return output

        try:
            with patch.object(state.adapter, "swap", first_swap_is_copy):
                with self.assertRaisesRegex(ValueError, "affine endpoint"):
                    runtime.execute(state)
            self.assertEqual(calls, 4)
        finally:
            runtime.cleanup(state)

    def test_source_byte_mutation_rejected_before_loading(self):
        target = runtime.ROOT / "research/selected-bit-fast-primitives/high_route.py"
        original = Path.read_bytes
        touched = []

        def changed(path):
            raw = original(path)
            if path == target:
                touched.append(path)
                return raw + b"\n# changed source bytes\n"
            return raw

        with patch.object(Path, "read_bytes", changed):
            with self.assertRaisesRegex(ValueError, "source hash: .*high_route.py"):
                runtime.authenticate()
        self.assertEqual(touched, [target])


if __name__ == "__main__":
    unittest.main()
