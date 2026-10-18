#!/usr/bin/env python3
"""Behavioral controls for the actual route wrapper and its cost observer."""

import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import invoice
import runtime
import verify


class AuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime = runtime.load()
        cls.native = runtime.native_fixture(cls.runtime, 3)
        cls.single = runtime.run_case(cls.runtime, 1)

    def test_literal_complete_invoice(self):
        row = self.single
        self.assertEqual(row["traffic"], 438000)
        self.assertEqual(row["cube_traffic"], 431027)
        self.assertEqual(row["wrapper_traffic"], 6973)
        self.assertEqual(row["native_traffic"], 154884)
        self.assertEqual(row["native_calls"], 6)
        self.assertEqual(row["disposed_traffic"], 438412)
        verify.check_wrapper(row)

    def test_alias_meters_are_not_physical_objects(self):
        pool = self.runtime.scratch_pool.ScratchPool(1)
        lease = pool.acquire()
        trace = runtime.Trace(self.runtime, self.native)
        meter = lease.physical.meter
        before = meter.reads + meter.writes + meter.moves
        with trace.installed():
            start = trace.snapshot()
            lease.append(self.runtime.words.ONE)
            lease.rewind()
            self.assertEqual(lease.read(), self.runtime.words.ONE)
            lease.clear()
            actual = trace.snapshot() - start
        physical = meter.reads + meter.writes + meter.moves - before
        alias = lease.meter.reads + lease.meter.writes + lease.meter.moves
        self.assertEqual(actual, 21)
        self.assertEqual(physical, 21)
        self.assertEqual(physical + alias, 42)
        pool.empty()

    def test_counter_oracle(self):
        count = self.runtime.cardinal_counts.Count
        pool = self.runtime.scratch_pool.ScratchPool(4)
        trace = runtime.Trace(self.runtime, self.native)
        for value in range(1, 257):
            source = count.literal(value)
            with trace.installed(), pool.install():
                start = trace.snapshot()
                counter = self.runtime.stream.Counter(source)
                for _ in range(value):
                    self.assertFalse(counter.finished)
                    counter.decrement()
                self.assertTrue(counter.finished)
                counter.close()
                actual = trace.snapshot() - start
                self.assertEqual(actual, invoice.countdown(value) + 1)
                pool.empty()
            source.close()

    def test_copy_rows_oracle(self):
        count, tape = self.runtime.cardinal_counts.Count, self.runtime.records.Tape
        pool = self.runtime.scratch_pool.ScratchPool(8)
        trace = runtime.Trace(self.runtime, self.native)
        values = (1, 2, 3, 4, 5, 8, 9, 13, 16, 17, 33)
        for highs in values:
            for fibre in values:
                rows, suffix = count.literal(highs), count.literal(fibre)
                source, output = tape(), tape()
                expected = bytes(i % 2 for i in range(highs * fibre))
                for bit in expected:
                    source.append(bit)
                source.rewind()
                with trace.installed(), pool.install():
                    start = trace.snapshot()
                    self.runtime.routes.copy_rows(source, output, rows, suffix)
                    actual = trace.snapshot() - start
                    self.assertEqual(actual, invoice.copy_rows(highs, fibre))
                    self.assertEqual(bytes(output.cells[1:]), expected)
                    pool.empty()
                for item in (source, output):
                    item.clear()
                rows.close()
                suffix.close()

    def test_sharp_wrapper_constants(self):
        self.assertEqual(invoice.wrapper(1, 1, 1), 265)
        self.assertEqual(invoice.wrapper(1, 1, 1, True), 277)
        for prefixes in range(1, 33):
            for highs in range(1, 33):
                for fibre in range(1, 33):
                    volume = prefixes * highs * fibre
                    self.assertLessEqual(
                        invoice.wrapper(prefixes, highs, fibre), 265 * volume
                    )
                    self.assertLessEqual(
                        invoice.wrapper(prefixes, highs, fibre, True), 277 * volume
                    )
        actual = runtime.run_case(self.runtime, 1, width=1)
        self.assertEqual(actual["wrapper_traffic"], 265)
        self.assertEqual(actual["disposed_traffic"] - actual["cube_traffic"], 277)

    def test_endpoint_preserving_quadratic_cost_mutant(self):
        ordinary = runtime.run_case(self.runtime, 3)
        mutant = runtime.run_case(self.runtime, 3, prefix_probe=True)
        # Both complete calls passed the affine endpoint and ownership oracle.
        self.assertEqual(mutant["traffic"] - ordinary["traffic"], 9)
        self.assertEqual(mutant["cube_traffic"], ordinary["cube_traffic"])
        self.assertEqual(mutant["native_traffic"], ordinary["native_traffic"])
        with self.assertRaisesRegex(ValueError, "exact wrapper invoice"):
            verify.check_wrapper(mutant)
        with self.assertRaisesRegex(ValueError, "complete typed receipt"):
            verify.check_receipt(mutant, ordinary)

    def test_complemented_payload_and_prefix_lift(self):
        complemented = runtime.run_case(self.runtime, 3, pattern=1)
        verify.check_lift(self.single, complemented)
        self.assertEqual(complemented["traffic"], 1313895)
        self.assertEqual(complemented["disposed_traffic"], 1315117)
        self.assertEqual(complemented["native_calls"], 18)

    def test_padded_prefix_changes_the_invoice(self):
        state = runtime.prepare(self.runtime, 1, 3, 2, 1, False, 0)
        try:
            # Same value, one extra high zero before RIGHT. This is deliberately
            # outside the canonical-input premise, not a selected-source bug.
            state.old_count.tape.cells.insert(-1, self.runtime.words.ZERO)
            traffic, _disposal, _calls, cubes = runtime.execute(state)
            self.assertEqual(traffic, self.single["traffic"] + 14)
            self.assertEqual(sum(cubes), self.single["cube_traffic"])
            self.assertNotEqual(traffic - sum(cubes), invoice.wrapper(1, 81, 1))
        finally:
            runtime.cleanup(state)

    def test_endpoint_fault(self):
        state = runtime.prepare(self.runtime, 1, 3, 1, 1, False, 0)
        output = state.pool.acquire()
        try:
            output.append(state.initial[0] ^ 1)
            output.rewind()
            with self.assertRaisesRegex(ValueError, "affine endpoint"):
                runtime.endpoint(state, output)
        finally:
            output.clear()
            state.pool.empty()
            runtime.cleanup(state)

    def test_cost_omission_and_type_corruptions(self):
        for key, change in (
            ("traffic", -1),
            ("wrapper_traffic", -1),
            ("native_traffic", -self.single["native_traffic"]),
        ):
            altered = copy.deepcopy(self.single)
            altered[key] += change
            with self.assertRaisesRegex(ValueError, "complete typed receipt"):
                verify.check_receipt(altered, self.single)
        altered = copy.deepcopy(self.single)
        altered["prefixes"] = True
        with self.assertRaisesRegex(ValueError, "complete typed receipt"):
            verify.check_receipt(altered, self.single)

    def test_invalid_domains(self):
        for value in (0, -1, True, 1.0):
            with self.assertRaisesRegex(ValueError, "positive integer cardinality"):
                invoice.wrapper(value, 1, 1)
        for prefixes in (0, 18, True):
            with self.assertRaisesRegex(ValueError, "fixture prefix range"):
                runtime.prepare(self.runtime, prefixes, 3, 1, 1, False, 0)
        for fibre in (0, 4, True):
            with self.assertRaisesRegex(ValueError, "fixture fibre"):
                runtime.prepare(self.runtime, 1, 3, 1, fibre, False, 0)

    def test_source_corruption_and_missing_declaration(self):
        original = Path.read_bytes
        target = runtime.PREDECESSOR / "high_route.py"

        def corrupted(path):
            body = original(path)
            return body + b"\n# corruption\n" if path == target else body

        with (
            patch.object(Path, "read_bytes", corrupted),
            self.assertRaisesRegex(ValueError, "source hash: .*high_route.py"),
        ):
            runtime.authenticate()
        with self.assertRaisesRegex(ValueError, "declared executable source"):
            runtime.load_module("kernels", {})

    def test_cold_namespace(self):
        with self.assertRaisesRegex(ValueError, "cold audit namespace"):
            runtime.load()


if __name__ == "__main__":
    unittest.main()
