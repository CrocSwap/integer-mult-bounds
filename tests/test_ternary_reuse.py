"""Independent algebra and full-size local controls for ternary plateau reuse."""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import random
import sys
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
sys.path.insert(0, str(ROOT/'scripts/experiments'))
from paired_triple_circuit import PairedTriple
from prime_field_checks import SmallProducer
from ternary_reuse_core2 import PRIME, span_mod, rank3, local_count, certificate
from ternary_reuse_plateaus import (
    rational_basis, plateau_plan, compile_plan, audit_coefficients,
    equal_span_clusters, audit_frames, audit_wrapper)


def dense_rank3(matrix):
    rows = [row[:] for row in matrix]
    rank = 0
    for col in range(len(rows[0])):
        pivot = next((j for j in range(rank, len(rows)) if rows[j][col] % 3), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inverse = rows[rank][col] % 3
        rows[rank] = [(x*inverse) % 3 for x in rows[rank]]
        for j in range(rank+1, len(rows)):
            factor = rows[j][col]
            rows[j] = [(x-factor*y) % 3 for x, y in zip(rows[j], rows[rank])]
        rank += 1
        if rank == len(rows):
            break
    return rank


class TernaryReuse(unittest.TestCase):
    def test_modular_canonical_spaces_match_exact_rationals(self):
        rng = random.Random(6431)
        for n in (6, 8):
            triples = list(combinations(range(n), 3))
            vectors = [tuple(int(j in t) for j in range(n)) for t in triples]
            for _ in range(60):
                rows = tuple(rng.sample(vectors, rng.randrange(1, min(16, len(vectors)))))
                exact = rational_basis(rows)
                reduced = tuple(tuple((x.numerator*pow(x.denominator, -1, PRIME)) % PRIME
                                      for x in row) for row in exact)
                self.assertEqual(span_mod(rows, n), reduced)
        # Equal rank by itself is insufficient; these rank-one spaces differ.
        self.assertNotEqual(span_mod([(1, 1, 1, 0)], 4), span_mod([(1, 1, 0, 1)], 4))

    def test_packed_boundary_rank_is_over_characteristic_three(self):
        matrix = [[int(i != j) for j in range(4)] for i in range(4)]
        self.assertEqual(len(rational_basis(tuple(map(tuple, matrix)))), 4)
        self.assertEqual(rank3([sum(value << j for j, value in enumerate(row)) for row in matrix]), 3)
        rng = random.Random(8721)
        for p in range(1, 10):
            for q in range(1, 10):
                matrix = [[rng.randrange(2) for _ in range(p)] for _ in range(q)]
                masks = [sum(value << j for j, value in enumerate(row)) for row in matrix]
                self.assertEqual(rank3(masks), dense_rank3(matrix))

    def test_equal_frame_three_sum_gate_halves_roles(self):
        inputs = [(0, 1, 2, 3, 4), (0, 1, 2, 3, 5), (0, 1, 2, 3, 6)]
        c = SimpleNamespace(h=8, inputs=inputs, variables={t:i+1 for i,t in enumerate(inputs)},
                            active=set(range(1, 7)), args=[None]*4+[(1, 2), (1, 3), (2, 3)],
                            support=[0, 1, 2, 4, 3, 5, 6], outputs={0:4, 1:5, 2:6})
        labels = {i+1: (tuple(Q(int(j in t)) for j in range(8)),) for i,t in enumerate(inputs)}
        common = rational_basis(tuple(labels[i][0] for i in (1, 2, 3)))
        labels.update({i:common for i in (4, 5, 6)})
        groups = {1:[1], 2:[2], 3:[3], 4:[4, 5, 6]}
        home = {i:(i if i < 4 else 4) for i in c.active}
        code = compile_plan(c, plateau_plan(c, labels, groups, home))
        self.assertEqual(code['roles'], 3)  # Binary c+q compiler would use 6.
        self.assertTrue(audit_coefficients(c, code)['every_dirty_basis_restored_by_inverse'])

    def test_complete_small_network_frames_and_dirty_wrapper(self):
        c = SmallProducer(8)
        labels, groups, home = equal_span_clusters(c, enlarged=True, core2_only=True)
        code = compile_plan(c, plateau_plan(c, labels, groups, home))
        self.assertEqual(code['roles'], 1044)
        for frame in audit_frames(c, code):
            self.assertEqual(frame['loss'], 168)
            self.assertEqual(frame['total_rank'], 9472)
        self.assertTrue(audit_wrapper(c, code)['dirty_wrapper_restores_every_scratch'])

    def test_positive_local_saving_and_full_size_certificate(self):
        local = local_count(10, PairedTriple)
        self.assertEqual(local['saved_roles_per_common_pair'], 9)
        result = certificate()
        self.assertEqual(result['saved_roles_per_common_pair'], 174)
        self.assertEqual(result['global_h28']['new_role_upper_bound'], 11775168)
        self.assertEqual(result['global_h28']['saved_roles'], 65772)
        self.assertEqual(result['global_h28']['center_loss_unchanged'], 9828)
        small = result['positive_small_context']
        self.assertEqual((small['original_roles'], small['new_roles']), (1204, 1195))
        self.assertEqual(small['dirty_wrapper']['all_basis_symbols'], 1435)
        self.assertFalse(small['dirty_wrapper']['intended_map_is_identity'])
        self.assertTrue(small['dirty_wrapper']['dirty_wrapper_restores_every_scratch'])
        for frame in small['physical_frames']:
            self.assertEqual(frame['loss'], 10)
            self.assertEqual(frame['total_rank'], 17000)
        bound = result['deterministic_exactness']['minor_bound']
        self.assertEqual(bound, 3**13)
        self.assertGreater(PRIME, 2*bound*bound)


if __name__ == '__main__':
    unittest.main()
