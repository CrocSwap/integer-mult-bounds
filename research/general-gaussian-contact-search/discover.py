#!/usr/bin/env python3
"""Optional floating discovery; solver output is not scientific acceptance.

Requires NumPy/SciPy. The registered verifier uses the standard library only.
Apache-2.0; substantial OpenAI Codex assistance and credited sources in README.
"""
import argparse
from collections import defaultdict
import hashlib,json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import model as M

def solve(source,forms,seconds,fixed_helper_side,mode="kernel"):
    import numpy as np
    import scipy
    from scipy.optimize import milp,Bounds,LinearConstraint
    from scipy.sparse import coo_array
    payload=M.load(source);builder={'kernel':M.build,'phase':M.build_phase,'pauli':M.build_pauli}[mode]
    model=builder(payload,forms);frozen=set(model['fixed'])
    for _,a,b,_ in model['helpers']:
        if fixed_helper_side=='entrance':frozen.add(a)
        if fixed_helper_side=='exit':frozen.add(b)
    variables={n:i for i,n in enumerate(n for n in range(2,len(model['nodes']))
               if n not in frozen and model['old_spaces'][model['nodes'][n]]!=model['new_spaces'][model['nodes'][n]])}
    C=.00302177585;powers=[r**(1-C) for r in range(10)]
    unary=defaultdict(float);pairs=defaultdict(float)
    def table(a,b,ranks,sign):
        z10,z01,z11=[sign*(powers[r]-powers[ranks[0]]) for r in ranks[1:]]
        if a==b:
            if a in variables:unary[variables[a]]+=z11
            return
        x,y=variables.get(a),variables.get(b)
        if x is not None:unary[x]+=z10
        if y is not None:unary[y]+=z01
        if x is not None and y is not None:pairs[min(x,y),max(x,y)]+=z11-z10-z01
    for _,a,b,ranks in model['edges']:table(a,b,ranks,1)
    for _,a,b,ranks in model['helpers']:
        M.need(min(ranks)>0,'discovery keeps every helper productive')
        table(a,b,ranks,-1)
    pairs={k:v for k,v in pairs.items() if abs(v)>1e-12};n=len(variables);total=n+len(pairs);cost=np.zeros(total)
    for i,v in unary.items():cost[i]=v
    rows=[];cols=[];values=[];lower=[];upper=[]
    def constraint(items,lo,hi):
        j=len(lower);lower.append(lo);upper.append(hi)
        for i,v in items:rows.append(j);cols.append(i);values.append(v)
    # Signed-cut formulation: positive edges use the lower XOR envelope;
    # negative helper rewards use the upper envelope. Both are exact when
    # the two contact switches are binary. Cut variables remain continuous.
    for j,((a,b),v) in enumerate(pairs.items(),n):
        weight=-v/2;cost[j]=weight;cost[a]+=v/2;cost[b]+=v/2
        if weight>=0:
            constraint([(j,1),(a,-1),(b,1)],0,np.inf)
            constraint([(j,1),(a,1),(b,-1)],0,np.inf)
        else:
            constraint([(j,1),(a,-1),(b,-1)],-np.inf,0)
            constraint([(j,1),(a,1),(b,1)],-np.inf,2)
    matrix=coo_array((np.array(values),(np.array(rows,dtype=np.int32),np.array(cols,dtype=np.int32))),shape=(len(lower),total)).tocsc();started=time.monotonic()
    result=milp(cost,integrality=np.r_[np.ones(n),np.zeros(total-n)],bounds=Bounds(np.zeros(total),np.ones(total)),constraints=LinearConstraint(matrix,np.array(lower),np.array(upper)),options=dict(time_limit=seconds,mip_rel_gap=0.0))
    out=dict(scope='BOUNDED_FLOATING_DISCOVERY_ONLY_NO_NEW_KAPPA',source_sha256=hashlib.sha256(Path(source).read_bytes()).hexdigest(),functionals=forms,
             mode=mode,tested_saving=C,scipy=scipy.__version__,status=int(result.status),message=result.message,
             seconds=time.monotonic()-started,variable_contacts=n,pair_terms=len(pairs),fixed_helper_side=fixed_helper_side)
    if result.x is not None:
        selected=[node for node,i in variables.items() if round(result.x[i])]
        p,h=M.invoice(model,selected);p0,h0=M.invoice(model,[])
        moment=lambda profile:sum(count*powers[r] for r,count in profile.items())
        true=moment(p)-moment(h)-moment(p0)+moment(h0)
        M.need(abs(true-result.fun)<1e-6,'actual full invoice agrees with binary objective')
        out.update(selected_nodes=selected,paid=dict(p),helpers=dict(h),actual_local_energy=true,solver_objective=float(result.fun))
    if getattr(result,'mip_dual_bound',None) is not None:out['floating_dual_bound']=float(result.mip_dual_bound)
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,default=Path(__file__).parent/'inputs/round3-word.json.gz')
    ap.add_argument('--functionals',default='1',help='Binary functionals, or X,Z masks in pauli mode');ap.add_argument('--mode',choices=['kernel','phase','pauli'],default='kernel')
    ap.add_argument('--seconds',type=float,default=30);ap.add_argument('--fixed-helper-side',choices=['none','entrance','exit'],default='none');ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    forms=[int(x) for x in args.functionals.split(',')]
    if args.mode=='pauli':M.need(len(forms)==2 and all(0<=x<512 for x in forms) and any(forms),'nonzero Pauli X,Z masks')
    else:M.need(forms and all(0<x<512 for x in forms),'nonzero nine-bit functionals')
    M.need(args.seconds>0,'positive bounded solver time')
    result=solve(args.source,forms,args.seconds,args.fixed_helper_side,args.mode);args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='selected_nodes'},sort_keys=True))
if __name__=='__main__':main()
