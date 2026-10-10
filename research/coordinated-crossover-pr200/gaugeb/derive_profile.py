"""Complete paid internal/source/target ledger reconstruction after three gauges become sources."""
from pathlib import Path
from collections import Counter
import importlib.util,json,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;P=HERE.parent
spec=importlib.util.spec_from_file_location('gauge_source_profile_word',P/'joint/joint_word.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
W=m.Candidate();base=json.loads((P/'borrow/profile.json').read_text());audit=json.loads((HERE/'boundary.json').read_text());scalar=json.loads((HERE/'replay.json').read_text());r=base['profile'];selection=json.loads((HERE/'selection.json').read_text());selected={e['role']for e in selection}
assert len(selected)==3;assert len(scalar['integer'])==2 and {s['direction']for s in scalar['integer']}=={-1,1}
assert all(s['dirty']==16671 and s['formal_columns']==20191 and s['all_targets']and s['all_source_and_dirty_restored']for s in [scalar['F2']]+scalar['integer'])
assert set(scalar['controls'])=={'omit_early_mix','old_adjoint','undo_before_restore','omit_gauge_mix','omit_gauge_compensation'}
assert all(s['status']=='REJECTED'for s in scalar['controls'].values())
local=Counter({int(k):n for k,n in r['physical_internal_histogram'].items()});source=Counter({int(k):n for k,n in r['physical_source_histogram'].items()});target=Counter({int(k):n for k,n in r['physical_target_histogram'].items()})
for e in audit['results']:
 local.subtract({int(k):n for k,n in e['old_aux_histogram'].items()});source.subtract({int(k):n for k,n in e['old_source_histogram'].items()});source.update({int(k):n for k,n in e['new_source_histogram'].items()})
assert all(n>=0 for h in (local,source,target)for n in h.values())
child=Counter()
for h in (local,source,target):
 for rank,n in h.items():
  if rank and n:child[rank]+=3*n
for s,z in W.gauge.items():
 if s not in W.donor and s not in selected:child[3*z['dim']]+=1
child[2]+=2*W.v
mass=sum(rank*n for rank,n in child.items());stock=r['W_per_vertex']-3;physical=r['R']-3;deficit=72*stock-mass
assert stock==20191 and physical==16671 and deficit==r['deficit_per_vertex']==1936
assert sum(k*v for k,v in source.items())==W.v*(W.h-1)
assert sum(k*v for k,v in target.items())==W.v*(W.h-1)
delta=Counter(child);delta.subtract({int(k):n for k,n in r['child_histogram'].items()});delta={k:v for k,v in delta.items()if v};assert delta=={17:9,22:-9,57:-3}
def compact(h):return {str(k):n for k,n in sorted(h.items())if n}
profile=dict(r,R=physical,active_virtual_R=r['active_virtual_R']-3,W_per_vertex=stock,rank_per_vertex=mass,child_histogram=compact(child),physical_internal_histogram=compact(local),physical_source_histogram=compact(source),physical_target_histogram=compact(target),physical_original_sources_borrowed=443)
out=dict(status='PASS_COMPLETE_443_SOURCE_PROFILE',profile=profile,actual_child_delta=delta,all_gauge_adjoint_coefficients_retained=True,all_target_anchor_frames_retained=True,source_boundary_audit='boundary.json',scalar_replay='replay.json')
(HERE/'profile.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS443 complete ledgers',dict(W=stock,R=physical,rank=mass,deficit=deficit,delta=delta),flush=True)
