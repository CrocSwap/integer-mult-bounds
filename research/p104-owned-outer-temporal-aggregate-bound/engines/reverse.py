"""R147 independent reverse ownership chronology and sparse signed covectors."""
from argparse import ArgumentParser
from collections import defaultdict
from fractions import Fraction as Q
from functools import cache
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from signal import SIGALRM, alarm, signal

HERE = Path(__file__).resolve().parent
PINS = {
    "inputs/PRICE.json": "144140e01329901d6563014a532c7711c3515972c9b6863979d8bb62d43f4d07",
    "inputs/FORWARD.json": "d70e526d2c97515a7ed78753549755e11552cf41af0981a6e465a58afe0b3e26",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
}
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
U, V, H, AXIS = 41996, 44242, 1531, 244
A, B, C = 594, 117, 534
NATIVE_EVENTS = 76466


def unique(items):
    out = dict(items)
    if len(out) != len(items):
        raise ValueError("duplicate JSON key")
    return out


def checked(root, name):
    raw = (root / name).read_bytes()
    if sha256(raw).hexdigest() != PINS[name]:
        raise ValueError("changed dependency " + name)
    return raw


@cache
def scalar(x):
    return Q(x)


def update(vec, key, delta):
    value = vec.get(key, 0) + delta
    if value:
        vec[key] = value
    else:
        vec.pop(key, None)


def reverse_axis(events, cut, role, axis):
    covector = {role: Q(1)}
    for t in range(cut - 1, -1, -1):
        event = events[t]
        op, dst = event[:2]
        if dst not in covector:
            continue
        if op == "ADD":
            update(covector, event[2], covector[dst] * scalar(event[3]))
        elif op == "COPY":
            update(covector, event[2], covector.pop(dst) * scalar(event[3]))
        elif op == "SCALE":
            covector[dst] *= scalar(event[2])
        elif op in ("INIT", "CLEAR"):
            covector.pop(dst)
        else:
            assert op == "MOVE"
        if not covector:
            return Q(0)
    return covector.get(axis, Q(0))


def operands(e):
    return e[1:3] if e[0] in ("ADD", "COPY") else e[1:2]


def potentially_changes_bank(event, chart):
    op = event[0]
    if all(r == H for r in operands(event)):
        return False
    return chart in event[2:4] if op == "MOVE" else chart == event[-1]


def reverse_inventory(word):
    n, m, events = word["public"], word["owned_fields"], word["program"]
    assert (n, m, len(events)) == (1501, 68, NATIVE_EVENTS)
    charts = list(word["final"]) + [None] * m
    bank = defaultdict(set)
    for r, c in enumerate(charts):
        if c is not None:
            bank[c].add(r)
    active_clear = {}
    birth = {}
    snapshots = {A: {}, C: {}}
    boundaries = {A: {U, U + 1, V}, C: {U, U + 1, V}}
    owner_contacts = []

    def reverse_change(r, after, before):
        assert charts[r] == after
        if after is not None:
            bank[after].remove(r)
        if before is not None:
            bank[before].add(r)
        charts[r] = before

    for t in range(len(events) - 1, -1, -1):
        event = events[t]
        op, dst = event[:2]
        if op == "MOVE":
            old, new, owned = event[2:]
            assert owned == (dst >= n)
            reverse_change(dst, new, old)
        elif op == "CLEAR":
            assert dst >= n and dst not in active_clear
            active_clear[dst] = t
            reverse_change(dst, None, event[2])
        elif op == "INIT":
            assert dst >= n and dst in active_clear
            birth[active_clear.pop(dst)] = t
            reverse_change(dst, event[2], None)
        elif op in ("ADD", "COPY", "SCALE"):
            assert all(charts[r] == event[-1] for r in operands(event))
        else:
            raise ValueError(op)
        if U < t < V and H in operands(event):
            owner_contacts.append([t,event])
        if U <= t <= V:
            for c in (A,C):
                labels = sorted(bank[c] - {H})
                snapshots[c][t] = labels, [(r,active_clear[r]) for r in labels if r >= n]
                if t < V and potentially_changes_bank(event,c):
                    boundaries[c].add(t+1)
    assert charts == word["initial"] + [None]*m and not active_clear
    assert owner_contacts[::-1] == [[41997,["ADD",H,1291,"-2",B]],
                                    [44241,["ADD",H,732,"-1",B]]]
    assert events[U] == ["MOVE",H,A,B,True] and events[V] == ["MOVE",H,B,C,True]
    assert birth[44247] == 32607 and events[32607][:2] == ["INIT",H] and events[44247][:2] == ["CLEAR",H]
    return snapshots, boundaries, birth


def controls():
    word = [
        ["ADD",1,0,"-3",0],
        ["SCALE",1,"2",0],
        ["INIT",3,0],
        ["COPY",3,1,"1/2",0],
        ["CLEAR",3,0],
    ]
    assert reverse_axis(word,4,3,0) == -3
    assert reverse_axis(word,3,3,0) == 0 and reverse_axis(word,5,3,0) == 0
    assert potentially_changes_bank(["MOVE",1,2,3,False],2)
    assert potentially_changes_bank(["MOVE",1,2,3,False],3)
    assert not potentially_changes_bank(["MOVE",H,2,3,True],2)
    return ["signed transpose COPY and SCALE", "clean initialization and erasure",
            "two-sided chart membership boundaries", "omitted changed owner excluded"]


def run(root):
    price = json.loads(checked(root,"inputs/PRICE.json"),object_pairs_hook=unique)
    lead = json.loads(checked(root,"inputs/FORWARD.json"),object_pairs_hook=unique)
    assert price["caps"] == {"events":NATIVE_EVENTS,"schedules":2,"bank_cuts":4494,"seconds":20}
    assert price["switches"] == {"early":U,"late":V} and price["owner"] == H and price["input_axis"] == AXIS
    assert (lead["head"],lead["caller"]) == (price["head"],price["caller"])
    assert lead["price_sha256"] == PINS["inputs/PRICE.json"]
    raw = decompress(checked(root,"inputs/7334-WORD.json.gz"))
    assert sha256(raw).hexdigest() == PAYLOAD
    word = json.loads(raw,object_pairs_hook=unique)
    events = word["program"]
    snapshots,boundaries,birth = reverse_inventory(word)
    cases, cuts, incidences = [], 0, 0
    for chart in (A,C):
        starts = sorted(boundaries[chart])
        prior = lead["aliases"][str(chart)]
        assert [r["first"] for r in prior] == starts
        for first,after,expected in zip(starts,starts[1:]+[V+1],prior):
            assert (first,after-1) == (expected["first"],expected["last"])
            roles,life = snapshots[chart][first]
            assert all(snapshots[chart][t] == (roles,life) for t in range(first,after))
            assert roles == expected["roles"] and [[r,birth[c]] for r,c in life] == expected["owned_births"]
            values = [[r,str(reverse_axis(events,first,r,AXIS))] for r in roles]
            assert all(value == "0" for _,value in values) and not expected["nonzero"]
            cuts += after-first
            incidences += (after-first)*len(roles)
            cases.append(dict(chart=chart,first=first,last=after-1,roles=roles,
                              owned_births=expected["owned_births"],coordinate_244=values))
    old = []
    for t in (41997,44241):
        op,dst,src,signed,chart = events[t]
        assert (op,dst,chart) == ("ADD",H,B)
        coefficient = reverse_axis(events,t,src,AXIS)
        old.append([t,src,signed,str(coefficient),str(coefficient*scalar(signed))])
    assert old == lead["old_source_responses"]
    aggregate = sum(scalar(row[-1]) for row in old)
    diagonal = [U,str(reverse_axis(events,U,H,AXIS))]
    assert diagonal == lead["owner_diagonal"] == [U,"0"]
    copies = [[t,e[1],str(reverse_axis(events,t,e[1],AXIS))]
              for t,e in enumerate(events) if e[0] == "COPY"]
    assert len(copies) == 1 and copies[0][-1] == "0"
    assert len(cases) == 9 and cuts == lead["bank_cuts"] == 4494
    assert incidences == lead["donor_incidences"] == 7163 and aggregate == Q(-1,2)
    return dict(pins=PINS,head=price["head"],caller=price["caller"],events=len(events),bank_cuts=cuts,
                donor_incidences=incidences,aliases=cases,old_source_responses=old,
                aggregate_response=str(aggregate),owner_diagonal=diagonal,copy_prewrite=copies,
                controls=controls(),unresolved=[])


def stop(_signal,_frame):
    raise TimeoutError("20 second reverse audit cap")


def main():
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,default=HERE)
    args = parser.parse_args()
    signal(SIGALRM,stop)
    alarm(20)
    try:
        print(json.dumps(run(args.root),sort_keys=True,indent=2))
    finally:
        alarm(0)


if __name__ == "__main__":
    main()
