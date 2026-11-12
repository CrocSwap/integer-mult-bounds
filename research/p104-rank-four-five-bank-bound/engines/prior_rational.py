"""Exact two-sided unit pairing on the structurally selected banks."""
from collections import Counter
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
import sys
from time import monotonic

from_path=Path(sys.argv[1])
PRICE="b4bf8e00a8289f03b1da731fb3ab563a771d88d875e0da73acf70954df2f2c56"
WORD="4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"
PINS={"inputs/paired_rank.py":"d1b7c34e6f8c8a7b810414762015e6e300a8292422af66ff671ae09741141f09",
      "inputs/paired_support.py":"38c796cbe1a73f386177faf88cd53294d4b911f6cde7fd47cd9fcef3b558373f"}


def checked(rel,want):
    data=(from_path/rel).read_bytes()
    if sha256(data).hexdigest()!=want:
        raise ValueError(f"changed dependency: {rel}")
    return data


def main():
    price=json.loads(checked("price/PRICE.json",PRICE))
    geom=json.loads(checked("lead/GEOMETRY.json",sys.argv[2]))
    assert geom["status"]=="EXHAUSTED" and geom["price_sha256"]==PRICE
    word=json.loads(decompress(checked("inputs/7334-WORD.json.gz",WORD)))
    engines=[]
    for rel,pin in PINS.items():
        checked(rel,pin)
        engines.append(run_path(str(from_path/rel)))
    rank,solve=engines
    checks=solve["controls"]()
    cohort,_=solve["initial_groups"](word)
    assert set(price["endpoint_cohort"])==cohort
    select={row["key"][0]:row for row in geom["selected"]}
    assert len(select)==len(geom["selected"])<=24
    banks={k:row["public"] for k,row in select.items()}
    deadline=monotonic()+22
    forward=rank["side"](word,banks,cohort,deadline,False) if banks else {}
    open_banks={}
    results={}
    for t,rows in forward.items():
        p=len(rows)
        if any(c for _,c in rows):
            open_banks[t]=p
        else:
            results[t]=dict(status="no nonzero pure prefix",prefix_kernel=p)
    if open_banks:
        deadline=monotonic()+32
        continuation=[row["key"][0] for row in geom["selected"] if row["key"][0] in open_banks][:6]
        back=rank["side"](word,{t:banks[t] for t in continuation},cohort,deadline,True)
        for t,rows in back.items():
            if monotonic()>=deadline:
                break
            row=dict(prefix_kernel=open_banks[t],suffix_kernel=len(rows))
            if not any(c for _,c in rows):
                results[t]=row|dict(status="no nonzero pure suffix")
                continue
            try:
                w=solve["paired"](forward[t],rows,deadline)
            except solve["Capped"]:
                break
            if w is None:
                results[t]=row|dict(status="no unit pairing")
                continue
            results[t]=row|dict(status="exact rational support only",
                witness={k:{i:str(x) for i,x in v.items()} for k,v in w.items()})
    output=[select[t]|result for t,result in sorted(results.items())]
    pending=[select[t]["key"] for t in select if t not in results]
    hits=[r["key"] for r in output if r["status"]=="exact rational support only"]
    print(json.dumps(dict(head=price["head"],price_sha256=PRICE,geometry_sha256=sys.argv[2],word_sha256=WORD,
        controls=checks,cap=24,paired_cap=6,prefix_seconds=22,paired_seconds=32,
        prefix_survivors=[select[t]["key"] for t in open_banks],results=output,
        counts=Counter(x["status"] for x in output),rational_survivors=hits,selected_unresolved=pending,
        unvisited_structural_keys=geom["unvisited_keys"],
        status="CAPPED" if geom["unvisited_keys"] or pending else "EXHAUSTED"),indent=2,sort_keys=True))


if __name__=="__main__":
    main()
