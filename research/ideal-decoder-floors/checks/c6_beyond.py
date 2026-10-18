"""CHECKED (exact): (a) §3.4 witnesses on E8 and the 2-adic carry of the dense E8 blocks; (b) the forced-minor bound omega_non on E8.
 (a) G = integer Gram (diagonal 2).  Z+ = (G o G + G)/2 and Z- = (G o G - G)/2 are integer matrices with odd diagonal, zero on orthogonal pairs, and
     G o C = 2 Z+ for the nonnegative coverage matrix C (C_tt = 3, C_ts = 2 where G_ts = +1, else 0); both have rank_Q = 44 = 36 + 8
     (rank G o G = 36 = dim Sym^2 Q^8).  The dense blocks B[D_j, D_j], D_j = {lines with coordinate j != 0} (78 lines), have 2-adic Smith invariants
     counted below: 9 units (F2 rank), 26 invariant factors exactly 2 (the 'carry'); over 8 coordinate terms: 72 and 208.
 (b) omega_non(S) = largest set of pairwise non-orthogonal lines in S (every principal minor of the dense B on such a set is the identity, hence
     the B-independent per-term bound r_j >= omega_non(D_j)): 8 on all of E8, 7 on N(a), 6 on N(a) n N(b) for every b != a (sizes 24 and 28)."""
import os
import sys
from collections import Counter
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from report import check, finish
from exact import rank_q
from units import E8, gram, bmasks

G = gram(E8)
n = 120
GG = [[G[a][b] * G[a][b] for b in range(n)] for a in range(n)]
Zp = [[(GG[a][b] + G[a][b]) // 2 for b in range(n)] for a in range(n)]
Zm = [[(GG[a][b] - G[a][b]) // 2 for b in range(n)] for a in range(n)]
integral = all((GG[a][b] + G[a][b]) % 2 == 0 for a in range(n) for b in range(n))
C = [[3 if a == b else (2 if G[a][b] == 1 else 0) for b in range(n)] for a in range(n)]
wit = (integral and all(G[a][b] * C[a][b] == 2 * Zp[a][b] for a in range(n) for b in range(n))
       and all(Zp[a][a] % 2 == 1 and Zm[a][a] % 2 == 1 for a in range(n))
       and all(Zp[a][b] == 0 == Zm[a][b] for a in range(n) for b in range(n) if a != b and G[a][b] == 0)
       and all(x >= 0 for row in C for x in row))
rg, rp, rm = rank_q(GG), rank_q(Zp), rank_q(Zm)
check('X1.rank44', wit and (rg, rp, rm) == (36, 44, 44),
      'E8: witness conditions hold (C >= 0, G o C = 2 Z+, odd diagonals, zero on orthogonal pairs): %s; rank G o G = %d, rank Z+ = %d, rank Z- = %d' % (wit, rg, rp, rm))

# 2-adic carry of the dense blocks (row operations on integer matrices mod 2^16; a unit pivot of minimal valuation each step)
K = 16
MOD = 1 << K


def val2(x):
    x %= MOD
    return K if x == 0 else (x & -x).bit_length() - 1


def smith_vals(A):
    A = [[x % MOD for x in r] for r in A]
    rows, cols = list(range(len(A))), list(range(len(A[0])))
    vals = []
    while rows and cols:
        best, bv = None, K
        for i in rows:
            for j in cols:
                if A[i][j]:
                    vv = val2(A[i][j])
                    if vv < bv:
                        bv, best = vv, (i, j)
                if bv == 0:
                    break
            if bv == 0:
                break
        if best is None:
            break
        i, j = best
        vals.append(bv)
        uinv = pow(A[i][j] >> bv, -1, MOD)
        for i2 in rows:
            if i2 != i and A[i2][j]:
                f = ((A[i2][j] >> bv) * uinv) % MOD
                for jj in cols:
                    A[i2][jj] = (A[i2][jj] - f * A[i][jj]) % MOD
        rows.remove(i)
        cols.remove(j)
    return vals


Br = bmasks(G)
tot0 = tot1 = 0
same = True
prof0 = None
for j in range(8):
    D = [t for t in range(n) if E8[t][j] != 0]
    blk = [[(Br[t] >> s) & 1 for s in D] for t in D]
    c = Counter(smith_vals(blk))
    tot0 += c[0]
    tot1 += c[1]
    prof = (len(D), tuple(sorted(c.items())))
    prof0 = prof0 or prof
    same &= prof == prof0
check('X1.carry', same and prof0[0] == 78 and tot0 == 72 and tot1 == 208 and dict(prof0[1])[0] == 9 and dict(prof0[1])[1] == 26,
      'E8 dense blocks (8 coordinate terms, each 78 lines): identical 2-adic profile %s per term; F2 rank total %d (= 8x9), carry (invariant factors exactly 2) total %d (= 8x26)' % (dict(prof0[1]), tot0, tot1))


# forced minors
def max_clique_nonorth(S):
    S = list(S)
    best = [0]
    adj = {a: set(b for b in S if b != a and G[a][b] != 0) for a in S}

    def rec(size, cand):
        if size > best[0]:
            best[0] = size
        if size + len(cand) <= best[0]:
            return
        # greedy colouring bound
        order = sorted(cand, key=lambda x: -len(adj[x] & cand))
        for i, c in enumerate(order):
            if size + len(order) - i <= best[0]:
                return
            rec(size + 1, (cand & adj[c]) - set(order[:i]))
    rec(0, set(S))
    return best[0]


a = 0
Na = [t for t in range(n) if t != a and G[a][t] != 0]
w_all = max_clique_nonorth(range(n))
w_Na = max_clique_nonorth(Na)
cnt = Counter()
for b in range(n):
    if b == a:
        continue
    Dset = [t for t in Na if G[b][t] != 0 and t != b]
    cnt[(G[a][b] % 2, len(Dset), max_clique_nonorth(Dset))] += 1
check('X1.forced', w_all == 8 and len(Na) == 56 and w_Na == 7 and dict(cnt) == {(0, 24, 6): 63, (1, 28, 6): 56},
      'E8: omega_non(all lines) = %d, |N(a)| = %d, omega_non(N(a)) = %d, omega_non(N(a) n N(b)) by (parity a.b, size): %s' % (w_all, len(Na), w_Na, dict(sorted(cnt.items()))))
finish()
