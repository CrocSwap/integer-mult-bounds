#!/usr/bin/env python3
"""One-vector upward and one-hyperplane downward closures on the chart graph."""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from importlib.util import module_from_spec, spec_from_file_location
from hashlib import sha256
from pathlib import Path
import gzip
import json
import sys


def span(basis):
    out={0}
    for v in basis:
        assert v not in out
        out|={v^x for x in out}
    return frozenset(out)


def bits(x):
    while x:
        b=x&-x
        yield b.bit_length()-1
        x^=b


def graph(w):
    n=w['public']
    charts=w['initial']+[None]*w['owned_fields']
    parent=list(range(len(charts)))
    nodes=list(range(len(charts)))
    meta=[(i,-1,f) for i,f in enumerate(charts)]
    moves=[]
    scalars=[]
    frozen=set(range(len(charts)))
    def find(x):
        while parent[x]!=x:
            parent[x]=parent[parent[x]]; x=parent[x]
        return x
    def union(a,b):
        a,b=find(a),find(b)
        if a!=b: parent[a]=b
    for i,e in enumerate(w['program']):
        op,r=e[:2]
        if op in ('MOVE','INIT','CLEAR'):
            f=e[3] if op=='MOVE' else (e[2] if op=='INIT' else None)
            j=len(meta)
            meta.append((r,i,f)); parent.append(j)
            if op=='MOVE' and r<n: moves.append((i,nodes[r],j))
            if r>=n: frozen.add(j)
            nodes[r]=j; charts[r]=f
        else:
            rr=e[1:3] if op in ('ADD','COPY') else e[1:2]
            for v in rr:
                assert charts[v]==e[-1]
                union(nodes[r],nodes[v])
            scalars.append((i,nodes[r]))
    frozen.update(nodes)
    comps=defaultdict(list); representatives={}
    for i,entry in enumerate(meta): comps[find(i)].append(entry)
    groups=list(comps.values())
    for i,x in enumerate(comps): representatives[x]=i
    frames=[g[0][2] for g in groups]
    assert all(all(f==frames[i] for _,_,f in g) for i,g in enumerate(groups))
    resolve=lambda x:representatives[find(x)]
    return groups,frames,{resolve(i) for i in frozen},[(i,resolve(a),resolve(b)) for i,a,b in moves],[(i,resolve(a)) for i,a in scalars]


def screen(w, power_bounds):
    groups,frames,frozen,moves,scalars=graph(w)
    dims=[-1 if f is None else len(w['frames'][f]) for f in frames]
    fmask=[0 if f is None else sum(1<<v for v in span(w['frames'][f])) for f in frames]
    indices=sorted(range(len(groups)),key=dims.__getitem__)
    adj_in=[set() for _ in groups]; adj_out=[set() for _ in groups]; touch=[[] for _ in groups]
    for j,(i,a,b) in enumerate(moves):
        assert dims[a]<dims[b]
        adj_in[b].add(a); adj_out[a].add(b); touch[a].append(j); touch[b].append(j)
    frozen_mask=sum(1<<i for i in frozen)
    best_losing_upper = None
    stats={}; hits=[]
    for mode in ('up','down'):
        counts=Counter(); seen=set()
        inward=adj_out if mode=='up' else adj_in
        visit=indices[::-1] if mode=='up' else indices
        step=1 if mode=='up' else -1
        for v in range(1,512):
            forbidden=1<<v if mode=='up' else sum(1<<x for x in range(512) if (x&v).bit_count()&1)
            active=[bool(m&forbidden)==(mode=='down') and d>=0 for m,d in zip(fmask,dims)]
            closures=[0]*len(groups)
            for a in visit:
                if not active[a]: continue
                r=1<<a
                for b in inward[a]:
                    r|=closures[b]
                closures[a]=r
                if a in frozen: continue
                counts['seeds']+=1
                if r&frozen_mask:
                    counts['blocked_frozen']+=1
                    continue
                if r in seen:
                    counts['duplicate_price_signature']+=1
                    continue
                seen.add(r)
                counts['distinct_closures']+=1
                change=list(bits(r)); counts['max_changed_components']=max(counts['max_changed_components'],len(change))
                delta=Counter()
                affected={j for i in change for j in touch[i]}
                for j in affected:
                    _,a,b=moves[j]
                    sa,sb=bool(r&(1<<a)),bool(r&(1<<b))
                    if sa==sb:continue
                    old=dims[b]-dims[a]; new=old+step*(sb-sa)
                    assert new>=0
                    delta[old]-=1
                    if new:delta[new]+=1
                delta={k:n for k,n in sorted(delta.items()) if n}
                assert sum(k*n for k,n in delta.items())==0
                if not delta:
                    counts['exact_invoice_tie']+=1
                    continue
                lo,hi=margin(delta,power_bounds)
                if hi<0:
                    counts['directed_price_losing']+=1
                    best_losing_upper=hi if best_losing_upper is None else max(best_losing_upper,hi)
                else:
                    hits.append({'mode':mode,'vector':v,'start':a,'changed':change,
                                 'gain_bounds':list(map(str,(lo,hi))),'local_delta':delta})
                    counts['not_ruled_out']+=1
        stats[mode]=dict(counts)
    hits.sort(key=lambda z:Q(z['gain_bounds'][1]),reverse=True)
    for hit in hits[:20]:
        hit['visits']={i:groups[i] for i in hit['changed']}
        hit['scalars']=[(i,a) for i,a in scalars if a in set(hit['changed'])]
    return {'components':len(groups),'frozen_components':len(frozen),'public_moves':len(moves),'stats':stats,'n_hits':len(hits),'top':hits[:20],
            'best_losing_upper':str(best_losing_upper)}


def margin(delta, bounds):
    low=high=Q(0)
    for r,paid in delta.items():
        c=-paid
        a,b=bounds[r]
        low+=c*(a if c>=0 else b)
        high+=c*(b if c>=0 else a)
    return low,high


if __name__=='__main__':
    p=Path(sys.argv[1]); raw=gzip.decompress(p.read_bytes()); w=json.loads(raw)
    digest=sha256(raw).hexdigest()
    assert digest=='e2db4293ac41720af326d3acddabb580c1781c781b18d50dc81cfc8739f0cc38'
    lower,upper=map(Q,sys.argv[2:4]); assert 0<lower<upper<1
    spec=spec_from_file_location('directed_price',Path(sys.argv[4])); engine=module_from_spec(spec); spec.loader.exec_module(engine)
    bounds={r:(engine.raw_margin({r:1},upper)[0],engine.raw_margin({r:1},lower)[1]) for r in range(1,10)}
    control={1:1,2:-2,3:1}
    assert margin(control,bounds)[0]>0
    assert margin({r:-n for r,n in control.items()},bounds)[1]<0
    out=screen(w,bounds)
    print(json.dumps({'source':digest,'screen_bracket':sys.argv[2:4],
                      'directed_price_controls':2,**out},indent=2))
