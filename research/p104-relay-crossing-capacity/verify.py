"""Exact finite premises and controls for the written relay crossing proof."""

import argparse
import hashlib
import json
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
INPUTS = {
    "LOWRANK-WITNESS.json": "0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e",
    "P104-FIXTURE.json": "516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4",
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result = dict(pairs)
    need(len(result) == len(pairs), "duplicate JSON key")
    return result


def read_json(path):
    need(path.stat().st_size <= 2_000_000, "input capacity")
    return json.loads(path.read_text(), object_pairs_hook=unique_object)


def span(basis):
    need(len(basis) <= 9, "nine-dimensional frame capacity")
    result = {0}
    for vector in basis:
        need(type(vector) is int and 0 < vector < 512, "binary frame vector")
        result.update(value ^ vector for value in tuple(result))
    need(len(result) == 1 << len(basis), "independent frame basis")
    return frozenset(result)


def roots(fixture):
    lines = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            lines.add(tuple(row))
    for signs in product((-1, 1), repeat=7):
        if signs.count(-1) % 2 == 0:
            lines.add((1, *signs))
    removed = {tuple(row) for row in fixture["F0"] + fixture["C"]}
    need(len(lines) == 120 and len(removed) == 16, "root fixture cardinality")
    return sorted(lines - removed)


def paths(witness):
    need(len(witness["program"]) == 4058, "frozen event capacity")
    names = [f"{kind}{i}" for kind in "XY" for i in range(104)]
    result = {name: [span(witness["initial_frames"][name])] for name in names}
    for event in witness["program"]:
        if event[0] == "add":
            need(not event[1].startswith("X"), "original sources are immutable")
        if event[0] != "transport" or event[1] not in result:
            continue
        _, name, old, new, rank = event
        before, after = span(old), span(new)
        need(result[name][-1] == before < after, "nested chronological data path")
        need(rank == len(new) - len(old), "data path rank")
        result[name].append(after)
    for name, frames in result.items():
        need(frames[-1] == span(witness["final_frames"][name]), "data endpoint")
        need(len(frames) <= 10, "at most nine strictly increasing data transports")
    return result


def parity(vector, covector):
    return (vector & covector).bit_count() % 2


def affine_functional(points):
    choices = [q for q in range(1, 512) if all(parity(p, q) for p in points)]
    need(bool(choices), "common affine odd functional")
    return choices[0]


def geometry(witness, fixture):
    rows, itinerary = roots(fixture), paths(witness)
    need(len(rows) == 104, "104 ordered ports")
    labels = [next(v for v in itinerary[f"X{i}"][0] if v) for i in range(104)]
    targets = [itinerary[f"Y{t}"][-1] for t in range(104)]
    normals = []
    for target in targets:
        need(len(target) == 256, "target is a hyperplane")
        annihilator = [q for q in range(1, 512) if all(not parity(v, q) for v in target)]
        need(len(annihilator) == 1, "unique target normal")
        normals.append(annihilator[0])
    need(len(set(labels)) == len(set(normals)) == 104, "distinct source and target labels")
    odd = [affine_functional(labels), affine_functional(normals)]
    demands = set()
    for t, row in enumerate(rows):
        for s, other in enumerate(rows):
            doubled_inner = sum(a * b for a, b in zip(row, other, strict=True))
            need(doubled_inner % 4 == 0, "integral root Gram entry")
            coefficient = Fraction(t == s) - Fraction(doubled_inner, 8)
            need((labels[s] in targets[t]) == (doubled_inner % 8 == 4), "root/frame pairing")
            if coefficient:
                need(coefficient in (Fraction(1, 2), Fraction(-1, 2)), "correction support")
                demands.add((t, s))
    need(len(demands) == 4992, "4992 correction demands")
    return itinerary, labels, targets, normals, odd, demands


def census(itinerary, labels, targets, demands, cut):
    source = {(t, s) for t, s in demands if any(
        len(frame) > 1 << cut and frame <= targets[t]
        for frame in itinerary[f"X{s}"])}
    target = {(t, s) for t, s in demands if any(
        len(frame) <= 1 << cut and labels[s] in frame
        for frame in itinerary[f"Y{t}"])}
    forced = demands - source - target
    encoded = json.dumps(sorted(forced), separators=(",", ":")).encode()
    result = {"cut": cut, "source_bypass": len(source), "target_bypass": len(target),
              "bypass_union": len(source | target), "forced": len(forced),
              "forced_sha256": hashlib.sha256(encoded).hexdigest()}
    return result, source, target


def carrier(geo, fault=None):
    """Literal local carrier over all three arbitrary logical input columns."""
    itinerary, labels, targets, _, _, demands = geo
    t, source = min(demands)
    line, hyperplane = span([labels[source]]), targets[t]
    full, zero = span([1 << i for i in range(9)]), span([])
    frames = {"X": line, "H": zero, "Y": zero}
    rows = {"X": [Fraction(1), Fraction(0), Fraction(0)],
            "H": [Fraction(0), Fraction(1), Fraction(0)],
            "Y": [Fraction(0), Fraction(0), Fraction(1)]}
    events = [("add", "Y", "H", -1), ("transport", "H", line),
              ("add", "H", "X", 1)]
    events += [("transport", "X", f) for f in itinerary[f"X{source}"][1:]]
    events += [("transport", "Y", f) for f in itinerary[f"Y{t}"][1:]]
    events += [("transport", "H", hyperplane), ("add", "Y", "H", 1),
               ("transport", "H", full), ("add", "H", "X", -1)]
    paid = []
    for event in events:
        op, dst, *args = event
        if fault == "compensation" and event == ("add", "Y", "H", -1):
            continue
        if fault == "cleanup" and event == ("add", "H", "X", -1):
            continue
        if op == "transport":
            after = zero if fault == "frame" and args[0] == hyperplane and dst == "H" else args[0]
            need(frames[dst] < after, "nested carrier transport")
            if dst == "H":
                paid.append(len(after).bit_length() - len(frames[dst]).bit_length())
            frames[dst] = after
        else:
            src, value = args
            need(frames[dst] == frames[src], "common carrier ADD frame")
            if fault == "capture" and dst == "H" and src == "X" and value == 1:
                value = 2
            rows[dst] = [a + value * b for a, b in zip(rows[dst], rows[src], strict=True)]
    need(rows == {"X": [1, 0, 0], "H": [0, 1, 0], "Y": [1, 0, 1]},
         "arbitrary dirty carrier endpoint")
    need(frames == {"X": full, "H": full, "Y": hyperplane}, "carrier endpoint frames")
    need(Counter(paid) == {1: 2, 7: 1}, "legal cheap carrier shape")


def controls(geo, cut_rows):
    itinerary, labels, targets, normals, _, demands = geo
    # Actual bypass witnesses show why charging an original crossing is unsound.
    _, source, target = census(itinerary, labels, targets, demands, 4)
    need(bool(source - target) and bool(target - source), "both bypasses are necessary")
    need(len(demands - source) == 4824 and len(demands - target) == 4824,
         "omitted bypass would overclaim 4824")
    need(cut_rows[3]["forced"] == 4680, "both bypasses restore valid census")
    carrier(geo)
    for fault in ["compensation", "cleanup", "capture", "frame"]:
        try:
            carrier(geo, fault)
        except ValueError:
            pass
        else:
            raise ValueError("accepted dirty carrier fault")
    # The capacity 64 is attained for affine alphabets in a 4->5 crossing.
    a = span([1, 2, 4, 8])
    b = span([1, 2, 4, 8, 16])
    source_odd = [v for v in a if parity(v, 1)]
    dual = [v for v in range(512) if all(not parity(v, w) for w in b)]
    target_odd = [v for v in dual if parity(v, 32)]
    need(len(source_odd) * len(target_odd) == 64, "affine capacity attains 64")
    need((len(a) - 1) * (len(dual) - 1) == 225, "odd premise cannot be dropped")
    need(all(not parity(x, n) for x in source_odd for n in target_odd), "nested rectangle")
    # Every positive composition of nine: no hidden assumption on jump order.
    shapes = []
    for mask in range(256):
        stops = [0] + [i + 1 for i in range(8) if mask >> i & 1] + [9]
        jumps = [y - x for x, y in zip(stops[:-1], stops[1:], strict=True)]
        crossing = next((x, y) for x, y in zip(stops[:-1], stops[1:], strict=True) if x <= 4 < y)
        x, y = crossing
        capacity = 0 if x == 0 or y == 9 else 1 << (7 - (y - x))
        if sorted(jumps) == [1, 1, 7]:
            shapes.append((jumps, capacity))
    need(sorted(c for _, c in shapes) == [0, 0, 1], "all three cheap permutations")
    need(len(set(normals)) == 104 and len(labels) == 104, "capacity alphabet")
    return {"bypass_omissions": 2, "dirty_carrier_faults": 4,
            "affine_capacity_positive": 64, "without_odd_countermodel": 225,
            "positive_compositions": 256, "cheap_shape_capacities": shapes}


def calculate():
    loaded = {}
    for name, digest in INPUTS.items():
        path = ROOT / "research/p104-native-channel/inputs" / name
        need(path.stat().st_size <= 2_000_000, "source capacity before hashing")
        need(hashlib.sha256(path.read_bytes()).hexdigest() == digest, "source hash " + name)
        loaded[name] = read_json(path)
    geo = geometry(loaded["LOWRANK-WITNESS.json"],
                   loaded["P104-FIXTURE.json"]["section4_explicit_P104"])
    itinerary, labels, targets, _, odd, demands = geo
    cut_rows = [census(itinerary, labels, targets, demands, k)[0] for k in range(1, 8)]
    return {"source_hashes": INPUTS, "demands": len(demands), "affine_functionals": odd,
            "cuts": cut_rows, "capacity_by_rank": {str(r): 1 << (7 - r) for r in range(1, 8)},
            "homogeneous_shape_lifetime_floor": max(row["forced"] for row in cut_rows),
            "other_shapes_at_482_lifetimes": (4680 - 482 + 62) // 63,
            "controls": controls(geo, cut_rows)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = calculate()
    expected = read_json(PACKAGE / "EXPECTED.json")
    # JSON normalization makes tuple/list representation irrelevant.
    payload = json.dumps(result, sort_keys=True, indent=2) + "\n"
    need(json.loads(payload) == expected, "complete expected receipt")
    if args.out:
        with args.out.open("x", encoding="utf-8") as output:
            need(output.write(payload) == len(payload), "complete receipt write")
    print("PASS_P104_RELAY_CROSSING_CAPACITY forced=4680 cheap_floor=4680 other_at_482=67")


if __name__ == "__main__":
    main()
