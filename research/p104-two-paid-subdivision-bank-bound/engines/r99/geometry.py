"""Find simultaneous mover-disjoint paid subdivisions with one common span."""
from bisect import bisect_left
from collections import defaultdict
from gzip import decompress
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "lead/PRICE.json": "0eba831b917331f7a84f4d8a5da726577ed516f04c5f1b94671e031dd2c0b3b4",
    "inputs/R92-GEOMETRY.json": "e9f93f3271855012b2de705c70f186f78c31a369d28110e92c5f2ffadae209b3",
    "inputs/R92-PRICE.json": "05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
}
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("duplicate JSON key")
    return result


def checked(name):
    value = (ROOT/name).read_bytes()
    if sha256(value).hexdigest() != PINS[name]:
        raise ValueError(f"changed dependency {name}")
    if name.endswith(".gz"):
        value = decompress(value)
        assert sha256(value).hexdigest() == PAYLOAD
    return json.loads(value,object_pairs_hook=unique)


def space(basis):
    values = {0}
    for v in basis:
        assert v not in values
        values.update(v^w for w in tuple(values))
    return frozenset(values)


def basis_of(span):
    values = {0}
    basis = []
    for v in span:
        if v not in values:
            values.update(v^w for w in tuple(values))
            basis.append(v)
    assert values == set(span)
    return basis


def incident(event):
    op,d,*args = event
    return (d,args[0]) if op in ("ADD","COPY") else (d,)


def window(clocks,at,end):
    i = bisect_left(clocks,at)
    assert clocks[i] == at
    return (clocks[i-1]+1 if i else 0, clocks[i+1] if i+1 < len(clocks) else end)


def controls():
    assert incident(["COPY",5,2,"-3/2",3]) == (5,2)
    assert window([0,3,5],3,7) == (1,5)
    assert basis_of((0,1,4,5)) == [1,4]
    assert space([1,4]) == frozenset((0,1,4,5))
    assert space([4,5]) == space([1,4])
    return ["source contact", "inclusive pre-event windows", "canonical span", "basis-invariant equality"]


def stopped(*_):
    raise TimeoutError("hard runner limit")


def cap(condition,label):
    if condition:
        raise TimeoutError(label)


def main():
    assert __debug__
    price = checked("lead/PRICE.json")
    limits = price["limits"]
    signal(SIGALRM,stopped)
    alarm(limits["geometry_seconds"])
    deadline = monotonic()+18
    out = {"stage":"authenticate","visited_placements":0,"pair_comparisons":0,"scheduled_cuts":0,
           "visited_cuts":0,"owned_rejections":0,"representatives":[],"pair_intervals":[],
           "outside_window":[],"first_unvisited_event":None,"current_pair":None}
    reason = None
    try:
        previous = checked("inputs/R92-GEOMETRY.json")
        prior_price = checked("inputs/R92-PRICE.json")
        word = checked("inputs/7334-WORD.json.gz")
        cohort = set(prior_price["endpoint_cohort"])
        program = word["program"]
        n = word["public"]
        size = len(program)
        assert (n,word["owned_fields"],size) == (1501,68,limits["events_each"])
        out["stage"] = "mover contacts"
        clocks = defaultdict(list)
        for t,event in enumerate(program):
            if t % 128 == 0:
                out["first_unvisited_event"] = t
                cap(monotonic()>=deadline,"mover contacts deadline")
            for role in incident(event):
                clocks[role].append(t)
        frames = word["frames"]
        spaces = [space(f) for f in frames]
        labels = defaultdict(list)
        for chart,span in enumerate(spaces):
            if len(frames[chart]) in (4,5):
                labels[tuple(sorted(span))].append(chart)
        groups = defaultdict(list)
        out["stage"] = "group frozen quotient lines"
        for p in previous["raw_placements"]:
            at,role,rank,v = (p["move_clock"],p["mover"],p["rank"],p["quotient_representative"])
            op,d,a,c,owned = program[at]
            assert op == "MOVE" and d == role and d in cohort and not owned
            lo,hi = spaces[a],spaces[c]
            mid = lo | {x^v for x in lo}
            assert lo < mid < hi and len(mid) == 2**rank
            span = tuple(sorted(mid))
            assert [r["chart"] for r in p["labels"]] == labels[span]
            first,last = window(clocks[role],at,size)
            groups[span].append((at,role,first,last,a,c))
            out["visited_placements"] += 1
        assert out["visited_placements"] == limits["placement_count"]
        out["distinct_spans"] = len(groups)
        out["pair_stock"] = sum(len(entries)*(len(entries)-1)//2 for entries in groups.values())
        out["stage"] = "pair windows"
        tasks = defaultdict(list)
        for span,rows in sorted(groups.items()):
            for left,right in combinations(sorted(rows),2):
                out["current_pair"] = [left[0],right[0],list(span)]
                cap(out["pair_comparisons"]>=limits["pair_comparisons"] or monotonic()>=deadline,"pair cap")
                out["pair_comparisons"] += 1
                assert left[0] != right[0] and left[1] != right[1]
                first,last = max(left[2],right[2]),min(left[3],right[3])
                if first > last:
                    out["outside_window"].append(out["current_pair"])
                    continue
                for chart in labels[span] or [None]:
                    pair_id = len(out["pair_intervals"])
                    out["pair_intervals"].append({"pair":pair_id,"chart":chart,"basis":basis_of(span),
                        "left":left,"right":right,"first":first,"last":last})
                    for t in range(first,last+1):
                        cap(out["scheduled_cuts"]>=limits["raw_pair_cuts"],"scheduled pair cut cap")
                        tasks[t].append(pair_id)
                        out["scheduled_cuts"] += 1
        assert out["pair_stock"] == out["pair_comparisons"]
        out["current_pair"] = None

        out["stage"] = "public bank snapshots"
        chart_of = word["initial"][:] + [None] * word["owned_fields"]
        banks = defaultdict(set)
        last_contact = {}
        previous_class = {}
        for t in range(size+1):
            if t % 128 == 0:
                out["first_unvisited_event"] = t
                cap(monotonic()>=deadline,"bank replay deadline")
            if t == 0:
                for r,c in enumerate(word["initial"]):
                    banks[c].add(r)
            for pair_id in tasks.get(t,()):
                out["visited_cuts"] += 1
                row = out["pair_intervals"][pair_id]
                chart = row["chart"]
                a,d,*_ = row["left"]
                b,e,*_ = row["right"]
                current = banks[chart] if chart is not None else set()
                assert not {d,e} & current
                if any(r >= n for r in current):
                    out["owned_rejections"] += 1
                    continue
                token = (last_contact.get(chart),t>a,t>b)
                if previous_class.get(pair_id) == token:
                    continue
                previous_class[pair_id] = token
                public = sorted(current|{d,e})
                out["representatives"].append({"key":[t,pair_id],"public":public,"owned":[],
                    "pivots":sorted(set(public)&cohort),"previous_chart_contact":token[0]})
            if t == size:
                break
            op,d,*args = program[t]
            src = chart_of[d]
            if src is not None:
                last_contact[src] = t
            if op in ("MOVE","INIT"):
                dest = args[1] if op == "MOVE" else args[0]
                if op == "MOVE":
                    assert src == args[0] and args[2] == (d>=n)
                    banks[src].remove(d)
                else:
                    assert src is None and d>=n
                banks[dest].add(d)
                chart_of[d] = dest
                last_contact[dest] = t
            elif op == "CLEAR":
                assert src == args[0] and d>=n
                banks[src].remove(d)
                chart_of[d] = None
            else:
                assert op in ("ADD","COPY","SCALE") and src == args[-1]
                if op in ("ADD","COPY"):
                    assert chart_of[args[0]] == src
        assert chart_of == word["final"] + [None] * word["owned_fields"]
        assert out["scheduled_cuts"] == out["visited_cuts"]
        out.update(stage="complete",first_unvisited_event=None)
    except TimeoutError as exc:
        reason = str(exc)
    finally:
        alarm(0)
    print(json.dumps(dict(head=price["head"],pins=PINS,limits=limits,controls=controls(),timeout=reason,**out),
                     indent=2,sort_keys=True))
    if reason:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
