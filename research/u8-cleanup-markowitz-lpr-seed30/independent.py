#!/usr/bin/env python3
"""Genuinely independent integer-lattice verifier for u8-cleanup-markowitz-lpr-seed30.

Disjoint from verify.py and from upstream hpe_*.py:
- Represents each dyadic row vector x in (Z[1/2])^728 as a pair (coeffs, shift)
  where coeffs: dict[int, int] maps column index j -> odd/integer numerator c_j in Z
  and shift >= 0 is the shared binary exponent such that x_j = c_j / 2^shift.
- Uses no fractions.Fraction in row state evolution.
- Independently checks:
  1. Exact operator equality Mat(W_lpr) == Mat(W_baseline) on all 728 columns
     in both forward and dual (inverse-transpose) orientations.
  2. Target isolation (112..223) and hyperplane-ended helper isolation (126 helpers).
  3. Full 16,609-gate raw U8 arbitrary-dirt endpoint replay on all 728 columns
     in both forward and backward orientations.
  4. Exact binary Horner real-component primitive bounds for baseline and LPR cleanup.

Prepared with Gemini 4 Argon assistance. Apache-2.0; see NOTICE.md.
"""
import gzip
import hashlib
import json
import pathlib
import sys
import tarfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(cond, msg):
    if not cond:
        raise RuntimeError(f"INDEPENDENT CHECK FAILED: {msg}")


def _normalize_row(coeffs, shift):
    clean = {j: val for j, val in coeffs.items() if val != 0}
    if not clean:
        return {}, 0
    while shift > 0 and all((val & 1) == 0 for val in clean.values()):
        clean = {j: val >> 1 for j, val in clean.items()}
        shift -= 1
    return clean, shift


def init_identity_rows(n):
    return [({r: 1}, 0) for r in range(n)]


def apply_gate_int(gate, rows):
    op = gate[0]
    if op == "scale":
        dst, num, den = int(gate[1]), int(gate[2]), int(gate[3])
        if den < 0:
            num, den = -num, -den
        require(num != 0 and (abs(num) & (abs(num) - 1)) == 0, f"non-power-of-two scale num: {gate}")
        require(den > 0 and (den & (den - 1)) == 0, f"non-power-of-two scale den: {gate}")
        coeffs, shift = rows[dst]
        if not coeffs:
            return
        num_sh = abs(num).bit_length() - 1
        den_sh = den.bit_length() - 1
        sign = -1 if num < 0 else 1
        if num_sh >= den_sh:
            mul = sign << (num_sh - den_sh)
            new_coeffs = {j: v * mul for j, v in coeffs.items()}
            rows[dst] = _normalize_row(new_coeffs, shift)
        else:
            add_sh = den_sh - num_sh
            new_coeffs = {j: v * sign for j, v in coeffs.items()} if sign < 0 else dict(coeffs)
            rows[dst] = _normalize_row(new_coeffs, shift + add_sh)
    elif op == "add":
        dst, src, num, den = int(gate[1]), int(gate[2]), int(gate[3]), int(gate[4])
        if den < 0:
            num, den = -num, -den
        require(dst != src, f"self-addition gate: {gate}")
        require(den > 0 and (den & (den - 1)) == 0, f"non-dyadic add den: {gate}")
        if num == 0:
            return
        s_coeffs, s_shift = rows[src]
        if not s_coeffs:
            return
        d_coeffs, d_shift = rows[dst]
        den_sh = den.bit_length() - 1
        term_shift = s_shift + den_sh
        target_shift = max(d_shift, term_shift)
        d_scale = 1 << (target_shift - d_shift)
        t_scale = num * (1 << (target_shift - term_shift))
        merged = {j: v * d_scale for j, v in d_coeffs.items()} if d_scale != 1 else dict(d_coeffs)
        for j, v in s_coeffs.items():
            nv = merged.get(j, 0) + v * t_scale
            if nv:
                merged[j] = nv
            else:
                merged.pop(j, None)
        rows[dst] = _normalize_row(merged, target_shift)
    else:
        raise RuntimeError(f"unknown gate op: {op}")


def dual_gate(gate):
    if gate[0] == "add":
        return ["add", gate[2], gate[1], -int(gate[3]), int(gate[4])] + list(gate[5:])
    elif gate[0] == "scale":
        num, den = int(gate[2]), int(gate[3])
        return ["scale", gate[1], den, num] + list(gate[4:])
    raise RuntimeError(f"unknown gate op: {gate[0]}")


def horner_real_primitives(gate):
    op = gate[0]
    if op == "scale":
        num, den = int(gate[2]), int(gate[3])
        if den < 0:
            num, den = -num, -den
        a = abs(num)
        b = den
        g = a
        x = b
        while x:
            g, x = x, g % x
        a //= g
        b //= g
        require(a > 0 and (a & (a - 1)) == 0 and (b & (b - 1)) == 0, f"invalid scale: {gate}")
        return 2 * (abs(a.bit_length() - b.bit_length()) + (1 if num < 0 else 0))
    elif op == "add":
        num, den = int(gate[3]), int(gate[4])
        if den < 0:
            num, den = -num, -den
        a = abs(num)
        b = den
        require(a > 0 and b > 0, f"invalid add coeff: {gate}")
        g = a
        x = b
        while x:
            g, x = x, g % x
        a //= g
        b //= g
        require((b & (b - 1)) == 0, f"non-dyadic add denominator: {gate}")
        return 2 * (3 + (a.bit_length() - 1) + a.bit_count() + (b.bit_length() - 1))
    raise RuntimeError(f"unknown gate op: {op}")


def eval_word_int(word, n, backward=False):
    rows = init_identity_rows(n)
    for g in word:
        apply_gate_int(dual_gate(g) if backward else g, rows)
    return rows


def run_independent_checks():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    expected = json.loads((HERE / "EXPECTED.json").read_text())
    recipe = json.loads((HERE / "RECIPE.json").read_text())

    tar_path = ROOT / sources["replay_bundle"]["path"]
    require(
        hashlib.sha256(tar_path.read_bytes()).hexdigest() == sources["replay_bundle"]["sha256"],
        "t37-replay.tar.gz sha256 mismatch",
    )

    with tarfile.open(tar_path, "r:gz") as tf:
        fw_raw = gzip.decompress(tf.extractfile("native/barch/FULL-WORD.json.gz").read())
        cw_raw = gzip.decompress(tf.extractfile("native/local/CANONICAL-WORD.json.gz").read())

    require(
        hashlib.sha256(fw_raw).hexdigest()
        == sources["replay_bundle"]["members"]["native/barch/FULL-WORD.json.gz"]["content_sha256"],
        "FULL-WORD.json.gz content sha256 mismatch",
    )
    require(
        hashlib.sha256(cw_raw).hexdigest()
        == sources["replay_bundle"]["members"]["native/local/CANONICAL-WORD.json.gz"]["content_sha256"],
        "CANONICAL-WORD.json.gz content sha256 mismatch",
    )

    fw = json.loads(fw_raw.decode())
    cw = json.loads(cw_raw.decode())
    n = 728
    v = 112

    base_cleanup = cw["cleanup"]
    lpr_cleanup = recipe["cleanup_word"]

    require(len(base_cleanup) == 6105, f"expected 6105 baseline cleanup gates, got {len(base_cleanup)}")
    require(len(lpr_cleanup) == 3525, f"expected 3525 LPR cleanup gates, got {len(lpr_cleanup)}")

    # 1. Check target isolation and HPE helper isolation on lpr_cleanup
    hpe_helpers = {r for r in range(2 * v, n) if cw["final"][r] != 1}
    require(len(hpe_helpers) == 126, f"expected 126 HPE helpers, got {len(hpe_helpers)}")
    for idx, g in enumerate(lpr_cleanup):
        regs = [int(g[1])] + ([int(g[2])] if g[0] == "add" else [])
        require(int(g[-1]) == 1, f"gate {idx} not at frame 1: {g}")
        for r in regs:
            require(0 <= r < n, f"register out of range in gate {idx}: {r}")
            require(not (v <= r < 2 * v), f"LPR cleanup gate {idx} touches target register {r}")
            require(r not in hpe_helpers, f"LPR cleanup gate {idx} touches HPE helper {r}")

    # 2. Check exact integer-lattice operator equality in both orientations
    for backward in (False, True):
        rows_base = eval_word_int(base_cleanup, n, backward=backward)
        rows_lpr = eval_word_int(lpr_cleanup, n, backward=backward)
        require(
            rows_base == rows_lpr,
            f"cleanup operator mismatch between baseline and LPR (backward={backward})",
        )

    # 3. Check exact Horner primitive bounds
    for backward in (False, True):
        base_prims = sum(horner_real_primitives(dual_gate(g) if backward else g) for g in base_cleanup)
        lpr_prims = sum(horner_real_primitives(dual_gate(g) if backward else g) for g in lpr_cleanup)
        require(base_prims == 68714, f"baseline prims mismatch: {base_prims}")
        require(lpr_prims == 31394, f"LPR prims mismatch: {lpr_prims}")

    # 4. Full 16,609-gate raw U8 arbitrary-dirt endpoint replay in pure integer arithmetic
    tau = lambda x: x ^ (43 if (x & 43).bit_count() % 2 else 0)
    ports = cw["ports"]
    mapping = {i: ports.index(tau(p)) for i, p in enumerate(fw["ports"])}
    mapping.update({v + i: v + mapping[i] for i in range(v)})
    mapping.update({r: r for r in range(2 * v, n)})
    inv_mapping = {can_r: raw_r for raw_r, can_r in mapping.items()}

    main_gates = fw["A"] + fw["cut"] + fw["B"]
    mat_main = eval_word_int(main_gates, n, backward=False)
    dirty_rows = [({}, 0) for _ in range(n)]
    for r in range(v, 2 * v):
        c_dict, sh = mat_main[r]
        dirty_rows[r] = _normalize_row({j: val for j, val in c_dict.items() if j >= 2 * v}, sh)
    for g in fw["precondition"]:
        apply_gate_int(g, dirty_rows)

    compensation = []
    for r in range(v, 2 * v):
        c_dict, sh = dirty_rows[r]
        den = 1 << sh
        for j in sorted(c_dict.keys()):
            num = -c_dict[j]
            g = abs(num)
            x = den
            while x:
                g, x = x, g % x
            compensation.append(["add", r, j, num // g, den // g, []])

    require(len(compensation) == 6320, f"expected 6320 compensation gates, got {len(compensation)}")

    early_tail = [fw["cleanup"][i][:-1] + [f] for i, f in fw["early_cleanup"]]
    full_raw_frame = [256, 128, 64, 32, 16, 8, 4, 2, 1]
    raw_lpr_rest = [
        ["add", inv_mapping[g[1]], inv_mapping[g[2]], g[3], g[4], full_raw_frame]
        if g[0] == "add"
        else ["scale", inv_mapping[g[1]], g[2], g[3], full_raw_frame]
        for g in lpr_cleanup
    ]

    full_program = fw["precondition"] + compensation + main_gates + early_tail + raw_lpr_rest
    require(len(full_program) == 16609, f"expected 16609 scalar operations, got {len(full_program)}")

    for backward in (False, True):
        actual = eval_word_int(full_program, n, backward=backward)
        for r in range(n):
            if not backward and v <= r < 2 * v:
                exp_row = ({r: 1, r - v: 1}, 0)
            elif backward and r < v:
                exp_row = ({r: 1, r + v: -1}, 0)
            else:
                exp_row = ({r: 1}, 0)
            require(
                actual[r] == exp_row,
                f"full program integer endpoint mismatch at row {r} (backward={backward}): got {actual[r]}",
            )

    summary = {
        "status": "PASS_INDEPENDENT_INTEGER_LATTICE_VERIFICATION",
        "columns_verified_each_orientation": n,
        "baseline_cleanup_macros": len(base_cleanup),
        "lpr_cleanup_macros": len(lpr_cleanup),
        "baseline_cleanup_real_primitives": 68714,
        "lpr_cleanup_real_primitives": 31394,
        "full_scalar_operations": len(full_program),
        "expected_status": expected["status"],
    }
    print(json.dumps(summary, indent=2), flush=True)
    return summary


if __name__ == "__main__":
    run_independent_checks()
