"""Lemma OC (exact numerical instances), the D5 floor for every number of terms, and the finite facts used by its proof.
Standard library only; Fractions."""
import sys, os, random, itertools
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from report import check, finish
from fractions import Fraction as Fr
from dirs import *

def matmul(A, B): return [[sum(a * b for a, b in zip(r, c)) for c in zip(*B)] for r in A]
def tr(A): return [list(r) for r in zip(*A)]
def inv(A):
    n = len(A); M = [[Fr(x) for x in r] + [Fr(int(i == j)) for j in range(n)] for i, r in enumerate(A)]
    for c in range(n):
        p = next(r for r in range(c, n) if M[r][c] != 0); M[c], M[p] = M[p], M[c]
        pv = M[c][c]; M[c] = [x / pv for x in M[c]]
        for r in range(n):
            if r != c and M[r][c] != 0:
                f = M[r][c]; M[r] = [x - f * y for x, y in zip(M[r], M[c])]
    return [r[n:] for r in M]
def ident(n): return [[Fr(int(i == j)) for j in range(n)] for i in range(n)]
def sub(A, B): return [[a - b for a, b in zip(r, s)] for r, s in zip(A, B)]

random.seed(20261014)
def random_decomposition(T, m):
    """X, Y in Q^{T x m} with X Y^T = I_T: Y^T = X^T (X X^T)^{-1} + (I - X^T (X X^T)^{-1} X) W"""
    while True:
        X = [[Fr(random.randint(-5, 5)) for _ in range(m)] for _ in range(T)]
        try: G = inv(matmul(X, tr(X)))
        except StopIteration: continue
        Y0 = matmul(tr(X), G)                                    # m x T,  X Y0 = I
        W = [[Fr(random.randint(-5, 5)) for _ in range(T)] for _ in range(m)]
        Pm = sub(ident(m), matmul(Y0, X))                        # projector onto ker X
        Yt = [[a + b for a, b in zip(r, s)] for r, s in zip(Y0, matmul(Pm, W))]   # Y^T
        return X, Yt

ok_idem = ok_trace = ok_sq = ok_rank1 = True; ninst = 0
for (T, m) in [(2, 2), (3, 3), (4, 4), (3, 4), (4, 5), (5, 6), (6, 7), (5, 7), (6, 8), (4, 7)]:
    for _ in range(12):
        X, Yt = random_decomposition(T, m); ninst += 1
        assert matmul(X, Yt) == ident(T)                             # X Y^T = I  (Yt = Y^T)
        K = matmul(Yt, X)                                            # K_ij = <y_i, x_j>
        Pi = sub(ident(m), K)
        ok_idem &= matmul(K, K) == K and matmul(Pi, Pi) == Pi
        ok_trace &= sum(K[i][i] for i in range(m)) == T and sum(Pi[i][i] for i in range(m)) == m - T
        ok_rank1 &= rank_q(K) == T and rank_q(Pi) == m - T
        if m == T: ok_sq &= K == ident(m)
        if m == T + 1:
            # Pi = u w^T, w^T u = 1, K_ij = -u_i w_j (i != j): off-diagonal of K is rank one
            ok_sq &= rank_q(Pi) == 1 and all(K[i][j] * K[k][l] == K[i][l] * K[k][j] for i in range(m) for j in range(m) for k in range(m) for l in range(m) if len({i, k}) == 2 and len({j, l}) == 2 and i != j and k != l and i != l and k != j)
check('c1.oc_idem', ok_idem, 'Lemma OC: K = Y^T X and I - K are idempotent on %d random exact instances (T,m up to 6,8)' % ninst)
check('c1.oc_trace', ok_trace and ok_rank1, 'Lemma OC: trace K = T, trace(I-K) = m-T, rank K = T, rank(I-K) = m-T on the same instances')
check('c1.oc_cases', ok_sq, 'Lemma OC: m = T gives K = I; m = T+1 gives I - K of rank one and a rank-one off-diagonal cross matrix')

# D5
L, T = UNITS['D5']; Br = b0rows(L)
dm = deficient_directions(L, T); X5 = sorted(set(dm.values()))
unit = sorted(tuple(int(i == j) for j in range(5)) for i in range(5))
check('c1.d5dirs', X5 == unit and len(dm) == 5, 'D5: the deficient directions are exactly the five coordinate axes e_1..e_5, one per deficient class')
check('c1.d5nspace', bilinear_space_dim(L, T) == 1, 'D5: the space of bilinear forms vanishing on orthogonal pairs is 1-dimensional')
rkt = {(a, b): blk(Br, support(L, unit[a]), support(L, unit[b])) for a in range(5) for b in range(5)}
check('c1.d5ranks', all(rkt[a, b] == (4 if a == b else 3) for a in range(5) for b in range(5)), 'D5: pair rank = 4 for matched (e_a, e_a), 3 for (e_a, e_b), a != b')
# rank of a pair with a non-deficient side is >= 4: via the F2 rank of B on random supports with one non-deficient direction (spot check) and Lemma 3.1 in the README
rng = random.Random(5); bad = 0
for _ in range(300):
    x = tuple(rng.choice([-2, -1, 0, 1, 2]) for _ in range(5)); y = tuple(rng.choice([0, 1, -1]) for _ in range(5))
    if not any(x) or not any(y): continue
    if x in unit or tuple(-c for c in x) in unit: continue        # x non-deficient (not +-e_a up to scale) -- scalings of e_a are caught below
    if sum(1 for c in x if c) == 1: continue
    if blk(Br, support(L, x), support(L, y)) < 4: bad += 1
check('c1.d5nondef', bad == 0, 'D5: 300 random pairs with a non-deficient row direction all have rank >= 4 (spot check of Lemma 3.1; proof in README)')
# the combinatorial core of the m = 6 argument: three terms (a_i, b_i) with a_i != b_i and b_i = a_j for all i != j do not exist
trip = [(a, b) for a in range(5) for b in range(5) if a != b]
found = [t for t in itertools.permutations(trip, 3) if all(t[i][1] == t[j][0] for i in range(3) for j in range(3) if i != j)]
check('c1.d5core', not found, 'D5: no three rank-3 terms (e_a_i, e_b_i), a_i != b_i, satisfy <y_i, x_j> != 0 for all i != j (checked over all %d ordered triples)' % (len(trip) * (len(trip) - 1) * (len(trip) - 2)))
finish()
