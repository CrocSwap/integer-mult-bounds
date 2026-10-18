#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent terminal-basis replay; Python standard library only.

This checker does not import either the primary boundary checker or any
predecessor Python module. It propagates terminal basis vectors backwards:
columns by M^{-1}, and covectors by right multiplication with M. Operators
are elements of the rational group algebra of the free group on the 72
numbered warp symbols. No numerical operator specialization is used.
"""

from __future__ import annotations

import argparse
import copy
from fractions import Fraction as F
import gzip
import hashlib
import json
from pathlib import Path


N = 704
TARGETS = set(range(112, 224))
E7 = (256, 128, 66, 36, 22, 8, 1)
E8 = (256, 128, 64, 36, 20, 8, 2, 1)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def addto(dst, src, scale=F(1)):
    for k, c in src.items():
        value = dst.get(k, F(0)) + scale * c
        if value:
            dst[k] = value
        else:
            dst.pop(k, None)


def word_left(t, w):
    return w[1:] if w and w[0] == -t else (t,) + w


def word_right(w, t):
    return w[:-1] if w and w[-1] == -t else w + (t,)


def inverse(g):
    k, d = g[:2]
    h = list(g)
    if k == "add":
        h[3] = -h[3]
    elif k == "scale":
        h[2], h[3] = h[3], h[2]
    elif k == "warp":
        h[2] = -h[2]
    else:
        raise ValueError(f"unsupported gate {g}")
    return h


def column_step(state, g):
    k, d = g[:2]
    if k == "add":
        addto(state[d], state[g[2]], F(g[3], g[4]))
    elif k == "scale":
        q = F(g[2], g[3])
        require(q != 0, "singular scale")
        state[d] = {key: q * c for key, c in state[d].items()}
    elif k == "warp":
        state[d] = {(j, word_left(g[2], w)): c for (j, w), c in state[d].items()}
    else:
        raise ValueError(f"unsupported gate {g}")


def row_step(state, g):
    k, d = g[:2]
    if k == "add":
        # rho(I+q e_d e_s^T): rho_s += q rho_d.
        addto(state[g[2]], state[d], F(g[3], g[4]))
    elif k == "scale":
        q = F(g[2], g[3])
        require(q != 0, "singular scale")
        state[d] = {key: q * c for key, c in state[d].items()}
    elif k == "warp":
        # Matrix multiplication is on the right: append, never prepend.
        state[d] = {(j, word_right(w, g[2])): c for (j, w), c in state[d].items()}
    else:
        raise ValueError(f"unsupported gate {g}")


def basis_state(registers):
    state = [{} for _ in range(N)]
    for j, r in enumerate(registers):
        state[r][(j, ())] = F(1)
    return state


def terminal_pullbacks(ops, registers, row=False):
    state = basis_state(registers)
    for g in reversed(ops):
        if row:
            row_step(state, g)
        else:
            column_step(state, inverse(g))
    return state


def scalar_action(ops, vector, row=False):
    state = [{} for _ in range(N)]
    for r, c in vector.items():
        state[r][(0, ())] = F(c)
    for g in reversed(ops) if row else ops:
        (row_step if row else column_step)(state, g)
    return state


def scalar_vector(state):
    result = {}
    for r, poly in enumerate(state):
        require(all(j == 0 and not w for j, w in poly), "nonscalar result")
        if poly:
            result[r] = poly[(0, ())]
    return result


def dot(a, b):
    return sum((v * b.get(k, F(0)) for k, v in a.items()), F(0))


def span(vectors):
    result = {0}
    for v in vectors:
        result |= {x ^ v for x in result}
    return result


def all_events(word):
    yield from word["A"]
    warps = {}
    for i, w in enumerate(word["warps"]):
        require(0 <= w[0] <= len(word["B"]), "warp cut outside B")
        warps.setdefault(w[0], []).append(["warp", w[1], i + 1, w[3], w[4]])
    for i in range(len(word["B"]) + 1):
        yield from warps.get(i, ())
        if i < len(word["B"]):
            yield word["B"][i]
    yield from word["restore"]


def middle(word):
    # The entry prelude is omitted exactly as declared by the predecessor.
    result = []
    for i, g in enumerate(all_events(word)):
        if i < word["prelude_events"]:
            continue
        if g[1] in TARGETS:
            continue
        require(g[0] != "add" or g[2] not in TARGETS,
                "a target is read by a non-target gate")
        result.append(g)
    require(len(word["warps"]) == 72, "unexpected warp namespace")
    return result


def terminal_frames(word):
    frames = {i: [word["ports"][i]] if i < 112 else [] for i in range(N)}
    frames.update({int(r): frame for r, frame in word["start_extra"].items()})
    seen = set()
    for position, g in enumerate(all_events(word)):
        if g[0] == "warp":
            regs, frame = [g[1]], g[4]
        elif g[0] == "add":
            regs, frame = g[1:3], g[5]
        else:
            regs, frame = [g[1]], g[4]
        require(frame is not None, "unexpected unspecified current frame")
        for r in regs:
            frames[r] = frame
            seen.add(r)
        if position == len(word["A"]) - 1:
            # The separate target-only cut uses the recorded center frames;
            # those frames are already present and introduce no hidden reset.
            require(all(span(frames[r]) == span(frame)
                        for r, frame in zip(word["centers"], word["center_frames"])),
                    "center cut would require a missing frame change")
            require(all(g[0] == "add" and g[1] in TARGETS and g[2] in word["centers"]
                        for g in word["cut"]), "cut reads an unaccounted non-center")
    require(set(range(N)) - set(word["removed"]) <= seen,
            "a live register lacks an observed terminal incidence")
    for r, frame in word["helper_final"].items():
        require(span(frames[int(r)]) == span(frame), "cold helper terminal frame mismatch")
    return frames


def helpers(word):
    protected = (set(map(int, word["helper_final"])) |
                 set(map(int, word["start_extra"])) |
                 set(word["removed"]) |
                 {c["source"] for c in word["initial_corrections"]})
    return set(range(224, N)) - protected


def eligible(word, endpoint):
    space = span(endpoint)
    frames = terminal_frames(word)
    return [r for r in range(N) if r not in TARGETS and r not in word["removed"]
            and set(frames[r]) <= space]


def constraints(state, allowed):
    # Every forbidden register/word coefficient is retained. No coefficient
    # cap, numeric sampling, operator commutation, or cancellation modulo p.
    result = []
    labels = []
    for r, poly in enumerate(state):
        by_word = {}
        for (j, w), c in poly.items():
            if r in allowed and not w:
                continue
            by_word.setdefault(w, {})[j] = c
        for w, coefficients in sorted(by_word.items()):
            result.append(coefficients)
            labels.append((r, w))
    return result, labels


def nullspace(rows, n):
    pivots = {}
    for original in rows:
        row = dict(original)
        while row:
            p = min(row)
            if p not in pivots:
                lead = row[p]
                pivots[p] = {j: c / lead for j, c in row.items()}
                break
            addto(row, pivots[p], -row[p])
    free = sorted(set(range(n)) - pivots.keys())
    basis = []
    for f in free:
        vector = {f: F(1)}
        for p in sorted(pivots, reverse=True):
            c = -sum((q * vector.get(j, F(0)) for j, q in pivots[p].items() if j != p), F(0))
            if c:
                vector[p] = c
        require(all(dot(r, vector) == 0 for r in rows), "invalid nullspace vector")
        basis.append(vector)
    return basis, len(pivots)


def format_vector(v, coordinates):
    return {str(coordinates[i]): str(q) for i, q in sorted(v.items())}


def focused_witness(word):
    """Two complete nonsingular 11-coordinate restrictions, read from replay."""
    cold = [307, 309, 314, 369, 371, 373, 378, 572, 573]
    R = eligible(word, E7)
    require(R == sorted([105, 408] + cold), "changed rank7 terminal set")
    H = helpers(word)
    columns = terminal_pullbacks(middle(word), R, row=False)
    rows = terminal_pullbacks(middle(word), R, row=True)
    col_spec = [(550, 408, F(1)), (551, 105, F(1))] + [(c, c, F(1)) for c in cold]
    row_spec = [(14, 105, F(-1, 2)), (41, 408, F(1, 2))] + [(c, c, F(1)) for c in cold]
    for state, spec in ((columns, col_spec), (rows, row_spec)):
        for forbidden, terminal, coefficient in spec:
            require(forbidden not in H, "witness coordinate is an allowed input")
            require(state[forbidden] == {(R.index(terminal), ()): coefficient},
                    "focused witness identity does not match complete free-operator replay")
    require(550 in map(int, word["start_extra"]) and 551 in map(int, word["start_extra"]),
            "the two inverse witnesses lack nonzero-entry protection")
    return {
        "inverse_column_restriction": [[i, j, str(q)] for i, j, q in col_spec],
        "forward_row_restriction": [[i, j, str(q)] for i, j, q in row_spec],
        "inverse_determinant_absolute": "1",
        "row_determinant_absolute": "1/4",
    }


def solve(word, endpoint, registers=None):
    ops = middle(word)
    H = helpers(word)
    R = eligible(word, endpoint) if registers is None else registers
    inverse_columns = terminal_pullbacks(ops, R, row=False)
    forward_rows = terminal_pullbacks(ops, R, row=True)
    col_constraints, col_labels = constraints(inverse_columns, H)
    row_constraints, row_labels = constraints(forward_rows, H)
    ys, col_rank = nullspace(col_constraints, len(R))
    alphas, row_rank = nullspace(row_constraints, len(R))
    pairing = [[dot(a, y) for y in ys] for a in alphas]
    return {
        "endpoint": list(endpoint), "terminal_registers": R, "helper_count": len(H),
        "column_constraint_count": len(col_constraints), "column_constraint_rank": col_rank,
        "row_constraint_count": len(row_constraints), "row_constraint_rank": row_rank,
        "column_dimension": len(ys), "row_dimension": len(alphas),
        "terminal_column_basis": [format_vector(v, R) for v in ys],
        "terminal_row_basis": [format_vector(v, R) for v in alphas],
        "pairing": [[str(x) for x in row] for row in pairing],
        "pairing_nonzero": any(x for row in pairing for x in row) != 0,
    }


def compensation_rows(word):
    result = {r: {} for r in TARGETS}
    for g in word["compensation"]:
        require(g[0] == "add" and g[1] in TARGETS and g[2] not in TARGETS,
                "unsupported compensation schema")
        addto(result[g[1]], {g[2]: F(g[3], g[4])})
    return result


def right_scalar_action(ops, row):
    return scalar_vector(scalar_action(ops, row, row=True))


def verify_cleanup_recipe(word):
    """Check the stored literal cleanup, including the private helper map."""
    cold = set(map(int, word["helper_final"]))
    full = span((256, 128, 64, 32, 16, 8, 4, 2, 1))

    def host(r):
        return r + N if r in cold else r

    expected = []
    for g in reversed(middle(word)):
        if g[0] == "add":
            expected.append(("add", host(g[1]), host(g[2]), -F(g[3], g[4])))
        elif g[0] == "scale":
            expected.append(("scale", host(g[1]), F(g[3], g[2])))
        else:
            expected.append(("warp", host(g[1]), -g[2]))
    observed = []
    for g in word["cleanup"]:
        require(span(g[-1]) == full, "cleanup is not in the complete paid frame")
        if g[0] == "add":
            observed.append(("add", g[1], g[2], F(g[3], g[4])))
        elif g[0] == "scale":
            observed.append(("scale", g[1], F(g[2], g[3])))
        else:
            require(g[0] == "warp", "unknown cleanup gate")
            observed.append(("warp", g[1], g[2]))
    require(observed == expected, "stored cleanup is not the full reverse-inverse recipe")
    return {"gates": len(expected), "private_zero_buffers": len(cold), "host_map": "r -> r+704 for cold r"}


def positive_control(parent, actual, transform):
    before, after = transform["before"], transform["after"]
    h = transform["helper"]
    p = parent["prelude_events"]
    require(actual["A"] == parent["A"][:p] + before + parent["A"][p:],
            "actual A is not the stated current-word input composition")
    require(actual["restore"] == parent["restore"] + after,
            "actual restore is not the stated terminal composition")
    for key in ("B", "warps", "prelude_events", "initial_corrections", "start_extra", "removed"):
        require(parent[key] == actual[key], f"unexpected changed {key}")
    H = helpers(parent)
    for g in before:
        touched = g[1:3] if g[0] == "add" else [g[1]]
        require(all(r in H for r in touched), "input composition touches protected input")
        require(g[-1] == [], "input composition is not at frame zero")
    R8 = set(eligible(parent, E8))
    for g in after:
        require(g[0] == "add" and set(g[1:3]) <= R8 and span(g[-1]) == span(E8),
                "terminal composition has an illegal endpoint support")
        require(not set(g[1:3]) & set(map(int, parent["helper_final"])),
                "terminal composition modifies an existing cold helper")
    require(actual["helper_final"] == dict(parent["helper_final"], **{str(h): list(E8)}),
            "existing cold helpers are not preserved exactly")
    e = {h: F(1)}
    v = scalar_vector(scalar_action(before, e))
    u = right_scalar_action([inverse(g) for g in reversed(before)], e)
    y = scalar_vector(scalar_action([inverse(g) for g in reversed(after)], e))
    alpha = right_scalar_action(after, e)
    M = middle(parent)
    require(scalar_vector(scalar_action(M, v)) == y, "rank8 Mv=y failed")
    require(right_scalar_action(M, alpha) == u, "rank8 alpha M=u failed")
    require(scalar_vector(scalar_action(after, y)) == e, "rank8 Ty=e failed")
    require(right_scalar_action(before, u) == e, "rank8 uS=e^T failed")
    require(dot(alpha, y) == dot(u, v) == 1, "rank8 pairing is not one")
    # The target correction is evaluated on the transformed raw inputs.
    oldC, newC = compensation_rows(parent), compensation_rows(actual)
    expected = {r: right_scalar_action(before, row) for r, row in oldC.items()}
    require(newC == expected, "actual target compensation is not C S")
    wrong = {r: right_scalar_action([inverse(g) for g in reversed(before)], row)
             for r, row in oldC.items()}
    require(wrong != newC, "C S^{-1} mutant was not distinguished")
    # Omit the inverse of the final terminal gate: changes the actual word.
    bad_y = scalar_vector(scalar_action([inverse(g) for g in reversed(after[:-1])], e))
    require(bad_y != y and scalar_vector(scalar_action(M, v)) != bad_y,
            "omitted inverse gate mutant was not distinguished")
    # Chronology matters in the dual action, not just sign conventions.
    bad_row = scalar_action(list(reversed(M)), alpha, row=True)
    require(bad_row != scalar_action([], u), "row chronology mutant was not distinguished")
    # Use the terminal-basis engine independently on the existing certificate.
    r8 = solve(parent, E8)
    require(r8["pairing_nonzero"], "rank8 full-space positive control failed")
    return {
        "alpha": {str(k): str(x) for k, x in alpha.items()},
        "y": {str(k): str(x) for k, x in y.items()},
        "input_v": {str(k): str(x) for k, x in v.items()},
        "input_u": {str(k): str(x) for k, x in u.items()},
        "identity_checks": ["Mv=y", "alpha M=u", "Ty=e408", "uS=e408^T",
                            "alpha y=uv=1", "actual A=A_parent S", "C_actual=C_parent S"],
        "controls_rejected": ["C S^{-1}", "omitted terminal inverse gate", "wrong row chronology"],
        "cleanup_parent": verify_cleanup_recipe(parent),
        "cleanup_actual": verify_cleanup_recipe(actual),
        "full_rank8": r8,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sources", type=Path, default=Path(__file__).resolve().parent / "sources" / "data")
    args = parser.parse_args()
    source_hashes = {}
    pins = json.loads((Path(__file__).resolve().parent / "SOURCE-PINS.json").read_text())
    require(pins["source_commit"] == "51309592971e3b5be935599eed2a95404dc7781e",
            "unexpected PR2908 source commit")
    require(pins["parent_commit"] == "18d03c447886895ef9abf888398178e0428533ca",
            "unexpected PR2894 predecessor commit")

    def load(name):
        data = (args.sources / name).read_bytes()
        sha = hashlib.sha256(data).hexdigest()
        blob = hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
        require(pins["files"]["data/" + name] == {"sha256": sha, "git_blob": blob},
                f"source bytes do not match pinned SHA256 and Git blob: {name}")
        source_hashes[name] = sha
        return json.loads(gzip.decompress(data) if name.endswith(".gz") else data)

    transform = load("TRANSFORM.json")
    results = {}
    for provider in ("base", "extra"):
        parent = load(f"PARENT-{provider}.json.gz")
        actual = load(f"WORD-{provider}.json.gz")
        result = solve(parent, E7)
        require(not result["pairing_nonzero"], f"{provider}: rank7 pairing is nonzero")
        result["focused_witness"] = focused_witness(parent)
        positive = positive_control(parent, actual, transform)
        # The known rank8 pair uses exactly the missing terminal coordinate42.
        relaxed = solve(parent, E7, sorted(set(result["terminal_registers"]) | {42}))
        require(relaxed["pairing_nonzero"], "missing-coordinate support control failed")
        bad = copy.deepcopy(parent)
        bad["restore"].append(["add", 408, 112, 1, 1, list(E7)])
        try:
            middle(bad)
        except ValueError as error:
            require("target is read" in str(error), "target-read control failed for wrong reason")
        else:
            raise ValueError("target-to-helper read was silently omitted")
        result["positive_control"] = positive
        result["semantic_controls"] = {
            "admit_illegal_terminal42": {"pairing_nonzero": relaxed["pairing_nonzero"],
                "column_dimension": relaxed["column_dimension"], "row_dimension": relaxed["row_dimension"]},
            "target_to_helper_read": "rejected",
        }
        results[provider] = result
    # Free symbols are noncommuting; only adjacent inverse pairs reduce.
    require(word_left(1, (2,)) != word_left(2, (1,)), "commuting operator implementation")
    require(word_left(-1, (1, 2)) == (2,) and word_right((2, 1), -1) == (2,),
            "free-group inverse cancellation failed")
    print(json.dumps({"status": "PASS_INDEPENDENT_RANK7_PAIRING no_new_kappa",
                      "source_sha256": source_hashes, "providers": results}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
