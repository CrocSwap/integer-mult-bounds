#!/usr/bin/env python3
"""Standard-library regressions for the new actual-port certificate checker."""
from pathlib import Path
from unittest.mock import patch
import copy
import importlib.util
import json
import unittest

HERE = Path(__file__).resolve().parent

def module(name):
    spec = importlib.util.spec_from_file_location('parity_' + name, HERE/(name+'.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

V = module('verify')

def gf4mul(a, b):
    value = 0
    for _ in range(2):
        if b & 1:
            value ^= a
        b >>= 1
        a <<= 1
        if a & 4:
            a ^= 7
    return value


def rank4(matrix):
    matrix = [row[:] for row in matrix]
    rank = 0
    for column in range(len(matrix[0])):
        pivot = next((i for i in range(rank, len(matrix)) if matrix[i][column]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        inverse = next(x for x in range(1, 4) if gf4mul(matrix[rank][column], x) == 1)
        matrix[rank] = [gf4mul(x, inverse) for x in matrix[rank]]
        for i, row in enumerate(matrix):
            if i != rank and row[column]:
                factor = row[column]
                matrix[i] = [x ^ gf4mul(factor, y) for x, y in zip(row, matrix[rank])]
        rank += 1
    return rank


class VerificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = V.load('CERTIFICATE.json')
        cls.code = V.turyn_code()
        cls.quotient = json.loads((V.ROOT/'research/turyn-code-space/evidence/PARITY-CERTIFICATE.json').read_text())['cliques']

    def test_exact_positive_receipt(self):
        self.assertEqual(V.run(), V.load('EXPECTED.json'))

    def test_all_required_corruption_controls(self):
        result = V.corruption_controls(self.data['profiles'][0], self.code, self.quotient)
        self.assertEqual(len(result), 7)
        self.assertIn('valid_same_class_port_breaks_actual_clique', result)

    def test_valid_same_class_geometry_is_not_enough(self):
        control = V.load('SAME-CLASS-CONTROL.json')
        V.actual_port(control['replacement_coordinates'], 0, self.code)
        changed = copy.deepcopy(self.data['profiles'][0])
        changed['coordinates'][control['position']] = control['replacement_coordinates']
        with self.assertRaisesRegex(ValueError, 'actual active port edge'):
            V.verify_profile(changed, self.code, self.quotient)

    def test_controls_cannot_silently_disappear(self):
        original = V.load
        for missing in ('SAME-CLASS-CONTROL.json', 'GLOBAL-SCOPE-CONTROL.json'):
            def absent(name, missing=missing):
                if name == missing:
                    raise FileNotFoundError(name)
                return original(name)
            with self.subTest(missing=missing), patch.object(V, 'load', absent):
                with self.assertRaises(FileNotFoundError):
                    V.run()

    def test_global_cross_profile_failure_is_exact(self):
        control = V.load('GLOBAL-SCOPE-CONTROL.json')
        report = V.global_scope_check(self.data['profiles'], self.quotient, control)
        self.assertEqual([r['missing_cross_profile_edges'] for r in report],
                         [138, 150, 128, 116, 108, 98, 142, 146, 140])
        for mode in ('count', 'dot', 'missing'):
            bad = copy.deepcopy(control)
            if mode == 'count':
                bad['cliques'][0]['missing_cross_profile_edges'] -= 1
            elif mode == 'dot':
                bad['cliques'][0]['first_missing_edge']['integer_block_dots'][0] = 1
            else:
                bad['cliques'].pop()
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                V.global_scope_check(self.data['profiles'], self.quotient, bad)

    def test_profile_geometry_and_membership_mutations(self):
        row = self.data['profiles'][0]['coordinates'][0]
        for mutation in (row[:-1], [0]*24, [True]+row[1:], [-x for x in row]):
            with self.subTest(mutation=mutation[:3]), self.assertRaises(ValueError):
                V.actual_port(mutation, 0, self.code)
        with self.assertRaises(ValueError):
            V.actual_port(row, 1, self.code)

    def test_incidence_and_provenance_mutations(self):
        source = self.data['profiles'][0]
        for key, value in (('profile', True), ('cliques', source['cliques'][:-1]),
                           ('classes', [0]*20), ('selected_ports', [0]*20),
                           ('all_ports_sha256', '0'*64), ('nine_bit_labels', [1]*20)):
            changed = copy.deepcopy(source)
            changed[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                V.verify_profile(changed, self.code, self.quotient)

    def test_source_pin_corruption(self):
        original = V.load
        def corrupt(name):
            value = original(name)
            if name == 'SOURCES.json':
                key = next(iter(value['files']))
                value['files'][key] = '0'*64
            return value
        with patch.object(V, 'load', corrupt), self.assertRaisesRegex(ValueError, 'Pinned source mismatch'):
            V.source_check()

    def test_binary_rank_against_span_enumeration(self):
        for a in range(16):
            for b in range(16):
                for c in range(16):
                    span = {0, a, b, c, a^b, a^c, b^c, a^b^c}
                    self.assertEqual(1 << V.binary_rank([a, b, c]), len(span))

    def test_asymmetric_extension_field_block_upper_bounds(self):
        # Vertex-dependent nonzero F4 row/column gauges make these actual
        # fitting matrices nonsymmetric while preserving rank and blocks.
        for record in self.data['profiles']:
            labels = record['nine_bit_labels']
            gram = [[(a&b).bit_count()%2 for b in labels] for a in labels]
            for d in (1, 2, 3):
                scales = [1+(i%3) for i in range(20*d)]
                inverses = [next(x for x in range(1, 4) if gf4mul(x, s) == 1) for s in scales]
                fitting = [[gf4mul(scales[i], inverses[j]) if i%d == j%d and gram[i//d][j//d] else 0
                            for j in range(20*d)] for i in range(20*d)]
                self.assertEqual(rank4(fitting), 9*d)
                for v in range(20):
                    self.assertEqual([row[v*d:(v+1)*d] for row in fitting[v*d:(v+1)*d]],
                                     [[int(i == j) for j in range(d)] for i in range(d)])
                for a in range(20):
                    for b in range(a):
                        if V.active(record['coordinates'][a], record['coordinates'][b]):
                            self.assertFalse(any(fitting[a*d+i][b*d+j] for i in range(d) for j in range(d)))
                if d < 3:
                    self.assertTrue(any(fitting[i][j] != fitting[j][i] for i in range(20*d) for j in range(i)))

    def test_complete_producer_replay_binds_literal_port_ids(self):
        generated = module('build').build()
        self.assertEqual(set(generated), {'CERTIFICATE.json', 'BUILD.json', 'FULL-PROFILE-UPPER.json',
                                        'SAME-CLASS-CONTROL.json', 'GLOBAL-SCOPE-CONTROL.json'})
        for name, data in generated.items():
            with self.subTest(name=name):
                self.assertEqual(data, V.load(name))


if __name__ == '__main__':
    unittest.main(verbosity=2)
