"""Priced Type B idle pairing and bounded signed projector transport."""

from argparse import ArgumentParser
from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict
from fractions import Fraction as Q
import gzip
from hashlib import sha256
from heapq import heapify, heappop, heappush
from itertools import combinations
import json
from math import isqrt
from pathlib import Path
import runpy
from time import monotonic

HEAD = "ed090b57ed88f8859e5ff4643645099e6ba856ea"
CALLER_HEAD = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
PINS = {
    "round30/complex/source/inputs/WORD.json.gz": "2c523ce6fdd6092d758fedc3602a0bcedb692b9766f1e41f903351ba4dee1756",
    "round30/complex/source/inputs/CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "round30/complex/source/inputs/EARLY-RESULT.json": "691025fe95c7938a6da211244d4d5b6187d88a9de1acff0862eeb7f0ce7deaa7",
    "7298/verify.py": "4a4291c9019ef23c664ae9646b076dc57054b49f5c5ffd21908aa9f0edf19902",
    "7298/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    "7298/RESULT.json": "aaf594b981f37e7dbddb12fd052d9286cf5c8c95c8d5265ab6426408f6e58cc5",
    "7113/research/signed-caller-8x9/replay/supplier7112/short-caller/check_odd_physical_binding.py":
        "5c80c3b0415a7f91d216395248dd6f13297eed637732098e1ca8fb0548951b98",
}
MOD = 65521
N = 36
BODIES = (tuple(range(2,19)), (19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89))
CAP = {"body1":22, "nonunit":22, "structural":42}


def unpack(raw):
    return json.loads(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)


def save(out,name,payload):
    raw = (json.dumps(payload,sort_keys=True,indent=2)+"\n").encode()
    tmp = out/(name+".tmp")
    tmp.write_bytes(raw)
    tmp.replace(out/name)
    return sha256(raw).hexdigest()


def authenticate(roots):
    files = {}
    for key, pin in PINS.items():
        label,path = key.split("/",1)
        raw = (roots[label]/path).read_bytes()
        if sha256(raw).hexdigest() != pin:
            raise ValueError(f"Changed input {key}")
        files[key] = raw
    return files


def maximum_matching(jobs):
    groups = defaultdict(list)
    for clock,role,stage in jobs:
        groups[stage].append(clock)
    heap = [(-len(g),s) for s,g in groups.items()]
    heapify(heap)
    selected = []
    while len(heap) > 1:
        na,a = heappop(heap)
        nb,b = heappop(heap)
        selected.append(sorted((groups[a].pop(),groups[b].pop())))
        if na < -1:
            heappush(heap,(na+1,a))
        if nb < -1:
            heappush(heap,(nb+1,b))
    counts = Counter(j[2] for j in jobs)
    upper = min(len(jobs)//2,len(jobs)-max(counts.values(),default=0))
    assert len(selected) == upper and len({x for pair in selected for x in pair}) == 2*upper
    return selected,counts


def price(roots):
    files = authenticate(roots)
    base = "round30/complex/source/inputs/"
    word,caller,early = (unpack(files[base+name]) for name in ("WORD.json.gz","CALLER.json","EARLY-RESULT.json"))
    old = runpy.run_path(str(roots["7298"]/"verify.py"))
    audit = old["complex_scan"](word,caller,early)
    assert json.loads(json.dumps(audit)) == unpack(files["7298/RESULT.json"])["complex"]
    binding = next(raw for key,raw in files.items() if key.startswith("7113/"))
    assert b"rank = 8*len(selected)" in binding
    assert (caller["stages"],caller["types"]["B"]["offset"],caller["types"]["B"]["roles"]) == (17,36,36)
    ports = len(caller["types"]["B"]["ports"])
    assert ports == 8
    jobs = [(i,e[2]-36,e[3][0]) for i,e in enumerate(caller["events"])
            if e[:2] == ["B","IDLE_ONE"] and len(e[3]) == 1]
    assert len(jobs) == 34 and all(0 <= r < N and 1 <= stage <= 17 for _,r,stage in jobs)
    cases = [(s[0],t[0]) for s,t in combinations(jobs,2) if s[2] != t[2]]
    assert len(cases) == 544
    matching,counts = maximum_matching(jobs)
    assert set(map(tuple,matching)) <= set(cases)
    kappa = Q(audit["probe"])
    paid = Counter({int(k):v for k,v in early["invoice"]["P"].items()})
    targets = Counter({int(k):v for k,v in early["invoice"]["T"].items()})
    assert (sum(paid.values()),sum(targets.values()),audit["copies"]) == (110536,22461,17)
    net = targets.copy()
    net.subtract(paid)
    delta = {8:2*ports,16:-ports}
    changed = net.copy()
    changed.update(delta)
    cost = old["PRICING"]["cost"]
    old_margin,new_margin,credit = cost(net,kappa),cost(changed,kappa),cost(delta,kappa)
    assert old_margin[1] < 0 < new_margin[0] and credit[0] > 0
    h8 = old["PRICING"]["power_bounds"](8,kappa)
    h16 = old["PRICING"]["power_bounds"](16,kappa)
    report = {
        "head":HEAD, "caller_head":CALLER_HEAD, "inputs":PINS, "crossing_upper":str(kappa),
        "native_copies":audit["copies"], "type_b_ports":ports, "old_complete_paid":paid,
        "old_complete_targets":targets, "old_complete_margin":list(map(str,old_margin)),
        "one_pair_paid_old_minus_new":delta, "one_pair_complete_margin":list(map(str,new_margin)),
        "one_pair_moment_credit":list(map(str,credit)),
        "break_even_volume_factor":list(map(str,(2*h8[0]/h16[1],2*h8[1]/h16[0]))),
        "whole_compatible_optimistic_upper":str(len(matching)*credit[1]),
        "maximum_disjoint_pairs":len(matching), "illustrative_matching":matching,
        "stage_counts":counts,"jobs":jobs,"pair_keys":cases,
        "new_work_assumed_free_in_price":True,
        "predeclared_followup":{"nonunit_body_vectors":BODIES,"nonunit_hard_seconds":25,
                                "structural_hard_seconds":45,"structural_max_cases":3},
    }
    return report,caller


def field_scalar(raw):
    q = Q(raw)
    if q.denominator % MOD == 0:
        raise ValueError("Nonunit modular denominator")
    return q.numerator*pow(q.denominator,-1,MOD)%MOD


def compile_gates(caller,q,body):
    gates = []
    for i,event in enumerate(caller["events"]):
        kind,op,*args = event
        if kind == "J":
            s,t,a,b = args[1]
            a,b = field_scalar(a),field_scalar(b)
            m = body[op-1]
            h = (m,m*a*q%MOD,m*b*q%MOD,m*(1+a*b)%MOD)
            assert (h[0]*h[3]-h[1]*h[2])%MOD
            gates.append((i,"J",s-36,t-36,h))
        elif kind == "B":
            d = args[0]-36
            assert 0 <= d < N
            if op == "ADD":
                gates.append((i,op,d,args[1]-36,field_scalar(args[2])))
            elif op == "QUERY":
                gates.append((i,"ADD",d,args[1]-36,pow(q,args[2]%4,MOD)))
            elif op == "SWAP":
                gates.append((i,op,d,args[1]-36,0))
            elif op == "SCALE":
                value = field_scalar(args[1])
                assert value
                gates.append((i,op,d,d,value))
            elif op in ("IDLE_ONE","IDLE_ODD"):
                value = pow(q,args[2]%4,MOD) if op == "IDLE_ODD" else 1
                for stage in args[1]:
                    value = value*body[stage-1]%MOD
                assert value
                if value != 1:
                    gates.append((i,"SCALE",d,d,value))
            elif op != "LAMBDA":
                raise ValueError(op)
    return [g[0] for g in gates],gates


def transport(gates,initial,row,mod=None,dimension=N):
    vec = [0]*dimension
    vec[initial] = 1
    mixed = False
    for _,op,d,s,c in reversed(gates) if row else gates:
        if op == "ADD":
            to,frm = (s,d) if row else (d,s)
            vec[to] += c*vec[frm]
            if mod:
                vec[to] %= mod
        elif op == "SCALE":
            vec[d] *= c
            if mod:
                vec[d] %= mod
        elif op == "SWAP":
            vec[d],vec[s] = vec[s],vec[d]
        elif op == "J":
            a,b,x,y = c
            if row:
                b,x = x,b
            u,v = vec[d],vec[s]
            vec[d],vec[s] = (a*u+b*v)%mod,(x*u+y*v)%mod
        else:
            raise ValueError(op)
        if mod is None and sum(bool(x) for x in vec) > 1:
            mixed = True
    assert any(vec)
    return vec,mixed


def outside(vec,axis):
    return next(([i,v] for i,v in enumerate(vec) if i != axis and v),None)


def controls():
    gates = [(0,"ADD",1,0,1),(1,"SCALE",0,0,2),(2,"ADD",1,0,-1)]
    assert outside(transport(gates,0,False,MOD,2)[0],0) == [1,MOD-1]
    gates[1] = (1,"SCALE",0,0,1)
    assert outside(transport(gates,0,False,MOD,2)[0],0) is None
    assert outside(transport(gates,0,True,MOD,2)[0],0) is None
    assert transport(gates,0,False,None,2)[1]
    read = [(0,"ADD",0,1,1)]
    assert outside(transport(read,0,True,MOD,2)[0],0) == [1,1]
    assert outside(transport(read,0,False,MOD,2)[0],0) is None
    match,_ = maximum_matching([(i,0,s) for i,s in enumerate([1,1,1,1,2,3])])
    assert len(match) == 2
    caller = {"events":[["B","IDLE_ONE",36,[1]],["B","ADD",37,36,"1"],
                        ["B","ADD",37,36,"-1"],["B","IDLE_ONE",36,[2]]]}
    assert structural(caller,0,3,0,0) == ("formal_projector_transport",True,None)
    caller["events"][2] = ["B","ADD",37,36,"1"]
    assert structural(caller,0,3,0,0) == ("unresolved_endpoint",True,3)
    return ["body_one_false_positive","genuine_nondiagonal_transient","outside_read_only",
            "distinct_mask_matching_does_not_double_spend"]


def modular_stage(caller,jobs,cases,bodies,deadline):
    compiled = [(v,q,*compile_gates(caller,q,body))
                for v,body in enumerate(bodies) for q in (1,MOD-1)]
    records = []
    for left,right in cases:
        if monotonic() >= deadline:
            break
        source,target = jobs[left],jobs[right]
        witness = None
        for v,q,clocks,gates in compiled:
            interval = gates[bisect_right(clocks,left):bisect_left(clocks,right)]
            write,_ = transport(interval,source,False,MOD)
            read,_ = transport(interval,target,True,MOD)
            bad_col,bad_row = outside(write,target),outside(read,source)
            if bad_col or bad_row:
                witness = {"vector_index":v,"q":1 if q == 1 else -1,
                           "outside_write":bad_col,"outside_read":bad_row}
                break
        records.append({"key":[left,right],"witness":witness})
    return records


def structural(caller,left,right,source,target):
    r = source
    block = []
    mixed = False

    def flush(axis):
        vec,m1 = transport(block,axis,False)
        nz = [i for i,v in enumerate(vec) if v]
        if len(nz) != 1:
            return None,True
        end = nz[0]
        dual,m2 = transport(block,end,True)
        return (None if outside(dual,axis) else end),m1 or m2

    for clock,event in enumerate(caller["events"][left+1:right],left+1):
        kind,op,*args = event
        if kind == "B" and op in ("ADD","SCALE","SWAP"):
            d = args[0]-36
            if op == "ADD":
                block.append((clock,op,d,args[1]-36,Q(args[2])))
            elif op == "SCALE":
                block.append((clock,op,d,d,Q(args[1])))
            else:
                block.append((clock,op,d,args[1]-36,0))
            continue
        if kind not in ("B","J"):
            continue
        r,inner = flush(r)
        mixed |= inner
        block.clear()
        if r is None:
            return "unresolved_constant_block",mixed,clock
        if kind == "J" and r in {args[1][0]-36,args[1][1]-36}:
            return "unresolved_active_j",True,clock
        if kind == "B" and op == "QUERY" and r in {args[0]-36,args[1]-36}:
            return "unresolved_query",True,clock
    r,inner = flush(r)
    mixed |= inner
    if r != target:
        return "unresolved_endpoint",mixed,right
    return ("formal_projector_transport" if mixed else "diagonal_path_overlap_pending"),mixed,None


def previous(out,name,price_sha):
    value = json.loads((out/name).read_text())
    assert value["price_sha256"] == price_sha
    return value


def main(args,start):
    roots = {"round30":args.round30,"7298":args.predecessor,"7113":args.caller_root}
    pre,caller = price(roots)
    out = args.out
    if args.stage in ("price","body1"):
        price_sha = save(out,"PRICE.json",pre)
    else:
        frozen = (out/"PRICE.json").read_bytes()
        assert unpack(frozen) == json.loads(json.dumps(pre))
        price_sha = sha256(frozen).hexdigest()
    if args.stage == "price":
        return
    jobs = {j[0]:j[1] for j in pre["jobs"]}
    cases = pre["pair_keys"]
    checks = controls()
    assert all(MOD%d for d in range(2,isqrt(MOD)+1))
    prior_unvisited = []
    if args.stage != "body1":
        first = previous(out,"BODY1.json",price_sha)
        cases = first["survivors"]
        prior_unvisited = first["unvisited"]
    if args.stage == "structural":
        second = previous(out,"NONUNIT.json",price_sha)
        cases = second["survivors"]
        prior_unvisited = second["unvisited"]
    deadline = start+CAP[args.stage]
    if args.stage in ("body1","nonunit"):
        bodies = ((1,)*17,) if args.stage == "body1" else BODIES
        rows = modular_stage(caller,jobs,cases,bodies,deadline)
        survivors = [r["key"] for r in rows if r["witness"] is None]
        save(out,("BODY1.json" if args.stage == "body1" else "NONUNIT.json"),{
            "stage":args.stage,"price_sha256":price_sha,"prime":MOD,"body_vectors":bodies,
            "scope":len(cases),"visited":len(rows),"exclusions":len(rows)-len(survivors),
            "survivors":survivors,"unvisited":[*prior_unvisited,*cases[len(rows):]],
            "records":rows,"controls":checks,
        })
        return
    rows = []
    for a,b in cases[:3]:
        if monotonic() >= deadline:
            break
        status,mixed,at = structural(caller,a,b,jobs[a],jobs[b])
        rows.append({"key":[a,b],"status":status,"nondiagonal_transient":mixed,"stop_clock":at})
    save(out,"STRUCTURAL.json",{
        "price_sha256":price_sha,"scope":len(cases),"visited":len(rows),"hard_seconds":45,
        "unvisited":[*prior_unvisited,*cases[len(rows):]],
        "support_survivors":[r["key"] for r in rows if r["status"] == "formal_projector_transport"],
        "unresolved":[r["key"] for r in rows if r["status"] != "formal_projector_transport"],
        "records":rows,"controls":checks,
    })


if __name__ == "__main__":
    start = monotonic()
    if not __debug__:
        raise RuntimeError("Assertions required")
    parser = ArgumentParser(description=__doc__)
    for flag in ("round30","predecessor","caller-root","out"):
        parser.add_argument("--"+flag,type=lambda x:Path(x).resolve(),required=True)
    parser.add_argument("--stage",choices=("price","body1","nonunit","structural"),default="body1")
    args = parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    main(args,start)
