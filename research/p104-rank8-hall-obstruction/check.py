#!/usr/bin/env python3
"""Exact checks for the 14-port Hall obstruction on P104.  Python 3.12, standard library only.

Run:  python3 -I -B research/p104-rank8-hall-obstruction/check.py
Marker: PASS_P104_RANK8_HALL_OBSTRUCTION

Input: the 104 ports of research/p104-designer-toolkit-v2/words/5561.json.gz (9-bit integers).
Mask: ports s != t are "forced zero" when their F2 dot product is 0 (the complex label pattern).
"""
import gzip
import itertools
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PORTS_FILE = HERE.parent / "p104-designer-toolkit-v2" / "words" / "5561.json.gz"


def require(ok, msg):
    if not ok:
        raise ValueError(msg)


ports = json.loads(gzip.decompress(PORTS_FILE.read_bytes()))["ports"]
n = len(ports)
dot = lambda a, b: bin(a & b).count("1") & 1
require(n == 104 and all(0 < p < 512 for p in ports) and len(set(ports)) == 104, "ports shape")
require(all(dot(p, p) == 1 for p in ports), "every port has odd weight")
Z = lambda s, t: s != t and dot(ports[s], ports[t]) == 0   # forced-zero pair
require(all(Z(s, t) == Z(t, s) for s in range(n) for t in range(n)), "mask symmetric")

K = [62, 63, 69, 74, 81, 86, 91, 99]
O = [57, 67, 68, 95, 100, 101]
EXPECT_A = {57: [62, 91], 67: [63, 99], 68: [62, 99], 95: [62, 63], 100: [62, 69], 101: [63, 69]}

# 1. the 8-clique of the forced-zero graph, maximal, and no 9-clique anywhere
require(all(Z(a, b) for a, b in itertools.combinations(K, 2)), "K is a forced-zero clique")
require(not any(all(Z(x, k) for k in K) for x in range(n) if x not in K), "K is a maximal clique")
adj = [{t for t in range(n) if Z(s, t)} for s in range(n)]
best = [0]
def bk(R, P, X):
    if not P and not X:
        best[0] = max(best[0], R); return
    u = max(P | X, key=lambda v: len(adj[v] & P))
    for v in list(P - adj[u]):
        bk(R + 1, P & adj[v], X & adj[v]); P = P - {v}; X = X | {v}
bk(0, set(range(n)), set())
require(best[0] == 8, "clique number of the forced-zero graph is 8, got %d" % best[0])
print("clique: K is an 8-clique, maximal; clique number of the forced-zero graph =", best[0])

# 2. the O-coordinate claims
A = {t: [k for k in K if not Z(t, k)] for t in O}
require(A == EXPECT_A, "A(T) sets: %r" % A)
require(set().union(*map(set, A.values())) == {62, 63, 69, 91, 99}, "5 available coordinates")
sharing = [(s, t) for s, t in itertools.combinations(O, 2) if set(A[s]) & set(A[t])]
require(len(sharing) == 11, "11 sharing pairs, got %d" % len(sharing))
for s, t in sharing:
    require(Z(s, t), "sharing pair is forced zero: %r" % ((s, t),))
    require(len(set(A[s]) & set(A[t])) == 1, "sharing pair shares exactly one coordinate")
print("O: A(T) =", A, "; 5 coordinates for 6 ports; %d sharing pairs, all forced zero, each sharing exactly one coordinate" % len(sharing))

# 3. k = 1, field-free support argument: T active at c means u_T[c] w_T[c] != 0 (needed for B_TT != 0).
# Two ports active at the same shared coordinate give B_ST = w_S[c] u_T[c] != 0 (the only term), contradicting the mask.
# So active coordinates must be pairwise distinct: a system of distinct representatives of A.
def sdr(sets):
    sets = list(sets)
    def go(i, used):
        if i == len(sets): return True
        return any(c not in used and go(i + 1, used | {c}) for c in sets[i])
    return go(0, frozenset())
require(not sdr(A[t] for t in O), "no system of distinct representatives for the 6 ports")
print("k=1, any field: no system of distinct representatives for A(57..101) (5 coordinates, 6 ports)")

# 4. k = 1 linear algebra over F_p, p = 2, 3, 7: gauge U_K = W_K = I, then search all (u_T, w_T)
# vectors on the 8 coordinates, B_ST = w_S . u_T = 0 on forced-zero pairs, B_TT != 0 for T in O.
def f_p_search(p, O=O):
    ip = lambda a, b: sum(x * y for x, y in zip(a, b)) % p
    unit = {k: tuple(int(i == j) for j in range(8)) for i, k in enumerate(K)}
    dom = {}
    for t in O:   # B_kT = u_T[k] and B_Tk = w_T[k] vanish when (t, k) is forced zero; B_TT != 0
        ok = [i for i, k in enumerate(K) if not Z(t, k)]
        rows = []
        for u in itertools.product(range(p), repeat=len(ok)):
            for w in itertools.product(range(p), repeat=len(ok)):
                fu, fw = [0] * 8, [0] * 8
                for i, a, b in zip(ok, u, w): fu[i], fw[i] = a, b
                if ip(fw, fu): rows.append((tuple(fu), tuple(fw)))
        dom[t] = rows
        # the gauge-fixed K ports pair with t as B_kT = u_T[k], B_Tk = w_T[k]
        for u, w in rows:
            for i, k in enumerate(K):
                if Z(t, k): require(ip(unit[k], u) == 0 and ip(w, unit[k]) == 0, "K-O mask")
    def go(i, dom):
        if i == len(O): return 1
        t = O[i]; total = 0
        for u, w in dom[t]:
            nd = dict(dom)
            for s in O[i + 1:]:
                if Z(s, t):
                    nd[s] = [(u2, w2) for u2, w2 in dom[s] if ip(w, u2) == 0 and ip(w2, u) == 0]
                    if not nd[s]: break
            else:
                total += go(i + 1, nd)
        return total
    return go(0, dom)
for p in (2, 3):
    cnt = f_p_search(p)
    require(cnt == 0, "F_%d: expected no solution, found %d" % (p, cnt))
    print("k=1, F_%d, rank 8 (gauge-fixed, asymmetric W,U): %d solutions on the 14 ports (UNSAT)" % (p, cnt))

# search control: the same search with port 101 left out (5 ports, 5 coordinates) must find solutions
O5 = [t for t in O if t != 101]
require(f_p_search(2, O5) > 0 and f_p_search(3, O5) > 0, "search control: 5-port subsystem is satisfiable")
print("search control: dropping port 101 leaves a satisfiable system over F_2 and F_3 (the search is not vacuous)")

# 5. rank-9 control: one extra coordinate lets the six O ports have distinct active coordinates.
# Port vectors over Z in dimension 9; the full 14x14 Gram B = W U^T must vanish on every forced-zero pair
# and be invertible on the diagonal.
def control():
    best_assign = None
    for extra in O:
        rest = [t for t in O if t != extra]
        for choice in itertools.product(*[A[t] for t in rest]):
            if len(set(choice)) == len(rest):
                best_assign = (extra, dict(zip(rest, choice))); break
        if best_assign: break
    require(best_assign is not None, "rank-9 control assignment exists")
    extra, ch = best_assign
    U = {k: [int(i == j) for j in range(9)] for i, k in enumerate(K)}
    for t in O:
        e = 8 if t == extra else K.index(ch[t])
        U[t] = [int(j == e) for j in range(9)]
    W = U
    B = {(s, t): sum(a * b for a, b in zip(W[s], U[t])) for s in K + O for t in K + O}
    for s in K + O:
        require(B[s, s] == 1, "diagonal")
        for t in K + O:
            if Z(s, t): require(B[s, t] == 0, "forced zero violated at %r" % ((s, t),))
    return extra, ch
extra, ch = control()
print("control: a symmetric dimension-9 realisation of the 14-port mask exists (port %d on the extra coordinate; %r on K positions)" % (extra, ch))
print("PASS_P104_RANK8_HALL_OBSTRUCTION")
