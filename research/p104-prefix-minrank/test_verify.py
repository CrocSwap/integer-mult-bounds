"""Exact positive fixtures and rejecting controls for the pooled-prefix audit.

AAAmirinu with substantial OpenAI Codex assistance. Apache-2.0.
Run directly with Python 3.12; unittest assertions also remain active under -O.
Frozen inputs are read only. Trace mutations live in independent in-memory copies.
"""
from copy import deepcopy
from fractions import Fraction as Q
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
SPEC = spec_from_file_location("p104_prefix_minrank_verify", HERE / "verify.py")
verify = module_from_spec(SPEC)
SPEC.loader.exec_module(verify)


def exact_rank(rows):
    """Independent small-matrix Gauss-Jordan oracle, not the verifier's basis code."""
    matrix = [[Q(value) for value in row] for row in rows]
    if not matrix:
        return 0
    width = len(matrix[0])
    if any(len(row) != width for row in matrix):
        raise ValueError("ragged independent rank input")
    next_row = 0
    for column in range(width):
        pivot = next((i for i in range(next_row, len(matrix))
                      if matrix[i][column]), None)
        if pivot is None:
            continue
        matrix[next_row], matrix[pivot] = matrix[pivot], matrix[next_row]
        scale = matrix[next_row][column]
        matrix[next_row] = [value / scale for value in matrix[next_row]]
        for i in range(len(matrix)):
            if i != next_row:
                scale = matrix[i][column]
                matrix[i] = [a - scale * b
                             for a, b in zip(matrix[i], matrix[next_row])]
        next_row += 1
    return next_row


def product(left, right):
    return [[sum(a * b for a, b in zip(row, column))
             for column in zip(*right)] for row in left]


def identity(size):
    return [[Q(i == j) for j in range(size)] for i in range(size)]


def subtract(left, right):
    return [[a - b for a, b in zip(x, y)] for x, y in zip(left, right)]


def add(left, right):
    return [a + b for a, b in zip(left, right)]


def scale(coefficient, vector):
    return [coefficient * value for value in vector]


def in_span(vector, rows):
    return exact_rank(rows + [vector]) == exact_rank(rows)


class AlgebraControls(unittest.TestCase):
    def test_rectangular_rank_identity_and_noninjective_global_map(self):
        # n=4, k=2, RR^T=2I and C=I-R^TR. The reparameterization factor is 1.
        roots = [[1, 1, 0, 0], [0, 0, 1, 1]]
        transpose = [list(column) for column in zip(*roots)]
        correction = subtract(identity(4), product(transpose, roots))
        self.assertEqual(product(roots, transpose), [[2, 0], [0, 2]])
        self.assertEqual(exact_rank(correction), 4)
        fixtures = [
            ([[0, 0]] * 4, 4, 2),
            ([[1, 0], [0, 0], [0, 0], [0, 0]], 3, 1),
            ([[Q(1, 2), 0], [Q(1, 2), 0],
              [0, Q(1, 2)], [0, Q(1, 2)]], 2, 0),
            (transpose, 4, 2),  # U=R^T-A=0; global U injectivity is false.
        ]
        for coefficients, expected_large, expected_small in fixtures:
            with self.subTest(coefficients=coefficients):
                actual = [add(row, adjustment) for row, adjustment in
                          zip(correction, product(coefficients, roots))]
                reduced = subtract(identity(2), product(roots, coefficients))
                self.assertEqual(exact_rank(actual), expected_large)
                self.assertEqual(exact_rank(reduced), expected_small)
                self.assertEqual(exact_rank(actual), 2 + exact_rank(reduced))
                self.assertEqual(verify.rank(actual), exact_rank(actual))
                self.assertEqual(verify.rank(reduced), exact_rank(reduced))
        kernel_vector = [[1], [-1], [0], [0]]
        self.assertEqual(product(roots, kernel_vector), [[0], [0]])
        self.assertEqual(product(correction, kernel_vector), kernel_vector)

    def check_lifting_counterexample(self, spaces, shared, local_parts):
        # Both targets have C=I-R^TR for R=(1,1); C is invertible.
        size = len(shared)
        pure_sources = identity(size)[:2]
        targets = [[0, -1] + [0] * (size - 2),
                   [-1, 0] + [0] * (size - 2)]
        root_code = [[1, 1]]
        for space, local in zip(spaces, local_parts):
            intersection_dimension = (exact_rank(space) + exact_rank(pure_sources)
                                      - exact_rank(space + pure_sources))
            self.assertEqual(intersection_dimension, 0)
            self.assertTrue(all(in_span(row[:2], root_code) for row in space))
            self.assertTrue(in_span(local, space))
        self.assertEqual(add(local_parts[0], shared), targets[0])
        self.assertEqual(add(local_parts[1], scale(-1, shared)), targets[1])
        self.assertEqual(exact_rank([shared]), 1)
        self.assertEqual(exact_rank(targets), 2)
        # h=0 is impossible even after source projection: c_1 is outside row(R).
        self.assertFalse(in_span(targets[0][:2], root_code))
        # Pure intersections force A=0, so the inapplicable formula would give 2.
        self.assertEqual(2 - 1 + exact_rank([[1]]), 2)

    def test_missing_dirty_unit_breaks_projection_lifting(self):
        # Coordinates: X1,X2,Y1,Y2,z. No own-target dirt occurs, but z is not free.
        first, second = [1, 1, 0, 0, 2], [1, 1, 0, 0, -2]
        spaces = [[[0, 0, 0, 1, 0], first],
                  [[0, 0, 1, 0, 0], second]]
        for target, space in enumerate(spaces):
            self.assertTrue(all(row[2 + target] == 0 for row in space))
            self.assertFalse(in_span([0, 0, 0, 0, 1], space))
        self.check_lifting_counterexample(
            spaces, [Q(1, 2), Q(-1, 2), 0, 0, 1],
            [scale(Q(-1, 2), first), scale(Q(-1, 2), second)])

    def test_own_target_dirt_breaks_projection_lifting(self):
        # All nuisance units other than Y_t are available, but Y_t occurs mixed.
        first, second = [1, 1, 2, 0], [1, 1, 0, -2]
        spaces = [[[0, 0, 0, 1], first], [[0, 0, 1, 0], second]]
        units = identity(4)
        for target, space in enumerate(spaces):
            self.assertTrue(in_span(units[3 - target], space))
            self.assertTrue(any(row[2 + target] != 0 for row in space))
        self.check_lifting_counterexample(
            spaces, [Q(1, 2), Q(-1, 2), 1, 1],
            [add(scale(Q(-1, 2), first), [0, 0, 0, -1]),
             add(scale(Q(-1, 2), second), [0, 0, 1, 0])])

    def test_extra_source_access_invalidates_common_code_floor(self):
        # Dropping source-code containment allows local service with H=0.
        first, second = [0, -1], [-1, 0]
        self.assertEqual(exact_rank([first, second]), 2)
        self.assertFalse(in_span(first, [[1, 1]]))
        self.assertFalse(in_span(second, [[1, 1]]))
        self.assertTrue(in_span(first, [first]))
        self.assertTrue(in_span(second, [second]))
        self.assertEqual(exact_rank([[0, 0], [0, 0]]), 0)


class FrozenTraceControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data = verify.sources()
        cls.ports = verify.geometry(data['P104-FIXTURE.json']['section4_explicit_P104'])
        cls.word = data['LOWRANK-WITNESS.json']
        cls.certificate = verify.read(HERE / 'WITNESS.json')
        wanted = [tuple(term[:3]) for witness in cls.certificate['witnesses']
                  for term in witness['terms']]
        # All positive/contact tests share this exact source-bound trace replay.
        cls.trace = verify.replay(cls.word, cls.ports, wanted)

    def test_positive_certificate_all_six_intervals(self):
        with patch.object(verify, 'replay', return_value=self.trace) as replay:
            result = verify.run(self.certificate)
        replay.assert_called_once()
        self.assertEqual(result['status'], 'PASS_P104_EARLY_PREFIX_MINRANK')
        self.assertEqual([row['minimum'] for row in result['intervals']],
                         [104, 103, 102, 101, 100, 99])
        self.assertEqual(result['cuts_replayed'], 4059)
        self.assertEqual(result['boundary_columns'], 280)

    def test_wrong_contact_sign_rejected_by_matching_bounds(self):
        bad = deepcopy(self.certificate)
        bad['witnesses'][0]['terms'][0][3] = '-1/2'
        with patch.object(verify, 'replay', return_value=self.trace) as replay:
            with self.assertRaisesRegex(ValueError, 'matching exact bounds'):
                verify.run(bad)
        replay.assert_called_once()

    def test_future_contact_rejected(self):
        witness = deepcopy(self.certificate['witnesses'][0])
        witness['terms'][0][1] = witness['cut'] + 1
        with self.assertRaisesRegex(ValueError, 'future cut'):
            verify.upper_bound(witness['terms'], self.trace[1], self.ports,
                               witness['cut'])

    def test_self_contact_excluded_by_actual_trace_replay(self):
        # Replay the real trace with a requested own-target row. This tests the
        # snapshot filter itself, not only an absent key in a hand-built mapping.
        with self.assertRaisesRegex(ValueError, 'contact absent or self-contact'):
            verify.replay(self.word, self.ports, [(7, 0, 'Y7')])

    def test_missing_initial_query_compensation_rejected_at_endpoint(self):
        bad = deepcopy(self.word)
        self.assertEqual(bad['program'][0], ['add', 'Y0', 'Q0', '-1/4', []])
        bad['program'][0][3] = '0'
        # Preserve all 4058 events and valid charts so this cannot pass merely
        # by detecting a shortened program or a transport-profile mismatch.
        with self.assertRaisesRegex(ValueError, 'arbitrary-input endpoint Y0'):
            verify.replay(bad, self.ports)

    def test_missing_final_query_cleanup_rejected_at_endpoint(self):
        bad = deepcopy(self.word)
        self.assertEqual(bad['program'][-1][:4], ['add', 'Q7', 'X103', -2])
        bad['program'][-1][3] = '0'
        with self.assertRaisesRegex(ValueError, 'arbitrary-input endpoint Q7'):
            verify.replay(bad, self.ports)

    def test_invalid_paid_transport_rank_rejected(self):
        bad = deepcopy(self.word)
        first = next(event for event in bad['program'] if event[0] == 'transport')
        self.assertEqual(first[-1], 3)
        first[-1] = 4
        with self.assertRaisesRegex(ValueError, 'transport rank'):
            verify.replay(bad, self.ports)


if __name__ == '__main__':
    unittest.main(verbosity=2)
