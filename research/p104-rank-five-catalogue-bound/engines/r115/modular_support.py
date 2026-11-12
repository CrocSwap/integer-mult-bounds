"""Reconstruct two-sided exterior minors for eleven frozen rank-five banks."""
from collections import Counter, defaultdict
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
from time import monotonic

ROOT = Path(__file__).resolve().parent
PINS = {
    "SELECTION.json":"a9d4cb3acf6ad489c631ae984665391fbacfc069a2ba8d4521970ed5dd46bb88",
    "lead/PRICE.json":"c04adfb199f6dbc25806d6062562c7d707b8fda8ad73f3ed818901248d25ffbf",
    "inputs/7334-WORD.json.gz":"4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/exterior_rank23.py":"7a20424d9a554795e89fd7288361529d8d1c91c256f529a63ef2d867a40bd31f",
    "inputs/reverse_engine.py":"751d5d0c4c665c8768ff69bcf939700d3be2f989c59f09af3a4aa14d3c1ebbc4",
}


def checked():
    output={}
    for path,digest in PINS.items():
        raw=(ROOT/path).read_bytes()
        if sha256(raw).hexdigest()!=digest:
            raise ValueError(f"changed dependency {path}")
        output[path]=raw
    return output


def reverse_side(word,rows,cohort,engine,reverse,deadline):
    n=word["public"]
    state=word["final"]+[None]*word["owned_fields"]
    cols=[{i:1} for i in range(n)]+[None]*word["owned_fields"]
    requests=defaultdict(list)
    for row in rows:
        requests[row["key"][0]].append(row)
    out={}
    tape=word["program"]
    for t in range(len(tape),-1,-1):
        if (t%128==0 or t in requests) and monotonic()>=deadline:
            break
        for row in requests.get(t,()):
            chart=row["key"][1]
            bank=[r for r in range(n) if state[r]==chart]
            owners=[r for r in range(n,len(state)) if state[r]==chart]
            assert bank==row["public"] and owners==row["owned"]
            out[tuple(row["key"])]=engine["exterior_minor"](bank,cols,cohort)
        if not t:
            assert state==word["initial"]+[None]*word["owned_fields"]
            break
        reverse["reverse_event"](tape[t-1],state,cols,n,engine["scalar"],engine["plus"],engine["P"])
    return out


def main():
    assert __debug__
    deadline=monotonic()+22
    docs=checked()
    price=json.loads(docs["lead/PRICE.json"])
    selection=json.loads(docs["SELECTION.json"])
    word=json.loads(decompress(docs["inputs/7334-WORD.json.gz"]))
    engine=run_path(str(ROOT/"inputs/exterior_rank23.py"))
    reverse=run_path(str(ROOT/"inputs/reverse_engine.py"))
    controls=reverse["controls"](engine)
    cohort=set(next(g["roles"] for g in price["groups"] if g["endpoints"]==selection["selected_group"]))
    assert cohort=={339,1101}
    rows=selection["selected"]
    assert len(rows)==11 and selection["head"]==price["head"]==engine["HEAD"]
    keys=[tuple(r["key"]) for r in rows]
    prefix,n=engine["sweep"](word,keys,cohort,deadline)
    for row in rows:
        k=tuple(row["key"])
        if k in prefix:
            assert all(row[f]==prefix[k][f] for f in ("public","owned","pivots"))
    open_rows=[r for r,k in zip(rows,keys,strict=True) if k in prefix and prefix[k]["disposition"]=="rank drop"]
    suffix=reverse_side(word,open_rows,cohort,engine,reverse,deadline) if open_rows else {}
    results=[]
    for row,k in zip(rows,keys,strict=True):
        f,s=prefix.get(k),suffix.get(k)
        if f and f["disposition"]=="excluded":
            status="prefix exclusion"
        elif s:
            status="suffix exclusion" if s["disposition"]=="excluded" else "dual drop"
        else:
            status="capped"
        results.append(row|dict(status=status,prefix=f,suffix=s))
    print(json.dumps(dict(head=price["head"],pins=PINS,prime=engine["P"],controls=controls,caps=selection["caps"],
        prefix_events=n,results=results,counts=Counter(r["status"] for r in results),unselected=selection["unselected"]),
        indent=2,sort_keys=True))


if __name__=="__main__":
    main()
