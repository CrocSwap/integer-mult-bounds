#!/usr/bin/env python3
"""One algebraic source-parity refactor on the PR168 v4 query modules.

Derived from research/source-assisted/decision/source_aligned_local.py
(icekylinx, GPT-6 Astra assistance, Apache-2.0). Only the three frozen
query modules change: this copy reads PR168 v4's selected modules
(eumemic, Claude assistance) from references/paired-cube/sources instead
of the PR168 fd25adb7 modules. The local configuration, arc transport,
frame inheritance, pair matching and physical layer code are unchanged.
Its output is a candidate, not a final supplier.
"""
from collections import Counter, defaultdict
from pathlib import Path
import argparse
import bisect
import importlib.util
import json
import sys
import time


def read(p):
    return json.loads(p.read_text())


def write(p,d):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(d,separators=(',',':'))+'\n')


def op_tags(g,w):
    v=len(g['inputs']);args=[None]+[None if a is None else [x+1 for x in a] for a in g['args']]
    roots=[dict(r,node=r['node']+1) for r in g['roots']]
    uses=[[] for _ in args]
    for x in w['order']:
        if args[x]:
            for j,y in enumerate(args[x]):uses[y].append(2*x+j)
    for j,r in enumerate(roots):uses[r['node']].append((1<<31)|j)
    incoming={u for _,u in w['matching_arcs']}
    tags=[]
    for x in w['order']:
        if args[x]:tags.append(('sum',x))
        free=[u for u in uses[x] if u not in incoming]
        assert free
        tags.extend(('copy',x,u) for u in free[1:])
    return tags


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--tree',type=Path,required=True)
    ap.add_argument('--cache',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--pairs',type=Path,help='Use this frozen, independently checked physical pair/deadline witness.')
    ap.add_argument('--g-only',action='store_true')
    a=ap.parse_args();start=time.monotonic()
    sys.path.insert(0,str(a.tree/'scripts'))
    from paired_cube.graph import Graph
    from paired_cube.modules import triple_module_from,pair_module_from,all_but_one_from,merge_outputs
    from paired_cube.closure import compile_closure
    from paired_cube.gauges import select
    from paired_cube.frames import basis,perp,contained
    import paired_cube_physical as physical
    import numpy as np
    from scipy.sparse import csr_matrix
    from scipy.sparse.csgraph import maximum_bipartite_matching
    s=a.tree/'references/paired-cube/sources'
    oldg,oldw,oldword=(read(a.cache/n) for n in ('graph.json','frames.json','selection.json'))
    local=read(s/'local_L1.json')
    local['G']={k:'s' for k in local['G']}
    if not a.g_only:local['A']={k:'fd' for k in local['A']}
    builder=Graph(11,local=local)
    g=builder.finish(triple_module_from(s/'tmod_TE_TD_TB3_1_1_4_full_6.0617964e-4.json',11),
                     pair_module_from(s/'pmod_J0_full_6.0666810e-4.json',10),
                     all_but_one_from(s/'qmod_climb3u_best.json',9))
    g=merge_outputs(g,builder,'f8:00111100');g['matching_frames']='coordinate'
    h,v=g['h'],g['v']
    oldcut=v+oldg['counts']['local_channel_additions']
    newcut=v+g['counts']['local_channel_additions']
    delta=newcut-oldcut
    # Exact integer fresh-vector names identify the unchanged local outputs.
    def local_values(gg,cut):
        rows=[((i,1),) for i in range(v)]
        for x in range(v,cut):
            aa,bb=gg['args'][x];d=dict(rows[aa]);sign=gg['signs'][x]
            for j,c in rows[bb]:
                z=d.get(j,0)+sign*c
                if z:d[j]=z
                else:d.pop(j,None)
            rows.append(tuple(sorted(d.items())))
        return rows
    oldvals,newvals=local_values(oldg,oldcut),local_values(g,newcut)
    newindex={row:i+1 for i,row in enumerate(newvals)}
    node_map={i+1:newindex[row] for i,row in enumerate(oldvals) if row in newindex}
    node_map.update({x+1:x+delta+1 for x in range(oldcut,len(oldg['args']))})
    def use_map(u):
        return u if u>>31 else 2*node_map[u//2]+(u&1)
    arcs=[]
    newargs=[None]+[None if x is None else [t+1 for t in x] for x in g['args']]
    newroots=[dict(r,node=r['node']+1) for r in g['roots']]
    for x,u in oldw['matching_arcs']:
        if x<=oldcut or x not in node_map or (not u>>31 and u//2 not in node_map):continue
        xx,uu=node_map[x],use_map(u)
        val=newroots[uu&0x7fffffff]['node'] if uu>>31 else newargs[uu//2][uu&1]
        if val in newargs[xx]:arcs.append([xx,uu])
    p,w=compile_closure(g,arcs)
    p,word=select(g,p,w)
    assert all(ca in (-1,1) and cb in (-1,1) for ca,cb in word['opcoeff'])
    print(json.dumps(dict(stage='word',local=g['counts']['local_channel_additions'],
                          mapped_arcs=len(arcs),R=p['R'],selected=p['selected_rank_histogram'],
                          seconds=time.monotonic()-start)),flush=True)
    # Each surviving query operation inherits its old preferred frame.  It
    # is clipped to its exact new future cap, then forward closure includes
    # both actual predecessor frames.  Local source/pair operations instead
    # use their literal source span.
    oldtags,newtags=op_tags(oldg,oldw),op_tags(g,w)
    assert len(oldtags)==len(oldword['ops']) and len(newtags)==len(word['ops'])
    oldframes=[perp(tuple(oldw['annihilators'][x]),h) for _,_,x in oldword['ops']]
    for i,F in read(a.tree/'references/paired-cube/physical/frames.json')['frames']:oldframes[i]=tuple(F)
    desired={}
    for tag,F in zip(oldtags,oldframes):
        if tag[1] not in node_map:continue
        if tag[0]=='copy' and not tag[2]>>31 and tag[2]//2 not in node_map:continue
        key=('sum',node_map[tag[1]]) if tag[0]=='sum' else ('copy',node_map[tag[1]],use_map(tag[2]))
        desired[key]=F
    spans=[()]+[(q,) for q in g['inputs']]
    for aa,bb in newargs[v+1:]:spans.append(basis(spans[aa]+spans[bb]))
    root_frames={}
    for r,slot in zip(newroots,word['rootroles']):
        root_frames[slot]=spans[r['node']] if r['kind']=='center' else perp(basis(g['inputs'][t] for t in r['targets']),h)
    R=p['R'];ops=word['ops'];pset=set(word['phase1'])
    # Both signs of a pair must occur before the center cut so that their
    # common-frame 2-by-2 map can actually be contracted.  Add precisely
    # the rank-at-most-two local prefix, then its role predecessors.
    previous=[-1]*R;parents=[]
    for i,(aa,bb,x) in enumerate(ops):
        parents.append((previous[aa],previous[bb]));previous[aa]=previous[bb]=i
        if x<=newcut and len(spans[x])<=2:pset.add(i)
    todo=list(pset)
    while todo:
        i=todo.pop()
        for j in parents[i]:
            if j>=0 and j not in pset:pset.add(j);todo.append(j)
    word['phase1']=sorted(pset)
    p['phase1_operations']=len(pset)
    chron=sorted(pset)+[i for i in range(len(ops)) if i not in pset]
    cap=[perp(root_frames[s],h) if s in root_frames else () for s in range(R)]
    maxima=[None]*len(ops)
    for i in reversed(chron):
        aa,bb,x=ops[i];A=basis(cap[aa]+cap[bb]);maxima[i]=perp(A,h);cap[aa]=cap[bb]=A
        assert contained(spans[x],maxima[i])
    selected=[z for z in word['selected'] if z['rank']==h-4]
    gauge={z['role']:perp(tuple(z['annihilator']),h) for z in selected}
    current=[() for _ in range(R)]
    for x,slot in word['sources'].items():current[slot]=(g['inputs'][int(x)-1],)
    for slot,U in gauge.items():current[slot]=U
    frames=[None]*len(ops);minimal_pairs=0;mapped=0
    for i in chron:
        aa,bb,x=ops[i]
        if x<=newcut:
            want=spans[x]
        else:
            want=desired.get(newtags[i],spans[x]);mapped+=newtags[i] in desired
            want=perp(basis(perp(want,h)+perp(maxima[i],h)),h)
        U=basis(spans[x]+want+current[aa]+current[bb])
        assert contained(U,maxima[i]),('Forward frame outside future cap',i)
        frames[i]=current[aa]=current[bb]=U
        if x<=newcut and len(spans[x])==2:
            assert U==spans[x],('Local pair failed its minimal physical frame',i)
            minimal_pairs+=1
    for slot,U in root_frames.items():assert contained(current[slot],U)
    role_ops=defaultdict(list)
    for i,(aa,bb,_) in enumerate(ops):role_ops[aa].append(i);role_ops[bb].append(i)
    pos={i:k for k,i in enumerate(chron)}
    for slot in role_ops:role_ops[slot].sort(key=pos.__getitem__)
    recipients=sorted(gauge)
    recipient_set=set(recipients)
    donors=[slot for slot in range(R) if slot not in recipient_set and slot not in root_frames and slot in role_ops]
    groups=defaultdict(list)
    for j,slot in enumerate(recipients):
        first=role_ops[slot][0]
        assert first not in pset
        groups[gauge[slot]].append((pos[first],j))
    group_data=[]
    for U,ls in groups.items():
        ls.sort();group_data.append((U,[x for x,_ in ls],[j for _,j in ls]))
    containment_cache={}
    indices=[];indptr=[0]
    for slot in donors:
        last=role_ops[slot][-1];U=frames[last]
        eligible=containment_cache.get(U)
        if eligible is None:
            eligible=[(ps,js) for V,ps,js in group_data if contained(U,V)]
            containment_cache[U]=eligible
        for ps,js in eligible:
            indices.extend(js[bisect.bisect_right(ps,pos[last]):])
        indptr.append(len(indices))
    matrix=csr_matrix((np.ones(len(indices),dtype=np.int8),np.array(indices,dtype=np.int32),
                       np.array(indptr,dtype=np.int32)),shape=(len(donors),len(recipients)))
    matched=maximum_bipartite_matching(matrix,perm_type='column')
    pairs=[[slot,recipients[j],None if role_ops[slot][-1] in pset else role_ops[recipients[j]][0]]
           for slot,j in zip(donors,matched) if j>=0]
    if a.pairs:
        pairs=read(a.pairs)['pairs']
    # The inherited negative replay moves its last late recipient to the
    # phase cut. Choose a donor whose VALUE is actually written afterwards;
    # a later control-only use would not make this scalar control negative.
    last_write={}
    for i,(aa,bb,x) in enumerate(ops):last_write[aa]=max(last_write.get(aa,-1),pos[i])
    controls=[q for q in pairs if q[2] is not None and last_write.get(q[0],-1)>=len(pset)]
    if controls:
        chosen=controls[-1];pairs.remove(chosen);pairs.append(chosen)
    kept={b for _,b,_ in pairs}
    word['selected']=[z for z in selected if z['role'] in kept]
    # Unmatched virtual gauges start at zero in the final word.  Removing a
    # gauge never invalidates the already monotone operation flags.
    moved=[[i,list(U)] for i,U in enumerate(frames) if U!=perp(tuple(w['annihilators'][ops[i][2]]),h)]
    deadline={b:t for _,b,t in pairs}
    Y=[() for _ in range(v)];target=Counter()
    for z in sorted(word['selected'],key=lambda z:len(pset) if deadline[z['role']] is None else pos[deadline[z['role']]]):
        U=gauge[z['role']]
        for t in z['targets']:
            assert contained(Y[t],U)
            target[len(U)-len(Y[t])]+=1;Y[t]=U
    for r,slot in zip(newroots,word['rootroles']):
        if r['kind']=='side':
            U=root_frames[slot]
            for t in r['targets']:
                assert contained(Y[t],U)
                target[len(U)-len(Y[t])]+=1;Y[t]=U
    for t in range(v):target[h-1-len(Y[t])]+=1
    p['target_data_histogram']=dict(target)
    print(json.dumps(dict(stage='physical',mapped_query_ops=mapped,minimal_pair_ops=minimal_pairs,
                          candidates=len(indices),pairs=len(pairs),gauges=len(word['selected']),
                          seconds=time.monotonic()-start)),flush=True)
    out=a.out
    for name,data in [('graph.json',g),('frames.json',w),('selection.json',word),('record.json',p)]:
        write(out/'cache'/name,data)
    write(out/'references/paired-cube/physical/frames.json',{'frames':moved})
    write(out/'references/paired-cube/physical/pairs.json',{'pairs':pairs})
    result=physical.physical(g,w,word,p,moved,pairs)
    write(out/'certificates/paired-cube-sinks-input.json',result)
    summary=dict(local_configuration=local,counts=g['counts'],mapped_arcs=len(arcs),
                 mapped_query_operations=mapped,minimal_pair_operations=minimal_pairs,
                 pairs=len(pairs),physical_R=result['physical_R'],
                 histogram=result['child_histogram'],seconds=time.monotonic()-start,
                 source='PR168 v4 frozen query modules; PR184 source-parity local factorization',
                 status='Physical scalar/frame checks passed. Frame-flow compression and source erasure are separate.')
    write(out/'summary.json',summary)
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
