#!/usr/bin/env python3
"""Exact finite JP8 compensation batching; Apache-2.0, Codex-assisted."""

import argparse
import copy
import gzip
import hashlib
import json
from collections import defaultdict, deque
from fractions import Fraction as Q
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROVIDER = "research/community-k492-audit/pr626/replay/mixed-global/base/providers/jp8/"
SPEC = "research/complex-k492-owner-repair/data/SPEC.json"
W = ["W", 0]
N = 716


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def read_json(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == ".gz" else data)


def inputs():
    pins = read_json(HERE / "SOURCES.json")
    for name, record in pins["files"].items():
        data = (ROOT / name).read_bytes()
        if record["mode"] == "decompressed-sha256":
            data = gzip.decompress(data)
        else:
            require(record["mode"] == "sha256", "unknown pin mode")
        require(hashlib.sha256(data).hexdigest() == record["sha256"], "source pin: " + name)
    word = read_json(ROOT / PROVIDER / "CANONICAL-WORD.json.gz")
    programs = read_json(ROOT / PROVIDER / "LOCAL-PROGRAMS.json.gz")
    spec = read_json(ROOT / SPEC)["providers"]["jp8"]
    checks = read_json(ROOT / PROVIDER / "LOCAL-CHECKS.json")
    for name, obj in [("CANONICAL-WORD.json.gz", word), ("LOCAL-PROGRAMS.json.gz", programs)]:
        require(digest(obj) == spec["artifact_semantic_sha256"][name], "selected SPEC binding")
    for orientation, events in programs.items():
        require(digest(events) == spec["program_hashes"][orientation], "program binding")
        require(digest(events) == checks[orientation]["sha256"], "check binding")
    require((word["v"], word["R"], word["h"]) == (112, 492, 9), "geometry")
    return word, programs, spec, checks


def scalar(gate, backward):
    require(gate[0] == "add" and gate[-1] == 0, "nonzero-frame/non-add compensation")
    _, t, s, a, b, _ = gate
    if backward:
        t, s, a = s, t, -a
    return ["add", ["L", t], ["L", s], a, b]


def panel(word, events, backward):
    start = 1 + len(word["precondition"])
    stop = start + len(word["compensation"])
    expected = [["scalar", scalar(g, backward), 0] for g in word["compensation"]]
    require(events[0] == ["phase", "zero_frame_precondition"], "panel phase")
    require(events[start:stop] == expected, "panel location/content")
    require(events[stop] == ["phase", "entry_adapters"], "panel end")
    targets = {g[1] for g in word["compensation"]}
    sources = {g[2] for g in word["compensation"]}
    require(not targets & sources, "panel writes a source")
    require(all(word["start"][r] == 0 for r in targets | sources), "panel frame")
    require(len(expected) == 8800, "panel gate count")
    return start, stop, [e[1] for e in expected]


def transitions(k):
    """The finite signed quarter-grid route class, in deterministic tie order."""
    for label, value in [("add", k + 4), ("sub", k - 4), ("double", 2 * k)]:
        if -4 <= value <= 4 and value != k:
            yield label, value
    if k % 2 == 0 and k:
        yield "halve", k // 2


def route(required):
    wanted = sum(1 << (k - 1) for k in required)
    queue = deque([(0, 0)])
    parents = {(0, 0): None}
    goal = None
    while queue:
        state = queue.popleft()
        if state[1] == wanted:
            goal = state
            break
        for label, k in transitions(state[0]):
            mask = state[1] | ((1 << (abs(k) - 1)) & wanted if k else 0)
            nxt = (k, mask)
            if nxt not in parents:
                parents[nxt] = state, label
                queue.append(nxt)
    require(goal is not None, "unreachable coefficient set")
    steps = []
    while parents[goal] is not None:
        old, label = parents[goal]
        steps.append([label, goal[0]])
        goal = old
    return list(reversed(steps))


def construct(ops):
    groups = defaultdict(lambda: defaultdict(list))
    for index, op in enumerate(ops):
        _, target, source, a, b = op
        q = Q(a, b)
        k = abs(q) * 4
        require(k.denominator == 1 and 1 <= k <= 4, "coefficient outside quarter grid")
        groups[tuple(source)][int(k)].append((index, target, 1 if q > 0 else -1))
    primitives, blocks = [], []
    for source, coefficients in sorted(groups.items()):
        first = len(primitives)
        primitives.append(["clear", W])
        seen = set()
        steps = route(set(coefficients))
        order = []
        for label, k in steps:
            if label in ("add", "sub"):
                primitives.append(["add", W, list(source), 1 if label == "add" else -1, 1])
            else:
                primitives.append(["scale", W, 2, 1] if label == "double" else ["scale", W, 1, 2])
            magnitude = abs(k)
            if magnitude in coefficients and magnitude not in seen:
                seen.add(magnitude)
                for index, target, sign in coefficients[magnitude]:
                    primitives.append(["add", target, W, sign * (1 if k > 0 else -1), 1])
                    order.append(index)
        require(seen == set(coefficients), "coefficient not served")
        primitives.append(["clear", W])
        blocks.append({"source": list(source), "required_quarters": sorted(coefficients),
                       "route": steps, "original_indices": order,
                       "primitive_start": first, "primitive_stop": len(primitives),
                       "preparation_and_clear": len(steps) + 2})
    require(sorted(i for b in blocks for i in b["original_indices"]) == list(range(len(ops))),
            "panel is not a permutation")
    return primitives, blocks


def primitive_bound(op):
    if op[0] in ("copy", "clear"):
        return 1
    q = Q(*op[-2:])
    a, b = abs(q.numerator), q.denominator
    require(a > 0 and b & (b - 1) == 0, "nondyadic coefficient")
    if op[0] == "scale":
        require(a & (a - 1) == 0, "nondyadic scale")
        return abs(a.bit_length() - b.bit_length()) + int(q < 0)
    require(op[0] == "add", "unknown macro")
    return 3 + a.bit_length() - 1 + a.bit_count() + b.bit_length() - 1


def lower(op):
    """Literal realization of the selected emitter's charged Horner rule."""
    if op[0] in ("copy", "clear"):
        return [op]
    q = Q(*op[-2:])
    a, b = abs(q.numerator), q.denominator
    if op[0] == "scale":
        shift = a.bit_length() - b.bit_length()
        result = [["scale", op[1], 2, 1] if shift > 0 else ["scale", op[1], 1, 2]
                  for _ in range(abs(shift))]
        if q < 0:
            result.append(["scale", op[1], -1, 1])
    else:
        result = [["clear", W]]
        for i, bit in enumerate(bin(a)[2:]):
            if i:
                result.append(["scale", W, 2, 1])
            if bit == "1":
                result.append(["add", W, op[2], 1, 1])
        result.extend([["scale", W, 1, 2] for _ in range(b.bit_length() - 1)])
        result.extend([["add", op[1], W, 1 if q > 0 else -1, 1], ["clear", W]])
    require(len(result) == primitive_bound(op), "lowering cost mismatch")
    return result


def apply(rows, op):
    tag, target = op[0], tuple(op[1])
    if tag == "clear":
        rows[target] = {}
    elif tag == "copy":
        rows[target] = rows[tuple(op[2])].copy()
    elif tag == "scale":
        q = Q(*op[-2:])
        rows[target] = {j: q * x for j, x in rows[target].items() if q * x}
    elif tag == "add":
        source, q = tuple(op[2]), Q(*op[-2:])
        require(source != target, "aliased addition")
        row = rows[target]
        for j, x in list(rows[source].items()):
            value = row.get(j, Q(0)) + q * x
            if value:
                row[j] = value
            else:
                row.pop(j, None)
    else:
        raise ValueError("unknown primitive")


def initial_rows():
    return {**{("L", i): {i: Q(1)} for i in range(N)},
            **{("C", i): {N + i: Q(1)} for i in range(8)},
            ("W", 0): {N + 8: Q(1)}}


def check_panel(ops, candidate, norm=None):
    targets = {tuple(op[1]) for op in ops}
    sources = {tuple(op[2]) for op in ops}
    require(not targets & sources, "source overwritten in panel")
    original = initial_rows()
    actual = initial_rows()
    for op in ops:
        apply(original, op)
    weights = norm or {r: Q(1) for r in actual}
    peak = Q(1)
    work_sources = set()
    for op in candidate:
        target = tuple(op[1])
        if target == tuple(W):
            require(op[0] in ("clear", "add", "scale"), "work vocabulary")
            if op[0] == "clear":
                work_sources.clear()
            if op[0] == "add":
                source = tuple(op[2])
                require(source in sources and abs(Q(*op[-2:])) == 1, "work source")
                work_sources.add(source)
            require(len(work_sources) <= 1, "mixed source work")
            if op[0] == "scale":
                require(Q(*op[-2:]) in (Q(2), Q(1, 2)), "work scale")
        else:
            require(op[0] == "add" and target in targets and op[2] == W
                    and abs(Q(*op[-2:])) == 1, "illegal target primitive")
        apply(actual, op)
        if target == tuple(W):
            row = actual[tuple(W)]
            require(all(j < N for j in row), "incoming private work leaked")
            require(len(row) <= 1 and all(abs(x) <= 1 and (4*x).denominator == 1 for x in row.values()),
                    "work outside signed quarter grid")
        peak = max(peak, sum(abs(x) * weights[("L", j)] for j, x in actual[target].items()))
    require(not actual[tuple(W)], "private work not cleared")
    for i in range(N):
        require(actual["L", i] == original["L", i], "panel scalar boundary")
    return {"columns": N + 1, "positive_prefix_bound": str(peak)}


def full_replay(events, bounds, replacement=None):
    """All native scalar rows plus eight arbitrary centers and arbitrary work."""
    rows = initial_rows()
    norms = {r: Q(1) for r in rows}
    peak, count = Q(1), 0
    start, stop = bounds
    for i, event in enumerate(events):
        if replacement is not None and i == start:
            panel_ops, primitives = replacement
            panel_result = check_panel(panel_ops, primitives, norms)
            peak = max(peak, Q(panel_result["positive_prefix_bound"]))
            for op in primitives:
                apply(rows, op)
            # Rectangular commuting updates have the same positive exit envelope.
            for op in panel_ops:
                norms[tuple(op[1])] += abs(Q(*op[-2:])) * norms[tuple(op[2])]
            norms[tuple(W)] = Q(0)
            count += len(primitives)
        if replacement is not None and start <= i < stop:
            continue
        if event[0] != "scalar":
            require(not rows[tuple(W)], "work crosses a nonscalar event") if i else None
            continue
        op = event[1]
        target = tuple(op[1])
        primitives = lower(op)
        for primitive in primitives:
            apply(rows, primitive)
        count += len(primitives)
        if op[0] == "clear":
            norms[target] = Q(0)
        elif op[0] == "copy":
            norms[target] = norms[tuple(op[2])]
        elif op[0] == "scale":
            q = Q(*op[-2:])
            peak = max(peak, norms[target])
            norms[target] *= abs(q)
        else:
            q = Q(*op[-2:])
            source = tuple(op[2])
            peak = max(peak, abs(q.numerator) * norms[source])
            norms[target] += abs(q) * norms[source]
            norms[tuple(W)] = Q(0)
        peak = max(peak, norms[target])
    require(all(not row for r, row in rows.items() if r[0] != "L"), "private output not zero")
    require(peak < 2**192, "192-bit prefix allowance")
    return rows, {"real_primitives": 2 * count, "prefix_l1_upper": str(peak),
                  "prefix_bits_upper": peak.numerator.bit_length() - peak.denominator.bit_length() + 1,
                  "columns": N + 9}


def expect_failure(label, function):
    try:
        function()
    except (ValueError, KeyError, IndexError):
        return label
    raise ValueError("negative control accepted: " + label)


def controls(word, programs, candidates):
    _, _, ops = panel(word, programs["forward"], False)
    original = candidates["forward"]
    controls = []
    for label, change in [
        ("missing_initial_clear", lambda xs: xs.pop(0)),
        ("missing_final_clear", lambda xs: xs.pop()),
        ("wrong_accumulation_sign", lambda xs: next(x for x in xs if x[0] == "add" and x[2] == W).__setitem__(3, -next(x for x in xs if x[0] == "add" and x[2] == W)[3])),
        ("omitted_target_update", lambda xs: xs.pop(next(i for i,x in enumerate(xs) if x[0] == "add" and x[2] == W))),
        ("write_to_source", lambda xs: xs.append(["add", ops[0][2], W, 1, 1])),
        ("wrong_dyadic_step", lambda xs: next(x for x in xs if x[0] == "scale").__setitem__(2, 3)),
        ("prefix_only_inflation", None),
    ]:
        if label == "prefix_only_inflation":
            mutant = copy.deepcopy(original)
            mutant[2:2] = [["scale", W, 2, 1], ["scale", W, 1, 2]]
        else:
            mutant = copy.deepcopy(original)
            change(mutant)
        controls.append(expect_failure(label, lambda: check_panel(ops, mutant)))
    changed = copy.deepcopy(word)
    changed["compensation"][0][-1] = 1
    controls.append(expect_failure("nonzero_frame", lambda: panel(changed, programs["forward"], False)))
    shifted = copy.deepcopy(programs["forward"])
    shifted[168], shifted[169] = shifted[169], shifted[168]
    controls.append(expect_failure("cross_precondition_boundary", lambda: panel(word, shifted, False)))
    _, _, backops = panel(word, programs["backward"], True)
    controls.append(expect_failure("forward_panel_used_backward", lambda: check_panel(backops, original)))
    return controls


def run():
    word, programs, spec, selected_checks = inputs()
    candidates, receipt = {}, {"status": "PASS_JP8_COMPENSATION_BATCHING", "orientations": {}}
    for name in ("forward", "backward"):
        events = programs[name]
        start, stop, ops = panel(word, events, name == "backward")
        candidate, blocks = construct(ops)
        candidates[name] = candidate
        original_rows, before = full_replay(events, (start, stop))
        new_rows, after = full_replay(events, (start, stop), (ops, candidate))
        require(original_rows == new_rows, "full scalar projection differs")
        for i in range(N):
            expected = {i: Q(1)}
            if name == "forward" and 112 <= i < 224:
                expected[i - 112] = Q(1)
            if name == "backward" and i < 112:
                expected[i + 112] = Q(-1)
            require(new_rows["L", i] == expected, "full multiplication-shear endpoint")
        require(before["real_primitives"] == selected_checks[name]["real_component_primitive_bound"], "selected primitive count")
        require(before["prefix_l1_upper"] == spec["complete_contract"]["local"][name]["prefix_l1"], "selected prefix")
        require(before["prefix_l1_upper"] == after["prefix_l1_upper"], "prefix changed")
        baseline_panel = sum(primitive_bound(op) for op in ops)
        require(before["real_primitives"] - after["real_primitives"] == 2 * (baseline_panel - len(candidate)), "saving accounting")
        receipt["orientations"][name] = {
            "panel_events": [start, stop], "panel_additions": len(ops),
            "source_groups": len(blocks), "before": before, "after": after,
            "real_primitives_saved": before["real_primitives"] - after["real_primitives"],
            "panel_real_primitives_before": 2 * baseline_panel,
            "panel_real_primitives_after": 2 * len(candidate),
            "candidate_sha256": digest(candidate), "blocks": blocks,
            "paid_profile": word["local_profile"],
            "unchanged_nonpanel_events_sha256": digest(events[:start] + events[stop:]),
        }
        print(name, "saved", receipt["orientations"][name]["real_primitives_saved"], flush=True)
    receipt["controls_rejected"] = controls(word, programs, candidates)
    receipt["route_table"] = {str(mask): route({k for k in range(1, 5) if mask & (1 << (k-1))}) for mask in range(1, 16)}
    return candidates, receipt


def render_receipt(receipt):
    display = copy.deepcopy(receipt)
    for name in ("forward", "backward"):
        display["orientations"][name]["blocks"] = "BLOCKS_" + name
    rendered = json.dumps(display, indent=2)
    for name in ("forward", "backward"):
        blocks = receipt["orientations"][name]["blocks"]
        lines = ",\n".join("        " + json.dumps(block, separators=(",", ":")) for block in blocks)
        rendered = rendered.replace('"BLOCKS_' + name + '"', "[\n" + lines + "\n      ]")
    return rendered + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write freshly checked candidate/receipt to this directory")
    args = parser.parse_args()
    candidates, receipt = run()
    if args.write:
        args.write.mkdir(parents=True, exist_ok=True)
        (args.write / "CANDIDATE.json").write_text(json.dumps(candidates, separators=(",", ":")) + "\n")
        (args.write / "EXPECTED.json").write_text(render_receipt(receipt))
    else:
        require(read_json(HERE / "CANDIDATE.json") == candidates, "candidate certificate mismatch")
        require(read_json(HERE / "EXPECTED.json") == receipt, "expected receipt mismatch")
    savings = [str(receipt["orientations"][name]["real_primitives_saved"]) for name in ("forward", "backward")]
    print("PASS_JP8_COMPENSATION_BATCHING additions=8800 saved=" + ",".join(savings)
          + " columns=716+9 controls=" + str(len(receipt["controls_rejected"])))


if __name__ == "__main__":
    main()
