"""Complete source492/87+8-group paid profile from literal endpoint ledgers.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
The full source, auxiliary, target, bank and scalar costs are retained.
"""
from pathlib import Path
from collections import Counter
from copy import deepcopy
import hashlib,json
D=Path(__file__).resolve().parent;P=D.parent
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
counter=lambda h:Counter({int(k):n for k,n in h.items()})
compact=lambda h:{str(k):n for k,n in sorted(h.items())if n}
base=read(P/'newg/profile.json');r=deepcopy(base['profile'])
scalar=read(D/'replay.json');source_boundary=read(P/'extra/boundary.json');target_boundary=read(D/'boundary.json')
selection=read(P/'extra/selection.json');groups=read(D/'selection.json')['groups'];banks=read(P/'joint/joint-banks.json')
assert len(selection)==21 and len(groups)==87
assert {x['role']for x in source_boundary['endpoint_rows']}=={x['role']for x in selection}
assert len(scalar['integer'])==2 and {x['direction']for x in scalar['integer']}=={-1,1}
assert len(scalar['controls'])==14 and all(x['status']=='REJECTED'for x in scalar['controls'].values())
assert target_boundary['all_local_integer_transfers_both_signs']and len(target_boundary['local_transfer_controls_rejected'])==3
assert {e['role']:(e['old_aux_histogram'],e['old_source_histogram'],e['complete_source_histogram'])for e in source_boundary['endpoint_rows']}=={e['role']:(e['old_aux_histogram'],e['old_source_histogram'],e['complete_source_histogram'])for e in target_boundary['source_rows']}
target=counter(scalar['F2']['actual_target_histogram'])
assert target==counter(target_boundary['new_complete_target_histogram'])
assert counter(target_boundary['old_complete_target_histogram'])==counter(r['physical_target_histogram'])
for x in [scalar['F2']]+scalar['integer']:
 assert x['formal_columns']==20142 and x['dirty']==16622 and x['all_targets']and x['all_source_and_dirty_restored']
 assert x['all_forward_centers_at_D0']and x['all_reflected_centers_at_D1']and x['copied_center_target_reads']==5280
 assert target==counter(x['actual_target_histogram'])==counter(x['actual_reflected_target_histogram'])
 assert x['aggregation_groups']==87 and x['aggregation_pivot_reads']==102
 assert x['rank_groups']==8 and x['rank_targets']==64 and x['rank_removed_reads']==122
 assert len(x['rank_restores'])==8
 assert counter(x['actual_extra_source_histogram'])==counter(x['actual_extra_reflected_source_histogram'])
 assert len(x['aggregation_restores'])==87 and {z['group']for z in x['aggregation_restores']}==set(range(87))
internal=counter(r['physical_internal_histogram']);source=counter(r['physical_source_histogram']);endpoint_delta=Counter()
for e in source_boundary['endpoint_rows']:
 old_aux=counter(e['old_aux_histogram']);old_source=counter(e['old_source_histogram']);new_source=counter(e['complete_source_histogram'])
 internal.subtract(old_aux);source.subtract(old_source);source.update(new_source)
 d=Counter(new_source);d.subtract(old_source);d.subtract(old_aux);endpoint_delta.update(d)
assert sum(k*n for k,n in endpoint_delta.items())==-504
assert all(n>=0 for h in[internal,source,target]for n in h.values())
target_delta=Counter(target);target_delta.subtract(counter(r['physical_target_histogram']))
assert sum(k*n for k,n in target_delta.items())==0
local_delta=Counter(endpoint_delta);local_delta.update(target_delta)
child=Counter()
for h in[internal,source,target]:
 for k,n in h.items():
  if k and n:child[k]+=3*n
for rank,count in r['selected_rank_histogram'].items():child[3*int(rank)]+=count
child[2]+=2*r['v']
assert all(n>0 for n in child.values())
stock=r['W_per_vertex']-21;physical=r['R']-21;mass=sum(k*n for k,n in child.items())
assert (stock,physical,mass)==(20142,16622,1448288)
assert stock*72-mass==1936
assert sum(k*n for k,n in source.items())==sum(k*n for k,n in target.items())==1760*23
delta=Counter(child);delta.subtract(counter(r['child_histogram']))
assert compact(delta)==compact({k:3*n for k,n in local_delta.items()})
profile=dict(r,R=physical,active_virtual_R=r['active_virtual_R']-21,W_per_vertex=stock,rank_per_vertex=mass,
 child_histogram=compact(child),physical_internal_histogram=compact(internal),physical_source_histogram=compact(source),physical_target_histogram=compact(target),
 physical_original_sources_borrowed=492,source_backed_new_rank2_gauges=45,source_owned_gauge_entrances=52,all_gauge_entrances=2331,
 target_aggregation_groups=87,target_aggregation_targets=324,new_source_gauge_target_reads=102,target_basis_scalar_gates=660)
profile['source_owned_gauge_rank_histogram']['2']+=19;profile['all_gauge_rank_histogram']['2']+=19
profile['source_owned_gauge_rank_histogram']['4']+=2;profile['all_gauge_rank_histogram']['4']+=2;profile['source_backed_shared_rank4_gauges']=4
profile.update(target_rank_compression_groups=8,target_rank_compression_targets=64,target_rank_compression_dependent_rows=29,target_aggregation_basis_scalar_gates=474,target_rank_basis_scaled_add_gates=186,target_basis_expanded_unit_adds=672)
assert profile['active_virtual_R']==18382 and profile['bankable_auxiliary_entrances']==profile['selected_roles']==2279
normalized=Counter(child)
for k,n in[(60,2200),(54,13),(36,18),(39,48)]:assert normalized.pop(k)==n
assert normalized.get(57,0)==0
normalized=Counter({k:24*n for k,n in normalized.items()if n});normalized_mass=sum(k*n for k,n in normalized.items())
assert normalized_mass==31513584 and banks['W']==438334 and banks['literal_stock']==1315002
assert 72*banks['W']-normalized_mass==banks['deficit']==46464
assert banks['assignments']==3590352 and banks['charts']==231
assert banks['conservative_extra_selector_calls']==177902746416
assert set(banks['extra_source_roles'])=={x['role']for x in selection}
# Charge all200 source compensation deliveries before compression and all672
# target setup/inverse unit additions; credit no removed operations. The21
# source mixes/unmixes retime already charged K operations.
uncompressed_reads=sum(len(x['targets'])for x in selection)
rankgroups=read(P/'rank/selection.json')['groups'];rankgates=2*sum(abs(c)for g in rankgroups for cs in g['dependent'].values()for c in cs.values());assert rankgates==198
target_gates=sum(2*(len(g['targets'])-1)for g in groups)+rankgates
assert uncompressed_reads==200 and target_gates==672
added_fixed=2*3*72*(uncompressed_reads+target_gates)
assert added_fixed==376704
total_fixed=banks['conservative_extra_selector_calls']+added_fixed
assert total_fixed==177903123120<2**40
out=dict(status='PASS_COMPLETE_SOURCE492_87_PLUS8_PAID_PROFILE',profile=profile,
 local_source_aux_delta=compact(endpoint_delta),local_target_delta=compact(target_delta),local_delta=compact(local_delta),
 child_delta=compact(delta),normalized_child_histogram=compact(normalized),raw_W=stock,raw_rank=mass,raw_deficit=1936,
 normalized_W=banks['W'],normalized_rank=normalized_mass,normalized_deficit=banks['deficit'],literal_stock=banks['literal_stock'],
 bankable_chart_families_unchanged=True,new_source_uncompressed_compensation_reads=uncompressed_reads,target_basis_scalar_gates=target_gates,
 retimed_existing_K_mix_unmix_gates=42,removed_operations_credited=False,conservative_added_fixed_calls=added_fixed,
 conservative_total_extra_selector_calls=total_fixed,existing_fixed_call_bound=2**40,
 input_pins={str(p):sha(p)for p in[P/'rank/selection.json',P/'newg/profile.json',P/'extra/selection.json',P/'extra/boundary.json',D/'selection.json',D/'boundary.json',D/'replay.json',P/'joint/joint-banks.json',Path(__file__)]})
(D/'profile.json').write_text(json.dumps(out,indent=2)+'\n')
print({k:v for k,v in out.items()if k not in['profile','input_pins','normalized_child_histogram']},flush=True)
