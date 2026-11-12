"""Match closed inherited public components and check their exact shared chart ranks."""
from argparse import ArgumentParser
from bisect import bisect_left
from collections import Counter
from fractions import Fraction
from functools import cache
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic

HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
ANCESTOR = "ed090b57ed88f8859e5ff4643645099e6ba856ea"
CAP,SECONDS = 13,20
PINS = {
    "inputs/PRICE.json": "e36932c2074e000da8f473f3b739d5e0c837f6d1887b3c46efb533f8dacce81a",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/7277-WORD.json.gz": "2c523ce6fdd6092d758fedc3602a0bcedb692b9766f1e41f903351ba4dee1756",
    "inputs/ancestor_contact.py": "ab89a72dc849b10e0837dd42f4be2d8717f75e32bb14630943dd8570bcfa3053",
}


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("duplicate JSON key")
    return result


def check_time(deadline):
    if monotonic() >= deadline:
        raise TimeoutError("cooperative exact support cap")


def inputs(root):
    raw = {}
    for rel, pin in PINS.items():
        raw[rel] = (root/rel).read_bytes()
        if sha256(raw[rel]).hexdigest() != pin:
            raise ValueError("changed dependency: " + rel)
    return raw


def paths(row):
    role = row["role"]
    low, middle, high = row["charts"]
    return ["MOVE",role,low,middle,False],["MOVE",role,middle,high,False]


def between(contacts, left, right):
    a,b = bisect_left(contacts,left),bisect_left(contacts,right)
    assert a<b and contacts[a]==left and contacts[b]==right
    return contacts[a+1:b]


def bind(old, new, old_index, new_index, case):
    old_tape,new_tape = old["program"],new["program"]
    mid = case["key"][0]
    ids = set(case["roles"])
    old_moves,new_moves,add_clock_map = {},{},{}
    payload = {}
    evidence = dict(ancestor_ADD_clocks=case["add_clocks"],ancestor_ADD_payload=payload,
                    current_ADD_clock_map=add_clock_map,ancestor_MOVE_clocks=old_moves,
                    current_MOVE_clocks=new_moves)
    for clock in case["add_clocks"]:
        event = old_tape[clock]
        d,s = event[1:3]
        assert event[0]=="ADD" and {d,s}<=ids and d!=s and event[-1]==mid
        assert Fraction(event[3])
        exact_old=[t for t in old_index[d] if old_tape[t]==event]
        exact_now=[t for t in new_index[d] if new_tape[t]==event]
        ordinal=exact_old.index(clock)
        payload[clock]=dict(literal=event,exact_ordinal=ordinal,old_matches=exact_old,new_matches=exact_now)
        if not exact_now:
            return "missing_inherited_signed_ADD",evidence
        if len(exact_now)!=len(exact_old):
            return "unresolved_signed_ADD_ordinal",evidence
        add_clock_map[clock]=exact_now[ordinal]
    assert len(add_clock_map)==len(set(add_clock_map.values()))
    for route in case["routes"]:
        r=route["role"]
        old_left,old_right=route["moves"]
        expected_left,expected_right=paths(route)
        old_moves[r]=route["moves"]
        assert old_tape[old_left]==expected_left and old_tape[old_right]==expected_right
        assert between(old_index[r],old_left,old_right)==route["contacts"]
        assert all(r in old_tape[t][1:3] for t in route["contacts"])
        new_contacts=[add_clock_map[t] for t in route["contacts"]]
        if new_contacts!=sorted(new_contacts):
            return "changed_inherited_ADD_order",evidence
        current=new_index[r]
        lo,hi = bisect_left(current,new_contacts[0]),bisect_left(current,new_contacts[-1])
        assert current[lo]==new_contacts[0] and current[hi]==new_contacts[-1]
        if lo==0 or hi+1==len(current):
            return "missing_inherited_MOVE_boundary",evidence
        left,right=current[lo-1],current[hi+1]
        new_moves[r]=[left,right]
        if new_tape[left]!=expected_left or new_tape[right]!=expected_right or between(current,left,right)!=new_contacts:
            evidence["first_failed_window"] = [[t,new_tape[t]] for t in current[lo-1:hi+2]]
            return "changed_inherited_contact_window",evidence
    clock_map = add_clock_map | {a:b for role,a_list in old_moves.items()
                                for a,b in zip(a_list,new_moves[role],strict=True)}
    assert len(clock_map)==len(case["add_clocks"])+len(case["paid_clocks"])
    assert len(set(clock_map.values()))==len(clock_map)
    if [clock_map[t] for t in sorted(clock_map)]!=sorted(clock_map.values()):
        return "changed_inherited_relative_clock_order",evidence
    charts={c for r in case["routes"] for c in r["charts"]}
    if any(old["frames"][c]!=new["frames"][c] for c in charts):
        return "unresolved_chart_payload",evidence
    return "matched",evidence


def geometry(case, frames, math, deadline):
    space,basis,rank = (math[name] for name in ("space","basis","dimensions"))

    @cache
    def chart(i):
        s=space(frames[i])
        assert rank(s)==len(frames[i])
        return s

    b=case["key"][0]
    old_rank=rank(chart(b))
    want=old_rank+case["key"][2]
    lows,highs,new_ranks=[],[],{}
    paid_shift=Counter()
    for r in case["routes"]:
        a,mid,c=r["charts"]
        assert mid==b and chart(a)<chart(b)<chart(c)
        old=[old_rank-rank(chart(a)),rank(chart(c))-old_rank]
        new=[want-rank(chart(a)),rank(chart(c))-want]
        assert old==r["ranks"] and min(new)>0
        new_ranks[r["role"]]=new
        paid_shift.update(new);paid_shift.subtract(old)
        lows.append(a);highs.append(c)
    shift={str(k):17*v for k,v in paid_shift.items() if v}
    assert shift==case["paid_delta"]
    lo=space([x for a in lows for x in frames[a]])
    hi=set.intersection(*(chart(c) for c in highs))
    assert lo<=chart(b)<=hi
    lo_rank,hi_rank=rank(lo),rank(hi)
    evidence=dict(old_rank=old_rank,wanted_rank=want,low_union_basis=basis(lo),low_union_rank=lo_rank,
        high_intersection_basis=basis(hi),high_intersection_rank=hi_rank,
        outer_frames={i:frames[i] for i in sorted(set(lows+highs+[b]))},new_paid_ranks=new_ranks,
        paid_delta=shift)
    if want<lo_rank:
        return "low_union_too_large",evidence
    if want>hi_rank:
        return "high_intersection_too_small",evidence
    for i,f in enumerate(frames):
        if i%32==0:
            check_time(deadline)
        if len(f)==want and all(x in hi for x in f) and lo<=chart(i):
            evidence["midpoint"]={"chart":i,"basis":f,"kind":"existing_chart"}
            break
    else:
        selected=basis(lo)
        current=lo.copy()
        for x in sorted(hi):
            if len(selected)==want:
                break
            if x not in current:
                selected.append(x)
                current|={x^y for y in current}
        assert lo<=current<=hi and rank(current)==want
        evidence["midpoint"]={"basis":selected,"kind":"new_descriptor_pending_compiler"}
    return "exact_geometry_survivor",evidence


def controls(math):
    frames=[[],[1],[1,2,4],[1,2,8],[1,2,16],[1,2]]
    tape=[["MOVE",i,0,1,False] for i in range(3)]+[["ADD",0,1,"-2",1],["ADD",1,2,"3/2",1]]+[
        ["MOVE",i,1,i+2,False] for i in range(3)]
    case=dict(key=[1,3,1],roles=[0,1,2],add_clocks=[3,4],paid_clocks=[0,1,2,5,6,7],
        routes=[dict(role=i,charts=[0,1,i+2],moves=[i,i+5],contacts=c,ranks=[1,2])
                for i,c in enumerate(([3],[3,4],[4]))],paid_delta={})
    word=dict(public=4,initial=[0,0,0,1],final=[2,3,4,1],program=tape,frames=frames)
    deadline=monotonic()+2
    ix=math["contacts"](word,set(case["roles"]),deadline)
    assert bind(word,word,ix,ix,case)[0]=="matched"
    geom,evidence=geometry(case,frames,math,deadline)
    assert geom=="exact_geometry_survivor" and evidence["midpoint"]["chart"]==5
    extra=word | {"program":tape[:4]+[["ADD",3,1,"1",1]]+tape[4:]}
    new_ix=math["contacts"](extra,set(case["roles"]),deadline)
    assert bind(word,extra,ix,new_ix,case)[0]=="changed_inherited_contact_window"
    frames2=[[1],[2],[4],[1,2,4],[1,2,4,8]]
    blocked=dict(key=[3,3,-1],routes=[dict(role=i,charts=[i,3,4],ranks=[2,1]) for i in range(3)],paid_delta={})
    assert geometry(blocked,frames2,math,deadline)[0]=="low_union_too_large"
    return ["three-route common high expansion","three-route blocked low union","extra source read opens component"]


def audit(root):
    deadline=monotonic()+SECONDS-2
    raw=inputs(root)
    math=run_path(str(root/"inputs/ancestor_contact.py"))
    diagnostic=controls(math)
    price=json.loads(raw["inputs/PRICE.json"],object_pairs_hook=unique)
    assert price["head"]==HEAD and price["predecessor_head"]==ANCESTOR
    assert price["word_sha256"]==PINS["inputs/7334-WORD.json.gz"]
    cases=price["positive"]
    assert price["case_cap"]==len(cases)==CAP and price["runner_cap_seconds"]==SECONDS
    assert len({tuple(r["key"]) for r in cases})==CAP and not any(r["scale_clocks"] for r in cases)
    tracked={role for r in cases for role in r["roles"]}
    assert not tracked & set(price["protected"])
    outcomes=[]
    stop=None
    stage="source admission"
    try:
        old,new=[json.loads(decompress(raw[f"inputs/{label}-WORD.json.gz"]),object_pairs_hook=unique)
                 for label in (7277,7334)]
        assert len(new["program"])==76466 and tracked <= math["helpers"](old)&math["helpers"](new)
        stage="literal contact scan"
        old_index,new_index=[math["contacts"](w,tracked,deadline) for w in (old,new)]
        stage="exact cases"
        for r in cases:
            check_time(deadline)
            status,evidence=bind(old,new,old_index,new_index,r)
            row=dict(key=r["key"],roles=r["roles"],contact=evidence)
            if status=="matched":
                status,proof=geometry(r,new["frames"],math,deadline)
                row["geometry"]=proof
            row["status"]=status
            outcomes.append(row)
    except (TimeoutError,math["DeadlineReached"]) as exc:
        stop=dict(stage=stage,reason=type(exc).__name__)
    unvisited=[r["key"] for r in cases[len(outcomes):]]
    return dict(head=HEAD,ancestor_head=ANCESTOR,pins=PINS,controls=diagnostic,case_cap=CAP,
        runner_cap_seconds=SECONDS,status="CAPPED" if unvisited else "EXHAUSTED",stop=stop,
        counts=dict(Counter(r["status"] for r in outcomes)),outcomes=outcomes,unvisited=unvisited,
        unresolved=[r["key"] for r in outcomes if r["status"].startswith("unresolved")],
        survivors=[r["key"] for r in outcomes if r["status"]=="exact_geometry_survivor"])


def main():
    p=ArgumentParser(description=__doc__)
    p.add_argument("root",type=Path)
    p.add_argument("--controls-only",action="store_true")
    args=p.parse_args()
    assert __debug__
    if args.controls_only:
        result=controls(run_path(str(args.root/"inputs/ancestor_contact.py")))
    else:
        def stop(*_):
            raise TimeoutError("hard exact support cap")
        signal(SIGALRM,stop)
        alarm(SECONDS)
        try:
            result=audit(args.root)
        finally:
            alarm(0)
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
