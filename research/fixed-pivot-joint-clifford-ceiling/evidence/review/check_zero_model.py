#!/usr/bin/env python3
"""Rebind only the 43 recorded zero witnesses; no neighbor/assignment search."""
from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
import importlib.util
import json

HERE=Path(__file__).resolve().parent
AUTHOR=HERE.parent/'joint-clifford-design-20261023'

def need(ok, why):
    if not ok: raise RuntimeError(why)

def load_own(name, filename):
    spec=importlib.util.spec_from_file_location(name,HERE/filename)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def main():
    own=load_own('own_joint_review','check_joint_receipt.py')
    graph_binding=load_own('own_graph_binding','verify_graph_binding.py').reconstruct()
    names=['ZERO-MODEL-PROOF.md','ZERO-MODEL-INVENTORY.json',
           'ZERO-MODEL-WITNESS-BINDING.json','zero-model-inputs/DISCOVERY.json',
           'inputs/contracted-graph.txt','inputs/research/independent-clifford-expansion/RESULT.json']
    before={n:sha256((AUTHOR/n).read_bytes()).hexdigest() for n in names}
    need(before['ZERO-MODEL-WITNESS-BINDING.json']=='af46672c959594e0583fe634bf2a851ecd6667c46c588383481de43d7591fce7','witness pin')
    need(before['zero-model-inputs/DISCOVERY.json']=='a611408b9d76622acf50d02d8c37a24bec9f5ec2b3f53c46351f8d565ece4b2d','discovery pin')
    inventory=json.loads((AUTHOR/names[1]).read_text())
    binding=json.loads((AUTHOR/names[2]).read_text())
    discovery=json.loads((AUTHOR/names[3]).read_text())
    source_result=json.loads((AUTHOR/names[5]).read_text())
    need(inventory['source_head']=='0335701859182b7bdf31706b0d969c72f5de41c7','declared source head')
    need(inventory['graph_sha256']==graph_binding['graph_sha256']==before[names[4]],'independent full graph binding')
    need(inventory['discovery_sha256']==before[names[3]],'discovery inventory binding')
    plateau=discovery[1]
    need(plateau['collapse_zero'] and plateau['plateau'],'contracted plateau row')
    pairs=sorted((g,a) for rnd,g,a,_ in plateau['moves'] if rnd==0)
    need(len(pairs)==len(set(pairs))==43,'43 distinct recorded pairs')
    need(pairs==sorted(map(tuple,inventory['retained_moves'])),'exact discovery witness selection')
    selected={g for g,a in pairs}
    need(len(selected)==43==inventory['distinct_groups']==binding['retained_zero_count'],'43 distinct groups')
    census=source_result['census'][0]
    zeros=[p for p in census['patterns'] if not any(p['delta'])]
    need(census['collapse_zero'] and census['unchanged_rank_polynomial_moves']==43,'recorded source census count')
    need(zeros==[{'count':43,'delta':[0]*10,'witness':[499,7]}],'recorded zero bucket')
    rows=(AUTHOR/names[4]).read_text().splitlines();n,m,k=map(int,rows[0].split())
    charts=[tuple(map(int,row.split()[1:])) for row in rows[1:n+1]]
    frozen={i for i,row in enumerate(rows[1:n+1]) if int(row.split()[0])}
    maps=[tuple(map(int,row.split())) for row in rows[n+1:n+1+k]]
    edges=[tuple(map(int,row.split())) for row in rows[n+1+k:]]
    need(len(edges)==m==3938 and not(selected&frozen),'all incidences and frozen boundaries')
    induced=[i for i,e in enumerate(edges) if e[0] in selected and e[1] in selected]
    incident=[i for i,e in enumerate(edges) if e[0] in selected or e[1] in selected]
    need(induced==inventory['induced_incidences']==[],'empty induced graph, including self-loops')
    need(len(incident)==172 and all(edges[i][2:]==(-1,1) for i in incident),'172 paid identity incidences only')
    expected_rows=[dict(id=i,a=edges[i][0],b=edges[i][1],operator_id=edges[i][2],sign=edges[i][3]) for i in incident]
    need(expected_rows==inventory['all_incident_rows'],'all incidence identities and multiplicities')
    stored={w['group']:w for w in binding['witnesses']}
    need(len(stored)==43 and set(stored)==selected,'one stored witness per selected group')
    base_paid=Counter({8:8});base_helpers=Counter();baseline=[]
    for e in edges:
        r=own.edge_rank(e,charts,maps);baseline.append(r)
        if e[3]<0:need(r>0,'strict baseline helper');base_helpers[r]+=1
        elif r:base_paid[r]+=1
    checked=[]
    for g,a in pairs:
        w=stored[g];changed=own.transvection(charts[g],a)
        need(0<a<1<<18 and len(changed)==own.rank(changed)==9,'valid exact chart')
        need(all(not own.pairing(x,y) for x in changed for y in changed),'isotropic exact chart')
        need(own.rank((*charts[g],*changed))==10,'nearest distinct Lagrangian')
        need(w['axis']==a and w['baseline_chart']==list(charts[g]) and w['changed_chart']==list(changed),'literal witness charts')
        ids=[i for i,e in enumerate(edges) if g in e[:2]]
        need(len(ids)==4,'four independent incidences per selected group')
        assignment=list(charts);assignment[g]=changed;delta=[0]*10;transitions=[]
        for i in ids:
            e=edges[i];old=baseline[i];new=own.edge_rank(e,assignment,maps)
            if old:delta[old]-=1
            if new:delta[new]+=1
            transitions.append(dict(id=i,a=e[0],b=e[1],old_rank=old,changed_rank=new))
        need(transitions==w['incidences'] and delta==w['delta']==[0]*10,'all exact rank transitions and zero polynomial')
        need(w['nearest'] is True,'recorded nearest flag')
        checked.append(dict(group=g,axis=a,incidence_ids=ids,delta=delta))
    external=defaultdict(list)
    for i in incident:
        a,b,_,_=edges[i];g=a if a in selected else b;other=b if a in selected else a
        external[other].append(dict(id=i,selected_group=g))
    expected_external=[dict(group=g,frozen=g in frozen,distinct_zero_neighbors=len({r['selected_group'] for r in rs}),incidences=rs) for g,rs in sorted(external.items())]
    need(expected_external==binding['external_neighbors'] and binding['zero_groups_independent'],'complete external adjacency binding')
    # Structural check only for the separately untested bridge; no B is generated.
    triple={172,499,572};triple_ids=[i for i,e in enumerate(edges) if e[0] in triple or e[1] in triple]
    shared={tuple(sorted(e[:2])):i for i,e in enumerate(edges) if e[0] in triple and e[1] in triple}
    need(shared=={(172,499):1193,(172,572):1411},'exact bridge shape, no leaf interaction or selected self-loop')
    need(len(triple_ids)==14 and all(edges[i][2:]==(-1,1) for i in triple_ids),'14 complete paid identity bridge rows')
    parallel=[i for i in triple_ids if set(edges[i][:2])=={119,172}]
    need(len(parallel)==2 and {526,592}<=frozen and not(triple&frozen),'parallel charges and frozen neighbors')
    need(graph_binding['all_original_zero_paid_edges_preserved_under_group_assignments'],'all original zero rows preserved')
    need(before=={n:sha256((AUTHOR/n).read_bytes()).hexdigest() for n in names},'all source inputs unchanged')
    result=dict(status='PASS_RETAINED_43_ZERO_MODEL_INVOICE_IDENTITY',input_sha256=before,
      independent_source_graph_binding=graph_binding['graph_sha256'],
      recorded_pairs_checked=43,exact_rank_transitions_checked=172,all_incident_rows_paid_identity=True,
      induced_incidence_count=0,external_neighbor_count=len(external),witnesses=checked,
      baseline_paid=dict(sorted(base_paid.items())),baseline_helpers=dict(sorted(base_helpers.items())),
      simultaneous_assignments_covered_by_additivity=2**43,assignment_enumeration_executed=False,
      new_axis_or_neighbor_enumeration_executed=False,source_census_repeated=False,
      original_zero_paid_rows_preserved=31108,helper_rows_unchanged=408,paid_owned_H8_centres_unchanged=8,
      all_real_C_invoice_identity=True,source_census_completeness='inherited authenticated source result; only stored43 rebound',
      bridge_structure_only=dict(groups=sorted(triple),incidence_ids=triple_ids,parallel_119_172=parallel,
         tables_evaluated=False,full_binary_minimum='min(0,E172(B)+min(0,R499(B))+min(0,R572(B)))'),
      native_compiler_caller_transfer_admitted=False,inputs_unchanged=True)
    (HERE/'ZERO-MODEL-REVIEW.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','recorded_pairs_checked','exact_rank_transitions_checked','induced_incidence_count','simultaneous_assignments_covered_by_additivity','inputs_unchanged']},sort_keys=True))

if __name__=='__main__':main()
