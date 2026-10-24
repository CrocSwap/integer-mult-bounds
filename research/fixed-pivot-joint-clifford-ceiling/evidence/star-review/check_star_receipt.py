#!/usr/bin/env python3
"""Verify a recorded star receipt; do not generate neighbors or run source code."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import importlib.util
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
AUTHOR=ROOT/'outputs/joint-clifford-three-group-star-20261023'
PRIOR=ROOT/'outputs/joint-clifford-independent-review-20261023'
STATES=[[b,x,y] for b in (0,1) for x in (0,1) for y in (0,1)]

def need(ok,why):
    if not ok:raise RuntimeError(why)

def load_own(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
    own=load_own('own_prior_joint',PRIOR/'check_joint_receipt.py')
    original=load_own('own_source_graph',PRIOR/'verify_graph_binding.py').reconstruct()
    static=json.loads((HERE/'STATIC-FREEZE.json').read_text())
    for n,h in static['author_freeze'].items():
        need(sha256((AUTHOR/n).read_bytes()).hexdigest()==h,'accepted static pin '+n)
    manifest=json.loads((AUTHOR/'AUTH-MANIFEST.json').read_text())
    for n,h in manifest.items():need(sha256((AUTHOR/n).read_bytes()).hexdigest()==h,'source input pin '+n)
    raw=(AUTHOR/'STAR-RESULT.json').read_bytes();result=json.loads(raw)
    need(sha256(raw).hexdigest()=='4533091920be9e8e71bd93ac7ebf7e13a67c5ae6e179ac7447e60e55f3654a8c','frozen result pin')
    run=json.loads((AUTHOR/'RUN-RECEIPT.json').read_text())
    start=json.loads((AUTHOR/'RUN-START.json').read_text())
    need(all(start[key]==run[key] for key in start),'run start/finish binding')
    need(run['before']==run['after'] and run['inputs_unchanged'],'unchanged run inputs')
    need(run['before']=={**manifest,**static['author_freeze']},'all execution inputs bound to accepted static gate')
    for name,digest in run['before'].items():need(sha256((AUTHOR/name).read_bytes()).hexdigest()==digest,'run input '+name)
    need(run['exit_code']==0 and run['output_exists'] and run['output_sha256']==sha256(raw).hexdigest(),'successful bound output')
    need(run['external_hard_cap_seconds']==60 and run['internal_cooperative_cap_seconds']==58,'one authorized 60/58 cap')
    need(run['command'][:4]==['/usr/bin/timeout','--signal=KILL','60s','/usr/bin/python3'],'external timeout command')
    need(run['environment']=={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8','LC_ALL':'C.UTF-8'},'clean environment')
    for name,field in [('STAR-STDOUT.txt','stdout_sha256'),('STAR-STDERR.txt','stderr_sha256')]:
        need(sha256((AUTHOR/name).read_bytes()).hexdigest()==run[field],'bound run '+name)
    need(not (AUTHOR/'STAR-STDERR.txt').read_bytes(),'empty author stderr')
    need(result['source_input_hashes']==manifest,'result source input bindings')
    need(result['checker_sha256']==static['author_freeze']['check_star.py'],'executed checker pin')
    need(result['graph_sha256']==original['graph_sha256']==manifest['inputs/contracted-graph.txt'],'independent chronological graph')
    rows=(AUTHOR/'inputs/contracted-graph.txt').read_text().splitlines();n,m,k=map(int,rows[0].split())
    charts=[tuple(map(int,r.split()[1:])) for r in rows[1:n+1]]
    frozen={i for i,r in enumerate(rows[1:n+1]) if int(r.split()[0])}
    maps=[tuple(map(int,r.split())) for r in rows[n+1:n+1+k]]
    edges=[tuple(map(int,r.split())) for r in rows[n+1+k:]]
    selected={172,499,572};need(not(selected&frozen),'frozen boundaries')
    union=[i for i,e in enumerate(edges) if selected.intersection(e[:2])]
    need(union==[130,131,1181,1187,1193,1194,1204,1212,1399,1405,1411,1412,1422,1430],'complete union')
    need(all(edges[i][2:]==(-1,1) for i in union),'all touched rows paid identity')
    leaves={499:own.transvection(charts[499],7),572:own.transvection(charts[572],25)}
    ints=lambda d:{int(r):v for r,v in d.items() if v}
    need(result['bridge_group']==172 and result['leaf_group_axes']==[[499,7],[572,25]],'fixed declared domain')
    need(result['states']==STATES,'global state order')
    need({int(g):tuple(c) for g,c in result['leaf_baseline_charts'].items()}=={g:charts[g] for g in leaves},'baseline leaf charts')
    need({int(g):tuple(c) for g,c in result['leaf_changed_charts'].items()}==leaves,'independent changed leaf charts')
    pair=json.loads((AUTHOR/'retained/SEARCH-RESULT.json').read_text())
    need(sha256((AUTHOR/'retained/SEARCH-RESULT.json').read_bytes()).hexdigest()==result['accepted_pair_receipt_sha256']==own.RESULT_SHA,'accepted pair pin')
    old_pairs={r['partner_axis']:r for r in pair['candidates'] if r['partner']==172}
    base_paid=Counter({8:8});base_helpers=Counter();outside_paid=Counter({8:8});outside_helpers=Counter();base_ranks=[]
    for i,e in enumerate(edges):
        rank=own.edge_rank(e,charts,maps);base_ranks.append(rank)
        if e[3]<0:
            need(rank>0,'strict baseline helper');base_helpers[rank]+=1
            if i not in union:outside_helpers[rank]+=1
        elif rank:
            base_paid[rank]+=1
            if i not in union:outside_paid[rank]+=1
    need(dict(base_paid)==ints(result['baseline_paid']) and dict(base_helpers)==ints(result['baseline_helpers']),'complete baseline source profile')
    records=result['bridge_records'];need(len(records)==1022,'complete bridge receipt')
    seen_axes=set();seen_charts=set();seen_ordinals=set();buckets=Counter();first={};point_cache={};cross_signs={499:Counter(),572:Counter()}
    rank_entries=profiles_checked=0;negatives=[];unresolved=0;minimum=None
    scale=int(result['scale']);need(scale==1<<128 and result['fixed_point_bits']==128,'128-bit scale')
    need(Q(result['test_C'])==own.C and list(map(Q,result['saving_domain']))==[Q(0),Q(1,200)],'exact point/domain')
    for record in records:
        ordinal=record['bridge_neighbor_ordinal'];axis=record['bridge_axis'];bridge=tuple(record['bridge_chart'])
        need(0<=ordinal<1022 and ordinal not in seen_ordinals,'unique ordinal')
        need(0<axis<1<<18 and axis not in seen_axes and bridge not in seen_charts,'distinct axis/chart')
        need(bridge==own.transvection(charts[172],axis),'independent bridge transvection')
        need(len(bridge)==own.rank(bridge)==9 and all(not own.pairing(x,y) for x in bridge for y in bridge),'valid bridge Lagrangian')
        need(own.rank((*charts[172],*bridge))==10,'nearest bridge chart')
        seen_ordinals.add(ordinal);seen_axes.add(axis);seen_charts.add(bridge)
        previous=old_pairs[axis];need(list(bridge)==previous['partner_chart'],'same accepted pair chart')
        need(record['states']==STATES and [r['id'] for r in record['incidences']]==union,'all eight states/all rows once')
        deltas=[];profiles=[];all_ranks=[]
        for state,(b,x,y) in enumerate(STATES):
            assignment=list(charts)
            if b:assignment[172]=bridge
            if x:assignment[499]=leaves[499]
            if y:assignment[572]=leaves[572]
            paid,helpers=Counter(outside_paid),Counter(outside_helpers);delta=[0]*10;state_ranks=[]
            for data,i in zip(record['incidences'],union):
                e=edges[i];need((data['a'],data['b'],data['op'],data['sign'])==(e[0],e[1],0,e[3]),'ordered incidence/operator/sign')
                r=own.edge_rank(e,assignment,maps);rank_entries+=1;state_ranks.append(r)
                need(r==data['ranks'][state],'exact independent eight-state rank')
                old=base_ranks[i]
                if old:delta[old]-=e[3]
                if r:delta[r]+=e[3]
                if e[3]<0:need(r>0,'strict state helper');helpers[r]+=1
                elif r:paid[r]+=1
            need(sum(helpers.values())==408 and 0 not in helpers,'every arbitrary helper once/productive')
            profile=dict(paid=dict(sorted(paid.items())),helpers=dict(sorted(helpers.items())))
            saved=record['profiles'][state]
            need(profile=={key:ints(saved[key]) for key in ('paid','helpers')},'all complete state invoices')
            deltas.append(delta);profiles.append(profile);all_ranks.append(state_ranks);profiles_checked+=1
        need(record['valid_states']==[True]*8 and record['energy_deltas']==deltas,'all feasible signed deltas')
        need(not any(v for d in deltas[:4] for v in d),'all bridge-off polynomials zero')
        for s,t in ((0,0),(2,1),(4,2),(6,3)):
            need(deltas[s]==previous['energy_deltas'][t],'accepted pair energy projection')
        prior_rows={r['id']:r for r in previous['incidences']}
        for j,i in enumerate(union):
            if i in prior_rows:need([all_ranks[s][j] for s in (0,2,4,6)]==prior_rows[i]['ranks'],'all overlapping pair rank projections')
        r499=[deltas[6][r]-deltas[4][r]-deltas[2][r]+deltas[0][r] for r in range(10)]
        r572=[deltas[5][r]-deltas[4][r]-deltas[1][r]+deltas[0][r] for r in range(10)]
        need(r499==record['R499']==previous['cross_difference'] and r572==record['R572'],'both exact interactions')
        need(deltas[7]==[deltas[4][r]+r499[r]+r572[r] for r in range(10)],'full star factorization')
        for group,d,field in ((499,r499,'point_R499_scaled'),(572,r572,'point_R572_scaled')):
            key=tuple(d)
            if key not in point_cache:point_cache[key]=own.bound(key,own.C,own.C)
            lo,hi=point_cache[key];sl,sh=map(int,record[field])
            need(Q(sl,scale)<=lo<=hi<=Q(sh,scale),'fresh rational interaction interval within source128')
            sign='zero' if not any(d) else 'negative' if hi<0 else 'positive' if lo>0 else 'unresolved'
            cross_signs[group][sign]+=1
        need([a['state_index'] for a in record['active_candidates']]==list(range(4,8)),'exact four active states')
        for active in record['active_candidates']:
            state=active['state_index'];need(active['bits']==STATES[state],'active state bits')
            key=tuple(deltas[state]);buckets[key]+=1;first.setdefault(key,[axis,state])
            if key not in point_cache:point_cache[key]=own.bound(key,own.C,own.C)
            lo,hi=point_cache[key];sl,sh=map(int,active['point_energy_scaled'])
            need(Q(sl,scale)<=lo<=hi<=Q(sh,scale),'fresh rational full energy inside source128')
            outcome='strict_improvement_at_test_C' if sh<0 else 'identically_zero' if not any(key) else 'nonnegative_at_test_C' if sl>=0 else 'unresolved_at_test_C'
            need(active['outcome']==outcome,'exact source endpoint classification')
            if outcome=='strict_improvement_at_test_C':need(hi<0,'independent strict gain');negatives.append([axis,state])
            elif outcome=='nonnegative_at_test_C':need(lo>=0,'independent nonnegative point')
            elif outcome=='unresolved_at_test_C':unresolved+=1
            if minimum is None or lo<minimum[0]:minimum=(lo,hi,axis,state,key,active['point_energy_scaled'])
    need(seen_axes==set(old_pairs) and len(seen_charts)==len(seen_ordinals)==1022,'complete nearest bridge coverage')
    need(all(d==minimum[4] or point_cache[d][0]>=minimum[1] for d in buckets),'certified global point minimum, allowing identical-polynomial ties')
    patterns=result['patterns'];need(len(patterns)==len(buckets),'lossless polynomial buckets')
    certs=Counter();domain_complete=True
    for pattern in patterns:
        d=tuple(pattern['delta']);need(pattern['count']==buckets[d] and pattern['first_witness']==first[d],'bucket multiplicity/witness')
        cert=pattern.get('domain_certificate',{});kind=cert.get('kind');certs[kind]+=1
        if kind=='identically_zero':need(not any(d),'zero certificate')
        elif kind=='concave_dominance':
            values=[sum(d[r]*min(r,k) for r in range(1,10)) for k in range(1,10)]
            need(values==cert['values'] and min(values)>=0,'exact concave dominance')
        elif kind in ('nonnegative_direct_intervals','nonnegative_derivative_from_zero'):
            pieces=cert['subdivisions'];need(pieces in (16,128),'declared subdivisions')
            derivative=kind=='nonnegative_derivative_from_zero'
            if derivative:need(sum(r*d[r] for r in range(1,10))==0,'zero initial mass')
            least=min(own.bound(d,Q(i,200*pieces),Q(i+1,200*pieces),derivative)[0] for i in range(pieces))
            need(least>=0 and Q(int(cert['minimum_scaled_lower']),scale)<=least,'fresh independent uniform interval certificate')
        else:need(kind in (None,'unresolved_on_full_domain'),'known certificate kind');domain_complete=False
    need(result['declared_bridge_charts']==result['completed_bridge_charts']==1022,'bridge coverage fields')
    need(result['declared_active_candidates']==result['completed_active_candidates']==4088,'active coverage fields')
    need(result['candidate_coverage_complete'] and result['processing_complete'],'completed process')
    need(result['domain_nonnegative_certificate_complete']==domain_complete,'full domain completeness')
    need(result['certified_negative_count']==len(negatives) and result['first_certified_negative']==(negatives[0] if negatives else None),'negative count/first')
    need(result['point_unresolved_candidates']==unresolved,'unresolved count')
    need(result['mincut_used'] is False and result['native_emitter_executed'] is False and result['compiler_executed'] is False and result['new_kappa'] is None,'execution scope')
    expected='EXACT_STAR_IMPROVEMENT_FOUND' if negatives else 'NO_STAR_IMPROVEMENT_ON_DECLARED_DOMAIN' if domain_complete else 'NO_STAR_IMPROVEMENT_AT_TEST_C' if not unresolved else 'INCONCLUSIVE_EXACT_POINT_SIGN'
    need(result['status']==expected,'scoped final status')
    need(original['all_original_zero_paid_edges_preserved_under_group_assignments'],'all original zero contacts preserved')
    receipt=dict(status='PASS_INDEPENDENT_STAR_RECEIPT',author_result_sha256=sha256(raw).hexdigest(),author_status=result['status'],
      source_graph_sha256=original['graph_sha256'],bridge_charts_checked=1022,active_candidates_checked=4088,
      complete_profiles_checked=profiles_checked,exact_rank_entries_checked=rank_entries,
      polynomial_buckets=len(buckets),uniform_certificate_kinds=dict(certs),domain_nonnegative_complete=domain_complete,
      strict_negative_candidates=negatives,point_unresolved_candidates=unresolved,
      point_minimum=dict(axis=minimum[2],state=minimum[3],bits=STATES[minimum[3]],delta=minimum[4],
        independent_interval_scale=str(1<<160),
        independent_scaled_lower=str((minimum[0]*(1<<160)).numerator//(minimum[0]*(1<<160)).denominator),
        independent_scaled_upper=str(-(-(minimum[1]*(1<<160)).numerator//(minimum[1]*(1<<160)).denominator)),
        source_scaled=minimum[5]),
      interaction_sign_counts={g:dict(v) for g,v in cross_signs.items()},
      baseline_paid=dict(sorted(base_paid.items())),baseline_helpers=dict(sorted(base_helpers.items())),
      all_original_zero_paid_rows_preserved=True,new_neighbors_generated=False,source_runtime_imported=False,
      native_compiler_or_outer_transfer_admitted=False,
      execution_receipt_sha256=sha256((AUTHOR/'RUN-RECEIPT.json').read_bytes()).hexdigest(),
      execution_exit_code=run['exit_code'],execution_inputs_unchanged=True)
    (HERE/'STAR-RECEIPT-REVIEW.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ['status','author_status','bridge_charts_checked','active_candidates_checked','complete_profiles_checked','exact_rank_entries_checked','polynomial_buckets','uniform_certificate_kinds','domain_nonnegative_complete']},sort_keys=True))

if __name__=='__main__':main()
