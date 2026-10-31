#!/usr/bin/env python3
"""Independent exact endpoint/frame/invoice audit of the unit-column handoff.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
This imports no predecessor or candidate executable. Integer vectors with a
common binary denominator check all columns at once; a separate rank-one
surgery argument is recorded in INDEPENDENT-REVIEW.md.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path

SOURCE_SHA256 = "b2a98c4bd0dbe86c09e9d15ee060dcf1aab09dbef90aa1e2127676f4039f406b"
CUT = 13762
PIVOT = 596
V = {592: Fraction(5, 16), 593: Fraction(5, 16),
     594: Fraction(5, 8), 596: Fraction(3, 8)}
U = {592: Fraction(-1), 593: Fraction(1), 594: Fraction(1), 596: Fraction(1)}
B = {188: Fraction(-1), **U}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dyadic(text):
    q = Fraction(text)
    denominator = q.denominator
    require(q != 0 and denominator & (denominator - 1) == 0,
            "nonzero dyadic coefficient")
    require(abs(q) + 1 < 2**16, "coefficient growth")
    return q.numerator, denominator.bit_length() - 1


def reduced(entries, exponent):
    entries = {j: a for j, a in entries.items() if a}
    if not entries:
        return {}, 0
    factor = min(exponent, min((abs(a) & -abs(a)).bit_length() - 1
                               for a in entries.values()))
    if factor:
        entries = {j: a >> factor for j, a in entries.items()}
    return entries, exponent - factor


def scaled(vector, numerator, exponent):
    values, level = vector
    return reduced({j: numerator * a for j, a in values.items()}, level + exponent)


def increment(destination, source, numerator, exponent):
    left, el = destination
    right, er = source
    common = max(el, er + exponent)
    result = {j: a << (common - el) for j, a in left.items()}
    multiplier = numerator << (common - er - exponent)
    for j, a in right.items():
        result[j] = result.get(j, 0) + multiplier * a
    return reduced(result, common)


def rational(vector):
    values, exponent = vector
    return {j: Fraction(a, 1 << exponent) for j, a in values.items()}


def binary_basis(vectors):
    pivots = {}
    for value in vectors:
        require(type(value) is int and 0 < value < 512, "binary frame vector")
        x = value
        while x:
            bit = x.bit_length() - 1
            if bit in pivots:
                x ^= pivots[bit]
            else:
                pivots[bit] = x
                break
        require(x != 0, "binary frame independence")
    return pivots


def contained(left, right):
    for value in left.values():
        x = value
        while x and x.bit_length() - 1 in right:
            x ^= right[x.bit_length() - 1]
        if x:
            return False
    return True


def replay(word, checkpoint=None):
    require(word["schema"] == "p104-productive-source/1", "word schema")
    n = word["public"]
    require(type(n) is int and n >= 735, "public width")
    require(len(word["initial"]) == len(word["final"]) == n, "boundary widths")
    require(len(word["program"]) < 26000, "operation cap")
    extent = n + 8
    # Formal columns include the eight initially inaccessible owned slots.
    # Their legal INIT operations erase those columns before any source use.
    state = [({j: 1}, 0) for j in range(extent)]
    chart = list(word["initial"]) + [None] * 8
    bases = [binary_basis(v) for v in word["frames"]]
    live_owned = set()
    initialized = cleared = maximum = allowance = 0
    paid = Counter()
    snapshot = None
    for index, event in enumerate(word["program"]):
        op, destination = event[:2]
        require(type(destination) is int and 0 <= destination < extent, "destination range")
        if op == "MOVE":
            _, _, start, finish, owned = event
            require(type(owned) is bool, "ownership type")
            require(chart[destination] == start, "move entry chart")
            require((destination in live_owned) == owned, "move ownership")
            small, large = (bases[finish], bases[start]) if owned else (bases[start], bases[finish])
            require(len(small) < len(large) and contained(small, large), "strict nested movement")
            paid[len(large) - len(small)] += 1
            chart[destination] = finish
        elif op == "INIT":
            require(destination >= n and destination not in live_owned,
                    "owned allocation only")
            live_owned.add(destination)
            chart[destination] = event[2]
            state[destination] = ({}, 0)
            initialized += 1
            maximum = max(maximum, len(live_owned))
            allowance += 2
        elif op == "CLEAR":
            require(destination in live_owned and chart[destination] == event[2],
                    "owned clear lifetime")
            live_owned.remove(destination)
            chart[destination] = None
            state[destination] = ({}, 0)
            cleared += 1
            allowance += 2
        elif op in ("ADD", "COPY", "SCALE"):
            numerator, exponent = dyadic(event[-2])
            require(chart[destination] == event[-1] and chart[destination] is not None,
                    "scalar destination chart")
            if op == "SCALE":
                absolute = abs(numerator)
                require(absolute & (absolute - 1) == 0, "unit scale")
                state[destination] = scaled(state[destination], numerator, exponent)
                allowance += 2 * (abs(absolute.bit_length() - 1 - exponent) + (numerator < 0))
            else:
                source = event[2]
                require(type(source) is int and 0 <= source < extent and source != destination,
                        "distinct scalar operands")
                require(chart[source] == chart[destination], "common scalar chart")
                if op == "COPY":
                    require(destination in live_owned and not state[destination][0],
                            "copy into owned zero")
                    state[destination] = scaled(state[source], numerator, exponent)
                else:
                    state[destination] = increment(state[destination], state[source], numerator, exponent)
                absolute = abs(numerator)
                allowance += 2 * (2 + absolute.bit_length() + absolute.bit_count() + exponent)
        else:
            raise ValueError("unknown opcode")
        if checkpoint == index:
            snapshot = {
                "rows": {r: rational(state[r]) for r in V},
                "charts": chart[:],
                "owned": sorted(live_owned),
            }
    require(not live_owned and all(f is None for f in chart[n:]), "owned return")
    require(chart[:n] == word["final"], "public exit charts")
    for j, vector in enumerate(state):
        expected = {j: 1} if j < n else {}
        if j - 112 in word["live"]:
            expected[j - 112] = 1
        require(vector == (expected, 0), "full independent-input endpoint at row " + str(j))
    mains = set(word["live"]) | {r + 112 for r in word["live"]}
    require(len(mains) == 208, "main inventory")
    helpers = Counter()
    for j in range(n):
        if j not in mains:
            a, b = bases[word["initial"][j]], bases[word["final"][j]]
            require(len(a) < len(b) and contained(a, b), "helper endpoint nesting")
            helpers[len(b) - len(a)] += 1
    return {"public": n, "input_columns": extent, "endpoint_coefficients": extent**2,
            "events": len(word["program"]), "paid": dict(sorted(paid.items())),
            "helpers": dict(sorted(helpers.items())), "allowance": allowance,
            "initialized": initialized, "cleared": cleared, "peak_owned": maximum}, snapshot


def boundary_audit(source, snapshot):
    require(snapshot is not None and not snapshot["owned"], "empty owned cut")
    require(all(snapshot["charts"][r] == 1053 for r in V), "specified cut chart")
    a = Counter()
    for row, coefficient in V.items():
        for j, value in snapshot["rows"][row].items():
            a[j] += coefficient * value
    require({j: value for j, value in a.items() if value} == V, "prefix functional")
    values = [Fraction(0)] * (source["public"] + 8)
    for j, value in U.items():
        values[j] = value
    for event in source["program"][CUT + 1:]:
        op, j = event[:2]
        if op == "MOVE":
            continue
        if op in ("INIT", "CLEAR"):
            values[j] = 0
        elif op == "SCALE":
            values[j] *= Fraction(event[-2])
        elif op == "COPY":
            values[j] = Fraction(event[-2]) * values[event[2]]
        elif op == "ADD":
            values[j] += Fraction(event[-2]) * values[event[2]]
        else:
            raise ValueError("suffix opcode")
    require({j: q for j, q in enumerate(values) if q} == B, "suffix direction")
    require(sum(V[j] * U.get(j, 0) for j in V) == 1, "dual pairing")
    mains = set(source["live"]) | {j + 112 for j in source["live"]}
    group = {j for j in range(source["public"]) if j not in mains
             and (source["initial"][j], source["final"][j]) == (3, 127)}
    require(len(group) == 424 and set(V) | set(B) <= group, "independent helper group")


def load_word(path):
    payload = Path(path).read_bytes()
    return json.loads(gzip.decompress(payload) if payload[:2] == b"\x1f\x8b" else payload)


def audit(source, candidate):
    before, snapshot = replay(source, checkpoint=CUT)
    boundary_audit(source, snapshot)
    after, _ = replay(candidate)
    require(before["public"] == 735 and before["events"] == 25140
            and before["allowance"] == 217428, "source fixture inventory")
    require(after["public"] == 736 and after["events"] == 25162
            and after["allowance"] == 217708, "candidate fixture inventory")
    require(after["paid"] == before["paid"], "paid profile preservation")
    expected = Counter(before["helpers"])
    expected[9] -= 1
    expected[5] += 1
    expected[4] += 1
    require(after["helpers"] == dict(sorted(expected.items())), "target split inventory")
    require(candidate["frames"] == source["frames"] and candidate["live"] == source["live"]
            and candidate["ports"] == source["ports"], "frame/port preservation")
    expected_initial = source["initial"] + [1053]
    expected_final = source["final"][:]
    expected_final[PIVOT] = 1053
    expected_final.append(127)
    require(candidate["initial"] == expected_initial and candidate["final"] == expected_final,
            "exact changed boundaries")
    require(after["initialized"] == after["cleared"] == before["initialized"] == before["cleared"] == 8,
            "eight complete owned lifetimes")
    require(after["peak_owned"] == before["peak_owned"] == 1, "peak owned preservation")
    return {"before": before, "after": after, "allowance_delta": after["allowance"] - before["allowance"],
            "rank_split": [9, 5, 4], "independent_arithmetic": "integer vectors / shared powers of two",
            "scope": "scalar word, all independent public inputs, binary frames, local invoice; no native/caller admission"}


def negative_controls(source, candidate):
    """Exercise mathematical/ownership/geometry failures in independent replay."""
    cases = []
    broken = deepcopy(candidate)
    broken["program"][0][-2] = str(-Fraction(broken["program"][0][-2]))
    cases.append(("changed boundary coefficient", broken))
    broken = deepcopy(candidate)
    del broken["program"][0]
    cases.append(("omitted boundary gate", broken))
    broken = deepcopy(candidate)
    broken["program"][0][-1] = 1053
    cases.append(("unavailable boundary chart", broken))
    broken = deepcopy(candidate)
    broken["program"].insert(0, ["INIT", 735, 1053])
    cases.append(("erase independent new public input", broken))
    broken = deepcopy(candidate)
    first_clear = next(i for i, e in enumerate(broken["program"]) if e[0] == "CLEAR")
    del broken["program"][first_clear]
    cases.append(("omit owned clear", broken))
    broken = deepcopy(candidate)
    broken["final"][596] = 127
    cases.append(("claim unsplit exit for retired input", broken))
    broken = deepcopy(candidate)
    broken["initial"][735] = 3
    cases.append(("misplace new input chart", broken))
    broken = deepcopy(candidate)
    broken["frames"][1053] = [7, 25, 42, 192, 192]
    cases.append(("dependent cut basis", broken))
    broken = deepcopy(candidate)
    broken["program"].insert(0, ["SCALE", 596, "3", 3])
    cases.append(("nonunit scale", broken))
    broken = deepcopy(candidate)
    broken["program"][0][-2] = "1/3"
    cases.append(("nondyadic boundary", broken))
    rejected = []
    for label, broken in cases:
        try:
            audit(source, broken)
        except ValueError as error:
            rejected.append({"control": label, "rejection": str(error)})
        else:
            raise ValueError("independent control accepted: " + label)
    return rejected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--word", required=True, type=Path)
    parser.add_argument("--controls", action="store_true")
    args = parser.parse_args()
    require(hashlib.sha256(args.source.read_bytes()).hexdigest() == SOURCE_SHA256, "source bytes")
    source, candidate = load_word(args.source), load_word(args.word)
    result = audit(source, candidate)
    if args.controls:
        result["negative_controls"] = negative_controls(source, candidate)
    print(json.dumps(result, sort_keys=True))
    print("PASS_INDEPENDENT_UNIT_COLUMN_HANDOFF")


if __name__ == "__main__":
    main()
