"""Census all strictly nested carriers in the frozen owner contact intervals."""
from collections import defaultdict
from fractions import Fraction
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "inputs/R137-RESULT.json": "a109deda97d3b4f5ceb52814a50186035ea44ac1bdaf47281f564dcc2da239db",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "next/PRICE.json": "7f99902aaa6b47029f51fa0e10a59c677a78eca0e91b43c213d4f7e34cfececa",
}


def unique(items):
    obj = dict(items)
    if len(obj) != len(items):
        raise ValueError("duplicate JSON key")
    return obj


def checked(path):
    data = (ROOT / path).read_bytes()
    if sha256(data).hexdigest() != PINS[path]:
        raise ValueError(f"changed dependency {path}")
    return data


@cache
def span(rows):
    out = {0}
    for row in rows:
        assert row not in out
        out.update(row ^ other for other in tuple(out))
    return frozenset(out)


def census(word, anchors, cells, deadline):
    frames = [tuple(frame) for frame in word["frames"]]
    public = word["public"]
    state = word["initial"] + [None] * word["owned_fields"]
    program = word["program"]
    by_clock = {a["move_clock"]: a for a in anchors}
    by_source = defaultdict(list)
    for a in anchors:
        m, h, lo, mid = (a[k] for k in ("move_clock", "role", "chart_from", "chart_to"))
        assert program[m] == ["MOVE", h, lo, mid, True]
        assert a["first_clock"] == m+1 and program[m+1] == a["first_event"]
        assert abs(len(frames[mid])-len(frames[lo])) == a["rank"]
        if span(frames[lo]) < span(frames[mid]):
            by_source[lo].append((m, h, mid))
        else:
            assert span(frames[mid]) < span(frames[lo])
    latest, inside, receipt, keys = {}, defaultdict(list), [], []
    for u, event in enumerate(program):
        if u%128 == 0 and monotonic() >= deadline:
            return receipt, keys, u
        op, role, *args = event
        before = state[role]
        if u in by_clock:
            a = by_clock[u]
            last = latest[role]
            matches = [x for x in inside[u] if x["carrier_move"]>last]
            keys.extend(x for x in matches if x["nested"])
            receipt.append(dict(anchor=u,owner=role,last_contact=last,
                charts=[a["chart_from"],a["chart_to"]],
                source_moves=len(matches),nested_keys=sum(x["nested"] for x in matches)))
        if op == "MOVE":
            lo, hi, owned = args
            assert before==lo and owned==(role>=public)
            for m,h,mid in by_source[lo]:
                if not (u<m and h!=role and state[h]==lo):
                    continue
                info=dict(anchor=m,owner=h,carrier_move=u,carrier=role,carrier_owned=owned,
                          charts=[lo,mid,hi],nested=span(frames[mid])<span(frames[hi]))
                if info["nested"]:
                    r,s = len(frames[mid])-len(frames[lo]),len(frames[hi])-len(frames[mid])
                    bank = [i for i,chart in enumerate(state) if chart==mid]
                    info.update(ranks=[r,s],public_bank=[i for i in bank if i<public],
                                owned_bank=[i for i in bank if i>=public],price_upper=cells[r,s]["gross"][1])
                inside[m].append(info)
            state[role]=hi
        elif op == "INIT":
            assert before is None and role>=public
            state[role]=args[0]
        elif op == "CLEAR":
            assert before==args[0] and role>=public
            state[role]=None
        else:
            assert op in {"SCALE","ADD","COPY"} and before==args[-1]
            if op in {"ADD","COPY"}:
                assert args[0]!=role and state[args[0]]==before
        for i in (event[1:3] if op in {"ADD","COPY"} else [role]):
            latest[i]=u
    assert state==word["final"]+[None]*word["owned_fields"]
    assert len(receipt)==len(anchors)==47
    return receipt, keys, None


def main():
    assert __debug__
    begin=monotonic()
    prices=loads(checked("next/PRICE.json"),object_pairs_hook=unique)
    old=loads(checked("inputs/R137-RESULT.json"),object_pairs_hook=unique)
    assert prices["head"]==old["head"] and prices["caller"]==old["caller"]
    assert prices["paid"]==110519 and prices["productive"]==22461 and len(prices["cells"])==33
    assert span(())<span((1,))<span((1,2)) and not span((1,))<span((2,4))
    raw=decompress(checked("inputs/7334-WORD.json.gz"))
    assert sha256(raw).hexdigest()=="9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
    word=loads(raw,object_pairs_hook=unique)
    assert len(word["program"])==76466
    cells={(p["r"],p["s"]):p for p in prices["cells"]}
    anchors,keys,stop=census(word,old["records"],cells,begin+24)
    keys.sort(key=lambda x:(-Fraction(x["price_upper"]),x["anchor"],x["carrier_move"],x["carrier"]))
    by_anchor=defaultdict(list)
    for key in keys:
        by_anchor[key["anchor"]].append(Fraction(key["price_upper"]))
    upper=sum(max(rows) for rows in by_anchor.values())
    assert upper<=Fraction(prices["whole_gross_upper"])
    print(dumps(dict(head=old["head"],caller=old["caller"],pins=PINS,
        scoped_upper=str(upper),geometry_keys=len(keys),case_cap=128,seconds_cap=25,
        prioritized=keys[:128],unresolved_keys=keys[128:],anchors=anchors,
        first_unvisited_event=stop,unresolved_anchors=sorted({r["move_clock"] for r in old["records"]}-{r["anchor"] for r in anchors})),
        indent=2,sort_keys=True))
    if stop is not None or len(keys)>128:
        raise SystemExit(2)


if __name__=="__main__":
    main()
