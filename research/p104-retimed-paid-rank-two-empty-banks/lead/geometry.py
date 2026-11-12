"""Reconstruct exact no-contact windows and occupied-chart representatives."""
from bisect import bisect_left
from collections import defaultdict
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "lead/PRICE.json": "b1484654ca01b98b566f5849249228ca61695185c90d6a54eebbd9c8649de5c4",
    "inputs/R92-PRICE.json": "05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
}
WORD_PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"


def unique(pairs):
    out = dict(pairs)
    if len(pairs) != len(out):
        raise ValueError("duplicate JSON key")
    return out


def checked(name):
    value = (ROOT/name).read_bytes()
    if sha256(value).hexdigest() != PINS[name]:
        raise ValueError(f"changed dependency {name}")
    if name.endswith(".gz"):
        value = decompress(value)
        assert sha256(value).hexdigest() == WORD_PAYLOAD
    return json.loads(value,object_pairs_hook=unique)


def window(contacts, at, size):
    where = bisect_left(contacts,at)
    assert contacts[where] == at
    first = contacts[where-1]+1 if where else 0
    last = contacts[where+1] if where+1 < len(contacts) else size
    return first,last


def roles(event):
    op,d,*args = event
    return (d,args[0]) if op in ("ADD","COPY") else (d,)


def controls():
    assert roles(["ADD",3,1,"-1",2]) == (3,1)
    assert roles(["SCALE",3,"-1",2]) == (3,)
    assert window([1,7,9],7,12) == (2,9)
    assert window([0],0,2) == (0,2)
    return ["source contacts count", "pre-event inclusive endpoints",
            "whole-word boundary with no other contact"]


def stop(*_):
    raise TimeoutError("hard geometry timeout")


def main():
    assert __debug__
    price = checked("lead/PRICE.json")
    prior = checked("inputs/R92-PRICE.json")
    limit = price["limits"]
    alarm(limit["geometry_seconds"])
    deadline = monotonic()+18
    state = {"first_unvisited_event": None, "stage":"authenticate literal", "windows":[],
             "raw_cut_count":0, "visited_labelled_cuts":0,"eligible_raw_cuts":0, "representatives":[]}
    reason = None
    try:
        word = checked("inputs/7334-WORD.json.gz")
        cohort = set(prior["endpoint_cohort"])
        n = word["public"]
        program = word["program"]
        size = len(program)
        assert (n, word["owned_fields"], size) == (1501,68,limit["events_each"])
        contacts = defaultdict(list)
        state["stage"] = "incident clocks"
        for t,event in enumerate(program):
            if t % 128 == 0:
                state["first_unvisited_event"] = t
                if monotonic() >= deadline:
                    raise TimeoutError("bounded contacts")
            for role in roles(event):
                contacts[role].append(t)

        by_cut = defaultdict(list)
        labelled = price["labelled"]
        scheduled = 0
        state["stage"] = "labelled windows"
        for at,mover,chart,rank,rep in labelled:
            first,last = window(contacts[mover],at,size)
            op,d,a,c,owned = program[at]
            assert op == "MOVE" and d == mover and not owned and d in cohort
            assert len(word["frames"][a])+1 == rank == len(word["frames"][chart])
            assert len(word["frames"][c])-1 == rank
            key = (at,mover,chart)
            state["windows"].append(dict(anchor=list(key),outer_charts=[a,c],cut_rank=rank,
                                         quotient_rep=rep,first=first,last=last))
            state["raw_cut_count"] += last-first+1
            for cut in range(first,last+1):
                if scheduled >= limit["raw_label_cuts"]:
                    raise TimeoutError("labelled cut cap")
                by_cut[cut].append(key)
                scheduled += 1
        state["stage"] = "literal banks"
        chart_of = word["initial"][:] + [None] * word["owned_fields"]
        banks = defaultdict(set)
        for r,chart in enumerate(word["initial"]):
            banks[chart].add(r)
        last_chart_touch = {}
        last_class = {}
        for t in range(size+1):
            if t % 128 == 0:
                state["first_unvisited_event"] = t
                if monotonic() >= deadline:
                    raise TimeoutError("bounded bank replay")
            for at,mover,chart in by_cut.get(t,()):
                state["visited_labelled_cuts"] += 1
                occupied = banks[chart]
                assert mover not in occupied
                peer = occupied & cohort
                if not peer or any(r >= n for r in occupied):
                    continue
                assert t != at
                state["eligible_raw_cuts"] += 1
                key = (at,mover,chart)
                token = (last_chart_touch.get(chart),t>at)
                if last_class.get(key) == token:
                    continue
                last_class[key] = token
                state["representatives"].append({
                    "key":[t,chart,mover,at],"public":sorted(occupied|{mover}),"owned":[],
                    "pivots":sorted(peer|{mover}),"previous_chart_contact":token[0],
                })
            if t == size:
                break
            op,d,*args = program[t]
            src = chart_of[d]
            if src is not None:
                last_chart_touch[src] = t
            if op == "MOVE":
                a,c,owned = args
                assert a == src and owned == (d >= n)
                banks[a].remove(d)
                banks[c].add(d)
                chart_of[d] = c
                last_chart_touch[c] = t
            elif op == "INIT":
                c = args[0]
                assert src is None and d >= n
                chart_of[d] = c
                banks[c].add(d)
                last_chart_touch[c] = t
            elif op == "CLEAR":
                assert src == args[0] and d >= n
                banks[src].remove(d)
                chart_of[d] = None
            else:
                assert src == args[-1] and op in ("ADD","SCALE","COPY")
                if op in ("ADD","COPY"):
                    assert chart_of[args[0]] == src
        assert chart_of == word["final"] + [None] * word["owned_fields"]
        assert state["visited_labelled_cuts"] == state["raw_cut_count"] == scheduled
        state["stage"] = "complete"
        state["first_unvisited_event"] = None
    except TimeoutError as exc:
        reason = str(exc)
    finally:
        alarm(0)
    print(json.dumps(dict(head=price["head"],pins=PINS,controls=controls(),limits=limit,
                          timeout=reason,**state),indent=2,sort_keys=True))
    if reason:
        raise SystemExit(2)


if __name__ == "__main__":
    signal(SIGALRM,stop)
    main()
