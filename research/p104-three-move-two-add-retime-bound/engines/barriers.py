"""Prove endpoint-chart absence without choosing a direct MOVE clock."""
from collections import defaultdict
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "lead/PRICE.json": "d9074aad58d3ffdad995ba68b2ffa541ae2b7df833b757d8e1a9767118140f39",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "lead/RESULT.json": "96d0cca54073810d12c9b01c408a52771e189b20a0863f9231a6e559f3a22729",
}
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"


def unique(items):
    result = dict(items)
    if len(result) != len(items):
        raise ValueError("duplicate JSON key")
    return result


def checked(path, zipped=False):
    raw = (ROOT / path).read_bytes()
    if sha256(raw).hexdigest() != PINS[path]:
        raise ValueError(f"changed dependency {path}")
    if zipped:
        raw = decompress(raw)
        assert sha256(raw).hexdigest() == PAYLOAD
    return loads(raw, object_pairs_hook=unique)


def affected(event):
    return event[1:3] if event[0] in ("ADD", "COPY") else event[1:2]


def commutes(add, event):
    if event[0] == "MOVE" or not set(affected(add)) & set(affected(event)):
        return True
    if event[0] in ("INIT", "CLEAR"):
        return False
    roles = sorted(set(affected(add)) | set(affected(event)))
    def evaluate(first, second):
        rows = {r:[Q(r==s) for s in roles] for r in roles}
        guard = None
        for e in (first, second):
            op,d,*args = e
            if op == "SCALE":
                rows[d] = [Q(args[0])*v for v in rows[d]]
            else:
                src,q,_ = args
                if op == "COPY":
                    guard = rows[d]
                    rows[d] = [Q(q)*v for v in rows[src]]
                else:
                    assert op == "ADD"
                    rows[d] = [a+Q(q)*b for a,b in zip(rows[d],rows[src],strict=True)]
        return rows,guard
    return evaluate(add,event) == evaluate(event,add)


def controls():
    add = ["ADD",1,2,"1",3]
    assert commutes(add,["ADD",1,4,"1",3])
    assert not commutes(add,["ADD",2,4,"1",3])
    assert commutes(add,["COPY",5,2,"1",3])
    assert not commutes(add,["COPY",5,1,"1",3])
    assert not commutes(add,["CLEAR",2,3])
    assert commutes(add,["SCALE",1,"1",3])
    return ["exact transvection commuting and noncommuting pairs",
            "same-source COPY commutes but changed COPY input does not", "owned lifetime barrier"]


def stop(*_):
    raise TimeoutError("15-second topology cap")


def scan(word, candidates, deadline):
    n, tape = word["public"], word["program"]
    state = word["initial"][:] + [None]*word["owned_fields"]
    paths, lifetimes, tests = defaultdict(list), defaultdict(list), []
    clocks = defaultdict(list)
    for row in candidates:
        mover = row["role"]
        left,middle,right = row["clocks"]
        assert mover < n
        for clock,a,b in zip(row["clocks"],row["charts"][:-1],row["charts"][1:],strict=True):
            assert tape[clock] == ["MOVE",mover,a,b,False]
        pair = []
        for clock,event in row["contacts"]:
            assert event[0] == "ADD" and tape[clock] == event and mover in affected(event)
            peer, = set(affected(event))-{mover}
            pair.append({"clock":clock,"event":event,"peer":peer,"left":None,"right":None})
            paths[peer] = [(0,state[peer])]
        assert left < pair[0]["clock"] < middle < pair[1]["clock"] < right
        for test in pair:
            tests.append((left,right,test,pair[1]["clock"] if test is pair[0] else pair[0]["clock"]))
        clocks[mover].append((left,right,{t["clock"] for t in pair}))
        row["independent_pair"] = pair
    for t,event in enumerate(tape):
        if t%256==0 and monotonic()>=deadline:
            stop()
        op,d,*args = event
        touched = set(affected(event))
        for mover in touched & clocks.keys():
            for left,right,expected in clocks[mover]:
                if left<t<right and op not in ("MOVE",):
                    assert t in expected
        for left,right,test,excluded in tests:
            old=test["clock"]
            if not left<=t<=right or t in (old,excluded):
                continue
            if op=="MOVE" or not touched.intersection(affected(test["event"])):
                continue
            if not commutes(test["event"],event):
                side="left" if t<old else "right"
                if side=="left" or test[side] is None:
                    test[side] = [t,event]
        before=state[d]
        if op=="MOVE":
            assert args[0]==before and args[2]==(d>=n)
            after=args[1]
        elif op=="INIT":
            assert before is None and d>=n
            after=args[0]
        elif op=="CLEAR":
            assert before==args[0] and d>=n
            after=None
        else:
            assert before==args[-1] and op in ("ADD","COPY","SCALE")
            if op in ("ADD","COPY"):
                assert state[args[0]]==before and args[0]!=d
            if op=="COPY":
                assert d>=n
            after=before
        state[d]=after
        if before!=after and d in paths:
            paths[d].append((t+1,after))
            if op in ("INIT","CLEAR"):
                lifetimes[d].append([t,event])
    assert state==word["final"]+[None]*word["owned_fields"]
    return paths,lifetimes


def main():
    assert __debug__
    signal(SIGALRM,stop)
    alarm(15)
    deadline=monotonic()+13
    test_controls=controls()
    price=checked("lead/PRICE.json")
    lead=checked("lead/RESULT.json")
    word=checked("inputs/7334-WORD.json.gz",zipped=True)
    assert price["head"]==lead["head"] and lead["price"]==PINS["lead/PRICE.json"]
    assert len(word["program"])==price["event_cap"]==76466
    assert len(price["candidates"])==len(lead["rows"])==5 and not lead["unvisited"]
    paths,lives=scan(word,price["candidates"],deadline)
    results=[]
    for row,old in zip(price["candidates"],lead["rows"],strict=True):
        left,_,right=row["clocks"]
        endpoints=[row["charts"][0],row["charts"][-1]]
        observed=[]
        for test in row["independent_pair"]:
            peer=test["peer"]
            lo=test["left"][0]+1 if test["left"] else left
            hi=test["right"][0] if test["right"] else right+1
            starts=paths[peer]+[(len(word["program"])+1,None)]
            occupancy=[[max(a,lo),min(b-1,hi),chart] for (a,chart),(b,_) in zip(starts,starts[1:])
                       if max(a,lo)<=min(b-1,hi)]
            assert sum(b-a+1 for a,b,_ in occupancy)==hi-lo+1
            assert any(a<=test["clock"]<=b and c==test["event"][-1] for a,b,c in occupancy)
            hits=[segment for segment in occupancy if segment[2] in endpoints]
            observed.append(test|{"bounds":[lo,hi],"occupancy":occupancy,"endpoint_hits":hits})
        assert row["clocks"]==old["clocks"] and row["role"]==old["role"]
        assert [o["bounds"] for o in observed]==old["commuting_intervals"]
        assert [o["peer"] for o in observed]==old["partners"]
        results.append({"role":row["role"],"clocks":row["clocks"],"endpoints":endpoints,"tests":observed,
                        "excluded":any(not o["endpoint_hits"] for o in observed)})
    assert 1555 in lives and len(lives[1555])>=2
    assert any(o["peer"]==1555 for row in results for o in row["tests"])
    alarm(0)
    print(dumps(dict(pins=PINS,head=price["head"],caller=price["caller"],controls=test_controls,
        events=76466,cap_seconds=15,results=results,owned_1555_lifetime_events=lives[1555],
        excluded=sum(r["excluded"] for r in results),unresolved=sum(not r["excluded"] for r in results),
        scope="Exact five priced windows and same original endpoint charts, partners and pairwise commuting relocation.",
        direct_move_clock_granted_arbitrary_inside_original_window=True),sort_keys=True,indent=2))


if __name__=="__main__":
    main()
