"""Test paid stage-17 retirement via its exact body-sign capacity."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

ROOT=Path(__file__).resolve().parent
IDLES=(4646,4660)
HOST=4691


def stop(*_):
    raise TimeoutError("20-second stage-17 rank-capacity gate")


def main():
    assert __debug__
    signal(SIGALRM,stop)
    alarm(20)
    pins={}
    for line in (ROOT/"PINS").read_text().splitlines():
        sha,name=line.split()
        assert name not in pins and sha256((ROOT/name).read_bytes()).hexdigest()==sha
        pins[name]=sha
    assert pins["inputs/CALLER.json"]=="255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
    c=loads((ROOT/"inputs/CALLER.json").read_bytes())
    p=loads((ROOT/"inputs/R92-PRICE.json").read_bytes())
    e=c["events"]
    b=c["types"]["B"]
    assert len(e)==4783 and b["offset"]==b["roles"]==36 and len(b["ports"])==8
    assert e[HOST]==["J",17,[17,0,18,35],[36,37,"-1","1/2"]]
    assert all(e[i]==["B","IDLE_ONE",36,[17]] for i in IDLES)
    assert [i for i,x in enumerate(e) if (x[0]=="B" and x[1] in ("IDLE_ONE","IDLE_ODD") and 17 in x[3]) or x[:2]==["J",17]]==[*IDLES,HOST]
    f=run_path(str(ROOT/"inputs/stage17.py"))
    axis,apply,gate=(f[n] for n in ("axis","apply","gate"))
    steps=[(i,gate(op)) for i,op in enumerate(e)]
    diagonal=[]
    stage_cols=[i for i,d in enumerate(b["diagonal"]) if d[18]]
    assert stage_cols==[0,1,16,17]
    for i in range(36):
        for sign in (1,-1):
            v=axis(i)
            for clock,g in steps:
                apply(v,g)
                if clock in IDLES or clock==HOST:
                    v[0]*=sign
                if clock==HOST:
                    v[1]*=sign
            assert v==[x*(sign if i in stage_cols else 1) for x in axis(i)]
        if i in stage_cols:
            diagonal.append([i,"2"])
    records=[]
    cost=run_path(str(ROOT/"inputs/pricing.py"))["cost"]
    k=Q(p["old_crossing_upper"])
    for remove in ([*IDLES],[IDLES[0]],[IDLES[1]]):
        bound=4-len(remove)
        quote=cost(Counter({8:len(b["ports"])*len(remove)}),k)
        assert len(diagonal)>bound and quote[0]>0
        records.append({"deleted_clocks":remove,"rank_upper":bound,
                        "optimistic_raw":quote,"result":"EXCLUDED"})
    alarm(0)
    print(dumps({"pins":pins,"native":p["head"],"caller":p["caller_head"],
                 "ports":b["ports"],"cases":records,"runner_cap_seconds":20,
                 "basis_columns_per_body":36,"body_signs":[1,-1],
                 "target_difference_rank":len(diagonal),"diagonal":diagonal},
                default=str,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
