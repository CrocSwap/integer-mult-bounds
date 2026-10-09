"""Shared aggregate diagnostic and a rank-metric producer-frontier bound.

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
No new finite multiplication network or exponent.
"""
from fractions import Fraction as Q
from pathlib import Path
from itertools import combinations
import argparse
import hashlib
import importlib.util
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


d=load('aggregate_design_helpers','research/hybrid-clean-design/design.py')
b=load('aggregate_budget_helpers','research/kappa-nine/target_budget.py')


def paired_readout(h):
    d.require(h>=6 and h not in (9,10),'nondegenerate paired-aggregate regime')
    ts=d.triples(h);S={0,1,2};T={0,1,3};G=d.metric(h)
    s=[int(len(set(R)&S)==1) for R in ts]
    t=[int(len(set(R)&T)==1) for R in ts]
    common=[x&y for x,y in zip(s,t)]
    us=[x^y for x,y in zip(s,common)]
    ut=[x^y for x,y in zip(t,common)]
    cs=[len(set(R)&S)%2 for R in ts]
    ct=[len(set(R)&T)%2 for R in ts]
    d.require(all((cs[i]^common[i]^us[i])==int(set(R)==S) and
                  (ct[i]^common[i]^ut[i])==int(set(R)==T) for i,R in enumerate(ts)),
              'complete scalar paired identity')
    Hs=d.sub(d.eye(h),d.projector([d.vector(S,h)],G))
    Ht=d.sub(d.eye(h),d.projector([d.vector(T,h)],G))
    K=d.projector([d.vector(R,h) for R,c in zip(ts,common) if c],G)
    expected=d.sub(d.eye(h),d.projector([d.vector(S,h),d.vector(T,h)],G))
    d.require(K==expected and d.rank(K)==h-2,'shared-neighbor span')
    Ls=d.projector([d.vector(R,h) for R,c in zip(ts,us) if c],G)
    Lt=d.projector([d.vector(R,h) for R,c in zip(ts,ut) if c],G)
    d.require(d.rank(Ls)==d.rank(Lt)==h-2,'unique aggregate dimensions')
    d.require(d.product(Hs,Ls)==Ls and d.product(Ht,Lt)==Lt,'unique aggregate containment')
    d.require(d.product(Hs,K)==K and d.product(Ht,K)==K,'nested paired readout')
    k=h-4
    d.require(sum(common)==k*k and sum(us)==sum(ut)==k*(k+3)//2,'support counts')
    d.require(d.rank([cs,ct,common,us,ut],2)==5,'nonzero independent local terms')
    widths=[d.rank(K),d.rank(K),d.rank(d.sub(Hs,K)),d.rank(d.sub(Ht,K)),
            d.rank(d.sub(Hs,Ls)),d.rank(d.sub(Ht,Lt))]
    d.require(widths==[h-2,h-2,1,1,1,1],'paired readout ranks')
    return dict(h=h,common_sources=sum(common),unique_sources_each=sum(us),
                scalar_input_basis_columns_checked=len(ts),local_form_rank=5,
                readout_widths=widths,readout_rank=sum(widths),unique_frame_rank=h-2,
                producer_supplied=False,
                scope='Includes natural unique-aggregate frame alignment; producer not supplied')


def source_distances(h=6):
    P=d.line_projectors(h)
    d.require(all(d.rank(A)==1 for A in P),'rank-one sources')
    d.require(all(d.rank(d.sub(A,B))==2 for A,B in combinations(P,2)),
              'separated source frames')
    return dict(h=h,sources=len(P),pairs_checked=len(P)*(len(P)-1)//2,
                pair_distance=2,zero_frontier_distance=1)


def forest_control(frames,edges,sources,roots):
    """Check a finite metric/DAG instance and emit a selected forest.

    Caller supplies a graph after removing identically zero streams.
    This verifies the geometry, not any unprovided scalar gate circuit.
    """
    d.require(all(u<v for u,v in edges),'topological numbering')
    for i,j in combinations(sources,2):
        d.require(d.rank(d.sub(frames[i],frames[j]))>=2,'source separation')
    for i in sources:
        for j in roots:
            d.require(d.rank(d.sub(frames[i],frames[j]))>=1,'root separation')
    reach=set(roots);choice={}
    for u in reversed(range(len(frames))):
        if u in roots:continue
        possible=sorted(v for a,v in edges if a==u and v in reach)
        if possible:choice[u]=possible[0];reach.add(u)
    d.require(set(sources)<=reach,'all sources must reach the frontier')
    selected=set();groups={}
    for source in sources:
        u=source
        while u not in roots:
            v=choice[u];selected.add((u,v));u=v
        groups.setdefault(u,[]).append(source)
    edge_cost=lambda e:d.rank(d.sub(frames[e[0]],frames[e[1]]))
    total=sum(map(edge_cost,edges));forest=sum(map(edge_cost,selected))
    d.require(total>=forest>=len(sources),'forest rank budget')
    return dict(sources=len(sources),total_edge_rank=total,forest_edge_rank=forest,
                selected_edges=sorted(selected),components={str(k):v for k,v in groups.items()},
                source_floor=len(sources))


def forest_examples():
    h=6;P=d.line_projectors(h);Z=[[Q(0)]*h for _ in range(h)]
    star=forest_control(P[:5]+[Z],[(i,5) for i in range(5)],list(range(5)),[5])
    d.require(star['total_edge_rank']==5,'sharp star control')
    # DAG: a=x0+x1, b=x1+x2, c=a+b, d=c+x3;
    # output0=d+x4, output1=b. Thus x1 cancels on one output but remains used.
    arbitrary=[[Q((i+1)*(j+2),7)+Q(i==j) for j in range(h)] for i in range(h)]
    frames=P[:5]+[P[5],P[6],d.eye(h),arbitrary,Z,Z]
    edges=[(0,5),(1,5),(1,6),(2,6),(5,7),(6,7),(7,8),(3,8),(8,9),(4,9),(6,10)]
    masks=[1<<i for i in range(5)]
    for v in range(5,11):
        mask=0
        for u,w in edges:
            if w==v:mask^=masks[u]
        masks.append(mask)
    d.require(all(masks),'zero-free DAG')
    d.require((masks[9]|masks[10])==31 and not (masks[9]&2) and masks[10]&2,
              'genuine cancellation and full source participation')
    return dict(sharp_star=star,shared_cancellation_dag=forest_control(frames,edges,list(range(5)),[9,10]),
                dag_scalar_outputs=masks[9:11])


def budget_consequence(h=23):
    n=len(d.triples(h));ell=h*(h-1)
    minimum_extra=n-ell
    lo,hi=b.moment({h-1:n+h,1:minimum_extra},h,n)
    d.require(lo>1,'boundary-rank profile still fails below exponent one')
    d.require((n+h)*(h-1)+minimum_extra==n*h,'rank saturation')
    return dict(h=h,n=n,producer_rank_floor=n,separate_readout_rank=n*(h-1),
                total_rank_floor=n*h,useful_rank_capacity=n*h,
                previously_reserved_central_rank=ell,extra_rank_floor=minimum_extra,
                previous_hypothetical_extra_singletons=1253,
                shortfall_at_that_profile=minimum_extra-1253,
                boundary_singleton_profile_moment=[str(lo),str(hi)],
                scope='Producer ends at zero-frame central frontier; separate readout costs n(h-1)')


def run():
    sources=['research/shared-aggregate-followup/audit.py','research/shared-aggregate-followup/test_audit.py',
             'research/hybrid-clean-design/design.py','research/hybrid-clean-design/REPORT.md',
             'research/kappa-nine/target_budget.py','docs/research/cancellation-audit.md',
             'docs/research/shared-computation.md']
    return dict(status='SCOPED PRODUCER-FRONTIER OBSTRUCTION; NO CONSTRUCTION PROMOTED',
                paired_readouts=[paired_readout(h) for h in (6,7,11)],
                paired_frame_exceptions=dict(ambient_degeneracy=9,unique_aggregate_degeneracy=10),
                source_separation=source_distances(),forest_controls=forest_examples(),
                budget=budget_consequence(),new_exponent_claimed=False,
                source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources})


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path);args=parser.parse_args()
    result=run()
    if args.output:args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS: paired identity, rank geometry, shared/cancelling DAG controls, frontier budget')
    print('Producer floor saturates useful rank capacity; no improved exponent.')
