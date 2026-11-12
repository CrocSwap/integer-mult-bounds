"""Round 82 reverse incident-interval geometry of five owned paid pairs."""

from argparse import ArgumentParser
from bisect import bisect_left
from collections import Counter
from fractions import Fraction
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import alarm
from time import monotonic

PRICE = "inputs/PRICE.json"
WORD = "inputs/7334-WORD.json.gz"
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
PINS = {
    PRICE: "82baf8740dfc695d304602d92bd3888961c965f76a5bcb4784cbd4f9726e7ee6",
    WORD: "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
}
CANONICAL = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"


def unique(pairs):
    value = dict(pairs)
    if len(value) != len(pairs):
        raise ValueError("duplicate JSON key")
    return value


def source(root, path):
    raw = (root / path).read_bytes()
    if sha256(raw).hexdigest() != PINS[path]:
        raise ValueError(f"changed dependency {path}")
    return raw


def reverse_index(word, tracked, deadline):
    """Index chart intervals by their next contact, retaining the clear lifetime."""
    n = word["public"]
    tail = {role: (word["final"][role], -1) if role < n else None for role in tracked}
    state = tail.copy()
    contacts = {role: [] for role in tracked}
    lifetimes = {}
    tape = word["program"]
    for clock in range(len(tape) - 1, -1, -1):
        if clock % 128 == 0 and monotonic() >= deadline:
            return None, [0, clock]
        e = tape[clock]
        op, d = e[:2]
        if d in state:
            active = state[d]
            if op == "MOVE":
                a, b, owned = e[2:]
                assert owned == (d >= n) and active is not None and active[0] == b
                state[d] = (a, active[1])
            elif op == "CLEAR":
                assert d >= n and active is None
                state[d] = (e[2], clock)
            elif op == "INIT":
                assert d >= n and active is not None and active[0] == e[2]
                lifetimes[d, active[1]] = (clock, active[1])
                state[d] = None
            else:
                assert op in ("ADD", "COPY", "SCALE") and active is not None and active[0] == e[-1]
            contacts[d].append((clock, state[d], "destination"))
        if op in ("ADD", "COPY") and e[2] in state:
            s = e[2]
            active = state[s]
            assert s != d and active is not None and active[0] == e[-1]
            contacts[s].append((clock, active, "source"))
    assert state == {role: (word["initial"][role], -1) if role < n else None for role in tracked}
    index = {}
    for role, records in contacts.items():
        records.reverse()
        clocks = [record[0] for record in records]
        assert len(clocks) == len(set(clocks))
        index[role] = (clocks, records, tail[role])
    return (index, lifetimes), None


def chart_at(index, role, cut):
    clocks, records, tail = index[role]
    offset = bisect_left(clocks, cut)
    return records[offset][1] if offset < len(clocks) else tail


def peer_block(tape, records, moved_owner, owner_access, old_add, cut):
    clocks, contacts, _ = records
    lo, hi = (cut, old_add) if cut < old_add else (old_add + 1, cut)
    if lo >= hi:
        return []
    blocked = []
    for clock, _, access in contacts[bisect_left(clocks, lo):bisect_left(clocks, hi)]:
        e = tape[clock]
        op = e[0]
        if op == "MOVE":
            continue
        if op == "ADD" and owner_access == "destination" and access == "source" and e[1] != moved_owner:
            continue
        blocked.append([clock, op, access, e])
    return blocked


def solve(word, candidates, deadline, limits=(10, 51)):
    tracks = {role for row in candidates for role in (row["owner"], row["peer"])}
    tape = word["program"]
    history, unvisited_interval = reverse_index(word, tracks, deadline)
    if history is None:
        return {
            "complete": False, "unvisited_literal_interval": unvisited_interval,
            "placements": [], "unvisited": [
                [row["owner"], row["move_clocks"][0], end, cut]
                for row in candidates
                for end, (lo, hi) in row["cut_windows_pre_event"].items()
                for cut in range(lo, hi + 1)
            ],
        }
    index, lifetimes = history
    n = word["public"]

    @cache
    def span(chart):
        group = {0}
        for vector in word["frames"][chart]:
            assert type(vector) is int and 0 < vector < 512 and vector not in group
            group.update(vector ^ existing for existing in tuple(group))
        return group

    placements, unvisited = [], []
    visited_cuts = 0
    for row in candidates:
        r, s = row["owner"], row["peer"]
        f, g = row["move_clocks"]
        t, (dst, src, q, b) = row["literal_ADD"]
        a, mid, c = row["chart_path"]
        assert f < t < g and r >= n and r != s and mid == b
        assert tape[f] == ["MOVE", r, a, b, True]
        assert tape[g] == ["MOVE", r, b, c, True]
        assert tape[t] == ["ADD", dst, src, q, b] and Fraction(q)
        assert (dst, src) == ((s, r) if row["owner_access"] == "source" else (r, s))
        assert span(a) < span(b) < span(c) or span(c) < span(b) < span(a)
        assert [abs(len(word["frames"][y])-len(word["frames"][x])) for x,y in ((a,b),(b,c))] == row["paid_old"]
        owner_state = chart_at(index, r, t)
        peer_state = chart_at(index, s, t)
        assert owner_state is not None and peer_state is not None
        assert owner_state[0] == peer_state[0] == b
        life = lifetimes[r, owner_state[1]]
        assert list(life) == row["owner_lifetime"]
        assert life[0] < f < g < life[1]
        owner_clocks = index[r][0]
        assert owner_clocks[bisect_left(owner_clocks, f):bisect_left(owner_clocks, g + 1)] == [f,t,g]
        expected_windows = {"entrance": [f,g], "exit": [f+1,g]}
        assert row["cut_windows_pre_event"] == expected_windows

        for end, fused_clock, required in (("entrance", g, a), ("exit", f, c)):
            cuts = []
            lo, hi = expected_windows[end]
            for cut in range(lo, hi + 1):
                if len(placements) >= limits[0] or visited_cuts >= limits[1] or monotonic() >= deadline:
                    unvisited.append([r, f, end, cut])
                    continue
                visited_cuts += 1
                seen = chart_at(index, s, cut)
                blockers = peer_block(tape, index[s], r, row["owner_access"], t, cut)
                same_lifetime = seen is not None and seen[1] == peer_state[1]
                cochart = seen is not None and seen[0] == required
                status = ("different_lifetime" if not same_lifetime else
                          "wrong_chart" if not cochart else
                          "crossed_binary_or_lifetime_barrier" if blockers else "survivor")
                cuts.append({
                    "cut": cut, "peer_chart": seen[0] if seen else None, "same_peer_lifetime": same_lifetime,
                    "cochart": cochart, "crossed_blockers": blockers, "status": status,
                })
            placements.append({
                "key": [r,f,g,end], "add_clock": t, "peer": s, "owner_access": row["owner_access"],
                "peer_lifetime": list(lifetimes[s,peer_state[1]]) if s >= n else "public",
                "replacement_move_clock": fused_clock, "required_chart": required,
                "cuts": cuts, "surviving_cuts": [x["cut"] for x in cuts if x["status"] == "survivor"],
            })
    return {
        "complete": not unvisited, "unvisited_literal_interval": None, "unvisited": unvisited,
        "placements": placements, "visited_cuts": visited_cuts,
        "status_counts": dict(sorted(Counter(c["status"] for p in placements for c in p["cuts"]).items())),
        "survivors": [p["key"] + [cut] for p in placements for cut in p["surviving_cuts"]],
    }


def controls():
    def toy(moved_is_source):
        d, s = (0, 2) if moved_is_source else (2, 0)
        tape = [
            ["INIT",2,1], ["MOVE",2,1,2,True], ["ADD",1,0,"7",1],
            ["MOVE",0,1,2,False], ["ADD",d,s,"-3/2",2], ["MOVE",2,2,3,True],
            ["CLEAR",2,3],
        ]
        word = {"program": tape, "public": 2, "initial": [1,1], "final": [2,1],
                "frames": [[], [1], [1,2], [1,2,4]]}
        row = {"owner": 2, "peer": 0, "move_clocks": [1,5], "chart_path": [1,2,3],
               "literal_ADD": [4,[d,s,"-3/2",2]], "owner_access": "source" if moved_is_source else "destination",
               "owner_lifetime": [0,6], "paid_old": [1,1],
               "cut_windows_pre_event": {"entrance": [1,5], "exit": [2,5]}}
        return solve(word, [row], monotonic()+2)

    write = toy(True)
    read = toy(False)
    assert write["placements"][0]["cuts"][0]["status"] == "crossed_binary_or_lifetime_barrier"
    assert [2, "ADD", "source", ["ADD",1,0,"7",1]] in write["placements"][0]["cuts"][0]["crossed_blockers"]
    assert read["placements"][0]["cuts"][0]["status"] == "survivor"
    life_tape = [["CLEAR", 3, 1], ["INIT", 3, 1], ["COPY", 1, 3, "1", 1]]
    synthetic_peer_index = ([0,1,2], [(0,None,"destination"), (1,None,"destination"), (2,None,"source")], None)
    assert [p[1] for p in peer_block(life_tape, synthetic_peer_index, 2, "destination", 3, 0)] == ["CLEAR","INIT","COPY"]
    return ["exact_cochart", "peer_read_blocks_mutated_destination", "peer_read_commutes_if_read_only",
            "owned_lifetime_and_guarded_copy_barriers"]


def main():
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    root = parser.parse_args().root
    alarm(20)
    deadline = monotonic()+18
    price = loads(source(root, PRICE), object_pairs_hook=unique)
    assert price["head"] == HEAD and price["word_sha256"] == PINS[WORD]
    assert price["typed_end_placements"] == 10 and price["first_runner_seconds"] == 20
    assert len(price["candidates"]) == price["candidate_count"] == 5
    word = loads(decompress(source(root, WORD)), object_pairs_hook=unique)
    assert sha256(dumps(word,sort_keys=True,separators=(",",":")).encode()).hexdigest() == CANONICAL
    check = controls()
    result = solve(word, price["candidates"], deadline)
    if result["complete"]:
        assert len(result["placements"]) == 10 and result["visited_cuts"] == 51
    result |= {"head": HEAD, "price_sha256": PINS[PRICE], "word_sha256": PINS[WORD],
               "input_sha256": PINS, "controls": check, "caps": [10,51,20],
               "scope": "Independent reverse next-contact interval reconstruction, pre-event cuts, exact peer chronology and the five frozen owned pairs."}
    print(dumps(result,sort_keys=True,indent=2))
    alarm(0)


if __name__ == "__main__":
    main()
