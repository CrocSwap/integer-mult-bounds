#!/usr/bin/env python3
"""Fault controls for the source-bound capacity and physical-cost claims."""

import copy
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import invoice
import runtime
import verify


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rt = runtime.load()

    def test_exact_scratch_capacity_and_one_short(self):
        for suffix in (1, 3):
            for pooled in (False, True):
                with self.subTest(suffix=suffix, pooled=pooled):
                    verify.run_case(self.rt, 5, 1, 1, suffix, -2,
                                    occupied=2, pooled=pooled)
                    with self.assertRaisesRegex(ValueError, "fixed scratch role inventory exhausted"):
                        verify.run_case(self.rt, 5, 1, 1, suffix, -2,
                                        occupied=2, pooled=pooled, spare=9 + (suffix > 1))
        f = runtime.prepare(self.rt, 5, 1, 1, 3, 2, 11, 2, True)
        try:
            original = runtime.encoded(f.source)
            for coefficient in (-4, 1, 2):
                trace = runtime.Traffic(self.rt)
                with trace.installed(), f.pool.install():
                    output = self.rt.kernels.added(f.source, f.ring, *f.extents, coefficient)
                runtime.endpoint(f, output, 5, 1, 1, 3, coefficient)
                self.assertEqual(trace.total - trace.arithmetic, invoice.shell(5, 1, 1, 3))
                output.clear()
                self.assertEqual(set(f.pool.live.values()), set(f.held))
                self.assertEqual(runtime.encoded(f.source), original)
        finally:
            runtime.dispose(f)

    def test_six_numerical_slots_are_needed_by_one_fixture(self):
        row = verify.run_case(self.rt, 3, 1, 1, 1, -4)
        self.assertEqual(row["numerical_extra"], 6)
        with self.assertRaisesRegex(ValueError, "fixed register inventory"):
            verify.run_case(self.rt, 3, 1, 1, 1, -4, numerical_capacity=7)
        guarded = verify.run_case(self.rt, 3, 1, 1, 1, -4,
                                  numerical_capacity=10, numerical_occupied=2)
        self.assertEqual(guarded["numerical_extra"], 6)

    def test_wrong_coefficient_rejects_at_endpoint(self):
        original = self.rt.kernels.fixed_coefficient
        def opposite(ring, value):
            return original(ring, -value)
        with patch.object(self.rt.kernels, "fixed_coefficient", opposite):
            with self.assertRaisesRegex(ValueError, "complete modular ADD endpoint"):
                verify.run_case(self.rt, 5, 1, 1, 2, 2)

    def test_endpoint_preserving_cost_mutation(self):
        original = self.rt.stream.copy_blocks
        def extra_read(source, *args, **kwargs):
            result = original(source, *args, **kwargs)
            source.read()
            return result
        with patch.object(self.rt.stream, "copy_blocks", extra_read):
            with self.assertRaisesRegex(ValueError, "exact non-arithmetic invoice"):
                verify.run_case(self.rt, 5, 2, 1, 2, 2)

    def test_noncanonical_borrow_preserves_endpoint_but_changes_cost(self):
        original = verify.prepare
        def padded(*args, **kwargs):
            fixture = original(*args, **kwargs)
            count = fixture.extents[0]
            count.msb()
            count.step(1)
            count.tape.write(0)
            count.step(1)
            count.tape.write(3)
            count.rewind()
            return fixture
        with patch.object(verify, "prepare", padded):
            with self.assertRaisesRegex(ValueError, "exact non-arithmetic invoice"):
                verify.run_case(self.rt, 5, 2, 1, 2, 2)

    def test_empty_split_is_not_the_positive_formula(self):
        for before, middle in ((1, 1), (2, 3)):
            row = verify.run_case(self.rt, 3, before, middle, 1, 1)
            wrong = invoice.shell(3, before, middle, 1, zero_correction=False)
            self.assertEqual(row["shell"] - wrong, 8 * before * middle)

    def test_source_corruption_rejected_before_loading(self):
        rows = json.loads((runtime.PACKAGE / "SOURCES.json").read_bytes())["files"]
        for wanted in ("kernels.py", "pr2899.tar", "scratch_pool.py"):
            changed = copy.deepcopy(rows)
            row = next(r for r in changed if r["path"].endswith(wanted))
            row["sha256"] = "0" * 64
            with self.subTest(wanted=wanted):
                with self.assertRaisesRegex(ValueError, "source hash"):
                    runtime.authenticate(changed)

    def test_typed_receipt_does_not_accept_boolean_alias(self):
        original = {"cases": [1], "scratch": 10}
        with self.assertRaisesRegex(ValueError, "complete typed receipt"):
            verify.check_receipt(original, {"cases": [True], "scratch": 10})

    def test_pooled_counter_zero_and_padding(self):
        self.assertEqual(verify.counter_controls(self.rt), 51)

    def test_integer_width_absorption_and_invoice_domain(self):
        for q in range(3, 4096, 2):
            b = q.bit_length() + 1
            self.assertLessEqual(b * b, 4 * q)
            self.assertLessEqual(invoice.shell(q, 1, 1, 1), 640 * q * q)
        with self.assertRaisesRegex(ValueError, "odd high modulus"):
            invoice.shell(4, 1, 1, 1)
        with self.assertRaisesRegex(ValueError, "positive canonical extents"):
            invoice.shell(3, 0, 1, 1)


if __name__ == "__main__":
    unittest.main()
