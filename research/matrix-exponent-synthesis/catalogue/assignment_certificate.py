"""Exact dual certificates for quantized fixed-DAG carrier assignments.

Discovery uses the community's SciPy assignment idea. Verification below uses
only integer/rational standard-library arithmetic. Actual signed profile costs
are enclosed with the inherited logarithm/Taylor-Pade method. Optimality is
for a pinned graph and quantized objective; true-cost regret is bounded, not
declared zero. No all-network, kappa or multiplication theorem is proved.
"""
from pathlib import Path
from fractions import Fraction as Q
from functools import lru_cache
from collections import deque
import argparse, hashlib, json, math, struct, sys, time

HERE=Path(__file__).resolve().parent
DEFAULT_EDGES=HERE/'inputs/matching/h23-even-edges.txt'
SCIPY=HERE.parent.parent/'community-synthesis/matching/python-packages'
PROFILE_SOURCE='b7194b8586844956904b33e9fe18f0c75606c11b'
SWAP_COMPONENT_SOURCE='117caf164e3b235ef20188aa2dc1b49617e9255c'


def need(condition,message):
    if not condition: raise ValueError(message)


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@lru_cache(None)
def log_bounds(x):
    """Inherited 32-term atanh log enclosure; no floating logarithm."""
    x=Q(x);need(x>=1,'log input must be at least one'); k=0
    while x>2: x/=2;k+=1
    def small(y):
        z=(y-1)/(y+1)
        lower=2*sum((z**(2*j+1)/Q(2*j+1) for j in range(32)),Q())
        return lower,lower+2*z**65/(65*(1-z*z))
    lo,hi=small(x);lo2,hi2=small(Q(2));lo+=k*lo2;hi+=k*hi2
    scale=10**30
    return Q((lo*scale).numerator//(lo*scale).denominator,scale),Q(-(-(hi*scale).numerator//(hi*scale).denominator),scale)


@lru_cache(None)
def power_weight_bounds(t,m,a):
    # F_t = t*exp(a*ln(m/t)) = m^a*t^(1-a).
    lo,hi=log_bounds(Q(m,t));u,v=a*lo,a*hi
    need(0<=u<=v<1,'exponential enclosure domain')
    return t*(1+u+u*u/2+u*u*u/6),t*(1+v+v*v/(2*(1-v/3)))


def parse_instance(path,a,m,scale):
    raw=[];donors=set();uses=set();h=None
    for line in Path(path).read_text().splitlines():
        p=line.split();x,e,j=map(int,p[:3])
        delta=tuple(sorted((int(t),int(c)) for t,c in (v.split(':') for v in p[3:])))
        rank=sum(t*c for t,c in delta)
        if h is None:h=-rank
        need(rank==-h and h>0,'edge changed a different whole carrier rank')
        raw.append((x,e,j,delta));donors.add(x);uses.add(j)
    need(raw,'empty carrier instance')
    donors=sorted(donors);uses=sorted(uses)
    di={x:i for i,x in enumerate(donors)};ui={x:i for i,x in enumerate(uses)}
    cache={};edges=[];seen={}
    for x,e,j,delta in raw:
        if delta not in cache:
            lower,upper=Q(),Q()
            for t,c in delta:
                need(0<t<m,'invalid child width')
                lo,hi=power_weight_bounds(t,m,a)
                lower+=c*(lo if c>=0 else hi)
                upper+=c*(hi if c>=0 else lo)
            middle=(lower+upper)/2*scale
            quantized=middle.numerator//middle.denominator
            cache[delta]=(lower,upper,quantized)
        lower,upper,quantized=cache[delta]
        key=di[x],ui[j]
        if key in seen:
            need(seen[key]==(e,delta),'ambiguous parallel carrier edge')
            continue
        seen[key]=(e,delta)
        edges.append(dict(row=di[x],column=ui[j],donor=x,use=e,delta=delta,
                          lower=lower,upper=upper,q=quantized))
    minimum=min(edge['q'] for edge in edges);maximum=max(edge['q'] for edge in edges)
    costrange=maximum-minimum;nd=len(donors);nu=len(uses)
    penalty=nd*costrange+1
    for edge in edges:edge['cost']=edge['q']-minimum
    return dict(edges=edges,donors=donors,uses=uses,nd=nd,nu=nu,nc=nu+nd,h=h,
                scale=scale,a=a,m=m,minimum=minimum,range=costrange,penalty=penalty,
                raw_edges=len(raw),unique_delta_profiles=len(cache))


def all_rows(instance):
    rows=[[] for _ in range(instance['nd'])]
    for edge in instance['edges']:rows[edge['row']].append((edge['column'],edge['cost']))
    for i,row in enumerate(rows):row.append((instance['nu']+i,instance['penalty']))
    return rows


def discover(instance):
    sys.path.insert(0,str(SCIPY))
    import numpy as np
    from scipy.sparse import csr_matrix
    from scipy.sparse.csgraph import min_weight_full_bipartite_matching
    rr=[];cc=[];ww=[]
    for i,row in enumerate(all_rows(instance)):
        for j,c in row:rr.append(i);cc.append(j);ww.append(c+1)
    # Every full assignment uses nd edges: +1 is objective-constant and avoids
    # sparse zero-weight removal. Integers remain below 2^53 in this instance.
    need(max(ww)<2**53,'discovery integers too large for an exact double representation')
    matrix=csr_matrix((np.asarray(ww,dtype=float),(rr,cc)),shape=(instance['nd'],instance['nc']))
    ri,ci=min_weight_full_bipartite_matching(matrix)
    need(ri.tolist()==list(range(instance['nd'])),'assignment omitted a donor row')
    return ci.tolist()


def dual_potentials(instance,selected):
    rows=all_rows(instance);nd,nc=instance['nd'],instance['nc']
    need(len(selected)==nd and len(set(selected))==nd,'assignment columns not injective')
    graph=[[] for _ in range(nc)]
    assigned_costs=[]
    for i,k in enumerate(selected):
        costs=dict(rows[i]);need(k in costs,'selected carrier/dummy is ineligible')
        ck=costs[k];assigned_costs.append(ck)
        graph[k].extend((j,c-ck) for j,c in rows[i])
    # Difference constraints v_j-v_assigned <= c_ij-c_i,assigned. All initial
    # zeros enforce v<=0, and unassigned columns have no outgoing edges.
    v=[0]*nc;queue=deque(k for k in selected);queued=[False]*nc
    for k in queue:queued[k]=True
    enqueues=[0]*nc;relaxations=0
    while queue:
        k=queue.popleft();queued[k]=False
        for j,difference in graph[k]:
            proposal=v[k]+difference
            if proposal<v[j]:
                v[j]=proposal;relaxations+=1
                if not queued[j]:
                    queue.append(j);queued[j]=True;enqueues[j]+=1
                    need(enqueues[j]<=nc,'candidate may contain an improving negative cycle')
    used=set(selected)
    need(all(v[j]==0 for j in range(nc) if j not in used),
         'candidate has an improving alternating path to an unused column')
    u=[c-v[k] for c,k in zip(assigned_costs,selected)]
    return u,v,relaxations


def verify_integer_dual(instance,selected,u,v):
    rows=all_rows(instance);nd,nc=instance['nd'],instance['nc']
    need(len(u)==nd and len(v)==nc and len(selected)==nd,'dual/assignment shape mismatch')
    need(all(type(x)is int for x in u+v+selected),'integer certificate required')
    need(all(x<=0 for x in v),'column prices must be nonpositive')
    need(len(set(selected))==nd,'assignment not injective')
    primal=0;constraints=0;used=set(selected)
    for i,row in enumerate(rows):
        costs=dict(row);need(selected[i] in costs,'selected edge not in fixed graph')
        primal+=costs[selected[i]]
        need(u[i]+v[selected[i]]==costs[selected[i]],'selected edge not dual-tight')
        for j,c in row:
            need(u[i]+v[j]<=c,'dual infeasible on an eligible edge')
            constraints+=1
    need(all(v[j]==0 for j in range(nc) if j not in used),'unused price violates complementary slackness')
    dual=sum(u)+sum(v);need(primal==dual,'primal-dual gap is nonzero')
    cardinality=sum(k<instance['nu'] for k in selected)
    need(instance['penalty']>nd*instance['range'],'dummy penalty does not force maximum cardinality')
    return dict(integer_primal=primal,integer_dual=dual,duality_gap=0,
                all_edge_inequalities=constraints,selected_edges=nd,
                maximum_cardinality=cardinality,private_dummies=nd-cardinality)


def true_cost_interval(instance,selected):
    lookup={(edge['row'],edge['column']):edge for edge in instance['edges']}
    chosen=[lookup[i,k] for i,k in enumerate(selected) if k<instance['nu']]
    K=len(chosen);S=instance['scale']
    qsum=sum(edge['q'] for edge in chosen)
    lower=sum((edge['lower'] for edge in chosen),Q())
    upper=sum((edge['upper'] for edge in chosen),Q())
    errors_low=[edge['lower']-Q(edge['q'],S) for edge in instance['edges']]
    errors_hi=[edge['upper']-Q(edge['q'],S) for edge in instance['edges']]
    universal_lower=Q(qsum,S)+K*min(errors_low)
    regret=upper-universal_lower
    need(regret>=0,'invalid quantization regret enclosure')
    # This lower bound applies to every maximum-cardinality matching of this
    # pinned graph, via integer dual optimality plus the per-edge intervals.
    return dict(selected_true_cost_lower=str(lower),selected_true_cost_upper=str(upper),
                all_maxcard_true_cost_lower_bound=str(universal_lower),
                selected_true_cost_regret_upper=str(regret),
                regret_display=float(regret),quantization_scale=S,
                raw_power_objective_regret_upper=str(regret),
                raw_power_objective_units='sum delta[t]*t^(1-a); this bound is conservative because scaled objective is m^a times raw',
                normalized_axis_profile_regret_upper=str(regret/instance['m']),
                normalized_axis_profile_regret_display=float(regret/instance['m']),
                normalized_axis_profile_units='sum delta[t]*(t/m)^(1-a), before division by W and axis repeat',
                per_edge_error_low_min=str(min(errors_low)),
                per_edge_error_high_max=str(max(errors_hi)),
                true_unrounded_optimality=False,
                objective='sum signed_delta[t] * t * exp(a*ln(m/t)); fixed-DAG maximum-cardinality carriers',
                normalized_internal_moment_regret_formula='axis_repeat * regret / (m * fixed_W); external/rank costs unchanged at fixed cardinality')


def certificate(path,a,m,scale):
    start=time.perf_counter();instance=parse_instance(path,a,m,scale)
    selected=discover(instance);u,v,relaxations=dual_potentials(instance,selected)
    checked=verify_integer_dual(instance,selected,u,v)
    true_bounds=true_cost_interval(instance,selected)
    return dict(status='exact_integer_dual_optimality_certified',
        edge_file_name=Path(path).name,edge_sha256=sha(path),
        certificate_tool_sha256=sha(__file__),
        profile_source_commit=PROFILE_SOURCE,component_swap_source_commit=SWAP_COMPONENT_SOURCE,
        exact_saving=str(a),parent_width=m,quantization_scale=scale,
        quantization='floor midpoint of rigorous rational cost interval times scale',
        raw_edges=instance['raw_edges'],eligible_edges=len(instance['edges']),
        donors=instance['nd'],real_use_columns=instance['nu'],private_dummy_columns=instance['nd'],
        whole_carrier_rank=instance['h'],unique_delta_profiles=instance['unique_delta_profiles'],
        integer_cost_shift=instance['minimum'],integer_cost_range=instance['range'],
        integer_dummy_penalty=instance['penalty'],checked=checked,true_cost_bounds=true_bounds,
        selected_columns=selected,row_potentials=u,column_potentials=v,
        constraint_relaxations=relaxations,elapsed_seconds=round(time.perf_counter()-start,3),
        discovery='SciPy float proposal on exactly represented integer costs; proposal is not trusted',
        verification='all integer dual inequalities, injectivity, selected tightness, unused prices and exact objective equality',
        mathematical_scope='quantized fixed-DAG assignment optimum and rigorous true-cost regret bound; not all-network or kappa optimality',
        attribution='Rohan Arun community weighted-matching discovery; inherited PR48 projector profile and rational enclosure method; local exact-dual checking added',
        no_external_write=True)


def replay(path,certificate_path):
    c=json.loads(Path(certificate_path).read_text())
    need(sha(path)==c['edge_sha256'],'edge instance changed')
    instance=parse_instance(path,Q(c['exact_saving']),c['parent_width'],c['quantization_scale'])
    need((instance['minimum'],instance['range'],instance['penalty'])==
         (c['integer_cost_shift'],c['integer_cost_range'],c['integer_dummy_penalty']),
         'quantization/penalty source mismatch')
    checked=verify_integer_dual(instance,c['selected_columns'],c['row_potentials'],c['column_potentials'])
    need(checked==c['checked'],'integer certificate receipt mismatch')
    bounds=true_cost_interval(instance,c['selected_columns'])
    need(bounds==c['true_cost_bounds'],'true-cost interval receipt mismatch')
    return dict(status='independent_stdlib_replay_passed',checked=checked,
                regret_bound=bounds['selected_true_cost_regret_upper'],edge_sha256=sha(path),
                certificate_sha256=sha(certificate_path))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--edges',type=Path,default=DEFAULT_EDGES)
    ap.add_argument('--saving',default='82375901/2000000000000')
    ap.add_argument('--width',type=int,default=575)
    ap.add_argument('--scale',type=int,default=10**12)
    ap.add_argument('--output',type=Path,default=HERE/'fixed-dag-dual-certificate.json')
    ap.add_argument('--verify',type=Path)
    args=ap.parse_args()
    if args.verify:
        print(json.dumps(replay(args.edges,args.verify),indent=2));return
    result=certificate(args.edges,Q(args.saving),args.width,args.scale)
    with args.output.open('x',encoding='utf-8') as stream:json.dump(result,stream,indent=2);stream.write('\n')
    small={k:result[k] for k in ('status','edge_file_name','edge_sha256','donors','real_use_columns',
        'eligible_edges','exact_saving','parent_width','checked','elapsed_seconds','mathematical_scope')}
    small['true_cost_regret_upper_display']=result['true_cost_bounds']['regret_display']
    small['normalized_axis_profile_regret_display']=result['true_cost_bounds']['normalized_axis_profile_regret_display']
    small['certificate_sha256']=sha(args.output)
    print(json.dumps(small,indent=2))


if __name__=='__main__':main()
