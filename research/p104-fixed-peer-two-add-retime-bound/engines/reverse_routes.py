"""Reconstruct the ten frozen R108 two-operand routes from reverse contacts."""
from argparse import ArgumentParser
from bisect import bisect_left
from collections import Counter, defaultdict
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import monotonic
import sys

ROOT = Path(__file__).resolve().parent
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
WORD = "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
PINS = {
    "inputs/STOCK.json": "2d256cbcc5fcbf2fb361c47b2d764c98e2f5ba1f734abb95e03be3935223ff28",
    "inputs/7334-WORD.json.gz": WORD,
}
EVENTS, ANCHORS, SECONDS = 76466, 10, 20


def unique(items):
    out = dict(items)
    if len(out) != len(items):
        raise ValueError("duplicate JSON key")
    return out


def authenticate(root, pins):
    result = {}
    for path, expected in pins.items():
        data = (root / path).read_bytes()
        if sha256(data).hexdigest() != expected:
            raise ValueError(f"changed dependency: {path}")
        result[path] = data
    return result


def operands(event):
    op, dst, *args = event
    return (dst,args[0]) if op in ("ADD","COPY") else (dst,)


def neighboring(contacts, clock):
    i = bisect_left(contacts,clock,key=lambda pair:pair[0])
    assert i < len(contacts) and contacts[i][0] == clock
    before = contacts[i-1] if i else None
    after = contacts[i+1] if i+1 < len(contacts) else None
    return before, after


def decode_route(before, after, role, chart, dimensions):
    result = dict(role=role, previous=before, next=after)
    if before is None or after is None:
        return result | dict(status="missing adjacent contact")
    f, first = before
    g, second = after
    if first[0] != "MOVE" or second[0] != "MOVE":
        return result | dict(status="adjacent contact is not MOVE")
    assert first[1] == second[1] == role and not first[4] and not second[4]
    a,b = first[2:4]
    bb,c = second[2:4]
    assert b == bb == chart
    p,q = dimensions[b]-dimensions[a], dimensions[c]-dimensions[b]
    assert p>0 and q>0
    return result | dict(status="both paid MOVEs adjacent", clocks=[f,g], charts=[a,b,c], ranks=[p,q])


def controls():
    move_in=["MOVE",1,4,5,False]
    add=["ADD",2,1,"-1/2",5]
    move_out=["MOVE",1,5,7,False]
    assert operands(add)==(2,1)
    assert operands(["COPY",7,1,"1",5])==(7,1)
    before,after=neighboring([(1,move_in),(4,add),(7,move_out)],4)
    assert decode_route(before,after,1,5,list(range(8)))["ranks"]==[1,2]
    blocker=["ADD",3,1,"1",5]
    before,after=neighboring([(1,move_in),(3,blocker),(4,add),(7,move_out)],4)
    assert decode_route(before,after,1,5,list(range(8)))["status"]=="adjacent contact is not MOVE"
    return ["ADD/COPY source counts as a contact","immediate signed adjacent paid MOVE pair",
            "intervening read prevents route"]


def walk(word, targets, deadline, progress):
    tape = word["program"]
    public, owned = word["public"], word["owned_fields"]
    assert (len(tape),public,owned)==(EVENTS,1501,68)
    active = word["final"] + [None]*owned
    contacts=defaultdict(list)
    for t in range(EVENTS-1,-1,-1):
        progress["first_unvisited_event"]=t
        if t%128==0 and monotonic()>=deadline:
            raise TimeoutError("reverse event cap")
        op,r,*args=event=tape[t]
        if op=="MOVE":
            old,new,is_owned=args
            assert active[r]==new and is_owned==(r>=public)
            active[r]=old
        elif op in ("INIT","CLEAR"):
            assert r>=public and active[r]==(args[0] if op=="INIT" else None)
            active[r]=None if op=="INIT" else args[0]
        else:
            assert op in ("ADD","COPY","SCALE") and active[r]==args[-1]
            if op!="SCALE":
                assert r!=args[0] and active[args[0]]==active[r]
                assert op!="COPY" or r>=public
        for role in operands(event):
            if role in targets:
                contacts[role].append((t,event))
        progress["events_replayed"]+=1
    assert active==word["initial"]+[None]*owned
    progress["first_unvisited_event"]=None
    return {role:list(reversed(contacts[role])) for role in targets}


def examine(word, anchors, contacts, deadline, rows):
    dimensions=list(map(len,word["frames"]))
    for anchor in anchors:
        if monotonic()>=deadline:
            raise TimeoutError("anchor case cap")
        clock,event=anchor["contact"]
        first,last,mover=anchor["key"]
        peer=anchor["peer"]
        assert first<clock<last and event==word["program"][clock] and event[0]=="ADD"
        assert {mover,peer}==set(operands(event)) and mover!=peer and Fraction(event[-2])
        assert 0<=mover<word["public"] and 0<=peer<word["public"]
        chart=event[-1]
        moving=decode_route(*neighboring(contacts[mover],clock),mover,chart,dimensions)
        other=decode_route(*neighboring(contacts[peer],clock),peer,chart,dimensions)
        assert moving["status"]=="both paid MOVEs adjacent"
        assert moving["clocks"]==[first,last] and moving["charts"]==anchor["charts"]
        assert moving["ranks"]==anchor["ranks"][:2] and sum(moving["ranks"])==anchor["ranks"][2]
        if "clocks" in other:
            assert len(set(moving["clocks"]+other["clocks"]))==4
        rows.append(dict(key=anchor["key"],contact=anchor["contact"],peer=peer,moving=moving,other=other,
                         midpoint_chart=chart,midpoint_rank=dimensions[chart],status=other["status"]))


def main():
    p=ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,default=ROOT)
    p.add_argument("--controls-only",action="store_true")
    a=p.parse_args()
    assert __debug__ and sys.version_info[:2]==(3,12)
    checks=controls()
    if a.controls_only:
        print(dumps(checks))
        return

    def stop(*_):
        raise TimeoutError("hard 20-second topology cap")

    signal(SIGALRM,stop)
    alarm(SECONDS)
    deadline=monotonic()+18
    anchors,rows=[],[]
    progress=dict(events_replayed=0,first_unvisited_event=EVENTS-1)
    reason=None
    try:
        raw=authenticate(a.root,PINS)
        stock=loads(raw["inputs/STOCK.json"],object_pairs_hook=unique)
        assert stock["head"]==HEAD and stock["caller"]==CALLER
        anchors=stock["midpoint_rank_tilt"]["anchors"]
        assert len(anchors)==len({tuple(r["key"]) for r in anchors})==ANCHORS
        assert len({r["contact"][0] for r in anchors})==ANCHORS
        payload=decompress(raw["inputs/7334-WORD.json.gz"])
        assert sha256(payload).hexdigest()==PAYLOAD
        word=loads(payload,object_pairs_hook=unique)
        targets={r for row in anchors for r in (row["peer"],row["key"][2])}
        contacts=walk(word,targets,deadline,progress)
        examine(word,anchors,contacts,deadline,rows)
    except TimeoutError as exc:
        reason=str(exc)
    finally:
        alarm(0)
    assert len(rows)<=ANCHORS
    if reason is None:
        assert len(rows)==ANCHORS and progress["events_replayed"]==EVENTS
    print(dumps(dict(head=HEAD,caller=CALLER,pins=PINS,controls=checks,cap_cases=ANCHORS,cap_events=EVENTS,
        cap_seconds=SECONDS,complete=reason is None,timeout=reason,progress=progress,rows=rows,
        unvisited=[r["key"] for r in anchors[len(rows):]],counts=Counter(r["status"] for r in rows)),
        indent=2,sort_keys=True))
    if reason:
        raise SystemExit(2)


if __name__=="__main__":
    main()
