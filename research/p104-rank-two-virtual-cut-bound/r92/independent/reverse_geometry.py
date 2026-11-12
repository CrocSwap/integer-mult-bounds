"""Independent reverse occupied-bank census for a rank-two paid subdivision."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import monotonic

HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
PINS = {
    "inputs/PRICE.json": "05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/PLAN.md": "85f09bdfb2168117560d841d45ee53fb8191c26ac7e33e645576b55ec122e6ff",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
}
PROTECTED={319,863,1355,1568}
EVENTS,SECONDS,FIRST=76466,20,12


def unique(pairs):
    result=dict(pairs)
    if len(result)!=len(pairs):
        raise ValueError("duplicate JSON key")
    return result


def authenticate(root):
    result={}
    for name,pin in PINS.items():
        raw=(root/name).read_bytes()
        if sha256(raw).hexdigest()!=pin:
            raise ValueError("changed dependency: "+name)
        result[name]=raw
    return result


def span(frame):
    vectors={0}
    for v in frame:
        assert type(v) is int and 0<v<512 and v not in vectors
        vectors.update(v^x for x in tuple(vectors))
    return frozenset(vectors)


def between_spaces(low,high):
    """All intermediate lines in the two-dimensional quotient high/low."""
    assert low<high and len(high)==4*len(low)
    todo=high-low
    entries=[]
    while todo:
        v=min(todo)
        coset=frozenset(x^v for x in low)
        assert coset<=todo
        todo-=coset
        entries.append((v,low|coset))
    assert len(entries)==3
    return entries


def filter_labels(labels,banks,n,mover,cohort):
    good,blocked=[],[]
    for c in labels:
        bank=banks.get(c,set())
        public=sorted(r for r in bank if r<n)
        owned=sorted(bank-set(public))
        other=sorted(bank&cohort)
        assert mover not in bank and set(other)<=set(public)
        row=dict(chart=c,public=public,owned=owned,other_pivots=other)
        if not owned and other:
            good.append(row|dict(virtual_public=sorted(public+[mover]),pivots=sorted(other+[mover]),
                                 outside=len(set(public)-cohort)))
        else:
            blocked.append(row|dict(reason="owned occupied" if owned else "no other cohort role"))
    good.sort(key=lambda r:(r["outside"],-len(r["pivots"]),r["chart"]))
    return good,blocked


def controls():
    a,c=span([1]),span([1,2,4])
    quotient=between_spaces(a,c)
    assert [r for r,_ in quotient]==[2,4,6]
    assert quotient[0][1]==span([1,2]) and quotient[2][1]==span([1,6])
    good,bad=filter_labels([9,10,11,12,13],{9:{3,8},10:{3,4,8},11:{2},12:{3,30},13:{3,4}},20,1,{1,3,4})
    assert [x["chart"] for x in good]==[13,10,9]
    assert good[0]["public"]==[3,4] and good[0]["virtual_public"]==[1,3,4]
    assert [x["reason"] for x in bad]==["no other cohort role","owned occupied"]
    return ["three quotient lines", "augment by a distinct virtual mover", "owned and missing-pivot guards", "deterministic label ranking"]


def census(word,price,deadline):
    n=word["public"]
    owners=word["owned_fields"]
    tape=word["program"]
    frames=word["frames"]
    assert len(tape)==EVENTS
    spaces=[span(frame) for frame in frames]
    labels=defaultdict(list)
    for i,s in enumerate(spaces):
        labels[s].append(i)
    mains=set(word["live"])|{r+112 for r in word["live"]}|set(word["hosted"]["X2"])|set(word["hosted"]["Y2"])
    cohort={r for r,(a,c) in enumerate(zip(word["initial"],word["final"],strict=True))
            if (a,c)==(3,127) and r not in mains|PROTECTED}
    assert len(cohort)==615 and sorted(cohort)==price["endpoint_cohort"]
    states=list(word["final"])+[None]*owners
    banks=defaultdict(set)
    for r,c in enumerate(states[:n]):
        banks[c].add(r)
    attempts,eligible=[],[]
    paid=Counter()
    progress=0
    stop=None

    def shift(r,after,before):
        assert states[r]==after
        if after is not None:
            banks[after].remove(r)
        if before is not None:
            banks[before].add(r)
        states[r]=before

    try:
        for t in range(len(tape)-1,-1,-1):
            if t%128==0 and monotonic()>=deadline:
                raise TimeoutError("cooperative reverse deadline")
            op,r,*args=tape[t]
            if op=="MOVE":
                a,c,owned=args
                assert states[r]==c and owned==(r>=n)
                la,lc=len(frames[a]),len(frames[c])
                if not owned:
                    assert spaces[a]<spaces[c]
                    paid[lc-la]+=1
                if not owned and r in cohort and lc-la==2 and la+1 in (4,5):
                    for direction,midspace in between_spaces(spaces[a],spaces[c]):
                        good,blocked=filter_labels(labels.get(midspace,()),banks,n,r,cohort)
                        record=dict(cut=t,mover=r,low_chart=a,high_chart=c,midpoint_rank=la+1,
                                    quotient_direction=direction,existing_labels=labels.get(midspace,[]),
                                    blocked_labels=blocked,other_eligible_labels=good[1:])
                        if good:
                            chosen=good[0]
                            assert spaces[a]<spaces[chosen["chart"]]<spaces[c]
                            assert states[r]==c and chosen["chart"] not in (a,c)
                            hit=record|chosen|dict(key=[t,chosen["chart"],r],
                                                  midpoint_basis=frames[chosen["chart"]])
                            eligible.append(hit)
                            record=record|dict(selected_label=chosen["chart"])
                        else:
                            record=record|dict(selected_label=None)
                        attempts.append(record)
                shift(r,c,a)
            elif op=="INIT":
                chart,=args
                assert r>=n
                shift(r,chart,None)
            elif op=="CLEAR":
                chart,=args
                assert r>=n
                shift(r,None,chart)
            elif op=="SCALE":
                assert states[r]==args[1]
            else:
                assert op in ("ADD","COPY") and states[r]==states[args[0]]==args[2]
                assert op!="COPY" or r>=n
            progress+=1
    except TimeoutError as exc:
        stop=str(exc)

    if progress==EVENTS:
        assert states==list(word["initial"])+[None]*owners
        assert {str(k):v for k,v in paid.items()}==price["public_paid_stock"]
        assert len(attempts)<=3*paid[2]
    attempts.sort(key=lambda r:(r["cut"],r["quotient_direction"]))
    eligible.sort(key=lambda r:(r["outside"],-len(r["pivots"]),r["cut"],r["chart"]))
    assert len(eligible)==len({tuple(r["key"]) for r in eligible})
    return dict(status="EXHAUSTED" if progress==EVENTS else "CAPPED",stop=stop,
        first_unvisited_event=None if progress==EVENTS else EVENTS-progress-1,events_replayed=progress,
        all_public_paid_rank_histogram=paid,cohort_size=len(cohort),
        qualifying_move_count=len({r["cut"] for r in attempts}),subspace_attempts=len(attempts),
        attempted=attempts,eligible=eligible,selected=[r["key"] for r in eligible[:FIRST]],
        unselected=[r["key"] for r in eligible[FIRST:]],
        distinct_eligible_MOVEs=sorted({r["cut"] for r in eligible}),
        distinct_eligible_movers=sorted({r["mover"] for r in eligible}),
        duplicate_eligible_chart_labels=sum(len(r["other_eligible_labels"]) for r in eligible))


def main():
    p=ArgumentParser(description=__doc__)
    p.add_argument("root",type=Path)
    p.add_argument("--controls-only",action="store_true")
    args=p.parse_args()
    assert __debug__
    checks=controls()
    if args.controls_only:
        result=checks
    else:
        start=monotonic()
        def hard_stop(*_):
            raise TimeoutError("hard reverse deadline")
        signal(SIGALRM,hard_stop)
        alarm(SECONDS)
        try:
            raw=authenticate(args.root)
            price=json.loads(raw["inputs/PRICE.json"],object_pairs_hook=unique)
            assert price["head"]==HEAD and price["word_sha256"]==PINS["inputs/7334-WORD.json.gz"]
            assert price["public_paid_stock"]["2"]==844
            word=json.loads(decompress(raw["inputs/7334-WORD.json.gz"]),object_pairs_hook=unique)
            result=census(word,price,start+SECONDS-2)|dict(head=HEAD,pins=PINS,
                controls=checks,event_cap=EVENTS,runner_seconds_cap=SECONDS,first_support_cap=FIRST)
        finally:
            alarm(0)
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
