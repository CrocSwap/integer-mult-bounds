# SPDX-License-Identifier: Apache-2.0
"""Behavioral rejection and inverse checks for the reached native boundary."""

import itertools
import json
import unittest

import verify as V

C = V.circuits


class ClimbTests(unittest.TestCase):
    def test_mixed_parity_wide_execution(self):
        for width in (5, 69, 133):
            for values in ((1, 3, -1, -3), (0, -2, 4, 6), (-3, 2, 1, -4)):
                for sign in (-1, 1):
                    for control in (False, True):
                        expected = V.expected_pair(values, sign)
                        self.assertEqual(
                            C.run(values, C.lift(sign, control), width), list(expected)
                        )

    def test_integral_endpoint_does_not_supply_lift_alignment(self):
        self.assertEqual(V.expected_pair((1, 1, 0, 0), 1), (0, 1, 1, 0))
        with self.assertRaisesRegex(ValueError, "half-source alignment"):
            C.run([1, 1, 0, 0], C.lift(), 5)

    def test_dirty_carries_rejected(self):
        gates, _ = C.primitive(5, ("add", 0, 1, 1, 1))
        with self.assertRaisesRegex(ValueError, "owned clean carry"):
            C.apply_words(gates, [0, 0, 1], 5)

    def test_signed_negation_and_difference_guards(self):
        with self.assertRaisesRegex(ValueError, "signed microstate"):
            C.run([-16], [("neg", 0)], 5)
        with self.assertRaisesRegex(ValueError, "signed microstate"):
            C.run([14, 0, -14, 0], C.lift(), 5)

    def test_invalid_owned_fields_and_coefficients(self):
        for instruction in (
            ("add", 0, 0, 1, 1),
            ("swap", 0, 0),
            ("add", 0, 1, 2, 1),
            ("neg", -1),
            ("unknown", 0),
        ):
            with self.assertRaises(ValueError):
                C.run([0, 0, 0, 0], [instruction], 5)

    def test_capacity_exhaustion(self):
        for width in (True, 2, 257):
            with self.assertRaisesRegex(ValueError, "bounded width"):
                C.run([0], [], width)
        with self.assertRaisesRegex(ValueError, "bounded macro"):
            C.run([0], [("neg", 0)] * (C.MAX_MACROS + 1), 5)
        with self.assertRaisesRegex(ValueError, "bounded field"):
            C.run([0] * (C.MAX_FIELDS + 1), [], 5)

    def test_wrong_sign_and_omitted_carry_gate_detected(self):
        cases = [
            v
            for v in itertools.product(range(-4, 4), repeat=4)
            if (v[0] - v[2]) % 2 == (v[1] - v[3]) % 2 == 0
        ]
        original = V.truth_columns(cases, 5)
        expected = V.truth_columns([V.expected_pair(v, 1) for v in cases], 5)
        self.assertNotEqual(C.packed(C.pair_gates(5, -1), original, 5), expected)
        gates = C.pair_gates(5)
        # The low borrow is identically zero on matched-parity inputs. Mutate
        # the next carry, which is live on this domain.
        cut = next(i for i, g in enumerate(gates) if g[0] == "ccx" and g[-1] == 21)
        self.assertTrue(
            C.packed(gates[:cut] + gates[cut + 1 :], original, 5) != expected
        )

    def test_packed_capacity_and_ports(self):
        with self.assertRaisesRegex(ValueError, "bounded packed truth"):
            C.packed([], [1 << C.MAX_TRUTH_COLUMNS] + [0] * 23, 5)
        with self.assertRaisesRegex(ValueError, "owned distinct packed"):
            C.packed([("cx", 0, 0)], [0] * 24, 5)

    def test_native_tail_omission_detected(self):
        retained = json.loads((V.binding.PRIOR / "RESULT.json").read_text())
        columns = retained["providers"]["base"]["columns"]
        program, operators = V.binding.dispatch(V.predecessor, columns)
        before, expected = V.binding.fixture(V.raw_fixtures(3)["dense"], operators)
        self.assertEqual(C.run(before, program, 8, bits=False), expected)
        self.assertNotEqual(C.run(before, program[:-1], 8, bits=False), expected)


if __name__ == "__main__":
    unittest.main()
