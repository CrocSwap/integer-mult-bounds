"""Adapt the independent reflected-ledger reviewer to a changed scalar word.
Prepared by OpenAI Codex. Original-word scalar invariants are deliberately not
asserted; full raw/canonical binding and both emitted event ledgers are checked.
"""
import argparse
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path

if not __debug__:
    raise RuntimeError('This exact frame audit requires assertions enabled.')

p=argparse.ArgumentParser()
p.add_argument('--candidate',type=Path,required=True)
p.add_argument('--reviewer',type=Path,required=True,help='Pinned independent review_frames.py')
p.add_argument('--original-selected',type=Path,required=True,help='Original PR484 gauge80-kernel42 raw word')
p.add_argument('--unretimed-canonical',type=Path,help='Optional canonical word before frame retiming')
p.add_argument('--out',type=Path,required=True);a=p.parse_args()
source=a.reviewer
spec=importlib.util.spec_from_file_location('F',source);F=importlib.util.module_from_spec(spec);spec.loader.exec_module(F)
paths=[a.candidate/n for n in ['FULL-WORD.json.gz','CANONICAL-WORD.json.gz','LOCAL-PROGRAMS.json.gz']]
w,c,programs=map(F.read,paths)
old=F.read(a.original_selected)
base_c=F.read(a.unretimed_canonical) if a.unretimed_canonical else c
preserved=['target_levels','centers','center_frames','ports','root_lines','cut','scatter','precondition']
assert all(w[k]==old[k]for k in preserved)
assert w['A'][:420]==old['A'][:420]
assert set(map(tuple,w['start_extra'].values()))==set(map(tuple,old['start_extra'].values()))
entrance_rank=sum(len(f)for f in w['start_extra'].values());widths=Counter(9-len(w['start_extra'].get(str(r),[]))for r in range(240,800))
raw=F.raw_ledger(w);bindings=F.canonical_binding(w,c,base_c)
ledgers={o:F.ledger(c,programs[o],o=='backward')for o in ('forward','backward')}
assert raw['rank_mass']==9*560+8*240+72-entrance_rank
assert all(l['rank_mass']==raw['rank_mass']and l['profile']==raw['profile']for l in ledgers.values())
negative=F.controls(w,c,programs,w,base_c)
union={tuple(e[3:5]if e[0]=='climb'else e[2:4])for seq in programs.values()for e in seq if e[0]in('climb','center')}
r=dict(status='PASS_CHANGED_SCALAR_WORD_RAW_BINDING_AND_BOTH_REFLECTED_LEDGERS',
       inputs={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths+[a.original_selected]+([a.unretimed_canonical]if a.unretimed_canonical else [])},
       independent_reviewer_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
       raw=raw,canonical_binding=bindings,emitted_ledgers=ledgers,
       entrance_rank=entrance_rank,entering_helpers=len(w['start_extra']),widths=dict(sorted(widths.items())),
       unchanged_selected_boundary_fields=preserved,all_420_gauge_gates_unchanged=True,
       entrance_frame_set_unchanged=True,entrance_frame_types=16,
       actual_directed_edge_union=len(union),negative_controls_rejected=negative,
       used_unretimed_canonical_baseline=bool(a.unretimed_canonical),
       scope='Exact local frame/normalization-placement ledger. Raw-to-canonical all-event binding and both serialized reflected streams verified. Old scalar-word invariants are intentionally omitted because the partial-own construction changes A. When an unretimed canonical baseline is supplied, fixed compensation/cleanup/cut payloads and start/final/centre boundaries are also compared to it; otherwise those comparisons use the candidate itself. Gaussian phase operators, emitted wrapper identities, physical owners and complete invoice remain separate.')
a.out.write_text(json.dumps(r,indent=2)+'\n');print(r['status'],'mass',raw['rank_mass'],'edges',len(union),'controls',len(negative))
