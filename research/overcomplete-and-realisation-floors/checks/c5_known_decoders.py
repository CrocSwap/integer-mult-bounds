"""The floors of Corollary 3.4 are attained: explicit decoders and their exact dense-B costs (E8 72, E7 49, D6 30, D4 12, P112 64, P104 56),
and the trivial decoder (cost v) for E6 and D5.  Exact Fractions; standard library only.
Frame decoder of a unit with an orthogonal frame f_1..f_T spanning its space: p_j(t) = <r_t, f_j>, q_j(s) = <r_s, f_j>/<f_j, f_j>; then
M = sum_j p_j q_j^T is the Gram matrix of the live lines.  (P112 uses the frame of the removed lines.)"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from report import check, finish
from fractions import Fraction as Fr
from roots import *
from frames import units

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, '..', 'data', 'p104_frames.json'))); F0, F1, pairs = D['F0'], D['F1'], D['pairs']

def frame_decoder(live, frame_vecs):
    v = len(live); Br = b0rows(live); G = gram(live); cost = 0
    M = [[Fr(0)] * v for _ in range(v)]
    for f in frame_vecs:
        nf = dot(f, f); p = [dot(r, f) for r in live]
        for t in range(v):
            if p[t]:
                for s in range(v):
                    if p[s]: M[t][s] += Fr(p[t] * p[s], nf)
        R = [t for t in range(v) if p[t] != 0]; cost += blk(Br, R, R)
    return M == [[Fr(G[t][s]) for s in range(v)] for t in range(v)], cost

U = units(); L8 = UNITS['E8'][0]
for name, want in (('D4', 12), ('D6', 30), ('E7', 49), ('E8', 72)):
    L, T = U[name]; fr = bits(next(c for c in maximal_cliques(orth_graph(L)) if popcount(c) == T))
    ok, cost = frame_decoder(L, [L[i] for i in fr])
    check('c5.' + name, ok and cost == want, '%s: frame decoder with %d terms has M = Gram (zero on orthogonal pairs, nonzero diagonal) and dense-B cost %d' % (name, T, cost))
live112 = [L8[t] for t in range(120) if t not in set(F0)]
ok, cost = frame_decoder(live112, [L8[i] for i in F0])
check('c5.P112', ok and cost == 64, 'P112 (E8 minus a frame): removed-frame decoder has M = Gram and dense cost %d' % cost)
# P104: E8 minus two frames; terms (a_j, b_j) with a_j in F0, b_j in F1 (pairs from the #968 construction as recorded in data/p104_frames.json):
live104i = [t for t in range(120) if t not in set(F0) | set(F1)]; live104 = [L8[t] for t in live104i]; v = len(live104); Br = b0rows(live104); G = gram(live104)
M = [[sum(dot(live104[t], L8[x]) * dot(live104[s], L8[y]) for x, y in pairs) for s in range(v)] for t in range(v)]
okM = all(M[t][t] != 0 for t in range(v)) and all(M[t][s] == 0 for t in range(v) for s in range(v) if t != s and G[t][s] == 0)
cost = 0
for x, y in pairs:
    R = [i for i, t in enumerate(live104i) if dot(L8[t], L8[x]) != 0]; A = [i for i, t in enumerate(live104i) if dot(L8[t], L8[y]) != 0]
    cost += blk(Br, R, A)
check('c5.P104', okM and cost == 56, 'P104: the 8 frame-pair terms give a realisation M (zero on orthogonal pairs, nonzero diagonal; not the Gram matrix) of dense cost %d' % cost)
for name, v_ in (('E6', 36), ('D5', 20)):
    L, T = U[name]; Br = b0rows(L)
    cost = sum(blk(Br, [t], [t]) for t in range(len(L)))
    check('c5.' + name, len(L) == v_ and cost == v_, '%s: the trivial decoder (M = I, one single-entry term per line) costs %d = v; this equals the floor proved for the scaled-Gram realisations (M = I is a different realisation)' % (name, cost))
finish()
