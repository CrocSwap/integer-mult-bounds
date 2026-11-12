"""Reverse literal interval census for a split earlier paid carrier."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parent
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
PINS = {
    "inputs/R142-PLAN.md": "53d2ea30224e63e841c43f93183cdc2f25b2720ca4626dfaa2d77edbe65cfe0a",
    "inputs/R142-PRICE.json": "7f99902aaa6b47029f51fa0e10a59c677a78eca0e91b43c213d4f7e34cfececa",
    "inputs/R139-PRICE.json": "b9d6d60d467af0269e5dd4d355607c8be5d35581da487f72a593ff775967fb57",
    "inputs/R137-RESULT.json": "a109deda97d3b4f5ceb52814a50186035ea44ac1bdaf47281f564dcc2da239db",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
}
RAW = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
EVENTS, ANCHORS, KEYS, SECONDS = 76466, 47, 128, 25


def unique(pairs):
    obj = dict(pairs)
    if len(obj) != len(pairs):
        raise ValueError("duplicate JSON key")
    return obj


def authenticate(root):
    payloads = {}
    for name, digest in PINS.items():
        raw = (root/name).read_bytes()
        if sha256(raw).hexdigest() != digest:
            raise ValueError("changed dependency "+name)
        payloads[name] = raw
    return payloads


def reduce(vector, basis):
    while vector:
        pivot = vector.bit_length()-1
        if pivot not in basis:
            break
        vector ^= basis[pivot]
    return vector


def span(vectors):
    basis = {}
    for vector in vectors:
        residual = reduce(vector,basis)
        assert residual
        basis[residual.bit_length()-1] = residual
    return basis


def incidences(event):
    return event[1:3] if event[0] in ("COPY","ADD") else event[1:2]


def reverse_census(word, rows, prices, deadline, progress):
    n, owned, tape = (word[k] for k in ("public","owned_fields","program"))
    state = word["final"] + [None]*owned
    frames = word["frames"]
    bank = defaultdict(set)
    for role,chart in enumerate(state):
        if chart is not None:
            bank[chart].add(role)
    open_by_role = {}
    open_by_source = defaultdict(set)
    next_contact = {}
    records = {}
    geometry = []
    paid_owned = set()

    @cache
    def is_strict_subset(a,b):
        return len(frames[a]) < len(frames[b]) and all(
            reduce(vector,basis(b)) == 0 for vector in frames[a])

    @cache
    def basis(chart):
        return span(frames[chart])

    def change(role, old, new):
        assert state[role] == old
        if old is not None:
            bank[old].remove(role)
        if new is not None:
            bank[new].add(role)
        state[role] = new

    for t in range(len(tape)-1,-1,-1):
        progress["first_unvisited_event"] = t
        if t%128 == 0 and monotonic() >= deadline:
            raise TimeoutError("reverse traversal time cap")
        event = tape[t]
        op,role,*args = event
        touched = incidences(event)
        for h in touched:
            if h in open_by_role:
                anchor = open_by_role.pop(h)
                source = rows[anchor]["chart_from"]
                open_by_source[source].remove(anchor)
                records[anchor]["previous"] = [t,event]

        if op == "MOVE":
            a,c,is_owned = args
            assert is_owned == (role >= n)
            change(role,c,a)
            if is_owned:
                paid_owned.add(t)
            for anchor in sorted(open_by_source[a]):
                r = rows[anchor]
                h,b = r["role"],r["chart_to"]
                assert role != h and state[h] == a and t < anchor
                count = records[anchor]
                count["source_moves"] += 1
                if not is_strict_subset(a,b) or not is_strict_subset(b,c):
                    count["not_strict_chain"] += 1
                    continue
                dr,ds = len(frames[b])-len(frames[a]),len(frames[c])-len(frames[b])
                assert dr == r["rank"] and (dr,ds) in prices
                if len(geometry) == KEYS:
                    raise OverflowError("128 exact geometry keys reached before all source incidences")
                donors = sorted(bank[b]-{h,role})
                geometry.append(dict(
                    anchor=anchor, carrier=t, h=h, f=role,
                    charts=[a,b,c], ranks=[dr,ds], carrier_owned=is_owned,
                    donor_public=[x for x in donors if x < n],
                    donor_owned=[x for x in donors if x >= n],
                    gross_upper=prices[dr,ds],
                ))
                count["strict_chain"] += 1
            if is_owned:
                r = rows[t]
                assert (role,a,c) == (r["role"],r["chart_from"],r["chart_to"])
                assert abs(len(frames[a])-len(frames[c])) == r["rank"]
                nxt = next_contact[role]
                assert nxt == r["first_clock"] == t+1 and tape[nxt] == r["first_event"]
                assert tape[nxt][0] in ("ADD","SCALE")
                open_by_role[role] = t
                open_by_source[a].add(t)
                records[t] = dict(anchor=t,h=role,first_use=[nxt,tape[nxt]],source_moves=0,
                                  not_strict_chain=0,strict_chain=0)
        elif op == "INIT":
            assert role >= n
            change(role,args[0],None)
        elif op == "CLEAR":
            assert role >= n
            change(role,None,args[0])
        else:
            assert op in ("ADD","COPY","SCALE")
            assert all(state[h] == args[-1] for h in touched)
            if op == "COPY":
                assert role >= n
        for h in touched:
            next_contact[h] = t
        progress["events"] += 1
    assert state == word["initial"]+[None]*owned
    assert paid_owned == rows.keys() and not open_by_role
    progress["first_unvisited_event"] = None
    return records,geometry


def controls():
    toy = {
        "public":3, "owned_fields":1, "frames":[[],[1],[1,2]],
        "initial":[0,1,0], "final":[2,1,0],
        "program":[["INIT",3,0],["ADD",3,2,"1",0],["MOVE",0,0,2,False],
                   ["MOVE",3,0,1,True],["ADD",1,3,"1",1],["CLEAR",3,1]],
    }
    rows = {3:dict(role=3,chart_from=0,chart_to=1,rank=1,first_clock=4,first_event=toy["program"][4])}
    records, geom = reverse_census(toy,rows,{(1,1):"17"},monotonic()+1,{"events":0})
    assert records[3]["previous"] == [1,toy["program"][1]]
    assert len(geom)==1 and geom[0]["donor_public"]==[1]
    assert geom[0]["carrier"] == 2 and geom[0]["charts"] == [0,1,2]
    toy["frames"][2] = [2,4]
    records, geom = reverse_census(toy,rows,{(1,1):"17"},monotonic()+1,{"events":0})
    assert not geom and records[3]["not_strict_chain"] == 1
    return ["nested carrier with untouched live B donor","larger dimension without B containment"]


def main():
    cli = ArgumentParser(description=__doc__)
    cli.add_argument("--root",type=Path,default=ROOT)
    cli.add_argument("--controls-only",action="store_true")
    args = cli.parse_args()
    assert __debug__
    tests = controls()
    if args.controls_only:
        print(dumps(tests))
        return
    data = authenticate(args.root)
    quote, old, previous = [loads(data["inputs/"+name],object_pairs_hook=unique) for name in
                            ("R142-PRICE.json","R139-PRICE.json","R137-RESULT.json")]
    assert all((p["head"],p["caller"]) == (HEAD,CALLER) for p in (quote,old,previous))
    prices = {(r["r"],r["s"]):r["gross"][1] for r in quote["cells"]}
    assert len(prices)==33 and all(Fraction(x)>0 for x in prices.values())
    rows = {r["move_clock"]:r for r in previous["records"]}
    assert len(rows) == ANCHORS and not previous["unvisited"]
    assert {str(t):[r["role"],r["chart_from"],r["chart_to"],r["rank"]] for t,r in rows.items()} == old["keys"]

    def stop(*_):
        raise TimeoutError("25-second hard cap")

    signal(SIGALRM,stop)
    alarm(SECONDS)
    progress = {"events":0,"first_unvisited_event":EVENTS-1}
    deadline = monotonic()+SECONDS-1
    result = dict(head=HEAD,caller=CALLER,pins=PINS,controls=tests,progress=progress,
                  caps=dict(events=EVENTS,anchors=ANCHORS,keys=KEYS,seconds=SECONDS))
    try:
        raw=decompress(data["inputs/7334-WORD.json.gz"])
        assert sha256(raw).hexdigest()==RAW
        word=loads(raw,object_pairs_hook=unique)
        assert (len(word["program"]),word["public"],word["owned_fields"]) == (EVENTS,1501,68)
        records,geometry=reverse_census(word,rows,prices,deadline,progress)
        ordered=sorted(geometry,key=lambda g:(-Fraction(g["gross_upper"]),g["anchor"],g["carrier"]))
        result |= dict(complete=True, anchors=[records[t] for t in sorted(records)], geometry=ordered,
                       counts=dict(Counter({name:sum(r[name] for r in records.values()) for name in
                                           ("source_moves","not_strict_chain","strict_chain")})),unresolved=[])
    except (TimeoutError,OverflowError) as e:
        result |= dict(complete=False, reason=str(e),unresolved=sorted(rows))
    finally:
        alarm(0)
    print(dumps(result,indent=2,sort_keys=True))
    if not result["complete"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
