"""Semantic and algebraic controls for the exact tail-prefix certificates.

AAAmirinu with substantial OpenAI Codex assistance. Apache-2.0.
All checks use unittest assertions or explicit exceptions, also under -O.
The immutable channel is read only; fault controls mutate in-memory copies.
"""
from copy import deepcopy
from fractions import Fraction as Q
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import subprocess
import sys
import unittest


HERE = Path(__file__).resolve().parent
SPEC = spec_from_file_location('p104_tail_control_verify', HERE / 'verify.py')
verify = module_from_spec(SPEC)
SPEC.loader.exec_module(verify)
trace = verify.trace


def unit(index):
    return [int(i == index) for i in range(8)]


def outer(left, right):
    return [[x * y for y in right] for x in left]


def matrix_sum(left, right):
    return [[x + y for x, y in zip(a, b)] for a, b in zip(left, right)]


def compression(matrix, lefts, rights):
    return [[sum(left[i] * matrix[i][j] * right[j]
                 for i in range(8) for j in range(8))
             for right in rights] for left in lefts]


def determinant2(matrix):
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def determinant3(matrix):
    a, b, c = matrix
    return (a[0] * (b[1] * c[2] - b[2] * c[1])
            - a[1] * (b[0] * c[2] - b[2] * c[0])
            + a[2] * (b[0] * c[1] - b[1] * c[0]))


class CompressionPremiseControls(unittest.TestCase):
    """Explicit low-rank counterexamples when a required equality is omitted."""
    p = [-1, 1, 0, 0, 0, 0, 0, 0]
    q = [-1, 0, 1, 0, 0, 0, 0, 0]
    w = [0, 0, 1, 1, 1, 1, -1, 1]
    a = [1, 1, 0, 0, 0, 0, 0, 0]
    b = [1, 0, 1, 0, 0, 0, 0, 0]
    k = [0, 0, 0, 0, 0, 0, -1, 1]
    x = [0, 0, -1, 1, 0, 0, 0, 1]

    def test_missing_zero_entry_allows_rank_one(self):
        # The two off-diagonal entries alone do not force rank two.
        left = [0, 1, 1, 0, 0, 0, 0, -1]
        matrix = outer(left, [-1, 0, 0, 0, 0, 0, 0, 0])
        small = compression(matrix, [self.p, self.q], [self.a, self.b])
        self.assertEqual(small, [[-1, -1], [-1, -1]])
        self.assertEqual(determinant2(small), 0)
        self.assertEqual(verify.rank(matrix), 1)
        self.assertNotEqual(small[0][0], 0)
        self.assertEqual(compression(matrix, [[1, 0, 0, 0, 0, 0, 0, 1]],
                                     [self.a]), [[1]])

    def test_missing_q_kernel_entry_allows_rank_two(self):
        # This is the actual new residual: q^T N k=-2, not zero. Omitting
        # that premise would falsely extend the rank-three lower bound.
        matrix = matrix_sum(outer(self.x, [0, 1, 0, 0, 0, 0, 0, 2]),
                            outer([0, -1, 0, 0, 0, 0, 0, 0], unit(2)))
        small = compression(matrix, [self.p, self.q, self.w],
                            [self.a, self.b, self.k])
        self.assertEqual(small, [[0, -1, 0], [-1, 0, -2], [1, 0, 2]])
        self.assertEqual(determinant3(small), 0)
        self.assertEqual(determinant2([row[:2] for row in small[:2]]), -1)
        self.assertEqual(verify.rank(matrix), 2)
        self.assertEqual(small[0][2], 0)
        self.assertEqual(small[2][2], 2)
        self.assertNotEqual(small[1][2], 0)

    def test_missing_nonzero_third_entry_allows_rank_two(self):
        matrix = matrix_sum(outer(self.x, unit(1)),
                            outer([0, -1, 0, 0, 0, 0, 0, 0], unit(2)))
        small = compression(matrix, [self.p, self.q, self.w],
                            [self.a, self.b, self.k])
        self.assertEqual(small, [[0, -1, 0], [-1, 0, 0], [1, 0, 0]])
        self.assertEqual(determinant3(small), 0)
        self.assertEqual(verify.rank(matrix), 2)
        # Restoring the required nonzero entry gives the certified determinant.
        forced = [row[:] for row in small]
        forced[2][2] = 2
        self.assertEqual(determinant3(forced), -2)
        self.assertEqual(verify.rank(forced), 3)


class FrozenTraceControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.certificate = trace.read(HERE / 'WITNESS.json')
        cls.wanted = verify.validate_certificate(cls.certificate)
        # Certificate controls share one full, pinned 280-input replay.
        cls.collected = trace.collect([2753, 2823], cls.wanted)
        cls.word = trace.sources()['LOWRANK-WITNESS.json']

    def test_positive_result_matches_complete_receipt(self):
        result = verify.run(self.certificate, self.collected)
        self.assertEqual(result, trace.read(HERE / 'RESULT.json'))
        self.assertEqual(result['intervals'], [
            {'start': 2718, 'end': 2753, 'minimum': 99},
            {'start': 2754, 'end': 2823, 'minimum': 98},
        ])
        self.assertEqual(result['trace']['cuts_replayed'], 4059)
        self.assertEqual(result['trace']['boundary_columns'], 280)

    def test_wrong_new_contact_weight_rejected(self):
        bad = deepcopy(self.certificate)
        self.assertEqual(bad['upper_witnesses'][1]['terms'][-1],
                         [19, 2754, 'Y0', '-4'])
        bad['upper_witnesses'][1]['terms'][-1][3] = '4'
        verify.validate_certificate(bad)
        with self.assertRaisesRegex(ValueError, 'explicit rank-two residual differs'):
            verify.check_upper(bad['upper_witnesses'][1], self.collected)

    def test_future_contact_rejected_before_replay(self):
        bad = deepcopy(self.certificate)
        bad['upper_witnesses'][1]['terms'][-1][1] = 2755
        with self.assertRaisesRegex(ValueError, 'future contact'):
            verify.validate_certificate(bad)

    def test_self_contact_rejected_by_real_initial_state(self):
        with self.assertRaisesRegex(ValueError, 'contact absent or self-contact'):
            trace.collect([], [(7, 0, 'Y7')])

    def test_initial_compensation_sign_fault_rejected_at_endpoint(self):
        bad = deepcopy(self.word)
        self.assertEqual(bad['program'][0], ['add', 'Y0', 'Q0', '-1/4', []])
        bad['program'][0][3] = '1/4'
        # Keep a nonzero, lattice-compatible scalar and the same event count:
        # rejection must come from semantics, not the zero-weight syntax guard.
        with self.assertRaisesRegex(ValueError, 'arbitrary-input endpoint: Y0'):
            trace.collect([], word_override=bad)

    def test_final_cleanup_sign_fault_rejected_at_endpoint(self):
        bad = deepcopy(self.word)
        self.assertEqual(bad['program'][-1][:4], ['add', 'Q7', 'X103', -2])
        bad['program'][-1][3] = 2
        with self.assertRaisesRegex(ValueError, 'arbitrary-input endpoint: Q7'):
            trace.collect([], word_override=bad)

    def test_equivalent_scalar_and_frame_representations_preserve_trace(self):
        equivalent = deepcopy(self.word)
        for field in ('initial_frames', 'final_frames'):
            equivalent[field] = {name: list(reversed(chart))
                                 for name, chart in reversed(list(equivalent[field].items()))}
        for event in equivalent['program']:
            if event[0] == 'transport':
                event[2] = list(reversed(event[2]))
                event[3] = list(reversed(event[3]))
            else:
                event[-1] = list(reversed(event[-1]))
                if event[0] == 'add':
                    value = Q(event[3])
                    event[3] = str(2 * value.numerator) + '/' + str(2 * value.denominator)
        replay = trace.collect([2753, 2823], self.wanted, word_override=equivalent)
        for key in ('ports', 'pools', 'contacts'):
            self.assertEqual(replay[key], self.collected[key])
        expected_receipt = dict(self.collected['receipt'], input_overrides=True)
        self.assertEqual(replay['receipt'], expected_receipt)
        # Semantic equivalence does not grant acceptance to unpinned overrides.
        with self.assertRaisesRegex(ValueError, 'acceptance requires pinned inputs'):
            verify.run(self.certificate, replay)

    def test_first_new_contact_invalidates_old_rank_three_premise(self):
        key = (19, 2754, 'Y0')
        coefficient = self.collected['contacts'][key]
        self.assertEqual(coefficient, (Q(0), Q(0), Q(0), Q(0),
                                       Q(1, 4), Q(0), Q(1, 4), Q(0)))
        vectors = self.certificate['lower_vectors']
        self.assertEqual(verify.dot(vectors['q'], self.collected['ports'][19]) *
                         verify.dot(coefficient, vectors['k']), Q(-1, 2))
        one_new_contact = [set() for _ in range(104)]
        one_new_contact[19].add(coefficient)
        with self.assertRaisesRegex(ValueError, 'annihilator is violated'):
            verify.check_lower(one_new_contact, self.collected['ports'], vectors, True)

    def test_degenerate_compression_vector_rejected(self):
        vectors = deepcopy(self.certificate['lower_vectors'])
        vectors['q'] = [0] * 8
        # Zero q annihilates everything, but cannot prove the required minor.
        with self.assertRaisesRegex(ValueError, 'fixed nonzero two-dimensional compression'):
            verify.check_lower(self.collected['pools'][2823], self.collected['ports'],
                               vectors, False)

    def test_occupied_output_directory_is_rejected(self):
        # An existing directory exercises the early existence guard without
        # writing temporary files or risking any scientific artifact contents.
        self.assertTrue(HERE.is_dir())
        result = subprocess.run(
            [sys.executable, '-I', '-O', '-B', str(HERE / 'verify.py'),
             '--out', str(HERE)], capture_output=True, text=True,
            timeout=15, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('output already exists', result.stderr)
        self.assertTrue(HERE.is_dir())


if __name__ == '__main__':
    unittest.main(verbosity=2)
