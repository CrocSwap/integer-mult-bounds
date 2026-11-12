"""Match the literal ADD source using other live rows in the retimed chart."""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import cache
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
import sys
from time import monotonic

HEAD="aaeec8c0acf01e99a5f331ef363a698d9c084ace"
WORD="4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"
PRICE="c9166ff18194a7e69f91a06f76329a2ff838bb65b08c4ed7a5a06038fdfa966d"


def checked(path,want,compressed=False):
    raw=path.read_bytes()
    if sha256(raw).hexdigest()!=want:
        raise ValueError(f"changed dependency: {path.name}")
    return json.loads(decompress(raw) if compressed else raw)


@cache
def scalar(x):
    return Q(x)


def axpy(dst,src,c):
    for k,a in src.items():
        value=dst.get(k,0)+c*a
        if value:
            dst[k]=value
        else:
            dst.pop(k,None)


def reduce_row(row,basis,weights,multiplier):
    for k,(v,w) in sorted(basis.items()):
        a=row.get(k,0)
        if a:
            axpy(row,v,-a)
            axpy(weights,w,multiplier*a)


def solve(target,bank,deadline):
    basis={}
    for role,vector in sorted(bank.items()):
        if monotonic()>=deadline:
            return None
        r=vector.copy()
        w={role:Q(1)}
        reduce_row(r,basis,w,-1)
        if r:
            k=min(r)
            d=r[k]
            basis[k]=({i:a/d for i,a in r.items()},{i:a/d for i,a in w.items()})
    residual=target.copy()
    weights={}
    reduce_row(residual,basis,weights,1)
    rebuilt={}
    for role,a in weights.items():
        axpy(rebuilt,bank[role],a)
    axpy(rebuilt,residual,Q(1))
    assert rebuilt==target
    return dict(rank=len(basis), residual={i:str(v) for i,v in residual.items()},
                matching_coefficients={i:str(v) for i,v in weights.items()} if not residual else None)


def snapshot(word,requested,targets,deadline):
    public=word["public"]
    active=word["initial"]+[None]*word["owned_fields"]
    rows=[{i:Q(1)} for i in range(public)]+[None]*word["owned_fields"]
    banks,values={},{}
    stop=max(requested.keys()|targets.keys())
    for t,e in enumerate(word["program"]):
        if t%64==0 and monotonic()>=deadline:
            break
        for chart,r in requested.get(t,()):
            banks[t,chart,r]={i:rows[i].copy() for i in range(len(active)) if i!=r and active[i]==chart and rows[i]}
        for s in targets.get(t,()):
            assert active[s] is not None
            values[t,s]=rows[s].copy()
        if t==stop:
            break
        op,r,*args=e
        if op=="MOVE":
            assert active[r]==args[0] and args[2]==(r>=public)
            active[r]=args[1]
        elif op=="INIT":
            assert active[r] is None and rows[r] is None and r>=public
            active[r]=args[0]
            rows[r]={}
        elif op=="CLEAR":
            assert active[r]==args[0] and rows[r] is not None and r>=public
            active[r]=rows[r]=None
        elif op=="SCALE":
            assert active[r]==args[1] and scalar(args[0])
            rows[r]={i:v*scalar(args[0]) for i,v in rows[r].items()}
        else:
            s,k,chart=args
            assert active[r]==active[s]==chart and r!=s and op in ("ADD","COPY")
            if op=="COPY":
                assert r>=public and not rows[r]
            axpy(rows[r],rows[s],scalar(k))
    return banks,values


def controls():
    d=monotonic()+1
    a,b={0:Q(1),1:Q(1)},{1:Q(2)}
    assert solve({0:Q(3)}, {7:a,8:b},d)["matching_coefficients"]=={7:"3",8:"-3/2"}
    assert solve({2:Q(1)}, {7:a,8:b},d)["residual"]=={2:"1"}
    assert solve({0:Q(3)}, {7:{0:Q(1),2:Q(1)},8:b},d)["residual"]=={2:"-3"}
    assert solve({}, {7:a},d)["matching_coefficients"]=={}
    return ["two-donor span","separating coordinate","changed donor row","zero source"]


def main():
    root=Path(sys.argv[1])
    price=checked(root/"price/PRICE.json",PRICE)
    word=checked(root/"inputs/7334-WORD.json.gz",WORD,True)
    assert price["head"]==HEAD and price["word_sha256"]==WORD
    moves=word["program"]
    req,targets=defaultdict(set),defaultdict(set)
    bykey={}
    for p in price["candidates"]:
        r,s=p["owner"],p["peer"]
        f,g=p["move_clocks"]
        a,b,c=p["chart_path"]
        t,add=p["literal_ADD"]
        assert add[:2]==[r,s] and moves[t]==["ADD",*add] and f<t<g
        assert moves[f]==["MOVE",r,a,b,True] and moves[g]==["MOVE",r,b,c,True]
        for e in moves[f+1:t]+moves[t+1:g]:
            assert r not in (e[1:3] if e[0] in ("ADD","COPY") else e[1:2])
        targets[t].add(s)
        for end,(lo,hi) in p["cut_windows_pre_event"].items():
            chart=a if end=="entrance" else c
            for cut in range(lo,hi+1):
                req[cut].add((chart,r))
                bykey[r,f,g,end,cut]=(t,s,chart)
    assert len(bykey)==33 and set(bykey)=={tuple(k) for k in price["keys"]}
    checks=controls()
    deadline=monotonic()+18
    banks,values=snapshot(word,req,targets,deadline)
    output,pending=[],[]
    for key in price["keys"]:
        r,_,_,_,cut=key
        t,s,chart=bykey[tuple(key)]
        if monotonic()>=deadline or (t,s) not in values or (cut,chart,r) not in banks:
            pending.append(key)
            continue
        bank=banks[cut,chart,r]
        source=values[t,s]
        result=solve(source,bank,deadline)
        if result is None:
            pending.append(key)
            continue
        output.append(dict(key=key,source=[t,s],target_chart=chart,bank_roles=sorted(bank),
                           source_nnz=len(source),**result,
                           decision="exact span survivor" if result["matching_coefficients"] is not None else "outside donor span"))
    print(json.dumps(dict(head=HEAD,price_sha256=PRICE,word_sha256=WORD,status="CAPPED" if pending else "EXHAUSTED",
        case_cap=33,seconds_cap=18,controls=checks,counts=Counter(x["decision"] for x in output),
        decisions=output,unvisited=pending,survivors=[x["key"] for x in output if x["matching_coefficients"] is not None]),
        indent=2,sort_keys=True))


if __name__=="__main__":
    main()
