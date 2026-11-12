"""Exact signed source-row specialization for Type A retained QUERY reuse."""
from fractions import Fraction as Q
from functools import cache
from hashlib import sha256
from itertools import combinations
import json
from math import prod
from pathlib import Path
from time import monotonic
import sys

HEAD="aaeec8c0acf01e99a5f331ef363a698d9c084ace"
PRICE="bbc486a3eb0e2aed03dd09f400fa94de1a59312058a9826880999155b10453bf"
CALLER="255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
CLOCKS=(1516,1580,1659,1721)


def checked(path,digest):
    data=path.read_bytes()
    if sha256(data).hexdigest()!=digest:
        raise ValueError(f"changed input: {path.name}")
    return json.loads(data)


@cache
def rat(s):
    return Q(s)


def add(dest,src,factor):
    for i,x in src.items():
        value=dest.get(i,0)+factor*x
        if value:
            dest[i]=value
        else:
            dest.pop(i,None)


def scale(row,c):
    return {i:c*x for i,x in row.items() if c*x}


def compare(a,b):
    """Return a scalar or a literal nonzero cross-product."""
    if not a:
        return None,{"zero_producer":bool(b)}
    if not b:
        return Q(0),None
    i=min(a)
    for j in sorted(a.keys()|b.keys()):
        cross=a[i]*b.get(j,0)-a.get(j,0)*b.get(i,0)
        if cross:
            return None,dict(coordinates=[i,j],cross_product=str(cross))
    return b.get(i,Q(0))/a[i],None


def snapshot(caller,clocks,body,q,deadline):
    rows=[{i:Q(1)} for i in range(36)]
    answers={}
    writes=[]
    a=Q(caller["types"]["A"]["alpha2"])
    assert a==-1 and q in (1,-1) and len(body)==caller["stages"]+1
    for clock,event in enumerate(caller["events"]):
        if clock%32==0 and monotonic()>=deadline:
            break
        kind,op,*args=event
        if clock in clocks:
            assert event==["A","QUERY",0,1,-1]
            answers[clock]=rows[1].copy()
        if clock>=clocks[-1]:
            break
        if kind=="J":
            x,y,u,v=args[0]
            add(rows[y],rows[x],q)
            add(rows[u],rows[v],a*q)
            for role in (x,y,u,v):
                rows[role]=scale(rows[role],body[op])
            if 1 in (x,y,u,v) and clock>clocks[0]:
                writes.append([clock,event])
        elif kind=="A":
            r,*z=args
            if op=="ADD":
                add(rows[r],rows[z[0]],rat(z[1]))
            elif op=="QUERY":
                add(rows[r],rows[z[0]],Q(q)**z[1])
            elif op=="SCALE":
                rows[r]=scale(rows[r],rat(z[0]))
            elif op=="SWAP":
                rows[r],rows[z[0]]=rows[z[0]],rows[r]
            elif op=="LAMBDA":
                assert q*q==1
            elif op=="IDLE_ONE":
                rows[r]=scale(rows[r],prod(body[j] for j in z[0]))
            elif op=="IDLE_ODD":
                rows[r]=scale(rows[r],prod(body[j] for j in z[0])*Q(q)**z[1])
            else:
                raise ValueError(op)
            if (r==1 or op=="SWAP" and z[0]==1) and clock>clocks[0]:
                writes.append([clock,event])
    return answers,writes


def controls():
    assert compare({0:Q(1),1:Q(2)},{0:Q(-2),1:Q(-4)})==(Q(-2),None)
    z,w=compare({0:Q(1),1:Q(2)},{0:Q(-2),1:Q(-3)})
    assert z is None and w["cross_product"]=="1"
    assert compare({1:Q(1)},{0:Q(1)})==(None,{"coordinates":[1,0],"cross_product":"1"})
    return ["signed proportional source", "changed intervening write", "outside coordinate"]


def main():
    root=Path(sys.argv[1])
    frozen=checked(root/"price/PRICE.json",PRICE)
    assert frozen["head"]==HEAD
    checks=controls()
    if sys.argv[2:]==["--controls-only"]:
        print(checks)
        return
    c=checked(root/"price/inputs/7113-CALLER.json",CALLER)
    assert (c["types"]["A"]["roles"],len(c["types"]["A"]["ports"]))==(36,96)
    deadline=monotonic()+18
    probes=[(1,)*18,tuple(j+1 for j in range(18)),tuple(2*j+1 for j in range(18))]
    snaps=[]
    for values in probes:
        sources,writes=snapshot(c,CLOCKS,values,-1,deadline)
        snaps.append(sources)
    answer=[]
    for first,second in combinations(CLOCKS,2):
        if monotonic()>=deadline or any(first not in r or second not in r for r in snaps):
            break
        ratios=[]
        reason=None
        for i,source in enumerate(snaps):
            k,w=compare(source[first],source[second])
            if w:
                reason=dict(status="source rows not proportional",probe=i,witness=w)
                break
            ratios.append(str(k))
            if len(set(ratios))>1:
                reason=dict(status="ratio depends on body values",probe=i,ratios=ratios)
                break
        answer.append(dict(key=[first,second],**(reason or dict(status="provisional",ratios=ratios))))
    keys=[list(pair) for pair in combinations(CLOCKS,2)]
    print(json.dumps(dict(head=HEAD,caller_sha256=CALLER,price_sha256=PRICE,case_cap=6,seconds=18,
        q=-1,probes=probes,source_rows=[{i:{k:str(x) for k,x in row.items()} for i,row in r.items()} for r in snaps],
        source_role_writes=writes,decisions=answer,unvisited=keys[len(answer):],
        survivors=[r for r in answer if r["status"]=="provisional"],controls=checks),indent=2,sort_keys=True))


if __name__=="__main__":
    main()
