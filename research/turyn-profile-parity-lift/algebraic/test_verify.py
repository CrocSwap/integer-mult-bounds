#!/usr/bin/env python3
"""Regression controls for the independent ordinary-polynomial checker."""
from pathlib import Path
import copy
import importlib.util
import json
import unittest

HERE = Path(__file__).resolve().parent

def module(name):
    spec = importlib.util.spec_from_file_location('ordinary_' + name, HERE/(name+'.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

V = module('verify')


class AlgebraicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        witness = json.loads((V.BASELINE/'WITNESS.json').read_text())
        cls.variables, cls.forms, cls.equations = V.encode(witness)
        cls.proof = json.loads((HERE/'ORDINARY-PC-PROOF.json').read_text())
        cls.minor = json.loads((HERE/'QUADRATIC-RANK.json').read_text())

    def test_expected_receipt_and_57_deletion_assignments(self):
        self.assertEqual(V.run(), json.loads((HERE/'EXPECTED.json').read_text()))

    def test_ordinary_repeated_variables_are_retained(self):
        x = frozenset({(0,)})
        self.assertEqual(V.product(x, x), frozenset({(0, 0)}))
        self.assertEqual(V.product(x, V.product(x, x)), frozenset({(0, 0, 0)}))
        self.assertEqual(V.product(frozenset({(), (0,)}), frozenset({(), (0,)})),
                         frozenset({(), (0, 0)}))
        self.assertNotEqual(V.product(x, x), x)

    def test_ordinary_degree_four_multiplication_is_rejected(self):
        equation = frozenset({(0, 0, 0)})
        proof = {'steps': [{'kind': 'axiom', 'edge': 0},
                           {'kind': 'multiply', 'input': 0, 'variable': 0}],
                 'final': 1, 'degree_bound': 3}
        with self.assertRaisesRegex(ValueError, 'total degree at most three'):
            V.verify_steps(proof, [equation], 1)

    def test_no_boolean_or_unrecognized_rules(self):
        for kind in ('boolean_reduce', 'field_relation', 'divide', 'trust_solver'):
            wrong = copy.deepcopy(self.proof)
            wrong['steps'][0] = {'kind': kind}
            with self.subTest(kind=kind), self.assertRaisesRegex(ValueError, 'Unknown proof rule'):
                V.verify_steps(wrong, self.equations, len(self.variables))

    def test_proof_mutation_controls(self):
        self.assertEqual(len(V.check_controls(self.proof, self.equations, len(self.variables))), 4)

    def test_quadratic_minor_rank_and_corruptions(self):
        self.assertEqual(V.check_quadratic_minor(self.equations, self.minor)['rank'], 57)
        repeated = copy.deepcopy(self.minor)
        repeated['pivot_monomials'][0] = repeated['pivot_monomials'][1]
        with self.assertRaisesRegex(ValueError, 'square 57-column minor'):
            V.check_quadratic_minor(self.equations, repeated)
        singular = copy.deepcopy(self.minor)
        singular['pivot_monomials'][0] = [0, 0]
        with self.assertRaisesRegex(ValueError, 'invertible'):
            V.check_quadratic_minor(self.equations, singular)
        bad_count = copy.deepcopy(self.minor)
        bad_count['all_quadratic_monomials'] -= 1
        with self.assertRaisesRegex(ValueError, 'quadratic support'):
            V.check_quadratic_minor(self.equations, bad_count)

    def test_distinct_producer_encoding_and_reproduction(self):
        builder = module('build')
        witness, variables, monomials, columns, packed = builder.encode()
        self.assertEqual(variables, self.variables)
        decoded = [frozenset(m for i, m in enumerate(monomials) if row >> i & 1) for row in packed]
        self.assertEqual(decoded, self.equations)
        outputs = builder.build()
        for name, data in outputs.items():
            with self.subTest(name=name):
                self.assertEqual(data, json.loads((HERE/name).read_text()))


if __name__ == '__main__':
    unittest.main(verbosity=2)
