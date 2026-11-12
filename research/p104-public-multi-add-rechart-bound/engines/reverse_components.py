"""Independent reverse full-route match and annihilator dimensions."""

from argparse import ArgumentParser
from collections import Counter
from gzip import decompress
from hashlib import sha256
from itertools import product
from json import dumps, loads
from pathlib import Path
from signal import alarm
from time import monotonic

PINS={
 "price":"e36932c2074e000da8f473f3b739d5e0c837f6d1887b3c46efb533f8dacce81a",
 "old":"2c523ce6fdd6092d758fedc3602a0bcedb692b9766f1e41f903351ba4dee1756",
 "current":"4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
}
WIDTH=9
CAP=13


class Deadline(Exception):
    pass


def check(deadline):
    if monotonic() >= deadline:
        raise Deadline


def unique(pairs):
    obj=dict(pairs)
    if len(obj)!=len(pairs):
        raise ValueError("duplicate JSON key")
    return obj


def authenticate(args):
    raw={}
    for k, pin in PINS.items():
        raw[k]=getattr(args,k).read_bytes()
        if sha256(raw[k]).hexdigest()!=pin:
            raise ValueError(f"changed dependency {k}")
    return {k:loads(v if k=="price" else decompress(v),object_pairs_hook=unique) for k,v in raw.items()}


def pivots(vectors):
    table={}
    for v in vectors:
        assert type(v) is int and 0 <= v < (1<<WIDTH)
        for p, row in sorted(table.items(),reverse=True):
            if (v>>p)&1:
                v ^= row
        if v:
            p=v.bit_length()-1
            for q, row in list(table.items()):
                if (row>>p)&1:
                    table[q]=row^v
            table[p]=v
    return table


def annihilator(vectors):
    table=pivots(vectors)
    return [(1<<free) | sum(1<<p for p,row in table.items() if (row>>free)&1)
            for free in range(WIDTH) if free not in table]


def ranks(frames, paths, delta):
    bs={b for _,b,_ in paths}
    assert len(bs)==1
    b=bs.pop()
    old=frames[b]
    old_dim=len(pivots(old))
    lower=[v for a,_,_ in paths for v in frames[a]]
    dual=[v for _,_,c in paths for v in annihilator(frames[c])]
    low=len(pivots(lower))
    high=WIDTH-len(pivots(dual))
    wanted=old_dim+delta
    assert len(pivots(lower+old))==old_dim and all(not (v&w).bit_count()%2 for v in old for w in dual)
    proof={"low_union_rank":low,"high_intersection_rank":high,"old_rank":old_dim,
           "wanted_rank":wanted,"low_union_basis":sorted(pivots(lower).values()),
           "high_intersection_annihilator_basis":sorted(pivots(dual).values()),
           "high_intersection_basis":sorted(annihilator(dual))}
    return ("low_union_too_large" if wanted<low else "high_intersection_too_small"
            if wanted>high else "geometry_survivor"),proof


def role_index(word, roles, deadline):
    tape=word["program"]
    chart={r:word["final"][r] for r in roles}
    rows={r:[] for r in roles}
    for clock in range(len(tape)-1,-1,-1):
        if clock%256==0:
            check(deadline)
        e=tape[clock]
        op,r=e[:2]
        if op=="MOVE" and r in rows:
            a,b,owned=e[2:]
            assert owned is False and chart[r]==b
            chart[r]=a
            rows[r].append(clock)
        elif op in ("ADD","COPY","SCALE"):
            for s in (e[1:3] if op in ("ADD","COPY") else e[1:2]):
                if s in rows:
                    assert chart[s]==e[-1]
                    rows[s].append(clock)
        elif op in ("INIT","CLEAR"):
            assert r not in rows
    assert all(chart[r]==word["initial"][r] for r in roles)
    return rows


def windows(tape, history, signature):
    # The clock histories and desired event signatures are both reverse chronological.
    n=len(signature)
    return [history[i:i+n] for i in range(len(history)-n+1)
            if tape[history[i]]==signature[0]
            and [tape[t] for t in history[i:i+n]]==signature]


def reconcile_component(row, old, current, old_index, current_index, deadline):
    p,q=old["program"],current["program"]
    choices=[]
    signed={}
    expected=set()
    for route in row["routes"]:
        r=route["role"]
        a,b,c=route["charts"]
        f,g=route["moves"]
        assert p[f]==["MOVE",r,a,b,False] and p[g]==["MOVE",r,b,c,False]
        chronological=[f,*route["contacts"],g]
        assert sorted(chronological)==chronological and len(set(chronological))==len(chronological)
        inherited=chronological[::-1]
        signature=[p[t] for t in inherited]
        assert inherited in windows(p,old_index[r],signature)
        matches=windows(q,current_index[r],signature)
        choices.append((inherited,matches))
        for t in route["contacts"]:
            event=p[t]
            assert event[0]=="ADD" and r in event[1:3] and event[-1]==b
            signed[t]=event
        expected.update(chronological)
    assert set(signed)==set(row["add_clocks"]) and not row["scale_clocks"]
    for clock,e in signed.items():
        incident={r["role"] for r in row["routes"] if clock in r["contacts"]}
        assert incident==set(e[1:3])
    if not all(found for _,found in choices):
        return "missing_inherited_signature",{"per_route_match_counts":[len(m) for _,m in choices]}

    mappings={}
    for joined in product(*(found for _,found in choices)):
        check(deadline)
        assignments=[(s,t) for (src,_),dst in zip(choices,joined,strict=True) for s,t in zip(src,dst,strict=True)]
        mapping=dict(assignments)
        if len(mapping)!=len(expected) or any(mapping[s]!=t for s,t in assignments):
            continue
        mapped=tuple(mapping[t] for t in sorted(expected))
        if all(a<b for a,b in zip(mapped,mapped[1:])):
            mappings[mapped]=mapping
    if len(mappings)!=1:
        return ("ambiguous_inherited_signature" if mappings else "missing_inherited_joint_chronology"),{
            "joint_match_count":len(mappings),"per_route_match_counts":[len(m) for _,m in choices]}
    mapping=next(iter(mappings.values()))
    frames=current["frames"]
    paths=[route["charts"] for route in row["routes"]]
    assert all(old["frames"][chart]==frames[chart] for path in paths for chart in path)
    status,geometry=ranks(frames,paths,row["key"][-1])
    delta=Counter()
    new_ranks={}
    for route,(a,b,c) in zip(row["routes"],paths,strict=True):
        a,b,c=map(lambda k:len(pivots(frames[k])),(a,b,c))
        p0,q0=b-a,c-b
        wanted=geometry["wanted_rank"]
        assert route["ranks"]==[p0,q0] and min(p0,q0,wanted-a,c-wanted)>0
        new_ranks[route["role"]]=[wanted-a,c-wanted]
        for r,signed_count in ((p0,-17),(q0,-17),(wanted-a,17),(c-wanted,17)):
            delta[r]+=signed_count
    assert {str(r):n for r,n in delta.items() if n}==row["paid_delta"]
    geometry["new_paid_ranks"]=new_ranks
    return status,{"signed_ancestor_ADDs":signed,"clock_map":mapping,"geometry":geometry}


def controls():
    assert annihilator([1,2])==[4,8,16,32,64,128,256]
    f=[[],[1],[1,2,4],[1,2,8]]
    good,r=ranks(f,[[0,1,2],[0,1,3]],1)
    assert good=="geometry_survivor" and r["high_intersection_rank"]==2
    low_frames=[[1,2],[1,2,4,8],[1,2,4,8,16],[1,2,4,8,32],[4,8]]
    blocked,r=ranks(low_frames,[[0,1,2],[4,1,3]],-1)
    assert blocked=="low_union_too_large" and r["low_union_rank"]==4
    seq=[["MOVE",1,0,1,False],["ADD",2,1,"1",1],["ADD",1,3,"-2",1],["MOVE",1,1,2,False]]
    assert windows(seq,[3,2,1,0],[seq[i] for i in (3,2,0)])==[]
    return ["annihilator_rank","expanded_common_high","obstructing_low_union","intervening_source_read"]


def main():
    assert __debug__
    p=ArgumentParser(description=__doc__)
    for name in PINS:
        p.add_argument("--"+name,type=Path)
    p.add_argument("--controls-only",action="store_true")
    args=p.parse_args()
    checks=controls()
    if args.controls_only:
        print(dumps(checks))
        return
    alarm(20)
    deadline=monotonic()+18
    d=authenticate(args)
    price,old,current=[d[k] for k in PINS]
    assert price["case_cap"]==CAP and price["runner_cap_seconds"]==20
    cases=price["positive"]
    assert len(cases)==CAP
    roles={r for item in cases for r in item["roles"]}
    for word in (old,current):
        mains=set(word["live"])|{r+112 for r in word["live"]}
        mains.update(word["hosted"]["X2"],word["hosted"]["Y2"])
        assert roles <= set(range(word["public"]))-mains and not roles&set(price["protected"])
    outcomes=[]
    try:
        left,right=[role_index(w,roles,deadline) for w in (old,current)]
        for row in cases:
            check(deadline)
            status,proof=reconcile_component(row,old,current,left,right,deadline)
            outcomes.append({"key":row["key"],"roles":row["roles"],"status":status,**proof})
    except Deadline:
        pass
    unvisited=[r["key"] for r in cases[len(outcomes):]]
    print(dumps({"head":price["head"],"pins":PINS,"case_cap":CAP,"seconds":20,"controls":checks,
                 "status":"CAPPED" if unvisited else "EXHAUSTED","outcomes":outcomes,"unvisited":unvisited,
                 "counts":dict(Counter(r["status"] for r in outcomes)),
                 "survivors":[r["key"] for r in outcomes if r["status"]=="geometry_survivor"],
                 "unresolved":[r["key"] for r in outcomes if r["status"]=="ambiguous_inherited_signature"]},
                sort_keys=True,indent=2))
    alarm(0)


if __name__=="__main__":
    main()
