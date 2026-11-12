"""Classify proven equivalences of the 19 frozen rank-five bank keys."""
from collections import defaultdict
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from signal import SIGALRM, alarm, signal
import sys
from time import monotonic

PINS = {
    "lead/PRICE.json": "c04adfb199f6dbc25806d6062562c7d707b8fda8ad73f3ed818901248d25ffbf",
    "lead/GEOMETRY.json": "c2a4406cf7130a819189e8ceefb4bb6e09edd392eb56820f9fcadb0e9415ef4e",
    "lead/MODULAR.json": "118fda832ce46e8e52e88a321bf0fcfd182b24e358756c956bc29a1944ec62ff",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
}


def checked(root):
    items = {}
    for path,pin in PINS.items():
        raw = (root/path).read_bytes()
        if sha256(raw).hexdigest()!=pin:
            raise ValueError(f"changed dependency {path}")
        items[path] = json.loads(decompress(raw) if path.endswith(".gz") else raw)
    return items


def harmless(event,chart,public):
    op,d,*args = event
    if op=="MOVE":
        return chart not in args[:2]
    if op in ("INIT","CLEAR"):
        return chart!=args[0]
    assert op in ("ADD","COPY","SCALE")
    if chart!=args[-1]:
        return True
    if op=="COPY":
        return False
    assert Fraction(args[-2])
    return op=="SCALE" or (d<public)==(args[0]<public)


def stop(*_):
    raise TimeoutError("hard alias classification cap")


def main():
    assert __debug__ and sys.version_info[:2]==(3,12)
    assert harmless(["ADD",4,3,"-1",6],6,5)
    assert not harmless(["ADD",4,5,"-1",6],6,5)
    assert not harmless(["MOVE",4,6,8,False],6,5)
    signal(SIGALRM,stop)
    alarm(20)
    deadline = monotonic()+18
    classes,links,unvisited = [],[],[]
    passed = set()
    reason = None
    try:
        docs = checked(Path(sys.argv[1]))
        price,geom,prefix,word = docs.values()
        assert price["head"]==geom["head"]==prefix["head"]
        group=geom["selected_group"]
        assert group==[3,241]
        rows=[r for r in geom["candidate_rows"] if r["key"][2:]==group]
        assert len(rows)==19 and len(word["program"])==76466
        assert len(prefix["results"])==11 and all(r["status"]=="prefix exclusion" for r in prefix["results"])
        passed = {tuple(r["key"]+group) for r in prefix["results"]}
        grouped = defaultdict(list)
        for r in rows:
            grouped[r["key"][1]].append(r)
        assert len(grouped)==2
        unvisited = [r["key"] for r in rows]
        for chart,bank_rows in sorted(grouped.items()):
            last = None
            for row in sorted(bank_rows,key=lambda r:r["key"]):
                if monotonic()>=deadline:
                    raise TimeoutError("cooperative alias classification cap")
                key = row["key"]
                ok = False
                if last is not None:
                    t0,t1 = last["key"][0],key[0]
                    same = all(last[f]==row[f] for f in ("public","owned","pivots"))
                    blockers = [j for j in range(t0,t1) if not harmless(word["program"][j],chart,word["public"])]
                    ok = same and not blockers
                    links.append({"left":last["key"],"right":key,"same_bank":same,"blockers":blockers,"alias":ok})
                if not ok:
                    classes.append([])
                classes[-1].append(key)
                unvisited.remove(key)
                last=row
        assert sum(map(len,classes))==19 and len(links)==17
    except TimeoutError as exc:
        reason = str(exc)
    finally:
        alarm(0)
    results = [{"keys":keys,"reuses":sorted(k for k in keys if tuple(k) in passed)} for keys in classes]
    print(json.dumps({"pins":PINS,"cap_cases":19,"cap_seconds":20,"classes":results,
                      "links":links,"unvisited":unvisited,"timeout":reason},indent=2,sort_keys=True))
    if reason:
        raise SystemExit(2)


if __name__=="__main__":
    main()
