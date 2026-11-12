"""Check the common non-chart3 coordinates of exact paid-descendant rows."""
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from signal import SIGALRM,alarm,signal

R=Path(__file__).resolve().parents[1]
PIN="d89a96743cd6162c9c301a79c6a51daa0ee04b7af2df7cd4af7d689454fb298a"


def stop(*_):
    raise TimeoutError("30-second shared descendant support cap")


def subtract(row, v, a):
    for j,x in v.items():
        z=row.get(j,0)-a*x
        if z:
            row[j]=z
        else:
            row.pop(j,None)


def echelon(vectors):
    piv={}
    for r in vectors:
        v=r.copy()
        for j,u in sorted(piv.items()):
            if j in v:
                subtract(v,u,v[j])
        if v:
            j=min(v)
            piv[j]={i:x/v[j] for i,x in v.items()}
    return piv


def main():
    assert __debug__
    signal(SIGALRM,stop)
    alarm(30)
    price=(R/"receipts/PRICE.json").read_bytes()
    assert sha256(price).hexdigest()==PIN
    price=loads(price)
    p=R/"inputs/R198.json"
    assert sha256(p.read_bytes()).hexdigest()==price["pins"]["inputs/R198.json"]
    old=loads(p.read_bytes())
    rows=old["records"]
    assert [r["key"] for r in rows]==price["keys"]
    vectors=[{int(j):Q(c) for j,c in r["row"].items() if int(j) not in dict(r["entry_chart_support"].get("3",[]))}
             for r in rows]
    assert all(len(v)==52 for v in vectors)
    assert len(echelon([{0:Q(1)},{0:Q(2)}]))==1
    assert len(echelon([{0:Q(1)},{1:Q(2)}]))==2
    records=[]
    for c in price["cases"]:
        if not c["price_positive"]:
            continue
        donors=echelon(vectors[i] for i in c["donors"])
        v=vectors[c["target"]].copy()
        for j,u in sorted(donors.items()):
            if j in v:
                subtract(v,u,v[j])
        first=min(v) if v else None
        records.append({**c,"donor_rank":len(donors),"survives":not v,
                        "first_residual":[first,v[first]] if v else None})
    assert len(records)==price["positive_count"]
    alarm(0)
    piv=echelon(vectors)
    print(dumps({"head":price["head"],"caller":price["caller"],"price_sha256":PIN,
                 "whole_exterior_rank":len(piv),"pivots":sorted(piv),"case_cap":247,
                 "seconds_cap":30,"all_subsets":len(price["cases"]),"tested_price_positive":len(records),
                 "records":records,"survivors":[r for r in records if r["survives"]]},
                indent=2,sort_keys=True,default=str))


if __name__=="__main__":
    main()
