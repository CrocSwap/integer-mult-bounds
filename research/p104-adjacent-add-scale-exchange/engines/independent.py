"""Independent direct-itinerary and complete signed-price check for one mixed swap."""
from argparse import ArgumentParser
from bisect import bisect_left
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import cache
import gzip
from hashlib import sha256
from itertools import pairwise
import json
from pathlib import Path
import runpy
import signal

HEAD = "ed090b57ed88f8859e5ff4643645099e6ba856ea"
SOURCE = "round30/complex/source/inputs/"
PINS = {
    SOURCE + "WORD.json.gz": "2c523ce6fdd6092d758fedc3602a0bcedb692b9766f1e41f903351ba4dee1756",
    SOURCE + "CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    SOURCE + "EARLY-RESULT.json": "691025fe95c7938a6da211244d4d5b6187d88a9de1acff0862eeb7f0ce7deaa7",
    "7298/verify.py": "4a4291c9019ef23c664ae9646b076dc57054b49f5c5ffd21908aa9f0edf19902",
    "7298/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    "7298/RESULT.json": "aaf594b981f37e7dbddb12fd052d9286cf5c8c95c8d5265ab6426408f6e58cc5",
}
CROSS = Q("91141748217473298207420876011401/25000000000000000000000000000000000")


def unique(pairs):
    d = dict(pairs)
    assert len(d) == len(pairs), "duplicate JSON key"
    return d


def inputs(root):
    values = {}
    for name, expected in PINS.items():
        raw = (root / name).read_bytes()
        if sha256(raw).hexdigest() != expected:
            raise ValueError("changed dependency " + name)
        if name.endswith(".gz"):
            raw = gzip.decompress(raw)
        if name.endswith((".json", ".gz")):
            values[name] = json.loads(raw, object_pairs_hook=unique)
    return values


def chart_space(frame):
    seen = {0}
    for axis in frame:
        assert axis not in seen
        seen.update([axis ^ x for x in seen])
    return frozenset(seen)


def apply(ops, add, scale, coeff):
    result = []
    for initial in [(Q(1), Q(0)), (Q(0), Q(1))]:
        field = dict(zip(add[1:3], initial, strict=True))
        for op in ops:
            if op == "ADD":
                field[add[1]] += coeff * field[add[2]]
            else:
                field[scale[1]] *= Q(scale[2])
        result.extend(field[r] for r in add[1:3])
    return tuple(result)


def conjugate(ops, add, scale):
    desired = apply(ops, add, scale, Q(add[3]))
    reversed_order = ops[::-1]
    zero = apply(reversed_order, add, scale, Q(0))
    one = apply(reversed_order, add, scale, Q(1))
    slopes = tuple(b-a for a,b in zip(zero, one, strict=True))
    i = next(i for i, slope in enumerate(slopes) if slope)
    coeff = (desired[i]-zero[i])/slopes[i]
    assert apply(reversed_order, add, scale, coeff) == desired
    assert apply(reversed_order, add, scale, -coeff) != desired
    return coeff


def alphabet(q):
    d = q.denominator
    for prime in (2, 3, 5):
        while d % prime == 0:
            d //= prime
    return q != 0 and d == 1 and abs(q)+1 < 65536


def controls():
    add = ["ADD", 1, 0, "-2", 1]
    for order, role, expected in [
        (("ADD", "SCALE"), 1, Q(-3)),
        (("ADD", "SCALE"), 0, Q(-4, 3)),
        (("SCALE", "ADD"), 1, Q(-4, 3)),
        (("SCALE", "ADD"), 0, Q(-3)),
    ]:
        assert conjugate(order, add, ["SCALE", role, "3/2", 2]) == expected
    assert alphabet(Q(-4, 3)) and not alphabet(Q(1, 7)) and not alphabet(Q(65535))
    return ["both_roles_and_orders", "signed_coefficients", "wrong_sign", "coefficient_boundary"]


def trace(word, rank):
    n = word["public"]
    chart = word["initial"] + [None]*word["owned_fields"]
    contacts = defaultdict(list)
    moves = defaultdict(list)
    paid, owned = Counter(), Counter()
    reduced = []
    for t, event in enumerate(word["program"]):
        tag, r, *v = event
        if tag == "MOVE":
            lo, hi, private = v
            assert private == (r >= n) and chart[r] == lo
            size = rank(lo, hi)
            assert size and (private or len(word["frames"][lo]) < len(word["frames"][hi]))
            chart[r] = hi
            paid[size] += 1
            if private:
                moves[r].append((t, lo, hi, size))
                owned[size] += 1
            continue
        reduced.append(t)
        if tag == "INIT":
            assert chart[r] is None and r >= n
            chart[r] = v[0]
        else:
            assert chart[r] == v[-1]
        if r >= n:
            contacts[r].append(t)
        if tag in ("ADD", "COPY"):
            s = v[0]
            assert s != r and chart[s] == v[-1]
            if s >= n:
                contacts[s].append(t)
        if tag == "CLEAR":
            assert r >= n
            chart[r] = None
    assert chart == word["final"] + [None]*word["owned_fields"]
    assert sum(paid.values()) == 6280 and sum(owned.values()) == 47
    assert len(reduced) == 70163
    return reduced, contacts, moves, paid, owned


def caller_invoice(word, caller, early, native):
    stages = [event[1] for event in caller["events"] if event[0]=="J"]
    assert stages == list(range(1, 18))
    copies = len(stages)
    paid = Counter({r:copies*n for r,n in native.items()})
    for event in caller["events"]:
        if event[0] == "J":
            continue
        kind, op, *args = event
        width = len(caller["types"][kind]["ports"])
        if op == "QUERY":
            paid[1] += width
        elif op in ("IDLE_ONE", "IDLE_ODD"):
            paid[8*len(args[1])+int(op=="IDLE_ODD")] += width
    hosted = set(word["hosted"]["X2"] + word["hosted"]["Y2"])
    hosted.update(word["live"])
    hosted.update(r+112 for r in word["live"])
    dims = list(map(len,word["frames"]))
    targets = Counter()
    for role, (a,b) in enumerate(zip(word["initial"],word["final"],strict=True)):
        if role not in hosted:
            targets[dims[b]-dims[a]] += copies
    for info in caller["types"].values():
        for q, scale, *stages in info["diagonal"]:
            assert q == -1 and scale == 0 and len(stages) == copies
            targets[1+8*sum(stages)] += len(info["ports"])
    assert paid == {int(r):n for r,n in early["invoice"]["P"].items()}
    assert targets == {int(r):n for r,n in early["invoice"]["T"].items()}
    assert sum(paid.values()) == 110536 and sum(targets.values()) == 22461
    return paid, targets, copies


@cache
def log_interval(x):
    z = (x-1)/(x+1)
    low = Q(0)
    term = z
    for j in range(80):
        low += 2*term/(2*j+1)
        term *= z*z
    return low, low+2*term/(161*(1-z*z))


def taylor(z, count):
    x = Q(1)
    acc = x
    for j in range(1, count+1):
        x *= -z/j
        acc += x
    return acc


@cache
def power(rank):
    a = rank.bit_length()-1
    logs = log_interval(Q(rank, 2**a))
    logs2 = log_interval(Q(2))
    lo, hi = (CROSS*(v+a*w) for v,w in zip(logs, logs2, strict=True))
    grid = 10**72
    lo, hi = Q((lo*grid).__floor__(), grid), Q((hi*grid).__ceil__(), grid)
    assert 0 <= lo <= hi < 1
    return rank*taylor(hi, 55), rank*taylor(lo, 54)


def quote(hist):
    lo = hi = Q(0)
    for r,n in hist.items():
        a,b = (n*x for x in power(r))
        lo += min(a,b)
        hi += max(a,b)
    g = 10**55
    return Q((g*lo).__floor__(), g), Q((g*hi).__ceil__(), g)


def report(root):
    data = inputs(root)
    word, caller, early = (data[SOURCE+x] for x in ("WORD.json.gz","CALLER.json","EARLY-RESULT.json"))
    assert Q(early["price"]["independent_raw_bracket"][1]) == CROSS
    predecessor = runpy.run_path(str(root/"7298/verify.py"))
    original = predecessor["complex_scan"](word,caller,early)
    assert json.loads(json.dumps(original)) == data["7298/RESULT.json"]["complex"]
    spaces = [chart_space(f) for f in word["frames"]]
    @cache
    def rank(a,b):
        if a == b:
            return 0
        left, right = spaces[a],spaces[b]
        if left < right or right < left:
            return abs(len(word["frames"][a])-len(word["frames"][b]))
        return None
    reduced, contacts, moves, native, owned = trace(word,rank)
    paid, targets, copies = caller_invoice(word,caller,early,native)
    net = targets.copy()
    net.subtract(paid)
    assert sum(r*n for r,n in net.items()) == 1424
    baseline = quote(net)
    assert baseline[1] < 0
    prog = word["program"]
    n = word["public"]
    rows, legal = [], []
    for t,u in pairwise(reduced):
        first, second = prog[t],prog[u]
        if not any(e[0]=="SCALE" and e[1]>=n for e in (first,second)):
            continue
        row = {"clocks":[t,u]}
        rows.append(row)
        order = (first[0],second[0])
        if set(order) != {"ADD","SCALE"}:
            row["status"] = "other_neighbor"
            continue
        add, scale = (first,second) if first[0]=="ADD" else (second,first)
        r = scale[1]
        if r not in add[1:3]:
            row["status"] = "disjoint_roles"
            continue
        if first[-1]==second[-1] or Q(scale[2])==1:
            row["status"] = "same_chart_or_unit_scale"
            continue
        coeff = conjugate(order,add,scale)
        if not alphabet(coeff):
            row["status"] = "scalar_alphabet"
            continue
        chain = contacts[r]
        i = bisect_left(chain,t)
        before, first_touch, second_touch, after = chain[i-1:i+3]
        assert (first_touch,second_touch)==(t,u) and i>0
        old_edges = list(zip((before,t,u),(t,u,after),strict=True))
        old_ranks = []
        for a,b in old_edges:
            x,y = prog[a][-1],prog[b][-1]
            size = rank(x,y)
            assert size is not None
            actual = [v[1:] for v in moves[r] if a < v[0] < b]
            assert actual == ([(x,y,size)] if size else [])
            old_ranks.append(size)
        a,b,c,d = [prog[i][-1] for i in (before,t,u,after)]
        new_ranks = [rank(a,c),rank(c,b),rank(b,d)]
        assert old_ranks[1] == new_ranks[1] and old_ranks[1] > 0
        if None in new_ranks:
            row["status"] = "nonnested"
            continue
        signed = Counter(x for x in old_ranks if x)
        signed.subtract(x for x in new_ranks if x)
        delta = {r:n*copies for r,n in signed.items() if n}
        complete = net.copy()
        complete.update(delta)
        saving, margin = quote(delta), quote(complete)
        assert saving[1] < 0 and margin[1] < 0
        row.update(status="no_positive_price", role=r, prior=before, next=after, new_coefficient=str(coeff),
                   old_route=old_ranks, new_route=new_ranks, paid_old_minus_new=delta,
                   signed_delta=list(map(str,saving)), full_margin=list(map(str,margin)))
        legal.append((row,saving,margin))
    counts = Counter(row["status"] for row in rows)
    assert len(rows)==44 and len(legal)==7
    best,saving,margin=max(legal,key=lambda z:z[1][1])
    assert all(r==best or delta[1]<saving[0] for r,delta,_ in legal)
    return dict(head=HEAD, pins=PINS, old_crossing=str(CROSS), copies=copies,
                paid=dict(paid), productive=dict(targets), owned_paid=dict(owned),
                old_margin=list(map(str,baseline)), rows=rows, counts=counts,
                best_clocks=best["clocks"], best_signed_delta=list(map(str,saving)),
                best_complete_margin=list(map(str,margin)), candidates=0, unresolved=0,
                controls=controls(), predecessor_7298="PASS")


if __name__ == "__main__":
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("dependencies", type=Path)
    args = parser.parse_args()
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError("24-second cap")))
    signal.alarm(24)
    print(json.dumps(report(args.dependencies), sort_keys=True, indent=2))
