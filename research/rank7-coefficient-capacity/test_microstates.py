# SPDX-License-Identifier: Apache-2.0
"""Behavioral controls for arithmetic, capacity and register lifecycle."""

import unittest
from fractions import Fraction as Q

import integer
import microstates as m
from vendor.lowering import lower
from vendor.native import format as native

X, Y, Z = ((i, ()) for i in range(3))


def trace(recipe):
    rows = ((Q(1), Q(0)), (Q(0), Q(1)), (Q(0), Q(0)))
    result = []
    for instruction in recipe:
        rows = lower.execute([instruction], rows)
        result.append((instruction[1], rows[instruction[1]]))
    return result


def run_recipe(recipe, before, source, expected, rank=0):
    ledger = native.Ledger(True, correlated=True)
    m.evaluate(recipe, trace(recipe), before, source, expected, rank, ledger, 1)
    return ledger.result(64)


class Microstates(unittest.TestCase):
    def test_literal_dyadic_macros(self):
        before, source = {X: Q(3), Y: Q(-2)}, {X: Q(-1), Z: Q(1, 2)}
        for q in (Q(7, 8), Q(3, 8), Q(3, 2), Q(-7, 4), Q(1, 2), Q(-1), Q(0)):
            for policy in m.POLICIES:
                with self.subTest(q=q, policy=policy):
                    recipe = lower.lower(
                        "add", q.numerator, q.denominator, policy=policy
                    )
                    expected = {
                        a: v for a, v in {X: 3 - q, Y: Q(-2), Z: q / 2}.items() if v
                    }
                    report = run_recipe(recipe, before, source, expected, rank=3)
                    self.assertTrue(native.capacity(report, 64, 7, 84))

    def test_scale_endpoint(self):
        recipe = lower.lower("scale", -1, 8)
        report = run_recipe(recipe, {X: Q(16)}, {}, {X: Q(-2)})
        self.assertEqual(report["fractional_bits"], 0)
        self.assertEqual(report["symmetric_amplitude_in_input_L"], "16")

    def test_correlation_cancels(self):
        recipe = [("add", 0, 1, 1)]
        report = run_recipe(recipe, {X: Q(1), Y: Q(1)}, {X: Q(-1)}, {Y: Q(1)})
        self.assertEqual(report["symmetric_amplitude_in_input_L"], "1")

    def test_restored_source_can_hide_fractional_overflow(self):
        report = run_recipe(
            [("half", 1), ("double", 1)], {Y: Q(1)}, {X: Q(1, 128)}, {Y: Q(1)}
        )
        self.assertEqual(report["fractional_bits"], 8)
        with self.assertRaisesRegex(ValueError, "sufficient common grid"):
            native.capacity(report, 64, 7, 84)

    def test_restored_source_can_hide_signed_overflow(self):
        report = run_recipe(
            [("double", 1), ("half", 1)], {Y: Q(1)}, {X: Q(4096)}, {Y: Q(1)}
        )
        self.assertEqual(report["symmetric_amplitude_in_input_L"], "8192")
        with self.assertRaisesRegex(ValueError, "strict symmetric signed capacity"):
            native.capacity(report, 64, 7, 84)

    def test_missing_source_restore_rejects(self):
        recipe = lower.lower("add", 7, 8, policy="source_walk")
        with self.assertRaisesRegex(ValueError, "restoration"):
            run_recipe(recipe[:-1], {Y: Q(1)}, {X: Q(8)}, {Y: Q(1), X: Q(7)})

    def test_missing_scratch_clear_rejects(self):
        recipe = lower.lower("add", 7, 8, policy="scratch")
        with self.assertRaisesRegex(ValueError, "scratch cleanup"):
            run_recipe(recipe[:-1], {Y: Q(1)}, {X: Q(8)}, {Y: Q(1), X: Q(7)})

    def test_wrong_sign_rejects(self):
        with self.assertRaisesRegex(ValueError, "literal macro"):
            run_recipe([("add", 0, 1, -1)], {Y: Q(1)}, {X: Q(1)}, {Y: Q(1), X: Q(1)})

    def test_wrong_port_rejects(self):
        with self.assertRaisesRegex(ValueError, "literal macro"):
            run_recipe([("add", 1, 0, 1)], {Y: Q(1)}, {X: Q(1)}, {Y: Q(1), X: Q(1)})

    def test_integer_remainder_rejects(self):
        with self.assertRaisesRegex(ValueError, "exact half remainder"):
            integer.step([{X: 1}, {}, {}], ("half", 0))

    def test_integer_wrong_prefix_rejects(self):
        with self.assertRaisesRegex(ValueError, "every-microstate equality"):
            integer.check_rows([("double", 0)], {X: Q(1)}, {}, {X: Q(2)}, [{X: Q(3)}])

    def test_dirty_copy_rejects(self):
        with self.assertRaisesRegex(ValueError, "zero scratch"):
            integer.step([{X: 1}, {Y: 1}, {Z: 1}], ("copy", 2, 1))


if __name__ == "__main__":
    unittest.main()
