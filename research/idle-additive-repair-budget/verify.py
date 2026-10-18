#!/usr/bin/env python3
"""Source-bound additive repair budget. Written theorem: PROOF.md.

Ross Richardson, with substantial OpenAI Codex assistance. Apache-2.0.
The retained source interpreter is reused, not independently reimplemented here.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
BASE = "463113d675af7410ac91d53a4fed51ec6494eb9a"
LIMIT_A = Q(1,400)
ALLOWANCE = Q(153,160)

def require(ok, why):
    if not ok:
        raise ValueError(why)

def load(name,path):
    spec = importlib.util.spec_from_file_location(name,path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def authenticate():
    sources=json.loads((PACKAGE/'SOURCES.json').read_text())
    require(sources['base_commit']==BASE,'base pin')
    inputs=[r for r in sources['files'] if r['usage']=='input']
    require(len(inputs)==19,'live input coverage')
    for row in inputs:
        p=ROOT/row['path']
        require(p.is_file() and not p.is_symlink(),'missing/linked input')
        raw=p.read_bytes()
        require(hashlib.sha256(raw).hexdigest()==row['sha256'],'SHA256 '+row['path'])
        blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw,usedforsecurity=False).hexdigest()
        require(blob==row['git_blob'],'Git blob '+row['path'])

def rank_q(rows):
    rows=[[Q(v) for v in row] for row in rows]
    rank=0
    for col in range(len(rows[0])):
        pivot=next((i for i in range(rank,len(rows)) if rows[i][col]),None)
        if pivot is None:
            continue
        rows[rank],rows[pivot]=rows[pivot],rows[rank]
        scale=rows[rank][col]
        rows[rank]=[v/scale for v in rows[rank]]
        for i in range(len(rows)):
            if i!=rank and rows[i][col]:
                scale=rows[i][col]
                rows[i]=[x-scale*y for x,y in zip(rows[i],rows[rank],strict=True)]
        rank+=1
        if rank==len(rows):
            break
    return rank

def difference(a,b):
    return [[(x-u,y-v) for (x,y),(u,v) in zip(ar,br,strict=True)] for ar,br in zip(a,b,strict=True)]

def rank_qi(matrix):
    real=[[v[0] for v in row]+[-v[1] for v in row] for row in matrix]
    real += [[v[1] for v in row]+[v[0] for v in row] for row in matrix]
    rank=rank_q(real)
    require(rank%2==0,'realification parity')
    return rank//2

def budget_domain(ranks,a,repair_rank=1,repair_count=1):
    require(len(ranks)<=20 and all(type(r) is int and 0<=r<=51 for r in ranks),'idle domain')
    require(0<=a<=LIMIT_A,'saving domain')
    require(type(repair_rank) is int and repair_rank>=1,'positive integral repair rank')
    require(type(repair_count) is int and repair_count>=1,'positive integral actual repair count')

def rejects(call):
    try:
        call()
    except ValueError:
        return
    raise ValueError('unrejected domain control')

def run():
    authenticate()
    old=load('retained_idle',ROOT/'research/idle-star-paired-axis-census/verify.py')
    cost=load('retained_cost',ROOT/'research/complex-local-word-ceiling/ceiling.py')
    allowance=load('independent_endpoint_allowance',PACKAGE/'allowance.py')
    old.authenticate()
    vendor=old.PACKAGE/'vendor'
    base=old.decode(old.read_bytes(vendor/'BASE-FILL.json.gz'))['rows']
    journal=old.decode(old.read_bytes(vendor/'EXCHANGE.json'))
    rows=old.project_all_ports(base,old.journal_edits(base,journal))
    allocation=ROOT/'research/rank7-joint-endframes/allocation'
    order0=old.decode(old.read_bytes(allocation/'ORDER.json'))
    require(len(order0)==666,'base order')
    order=[[s,r+74*c] for s,r in order0 for c in range(10)]
    dr=old.decode(old.read_bytes(allocation/'DISPATCH.json'))
    dispatch={(s,r):t for s,r,t in dr}
    require(len(dispatch)==len(dr)==666,'dispatch')
    providers=old.decode(old.read_bytes(vendor/'PROVIDERS.json'))
    plan=old.decode(old.read_bytes(allocation/'vendor/PLAN.json.gz'))
    template=old.decode(old.read_bytes(allocation/'vendor/TEMPLATE.json.gz'))
    recipes=old.decode(old.read_bytes(ROOT/'research/adaptive-kernel-demotion/inputs/DATA-PHASES.json'))['recipes']
    require(len(recipes)==112 and all(len(r['idle_children'])==20 for r in recipes),'source slot count')
    full_ranks=sorted({len(c['orthogonal_axes']) for r in recipes for c in r['idle_children']})
    require(full_ranks==[0,8,16,32,48],'full recipe rank domain')
    require(2*51**2<73**2<=2*52**2,'strict halving cap')
    blocks=old.stage_blocks(template)
    partial_e=Q(1)+Q(1)+Q(1,2)+Q(1,6)
    require(partial_e==Q(8,3),'positive-tail lower bound for e')
    require(20*LIMIT_A*51/partial_e==ALLOWANCE and 1-ALLOWANCE==Q(7,160),'analytic rational constants')
    c1=cost.child_cost(1,73,LIMIT_A)
    c51=cost.child_cost(51,73,LIMIT_A)
    ports=[]
    for port in range(112):
        ctx=old.prepare_port(port,rows[port],order,dispatch,providers,plan,template,recipes)
        ranks=[len(ctx['residual'][j]) for j in range(20)]
        budget_domain(ranks,LIMIT_A)
        mass=sum(ranks)
        upper=sum((cost.child_cost(r,73,LIMIT_A)[1] for r in ranks if r),Q(0))-Q(mass,51)*c51[0]
        raw_upper=upper/c1[0]
        require(raw_upper<ALLOWANCE,'actual endpoint allowance')
        require(old.replay(ctx,ctx['residual'],0,blocks)==old.identity(),'zero-character control')
        ports.append({'port':port,'ranks':ranks,'mass':mass,'raw_relaxation_upper_at_a_1_400':str(raw_upper)})
        if port==0:
            ctx0=ctx
    original={j:list(v) for j,v in ctx0['residual'].items()}
    moved={j:list(v) for j,v in original.items()}
    donor,receiver,axis=10,12,16
    require(axis in moved[donor],'donor residual axis')
    require(all(old.parity(axis,v)==0 for v in ctx0['full_axes'][receiver]),'receiver orthogonality')
    moved[donor].remove(axis)
    moved[receiver].append(axis)
    require(old.orthonormal(moved[donor]) and old.orthonormal(moved[receiver]),'moved residual bases')
    before=old.replay(ctx0,original,axis,blocks)
    after=old.replay(ctx0,moved,axis,blocks)
    require(before==old.baseline_target(axis),'specific baseline target including phase')
    require(rank_qi(difference(before,after))==2,'rank-two discrepancy')
    nonzero=[(i,j,z[0],z[1]) for i,row in enumerate(difference(after,before)) for j,z in enumerate(row) if z!=(0,0)]
    require(nonzero==[(1,1,-1,-1),(3,1,-1,-1),(7,7,1,-1)],'exact discrepancy entries')
    require((-1)*1-(-1)*(-1)==-2 and (-1)*(-1)+(-1)*1==0,'nonzero Gaussian minor')
    # Repeated axes below encode separate added phase operations. They are
    # NEVER treated as orthonormal residual children. C_v^-1=C_v^3 is one
    # inverse rank-one child at the same tariff as its forward child.
    repaired={j:list(v) for j,v in moved.items()}
    repaired[donor].append(axis)
    repaired[receiver].extend([axis]*3)
    wrong={j:list(v) for j,v in moved.items()}
    wrong[donor].append(axis)
    wrong[receiver].append(axis)
    missing_d={j:list(v) for j,v in moved.items()}
    missing_d[receiver].extend([axis]*3)
    missing_r={j:list(v) for j,v in moved.items()}
    missing_r[donor].append(axis)
    modes=sorted({0,axis,*[1<<j for j in range(73)],*[(1<<j)^axis for j in range(73)]})
    for x in modes:
        require(old.replay(ctx0,repaired,x,blocks)==old.replay(ctx0,original,x,blocks),'two-child repair')
    for name,mutant in [('wrong-inverse',wrong),('missing-donor',missing_d),('missing-receiver',missing_r)]:
        require(old.replay(ctx0,mutant,axis,blocks)!=before,name)
    flatten=lambda d:sorted(v for vs in d.values() for v in vs)
    require(flatten(original)==flatten(moved) and after!=before,'axis multiset is insufficient')
    one=[list(row) for row in after]
    old.phase(one,0,1)
    require(rank_qi(difference(one,after))==1,'positive single-insertion control')
    controls=['wrong-inverse','missing-donor','missing-receiver','axis-multiset-insufficiency','positive-rank-one-insertion']
    for name,call in [('rank-cap',lambda:budget_domain([52],LIMIT_A)),
                      ('slot-count',lambda:budget_domain([1]*21,LIMIT_A)),
                      ('saving-range',lambda:budget_domain([1],Q(1,399))),
                      ('rank-zero-repair',lambda:budget_domain([1],LIMIT_A,0)),
                      ('fractional-actual-count',lambda:budget_domain([1],LIMIT_A,1,Q(1,2)))]:
        rejects(call)
        controls.append(name)
    gain_lo=c1[0]+cost.child_cost(48,73,LIMIT_A)[0]-cost.child_cost(49,73,LIMIT_A)[1]
    require(gain_lo>Q(1,1000)*c1[1],'fractional repair loophole control')
    return {'status':'PASS_IDLE_ADDITIVE_REPAIR_BUDGET','base':BASE,'live_inputs_authenticated':19,
            't740_rows_authenticated':old.TOTAL_ROWS,'source_geometry':{'ports':112,'idle_slots':20,'full_ranks':full_ranks,'rank_cap':51},
            'analytic_domain':{'a_min':'0','a_max':'1/400','raw_allowance_strict_upper':'153/160','raw_net_loss_strict_lower':'7/160'},
            'actual_owner_replica_zero':ports,
            'operator_witness':{'owner_replica':0,'port':0,'donor':donor,'receiver':receiver,'axis':axis,'character':axis,
                                'baseline':before,'overlay':after,'difference_rank_Qi':2,
                                'overlay_minus_baseline_nonzero_entries':nonzero,'minor_rows_and_columns':[1,7],'minor_determinant':[-2,0],
                                'single_stream_insertions_required_at_least':2,'two_signed_rank_one_children_suffice':True,'finite_repair_control_modes':len(modes)},
            'independent_endpoint_invoice_controls':allowance.run(),
            'controls':controls,'control_count':len(controls),'selected_frontier_changed':False,'new_kappa':None}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,help='new external deterministic result receipt')
    args=parser.parse_args()
    result=json.loads(json.dumps(run()))
    if args.output:
        require(not args.output.exists() and args.output.resolve().parent!=PACKAGE,'new external output required')
        args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        require(result==json.loads((PACKAGE/'RESULT.json').read_text()),'committed result differs')
    print('PASS_IDLE_ADDITIVE_REPAIR_BUDGET ports=112 rows=2717280 allowance<153/160 repair>=1 witness_rank=2 no_new_kappa')

if __name__=='__main__':
    main()
