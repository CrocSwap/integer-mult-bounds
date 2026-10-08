import random
import sys
import unittest
from fractions import Fraction as Q
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/experiments'))
import merged_exterior as me


def dense(X, h):
    classes, U, V, d, mask, sigma = X
    cls = [next(c for c, part in enumerate(classes) if part >> i & 1) for i in range(h)]
    return [[Q(int(i == j and mask >> i & 1)) + Q(sigma * sum(a * b for a, b in zip(U[cls[i]], V[cls[j]])), d)
             for j in range(h)] for i in range(h)]


def rational_rank(rows):
    rows = [r[:] for r in rows]
    rank = 0
    for c in range(len(rows[0]) if rows else 0):
        p = next((k for k in range(rank, len(rows)) if rows[k][c]), None)
        if p is None:
            continue
        rows[rank], rows[p] = rows[p], rows[rank]
        for k in range(len(rows)):
            if k != rank and rows[k][c]:
                f = rows[k][c] / rows[rank][c]
                rows[k] = [x - f * y for x, y in zip(rows[k], rows[rank])]
        rank += 1
    return rank


def ne_runs(M):
    """Top-row-first, rightmost-pivot elimination over Q."""
    M = [r[:] for r in M]
    pivots = []
    for i in range(len(M)):
        j = max((j for j, x in enumerate(M[i]) if x), default=None)
        if j is None:
            continue
        pivots.append((i, j))
        for k in range(i + 1, len(M)):
            if M[k][j]:
                f = M[k][j] / M[i][j]
                M[k] = [x - f * y for x, y in zip(M[k], M[i])]
    return len(pivots), me.runs(pivots)


def random_frame(rng, h):
    c = rng.choice((1, 2, 3))
    core = sum(1 << x for x in rng.sample(range(h), c))
    if c == 3:
        return core, core
    return core, core | sum(1 << x for x in rng.sample(range(h), rng.randrange(1, h - c)))


class MergedExteriorTest(unittest.TestCase):
    def test_exact_rank_matches_rational_elimination(self):
        rng = random.Random(2325)
        for h in (23, 25):
            for _ in range(40):
                X = me.operator(*random_frame(rng, h), h, rng.random() < 0.5)
                D = dense(X, h)
                S = sum(1 << x for x in range(h) if rng.random() < 0.6)
                T = sum(1 << x for x in range(h) if rng.random() < 0.6)
                sub = [[D[i][j] for j in range(h) if T >> j & 1] for i in range(h) if S >> i & 1]
                self.assertEqual(me.rank(X, S, T), rational_rank(sub) if sub and sub[0] else 0)

    def test_operators_are_idempotent(self):
        rng = random.Random(7)
        for h in (23, 25):
            for _ in range(4):
                frame = random_frame(rng, h)
                for complement in (False, True):
                    D = dense(me.operator(*frame, h, complement), h)
                    self.assertEqual([[sum(D[i][k] * D[k][j] for k in range(h)) for j in range(h)] for i in range(h)], D)

    def test_lemma_profile_matches_direct_elimination(self):
        """Random layouts pairing each local coordinate once with each line coordinate."""
        rng = random.Random(46)
        h, n = 23, 3
        for _ in range(12):
            layout = [(a, c) for a in range(h) for c in range(n)]
            rng.shuffle(layout)
            lam = [a for a, c in layout]
            v = [rng.randrange(1, 9) for _ in range(n)]
            nu0 = [rng.randrange(1, 9) for _ in range(n)]
            nu = [Q(x, sum(a * b for a, b in zip(nu0, v))) for x in nu0]
            X = me.operator(*random_frame(rng, h), h, rng.random() < 0.5)
            D = dense(X, h)
            M = [[Q(int(k == l)) - D[a][b] * v[c] * nu[e] for l, (b, e) in enumerate(layout)]
                 for k, (a, c) in enumerate(layout)]
            self.assertEqual(me.merged_profile(X, h, me.flags(lam)), ne_runs(M))

    def test_layout_reproduces_inherited_exterior(self):
        for h in (23, 25):
            identity = ((((1 << h) - 1), 0, 0), [(0,)] * 3, [(0,)] * 3, 1, (1 << h) - 1, 1)
            self.assertEqual(me.merged_profile(identity, h, me.FLAGS[h]), (me.M_ - h, [me.M_ - 2 * h, h]))


if __name__ == '__main__':
    unittest.main()
