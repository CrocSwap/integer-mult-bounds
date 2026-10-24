#!/usr/bin/env python3
"""Regression and negative controls for the new independent package only."""
from itertools import product
from pathlib import Path
import copy
import importlib.util
import random
import unittest

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location('turyn_cnf_'+name, HERE/(name+'.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


producer = load('build')
checker = load('verify')


def truth_table(clauses, variables):
    for values in product((False, True), repeat=variables):
        if all(any(values[abs(lit)-1] == (lit > 0) for lit in clause) for clause in clauses):
            return True
    return False


class IndependentChecks(unittest.TestCase):
    def test_every_two_variable_cnf(self):
        # All 512 sets of non-tautological clauses on two variables,
        # including the empty clause and empty formula.
        possible = [[i+1 if sign > 0 else -i-1 for i, sign in enumerate(signs) if sign]
                    for signs in product((-1, 0, 1), repeat=2)]
        for mask in range(1 << len(possible)):
            clauses = [row for i, row in enumerate(possible) if mask >> i & 1]
            solution, proof, _ = producer.solve(clauses)
            self.assertEqual(solution is not None, truth_table(clauses, 2))
            if solution is None:
                checker.check_tree(clauses, 2, proof)

    def test_seeded_three_variable_cnf(self):
        rng = random.Random(78)
        possible = [[i+1 if sign > 0 else -i-1 for i, sign in enumerate(signs) if sign]
                    for signs in product((-1, 0, 1), repeat=3)]
        for _ in range(512):
            clauses = rng.sample(possible, rng.randrange(28))
            solution, proof, _ = producer.solve(clauses)
            self.assertEqual(solution is not None, truth_table(clauses, 3))
            if solution is None:
                checker.check_tree(clauses, 3, proof)

    def test_source_pins(self):
        checker.check_sources()

    def test_two_independent_encodings(self):
        witness = checker.read('WITNESS.json')
        graph, _ = checker.geometry(witness)
        for edges in ([], witness['core_variable_edges'], witness['original_variable_edges']):
            first = producer.make_problem(witness['coordinates'], edges)
            second, variables, sizes = checker.encode(graph, edges)
            self.assertEqual(first['clauses'], second)
            self.assertEqual(len(first['labels']), variables)
            self.assertEqual(list(map(len, first['domains'])), sizes)

    def test_default_receipt(self):
        self.assertEqual(checker.run(), checker.read('EXPECTED.json'))

    def test_every_deleted_core_edge_breaks_its_old_proof(self):
        witness = checker.read('WITNESS.json')
        graph, _ = checker.geometry(witness)
        proof = checker.read('PROOF.json')
        for removed in witness['core_variable_edges']:
            edges = [e for e in witness['core_variable_edges'] if e != removed]
            clauses, variables, _ = checker.encode(graph, edges)
            with self.assertRaises((ValueError, IndexError)):
                checker.check_tree(clauses, variables, proof)

    def test_coordinate_and_edge_mutations(self):
        witness = checker.read('WITNESS.json')
        duplicate = copy.deepcopy(witness)
        duplicate['coordinates'][1] = duplicate['coordinates'][0]
        with self.assertRaises(ValueError):
            checker.geometry(duplicate)
        missing = copy.deepcopy(witness)
        missing['original_variable_edges'].pop()
        with self.assertRaises(ValueError):
            checker.geometry(missing)
        duplicate_edge = copy.deepcopy(witness)
        duplicate_edge['core_variable_edges'].append(duplicate_edge['core_variable_edges'][0])
        with self.assertRaises(ValueError):
            checker.geometry(duplicate_edge)

    def test_label_mutations(self):
        witness = checker.read('WITNESS.json')
        graph, _ = checker.geometry(witness)
        labels = checker.read('CONTROLS.json')['nine_bit_labels']
        for bad in (-1, 512, 0):
            altered = labels.copy()
            altered[0] = bad
            with self.assertRaises(ValueError):
                checker.fitting(graph, witness['original_variable_edges'], altered, 9)


if __name__ == '__main__':
    unittest.main()
