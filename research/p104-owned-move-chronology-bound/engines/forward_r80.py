"""Exact same-lifetime owned MOVE contractions with unary intervening contacts."""
from collections import Counter
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
import sys
from time import monotonic

HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
WORD_SHA = "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"


def unique(items):
    d=dict(items)
    if len(d)!=len(items):
        raise ValueError("duplicate JSON key")
    return d


def checked(path,digest,compressed=False):
    raw=path.read_bytes()
    if sha256(raw).hexdigest()!=digest:
        raise ValueError(f"changed dependency: {path.name}")
    return json.loads(decompress(raw) if compressed else raw,object_pairs_hook=unique)


def span(frame):
    space={0}
    for vector in frame:
        assert vector and vector not in space
        space|={vector ^ p for p in space}
    return space


def roles(e):
    if e[0] in ("ADD","COPY"):
        return e[1:3]
    assert e[0] in ("MOVE","SCALE","INIT","CLEAR")
    return e[1:2]


def enumerate_turns(word, deadline):
    spans=list(map(span,word["frames"]))
    n=word["public"]
    active=word["initial"]+[None]*word["owned_fields"]
    age={}
    pending={}
    blocks=Counter()
    paid=Counter()
    pairs=[]
    unary=[]
    end=0
    for clock,e in enumerate(word["program"]):
        if clock%128==0 and monotonic()>=deadline:
            break
        end=clock+1
        op,r,*args=e
        if op=="INIT":
            assert r>=n and active[r] is None and r not in age
            active[r]=args[0]
            age[r]=clock
        elif op=="CLEAR":
            assert r>=n and active[r]==args[0] and r in age
            active[r]=None
            del age[r]
            if r in pending:
                del pending[r]
        elif op=="MOVE":
            a,b,owned=args
            assert active[r]==a and owned==(r>=n)
            assert spans[a]<spans[b] or (owned and spans[b]<spans[a])
            active[r]=b
            if owned:
                assert r in age
                paid[abs(len(word["frames"][a])-len(word["frames"][b]))]+=1
                if r in pending:
                    old,source,mid,scales,blocker=pending[r]
                    assert mid==a
                    sign1=(spans[source]<spans[mid])
                    sign2=(spans[a]<spans[b])
                    row=dict(key=[r,age[r],old,clock],frames=[source,mid,b],
                             directions=["up" if sign else "down" for sign in (sign1,sign2)],
                             scales=scales,blocker=blocker,turn=sign1!=sign2)
                    pairs.append(row)
                    if blocker is None and sign1!=sign2:
                        unary.append(row)
                    elif blocker is not None:
                        blocks[blocker[1][0]]+=1
                pending[r]=[clock,a,b,[],None]
        else:
            assert op in ("ADD","COPY","SCALE")
            for q in roles(e):
                assert active[q]==e[-1]
                if q not in pending:
                    continue
                if op=="SCALE":
                    if pending[q][4] is None:
                        pending[q][3].append([clock,e])
                elif pending[q][4] is None:
                    pending[q][4]=[clock,e]
    closed=end==len(word["program"])
    if closed:
        assert active==word["final"]+[None]*word["owned_fields"] and not age and not pending
    return spans, paid, pairs, unary, blocks, end


def evaluate(word,spans,row):
    a,b,c=row["frames"]
    x,y,z=map(lambda i:word["frames"][i],(a,b,c))
    old=[abs(len(y)-len(x)),abs(len(z)-len(y))]
    if spans[a]==spans[c] and a!=c:
        return dict(key=row["key"],decision="equal spans with distinct chart labels",old=old)
    if not (a==c or spans[a]<spans[c] or spans[c]<spans[a]):
        return dict(key=row["key"],decision="non-nested endpoints",old=old)
    changes=Counter(old)
    changes=Counter({r:-c for r,c in changes.items()})
    new=abs(len(z)-len(x))
    if new:
        changes[new]+=1
    # The retained physical canonical frame, scalar, and phase must still replay.
    coeff=Fraction(1)
    for _,event in row["scales"]:
        assert event[:2]==["SCALE",row["key"][0]] and event[-1]==b
        coeff*=Fraction(event[2])
    return dict(key=row["key"],decision="nested unary survivor",old=old,new=new,
                native_paid_delta={r:c for r,c in changes.items() if c},scalar_product=str(coeff))


def controls():
    w=dict(public=1,owned_fields=1,initial=[1],final=[1],frames=[[],[1],[1,2]],
           program=[["INIT",1,1],["MOVE",1,1,2,True],["SCALE",1,"-2",2],
                    ["MOVE",1,2,1,True],["CLEAR",1,1]])
    space, paid, pairs, unary, _, _=enumerate_turns(w,monotonic()+2)
    assert paid=={1:2} and len(unary)==len(pairs)==1
    assert evaluate(w,space,unary[0])["native_paid_delta"]=={1:-2}
    blocked=dict(w,program=w["program"][:1]+[["MOVE",1,1,0,True],["MOVE",1,0,1,True],
                 ["ADD",0,1,"1",1],["MOVE",1,1,0,True],["CLEAR",1,0]])
    _,_,p,u,_,_=enumerate_turns(blocked,monotonic()+2)
    assert len(u)==1 and p[1]["blocker"][1]==["ADD",0,1,"1",1]
    return ["unary signed round trip", "binary source read blocks pair"]


def main():
    root=Path(sys.argv[1])
    price_hash=sys.argv[2]
    price=checked(root/"price/PRICE.json",price_hash)
    word=checked(root/"inputs/7334-WORD.json.gz",WORD_SHA,compressed=True)
    assert HEAD in (price.get("head"),price.get("comparator_head"))
    checks=controls()
    deadline=monotonic()+18
    spans,paid,pairs,unary,blocks,end=enumerate_turns(word,deadline)
    if end==len(word["program"]):
        assert sum(paid.values())==47
    chosen=[]
    for row in unary[:4]:
        if monotonic()>=deadline:
            break
        chosen.append(evaluate(word,spans,row))
    print(json.dumps(dict(head=HEAD,word_sha256=WORD_SHA,price_sha256=price_hash,
        total_events=len(word["program"]),visited_events=end,paid_owned_rank=paid,
        consecutive_same_lifetime_pairs=pairs,blocked_by=blocks,eligible_turns=unary,
        tested=chosen,remaining=[row["key"] for row in unary[len(chosen):]],
        case_cap=4,seconds_cap=18,controls=checks,
        status="EXHAUSTED" if end==len(word["program"]) and len(chosen)==len(unary) else "CAPPED"),
        indent=2,sort_keys=True))


if __name__=="__main__":
    main()
