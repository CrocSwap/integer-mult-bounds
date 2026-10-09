"""Full actual target aggregation profile from the scalar replay, retaining all paid source/internal paths.
Prepared with OpenAI Codex assistance; Apache-2.0. No assembly claim.
"""
from pathlib import Path
from collections import Counter
import hashlib,json
D=Path(__file__).resolve().parent;P=D.parent
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
boundary=read(D/'boundary.json');assert boundary['status']=='PASS_TARGET_AGGREGATION_ACTUAL_CHAINS_REFLECTION_AND_PRIMES'
base=read(P/'newg/profile.json');r=base['profile'];s=read(D/'replay.json');selection=read(D/'selection.json')
counter=lambda h:Counter({int(k):n for k,n in h.items()});compact=lambda h:{str(k):n for k,n in sorted(h.items())if n}
assert len(s['integer'])==2 and {x['direction']for x in s['integer']}=={-1,1}
assert len(s['controls'])==9 and all(x['status']=='REJECTED'for x in s['controls'].values())
newtarget=counter(s['F2']['actual_target_histogram']);assert newtarget==counter(boundary['new_complete_target_histogram'])==counter(boundary['reflected_target_histogram']);oldtarget=counter(r['physical_target_histogram']);delta=Counter(newtarget);delta.subtract(oldtarget);delta=Counter({k:n for k,n in delta.items()if n})
assert dict(delta)=={int(k):n for k,n in selection['local_delta'].items()}
for x in [s['F2']]+s['integer']:
 assert x['formal_columns']==20163 and x['dirty']==16643 and x['all_targets']and x['all_source_and_dirty_restored']
 assert x['all_forward_centers_at_D0']and x['all_reflected_centers_at_D1']and x['copied_center_target_reads']==5280
 assert counter(x['actual_target_histogram'])==counter(x['actual_reflected_target_histogram'])==newtarget
 assert x['aggregation_groups']==27 and x['aggregation_pivot_reads']==28 and len(x['aggregation_restores'])==27
 assert {a['group']for a in x['aggregation_restores']}==set(range(27))
assert sum(k*n for k,n in delta.items())==0
child=counter(r['child_histogram'])
for k,n in delta.items():child[k]+=3*n
assert all(n>=0 for n in child.values())
profile=dict(r,physical_target_histogram=compact(newtarget),child_histogram=compact(child),target_aggregation_groups=27,target_aggregation_targets=108,new_source_gauge_target_reads=28,target_basis_scalar_gates=162)
assert sum(k*n for k,n in child.items())==r['rank_per_vertex']==1449800
assert r['W_per_vertex']==20163 and r['R']==16643 and r['active_virtual_R']==18403
assert 72*r['W_per_vertex']-r['rank_per_vertex']==1936
assert sum(k*n for k,n in newtarget.items())==1760*23
banks=read(P/'joint/joint-banks.json');normalized=counter(child)
for k,n in [(60,2200),(54,13),(36,18),(39,48)]:assert normalized.pop(k)==n
assert normalized.get(57,0)==0
normalized=Counter({k:24*n for k,n in normalized.items()if n})
assert sum(k*n for k,n in normalized.items())==31549872
assert 72*banks['W']-31549872==banks['deficit']==46464
added_fixed=2*3*72*162
assert banks['conservative_extra_selector_calls']+added_fixed<2**40
result=dict(status='PASS_COMPLETE_SOURCE471_TARGET_AGGREGATION_PROFILE',profile=profile,local_target_delta=compact(delta),child_delta=compact({k:3*n for k,n in delta.items()}),normalized_child_delta=compact({k:72*n for k,n in delta.items()}),source_and_auxiliary_paths_unchanged=True,bank_and_chart_assignments_unchanged=True,raw_W=20163,raw_rank=1449800,raw_deficit=1936,normalized_W=438838,normalized_rank=31549872,normalized_deficit=46464,literal_stock=banks['literal_stock'],new_literal_scalar_gates=162,removed_literal_gauge_reads=84,net_literal_scalar_gate_change=78,conservative_added_fixed_calls=added_fixed,conservative_total_extra_selector_calls=banks['conservative_extra_selector_calls']+added_fixed,existing_fixed_call_bound=2**40,input_pins={str(p):sha(p)for p in[P/'newg/profile.json',D/'replay.json',D/'selection.json',P/'joint/joint-banks.json',Path(__file__)]})
(D/'profile.json').write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items()if k not in('profile','input_pins')})
