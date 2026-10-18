# Rank-8 clique rigidity, zero-pattern model (Boolean abstraction; every clause is a necessary condition).
# L' = E8 \ K (K = maximal clique rep of the given size). N rank 8 on L', N_tt != 0, N_ts = 0 for t perp s, other entries free.
# For every frame F inside L' (N[F,F] diagonal invertible, rank 8): N_us = sum_{i in T(u)∩T(s)} N_{u f_i} N_{f_i s} / N_{f_i f_i}.
# Variables z(u,s) (u != s non-orthogonal): "N_us = 0".  t(u,f,s) <-> !z(u,f) & !z(f,s)  (term nonzero).
# Clauses: u = s: some term nonzero; N_us = 0 (forced or z): number of nonzero terms != 1; N_us != 0: >= 1 nonzero term.
# Goal clause: some z true. UNSAT  =>  no extra zero on L' (iff pattern).
import sys, itertools, random
sys.path.insert(0, sys.argv[1])
from e8lib import E, N, G, O, frames
size = int(sys.argv[2]); nfr = int(sys.argv[3]); out = sys.argv[4]
NB = [set(s for s in range(N) if s != u and G[u][s] != 0) for u in range(N)]
# deterministic clique rep: greedy from line 0
def clique(size):
    for start in range(N):
        for order in range(200):
            rnd = random.Random(order); K = [start]
            for u in rnd.sample(range(N), N):
                if u not in K and all(G[u][k] != 0 for k in K) and len(K) < size: K.append(u)
            if len(K) == size and all(any(G[v][k] == 0 for k in K) for v in range(N) if v not in K): return sorted(K)
K = clique(size); L = [u for u in range(N) if u not in K]; Ls = set(L)
FR = frames(L); print('K', K, '|L|', len(L), 'frames inside', len(FR), flush=True)
rnd = random.Random(1); FRs = FR if nfr >= len(FR) else rnd.sample(FR, nfr)
if len(sys.argv) > 5:   # CEGAR: extra frame indices (into FR) from a file
    FRs = list(dict.fromkeys(FRs + [FR[int(x)] for x in open(sys.argv[5]).read().split()]))
var = {}
def v(key):
    if key not in var: var[key] = len(var) + 1
    return var[key]
cl = []
def Z(u, s): return v(('z', u, s))
def T(u, f, s):
    key = ('t', u, f, s)
    if key not in var:
        t = v(key); a = [] 
        for (p, q) in ((u, f), (f, s)):
            if p != q: a.append(Z(p, q))
        # t <-> AND(!a)
        for x in a: cl.append([-t, -x])
        cl.append([t] + a)
    return var[key]
for F in FRs:
    Fs = set(F)
    for u in L:
        if u in Fs: continue
        Tu = [f for f in F if G[u][f] != 0]
        for s in L:
            if s in Fs: continue
            I = [f for f in Tu if G[s][f] != 0]
            ts = [T(u, f, s) for f in I]
            if u == s: cl.append(ts); continue
            if G[u][s] == 0:
                for i, t in enumerate(ts): cl.append([-t] + [x for j, x in enumerate(ts) if j != i])
            else:
                z = Z(u, s)
                cl.append([z] + ts)
                for i, t in enumerate(ts): cl.append([-z, -t] + [x for j, x in enumerate(ts) if j != i])
# NZF (all frames inside L', not only the equation frames): at rank 8, M = M[:,F]M[F,F]^-1 M[F,:], so a row (column) vanishing on F
# vanishes entirely and M_ww = 0. Hence every off-frame w has a nonzero entry in row w and in column w at F.
for F in FR:
    Fs = set(F)
    for w in L:
        if w in Fs: continue
        Tw = [f for f in F if G[w][f] != 0]
        cl.append([-Z(w, f) for f in Tw]); cl.append([-Z(f, w) for f in Tw])
import os
if os.environ.get('NOGOAL') != '1': cl.append([var[k] for k in var if k[0] == 'z'])   # NOGOAL=1: negative control (must be SAT)
with open(out, 'w') as fh:
    fh.write('p cnf %d %d\n' % (len(var), len(cl)))
    for c in cl: fh.write(' '.join(map(str, c)) + ' 0\n')
import pickle; pickle.dump({k: i for k, i in var.items() if k[0] == "z"}, open(out + ".map", "wb"))
print('frames used', len(FRs), 'vars', len(var), 'clauses', len(cl), flush=True)
