"""Exact normalized row support for one saved-entry owned MOVE replacement."""
from fractions import Fraction as Q
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from signal import SIGALRM,alarm,signal

ROOT=Path(__file__).resolve().parent
ZIP="4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"
RAW="9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
PRICE="d7d91fd120f93eed730a4bd655545d64b68752169c06f88db8ef468bedfc2afc"


@cache
def scalar(a):
    return Q(a)


def stop(*_):
    raise TimeoutError("25-second rank-one-destination census")


def main():
    assert __debug__
    signal(SIGALRM,stop)
    alarm(25)
    raw=(ROOT/"inputs/7334-WORD.json.gz").read_bytes()
    p=(ROOT/"CENSUS.json").read_bytes()
    assert sha256(raw).hexdigest()==ZIP and sha256(p).hexdigest()==PRICE
    raw=decompress(raw)
    assert sha256(raw).hexdigest()==RAW
    w=loads(raw)
    t=w["program"]
    n,m=w["public"],w["owned_fields"]
    assert (n,m,len(t))==(1501,68,76466)
    assert t[38967]==["MOVE",146,3,365,False]
    assert t[39811]==["MOVE",1503,520,595,True] and t[39828]==["INIT",1504,591]
    assert not any(e[1]==1504 or (e[0] in ("ADD","COPY") and e[2]==1504) for e in t[:39828])
    assert len(w["frames"][3])==0 and len(w["frames"][595])==1
    assert sum(x==3 for x in w["initial"])==1060
    rows=[{i:Q(1)} for i in range(n)]+[{} for _ in range(m)]
    charts=w["initial"]+[None]*m
    keys={row[0]:row for row in loads(p)["census"]}
    records=[]
    for i,(op,r,*a) in enumerate(t[:max(keys)+1]):
        if i in keys:
            key=keys[i]
            _,owner,source,dest,rank=key
            assert t[i]==["MOVE",owner,source,dest,True] and charts[owner]==source
            group={}
            for j,c in sorted(rows[owner].items()):
                group.setdefault(w["initial"][j],[]).append([j,str(c)])
            missing=[(c,j,x) for c,g in sorted(group.items()) if c not in (3,dest) for j,x in g]
            records.append({"key":key,"row":rows[owner].copy(),"entry_chart_support":group,
                            "outside_count":len(missing),"first_outside":missing[0] if missing else None})
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
            assert charts[r]==a[1]
            rows[r]={j:x*scalar(a[0]) for j,x in rows[r].items()}
        else:
            s,k,c=a
            assert op in ("ADD","COPY") and charts[r]==charts[s]==c and r!=s
            assert op!="COPY" or not rows[r]
            k=scalar(k)
            for j,x in rows[s].items():
                y=rows[r].get(j,Q(0))+k*x
                if y:
                    rows[r][j]=y
                else:
                    rows[r].pop(j,None)
    assert len(records)==8 and sum(r["key"][0]==39811 for r in records)==1
    alarm(0)
    print(dumps({"head":loads(p)["head"],"pins":{"word_gzip":ZIP,"word_payload":RAW,"census":PRICE},
                 "source_coordinates":1501,"case_cap":8,"seconds_cap":25,"records":records,
                 "survivors":[r["key"] for r in records if not r["outside_count"]]},
                indent=2,sort_keys=True,default=str))


if __name__=="__main__":
    main()
