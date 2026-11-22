"""final_l27.py -- replicate the five extractions (n=42 x3: 226,228,230; n=7 x2: 363,395) on L22-{base,extra}; per-step TRANSFORM
records; structure + certified frames + auditor each step; exact spec (lane D wordedit) vs WORD-2942-*; summary."""
import sys, json, collections, hashlib
sys.path.insert(0, 'S/r13/agents/A-extract/code')
sys.path.insert(0, 'S/r13/agents/D-chain/code')
from synth import *
import wordedit as WE
BE = 2091300
trs = [r['transform'] for r in json.load(open('R42.json'))] + [r['transform'] for r in json.load(open('R42R7.json'))]
out = {}
for v in ('base', 'extra'):
    w2942 = load(S / f'r14/inputs/WORD-2942-{v}.json.gz'); p0 = solve_frames(w2942, key='p' + v)
    cur = load(f'L22-{v}.json.gz'); cur_pf = solve_frames(cur, key='l' + v); steps = []
    for k, tr in enumerate(trs, 1):
        s = structure_check(cur, tr); assert s.startswith('PASS'), (v, k, s)
        x = apply_stage(cur, tr); pf = solve_frames(x); wf = finish(bp.write_frames(x, pf)); ok, msg, rep = audit(wf); assert ok, (v, k, msg)
        steps.append(dict(step=k, normal=tr['normal'], helper=tr['helper'], structure=s, audit=msg, delta=pf['cost'] - cur_pf['cost'], cumulative_vs_PR2942=pf['cost'] - p0['cost']))
        json.dump(dict(helper=tr['helper'], normal=tr['normal'], before=tr['before'], after=tr['after'], step=k, parent='L22 + previous steps'),
                  open(f'L27-{v}-TRANSFORM-step{k}-h{tr["helper"]}.json', 'w'), indent=1)
        cur, cur_pf = wf, pf
    dump(cur, f'L27-{v}.json.gz'); spec = WE.make_spec(w2942, cur); json.dump(spec, open(f'L27-{v}-SPEC.json', 'w'), indent=0)
    rebuilt = WE.apply_spec(w2942, spec); rt = [k for k in cur if rebuilt.get(k) != cur[k]]
    dp = collections.Counter(cur_pf['profile']); dp.subtract(collections.Counter(p0['profile']))
    out[v] = dict(steps=steps, total_vs_PR2942=cur_pf['cost'] - p0['cost'], freed_units=27, margin=-(cur_pf['cost'] - p0['cost']) - 27 * BE,
                  profile=cur_pf['profile'], profile_delta_vs_PR2942={a: b for a, b in sorted(dp.items()) if b}, inventory=cur['report']['width_inventory'],
                  buffers=len(cur['helper_final']), spec_roundtrip_differing_keys=rt, changed_sections=sorted(k for k in w2942 if w2942[k] != cur[k]),
                  sha256=hashlib.sha256(open(f'L27-{v}.json.gz', 'rb').read()).hexdigest())
    print(v, {k: x for k, x in out[v].items() if k != 'steps'}, flush=True)
    for st in steps: print('   ', st, flush=True)
json.dump(out, open('L27-SUMMARY.json', 'w'), indent=1, default=str)
