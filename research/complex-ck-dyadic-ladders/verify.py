#!/usr/bin/env python3
"""Exact offline CK ladder verification; standard library, Python 3.11+."""

import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROVIDER = "research/community-k492-audit/pr626/replay/mixed-global/base/providers/ck"
SPEC = "research/complex-k492-owner-repair/data/SPEC.json"
SELECTED = "certificates/selected-result.json"
BASE = "66849e1475c930fd7732b1a0067ffee7e1e95f60"
spec = importlib.util.spec_from_file_location("ck_ladder_circuit", HERE / "circuit.py")
circuit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(circuit)
WORK = ("W", 0)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def read_source(path):
    data = (ROOT / path).read_bytes()
    return gzip.decompress(data) if path.endswith(".gz") else data


def load_sources():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    require(manifest["base_commit"] == BASE, "wrong base pin")
    for path, expected in manifest["sha256"].items():
        require(hashlib.sha256(read_source(path)).hexdigest() == expected, "source pin: " + path)
    selected = json.loads(read_source(SELECTED))
    require(selected["audited_source_head"] == "660de893d27bb7abd1d5b01b1640207528a5c851", "selected source")
    provider = json.loads(read_source(SPEC))["providers"]["ck"]
    word = json.loads(read_source(PROVIDER + "/CANONICAL-WORD.json.gz"))
    programs = json.loads(read_source(PROVIDER + "/LOCAL-PROGRAMS.json.gz"))
    checks = json.loads(read_source(PROVIDER + "/LOCAL-CHECKS.json"))
    audit = json.loads(read_source(PROVIDER + "/INDEPENDENT-LOCAL-REPLAY.json"))
    for name, value in [("CANONICAL-WORD.json.gz", word), ("LOCAL-PROGRAMS.json.gz", programs),
                        ("LOCAL-CHECKS.json", checks)]:
        require(digest(value) == provider["artifact_semantic_sha256"][name], "SPEC binding: " + name)
    require((word["v"], word["R"], word["h"]) == (112, 492, 9), "CK dimensions")
    require(set(programs) == {"forward", "backward"}, "orientation domain")
    for orientation, events in programs.items():
        require(digest(events) == provider["program_hashes"][orientation] == checks[orientation]["sha256"],
                "event-stream binding")
    return selected, word, programs, checks, audit


def original_count(op):
    """Independent arithmetic recount of the selected primitive invoice."""
    if op[0] in ("clear", "copy"):
        return 1
    q = Q(op[3], op[4]) if op[0] == "add" else Q(op[2], op[3])
    a, b = abs(q.numerator), q.denominator
    require(a > 0 and b & (b - 1) == 0, "dyadic domain")
    if op[0] == "scale":
        require(a & (a - 1) == 0, "scale domain")
        return abs(a.bit_length() - b.bit_length()) + int(q < 0)
    require(op[0] == "add" and op[1] != op[2], "addition domain")
    return 3 + (a.bit_length() - 1) + a.bit_count() + (b.bit_length() - 1)


def inspect_block(events, primitives, claimed_count=None):
    """Check the exact source coefficient at EVERY ordered target update.

    This checker does not call the constructor's key, prepare or transition
    functions. The work stream initially contains an arbitrary unknown value.
    Its normalized coefficient and every live-register write are checked.
    """
    require(len(events) >= 2, "block too short")
    source = tuple(events[0][1][2])
    frame = events[0][2]
    targets, values = [], []
    for e in events:
        require(e[0] == "scalar" and e[1][0] == "add", "non-addition in block")
        op = e[1]
        q = Q(op[3], op[4])
        require(tuple(op[2]) == source and e[2] == frame, "source/frame boundary")
        require(op[1][0] == op[2][0] == "L" and tuple(op[1]) != source, "source write or private alias")
        require(q != 0 and abs(q) != 1 and q.denominator & (q.denominator - 1) == 0, "coefficient domain")
        targets.append(tuple(op[1]))
        values.append(q)
    for a, b in zip(values, values[1:]):
        ratio = abs(b / a)
        require(ratio.numerator & (ratio.numerator - 1) == 0 and
                ratio.denominator & (ratio.denominator - 1) == 0, "non-power-of-two ratio")
    bound = max(abs(q.numerator) for q in values)
    coefficient, seen, peak = None, 0, Q(0)
    for p in primitives:
        tag, target = p[:2]
        if target == WORK:
            if tag == "clear":
                coefficient = Q(0)
            else:
                require(coefficient is not None, "arbitrary incoming work not erased")
                if tag == "double":
                    coefficient *= 2
                elif tag == "half":
                    coefficient /= 2
                else:
                    require(tag == "add" and p[2:] == (source, 1), "invalid work operation")
                    coefficient += 1
            peak = max(peak, abs(coefficient))
            require(abs(coefficient) <= bound, "work prefix exceeds original Horner envelope")
        else:
            require(seen < len(values), "extra target write")
            require(p == ("add", targets[seen], WORK, 1 if values[seen] > 0 else -1),
                    "target update order/sign changed")
            require(coefficient == abs(values[seen]), "wrong coefficient at accumulation")
            seen += 1
    require(seen == len(values) and coefficient == 0, "missing target update or final clearing")
    if claimed_count is not None:
        require(len(primitives) == claimed_count, "incorrect primitive charge")
    return peak, bound


def independent_inventory(events):
    """Reconstruct maximal runs from adjacent-edge relations and exact costs."""
    def eligible(e):
        if e[0] != "scalar" or e[1][0] != "add":
            return False
        op = e[1]
        q = Q(op[3], op[4])
        return (op[1][0] == op[2][0] == "L" and op[1] != op[2] and
                q != 0 and abs(q) != 1 and q.denominator & (q.denominator - 1) == 0)

    def connected(a, b):
        if not eligible(a) or not eligible(b) or a[2] != b[2] or a[1][2] != b[1][2]:
            return False
        ratio = abs(Q(b[1][3], b[1][4]) / Q(a[1][3], a[1][4]))
        return (ratio.numerator & (ratio.numerator - 1) == 0 and
                ratio.denominator & (ratio.denominator - 1) == 0)

    starts = [0] + [i for i in range(1, len(events)) if not connected(events[i - 1], events[i])]
    stops = starts[1:] + [len(events)]
    selected, savings = [], []
    for i, j in zip(starts, stops):
        if j - i < 2:
            continue
        total, variable = 0, 0
        for a, b in zip(events[i:j - 1], events[i + 1:j]):
            qa, qb = abs(Q(a[1][3], a[1][4])), abs(Q(b[1][3], b[1][4]))
            ratio = qb / qa
            steps = abs(ratio.numerator.bit_length() - ratio.denominator.bit_length())
            saved = max(0, original_count(b[1]) - 1 - steps)
            total += saved
            variable += saved if qa != qb else 0
        if variable:
            selected.append((i, j))
            savings.append(2 * total)
    return selected, savings


def initialize(word):
    n = 2 * word["v"] + word["R"]
    registers = [("L", r) for r in range(n)]
    registers += [("C", r) for r in range(len(word["centers"]))] + [WORK]
    return {r: {i: Q(1)} for i, r in enumerate(registers)}, {r: Q(1) for r in registers}


def row_add(rows, norms, target, source, q):
    for j, x in list(rows[source].items()):
        value = rows[target].get(j, Q(0)) + q * x
        if value:
            rows[target][j] = value
        else:
            rows[target].pop(j, None)
    norms[target] += abs(q) * norms[source]


def primitive_step(rows, norms, p):
    tag, target = p[:2]
    if tag == "clear":
        rows[target], norms[target] = {}, Q(0)
    elif tag == "copy":
        rows[target], norms[target] = dict(rows[p[2]]), norms[p[2]]
    elif tag == "add":
        row_add(rows, norms, target, p[2], Q(p[3]))
    else:
        require(tag in ("double", "half", "negate"), "unknown primitive")
        q = {"double": Q(2), "half": Q(1, 2), "negate": Q(-1)}[tag]
        rows[target] = {j: q * x for j, x in rows[target].items()}
        norms[target] *= abs(q)
    return norms[target]


def macro_step(rows, norms, op):
    target = tuple(op[1])
    if op[0] in ("clear", "copy"):
        p = (op[0], target) + ((tuple(op[2]),) if op[0] == "copy" else ())
        return primitive_step(rows, norms, p)
    if op[0] == "scale":
        q = Q(op[2], op[3])
        old = norms[target]
        rows[target] = {j: q * x for j, x in rows[target].items()}
        norms[target] *= abs(q)
        return max(old, norms[target])
    source, q = tuple(op[2]), Q(op[3], op[4])
    # Binary Horner reaches |numerator| times the unchanged source norm.
    peak = abs(q.numerator) * norms[source]
    row_add(rows, norms, target, source, q)
    rows[WORK], norms[WORK] = {}, Q(0)
    return max(peak, norms[target])


def replay(events, word, blocks=None):
    rows, norms = initialize(word)
    blocks = dict(blocks or [])
    prefix, primitives, i = Q(1), 0, 0
    while i < len(events):
        if i in blocks:
            j = blocks[i]
            stream = circuit.lower_block(events[i:j])
            for p in stream:
                prefix = max(prefix, primitive_step(rows, norms, p))
            primitives += len(stream)
            i = j
            continue
        event = events[i]
        if event[0] == "scalar":
            prefix = max(prefix, macro_step(rows, norms, event[1]))
            primitives += original_count(event[1])
        i += 1
    return rows, prefix, 2 * primitives


def endpoint(rows, word, orientation):
    v, n = word["v"], 2 * word["v"] + word["R"]
    for r in range(n):
        expected = {r: Q(1)}
        if orientation == "forward" and v <= r < 2 * v:
            expected[r - v] = Q(1)
        if orientation == "backward" and r < v:
            expected[v + r] = Q(-1)
        require(rows["L", r] == expected, "full scalar endpoint: " + str(r))
    require(all(not row for r, row in rows.items() if r[0] != "L"), "private input/output leakage")


def controls():
    fixture = [["scalar", ["add", ["L", t], ["L", 0], a, b], 7]
               for t, a, b in [(1, 1, 2), (2, -1, 4), (1, 1, 8), (3, 1, 4)]]
    good = circuit.lower_block(fixture)
    inspect_block(fixture, good)
    results = []

    def reject(name, function):
        try:
            function()
        except ValueError:
            results.append(name)
        else:
            raise ValueError("negative control accepted: " + name)

    reject("missing_initial_clear", lambda: inspect_block(fixture, good[1:]))
    reject("missing_final_clear", lambda: inspect_block(fixture, good[:-1]))
    bad = list(good)
    i = next(i for i, p in enumerate(bad) if p[0] == "half")
    bad[i] = ("double", WORK)
    reject("wrong_scale_direction", lambda: inspect_block(fixture, bad))
    signed = list(good)
    i = next(i for i, p in enumerate(signed) if p[0] == "add" and p[1] != WORK)
    signed[i] = (*signed[i][:3], -signed[i][3])
    reject("wrong_target_sign", lambda: inspect_block(fixture, signed))
    reordered = list(good)
    indices = [i for i, p in enumerate(reordered) if p[0] == "add" and p[1] != WORK]
    reordered[indices[0]], reordered[indices[1]] = reordered[indices[1]], reordered[indices[0]]
    reject("target_order", lambda: inspect_block(fixture, reordered))
    reject("undercharged_work", lambda: inspect_block(fixture, good, len(good) - 1))
    i = indices[0]
    excursion = good[:i] + [("double", WORK)] * 3 + [("half", WORK)] * 3 + good[i:]
    reject("endpoint_neutral_prefix_excursion", lambda: inspect_block(fixture, excursion))
    for name, mutate in [
        ("frame_boundary", lambda e: e[1].__setitem__(2, 8)),
        ("source_boundary", lambda e: e[1][1].__setitem__(2, ["L", 4])),
        ("source_write", lambda e: e[1][1].__setitem__(1, ["L", 0])),
        ("non_dyadic_coefficient", lambda e: e[1][1].__setitem__(4, 3)),
        ("non_power_two_ratio", lambda e: e[1][1].__setitem__(3, 3)),
    ]:
        changed = copy.deepcopy(fixture)
        mutate(changed)
        reject(name, lambda: inspect_block(changed, good))
    boundary = fixture[:2] + [["phase", "forbidden"]] + fixture[2:]
    reject("phase_boundary", lambda: inspect_block(boundary, good))
    # Equal-only runs are deliberately outside the selected new mechanism.
    equal = copy.deepcopy(fixture)
    for e in equal:
        e[1][3:5] = [1, 2]
    require(circuit.select_blocks(equal) == [], "equal-only block selected")
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", type=Path, help="create a NEW receipt path; never overwrite")
    args = parser.parse_args()
    if args.write_receipt:
        require(not args.write_receipt.exists(), "receipt output already exists")
    selected, word, programs, checks, audit = load_sources()
    result = {"schema": "ck-dyadic-ladders/1", "base_commit": BASE,
              "selected_kappa_unchanged": selected["kappa"], "assignment_seed": 36,
              "status": "finite scalar circuit improvement; no new kappa",
              "negative_controls": controls(), "programs": {}}
    for orientation in ("forward", "backward"):
        events = programs[orientation]
        phase_at, phase = [], None
        for event in events:
            if event[0] == "phase":
                phase = event[1]
            phase_at.append(phase)
        blocks = circuit.select_blocks(events)
        independent_blocks, independent_savings = independent_inventory(events)
        require(blocks == independent_blocks, "incomplete or non-maximal block inventory")
        records, equal_only_saving = [], 0
        for i, j in blocks:
            group = events[i:j]
            primitives = circuit.lower_block(group)
            peak, old_bound = inspect_block(group, primitives)
            before = sum(original_count(e[1]) for e in group)
            same = circuit.lower_block(group, equal_only=True)
            inspect_block(group, same)
            require(len(primitives) < len(same) <= before, "no incremental ladder saving")
            equal_only_saving += 2 * (before - len(same))
            records.append({"start": i, "stop": j, "events_sha256": digest(group),
                            "phase": phase_at[i],
                            "frame": group[0][2], "source": group[0][1][2],
                            "original_real_primitives": 2 * before,
                            "equal_only_real_primitives": 2 * len(same),
                            "ladder_real_primitives": 2 * len(primitives),
                            "work_coefficient_peak": str(peak), "reference_peak": old_bound})
        old_rows, old_prefix, before = replay(events, word)
        new_rows, new_prefix, after = replay(events, word, blocks)
        endpoint(old_rows, word, orientation)
        endpoint(new_rows, word, orientation)
        require(old_rows == new_rows, "scalar maps differ")
        require(before == checks[orientation]["real_component_primitive_bound"], "baseline invoice mismatch")
        require(old_prefix == Q(audit["local"][orientation]["prefix_l1_upper"]), "baseline prefix mismatch")
        require(new_prefix <= old_prefix < 2 ** 192, "prefix allowance exceeded")
        saving = sum(r["original_real_primitives"] - r["ladder_real_primitives"] for r in records)
        require(before - after == saving, "replacement cost mismatch")
        require([r["original_real_primitives"] - r["ladder_real_primitives"] for r in records]
                == independent_savings, "independent per-run cost mismatch")
        paid = Counter()
        for e in events:
            if e[0] == "climb":
                paid[e[5]] += 1
            elif e[0] == "center":
                paid[e[4]] += 1
        require(dict(paid) == {int(k): v for k, v in word["local_profile"].items()}, "paid profile")
        result["programs"][orientation] = {
            "events": len(events), "event_sha256": digest(events), "blocks": records,
            "changed_additions": sum(j - i for i, j in blocks), "live_input_columns": len(old_rows) - 9,
            "arbitrary_private_input_columns": 9, "original_real_primitives": before,
            "ladder_real_primitives": after, "saved_real_primitives": before - after,
            "equal_only_savings_on_same_blocks": equal_only_saving,
            "incremental_variable_magnitude_saving": before - after - equal_only_saving,
            "original_prefix_l1_upper": str(old_prefix), "ladder_prefix_l1_upper": str(new_prefix),
            "paid_profile": {str(k): v for k, v in sorted(paid.items())},
            "private_centres_and_work_cleared": True,
        }
        print(f"CHECK {orientation} blocks={len(blocks)} primitives={before}->{after} prefix={new_prefix}", flush=True)
    if args.write_receipt:
        with args.write_receipt.open("x") as output:
            json.dump(result, output, indent=2, sort_keys=True)
            output.write("\n")
    else:
        require(result == json.loads((HERE / "RESULT.json").read_text()), "committed receipt mismatch")
    saved = [result["programs"][o]["saved_real_primitives"] for o in ("forward", "backward")]
    total = sum(len(p["blocks"]) for p in result["programs"].values())
    print(f"PASS_CK_DYADIC_LADDERS blocks={total} saved={saved[0]},{saved[1]} columns=716+9 controls={len(result['negative_controls'])}")


if __name__ == "__main__":
    main()
