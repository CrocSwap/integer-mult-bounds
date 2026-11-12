"""Exact rank-five catalogue and occupancy, keyed by endpoint cohort."""
from collections import Counter, defaultdict
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT=Path(__file__).resolve().parents[1]
PINS={
    "lead/PRICE.json":"c04adfb199f6dbc25806d6062562c7d707b8fda8ad73f3ed818901248d25ffbf",
    "inputs/7334-WORD.json.gz":"4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
}


def checked(path):
    raw=(ROOT/path).read_bytes()
    if sha256(raw).hexdigest()!=PINS[path]:
        raise ValueError(f"changed dependency {path}")
    return raw


def span(frame):
    out={0}
    for v in frame:
        assert v not in out
        out|={x^v for x in out}
    return out


def stopped(*_):
    raise TimeoutError("hard geometry cap")


def score(row):
    return (-len(row["pivots"]),bool(row["owned"]),-len(row["public"]),row["key"])


def main():
    assert __debug__
    p=json.loads(checked("lead/PRICE.json"))
    raw=decompress(checked("inputs/7334-WORD.json.gz"))
    w=json.loads(raw)
    n=w["public"]
    tape=w["program"]
    assert len(tape)==p["event_cap"]==76466 and n==1501
    assert len(p["cohort"])==80 and len(p["groups"])==28
    signal(SIGALRM,stopped)
    alarm(20)
    deadline=monotonic()+18
    frames=w["frames"]
    spans=list(map(span,frames))
    groups=[]
    chart_groups=defaultdict(list)
    for g in p["groups"]:
        a,c=g["endpoints"]
        roles=set(g["roles"])
        assert len(frames[c])-len(frames[a])==5 and spans[a]<spans[c]
        assert all(w["initial"][r]==a and w["final"][r]==c for r in roles)
        dims={len(frames[a])+2,len(frames[a])+3}
        labels=[i for i,s in enumerate(spans) if len(frames[i]) in dims and spans[a]<s<spans[c]]
        groups.append(g|{"labels":labels})
        for b in labels:
            chart_groups[b].append((a,c,roles))
    active=w["initial"]+[None]*w["owned_fields"]
    occupied=defaultdict(set)
    for r,c in enumerate(active[:n]):
        if c in chart_groups:
            occupied[c].add(r)
    rows=[]
    visited=0
    reason=None
    def save(t,b):
        bank=occupied[b]
        for a,c,cohort in chart_groups[b]:
            pivots=bank&cohort
            if not pivots:
                continue
            if len(rows)>=p["bank_case_cap"]:
                raise TimeoutError("representative bank cap")
            rows.append(dict(key=[t,b,a,c],public=sorted(r for r in bank if r<n),
                             owned=sorted(r for r in bank if r>=n),pivots=sorted(pivots)))
    try:
        for b in sorted(occupied):
            save(0,b)
        for t,event in enumerate(tape):
            if t%128==0 and monotonic()>=deadline:
                raise TimeoutError("cooperative geometry cap")
            op,r,*a=event
            old=active[r]
            if op=="MOVE":
                assert a[0]==old and a[2]==(r>=n)
                new=a[1]
            elif op=="INIT":
                assert old is None and r>=n
                new=a[0]
            elif op=="CLEAR":
                assert old==a[0] and r>=n
                new=None
            else:
                assert op in ("ADD","COPY","SCALE") and old==a[-1]
                if op!="SCALE":
                    assert active[a[0]]==old and a[0]!=r
                new=old
            if old in chart_groups:
                occupied[old].remove(r)
            if new in chart_groups:
                occupied[new].add(r)
            active[r]=new
            for b in sorted({c for c in (old,new) if c in chart_groups}):
                save(t+1,b)
            visited=t+1
        assert active==w["final"]+[None]*w["owned_fields"]
    except TimeoutError as exc:
        reason=str(exc)
    finally:
        alarm(0)
    assert len(rows)==len({tuple(r["key"]) for r in rows})
    counts=Counter(tuple(r["key"][2:]) for r in rows)
    chosen=[]
    used_clocks,used_shapes=set(),set()
    selected_group=None
    if rows and reason is None:
        ordered=sorted(rows,key=score)
        selected_group=ordered[0]["key"][2:]
        for r in ordered:
            if r["key"][2:]!=selected_group:
                continue
            t,b,*_=r["key"]
            shape=(b,tuple(r["public"]),tuple(r["owned"]))
            if t not in used_clocks and shape not in used_shapes:
                chosen.append(r)
                used_clocks.add(t)
                used_shapes.add(shape)
                if len(chosen)==p["support_cap"]:
                    break
    print(json.dumps(dict(head=p["head"],pins=PINS,groups=[g|{"banks":counts[tuple(g["endpoints"])]} for g in groups],
        status="CAPPED" if reason else "EXHAUSTED",timeout=reason,visited_events=visited,bank_cap=p["bank_case_cap"],
        candidate_rows=rows,selected_group=selected_group,selected=chosen,
        caps={"modular":16,"exact":4,"geometry_seconds":20}),indent=2,sort_keys=True))


if __name__=="__main__":
    main()
