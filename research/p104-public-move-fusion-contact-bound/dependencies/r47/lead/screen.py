"""Preprice one signed adjacent ADD/SCALE exchange on the pinned #7277 word."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import cache
import gzip
from hashlib import sha256
import json
from pathlib import Path
import runpy
from time import monotonic

HEAD = "ed090b57ed88f8859e5ff4643645099e6ba856ea"
PINS = {
    "round30/complex/source/inputs/WORD.json.gz": "2c523ce6fdd6092d758fedc3602a0bcedb692b9766f1e41f903351ba4dee1756",
    "round30/complex/source/inputs/CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "round30/complex/source/inputs/EARLY-RESULT.json": "691025fe95c7938a6da211244d4d5b6187d88a9de1acff0862eeb7f0ce7deaa7",
    "7298/verify.py": "4a4291c9019ef23c664ae9646b076dc57054b49f5c5ffd21908aa9f0edf19902",
    "7298/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    "7298/RESULT.json": "aaf594b981f37e7dbddb12fd052d9286cf5c8c95c8d5265ab6426408f6e58cc5",
}


def unique(items):
    result = dict(items)
    assert len(result) == len(items), "Duplicate JSON key"
    return result


def authenticate(roots):
    files = {}
    for key, digest in PINS.items():
        label, relative = key.split("/", 1)
        path = roots[label] / relative
        data = path.read_bytes()
        if sha256(data).hexdigest() != digest:
            raise ValueError(f"Changed input {key}")
        if relative.endswith(".gz"):
            data = gzip.decompress(data)
        if relative.endswith((".json", ".json.gz")):
            files[key] = json.loads(data, object_pairs_hook=unique)
    return files


def write(root, filename, payload):
    target = root / filename
    temp = target.with_suffix(".tmp")
    temp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    temp.replace(target)


def interval(bounds):
    return [str(x) for x in bounds]


def exchange(first, second):
    add, scale = (first, second) if first[0] == "ADD" else (second, first)
    role, lam = scale[1], Q(scale[2])
    exponent = int(role == add[1]) - int(role == add[2])
    assert exponent and lam
    if first[0] == "SCALE":
        exponent = -exponent
    updated = [*add]
    updated[3] = str(Q(add[3])*lam**exponent)
    return (scale, updated) if first[0] == "ADD" else (updated, scale)


def scalar_product(events, roles):
    rows = {r: [Q(int(r == j)) for j in roles] for r in roles}
    for event in events:
        op, d, *args = event
        if op == "SCALE":
            rows[d] = [Q(args[0])*v for v in rows[d]]
        else:
            s, coefficient, _ = args
            rows[d] = [x+Q(coefficient)*y for x,y in zip(rows[d],rows[s],strict=True)]
    return rows


def coefficient_legal(coefficient):
    q = Q(coefficient)
    denominator = q.denominator
    for p in (2,3,5):
        while denominator % p == 0:
            denominator //= p
    return q != 0 and denominator == 1 and abs(q)+1 < 2**16


def controls():
    add = ["ADD",1,0,"-2",1]
    for role, expected in ((1,"-3"), (0,"-4/3")):
        scale = ["SCALE",role,"3/2",2]
        old = (add,scale)
        result = exchange(*old)
        assert result[1][3] == expected
        assert scalar_product(old,[0,1]) == scalar_product(result,[0,1])
        assert exchange(*result) == old
        sign = [*result[1]]
        sign[3] = str(-Q(sign[3]))
        assert scalar_product(old,[0,1]) != scalar_product((result[0],sign),[0,1])
    assert coefficient_legal("-4/3") and not coefficient_legal("1/7")
    assert not coefficient_legal(65535)
    return ["exact_destination_and_source_conjugation", "both_orders",
            "wrong_sign_rejected", "coefficient_alphabet_checked"]


def chronology(word, edge):
    public, program = word["public"], word["program"]
    current = word["initial"] + [None]*word["owned_fields"]
    pending = defaultdict(list)
    active, locations, incoming = {}, {}, {}
    normalized, paid, owned_paid = [], Counter(), Counter()
    for clock, event in enumerate(program):
        op, role, *args = event
        owned = role >= public
        if op == "MOVE":
            source,target,private = args
            assert current[role] == source and private == owned
            r = edge(source,target)
            assert r and (owned or len(word["frames"][target]) > len(word["frames"][source]))
            paid[r] += 1
            if owned:
                assert role in active
                owned_paid[r] += 1
                pending[role].append([clock,source,target,r])
            current[role] = target
            continue
        normalized.append(clock)
        chart = args[-1]
        if op == "INIT":
            assert owned and current[role] is None and role not in active
            assert not pending[role]
            active[role] = [clock]
            locations[role,clock] = active[role],0
            current[role] = chart
            continue
        for r in (role,args[0]) if op in ("ADD","COPY") else (role,):
            assert current[r] == chart
            if r < public:
                continue
            chain = active[r]
            prior = chain[-1]
            a = program[prior][-1]
            rank = edge(a,chart)
            path = pending.pop(r,[])
            assert (not path and rank == 0) or (
                len(path) == 1 and path[0][1:] == [a,chart,rank])
            incoming[r,clock] = path
            locations[r,clock] = chain,len(chain)
            chain.append(clock)
        if op == "CLEAR":
            assert owned
            del active[role]
            current[role] = None
    assert not active and not any(pending.values())
    assert current == word["final"] + [None]*word["owned_fields"]
    assert len(program) == 76443 and len(normalized) == 70163 and sum(paid.values()) == 6280
    assert owned_paid == {1:20,2:9,3:2,4:13,5:2,6:1}
    return normalized, locations, incoming, paid, owned_paid


def gate(roots, out, start, seconds):
    files = authenticate(roots)
    input_prefix = "round30/complex/source/inputs/"
    word,caller,early = (files[input_prefix+name] for name in ("WORD.json.gz","CALLER.json","EARLY-RESULT.json"))
    predecessor = runpy.run_path(str(roots["7298"]/"verify.py"))
    prior = predecessor["complex_scan"](word,caller,early)
    assert json.loads(json.dumps(prior)) == files["7298/RESULT.json"]["complex"]
    gf2_rank = predecessor["rank"]
    cost = predecessor["PRICING"]["cost"]
    frames = word["frames"]

    @cache
    def edge(a,b):
        if a == b:
            return 0
        gap = abs(len(frames[a])-len(frames[b]))
        distance = 2*gf2_rank(frames[a]+frames[b])-len(frames[a])-len(frames[b])
        return gap if gap and gap == distance else None

    normalized,loc,incoming,native,owned = chronology(word,edge)
    p = Counter({int(k):v for k,v in early["invoice"]["P"].items()})
    targets = Counter({int(k):v for k,v in early["invoice"]["T"].items()})
    copies = prior["copies"]
    net = targets.copy()
    net.subtract(p)
    kappa = Q(prior["probe"])
    baseline = cost(net,kappa)
    assert sum(p.values()) == 110536 and sum(targets.values()) == 22461 and copies == 17
    assert baseline[1] < 0 and sum(k*v for k,v in net.items()) == 1424
    prog, public = word["program"],word["public"]
    anchors = [i for i,t in enumerate(normalized) if prog[t][0] == "SCALE" and prog[t][1] >= public]
    assert len(anchors) == 22
    stock_rank = copies*sum(k*v for k,v in owned.items())
    two_rank = copies*sum(sorted(owned.elements(),reverse=True)[:2])
    assert (stock_rank,two_rank) == (1904,187)
    preprice = {
        "head":HEAD, "inputs":PINS, "crossing_upper":str(kappa),
        "complete_old_paid":p, "complete_targets":targets, "complete_old_margin":interval(baseline),
        "complete_native_paid":native, "owned_paid":owned, "old_surplus":1424, "copies":copies,
        "owned_scales":len(anchors), "neighbor_slot_cap":44, "hard_runner_cap_seconds":25,
        "whole_compatible_stock_rank_upper_before_charges":stock_rank,
        "single_swap_rank_upper_before_charges":two_rank,
        "one_swap_only":True, "predecessor_add_add_receipt_reproduced":True,
        "controls":controls(),
    }
    write(out,"PRICE.json",preprice)

    slots = sorted({j for i in anchors for j in (i-1,i) if 0 <= j < len(normalized)-1})
    assert len(slots) <= 44
    clocks = [(normalized[i],normalized[i+1]) for i in slots]
    records = []
    for t,u in clocks:
        if monotonic()-start >= seconds:
            break
        first,second = prog[t],prog[u]
        row = {"clocks":[t,u],"literal":[first,second]}
        records.append(row)
        if {first[0],second[0]} != {"ADD","SCALE"}:
            row["status"] = "other_neighbor"
            continue
        add,scale = (first,second) if first[0] == "ADD" else (second,first)
        role = scale[1]
        assert role >= public
        if role not in add[1:3]:
            row["status"] = "disjoint_roles"
            continue
        if first[-1] == second[-1] or Q(scale[2]) == 1:
            row["status"] = "same_chart_or_unit_scale"
            continue
        rewritten = exchange(first,second)
        replacement = next(event for event in rewritten if event[0] == "ADD")
        if not coefficient_legal(replacement[3]):
            row["status"] = "scalar_alphabet"
            continue
        domain = sorted(set(add[1:3]))
        assert scalar_product([first,second],domain) == scalar_product(rewritten,domain)
        chain,i = loc[role,t]
        chain2,j = loc[role,u]
        assert chain is chain2 and j == i+1 and i > 0 and j+1 < len(chain)
        prev,nxt = chain[i-1],chain[j+1]
        l,a,b,r = prog[prev][-1],first[-1],second[-1],prog[nxt][-1]
        old = (edge(l,a),edge(b,r))
        new = (edge(l,b),edge(a,r))
        middle = edge(a,b)
        assert None not in old and middle and middle == edge(b,a)
        row.update(role=role, life_bounds=[chain[0],chain[-1]], contact_clocks=[prev,t,u,nxt],
                   chart_chain=[l,a,b,r], exterior_old=old, exterior_new=new,
                   literal_old_exterior_moves=incoming[role,t]+incoming[role,nxt],
                   old_middle_move=incoming[role,u], candidate_scalars=rewritten)
        if None in new:
            row["status"] = "nonnested"
            continue
        delta = Counter(x for x in old if x)
        delta.subtract(x for x in new if x)
        delta = {k:copies*v for k,v in delta.items() if v}
        next_paid = p.copy()
        next_paid.subtract(delta)
        assert all(n >= 0 for n in next_paid.values())
        next_paid = +next_paid
        next_net = targets.copy()
        next_net.subtract(next_paid)
        margin = cost(next_net,kappa)
        row.update(full_paid=next_paid, paid_old_minus_new=delta,
                   incremental_moment=interval(cost(delta,kappa)),
                   complete_margin=interval(margin),
                   status="positive" if margin[0] > 0 else
                          ("possible_positive" if margin[1] > 0 else "no_positive_price"))
    survivors = [r for r in records if r["status"] in ("positive","possible_positive")]
    pending = clocks[len(records):]
    result = {
        "head":HEAD, "pair_slots":len(clocks), "visited":len(records), "unvisited":pending,
        "unvisited_single_swap_rank_upper_before_charges":two_rank if pending else 0,
        "counts":dict(Counter(r["status"] for r in records)), "survivors":survivors, "records":records,
    }
    write(out,"SUPPORT.json",result)


def main():
    start = monotonic()
    if not __debug__:
        raise RuntimeError("Run with assertions enabled")
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--round30",type=Path,required=True)
    parser.add_argument("--predecessor",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--seconds",type=float,default=22)
    args = parser.parse_args()
    assert 0 < args.seconds <= 22
    args.out.mkdir(parents=True,exist_ok=True)
    gate({"round30":args.round30.resolve(),"7298":args.predecessor.resolve()},args.out,start,args.seconds)


if __name__ == "__main__":
    main()
