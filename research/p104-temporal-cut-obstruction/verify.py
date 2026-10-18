#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact read-only P104 temporal-cut certificate and adverse controls.

Only the standard library is used. No predecessor producer, native compiler,
network access, Git command, or floating-point acceptance test is used.
"""
from __future__ import annotations

import argparse
import copy
from fractions import Fraction as Q
import hashlib
import importlib.util
from itertools import combinations, product
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
WITNESS = "research/p104-native-channel/inputs/LOWRANK-WITNESS.json"
FIXTURE = "research/p104-native-channel/inputs/P104-FIXTURE.json"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def module(name):
    spec = importlib.util.spec_from_file_location(name, PACKAGE / (name + ".py"))
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def check_sources():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    for item in sources["files"]:
        if item["usage"] == "input":
            digest = hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest()
            require(digest == item["sha256"], "source changed: " + item["path"])


def gram_certificate(fixture):
    """Reconstruct roots, tight-frame identity, correction inverse, witnesses."""
    roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            roots.add(tuple(row))
    for signs in product((-1, 1), repeat=7):
        if signs.count(-1) % 2 == 0:
            roots.add((1, *signs))
    require(len(roots) == 120, "E8 root-line count")
    removed = {tuple(row) for row in fixture["F0"] + fixture["C"]}
    require(len(removed) == 16 and removed <= roots, "two deleted frames")
    ports = sorted(roots - removed)
    require(len(ports) == 104, "P104 port count")
    for i in range(8):
        for j in range(8):
            require(sum(row[i] * row[j] for row in ports) == 104 * (i == j),
                    "doubled coordinate tight-frame identity")
    dots = [[sum(a * b for a, b in zip(x, y)) for y in ports] for x in ports]
    require(all(value % 4 == 0 for row in dots for value in row), "integral Gram")
    gram = [[value // 4 for value in row] for row in dots]
    # A^t A = 26 I proves rank(G)=8 without numerical rank thresholds.
    for i in range(104):
        for j in range(104):
            square = sum(gram[i][k] * gram[k][j] for k in range(104))
            require(square == 26 * gram[i][j], "G squared equals 26 G")
            # Clear denominators in (I-G/2)(I-G/24)=I.
            require(48 * (i == j) - 26 * gram[i][j] + square == 48 * (i == j),
                    "correction inverse")
    for t in range(104):
        z = [26 * (s == t) - gram[s][t] for s in range(104)]
        require(all(sum(row[s] * z[s] for s in range(104)) == 0 for row in gram),
                "lost source direction")
        require(z[t] == 24, "visible correction witness")
    return gram, {
        "ports": 104, "gram_rank": 8, "gram_square_multiplier": 26,
        "correction_rank": 104, "correction_inverse": "I-G/24",
        "kernel_witnesses": 104,
        "nonzero_correction_entries": sum(i != j and gram[i][j] != 0
                                           for i in range(104) for j in range(104)),
    }


def replay_scalar(witness, gram):
    """Independent sparse rational replay over every arbitrary dirty input."""
    initial = witness["initial_frames"]
    rows = {reg: {reg: Q(1)} for reg in initial}
    counts = {}
    for event in witness["program"]:
        op = event[0]
        counts[op] = counts.get(op, 0) + 1
        if op == "transport":
            continue
        if op == "zero":
            require(event[1] not in rows, "private lifetime overlaps")
            rows[event[1]] = {}
        elif op == "erase":
            require(event[1] == "C" and event[1] in rows, "private erasure")
            del rows[event[1]]
        elif op == "copy":
            _, dest, source, _ = event
            require(not rows[dest], "copy into nonzero logical register")
            rows[dest] = dict(rows[source])
        elif op == "add":
            _, dest, source, coefficient, _ = event
            require(dest != source, "self addition outside original word")
            for key, value in list(rows[source].items()):
                result = rows[dest].get(key, Q(0)) + Q(coefficient) * value
                if result:
                    rows[dest][key] = result
                else:
                    rows[dest].pop(key, None)
        else:
            raise ValueError("unknown scalar event")
    require(set(rows) == set(initial), "unclosed private lifetime")
    for reg in rows:
        expected = {reg: Q(1)}
        if reg.startswith("Y"):
            t = int(reg[1:])
            expected.update({"X" + str(s): Q(value, 2)
                             for s, value in enumerate(gram[t]) if value})
        require(rows[reg] == expected, "scalar endpoint " + reg)
    return {"arbitrary_input_columns": len(initial), "events": counts,
            "dirty_helpers_restored": sum(reg[0] in "GDQ" for reg in initial)}


def budget_certificate():
    """Conditional retained-template accounting; no numerical root finding."""
    width, families, calls, centre, missing = 73, 832, 9, 56, 104 - 8
    baseline = (width - 1) * families + calls * centre
    capacity = width * families
    minimum = baseline + calls * missing
    require(baseline < capacity < minimum, "added excess must decide the sign")
    return {
        "model": "checkpoint-preserving insertions; retained fully hosted nine-stage four-pair coverage",
        "width": width, "families": families, "calls": calls,
        "private_copy_rank_per_call": centre,
        "baseline_paid_mass": baseline, "capacity": capacity,
        "baseline_headroom_per_call": str(Q(capacity - baseline, calls)),
        "minimum_added_transport_occurrences_per_call": missing,
        "minimum_completed_paid_mass": minimum,
        "zero_saving_moment_lower_bound": str(Q(minimum, capacity)),
        "minimum_moment_excess": str(Q(minimum - capacity, capacity)),
        "example_208_added_rank_moment_at_zero": str(Q(baseline + calls * 208, capacity)),
        "positive_saving_possible_in_this_model": False,
        "omitted_extra_charge_positive_control": str(Q(baseline, capacity)),
    }


def rejects(function, label, expected_reason):
    try:
        function()
    except ValueError as error:
        require(expected_reason in str(error), "wrong rejection reason for " + label)
        return label
    raise ValueError("control accepted: " + label)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate this package's RESULT.json")
    args = parser.parse_args()
    check_sources()
    witness = json.loads((ROOT / WITNESS).read_text())
    fixture = json.loads((ROOT / FIXTURE).read_text())["section4_explicit_P104"]
    gram, algebra = gram_certificate(fixture)
    scalar = replay_scalar(witness, gram)
    forward = module("temporal")
    backward = module("backward")
    fwd = forward.analyze(witness)
    rev = backward.analyze(witness)
    require([edge["event_index"] for edge in fwd["deleted_edges"]]
            == rev["deleted_transport_indices"], "independent cut agreement")
    require(fwd["paid_profile"] == rev["transport_profile"], "independent invoice agreement")
    require(fwd["source_count"] == fwd["target_count"] == algebra["ports"] == 104,
            "algebra and temporal boundary inventory disagree")
    require(fwd["event_count"] == rev["event_count"] == 4058
            and fwd["event_boundary_count"] == 4059,
            "complete frozen event-boundary coverage")
    require(fwd["deleted_edge_count"] == algebra["gram_rank"] == 8,
            "cut capacity and attained rank disagree")
    require(all(edge["reachable_source_inputs_before_deletion"] == 52
                and edge["reachable_target_outputs_after_deletion"] == 52
                for edge in fwd["deleted_edges"]),
            "private cut source/target support census")
    result = {
        "status": "PASS_P104_TEMPORAL_CUT_OBSTRUCTION",
        "algebra": algebra, "scalar_positive_control": scalar,
        "forward": fwd, "backward": rev,
        "conditional_budget": budget_certificate(), "controls": [],
        "scope": "Sharp rank-eight obstruction for the frozen chronological common-frame access graph; conditional no-saving result for checkpoint-preserving paid transport insertions. No general P104 impossibility, supplier admission or new kappa.",
    }
    bad = copy.deepcopy(witness)
    bad["program"][0][3] = "0"
    result["controls"].append(rejects(lambda: replay_scalar(bad, gram), "missing_dirty_compensation", "scalar endpoint Y0"))
    bad_frame = copy.deepcopy(witness)
    event = next(e for e in bad_frame["program"] if e[0] == "transport")
    event[4] += 1
    result["controls"].append(rejects(lambda: forward.analyze(bad_frame), "incorrect_transport_rank", "positive transport rank"))
    dependent = copy.deepcopy(witness)
    event = next(e for e in dependent["program"]
                 if e[0] == "transport" and len(e[2]) >= 2)
    event[2][1] = event[2][0]
    result["controls"].append(rejects(
        lambda: forward.analyze(dependent), "dependent_frame_basis",
        "dependent frame basis"))
    wrong_gate_frame = copy.deepcopy(witness)
    event = next(e for e in wrong_gate_frame["program"]
                 if e[0] == "add" and e[4] == [])
    event[4] = [1]
    result["controls"].append(rejects(
        lambda: forward.analyze(wrong_gate_frame), "incorrect_common_gate_frame",
        "common-frame addition"))
    wrong_erasure = copy.deepcopy(witness)
    event = next(e for e in wrong_erasure["program"] if e[0] == "erase")
    event[1] = "Q0"
    result["controls"].append(rejects(
        lambda: forward.analyze(wrong_erasure), "erasure_outside_owned_private_role",
        "owned private discard"))
    reordered = copy.deepcopy(witness)
    for endpoint in ("initial_frames", "final_frames"):
        for basis in reordered[endpoint].values():
            basis.reverse()
    for event in reordered["program"]:
        for field in event[2:]:
            if isinstance(field, list):
                field.reverse()
    require(reordered != witness, "basis-order positive control made no change")
    require(forward.analyze(reordered) == fwd,
            "forward certificate depends on listed frame basis order")
    require(backward.analyze(reordered) == rev,
            "independent reverse certificate depends on listed frame basis order")
    result["controls"].append("all_frame_basis_orders_reversed_same_certificate")
    bad_gram = copy.deepcopy(gram)
    bad_gram[0][0] = 0
    result["controls"].append(rejects(lambda: replay_scalar(witness, bad_gram), "incorrect_claimed_endpoint", "scalar endpoint Y0"))
    bypass = copy.deepcopy(witness)
    frame = list(witness["initial_frames"]["X0"])
    bypass["program"][:0] = [
        ["transport", "Y0", [], frame, 1],
        ["add", "Y0", "X0", 1, frame],
        ["transport", "Y0", frame, [], 1],
    ]
    result["controls"].append(rejects(
        lambda: forward.analyze(bypass), "new_paid_bridge_invalidates_old_cut",
        "deleted edges do not cut every source-to-target path"))
    payload = json.dumps(result, sort_keys=True, indent=2) + "\n"
    path = PACKAGE / "RESULT.json"
    if args.write:
        path.write_text(payload)
    else:
        require(json.loads(path.read_text()) == result, "complete certificate differs; review changes")
    print(payload, end="")


if __name__ == "__main__":
    main()
