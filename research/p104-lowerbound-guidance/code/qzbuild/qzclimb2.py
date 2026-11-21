# warm-started word-level climb (merge moves), parent solution reused as the initial point.
import sys, itertools, pickle, time
import numpy as np
from qzdrive import *
from qzclimb import val, placements
def inc_index(d):
    """map piece index (in pieces list) -> incidence index in design d"""
    out = {}; idx = 0; pi = 0
    # design events built by make_design: per position p: H (2 contacts) then pieces with place==p in list order
    return None
def warm_z(dpar, zpar, dnew, map_new_to_old, rng, noise=0.05):
    n = dpar.n; Vp, Wp, abp = dpar.unpack(zpar)
    V = np.zeros((dnew.m, n)); W = np.zeros((dnew.m, n))
    for e in range(dnew.m):
        o = map_new_to_old[e]
        if o is None: V[e] = rng.normal(size=n); W[e] = rng.normal(size=n)
        else: V[e] = Vp[o]; W[e] = Wp[o]
    z = np.concatenate([V.ravel(), W.ravel(), abp.ravel()])
    return z + noise*rng.normal(size=z.shape)
def build(n, k, masks, pieces, order, place):
    d = make_design(n, k, masks, pieces, order, place)
    # tag each incidence with ('c', host#, 0/1) or ('p', piece index)
    tags = []; h = 0
    for p in range(k+1):
        if p > 0: tags += [('c', h, 0), ('c', h, 1)]; h += 1
        for i in range(len(pieces)):
            if place[i] == p: tags.append(('p', i))
    return d, tags
def climb2(n, k, masks, pieces, order, place, z0=None, log=sys.stdout, maxsteps=30, tries=3):
    rng = np.random.default_rng(7)
    d, tags = build(n, k, masks, pieces, order, place)
    S = Sys(d)
    if z0 is None:
        ok, z, S, nr = try_design(d, tries=20, seed=1)
    else:
        z, nr = lm(S, z0, it=200); ok = nr < 1e-8
    print('start', ok, '%.2e' % nr, 'val %.3f' % val(n, k, masks, pieces), flush=True, file=log)
    if not ok: return None
    cur = (list(pieces), dict(place), d, tags, z)
    for step in range(maxsteps):
        P, pl, d, tags, z = cur
        cands = []
        for i, j in itertools.combinations(range(len(P)), 2):
            if P[i] & P[j]: continue
            U = P[i] | P[j]
            if not any(U <= set(M) for M in masks): continue
            cands.append((val(n, k, masks, [p for x, p in enumerate(P) if x not in (i, j)] + [U]), i, j, U))
        seen = set(); C2 = []
        for c in sorted(cands, key=lambda c: -c[0]):
            key = (tuple(sorted(P[c[1]])), tuple(sorted(P[c[2]])), pl[c[1]], pl[c[2]])
            if key in seen: continue
            seen.add(key); C2.append(c)
        moved = False
        for v, i, j, U in C2:
            keep = [x for x in range(len(P)) if x not in (i, j)]
            newP = [P[x] for x in keep] + [U]
            for p in placements(U, order, k):
                npl = {a: pl[x] for a, x in enumerate(keep)}; npl[len(newP)-1] = p
                dn, tn = build(n, k, masks, newP, order, npl)
                oldpos = {t: e for e, t in enumerate(tags)}
                mp = []
                for t in tn:
                    if t[0] == 'c': mp.append(oldpos[t])
                    elif t[1] == len(newP)-1: mp.append(oldpos[('p', i)])
                    else: mp.append(oldpos[('p', keep[t[1]])])
                Sn = Sys(dn); best = (1e9, None)
                for tr in range(tries):
                    zi = warm_z(d, z, dn, mp, rng, noise=0.02*(tr+1))
                    zz, nr = lm(Sn, zi, it=300)
                    if nr < best[0]: best = (nr, zz)
                    if nr < 1e-9 and abok(Sn, zz): break
                nr, zz = best; ok = nr < 1e-9 and abok(Sn, zz)
                print('  try', sorted(P[i]), sorted(P[j]), 'at', p, 'val %.3f' % v, ok, '%.2e' % nr, flush=True, file=log)
                if ok:
                    cur = (newP, npl, dn, tn, zz); moved = True; break
            if moved: break
        if not moved: break
        print('STEP', step, 'val %.3f' % val(n, k, masks, cur[0]), [sorted(p) for p in cur[0]], cur[1], flush=True, file=log)
        pickle.dump((n, k, masks, cur[0], order, cur[1], cur[4]), open('climb2_k%d_last.pkl' % k, 'wb'))
    return cur
