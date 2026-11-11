"""Forward owned-lifetime census on the literal funded-return word."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from functools import cache
import gzip
from hashlib import sha256
import json
from pathlib import Path
from time import monotonic

HEAD = "9d0119eb12fbd9fa534b48cd37b68e7099757b91"
WORD_SHA = "c404b9b61220e6cf740d85276df2828bbb4a9d68a4d44b5e283f8d96f78c0fd9"
PROTECTED = {863, 1355, 1568}


def decode(raw):
    def unique(entries):
        result = dict(entries)
        if len(result) != len(entries):
            raise ValueError("duplicate JSON key")
        return result
    return json.loads(raw, object_pairs_hook=unique)


def authenticate(path, expected):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != expected:
        raise ValueError(f"changed pinned input: {path.name}")
    return raw


def dimension_basis(rows):
    pivots = {}
    for row in rows:
        while row and row.bit_length() in pivots:
            row ^= pivots[row.bit_length()]
        if not row:
            raise ValueError("dependent chart basis")
        pivots[row.bit_length()] = row
    return pivots


def inside(row, basis):
    while row and row.bit_length() in basis:
        row ^= basis[row.bit_length()]
    return row == 0


def classify(role, init, clear, contacts, ranks):
    out = dict(role=role, init=init[0], initial_chart=init[1], clear=clear[0],
               final_chart=clear[1], capture=None, moves=[], reads=[], contacts=len(contacts))
    if contacts:
        clock, op, dst, src, q, chart = contacts[0]
        if op in ("ADD", "COPY") and dst == role:
            out["capture"] = clock
    for clock, op, dst, src, q, chart in contacts:
        if op == "MOVE":
            old, new = chart
            out["moves"].append(dict(clock=clock, old=old, new=new, rank=abs(ranks[new]-ranks[old])))
        elif op == "ADD" and src == role and dst != role:
            out["reads"].append(dict(clock=clock, destination=dst, coefficient=q, chart=chart))
    if role in PROTECTED:
        reason = "protected role"
    elif not out["moves"]:
        reason = "no paid MOVE"
    elif not contacts or contacts[0][1] != "ADD" or out["capture"] != init[0] + 1:
        reason = "no immediate ADD capture"
    elif contacts[0][3] == role or not Fraction(contacts[0][4]):
        reason = "invalid capture source"
    elif any(op != "MOVE" and (op != "ADD" or src != role or dst == role)
             for _, op, dst, src, _, _ in contacts[1:]):
        reason = "other lifetime contact"
    elif not out["reads"]:
        reason = "no source ADD"
    else:
        charts = {read["chart"] for read in out["reads"]}
        if len(charts) != 1:
            reason = "several read charts"
        elif ranks[next(iter(charts))] <= ranks[init[1]]:
            reason = "read chart does not have higher rank"
        else:
            reason = "survives"
            out["read_chart"], = charts
            out["capture_source"] = contacts[0][3]
            out["capture_coefficient"] = contacts[0][4]
    out["decision"] = reason
    return out


def inventory(word, max_lifetimes, seconds):
    deadline = monotonic() + seconds
    public, owned = word["public"], word["owned_fields"]
    frames = word["frames"]
    bases = list(map(dimension_basis, frames))
    ranks = list(map(len, frames))
    charts = list(word["initial"]) + [None] * owned
    paid = Counter()
    births, completed = {}, []

    @cache
    def nested(a, b):
        return ranks[a] < ranks[b] and all(inside(row, bases[b]) for row in frames[a])

    visited = 0
    for clock, (op, dst, *args) in enumerate(word["program"]):
        if clock % 128 == 0 and monotonic() >= deadline:
            break
        if len(completed) == max_lifetimes and op == "CLEAR":
            break
        visited = clock + 1
        if op == "INIT":
            frame, = args
            assert dst >= public and charts[dst] is None
            charts[dst] = frame
            births[dst] = (clock, frame), []
        elif op == "CLEAR":
            frame, = args
            assert dst >= public and charts[dst] == frame
            start, contacts = births.pop(dst)
            completed.append(classify(dst, start, (clock, frame), contacts, ranks))
            charts[dst] = None
        elif op == "MOVE":
            old, new, is_owned = args
            assert charts[dst] == old and is_owned == (dst >= public)
            assert nested(old, new) or is_owned and nested(new, old)
            charts[dst] = new
            if is_owned:
                paid[abs(ranks[new]-ranks[old])] += 1
                births[dst][1].append((clock, op, dst, dst, None, (old, new)))
        else:
            assert op in ("ADD", "COPY", "SCALE")
            q, frame = args[-2:]
            src = args[0] if op != "SCALE" else dst
            assert charts[dst] == charts[src] == frame and Fraction(q)
            assert op == "SCALE" or dst != src
            assert op != "COPY" or dst >= public
            for role in {dst, src}:
                if role >= public:
                    births[role][1].append((clock, op, dst, src, q, frame))
    complete = visited == len(word["program"])
    if complete:
        assert not births and charts == word["final"] + [None] * owned
    ordered = sorted(completed, key=lambda x: x["init"])
    return dict(complete=complete, visited_events=visited, literal_events=len(word["program"]),
                lifetimes=len(ordered), open_lifetimes=sorted((r, x[0][0]) for r, x in births.items()),
                first_unvisited_clock=None if complete else visited,
                dispositions=dict(Counter(row["decision"] for row in ordered)),
                owned_move_histogram=dict(paid), decisions=ordered,
                survivors=[row for row in ordered if row["decision"] == "survives"])


def controls():
    word = dict(public=3, owned_fields=1, frames=[[], [1], [1, 2]], initial=[0, 0, 0],
                final=[0, 2, 2], program=[
                    ["INIT", 3, 0], ["ADD", 3, 0, "-2", 0],
                    ["MOVE", 3, 0, 2, True], ["MOVE", 1, 0, 2, False],
                    ["MOVE", 2, 0, 2, False], ["ADD", 2, 3, "1/2", 2], ["CLEAR", 3, 2]])
    good = inventory(word, 1, 15)
    assert good["complete"] and good["survivors"][0]["reads"][0]["destination"] == 2
    bad = word | {"program": word["program"][:5] + [["ADD", 3, 2, "1", 2]] + word["program"][5:]}
    assert inventory(bad, 1, 15)["dispositions"] == {"other lifetime contact": 1}
    bad = word | {"program": word["program"][:1] + [["COPY", 3, 0, "-2", 0]] + word["program"][2:]}
    assert inventory(bad, 1, 15)["dispositions"] == {"no immediate ADD capture": 1}
    bad = word | {"program": word["program"][:4] + [["MOVE", 2, 0, 2, False]] + word["program"][4:]}
    try:
        inventory(bad, 1, 15)
    except AssertionError:
        pass
    else:
        raise AssertionError("duplicate paid MOVE must be rejected")
    return ["signed valid capture", "late write rejected", "COPY outside scope", "duplicate MOVE rejected"]


def main():
    p = ArgumentParser()
    p.add_argument("--word", type=Path)
    p.add_argument("--price", type=Path)
    p.add_argument("--price-sha")
    p.add_argument("--lifetimes", type=int, choices=range(1, 73), default=72, metavar="[1,72]")
    p.add_argument("--seconds", type=int, choices=range(1, 18), default=17, metavar="[1,17]")
    p.add_argument("--controls-only", action="store_true")
    a = p.parse_args()
    checks = controls()
    if a.controls_only:
        print(json.dumps(checks))
        return
    price = decode(authenticate(a.price, a.price_sha))
    assert price["head"] == HEAD
    word = decode(gzip.decompress(authenticate(a.word, WORD_SHA)))
    result = inventory(word, a.lifetimes, a.seconds)
    if result["complete"]:
        assert result["lifetimes"] == 72
        assert result["owned_move_histogram"] == {1: 20, 2: 9, 3: 2, 4: 13, 5: 2, 6: 1}
    result.update(head=HEAD, word_sha256=WORD_SHA, price_sha256=a.price_sha,
                  controls=checks, caps=dict(lifetimes=a.lifetimes, seconds=a.seconds))
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
