"""Odd characteristic (Theorem 4): the odd graph on the 120 vectors is the orthogonality graph of the 120 root lines of E8;
the matrix O = <r,s>/2 has unit diagonal, zeros on adjacent pairs, rank <= 8. Hadamard step on random fitting matrices; controls."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import itertools, random
from common import *
rnd = random.Random(7)
M_ = load('e8_line_map.json')
V, R2 = M_['vectors'], M_['roots2']
req(sorted(V) == P120 and len(R2) == 120, 'the map is defined on the 120 vectors of weight 3 mod 4')
def is_root2(r):
    return (sorted(map(abs, r)) == [0] * 6 + [2, 2]) or (all(abs(x) == 1 for x in r) and sum(1 for x in r if x < 0) % 2 == 0)
req(all(is_root2(r) for r in R2), 'every r is an E8 root in doubled coordinates (+-2 in two places, or all +-1 with an even number of minus signs)')
ip = lambda r, s: sum(x * y for x, y in zip(r, s))   # = 4 <r, s>
req(all(ip(r, r) == 8 for r in R2), 'every root has norm 2 (doubled inner product 8)')
vals = {}
bad = 0
for i, j in itertools.combinations(range(120), 2):
    a = ip(R2[i], R2[j]); adj = dot(V[i], V[j])
    vals[a] = vals.get(a, 0) + 1
    bad += (adj == 1) != (a == 0)
req(bad == 0 and sorted(vals) == [-4, 0, 4], 'distinct lines: <r,s> = 0 exactly on the adjacent pairs (dot 1), and +-1 on the non-adjacent ones; no pair of lines coincides')
req(vals[0] == 120 * 63 // 2, 'each root is orthogonal to 63 others: %d adjacent pairs' % vals[0])

idx = {v: i for i, v in enumerate(V)}
SYS = {'P104': PORTS}
# P112 and P120 as in graph_counts
deleted = sorted(set(P120) - set(PORTS))
frames = [c for c in maximal_cliques(deleted, lambda a, b: dot(a, b) == 1) if len(c) == 8]
SYS['P112'] = list(PORTS) + list(frames[0]); SYS['P120'] = list(P120)
for name, S in SYS.items():
    n = len(S)
    Rm = [R2[idx[v]] for v in S]
    O8 = [[ip(a, b) for b in Rm] for a in Rm]       # 8 * O = 4 <r,s> * 2 ... (integer matrix, entries 8, 0, +-4)
    req(rank_q(Rm) == 8, '%s: root matrix %d x 8 has rank 8 over Q, so rank O <= 8' % (name, n))
    ranks = {p: rank_mod(O8, p) for p in (3, 5, 7, 101)}
    req(all(r == 8 for r in ranks.values()), '%s: O has rank %s over F_3, F_5, F_7, F_101 (at most 8, as it factors through 8 dimensions)' % (name, tuple(ranks.values())))
    req(all(O8[i][i] == 8 for i in range(n)) and all(O8[i][j] == 0 for i in range(n) for j in range(n) if i != j and dot(S[i], S[j]) == 1),
        '%s: O has unit diagonal and zeros on all adjacent pairs' % name)
    # Hadamard step on a random matrix fitting G over F_101, k = 2
    p, k = 101, 2
    Mrand = [[0] * (n * k) for _ in range(n * k)]
    for a in range(n):
        for b in range(n):
            if a == b:
                for i in range(k): Mrand[a * k + i][b * k + i] = 1
            elif dot(S[a], S[b]) == 1:
                for i in range(k):
                    for j in range(k): Mrand[a * k + i][b * k + j] = rnd.randrange(p)
    inv8 = pow(8, -1, p)
    N = [[Mrand[a * k + i][b * k + j] * O8[a][b] * inv8 % p for b in range(n) for j in range(k)] for a in range(n) for i in range(k)]
    eye = [[int(x == y) for y in range(n * k)] for x in range(n * k)]
    req(N == eye, '%s: M o (O tensor J_2) is the %d x %d identity for a random M fitting G over F_101' % (name, n * k, n * k))
    req(n * k <= 8 * rank_mod(Mrand, p), '%s: so %d <= 8 rank M, i.e. rank M / k >= %s (check at a random M: rank M = %d)' % (name, n * k, n / 8, rank_mod(Mrand, p)))
# controls
Rbad = [list(r) for r in R2]
Rbad[5] = list(R2[17])
badc = sum(1 for i, j in itertools.combinations(range(120), 2) if (dot(V[i], V[j]) == 1) != (ip(Rbad[i], Rbad[j]) == 0))
req(badc > 0, 'control: replacing one root by another breaks the adjacency correspondence (%d pairs wrong)' % badc)
S = PORTS; n = 104
O8 = [[ip(R2[idx[a]], R2[idx[b]]) for b in S] for a in S]
i0, j0 = next((i, j) for i in range(n) for j in range(n) if i != j and dot(S[i], S[j]) == 1)
O8[i0][j0] = 4
req(not all(O8[i][j] == 0 for i in range(n) for j in range(n) if i != j and dot(S[i], S[j]) == 1), 'control: one planted nonzero entry of O on an adjacent pair is detected')
req(all(x % 2 == 0 for r in [[ip(R2[idx[a]], R2[idx[b]]) for b in S] for a in S] for x in r), 'control: modulo 2 the integer matrix 8 O is zero; in characteristic 2 the division by 2 behind O does not exist, and the argument is unavailable (a rank-9 representation exists there)')
finish('PASS_ODDCHAR')
