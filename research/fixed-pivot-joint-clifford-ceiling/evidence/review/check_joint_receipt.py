#!/usr/bin/env python3
"""Independent verification of the already recorded3066 candidates.

No neighbor search, source-model import, native circuit or compiler executes.
Exact powers use a fresh rational negative-exp enclosure, not source128 code.
"""
from collections import Counter,defaultdict
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import importlib.util
import json
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
AUTHOR=ROOT/'outputs/joint-clifford-design-20261023'
RESULT_SHA='d2ea1bd88173a46d8fa59c2958ef234ae9811e44c677aadf012423e77cbf78a9'
CODE_SHA='575136ee932e697c97b8a15d2edc1f5ab159de482c66c01a6f211a9dfd301630'
C=Q(15108879,5000000000)


def need(ok,why):
    if not ok:raise RuntimeError(why)


def rank(rows):
    pivots={}
    for value in rows:
        while value:
            bit=value.bit_length()-1
            if bit in pivots:value^=pivots[bit]
            else:pivots[bit]=value;break
    return len(pivots)


def canonical(rows):
    rows=list(rows);i=0
    for bit in range(17,-1,-1):
        p=next((j for j in range(i,len(rows))if rows[j]>>bit&1),None)
        if p is None:continue
        rows[i],rows[p]=rows[p],rows[i]
        for j in range(len(rows)):
            if j!=i and rows[j]>>bit&1:rows[j]^=rows[i]
        i+=1
    return tuple(rows[:i])


def pairing(x,y):
    return (((x&511)&(y>>9)).bit_count()+((x>>9)&(y&511)).bit_count())%2


def transvection(chart,axis):
    return canonical(x^(axis if pairing(x,axis)else 0)for x in chart)


def image(columns,value):
    out=0
    for i,c in enumerate(columns):
        if value>>i&1:out^=c
    return out


def edge_rank(edge,assignment,maps):
    a,b,op,sgn=edge
    left=assignment[a]
    if op>=0:left=tuple(image(maps[op],x)for x in left)
    return rank((*left,*assignment[b]))-len(left)


@lru_cache(maxsize=None)
def logs(r):
    def series(z):
        N=64
        lo=sum((2*z**(2*i+1)/Q(2*i+1)for i in range(N)),Q())
        return lo,lo+2*z**(2*N+1)/((2*N+1)*(1-z*z))
    k=r.bit_length()-1;t=Q(r,1<<k)
    a,b=series((t-1)/(t+1));c,d=series(Q(1,3))
    return a+k*c,b+k*d


def negexp(x,n):
    need(0<=x<Q(1,50),'negative exp range')
    term,total=Q(1),Q(1)
    for i in range(1,n+1):term*=-x/i;total+=term
    return total


@lru_cache(maxsize=None)
def powers(r,c):
    need(1<=r<=9 and 0<=c<=Q(1,200),'power domain')
    if r==1 or c==0:return Q(r),Q(r)
    lo,hi=logs(r)
    return r*negexp(c*hi,21),r*negexp(c*lo,22)


def bound(delta,a,b,derivative=False):
    lo=hi=Q()
    for r in range(1,10):
        l,u=powers(r,b)[0],powers(r,a)[1];coef=delta[r]
        if derivative:l*=logs(r)[0];u*=logs(r)[1];coef=-coef
        lo+=coef*(l if coef>=0 else u)
        hi+=coef*(u if coef>=0 else l)
    return lo,hi


def main():
    raw=(AUTHOR/'SEARCH-RESULT.json').read_bytes()
    need(sha256(raw).hexdigest()==RESULT_SHA,'recorded result pin')
    need(sha256((AUTHOR/'check_joint.py').read_bytes()).hexdigest()==CODE_SHA,'search checker pin')
    result=json.loads(raw)
    run_raw=(AUTHOR/'RUN-RECEIPT.json').read_bytes();run=json.loads(run_raw)
    need(run['before']==run['after'] and run['inputs_unchanged'],'search before/after inputs unchanged')
    for name,digest in run['before'].items():
        need(sha256((AUTHOR/name).read_bytes()).hexdigest()==digest,'execution bound input '+name)
    need(run['output_sha256']==RESULT_SHA and run['exit_code']==0,'successful bound execution receipt')
    need(run['external_hard_cap_seconds']==60 and run['internal_cooperative_cap_seconds']==58,'one authorized cap')
    need(sha256((AUTHOR/'SEARCH-STDOUT.txt').read_bytes()).hexdigest()==run['stdout_sha256'],'stdout hash')
    need(sha256((AUTHOR/'SEARCH-STDERR.txt').read_bytes()).hexdigest()==run['stderr_sha256'],'stderr hash')
    for name,digest in result['source_input_hashes'].items():
        need(sha256((AUTHOR/name).read_bytes()).hexdigest()==digest,'frozen source '+name)
    # Execute only this review's independent source-data reconstruction.
    spec=importlib.util.spec_from_file_location('own_graph_binding',HERE/'verify_graph_binding.py')
    own=importlib.util.module_from_spec(spec);spec.loader.exec_module(own)
    binding=own.reconstruct()
    graph=(AUTHOR/'inputs/contracted-graph.txt').read_bytes()
    need(sha256(graph).hexdigest()==binding['graph_sha256']==result['graph_sha256'],'full source binding')
    rows=graph.decode().splitlines();n,m,k=map(int,rows[0].split())
    charts=[tuple(map(int,row.split()[1:]))for row in rows[1:n+1]]
    frozen={i for i,row in enumerate(rows[1:n+1])if int(row.split()[0])}
    maps=[tuple(map(int,row.split()))for row in rows[n+1:n+1+k]]
    edges=[tuple(map(int,row.split()))for row in rows[n+1+k:]]
    need(len(edges)==m==3938,'complete signed incidence list')
    base_paid=Counter({8:8});base_helpers=Counter();base_ranks=[]
    for e in edges:
        r=edge_rank(e,charts,maps);base_ranks.append(r)
        if e[3]<0:need(r>0,'every baseline helper strictly productive');base_helpers[r]+=1
        elif r:base_paid[r]+=1
    ints=lambda d:{int(r):v for r,v in d.items()if v}
    need(dict(base_paid)==ints(result['baseline_paid'])and dict(base_helpers)==ints(result['baseline_helpers']),'complete baseline')
    pivot,axis=result['pivot'];need((pivot,axis)==(499,7),'declared pivot')
    pivot_chart=transvection(charts[pivot],axis)
    need(list(pivot_chart)==result['pivot_chart'],'independent pivot transvection')
    partners=[172,497,504];need(result['partners']==partners,'declared partner set')
    outside={};unions={}
    for partner in partners:
        need(partner not in frozen and pivot not in frozen,'frozen boundaries')
        union={i for i,e in enumerate(edges)if pivot in e[:2]or partner in e[:2]}
        unions[partner]=sorted(union);p,h=Counter({8:8}),Counter()
        for eid,e in enumerate(edges):
            if eid in union:continue
            rr=base_ranks[eid]
            if e[3]<0:h[rr]+=1
            elif rr:p[rr]+=1
        outside[partner]=(p,h)
    # Consequence of independently checked source partition: every omitted
    # original zero row stays zero for these common group-chart assignments.
    need(binding['all_original_zero_paid_edges_preserved_under_group_assignments'],'original zero rows')
    records=result['candidates'];need(len(records)==3066,'complete receipt candidate count')
    seen_charts=defaultdict(set);seen_ordinals=defaultdict(set);buckets=Counter();first={}
    point_cache={};all_deltas=[];checked_rank_entries=0;profiles_checked=0
    cross_sign_counts=Counter();minimum=None
    scale=int(result['scale']);need(scale==1<<128,'128-bit receipt scale')
    for row in records:
        partner=row['partner'];need(partner in partners,'unexpected partner')
        ordinal=row['neighbor_ordinal'];alt=tuple(row['partner_chart']);move=row['partner_axis']
        need(0<=ordinal<1022 and ordinal not in seen_ordinals[partner],'unique ordinal')
        need(0<move<1<<18 and alt==transvection(charts[partner],move),'independent partner transvection')
        need(len(alt)==rank(alt)==9 and all(not pairing(a,b)for a in alt for b in alt),'valid partner Lagrangian')
        need(rank((*charts[partner],*alt))-9==1 and alt not in seen_charts[partner],'unique nearest neighbor')
        seen_charts[partner].add(alt);seen_ordinals[partner].add(ordinal)
        need(row['states']==['00','10','01','11'],'state order')
        need([x['id']for x in row['incidences']]==unions[partner],'all incidence IDs once, preserving parallel rows')
        deltas=[[0]*10 for _ in range(4)];valid=[True]*4
        state_profiles=[]
        for state in range(4):
            assignment=list(charts)
            if state in (1,3):assignment[pivot]=pivot_chart
            if state in (2,3):assignment[partner]=alt
            paid,helper=(Counter(x)for x in outside[partner])
            for data in row['incidences']:
                eid=data['id'];e=edges[eid]
                a,b,op,sgn=e
                # Receipt uses literal op labels; current domain is identity.
                need((a,b,sgn)==(data['a'],data['b'],data['sign']),'ordered endpoints/sign')
                need((op==-1)==(data['op']==0),'identity/warp convention')
                rr=edge_rank(e,assignment,maps);checked_rank_entries+=1
                need(rr==data['ranks'][state],'independent exact four-state incidence rank')
                old=base_ranks[eid]
                if old:deltas[state][old]-=sgn
                if rr:deltas[state][rr]+=sgn
                if sgn<0:
                    if rr==0:valid[state]=False
                    helper[rr]+=1
                elif rr:paid[rr]+=1
            need(all(c>=0 for c in paid.values())and all(c>=0 for c in helper.values()),'nonnegative complete invoice')
            need(sum(helper.values())==408 and 0 not in helper,'all408helpers once, strictly productive')
            state_profiles.append((dict(sorted(paid.items())),dict(sorted(helper.items()))));profiles_checked+=1
        need(valid==row['valid_states']==[True]*4,'all state helper feasibility')
        need(deltas==row['energy_deltas']and not any(deltas[0])and not any(deltas[1]),'all signed integer polynomials')
        paid,helpers=state_profiles[3]
        need(paid==ints(row['joint_paid'])and helpers==ints(row['joint_helpers']),'complete joint paid/helper profile')
        delta=tuple(deltas[3]);cross=tuple(deltas[3][r]-deltas[1][r]-deltas[2][r]+deltas[0][r]for r in range(10))
        need(list(cross)==row['cross_difference'],'exact cross difference')
        for coeffs,field in ((delta,'point_energy_scaled'),(cross,'point_cross_scaled')):
            if coeffs not in point_cache:point_cache[coeffs]=bound(coeffs,C,C)
            lo,hi=point_cache[coeffs];stored_lo,stored_hi=map(int,row[field])
            need(Q(stored_lo,scale)<=lo<=hi<=Q(stored_hi,scale),'fresh rational point bound inside source128 enclosure')
        need(point_cache[delta][0]>0 and row['outcome']=='nonnegative_at_test_C','strict positive point energy')
        cross_lo,cross_hi=point_cache[cross]
        if not any(cross):cross_sign_counts['zero']+=1
        elif cross_hi<0:cross_sign_counts['negative']+=1
        elif cross_lo>0:cross_sign_counts['positive']+=1
        else:raise RuntimeError('independent cross sign unresolved')
        if minimum is None or point_cache[delta][0]<minimum[0]:
            minimum=(point_cache[delta][0],partner,move,delta,row['point_energy_scaled'])
        buckets[delta]+=1;first.setdefault(delta,[partner,move]);all_deltas.append(delta)
    need(all(len(seen_charts[p])==len(seen_ordinals[p])==1022 for p in partners),'all nearest domains covered')
    # There are exactly1022 nearest Lagrangians by the511-hyperplane/two-line
    # quotient argument. Distinctness and distance one establish full coverage.
    patterns=result['patterns'];need(len(patterns)==len(buckets)==24,'lossless complete pattern buckets')
    certificates=[]
    for p in patterns:
        d=tuple(p['delta']);need(p['count']==buckets[d]and p['first_witness']==first[d],'bucket multiplicity/witness')
        cert=p['domain_certificate'];kind=cert['kind']
        if kind=='concave_dominance':
            values=[sum(d[r]*min(r,j)for r in range(1,10))for j in range(1,10)]
            need(values==cert['values']and min(values)>=0,'exact discrete concave dominance')
            certificates.append({'delta':d,'count':buckets[d],'kind':kind,'values':values})
        elif kind in ('nonnegative_direct_intervals','nonnegative_derivative_from_zero'):
            pieces=cert['subdivisions'];need(pieces in (16,128),'declared subdivisions')
            derivative=kind=='nonnegative_derivative_from_zero'
            if derivative:need(sum(r*d[r]for r in range(1,10))==0,'exact zero initial rank mass')
            interval_bounds=[bound(d,Q(i,200*pieces),Q(i+1,200*pieces),derivative)for i in range(pieces)]
            least=min(x[0]for x in interval_bounds)
            need(least>0 and Q(int(cert['minimum_scaled_lower']),scale)<=least,'independent uniform interval proof')
            certificates.append({'delta':d,'count':buckets[d],'kind':kind,'subdivisions':pieces,
                                 'independent_lower_exceeds_source_scaled_lower':True,
                                 'source_scaled_lower':cert['minimum_scaled_lower']})
        else:raise RuntimeError('unproved domain pattern '+str(cert))
    need(result['status']=='NO_IMPROVEMENT_ON_DECLARED_DOMAIN'and result['candidate_coverage_complete']
         and result['processing_complete']and result['domain_nonnegative_certificate_complete'],'negative header consistent')
    need(result['certified_negative_count']==0 and result['point_unresolved_candidates']==0
         and result['first_certified_negative']is None,'no positive witness misclassification')
    # Synthetic incidence controls: selfloop must substitute both endpoints;
    # parallel duplicate rows count twice rather than once.
    z,x=(2,),(1,);swap=(2,1)
    selfloop_old=rank((image(swap,z[0]),*z))-1
    selfloop_both=rank((image(swap,x[0]),*x))-1
    selfloop_wrong_one=rank((image(swap,x[0]),*z))-1
    need((selfloop_old,selfloop_both,selfloop_wrong_one)==(1,1,0),'selfloop both-endpoint control')
    need(sum([selfloop_both,selfloop_both])==2 and selfloop_both!=2,'parallel incidence multiplicity control')
    need(rank((*x,*x))-1==0,'zero helper rank rejection control has invalid target')
    need(sha256((AUTHOR/'SEARCH-RESULT.json').read_bytes()).hexdigest()==RESULT_SHA,'result unchanged after review')
    output={'status':'PASS_INDEPENDENT_ALL3066_FOUR_STATE_TABLES_AND_SCOPED_NEGATIVE',
            'reviewed_result_sha256':RESULT_SHA,'checker_sha256':CODE_SHA,
            'run_receipt_sha256':sha256(run_raw).hexdigest(),
            'execution_receipt_bindings_verified':True,
            'source_graph_binding':binding,'candidates_independently_checked':len(records),
            'full_state_profiles_independently_checked':profiles_checked,
            'exact_incidence_rank_entries_independently_checked':checked_rank_entries,
            'four_state_profiles_method':'all unchanged source incidences summed once per partner, plus every candidate affected incidence; no sampled global checks',
            'patterns':certificates,'point_energy':'STRICTLY_POSITIVE_FOR_EVERY_RECORDED_CANDIDATE',
            'minimum_point_witness':{'partner':minimum[1],'axis':minimum[2],'delta':minimum[3],
                                     'source128_scaled_interval':minimum[4],'scale':str(scale)},
            'cross_difference_point_sign_counts':dict(cross_sign_counts),
            'saving_domain':['0','1/200'],'domain_result':'NONNEGATIVE_EVERY_CANDIDATE_ON_DECLARED_DOMAIN',
            'nearest_coverage':'1022distinctvalidneighbors per partner;511hyperplanes times2 quotient lines',
            'interval_method':'fresh64term rational log plus21/22term negative exp; no source interval engine imported',
            'generic_controls':{'selfloop_both_endpoints':'PASS','parallel_rows_charged_twice':'PASS','helper_zero':'INVALID_AS_REQUIRED'},
            'single_move_census_rerun':False,'candidate_search_rerun':False,'native_or_compiler_execution':False,
            'new_kappa':None}
    path=HERE/('JOINT-RECEIPT-REVIEW-OPTIMIZED.json'if sys.flags.optimize else 'JOINT-RECEIPT-REVIEW.json')
    path.write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({k:output[k]for k in ('status','candidates_independently_checked','full_state_profiles_independently_checked','exact_incidence_rank_entries_independently_checked')}))


if __name__=='__main__':main()
