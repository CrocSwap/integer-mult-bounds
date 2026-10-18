#!/usr/bin/env python3
"""Source-pinned adaptive affine leaf certificates; no floating arithmetic."""
from collections import Counter
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from model import (need,load,Protocol,Geometry,FRAMES,parity,affine_system,xor_rows)


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'))


def reject(call,label):
    try:
        call()
    except ValueError:
        return label
    raise ValueError('accepted control '+label)


def fixtures():
    all_one=[1]*40
    small=[int(t in sum((list(f) for f in FRAMES[:3]),[])) for t in range(40)]
    block=[2*b for b in small]
    unequal=[0]*40
    for t,b in zip(FRAMES[0],(1,2,3,1)):
        unequal[t]=b
    return [('full_adaptive',Protocol('adaptive',all_one)),
            ('full_variable',Protocol('variable',all_one)),
            ('small_adaptive',Protocol('adaptive',small)),
            ('small_affine',Protocol('affine',small)),
            ('block',Protocol('block',block)),
            ('unequal',Protocol('unequal',unequal)),
            ('zero',Protocol('unequal',[0]*40))]


def export_small(protocol):
    nodes={}
    for history,_,path,_ in protocol.leaves():
        for depth,query in enumerate(path):
            prefix=history[:depth]
            nodes[prefix]=dict(history=list(prefix),**query)
        nodes[history]=dict(history=list(history),terminal=True)
    return dict(kind=protocol.kind,demands=protocol.demands,
                nodes=[nodes[h] for h in sorted(nodes,key=lambda h:(len(h),h))])


def run():
    floor,source=load()
    original=io.StringIO()
    with redirect_stdout(original):
        floor.main()
    need('PASS_EISENSTEIN_REDUCTION_COPY_FLOOR' in original.getvalue(), 'original predecessor replay')
    geo=Geometry(floor,source)
    cases=fixtures()
    summary={};digest=hashlib.sha256();total=0;directions=0;bits_checked=0
    for name,protocol in cases:
        leaves=0;costs=Counter();ranks=Counter();fiber_sum=0
        for history,equations,path,(point,kernel,rank) in protocol.leaves():
            need(protocol.walk(point)==history,'exact leaf representative')
            need(len(kernel)+rank==protocol.n,'full fiber dimension')
            for vector in kernel:
                need(all(parity(row & vector)==0 for row,_ in equations),'kernel equations')
                need(protocol.walk(point^vector)==history,'kernel direction follows same adaptive path')
                directions+=1
            cost,decoder,fitting=geo.certify(protocol,equations,path)
            # Exact affine offset: e_k = d_k E + (e_k+B_k) orthogonal side row.
            rhs=sum(b << i for i,(_,b) in enumerate(equations))
            for k,(d,b) in enumerate(zip(decoder,fitting)):
                decoded=parity(d & rhs)^parity(((1 << k)^b)&point)
                need(decoded==((point >> k)&1),'actual affine offset recovery')
                bits_checked+=1
            digest.update((canonical([name,history,equations,cost,point,kernel,fitting])+'\n').encode())
            leaves+=1;costs[cost]+=1;ranks[rank]+=1;fiber_sum+=1 << len(kernel)
        need(fiber_sum==1 << protocol.n,'complete disjoint leaf coverage')
        if protocol.kind!='variable':
            need(set(costs)=={protocol.n},'sharp pathwise attainment')
        else:
            need(set(costs)=={40,44},'variable paid termination')
        summary[name]=dict(input_bits=protocol.n,reachable_leaves=leaves,
                           cost_counts=dict(sorted(costs.items())),rank_counts=dict(sorted(ranks.items())),
                           fiber_cardinality=str(fiber_sum))
        total+=leaves
    small={name:export_small(protocol) for name,protocol in cases if name in ('small_adaptive','small_affine','unequal')}
    need(canonical(small)==canonical(json.loads((HERE/'SMALL-TREES.json').read_text())), 'literal small-tree binding')
    selected=dict(cases)
    adaptive=selected['small_adaptive']
    a=1 << adaptive.owners.index(FRAMES[0][0]);b=1 << adaptive.owners.index(FRAMES[2][0])
    mixed=adaptive.walk(0)[1]^adaptive.walk(a)[1]^adaptive.walk(b)[1]^adaptive.walk(a^b)[1]
    need(mixed==1,'globally nonlinear branch-dependent encoder')
    controls=[]
    dropped=Protocol('dropped',[1]*40)
    _,eq,path,_=next(dropped.leaves())
    controls.append(reject(lambda:geo.certify(dropped,eq,path),'omitted actual frame query'))
    protocol=selected['block'];_,eq,path,_=next(protocol.leaves())
    bill,_,_=geo.certify(protocol,eq,path)
    wrong=sum(geo.price(tuple(q['sources'])) for q in path)
    controls.append(reject(lambda:need(wrong>=protocol.n,'block width undercharge'),'undercharged block width'))
    need(bill==24 and wrong==12,'effective width counterexample')
    bad=[dict(q) for q in path];bad[0]['sources']=()
    controls.append(reject(lambda:geo.certify(protocol,eq,bad),'undeclared actual query source'))
    protocol=selected['small_affine'];history,eq,path,_=next(protocol.leaves())
    wrong_eq=[(row,(history[j] >> i)&1) for j,q in enumerate(path) for i,row in enumerate(q['rows'])]
    wrong_point=affine_system(wrong_eq,protocol.n)[0]
    controls.append(reject(lambda:need(protocol.walk(wrong_point)==history,'omitted affine constants'), 'omitted affine constants'))
    protocol=selected['small_adaptive']
    history,eq,path,_=next(leaf for leaf in protocol.leaves() if leaf[0][0]==leaf[0][2]==1)
    wrong_eq=list(eq);wrong_eq[1]=(wrong_eq[1][0]^protocol.frame_rows[2],wrong_eq[1][1])
    wrong_point=affine_system(wrong_eq,protocol.n)[0]
    controls.append(reject(lambda:need(protocol.walk(wrong_point)==history,'wrong adaptive coefficient'), 'wrong frozen branch'))
    # A private parity header can reveal the three needed frame parities at
    # zero payload cost. Its leaf is not the fiber of the empty paid system.
    private_fiber=[x for x in range(1 << protocol.n)
                   if all(parity(row & x)==0 for row in protocol.frame_rows)]
    need(len(private_fiber)==512,'actual hidden-header fiber')
    controls.append(reject(lambda:need(len(private_fiber)==1 << protocol.n,'unpaid private header'), 'private header invalidates fiber equality'))
    nonlinear_zero=[x for x in range(4) if ((x&1)*((x>>1)&1))==0]
    need(len(nonlinear_zero)==3,'nonlinear product zero fiber')
    controls.append(reject(lambda:need(len(nonlinear_zero)&(len(nonlinear_zero)-1)==0,'nonaffine node fiber'), 'nonlinear payload invalidates affine fiber'))
    # At every positive stage count, the conditional inherited Dfc screen is negative.
    screen=[]
    for stage in (1,2,3,7,9,37,100):
        for width in (1,2,7):
            need((stage-1)*80*width-2*stage*40*width==-80*width,'conditional stage identity')
            screen.append([stage,width,-80*width])
    return dict(status='PASS_EISENSTEIN_ADAPTIVE_AFFINE_FLOOR',reachable_leaves=total,
                kernel_directions_checked=directions,affine_decoded_bits=bits_checked,fixtures=summary,
                path_certificate_sha256=digest.hexdigest(),global_mixed_derivative=mixed,
                original_predecessor_replay='PASS_EISENSTEIN_REDUCTION_COPY_FLOOR',
                semantic_controls=controls,conditional_stage_screen=screen,
                theorem='Each reachable execution costs at least sum b_t; equal demand sharp40b.',
                limits='Public paid-history affine broadcast trees only; no private headers, nonlinear node queries, native supplier or kappa.')


if __name__=='__main__':
    if sys.argv[1:]==['--create-small']:
        data={name:export_small(p) for name,p in fixtures() if name in ('small_adaptive','small_affine','unequal')}
        with (HERE/'SMALL-TREES.json').open('x',encoding='utf-8') as out:
            json.dump(data,out,indent=2,sort_keys=True);out.write('\n')
    else:
        need(len(sys.argv)==1 or (len(sys.argv)==3 and sys.argv[1]=='--output'),'unknown arguments')
        if len(sys.argv)==3:
            need(not Path(sys.argv[2]).exists(),'output already exists')
        result=run()
        if len(sys.argv)==3 and sys.argv[1]=='--output':
            with Path(sys.argv[2]).open('x',encoding='utf-8') as out:
                json.dump(result,out,indent=2,sort_keys=True);out.write('\n')
        else:
            need(len(sys.argv)==1,'unknown arguments')
            need(canonical(result)==canonical(json.loads((HERE/'RESULT.json').read_text())),'typed receipt mismatch')
        print('PASS_EISENSTEIN_ADAPTIVE_AFFINE_FLOOR leaves={} kernel_directions={} controls={}'.format(
            result['reachable_leaves'],result['kernel_directions_checked'],len(result['semantic_controls'])))
