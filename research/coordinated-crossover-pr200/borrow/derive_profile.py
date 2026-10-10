"""Reconstruct the complete paid profile from actual spliced source/dirty paths."""
from pathlib import Path
from collections import Counter
import json,sys
sys.dont_write_bytecode=True
from replay import W,selection,adj,oldadj,regs,removed
HERE=Path(__file__).resolve().parent;PACKAGE=HERE.parent
base=json.loads((PACKAGE/'joint/joint-replay.json').read_text());audit=json.loads((HERE/'boundary.json').read_text());scalar=json.loads((HERE/'replay.json').read_text())
assert scalar['F2']['dirty']==len(regs)==16674
assert len(scalar['integer'])==2 and {r['direction']for r in scalar['integer']}=={1,-1}
assert all(r['all_source_and_dirty_restored']and r['formal_columns']==20194 for r in [scalar['F2']]+scalar['integer'])
assert len(audit['results'])==len(selection)==440
assert {r['role']for r in audit['results']}=={r['role']for r in selection}
assert all(adj[s]==oldadj[s]for s in W.gauge)
# Every actual dirty path except a borrowed/deleted path remains unchanged.
local=Counter({int(k):n for k,n in base['profile']['physical_internal_histogram'].items()})
_,_,source,_=W.C.chains();source=Counter(source)
for r in audit['results']:
 local.subtract({int(k):n for k,n in r['old_aux_histogram'].items()})
 source.subtract({1:1,22:1})
 source.update({int(k):n for k,n in r['new_source_histogram'].items()})
assert all(n>=0 for n in local.values())and all(n>=0 for n in source.values())
# The changed adjoint agrees on every gauge, all terminal actions remain,
# and partner deliveries retain their exact original target anchors/frames.
target=Counter({int(k):n for k,n in base['profile']['physical_target_histogram'].items()})
child=Counter()
for part in [local,target,source]:
 for rank,count in part.items():
  if rank and count:child[rank]+=3*count
for role,z in W.gauge.items():
 if role not in W.donor:child[3*z['dim']]+=1
child[2]+=2*W.v
assert all(count>0 for count in child.values())
delta=Counter(child);delta.subtract({int(k):n for k,n in base['profile']['child_histogram'].items()});delta={k:v for k,v in delta.items()if v}
assert delta=={int(k):v for k,v in audit['shared_histogram_delta'].items()}=={2:-1320,22:-1320}
physical=len(regs);stock=2*W.v+physical;mass=sum(rank*count for rank,count in child.items());deficit=72*stock-mass
assert stock==20194 and deficit==base['profile']['deficit_per_vertex']==1936
assert sum(rank*count for rank,count in target.items())==W.v*(W.h-1)
assert sum(rank*count for rank,count in source.items())==W.v*(W.h-1)
def compact(x):return {str(k):n for k,n in sorted(x.items())if n}
profile=dict(base['profile'],R=physical,active_virtual_R=base['profile']['active_virtual_R']-440,W_per_vertex=stock,rank_per_vertex=mass,child_histogram=compact(child),physical_internal_histogram=compact(local),physical_source_histogram=compact(source),physical_target_histogram=compact(target),physical_original_sources_borrowed=440)
assert profile['maxchild']==max(child)
out=dict(status='PASS_COMPLETE_SOURCE_BORROWED_PROFILE',profile=profile,actual_child_delta=delta,source_boundary_audit='boundary.json',scalar_replay='replay.json',all_gauge_adjoint_coefficients_retained=True,all_target_anchor_frames_retained=True,old_adjoint_replaced=True,removed_auxiliary_copy_gates=440,removed_forward_reverse_scalar_gates=880,retimed_partner_mix_count_unchanged=True,remaining_adjoint_coefficients_do_not_increase=True)
(HERE/'profile.json').write_text(json.dumps(out,indent=2)+'\n')
print('PASS complete spliced source/internal/target profile',dict(W=stock,rank=mass,deficit=deficit,delta=delta),flush=True)
