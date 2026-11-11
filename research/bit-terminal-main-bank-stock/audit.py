"""Independent projective-normal and marked-suffix audit of all stock classes."""
from collections import defaultdict
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys

WORD="51203e7fc75ba10bd3ac3f8e675759f47e13d262bea66b6600d1e515095cad78"


def normalize(x):
    a=next(t for t in x if t)
    return tuple(t/a for t in x)


def dot(a,b):
    return sum(x*y for x,y in zip(a,b,strict=True))


def ledger(w,dim):
    # Carry bank identity forward across the physical role swaps.
    current=[None]*(w["public"]+w["owned_fields"])
    for t,(op,i,*a) in enumerate(w["program"]):
        if op=="MOVE":
            current[i]=(t,i,a[0],a[1])
        elif op=="SWAP":
            j=a[0]
            current[i],current[j]=current[j],current[i]
        elif op in ("INIT","CLEAR"):
            current[i]=None
    eligible={}
    main=[]
    for i,f in enumerate(w["final"]):
        if f!=1:
            continue
        t,j,b,e=current[i]
        assert e==1
        if dim[b]<=6:
            eligible[t]=(j,b)
            if i<222:
                main.append(t)
    assert len(eligible)==185 and len(main)==22
    return eligible,set(main)


def sweep(w,dim,selected,reverse):
    n=w["public"]
    rows=[{i} for i in range(n)]+[set() for _ in range(w["owned_fields"])]
    frames=(w["final"] if reverse else w["start"])+[None]*w["owned_fields"]
    literal=defaultdict(set)
    virtual={}
    def store(j):
        f=frames[j]
        if f is not None and dim[f]==7:
            literal[f].add(sum(1<<i for i in rows[j]))
    for i in range(len(rows)):
        store(i)
    order=list(enumerate(w["program"]))
    for t,(op,i,*a) in (reversed(order) if reverse else order):
        changed=[i]
        if t in selected:
            virtual[t]=sum(1<<j for j in rows[i])
        if op=="ADD":
            j,f=a
            assert frames[i]==frames[j]==f
            x,y=(j,i) if reverse else (i,j)
            rows[x]=rows[x]^rows[y]
            changed=[x]
        elif op=="SWAP":
            j=a[0]
            frames[i],frames[j]=frames[j],frames[i]
            rows[i],rows[j]=rows[j],rows[i]
            changed.append(j)
        elif op=="MOVE":
            old,new=(a[1],a[0]) if reverse else a
            assert frames[i]==old
            frames[i]=new
        elif op=="INIT":
            frames[i]=None if reverse else a[0]
            rows[i]=set()
        else:
            assert op=="CLEAR"
            frames[i]=a[0] if reverse else None
            rows[i]=set()
        for j in changed:
            store(j)
    return literal,virtual


def hi_basis(vectors):
    b={}
    for x in vectors:
        while x:
            p=x.bit_length()-1
            if p not in b:
                b[p]=x
                break
            x^=b[p]
    return b


def quotient(raw,outside):
    b=list(hi_basis(raw).values())
    equations=[sum(((v>>i)&1)<<j for j,v in enumerate(b)) for i in outside]
    rows=hi_basis(equations)
    values=[]
    for i in range(len(b)):
        if i in rows:
            continue
        coefficients=1<<i
        for j,e in sorted(rows.items()):
            if (e&coefficients).bit_count()%2:
                coefficients|=1<<j
        v=0
        for j,x in enumerate(b):
            if coefficients>>j&1:
                v^=x
        assert all(not(v>>i&1) for i in outside)
        values.append(v)
    return values


def run(native,receipt):
    raw=native.read_bytes()
    assert sha256(raw).hexdigest()==WORD
    w=json.loads(gzip.decompress(raw))
    data=json.loads(receipt.read_bytes())
    dim={int(k):v["dim"] for k,v in w["frames"].items()}
    B={int(k):[tuple(map(Q,u)) for u in v["B"]] for k,v in w["frames"].items()}
    A={int(k):[tuple(map(Q,u)) for u in v["A"]] for k,v in w["frames"].items()}
    canonical={normalize(A[f][0]):f for f in dim if dim[f]==7}
    eligible,main=ledger(w,dim)
    prefix,P=sweep(w,dim,eligible,False)
    suffix,S=sweep(w,dim,eligible,True)
    group={i for i in range(222,w["public"]) if (w["start"][i],w["final"][i])==(0,1)}
    outside=[i for i in range(w["public"]) if i not in group]
    mark=1<<w["public"]
    cases=duals=paired_fail=0
    assert {x["event"] for x in data["bank_maps"]}==main
    for row in data["bank_maps"]:
        t=row["event"]
        j,f=eligible[t]
        assert j==row["role"]
        assert P[t]==sum(1<<i for i in row["prefix_input"])
        assert S[t]==sum(1<<i for i in row["suffix_response"])
        left,right=A[f]
        generics=set()
        specific=defaultdict(set)
        for k,(_,src) in eligible.items():
            vectors=[(dot(left,b),dot(right,b)) for b in B[src]]
            active=[(u,v) for u,v in vectors if u or v]
            if not active:
                generics.add(k)
                continue
            u,v=active[0]
            if all(u*y==v*x for x,y in active):
                n=normalize(tuple(v*a-u*b for a,b in zip(left,right,strict=True)))
                specific[n].add(k)
        for n in canonical:
            if all(dot(n,b)==0 for b in B[f]):
                specific[n]
        expected={None:generics}
        expected.update({n:generics|x for n,x in specific.items()})
        assert len(expected)==len(row["variants"])
        for item in row["variants"]:
            value=item["midpoint_normal"]
            normal=None if value is None else tuple(map(Q,value))
            cohort=expected.pop(normal)
            chart=canonical.get(normal)
            assert chart==item["literal_chart"] and cohort==set(item["virtual_bank_events"])
            p=quotient(sorted(prefix.get(chart,set())|{P[k] for k in cohort}),outside)
            o=sorted(suffix.get(chart,set())|{S[k] for k in cohort if k!=t})
            q=quotient(o+[S[t]|mark],outside)
            assert len(hi_basis(p))==item["prefix_group_rank"]
            if not any(v&mark for v in q):
                d=sum(1<<i for i in item["outside_dual"])
                assert d&S[t] and (d&S[t]).bit_count()%2
                assert set(item["outside_dual"])<=set(outside)
                assert all(not (d&v).bit_count()%2 for v in o)
                assert item["compulsory_suffix_group_span_rank"] is None
                duals+=1
            else:
                assert item["outside_dual"] is None
                q=[v&~mark for v in q]
                assert len(hi_basis(q))==item["compulsory_suffix_group_span_rank"]
                assert all(not (a&b).bit_count()%2 for a in p for b in q)
                paired_fail+=1
            assert not item["paired_support"]
            cases+=1
        assert not expected and not row["viable"]
    assert (cases,duals,paired_fail)==(110,70,40)
    return {"status":"PASS_PROJECTIVE_NORMAL_SET_SWEEP_AND_MARKED_SUFFIX","canonical_word":WORD,
            "classes":cases,"outside_duals":duals,"outside_canceled_but_unpaired":paired_fail,"stock":0}


if __name__=="__main__":
    assert __debug__
    print(json.dumps(run(*map(Path,sys.argv[1:])),sort_keys=True,indent=2))
