"""Pinned forward chart-207 census around the exact #7334 retimed block."""
from argparse import ArgumentParser
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from time import monotonic

PINS = {
    "price/PRICE.json": "b3c36d5a1d199a1e74f979d660fac295c55659a9d4edb70eaef541095670323b",
    "inputs/7314-WORD.json.gz": "c404b9b61220e6cf740d85276df2828bbb4a9d68a4d44b5e283f8d96f78c0fd9",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/IDENTITIES.json": "f4d3f6ca2d87f8cd68c01ac9f77b69bd5a796f92bd567cea8afe3ac7c72e8e4b",
}
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
FRAME = 207
PROTECTED = {319, 863, 1355, 1568}
CAP = 128
SECONDS = 18


def read(root, name):
    raw = (root / name).read_bytes()
    if sha256(raw).hexdigest() != PINS[name]:
        raise ValueError(f"changed input: {name}")
    def unique(pairs):
        result = dict(pairs)
        if len(result) != len(pairs):
            raise ValueError("duplicate JSON key")
        return result
    return json.loads(decompress(raw) if name.endswith(".gz") else raw, object_pairs_hook=unique)


def span(basis):
    vectors = {0}
    for v in basis:
        assert v not in vectors
        vectors |= {v ^ x for x in vectors}
    return vectors


def walk(word, interval, members, deadline, frame=FRAME):
    n = word["public"]
    tape = word["program"]
    charts = word["initial"].copy() + [None] * word["owned_fields"]
    lo, hi = interval
    assert 0 <= lo <= hi <= len(tape)
    rows = []
    last = None
    for k in range(len(tape)+1):
        if k % 256 == 0 and monotonic() >= deadline:
            return {"complete": False, "rows": rows, "unvisited_from_clock": k}
        if lo <= k <= hi:
            bank = [r for r, f in enumerate(charts[:n]) if f == frame]
            rows.append(dict(cut=k, public_bank=bank, pivots=sorted(members.intersection(bank)),
                             owned_bank=[r for r in range(n,len(charts)) if charts[r]==frame],
                             representative=k==lo or last))
        if k == len(tape):
            break
        op,d,*a = tape[k]
        if op == "MOVE":
            x,y,owned = a
            assert charts[d]==x and owned==(d>=n)
            charts[d]=y
            last = frame in (x,y)
        elif op in ("INIT","CLEAR"):
            f, = a
            assert d>=n and charts[d]==(None if op=="INIT" else f)
            charts[d]=f if op=="INIT" else None
            last = f==frame
        else:
            assert op in ("ADD","COPY","SCALE") and Fraction(a[-2]) and charts[d]==a[-1]
            if op!="SCALE":
                assert charts[a[0]]==a[-1] and a[0]!=d
            assert op!="COPY" or d>=n
            last = a[-1]==frame
    assert charts==word["final"]+[None]*word["owned_fields"]
    return {"complete": True,"rows": rows,"unvisited_from_clock": None}


def controls():
    word = dict(public=2,owned_fields=1,initial=[0,0],final=[2,2],program=[
        ["MOVE",0,0,1,False],["MOVE",1,0,1,False],["INIT",2,1],
        ["COPY",2,1,"1",1],["CLEAR",2,1],
        ["MOVE",0,1,2,False],["MOVE",1,1,2,False]])
    s=walk(word,(0,7),{0},float("inf"),1)
    assert [r["cut"] for r in s["rows"] if r["pivots"]]==[1,2,3,4,5]
    assert s["rows"][4]["public_bank"]==[0,1] and s["rows"][4]["owned_bank"]==[2]
    assert not s["rows"][7]["public_bank"]
    return ["pre-event cuts and both MOVE endpoints", "owned row separated from public bank"]


def main():
    p=ArgumentParser()
    p.add_argument("root", type=Path)
    p.add_argument("--controls-only",action="store_true")
    a=p.parse_args()
    check=controls()
    if a.controls_only:
        print(json.dumps(check))
        return
    d=a.root
    price=read(d,"price/PRICE.json")
    assert price["head"]==HEAD and not price["paid_delta"]
    assert price["productive_delta"]=={"1":17,"8":17,"9":-17}
    meta=read(d,"inputs/IDENTITIES.json")
    old,new=(read(d,f"inputs/{name}-WORD.json.gz") for name in (7314,7334))
    n=new["public"]
    assert n==old["public"]==1501 and new["initial"]==old["initial"] and new["final"]==old["final"]
    assert new["frames"]==old["frames"] and new["live"]==old["live"] and new["hosted"]==old["hosted"]
    ranks=[len(new["frames"][f]) for f in (3,207,127)]
    assert ranks==[0,8,9]
    assert span(new["frames"][3])<span(new["frames"][207])<span(new["frames"][127])
    main=set(new["live"]) | {r+112 for r in new["live"]}
    main.update(new["hosted"]["X2"],new["hosted"]["Y2"])
    cohort={i for i,(start,end) in enumerate(zip(new["initial"],new["final"],strict=True))
            if (start,end)==(3,127) and i not in main | PROTECTED}
    members=cohort.intersection(meta["roles"])
    assert len(members)<=price["geometry_stock_cap"]
    body=meta["body_clocks"]
    nlo,nhi=meta["literal_candidate_clocks"]
    o_interval=(min(body),max(max(body)+1,meta["window"][1]))
    deadline=monotonic()+SECONDS
    before=walk(old,o_interval,members,deadline)
    after=walk(new,(nlo,nhi+1),members,deadline)
    signatures={tuple(r["public_bank"]) for r in before["rows"]}
    keys=[[r["cut"],207,q] for r in after["rows"] if r["representative"] for q in r["pivots"]]
    out=dict(head=HEAD,price_sha256=PINS["price/PRICE.json"],pins=PINS,controls=check,
             endpoint_cohort=sorted(cohort),affected_candidates=sorted(members),
             old_interval=list(o_interval),new_interval=[nlo,nhi+1],old=before,new=after,
             new_bank_signatures=sum(tuple(r["public_bank"]) not in signatures for r in after["rows"] if r["representative"]),
             representative_keys=keys[:CAP],unvisited_keys=keys[CAP:],
             complete=before["complete"] and after["complete"] and len(keys)<=CAP,
             cap=CAP,seconds=SECONDS)
    print(json.dumps(out,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
