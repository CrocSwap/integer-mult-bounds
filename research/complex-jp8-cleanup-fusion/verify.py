#!/usr/bin/env python3
"""Exact finite check of shared coefficient work in the selected JP8 cleanup.

Prepared for @ellipsi2 with substantial OpenAI Codex assistance. Apache-2.0.
No selected supplier, emitter, invoice, or frontier is changed by this script.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "66849e1475c930fd7732b1a0067ffee7e1e95f60"
PROVIDER = "research/community-k492-audit/pr626/replay/mixed-global/base/providers/jp8/"
SPEC = "research/complex-k492-owner-repair/data/SPEC.json"
WORK = ("W", 0)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load_sources():
    pins = json.loads((HERE / "SOURCE-PINS.json").read_text(encoding="utf-8"))
    require(pins["base_commit"] == BASE, "wrong base pin")
    result = {}
    for name, entry in pins["files"].items():
        raw = (ROOT / name).read_bytes()
        data = gzip.decompress(raw) if entry["representation"] == "gzip-payload" else raw
        require(hashlib.sha256(data).hexdigest() == entry["sha256"], "source pin mismatch: " + name)
        if name.endswith((".json", ".json.gz")):
            result[name] = json.loads(data)
    return result, pins


def reg(value):
    return tuple(value)


def coefficient(op):
    return Q(op[3], op[4]) if op[0] == "add" else Q(op[2], op[3])


def checked_add(op):
    require(op[0] == "add" and len(op) == 5, "expected an addition")
    require(reg(op[1]) != reg(op[2]), "source/target alias")
    q = coefficient(op)
    require(q != 0 and q.denominator & (q.denominator - 1) == 0, "nonzero dyadic coefficient required")
    return q


def preparation(source, magnitude):
    """The inherited cleared-work binary Horner, including every source read."""
    a, b = magnitude.numerator, magnitude.denominator
    require(a > 0 and b & (b - 1) == 0, "invalid magnitude")
    result = [["clear", WORK]]
    for index, bit in enumerate(bin(a)[2:]):
        if index:
            result.append(["scale", WORK, 2, 1])
        if bit == "1":
            result.append(["add", WORK, source, 1, 1])
    result.extend([["scale", WORK, 1, 2] for _ in range(b.bit_length() - 1)])
    return result


def ordinary(op):
    if op[0] in ("copy", "clear"):
        return [op]
    if op[0] == "scale":
        q = coefficient(op)
        a, b = abs(q.numerator), q.denominator
        require(a and a & (a - 1) == 0 and b & (b - 1) == 0, "scale must be a signed power of two")
        exponent = a.bit_length() - b.bit_length()
        result = [["scale", op[1], 2, 1] for _ in range(max(exponent, 0))]
        result += [["scale", op[1], 1, 2] for _ in range(max(-exponent, 0))]
        if q < 0:
            result.append(["scale", op[1], -1, 1])
        return result
    q = checked_add(op)
    return preparation(op[2], abs(q)) + [["add", op[1], WORK, 1 if q > 0 else -1, 1], ["clear", WORK]]


def group_key(op):
    if op[0] != "add":
        return None
    q = checked_add(op)
    return (reg(op[2]), abs(q)) if abs(q) != 1 else None


def fanout(ops):
    require(len(ops) >= 2, "fanout must contain at least two additions")
    key = group_key(ops[0])
    require(key is not None and all(group_key(op) == key for op in ops), "incompatible fanout")
    source, magnitude = key
    require(source != WORK and all(reg(op[1]) != WORK for op in ops), "work alias")
    result = preparation(source, magnitude)
    result.extend(["add", op[1], WORK, 1 if coefficient(op) > 0 else -1, 1] for op in ops)
    result.append(["clear", WORK])
    return result


def apply(op, rows):
    """Sparse exact row interpreter, independent of the Horner constructor."""
    kind, target = op[0], reg(op[1])
    if kind == "clear":
        rows[target] = {}
    elif kind == "copy":
        rows[target] = dict(rows[reg(op[2])])
    elif kind == "scale":
        q = coefficient(op)
        rows[target] = {j: q * x for j, x in rows[target].items() if q * x}
    elif kind == "add":
        q = checked_add(op)
        row = rows.setdefault(target, {})
        for j, x in list(rows[reg(op[2])].items()):
            value = row.get(j, Q(0)) + q * x
            if value:
                row[j] = value
            else:
                row.pop(j, None)
    else:
        raise ValueError("unknown scalar operation")


def norms_apply(op, norms, prefix):
    target = reg(op[1])
    if op[0] == "clear":
        norms[target] = Q(0)
    elif op[0] == "copy":
        norms[target] = norms[reg(op[2])]
    elif op[0] == "scale":
        norms[target] *= abs(coefficient(op))
    else:
        q, source = checked_add(op), reg(op[2])
        # This also encloses the inherited coefficient preparation for macros.
        prefix = max(prefix, abs(q.numerator) * norms[source])
        norms[target] = norms.get(target, Q(0)) + abs(q) * norms[source]
    return max(prefix, norms[target])


def block_check(ops, replacement=None):
    replacement = fanout(ops) if replacement is None else replacement
    registers = {WORK} | {reg(op[1]) for op in ops} | {reg(op[2]) for op in ops}
    require(all(reg(op[1]) in registers and (op[0] != "add" or reg(op[2]) in registers)
                for op in replacement), "extra scratch or source register")
    expected = {r: {r: Q(1)} for r in registers}
    actual = deepcopy(expected)
    for op in ops:
        apply(op, expected)
    expected[WORK] = {}
    for op in replacement:
        require(op[0] not in ("clear", "scale") or reg(op[1]) == WORK,
                "fanout may only clear or scale coefficient work")
        require(op[0] == "clear" or
                (op[0] == "add" and abs(coefficient(op)) == 1) or
                (op[0] == "scale" and coefficient(op) in (Q(2), Q(1, 2), Q(-1))),
                "unpriced primitive")
        apply(op, actual)
    require(actual == expected, "fanout arbitrary-input map or work clearing mismatch")

    # Formal nonnegative coefficients in independent register norm variables.
    # Target trace must match at each accumulation, not only at the endpoint.
    reference_norm = {r: {r: Q(1)} for r in registers}
    candidate_norm = deepcopy(reference_norm)
    target_steps = iter(ops)
    next_target = next(target_steps, None)
    for primitive in replacement:
        positive = deepcopy(primitive)
        if positive[0] == "add":
            positive[3] = abs(positive[3])
        elif positive[0] == "scale":
            positive[2] = abs(positive[2])
        apply(positive, candidate_norm)
        if primitive[0] == "add" and reg(primitive[1]) != WORK:
            require(next_target is not None, "extra target update")
            original = deepcopy(next_target)
            original[3] = abs(original[3])
            apply(original, reference_norm)
            require(all(candidate_norm[r] == reference_norm[r] for r in registers - {WORK}),
                    "target prefix envelope changed")
            next_target = next(target_steps, None)
        # Coefficient work can never exceed a * norm(source), the original
        # Horner bound. Check it symbolically at every primitive boundary.
        source, q = group_key(ops[0])
        bound = {source: Q(q.numerator)}
        require(all(value <= bound.get(j, Q(0)) for j, value in candidate_norm[WORK].items()),
                "coefficient prefix envelope exceeded")
    require(next_target is None, "missing target update")
    require(len(replacement) <= sum(len(ordinary(op)) for op in ops), "primitive cost increased")


def canonical_scalar(e, backward):
    if e[0] == "add":
        t, s, a, b = e[1:5]
        if backward:
            t, s, a = s, t, -a
        return ["add", ["L", t], ["L", s], a, b]
    t, a, b = e[1:4]
    if backward:
        a, b = b, a
    return ["scale", ["L", t], a, b]


def check_program(events, canonical, backward):
    n = 2 * canonical["v"] + canonical["R"]
    rows = {("L", r): {r: Q(1)} for r in range(n)}
    norms = {r: Q(1) for r in rows}
    rows[WORK], norms[WORK] = {}, Q(0)
    prefix = Q(1)
    phase = None
    cleanup = 0
    groups = []
    old_cost = new_cost = old_cleanup_cost = new_cleanup_cost = macros = 0
    paid = Counter()
    index = 0
    while index < len(events):
        event = events[index]
        if event[0] == "phase":
            phase = event[1]
            require(not rows[WORK], "work leaks across phase boundary")
        elif event[0] in ("climb", "center"):
            paid[event[-1]] += 1
            require(not rows[WORK], "work leaks across recursive child")
        elif event[0] == "scalar":
            op = event[1]
            run = [op]
            if phase == "full_frame_cleanup":
                require(event[2] == 1, "wrong cleanup frame")
                key = group_key(op)
                if key is not None:
                    j = index + 1
                    while j < len(events) and events[j][0] == "scalar" and events[j][2] == 1 and group_key(events[j][1]) == key:
                        run.append(events[j][1])
                        j += 1
                expected = [canonical_scalar(e, backward) for e in canonical["cleanup"][cleanup:cleanup + len(run)]]
                require(run == expected, "emitted cleanup detached from canonical word")
                for member in run:
                    touched = [member[1]] + ([member[2]] if member[0] == "add" else [])
                    require(all(r[0] == "L" and canonical["final"][r[1]] == 1 for r in touched), "non-FULL cleanup register")
            reference = sum(len(ordinary(member)) for member in run)
            if len(run) > 1:
                replacement = fanout(run)
                block_check(run, replacement)
                old_norms, old_prefix = dict(norms), prefix
                for member in run:
                    old_prefix = norms_apply(member, old_norms, old_prefix)
                for primitive in replacement:
                    apply(primitive, rows)
                    prefix = norms_apply(primitive, norms, prefix)
                require(norms == old_norms and prefix == old_prefix, "full-program prefix envelope changed")
                amount = len(replacement)
                groups.append({"cleanup_start": cleanup, "length": len(run), "source": run[0][2][1],
                               "abs_coefficient": str(abs(coefficient(run[0]))),
                               "reference_primitives_per_component": reference,
                               "shared_primitives_per_component": amount})
            else:
                if op[0] in ("copy", "clear") and reg(op[1]) not in rows:
                    rows[reg(op[1])], norms[reg(op[1])] = {}, Q(0)
                apply(op, rows)
                prefix = norms_apply(op, norms, prefix)
                amount = reference
            macros += len(run)
            old_cost += 2 * reference
            new_cost += 2 * amount
            if phase == "full_frame_cleanup":
                cleanup += len(run)
                old_cleanup_cost += 2 * reference
                new_cleanup_cost += 2 * amount
            index += len(run) - 1
        elif event[0] in ("adapter", "residual_adapter"):
            require(not rows[WORK], "work leaks across wrapper")
        else:
            raise ValueError("unknown event")
        index += 1
    require(cleanup == len(canonical["cleanup"]), "incomplete cleanup coverage")
    v = canonical["v"]
    for r in range(n):
        expected = {r: Q(1)}
        if backward and r < v:
            expected[v + r] = Q(-1)
        elif not backward and v <= r < 2 * v:
            expected[r - v] = Q(1)
        require(rows["L", r] == expected, "full-program column identity failed")
    require(all(not row for r, row in rows.items() if r[0] != "L"), "private work not cleared")
    require(dict(paid) == {int(r): count for r, count in canonical["local_profile"].items()}, "paid profile changed")
    return {"all_input_columns": n, "dirty_helpers": canonical["R"], "scalar_macros": macros,
            "original_real_primitives": old_cost, "shared_real_primitives": new_cost,
            "saved_real_primitives": old_cost - new_cost,
            "original_cleanup_real_primitives": old_cleanup_cost,
            "shared_cleanup_real_primitives": new_cleanup_cost,
            "prefix_l1": str(prefix), "groups": groups,
            "paid_profile": {str(r): count for r, count in sorted(paid.items())}}


def expect_rejection(name, operation):
    try:
        operation()
    except ValueError:
        return name
    raise ValueError("negative control survived: " + name)


def controls():
    s, a, b = ("L", 0), ("L", 1), ("L", 2)
    ops = [["add", a, s, 3, 2], ["add", b, s, -3, 2]]
    correct = fanout(ops)
    block_check(ops)
    cases = []
    wrong_sign = deepcopy(correct)
    wrong_sign[-2][3] *= -1
    cases.append(("wrong_accumulation_sign", lambda: block_check(ops, wrong_sign)))
    cases.append(("missing_final_clear", lambda: block_check(ops, correct[:-1])))
    cases.append(("missing_initial_clear_arbitrary_work", lambda: block_check(ops, correct[1:])))
    missing_half = [p for p in correct if not (p[0] == "scale" and p[2:] == [1, 2])]
    cases.append(("wrong_coefficient_preparation", lambda: block_check(ops, missing_half)))
    cases.append(("changed_source", lambda: fanout([ops[0], ["add", b, a, -3, 2]])))
    cases.append(("source_target_alias", lambda: fanout([ops[0], ["add", s, s, -3, 2]])))
    cases.append(("changed_magnitude", lambda: fanout([ops[0], ["add", b, s, -5, 2]])))
    # Endpoint-neutral excursion: double then halve prepared work. This must
    # fail the prefix check, not just a digest or a final-map comparison.
    large_ops = [["add", a, s, 3, 1], ["add", b, s, 3, 1]]
    large = fanout(large_ops)
    excursion = large[:-3] + [["scale", WORK, 2, 1], ["scale", WORK, 1, 2]] + large[-3:]
    cases.append(("endpoint_neutral_prefix_growth", lambda: block_check(large_ops, excursion)))
    signed_excursion = large[:-3] + [["scale", WORK, -1, 1], ["scale", WORK, 2, 1],
                                    ["scale", WORK, 1, 2], ["scale", WORK, -1, 1]] + large[-3:]
    cases.append(("endpoint_neutral_signed_prefix_growth", lambda: block_check(large_ops, signed_excursion)))
    live_excursion = large[:1] + [["scale", a, 2, 1], ["scale", a, 1, 2]] + large[1:]
    cases.append(("endpoint_neutral_live_prefix_growth", lambda: block_check(large_ops, live_excursion)))
    return [expect_rejection(name, operation) for name, operation in cases]


def commuting_census(cleanup):
    """Complete first-obstruction scan for the initial, unsuccessful hypothesis."""
    pairs = []
    for i, op in enumerate(cleanup):
        if op[0] != "add":
            continue
        target, source = op[1:3]
        for j in range(i + 1, len(cleanup)):
            other = cleanup[j]
            if other[-1] != op[-1]:
                break
            if other[0] == "add" and other[1:3] == [target, source]:
                pairs.append([i, j])
                break
            if other[0] == "scale":
                if other[1] in (target, source):
                    break
            elif other[1] == source or other[2] == target:
                break
    return {"cleanup_gates": len(cleanup), "same_edge_pairs_before_first_obstruction": pairs}


def verify():
    sources, pins = load_sources()
    canonical = sources[PROVIDER + "CANONICAL-WORD.json.gz"]
    programs = sources[PROVIDER + "LOCAL-PROGRAMS.json.gz"]
    spec = sources[SPEC]["providers"]["jp8"]
    require((canonical["v"], canonical["R"], canonical["h"]) == (112, 492, 9), "wrong supplier")
    for filename in ("CANONICAL-WORD.json.gz", "LOCAL-PROGRAMS.json.gz"):
        require(pins["files"][PROVIDER + filename]["sha256"] == spec["artifact_semantic_sha256"][filename], "SPEC payload binding mismatch")
    result = {"status": "PASS_JP8_SHARED_COEFFICIENT_CLEANUP", "base_commit": BASE,
              "assignment_seed": 31, "scope": "finite primitive lowering; no new kappa", "programs": {}}
    result["initial_commuting_scan"] = commuting_census(canonical["cleanup"])
    for name, backward in (("forward", False), ("backward", True)):
        require(digest(programs[name]) == spec["program_hashes"][name], "SPEC event binding mismatch")
        record = check_program(programs[name], canonical, backward)
        inherited = spec["complete_contract"]["local"][name]
        require(record["original_real_primitives"] == inherited["real_component_primitives"], "baseline cost mismatch")
        require(record["prefix_l1"] == inherited["prefix_l1"], "inherited prefix bound mismatch")
        result["programs"][name] = record
        print("checked", name, "columns=", record["all_input_columns"], "groups=", len(record["groups"]), flush=True)
    result["negative_controls"] = controls()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", type=Path, help="write a new receipt exclusively; never overwrite an existing file")
    args = parser.parse_args()
    result = verify()
    if args.write_receipt:
        with args.write_receipt.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(result, handle, indent=2)
            handle.write("\n")
    else:
        expected = json.loads((HERE / "EXPECTED.json").read_text(encoding="utf-8"))
        require(result == expected, "committed receipt mismatch")
    forward = result["programs"]["forward"]
    print(result["status"], "groups=" + str(len(forward["groups"])),
          "saved=" + str(forward["saved_real_primitives"]), "columns=716 orientations=2",
          "controls=" + str(len(result["negative_controls"])))


if __name__ == "__main__":
    main()
