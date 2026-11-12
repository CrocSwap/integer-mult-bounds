"""Propagate independent owned-MOVE defect tags through the full word."""
from fractions import Fraction as Q
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
import sys
from time import monotonic

ROOT=Path(__file__).resolve().parents[1]
PINS={
    "inputs/7334-WORD.json.gz":"4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/PRICE.json":"1e8270d9a48728327f7eab9610a272fbb8ef09518dc4ddc5ceb573be00ae2beb",
    "inputs/RESULT.json":"a109deda97d3b4f5ceb52814a50186035ea44ac1bdaf47281f564dcc2da239db",
}


def unique(items):
    x=dict(items)
    if len(x)!=len(items):
        raise ValueError("duplicate JSON key")
    return x


def read(path):
    raw=(ROOT/path).read_bytes()
    if sha256(raw).hexdigest()!=PINS[path]:
        raise ValueError(f"changed dependency {path}")
    return raw


def quote():
    p,r=(loads(read(path),object_pairs_hook=unique) for path in ("inputs/PRICE.json","inputs/RESULT.json"))
    assert p["head"]==r["head"] and p["caller"]==r["caller"]
    assert r["counts"]=={"outside donor span":47}
    assert all(row["row"] and Q(row["separator_value"]) for row in r["records"])
    keys={row["move_clock"]:[row["role"],row["chart_from"],row["chart_to"],row["rank"]] for row in r["records"]}
    assert len(keys)==47 and all(Q(p["one"][str(a[3])]["complete_probe"][0])>0 for a in keys.values())
    return dict(head=p["head"],caller=p["caller"],pins=PINS,keys=keys,quotes=p["one"],
                whole_gross_upper=p["whole_gross_upper"],fixed_target_upper=p["fixed_target_upper"],
                event_cap=76466,case_cap=47,seconds_cap=25)


@cache
def scalar(value):
    return Q(value)


def axpy(dst,src,q):
    for j,c in src.items():
        value=dst.get(j,0)+q*c
        if value:
            dst[j]=value
        else:
            dst.pop(j,None)


def sweep(w,p):
    n=w["public"]
    state=w["initial"]+[None]*w["owned_fields"]
    values=[{} for _ in state]
    guards={}
    visited=set()
    deadline=monotonic()+22
    assert len(w["program"])==p["event_cap"]
    for t,(op,r,*a) in enumerate(w["program"]):
        if t%128==0 and monotonic()>=deadline:
            return dict(first_unvisited_event=t,unresolved=sorted(p["keys"]))
        c=state[r]
        if op=="MOVE":
            assert a[0]==c and a[2]==(r>=n)
            state[r]=a[1]
            if a[2]:
                q=abs(len(w["frames"][a[0]])-len(w["frames"][a[1]]))
                assert p["keys"][t]==[r,a[0],a[1],q]
                assert t not in values[r]
                values[r][t]=Q(1)
                visited.add(t)
        elif op=="INIT":
            assert r>=n and c is None and not values[r]
            state[r]=a[0]
        elif op=="CLEAR":
            assert r>=n and c==a[0]
            state[r]=None
            values[r]={}
        elif op=="SCALE":
            assert c==a[-1] and scalar(a[0])
            values[r]={j:q*scalar(a[0]) for j,q in values[r].items()}
        else:
            s,scale,chart=a
            assert s!=r and state[s]==c==chart and op in {"COPY","ADD"}
            if op=="COPY":
                assert r>=n
                guards[t]=values[r].copy()
                values[r]={}
            axpy(values[r],values[s],scalar(scale))
    assert state==w["final"]+[None]*w["owned_fields"] and visited==set(p["keys"])
    assert not any(values[n:])
    columns={t:[] for t in visited}
    for label,source in (("public",enumerate(values[:n])),("COPY guard",guards.items())):
        for coordinate,vec in source:
            for t,value in vec.items():
                columns[t].append([label,coordinate,str(value)])
    return dict(first_unvisited_event=None,unresolved=[],COPY_clocks=sorted(guards),
        rows=[dict(move_clock=t,key=p["keys"][t],observable_count=len(v),first=v[0] if v else None)
              for t,v in sorted(columns.items())],
        survivors=[t for t,v in sorted(columns.items()) if not v])


def controls():
    out={}
    axpy(out,{4:Q(3)},Q(2))
    axpy(out,{4:Q(1)},Q(-6))
    assert not out
    axpy(out,{4:Q(1)},Q(1))
    assert out=={4:Q(1)}
    return ["exact cancellation","wrong coefficient exposes a tag"]


def main():
    assert __debug__
    p=quote()
    if sys.argv[1:]==["--price-only"]:
        print(dumps(p,indent=2,sort_keys=True))
        return
    assert not sys.argv[1:]
    raw=decompress(read("inputs/7334-WORD.json.gz"))
    assert sha256(raw).hexdigest()=="9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
    out=sweep(loads(raw,object_pairs_hook=unique),p)
    print(dumps(dict(head=p["head"],caller=p["caller"],pins=PINS,controls=controls(),**out),
                indent=2,sort_keys=True))
    if out["unresolved"]:
        raise SystemExit(2)


if __name__=="__main__":
    main()
