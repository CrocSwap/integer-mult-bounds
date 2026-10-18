#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent paired-block check; reads fixed data, never predecessor code.

This oracle pushes selected columns and pulls covectors backward.  It does not
construct the middle's full input/output matrix or import another checker.
Free words are literal tuples, in left-to-right multiplication order.
"""

from copy import deepcopy
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path


SOURCE_COMMIT = "a027b0f6fdb0ab2b42ba10fc31b53960166bf2bf"
DATA = Path(__file__).resolve().parents[1] / "paired-extension-normal45" / "data"
HELPERS = (249, 267, 251, 265)
FRAME = [256, 128, 64, 33, 16, 9, 5, 2]
PINS = {
    "PARENT-base.json.gz": "fec3c120db1a35022944628d34b56a36f2456248c274c2eaba1a325cdc690ce8",
    "PARENT-extra.json.gz": "e4d0c617df85bf8a824ff68310ca3373dc017c1ebf9ea733056a3ee4a784b36f",
    "WORD-base.json.gz": "54ca34c749e3228d7e2df3d8dbf7aa1568c2872490166997c5962f12fd03da35",
    "WORD-extra.json.gz": "eded756dfe8f411c3d1f80a3ac16516f0ea5dd6f9866728b2179b157630fa7b6",
    "TRANSFORM-249.json": "fb8cae03c69e868e3d6f2caa56a45cdeb78e2a8f0289465c75bf2bb40a6c8979",
    "TRANSFORM-267.json": "afa89055509f87febd8879fda8e308d1c9f98f914bc36b5b49604caf11a5ff0c",
    "TRANSFORM-251.json": "8b3fea5c113ef82c78c33c809b282fa781be234299672cd1c987604929a34dc0",
    "TRANSFORM-265.json": "3ae3261cc35ab19c799d5d6d632e8e79e3b588e3c342be2b5ef1b3085ab61af4",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(name):
    raw = (DATA / name).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == PINS[name], "source pin: " + name)
    return json.loads(gzip.decompress(raw) if name.endswith(".gz") else raw)


def add_to(dst, src, q):
    for key, value in src.items():
        value = dst.get(key, Q(0)) + q * value
        if value:
            dst[key] = value
        else:
            dst.pop(key, None)


def invert(gate):
    g = list(gate)
    if g[0] == "add":
        g[3] = -g[3]
    elif g[0] == "scale":
        g[2], g[3] = g[3], g[2]
    else:
        require(g[0] == "warp", "unknown inverse primitive")
        g[2] = -g[2]
    return g


def scalar_value(g):
    if g[0] == "add":
        require(g[1] != g[2], "self add")
        q = Q(g[3], g[4])
    else:
        require(g[0] == "scale", "scalar primitive")
        q = Q(g[2], g[3])
        require(q != 0, "invertible scale")
    require(q.denominator & (q.denominator - 1) == 0, "dyadic coefficient")
    return q


def scalar_column(gates, vector):
    """Forward scalar column action, using no matrix constructor."""
    v = dict(vector)
    for g in gates:
        q = scalar_value(g)
        r = g[1]
        value = v.get(r, Q(0))
        value = value + q * v.get(g[2], Q(0)) if g[0] == "add" else q * value
        if value:
            v[r] = value
        else:
            v.pop(r, None)
    return v


def scalar_row(gates, covector):
    """Pull a scalar output row back through gates in reverse chronology."""
    row = dict(covector)
    for g in reversed(gates):
        q = scalar_value(g)
        dst = g[2] if g[0] == "add" else g[1]
        value = row.get(dst, Q(0))
        value = value + q * row.get(g[1], Q(0)) if g[0] == "add" else q * value
        if value:
            row[dst] = value
        else:
            row.pop(dst, None)
    return row


def middle(word):
    """The exact non-target middle, including every ordered warp occurrence."""
    live = set(range(704)) - set(word["removed"]) - set(range(112, 224))
    out = []
    by_position = {}
    for op, record in enumerate(word["warps"], 1):
        position, register = record[:2]
        require(0 <= position <= len(word["B"]), "warp position")
        by_position.setdefault(position, []).append(["warp", register, op])
    all_gates = list(word["A"][word["prelude_events"]:])
    for pos in range(len(word["B"]) + 1):
        all_gates.extend(by_position.get(pos, []))
        if pos < len(word["B"]):
            all_gates.append(word["B"][pos])
    all_gates.extend(word["restore"])
    for g in all_gates:
        if 112 <= g[1] < 224:
            continue
        regs = g[1:3] if g[0] == "add" else g[1:2]
        require(all(r in live for r in regs), "middle reads only live non-targets")
        if g[0] != "warp":
            scalar_value(g)
        else:
            require(g[2] > 0, "middle uses positive free generators")
        # Frames are checked against their exact edit preimages separately;
        # numerical/free semantics depend only on these literal operands.
        out.append(g[:3] if g[0] == "warp" else g[:5] if g[0] == "add" else g[:4])
    return out, tuple(sorted(live))


def free_action(gates, seeds, backward=False):
    """Push columns or pull rows; labels identify distinct independent probes.

    A state entry (label, word) is an exact rational coefficient of a literal
    noncommuting monomial. Forward warps prefix a letter, pullbacks suffix it.
    The middle has positive letters only, so no group reduction is needed.
    """
    state = {r: dict(poly) for r, poly in seeds.items()}
    for g in reversed(gates) if backward else gates:
        if g[0] == "warp":
            r, op = g[1:3]
            state[r] = {(label, word + (op,) if backward else (op,) + word): q
                        for (label, word), q in state.get(r, {}).items()}
        elif g[0] == "scale":
            r, q = g[1], scalar_value(g)
            state[r] = {key: q * a for key, a in state.get(r, {}).items()}
        else:
            q = scalar_value(g)
            dst, src = (g[2], g[1]) if backward else (g[1], g[2])
            add_to(state.setdefault(dst, {}), state.get(src, {}), q)
    return {r: poly for r, poly in state.items() if poly}


def one_probe(v):
    return {r: {(0, ()): q} for r, q in v.items() if q}


def scalar_probe(state):
    out = {}
    for r, poly in state.items():
        require(set(poly) <= {(0, ())}, "non-scalar pullback")
        if poly:
            out[r] = poly[0, ()]
    return out


def endpoints(program, registers):
    """Check both complete row and column blocks, all non-target coordinates."""
    seed = {r: {(r, ()): Q(1)} for r in registers}
    require(free_action(program, seed) == seed, "restored endpoint column block")
    require(free_action(program, seed, True) == seed, "restored endpoint row block")


def compensation(word):
    rows = {r: {} for r in range(112, 224)}
    helpers = set(range(224, 704)) - set(word["removed"])
    for g in word["compensation"]:
        require(g[0] == "add" and g[-1] == [] and g[1] in rows,
                "zero-frame target compensation")
        require(g[2] in helpers, "compensation reads a live dirty helper")
        add_to(rows[g[1]], {g[2]: scalar_value(g)}, Q(1))
    return rows


def right_product(rows, gates):
    return {r: scalar_row(gates, row) for r, row in rows.items()}


def refit(word, transform):
    w = deepcopy(word)
    seen = set()
    for edit in transform["frame_changes"]:
        sec, pos = edit["section"], edit["parent_index"]
        require(sec in ("A", "restore") and (sec, pos) not in seen,
                "unique frame substitution")
        require(sec != "A" or pos >= w["prelude_events"], "refit after prelude")
        seen.add((sec, pos))
        old = w[sec][pos]
        require(old[:-1] == edit["gate"] and old[-1] == edit["old_frame"],
                "exact step-refitted gate preimage")
        old[-1] = list(edit["new_frame"])
    return w


def refit_and_insert(word, transform):
    w = refit(word, transform)
    n = w["prelude_events"]
    w["A"][n:n] = deepcopy(transform["before"])
    w["restore"].extend(deepcopy(transform["after"]))
    w["helper_final"][str(transform["helper"])] = FRAME
    return w


def rejected(thunk, expected):
    try:
        thunk()
    except ValueError as exc:
        require(str(exc) == expected, "wrong rejecting predicate: " + str(exc))
        return expected
    raise ValueError("negative control accepted: " + expected)


def encode(v):
    return {str(r): str(q) for r, q in sorted(v.items())}


def paired_check(word, transform, C):
    h, before, after = transform["helper"], transform["before"], transform["after"]
    program, live = middle(word)
    protected = set(map(int, word["helper_final"])) | set(map(int, word["start_extra"]))
    protected |= {c["source"] for c in word["initial_corrections"]}
    eligible = set(live) - set(range(224)) - protected
    require(h in eligible, "fresh eligible pivot")
    require(transform["normal"] == 45 and all(g[-1] == [] for g in before)
            and all(g[-1] == FRAME for g in after), "declared input/output frame")
    require(all(r in eligible for g in before
                for r in (g[1:3] if g[0] == "add" else g[1:2])),
            "input map touches only unprotected helpers")
    v = scalar_column(before, {h: Q(1)})
    alpha = scalar_row(after, {h: Q(1)})
    y = scalar_column([invert(g) for g in reversed(after)], {h: Q(1)})
    require(set(v) <= eligible, "v supported on eligible dirty helpers")
    require(free_action(program, one_probe(v)) == one_probe(y), "M v = y")
    u = scalar_probe(free_action(program, one_probe(alpha), True))
    require(set(u) <= eligible, "u supported on eligible dirty helpers")
    require(scalar_row(before, u) == {h: Q(1)}, "u S = e_h^T")
    require(sum(alpha.get(r, Q(0)) * q for r, q in y.items()) == 1, "alpha y = 1")
    require(scalar_column(after, y) == {h: Q(1)}, "T y = e_h")
    require(all(sum(row.get(r, Q(0)) * q for r, q in v.items()) == 0
                for row in C.values()), "C v = 0")
    return {"helper": h, "v": encode(v), "u": encode(u), "alpha": encode(alpha),
            "y": encode(y), "middle_gates": len(program),
            "non_target_inputs": len(live), "dirty_helper_inputs": sum(r >= 224 for r in live)}


def main():
    transforms = [read("TRANSFORM-%d.json" % h) for h in HELPERS]
    require([t["step"] for t in transforms] == [1, 2, 3, 4], "ordered four stages")
    results = {}
    for provider in ("base", "extra"):
        parent, final = read("PARENT-" + provider + ".json.gz"), read("WORD-" + provider + ".json.gz")
        w, C = deepcopy(parent), compensation(parent)
        initial_program, live = middle(w)
        initial_ends = set(map(int, w["helper_final"]))
        require(len(initial_ends) == 82, "parent has 82 restored endpoints")
        endpoints(initial_program, initial_ends)
        require(all(not (set(row) & initial_ends) for row in C.values()),
                "parent compensation omits every inherited cold column")
        total_S = {r: {r: Q(1)} for r in live}
        literal_prefix = []
        stages, snapshots = [], []
        for transform in transforms:
            snapshots.append(deepcopy(w))
            # Frame substitutions leave scalar/free semantics unchanged, but the
            # exact current preimage is checked before each insertion.
            refitted = refit(w, transform)
            require(middle(refitted) == middle(w), "refit leaves middle operator unchanged")
            record = paired_check(refitted, transform, C)
            C = right_product(C, transform["before"])
            total_S = right_product(total_S, transform["before"])
            literal_prefix = transform["before"] + literal_prefix
            h = transform["helper"]
            require(all(h not in row for row in C.values()), "new compensation column is zero")
            w = refit_and_insert(w, transform)
            program, _ = middle(w)
            cold = set(map(int, w["helper_final"]))
            endpoints(program, cold)
            require(all(not (set(row) & cold) for row in C.values()),
                    "compensation omits every restored cold column")
            require(initial_ends <= cold and len(cold) == 82 + len(stages) + 1,
                    "all inherited and new endpoints retained")
            record["restored_endpoints"] = len(cold)
            stages.append(record)
        # Distinct derivation: direct chronological column action of the final
        # prefix, compared against S1*S2*S3*S4 formed by covector pullbacks.
        for r in live:
            column = scalar_column(literal_prefix, {r: Q(1)})
            expected = {s: row[r] for s, row in total_S.items() if r in row}
            require(column == expected, "ordered total S matches literal prefix")
        require(C == right_product(compensation(parent), literal_prefix), "C0 times literal prefix")
        require(C == compensation(final), "C0 S1 S2 S3 S4 equals final compensation")
        for sec in ("A", "B", "restore", "warps", "helper_final"):
            require(w[sec] == final[sec], "final declared section binding: " + sec)
        require(all(final["helper_final"][str(r)] == parent["helper_final"][str(r)]
                    for r in initial_ends), "inherited endpoint frames unchanged")
        controls = {}
        wrong_prefix = sum((t["before"] for t in transforms), [])
        require(wrong_prefix != literal_prefix, "order control changes actual prefix")
        controls["reverse_stage_order"] = rejected(
            lambda: require(right_product(compensation(parent), wrong_prefix) == C,
                            "wrong-order compensation differs"), "wrong-order compensation differs")
        inverse_prefix = [invert(g) for g in reversed(literal_prefix)]
        controls["inverse_compensation"] = rejected(
            lambda: require(right_product(compensation(parent), inverse_prefix) == C,
                            "C S^-1 differs"), "C S^-1 differs")
        controls["stale_compensation"] = rejected(
            lambda: require(compensation(parent) == C, "stale C0 differs"), "stale C0 differs")
        # Introduce a real read of the prior restored dirty helper in stage 2.
        bad = deepcopy(transforms[1])
        bad["before"] = [["add", 267, 249, 1, 1, []]] + bad["before"]
        bad_word = refit_and_insert(snapshots[1], bad)
        bad_program, _ = middle(bad_word)
        controls["prior_endpoint_interference"] = rejected(
            lambda: endpoints(bad_program, set(map(int, bad_word["helper_final"]))),
            "restored endpoint column block")
        # Equivalent scalar presentations must be accepted. Split one actual
        # add into two equal half-adds, and compare the entire prefix matrix.
        split = deepcopy(literal_prefix)
        require(split[0][0] == "add", "positive control site is an add")
        half = Q(split[0][3], 2 * split[0][4])
        replacement = [split[0][0], split[0][1], split[0][2], half.numerator,
                       half.denominator, split[0][-1]]
        split[0:1] = [deepcopy(replacement), deepcopy(replacement)]
        require(split != literal_prefix, "positive control changes actual prefix")
        require(right_product({r: {r: Q(1)} for r in live}, split) == total_S,
                "equivalent split prefix accepted on every coordinate")
        controls["equivalent_split_add"] = "accepted complete prefix matrix"
        results[provider] = {"stages": stages, "controls": controls,
                             "compensation_rows": len(C), "compensation_terms": sum(map(len, C.values())),
                             "total_S_nonidentity_rows": sum(row != {r: Q(1)} for r, row in total_S.items()),
                             "final_restored_endpoints": len(w["helper_final"])}
    print(json.dumps({"status": "PASS_NORMAL45_INDEPENDENT_PAIRED_BLOCKS", "source_commit": SOURCE_COMMIT,
                      "providers": results, "scope": "finite exact free-operator paired blocks and ordered compensation; no_new_kappa"},
                     sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
