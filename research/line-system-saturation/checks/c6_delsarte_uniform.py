"""CHECKED (exact): (1) Delsarte linear-programming cap for the D16+ construction: an exact rational DUAL certificate (derived by solving a 6x6 system in Fractions, then verified
feasible) bounds the antipodal binary codes of length 16 with distances in S = {2,6,10,14} u {8,16}: at most 317 spinor lines, so roots + spinors <= 240 + 317 = 557.
(2) Theorem G arithmetic: which (k', m) admit a uniform-angle saturated system (lambda^2 = 2^(k'-1) m a perfect square), the known cases D4 / D6 / E7, and the common-neighbour counts
of the 510-vertex and 1023-vertex signed graphs."""
import os, sys, itertools
from math import comb, isqrt
from fractions import Fraction as Fr
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from report import check, finish
from units import UNITS, gram
from sympl import bf


def K(n, k, i):
    return sum((-1) ** j * comb(i, j) * comb(n - i, k - j) for j in range(k + 1))


# --- Krawtchouk identity K_k(d(x,y)) = sum_{wt u = k} (-1)^{u.(x+y)}  (n = 6, all pairs), and Delsarte inequalities on a real code, RM(1,4)
n6 = 6
ok = all(K(n6, k, bin(z).count('1')) == sum((-1) ** (bin(u & z).count('1')) for u in range(1 << n6) if bin(u).count('1') == k) for z in range(1 << n6) for k in range(n6 + 1))
g = [0xFFFF, 0xFF00, 0xF0F0, 0xCCCC, 0xAAAA]
rm = {0}
for gen in g:
    rm |= {x ^ gen for x in rm}
dd = {}
for a in rm:
    for b in rm:
        d = bin(a ^ b).count('1')
        dd[d] = dd.get(d, 0) + 1
A = {d: Fr(c, len(rm)) for d, c in dd.items()}
delsarte_ok = all(sum(A[d] * K(16, k, d) for d in A) >= 0 for k in range(17))
check('D.krawtchouk', ok and len(rm) == 32 and set(A) == {0, 8, 16} and delsarte_ok,
      'Krawtchouk identity verified for n=6 on all (word, k); Delsarte inequalities sum_i A_i K_k(i) >= 0 hold for all k=0..16 on the real code RM(1,4) (32 words, distance distribution %s)' % dict(sorted(A.items())))

# --- exact dual certificate
n = 16
S = [2, 6, 8, 10, 14, 16]
supp = [2, 3, 5, 6, 7, 8]            # dual support found from a floating-point LP; the multipliers below are recomputed exactly
M = [[Fr(-K(n, k, i)) for k in supp] + [Fr(1)] for i in S]
for c in range(6):
    p = next(r for r in range(c, 6) if M[r][c] != 0)
    M[c], M[p] = M[p], M[c]
    iv = 1 / M[c][c]
    M[c] = [x * iv for x in M[c]]
    for r in range(6):
        if r != c and M[r][c] != 0:
            f = M[r][c]
            M[r] = [a - f * b for a, b in zip(M[r], M[c])]
y = {k: M[i][6] for i, k in enumerate(supp)}
feas = all(sum(y[k] * -K(n, k, i) for k in y) >= 1 for i in S) and all(v >= 0 for v in y.values())
bound = 1 + sum(y[k] * K(n, k, 0) for k in y)
# proof of the bound: sum_{i in S\0}A_i <= sum_i A_i (-sum_k y_k K_k(i)) = -sum_k y_k sum_i A_i K_k(i) <= sum_k y_k K_k(0)
words = int(bound)           # floor
lines = (words - words % 2) // 2
check('D.dual', feas and bound == Fr(18432, 29) and lines == 317,
      'exact dual y>=0 on k=%s: y=%s; for every i in S, sum_k y_k(-K_k(i)) >= 1; so |C| <= 1 + sum_k y_k K_k(0) = %s = %.4f; C antipodal (even size) => |C| <= %d => at most %d spinor lines'
      % (supp, {k: str(v) for k, v in y.items()}, bound, float(bound), words - words % 2, lines))
need = Fr(17 * 16) / (Fr(5385, 10000) - Fr(1495, 100000) * 8)
check('D.cap', 240 + lines == 557 and 240 + lines < need and 16 * 15 == 240,
      "D16+ family: 16*15 = 240 root lines + <= %d spinor lines = %d < %.1f = h T / x*(h) at h=17, T=16 (x* is the RECORDED repo fit); this cap is for roots+spinors of D16+ only" % (lines, 240 + lines, float(need)))

# --- Theorem G arithmetic
sols = []
for k in range(1, 10):
    for m in range(1, 51):
        l2 = 2 ** (k - 1) * m
        if isqrt(l2) ** 2 == l2:
            sols.append((k, m, isqrt(l2)))
m1 = [(k, l) for k, m, l in sols if m == 1]
check('G.table', [k for k, _ in m1] == [1, 3, 5, 7, 9] and (4, 2, 4) in sols and (2, 2, 2) in sols and (1, 4, 2) in sols and (3, 1, 2) in sols and (5, 1, 4) in sols
      and not any(k == 4 and m == 1 for k, m, _ in sols),
      "lambda^2 = 2^(k'-1) m a perfect square (k'<=9, m<=50): m=1 exactly for odd k' = 1,3,5,7,9 (lambda = %s); k'=4 needs m in %s; D4 (k'=1,m=4), D6 (2,2), E7 (3,1) satisfy it with lambda = 2"
      % ([l for _, l in m1], [m for k, m, _ in sols if k == 4]))
for nm, (k, m) in (('D4', (1, 4)), ('D6', (2, 2)), ('E7', (3, 1))):
    L, T = UNITS[nm]
    G = gram(L)
    unif = all(G[t][t] == 2 and G[t][s] in (0, 1, -1) for t in range(len(L)) for s in range(len(L)) if t != s)
    lam = 2
    N = 4 ** k - 1
    trace0 = lam * 2 ** k * (m * (2 ** k - 1)) - lam * (N * m - m * (2 ** k - 1)) == 0
    check('G.known-' + nm, unif and len(L) == N * m and T == m * (2 ** k - 1) and trace0 and 2 ** k * lam ** 2 == 2 ** (2 * k - 1) * m,
          '%s: all non-orthogonal pairs have |cos| = 1/2 = 1/lambda, v = m(4^k\'-1) = %d, T = m(2^k\'-1) = %d, tr S = 0 for spectrum {2^k\' lambda (x T), -lambda (x v-T)}, degree 2^(2k\'-1) m = 2^k\' lambda^2' % (nm, len(L), T))


# --- 510-vertex (k'=4, m=2) and 1023-vertex (k'=5, m=1) signed-graph counts
def counts(k, m):
    N = 4 ** k - 1
    nb = []
    for p in range(1, N + 1):
        mm = 0
        for q in range(1, N + 1):
            if bf(p, q, k):
                mm |= 1 << (q - 1)
        nb.append(mm)
    # doubled graph: vertex (p, j); neighbours = all copies of points q with b(p,q)=1
    big = []
    for p in range(N):
        row = 0
        for q in range(N):
            if (nb[p] >> q) & 1:
                for j in range(m):
                    row |= 1 << (q * m + j)
        big.append(row)
    seen = {}
    V = N * m
    for u in range(V):
        for w in range(u + 1, V):
            typ = 'twin' if u // m == w // m else ('adj' if (nb[u // m] >> (w // m)) & 1 else 'nonadj')
            seen.setdefault(typ, set()).add((big[u // m] & big[w // m]).bit_count())
    return seen, big[0].bit_count()


for (k, m, lam, label) in ((4, 2, 4, '510-vertex'), (5, 1, 4, '1023-vertex')):
    seen, deg = counts(k, m)
    a = (2 ** k - 1) * lam           # S^2 = a S + b I
    b = 2 ** k * lam * lam
    adj = seen['adj'].pop()
    non = seen['nonadj'].pop()
    tw = seen.get('twin', {None}).pop()
    agree, dis = Fr(adj + a, 2), Fr(adj - a, 2)
    ok = deg == b and len(seen['adj']) == len(seen['nonadj']) == 0 and agree.denominator == 1 and dis >= 0
    check('G.%s' % label, ok,
          "%s signed graph (k'=%d, m=%d, lambda=%d): S^2 = %d S + %d I, degree %d (= b); common neighbours: adjacent %d (signed sum +-%d: %d agree / %d disagree), non-adjacent distinct %d (signed sum 0), twins %s (signed sum 0)"
          % (label, k, m, lam, a, b, deg, adj, a, agree, dis, non, tw if tw is not None else 'none (m=1)'))
finish()
