"""Deterministic local frame search; every accepted move preserves inclusions.

No optimality is claimed. The exact moment and literal word are checked after
selection. Prepared with OpenAI Codex assistance, Apache-2.0.
"""
from functools import lru_cache
from math import log
from lift115 import basis, perp, nondeg, contained, safe_subspace

@lru_cache(None)
def inside(A, B):
    return contained(A, B)

@lru_cache(None)
def intersection(A, B, h):
    return perp(basis(perp(A, h) + perp(B, h)), h)

@lru_cache(None)
def minimum(L, C, h):
    """Complete each radical direction with one dual vector from C."""
    while not nondeg(L):
        radical = intersection(L, perp(L, h), h)
        r = radical[0]
        y = next(x for x in C if (x & r).bit_count() & 1)
        L = basis(L + (y,))
    return L

def optimize(ops, frames, roots, h, v, triples, envelope, rounds=4, gauges=None):
    full = basis(1 << i for i in range(h))
    frames = {i: basis(F) for i, F in frames.items()}
    visits = {}; initial = {s:basis(F) for s,F in (gauges or {}).items()}
    for i, o in enumerate(ops):
        if o[0] == 'src':
            initial[o[1]] = (triples[o[2]-1],)
        else:
            for s in o[1:3]: visits.setdefault(s, []).append(i)
    neighbors = {}
    for s, events in visits.items():
        for j, i in enumerate(events):
            neighbors[i, s] = (events[j-1] if j else None,
                                events[j+1] if j+1 < len(events) else None)
    weight = [0] + [round(r*log(r)*10**9) for r in range(1, h+1)]
    changes = []
    for cycle in range(rounds):
        changed = 0; gain = 0
        for i in sorted(frames, reverse=bool(cycle % 2)):
            old = frames[i]; sides = []
            for s in ops[i][1:3]:
                prev, nxt = neighbors[i, s]
                sides.append((frames[prev] if prev is not None else initial.get(s, ()),
                              frames[nxt] if nxt is not None else basis(roots.get(s, full))))
            lower = basis(tuple(envelope(ops[i][3])) + sides[0][0] + sides[1][0])
            assert inside(lower, old)
            small = minimum(lower, old, h)
            candidates = [old, small]
            # A future cap may allow an earlier larger jump after neighbors move.
            upper = intersection(sides[0][1], sides[1][1], h)
            if len(upper) > len(old):
                extra = intersection(upper, perp(old, h), h)
                candidates.append(basis(old + safe_subspace(extra, ())))
            def score(F):
                d = len(F)
                return sum(weight[d-len(A)] + weight[len(B)-d] for A, B in sides)
            best = max(candidates, key=score)
            delta = score(best) - score(old)
            if delta > 0:
                assert nondeg(best) and all(inside(A, best) and inside(best, B) for A, B in sides)
                frames[i] = best; changed += 1; gain += delta
        changes.append(dict(pass_index=cycle, changed=changed, objective_gain= gain))
        print('frame search', changes[-1], flush=True)
        if not changed: break
    return {i: list(F) for i, F in frames.items()}, changes
