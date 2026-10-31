#!/usr/bin/env python3
"""Bounded exact corroboration of the refined-chain theorem and codec.

For @CubeJerry, substantial OpenAI Codex assistance. Apache-2.0.
The mathematical proof is PROOF.md; these finite checks are not that proof.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import recovery as r
import optimal_verify

SOURCE = HERE.parent / "precision-state-frontier" / "FIXTURE.json"
SOURCE_HASH = "2ca4d7550fcae5b757ec500f87aee1d2ef9f64b59e4abe2bda93319521304af8"


def rejected(function, message):
    try:
        function()
    except (ValueError, TypeError):
        return 1
    raise ValueError("control failed to reject: " + message)


def source_facts(matrix):
    r.require(len(matrix) == 112 and all(len(row) == 8 for row in matrix),
              "source matrix has wrong dimensions")
    r.require(all(type(x) is int and x in (-1, 0, 1)
                  for row in matrix for x in row), "invalid source coefficients")
    r.require(all(sum(x != 0 for x in row) == 4 for row in matrix),
              "source support changed")
    gram = [[sum(row[i] * row[j] for row in matrix) for j in range(8)]
            for i in range(8)]
    r.require(gram == [[56 * (i == j) for j in range(8)] for i in range(8)],
              "source Gram identity changed")
    row_code = {0}
    for row in matrix:
        mask = sum((x & 1) << i for i, x in enumerate(row))
        row_code |= {a ^ mask for a in tuple(row_code)}
    kernel = set(r.parity_options(matrix, [0] * 112))
    r.require(row_code == kernel and len(kernel) == 16, "self-dual code changed")
    r.require(Counter(x.bit_count() for x in kernel) == {0: 1, 4: 14, 8: 1},
              "code weight enumerator changed")
    return {"gram_entries": 64, "codewords": len(kernel)}


def scalar_checks():
    points = 0
    for s in range(-52, 53):
        for depth in range(1, 4):
            lo, hi = r.total_interval(s, depth)
            r.require(hi - lo + 1 <= 13 ** depth, "scalar capacity exceeded")
            for total in range(lo - 2, hi + 3):
                value = total
                for _ in range(depth):
                    value = r.scalar_step(s, value)
                r.require((value == 0) == (lo <= total <= hi),
                          "inverse interval differs from literal scalar replay")
                points += 1
    for depth in range(1, 9):
        radius = (13 ** depth - 1) // 2
        r.require(r.total_interval(0, depth) == (-radius, radius),
                  "zero-output interval does not attain the bound")
    r.require([r.nearest(x) for x in [-78, -26, 26, 78]] == [-2, -1, 1, 2],
              "half-away convention changed")
    return {"scalar_input_points": points, "interval_depths": [1, 2, 3]}


def shear_checks(matrix):
    for shear in (r.U, r.V):
        r.validate_shear(matrix, shear)
        for i in range(112):
            e = [int(i == j) for j in range(112)]
            u = r.apply_shear(e, shear)
            r.require(r.apply_shear(u, shear, True) == e, "inverse shear failed")
            r.require(r.project(matrix, u) == r.project(matrix, e),
                      "shear changed mode projection")
            r.require(all((a - b) % 2 == 0 for a, b in zip(e, u)),
                      "shear changed parity")
    e = [0] * 112
    e[2] = 52
    lhs = r.kernel(matrix, r.apply_shear(e, r.U))
    rhs = r.apply_shear(r.kernel(matrix, e), r.U)
    expected = [0] * 112
    for i, value in r.U[0]:
        expected[i] = 8 * value
    r.require([a - b for a, b in zip(lhs, rhs)] == expected,
              "source-sized noncommutation witness changed")
    e[2], e[3] = 0, 1
    uv = r.apply_shear(r.apply_shear(e, r.V), r.U)
    vu = r.apply_shear(r.apply_shear(e, r.U), r.V)
    r.require([a - b for a, b in zip(uv, vu)] == [-v // 2 for v in expected],
              "two frame shears unexpectedly commute")
    return {"shear_basis_vectors": 224, "noncommutation_witnesses": 2}


def chosen_frames(depth):
    return [r.U if i % 2 == 0 else r.V for i in range(depth - 1)]


def codec_checks(matrix):
    cases = 0
    for depth in range(1, 7):
        frames, zero = chosen_frames(depth), [0] * 112
        count = r.fiber_count(matrix, zero, depth)
        r.require(count == r.max_states(depth), "sharp zero fiber failed")
        offset = 0
        for _, _, size in r.blocks(matrix, zero, depth):
            for tag in sorted({offset, offset + size // 2, offset + size - 1}):
                vector = r.decode(matrix, zero, frames, tag)
                r.require(r.encode(matrix, vector, frames) == (zero, tag),
                          "attaining block witness did not round-trip")
                cases += 1
            offset += size
    for depth in range(1, 5):
        frames = chosen_frames(depth)
        for sample in range(24):
            vector = [((sample + 3) * (i * i + 17) % 127) - 63
                      for i in range(112)]
            output, tag = r.encode(matrix, vector, frames)
            r.require(r.decode(matrix, output, frames, tag) == vector,
                      "arbitrary input did not round-trip")
            r.require(r.fiber_count(matrix, output, depth) <= r.max_states(depth),
                      "arbitrary output exceeds the proved maximum")
            cases += 1
    return {"source_sized_codec_roundtrips": cases, "maximum_tested_depth": 6}


def controls(matrix):
    zero = [0] * 112
    mutated = [list(row) for row in matrix]
    mutated[0][0] = 0
    checks = [
        (lambda: source_facts(mutated), "changed native matrix"),
        (lambda: r.validate_shear(matrix, (r.U[0], 2, 1)), "odd frame"),
        (lambda: r.validate_shear(matrix, (((0, 1),), 2, 2)), "mode-changing frame"),
        (lambda: r.validate_shear(matrix, (r.U[0], 1, 2)), "non-unimodular shear"),
        (lambda: r.decode(matrix, zero, [r.U], r.max_states(2)), "oversized tag"),
        (lambda: r.decode(matrix, zero, [r.U], -1), "negative tag"),
        (lambda: r.total_interval(0, 0), "zero depth"),
        (lambda: r.total_interval(0, 9), "operational depth cap"),
        (lambda: r.forward(matrix, [0.0] * 112, []), "inexact input"),
        (lambda: r.require(r.max_states(2) == r.max_states(1) * 13 ** 8,
                           "false product"), "multiplying one-step maxima"),
    ]
    count = sum(rejected(function, label) for function, label in checks)
    original = r.scalar_step
    try:
        r.scalar_step = lambda s, t: t + r.nearest(s + 56 * t)
        count += rejected(lambda: r.decode(matrix, zero, [r.U], 0),
                          "reversed quotient sign")
    finally:
        r.scalar_step = original
    output = [0] * 112
    output[0] = 1
    r.require(r.fiber_count(matrix, output, 2) == 0, "invalid parity accepted")
    return {"rejecting_controls": count + 1}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    raw = SOURCE.read_bytes()
    r.require(hashlib.sha256(raw).hexdigest() == SOURCE_HASH, "source hash mismatch")
    fixture = json.loads(raw)
    matrix = list(map(list, zip(*fixture["mode_columns"])))
    report = {"schema": "refined-native-recovery-result-v2", "no_new_kappa": True}
    for check in (source_facts, shear_checks, codec_checks, controls):
        report.update(check(matrix))
    report.update(scalar_checks())
    report["optimal_two_stage"] = optimal_verify.checks(matrix)
    report["parity_I_two_step_states"] = r.max_states(2)
    report["parity_I_naive_two_step_product"] = r.max_states(1) * 13 ** 8
    report["parity_I_two_step_state_reduction"] = report["parity_I_naive_two_step_product"] - r.max_states(2)
    report["parity_I_two_step_packed_bits"] = (r.max_states(2) - 1).bit_length()
    report["source_sha256"] = SOURCE_HASH
    report["package_sha256"] = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                                for path in sorted(HERE.iterdir()) if path.is_file()
                                and path.name not in {"RESULT.json", "VALIDATION.md"}}
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(rendered)
    print(rendered, end="")
    print("PASS_REFINED_NATIVE_RECOVERY")


if __name__ == "__main__":
    main()
