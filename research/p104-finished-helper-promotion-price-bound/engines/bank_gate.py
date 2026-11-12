"""Check the exact final-chart bank for one paid public MOVE fusion."""
from fractions import Fraction as Q
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from signal import SIGALRM,alarm,signal

ROOT=Path(__file__).resolve().parent
PINS={"inputs/7334-WORD.json.gz":"4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
      "inputs/BANK.json":"4843481ba524572696ac5977182dfe55768c2746c8d5dbf59ee7ba7ee6feeffb"}
RAW="9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"


@cache
def scalar(text):
    return Q(text)


def timeout(*_):
    raise TimeoutError("20-second exact bank gate")


def add(a,b,c):
    for j,v in b.items():
        x=a.get(j,0)+c*v
        if x:
            a[j]=x
        else:
            a.pop(j,None)


def trace(w):
    n,m=w["public"],w["owned_fields"]
    rows=[{i:Q(1)} for i in range(n)]+[{} for _ in range(m)]
    charts=w["initial"]+[None]*m
    for i,(op,r,*a) in enumerate(w["program"][:48768]):
        if i==48766:
            assert charts[1561]==306
            source=rows[1561].copy()
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
            add(rows[r],rows[s],scalar(k))
    return source,{i:rows[i] for i,c in enumerate(charts) if c==127 and i!=1034}


def solve(target,bank):
    piv={}
    for i,row in sorted(bank.items(),key=lambda t:(len(t[1]),t[0])):
        v=row.copy()
        uses={i:Q(1)}
        # Eliminate any existing pivot, from lowest coordinate upward.
        while True:
            k=min((j for j in v if j in piv),default=None)
            if k is None:
                break
            row,history=piv[k]
            a=v[k]
            add(v,row,-a)
            add(uses,history,-a)
        if v:
            k=min(v)
            den=v[k]
            piv[k]=({j:x/den for j,x in v.items()},
                    {j:x/den for j,x in uses.items()})
    v=target.copy()
    answer={}
    for j,(row,history) in sorted(piv.items()):
        if j in v:
            a=v[j]
            add(v,row,-a)
            add(answer,history,a)
    if not v:
        check={}
        for j,c in answer.items():
            add(check,bank[j],c)
        assert check==target
        return len(piv),answer,None
    k=min(v)
    x={k:Q(1)}
    for j,(row,_) in sorted(piv.items(),reverse=True):
        a=-sum(v*x.get(i,0) for i,v in row.items() if i!=j)
        if a:
            x[j]=a
    def dot(row):
        return sum(c*x.get(j,0) for j,c in row.items())
    assert all(not dot(row) for row in bank.values())
    assert dot(target)==v[k]!=0
    return len(piv),None,{"input":x,"source_value":dot(target)}


def main():
    assert __debug__
    signal(SIGALRM,timeout)
    alarm(20)
    for p,h in PINS.items():
        assert sha256((ROOT/p).read_bytes()).hexdigest()==h
    raw=decompress((ROOT/"inputs/7334-WORD.json.gz").read_bytes())
    assert sha256(raw).hexdigest()==RAW
    w=loads(raw)
    price=loads((ROOT/"inputs/BANK.json").read_bytes())
    assert len(w["program"])==76466 and w["public"]==1501
    assert w["program"][48765:48768]==price["frozen_historical_bank_candidate"]["events"]
    assert Q(price["price_interval_17_calls"][0])>0
    source,bank=trace(w)
    assert len(bank)==760 and sorted(bank)==price["after_second_move_bank"]
    assert solve({1:Q(2)},{0:{1:Q(1)}})[1]=={0:Q(2)}
    assert solve({2:Q(1)},{0:{1:Q(1)}})[2]["source_value"]==1
    rank,coeff,separator=solve(source,bank)
    alarm(0)
    print(dumps({"head":price["head"],"caller":price["caller"],"pins":PINS,"source":source,
                 "bank_role_count":len(bank),"bank_rank":rank,"post_move_cut":48768,
                 "case_cap":1,"seconds_cap":20,"coefficients":coeff,"separator":separator,
                 "survives":coeff is not None},indent=2,sort_keys=True,default=str))


if __name__=="__main__":
    main()
