"""Small arithmetic, forest-optimality, and defect-sensitivity checks for the separate replay.

Run: python3 -I -B research/u8-two-sided-biforest-seed35/test_independent.py
Prepared by Stephan Arrington (@steph4n-gh) with substantial Google DeepMind
Antigravity assistance. Apache-2.0.
"""

import unittest
from pathlib import Path
import sys

# Permit the documented isolated-mode invocation without ambient PYTHONPATH.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from independent import ReplayError, _verify_forest_optimality, check_endpoint, replay


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

    def test_depth_two_helper_forest_requires_leaf_before_parent_order(self):
        # 1 target L[1], 3 helpers L[2], L[3], L[4] with chain 4 -> 3 -> 2 (all +1).
        # Target row is [1, 1, 1] on (h2, h3, h4), so after leaf-before-parent
        # h3 += h4; h2 += h3, h2 holds h2 + h3 + h4 and a single add L[1] += L[2]
        # realizes L[1] += h2 + h3 + h4.
        good = [
            ["clear", ["W", 0]],
            ["add", ["L", 3], ["L", 4], 1],   # leaf 4 -> parent 3 first
            ["add", ["L", 2], ["L", 3], 1],   # then 3 -> root 2
            ["add", ["L", 1], ["L", 2], 1],   # residual on root 2 only
            ["add", ["L", 2], ["L", 3], -1],  # restore parent-before-leaf
            ["add", ["L", 3], ["L", 4], -1],
        ]
        res_good = replay(good, n=5, centers=0)
        self.assertEqual(res_good["endpoint"]["L"][1],
                         {"denominator_power": 0, "terms": [[1, 1], [2, 1], [3, 1], [4, 1]]})
        for h in (2, 3, 4):
            self.assertEqual(res_good["endpoint"]["L"][h],
                             {"denominator_power": 0, "terms": [[h, 1]]})
        # Reversing helper preparation omits leaf 4 from L[1]:
        bad_prep = [good[0], good[2], good[1], good[3], good[4], good[5]]
        res_bad = replay(bad_prep, n=5, centers=0)
        self.assertNotEqual(res_bad["endpoint"]["L"][1], res_good["endpoint"]["L"][1])

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

    def test_forest_verifier_rejects_wrong_depth_order_and_suboptimal_tree(self):
        vectors = [[4, 4, 4], [4, 4, 4], [4, 4, 4]]
        price_fn = lambda x: 0 if x == 0 else 4
        # Valid chain 2 -> 1 (depth 2), 1 -> 0 (depth 1): cost 12 + 8 + 8 = 28
        _, cost, edges = _verify_forest_optimality(
            vectors, [[2, 1, 1, 2], [1, 0, 1, 1]], price_fn, "chain"
        )
        self.assertEqual((cost, edges), (28, 9))
        # Wrong depth order (parent before leaf) must be rejected:
        with self.assertRaisesRegex(ReplayError, "leaf-before-parent depth order"):
            _verify_forest_optimality(
                vectors, [[1, 0, 1, 1], [2, 1, 1, 2]], price_fn, "bad_order"
            )
        # Suboptimal forest (only 1 edge, cost 12 + 12 + 8 = 32 > 28) must be rejected:
        with self.assertRaisesRegex(ReplayError, "differs from Prim minimum"):
            _verify_forest_optimality(
                vectors, [[1, 0, 1, 1]], price_fn, "suboptimal"
            )

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
