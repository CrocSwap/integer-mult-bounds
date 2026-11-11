"""Inventory and exact scalar-silence gate for one #7277 public MOVE fusion."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import cache
from hashlib import sha256
import json
from pathlib import Path
import runpy
from time import monotonic

R47 = "04c6f986b45945dcb4df22bcbfc74780e5840ff9c97b6c4dad064fc2c5576f75"
CORE = "fd7a1a7f9cb8f71caa5e0d89ed16ea056503fa283bc05f655eb0da7e8d5fc6e0"
LIMIT = 6279


def checked(path, pin):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != pin:
        raise ValueError(f"Unexpected source hash for {path.name}")
    return raw


def contacts(event):
    return event[1:3] if event[0] in ("ADD","COPY") else event[1:2]


def enumerate_pairs(word, edge):
    prior, middle = {}, defaultdict(list)
    pairs = []
    for clock,event in enumerate(word["program"]):
        op, role, *args = event
        if op == "MOVE":
            source,dest,owned = args
            if owned:
                continue
            rank = edge(source,dest)
            assert role < word["public"] and rank
            if role in prior:
                first,a,b,x = prior[role]
                assert b == source
                pairs.append({"moves":[first,clock], "role":role, "charts":[a,b,dest],
                              "ranks":[x,rank], "contacts":middle.pop(role,[])})
            prior[role] = (clock,source,dest,rank)
        else:
            assert op in ("ADD","SCALE","COPY","INIT","CLEAR")
            for r in contacts(event):
                if r in prior:
                    middle[r].append(clock)
    assert len(pairs) <= LIMIT
    return pairs


def stock(pairs, uppers):
    """Maximum bound with no old MOVE credited twice. Cross-role clashes are granted away."""
    windows = defaultdict(list)
    for pair,upper in zip(pairs,uppers,strict=True):
        windows[pair["role"]].append((pair["moves"],upper))
    total = Q(0)
    for edges in windows.values():
        before, last = Q(0), Q(0)
        previous = None
        for (first,second), credit in edges:
            assert previous is None or first == previous
            before,last = last,max(last,before+credit)
            previous = second
        total += last
    return total


def silent(event, rows, fresh):
    op,d,*args = event
    if op == "ADD":
        s = args[0]
        if rows[s][1]:
            return "nonzero_add_source"
        return "fresh_token_change" if d in fresh else "silent_zero_source_add"
    if op == "SCALE":
        return "nonzero_scale_row" if rows[d][1] else "silent_zero_row_scale"
    return "hard_contact"


def scalar_audit(path, raw):
    source = raw.decode()
    old = "def audit(word, start, seconds, visit_owned_move=None):"
    new = "def audit(word, start, seconds, visit_owned_move=None, visit_scalar=None):"
    key = "        op, d, *args = event\n"
    assert source.count(old) == source.count(key) == 1
    adapter = ("        if visit_scalar is not None and op in ('ADD','SCALE','COPY'):\n"
               "            visit_scalar(index, event, rows, fresh)\n")
    source = source.replace(old,new).replace(key,key+adapter)
    scope = {"__name__":"r48_signed_replay", "__file__":str(path)}
    exec(compile(source,str(path),"exec"),scope)
    return scope["audit"]


def controls(audit):
    zero = (1,{})
    one = (1,{0:1})
    add = ["ADD",0,1,"-3/2",1]
    assert silent(add,[one,zero],set()) == "silent_zero_source_add"
    assert silent(add,[one,zero],{0}) == "fresh_token_change"
    assert silent(add,[one,one],set()) == "nonzero_add_source"
    assert silent(["COPY",0,1,"1",1],[one,zero],set()) == "hard_contact"
    word = {"public":1,"owned_fields":1,"frames":[[],[1],[1,2]],"initial":[0],"final":[2],
            "program":[["INIT",1,0],["COPY",1,0,"1",0],["ADD",0,1,"-1",0],
                       ["CLEAR",1,0],["MOVE",0,0,1,False],["SCALE",0,"3/2",1],
                       ["MOVE",0,1,2,False]]}
    observed = {}
    report = audit(word,monotonic(),1,visit_scalar=lambda i,e,rows,fresh:
                   observed.update({i:silent(e,rows,fresh)}))
    assert report["scope_exhausted"] and observed[5] == "silent_zero_row_scale"
    word["program"][2][3] = "1"
    report = audit(word,monotonic(),1,visit_scalar=lambda i,e,rows,fresh:
                   observed.update({i:silent(e,rows,fresh)}))
    assert report["scope_exhausted"] and observed[5] == "nonzero_scale_row"
    assert stock([{"role":0,"moves":[1,2]},{"role":0,"moves":[2,3]},
                  {"role":0,"moves":[3,4]}],[Q(2),Q(3),Q(2)]) == 4
    return ["zero_source_add","fresh_token_barrier","copy_barrier","exact_signed_zero_row_scale",
            "changed_sign_breaks_silence","stock_cannot_double_spend_middle_move"]


def main(args, start):
    source = checked(args.r47,R47)
    assert source
    old = runpy.run_path(str(args.r47))
    roots = {"round30":args.round30,"7298":args.predecessor}
    files = old["authenticate"](roots)
    core = checked(args.core,CORE)
    prefix = "round30/complex/source/inputs/"
    word,caller,early = (files[prefix+x] for x in ("WORD.json.gz","CALLER.json","EARLY-RESULT.json"))
    previous = runpy.run_path(str(args.predecessor/"verify.py"))
    receipt = previous["complex_scan"](word,caller,early)
    assert json.loads(json.dumps(receipt)) == files["7298/RESULT.json"]["complex"]
    rank, cost = previous["rank"],previous["PRICING"]["cost"]
    frames = word["frames"]

    @cache
    def edge(a,b):
        if a == b:
            return 0
        gap = abs(len(frames[a])-len(frames[b]))
        distance = 2*rank(frames[a]+frames[b])-len(frames[a])-len(frames[b])
        return gap if gap and gap == distance else None

    _,_,_,native,owned = old["chronology"](word,edge)
    paid = Counter({int(k):v for k,v in early["invoice"]["P"].items()})
    targets = Counter({int(k):v for k,v in early["invoice"]["T"].items()})
    kappa,copies = Q(receipt["probe"]),receipt["copies"]
    net = targets.copy()
    net.subtract(paid)
    base = cost(net,kappa)
    assert sum(paid.values()) == 110536 and sum(targets.values()) == 22461 and copies == 17
    assert base[1] < 0 and sum(k*v for k,v in net.items()) == 1424
    pairs = enumerate_pairs(word,edge)
    program = word["program"]

    @cache
    def quote(x,y):
        delta = Counter({x:copies})
        delta[y] += copies
        delta[x+y] -= copies
        new_net = net.copy()
        new_net.update(delta)
        return old["interval"](cost(delta,kappa)),old["interval"](cost(new_net,kappa)),dict(delta)

    eligible, rows, uppers = [],[],[]
    for pair in pairs:
        if monotonic()-start >= args.seconds:
            break
        a,b,c = pair["charts"]
        x,y = pair["ranks"]
        fused = edge(a,c)
        barriers = [i for i in pair["contacts"] if program[i][0] not in ("ADD","SCALE")]
        row = {**pair,"fused_rank":fused,"hard_contacts":barriers}
        rows.append(row)
        if fused != x+y or barriers:
            row["status"] = "structural_exclusion"
            uppers.append(Q(0))
            continue
        saving,margin,delta = quote(x,y)
        row.update(saving=saving,complete_margin=margin,full_paid_old_minus_new=delta,
                   status="price_candidate" if Q(margin[1]) > 0 else "price_exclusion")
        uppers.append(max(Q(0),Q(saving[1])))
        if row["status"] == "price_candidate":
            eligible.append(row)

    unresolved_price = pairs[len(rows):]
    upper = stock(pairs,uppers+[Q(copies*sum(pair["ranks"])) for pair in unresolved_price])
    price = {
        "head":old["HEAD"],"input_pins":{**old["PINS"],"r47/lead/screen.py":R47,
                    "round41/independent/replay_core.py":CORE},
        "crossing_upper":str(kappa),"copies":copies,"old_margin":old["interval"](base),
        "old_full_paid":paid,"old_full_targets":targets,"old_native_paid":native,"old_owned_paid":owned,
        "pair_scope":len(pairs),"priced":len(rows),"whole_compatible_upper":str(upper),
        "unresolved_price":unresolved_price,"price_candidates":len(eligible),"records":rows,
        "budget":{"pair_limit":LIMIT,"hard_seconds":45,"cooperative_seconds":args.seconds},
    }
    old["write"](args.out,"PRICE.json",price)
    if args.inventory_only or unresolved_price or upper <= 0:
        return

    audit = scalar_audit(args.core,core)
    verified_controls = controls(audit)
    requested = {i for pair in eligible for i in pair["contacts"]}
    observed = {}
    def observe(i,event,rows,fresh):
        if i in requested:
            observed[i] = silent(event,rows,fresh)

    decoded = None
    if requested and monotonic()-start < args.seconds:
        decoded = audit(word,start,args.seconds,visit_scalar=observe)
    decisions = []
    for row in eligible:
        states = [[i,observed.get(i,"unvisited")] for i in row["contacts"]]
        failing = [s for _,s in states if s not in ("unvisited","silent_zero_source_add","silent_zero_row_scale")]
        if failing:
            status = "scalar_exclusion"
        elif any(s == "unvisited" for _,s in states):
            status = "unresolved"
        elif Q(row["complete_margin"][0]) > 0:
            status = "positive_contact_free" if not states else "positive_silent_contacts"
        else:
            status = "unresolved_price_interval"
        decisions.append({**row,"status":status,"scalar_evidence":states})
    old["write"](args.out,"SUPPORT.json",{
        "head":old["HEAD"],"counts":dict(Counter(r["status"] for r in decisions)),
        "scope_exhausted":all(not r["status"].startswith("unresolved") for r in decisions),
        "unresolved":[r["moves"] for r in decisions if r["status"].startswith("unresolved")],
        "survivors":[r for r in decisions if r["status"].startswith("positive")],
        "controls":verified_controls,"literal_signed_replay":decoded,"records":decisions,
    })


if __name__ == "__main__":
    start = monotonic()
    if not __debug__:
        raise RuntimeError("Run with assertions enabled")
    parser = ArgumentParser(description=__doc__)
    for flag in ("r47","round30","predecessor","core","out"):
        parser.add_argument("--"+flag,type=Path,required=True)
    parser.add_argument("--seconds",type=float,default=42)
    parser.add_argument("--inventory-only",action="store_true")
    args = parser.parse_args()
    assert 0 < args.seconds <= 42
    for name in ("r47","round30","predecessor","core","out"):
        setattr(args,name,getattr(args,name).resolve())
    args.out.mkdir(parents=True,exist_ok=True)
    main(args,start)
