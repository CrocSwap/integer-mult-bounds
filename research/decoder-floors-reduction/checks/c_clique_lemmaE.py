"""BATCH17 Lemma E, clique part (exact Fractions, standard library): the 9-term digon clique for GL(9) charts.
Slots = the 72 ordered pairs (i, j), i != j (arc i -> j).  Term j has a_j = 1 on {(i,j)} (out class O_j), c_j = K_jk = -1 on {(j,k)} (in class I_j);
N = sum_j a_j c_j^T, E = I - N.  Claims: K = I - 11^T (9x9) has corank(I-K) = 8; rank E = 64; col E meets span(O_j) trivially and row E meets span(I_i) trivially.
(The explicit GL(9, F2) charts realising the 72 arcs are glclique.py of the card: RECORDED, evidence/batch/, not re-run.)"""
from fractions import Fraction as Fr
import itertools
ok = True
def chk(name, cond, extra=''):
    global ok
    print(('PASS ' if cond else 'FAIL ') + name + (' ' + extra if extra else ''), flush=True); ok &= bool(cond)
def rank(rows):
    M = [[Fr(x) for x in r] for r in rows]; r = 0
    if not M: return 0
    for c in range(len(M[0])):
        p = next((i for i in range(r, len(M)) if M[i][c] != 0), None)
        if p is None: continue
        M[r], M[p] = M[p], M[r]; pv = M[r][c]; M[r] = [x / pv for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] != 0:
                f = M[i][c]; M[i] = [x - f * y for x, y in zip(M[i], M[r])]
        r += 1
    return r
t = 9
K = [[(1 if i == j else 0) - 1 for j in range(t)] for i in range(t)]        # K = I - 11^T  (K_ij = -1 off-diagonal, K_ii = 0)
IK = [[(1 if i == j else 0) - K[i][j] for j in range(t)] for i in range(t)]
chk('E.1 K_ii = 0, K_ij = -1; corank(I - K) = 8 = t - 1', all(K[i][i] == 0 for i in range(t)) and t - rank(IK) == 8)
S = [(i, j) for i in range(t) for j in range(t) if i != j]; ix = {s: n for n, s in enumerate(S)}
n = len(S)
N = [[0] * n for _ in range(n)]
for j in range(t):
    for i in range(t):
        if i == j: continue
        for k in range(t):
            if k == j: continue
            N[ix[(i, j)]][ix[(j, k)]] += -1          # a_j(s_ij) * c_j(s_jk)
E = [[(1 if r == c else 0) - N[r][c] for c in range(n)] for r in range(n)]
rE = rank(E)
chk('E.2 rank(I - N) = 64 = 72 - 8 on the 72 arc slots', n == 72 and rE == 64, 'rank %d' % rE)
colE = [[E[r][c] for r in range(n)] for c in range(n)]       # columns of E as vectors: spans col E
def inter_dim(U, W):                                        # dim(span U cap span W) = rk U + rk W - rk(U cup W)
    return rank(U) + rank(W) - rank(U + W)
def unit(s): return [1 if x == s else 0 for x in range(n)]
O = {j: [unit(ix[(i, j)]) for i in range(t) if i != j] for j in range(t)}
I = {i: [unit(ix[(i, j)]) for j in range(t) if j != i] for i in range(t)}
chk('E.3 col E meets span(O_j) in 0 for all 9 out classes', all(inter_dim(E_ := [list(c) for c in colE], O[j]) == 0 for j in range(t)))
chk('E.3 row E meets span(I_i) in 0 for all 9 in classes', all(inter_dim([list(r) for r in E], I[i]) == 0 for i in range(t)))
raise SystemExit(0 if ok else 1)
