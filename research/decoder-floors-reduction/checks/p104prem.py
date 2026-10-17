"""BATCH17 mixed-unit premises (Gram realisation): which label subspaces can a col-M support of P112 / P104 avoid?
Avoidable codim-r subspace W^perp <=> the live lines with a label outside ker(W) ... i.e. support span inside ker(h_1..h_r)
requires x != 0 orthogonal (over Q) to every root whose label has some h_i = 1; feasible iff those roots have rank < 8."""
import sys, itertools, numpy as np
sys.path.insert(0, '.')
import e8
from e8 import L, G
F1 = [e8.idx(v) for v in [(1,1,1,1,1,1,1,1),(1,1,1,1,-1,-1,-1,-1),(1,1,-1,-1,1,1,-1,-1),(1,1,-1,-1,-1,-1,1,1),
                           (1,-1,1,-1,1,-1,1,-1),(1,-1,1,-1,-1,1,-1,1),(1,-1,-1,1,1,-1,-1,1),(1,-1,-1,1,-1,1,1,-1)]]
def rank2(M):
    M = (np.array(M, dtype=np.uint8) % 2).copy(); r = 0
    for c in range(M.shape[1]):
        p = next((i for i in range(r, M.shape[0]) if M[i, c]), None)
        if p is None: continue
        M[[r, p]] = M[[p, r]]
        for i in range(M.shape[0]):
            if i != r and M[i, c]: M[i] ^= M[r]
        r += 1
        if r == M.shape[0]: break
    return r
def labels(live):
    B = ((1 + G) % 2)[np.ix_(live, live)]
    basis = []
    for t in range(len(live)):
        if rank2(B[basis + [t]]) == len(basis) + 1: basis.append(t)
    h = len(basis)
    # label of t = coefficients c with B[t] = c @ B[basis]
    Bb = B[basis]; lab = []
    for t in range(len(live)):
        for c in itertools.product((0, 1), repeat=h):
            if np.array_equal((np.array(c) @ Bb) % 2, B[t]): lab.append(c); break
    lab = np.array(lab, dtype=np.uint8); Gb = B[np.ix_(basis, basis)]
    assert np.array_equal((lab @ Gb @ lab.T) % 2, B)
    return lab, Gb, h
import json
reps = json.load(open('p104reps.json'))
units = [('P112', list(e8.P112)), ('P104', [t for t in e8.P112 if t not in F1])]
units += [('P104:' + k.split(',')[0][1:], [t for t in e8.P112 if t not in v]) for k, v in reps.items()]
for name, live in units:
    assert len(live) in (112, 104), (name, len(live))
    lab, Gb, h = labels(live); Lr = L[live].astype(float)
    fun = [np.array(f, dtype=np.uint8) for f in itertools.product((0, 1), repeat=h) if any(f)]
    hit = {tuple(f): set(np.nonzero((lab @ f) % 2)[0]) for f in fun}
    av1 = [f for f in fun if np.linalg.matrix_rank(Lr[sorted(hit[tuple(f)])]) < 8]
    # codim-2: pairs of avoidable functionals whose span (f, g, f+g) is jointly avoidable
    av2 = []
    for a, b in itertools.combinations(av1, 2):
        S = hit[tuple(a)] | hit[tuple(b)]
        if np.linalg.matrix_rank(Lr[sorted(S)]) < 8: av2.append((a, b))
    # within-call pairing rank between avoidable hyperplanes ker(f) (out) and ker(g) (in): rank = 8 - [f, g dependent under pairing]
    # rho(ker f, ker g) over the dense pairing Gb: dim S - dim(S cap T^perp) computed directly
    def kerbasis(fs):
        K = [np.array(v, dtype=np.uint8) for v in itertools.product((0, 1), repeat=h) if all(int(v @ f) % 2 == 0 for f in fs)]
        return np.array(K)
    pr = {}
    for f in av1:
        for g in av1:
            pr.setdefault(rank2((kerbasis([f]) @ Gb @ kerbasis([g]).T) % 2), 0); pr[rank2((kerbasis([f]) @ Gb @ kerbasis([g]).T) % 2)] += 1
    print(f'{name}: label dim h={h}; avoidable hyperplane classes={len(av1)}; avoidable codim-2 subspaces={len(av2)}; '
          f'within-call out/in hyperplane pair ranks {pr}')
