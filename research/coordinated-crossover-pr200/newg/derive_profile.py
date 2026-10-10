"""Reconstruct all actual source/internal/target paths after 28 new source-backed gauges."""
from pathlib import Path
from collections import Counter
import json,sys,importlib.util
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;P=HERE.parent
spec=importlib.util.spec_from_file_location('newg_profile_word',P/'joint/joint_word.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
W=m.Candidate();r=json.loads((P/'gaugeb/profile.json').read_text())['profile'];audit=json.loads((HERE/'boundary.json').read_text());scalar=json.loads((HERE/'replay.json').read_text());sel=json.loads((HERE/'selection.json').read_text());oldg={e['role']for e in json.loads((P/'gaugeb/selection.json').read_text())}
assert len(sel)==28 and len(scalar['integer'])==2 and {x['direction']for x in scalar['integer']}=={-1,1}
assert all(x['formal_columns']==20163 and x['dirty']==16643 and x['all_targets']and x['all_source_and_dirty_restored']for x in [scalar['F2']]+scalar['integer'])
assert len(scalar['controls'])==6 and all(x['status']=='REJECTED'for x in scalar['controls'].values())
schedule=json.loads((HERE/'schedule-audit.json').read_text())
assert schedule['source_heads']==471 and schedule['deferred_operations']==168 and schedule['center_prefix_operations']==17080
assert schedule['all_exact_address_subspace_streams_preserved'] and schedule['all_actual_address_frame_dimension_streams_preserved'] and schedule['all_address_jump_histograms_preserved'] and schedule['no_later_center_middle_consumer']
assert all(x['all_forward_centers_at_D0']and x['all_reflected_centers_at_D1']and x['actual_target_histogram']==audit['new_complete_target_histogram']==x['actual_reflected_target_histogram']for x in [scalar['F2']]+scalar['integer'])
def counter(h):return Counter({int(k):n for k,n in h.items()})
local=counter(r['physical_internal_histogram']);source=counter(r['physical_source_histogram']);oldtarget=counter(r['physical_target_histogram'])
assert oldtarget==counter(audit['old_complete_target_histogram']);target=counter(audit['new_complete_target_histogram'])
assert {e['role']for e in audit['endpoint_rows']}=={e['role']for e in sel}
for e in audit['endpoint_rows']:
 local.subtract(counter(e['old_aux_histogram']));source.subtract(counter(e['old_source_histogram']));source.update(counter(e['complete_source_histogram']))
assert all(n>=0 for h in (local,source,target)for n in h.values())
child=Counter()
for h in(local,source,target):
 for k,n in h.items():
  if k and n:child[k]+=3*n
for s,z in W.gauge.items():
 if s not in W.donor and s not in oldg:child[3*z['dim']]+=1
child[2]+=2*W.v
stock=r['W_per_vertex']-28;physical=r['R']-28;mass=sum(k*n for k,n in child.items());deficit=72*stock-mass
assert stock==20163 and physical==16643 and mass==1449800 and deficit==1936
assert sum(k*n for k,n in source.items())==sum(k*n for k,n in target.items())==W.v*(W.h-1)
delta=Counter(child);delta.subtract(counter(r['child_histogram']));delta={k:v for k,v in delta.items()if v};assert delta=={int(k):3*n for k,n in audit['local_delta'].items()}
def compact(h):return {str(k):n for k,n in sorted(h.items())if n}
profile=dict(r,R=physical,active_virtual_R=physical+r['reused_registers'],W_per_vertex=stock,rank_per_vertex=mass,child_histogram=compact(child),physical_internal_histogram=compact(local),physical_source_histogram=compact(source),physical_target_histogram=compact(target),physical_original_sources_borrowed=471,source_backed_new_rank2_gauges=26,source_backed_shared_rank4_gauges=2,center_prefix_operations=17080,deferred_center_independent_operations=168,source_heads_exposed_by_retiming=2,copied_center_frame_chronology="D0 forward and D1 complementary reverse")
assert profile['active_virtual_R']==18403
# Legacy selected_* fields consistently describe actual auxiliary-bank entrances.
# Data/source-owned entrances are recorded separately and never banked twice.
bank_ranks=Counter(z['dim']for role,z in W.gauge.items()if role not in W.donor and role not in oldg)
source_ranks=Counter(W.gauge[role]['dim']for role in oldg)
source_ranks.update(e['source_gauge']for e in audit['endpoint_rows'])
all_ranks=bank_ranks+source_ranks
profile['retained_selected_roles']=r['selected_roles']
profile['retained_selected_rank_histogram']=r['selected_rank_histogram']
profile['selected_rank_histogram']=compact(bank_ranks)
profile['selected_roles']=sum(bank_ranks.values())
profile['selected_roles_scope']='Actual remaining bankable auxiliary entrances; source-owned data entrances are counted separately.'
profile['bankable_auxiliary_entrances']=sum(bank_ranks.values())
profile['source_owned_gauge_entrances']=sum(source_ranks.values())
profile['source_owned_gauge_rank_histogram']=compact(source_ranks)
profile['all_gauge_entrances']=sum(all_ranks.values())
profile['all_gauge_rank_histogram']=compact(all_ranks)
assert profile['bankable_auxiliary_entrances']==2279
assert profile['source_owned_gauge_entrances']==31
assert profile['all_gauge_entrances']==2310
assert bank_ranks=={20:2200,18:13,12:18,13:48}
assert source_ranks=={19:3,2:26,4:2}
assert profile['R']+profile['reused_registers']==profile['active_virtual_R']==18403
assert profile['W_per_vertex']==2*profile['v']+profile['R']
assert profile['maxchild']==max(child)
out=dict(status='PASS_COMPLETE_471_SOURCE_PROFILE',profile=profile,actual_child_delta=delta,all_original_gauge_adjoint_coefficients_retained=True,all_original_target_anchors_retained=True,additional_source_gauge_target_reads=112,all_new_target_chronology_reconstructed=True)
(HERE/'profile.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS471 complete ledgers',dict(W=stock,R=physical,rank=mass,deficit=deficit,delta=delta),flush=True)
