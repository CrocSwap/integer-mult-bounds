"""Price every contiguous native J replacement using the exact two-sign rank floor."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM,alarm,signal

ROOT=Path(__file__).resolve().parents[1]
BIT=Q("0.00376669")
LOW=Q("0.00364665195644044790699554028334161")


def stop(*_):
    raise TimeoutError("60-second signed window census cap")


def main():
    assert __debug__
    pins={}
    for line in (ROOT/"receipts/R193-LEAD-PINS.txt").read_text().splitlines():
        h,p=line.split()
        assert p not in pins and sha256((ROOT/(p if p.startswith("inputs/") else "engines/"+p)).read_bytes()).hexdigest()==h
        pins[p]=h
    assert pins["inputs/PRICE.json"]=="1ad9852ecff0b3780770cbf4e500731e65214a9c438f8b1ed2c0cbe484d9b36b"
    f=run_path(str(ROOT/"engines/forward.py"))
    rank=run_path(str(ROOT/"engines/rank_gate.py"))["rank"]
    assert pins["inputs/CALLER.json"]==f["PINS"]["inputs/CALLER.json"]
    unit,apply=f["unit"],f["apply"]
    c=loads((ROOT/"inputs/CALLER.json").read_bytes())
    p=loads((ROOT/"inputs/PRICE.json").read_bytes())
    tape=c["events"]
    clocks=[i for i,e in enumerate(tape) if e[0]=="J"]
    queries=[i for i,e in enumerate(tape) if e[:2]==["A","QUERY"]]
    assert len(clocks)==17 and len(queries)==4 and len(tape)==4783
    assert len(c["types"]["A"]["ports"])==96 and len(c["types"]["B"]["ports"])==8
    assert not any(e[:2]==["A","IDLE_ODD"] for e in tape)
    starts=[0]+[j+1 for j in clocks[:-1]]
    ends=clocks[1:]+[len(tape)]
    cost=run_path(str(ROOT/"inputs/pricing.py"))["cost"]
    price=Counter({int(k):n for k,n in p["per_J_old_P"].items()})
    price.subtract({int(k):n for k,n in p["per_J_old_helper_T"].items()})
    price.subtract({8:400,1:16})
    k=Q(p["exact_crossing_upper"])
    credit=cost(price,k)
    point_positive={r:n for r,n in price.items() if n>0}
    point_negative={r:n for r,n in price.items() if n<0}
    whole_bound=cost(point_positive,LOW)[1]+cost(point_negative,BIT)[1]
    assert 0<credit[0]<=credit[1]<=whole_bound
    records=[]
    capped=False
    signal(SIGALRM,stop)
    alarm(60)
    try:
        h={}
        for cut in sorted(set(starts+ends)):
            prefix=tape[:cut]
            plus=[apply(prefix,unit(i),1) for i in range(36)]
            relative=[apply(prefix,col,-1,inverse=True) for col in plus]
            assert all(apply(prefix,col,-1)==v for col,v in zip(relative,plus,strict=True))
            h[cut]=relative
        for i in range(17):
            for j in range(i,17):
                a,b=starts[i],ends[j]
                delta=[[u-v for u,v in zip(x,y,strict=True)] for x,y in zip(h[b],h[a],strict=True)]
                rho=len(rank(delta))
                n=j-i+1
                q=sum(a<=t<b for t in queries)
                paid=max(0,rho-q)
                interval=[n*credit[0]-96*paid,n*credit[1]-96*paid]
                records.append({"hosts":[i+1,j+1],"clock_interval":[a,b],
                                "rank":rho,"retained_QUERY":q,"new_type_A_channels_lower":paid,
                                "optimistic_gross":interval,"uniform_price_upper":n*whole_bound-96*paid})
    except TimeoutError:
        capped=True
    finally:
        alarm(0)
    first=next((r for r in records if r["hosts"]==[1,3]),None)
    assert first is None or first["rank"]==6 and first["retained_QUERY"]==0
    visited={tuple(r["hosts"]) for r in records}
    unresolved=sorted({(i,j) for i in range(1,18) for j in range(i,18)}-visited)
    assert capped or len(records)==153
    print(dumps({"pins":pins,"head":p["head"],"caller":p["caller"],"window_cap":153,
                 "seconds_cap":60,"capped":capped,"per_host_before_new_A_channels":credit,
                 "per_host_uniform_upper":whole_bound,"records":records,
                 "positive_price_upper":[r["hosts"] for r in records if r["optimistic_gross"][1]>0],
                 "uniform_upper_positive":[r["hosts"] for r in records if r["uniform_price_upper"]>0],
                 "unvisited":unresolved},default=str,indent=2,sort_keys=True))
    if capped:
        raise SystemExit(2)


if __name__=="__main__":
    main()
