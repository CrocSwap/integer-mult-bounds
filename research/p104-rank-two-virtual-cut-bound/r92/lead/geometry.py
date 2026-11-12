"""Freeze rank-two public MOVE subdivisions and virtual bank geometry."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import monotonic

HEAD="aaeec8c0acf01e99a5f331ef363a698d9c084ace"
PRICE="05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f"
WORD="4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"
PAYLOAD="9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
PROTECTED={319,863,1355,1568}
PRIME=65537


def unique(pairs):
    result=dict(pairs)
    if len(result)!=len(pairs):
        raise ValueError("Duplicate JSON key")
    return result


def checked(path,pin,compressed=False):
    raw=path.read_bytes()
    if sha256(raw).hexdigest()!=pin:
        raise ValueError(f"Changed input {path.name}")
    if compressed:
        raw=decompress(raw)
        assert sha256(raw).hexdigest()==PAYLOAD
    return loads(raw,object_pairs_hook=unique)


def space(basis):
    values={0}
    for v in basis:
        assert isinstance(v,int) and 0<v<512 and v not in values
        values.update(v^w for w in tuple(values))
    return frozenset(values)


def midspaces(low,high):
    assert low < high and len(high)==4*len(low)
    remain=set(high-low)
    result=[]
    while remain:
        rep=min(remain)
        coset={x^rep for x in low}
        assert coset <= remain
        remain.difference_update(coset)
        result.append((rep,low|coset))
    assert len(result)==3
    return result


@cache
def scalar(v):
    q=Fraction(v)
    assert q and q.denominator%PRIME
    return q


def bank_record(roles,mover,public,cohort):
    owned=sorted(r for r in roles if r>=public)
    others=sorted(r for r in roles if r<public)
    assert mover not in others and mover in cohort
    existing=sorted(set(others)&cohort)
    if owned or not existing:
        return None
    return {"existing_public":others,"existing_owned":owned,"eligible_before":existing,
            "virtual_public":sorted([*others,mover]),"virtual_eligible":sorted([*existing,mover])}


def bank_score(row):
    return (len(row["virtual_public"])-len(row["virtual_eligible"]),-len(row["virtual_eligible"]),row["key"])


def controls():
    low,high=space([1]),space([1,2,4])
    choices=midspaces(low,high)
    assert [r for r,_ in choices]==[2,4,6]
    assert all(len(v)==4 and low<v<high for _,v in choices)
    assert bank_record({2},1,5,{1,2})["virtual_public"]==[1,2]
    assert bank_record({2,6},1,5,{1,2}) is None
    assert bank_record({3},1,5,{1,2}) is None
    return ["rank_two_quotient_has_three_midspaces","mover_augments_cocharted_cohort",
            "owned_bank_rejected","no_other_cohort_role_rejected"]


def audit(word,price,deadline,out):
    n=word["public"]
    owned=word["owned_fields"]
    program=word["program"]
    assert (n,owned,len(program))==(1501,68,76466)
    frames=word["frames"]
    mains=set(word["live"])|{r+112 for r in word["live"]}
    mains.update(word["hosted"]["X2"],word["hosted"]["Y2"])
    cohort=set(price["endpoint_cohort"])
    assert len(cohort)==615 and cohort=={r for r,az in enumerate(zip(word["initial"],word["final"],strict=True))
                                       if az==(3,127) and r not in mains|PROTECTED}
    quotes={tuple(r["key"]):r for r in price["quotes"]}
    spans=[space(v) for v in frames]
    labels=defaultdict(list)
    for chart,subspace in enumerate(spans):
        if len(frames[chart]) in (4,5):
            labels[subspace].append(chart)
    charts=list(word["initial"])+[None]*owned
    banks=defaultdict(set)
    for r,c in enumerate(charts[:n]):
        banks[c].add(r)
    fresh=set()
    paid=Counter()
    paid_public=Counter()
    counts=Counter()
    eligible,raw_placements,other_labels=[],[],[]
    out.update(eligible=eligible,raw_placements=raw_placements,other_chart_labels=other_labels)
    for t,event in enumerate(program):
        out["first_unvisited_event"]=t
        if t%128==0 and monotonic()>=deadline:
            raise TimeoutError("bounded structural scan")
        op,d,*args=event
        assert 0<=d<len(charts)
        current=charts[d]
        if op=="MOVE":
            a,c,flag=args
            assert current==a and flag==(d>=n)
            assert spans[a]<spans[c] or flag and spans[c]<spans[a]
            rank=abs(len(frames[a])-len(frames[c]))
            paid[rank]+=1
            if not flag:
                paid_public[rank]+=1
            m=len(frames[a])+1
            if not flag and rank==2:
                counts["rank_two_public_moves"]+=1
            if not flag and rank==2 and d in cohort and m in (4,5):
                counts["cohort_rank_two_crossings"]+=1
                assert len(frames[c])==m+1
                quote=quotes[m,1,1]
                assert quote["endpoint_chart_ranks"]==[m-1,m+1] and Fraction(quote["full_probe"][0])>0
                for rep,mid in midspaces(spans[a],spans[c]):
                    picked=[]
                    label_rows=[]
                    for b in labels[mid]:
                        record=bank_record(banks[b],d,n,cohort)
                        if record is None:
                            label_rows.append({"chart":b,"eligible":False})
                            continue
                        label_rows.append({"chart":b,"eligible":True})
                        picked.append(record | dict(key=[t,b,d],mover=d,old_move=event,
                            outer_charts=[a,c],rank_tuple=[m,1,1],quotient_representative=rep,
                            chart_bases=[frames[a],frames[b],frames[c]],paid_delta=quote["paid_delta"],
                            target_delta=quote["target_delta"],complete_probe_margin=quote["full_probe"]))
                    picked.sort(key=bank_score)
                    status="eligible" if picked else "unoccupied_or_guarded" if label_rows else "no_existing_chart"
                    raw_placements.append(dict(move_clock=t,mover=d,rank=m,quotient_representative=rep,
                                               labels=label_rows,status=status))
                    counts[status]+=1
                    if picked:
                        eligible.append(picked[0])
                        other_labels.extend(row["key"] for row in picked[1:])
            charts[d]=c
            banks[a].remove(d)
            banks[c].add(d)
            fresh.discard(d)
        elif op=="INIT":
            assert d>=n and current is None
            c=args[0]
            charts[d]=c
            banks[c].add(d)
            fresh.add(d)
        elif op=="CLEAR":
            assert d>=n and current==args[0]
            banks[current].remove(d)
            charts[d]=None
            fresh.discard(d)
        else:
            assert op in ("ADD","COPY","SCALE") and current==args[-1]
            scalar(args[-2])
            if op!="SCALE":
                src=args[0]
                assert src!=d and charts[src]==current
            if op=="COPY":
                assert d>=n and d in fresh
            fresh.discard(d)
    assert charts==word["final"]+[None]*owned and not fresh
    assert dict(paid)=={1:4000,2:853,3:829,4:223,5:345,6:14,7:10,8:5}
    assert dict(paid_public)=={int(k):v for k,v in price["public_paid_stock"].items()}
    assert counts["rank_two_public_moves"]==844
    assert len(raw_placements)==3*counts["cohort_rank_two_crossings"]<=2532
    assert len(eligible)==len({tuple(r["key"]) for r in eligible})
    eligible.sort(key=bank_score)
    out.update(first_unvisited_event=None,events_replayed=len(program),native_paid_histogram=dict(paid),
               native_public_paid_histogram=dict(paid_public),counts=dict(counts),
               selected=eligible[:12],unvisited_support_keys=[r["key"] for r in eligible[12:]])


def main():
    parser=ArgumentParser(description=__doc__)
    parser.add_argument("--price",type=Path)
    parser.add_argument("--word",type=Path)
    parser.add_argument("--controls-only",action="store_true")
    a=parser.parse_args()
    assert __debug__
    if a.controls_only:
        print(dumps(controls()))
        return
    if not a.price or not a.word:
        parser.error("Both pinned inputs required")
    def stop(*_):
        raise TimeoutError("hard 20-second geometry cap")
    result={}
    timer=None
    signal(SIGALRM,stop)
    alarm(20)
    deadline=monotonic()+18
    try:
        price=checked(a.price,PRICE)
        assert price["head"]==HEAD and price["word_sha256"]==WORD
        audit(checked(a.word,WORD,True),price,deadline,result)
    except TimeoutError as error:
        timer=str(error)
    finally:
        alarm(0)
    print(dumps(dict(head=HEAD,price_sha256=PRICE,word_sha256=WORD,controls=controls(),runner_seconds_cap=20,
        event_cap=76466,raw_placement_cap=2532,support_case_cap=12,geometry_timeout=timer,**result),
        indent=2,sort_keys=True))
    if timer:
        raise SystemExit(2)


if __name__=="__main__":
    main()
