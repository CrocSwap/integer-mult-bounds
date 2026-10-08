"""Independent finite linear-algebra checks for the affine-center screen."""
from fractions import Fraction as Q
from itertools import combinations
from math import comb
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts/experiments'))
from bit_breakthrough_affine_centers import (
    predicate_span, optimistic_saving_bounds, ceiling)


def rational_rank(matrix):
    """Fraction elimination independent of the screen's modular procedure."""
    if not matrix:
        return 0
    rows = [[Q(value) for value in row] for row in matrix]
    rank = 0
    for col in range(len(rows[0])):
        pivot = next((j for j in range(rank, len(rows)) if rows[j][col]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        divisor = rows[rank][col]
        rows[rank] = [value/divisor for value in rows[rank]]
        for row in rows[rank+1:]:
            factor = row[col]
            if factor:
                row[:] = [value-factor*leading for value, leading in zip(row, rows[rank])]
        rank += 1
        if rank == len(rows):
            break
    return rank


def binary_rank(integer_rows):
    """Exact GF2 bitset elimination; no rational/modular helper is reused."""
    pivots = {}
    for value in integer_rows:
        while value:
            pivot = value.bit_length()-1
            if pivot not in pivots:
                pivots[pivot] = value
                break
            value ^= pivots[pivot]
    return len(pivots)


class AffineCenterTargets(unittest.TestCase):
    def test_canonical_center_matrix_rank_directly_over_f2(self):
        for h in range(6, 11):
            triples = [frozenset(t) for t in combinations(range(h), 3)]
            B = [sum((len(s & t) % 2) << j for j, t in enumerate(triples))
                 for s in triples]
            self.assertEqual(binary_rank(B), h)
            for i, s in enumerate(triples):
                for j, t in enumerate(triples):
                    side = int(len(s & t) == 1)
                    self.assertEqual(((B[i] >> j) & 1) ^ side, int(i == j))

    def test_all_small_masks_have_predicted_exact_rational_rank(self):
        h = 6
        triples = list(combinations(range(h), 3))
        for mask in range(1 << h):
            support = [tuple(int(i in triple) for i in range(h)) for triple in triples
                       if sum((mask >> i) & 1 for i in triple) % 2]
            dimension, normal = predicate_span(h, mask)
            self.assertEqual(rational_rank(support), dimension, mask)
            if normal is not None:
                self.assertTrue(any(normal))
                self.assertTrue(all(sum(x*y for x, y in zip(row, normal)) == 0
                                    for row in support))

    def test_hyperplane_and_full_span_orbits_over_rationals(self):
        for h in (7, 8, 9, 11):
            triples = list(combinations(range(h), 3))
            for weight in (1, 2, 3, h-3, h-2, h-1, h):
                mask = (1 << weight)-1
                support = [[int(i in triple) for i in range(h)] for triple in triples
                           if sum(i < weight for i in triple) % 2]
                self.assertEqual(rational_rank(support), predicate_span(h, mask)[0])
            # Weight-two masks really are hyperplanes, not full spans.
            self.assertEqual(predicate_span(h, 3)[0], h-1)
            self.assertEqual(predicate_span(h, (1 << h)-4)[0], h-1)

    def test_affine_constant_is_complementation(self):
        h = 7
        for mask in range(1 << h):
            for triple in combinations(range(h), 3):
                parity = sum((mask >> i) & 1 for i in triple) % 2
                complement = sum((((1 << h)-1) ^ mask) >> i & 1 for i in triple) % 2
                self.assertEqual(parity ^ 1, complement)

    def test_role_and_loss_floors_reproduce_boundary_and_ceiling(self):
        self.assertIsNone(optimistic_saving_bounds(37))
        self.assertEqual(comb(37, 3), 6*37*(37-2))
        for h in (38, 48, 50):
            v = comb(h, 3)
            R, loss = v, h*(h-2)
            N, W, m = v**3, 2*v**3+2*v*v*R, h**3
            eta = Q(N-6*v*v*loss, W*m)
            self.assertEqual(optimistic_saving_bounds(h)[2], eta)
        result = ceiling()
        self.assertEqual(result['smallest_positive_h'], 38)
        self.assertEqual(result['optimistic_best_h'], 48)
        self.assertLess(Q(result['tail_primitive_saving_upper']),
                        Q(result['primitive_saving_lower']))
        self.assertLess(Q(result['primitive_saving_upper'])/2,
                        Q(result['kappa_upper']))
        self.assertLess(Q(result['improvement_factor_upper']), Q(14027, 1000))
        self.assertIn('NO NEW WITNESS', result['status'])


if __name__ == '__main__':
    unittest.main()
