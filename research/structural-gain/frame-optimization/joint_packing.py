#!/usr/bin/env python3
"""Joint finite-frame and fractional capacity-packing discovery model.

Every local gate chooses among all subspaces allowed by the fixed scalar DAG.
Existing entrances may be enlarged; new scalar kernels/gauges are not added.
Gate and edge marginals plus provider multiplicities are relaxed continuously.
Only an independently checked literal assignment can supply a new provider.
Prepared with OpenAI Codex (GPT-6 Astra) assistance. Apache-2.0.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import json
import math
from pathlib import Path

from optimize_frames import model


def main():
    import numpy as np
    import scipy
    from scipy.optimize import linprog
    from scipy.sparse import block_diag, csc_matrix, hstack, vstack
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--word', type=Path, action='append', required=True)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--rate', type=float, default=.0016033769575402628)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise ValueError('Use fresh output')
    args.out.mkdir(parents=True)
    words = [json.loads(gzip.decompress(p.read_bytes())) for p in args.word]
    models = [model(w,args.rate,unlock_entrances=True) for w in words]
    costs = lambda r: r * math.expm1(args.rate * math.log(73 / r)) / args.rate if r else 0
    widths = set()
    for w,(g,frames,nv,*_) in zip(words,models):
        for r in range(2*g.v,len(g.regs)):
            widths.update(g.h-len(f) for f in frames[g.regs[r][0]])
    widths = sorted(widths)
    if not all(w>0 for w in widths):
        raise ValueError('Zero width unsupported')
    plan = json.loads(args.plan.read_text())
    capacities = {r:112*n for r,n in sorted(Counter(v[0] for v in plan['windows'].values()).items())}
    packing_rhs = list(capacities.values())+[0]*len(widths)+[72]
    nrows = len(packing_rhs)
    local_blocks, packing_blocks, objective, total_local = [],[],[],0
    for word,md in zip(words,models):
        g,frames,nv,ev,mr,c,mat,rhs = md
        n = len(c)
        local_blocks.append(hstack([mat,csc_matrix(-rhs.reshape(-1,1))],format='csc'))
        pack = np.zeros((nrows,n+1))
        for r in range(2*g.v,len(g.regs)):
            k = g.regs[r][0]
            for f,var in zip(frames[k],nv[k]):
                pack[len(capacities)+widths.index(g.h-len(f)),var] -= 1
        pack[-1,-1] = 1
        packing_blocks.append(csc_matrix(pack))
        objective.extend(c)
        objective.append(sum(n*costs(r) for r,n in g.center_profile.items()))
        total_local += n+1
    descriptors, patterns = [],[]
    for ci,cap in enumerate(capacities):
        def rec(i,remaining,counts):
            if i==len(widths):
                col=[int(j==ci) for j in range(len(capacities))]+counts+[0]
                patterns.append(col)
                descriptors.append(dict(capacity=cap,counts=counts,remainder=remaining))
                objective.append(costs(remaining))
                return
            w=widths[i]
            for count in range(remaining//w+1):
                rec(i+1,remaining-count*w,counts+[count])
        rec(0,cap,[])
    local=block_diag(local_blocks,format='csc')
    packing=hstack(packing_blocks+[csc_matrix(np.array(patterns).T)],format='csc')
    matrix=vstack([hstack([local,csc_matrix((local.shape[0],len(patterns)))]),packing],format='csc')
    rhs=np.r_[np.zeros(local.shape[0]),packing_rhs]
    print(json.dumps(dict(variables=matrix.shape[1],constraints=matrix.shape[0],patterns=len(patterns),widths=widths)),flush=True)
    result=linprog(objective,A_eq=matrix,b_eq=rhs,bounds=(0,None),method='highs')
    if not result.success:
        raise ValueError(result.message)
    provider_results=[]
    offset=0
    for path,word,md in zip(args.word,words,models):
        g,frames,nv,ev,mr,c,mat,brhs=md
        t=float(result.x[offset+len(c)])
        summary=dict(word=str(path.resolve()),word_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),calls=t)
        if t>1e-7:
            xs=result.x[offset:offset+len(c)]/t
            fractional=sum(int(abs(xs[v]-round(xs[v]))>1e-7) for choices in nv for v in choices)
            summary['fractional_node_states']=fractional
            if not fractional:
                trace=[]
                for k,choices in enumerate(nv):
                    f=frames[k][int(np.argmax(xs[choices]))]
                    node=g.nodes[k]
                    if f!=node['F']:
                        if k in g.locked:
                            raise ValueError('Locked state changed')
                        trace.append(dict(node=k,section=node['section'],index=node['index'],old=node['F'],new=f))
                        if node['section']=='start':
                            word['start_extra'][str(node['regs'][0])]=list(f)
                        else:
                            word[node['section']][node['index']][-1]=list(f)
                        node['F']=f
                profile=dict(sorted(g.profile().items()))
                inventory=dict(sorted(Counter(g.h-len(g.nodes[g.regs[r][0]]['F']) for r in range(2*g.v,len(g.regs))).items()))
                summary.update(profile_after=profile,widths_after=inventory,changed_nodes=len(trace),trace=trace)
                word['report']['local_profile']=profile
                out=args.out/('provider-%d'%len(provider_results));out.mkdir()
                payload=gzip.compress(json.dumps(word,sort_keys=True,separators=(',',':')).encode(),mtime=0)
                (out/'FULL-WORD.json.gz').write_bytes(payload)
                (out/'CONSTRUCTION.json').write_text(json.dumps(summary,indent=2)+'\n')
        provider_results.append(summary)
        offset+=len(c)+1
    report=dict(status='FLOATING_JOINT_RELAXATION_NOT_A_CERTIFICATE',rate=args.rate,
                cost=float(result.fun),rate_times_cost=float(args.rate*result.fun),deficit=2560,
                variables=matrix.shape[1],constraints=matrix.shape[0],widths=widths,
                providers=provider_results,active_patterns=[dict(d,multiplicity=float(n)) for d,n in zip(descriptors,result.x[total_local:]) if n>1e-7],
                scipy_version=scipy.__version__,source_plan_sha256=hashlib.sha256(args.plan.read_bytes()).hexdigest(),
                script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                scope='All monotone local frame states and enlargements of already entered helper axes, '
                      'jointly priced against all pending-capacity patterns. Scalar word/cuts/output caps fixed. '
                      'Fractional local marginals and packing ignore physical chronology and integrality.')
    (args.out/'RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
    duals=[]
    row_offset=0
    for _,_,_,_,mr,_,mat,_ in models:
        values=result.eqlin.marginals[row_offset:row_offset+mat.shape[0]]
        duals.append([[list(map(float,values[left])),list(map(float,values[right]))] for left,right in mr])
        row_offset+=mat.shape[0]
    (args.out/'DUAL-MESSAGES.json.gz').write_bytes(gzip.compress(json.dumps(dict(
        providers=duals,widths={str(w):float(result.eqlin.marginals[row_offset+len(capacities)+i]) for i,w in enumerate(widths)}
    ),separators=(',',':')).encode(),mtime=0))
    print(json.dumps({k:v for k,v in report.items() if k not in ('providers','active_patterns')}),flush=True)
    print(json.dumps([{k:v for k,v in p.items() if k!='trace'} for p in provider_results]),flush=True)


if __name__=='__main__':
    main()
