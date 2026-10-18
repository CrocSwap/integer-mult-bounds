"""CHECKED (exact): the ingredients of Theorem E (norm-2 line systems with products in {0,+-1}: v/T <= max(15, 2k'+1)) on the A_c and D_c lines
(identity A-bar = N^T N mod 2, rank formula c-1-[c even], T, ratio bound), and the arithmetic of Theorem F's constants."""
import os, sys, random, itertools
from fractions import Fraction as Fr
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from report import check, finish
from exact import rank_f2, rank_q
from lines import abar_rows


def lines_A(c):
    out = []
    for i, j in itertools.combinations(range(c), 2):
        v = [0] * c; v[i], v[j] = 1, -1; out.append(tuple(v))
    return out


def lines_D(c):
    out = lines_A(c)
    for i, j in itertools.combinations(range(c), 2):
        v = [0] * c; v[i], v[j] = 1, 1; out.append(tuple(v))
    return out


def connected(S, c):
    par = list(range(c))
    def f(x):
        while par[x] != x:
            par[x] = par[par[x]]; x = par[x]
        return x
    for r in S:
        a, b = [i for i, x in enumerate(r) if x]
        par[f(a)] = f(b)
    return len({f(i) for i in range(c)}) == 1


def test(c, pool, subsets):
    n = 0
    worst = Fr(0)
    for S in subsets:
        S = [pool[i] for i in S]
        if not S:
            continue
        G = [[sum(x * y for x, y in zip(a, b)) for b in S] for a in S]
        assert all(G[t][t] == 2 and abs(G[t][s]) <= 1 for t in range(len(S)) for s in range(len(S)) if t != s)
        rows = abar_rows(G)
        # A-bar = N^T N mod 2 (N = |incidence|): off-diagonal parity of the number of shared coordinates
        for t in range(len(S)):
            for s in range(len(S)):
                if t != s:
                    sh = sum(1 for x, y in zip(S[t], S[s]) if x and y)
                    assert ((rows[t] >> s) & 1) == (sh % 2), "A-bar != N^T N mod 2"
        T = rank_q([list(r) for r in S])
        r2 = rank_f2(rows)
        k = r2 // 2
        if connected(S, c):
            assert r2 == c - 1 - (c % 2 == 0), (c, r2)
            assert T in (c - 1, c)
        ratio = Fr(len(S), T)
        assert ratio <= max(15, 2 * k + 1), (c, len(S), T, k)
        worst = max(worst, Fr(len(S), T) / (2 * k + 1))
        n += 1
    return n, worst


rng = random.Random(7)
for typ, gen in (('A', lines_A), ('D', lines_D)):
    tot = 0
    for c in range(2, 8):
        pool = gen(c)
        m = len(pool)
        if m <= 15:
            subs = (tuple(i for i in range(m) if (mask >> i) & 1) for mask in range(1, 1 << m))
            mode = 'exhaustive'
        else:
            subs = (tuple(i for i in range(m) if rng.random() < rng.choice((0.3, 0.6, 0.9))) for _ in range(1500))
            mode = 'seeded random'
        n, worst = test(c, pool, subs)
        tot += n
        check('E.%s%d' % (typ, c), True, '%s_%d lines (%d lines in the pool), %s: %d subsets, A-bar = N^T N mod 2, connected support => rank_F2 A-bar = c-1-[c even], v/T <= max(15, 2k\'+1) (max v/(T(2k\'+1)) seen: %s)' % (typ, c, m, mode, n, worst))
# exceptional types: v/T of full root systems
check('E.exceptional', all(Fr(a, b) <= 15 for a, b in ((36, 6), (63, 7), (120, 8))), 'E6, E7, E8 lines: v/T = 6, 9, 15 (counts 36, 63, 120 are CHECKED in c1)')


# Theorem F constants (formula arithmetic only; the group-theoretic values themselves are citations)
vals = []
for n in (3, 4, 5):
    d = Fr((2 ** n - 1) * (2 ** (n - 1) - 1), 3)
    m = 2 ** (n - 1) * (2 ** n - 1)
    assert d.denominator == 1
    vals.append((n, int(d), m, 4 ** n - 1))
check('F.constants', [(n, d, m) for n, d, m, _ in vals] == [(3, 7, 28), (4, 35, 120), (5, 155, 496)],
      "formulas (2^n-1)(2^(n-1)-1)/3 and 2^(n-1)(2^n-1) for Sp(2n,2): n=3,4,5 -> degrees 7, 35, 155 and indices 28, 120, 496 [values are citations, only the arithmetic is checked]; "
      "a multiplicity-1 system on all 4^n-1 labels would then have v/T <= %s" % ', '.join('%d/%d=%.2f' % (N, min(d, m), N / min(d, m)) for n, d, m, N in vals))
finish()
