#!/usr/bin/env python3
"""Focused mathematical and rejection tests; no repository-wide regeneration."""
import copy
import importlib.util
import unittest
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("compensation_verifier", HERE / "verify.py")
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)


class CompensationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        V.sources()
        cls.word = V.read(V.ROOT / V.NATIVE / "CANONICAL-WORD.json.gz")
        cls.recipe = V.read(HERE / "RECIPE.json")
        cls.changed = V.construct(cls.word, cls.recipe)

    def test_all_signed_dyadic_pair_coefficients(self):
        # A synthetic non-unit example checks the general formula even though
        # all 56 nominated coefficients happen to equal +1.
        word = copy.deepcopy(self.word)
        word["compensation"] = [V.add(112, 224, Q(3, 4)), V.add(112, 225, Q(-1, 2)),
                                V.add(113, 224, Q(-1, 4)), V.add(113, 225, Q(2))]
        # Explicitly set these two synthetic helper boundaries to unwrapped.
        for helper in (224, 225):
            word["start"][helper], word["final"][helper] = 0, 1
        for q in (Q(s) * Q(2) ** k for s in (-1, 1) for k in range(-2, 3)):
            ops = [V.add(112, 113, -q), V.add(112, 224, Q(3, 4) + q / 4),
                   V.add(112, 225, Q(-1, 2) - 2 * q), V.add(113, 224, Q(-1, 4)),
                   V.add(113, 225, Q(2)), V.add(112, 113, q)]
            ops = [e for e in ops if e[3]]
            V.check_boundary(word, ops)

    def test_literal_coefficient_primitives(self):
        coefficients = {Q(e[3], e[4]) for e in self.word["compensation"] + self.changed["compensation"]}
        coefficients.update(Q(s * a, 2 ** b) for s in (-1, 1) for a in (1, 3, 5, 17) for b in range(5))
        for q in coefficients:
            # Three symbolic input coordinates: target, source and private work.
            target, source, work = [Q(1), Q(0), Q(0)], [Q(0), Q(1), Q(0)], [Q(0), Q(0), Q(1)]
            operations = 1
            work = [Q(0)] * 3  # charged initial clear
            for index, bit in enumerate(bin(abs(q.numerator))[2:]):
                if index:
                    work = [2 * x for x in work]
                    operations += 1
                if bit == "1":
                    work = [x + y for x, y in zip(work, source)]
                    operations += 1
            denominator = q.denominator
            while denominator > 1:
                work = [x / 2 for x in work]
                operations += 1
                denominator //= 2
            sign = 1 if q > 0 else -1
            target = [x + sign * y for x, y in zip(target, work)]
            operations += 1
            work = [Q(0)] * 3
            operations += 1
            self.assertEqual(target, [1, q, 0])
            self.assertEqual(source, [0, 1, 0])
            self.assertEqual(work, [0, 0, 0])
            self.assertEqual(2 * operations, V.coefficient_cost(q))

    def test_complete_boundary_and_meaningful_controls(self):
        V.check_boundary(self.word, self.changed["compensation"])
        self.assertEqual(len(V.controls(self.word, self.changed, self.recipe)), 10)

    def test_integer_engine_fractional_cleanup_and_dual(self):
        gates = [["scale", ["L", 2], -1, 4],
                 ["add", ["L", 1], ["L", 2], 3, 2],
                 ["add", ["L", 1], ["L", 0], 1, 1],
                 ["add", ["L", 1], ["L", 2], -3, 2],
                 ["scale", ["L", 2], -4, 1]]
        for back in (False, True):
            reflected = copy.deepcopy(gates)
            if back:
                for e in reflected:
                    if e[0] == "add":
                        e[1], e[2], e[3] = e[2], e[1], -e[3]
                    else:
                        e[2], e[3] = e[3], e[2]
            events = [["scalar", e, 0] for e in reflected]
            V.replay_integer_matrix(events, 3, 1, back)
            with self.assertRaisesRegex(ValueError, "full scalar operator"):
                V.replay_integer_matrix(events[:-1], 3, 1, back)

    def test_untouched_non_scalar_events_and_replacement_boundaries(self):
        original = V.read(V.ROOT / V.NATIVE / "LOCAL-PROGRAMS.json.gz")
        changed = V.replace_programs(self.word, self.changed, original)
        for name in original:
            self.assertEqual([e for e in original[name] if e[0] != "scalar"],
                             [e for e in changed[name] if e[0] != "scalar"])
        bad = copy.deepcopy(original)
        bad["forward"][1 + len(self.word["precondition"])][1][3] *= -1
        with self.assertRaisesRegex(ValueError, "correspondence"):
            V.replace_programs(self.word, self.changed, bad)

    def test_changed_input_and_certificate_pins(self):
        expected = V.read(HERE / "EXPECTED.json")
        self.assertEqual(V.digest(self.changed), expected["canonical_sha256"])
        bad = copy.deepcopy(self.changed)
        bad["compensation"][0][3] *= -1
        self.assertNotEqual(V.digest(bad), expected["canonical_sha256"])
        with self.assertRaisesRegex(ValueError, "complete boundary operator"):
            V.check_boundary(self.word, bad["compensation"])


if __name__ == "__main__":
    unittest.main()
