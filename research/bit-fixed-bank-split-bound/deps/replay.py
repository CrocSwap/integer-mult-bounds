"""Price coupled fixed-order BIT chart labels over one nested pair at a time."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction as F
from functools import cache
import gzip
from hashlib import sha256
import json
from pathlib import Path
import runpy
from time import monotonic

ROOT=Path(__file__).resolve().parent
PINS={
 'mincut.py':'c6b09de3e6c1f343d53dc099ca23c9bcace150517b1428e0b3bc1e3857bd6a5a',
 'price.py':'6a33aac4c7032de9bb3881da248f5371b69c6b9af0893220825727f3d4878fae',
 'inputs/INVOICE.json':'a46b6c6040f75184cab5467656811ad988c216e3bc8e44d595a5015b6e49620b',
 'inputs/WORD.json.gz':'51203e7fc75ba10bd3ac3f8e675759f47e13d262bea66b6600d1e515095cad78',
}


def graph(w):
    charts=w['start']+[None]*w['owned_fields']
    previous=list(range(w['public']))+[None]*w['owned_fields']
    due=[None]*len(previous)
    vertices=[(f,False,-1) for f in w['start']]
    edges=[]
    old=[]
    events=Counter()

    def append(r,v):
        a,b=vertices[previous[r]][0],vertices[v][0]
        assert (due[r] is None and a==b) or due[r]==(a,b)
        edges.append((previous[r],v))
        due[r]=None
        previous[r]=v

    for t,(op,r,*a) in enumerate(w['program']):
        events[op]+=1
        if op=='SWAP':
            other=a[0]
            for arr in (charts,previous,due):
                arr[r],arr[other]=arr[other],arr[r]
            continue
        if op=='MOVE':
            before,after=a
            assert charts[r]==before and previous[r] is not None and due[r] is None
            due[r]=before,after
            charts[r]=after
            old.append((before,after))
            continue
        v=len(vertices)
        f=a[-1]
        vertices.append((f,True,t))
        if op=='INIT':
            assert charts[r] is previous[r] is due[r] is None
            charts[r]=f
            previous[r]=v
        else:
            assert charts[r]==f and previous[r] is not None
            append(r,v)
            if op=='ADD':
                other=a[0]
                if other!=r:
                    assert charts[other]==f and previous[other] is not None
                    append(other,v)
            else:
                assert op=='CLEAR'
                charts[r]=previous[r]=None
    assert charts==w['final']+[None]*w['owned_fields']
    for r,f in enumerate(w['final']):
        v=len(vertices)
        vertices.append((f,False,len(w['program'])))
        append(r,v)
    assert all(x is None for x in due)
    assert events=={'ADD':30789,'MOVE':2871,'INIT':237,'CLEAR':237,'SWAP':3}
    observed=Counter((vertices[u][0],vertices[v][0]) for u,v in edges if vertices[u][0]!=vertices[v][0])
    assert observed==Counter(old)
    return vertices,edges,old


def run(retry=False,remaining=False):
    retry=retry or remaining
    start=monotonic()
    blobs={}
    assert __debug__
    for f,d in PINS.items():
        raw=(ROOT/f).read_bytes()
        if sha256(raw).hexdigest()!=d:
            raise ValueError(f'changed source {f}')
        blobs[f]=raw
    word=json.loads(gzip.decompress(blobs['inputs/WORD.json.gz']))
    invoice=json.loads(blobs['inputs/INVOICE.json'])
    p=runpy.run_path(str(ROOT/'price.py'))
    flow=runpy.run_path(str(ROOT/'mincut.py'))
    flow['controls']()
    verts,edges,old=graph(word)
    dims={int(j):f['dim'] for j,f in word['frames'].items()}
    bases={int(j):[list(map(F,row)) for row in f['B']] for j,f in word['frames'].items()}
    norms={i:p['annihilator'](rows) for i,rows in bases.items()}
    scope=sorted({(a,b) if dims[a]<dims[b] else (b,a) for a,b in old if abs(dims[a]-dims[b])==1})
    cap=2871
    assert len(scope)<=cap
    signed,copies=p['profile'](invoice,Counter(abs(dims[a]-dims[b]) for a,b in old),word,dims)
    base=p['cost'](signed,F(p['TARGET']))
    grid=p['SCALE']
    tariffs={0:(0,0)}
    for r in range(1,9):
        tariffs[r]=tuple(int(x*grid) for x in p['power_bounds'](r,F(p['TARGET'])))
    incident=defaultdict(set)
    for i,(u,v) in enumerate(edges):
        for j in (u,v):
            f,m,_=verts[j]
            if m:
                incident[f].add(i)

    @cache
    def rank(a,b):
        if a==b:
            return 0
        if dims[a]==dims[b]:
            return None
        x,y=sorted((a,b),key=dims.__getitem__)
        if any(sum(a*b for a,b in zip(row,n,strict=True)) for row in bases[x] for n in norms[y]):
            return None
        return dims[y]-dims[x]

    assert all(rank(a,b)==abs(dims[a]-dims[b]) for a,b in old)
    old_edges=[rank(verts[u][0],verts[v][0]) for u,v in edges]
    assert all(v is not None for v in old_edges)
    ranked=[]
    results=[]
    for a,b in scope:
        if monotonic()-start>=180:
            return {'status':'INCOMPLETE_EDGE_SCREEN','checked':len(results),
                    'unvisited':scope[len(results):], 'results':results,'pins':PINS}
        assert rank(a,b)==1
        ids=incident[a]|incident[b]
        total=0
        for i in ids:
            opts=[(a,b) if verts[v][1] and verts[v][0] in (a,b) else (verts[v][0],) for v in edges[i]]
            admissible=[tariffs[r][0] for x in opts[0] for y in opts[1] if (r:=rank(x,y)) is not None]
            total+=tariffs[old_edges[i]][1]-min(admissible)
        bound=base[1]+copies*F(total,grid)
        results.append([a,b,str(bound)])
        if bound>=0:
            ranked.append((bound,a,b))

    if retry:
        prior=json.loads((ROOT/'RESULT.json').read_bytes())
        assert prior['edgewise']==results and not prior['exact_cuts']
        assert sha256((ROOT/'flow.py').read_bytes()).hexdigest()=='41238bd85a516550c3eace6891baf6d8ceb67625940758c7001ad26ba2f6c58b'
        solve=runpy.run_path(str(ROOT/'flow.py'))['dinic']
    exact=[]
    if remaining:
        raw=(ROOT/'RETRY.json').read_bytes()
        assert sha256(raw).hexdigest()=='f52158e2ffabb4d9499d99f374586307008d37e9df4f1fbefb279f7f0f8f010c'
        certified=json.loads(raw)
        assert certified['edgewise']==results and len(certified['exact_cuts'])==16
        exact=certified['exact_cuts']
    done={tuple(x['pair']) for x in exact}
    cut_start=monotonic()
    inf=sum(tariffs[old_edges[i]][1] for i in range(len(edges)))+1
    ordered=sorted(ranked,key=lambda x:(-x[0],x[1],x[2]))
    for _,a,b in ordered[:len(ordered) if remaining else 16]:
        if (a,b) in done:
            continue
        def clock():
            if monotonic()-cut_start>=(180 if remaining else 90):
                raise TimeoutError
        try:
            clock()
            ids=incident[a]|incident[b]
            variables=sorted({v for i in ids for v in edges[i] if verts[v][1] and verts[v][0] in (a,b)})
            ids_of={v:i for i,v in enumerate(variables)}
            unary=[[0,0] for _ in variables]
            arcs=[]
            for i in sorted(ids):
                u,v=edges[i]
                mutable=(u in ids_of,v in ids_of)
                if all(mutable):
                    arcs.extend(((ids_of[u],ids_of[v],tariffs[1][0]),(ids_of[v],ids_of[u],tariffs[1][0])))
                else:
                    j,k=(u,v) if mutable[0] else (v,u)
                    assert j in ids_of and k not in ids_of
                    for bit,f in enumerate((a,b)):
                        rr=rank(f,verts[k][0])
                        unary[ids_of[j]][bit]+=inf if rr is None else tariffs[rr][0]
            certificate=None
            if retry:
                source,sink=len(unary),len(unary)+1
                cap=defaultdict(int)
                shift=0
                for j,(lower,higher) in enumerate(unary):
                    m=min(lower,higher)
                    shift+=m
                    cap[source,j]+=higher-m
                    cap[j,sink]+=lower-m
                for u,v,w in arcs:
                    if u!=v:
                        cap[u,v]+=w
                flow_value,certificate,cut=solve(len(unary)+2,source,sink,cap,clock)
                reachable=set(cut)
                assign=[int(j not in reachable) for j in range(len(unary))]
                value=flow_value+shift
            else:
                value,assign=flow['mincut'](unary,arcs,clock)
            labels={v:(a,b)[c] for v,c in zip(variables,assign,strict=True)}
            old_hi=sum(tariffs[old_edges[i]][1] for i in ids)
            replacement=Counter()
            original=Counter(old_edges[i] for i in ids)
            for i in ids:
                u,v=edges[i]
                rr=rank(labels.get(u,verts[u][0]),labels.get(v,verts[v][0]))
                assert rr is not None
                replacement[rr]+=1
            assert value==sum(n*tariffs[r][0] for r,n in replacement.items())
            delta=Counter({r:copies*(original[r]-replacement[r]) for r in set(original)|set(replacement) if r})
            actual=p['cost'](delta,F(p['TARGET']))
            upper=base[1]+copies*F(old_hi-value,grid)
            exact.append({'pair':[a,b],'signed_paid_saving_hist':dict(delta),'flow_certificate':certificate,'affected_edges':len(ids),
                          'variables':len(variables),'signed_saving_interval':list(map(str,actual)),
                          'directed_whole_upper':str(upper),
                          'changed_contacts':[[v,verts[v][2],f] for v,f in labels.items() if f!=verts[v][0]]})
            if upper>=0:
                break
        except TimeoutError:
            break
    unresolved=[[a,b] for _,a,b in sorted(ranked,key=lambda x:(-x[0],x[1],x[2])) if [a,b] not in [x['pair'] for x in exact]]
    return {'status':'PASS_COUPLED_BIT_CHART_SCREEN','pins':PINS,'vertices':len(verts),'edges':len(edges),
            'scoped_pairs':len(scope),'pruned_edgewise':len(scope)-len(ranked),'edgewise':results,
            'signed_original_net':list(map(str,base)),'exact_cuts':exact,'unresolved':unresolved,
            'physical_sites':0}


if __name__=='__main__':
    cli=ArgumentParser()
    cli.add_argument('--retry',action='store_true')
    cli.add_argument('--remaining',action='store_true')
    print(json.dumps(run(**vars(cli.parse_args())),indent=2,sort_keys=True))
