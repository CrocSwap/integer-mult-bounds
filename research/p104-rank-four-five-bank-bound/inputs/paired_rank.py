"""Rational paired exclusion using wedge identities and a stacked rank check."""
from collections import Counter
from fractions import Fraction as Q
from functools import cache
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
import sys
from time import monotonic

GEOMETRY="4c349e06b22bfebb431fab1c9ae04f0e798f398acc6fdd99591b49b1c95ef6ca"
WORD="4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"


@cache
def coefficient(s):
    return Q(s)


def checked(path,digest):
    data=path.read_bytes()
    if sha256(data).hexdigest()!=digest:
        raise ValueError(f"changed pin: {path.name}")
    return data


def plus(row,other,q):
    for i,x in other.items():
        v=row.get(i,0)+q*x
        if v:
            row[i]=v
        else:
            row.pop(i,None)


def null_pure(bank,rows,allowed):
    """Eliminate exterior inputs, carrying coefficient vectors on the bank."""
    pivots={}
    pure=[]
    for r in bank:
        row={i:x for i,x in rows[r].items() if i not in allowed}
        u={r:Q(1)}
        while row:
            lead=max(row)
            if lead not in pivots:
                pivots[lead]=row,u
                break
            p,a=pivots[lead]
            ratio=-row[lead]/p[lead]
            plus(row,p,ratio)
            plus(u,a,ratio)
        else:
            full={}
            for i,x in u.items():
                plus(full,rows[i],x)
            assert set(full)<=allowed
            pure.append((u,full))
    assert len(pivots)+len(pure)==len(bank)
    return pure


def rank(matrix):
    basis={}
    for source in matrix:
        row=source.copy()
        while row:
            lead=max(row)
            if lead not in basis:
                basis[lead]=row
                break
            plus(row,basis[lead],-row[lead]/basis[lead][lead])
    return len(basis)


def pairing(B,D):
    # No (x,y) with xBy=1 and xDy=0 iff each xB is proportional to xD
    # and ker(x -> xD) lies inside ker(x -> xB).
    rows=len(B)
    cols=len(B[0]) if B else 0
    def wedge(b,d):
        return any(b[i]*d[j]!=b[j]*d[i] for i in range(cols) for j in range(i))
    has_wedge=any(wedge(b,d) for b,d in zip(B,D,strict=True))
    if not has_wedge:
        for i in range(rows):
            for j in range(i):
                if wedge([x+y for x,y in zip(B[i],B[j],strict=True)],
                         [x+y for x,y in zip(D[i],D[j],strict=True)]):
                    has_wedge=True
                    break
            if has_wedge:
                break
    dr=rank([{i:x for i,x in enumerate(r) if x} for r in D])
    sr=rank([{i:x for i,x in enumerate(d+b) if x} for d,b in zip(D,B,strict=True)])
    return has_wedge,dr,sr


def side(word,banks,allowed,deadline,reverse):
    n=word["public"]
    tape=word["program"]
    vectors=[{i:Q(1)} for i in range(n)]+[{} for _ in range(word["owned_fields"])]
    rows={}
    cuts=range(len(tape),min(banks)-1,-1) if reverse else range(0,max(banks)+1)
    for t in cuts:
        if t%128==0 and monotonic()>=deadline:
            break
        if t in banks:
            rows[t]=null_pure(banks[t],vectors,allowed)
        if t==0 and reverse:
            break
        op,d,*args=tape[t-1 if reverse else t]
        if op=="MOVE":
            continue
        if op in ("INIT","CLEAR"):
            vectors[d]={}
        else:
            q=coefficient(args[-2])
            source=d if op=="SCALE" else args[0]
            assert op=="SCALE" or source!=d
            if op=="SCALE":
                vectors[d]={i:q*x for i,x in vectors[d].items()}
            elif reverse:
                plus(vectors[source],vectors[d],q)
                if op=="COPY":
                    vectors[d]={}
            elif op=="COPY":
                vectors[d]={i:q*x for i,x in vectors[source].items()}
            else:
                assert op=="ADD"
                plus(vectors[d],vectors[source],q)
    return rows


def run(word,geom,keys):
    deadline=monotonic()+32
    groups=Counter(k[0] for k in keys)
    banks={row["cut"]:row["public_bank"] for row in geom["new"]["rows"] if row["cut"] in groups}
    allowed=set(geom["endpoint_cohort"])
    forward=side(word,banks,allowed,deadline,False)
    reverse=side(word,banks,allowed,deadline,True)
    ans=[]
    def dot(a,b):
        return sum(x*b.get(i,0) for i,x in a.items())
    for t,n in sorted(groups.items()):
        if t not in forward or t not in reverse or monotonic()>=deadline:
            continue
        F,R=forward[t],reverse[t]
        w=dr=sr=None
        if not any(c for a,c in F):
            status="no nonzero pure prefix"
        elif not any(d for b,d in R):
            status="no nonzero pure suffix"
        else:
            B=[[dot(a,b) for b,d in R] for a,c in F]
            C=[[dot(c,d) for b,d in R] for a,c in F]
            D=[[x-y for x,y in zip(b,c,strict=True)] for b,c in zip(B,C,strict=True)]
            w,dr,sr=pairing(B,D)
            status="paired support unresolved" if w or dr!=sr else "no unit pairing"
        ans.append(dict(cut=t,cases=n,status=status,prefix_dimension=len(F),suffix_dimension=len(R),
                        nonzero_wedge=w,exterior_rank=dr,stacked_rank=sr))
    missing=set(groups)-{r["cut"] for r in ans}
    counts=Counter()
    for row in ans:
        counts[row["status"]]+=row["cases"]
    return dict(cases=len(keys),rows=ans,counts=dict(counts),
                unvisited=[key for key in keys if key[0] in missing])


def main():
    root=Path(sys.argv[1])
    which=sys.argv[2]
    assert which in ("first","remaining")
    geom=json.loads(checked(root/"lead/OCCUPANCY.json",GEOMETRY))
    word=json.loads(decompress(checked(root/"inputs/7334-WORD.json.gz",WORD)))
    assert pairing([[Q(1),Q(0)]],[[Q(0),Q(1)]])[0]
    assert pairing([[Q(1)]],[[Q(2)]])==(False,1,1)
    assert pairing([[Q(1)]],[[Q(0)]])==(False,0,1)
    keys=geom["representative_keys" if which=="first" else "unvisited_keys"]
    assert len(keys)==(128 if which=="first" else 18)
    data=run(word,geom,keys)
    print(json.dumps(data|dict(selection=which,word_sha256=WORD,geometry_sha256=GEOMETRY,
        controls=["nonzero wedge","proportional equal rank","nonzero pairing on difference kernel"]),
        indent=2,sort_keys=True))


if __name__=="__main__":
    main()
