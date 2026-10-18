"""Equivalence of optimized exact-rank helpers with hash-pinned predecessors.

Reference functions are verbatim copies of the base-commit implementations
(base 7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261):
- scripts/audit_fused_block.py rational_rank (Q(Q) construction)
- scripts/audit_stage_pair.py modular_rank (direct pow() inverses)

The optimized versions must return identical ranks and raise identical
exceptions on all inputs, including edge cases. No search domain,
stopping rule, or rejection logic is changed.
"""
from fractions import Fraction as Q
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_fused_block import rational_rank as optimized_rank
from audit_stage_pair import modular_rank as optimized_mod, _mod_inv
from audit_joint_frames import matrix


def reference_rank(m):
    rows = [[Q(x) for x in row] for row in m]
    rank = 0
    if not rows:
        return 0
    for col in range(len(rows[0])):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][col]
        rows[rank] = [x / scale for x in rows[rank]]
        for i in range(rank + 1, len(rows)):
            s = rows[i][col]
            if s:
                rows[i] = [x - s * y for x, y in zip(rows[i], rows[rank])]
        rank += 1
        if rank == len(rows):
            break
    return rank


def reference_mod(A, prime=101):
    rows = [[int(x.numerator) * pow(int(x.denominator) % prime, -1, prime) % prime
             for x in row] for row in A]
    n = len(rows)
    pivot = 0
    for j in range(len(rows[0])):
        k = next((i for i in range(pivot, n) if rows[i][j]), None)
        if k is None:
            continue
        rows[pivot], rows[k] = rows[k], rows[pivot]
        inv = pow(rows[pivot][j], -1, prime)
        rows[pivot] = [(x * inv) % prime for x in rows[pivot]]
        for i in range(pivot + 1, n):
            if rows[i][j]:
                c = rows[i][j]
                rows[i] = [(x - c * y) % prime for x, y in zip(rows[i], rows[pivot])]
        pivot += 1
        if pivot == n:
            break
    return pivot


class RankEquivalence(unittest.TestCase):
    def test_rational_rank_matches_reference(self):
        cases = [
            [[]],
            [[0]],
            [[1]],
            [[Q(1, 3)]],
            ((Q(1, 2), Q(1, 3)), (Q(1, 4), Q(1, 5))),
            ((1, 0), (0, 1)),
            ((1, 2), (2, 4)),
            ((101, 0), (0, Q(1, 2))),
            ((-Q(1, 6), Q(1, 3)), (Q(0), Q(-1, 6))),
            tuple(tuple(Q(i * j, 7) for j in range(5)) for i in range(4)),
            tuple(tuple(Q((-1) ** (i + j), 6) for j in range(6)) for i in range(6)),
            [[Q(10 ** 30, 3), Q(-7, 11)], [Q(5), Q(0)]],
            matrix(((1, 0), (0, 1))),
        ]
        for m in cases:
            self.assertEqual(optimized_rank(m), reference_rank(m), msg=str(m)[:120])

    def test_rational_rank_accepts_ints_and_fractions(self):
        m = [[1, 0], [0, 1]]
        self.assertEqual(optimized_rank(m), 2)
        mf = [[Q(1), Q(0)], [Q(0), Q(1)]]
        self.assertEqual(optimized_rank(mf), 2)
        self.assertEqual(optimized_rank(m), reference_rank(m))

    def test_modular_rank_matches_reference(self):
        cases = [
            matrix(((101, 0), (0, Q(1, 2)))),
            matrix(((1, 0), (0, 1))),
            matrix(((1, 2), (3, 4))),
            matrix(((Q(1, 3), Q(-1, 6)), (Q(0), Q(1, 3)))),
            matrix(tuple(tuple(Q(i + j, 6) for j in range(4)) for i in range(4))),
        ]
        for m in cases:
            for prime in (101, 103):
                self.assertEqual(optimized_mod(m, prime), reference_mod(m, prime))

    def test_modular_lower_bound_property_preserved(self):
        from audit_joint_frames import rank as exact_rank
        m = matrix(((101, 0), (0, Q(1, 2))))
        self.assertEqual(optimized_mod(m), 1)
        self.assertEqual(exact_rank(m), 2)
        self.assertEqual(optimized_mod(m, 103), 2)

    def test_noninvertible_denominator_raises_same_error(self):
        m = ((Q(1, 101),),)
        with self.assertRaises(ValueError):
            reference_mod(m, 101)
        with self.assertRaises(ValueError):
            optimized_mod(m, 101)
        with self.assertRaises(ValueError):
            _mod_inv(0, 101)

    def test_mod_inv_cache_returns_same_values(self):
        for d in (1, 2, 3, 6, 7, 50, 100):
            self.assertEqual(_mod_inv(d, 101), pow(d, -1, 101))
            self.assertEqual(_mod_inv(d, 103), pow(d, -1, 103))


if __name__ == "__main__":
    unittest.main()
