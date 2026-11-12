"""Reconcile every R91 signed contact and binary span certificate."""

from argparse import ArgumentParser
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path

PINS={
    "lead":"dcc63db134df24725da177ba99b1df20fd3109379e2672291897442b43fcb6df",
    "reverse":"917ddb1a1af768333e9e6dd797f4f99704e8160ea9a8210128b9293e0a7166cc",
    "engine":"fe7922518020da505f25b4779382cc2e756d492b6c9bc09bc96aae4e9fddd006",
}


def get(path, key):
    raw=path.read_bytes()
    assert sha256(raw).hexdigest()==PINS[key]
    return raw


def main():
    assert __debug__
    p=ArgumentParser(description=__doc__)
    p.add_argument("lead",type=Path)
    p.add_argument("reverse",type=Path)
    args=p.parse_args()
    engine=Path(__file__).resolve().with_name("reverse_components.py")
    get(engine,"engine")
    rank=lambda vectors:len(run_basis(vectors))
    run_basis=run_path(str(engine))["pivots"]
    a,b=(loads(get(getattr(args,k),k)) for k in ("lead","reverse"))
    assert a["head"]==b["head"] and a["status"]==b["status"]=="EXHAUSTED"
    assert not any(x[k] for x in (a,b) for k in ("unvisited","unresolved","survivors"))
    assert a["counts"]==b["counts"]=={"high_intersection_too_small":11,"low_union_too_large":2}
    rows=[]
    for f,r in zip(a["outcomes"],b["outcomes"],strict=True):
        for k in ("key","roles","status"):
            assert f[k]==r[k]
        forward=f["contact"]
        clock_map=forward["current_ADD_clock_map"].copy()
        for role, old in forward["ancestor_MOVE_clocks"].items():
            for x,y in zip(old,forward["current_MOVE_clocks"][role],strict=True):
                clock_map[str(x)]=y
        assert clock_map==r["clock_map"]
        assert {k:v["literal"] for k,v in forward["ancestor_ADD_payload"].items()}==r["signed_ancestor_ADDs"]
        g,h=f["geometry"],r["geometry"]
        for k in ("low_union_rank","high_intersection_rank","old_rank","wanted_rank","new_paid_ranks"):
            assert g[k]==h[k], (f["key"],k)
        for name in ("low_union","high_intersection"):
            key=name+"_basis"
            assert rank(g[key]+h[key])==rank(g[key])==rank(h[key])
        rows.append({"key":f["key"],"ranks":[h["low_union_rank"],h["old_rank"],h["wanted_rank"],h["high_intersection_rank"]],
                     "status":f["status"],"signed_ADD_clocks":sorted(r["signed_ancestor_ADDs"],key=int)})
    assert len(rows)==13
    print(dumps({"input_sha256":PINS,"exact_key_agreements":13,"counts":b["counts"],"rows":rows,
                 "unresolved":0,"compatible_saving":"0"},sort_keys=True,indent=2))


if __name__=="__main__":
    main()
