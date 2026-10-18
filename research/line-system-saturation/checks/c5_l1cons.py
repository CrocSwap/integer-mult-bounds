"""CHECKED (exact integer arithmetic): the 14 best systems of the L1_CONS construction table (data/best_kprime_*.json).  For each: lines distinct up to sign, nonzero norms,
every pairwise product 0 or odd (after division by 'div' or through the stored lattice Gram), T = exact Q-rank, A-bar and its F2 rank 2k', window h = rank_F2(J + A-bar),
saturation v / (T (2^k'+1)) as a Fraction.  The comparison with the break-even fit x*(h) is relative to a RECORDED repo fit (not proved here)."""
import os, sys, json, glob
from fractions import Fraction as Fr
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
from report import check, finish
from exact import rank_f2, rank_q
from lines import abar_rows, window


def pos_def(M):
    n = len(M)
    A = [[Fr(x) for x in r] for r in M]
    for i in range(n):
        if A[i][i] <= 0:
            return False
        for j in range(i + 1, n):
            f = A[j][i] / A[i][i]
            A[j] = [a - f * b for a, b in zip(A[j], A[i])]
    return True


def xstar(h):
    return Fr(5385, 10000) - Fr(1495, 100000) * (h - 9)


files = sorted(glob.glob(os.path.join(HERE, '..', 'data', 'best_kprime_*.json')), key=lambda f: int(f.split('_')[-1][:-5]))
assert len(files) == 14
EXPECT = {0: (64, 64), 3: (56, 8), 4: (120, 8), 5: (140, 11), 6: (166, 13), 7: (240, 16), 8: (496, 16), 9: (55, 20), 12: (728, 24),
          15: (992, 32), 16: (480, 32), 20: (600, 40), 25: (960, 64), 32: (666, 64)}
rowsout = []
for f in files:
    d = json.load(open(f))
    V = [tuple(int(x) for x in r) for r in d['vectors']]
    v = len(V)
    n = len(V[0])
    canon = {tuple(x if next(y for y in r if y) > 0 else -x for x in r) for r in V}
    distinct = len(canon) == v
    if 'gram' in d:
        G0 = d['gram']
        assert len(G0) == n and rank_q(G0) == n and pos_def(G0)
        W = [[sum(r[i] * G0[i][j] for i in range(n)) for j in range(n)] for r in V]
        G = [[sum(a * b for a, b in zip(W[s], V[t])) for t in range(v)] for s in range(v)]
    else:
        div = d['div']
        G = [[0] * v for _ in range(v)]
        for s in range(v):
            for t in range(s, v):
                x = sum(a * b for a, b in zip(V[s], V[t]))
                assert x % div == 0
                G[s][t] = G[t][s] = x // div
    norms = all(G[t][t] > 0 for t in range(v))
    oz = all(G[s][t] == 0 or G[s][t] % 2 != 0 for s in range(v) for t in range(v) if s != t)
    T = rank_q([list(r) for r in V])
    rows = abar_rows(G)
    r2, h, inc = window(rows)
    k = r2 // 2
    sat = Fr(v, T * (2 ** k + 1))
    ex = EXPECT[d['kprime']]
    ok = distinct and norms and oz and (v, T) == ex and k == d['kprime'] and r2 == d['rank_mod2_gram'] and abs(float(sat) - d['saturation']) < 1e-12 and d['v'] == v and d['T'] == T
    x = Fr(h * T, v)
    xs = xstar(h)
    rowsout.append((k, d['name'], v, T, h, inc, sat, x, xs))
    check('L.%s' % d['name'], ok,
          "%s (k'=%d): v=%d distinct lines, T=%d, all products 0/odd, rank_F2 A-bar=%d, window h=%d%s, v/T=%.2f, saturation %s=%.4f; dense x=hT/v=%.3f vs break-even fit x*(h)=%.3f [RECORDED fit]%s"
          % (d['name'], k, v, T, r2, h, ' (even window, 1 in col A-bar)' if inc else '', v / T, sat, float(sat), float(x), float(xs), '' if xs <= 0 or x >= xs else '  BELOW x*'))
below = [r for r in rowsout if r[8] > 0 and r[7] < r[8]]
check('L.none-below', not below, 'no system in the table has dense x below the recorded break-even fit x*(h) (rows with x*(h) <= 0 are outside the fit)')
inscope = [r for r in rowsout if r[4] <= 13]
best = {}
for r in inscope:
    best[r[0]] = max(best.get(r[0], Fr(0)), r[6])
check('L.best-scope', best == {0: Fr(1, 2), 3: Fr(7, 9), 4: Fr(15, 17), 5: Fr(140, 11 * 33), 6: Fr(166, 13 * 65)},
      'best saturation per k\' for window h <= 13 in the saved table: %s' % ', '.join('k\'=%d: %.3f' % (k, float(s)) for k, s in sorted(best.items())))
# thresholds: required v/T and saturation to tie the recorded break-even fit x*(h) at window h (conditional on the RECORDED fit)
trow = []
for h in range(9, 14):
    k = h // 2
    need = Fr(h) / xstar(h)
    cap = Fr(2 ** k + (h % 2))
    trow.append((h, k, float(xstar(h)), float(need), int(cap), float(need / cap)))
check('L.thresholds', [round(r[5] * 100) for r in trow] == [98, 60, 66, 38, 42] and [r[4] for r in trow] == [17, 32, 33, 64, 65],
      'needed v/T = h/x*(h) and saturation vs the Lagrangian cap (2^(h//2) + [h odd]): ' + '; '.join('h=%d (k\'=%d): x*=%.4f, need v/T=%.2f of cap %d = %.1f%%' % (r[0], r[1], r[2], r[3], r[4], 100 * r[5]) for r in trow))
finish()
