"""Independently verify the frozen R106 source-side ADD retimes."""
from argparse import ArgumentParser
from bisect import bisect_left
from collections import Counter
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parent
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
PINS = {
    "inputs/PRICE.json": "4ac52a9f1b56a86cb96d9eb6f3be9f635a58b7341ce10905c4a40e296c0f7f8a",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
}
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
EVENTS, WINDOWS, CUTS, SECONDS = 76466, 8, 33560, 20


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("Duplicate JSON key")
    return result


def read(root,name):
    raw = (root/name).read_bytes()
    if sha256(raw).hexdigest() != PINS[name]:
        raise ValueError("Changed input " + name)
    if name.endswith(".gz"):
        raw = decompress(raw)
        assert sha256(raw).hexdigest() == PAYLOAD
    return loads(raw,object_pairs_hook=unique)


def contacts(event):
    return event[1:3] if event[0] in ("ADD","COPY") else event[1:2]


def blocker(recipient,event):
    if recipient not in contacts(event):
        return None
    op,d,*args = event
    if op == "MOVE" or (op == "ADD" and d == recipient and args[0] != recipient):
        return None
    if op == "ADD":
        assert args[0] == recipient
        return "recipient read"
    assert op in ("COPY","SCALE","INIT","CLEAR")
    return "recipient "+op


def crossed_indices(clocks,old,cut):
    lo, hi = sorted((old,cut))
    return clocks[bisect_left(clocks,lo):bisect_left(clocks,hi)]


def controls():
    assert blocker(2,["ADD",2,3,"1",4]) is None
    assert blocker(2,["ADD",3,2,"1",4]) == "recipient read"
    assert blocker(2,["COPY",9,2,"1",4]) == "recipient COPY"
    assert blocker(2,["SCALE",2,"2",4]) == "recipient SCALE"
    assert blocker(2,["MOVE",2,4,5,False]) is None
    assert crossed_indices([7,9,11],8,11) == [9]
    assert crossed_indices([7,9,11],8,7) == [7]
    return ["incoming ADD","recipient read","COPY source","SCALE","MOVE","pre-event cuts"]


def walk(word,roles,deadline,progress):
    n, owned = word["public"],word["owned_fields"]
    tape = word["program"]
    assert (n,owned,len(tape)) == (1501,68,EVENTS)
    state = word["final"] + [None]*owned
    by_role = {r:[] for r in roles}
    pending_fresh = set()
    for t in range(EVENTS-1,-1,-1):
        progress["first_unvisited_event"] = t
        if t%128 == 0 and monotonic() >= deadline:
            raise TimeoutError("reverse event cap")
        event = tape[t]
        op,d,*args = event
        assert 0 <= d < len(state) and (d not in pending_fresh or op == "INIT")
        if op == "MOVE":
            a,b,flag = args
            assert state[d] == b and flag == (d>=n)
            state[d] = a
        elif op == "INIT":
            assert d>=n and state[d] == args[0]
            state[d] = None
            pending_fresh.discard(d)
        elif op == "CLEAR":
            assert d>=n and state[d] is None
            state[d] = args[0]
        else:
            assert op in ("ADD","COPY","SCALE") and state[d] == args[-1]
            assert Fraction(args[-2])
            if op != "SCALE":
                assert args[0] != d and state[args[0]] == args[-1]
            if op == "COPY":
                assert d>=n
                pending_fresh.add(d)
        for r in contacts(event):
            if r in by_role:
                by_role[r].append((t,event,state[r]))
        progress["events_checked"] += 1
    assert state == word["initial"]+[None]*owned and not pending_fresh
    progress["first_unvisited_event"] = None
    return {r:list(reversed(items)) for r,items in by_role.items()}


def evaluate(word,price,history,deadline,progress,rows,counts,survivors):
    for candidate in price["candidate_rows"]:
        f,g,s = candidate["key"]
        a,b,c = candidate["charts"]
        old,add = candidate["add"]
        d = add[1]
        assert s<word["public"] and d<word["public"] and s!=d and f<old<g
        source = [(t,e) for t,e,_ in history[s] if f<=t<=g]
        assert source == [(f,["MOVE",s,a,b,False]),(old,add),(g,["MOVE",s,b,c,False])]
        assert add == ["ADD",d,s,add[3],b]
        recipient = history[d]
        rc = {t:e for t,e,_ in recipient}
        assert rc[old] == add
        moves = [(t,e[3]) for t,e,_ in recipient if e[0] == "MOVE"]
        clocks = [t for t,_ in moves]
        guards = {t:why for t,e,_ in recipient if t!=old and (why:=blocker(d,e))}
        guard_clocks = sorted(guards)
        by_side = []
        row = dict(pair=candidate["key"],recipient=d,old_add=candidate["add"],cuts=by_side)
        rows.append(row)
        for side,required in (("A",a),("C",c)):
            side_counts = Counter()
            intervals = []
            by_side.append(dict(side=side,required_chart=required,intervals=intervals,counts=side_counts))
            for cut in range(f+1,g+1):
                if cut == old:
                    continue
                progress["first_unvisited_cut"] = [f,g,s,side,cut]
                if progress["typed_cuts_checked"] == CUTS or monotonic()>=deadline:
                    raise TimeoutError("typed cut cap")
                idx = bisect_left(clocks,cut)
                actual = moves[idx-1][1] if idx else word["initial"][d]
                crossed = crossed_indices(guard_clocks,old,cut)
                reason = "different chart" if actual != required else guards[crossed[0]] if crossed else "eligible"
                evidence = [actual,reason,[crossed[0],rc[crossed[0]]] if crossed else None]
                if intervals and intervals[-1][1] == cut-1 and intervals[-1][2:] == evidence:
                    intervals[-1][1] = cut
                else:
                    intervals.append([cut,cut,*evidence])
                if reason == "eligible":
                    survivors.append([f,g,s,side,cut])
                side_counts[reason] += 1
                counts[reason] += 1
                progress["typed_cuts_checked"] += 1
    assert progress["typed_cuts_checked"] == CUTS and len(rows) == WINDOWS
    progress["first_unvisited_cut"] = None


def main():
    assert __debug__
    p = ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,default=ROOT)
    p.add_argument("--controls-only",action="store_true")
    args = p.parse_args()
    tests = controls()
    if args.controls_only:
        print(dumps(tests))
        return
    progress = dict(events_checked=0,typed_cuts_checked=0,first_unvisited_event=EVENTS-1,first_unvisited_cut=None)
    rows,survivors = [],[]
    counts = Counter()
    reason = None

    def stop(*_):
        raise TimeoutError("Hard 20-second cap")

    signal(SIGALRM,stop)
    alarm(SECONDS)
    deadline = monotonic()+SECONDS-2
    try:
        price = read(args.root,"inputs/PRICE.json")
        assert price["head"] == HEAD and price["caller"] == CALLER
        assert price["word_sha256"] == PINS["inputs/7334-WORD.json.gz"] and price["payload_sha256"] == PAYLOAD
        assert [price["limits"][k] for k in ("events","windows","typed_cuts","seconds")] == [EVENTS,WINDOWS,CUTS,SECONDS]
        word = read(args.root,"inputs/7334-WORD.json.gz")
        roles = {r for w in price["candidate_rows"] for r in w["add"][1][1:3]}
        history = walk(word,roles,deadline,progress)
        evaluate(word,price,history,deadline,progress,rows,counts,survivors)
    except TimeoutError as exc:
        reason = str(exc)
    finally:
        alarm(0)
    print(dumps(dict(head=HEAD,caller=CALLER,pins=PINS,controls=tests,rows=rows,counts=counts,
        survivors=survivors,progress=progress,timeout=reason),indent=2,sort_keys=True))
    if reason:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
