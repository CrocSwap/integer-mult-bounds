"""Rebuild the 31 existing-label occupancy decisions by a reverse chart walk."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from hashlib import sha256
from json import dumps
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT=Path(__file__).resolve().parent
GEOMETRY="e9f93f3271855012b2de705c70f186f78c31a369d28110e92c5f2ffadae209b3"
ENGINE="d55203b92c74ddf362fc3886f8620507d5c6dd8e05cf1b5b7528b78cb6219065"


def main():
    p=ArgumentParser(description=__doc__)
    for name in ("price","geometry","word"):
        p.add_argument("--"+name,required=True,type=Path)
    a=p.parse_args()
    assert __debug__
    tool=ROOT/"geometry.py"
    assert sha256(tool.read_bytes()).hexdigest()==ENGINE
    e=run_path(str(tool))
    def stop(*_):
        raise TimeoutError("20-second reverse occupancy cap")
    signal(SIGALRM,stop)
    alarm(20)
    deadline=monotonic()+18
    try:
        price=e["checked"](a.price,e["PRICE"])
        geom=e["checked"](a.geometry,GEOMETRY)
        assert price["head"]==geom["head"]==e["HEAD"] and geom["word_sha256"]==e["WORD"]
        assert geom["events_replayed"]==76466 and not geom["eligible"] and not geom["selected"]
        word=e["checked"](a.word,e["WORD"],True)
        n=word["public"]
        cohort=set(price["endpoint_cohort"])
        requests=defaultdict(list)
        raw=geom["raw_placements"]
        assert len(raw)==285
        for row in raw:
            for lab in row["labels"]:
                assert not lab["eligible"]
                requests[row["move_clock"]].append((row,lab["chart"]))
        assert sum(map(len,requests.values()))==31
        charts=list(word["final"])+[None]*word["owned_fields"]
        frames=word["frames"]
        rows=[]
        for t in range(len(word["program"]),-1,-1):
            if t%128==0 and monotonic()>=deadline:
                raise TimeoutError("reverse chart walk")
            for record,chart in requests.get(t,()):
                mover=record["mover"]
                literal=word["program"][t]
                assert literal[0]=="MOVE" and literal[1]==mover and literal[-1] is False
                a_chart,c_chart=literal[2:4]
                assert charts[mover]==a_chart
                low,mid,high=map(e["space"],(frames[a_chart],frames[chart],frames[c_chart]))
                assert low<mid<high and len(frames[chart])==record["rank"]
                rep=record["quotient_representative"]
                assert mid==low|{v^rep for v in low}
                public=[r for r in range(n) if charts[r]==chart]
                owned=[r for r in range(n,len(charts)) if charts[r]==chart]
                pivots=sorted(set(public)&cohort)
                assert mover not in public and (owned or not pivots)
                status=("empty_chart" if not public and not owned else "owned_guard"
                        if owned else "live_public_no_other_cohort")
                rows.append(dict(key=[t,chart,mover],old_move=literal,rank=record["rank"],
                                 chart_bases=[frames[a_chart],frames[chart],frames[c_chart]],
                                 public=public,owned=owned,other_eligible=pivots,status=status))
            if not t:
                break
            op,d,*args=word["program"][t-1]
            if op=="MOVE":
                low,high,flag=args
                assert charts[d]==high and flag==(d>=n)
                charts[d]=low
            elif op=="INIT":
                assert d>=n and charts[d]==args[0]
                charts[d]=None
            elif op=="CLEAR":
                assert d>=n and charts[d] is None
                charts[d]=args[0]
            else:
                assert charts[d]==args[-1] and op in ("ADD","COPY","SCALE")
                if op!="SCALE":
                    assert charts[args[0]]==args[-1] and args[0]!=d
        assert charts==word["initial"]+[None]*word["owned_fields"] and len(rows)==31
    finally:
        alarm(0)
    rows.sort(key=lambda r:r["key"])
    print(dumps(dict(head=e["HEAD"],geometry_sha256=GEOMETRY,engine_sha256=ENGINE,word_sha256=e["WORD"],
        counts=dict(Counter(r["status"] for r in rows)),cases=rows,eligible=0,unresolved_in_scoped_geometry=0),
        indent=2,sort_keys=True))


if __name__=="__main__":
    main()
