#!/usr/bin/env python3
"""Adverse controls for the exact X4 forest exclusion (standard library only)."""
import copy
import importlib.util
import json
from pathlib import Path
from fractions import Fraction as Q
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('dyadic_verify_tests', HERE / 'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
c = v.primary


class DyadicForestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = c.load()
        cls.certificate = json.loads((HERE / 'CERTIFICATE.json').read_text(encoding='utf-8'))

    def test_synthetic_nonunit_really_beats_units(self):
        # Ten repeated quarter-grid entries. This disproves an alphabet-only
        # exclusion and catches silently restricting the search to unit inputs.
        root = 10 * c.cost(Q(3, 4))
        edge = lambda q: 2 * c.cost(q) + 10 * c.cost(Q(3, 4) - q * Q(1, 4))
        self.assertEqual((root, edge(Q(1)), edge(Q(-1)), edge(Q(3))), (80, 58, 48, 12))
        self.assertLess(edge(Q(3)), min(root, edge(Q(1)), edge(Q(-1))))

    def test_paid_horner_words_and_arbitrary_private_dirt(self):
        self.assertEqual(v.independent.primitive_controls('complete'), 1087)
        for q in (Q(1), Q(-1), Q(3, 2), Q(-543, 8), Q(1, 16)):
            self.assertEqual(c.cost(q), len(v.independent.horner_word(q.numerator, q.denominator)))
        self.assertEqual(c.cost(Q(3, 2)), 7)  # Each boundary is paid, not zero.
        with self.assertRaisesRegex(ValueError, 'non-dyadic'):
            c.cost(Q(1, 3))

    def test_tail_boundaries_and_large_exact_values(self):
        # Corroborates boundary arithmetic; the written proof covers the tails.
        coefficients = [Q(n, 2**k) for k in (4, 5, 31) for n in (-101, -3, -1, 1, 3, 101)]
        coefficients += [Q(-68), Q(68), Q(2**127), Q(-2**127)]
        for q in coefficients:
            for a in range(-4, 5):
                for b in range(-4, 5):
                    self.assertGreaterEqual(c.cost(Q(a, 4) - q * Q(b, 4)), c.cost(Q(a, 4)))

    def test_arbitrary_targets_depth_two_and_wrong_order(self):
        rows = {10: {0: Q(1)}, 11: {0: Q(3, 2)}, 12: {0: Q(1, 4)}}
        edges = [(11, 10, Q(3, 2)), (12, 11, Q(-5, 4))]
        receipt = v.independent.endpoint_control(rows, edges)
        self.assertEqual(len(receipt['negative_controls_rejected']), 6)
        prepare = [(12, 11, Q(5, 4)), (11, 10, Q(-3, 2))]
        inject = [(10, 0, Q(1)), (12, 0, Q(17, 8))]
        good = prepare + inject + edges
        registers = [0, 10, 11, 12]
        for backward in (False, True):
            endpoint = v.independent.replay(good, registers, backward)
            self.assertNotEqual(v.independent.replay(list(reversed(prepare)) + inject + edges,
                                                    registers, backward), endpoint)
            self.assertNotEqual(v.independent.replay(prepare + inject + list(reversed(edges)),
                                                    registers, backward), endpoint)

    def test_zero_target_trap(self):
        # Preparation is invisible on helper-only inputs but required on dirt.
        operations = [(11, 10, Q(-3, 2)), (10, 0, Q(1)), (11, 10, Q(3, 2))]
        full = v.independent.replay(operations, [0, 10, 11])
        missing = v.independent.replay(operations[1:], [0, 10, 11])
        self.assertNotEqual(full, missing)
        self.assertEqual([full[r].get(0, 0) for r in full], [missing[r].get(0, 0) for r in missing])

    def test_certificate_coverage_and_types(self):
        v.validate_census(self.certificate)
        altered = copy.deepcopy(self.certificate)
        altered['records'][0] = copy.deepcopy(altered['records'][1])
        with self.assertRaisesRegex(ValueError, 'coefficient coverage'):
            v.validate_census(altered)
        altered = copy.deepcopy(self.certificate)
        altered['records'][0]['strict_improvement_dominance'] = False
        with self.assertRaisesRegex(ValueError, 'typed certificate'):
            v.validate_census(altered)
        altered = copy.deepcopy(self.certificate)
        altered['records'][0]['min_dominance_margin'] = -1
        with self.assertRaisesRegex(ValueError, 'nonunit dominance'):
            v.validate_census(altered)

    def test_reject_unpaid_tree_edge(self):
        forest = copy.deepcopy(self.certificate['unit_forest'])
        index = next(i for i, row in enumerate(forest['edges']) if row[1] != -1)
        forest['edges'][index][0] -= 8
        with self.assertRaisesRegex(ValueError, 'tree edge invoice'):
            v.cycle_certificate(self.rows, forest)

    def test_reject_valid_but_nonminimal_forest(self):
        roots = {'edges': [[sum(c.cost(Q(a, 4)) for a in row.values()), -1, i, 0]
                            for i, row in self.rows.items()]}
        with self.assertRaisesRegex(ValueError, 'unit cycle inequality'):
            v.cycle_certificate(self.rows, roots)

    def test_reject_corrupt_source(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'source.tar.gz'
            path.write_bytes(b'corrupt source')
            with self.assertRaisesRegex(ValueError, 'archive hash'):
                c.load(path)
            with self.assertRaisesRegex(ValueError, 'archive SHA-256'):
                v.independent.read_rows(path)


if __name__ == '__main__':
    unittest.main(verbosity=2)
