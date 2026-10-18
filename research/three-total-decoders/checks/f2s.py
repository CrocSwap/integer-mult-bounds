"""Group G5: the F2S rowspace identity and small F2S configurations (fprime/PROOF.md 13, fleet/S2.md).
F2S = full-support points, two-support lines.  Identity: with W = rowspace(B), rho = dim W, w_j = dim(W cap F2^{C_j}) (C_j = columns with q_j = 0),
cost = sum_j r_j = 3 rho - sum_j w_j >= 2 rho  for EVERY B (w_j computed here by counting the elements of W, not by rank-nullity)."""
import sys, os, random, itertools
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from kit import *
from satlib import cost_leq

rng = random.Random(21); vals = (-2, -1, 1, 2)
PF = [x for x in itertools.product(vals, repeat=3)]
Q2 = [x for x in itertools.product((-2, -1, 0, 1, 2), repeat=3) if sum(1 for c in x if c) == 2]
def f2s_config(v):
    P = []; Q = []
    while len(P) < v:
        if P and rng.random() < 0.9:
            s = rng.randrange(len(P)); t = rng.randrange(len(P))
            p = rng.choice([x for x in PF if dot(x, Q[s]) == 0] or PF); q = rng.choice([x for x in Q2 if dot(P[t], x) == 0] or Q2)
        else: p = rng.choice(PF); q = rng.choice(Q2)
        if dot(p, q): P.append(list(p)); Q.append(list(q))
    return P, Q
def rowspace_elems(B):
    v = len(B); basis = []
    for r in B:
        x = sum(b << s for s, b in enumerate(r))
        for b in basis: x = min(x, x ^ b)
        if x: basis.append(x)
    el = {0}
    for b in basis: el |= {w ^ b for w in el}
    return len(basis), el
ident = 0; ge2 = 0; n = 0; direct = 0; tot_inc = 0
for it in range(40):
    v = rng.randrange(6, 14); P, Q = f2s_config(v); R, A, free = setup(P, Q)
    zero = [[s for s in range(v) if Q[s][k] == 0] for k in range(3)]
    for rep in range(5):
        g = rng.getrandbits(len(free)) & rng.getrandbits(len(free)) if rep else (1 << len(free)) - 1
        B = tomat(g, free, v); rho, W = rowspace_elems(B)
        if rho > 12: continue
        w = [(sum(1 for x in W if x & ~sum(1 << s for s in zero[k]) == 0)).bit_length() - 1 for k in range(3)]
        br = blockranks(B, R, A); n += 1; ident += (sum(br) == 3 * rho - sum(w)); ge2 += (sum(br) >= 2 * rho); direct += (sum(w) <= rho)
    tot_inc += len(free)
print("F2S identity cost = 3 rho - sum_j w_j on %d (configuration, B) pairs (40 random F2S configurations, v 6-13, B random, sparse to full): holds in %d; cost >= 2 rho in %d; sum_j w_j <= rho (direct sum) in %d" % (n, ident, ge2, direct))
# small exact: random F2S configurations have cost >= v (UNSAT at v-1); tied_min is the sharp one
rng = random.Random(33); okc = 0; N = 8
for it in range(N):
    v = rng.randrange(6, 9); P, Q = f2s_config(v)
    okc += cost_leq(P, Q, v - 1) is None
print("F2S %d random F2S configurations (v 6-8): cost <= v-1 UNSAT (cost >= v) in %d" % (N, okc))
