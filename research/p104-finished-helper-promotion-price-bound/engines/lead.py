"""Price one finished helper's paid chart promotion with productive credit."""
from collections import Counter
from fractions import Fraction as Q
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM,alarm,signal

R=Path(__file__).resolve().parent


def stop(*_):
    raise TimeoutError("20-second terminal-helper promotion price gate")


def main():
    assert __debug__
    signal(SIGALRM,stop)
    alarm(20)
    pins={}
    for line in (R/"PINS").read_text().splitlines():
        h,p=line.split()
        assert p not in pins and sha256((R/p).read_bytes()).hexdigest()==h
        pins[p]=h
    raw=decompress((R/"inputs/7334-WORD.json.gz").read_bytes())
    assert sha256(raw).hexdigest()=="9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
    w=loads(raw)
    def get(n):
        return loads((R/"inputs"/n).read_bytes())
    p=get("R92-PRICE.json")
    inv={tuple(x["clocks"]):x for x in get("INVENTORY.json")["records"]}
    cases={(48765,48766,48767):get("R200.json")["separator"]["input"]}
    for row in get("R201.json")["checked"]:
        cases[tuple(row["clocks"])]=row["decision"]["separating_covector"]
    for name in ("R203.json","R204.json"):
        for row in get(name)["records"]:
            cases[tuple(row["clocks"])]=row["separator"]["input"]
    assert len(cases)==119 and all(key in inv for key in cases)
    t=w["program"]
    frames=w["frames"]
    n=w["public"]
    last=[-1]*(n+w["owned_fields"])
    for i,e in enumerate(t):
        last[e[1]]=i
        if e[0] in ("ADD","COPY"):
            last[e[2]]=i
    live=set(w["live"])|{r+112 for r in w["live"]}|set(w["hosted"]["X2"])|set(w["hosted"]["Y2"])
    assert n-len(live)==1101
    @cache
    def span(chart):
        s={0}
        for bit in frames[chart]:
            assert bit not in s
            s|={v^bit for v in s}
        return s
    cost=run_path(str(R/"inputs/pricing.py"))["cost"]
    k=Q(p["old_crossing_upper"])
    @cache
    def quote(a,b,d,r):
        v=Counter()
        for size,mass in ((a,17),(b,17),(a+b,-17),(d,-17),(r,-17),(r+d,17)):
            v[size]+=mass
        assert sum(size*count for size,count in v.items())==0
        return cost({s:c for s,c in v.items() if c},k)
    priced=[]
    census=Counter()
    for key,dual in sorted(cases.items()):
        _,_,i=key
        c=inv[key]["chart"]
        a,b,_=inv[key]["ranks"]
        for j,q in sorted(dual.items(),key=lambda row:int(row[0])):
            r=int(j)
            assert Q(q)
            census["witness_coordinates"]+=1
            if r in live or last[r]>i:
                census["not_finished_proper_helper"]+=1
                continue
            start,old=w["initial"][r],w["final"][r]
            if not span(old)<span(c):
                census["no_strict_nested_destination"]+=1
                continue
            assert span(start)<span(old)
            d=len(frames[c])-len(frames[old])
            grade=len(frames[old])-len(frames[start])
            assert d>0 and grade>0
            gain=quote(a,b,d,grade)
            priced.append({"clocks":key,"role":r,"last_role_contact":last[r],"charts":[start,old,c],
                           "old_helper_rank":grade,"new_helper_rank":grade+d,
                           "added_paid_rank":d,"gross":gain})
    assert sum(census[k] for k in ("not_finished_proper_helper","no_strict_nested_destination"))+len(priced)==census["witness_coordinates"]
    alarm(0)
    print(dumps({"pins":pins,"head":p["head"],"caller":p["caller_head"],"cases":119,
                 "seconds_cap":20,"counts":census,"priced":priced,
                 "positive":[r for r in priced if r["gross"][0]>0]},
                default=str,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
