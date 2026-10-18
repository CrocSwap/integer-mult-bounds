"""Small arithmetic and defect-sensitivity checks for the separate replay.

Run: python3 -m unittest discover -s research/complex-ck-two-sided -p test_independent.py
Prepared for Ross with substantial OpenAI Codex assistance. Apache-2.0.
"""

import unittest
from pathlib import Path
import sys

# Permit the documented isolated-mode invocation without ambient PYTHONPATH.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from independent import ReplayError, check_endpoint, replay


class IndependentReplayTests(unittest.TestCase):
    def test_exact_signed_dyadic_and_positive_envelope(self):
        result = replay([
            ["copy", ["W", 0], ["L", 0]],
            ["halve", ["W", 0]],
            ["add", ["L", 1], ["W", 0], -1],
            ["double", ["W", 0]],
            ["add", ["L", 1], ["W", 0], 1],
            ["negate", ["L", 0]],
            ["clear", ["W", 0]],
        ], n=2, centers=0)
        self.assertEqual(result["endpoint"]["L"], [
            {"denominator_power": 0, "terms": [[0, -1]]},
            {"denominator_power": 1, "terms": [[0, 1], [1, 2]]},
        ])
        self.assertEqual(result["primitive_count"], 7)
        self.assertEqual(result["positive_prefix"]["numerator"], 5)
        self.assertEqual(result["positive_prefix"]["denominator_power"], 1)
        self.assertEqual(result["maximum_denominator_power"], 1)
        transient = replay([["halve", ["L", 0]], ["double", ["L", 0]]], n=1, centers=0)
        self.assertEqual(transient["maximum_denominator_power"], 1)
        self.assertEqual(transient["endpoint"]["L"][0]["denominator_power"], 0)

    def test_all_private_registers_enter_dirty(self):
        result = replay([], n=2, centers=1)
        self.assertEqual(result["input_columns"], 4)
        self.assertEqual(result["endpoint"]["C"][0]["terms"], [[2, 1]])
        self.assertEqual(result["endpoint"]["W"][0]["terms"], [[3, 1]])
        with self.assertRaises(ReplayError):
            check_endpoint(result, "forward", v=1)

    def test_both_endpoints_and_helper_restoration(self):
        for orientation in ("forward", "backward"):
            target, source, sign = ((1, 0, 1) if orientation == "forward" else (0, 1, -1))
            program = [
                ["clear", ["C", 0]],
                ["clear", ["W", 0]],
                ["add", ["L", 2], ["L", 0], 1],
                ["add", ["L", 2], ["L", 0], -1],
                ["add", ["L", target], ["L", source], sign],
            ]
            self.assertTrue(check_endpoint(replay(program, n=3, centers=1), orientation, v=1))
            with self.assertRaises(ReplayError):
                check_endpoint(replay(program[:3] + program[4:], n=3, centers=1), orientation, v=1)

    def test_missing_scratch_clear_exposes_entering_dirt(self):
        program = [
            ["add", ["W", 0], ["L", 0], 1],
            ["add", ["L", 1], ["W", 0], 1],
            ["clear", ["W", 0]],
        ]
        with self.assertRaises(ReplayError):
            check_endpoint(replay(program, n=2, centers=0), "forward", v=1)
        self.assertTrue(check_endpoint(
            replay([["clear", ["W", 0]]] + program, n=2, centers=0), "forward", v=1))

    def test_copy_does_not_alias_later_mutations(self):
        result = replay([
            ["copy", ["W", 0], ["L", 0]],
            ["add", ["L", 0], ["L", 1], 1],
            ["halve", ["W", 0]],
        ], n=2, centers=0)
        self.assertEqual(result["endpoint"]["W"][0],
                         {"denominator_power": 1, "terms": [[0, 1]]})

    def test_malformed_instructions_fail_closed(self):
        examples = [
            ["add", ["L", 0], ["L", 1], 2],
            ["add", ["L", 0], ["L", 1], True],
            ["add", ["L", 0], ["L", 0], 1],
            ["clear", ["L", 2]],
            ["clear", ["W", 1]],
            ["clear", ["L", True]],
            ["scale", ["L", 0], 1, 2],
            ["negate", ["L", 0], "unexpected"],
            ["phase", "anything"],
        ]
        for instruction in examples:
            with self.subTest(instruction=instruction), self.assertRaises(ReplayError):
                replay([instruction], n=2, centers=0)


if __name__ == "__main__":
    unittest.main()
