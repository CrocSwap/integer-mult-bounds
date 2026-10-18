"""Exactness witnesses and adverse grid/primitive controls; Apache-2.0.

Gareth Davidson (@bitplane), substantial OpenAI Codex assistance.
"""

import importlib.util
import unittest
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("grid_verifier", HERE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
lower = v.load(HERE / "vendor/pr837/lower.py", "lower")
grid = v.load(HERE / "fixed_grid.py", "grid")


class GridTests(unittest.TestCase):
    def test_coefficient_grid_counterexample(self):
        op = ["add", ["T", 0], ["S", 0], 31, 8]
        old, new = lower.choose(op, reverse=False)[1], lower.lower(op)
        self.assertEqual(v.coefficient_trace(Q(31, 8), old)[0], 3)
        self.assertEqual(v.coefficient_trace(Q(31, 8), new)[0], 5)
        self.assertEqual(grid.local(old, 3), ("31/8", 0))
        self.assertEqual(grid.local(new, 3)[0], "4")
        self.assertEqual(grid.local(new, 5), ("31/8", 0))

    def test_negative_rounding_direction(self):
        values = {("W", 0): -1}
        self.assertTrue(grid.step(("halve", ("W", 0)), values, integer=True))
        self.assertEqual(values["W", 0], -1)  # Floor, not truncation to zero.

    def test_zero_does_not_acquire_fractional_depth(self):
        state = {("W", 0): ({}, 0)}
        for _ in range(100):
            self.assertEqual(v.rows.primitive(("halve", ("W", 0)), state), 0)

    def test_cancellation_removes_denominator(self):
        self.assertEqual(v.rows.plus(({0: 3}, 7), ({0: -3}, 7)), ({}, 0))
        self.assertEqual(v.rows.plus(({0: 1}, 3), ({0: 3}, 3)), ({0: 1}, 1))

    def test_negative_and_unreduced_multiplier_denominators(self):
        row = ({0: 1}, 0)
        self.assertEqual(v.rows.multiply(row, -3, -6), ({0: 1}, 1))
        self.assertEqual(v.rows.multiply(row, 3, -6), ({0: -1}, 1))
        with self.assertRaisesRegex(ValueError, "non-dyadic"):
            v.rows.multiply(row, 1, 3)

    def test_copy_then_halve_does_not_change_source(self):
        state = {("S", 0): ({0: 1}, 0), ("T", 0): ({1: 1}, 0)}
        v.rows.primitive(("copy", ("T", 0), ("S", 0)), state)
        v.rows.primitive(("halve", ("T", 0)), state)
        self.assertEqual(state["S", 0], ({0: 1}, 0))
        self.assertEqual(state["T", 0], ({0: 1}, 1))

    def test_dirty_work_and_wrong_halving_are_detected(self):
        word = lower.lower(["add", ["T", 0], ["S", 0], 31, 8])
        for bad in [word[1:], word[:1]+word[2:], word[:-1]]:
            with self.assertRaises(ValueError):
                v.coefficient_trace(Q(31, 8), bad)

    def test_every_recorded_global_witness_rejects_one_less_bit(self):
        receipt = v.read(HERE / "EXPECTED.json")
        for result in receipt["programs"].values():
            for mode in ("forward_best", "bidirectional"):
                row = result[mode]
                proof = row["sharpness_witness"]
                g = row["scalar_projection_guard_bits"]
                value = Q(proof["odd_numerator"], 2**proof["denominator_exponent"])
                self.assertEqual((value * 2**g).denominator, 1)
                self.assertEqual((value * 2**(g-1)).denominator, 2)

    def test_wrong_global_witness_location_is_rejected(self):
        result = v.read(HERE / "EXPECTED.json")["programs"]["ck/forward"]["bidirectional"]
        proof = dict(result["sharpness_witness"])
        proof["step"] += 1
        import json
        provider, _, parts = next(v.inputs())
        self.assertEqual(provider, "ck")
        word = json.loads(parts["CANONICAL-WORD.json.gz"])
        events = json.loads(parts["LOCAL-PROGRAMS.json.gz"])["forward"]
        with self.assertRaisesRegex(ValueError, "witness address"):
            grid.check_witness(events, word, lower, True, proof)


if __name__ == "__main__":
    unittest.main()
