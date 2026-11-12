"""Direct endpoint tangents and independent prefix/suffix impulses for R123."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from itertools import combinations
from json import dumps,loads
from pathlib import Path
from signal import SIGALRM,alarm,signal
from time import monotonic

ROOT=Path(__file__).resolve().parents[1]
PINS={
    "plan/PRICE.json":"3633b57cc096fe511daac7c23ead578f839096df8b6ef62651844c2e62a3f2a6",
    "inputs/7113-CALLER.json.gz":"7e8038559cd158f6e32ef6d1a3bf15ab6a8ecc2239af32ab1699511ac28e26d9",
}
HEAD="aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER="07a76c5e2738882c0cb322278e56f6cae3c9885d"
CALLER_PAYLOAD="255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
CAP,SECONDS=210,25


def unique(pairs):
    result=dict(pairs)
    if len(result)!=len(pairs):
        raise ValueError("duplicate JSON key")
    return result


def checked(root,name):
    raw=(root/name).read_bytes()
    if sha256(raw).hexdigest()!=PINS[name]:
        raise ValueError("changed dependency "+name)
    return raw


def unit_ops(events,n,offset):
    """Decode the signed caller only at q=+1 and body variables all one."""
    rows,odd,even=[],{},{}
    hosts=0
    for t,event in enumerate(events):
        ty,tag,*tail=event
        if ty=="J":
            assert type(tag) is int and tag==hosts+1
            hosts+=1
            u,v,left,right=tail[1]
            u,v=u-offset,v-offset
            assert 0<=u<n and 0<=v<n and u!=v
            rows.append((("ADD",u,v,Q(left)),("ADD",v,u,Q(right))))
            continue
        assert ty in ("A","B")
        ops=()
        if ty=="B":
            d,*a=tail
            d-=offset
            assert 0<=d<n
            if tag in ("ADD","QUERY","SWAP"):
                s=a[0]-offset
                assert 0<=s<n and s!=d
                q=Q(a[1]) if tag=="ADD" else Q(1)
                if tag=="QUERY":
                    assert a[1] in (-1,1)
                ops=(("SWAP" if tag=="SWAP" else "ADD",d,s,q),)
            elif tag=="SCALE":
                q=Q(a[0])
                assert q
                ops=(("SCALE",d,d,q),)
            elif tag in ("IDLE_ODD","IDLE_ONE"):
                mask=tuple(sorted(a[0]))
                assert mask and len(mask)==len(set(mask)) and all(1<=x<=17 for x in mask)
                if tag=="IDLE_ODD":
                    assert len(mask)==1 and a[1:]==[-1]
                    odd[t]=(d,mask)
                else:
                    assert len(a)==1
                    even[t]=(d,mask)
            else:
                assert tag=="LAMBDA" and len(a)==1 and a[0] in (-1,1)
        rows.append(ops)
    assert hosts==17 and len(odd)==4 and len(even)==60
    return rows,odd,even


def stock(odd,even):
    eligible=[(o,e) for o,(_,a) in odd.items() for e,(_,b) in even.items() if set(a).isdisjoint(b)]
    assert len(eligible)==180
    keys,total=[],0
    for (o,e),(p,f) in combinations(sorted(eligible),2):
        if o==p or e==f:
            continue
        total+=1
        if even[e][1]==even[f][1]:
            keys.append({"fusions":[[o,e],[p,f]],"even_mask":list(even[e][1])})
    keys.sort(key=lambda r:(-len(r["even_mask"]),r["fusions"]))
    return keys,total


def axpy(dst,src,q):
    out=dst.copy()
    for k,v in src.items():
        z=out.get(k,0)+q*v
        if z:
            out[k]=z
        else:
            out.pop(k,None)
    return out


def update(vectors,op,reverse=False):
    tag,d,s,q=op
    if tag=="ADD":
        if reverse:
            d,s=s,d
        vectors[d]=axpy(vectors[d],vectors[s],q)
    elif tag=="SCALE":
        vectors[d]={k:q*v for k,v in vectors[d].items()}
    else:
        assert tag=="SWAP"
        vectors[d],vectors[s]=vectors[s],vectors[d]


def identity(n):
    return [{i:Q(1)} for i in range(n)]


def tangent(steps,injections,n):
    primal=identity(n)
    derivative=[{} for _ in range(n)]
    for t,ops in enumerate(steps):
        if t in injections:
            r,sign=injections[t]
            assert not ops
            derivative[r]=axpy(derivative[r],primal[r],sign)
        for op in ops:
            update(primal,op)
            update(derivative,op)
    return primal,{(i,j):v for i,row in enumerate(derivative) for j,v in row.items()}


def impulses(steps,roles,n,deadline):
    rows,columns=identity(n),identity(n)
    prefix,suffix={},{}
    for t,ops in enumerate(steps):
        if t%128==0 and monotonic()>=deadline:
            raise TimeoutError("prefix impulse cap")
        if t in roles:
            assert not ops
            prefix[t]=rows[roles[t]]
        for op in ops:
            update(rows,op)
    for t in range(len(steps)-1,-1,-1):
        if t%128==0 and monotonic()>=deadline:
            raise TimeoutError("suffix impulse cap")
        if t in roles:
            suffix[t]=columns[roles[t]]
        for op in reversed(steps[t]):
            update(columns,op,True)
    assert rows==columns==identity(n)
    return {t:{(i,j):u*v for i,u in suffix[t].items() for j,v in prefix[t].items()} for t in roles}


def exact_delta(terms,placements,roles):
    inject={t:(roles[t],sign) for o,e in placements for t,sign in ((o,1),(e,-1))}
    assert len(inject)==2*len(placements)
    out={}
    for t,(_,sign) in inject.items():
        out=axpy(out,terms[t],sign)
    return out,inject


def controls():
    steps=[(),(),(("SWAP",0,1,Q(1)),),(),(),(("SWAP",0,1,Q(1)),)]
    roles={0:0,1:1,3:0,4:1}
    terms=impulses(steps,roles,2,float("inf"))
    first,_=exact_delta(terms,[(0,1)],roles)
    other,_=exact_delta(terms,[(3,4)],roles)
    total,inject=exact_delta(terms,[(0,1),(3,4)],roles)
    assert first and other and not total
    assert tangent(steps,inject,2)==(identity(2),{})
    inject[4]=(1,1)
    assert tangent(steps,inject,2)[1]
    fraction=identity(2)
    update(fraction,("ADD",0,1,Q(-3,2)))
    assert fraction[0]=={0:1,1:Q(-3,2)}
    return ["two nonzero transported derivatives cancel across swaps","wrong sign spoils cancellation","exact fractional transport"]


def launch(caller,price,deadline,rows,progress):
    b=caller["types"]["B"]
    n,offset=b["roles"],b["offset"]
    assert (caller["stages"],n,offset,len(b["ports"]))==(17,36,36,8)
    steps,odd,even=unit_ops(caller["events"],n,offset)
    keys,total=stock(odd,even)
    assert keys==price["equal_mask_keys"] and len(keys)==CAP
    assert total==price["all_disjoint_pair_placements"]==11938
    assert total-len(keys)==price["unequal_mask_exclusions"]==11728
    roles={t:r for t,(r,_) in (odd|even).items()}
    progress.update(caller_events=len(steps),literal_single_edits=180,odd_sites=len(odd),even_sites=len(even))
    direct=[]
    for item in keys[:2]:
        assert len(item["even_mask"])==8
        inject={t:(roles[t],sign) for o,e in item["fusions"] for t,sign in ((o,1),(e,-1))}
        assert len(inject)==4
        old,delta=tangent(steps,inject,n)
        assert old==identity(n)
        direct.append(delta)
    progress["old_endpoint_columns"]=n
    progress["direct_tangent_keys"]=2
    terms=impulses(steps,roles,n,deadline)
    for i,item in enumerate(keys):
        if monotonic()>=deadline:
            raise TimeoutError("paired derivative cap")
        delta,_=exact_delta(terms,item["fusions"],roles)
        if i<2:
            assert delta==direct[i]
        witness=None
        if delta:
            a,b=min(delta)
            witness=[a+offset,b+offset,str(delta[a,b])]
        rows.append(item|dict(status="exact derivative exclusion" if witness else "first derivative zero",
            witness=witness,nonzero_coordinates=len(delta),direct_tangent=i<2))


def main():
    parser=ArgumentParser()
    parser.add_argument("--root",type=Path,default=ROOT)
    parser.add_argument("--controls-only",action="store_true")
    args=parser.parse_args()
    assert __debug__
    price=loads(checked(args.root,"plan/PRICE.json"),object_pairs_hook=unique)
    assert price["head"]==HEAD and price["caller"]==CALLER and price["caller_sha256"]==CALLER_PAYLOAD
    assert price["first_gate"]=={"keys":CAP,"runner_seconds":SECONDS}
    assert price["formal_gate"]=={"keys":4,"runner_seconds":35}
    tests=controls()
    keys=price["equal_mask_keys"]
    assert len(keys)==CAP
    if args.controls_only:
        print(dumps(dict(controls=tests,highest_price=keys[:2]),indent=2,sort_keys=True))
        return 0

    def stop(*_):
        raise TimeoutError("hard 25-second cap")

    signal(SIGALRM,stop)
    alarm(SECONDS)
    rows,progress,error=[],{},None
    try:
        raw=decompress(checked(args.root,"inputs/7113-CALLER.json.gz"))
        assert sha256(raw).hexdigest()==CALLER_PAYLOAD
        launch(loads(raw,object_pairs_hook=unique),price,monotonic()+22,rows,progress)
    except TimeoutError as exc:
        error=str(exc)
    finally:
        alarm(0)
    print(dumps(dict(head=HEAD,caller=CALLER,pins=PINS,q=1,body="unit",controls=tests,
        cap_cases=CAP,cap_seconds=SECONDS,counts=Counter(r["status"] for r in rows),progress=progress,
        results=rows,unvisited=keys[len(rows):],timeout=error),indent=2,sort_keys=True))
    return 2 if error else 0


if __name__=="__main__":
    raise SystemExit(main())
