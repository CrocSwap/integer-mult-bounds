"""Exact projective screening of the 1081 two-site owned zeroings."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
from json import dumps,loads
from pathlib import Path
from runpy import run_path
import sys

ROOT=Path(__file__).resolve().parents[1]
PINS={
    "inputs/R137-PRICE.json":"1e8270d9a48728327f7eab9610a272fbb8ef09518dc4ddc5ceb573be00ae2beb",
    "inputs/R137-RESULT.json":"a109deda97d3b4f5ceb52814a50186035ea44ac1bdaf47281f564dcc2da239db",
    "inputs/R139-RESULT.json":"c81636f5fe4a5db1cb31220b451e400f2eb86af6dc3480235b7cfd34d09a8f40",
    "inputs/R92-PRICE.json":"05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/pricing.py":"f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}


def unique(items):
    out=dict(items)
    if len(out)!=len(items):
        raise ValueError("duplicate JSON key")
    return out


def read(path):
    raw=(ROOT/path).read_bytes()
    if sha256(raw).hexdigest()!=PINS[path]:
        raise ValueError(f"changed dependency {path}")
    return raw


def load(path):
    return loads(read(path),object_pairs_hook=unique)


def quote():
    a,b=load("inputs/R137-PRICE.json"),load("inputs/R92-PRICE.json")
    assert a["head"]==b["head"] and a["caller"]==b["caller_head"]
    stock=Counter({int(r):v for r,v in a["stock"].items()})
    ranks=sorted(stock.elements(),reverse=True)
    assert len(ranks)==47 and ranks[:2]==[6,5]
    read("inputs/pricing.py")
    cost=run_path(str(ROOT/"inputs/pricing.py"))["cost"]
    delta={r:17 for r in ranks[:2]}
    profile=Counter({int(r):n for r,n in b["old_targets"].items()})
    profile.subtract({int(r):n for r,n in b["old_paid"].items()})
    profile.update(delta)
    at,moon=Q(b["old_crossing_upper"]),Q(b["moonshot"])
    return dict(head=a["head"],caller=a["caller"],pins=PINS,case_cap=1081,max_edits=2,
        best_ranks=ranks[:2],paid=110485,productive=22461,
        max_gross_upper=str(cost(delta,at)[1]),fixed_target_complete_upper=str(cost(profile,moon)[1]))


def line(row):
    first=min(row,key=int)
    d=Q(row[first])
    return tuple((i,str(Q(x)/d)) for i,x in sorted(row.items(),key=lambda p:int(p[0])))


def screen(price):
    pre,post=load("inputs/R137-RESULT.json"),load("inputs/R139-RESULT.json")
    assert pre["head"]==post["head"]==price["head"] and not post["survivors"] and not post["unresolved"]
    row={r["move_clock"]:r for r in pre["records"]}
    col={r["move_clock"]:r for r in post["rows"]}
    assert len(row)==len(col)==47 and set(row)==set(col)
    assert all(col[t]["key"]==[a["role"],a["chart_from"],a["chart_to"],a["rank"]] for t,a in row.items())
    prefix={t:line(a["row"]) for t,a in row.items()}
    suffix={t:(a["observable_count"],tuple(a["first"][:2])) for t,a in col.items()}
    assert line({"2":"3","6":"-1"})==line({"2":"-6","6":"2"})
    assert line({"2":"3","6":"-1"})!=line({"2":"-6","6":"3"})
    cases=[]
    for i,j in combinations(sorted(row),2):
        if prefix[i]!=prefix[j]:
            decision="independent prefix rows"
        elif suffix[i]!=suffix[j]:
            decision="different guarded suffix support"
        else:
            decision="unresolved exact cross transport"
        cases.append(dict(clocks=[i,j],disposition=decision))
    assert len(cases)==price["case_cap"]
    return dict(head=price["head"],caller=price["caller"],pins=PINS,
        cases=cases,counts=Counter(r["disposition"] for r in cases),
        unresolved=[r["clocks"] for r in cases if r["disposition"]=="unresolved exact cross transport"])


if __name__=="__main__":
    assert __debug__
    p=quote()
    assert not sys.argv[1:] or sys.argv[1:]==["--price-only"]
    print(dumps(p if sys.argv[1:] else screen(p),indent=2,sort_keys=True))
