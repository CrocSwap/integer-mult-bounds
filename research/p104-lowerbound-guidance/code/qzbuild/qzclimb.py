# QZBUILD word-level climb: from a buildable design, try merging idle incidences (event-form invoice rises),
# test each candidate (all placements in a small set) with the word-level solver; keep the first feasible.
import sys, time, json, itertools, pickle
from qzdrive import *
def val(n, k, masks, pieces):
    return 104/k*(sum((8*len(M)+1)**S for M in masks) - sum((8*len(P))**S for P in pieces) - 2*k*8**S)
from qzcore import S
def placements(S_, order, k):
    pos = {t: i+1 for i, t in enumerate(order)}
    c = {0, k} | {pos[t] for t in S_} | {pos[t]-1 for t in S_}
    return sorted(c)
def climb(n, k, masks, pieces, order, place, tries=6, log=None, maxsteps=20):
    cur = (list(pieces), dict(place))
    d = make_design(n, k, masks, cur[0], order, cur[1]); ok, z, Ssys, nr = try_design(d, tries=3*tries, seed=1)
    print('start', ok, '%.2e' % nr, 'val %.3f' % val(n, k, masks, cur[0]), flush=True, file=log)
    if not ok: return None
    best = (val(n, k, masks, cur[0]), cur, z)
    for step in range(maxsteps):
        P, pl = cur; cands = []
        for i, j in itertools.combinations(range(len(P)), 2):
            if P[i] & P[j]: continue
            U = P[i] | P[j]
            if not any(U <= set(M) for M in masks): continue
            newP = [p for x, p in enumerate(P) if x not in (i, j)] + [U]
            cands.append((val(n, k, masks, newP), i, j, U, newP))
        # dedupe by multiset
        seen = set(); C2 = []
        for c in sorted(cands, key=lambda c: -c[0]):
            key = tuple(sorted(tuple(sorted(p)) for p in c[4]))
            if key in seen: continue
            seen.add(key); C2.append(c)
        moved = False
        for v, i, j, U, newP in C2:
            oldpl = [pl[x] for x in range(len(P)) if x not in (i, j)]
            for p in placements(U, order, k):
                npl = {x: q for x, q in enumerate(oldpl)}; npl[len(newP)-1] = p
                d = make_design(n, k, masks, newP, order, npl)
                ok, z, Ssys, nr = try_design(d, tries=tries)
                print('  try', sorted(U), 'at', p, 'val %.3f' % v, ok, '%.2e' % nr, flush=True, file=log)
                if ok:
                    cur = (newP, npl); best = (v, cur, z); moved = True; break
            if moved: break
        if not moved: break
        print('STEP', step, 'val %.3f' % best[0], [sorted(p) for p in cur[0]], cur[1], flush=True, file=log)
    return best
