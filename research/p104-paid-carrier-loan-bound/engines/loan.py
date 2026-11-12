"""Bound one carrier loan while preserving both literal ownership itineraries."""
from collections import defaultdict
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from pathlib import Path
from time import monotonic
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "inputs/R137-RESULT.json": "a109deda97d3b4f5ceb52814a50186035ea44ac1bdaf47281f564dcc2da239db",
    "inputs/R139-PRICE.json": "b9d6d60d467af0269e5dd4d355607c8be5d35581da487f72a593ff775967fb57",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
}


def unique(items):
    out = dict(items)
    if len(out) != len(items):
        raise ValueError("duplicate key")
    return out


def raw(path):
    data = (ROOT / path).read_bytes()
    if sha256(data).hexdigest() != PINS[path]:
        raise ValueError(f"changed {path}")
    return data


def quote():
    anchors = json.loads(raw("inputs/R137-RESULT.json"), object_pairs_hook=unique)
    price = json.loads(raw("inputs/R139-PRICE.json"), object_pairs_hook=unique)
    assert (price["head"], price["caller"]) == (anchors["head"], anchors["caller"])
    assert len(anchors["records"]) == 47 and all(a["first_clock"] == a["move_clock"]+1 for a in anchors["records"])
    assert all(a["first_event"][0] in {"ADD", "SCALE"} for a in anchors["records"])
    raw("inputs/7334-WORD.json.gz")
    return dict(head=price["head"], caller=price["caller"], quotes=price["quotes"], pins=PINS,
                whole_gross_upper=price["whole_gross_upper"], fixed_target_upper=price["fixed_target_upper"],
                max_anchors=47, max_events=76466, max_cases=128, max_seconds=25, max_support_cases=8,
                max_support_seconds=30, max_builds=1)


def roles(event):
    return event[1:3] if event[0] in {"ADD", "COPY"} else event[1:2]


def candidates(program, records):
    contacts, endpoint_moves = defaultdict(list), defaultdict(list)
    preceding, following = {}, {}
    for t, e in enumerate(program):
        op = e[0]
        for r in set(roles(e)):
            past = contacts[r]
            if past:
                preceding[t,r] = past[-1]
                following[past[-1],r] = t
            past.append(t)
        if op == "MOVE":
            endpoint_moves[tuple(e[2:4])].append((t,e[1]))
    result = []
    for a in records:
        m, h, k = (a[field] for field in ("move_clock", "role", "first_clock"))
        ab = (a["chart_from"], a["chart_to"])
        assert program[m] == ["MOVE",h,*ab,True]
        assert program[k] == a["first_event"] and following[m,h] == k
        for t,f in endpoint_moves[ab]:
            if preceding.get((m,h),-1) < t < m and f != h and following.get((t,f),len(program)) >= k:
                result.append(dict(owner=h, anchor=m, carrier=f, carrier_move=t, first_use=k, charts=list(ab), rank=a["rank"]))
    return sorted(result,key=lambda r:(-r["rank"], r["anchor"]-r["carrier_move"],r["anchor"],r["carrier"]))


def screen(price):
    begin = monotonic()
    expected = json.dumps(price, indent=2, sort_keys=True)+"\n"
    assert (ROOT / "lead/PRICE.json").read_text() == expected
    program = json.loads(decompress(raw("inputs/7334-WORD.json.gz")), object_pairs_hook=unique)["program"]
    records = json.loads(raw("inputs/R137-RESULT.json"), object_pairs_hook=unique)["records"]
    assert len(program) == price["max_events"]
    control = [["INIT",3,1],["MOVE",2,1,2,False],["MOVE",3,1,2,True],["ADD",2,3,"1",2]]
    synthetic = [dict(move_clock=2,role=3,first_clock=3,first_event=control[3],chart_from=1,chart_to=2,rank=1)]
    assert len(candidates(control,synthetic)) == 1
    bad = control[:2]+[["SCALE",2,"-1",2]]+control[2:]
    assert not candidates(bad,[dict(synthetic[0],move_clock=3,first_clock=4)])
    found = candidates(program, records)
    assert monotonic()-begin < price["max_seconds"], "event cap expired before complete inventory"
    ranks = {k["anchor"]:k["rank"] for k in found}
    upper = sum(Fraction(price["quotes"][str(r)]["gross"][1]) for r in ranks.values())
    return dict(head=price["head"], events=len(program), anchors=len(records), topology_keys=len(found),
                distinct_supported_anchors=len(ranks), visited=found[:price["max_cases"]], unvisited=found[price["max_cases"]:],
                conditional_upper=str(upper), support_unresolved=found)


if __name__ == "__main__":
    assert __debug__
    p = quote()
    assert sys.argv[1:] in ([], ["--price-only"])
    print(json.dumps(p if sys.argv[1:] else screen(p), indent=2, sort_keys=True))
