"""vlower.py -- option (a) on the PR2942 words: lower the end frames of a subset Q of the four normal-45 pivots from E_45 to
V = E_7 ∩ E_42 ∩ E_45 (8->7 each), frame-only (gates and algebra unchanged); certified solver refit; PR2833 auditor on the
written-back word.  usage: python -B vlower.py WORD.json.gz TAG [audit_all]"""
import sys, json, copy, itertools, collections
sys.path.insert(0, 'S/r13/agents/A-extract/code')
from synth import *
BE = 2091300; V = [256, 128, 64, 35, 16, 11, 5]; PIV = [249, 251, 265, 267]
w = load(sys.argv[1]); tag = sys.argv[2]; base = solve_frames(w, key='b'); out = []
print('base', base['profile'], base['cost'], 'inventory', w['report']['width_inventory'], flush=True)
for k in range(1, 5):
    for Qs in itertools.combinations(PIV, k):
        x = copy.deepcopy(w)
        for h in Qs: x['helper_final'][str(h)] = list(V)
        try: pf = bp.frame_profile(x, literal=False)
        except Exception as ex: out.append(dict(Q=Qs, status='INFEASIBLE', why=str(ex)[:160])); print(Qs, 'INFEASIBLE', str(ex)[:100], flush=True); continue
        d = pf['cost'] - base['cost']; dp = collections.Counter(pf['profile']); dp.subtract(collections.Counter(base['profile']))
        rec = dict(Q=Qs, delta_units=d, margin_vs_k_BE=-d - k * BE, profile=pf['profile'], profile_delta={a: b for a, b in sorted(dp.items()) if b}, certified=pf['certified'])
        if k == 4 or (len(sys.argv) > 3):
            wf = finish(bp.write_frames(x, pf)); ok, msg, rep = audit(wf); rec['audit'] = msg; rec['inventory'] = wf['report']['width_inventory']
            if ok: dump(wf, f'{tag}-Q{"-".join(map(str, Qs))}.json.gz')
        out.append(rec); print(rec, flush=True)
json.dump(out, open(f'{tag}-vlower.json', 'w'), indent=1, default=str)
