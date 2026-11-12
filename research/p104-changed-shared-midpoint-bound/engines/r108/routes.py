"""Authenticate ten anchors and price actual four-clock rank changes."""
from bisect import bisect_left
from collections import Counter, defaultdict
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT=Path(__file__).resolve().parents[1]
PINS={
    "inputs/7334-WORD.json.gz":"4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/R100-PRICE.json":"7109125bbf60e3015c8c0ac7b10b24b7de61f358c1508d06604ebccd89ef6343",
    "inputs/R92-PRICE.json":"05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/STOCK.json":"2d256cbcc5fcbf2fb361c47b2d764c98e2f5ba1f734abb95e03be3935223ff28",
    "inputs/pricing.py":"f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}


def checked():
    out={}
    for path,pin in PINS.items():
        raw=(ROOT/path).read_bytes()
        if sha256(raw).hexdigest()!=pin:
            raise ValueError(f"changed dependency {path}")
        out[path]=raw
    return out


def touches(e):
    op,d,*a=e
    return (d,a[0]) if op in ("ADD","COPY") else (d,)


def enclosing(clocks,t):
    i=bisect_left(clocks,t)
    assert clocks[i]==t
    return [clocks[i-1] if i else None,clocks[i+1] if i+1<len(clocks) else None]


def paid_delta(ranks,d):
    p,q,l,r=ranks
    new=Counter((p+d,q-d,l+d,r-d))
    new.subtract(ranks)
    return {k:17*v for k,v in new.items() if v}


def stop(*_):
    raise TimeoutError("R108 topology cap")


def main():
    assert __debug__
    assert enclosing([3,4,7],4)==[3,7]
    assert paid_delta((3,3,3,3),1)=={4:34,2:34,3:-68}
    signal(SIGALRM,stop)
    alarm(20)
    deadline=monotonic()+18
    raw=checked()
    old,prior,stock=[json.loads(raw[p]) for p in ("inputs/R100-PRICE.json","inputs/R92-PRICE.json","inputs/STOCK.json")]
    assert old["head"]==prior["head"]==stock["head"]
    word_data=decompress(raw["inputs/7334-WORD.json.gz"])
    assert sha256(word_data).hexdigest()==old["word_payload_sha256"]
    word=json.loads(word_data)
    tape=word["program"]
    frames=word["frames"]
    n=word["public"]
    assert len(tape)==76466 and n==1501
    rows=stock["midpoint_rank_tilt"]["anchors"]
    assert len(rows)==10
    roles={r for a in rows for r in (a["key"][2],a["peer"])}
    log=defaultdict(list)
    for t,e in enumerate(tape):
        if t%128==0 and monotonic()>=deadline:
            raise TimeoutError("R108 contact index")
        for r in touches(e):
            if r in roles:
                log[r].append(t)
    invoice=Counter({int(k):v for k,v in prior["old_targets"].items()})
    invoice.subtract({int(k):v for k,v in prior["old_paid"].items()})
    assert sum(k*v for k,v in invoice.items())==1424
    at,probe,target=[Q(old[k]) for k in ("old_crossing_upper","probe","fixed_target")]
    cost=run_path(str(ROOT/"inputs/pricing.py"))["cost"]
    results=[]
    counts=Counter()
    for row in rows:
        f,g,s=row["key"]
        p=row["peer"]
        a,b,c=row["charts"]
        t,add=row["contact"]
        assert tape[t]==add and set(add[1:3])=={s,p} and s<n and p<n
        assert enclosing(log[s],t)==[f,g] and tape[f]==["MOVE",s,a,b,False] and tape[g]==["MOVE",s,b,c,False]
        i,j=enclosing(log[p],t)
        other=[None if k is None else tape[k] for k in (i,j)]
        match=(all(e is not None and e[0]=="MOVE" and not e[4] and e[1]==p for e in other)
               and other[0][3]==other[1][2]==b)
        record=dict(key=row["key"],clock=t,mover=s,peer=p,add=add,old_chart=b,anchor_move_clocks=[f,g],
                    peer_neighbour_clocks=[i,j],peer_neighbour_events=other,variants=[])
        if not match:
            record["status"]="no four-MOVE topology"
        else:
            assert len({f,g,i,j,t})==5
            ap,cp=other[0][2],other[1][3]
            rs=[len(frames[b])-len(frames[a]),len(frames[c])-len(frames[b]),
                len(frames[b])-len(frames[ap]),len(frames[cp])-len(frames[b])]
            assert all(r>0 for r in rs)
            record.update(charts=[a,ap,b,c,cp],ranks=rs,all_paid_clocks=[f,g,i,j])
            for d in range(1-min(rs[0],rs[2]),min(rs[1],rs[3])):
                if not d:
                    continue
                delta=paid_delta(rs,d)
                signed={k:-v for k,v in delta.items()}
                after=invoice.copy()
                after.update(signed)
                lower,upper=cost(after,probe)
                margin=cost(signed,at)
                assert sum(k*v for k,v in delta.items())==0 and sum(delta.values())==0
                record["variants"].append(dict(offset=d,required_rank=len(frames[b])+d,paid_delta=delta,
                    net=list(map(str,margin)),full_probe=[str(lower),str(upper)],
                    target_net=list(map(str,cost(signed,target))),
                    status="positive" if lower>0 else "nonpositive" if upper<=0 else "price unresolved"))
            record["status"]="four-MOVE topology"
        counts[record["status"]]+=1
        results.append(record)
    alarm(0)
    variants=[v for r in results for v in r["variants"]]
    assert len(variants)<=160
    print(json.dumps(dict(head=old["head"],caller=old["caller_head"],pins=PINS,events=len(tape),
        controls=["bidirectional contact index","positive ranks","unchanged paid mass and count"],
        old_paid=110519,productive=22461,results=results,topology_counts=counts,
        price_counts=Counter(v["status"] for v in variants),caps={"anchors":10,"events":76466,"seconds":20,"offsets":160}),
        indent=2,sort_keys=True))


if __name__=="__main__":
    main()
