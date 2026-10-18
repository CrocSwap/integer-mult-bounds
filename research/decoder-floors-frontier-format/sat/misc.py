"""Registry of the smaller SAT instances: EDGE E1a (coordinate block N(f) of P112 has fitting minrank 8 for every admissible B) and the C4.1 clique-hitting
bounds on punctures.  Standard library only; DIMACS text is a deterministic function of the name."""
import os, sys, functools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
from units import *
from satgen import fitting_cnf, clique_in, nonorth_graph
import hitting as H

@functools.lru_cache(maxsize=None)
def edge_instance(i, r):
    """rank <= r admissible B on the block B[N(f_i), N(f_i)] of P112 (f_i = i-th removed root); gauge clique = largest non-orthogonal clique in N(f_i)"""
    L = sub(P112_IDX); f = F0[i]
    N = [t for t in range(len(L)) if dot(L[t], E8[f]) != 0]
    adj = nonorth_graph(L); C = clique_in(adj, sum(1 << t for t in N))
    return fitting_cnf(L, N, N, r, C[:r], fixV=False), N, C

def registry():
    R = {}
    for i in range(8): R['edge_N%d_r7' % i] = dict(expect='UNSAT', slow=False)
    R['edge_N0_r8'] = dict(expect='SAT', slow=False)
    R['hit_k7_z13'] = dict(expect='UNSAT', slow=False); R['hit_k7_z14'] = dict(expect='SAT', slow=False)
    R['tri_keep11'] = dict(expect='UNSAT', slow=False); R['tri_keep10'] = dict(expect='SAT', slow=False)
    for k, z in ((6, 22), (5, 31), (4, 37)):
        R['hit_k%d_z%d' % (k, z)] = dict(expect='UNSAT', slow=True)
    return R

def dimacs_of(name):
    if name.startswith('edge_N'):
        i = int(name[6]); r = int(name.split('_r')[1]); return edge_instance(i, r)[0].dimacs()
    if name.startswith('hit_k'):
        k, z = name[5:].split('_z'); nv, cl, _ = H.hit_cnf(int(k), int(z)); return H.dimacs(nv, cl)
    if name.startswith('tri_keep'):
        nv, cl, _ = H.tri_cnf(int(name[8:])); return H.dimacs(nv, cl)
    raise KeyError(name)

def check_model(name, pos):
    """SAT models: edge_N0_r8 -> decode U,V and check B = U V^T is admissible on the block; hit_*: the hitting set of the model hits every clique and has <= z lines;
    tri_keep10: the kept set is triangle-free of size >= 10."""
    if name.startswith('edge_N'):
        i = int(name[6]); r = int(name.split('_r')[1]); c, N, C = edge_instance(i, r); L = sub(P112_IDX)
        ent = lambda t, s: sum(((u in pos) & (w in pos)) for u, w in zip(c.U[t], c.V[s])) & 1
        return all(ent(t, t) == 1 for t in N) and all(ent(t, s) == 0 for t in N for s in N if t != s and dot(L[t], L[s]) != 0)
    L, R = H.region(); idx = {t: j + 1 for j, t in enumerate(R)}
    if name.startswith('hit_k'):
        k, z = name[5:].split('_z'); k, z = int(k), int(z); D = [t for t in R if idx[t] in pos]
        return len(D) <= z and all(any(t in D for t in cl) for cl in H.cliques(L, R, k))
    if name.startswith('tri_keep'):
        keep = int(name[8:]); K = [t for t in R if idx[t] in pos]
        return len(K) >= keep and not any(all(t in K for t in tr) for tr in H.cliques(L, R, 3))
    raise KeyError(name)
