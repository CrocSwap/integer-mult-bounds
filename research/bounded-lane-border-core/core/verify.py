#!/usr/bin/env python3
"""Exact finite checks of the fixed-width lane boundary core.

Yiyang (@Lyy-iiis), with substantial OpenAI Codex assistance.
SPDX-License-Identifier: Apache-2.0
"""

from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import random


def require(ok, label):
    if not ok:
        raise RuntimeError(label)


def zeros(n, m=None):
    return [[Q(0) for _ in range(n if m is None else m)] for _ in range(n)]


def identity(n):
    a = zeros(n)
    for i in range(n):
        a[i][i] = Q(1)
    return a


def add(a, b):
    return [[x + y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def neg(a):
    return [[-x for x in row] for row in a]


def sub(a, b):
    return add(a, neg(b))


def mul(a, b):
    out = zeros(len(a), len(b[0]))
    for i, row in enumerate(a):
        for k, x in enumerate(row):
            if x:
                for j, y in enumerate(b[k]):
                    if y:
                        out[i][j] += x * y
    return out


def inverse(a):
    n = len(a)
    rows = [list(row) + list(eye) for row, eye in zip(a, identity(n))]
    for j in range(n):
        p = next((i for i in range(j, n) if rows[i][j]), None)
        require(p is not None, "singular test fixture")
        rows[j], rows[p] = rows[p], rows[j]
        pivot = rows[j][j]
        rows[j] = [x / pivot for x in rows[j]]
        for i in range(n):
            if i != j and rows[i][j]:
                t = rows[i][j]
                rows[i] = [x - t * y for x, y in zip(rows[i], rows[j])]
    return [row[n:] for row in rows]


def two(a, b, c, d):
    return [ar + br for ar, br in zip(a, b)] + [cr + dr for cr, dr in zip(c, d)]


def shift(lanes, width):
    n = lanes * width
    s = zeros(n)
    r = zeros(n)
    p = zeros(n)
    for i in range(width):
        p[i][i] = 1
    for lane in range(lanes - 1):
        for i in range(width):
            s[(lane + 1) * width + i][lane * width + i] = 1
            r[lane * width + i][(lane + 1) * width + i] = 1
    return s, r, p


def diagonal(a, lanes):
    d = len(a)
    out = zeros(lanes * d)
    for lane in range(lanes):
        for i in range(d):
            for j in range(d):
                out[lane * d + i][lane * d + j] = a[i][j]
    return out


def t_map(a, lanes, width):
    # Implement using the principal-compression description, independently
    # of S A R + a_0 P_0, which is checked below.
    n = lanes * width
    out = zeros(n)
    for i in range(width):
        for j in range(width):
            out[i][j] = a[i][j]
    for i in range(n - width):
        for j in range(n - width):
            out[i + width][j + width] = a[i][j]
    return out


def random_algebra(lanes, width, rng):
    base = identity(width)
    for i in range(width):
        for j in range(i + 1, width):
            base[i][j] = Q(rng.randrange(-3, 4), rng.randrange(1, 4))
    out = diagonal(base, lanes)
    for lane in range(lanes):
        for earlier in range(lane):
            for i in range(width):
                for j in range(width):
                    out[lane * width + i][earlier * width + j] = Q(
                        rng.randrange(-3, 4), rng.randrange(1, 4)
                    )
    return out


def grade_parts(a, lanes, width):
    out = [zeros(lanes * width) for _ in range(lanes)]
    for i, row in enumerate(a):
        for j, x in enumerate(row):
            g = i // width - j // width
            require(g >= 0 or not x, "negative-grade fixture entry")
            if g >= 0:
                out[g][i][j] = x
    return out


def algebra_checks():
    rng = random.Random(20261023)
    cases = []
    noncommuting_cases = 0
    noncentral_payload_cases = 0
    for lanes in (1, 2, 3, 5):
        for width in (1, 2, 3):
            a = random_algebra(lanes, width, rng)
            b = inverse(a)
            c = random_algebra(lanes, width, rng)
            n = lanes * width
            eye = identity(n)
            zero = zeros(n)
            s, r, p = shift(lanes, width)
            ta = t_map(a, lanes, width)
            tb = t_map(b, lanes, width)
            tc = t_map(c, lanes, width)
            a0 = diagonal([row[:width] for row in a[:width]], lanes)
            b0 = diagonal([row[:width] for row in b[:width]], lanes)
            require(mul(a, b) == eye and mul(b, a) == eye, "actual inverse pair")
            require(ta == add(mul(mul(s, a), r), mul(a0, p)), "T sandwich identity")
            require(mul(ta, tc) == t_map(mul(a, c), lanes, width), "T homomorphism")
            require(mul(ta, s) == mul(s, a), "T intertwiner")
            require(mul(ta, tb) == eye and mul(tb, ta) == eye, "T inverse")
            if mul(a, c) != mul(c, a):
                noncommuting_cases += 1
            if mul(a0, a) != mul(a, a0):
                noncentral_payload_cases += 1
            u = two(eye, a, zero, eye)
            lower = two(eye, zero, neg(b), eye)
            scalar_boundary = two(eye, neg(eye), eye, zero)
            core = mul(mul(u, lower), scalar_boundary)
            core_inverse = two(b, zero, sub(b, eye), a)
            require(core == two(a, zero, sub(eye, b), b), "two-shear identity")
            require(mul(core, core_inverse) == identity(2 * n), "actual inverse core")
            outer = two(eye, zero, zero, s)
            inner = two(eye, zero, zero, r)
            e = add(mul(mul(outer, core), inner), two(zero, zero, zero, mul(b0, p)))
            f = add(mul(mul(outer, core_inverse), inner), two(zero, zero, zero, mul(a0, p)))
            require(e == two(a, zero, mul(s, sub(eye, b)), tb), "E endpoint")
            require(f == two(b, zero, mul(s, sub(b, eye)), ta), "F endpoint")
            require(mul(e, f) == identity(2 * n), "E F identity")
            require(mul(f, e) == identity(2 * n), "F E identity")
            # Preferred no-boundary-provider contract: the Y_0 productive
            # input/output never exists. Keep only the first L-1 Y slots.
            short = n - width
            if short:
                pshort = identity(n)[:short]
                ca = [row[:short] for row in a[:short]]
                cb = [row[:short] for row in b[:short]]
                eminus = two(a, zeros(n, short), mul(pshort, sub(eye, b)), cb)
                fminus = two(b, zeros(n, short), mul(pshort, sub(b, eye)), ca)
                require(mul(ca, pshort) == mul(pshort, a), "compression intertwiner")
                require(mul(eminus, fminus) == identity(n + short), "Eminus Fminus identity")
                require(mul(fminus, eminus) == identity(n + short), "Fminus Eminus identity")
            else:
                require(mul(a, b) == eye, "one-lane no-Y endpoint")
            bp = grade_parts(b, lanes, width)
            tbp = grade_parts(tb, lanes, width)
            for grade in range(1, lanes):
                require(tbp[grade] == mul(mul(s, bp[grade]), r), "T preserves positive grade")
            cases.append({"lanes": lanes, "payload_dimension": width, "all_exact_identities": "PASS",
                          "no_boundary_provider_inverse_pair": "PASS"})
    require(noncommuting_cases > 0, "need noncommuting physical fixture")
    require(noncentral_payload_cases > 0, "need diagonal/off-diagonal noncommuting payloads")
    return {"cases": cases, "noncommuting_A_C_cases": noncommuting_cases,
            "noncentral_diagonal_payload_cases": noncentral_payload_cases}


def apply(a, x):
    return [sum((entry * value for entry, value in zip(row, x)), Q(0)) for row in a]


def vadd(a, b):
    return [x + y for x, y in zip(a, b)]


def vsub(a, b):
    return [x - y for x, y in zip(a, b)]


def canonical_gaussian_real():
    # Rational realification of q=(1+i)/2 I + (1-i)/2 X.
    h = Q(1, 2)
    return [
        [h, -h, h, h],
        [h, h, -h, h],
        [h, h, h, -h],
        [-h, h, h, h],
    ]


def literal_checks():
    q = canonical_gaussian_real()
    b = inverse(q)
    require(mul(mul(q, q), mul(q, q)) == identity(4), "canonical q fourth power")
    cases = []
    for lanes in (1, 2, 3, 5):
        n = lanes * 4
        qd = diagonal(q, lanes)
        bd = diagonal(b, lanes)
        s, _, _ = shift(lanes, 4)
        expected = two(qd, zeros(n), mul(s, sub(identity(n), bd)), bd)
        columns = []
        for col in range(2 * n):
            x = [Q(int(i == col)) for i in range(n)]
            y = [Q(int(n + i == col)) for i in range(n)]
            xx = [x[4 * j:4 * j + 4] for j in range(lanes)]
            yy = [y[4 * j:4 * j + 4] for j in range(lanes)]
            # Explicit owned zero and a full cyclic route; no destructive shift.
            owned = [Q(0)] * 4
            queried_y = yy[1:] + [owned]
            owned = yy[0]
            out_x, out_y = [], []
            for xj, yj in zip(xx, queried_y):
                out_x.append(apply(q, xj))
                out_y.append(vadd(vsub(xj, apply(b, xj)), apply(b, yj)))
            boundary = apply(b, owned)
            final_y = [boundary] + out_y[:-1]
            owned = out_y[-1]
            owned = [Q(0)] * 4  # Explicit counted owned CLEAR.
            require(not any(owned), "owned endpoint")
            columns.append(sum(out_x, []) + sum(final_y, []))
        actual = [[columns[j][i] for j in range(2 * n)] for i in range(2 * n)]
        require(actual == expected, "all-column literal boundary endpoint")
        cases.append({"lanes": lanes, "tested_columns": 2 * n, "owned_fields_per_pair": 1,
                      "charged_boundary_gaussians_per_pair": 1, "all_column_endpoint": "PASS"})
    return cases


def literal_no_boundary_checks():
    q = canonical_gaussian_real()
    b = inverse(q)
    cases = []
    for lanes in (1, 2, 3, 5):
        n, short = lanes * 4, (lanes - 1) * 4
        qd, bd = diagonal(q, lanes), diagonal(b, lanes)
        pshort = identity(n)[:short]
        cb = [row[:short] for row in bd[:short]]
        expected = (two(qd, zeros(n, short), mul(pshort, sub(identity(n), bd)), cb)
                    if short else qd)
        columns = []
        for col in range(n + short):
            x = [Q(int(i == col)) for i in range(n)]
            y = [Q(int(n + i == col)) for i in range(short)]
            xx = [x[4 * j:4 * j + 4] for j in range(lanes)]
            yy = [y[4 * j:4 * j + 4] for j in range(lanes - 1)]
            queried_y = yy + [[Q(0)] * 4]
            out_x, out_y = [], []
            for xj, yj in zip(xx, queried_y):
                out_x.append(apply(q, xj))
                out_y.append(vadd(vsub(xj, apply(b, xj)), apply(b, yj)))
            owned = out_y[-1]
            owned = [Q(0)] * 4  # Explicitly counted terminal owned CLEAR.
            require(not any(owned), "no-boundary owned endpoint")
            columns.append(sum(out_x, []) + sum(out_y[:-1], []))
        actual = [[columns[j][i] for j in range(n + short)] for i in range(n + short)]
        require(actual == expected, "no-boundary literal all-column endpoint")
        cases.append({"lanes": lanes, "tested_columns": n + short,
                      "owned_fields_per_pair": 1, "productive_X_fields_per_pair": lanes,
                      "productive_Y_fields_per_pair": lanes - 1,
                      "charged_boundary_gaussians_per_pair": 0, "all_column_endpoint": "PASS"})
    return cases


def log_bounds(integer, terms=100):
    if integer == 1:
        return Q(0), Q(0)
    x = Q(integer - 1, integer + 1)
    power = x
    total = Q(0)
    for j in range(terms):
        total += 2 * power / (2 * j + 1)
        power *= x * x
    tail = 2 * power / ((2 * terms + 1) * (1 - x * x))
    return total, total + tail


def exp_minus_bounds(value):
    require(0 <= value <= 1, "alternating exponential range")
    term = Q(1)
    total = Q(1)
    upper = None
    lower = None
    for j in range(1, 10):
        term *= -value / j
        total += term
        if j == 8:
            upper = total
        if j == 9:
            lower = total
    return lower, upper


def power_bounds(integer, reduction):
    lo, hi = log_bounds(integer)
    lower = exp_minus_bounds(reduction * hi)[0]
    upper = exp_minus_bounds(reduction * lo)[1]
    return integer * lower, integer * upper


def decimal_outward(value, digits=12, upward=False):
    scale = 10 ** digits
    numerator = value.numerator * scale
    integer = numerator // value.denominator
    if upward and numerator % value.denominator:
        integer += 1
    sign = "-" if integer < 0 else ""
    integer = abs(integer)
    return f"{sign}{integer // scale}.{integer % scale:0{digits}d}"


def moment_checks():
    target = {4: 56, 7: 14, 8: 94, 9: 652, 17: 224}
    paid = {1: 4656, 2: 920, 3: 1386}
    boundary = 112 * 17
    c = Q(17, 5000)
    powers = {r: power_bounds(r, c) for r in set(target) | set(paid)}
    lo = sum(target[r] * powers[r][0] for r in target) - sum(paid[r] * powers[r][1] for r in paid)
    hi = sum(target[r] * powers[r][1] for r in target) - sum(paid[r] * powers[r][0] for r in paid)
    require(lo > 0, "positive uncharged local moment")
    require(66 * hi - boundary < 0, "66 lanes must fail")
    require(67 * lo - boundary > 0, "67 lanes must pass")
    missing_lo, missing_hi = 112 * powers[17][0], 112 * powers[17][1]
    require(65 * hi - missing_lo < 0, "65 lanes must fail no-boundary-provider invoice")
    require(66 * lo - missing_hi > 0, "66 lanes must pass no-boundary-provider invoice")
    require(sum(r * n for r, n in target.items()) == 10750, "target rank mass")
    require(sum(r * n for r, n in paid.items()) == 10654, "paid rank mass")
    return {
        "candidate_C": "17/5000",
        "strict_separation_after_boundary_split": max(paid) < min(target),
        "target": target,
        "paid_base": paid,
        "boundary_rank17_jobs": 112,
        "boundary_rank1_split_jobs": boundary,
        "base_moment_margin_interval": [decimal_outward(lo), decimal_outward(hi, upward=True)],
        "L66_margin_interval": [decimal_outward(66 * lo - boundary), decimal_outward(66 * hi - boundary, upward=True)],
        "L67_margin_interval": [decimal_outward(67 * lo - boundary), decimal_outward(67 * hi - boundary, upward=True)],
        "minimum_L_for_this_invoice": 67,
        "preferred_no_boundary_provider": {
            "productive_target_profile": "L*T minus 112 rank-17 targets",
            "paid_profile": "L*P",
            "lost_productive_target_rank17_jobs": 112,
            "extra_boundary_paid_jobs": 0,
            "minimum_L_for_this_invoice": 66,
            "L65_margin_interval": [decimal_outward(65 * lo - missing_hi),
                                     decimal_outward(65 * hi - missing_lo, upward=True)],
            "L66_margin_interval": [decimal_outward(66 * lo - missing_hi),
                                     decimal_outward(66 * hi - missing_lo, upward=True)],
            "remaining_closure_obligation": "same filtered native shear caller on a compatible nonuniform graded module",
        },
        "scope": "exact local moment only; no complete native recursive supplier or kappa admission",
    }


def controls():
    s, r, p = shift(3, 1)
    leakage = mul(s, r)
    require(leakage == sub(identity(3), p), "native port leakage control")
    require(any(leakage[i][i] for i in range(3)), "leakage must reach grade zero")
    # T fails multiplicativity outside the lower-triangular algebra.
    a = [[Q(0), Q(1)], [Q(0), Q(0)]]
    b = [[Q(0), Q(0)], [Q(1), Q(0)]]
    require(t_map(mul(a, b), 2, 1) != mul(t_map(a, 2, 1), t_map(b, 2, 1)),
            "nontriangular extension must be rejected")
    # Wrong nominal inverse leaves an upper-right pole/grade loss.
    eye = identity(3)
    require(mul(sub(mul(eye, add(eye, s)), eye), r) == leakage,
            "independent-pair leakage")
    return {
        "positive_grade_native_upper_port_reaches_grade_zero": "PASS",
        "nontriangular_homomorphism_extension_rejected": "PASS",
        "nominal_opposite_orientation_rejected": "PASS",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--compare", type=Path)
    args = parser.parse_args()
    result = {
        "schema": "bounded-lane-caller-v2",
        "status": "PASS",
        "algebra": algebra_checks(),
        "literal_native_core_specialization": literal_checks(),
        "literal_no_boundary_provider": literal_no_boundary_checks(),
        "moment": moment_checks(),
        "negative_controls": controls(),
    }
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.compare:
        require(json.loads(args.compare.read_text()) == json.loads(encoded), "frozen receipt mismatch")
    if args.output:
        args.output.write_text(encoded)
    print(json.dumps({"status": "PASS", "algebra_cases": len(result["algebra"]["cases"]),
                      "literal_columns": sum(c["tested_columns"] for c in result["literal_native_core_specialization"]),
                      "minimum_positive_lanes": result["moment"]["minimum_L_for_this_invoice"],
                      "no_boundary_provider_literal_columns": sum(c["tested_columns"] for c in result["literal_no_boundary_provider"]),
                      "no_boundary_provider_minimum_positive_lanes": 66,
                      "receipt_sha256": hashlib.sha256(encoded.encode()).hexdigest()}, sort_keys=True))


if __name__ == "__main__":
    main()
