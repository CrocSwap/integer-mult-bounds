#!/usr/bin/env python3
"""Exact corroboration of the written all-precision reciprocal guard lemma.

Prepared for @ToikY with OpenAI Codex assistance. Apache-2.0.
The finite census is not the proof of the all-precision theorem.
"""
import argparse
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = "upstream/build/sections/09-exact-arithmetic.tex"
SOURCE_SHA = "5714e5d0656c78c6a1fde8d01fd11f1ba856a7ea94149b283bd9a50fdbf516c3"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def floor_grid(z, t):
    require(type(t) is int and t >= 1, "positive integer precision required")
    z = F(z)
    scale = 1 << t
    return F((z.numerator * scale) // z.denominator, scale)


def step(c, x, t):
    c, x = F(c), F(x)
    ct = floor_grid(c, t)
    u = floor_grid(ct * x, t)
    out = floor_grid(x * (2 - u), t)
    delta = F(1, 1 << t)
    e = 1 - c * x
    h, eta1, eta2 = c - ct, u - ct * x, out - x * (2 - u)
    require(0 <= h < delta and -delta < eta1 <= 0 and -delta < eta2 <= 0,
            "directed rounding interval")
    residual = 1 - c * out
    require(residual == e * e - c * h * x * x + c * x * eta1 - c * eta2,
            "signed residual identity")
    if 1 <= c < 2 and abs(e) <= F(1, 2):
        require(e * e - F(15, 4) * delta < residual < e * e + 2 * delta,
                "asymmetric residual bounds")
    return ct, u, out


def reciprocal(c, p, guards=3, warmup=True, stale_prefix=False):
    c = F(c)
    require(1 <= c < 2, "normalized input outside [1,2)")
    require(type(p) is int and p >= 1, "positive integer target required")
    require(type(guards) is int and guards >= 0, "nonnegative integer guards required")
    x = F(5, 8)
    trace = []
    if warmup:
        ct, u, x = step(c, x, 6)
        trace.append((1, 6, ct, u, x))
    m = 1
    while m < p:
        m = min(2 * m, p)
        t = m + guards
        read = floor_grid(c, 6) if stale_prefix else c
        ct, u, x = step(read, x, t)
        trace.append((m, t, ct, u, x))
    return x, trace


def polynomial_add(*polys):
    out = {}
    for poly in polys:
        for key, value in poly.items():
            out[key] = out.get(key, F(0)) + value
    return {key: value for key, value in out.items() if value}


def polynomial_mul(a, b):
    out = {}
    for ka, va in a.items():
        for kb, vb in b.items():
            key = tuple(x + y for x, y in zip(ka, kb))
            out[key] = out.get(key, F(0)) + va * vb
    return {key: value for key, value in out.items() if value}


def polynomial_scale(a, n):
    return {key: value * n for key, value in a.items() if value * n}


def symbolic_checks():
    # Five independent formal variables: c, h=c-c_t, x, a=-eta1, b=-eta2.
    one = {(0, 0, 0, 0, 0): F(1)}
    variables = []
    for i in range(5):
        key = [0] * 5
        key[i] = 1
        variables.append({tuple(key): F(1)})
    c, h, x, a, b = variables
    ct = polynomial_add(c, polynomial_scale(h, -1))
    u = polynomial_add(polynomial_mul(ct, x), polynomial_scale(a, -1))
    xp = polynomial_add(polynomial_mul(x, polynomial_add(polynomial_scale(one, 2),
                         polynomial_scale(u, -1))), polynomial_scale(b, -1))
    lhs = polynomial_add(one, polynomial_scale(polynomial_mul(c, xp), -1))
    e = polynomial_add(one, polynomial_scale(polynomial_mul(c, x), -1))
    rhs = polynomial_add(polynomial_mul(e, e),
          polynomial_scale(polynomial_mul(polynomial_mul(c, h), polynomial_mul(x, x)), -1),
          polynomial_scale(polynomial_mul(polynomial_mul(c, x), a), -1), polynomial_mul(c, b))
    require(lhs == rhs, "formal signed residual identity")
    # Uniform upper slack: v=2^-(2m-m'), s=epsilon/2^-(m+1), c.
    v, s, c = variables[:3]
    s2 = polynomial_mul(s, s)
    upper = polynomial_add(polynomial_scale(one, F(1, 2)),
            polynomial_scale(polynomial_mul(v, s2), F(-1, 4)), polynomial_scale(c, F(-1, 8)))
    decomposition = polynomial_add(
        polynomial_scale(polynomial_add(one, polynomial_scale(v, -1)), F(1, 4)),
        polynomial_scale(polynomial_mul(v, polynomial_add(one, polynomial_scale(s2, -1))), F(1, 4)),
        polynomial_scale(polynomial_add(polynomial_scale(one, 2), polynomial_scale(c, -1)), F(1, 8)))
    require(upper == decomposition, "uniform upper slack decomposition")
    require(F(1, 2) - F(15, 32) == F(1, 32), "uniform lower slack")
    require(F(9, 64) + F(2, 64) == F(11, 64) < F(1, 4), "warm-up upper")
    require(-F(15, 256) > -F(1, 4), "warm-up lower")
    return {"residual_identity_monomials": len(lhs), "slack_identity_monomials": len(upper),
            "three_guard_lower_slack": "1/32", "warmup_upper": "11/64"}


def sharp_invariant_witness():
    rows = []
    for guards, c, x in ((0, F(1), F(49, 64)), (1, F(11, 8), F(35, 64)),
                         (2, F(11, 8), F(35, 64)), (3, F(11, 8), F(35, 64))):
        initial = 1 - c * x
        require(abs(initial) < F(1, 4), "counterexample initial invariant")
        ct, u, out = step(c, x, 2 + guards)
        residual = 1 - c * out
        passes = abs(residual) <= F(1, 8)
        require(passes == (guards == 3), "guard counterexample changed")
        warmup, _ = reciprocal(c, 1)
        if guards < 3:
            require(warmup != x, "counterexample is not the actual warm-up state")
        rows.append({"guards": guards, "c": str(c), "x": str(x), "initial_residual": str(initial),
                     "ct": str(ct), "u": str(u), "out": str(out),
                     "residual": str(residual), "passes": passes, "actual_warmup": str(warmup)})
    actual_warmup, _ = reciprocal(F(11, 8), 1)
    require(actual_warmup == F(45, 64), "reachable-state distinction")
    return {"actual_warmup_at_11_over_8": str(actual_warmup), "steps": rows,
            "scope": "Sharp for propagation from every admitted invariant state; actual two-guard routine optimality remains open."}


def encoded(trace):
    return [[m, t, str(c), str(u), str(x)] for m, t, c, u, x in trace]


def census(max_p=8):
    # A common fine cell fixes every input prefix in both implementations.
    spec = importlib.util.spec_from_file_location("reciprocal_integer_checker", HERE / "independent.py")
    independent = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(independent)
    hashes = {3: hashlib.sha256(), 5: hashlib.sha256()}
    cells = 0
    outer_steps = {3: 0, 5: 0}
    rows = []
    for p in range(1, max_p + 1):
        T = max(6, p + 5)
        scale = 1 << T
        margins = {3: None, 5: None}
        for k in range(scale, 2 * scale):
            c, upper = F(k, scale), F(k + 1, scale)
            for guards in (3, 5):
                out, trace = reciprocal(c, p, guards)
                other_num, other_bits, other_trace = independent.reciprocal(k, T, p, guards)
                converted = [[s["m"], s["t"], str(F(s["c_prefix"], 1 << s["t"])),
                              str(F(s["u_num"], 1 << s["t"])),
                              str(F(s["x_num"], 1 << s["x_bits"]))] for s in other_trace]
                require(out == F(other_num, 1 << other_bits) and encoded(trace) == converted,
                        "independent full trace mismatch")
                previous = F(5, 8)
                for s in other_trace:
                    require(previous == F(s["input_x_num"], 1 << s["input_x_bits"]),
                            "incoming iterate precision was discarded")
                    previous = F(s["x_num"], 1 << s["x_bits"])
                bound = F(1, 1 << (p + 1))
                margin = bound - max(abs(1 - c * out), abs(1 - upper * out))
                require(margin >= 0, "cell endpoint residual bound")
                require(out > 0, "positive output")
                for m, t, ct, u, x in trace:
                    require(max(abs(1 - c * x), abs(1 - upper * x)) <= F(1, 1 << (m + 1)),
                            "intermediate cell invariant")
                if margins[guards] is None or margin < margins[guards]:
                    margins[guards] = margin
                outer_steps[guards] += len(trace)
                payload = json.dumps([p, k, T, encoded(trace)], separators=(",", ":")).encode()
                hashes[guards].update(payload + b"\n")
            cells += 1
        rows.append({"p": p, "common_cell_bits": T, "cells": scale,
                     "candidate_min_margin": str(margins[3]), "baseline_min_margin": str(margins[5])})
    return {"cells": cells, "rows": rows, "rounded_steps": outer_steps,
            "trace_sha256": {g: h.hexdigest() for g, h in hashes.items()}}


def mathematical_controls():
    missing, _ = reciprocal(F(1), 1, warmup=False)
    require(abs(1 - missing) > F(1, 4), "omitted warm-up must fail")
    c = F(129, 128)
    stale, _ = reciprocal(c, 12, stale_prefix=True)
    require(abs(1 - c * stale) > F(1, 1 << 13), "stale-prefix control must fail")
    return {"omitted_warmup": {"c": "1", "p": 1, "out": str(missing)},
            "stale_prefix": {"c": str(c), "p": 12, "out": str(stale)}}


def build_certificate():
    require(hashlib.sha256((ROOT / SOURCE).read_bytes()).hexdigest() == SOURCE_SHA,
            "pinned Section09 source bytes changed")
    return {"schema_version": 1, "scope": "Written uniform three-guard reciprocal theorem; finite exact corroboration only.",
            "source_sha256": SOURCE_SHA, "symbolic": symbolic_checks(),
            "invariant_counterexample": sharp_invariant_witness(),
            "census": census(), "controls": mathematical_controls()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", type=Path)
    args = parser.parse_args()
    report = build_certificate()
    raw = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.write_receipt:
        with args.write_receipt.open("x") as stream:
            stream.write(raw)
    else:
        require(json.loads((HERE / "CERTIFICATE.json").read_text()) == json.loads(raw),
                "certificate content changed")
    print("PASS_RECIPROCAL_DIRECTED_GUARDS cells=" + str(report["census"]["cells"]) + " invariant_guards=3")


if __name__ == "__main__":
    main()
