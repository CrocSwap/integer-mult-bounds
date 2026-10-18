#!/usr/bin/env python3
"""Behavioral controls for the original-input F0 collision. Apache-2.0."""
import copy
import importlib.util
import itertools
import json
import unittest
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch

PATH = Path(__file__).with_name("verify.py")
SPEC = importlib.util.spec_from_file_location("f0_collision", PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Cannot load collision verifier")
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)


class CollisionControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module, cls.data = V.load()

    def test_rational_oracle_against_integer_rounding(self):
        for bits, exponent, number in itertools.product(
                range(2, 8), range(-3, 4), range(-33, 34)):
            value = Fraction(number) * Fraction(2) ** (-exponent)
            expected = Fraction(self.module.nearest_integer(number, bits))
            expected *= Fraction(2) ** (-exponent)
            self.assertEqual(V.round_fraction(value, bits), expected)
        for bits in (1, 114):
            with self.assertRaisesRegex(ValueError, "Precision"):
                V.round_fraction(Fraction(1), bits)

    def test_all_single_coordinate_sign_changes_merge(self):
        baseline, report = V.prefix(self.module, self.data, (-1,) * V.DIM)
        for coordinate in range(V.DIM):
            signs = [-1] * V.DIM
            signs[coordinate] = 1
            state, faults = V.prefix(self.module, self.data, signs)
            self.assertEqual(state, baseline)
            self.assertEqual(faults, report)
        for wrong in ([1] * 511, [0] * 512):
            with self.assertRaisesRegex(ValueError, "signs"):
                V.initial(self.module, wrong, 53)

    def test_prefix_semantic_mutants_are_rejected(self):
        for field, value in ((1, ["L", 118]), (2, ["L", 112]), (4, 4)):
            events = self.data[0].copy()
            events[2] = copy.deepcopy(events[2])
            events[2][1][field] = value
            data = (events, *self.data[1:])
            with self.assertRaises(ValueError):
                V.check_cut(self.module, data)

    def test_exact_add_does_not_fake_the_collision(self):
        def exact_add(_engine, left, right):
            return self.module.N.plus(left, right)
        with (patch.object(self.module.Dyadic, "add", exact_add),
              self.assertRaisesRegex(ValueError, "coalescence")):
            V.check_cut(self.module, self.data)

    def test_all_live_source_corruptions_fail_before_execution(self):
        pins = json.loads((V.HERE / "SOURCES.json").read_text())
        original = Path.read_bytes
        for row in pins["files"]:
            if row["usage"] != "input":
                continue
            target = V.ROOT / row["path"]
            def corrupt(path, target=target):
                raw = original(path)
                return raw[:-1] + bytes([raw[-1] ^ 1]) if path == target else raw
            with (patch.object(Path, "read_bytes", corrupt),
                  self.assertRaisesRegex(ValueError, "Scientific source hash")):
                V.load()

    def test_endpoint_comparison_includes_helpers_and_trace(self):
        zero = [self.module.N.ZERO] * V.FIELDS
        bad = zero.copy()
        bad[224] = self.module.N.ONE
        for second in ((bad, "same"), (zero, "changed")):
            with (patch.object(V, "load", return_value=(self.module, self.data)),
                  patch.object(V, "finish", side_effect=[(zero, "same"), second]),
                  self.assertRaisesRegex(ValueError, "suffix disagrees")):
                V.audit()
        with (patch.object(V, "load", return_value=(self.module, self.data)),
              patch.object(V, "finish", return_value=(zero, "same")),
              self.assertRaisesRegex(ValueError, "Explicit common endpoint")):
            V.audit()


if __name__ == "__main__":
    unittest.main(verbosity=2)
