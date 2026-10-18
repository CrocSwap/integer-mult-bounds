"""CHECKED (exact): Theorem A (labels from the F2 rank of the non-orthogonality adjacency A-bar; B = J + A-bar is the Omega-Gram of u_t = (1, l_t)),
Theorem B (Lagrangian classes <= T; the bound v <= T(2^k'+1) and its equality case) and the saturation ladder D4 / D6 / E7 (100% or tight) and E8 (88%),
plus Theorem C (unions of generic orthonormal frames) and Theorem D(b) (real blow-up)."""
import os, sys, random
from fractions import Fraction as Fr
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from report import check, finish
from exact import rank_f2, rank_q
from units import UNITS, gram
from lines import abar_rows, alt_labels, window, parity
from sympl import lagrangians, bf
from rat import cayley

EXP = {'D4': (12, 4, 1), 'D5': (20, 5, 2), 'D6': (30, 6, 2), 'E6': (36, 6, 3), 'E7': (63, 7, 3), 'E8': (120, 8, 4)}   # v, T, k'
LAG = {}
for name, (L, T) in UNITS.items():
    G = gram(L)
    v = len(L)
    rows = abar_rows(G)
    ev, eT, ek = EXP[name]
    oz = all(((rows[t] >> s) & 1) == (G[t][s] % 2) for t in range(v) for s in range(v) if t != s)
    labels, k = alt_labels(rows)           # self-verifying factorisation A-bar = L^T b L
    r2, h, inc = window(rows)
    check('A.labels-' + name, v == ev and T == eT and k == ek and r2 == 2 * k and oz,
          '%s: v=%d T=%d, A-bar = G mod 2 off the diagonal: %s, rank_F2 A-bar = %d = 2k\' (k\'=%d), factorisation b(l_t,l_s) = A-bar_ts verified on all %d pairs' % (name, v, T, oz, r2, k, v * v))
    # Theorem A: B = J + A-bar = Omega(u_t,u_s), u_t = (1, l_t), Omega = 1 + b, on ALL pairs including t = s
    okB = all((1 ^ bf(labels[t], labels[s], k)) == (1 ^ ((rows[t] >> s) & 1)) for t in range(v) for s in range(v))
    want_h = 2 * k if inc else 2 * k + 1
    check('A.polar-' + name, okB and h == want_h,
          '%s: B = J + A-bar equals Omega(u_t,u_s) on all pairs; 1 in col(A-bar): %s; h = rank_F2(J + A-bar) = %d = %s' % (name, inc, h, '2k\'' if inc else '2k\'+1'))
    # Theorem B: class sizes over all Lagrangians
    Ls = LAG.setdefault(k, lagrangians(k))
    m = {}
    for l in labels:
        m[l] = m.get(l, 0) + 1
    assert 0 not in m
    sizes = [sum(m.get(p, 0) for p in Lg) for Lg in Ls]
    NL = len(Ls)
    dist = {}
    for s in sizes:
        dist[s] = dist.get(s, 0) + 1
    bound = T * (2 ** k + 1)
    tight = all(s == T for s in sizes)
    check('B.classes-' + name, max(sizes) <= T and sum(sizes) * (2 ** k + 1) == v * NL and v <= bound and tight == (v == bound),
          '%s: %d Lagrangians, class size <= T=%d (distribution %s), sum of class sizes = v*N_L/(2^k\'+1), v=%d <= T(2^k\'+1)=%d, equality iff every class is a full basis: %s; saturation %s' % (name, NL, T, dict(sorted(dist.items())), v, bound, tight, Fr(v, bound)))
    # tight frame: sum_t r r^T / (r.r) = (v/T) I   (exact)
    n = len(L[0])
    S = [[Fr(0)] * n for _ in range(n)]
    for r in L:
        nn = sum(x * x for x in r)
        for i in range(n):
            for j in range(n):
                S[i][j] += Fr(r[i] * r[j], nn)
    S2 = [[sum(S[i][a] * S[a][j] for a in range(n)) for j in range(n)] for i in range(n)]
    c = Fr(v, T)
    proj = all(S2[i][j] == c * S[i][j] for i in range(n) for j in range(n)) and sum(S[i][i] for i in range(n)) == v
    check('B.frame-' + name, proj and ((c == 2 ** k + 1) == tight),
          '%s: F := sum_t r_t r_t^T/|r_t|^2 satisfies F^2 = (v/T) F, tr F = v, so F = (v/T) x (orthogonal projection onto span, rank T) with v/T = %s; equals 2^k\'+1 iff saturated' % (name, c))

# Theorem C: F generic rational orthonormal frames (Cayley transforms) of Q^T
rng = random.Random(20261014)
for (T, F) in [(3, 3), (4, 3), (4, 5), (5, 5), (3, 7)]:
    vecs = []
    for f in range(F):
        O = cayley(T, rng)
        vecs += [tuple(O[i][j] for i in range(T)) for j in range(T)]      # columns of O
    v = len(vecs)
    G = [[sum(a * b for a, b in zip(x, y)) for y in vecs] for x in vecs]
    cross = all((G[a][b] != 0) == (a // T != b // T) for a in range(v) for b in range(v) if a != b)
    rows = abar_rows(G)
    r2, h, inc = window(rows)
    k = r2 // 2
    ok = cross and r2 == F - 1 and h == F and rank_q([list(x) for x in vecs]) == T and F == 2 * k + 1 and v == F * T
    check('C.frames-T%d-F%d' % (T, F), ok,
          '%d generic ONBs of Q^%d: all cross products nonzero, within-frame orthogonal, rank_F2 A-bar = %d (k\'=%d, F = 2k\'+1), h = %d = F, v = %d, v/T = %d, dense x = hT/v = %s, saturation %s' % (F, T, r2, k, h, v, F, Fr(h * T, v), Fr(v, T * (2 ** k + 1))))

# Theorem D(b): m = 2 real blow-up of E7: a_l (x) (cos th_l, sin th_l) and a_l (x) (-sin th_l, cos th_l), th_l with rational tan(th/2) = 1/(l+2)
L7, T7 = UNITS['E7']
G7 = gram(L7)
vecs = []
for l, a in enumerate(L7):
    t = Fr(1, l + 2)
    c, s = (1 - t * t) / (1 + t * t), 2 * t / (1 + t * t)
    for (p, q) in ((c, s), (-s, c)):
        vecs.append(tuple(Fr(x) * p for x in a) + tuple(Fr(x) * q for x in a))
G = [[sum(x * y for x, y in zip(a, b)) for b in vecs] for a in vecs]
ok = all((G[2 * l + i][2 * l2 + j] != 0) == (l != l2 and G7[l][l2] != 0) for l in range(63) for l2 in range(63) for i in range(2) for j in range(2) if (l, i) != (l2, j))
rows = abar_rows(G)
r2, h, inc = window(rows)
Tq = rank_q([list(x) for x in vecs])
check('D.blowup-E7x2', ok and Tq == 14 and r2 == 6 and h == 7 and len(vecs) == 126,
      'E7 blown up m=2 in Q^14: non-orthogonality pattern = A-bar(E7) (x) J_2 on all %d pairs, v=126, T=%d, rank_F2 A-bar = %d (k\'=3 unchanged), h = %d, v/T = 9 = 2^3+1 (saturated, as E7)' % (126 * 125 // 2, Tq, r2, h))
finish()
