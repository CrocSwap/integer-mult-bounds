# SPDX-License-Identifier: Apache-2.0
"""Behavioral checks for scalar circuits, guards and rejection controls."""

import unittest

import caller
import check_bits
from replay import lower


def circuit(width, kind, a, b):
    recipe = lower.certify(kind, a, b, policy="target_walk")
    return caller.circuit(width, kind, a, b, recipe)


class CallerTests(unittest.TestCase):
    def test_signed_add_and_read_only_source(self):
        for a, b in ((7, 8), (-7, 4), (-3, 2), (1, 4)):
            self.assertEqual(
                caller.execute(12, "add", a, b, 17, -24, circuit(12, "add", a, b)),
                17 + a * (-24) // b,
            )

    def test_modular_signed_digit_intermediate(self):
        # 3/2 = 2 - 1/2. The intermediate may exceed the signed range.
        self.assertEqual(
            caller.execute(5, "add", 3, 2, -5, 12, circuit(5, "add", 3, 2)), 13
        )

    def test_half_double_all_small_signed_values(self):
        for width in range(2, 8):
            limit = 1 << (width - 1)
            for x in range(-limit, limit):
                if x % 2 == 0:
                    gates = caller.shift(width, 0, True)
                    self.assertEqual(
                        check_bits.array(gates, width, x, 0), (x // 2) % (1 << width)
                    )
                if -limit <= 2 * x < limit:
                    gates = caller.shift(width, 0, False)
                    self.assertEqual(
                        check_bits.array(gates, width, x, 0), (2 * x) % (1 << width)
                    )

    def test_negation_all_small_bit_patterns(self):
        for width in range(2, 8):
            for x in range(1 << width):
                self.assertEqual(
                    check_bits.array(caller.negate(width, 0), width, x, 0),
                    (-x) % (1 << width),
                )

    def test_scale_signed_fixtures(self):
        for a, b in ((-2, 1), (-1, 1), (-1, 2), (1, 2), (2, 1)):
            self.assertEqual(
                caller.execute(84, "scale", a, b, -80, 0, circuit(84, "scale", a, b)),
                -80 * a // b,
            )

    def test_alignment_rejection(self):
        with self.assertRaisesRegex(ValueError, "common-grid"):
            caller.execute(8, "add", 1, 2, 0, 3, circuit(8, "add", 1, 2))

    def test_signed_endpoint_overflow(self):
        with self.assertRaisesRegex(ValueError, "signed endpoint"):
            caller.execute(5, "add", 1, 1, 15, 1, circuit(5, "add", 1, 1))

    def test_negation_prefix_overflow(self):
        with self.assertRaisesRegex(ValueError, "negation prefix"):
            caller.execute(5, "scale", -1, 2, -16, 0, circuit(5, "scale", -1, 2))

    def test_dirty_stock_rejection(self):
        gates = circuit(8, "add", 1, 1)
        for args in ({"carry": 1}, {"scratch": 1}):
            with self.assertRaisesRegex(ValueError, "initially-zero"):
                caller.execute(8, "add", 1, 1, 2, 3, gates, **args)

    def test_omitted_sign_fill(self):
        gates = caller.shift(8, 0, True)[:-1]
        with self.assertRaisesRegex(ValueError, "endpoint"):
            caller.execute(8, "scale", 1, 2, -8, 0, gates)

    def test_missing_carry_cleanup(self):
        gates = circuit(8, "add", 1, 1)
        # Delete the bottom carry erasure, retaining the final target XOR.
        gates = gates[:-2] + gates[-1:]
        with self.assertRaisesRegex(ValueError, "clean return"):
            caller.execute(8, "add", 1, 1, 1, 1, gates)

    def test_control_requires_inverse_scratch_preparation(self):
        recipe = lower.certify("add", 1, 8, policy="target_walk")
        gates = caller.control(12, recipe)
        self.assertEqual(caller.execute(12, "add", 1, 8, 0, 24, gates), 3)
        with self.assertRaisesRegex(ValueError, "clean return|endpoint"):
            caller.execute(12, "add", 1, 8, 0, 24, gates[:-12])

    def test_wrong_sign_and_missing_negation(self):
        with self.assertRaisesRegex(ValueError, "endpoint"):
            caller.execute(8, "add", -1, 1, 2, 3, circuit(8, "add", 1, 1))
        with self.assertRaisesRegex(ValueError, "endpoint"):
            caller.execute(8, "scale", -1, 1, 2, 0, [])

    def test_ports_and_capacity(self):
        with self.assertRaisesRegex(ValueError, "read-only"):
            caller.validate([("cx", (0, 0), (1, 0))], 8)
        with self.assertRaisesRegex(ValueError, "distinct"):
            caller.validate([("cx", (0, 0), (0, 0))], 8)
        with self.assertRaisesRegex(ValueError, "bounded width"):
            circuit(257, "add", 1, 1)


if __name__ == "__main__":
    unittest.main()
