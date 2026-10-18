"""Independent column arithmetic and failure controls for the finite lowering.

Prepared for @ellipsi2 with substantial OpenAI Codex assistance. Apache-2.0.
"""
from copy import deepcopy
from fractions import Fraction
import importlib.util
import itertools
import json
from pathlib import Path
import unittest

PACKAGE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("fanout_verify", PACKAGE / "verify.py")
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


def column_execution(registers, primitives, column):
    """Flat vector engine; does not call the verifier's row interpreter."""
    values = [Fraction(i == column) for i in range(len(registers))]
    positions = {r: i for i, r in enumerate(registers)}
    for op in primitives:
        target = positions[tuple(op[1])]
        if op[0] == "clear":
            values[target] = Fraction(0)
        elif op[0] == "scale":
            values[target] *= Fraction(op[2], op[3])
        elif op[0] == "add":
            values[target] += Fraction(op[3], op[4]) * values[positions[tuple(op[2])]]
        else:
            raise ValueError("unexpected primitive")
    return values


class FanoutVerification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources, _ = check.load_sources()
        cls.word = cls.sources[check.PROVIDER + "CANONICAL-WORD.json.gz"]
        cls.programs = cls.sources[check.PROVIDER + "LOCAL-PROGRAMS.json.gz"]

    def test_every_certified_block_by_independent_columns(self):
        evidence = json.loads((PACKAGE / "EXPECTED.json").read_text(encoding="utf-8"))
        groups = evidence["programs"]["forward"]["groups"]
        self.assertEqual(len(groups), 999)
        for group in groups:
            start, count = group["cleanup_start"], group["length"]
            ops = [check.canonical_scalar(e, False) for e in self.word["cleanup"][start:start + count]]
            registers = sorted({check.WORK} | {tuple(e[1]) for e in ops} | {tuple(e[2]) for e in ops})
            primitives = check.fanout(ops)
            # Closed-form column oracle: only the common source contributes
            # off-diagonal entries; an arbitrary incoming W is discarded.
            for column, origin in enumerate(registers):
                expected = [Fraction(r == origin) for r in registers]
                expected[registers.index(check.WORK)] = Fraction(0)
                for op in ops:
                    if tuple(op[2]) == origin:
                        expected[registers.index(tuple(op[1]))] += Fraction(op[3], op[4])
                with self.subTest(start=start, column=column):
                    self.assertEqual(column_execution(registers, primitives, column), expected)

    def test_same_order_dual_is_inverse_transpose(self):
        # Noncommuting witness: reversing the two dual gates is incorrect.
        a, b, c = ("L", 0), ("L", 1), ("L", 2)
        regs = [a, b, c]
        forward = [["add", a, b, 2, 1], ["add", b, c, 3, 1]]
        backward = [["add", b, a, -2, 1], ["add", c, b, -3, 1]]
        fcols = [column_execution(regs, forward, j) for j in range(3)]
        bcols = [column_execution(regs, backward, j) for j in range(3)]
        for i in range(3):
            for j in range(3):
                self.assertEqual(sum(fcols[i][k] * bcols[j][k] for k in range(3)), int(i == j))
        self.assertNotEqual(bcols, [column_execution(regs, list(reversed(backward)), j) for j in range(3)])

    def test_all_groups_and_costs_by_separate_scan(self):
        evidence = json.loads((PACKAGE / "EXPECTED.json").read_text(encoding="utf-8"))
        key = lambda e: (e[2], abs(Fraction(e[3], e[4]))) if e[0] == "add" else None
        result = []
        start = 0
        for identity, iterator in itertools.groupby(self.word["cleanup"], key):
            block = list(iterator)
            m = len(block)
            if identity is not None and identity[1] != 1 and m > 1:
                source, magnitude = identity
                a, b = magnitude.numerator, magnitude.denominator
                h = a.bit_length() - 1 + a.bit_count() + b.bit_length() - 1
                result.append({"cleanup_start": start, "length": m, "source": source,
                               "abs_coefficient": str(magnitude),
                               "reference_primitives_per_component": m * (h + 3),
                               "shared_primitives_per_component": h + m + 2})
            start += m
        self.assertEqual(result, evidence["programs"]["forward"]["groups"])
        self.assertEqual(sum(2 * (x["reference_primitives_per_component"] -
                                 x["shared_primitives_per_component"]) for x in result), 19688)

    def test_actual_emitted_frame_mutation(self):
        events = deepcopy(self.programs["forward"])
        start = next(i for i, event in enumerate(events) if event == ["phase", "full_frame_cleanup"])
        events[start + 1][2] = 0
        with self.assertRaisesRegex(ValueError, "wrong cleanup frame"):
            check.check_program(events, self.word, False)

    def test_ended_helper_cannot_enter_full_cleanup(self):
        word = deepcopy(self.word)
        first = word["cleanup"][0][1]
        word["final"][first] = 0
        with self.assertRaisesRegex(ValueError, "non-FULL cleanup register"):
            check.check_program(self.programs["forward"], word, False)

    def test_paid_child_omission(self):
        events = deepcopy(self.programs["backward"])
        index = next(i for i, event in enumerate(events) if event[0] == "climb")
        del events[index]
        with self.assertRaisesRegex(ValueError, "paid profile changed"):
            check.check_program(events, self.word, True)

    def test_all_arithmetic_controls(self):
        self.assertEqual(len(check.controls()), 10)


if __name__ == "__main__":
    unittest.main()
