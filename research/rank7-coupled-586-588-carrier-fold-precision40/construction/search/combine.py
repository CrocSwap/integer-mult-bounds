"""combine.py -- PR2942 + frame-only end-frame lowerings: the four normal-45 pivots to V and the restored-helper groups A-D to their W.
Certified solver frames written back, report re-derived, PR2833 auditor; leave-one-out inside groups (base only)."""
import sys, json, copy, collections
sys.path.insert(0, 'S/r13/agents/A-extract/code')
from synth import *
BE = 2091300
V = (256, 128, 64, 35, 16, 11, 5)
G = {'V45': (V, [249, 251, 265, 267]),
     'A': ((256, 128, 64, 38, 20, 10, 1), [331, 450, 451, 508, 509]),
     'B': ((256, 128, 64, 34, 17, 11, 4), [299, 448, 449, 484, 485]),
     'C': ((256, 128, 64, 32, 19, 11, 6), [452, 453, 532, 533]),
     'D': ((256, 128, 64, 37, 21, 8, 3), [454, 455, 556, 557])}
def build(w, groups):
    x = copy.deepcopy(w)
    for g in groups:
        W, hs = G[g]
        for h in hs: x['helper_final'][str(h)] = list(W)
    return x
res = {}
for v in ('base', 'extra'):
    w = load(S / f'r14/inputs/WORD-2942-{v}.json.gz'); base = solve_frames(w, key=v)
    x = build(w, G); pf = bp.frame_profile(x, literal=False); d = pf['cost'] - base['cost']; k = sum(len(hs) for W, hs in G.values())
    wf = finish(bp.write_frames(x, pf)); ok, msg, rep = audit(wf)
    dp = collections.Counter(pf['profile']); dp.subtract(collections.Counter(base['profile']))
    res[v] = dict(delta_units=d, freed_units=k, margin=-d - k * BE, profile=pf['profile'], profile_delta={a: b for a, b in sorted(dp.items()) if b},
                  inventory=wf['report']['width_inventory'], audit=msg, certified=pf['certified'], buffers=len(wf['helper_final']))
    print(v, res[v], flush=True)
    if ok: dump(wf, f'L22-{v}.json.gz')
    if v == 'base':
        for g in ('A', 'B', 'C', 'D'):
            W, hs = G[g]
            for h in hs:
                y = copy.deepcopy(x); y['helper_final'][str(h)] = list(w['helper_final'][str(h)])
                try: dd = bp.frame_profile(y, literal=False)['cost'] - base['cost']
                except Exception: dd = None
                print(f'  leave-one-out {g} without {h}: margin {None if dd is None else -dd - (k - 1) * BE} (full {res[v]["margin"]})', flush=True)
json.dump(res, open('L22-summary.json', 'w'), indent=1, default=str)
