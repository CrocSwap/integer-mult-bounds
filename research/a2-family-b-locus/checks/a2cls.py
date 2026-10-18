# Class-level catalogue of an A2 triangle (UNIT env, A2TRI env), shared by mergedkill.py and iib.py.
# A column normal (f,1) kills a label class O iff (f,1).b_s = 0 for every s in O.  Off X, b_s = (r_s, -gamma_i (r_1.r_s)) on O_{u_i} (gamma_1 = 0); on X, b_{u_i} = (r_i, zeta_i).
# info(U) = (dim S, dim K, dim S - dim K) for the line set U off X, S = {(w, g2, g3): r_s.w = g_i (r_1.r_s) on U}, K = {g = 0}: the same quantity as unitcensus.py (the census is the recorded reference).
from a2lib import *
Xs = list(X)
p = 2**31 - 1
def rkp(M, n):
    # Rank mod p = 2^31 - 1.  EXACT here, not only a lower bound: every row used has integer entries (E8 roots doubled: entries <= 2 in absolute value; the g-entry r_1.s doubled twice: <= 4)
    # and at most 10 columns; a row has at most 8 doubled-root coordinates (squared norm 8) plus ONE g-entry (squared <= 16), so squared norm <= 24, and by Hadamard every minor has absolute
    # value <= 24^(10/2) = 24^5 < 8.0e6 < 2^31 - 1: a minor is nonzero mod p iff it is nonzero over Z.
    M = [[x % p for x in r] for r in M]; r = 0
    for c in range(n):
        q = next((i for i in range(r, len(M)) if M[i][c]), None)
        if q is None: continue
        M[r], M[q] = M[q], M[r]; inv = pow(M[r][c], p - 2, p); M[r] = [x * inv % p for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c]:
                f = M[i][c]; M[i] = [(a - f * b) % p for a, b in zip(M[i], M[r])]
        r += 1
    return r
Ri = [[int(2 * x) for x in r] for r in L]; r1i = Ri[Xs[0]]
idot = lambda a, b: sum(x * y for x, y in zip(a, b))
rowsg = {}
for s in range(v):
    if s in Xs: continue
    ii = [i for i in range(3) if idot(Ri[Xs[i]], Ri[s]) == 0]; i = ii[0]; g = [0, 0]; c = idot(r1i, Ri[s])
    if len(ii) > 1: assert c == 0
    if i == 1: g[0] = -c
    if i == 2: g[1] = -c
    assert max(abs(x) for x in Ri[s] + g) <= 4 and sum(1 for x in g if x) <= 1
    rowsg[s] = Ri[s] + g
def info(U):
    M = [rowsg[s] for s in U]; r = rkp(M, 10); rg = rkp([x[:8] for x in M], 8)
    dimS = 10 - r; dimK = 8 - rg; return dimS, dimK, dimS - dimK
single = {co: info([s for s in bits(w) if s not in Xs]) for co, w in cls.items()}
gen = [co for co in cls if single[co][2] == 2]                       # generic-gamma killable classes
Mg = [c for c in gen if len([t for t in bits(cls[c]) if t in Xs]) == 2]; Tg = [c for c in gen if c not in Mg]
assert len(gen) == 6 and len(Mg) == 3 and len(Tg) == 3
# row-deficient classes: |O cap X| >= 1 and rank r(O \ X) = 7
rowdef = []
for co, w in cls.items():
    Ob = bits(w)
    if not any(t in Xs for t in Ob): continue
    if rank([R[t] for t in Ob if t not in Xs], 8) == 7: rowdef.append(co)
# eta = 0 column killers (the "survivor" classes): r-rank 7 off X and every X-column orthogonal to the normal
colS = []
for co in rowdef:
    Ob = bits(cls[co]); n = nullspace([R[t] for t in Ob if t not in Xs], 8)[0]
    if all(dot(R[t], n) == 0 for t in Ob if t in Xs): colS.append(co)
assert not [c for c in colS if c in Tg]
def sup_avoid(cl): return [u for u in range(v) if not any((cls[a] >> u) & 1 for a in cl)]
