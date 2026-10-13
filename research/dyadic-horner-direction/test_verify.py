"""Focused mathematical and verifier failure-mode tests; Apache-2.0.

Gareth Davidson (@bitplane), substantial OpenAI Codex assistance.
"""

import importlib.util
import unittest
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


v, lower, independent = load("verify"), load("lower"), load("crosscheck")


class DirectionTests(unittest.TestCase):
    def test_elementary_fraction(self):
        # 1 -> 1/2 -> 3/2, then accumulate and clear: five primitives.
        op = ["add", ["T", 0], ["S", 0], 3, 2]
        name, word = lower.choose(op)
        self.assertEqual(name, "binary-reverse")
        self.assertEqual(len(word), 5)
        self.assertEqual(v.coefficient_check(Q(3, 2), word, 5), "5/2")
        self.assertEqual(independent.execute(word, 3, 2), "5/2")

    def test_negative_initial_naf_and_sign(self):
        for sign in (-1, 1):
            op = ["add", ["T", 0], ["S", 0], sign*11, 8]
            word = lower.candidates(op)["naf-reverse"]
            self.assertEqual(word[-2][0], "subtract" if sign > 0 else "add")
            self.assertEqual(v.coefficient_check(Q(sign*11, 8), word, len(word)),
                             independent.execute(word, sign*11, 8))

    def test_reducible_fraction_and_even_integer(self):
        for numerator, denominator in [(6, 4), (24, 1), (-8, 32), (-2, 2)]:
            costs, _, _ = independent.check(lower, numerator, denominator)
            self.assertTrue(costs)
        a = lower.lower(["add", ["T", 0], ["S", 0], 6, 4])
        b = lower.lower(["add", ["T", 0], ["S", 0], 3, 2])
        self.assertEqual(a, b)

    def test_dirty_work_is_an_independent_input(self):
        op = ["add", ["T", 0], ["S", 0], 3, 2]
        word = lower.lower(op)[1:]
        with self.assertRaisesRegex(ValueError, "endpoint"):
            independent.execute(word, 3, 2)
        with self.assertRaisesRegex(ValueError, "endpoint"):
            v.coefficient_check(Q(3, 2), word, 100)

    def test_contract_controls_survive_optimization(self):
        names = v.negative_controls(lower)
        self.assertEqual(len(names), 14)
        self.assertIn("endpoint_neutral_prefix_growth", names)
        self.assertIn("reverse_naf_initial_sign", names)

    def test_endpoint_neutral_prefix_growth(self):
        op = ["add", ["T", 0], ["S", 0], 3, 4]
        word = lower.lower(op)
        peak = Q(v.coefficient_check(Q(3, 4), word, len(word)))
        mutated = word[:1] + [("double", v.WORK), ("halve", v.WORK)] + word[1:]
        # Endpoint and scratch checks alone accept this exact neutral pair.
        self.assertGreater(Q(v.coefficient_check(Q(3, 4), mutated, len(mutated))), peak)
        with self.assertRaisesRegex(ValueError, "prefix"):
            v.coefficient_check(Q(3, 4), mutated, len(mutated), peak)

    def test_coefficient_cost_control_is_independent_of_map(self):
        op = ["add", ["T", 0], ["S", 0], 3, 2]
        word = lower.lower(op)
        self.assertEqual(independent.execute(word, 3, 2), "5/2")
        with self.assertRaisesRegex(ValueError, "cost"):
            v.coefficient_check(Q(3, 2), word, len(word)-1)

    def test_unit_coefficients_preserve_arbitrary_private_input_contract(self):
        for sign in (-1, 1):
            word = lower.lower(["add", ["T", 0], ["S", 0], sign, 1])
            self.assertEqual(len(word), 2)
            self.assertEqual(independent.execute(word, sign, 1), "2")
            with self.assertRaisesRegex(ValueError, "work"):
                independent.execute(word[:-1], sign, 1)


if __name__ == "__main__":
    unittest.main()
