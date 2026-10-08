"""Independent Gram-rank and all-role checks for the polynomial-label screen."""
from fractions import Fraction as Q
from itertools import combinations
from math import comb
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts/experiments'))
from label_breakthrough_polynomial_screen import (
    audit, harmonic_dimension, optimistic_case, GLOBAL_BIT_UPPER,
    BASELINE_BIT_SAVING, BASELINE_KAPPA)


def rank_mod_prime(matrix, p=1009):
    """Direct row elimination; rank modulo p lower-bounds rational rank."""
    rows = [[x % p for x in row] for row in matrix]
    pivot = 0
    for col in range(len(rows[0])):
        candidate = next((j for j in range(pivot, len(rows)) if rows[j][col]), None)
        if candidate is None:
            continue
        rows[pivot], rows[candidate] = rows[candidate], rows[pivot]
        inverse = pow(rows[pivot][col], -1, p)
        leading = [(x * inverse) % p for x in rows[pivot][col:]]
        rows[pivot][col:] = leading
        for row in rows[pivot+1:]:
            factor = row[col]
            if factor:
                row[col:] = [(a-factor*b) % p for a, b in zip(row[col:], leading)]
        pivot += 1
        if pivot == len(rows):
            break
    return pivot


class PolynomialLabels(unittest.TestCase):
    def test_explicit_degree_two_gram_and_star_ranks(self):
        # Build the integer kernel directly from sets, without using the
        # harmonic eigenvalue or binomial-basis formula in the proof.
        labels = [frozenset(s) for s in combinations(range(10), 5)]
        matrix = [[(len(s & t)-1)*(len(s & t)-3) for t in labels] for s in labels]
        rank = rank_mod_prime(matrix)
        self.assertEqual(rank, 45)
        self.assertGreaterEqual(rank, harmonic_dimension(10, 2))
        star_indices = [i for i, s in enumerate(labels) if 0 in s]
        star = [[matrix[i][j] for j in star_indices] for i in star_indices]
        star_rank = rank_mod_prime(star)
        self.assertEqual(star_rank, 36)
        self.assertGreaterEqual(star_rank, harmonic_dimension(9, 2))
        for i, s in enumerate(labels):
            self.assertEqual(matrix[i][i], 8)
            for j, t in enumerate(labels):
                if i != j and len(s & t) % 2:
                    self.assertEqual(matrix[i][j], 0)

    def test_optimistic_ratio_from_complete_role_counts(self):
        for h in (22, 23, 24, 25, 40):
            case = optimistic_case(h, 2)
            v = comb(h, 5)
            r = comb(h, 2)-h
            rho = comb(h-1, 2)-(h-1)
            N, W, m = v**3, 2*v**3, r**3
            L = 3*v*v*h*rho
            self.assertEqual(case['optimistic_eta'], Q(N-2*L, W*m))
            self.assertLess(case['optimistic_saving_upper'], GLOBAL_BIT_UPPER)

    def test_finite_cases_and_rank_tail_boundary(self):
        result = audit()
        cases = result['finite_small_rank_cases']
        self.assertEqual(len(cases), 16)
        self.assertEqual([(c['k'], c['h']) for c in cases if c['positive_deficit_possible']],
                         [(5, 22), (5, 23), (5, 24)])
        self.assertEqual(harmonic_dimension(25, 2), 275)
        self.assertLess(harmonic_dimension(14, 3), 275)
        self.assertGreater(harmonic_dimension(15, 3), 275)
        self.assertGreater(harmonic_dimension(18, 4), 275)
        self.assertLess(result['bit_saving_strict_upper'], BASELINE_BIT_SAVING)
        self.assertLess(result['kappa_strict_upper'], BASELINE_KAPPA)


if __name__ == '__main__':
    unittest.main()
