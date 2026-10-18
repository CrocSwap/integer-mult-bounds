#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 thakrarsagar. Developed with substantial OpenAI Codex assistance.
"""Focused source, phase, inverse-domain, and representation controls."""

import copy
from fractions import Fraction
from functools import reduce
import json
from operator import xor
from pathlib import Path
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import independent
import verify


class Gaussian:
    """Exact rational complex arithmetic for independent numerical controls."""
    def __init__(self, real=0, imag=0):
        self.real, self.imag = Fraction(real), Fraction(imag)

    @classmethod
    def cast(cls, value):
        return value if isinstance(value, cls) else cls(value)

    def __add__(self, other):
        other = self.cast(other)
        return Gaussian(self.real + other.real, self.imag + other.imag)

    __radd__ = __add__

    def __neg__(self):
        return Gaussian(-self.real, -self.imag)

    def __sub__(self, other):
        return self + -self.cast(other)

    def __rsub__(self, other):
        return self.cast(other) + -self

    def __mul__(self, other):
        other = self.cast(other)
        return Gaussian(self.real * other.real - self.imag * other.imag,
                        self.real * other.imag + self.imag * other.real)

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = self.cast(other)
        norm = other.real ** 2 + other.imag ** 2
        return Gaussian((self.real * other.real + self.imag * other.imag) / norm,
                        (self.imag * other.real - self.real * other.imag) / norm)

    def __eq__(self, other):
        other = self.cast(other)
        return (self.real, self.imag) == (other.real, other.imag)

    def __repr__(self):
        return f"Gaussian({self.real}, {self.imag})"


def evaluate(rows, phases, ambient):
    """Direct finite polynomial evaluation, independent of inverse arithmetic."""
    result = [[0 for _ in range(8)] for _ in range(8)]
    for row, column, mask, exponent, coefficient in rows:
        value = coefficient * (ambient if exponent == -1 else 1)
        for index, phase in enumerate(phases):
            if mask >> index & 1:
                value *= phase
        result[row][column] += value
    return result


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source, cls.context, cls.blocks = verify.load_context()
        cls.receipt = verify.certify(cls.context, cls.blocks)
        cls.rows = cls.receipt["polynomial_matrix"]

    def test_independent_source_and_exact_inverse(self):
        observed = independent.build()
        for key, value in self.receipt.items():
            self.assertEqual(observed[key], value, key)
        self.assertEqual(set(observed["independent_inverse"]["recovered_sites"]), set(range(20)))
        self.assertEqual(observed["independent_inverse"]["checked_divisions"], 21)
        faulty = copy.deepcopy(self.rows)
        next(row for row in faulty if row[:2] == [0, 2])[4] *= -1
        with self.assertRaises(ValueError):
            independent.inverse_certificate(faulty)

    def test_quadratic_character_term_cannot_be_dropped(self):
        # Coordinate characters alone cannot distinguish this mutant.
        correct = verify.phase_axis(11)
        linear_only = correct[0], correct[1], 0
        for character in [0] + [1 << bit for bit in range(verify.BITS)]:
            self.assertEqual(verify.phase_value(correct, character),
                             verify.phase_value(linear_only, character))
        self.assertNotEqual(verify.phase_value(correct, 3), verify.phase_value(linear_only, 3))
        for character in range(16):
            self.assertEqual(verify.phase_value(correct, character), (11 & character).bit_count() % 2)
            self.assertEqual(independent.phase_value(independent.parity(11), character),
                             verify.phase_value(correct, character))
        cancellation = verify.phase_add(verify.phase_axis(3), verify.phase_scale(
            verify.phase_add(verify.phase_axis(1), verify.phase_axis(2)), -1))
        self.assertEqual([verify.phase_value(cancellation, x) for x in range(4)], [0, 0, 0, 2])

    def test_omitted_hosted_action_and_bridge_rejected(self):
        context = copy.deepcopy(self.context)
        time = min(context["hosts"])
        self.assertTrue(context["hosts"][time])
        context["hosts"][time].pop(0)
        with self.assertRaises(ValueError):
            verify.certify(context, self.blocks)
        blocks = copy.deepcopy(self.blocks)
        stage = next(stage for stage, events in blocks.items()
                     if any(event["kind"] == "bridge" for event in events))
        index = next(index for index, event in enumerate(blocks[stage]) if event["kind"] == "bridge")
        blocks[stage].pop(index)
        with self.assertRaises(ValueError):
            verify.certify(self.context, blocks)

    def test_multiple_nontrivial_phase_specializations(self):
        identity = [[int(row == column) for column in range(8)] for row in range(8)]
        ambient = Gaussian(0, -1)
        self.assertEqual(evaluate(self.rows, [1] * 20, ambient), identity)
        units = (Gaussian(1), Gaussian(0, 1), Gaussian(-1), Gaussian(0, -1))
        for salt in range(1, 5):
            phases = [units[(index * index + salt * index + salt) % 4] for index in range(20)]
            matrix = evaluate(self.rows, phases, ambient)
            self.assertNotEqual(matrix, identity)
            self.assertEqual(verify.inverse(matrix, ambient), phases)
        # The inverse is also exact away from fourth roots of unity.
        phases = [Fraction((-1) ** index * (index + 2), index + 1) for index in range(20)]
        ambient = Fraction(-3, 5)
        self.assertEqual(verify.inverse(evaluate(self.rows, phases, ambient), ambient), phases)
        for site in range(20):
            phases = [Fraction(1)] * 20
            phases[site] = 0
            with self.assertRaises((ValueError, ZeroDivisionError)):
                verify.inverse(evaluate(self.rows, phases, Fraction(1)), Fraction(1))
        with self.assertRaises((ValueError, ZeroDivisionError)):
            verify.inverse(evaluate(self.rows, [Fraction(1)] * 20, Fraction(0)), Fraction(0))

    def test_complete_polynomial_matches_frozen_numeric_source(self):
        # These augmented lists test the scalar phase interface; independence
        # and a realizable rank-saving replacement are deliberately not assumed.
        residual = {child: list(axes) + [1 << child]
                    for child, axes in self.context["residual"].items()}
        units = (Gaussian(1), Gaussian(0, 1), Gaussian(-1), Gaussian(0, -1))
        mixed = sum(1 << bit for bit in range(73) if bit % 3 == 1)
        for character in (0, 3, 11, (1 << 73) - 1, mixed):
            phases = [units[(character >> child) & 1] for child in range(20)]
            ambient = units[-((character & 11).bit_count() % 2) % 4]
            baseline = units[character.bit_count() % 4]
            symbolic = evaluate(self.rows, phases, ambient)
            numeric = self.source.replay(self.context, residual, character, self.blocks)
            observed = [[Gaussian(*value) for value in row] for row in numeric]
            expected = [[baseline * value for value in row] for row in symbolic]
            self.assertEqual(observed, expected, f"character={character}")
            if character:
                self.assertNotEqual(observed, [[baseline * int(i == j) for j in range(8)]
                                              for i in range(8)])

    def test_symbolic_division_checks_its_domain(self):
        one = verify.Laurent.constant(1)
        x, y = verify.Laurent.variable(0), verify.Laurent.variable(1)
        self.assertEqual((x * y) / x, y)
        self.assertEqual((one / x) * x, one)
        for denominator in (verify.Laurent.constant(0), x + y):
            with self.assertRaisesRegex(ValueError, "nonzero monomial"):
                one / denominator
        with self.assertRaisesRegex(ValueError, "nonzero monomial"):
            independent.quotient({independent.EXP_ZERO: Fraction(1)}, {})

    def test_same_phase_distinct_basis_is_permitted_but_rank_change_is_not(self):
        context = copy.deepcopy(self.context)
        before = context["residual"][8]
        self.assertEqual(len(before), 48)
        # I+11^T in dimension six is orthogonal and preserves weight mod four.
        # Replace six actual source axes by their five-axis complements.
        combined = reduce(xor, before[:6])
        after = [combined ^ axis for axis in before[:6]] + before[6:]
        self.assertNotEqual(after, before)
        self.assertEqual(len(set(after)), len(before))
        self.assertTrue(all((a & b).bit_count() % 2 == int(i == j)
                            for i, a in enumerate(after) for j, b in enumerate(after)))
        self.assertEqual(independent.phase_sum(independent.parity(axis) for axis in before),
                         independent.phase_sum(independent.parity(axis) for axis in after))
        context["residual"][8] = after
        self.assertEqual(verify.certify(context, self.blocks), self.receipt)
        # Drop an independent axis, then check actual ambient operator phases,
        # bypassing certify's simpler pinned-rank guard.
        context["residual"][8] = after[:-1]
        changed, _ = verify.symbolic_replay(context, self.blocks)
        with self.assertRaisesRegex(ValueError, "ambient phase"):
            verify.normalized_rows(changed)

    def test_source_bytes_are_authenticated(self):
        pins = json.loads((verify.HERE / "SOURCES.json").read_bytes())["files"]
        pin = next(row for row in pins if row["usage"] == "input")
        with tempfile.TemporaryDirectory(prefix="phase-map-control-") as directory:
            path = Path(directory) / pin["path"]
            path.parent.mkdir(parents=True)
            path.write_bytes((verify.ROOT / pin["path"]).read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "source hash"):
                verify.authenticate(root=Path(directory))


if __name__ == "__main__":
    unittest.main()
