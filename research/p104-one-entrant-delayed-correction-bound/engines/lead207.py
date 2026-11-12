"""Evaluate every frozen old dual on its single late bank entrant."""
from collections import defaultdict
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM,alarm,signal

R=Path(__file__).resolve().parent


def stop(*_):
    raise TimeoutError("20-second entrant-dual gate")


def main():
    assert __debug__
    signal(SIGALRM,stop)
    alarm(20)
    pins={}
    for line in (R/"PINS").read_text().splitlines():
        h,n=line.split()
        assert n not in pins and sha256((R/n).read_bytes()).hexdigest()==h
        pins[n]=h
    def get(n):
        return loads((R/"inputs"/n).read_bytes())
    c=get("R206.json")
    old={tuple(x["clocks"]):x["separator"] for name in ("R203.json","R204.json") for x in get(name)["records"]}
    pick=[r for r in c["results"] if r["cut"]==r["clocks"][-1]+2 and r["clocks"] not in c["span_attempted"]]
    assert len(pick)==12 and sum(Q(r["gross"][1]) for r in pick)<Q("2.177")
    w=loads(decompress((R/"inputs/7334-WORD.json.gz").read_bytes()))
    t=w["program"]
    f=run_path(str(R/"bank_gate.py"))
    add,scalar=f["add"],f["scalar"]
    n,m=w["public"],w["owned_fields"]
    rows=[{i:Q(1)} for i in range(n)]+[{} for _ in range(m)]
    charts=w["initial"]+[None]*m
    checks=defaultdict(list)
    for r in pick:
        checks[r["cut"]-1].append(r)
    results=[]
    for i,(op,r,*a) in enumerate(t[:max(checks)+1]):
        for case in checks.get(i,[]):
            key=tuple(case["clocks"])
            assert op=="MOVE" and r!=case["role"] and a[1]==case["chart"] and charts[r]==a[0]
            cert=old[key]
            x={int(j):Q(v) for j,v in cert["input"].items()}
            v=sum(rows[r].get(j,0)*a for j,a in x.items())
            results.append({"clocks":key,"entrant":r,"arrival":i,"value":v,
                            "old_target_value":cert["source_value"]})
        if op=="MOVE":
            assert charts[r]==a[0]
            charts[r]=a[1]
        elif op=="INIT":
            assert charts[r] is None and not rows[r]
            charts[r]=a[0]
        elif op=="CLEAR":
            assert charts[r]==a[0]
            charts[r]=None
            rows[r].clear()
        elif op=="SCALE":
            assert charts[r]==a[1] and scalar(a[0])
            rows[r]={j:x*scalar(a[0]) for j,x in rows[r].items()}
        else:
            j,k,c=a
            assert op in ("ADD","COPY") and charts[r]==charts[j]==c and r!=j
            assert op!="COPY" or not rows[r]
            add(rows[r],rows[j],scalar(k))
    assert len(results)==12
    alarm(0)
    print(dumps({"pins":pins,"case_cap":12,"seconds_cap":20,"records":results,
                 "unresolved":[r for r in results if r["value"]]},
                indent=2,sort_keys=True,default=str))


if __name__=="__main__":
    main()
