"""Disjoint-mask Type B idle pairing with an arbitrary insertion slot."""

from argparse import ArgumentParser
from bisect import bisect_left, bisect_right
from collections import Counter
from fractions import Fraction as Q
from functools import cache
from hashlib import sha256
from itertools import combinations
import json
from math import isqrt
from pathlib import Path
import runpy
from time import monotonic

R52 = "cdf54b266ac31fd0efe544badbb9840598d4c63c4d3cd363f60ae9a74cc4b256"
R52_PRICE = "95b4d2ca88d7716fcd86cbe07811703b9fadbad24dad15a3753b4bab49036e59"
R52_BODY = "487d2788192b1e9845a6b047c105050987dba7ba6f72aef413ce6261b1b9a3e5"
CAP = {"body1":22,"nonunit":22,"structural":42}


def checked(path,pin):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != pin:
        raise ValueError(f"Changed input {path.name}")
    return raw


def distinct_mask_pairs(jobs):
    return [(a,b) for a,b in combinations(jobs,2) if jobs[a][1].isdisjoint(jobs[b][1])]


def compatible_upper(pairs,weights):
    per_event = {}
    for a,b in pairs:
        w = weights[a,b]
        assert w >= 0
        per_event[a] = max(w,per_event.get(a,0))
        per_event[b] = max(w,per_event.get(b,0))
    return sum(per_event.values(),Q(0))/2,per_event


def price(roots, old, known):
    files = old["authenticate"](roots)
    unpack = old["unpack"]
    input_path = "round30/complex/source/inputs/"
    word,caller,early = (unpack(files[input_path+x]) for x in ("WORD.json.gz","CALLER.json","EARLY-RESULT.json"))
    predecessor = runpy.run_path(str(roots["7298"]/"verify.py"))
    replay = predecessor["complex_scan"](word,caller,early)
    assert json.loads(json.dumps(replay)) == unpack(files["7298/RESULT.json"])["complex"]
    binding = next(raw for key,raw in files.items() if key.startswith("7113/"))
    assert b"rank = 8*len(selected)" in binding
    block = caller["types"]["B"]
    ports = len(block["ports"])
    assert (block["roles"],block["offset"],ports,caller["stages"],replay["copies"]) == (36,36,8,17,17)
    jobs = {}
    for i,e in enumerate(caller["events"]):
        if e[:2] == ["B","IDLE_ONE"]:
            mask = frozenset(e[3])
            assert mask and len(mask) == len(e[3]) and all(1 <= x <= 17 for x in mask)
            assert 36 <= e[2] < 72
            jobs[i] = (e[2]-36,mask)
    assert len(jobs) == 60
    cases = distinct_mask_pairs(jobs)
    assert len(cases) <= 1770
    singleton_pairs = [p for p in cases if all(len(jobs[i][1]) == 1 for i in p)]
    assert len(singleton_pairs) == 544 and list(map(list,singleton_pairs)) == known["pair_keys"]
    kappa = Q(replay["probe"])
    paid = Counter({int(k):v for k,v in early["invoice"]["P"].items()})
    targets = Counter({int(k):v for k,v in early["invoice"]["T"].items()})
    assert sum(paid.values()) == 110536 and sum(targets.values()) == 22461
    net = targets.copy()
    net.subtract(paid)
    assert sum(r*v for r,v in net.items()) == 1424
    cost = predecessor["PRICING"]["cost"]
    power = predecessor["PRICING"]["power_bounds"]
    old_margin = cost(net,kappa)
    assert old_margin[1] < 0

    @cache
    def quote(r,s):
        delta = Counter()
        delta[r] += ports
        delta[s] += ports
        delta[r+s] -= ports
        next_net = net.copy()
        next_net.update(delta)
        credit = cost(delta,kappa)
        margin = cost(next_net,kappa)
        assert credit[0] > 0 and margin[0] > 0
        a,b,c = power(r,kappa),power(s,kappa),power(r+s,kappa)
        volume = ((a[0]+b[0])/c[1],(a[1]+b[1])/c[0])
        return {"old_ranks":[r,s],"new_rank":r+s,"paid_old_minus_new":dict(delta),
                "credit":list(map(str,credit)), "complete_margin":list(map(str,margin)),
                "break_even_volume_factor_before_other_charges":list(map(str,volume))}

    prices,weights,key_signatures = {},{},{}
    for a,b in cases:
        r,s = sorted(8*len(jobs[i][1]) for i in (a,b))
        signature = f"{r}+{s}"
        prices[signature] = quote(r,s)
        key_signatures[a,b] = signature
        weights[a,b] = Q(prices[signature]["credit"][1])
    upper,event_bounds = compatible_upper(cases,weights)
    pre = {
        "head":old["HEAD"], "caller_head":old["CALLER_HEAD"],
        "inputs":{**old["PINS"],"r52/lead/screen.py":R52,"r52/run/PRICE.json":R52_PRICE,
                  "r52/run/BODY1.json":R52_BODY},
        "crossing_upper":str(kappa),"native_copies":17,"type_b_ports":ports,
        "old_complete_paid":paid,"old_complete_targets":targets,"old_complete_margin":list(map(str,old_margin)),
        "job_masks":[[i,r,sorted(mask)] for i,(r,mask) in jobs.items()],
        "mask_size_counts":dict(Counter(len(m) for r,m in jobs.values())),
        "price_by_rank_signature":prices,
        "pair_keys":[[a,b,key_signatures[a,b]] for a,b in cases],
        "singleton_control_pairs":len(singleton_pairs),"scope_pairs":len(cases),"pair_cap":1770,
        "per_event_upper":{i:str(x) for i,x in event_bounds.items()},
        "whole_compatible_optimistic_upper":str(upper),
        "whole_upper_rule":"half sum of per-event maximum incident upper credit",
        "one_new_grouped_idle_clock_and_role":"arbitrary",
        "equal_original_volume_and_free_extra_work_granted":True,
        "followup":{"nonunit_body_vectors":old["BODIES"],"pin_union_coordinates_to_one":True,
                    "nonunit_hard_seconds":25,
                    "structural_max_cases":3,"structural_hard_seconds":45},
    }
    return pre,caller,jobs,cases,weights


def controls(old):
    jobs = {10:(0,frozenset({1,2})),20:(1,frozenset({2,3})),30:(0,frozenset({4}))}
    assert distinct_mask_pairs(jobs) == [(10,30),(20,30)]
    assert compatible_upper([(10,30),(20,30)],{(10,30):Q(1),(20,30):Q(2)})[0] == Q(5,2)
    vector,_ = old["transport"]([],0,False,old["MOD"],2)
    assert old["outside"](vector,1) == [0,1]
    swap = [(0,"SWAP",0,1,0)]
    vector,_ = old["transport"](swap,0,False,old["MOD"],2)
    dual,_ = old["transport"](swap,1,True,old["MOD"],2)
    assert old["outside"](vector,1) is None and old["outside"](dual,0) is None
    return [*old["controls"](),"multistage_intersection_rejected","per_event_weight_bound",
            "different_projectors_fail_common_derivative","transported_projectors_pass"]


def nonunit_stage(old,caller,jobs,cases,bodies,deadline):
    # Different pairs require different identity loci for their removed idles.
    # Reuse transports only when that mask union is identical.
    compiled = {}
    rows = []
    for a,b in cases:
        if monotonic() >= deadline:
            break
        source,first_mask = jobs[a]
        target,second_mask = jobs[b]
        union = first_mask | second_mask
        if union not in compiled:
            values = [tuple(1 if j in union else v for j,v in enumerate(body,1)) for body in bodies]
            compiled[union] = [(n,q,*old["compile_gates"](caller,q,body))
                               for n,body in enumerate(values) for q in (1,old["MOD"]-1)]
        if monotonic() >= deadline:
            break
        witness = None
        for i,q,clocks,gates in compiled[union]:
            interval = gates[bisect_right(clocks,a):bisect_left(clocks,b)]
            write,_ = old["transport"](interval,source,False,old["MOD"])
            read,_ = old["transport"](interval,target,True,old["MOD"])
            outside_write = old["outside"](write,target)
            outside_read = old["outside"](read,source)
            if outside_write or outside_read:
                witness = {"vector_index":i,"q":1 if q == 1 else -1,
                           "outside_write":outside_write,"outside_read":outside_read}
                break
        rows.append({"key":[a,b],"unit_body_mask":sorted(union),"witness":witness})
    return rows


def main(args,start):
    checked(args.r52,R52)
    old = runpy.run_path(str(args.r52))
    known = json.loads(checked(args.r52_run/"PRICE.json",R52_PRICE))
    known_body = json.loads(checked(args.r52_run/"BODY1.json",R52_BODY))
    assert known_body["exclusions"] == known_body["visited"] == 544 and not known_body["unvisited"]
    known_by_key = {tuple(r["key"]):r["witness"] for r in known_body["records"]}
    roots = {"round30":args.round30,"7298":args.predecessor,"7113":args.caller_root}
    pre,caller,jobs,cases,weights = price(roots,old,known)
    out = args.out
    if args.stage in ("price","body1"):
        pin = old["save"](out,"PRICE.json",pre)
    else:
        frozen = (out/"PRICE.json").read_bytes()
        assert json.loads(frozen) == json.loads(json.dumps(pre))
        pin = sha256(frozen).hexdigest()
    if args.stage == "price":
        return
    assert all(old["MOD"]%d for d in range(2,isqrt(old["MOD"])+1))
    checks = controls(old)
    by_clock = {i:r for i,(r,mask) in jobs.items()}
    remaining = []
    if args.stage != "body1":
        earlier = old["previous"](out,"BODY1.json" if args.stage == "nonunit" else "NONUNIT.json",pin)
        cases = list(map(tuple,earlier["survivors"]))
        remaining = list(map(tuple,earlier["unvisited"]))
    deadline = start+CAP[args.stage]
    if args.stage in ("body1","nonunit"):
        bodies = ((1,)*17,) if args.stage == "body1" else old["BODIES"]
        if args.stage == "body1":
            rows = old["modular_stage"](caller,by_clock,cases,bodies,deadline)
        else:
            rows = nonunit_stage(old,caller,jobs,cases,bodies,deadline)
        survivors = [tuple(r["key"]) for r in rows if r["witness"] is None]
        unvisited = remaining+cases[len(rows):]
        upper,_ = compatible_upper([*survivors,*unvisited],weights)
        singleton_matched = 0
        if args.stage == "body1":
            for row in rows:
                key = tuple(row["key"])
                if key in known_by_key:
                    assert row["witness"] == known_by_key[key]
                    singleton_matched += 1
            if len(rows) == len(cases):
                assert singleton_matched == 544
        old["save"](out,"BODY1.json" if args.stage == "body1" else "NONUNIT.json",{
            "price_sha256":pin,"stage":args.stage,"scope":len(cases),"visited":len(rows),
            "exclusions":len(rows)-len(survivors),"survivors":survivors,"unvisited":unvisited,
            "unresolved_optimistic_upper":str(upper),"singleton_controls_matched":singleton_matched,
            "prime":old["MOD"],"body_vectors":bodies,"records":rows,"controls":checks,
        })
        return
    rows = []
    for a,b in cases[:3]:
        if monotonic() >= deadline:
            break
        status,mixed,clock = old["structural"](caller,a,b,by_clock[a],by_clock[b])
        rows.append({"key":[a,b],"status":status,"nondiagonal_transient":mixed,"stop_clock":clock})
    unvisited = remaining+cases[len(rows):]
    unresolved = [r["key"] for r in rows if r["status"] != "formal_projector_transport"]
    old["save"](out,"STRUCTURAL.json",{
        "price_sha256":pin,"scope":len(cases),"visited":len(rows),"unvisited":unvisited,
        "unresolved":unresolved,"records":rows,
        "support_survivors":[r["key"] for r in rows if r["status"] == "formal_projector_transport"],
        "controls":checks,
    })


if __name__ == "__main__":
    start = monotonic()
    if not __debug__:
        raise RuntimeError("Assertions required")
    p = ArgumentParser(description=__doc__)
    for name in ("round30","predecessor","caller-root","r52","r52-run","out"):
        p.add_argument("--"+name,type=lambda x:Path(x).resolve(),required=True)
    p.add_argument("--stage",choices=("price","body1","nonunit","structural"),default="body1")
    args = p.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    main(args,start)
