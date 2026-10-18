# SPDX-License-Identifier: Apache-2.0
"""Behavioral failure controls for the complete one-carry scalar boundary."""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from fractions import Fraction as Q

import bindings
import checks
import scalars as s
import verify

BITS, CALLER, REPLAY, LOWER = bindings.load()
BUILD = verify.factory(BITS, LOWER)


class ScalarTests(unittest.TestCase):
    def test_dirty_negation_and_inverse(self):
        gates = BUILD(8, "scale", -1, 1)
        for source in (-128, -7, 0, 127):
            for target in (-128, -1, 0, 127):
                self.assertEqual(s.execute(8, gates, source, target), -target % 256)
        self.assertEqual(s.counts(gates), {"cx": 114, "ccx": 42})

    def test_shift_tariffs_and_edge_cases(self):
        for width in (4, 23, 84, 256):
            for exponent in range(-3, 9):
                gates = s.shifted(width, exponent)
                n = width - max(0, exponent)
                expected = (
                    {"cx": 0, "ccx": 0}
                    if n <= 0
                    else {"cx": 1, "ccx": 0}
                    if n == 1
                    else {"cx": 4 * n - 2 + 2 * max(0, -exponent), "ccx": 2 * n - 2}
                )
                self.assertEqual(s.counts(gates), expected)
                source = -(1 << max(0, -exponent))
                observed = s.execute(width, gates, source, 0)
                self.assertEqual(
                    observed, int(Q(source) * Q(2) ** exponent) % (1 << width)
                )

    def test_missing_sign_fill_rejects(self):
        gates = BUILD(8, "add", 1, 8)
        with self.assertRaises(ValueError):
            checks.check_batch(8, gates[1:], [(-8, 0, -1)])

    def test_missing_sign_cleanup_rejects(self):
        gates = BUILD(8, "add", 1, 8)
        with self.assertRaises(ValueError):
            checks.check_batch(8, gates[:-1], [(-8, 0, -1)])

    def test_missing_carry_cleanup_and_wrong_sign_reject(self):
        gates = BUILD(4, "add", 1, 1)
        cases = [(a, b, a + b) for a in range(-8, 8) for b in range(-8, 8)]
        with self.assertRaises(ValueError):
            checks.check_batch(4, gates[:-2], cases)
        with self.assertRaises(ValueError):
            checks.check_batch(4, gates, [(2, 3, 1)])

    def test_negation_swap_is_necessary(self):
        gates = BUILD(8, "scale", -1, 1)
        with self.assertRaises(ValueError):
            checks.check_batch(8, gates[:-24], [(37, -9, 9)])

    def test_clean_carry_entrance(self):
        with self.assertRaises(ValueError):
            s.execute(8, BUILD(8, "add", 1, 1), 2, 3, carry=1)

    def test_original_alignment_and_signed_endpoint_guards(self):
        for args in (
            (8, "add", 1, 2, 0, -7),
            (8, "add", 1, 1, 127, 1),
            (8, "scale", -1, 1, -128, 37),
        ):
            with self.assertRaises(ValueError):
                CALLER.guards(*args)
        self.assertEqual(s.execute(8, BUILD(8, "add", 1, 1), 1, 127), 128)

    def test_actual_internal_source_write_and_return(self):
        gates = BUILD(8, "add", 1, 1)
        self.assertTrue(any(8 <= gate[-1] < 16 for gate in gates))
        self.assertEqual(s.execute(8, gates, -19, 5), 242)
        self.assertEqual(BUILD(8, "scale", 1, 1), [])

    def test_changed_source_rejects_before_import(self):
        with tempfile.TemporaryDirectory(prefix="one-carry-hash-") as directory:
            root = Path(directory)
            (root / "input.py").write_text("changed source")
            (root / "SOURCES.json").write_text(
                json.dumps(
                    {
                        "files": [
                            {
                                "path": "input.py",
                                "usage": "input",
                                "sha256": hashlib.sha256(
                                    b"original source"
                                ).hexdigest(),
                            }
                        ]
                    }
                )
            )
            with (
                patch.object(bindings, "PACKAGE", root),
                patch.object(bindings, "ROOT", root),
            ):
                with self.assertRaisesRegex(ValueError, "source hash"):
                    bindings.load()

    def test_stronger_alignment_and_wrong_scale_recipe_reject(self):
        with self.assertRaisesRegex(ValueError, "denominator alignment"):
            s.circuit(8, "add", 1, 1, [], [(1, -1), (1, -1)])
        with self.assertRaisesRegex(ValueError, "guarded SCALE recipe"):
            s.circuit(8, "scale", 2, 1, [], [])
        with self.assertRaisesRegex(ValueError, "guarded SCALE recipe"):
            s.circuit(8, "scale", 1, 1, [("half", 0), ("double", 0)], [])

    def test_boundary_validation(self):
        for width in (3, 257):
            with self.assertRaises(ValueError):
                s.shifted(width, 0)
        with self.assertRaises(ValueError):
            s.shifted(4, -4)
        for gates in ([(0, 0)], [(0, 17)], [(0, 1, 2, 3)]):
            with self.assertRaises(ValueError):
                s.validate(8, gates)
        with self.assertRaises(ValueError):
            s.adder((0, 1), (1, 2), 3)
        with self.assertRaises(ValueError):
            s.circuit(8, "add", 3, 2, [], [(1, 0)])


if __name__ == "__main__":
    unittest.main()
