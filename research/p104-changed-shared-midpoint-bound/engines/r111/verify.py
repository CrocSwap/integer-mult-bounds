"""Reverse closure, exact actual price, and GF(2) interval for the frozen chart-746 component."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM,alarm,signal
from time import monotonic
import sys

ROOT=Path(__file__).resolve().parent
HEAD="aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER="07a76c5e2738882c0cb322278e56f6cae3c9885d"
WORD="4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"
PAYLOAD="9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
PINS={
    "inputs/PRICE.json":"96802c4ee39368c0e0b7d5b245372a979f68047ecbb0ae3517ced7e38dbf9a9a",
    "inputs/R108-ROUTES.json":"7787cbedb364a51ae1c3712086bbc3f70da35ba018037429ad7794d52c8edb93",
    "inputs/R100-PRICE.json":"7109125bbf60e3015c8c0ac7b10b24b7de61f358c1508d06604ebccd89ef6343",
    "inputs/R92-PRICE.json":"05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/pricing.py":"f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    "inputs/reverse_routes.py":"a81a41c1cd33de0a612b568cbf470003d933a344396bc6dc53b85a91888dfe27",
    "inputs/7334-WORD.json.gz":WORD,
}
EVENTS,SECONDS,OFFSETS=76466,20,3


def unique(items):
    d=dict(items)
    if len(d)!=len(items):
        raise ValueError("duplicate JSON key")
    return d


def pinned(path,digest):
    raw=path.read_bytes()
    if sha256(raw).hexdigest()!=digest:
        raise ValueError(f"changed dependency: {path.name}")
    return raw


def closure(word,price,prior,old_price,engine,cost,deadline,state):
    fields=price["fields"]
    adds=price["add_events"]
    expected={r:[(f,["MOVE",r,a,b,False]),*((t,e) for t,e in adds if r in e[1:3]),(g,["MOVE",r,b,c,False])]
              for r,a,b,c,f,g in fields}
    assert set(expected)=={1250,452,532} and all(Q(e[-2]) for _,e in adds)
    state.update(events_replayed=0,first_unvisited_event=EVENTS-1)
    contacts=engine["walk"](word,set(expected),deadline,state)
    ranks,rows,blockers=[],[],[]
    for role,a,b,c,f,g in fields:
        assert role<word["public"] and b==746 and f<g
        found=[r for r in contacts[role] if f<=r[0]<=g]
        if found!=expected[role]:
            blockers.append(role)
        rows.append(dict(role=role,outer_charts=[a,c],contacts=found))
        p,q=len(word["frames"][b])-len(word["frames"][a]),len(word["frames"][c])-len(word["frames"][b])
        assert p>0 and q>0
        ranks.append((p,q))
    assert len({t for _,_,_,_,f,g in fields for t in (f,g)})==6
    if blockers:
        return dict(contacts=rows,blocked_roles=blockers,actual_offsets=[],positive_offsets=[])
    assert ranks[0]==ranks[2]==(3,2) and len(word["frames"][746])==6
    p,q=ranks[1]
    targets=Counter({int(r):n for r,n in prior["old_targets"].items()})
    paid=Counter({int(r):n for r,n in prior["old_paid"].items()})
    assert sum(paid.values())==price["old_paid"]==price["new_paid"]==110519
    assert sum(targets.values())==price["productive"]==22461
    old=targets.copy()
    old.subtract(paid)
    assert sum(r*n for r,n in old.items())==1424
    at,probe,target=(Q(old_price[k]) for k in ("old_crossing_upper","probe","fixed_target"))
    expected_prices={v["offset"]:v for v in price["positive_relaxed_variants"] if v["old_peer_ranks"]==[p,q]}
    actual,positive=[],[]
    for delta in range(1-min(p,3),min(q,2)):
        if not delta:
            continue
        if monotonic()>=deadline:
            raise TimeoutError("actual offset price cap")
        change=Counter()
        for l,h in ranks:
            change.update((l+delta,h-delta))
            change.subtract((l,h))
        d_paid={r:17*n for r,n in change.items() if n}
        assert sum(d_paid.values())==sum(r*n for r,n in d_paid.items())==0
        credit={r:-n for r,n in d_paid.items()}
        invoice=old.copy()
        invoice.update(credit)
        whole=cost(invoice,probe)
        row=dict(offset=delta,rank=6+delta,paid_delta=d_paid,full_probe=list(map(str,whole)))
        actual.append(row)
        if whole[0]>0:
            positive.append(row)
            original=expected_prices[delta]
            assert {str(k):v for k,v in d_paid.items()}==original["paid_delta"] and row["full_probe"]==original["full_probe"]
            assert list(map(str,cost(credit,at)))==original["net"]
            assert list(map(str,cost(credit,target)))==original["target_net"]
        else:
            assert whole[1]<=0 and delta not in expected_prices
    assert len(actual)<=OFFSETS and {r["offset"] for r in positive}==set(expected_prices)
    return dict(contacts=rows,blocked_roles=[],old_ranks=ranks,actual_offsets=actual,positive_offsets=positive)


def vector_span(basis):
    result={0}
    for v in basis:
        assert isinstance(v,int) and 0<v<512 and v not in result
        result|={x^v for x in result}
    return result


def dimension(values):
    rank=len(values).bit_length()-1
    assert len(values)==1<<rank
    return rank


def interval(frames,fields):
    lows=[vector_span(frames[a]) for _,a,_,_,_,_ in fields]
    mids=[vector_span(frames[b]) for _,_,b,_,_,_ in fields]
    highs=[vector_span(frames[c]) for _,_,_,c,_,_ in fields]
    assert all(a<b<c for a,b,c in zip(lows,mids,highs,strict=True))
    assert all(b==mids[0] for b in mids)
    lower={0}
    for low in lows:
        lower={x^y for x in lower for y in low}
    upper=set.intersection(*highs)
    assert lower<=mids[0]<=upper
    return lows,highs,lower,upper


def gaussian_rank(vectors):
    pivots={}
    for v in vectors:
        while v:
            bit=v.bit_length()-1
            if bit not in pivots:
                pivots[bit]=v
                break
            v^=pivots[bit]
    return len(pivots)


def geometry(word,price,literal,deadline,state):
    assert literal["head"]==HEAD and literal["mode"]=="literal-price" and literal["complete"]
    assert literal["pins"]==PINS and not literal["blocked_roles"]
    fields=price["fields"]
    frames=word["frames"]
    lows,highs,lower,upper=interval(frames,fields)
    l,h=dimension(lower),dimension(upper)
    assert lows[0]==lows[2] and highs[0]==highs[2]
    assert l==gaussian_rank(frames[744]+frames[263])
    assert h==len(frames[207])+len(frames[916])-gaussian_rank(frames[207]+frames[916])
    low_obstruction=min(lows[0]-lows[1])
    high_obstruction=min(highs[1]-highs[0])
    assert dimension(lows[0])==dimension(lows[1])==3
    assert dimension(highs[1])==7 and low_obstruction and high_obstruction
    positives=literal["positive_offsets"]
    assert len(positives)<=OFFSETS
    rows=[]
    for v in positives:
        if monotonic()>=deadline:
            raise TimeoutError("exact GF(2) cap")
        rank=v["rank"]
        assert max(map(dimension,lows))<rank<min(map(dimension,highs))
        feasible=l<=rank<=h
        labels=[]
        if feasible:
            for c,basis in enumerate(frames):
                if len(basis)==rank:
                    s=vector_span(basis)
                    if lower<=s<=upper:
                        labels.append(c)
        rows.append(dict(offset=v["offset"],rank=rank,abstract_feasible=feasible,existing_chart_labels=labels))
        state["offsets_replayed"]=len(rows)
    return dict(low_union_rank=l,high_intersection_rank=h,low_union_vectors=sorted(lower),
                high_intersection_vectors=sorted(upper),results=rows,
                distinct_coframe_chronology=dict(
                    entrance_between_adds=dict(required_strict_inclusion=[744,263],outside_vector=low_obstruction),
                    exit_between_adds=dict(required_strict_inclusion=[916,207],outside_vector=high_obstruction)))


def controls():
    frames=[[1],[2],[1,2,4],[1,2,4,8],[1,2,4,16]]
    f=[(1,0,2,3,0,3),(2,1,2,4,0,3),(3,0,2,3,1,4)]
    _,_,lo,hi=interval(frames,f)
    assert (dimension(lo),dimension(hi))==(2,3)
    assert 2 in range(dimension(lo),dimension(hi)+1) and 4 not in range(dimension(lo),dimension(hi)+1)
    return ["exact three-role GF(2) union/intersection","strict geometry has positive and negative control"]


def main():
    p=ArgumentParser(description=__doc__)
    p.add_argument("mode",choices=("controls","literal-price","geometry"))
    p.add_argument("--root",type=Path,default=ROOT)
    p.add_argument("--literal",type=Path)
    p.add_argument("--literal-sha256")
    a=p.parse_args()
    assert __debug__ and sys.version_info[:2]==(3,12)
    checks=controls()
    if a.mode=="controls":
        print(dumps(checks))
        return
    if a.mode=="geometry" and (a.literal is None or a.literal_sha256 is None):
        p.error("freeze the independently priced literal receipt before geometry")
    def stop(*_):
        raise TimeoutError("hard 20-second cap")
    signal(SIGALRM,stop)
    alarm(SECONDS)
    deadline=monotonic()+18
    state,result={},{}
    reason=None
    try:
        raw={path:pinned(a.root/path,digest) for path,digest in PINS.items()}
        if a.mode=="geometry":
            literal=loads(pinned(a.literal,a.literal_sha256),object_pairs_hook=unique)
        price=loads(raw["inputs/PRICE.json"],object_pairs_hook=unique)
        assert price["head"]==HEAD and price["caller"]==CALLER and price["word_sha256"]==WORD
        assert price["limits"]["actual_offsets"]==OFFSETS and price["limits"]["events"]==EVENTS
        assert price["limits"]["seconds"]==SECONDS and price["limits"]["components"]==1
        assert all(PINS[k]==v for k,v in price["pins"].items())
        word_raw=decompress(raw["inputs/7334-WORD.json.gz"])
        assert sha256(word_raw).hexdigest()==price["payload_sha256"]==PAYLOAD
        word=loads(word_raw,object_pairs_hook=unique)
        if a.mode=="literal-price":
            engine=run_path(str(a.root/"inputs/reverse_routes.py"))
            cost=run_path(str(a.root/"inputs/pricing.py"))["cost"]
            prior,old_price=(loads(raw[f"inputs/{name}.json"],object_pairs_hook=unique) for name in ("R92-PRICE","R100-PRICE"))
            result=closure(word,price,prior,old_price,engine,cost,deadline,state)
        else:
            result=geometry(word,price,literal,deadline,state)
    except TimeoutError as exc:
        reason=str(exc)
    finally:
        alarm(0)
    print(dumps(dict(head=HEAD,pins=PINS,mode=a.mode,controls=checks,complete=reason is None,
        cap_events=EVENTS,cap_offsets=OFFSETS,cap_seconds=SECONDS,literal_sha256=a.literal_sha256,
        timeout=reason,progress=state,**result),indent=2,sort_keys=True))
    if reason:
        raise SystemExit(2)


if __name__=="__main__":
    main()
