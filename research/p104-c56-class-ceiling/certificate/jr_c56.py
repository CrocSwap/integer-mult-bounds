# JS-RANK jr_c56: the C=56 rank-8-row class (F1/W2/HC4): 8 chains (z_k, z'_k), each a complete flag <z'> < ... < z^perp
# (descent mass 7 per chain, 56 total); M[t,s] = sum_k [tau_k(t) > g_k(s)] w_k[t] u_k[s] / g_kk, gather g_k(s) free in [0, sigma_k(s)].
# Flag encoded by a basis b_1=z',...,b_9 and its dual d_1..d_9 (d_9 = z): tau(t) = max{j: q_t.d_j=1} - 1, sigma(s) = min{j: b_j.q_s=1} - 2.
# Usage: jr_c56.py CFG KILLS.json OUT.cnf  -> CNF: some flags + gathers make every listed cell (t,s) AND every odd cell exactly zero,
# with every diagonal nonzero. Own code.
import sys, json, pickle, itertools
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import geo
from fractions import Fraction as Fr
G = geo.G120; U = geo.U; n = 104; Q = [U[t] for t in range(n)]; dot = geo.dot
cfgs = [c for c in pickle.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'f1cfgs.pkl'), 'rb')) if all(dot(U[z], U[zp]) == 0 for z, zp in c)]
def chains(ci):
    return [(U[z], U[zp], [int(G[t, z]) for t in range(n)], [int(G[s, zp]) for s in range(n)], int(G[z, zp])) for z, zp in cfgs[ci]]
def prodk(ch, k, t, s):
    z, zp, w, u, g = ch[k]; return Fr(w[t] * u[s], g) if w[t] and u[s] else 0
class CNF:
    def __init__(s): s.nv = 0; s.cl = []
    def new(s): s.nv += 1; return s.nv
    def xor(s, lits, rhs=None):          # returns var = XOR(lits) (lits are vars); or constrains XOR = rhs
        if not lits:
            if rhs is None: v = s.new(); s.cl.append([-v]); return v
            assert rhs == 0; return None
        acc = lits[0]
        for l in lits[1:]:
            v = s.new(); s.cl += [[-v, acc, l], [-v, -acc, -l], [v, -acc, l], [v, acc, -l]]; acc = v
        if rhs is not None: s.cl.append([acc] if rhs else [-acc]); return None
        return acc
    def AND(s, a, b):
        v = s.new(); s.cl += [[-v, a], [-v, b], [v, -a, -b]]; return v
    def OR(s, ls):
        v = s.new(); s.cl.append([-v] + ls); s.cl += [[v, -l] for l in ls]; return v
def build(ci, kills):
    ch = chains(ci); C = CNF(); need = {}
    cells = [tuple(c) for c in kills]
    zero = set(cells) | {(t, s) for t in range(n) for s in range(n) if t != s and dot(Q[t], Q[s])}   # odd cells must stay 0
    diag = [(t, t) for t in range(n)]
    cells = sorted(zero) + diag
    for (t, s) in cells:
        for k in range(8):
            if prodk(ch, k, t, s): need.setdefault(k, set()).add((t, s))
    live = {}
    for k in range(8):
        z, zp, w, u, g = ch[k]
        b = [[C.new() for p in range(9)] for i in range(9)]; d = [[C.new() for p in range(9)] for j in range(9)]
        for p in range(9):
            C.cl.append([b[0][p]] if zp >> p & 1 else [-b[0][p]]); C.cl.append([d[8][p]] if z >> p & 1 else [-d[8][p]])
        for i in range(9):
            for j in range(9):
                C.xor([C.AND(b[i][p], d[j][p]) for p in range(9)], 1 if i == j else 0)
        if k not in need: continue
        Ts = {}; Gs = {}
        for (t, s) in need[k]:
            if t not in Ts:
                x = [C.xor([d[j][p] for p in range(9) if Q[t] >> p & 1]) for j in range(9)]   # q_t . d_j
                Ts[t] = {m: C.OR([x[j] for j in range(m, 9)]) for m in range(1, 8)}         # tau >= m  <=> some j+1 >= m+1
            if s not in Gs:
                y = [C.xor([b[j][p] for p in range(9) if Q[s] >> p & 1]) for j in range(8)]   # b_{j+1} . q_s
                C.cl.append([-y[0]])                                                       # sigma >= 0 (b_1 = z')
                Gm = {m: C.new() for m in range(1, 8)}
                for m in range(1, 8):
                    if m > 1: C.cl.append([-Gm[m], Gm[m - 1]])
                    for jj in range(0, min(m + 1, 8)): C.cl.append([-Gm[m], -y[jj]])          # g >= m => b_1..b_{m+1} even to q_s
                Gs[s] = Gm
            live[k, t, s] = C.OR([C.AND(Ts[t][m], -Gs[s][m]) for m in range(1, 8)])
    for (t, s) in cells:
        ks = [k for k in range(8) if (k, t, s) in live]; vals = [prodk(ch, k, t, s) for k in ks]
        for mask in range(1 << len(ks)):
            if (sum(v for i, v in enumerate(vals) if mask >> i & 1) != 0) == (t != s):
                C.cl.append([(-live[ks[i], t, s] if mask >> i & 1 else live[ks[i], t, s]) for i in range(len(ks))])
    return C
if __name__ == '__main__':
    ci = int(sys.argv[1]); kills = json.load(open(sys.argv[2])); C = build(ci, kills)
    with open(sys.argv[3], 'w') as f:
        f.write(f'p cnf {C.nv} {len(C.cl)}\n')
        for c in C.cl: f.write(' '.join(map(str, c)) + ' 0\n')
    print(sys.argv[3], 'cells', len(kills), 'vars', C.nv, 'clauses', len(C.cl))
