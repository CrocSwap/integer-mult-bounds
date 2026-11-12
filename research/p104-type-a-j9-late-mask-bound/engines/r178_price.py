"""Price one Type A late-mask transposition and its whole permutation ceiling."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from runpy import run_path

ROOT=Path(__file__).resolve().parent
PINS={"CALLER.json":"255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
      "R92-PRICE.json":"05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
      "pricing.py":"f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182"}


def main():
    assert __debug__
    raw={}
    for name,h in PINS.items():
        b=(ROOT/"inputs"/name).read_bytes()
        assert sha256(b).hexdigest()==h
        raw[name]=b
    c=loads(raw["CALLER.json"])
    base=loads(raw["R92-PRICE.json"])
    a=c["types"]["A"]
    assert len(a["ports"])==96 and a["roles"]==36
    counts=[(sum(r[2:10]),sum(r[10:])) for r in a["diagonal"]]
    assert all(r[:2]==[-1,0] for r in a["diagonal"])
    old=[1+8*(x+y) for x,y in counts]
    pair=(0,9)
    i,j=pair
    after=[1+8*(counts[i][0]+counts[j][1]),1+8*(counts[j][0]+counts[i][1])]
    assert [old[i],old[j],*after]==[137,9,73,73]
    best=[1+8*(x+y) for x,y in zip(sorted(x for x,_ in counts),sorted((y for _,y in counts),reverse=True),strict=True)]
    k=Q(base["old_crossing_upper"])
    cost=run_path(str(ROOT/"inputs/pricing.py"))["cost"]
    whole=Counter({d:96*n for d,n in Counter(best).items()})
    whole.subtract({d:96*n for d,n in Counter(old).items()})
    delta=Counter({73:192,137:-96,9:-96})
    stock=Counter({int(r):n for r,n in base["old_targets"].items()})
    stock.subtract({int(r):n for r,n in base["old_paid"].items()})
    stock.update(delta)
    gross=cost(delta,k)
    assert sum(r*n for r,n in delta.items())==sum(r*n for r,n in whole.items())==0
    assert 0<gross[0]<gross[1]<96
    print(dumps({"pins":PINS,"head":base["head"],"caller":base["caller_head"],"pair":pair,"cut":1741,
                 "pair_old_ranks":[old[i],old[j]],"pair_new_ranks":after,"signed_delta":delta,
                 "gross":gross,"complete_probe":cost(stock,Q(base["probe"])),
                 "whole_reverse_sorted_upper":cost(whole,k)[1],"whole_perm_cap":36,
                 "added_paid":0,"ordinary_macro_cap_pending_construction":384},default=str,sort_keys=True,indent=2))


if __name__=="__main__":
    main()
