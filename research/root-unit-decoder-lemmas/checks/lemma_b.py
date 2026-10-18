"""Lemma B (lift identity) -- instance checks.  usage: lemma_b.py   (reads ../lib only)
Claim: for every rational B' supported on supp(B) with nonzero diagonal, B' o M = diag(B'_tt M_tt) = sum_j D(p_j) B' D(q_j),
hence v <= sum_j rank_Q B'[R_j, A_j].  Rank is computed mod the prime 2^61-1, which is <= rank_Q, so a passing sum is a valid
lower bound for the Q-rank sum.  Part 1: random exact decoders (T = 3, 4) on small root units.  Part 2: the dyadic E6 / E8
decoders of ERR1, where sum_j rank_F2 B0[R_j,A_j] < v: every sampled lift B' still has sum_j rank_Q >= v.  Part 3: the Fano
matrix (illustration only)."""
import io, contextlib, os, random, sys
from fractions import Fraction as F
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
with contextlib.redirect_stdout(io.StringIO()):
    import ade
from dyadic import dyadic_decoder
PR = (1 << 61) - 1
def rank_mod(rows, p=PR):
    M = [[x % p for x in r] for r in rows]; r = 0
    if not M: return 0
    nc = len(M[0])
    for c in range(nc):
        piv = next((i for i in range(r, len(M)) if M[i][c]), None)
        if piv is None: continue
        M[r], M[piv] = M[piv], M[r]; inv = pow(M[r][c], p - 2, p)
        for i in range(r + 1, len(M)):
            if M[i][c]:
                f = M[i][c] * inv % p; M[i] = [(a - f * b) % p for a, b in zip(M[i], M[r])]
        r += 1
    return r
def block(Bp, R, A): return [[Bp[t][s] for s in A] for t in R]
def lift_check(M, P, Q, B, Bp, v, T):
    """M, P, Q: nested lists of numbers (int or Fraction); B 0/1; Bp integer lift.  Returns (identity_ok, qrank_sum, f2_sum)."""
    for t in range(v):
        assert Bp[t][t] != 0 and B[t][t] == 1
        for s in range(v):
            if t != s and Bp[t][s] != 0: assert B[t][s] == 1 and M[t][s] == 0
    ident = True
    for t in range(v):
        for s in range(v):
            lhs = Bp[t][s] * M[t][s]
            rhs = sum(P[t][j] * Bp[t][s] * Q[s][j] for j in range(T))
            want = Bp[t][t] * M[t][t] if t == s else 0
            ident = ident and lhs == rhs == want
    qs = fs = 0
    for j in range(T):
        R = [t for t in range(v) if P[t][j] != 0]; A = [t for t in range(v) if Q[t][j] != 0]
        qs += rank_mod(block(Bp, R, A)); fs += ade.f2rank(np.array(block(B, R, A), dtype=np.uint8)) if R and A else 0
    return ident, qs, fs
rng = random.Random(20261013)
# Part 1
n = bad = 0; nlow = 0
for nm, L in [('A3', ade.A(3)), ('D4', ade.D(4)), ('D5', ade.D(5)), ('A4', ade.A(4))]:
    G = np.rint(L @ L.T).astype(int); v = len(L); cnt = bl = 0
    for it in range(60):
        T = rng.choice((3, 4))
        while True:
            P = [[rng.choice((-1, 0, 1, 1)) for _ in range(T)] for _ in range(v)]; Q = [[rng.choice((-1, 0, 1, 1, 2)) for _ in range(T)] for _ in range(v)]
            M = [[sum(P[t][j] * Q[s][j] for j in range(T)) for s in range(v)] for t in range(v)]
            if all(M[t][t] != 0 for t in range(v)): break
        B = [[1 if t == s else int(G[t, s] == 0 and M[t][s] == 0 and rng.random() < 0.8) for s in range(v)] for t in range(v)]
        for tryb in range(3):
            Bp = [[(B[t][s] * (rng.choice((-3, -2, -1, 1, 2, 3)) if (tryb and (t != s or tryb == 2)) else 1)) for s in range(v)] for t in range(v)]
            ident, qs, fs = lift_check(M, P, Q, B, Bp, v, T)
            cnt += 1; bl += (not ident) or qs < v
    print(f"{nm} v {v} random decoders x lifts {cnt} violations {bl}"); n += cnt; bad += bl
print(f"PART1 instances {n} violations {bad}")
# Part 2
for nm, L in [('E6', ade.E6b()), ('E7', ade.E7()), ('E8', ade.E8())]:
    G, idx, P, Q = dyadic_decoder(L); v = len(L); T = len(idx)
    M = [[int(G[t, s]) for s in range(v)] for t in range(v)]
    B = [[int((1 + G[t, s]) % 2) for s in range(v)] for t in range(v)]
    for k, mode in enumerate(('B0 itself (0/1 lift)', 'random signed weights', 'random weights 1..5')):
        Bp = [[B[t][s] * (1 if k == 0 else (rng.choice((-3, -2, -1, 1, 2, 3)) if k == 1 else rng.randint(1, 5))) if (t != s) else 1 for s in range(v)] for t in range(v)]
        ident, qs, fs = lift_check(M, P, Q, B, Bp, v, T)
        print(f"{nm} v {v} T {T} lift {mode}: identity {ident} sum rank_Q >= {qs} >= v {qs >= v} | sum rank_F2 B0 blocks {fs} < v {fs < v}")
# Part 3: illustration only
pts = range(7); lines = [{0, 1, 2}, {0, 3, 4}, {0, 5, 6}, {1, 3, 5}, {1, 4, 6}, {2, 3, 6}, {2, 4, 5}]
N = [[1 if p in l else 0 for p in pts] for l in lines]
print(f"FANO incidence 7x7: rank_F2 {ade.f2rank(np.array(N, dtype=np.uint8))} rank_Q {rank_mod(N)} (illustration only)")
