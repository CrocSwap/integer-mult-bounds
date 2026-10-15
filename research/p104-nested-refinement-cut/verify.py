#!/usr/bin/env python3
"""Exact interval premises for the P104 nested-refinement cut.

Tairitsu-Aya, with substantial OpenAI Codex assistance. Apache-2.0.
No producer imports; no floating point; explicit guards also run under -O.
The transcript/rank implication is the written proof in README.md.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from functools import lru_cache
import hashlib
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SOURCE = "research/p104-native-channel/inputs/LOWRANK-WITNESS.json"
SHA256 = "0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e"
PASS = "PASS_P104_NESTED_REFINEMENT_CUT"


def require(condition, message):
    if not condition:
        raise ValueError(message)


@lru_cache(maxsize=None)
def reduced(vectors):
    """Unique high-pivot reduced basis; dependencies are permitted here."""
    rows = {}
    for value in vectors:
        require(type(value) is int and 0 < value < 512, "nine-bit nonzero vector")
        x = value
        for bit in sorted(rows, reverse=True):
            if x & (1 << bit):
                x ^= rows[bit]
        if not x:
            continue
        bit = x.bit_length() - 1
        for other in rows:
            if rows[other] & (1 << bit):
                rows[other] ^= x
        rows[bit] = x
    return tuple(rows[bit] for bit in sorted(rows, reverse=True))


def basis(values):
    result = reduced(tuple(values))
    require(len(result) == len(values), "independent input frame")
    return result


@lru_cache(maxsize=None)
def contains(space, vector):
    for row in space:
        if vector & (1 << (row.bit_length() - 1)):
            vector ^= row
    return vector == 0


@lru_cache(maxsize=None)
def included(smaller, larger):
    return all(contains(larger, x) for x in smaller)


def elements(space):
    out = [0]
    for x in space:
        out += [y ^ x for y in out]
    return sorted(out)


def numeric_names(names, prefix):
    return sorted((r for r in names if r.startswith(prefix)), key=lambda r: int(r[1:]))


def frame_trace(witness):
    initial = {r: basis(v) for r, v in witness["initial_frames"].items()}
    final = {r: basis(v) for r, v in witness["final_frames"].items()}
    require(set(initial) == set(final) and len(initial) == 280, "280 persistent roles")
    require(numeric_names(initial, "X") == [f"X{i}" for i in range(104)], "source roles")
    require(numeric_names(final, "Y") == [f"Y{i}" for i in range(104)], "target roles")
    current = dict(initial)
    phases = defaultdict(list)
    for name, space in initial.items():
        phases[name].append(space)
    transports = []
    lifetimes = []
    active = None
    operations = Counter()
    for index, event in enumerate(witness["program"]):
        op, reg = event[:2]
        operations[op] += 1
        if op == "transport":
            old, new, rank = basis(event[2]), basis(event[3]), event[4]
            require(current[reg] == old, "transport continuity")
            require(included(old, new) or included(new, old), "nested transport")
            require(type(rank) is int and rank == abs(len(old) - len(new)) > 0,
                    "positive dimension-difference rank")
            transports.append((index, reg, old, new, rank))
            current[reg] = new
            phases[reg].append(new)
            if reg == "C":
                require(active is not None, "private transport owns a lifetime")
                active.append(index)
        elif op == "zero":
            require(reg == "C" and reg not in current and active is None, "fresh private lifetime")
            current[reg] = basis(event[2])
            active = [index]
        elif op == "erase":
            require(reg == "C" and active is not None and current[reg] == basis(event[2]),
                    "private discard frame")
            active.append(index)
            require(len(active) == 4, "one initialization, copy, transport, discard per lifetime")
            lifetimes.append(active)
            active = None
            del current[reg]
        elif op in ("add", "copy"):
            src = event[2]
            require(reg != src and current[reg] == current[src] == basis(event[-1]),
                    "literal common-chart operation")
            if op == "copy":
                require(reg == "C" and active is not None and len(active) == 1,
                        "private copy follows initialization")
                active.append(index)
        else:
            raise ValueError("unknown source event")
    require(active is None and current == final, "complete frame endpoints")
    require(len(lifetimes) == 8, "eight owned private lifetimes")
    return initial, final, phases, transports, lifetimes, operations


def geometry(transports):
    drops = [row for row in transports if len(row[2]) > len(row[3])]
    require(len(drops) == 8, "eight descending occurrences")
    require(all(reg == "C" and len(old) == 8 and len(new) == 1 and rank == 7
                for _, reg, old, new, rank in drops), "eight private hyperplane-to-line drops")
    lines = tuple(row[3][0] for row in drops)
    span = basis(lines)
    require(len(span) == 8, "independent survivor lines")
    for _, _, old, new, _ in drops:
        require(sum(contains(old, a) for a in lines) == 1, "one survivor in each drop hyperplane")
        require(not included(old, span) and included(new, span), "drop enters survivor span")
    return drops, lines, span


def target_side(space, lines, survivor_span):
    return len(space) < 9 and (included(space, survivor_span)
                              or sum(contains(space, a) for a in lines) >= 2)


def upward_case(lower, upper, lines, survivor_span):
    require(len(lower) < len(upper) and included(lower, upper), "strict upward interval")
    if sum(contains(upper, a) for a in lines) <= 1:
        return "upper_at_most_one_survivor"
    if included(upper, survivor_span):
        return "upper_in_survivor_span"
    if sum(contains(lower, a) for a in lines) >= 2:
        return "lower_at_least_two_survivors"
    if len(lower) == 8 and len(upper) == 9:
        return "last_step_to_full"
    raise ValueError("uncovered upward interval: the claimed cut is not established")


def slots(phases, transports, prefix):
    result = []
    for reg in numeric_names(phases, prefix):
        for space in phases[reg]:
            result.append((space, space, len(space), len(space)))
    for _, reg, lower, upper, _ in transports:
        if not reg.startswith(prefix):
            continue
        require(included(lower, upper), "upward data itinerary")
        if len(upper) - len(lower) > 1:
            result.append((lower, upper, len(lower) + 1, len(upper) - 1))
    return result


def common_chart(first, second):
    a, b, amin, amax = first
    c, d, cmin, cmax = second
    if not included(a, d) or not included(c, b):
        return False
    join_dimension = len(reduced(a + c))
    intersection_dimension = len(b) + len(d) - len(reduced(b + d))
    return max(join_dimension, amin, cmin) <= min(intersection_dimension, amax, cmax)


def analyze(witness):
    initial, final, phases, transports, lifetimes, operations = frame_trace(witness)
    drops, lines, span = geometry(transports)
    classes = defaultdict(list)
    for index, _, lower, upper, _ in transports:
        key = ("private_downward_interval" if len(lower) > len(upper)
               else upward_case(lower, upper, lines, span))
        classes[key].append(index)
    inside, outside = [], []
    for reg in numeric_names(initial, "X"):
        require(len(initial[reg]) == 1, "singleton source entry")
        (inside if target_side(initial[reg], lines, span) else outside).append(reg)
    targets = numeric_names(final, "Y")
    require(all(len(final[r]) == 8 and target_side(final[r], lines, span) for r in targets),
            "all target endpoints lie on target side")
    xs, ys = slots(phases, transports, "X"), slots(phases, transports, "Y")
    direct_count = sum(common_chart(x, y) for x in xs for y in ys)
    require(direct_count == 0, "no direct source/target common chart under refinements")
    signature = [[i, reg, elements(a), elements(b), rank] for i, reg, a, b, rank in transports]
    return {
        "schema_version": 1,
        "status": PASS,
        "source": {"path": SOURCE, "sha256": SHA256},
        "ambient_binary_dimension": 9,
        "original_events": sum(operations.values()),
        "original_operations": dict(sorted(operations.items())),
        "transport_occurrences": len(transports),
        "transport_signature_sha256": hashlib.sha256(json.dumps(signature, separators=(",", ":")).encode()).hexdigest(),
        "survivor_lines_in_drop_order": list(lines),
        "survivor_span_reduced_basis": list(span),
        "drop_hyperplanes": [list(row[2]) for row in drops],
        "survivors_per_drop_hyperplane": [sum(contains(row[2], a) for a in lines) for row in drops],
        "private_lifetimes": lifetimes,
        "interval_classes": {key: value for key, value in sorted(classes.items())},
        "interval_class_counts": {key: len(value) for key, value in sorted(classes.items())},
        "initial_sources_on_target_side": inside,
        "initial_sources_on_other_side": outside,
        "target_survivor_count_histogram": dict(sorted(Counter(str(sum(contains(final[r], a) for a in lines)) for r in targets).items())),
        "rank_bounds_in_array_units": {
            "other_side_source_count": len(outside),
            "other_side_source_transfer_upper_bound": len(drops),
            "all_source_transfer_upper_bound": len(inside) + len(drops),
            "identity_required": len(inside) + len(outside),
            "sharpness_claimed": False,
        },
        "direct_read_gate": {
            "source_slots": len(xs), "target_slots": len(ys),
            "slot_pairs": len(xs) * len(ys), "common_chart_pairs": direct_count,
            "timing_constraints_used": False,
        },
    }


def controls(witness):
    _, _, _, transports, _, _ = frame_trace(witness)
    drops, lines, span = geometry(transports)
    rejected = []

    def reject(name, call):
        try:
            call()
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("negative control did not reject: " + name)

    full = basis([1 << i for i in range(9)])
    outsider = next(x for x in range(1, 512) if not contains(span, x))
    lower = basis([outsider])
    upper = basis([outsider, lines[0], lines[1]])
    require(not target_side(lower, lines, span) and target_side(upper, lines, span),
            "actual new-interval crossing counterexample")
    reject("new_upward_route_crosses_cut", lambda: upward_case(lower, upper, lines, span))
    reject("zero_to_full_can_cross_back_and_forth", lambda: upward_case((), full, lines, span))
    reject("nonnested_replacement", lambda: upward_case(lower, basis(lines[:2]), lines, span))
    reject("dependent_survivors", lambda: basis(lines[:-1] + lines[:1]))
    reject("ninth_descending_occurrence", lambda: geometry(transports + [drops[0]]))
    changed = list(transports)
    where = next(i for i, row in enumerate(changed) if row == drops[0])
    i, reg, _, line, _ = changed[where]
    changed[where] = (i, reg, full, line, 8)
    reject("unretained_full_to_line_drop", lambda: geometry(changed))
    require(not target_side(full, lines, span), "full chart is on other side")
    require(all(not target_side(row[2], lines, span) for row in drops), "gather hyperplanes on other side")
    require(all(target_side(basis([a]), lines, span) for a in lines), "survivor lines on target side")
    inside_non_survivor = next(x for x in elements(span) if x and x not in lines)
    require(target_side(basis([inside_non_survivor]), lines, span), "inside-span sources cannot be counted as outside")
    same = (lower, lower, 1, 1)
    require(common_chart(same, same), "direct-read positive control")
    require(common_chart(((), upper, 1, 2), (lower, upper, 1, 2)), "strict-refinement positive control")
    require(not common_chart((lower, lower, 1, 1), (basis([lines[0]]), basis([lines[0]]), 1, 1)),
            "equal dimensions do not mean equal subspaces")
    # An equivalent presentation must not change the certificate.
    alternate = json.loads(json.dumps(witness))

    def rebase(v):
        values = list(reversed(v))
        if len(values) > 1:
            values[0] ^= values[1]
        return values

    for group in ("initial_frames", "final_frames"):
        alternate[group] = {r: rebase(v) for r, v in alternate[group].items()}
    for event in alternate["program"]:
        if event[0] == "transport":
            event[2], event[3] = rebase(event[2]), rebase(event[3])
        else:
            event[-1] = rebase(event[-1])
    require(analyze(alternate) == analyze(witness), "basis-presentation invariance")
    return rejected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="write computed receipt exclusively; otherwise compare RESULT.json")
    args = parser.parse_args()
    raw = (ROOT / SOURCE).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == SHA256, "source SHA256")
    witness = json.loads(raw)
    result = analyze(witness)
    checks = controls(witness)
    if args.out:
        with args.out.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(result, indent=2) + "\n")
    else:
        require(result == json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8")), "exact receipt")
    print(PASS + ": 56-array total upper bound; 8 from 56 outside sources; 529984 direct-read pairs reject")
    print("Controls: " + ", ".join(checks) + "; basis presentation and positive/counter-controls pass")


if __name__ == "__main__":
    main()
