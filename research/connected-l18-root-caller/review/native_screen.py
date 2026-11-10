#!/usr/bin/env python3
"""Exact two-plane replay and optimistic budget screen; no new supplier claim."""
import argparse
import gzip
import hashlib
import json
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from pathlib import Path

def read(p):
    raw=p.read_bytes()
    return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)

def mm(a,b):
    return [[sum(x*y for x,y in zip(r,c)) for c in zip(*b)] for r in a]

def replay(w):
    n=len(w['initial']); current=w['initial'][:]+[None]*w['owned_fields']
    rows=[{r:Q(1)} for r in range(n)]+[{} for _ in range(w['owned_fields'])]
    dim=list(map(len,w['frames'])); spans=[]
    for f in w['frames']:
        s={0}
        for v in f:
            assert v not in s
            s|={x^v for x in tuple(s)}
        spans.append(s)
    owned=set(); paid=Counter()
    for i,e in enumerate(w['program']):
        op,r=e[:2]
        if op=='MOVE':
            _,_,a,b,private=e
            assert current[r]==a and bool(private)==(r in owned),i
            assert spans[a]<spans[b] or (private and spans[b]<spans[a]),i
            current[r]=b; paid[abs(dim[b]-dim[a])]+=1
        elif op=='INIT':
            assert r>=n and r not in owned,i
            owned.add(r); current[r]=e[2]; rows[r]={}
        elif op=='CLEAR':
            assert r in owned and current[r]==e[2],i
            owned.remove(r); current[r]=None; rows[r]={}
        elif op=='SCALE':
            assert current[r]==e[3],i
            q=Q(e[2]); assert q
            rows[r]={k:q*v for k,v in rows[r].items()}
        else:
            assert op in ('ADD','COPY'),i
            _,_,s,q,f=e
            assert r!=s and current[r]==f==current[s],i
            if op=='COPY': assert r in owned and not rows[r],i
            q=Q(q)
            for k,v in rows[s].items():
                z=rows[r].get(k,Q(0))+q*v
                if z: rows[r][k]=z
                else: rows[r].pop(k,None)
    assert not owned and current[:n]==w['final']
    live=w['live']; h=w['hosted']; type_a=set(h['Dports'])
    main=set(live)|{r+112 for r in live}|set(h['X2'])|set(h['Y2'])
    checked=0
    for i,x2,y2 in zip(h['Dports'],h['X2'],h['Y2']):
        x,y=live[i],live[i]+112
        assert rows[x]=={x:Q(1)}
        assert rows[y]=={x:Q(1),y:Q(1)}
        assert rows[x2]=={x2:Q(1),y2:Q(-1)}
        assert rows[y2]=={y2:Q(1)}
        for boundary in ('initial','final'):
            f=w[boundary]
            assert f[x]==f[x2] and f[y]==f[y2] and f[x]!=f[y]
        checked+=1
    for i,x in enumerate(live):
        if i not in type_a:
            y=x+112
            assert rows[x]=={x:Q(1),y:Q(-1)}
            assert rows[y]=={x:Q(1,2),y:Q(1,2)}
    helpers=Counter()
    for r in range(n):
        if r not in main:
            assert rows[r]=={r:Q(1)}
            a,b=w['initial'][r],w['final'][r]
            assert spans[a]<spans[b]
            helpers[dim[b]-dim[a]]+=1
    return checked,paid,helpers

def main():
    p=argparse.ArgumentParser()
    for flag in ('word','caller','base-invoice'): p.add_argument('--'+flag,type=Path,required=True)
    args=p.parse_args(); paths=[args.word,args.caller,args.base_invoice]
    w,c,base=map(read,paths); checked,paid,helpers=replay(w)
    target=Counter(1+8*int(m).bit_count() for m in c['masks']); outside=Counter()
    for e in c['events']:
        if e[0]=='QUERY': outside[1]+=1
        elif e[0]=='IDLE_ONE': outside[8*len(e[2])]+=1
    assert c['stages']==18 and outside=={1:3,8:181}
    fpaid=Counter({int(k):v for k,v in base['local_paid'].items()})
    fhel=Counter({int(k):v for k,v in base['helpers'].items()})
    flux=sum(r*(fpaid[r]-fhel[r]) for r in set(fpaid)|set(fhel))
    U,F,J=[[1,-1],[0,1]],[[1,0],[1,1]],[[1,0],[0,-1]]
    assert mm(F,U)==[[1,-1],[1,0]]
    assert mm(J,mm(mm(F,U),J))==[[1,1],[-1,0]]
    half=[[Q(1),Q(-1)],[Q(1,2),Q(1,2)]]
    assert half[1][1] and mm(F,U)[1][1]==0
    assert sum(half[i][i] for i in range(2))!=1
    records=[]
    with localcontext() as ctx:
        ctx.prec=70
        for k in map(Decimal,('.00362701882','.00363005817')):
            def moment(h): return sum(Decimal(v)*Decimal(r)**(1-k) for r,v in h.items())
            gate=(moment(target)-moment(outside))/18
            fcost=(moment(fpaid)-moment(fhel))/104
            full=moment(paid)-moment(helpers)
            records.append(dict(kappa=str(k),root_native_gate=str(gate),source_F=str(fcost),
                F_plus_owned_H1=str(fcost+1),F_plus_H1_excess=str(fcost+1-gate),
                direct_2H8_2H1=str(2*Decimal(8)**(1-k)+2),two_plane_total=str(full),
                optimistic_200_pair_average=str(full/200)))
    out=dict(status='SCOPED_OBSTRUCTIONS_ONLY_NO_NEW_NATIVE',
        inputs={key:hashlib.sha256(path.read_bytes()).hexdigest() for key,path in zip(('word','caller','base_invoice'),paths)},
        native_type_A_exact_ports=checked,native_public_inputs=len(w['initial']),
        grouped_order=['X1','X2','Y1','Y2'],
        type_A_matrix=[[1,0,0,0],[0,1,0,-1],[1,0,1,0],[0,0,0,1]],
        root_targets=dict(sorted(target.items())),root_outside_paid=dict(sorted(outside.items())),
        source_F_paid=dict(sorted(fpaid.items())),source_F_helpers=dict(sorted(fhel.items())),
        source_F_flux=flux,F_plus_H1_flux=flux+104,
        F_plus_H1_total_surplus=104*sum(r*(target[r]-outside[r]) for r in set(target)|set(outside))-18*(flux+104),
        decimal_diagnostics=records,
        scope='Same-frame invertible input/output remix of two main planes only; excludes paid cross-frame mixing, feedback, helper mixing and larger rewrites. CLEAR uses inherited owned erasure. No Clifford/all-width replay newly claimed.')
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=='__main__': main()
