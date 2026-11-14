"""Independent full-point capacity/flow/cut checker; no orbit author code imports."""
from collections import Counter
from itertools import product
from math import isqrt, prod
from pathlib import Path
from functools import lru_cache
import argparse, copy, hashlib, json

H=((1,1,1,1),(1,-1,1,-1),(1,1,-1,-1),(1,-1,-1,1))
Q=1<<128

def need(ok,why):
    if not ok: raise ValueError(why)

def key(v):
    return tuple(sorted(map(abs,v))), (None if 0 in v else (1 if prod(v)>0 else -1))
def decode(k):return tuple(k[0]),k[1]
def n2(v):return sum(a*a for a in v)
def ball(r):
    pairs=[(a,b) for a in range(-r,r+1) for b in range(-r,r+1) if a*a+b*b<=r*r]
    return [(a,b,c,d) for a,b in pairs for c,d in pairs if a*a+b*b+c*c+d*d<=r*r]
def neighbors(x):
    hx=tuple(sum(a*b for a,b in zip(row,x)) for row in H)
    need(len({t%2 for t in hx})==1,'common image parity')
    if hx[0]%2:
        for bits in product((0,1),repeat=4):yield tuple(t//2+b for t,b in zip(hx,bits))
    else:
        y=tuple(t//2 for t in hx);yield y
        for i in range(4):
            for s in (-1,1):
                z=list(y);z[i]+=s;yield tuple(z)
@lru_cache(None)
def interval(n):
    lo=isqrt(n*Q*Q);return lo,lo+(lo*lo!=n*Q*Q)
@lru_cache(None)
def gap(a,b):
    la,ua=interval(a);lb,ub=interval(b);return la-ub,ua-lb
@lru_cache(None)
def compare(edge,threshold):
    if edge==threshold:return 0
    lo,hi=gap(*edge);tl,th=gap(*threshold)
    if hi<tl:return -1
    if lo>th:return 1
    raise ValueError(('unseparated radicals',edge,threshold))
def verify_tables(record,xs,ys):
    maps=[]
    for side,points in [('inputs',xs),('candidate_outputs',ys)]:
        actual=Counter(key(v) for v in points)
        saved=record['orbit_capacity_tables'][side]
        need(len(saved)==len(actual),'exact number of orbit classes')
        klist=[decode(row['key']) for row in saved]
        need(len(set(klist))==len(klist),'duplicate orbit key')
        need(set(klist)==set(actual),'complete orbit class coverage')
        for row,k in zip(saved,klist):
            need(row['capacity']==actual[k],'orbit capacity by actual point count')
            need(row['norm_squared']==n2(k[0]),'orbit squared norm')
            if 'representative' in row:need(key(row['representative'])==k,'representative class')
        maps.append({k:i for i,k in enumerate(klist)})
    return maps

def active_edges(pairs,threshold,inclusive):
    return {(i,j) for (i,j),ab in pairs.items() if compare(ab,threshold)<0 or (inclusive and compare(ab,threshold)==0)}
def check_flow(record,receipt,active):
    rows=[0]*len(record['orbit_capacity_tables']['inputs']);cols=[0]*len(record['orbit_capacity_tables']['candidate_outputs']);seen=set()
    f=receipt['flow_certificate']
    for i,j,v in f['positive_orbit_pair_flows']:
        need(type(v)is int and v>0 and (i,j) in active,'positive active orbit flow')
        need((i,j) not in seen,'unique flow edge');seen.add((i,j));rows[i]+=v;cols[j]+=v
    need(rows==f['input_supplies'] and cols==f['output_loads'],'flow conservation')
    need(all(0<=v<=a['capacity'] for v,a in zip(rows,record['orbit_capacity_tables']['inputs'])),'input capacities')
    need(all(0<=v<=a['capacity'] for v,a in zip(cols,record['orbit_capacity_tables']['candidate_outputs'])),'output capacities')
    need(sum(rows)==sum(cols)==receipt['flow'],'flow value')
    if receipt['feasible']:need(rows==[a['capacity'] for a in record['orbit_capacity_tables']['inputs']],'all inputs saturated')
    return sum(rows)
def check_cut(record,receipt,active,im,om):
    cut=receipt['maximal_hall_cut']
    li=[decode(a['key']) for a in cut['input_orbits']];lo=[decode(a['key']) for a in cut['output_orbits']]
    need(len(set(li))==len(li) and len(set(lo))==len(lo),'cut key uniqueness')
    ii={im[k] for k in li};oo={om[k] for k in lo}
    need({j for i,j in active if i in ii}==oo,'complete cut neighborhood')
    tables=record['orbit_capacity_tables'];ni=sum(tables['inputs'][i]['capacity'] for i in ii);no=sum(tables['candidate_outputs'][j]['capacity'] for j in oo)
    need((ni,no,ni-no)==(cut['input_count'],cut['neighbor_count'],cut['deficiency']),'exact cut cardinalities')
    need(record['domain_and_graph']['input_count']-ni+no==receipt['flow'],'reported cut capacity')
    return ni,no

def rejection(fn,label):
    try:fn()
    except (ValueError,KeyError,IndexError):return
    raise ValueError('negative control accepted: '+label)

def verify(record):
    r=record['radius'];xs=ball(r);ys=set();raw=[];edge_total=0
    # Count every point and every candidate edge; no orbit capacity formula or representative generator.
    input_counts=Counter(key(x) for x in xs)
    for x in xs:
        kx=key(x);n=n2(x)
        for y in neighbors(x):
            ys.add(y);raw.append((kx,key(y),n2(y),n));edge_total+=1
    im,om=verify_tables(record,xs,ys)
    pairs={};pair_count=Counter()
    for ki,kj,a,b in raw:
        ij=(im[ki],om[kj]);need(ij not in pairs or pairs[ij]==(a,b),'constant norm gap within orbit pair');pairs[ij]=(a,b);pair_count[ij]+=1
    del raw
    domain=record['domain_and_graph'];need((len(xs),len(ys),edge_total)==(domain['input_count'],domain['error_one_candidate_output_count'],domain['error_one_edge_count']),'complete graph size')
    need(len(pairs)==domain['all_quotient_adjacencies'],'complete quotient adjacency')
    # Biregularity follows from the paired group action proved in the manuscript.
    # Exact edge counts must agree with integer degrees at both ends.
    for (i,j),c in pair_count.items():
        need(c%record['orbit_capacity_tables']['inputs'][i]['capacity']==0,'integral left degree')
        need(c%record['orbit_capacity_tables']['candidate_outputs'][j]['capacity']==0,'integral right degree')
    target=tuple(record['target_pair'])
    for name,inc in [('inclusive',True),('strict',False)]:
        receipt=record['target_threshold_tests'][name];act=active_edges(pairs,target,inc)
        check_flow(record,receipt,act);check_cut(record,receipt,act,im,om)
    opt=record['exact_finite_optimum'];delta=tuple(opt['optimum_pair']);upper=active_edges(pairs,delta,True);lower=active_edges(pairs,delta,False)
    need(opt['upper_flow']['feasible'],'saturating upper witness');check_flow(record,opt['upper_flow'],upper)
    ni,no=check_cut(record,opt['strict_lower_cut'],lower,im,om);need(ni>no,'strict Hall failure')
    # Deliberate corruptions exercise independent acceptance and complete-neighbor detection.
    bad=copy.deepcopy(opt['upper_flow']);bad['flow_certificate']['positive_orbit_pair_flows'][0][2]+=1
    rejection(lambda:check_flow(record,bad,upper),'changed positive flow')
    bad=copy.deepcopy(opt['strict_lower_cut']);bad['maximal_hall_cut']['output_orbits'].pop()
    rejection(lambda:check_cut(record,bad,lower,im,om),'missing neighbor orbit')
    # Treating the strict obstruction as inclusive must fail; this detects a wrong boundary convention.
    rejection(lambda:check_cut(record,opt['strict_lower_cut'],upper,im,om),'strict cut used at inclusive threshold')
    return {'radius':r,'inputs':len(xs),'candidate_outputs':len(ys),'error_one_edges':edge_total,'orbit_adjacencies':len(pairs),'optimum_pair':delta,'strict_cut':[ni,no],'strict_deficiency':ni-no,'negative_controls':3}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('receipt',type=Path,nargs='?',default=Path(__file__).resolve().parents[2]/'orbit-extension/RESULT.json');args=ap.parse_args();b=args.receipt.read_bytes();receipt=json.loads(b)
    need(receipt['operator']==[list(row) for row in H],'operator')
    rows=[verify(r) for r in receipt['completed_radii']]
    need([r['radius'] for r in rows]==[6,7,9,11],'bounded scope')
    print(json.dumps({'status':'PASS_INDEPENDENT_FULL_POINT_CERTIFICATES','receipt_sha256':hashlib.sha256(b).hexdigest(),'verified':rows,'method':'full individual-point and edge enumeration, actual class counts, 128-bit rational radical intervals, direct certificate conservation and complete Hall neighborhoods; imports no author code'},indent=2))
if __name__=='__main__':main()
