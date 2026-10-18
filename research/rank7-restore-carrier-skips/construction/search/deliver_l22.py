"""deliver_v.py -- declared frame-edit record + exact spec (lane D wordedit) for the V-lowered PR2942 words; re-verifies by applying
the declared edits to WORD-2942 (frames + helper_final), re-deriving report/cleanup, solver profile, auditor."""
import sys, json, copy, collections, hashlib
sys.path.insert(0, 'S/r13/agents/A-extract/code')
sys.path.insert(0, 'S/r13/agents/D-chain/code')
from synth import *
import wordedit as WE
V = [256, 128, 64, 35, 16, 11, 5]
summary = {}
for v in ('base', 'extra'):
    old = load(S / f'r14/inputs/WORD-2942-{v}.json.gz'); new = load(f'L22-{v}.json.gz')
    edits = []
    for sec in ('A', 'B', 'restore'):
        assert len(old[sec]) == len(new[sec])
        for i, (a, b) in enumerate(zip(old[sec], new[sec])):
            if a[0] == 'warp': assert a == b; continue
            assert a[:-1] == b[:-1], ('gate changed', sec, i)
            if PM.basis(a[-1] or []) != PM.basis(b[-1] or []):
                edits.append(dict(section=sec, index=i, gate=a[:-1], old_frame=a[-1], new_frame=b[-1]))
    hf = {k: dict(old=old['helper_final'][k], new=new['helper_final'][k]) for k in new['helper_final'] if old['helper_final'][k] != new['helper_final'][k]}
    other = [k for k in old if k not in ('A', 'B', 'restore', 'helper_final', 'report', 'cleanup') and old[k] != new[k]]
    # re-apply declared edits to the old word and re-verify
    x = copy.deepcopy(old)
    for e in edits: x[e['section']][e['index']][-1] = list(e['new_frame'])
    for k, d in hf.items(): x['helper_final'][k] = list(d['new'])
    x = finish(x); ok, msg, rep = audit(x)
    same = all(x[k] == new[k] for k in new)
    prof = PM.frame_report(x)
    spec = WE.make_spec(old, new); rebuilt = WE.apply_spec(old, spec); rt = [k for k in new if rebuilt.get(k) != new[k]]
    json.dump(dict(stage='codim2-end-frame-lowering', groups={'V45': [[256,128,64,35,16,11,5], [249,251,265,267]], 'A': [[256,128,64,38,20,10,1], [331,450,451,508,509]], 'B': [[256,128,64,34,17,11,4], [299,448,449,484,485]], 'C': [[256,128,64,32,19,11,6], [452,453,532,533]], 'D': [[256,128,64,37,21,8,3], [454,455,556,557]]}, helper_final_changes=hf, frame_edits=edits,
                   declared_local_profile=new['report']['local_profile'], declared_width_inventory=new['report']['width_inventory']),
              open(f'L22-{v}-FRAME-EDITS.json', 'w'), indent=1)
    json.dump(spec, open(f'L22-{v}-SPEC.json', 'w'), indent=0)
    summary[v] = dict(frame_edits=len(edits), by_section=dict(collections.Counter(e['section'] for e in edits)), helper_final_changes=len(hf), other_changed_sections=other,
                      reapply_equals_word=same, audit=msg, profile=prof[0], inventory=prof[1], spec_roundtrip_differing_keys=rt,
                      changed_sections=sorted(k for k in old if old[k] != new[k]), sha256=hashlib.sha256(open(f'L22-{v}.json.gz', 'rb').read()).hexdigest())
    print(v, summary[v], flush=True)
json.dump(summary, open('L22-DELIVERABLE.json', 'w'), indent=1)
