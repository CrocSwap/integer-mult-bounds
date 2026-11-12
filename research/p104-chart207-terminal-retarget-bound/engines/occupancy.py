"""Reverse chart occupancy for the four fixed terminal ADD partners."""
from fractions import Fraction
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/PRICE.json": "76fe970dde53c19b1a068d705344a50afbd3c9a1a1dcd863d6fd605451119ac8",
    "inputs/LEAD.json": "26d1dd900720a87cbc483bd79538066d45f1a52a0801e25e1bce1617e52032eb",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
}
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("duplicate JSON key")
    return result


def read(name, packed=False):
    raw = (ROOT / name).read_bytes()
    if sha256(raw).hexdigest() != PINS[name]:
        raise ValueError(f"changed dependency {name}")
    if packed:
        raw = decompress(raw)
        assert sha256(raw).hexdigest() == PAYLOAD
    return loads(raw, object_pairs_hook=unique)


def touched(event):
    return event[1:3] if event[0] in ("ADD","COPY") else event[1:2]


def barrier(add, event):
    op,d,*args = event
    if op == "MOVE":
        return False
    dst,src = add[1:3]
    if op == "ADD":
        return bool(Fraction(args[1])) and (d == src or args[0] == dst)
    if op == "SCALE" and Fraction(args[0]) == 1:
        return False
    return bool({dst,src} & set(touched(event)))


def ordered(first,second):
    return bool(first and second and min(first) <= max(second))


def controls():
    toy = ["ADD",2,1,"-2",3]
    assert barrier(toy,["ADD",1,4,"3",3])
    assert not barrier(toy,["ADD",2,4,"3",3])
    assert barrier(toy,["COPY",1,4,"1",3])
    assert ordered([3,4],[1,4]) and ordered([4],[4])
    assert not ordered([4],[3]) and not ordered([], [4])
    return ["signed ADD dependency", "COPY guard barrier", "ordered/equal/reversed/absent coframe slots"]


def stop(*_):
    raise TimeoutError("20-second reverse chart census")


def inspect(word,price,deadline):
    tape = word["program"]
    n,owners = word["public"],word["owned_fields"]
    state = word["final"][:] + [None]*owners
    requests,partners = [],set()
    for row in price["candidates"]:
        r,e,t = (row[k] for k in ("role","entry_clock","terminal_clock"))
        assert tape[e] == ["MOVE",r,row["entry_chart"],207,False]
        assert tape[t] == ["MOVE",r,207,127,False]
        expected = []
        for clock,access,event in row["contacts"]:
            other, = set(touched(event))-{r}
            assert tape[clock] == event and event[0] == "ADD" and Fraction(event[-2])
            assert access == ("source" if event[2] == r else "destination")
            assert other < n and clock > t and event[-1] == 127
            partners.add(other)
            expected.append(dict(clock=clock,event=event,partner=other))
        requests.append((r,e,t,expected))
    assert partners == {1,232,363,773}
    moves = {r:[] for r in partners}
    cuts = {r:[] for r in partners if state[r] == 207}
    last_barriers = {}

    @cache
    def span(chart):
        result = {0}
        for x in word["frames"][chart]:
            assert x not in result
            result |= {x ^ y for y in result}
        return result

    for t in range(len(tape)-1,-1,-1):
        if t%128 == 0 and monotonic() >= deadline:
            stop()
        event = tape[t]
        op,d,*args = event
        for mover,entry,terminal,expect in requests:
            if entry < t+1 <= terminal:
                assert state[mover] == 207
            for add in expect:
                clock = add["clock"]
                if t == clock:
                    assert state[mover] == state[add["partner"]] == 127
                if entry < t < clock and t not in {r["clock"] for r in expect} and clock not in last_barriers:
                    if barrier(add["event"], event):
                        last_barriers[clock] = [t,event]
        old = state[d]
        if op == "MOVE":
            before,after,owned = args
            assert old == after and owned == (d >= n)
            if d in partners:
                assert span(before) < span(after)
                moves[d].append([t,before,after])
            state[d] = before
        elif op == "INIT":
            assert d>=n and old == args[0]
            state[d] = None
        elif op == "CLEAR":
            assert d>=n and old is None
            state[d] = args[0]
        else:
            assert op in ("ADD","COPY","SCALE") and old == args[-1]
            if op in ("ADD","COPY"):
                assert state[args[0]] == old and d != args[0]
            if op == "COPY":
                assert d>=n
        for partner in partners:
            if state[partner] == 207:
                cuts.setdefault(partner,[]).append(t)
    assert state == word["initial"]+[None]*owners
    results,typed= [],0
    for r,e,t,expect in requests:
        for row in expect:
            chart207 = sorted(cuts.get(row["partner"],[]))
            previous = last_barriers.get(row["clock"])
            coframe = [k for k in chart207 if e < k <= t]
            allowed = [k for k in coframe if previous is None or previous[0] < k]
            typed += t-e
            row.update(global_chart207_cuts=chart207,coframe=coframe,allowed=allowed,barrier=previous)
        results.append(dict(mover=r,entry_clock=e,terminal_clock=t,placements=expect,
                            ordered_feasible=ordered(*(row["allowed"] for row in expect))))
    paths = {r:dict(initial=word["initial"][r],final=word["final"][r],moves=events[::-1])
             for r,events in sorted(moves.items())}
    return results,paths,typed


def main():
    assert __debug__
    signal(SIGALRM,stop)
    alarm(20)
    deadline=monotonic()+18
    tests=controls()
    price,lead=read("inputs/PRICE.json"),read("inputs/LEAD.json")
    assert price["head"]==lead["head"]==HEAD and price["caller_head"]==lead["caller"]==CALLER
    assert lead["price_sha256"]==PINS["inputs/PRICE.json"] and not lead["unresolved"]
    assert price["delta_paid_per_edit"]=={"1":-17} and price["delta_productive_per_edit"]=={"8":17,"9":-17}
    word=read("inputs/7334-WORD.json.gz",packed=True)
    assert len(word["program"])==price["event_cap"]==76466
    results,paths,typed=inspect(word,price,deadline)
    assert typed==lead["typed_cuts"]==price["typed_cut_cap"]==5084
    for row,old in zip(results,lead["rows"],strict=True):
        assert row["mover"]==old["role"] and row["terminal_clock"]==old["terminal_clock"]
        assert not row["ordered_feasible"] and old["witness"] is None
        for actual,baseline in zip(row["placements"],old["placements"],strict=True):
            assert (actual["clock"],actual["event"],actual["partner"],actual["barrier"])==(
                baseline["old_clock"],baseline["event"],baseline["partner"],baseline["first_noncommuting_barrier"])
            assert actual["coframe"]==baseline["coframe_slots_before_commutation"]==[]
            assert actual["allowed"]==baseline["allowed_slots"]==[]
            assert not actual["global_chart207_cuts"] and not baseline["partner_chart207_anywhere"]
    alarm(0)
    print(dumps(dict(head=HEAD,caller=CALLER,pins=PINS,controls=tests,events=76466,typed_cuts=typed,
        cap_seconds=20,partner_histories=paths,results=results,excluded=2,unresolved=[]),sort_keys=True,indent=2))


if __name__ == "__main__":
    main()
