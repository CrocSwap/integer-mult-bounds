"""Exact controls for the scoped idempotent path-rank audit.

Copyright 2026 Curtis Dransfield. Apache-2.0.
Prepared with substantial OpenAI Codex assistance; historical source
attribution remains in the package's proof note and retained repository.
"""
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import random
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import linalg as algebra
from independent import independent_check, rank_by_minors


def fixture_data():
    return json.loads((HERE / 'WITNESSES.json').read_text())


def apply_literal(matrix, vector):
    return tuple(sum(a*b for a, b in zip(row, vector)) for row in matrix)


class ExactLinearAlgebra(unittest.TestCase):
    def test_rational_rectangular_ranks_against_permutation_minors(self):
        rng = random.Random(71)
        examples = [[[0, 1, 0], [0, 0, 1], [1, 0, 0]],
                    [[1, '1/2', 0], [0, 0, 1], [2, 1, 3]],
                    [['1/2', 1, '3/2'], [1, 2, 3], [0, 0, 0]],
                    [[0, 0, 0]] * 3, [[1, 2], [2, 4], [3, 6]]]
        for height in range(1, 4):
            for width in range(1, 4):
                for _ in range(12):
                    examples.append([[F(rng.randrange(-3, 4), rng.randrange(1, 6))
                                      for _ in range(width)] for _ in range(height)])
        for example in examples:
            matrix = algebra.matrix(example)
            with self.subTest(matrix=matrix):
                self.assertEqual(algebra.rank(matrix), rank_by_minors(matrix))
                reduced, pivots = algebra.rref(matrix)
                self.assertEqual(rank_by_minors(reduced), len(pivots))
                self.assertTrue(all(isinstance(x, F) for row in reduced for x in row))

    def test_nullspace_spans_exact_kernel_for_rectangular_matrices(self):
        examples = ([[0, 0, 0]], [[1, '1/2', 0], [2, 1, 0]],
                    [[0, 1, 2], [0, 2, 4]], [[1, 2], [2, 4], [3, 6]],
                    [[0, 1], [1, 0]], [[1, 0, 2], [0, 1, 3]])
        for example in examples:
            matrix = algebra.matrix(example)
            basis = algebra.nullspace(matrix)
            with self.subTest(matrix=matrix):
                self.assertEqual(len(basis), len(matrix[0]) - rank_by_minors(matrix))
                self.assertEqual(rank_by_minors(basis), len(basis))
                for vector in basis:
                    self.assertEqual(apply_literal(matrix, vector), (0,) * len(matrix))

    def test_rational_inverse_and_singular_rejection(self):
        for raw in ([[0, 1], [1, 0]], [[1, '1/2'], ['1/3', 1]],
                    [[0, 1, 0], [0, 0, 1], [1, 0, 0]]):
            matrix = algebra.matrix(raw)
            inverse = algebra.inverse(matrix)
            self.assertEqual(algebra.mul(matrix, inverse), algebra.eye(len(matrix)))
            self.assertEqual(algebra.mul(inverse, matrix), algebra.eye(len(matrix)))
            self.assertEqual(rank_by_minors(inverse), len(matrix))
        with self.assertRaisesRegex(ValueError, 'Singular inverse'):
            algebra.inverse(algebra.matrix([[1, 2], [2, 4]]))
        with self.assertRaisesRegex(ValueError, 'Square inverse'):
            algebra.inverse(algebra.matrix([[1, 2, 3]]))

    def test_exact_inputs_shapes_and_idempotence_are_required(self):
        for raw in ([], [[]], [[1], [1, 2]], [[1.0]], [[True]]):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                algebra.matrix(raw)
        invalid_pairs = (([[F(1, 2), 0], [0, F(1, 2)]], algebra.eye(2)),
                         ([[0, 1], [0, 0]], algebra.eye(2)),
                         (algebra.eye(2), algebra.eye(3)),
                         ([[1, 0, 0], [0, 1, 0]], algebra.eye(2)))
        for p, q in invalid_pairs:
            with self.subTest(p=p, q=q), self.assertRaises(ValueError):
                algebra.analyze_pair(p, q)
        for raw in ([[1.0]], [[1], [1, 2]], [[1] * 4] * 4):
            with self.assertRaises(ValueError):
                rank_by_minors(raw)

    def test_source_guard_rejects_mutated_and_missing_bytes(self):
        from verify import verify_pins
        with tempfile.TemporaryDirectory(prefix='path-rank-pin-control-') as directory:
            root = Path(directory)
            source = root / 'fixture.py'
            content = b'# exact pinned input\n'
            source.write_bytes(content)
            manifest = dict(base_commit='test-only', sha256={'fixture.py': sha256(content).hexdigest()})
            self.assertEqual(verify_pins(root=root, manifest=manifest)['checked_files'], 1)
            source.write_bytes(content + b'# changed\n')
            with self.assertRaisesRegex(ValueError, 'Source pin mismatch: fixture.py'):
                verify_pins(root=root, manifest=manifest)
            source.unlink()
            with self.assertRaises(FileNotFoundError):
                verify_pins(root=root, manifest=manifest)


class IdempotentPathAudit(unittest.TestCase):
    def test_all_ten_named_fixture_ranks_use_independent_oracle(self):
        fixtures = fixture_data()
        self.assertEqual(len(fixtures), 10)
        for name, fixture in fixtures.items():
            p, q = algebra.matrix(fixture['P']), algebra.matrix(fixture['Q'])
            difference = algebra.sub(algebra.sub(algebra.eye(len(p)), p), q)
            matrices = (p, q, algebra.mul(p, q), algebra.mul(q, p), difference)
            independent_ranks = [rank_by_minors(matrix) for matrix in matrices]
            with self.subTest(name=name):
                self.assertEqual(independent_ranks, fixture['expected_ranks'])
                result = algebra.analyze_pair(p, q)
                keys = ('rank_P', 'rank_Q', 'rank_PQ', 'rank_QP', 'endpoint_difference_rank')
                self.assertEqual([result[key] for key in keys], independent_ranks)
                self.assertEqual(result['minimum_path_excess'], fixture['expected_excess'])

    def test_named_kernel_witnesses_lie_in_the_two_intersections(self):
        for name, fixture in fixture_data().items():
            p, q = algebra.matrix(fixture['P']), algebra.matrix(fixture['Q'])
            result = algebra.analyze_pair(p, q)
            left, right = result['kernel_left_basis'], result['kernel_right_basis']
            with self.subTest(name=name):
                for vector in left:
                    self.assertEqual(apply_literal(p, vector), vector)
                    self.assertEqual(apply_literal(q, vector), (0,) * len(p))
                for vector in right:
                    self.assertEqual(apply_literal(q, vector), vector)
                    self.assertEqual(apply_literal(p, vector), (0,) * len(p))
                self.assertEqual(rank_by_minors(left + right), len(left) + len(right))
                self.assertEqual(len(left) + len(right),
                                 len(p) - result['endpoint_difference_rank'])

    def test_arbitrary_nonidempotent_internal_frames_preserve_path_bound(self):
        middle = algebra.matrix([[F(2, 3), -2], [3, F(7, 5)]])
        self.assertNotEqual(algebra.mul(middle, middle), middle)
        for name in ('same_line', 'one_sided_rank_one', 'reverse_one_sided_rank_one'):
            fixture = fixture_data()[name]
            p, q = algebra.matrix(fixture['P']), algebra.matrix(fixture['Q'])
            end = algebra.sub(algebra.eye(2), q)
            bound = algebra.analyze_pair(p, q)['minimum_path_excess']
            for chain in ((p, end), (p, middle, end), (p, middle, algebra.zero(2), end)):
                actual = algebra.path_excess(chain)
                independent_charge = sum(rank_by_minors(algebra.sub(b, a))
                                         for a, b in zip(chain, chain[1:]))
                signed = rank_by_minors(end) - rank_by_minors(p)
                self.assertEqual(actual['charge'], independent_charge)
                self.assertEqual(actual['excess'], independent_charge - signed)
                self.assertGreaterEqual(actual['excess'], bound)
            self.assertEqual(algebra.path_excess((p, end))['excess'], bound)

    def test_common_nondegenerate_indefinite_form_equalizes_product_ranks(self):
        h = algebra.matrix([[1, 0], [0, -1]])
        p = algebra.matrix([[1, 0], [0, 0]])
        q = algebra.matrix([['4/3', '-2/3'], ['2/3', '-1/3']])
        self.assertEqual(rank_by_minors(h), 2)
        for projector in (p, q):
            self.assertEqual(algebra.mul(h, projector),
                             algebra.mul(algebra.transpose(projector), h))
        result = algebra.analyze_pair(p, q)
        self.assertEqual(result['rank_PQ'], result['rank_QP'])
        self.assertEqual(result['minimum_path_excess'], 2)
        # A degenerate H=0 is common and symmetric for the asymmetric pair,
        # so merely saying "symmetric form" would not justify equal ranks.
        asymmetric = fixture_data()['one_sided_rank_one']
        p, q = algebra.matrix(asymmetric['P']), algebra.matrix(asymmetric['Q'])
        degenerate = algebra.zero(2)
        for projector in (p, q):
            self.assertEqual(algebra.mul(degenerate, projector),
                             algebra.mul(algebra.transpose(projector), degenerate))
        self.assertNotEqual(rank_by_minors(algebra.mul(p, q)), rank_by_minors(algebra.mul(q, p)))

    def test_tensor_spectator_scales_all_endpoint_terms(self):
        fixture = fixture_data()['one_sided_rank_one']
        p, q = algebra.matrix(fixture['P']), algebra.matrix(fixture['Q'])
        end = algebra.sub(algebra.eye(2), q)
        base = algebra.path_excess((p, end))
        for spectator in (algebra.matrix([[1, 1], [0, 0]]), algebra.eye(2), algebra.zero(2)):
            weight = rank_by_minors(spectator)
            lifted = algebra.path_excess((algebra.kron(p, spectator), algebra.kron(end, spectator)))
            for key in ('charge', 'signed_rank_increment', 'excess'):
                self.assertEqual(lifted[key], weight * base[key])

    def test_common_additive_block_needs_complementary_support(self):
        p = algebra.matrix([[1, 0], [0, 0]])
        q = algebra.matrix([[0, 1], [0, 1]])
        # For P=Q, arbitrary B=-P gives zero excess despite product-rank sum2.
        bad_offset = algebra.scale(p, -1)
        bad_start = algebra.add(bad_offset, p)
        bad_end = algebra.add(bad_offset, algebra.sub(algebra.eye(2), p))
        self.assertEqual(algebra.path_excess((bad_start, bad_end))['excess'], 0)
        self.assertEqual(algebra.analyze_pair(p, p)['minimum_path_excess'], 2)
        # Actual compiler structure: low=(I-prior) tensor I and variable
        # prior tensor P mutually annihilate and have additive ranks.
        prior = algebra.matrix([[1, 1], [0, 0]])
        low = algebra.kron(algebra.sub(algebra.eye(2), prior), algebra.eye(2))
        start_active = algebra.kron(prior, p)
        end_active = algebra.kron(prior, algebra.sub(algebra.eye(2), q))
        for active in (start_active, end_active):
            self.assertEqual(algebra.mul(low, active), algebra.zero(4))
            self.assertEqual(algebra.mul(active, low), algebra.zero(4))
            self.assertEqual(algebra.rank(algebra.add(low, active)),
                             algebra.rank(low) + algebra.rank(active))
        lifted = algebra.path_excess((algebra.add(low, start_active), algebra.add(low, end_active)))
        self.assertEqual(lifted['excess'], algebra.analyze_pair(p, q)['minimum_path_excess'])

    def test_bounded_enumeration_and_counterexamples_complete(self):
        result = independent_check()
        self.assertEqual(result['domain']['matrices_examined'], 7**4)
        self.assertEqual(result['domain']['idempotents'], 44)
        self.assertEqual(result['domain']['ordered_pairs'], 44**2)
        self.assertEqual(sum(result['product_rank_histogram'].values()), 44**2)
        controls = result['controls']
        nonidempotent = controls['false_identity_without_idempotence']
        self.assertNotEqual(nonidempotent['ranks']['difference'], nonidempotent['invalid_identity_rhs'])
        converse = controls['false_converse_equal_product_ranks_implies_common_form']
        self.assertEqual(converse['ranks']['pq'], converse['ranks']['qp'])
        self.assertFalse(converse['common_nondegenerate_symmetric_form_exists'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
