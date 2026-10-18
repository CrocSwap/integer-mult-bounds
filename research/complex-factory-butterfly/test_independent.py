#!/usr/bin/env python3
"""Focused checks of independent-checker failure detection.

Prepared for Ross Richardson with substantial OpenAI Codex assistance.
Apache-2.0. Retained matrix evidence credits Alluri PR681 / Jeremy Kothe PR622.
"""
import copy
from fractions import Fraction
import json
import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent

def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

independent = load('independent')
factor = load('factor')


class IndependentFactoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference = json.loads(independent.REFERENCE.read_text())

    def test_retained_word_matches_explicit_target_in_every_orientation(self):
        receipt = independent.check(self.reference, self.reference)
        self.assertEqual(set(receipt), {'forward', 'inverse', 'inverse_transpose', 'transpose'})
        for result in receipt.values():
            self.assertEqual(result['pr681']['scalar_macros'], 34)
            self.assertEqual(result['pr681']['real_primitives'],
                             {'historical_horner': 128, 'pr696': 81})
            self.assertEqual(result['original']['real_primitives'],
                             {'historical_horner': 310, 'pr696': 169})

    def test_mutated_certificate_controls_fail_for_intended_reasons(self):
        controls = independent.negative_controls(self.reference, self.reference)
        for name in ('wrong_sign', 'missing_gate', 'wrong_coefficient'):
            self.assertEqual(controls[name], 'forward: candidate map differs')
        for name in ('missing_private_clear_historical_horner', 'missing_private_clear_pr696'):
            self.assertEqual(controls[name], 'private work not cleared')
        self.assertEqual(controls['changed_entry_frame'], 'changed entry_frames')
        self.assertEqual(controls['wrong_gate_frame'], 'changed gate frame')

    def test_nonunit_dyadic_lowering_overwrites_arbitrary_private_input(self):
        # 3/4 exercises a second set bit and two denominator halvings, beyond
        # the candidate's predominantly power-of-two coefficient alphabet.
        word = [['add', 0, 1, -3, 4, self.reference['frame']]]
        expected = [[Fraction(i == j) for i in range(8)] for j in range(8)]
        expected[1][0] = Fraction(-3, 4)
        for scheme in ('historical_horner', 'pr696'):
            self.assertEqual(independent.primitive_columns(independent.lower(word, scheme)), expected)

    def test_wrong_primitive_sign_is_detected_on_source_basis(self):
        word = [['add', 0, 1, -1, 2, self.reference['frame']]]
        primitives = independent.lower(word, 'pr696')
        intended = independent.primitive_columns(primitives)
        changed = [tuple(event[:-1]) + (1,) if event[0] == 'add' and event[1] == 0
                   else event for event in primitives]
        self.assertNotEqual(independent.primitive_columns(changed), intended)

    def test_private_alias_and_non_dyadic_are_rejected(self):
        candidate = copy.deepcopy(self.reference)
        first = next(e for e in candidate['replacement'] if e[0] == 'add')
        first[2] = 8
        with self.assertRaisesRegex(ValueError, 'private register'):
            independent.check(candidate, self.reference)
        first[2], first[3], first[4] = 0, 1, 3
        with self.assertRaisesRegex(ValueError, 'not dyadic'):
            independent.check(candidate, self.reference)

    def test_changed_target_cannot_self_certify(self):
        candidate = copy.deepcopy(self.reference)
        candidate['matrix'][0][0] = '7'
        with self.assertRaisesRegex(ValueError, 'changed claimed target'):
            independent.check(candidate, self.reference)


class FiniteFamilyTests(unittest.TestCase):
    def test_butterfly_variants_have_declared_two_by_two_maps(self):
        for reverse in (False, True):
            i, j = (1, 0) if reverse else (0, 1)
            for form in range(4):
                columns = independent.macro_columns(factor.butterfly(i, j, form))
                expected = [[Fraction(a == b) for a in range(8)] for b in range(8)]
                upper = Fraction(1, 2) if form & 1 else Fraction(1)
                lower = Fraction(1, 2) if form & 2 else Fraction(1)
                expected[i][i], expected[j][i] = upper, upper
                expected[i][j], expected[j][j] = lower, -lower
                self.assertEqual(columns, expected)

    def test_seven_input_prefixes_match_explicit_coordinate_table(self):
        half = Fraction(1, 2)
        blocks = [((half, 1), (half, -1)),
                  ((half, -1), (half, 0)),
                  ((half, 1), (-half, 1)),
                  ((1, -2), (half, 0)),
                  ((1, 0), (-half, 1)),
                  ((1, -2), (0, 1)),
                  ((1, 0), (0, 1))]
        for i, j in ((1, 7), (2, 5)):
            for form, block in enumerate(blocks):
                expected = [[Fraction(a == b) for a in range(8)] for b in range(8)]
                expected[i][i], expected[j][i] = block[0]
                expected[i][j], expected[j][j] = block[1]
                self.assertEqual(independent.macro_columns(factor.input_pair(i, j, form)), expected)

    def test_weighted_input_prefix_right_inverse_has_correct_order(self):
        target = [[Fraction(x) for x in row] for row in factor.C['matrix']]
        for first in range(7):
            for second in range(7):
                prefix = factor.input_pair(1, 7, first) + factor.input_pair(2, 5, second)
                residual = factor.right_inverse(target, prefix)
                prefix_columns = independent.macro_columns(prefix)
                product = [[sum(residual[i][k]*prefix_columns[j][k] for k in range(8))
                            for j in range(8)] for i in range(8)]
                self.assertEqual(product, target)

    def test_current_cost_matches_independent_literal_lowering(self):
        # Covers non-power-of-two numerators and denominator reduction as well
        # as every sign and scale used by the declared template generators.
        for numerator in range(-31, 32):
            if numerator:
                for exponent in range(7):
                    event = factor.add(0, 1, Fraction(numerator, 2**exponent))
                    self.assertEqual(factor.current_cost([event]),
                                     len(independent.lower([event], 'pr696')))
        for exponent in range(-8, 9):
            for sign in (-1, 1):
                event = factor.scale(0, sign * Fraction(2)**exponent)
                self.assertEqual(factor.current_cost([event]),
                                 len(independent.lower([event], 'pr696')))


if __name__ == '__main__':
    unittest.main()
