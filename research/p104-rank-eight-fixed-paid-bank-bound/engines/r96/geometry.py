"""Exact full-word occupied rank-four cochart bank census."""
from collections import defaultdict
from gzip import decompress
from hashlib import sha256
from pathlib import Path
from time import monotonic
import json
import sys

PRICE="a78be64c3e3ae8a0e532237c4dd3541aa9ad3fcbbc3c25d79c8a03fb7e07c525"
WORD="4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"


def checked(path,pin):
    b=path.read_bytes()
    if sha256(b).hexdigest()!=pin:
        raise ValueError(f"changed dependency: {path.name}")
    return b


def span(frame):
    result={0}
    for v in frame:
        assert v not in result
        result|={w^v for w in result}
    return result


def main():
    root=Path(sys.argv[1])
    price=json.loads(checked(root/"price/PRICE.json",PRICE))
    word=json.loads(decompress(checked(root/"inputs/7334-WORD.json.gz",WORD)))
    assert price["word_sha256"]==WORD and price["support_cap"]==16
    n=word["public"]
    cohort=set(price["cohort"])
    assert len(cohort)==15 and all(word["initial"][r]==3 and word["final"][r]==245 for r in cohort)
    spaces=list(map(span,word["frames"]))
    intermediate={i for i,w in enumerate(spaces) if len(w)==16 and spaces[3]<w<spaces[245]}
    chart=word["initial"]+[None]*word["owned_fields"]
    bank=defaultdict(set)
    for i,c in enumerate(chart):
        if c in intermediate:
            bank[c].add(i)
    rows=[]
    def save(t,c):
        roles=bank[c]
        pivots=roles&cohort
        if pivots:
            rows.append(dict(key=[t,c],public=sorted(i for i in roles if i<n),
                             owned=sorted(i for i in roles if i>=n),pivots=sorted(pivots)))
    for c in sorted(bank):
        save(0,c)
    until=monotonic()+18
    visited=0
    for t,e in enumerate(word["program"]):
        if t%128==0 and monotonic()>=until:
            break
        op,r,*args=e
        old=chart[r]
        if op=="MOVE":
            assert old==args[0] and args[2]==(r>=n)
            new=args[1]
        elif op=="INIT":
            assert old is None and r>=n
            new=args[0]
        elif op=="CLEAR":
            assert old==args[0] and r>=n
            new=None
        else:
            assert old==args[-1] and op in ("ADD","COPY","SCALE")
            if op in ("ADD","COPY"):
                assert chart[args[0]]==old
            new=old
        if old in intermediate:
            bank[old].remove(r)
        if new in intermediate:
            bank[new].add(r)
        chart[r]=new
        for c in sorted({v for v in (old,new) if v in intermediate}):
            save(t+1,c)
        visited=t+1
    complete=visited==len(word["program"])
    if complete:
        assert chart==word["final"]+[None]*word["owned_fields"]
    def score(r):
        return (bool(r["owned"]),len(r["pivots"])<2,len(r["public"])-len(r["pivots"]),
                len(r["public"]),r["key"])
    selected=[]
    bank_shapes=set()
    selected_clocks=set()
    if complete:
        for row in sorted(rows,key=score):
            shape=row["key"][1],tuple(row["public"]),tuple(row["owned"])
            if shape in bank_shapes or row['key'][0] in selected_clocks:
                continue
            bank_shapes.add(shape)
            selected_clocks.add(row['key'][0])
            selected.append(row)
            if len(selected)==16:
                break
    assert len({tuple(row["key"]) for row in rows})==len(rows)
    picked={tuple(r["key"]) for r in selected}
    print(json.dumps(dict(head=price["head"],word_sha256=WORD,price_sha256=PRICE,visited_events=visited,
        status="EXHAUSTED" if complete else "CAPPED",ranks=[4],bank_cap=16,
        eligible_bank_count=len(rows),eligible_chart_count=len({r["key"][1] for r in rows}),
        selected=selected,unvisited_keys=[r["key"] for r in rows if tuple(r["key"]) not in picked],
        all_representative_keys=[r["key"] for r in rows],scope="Representatives after each chart incident event; grouping for selection only."),
        indent=2,sort_keys=True))


if __name__=="__main__":
    main()
