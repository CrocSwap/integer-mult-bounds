"""Complete dyadic-prefix census with integer significands.

No predecessor imports. Ross Richardson with OpenAI Codex. Apache-2.0.
"""
from fractions import Fraction as F
import hashlib
import struct


def schedule(p, guards):
    if type(p) is not int or not 1 <= p <= 15:
        raise ValueError("target must be an integer in 1..15")
    if type(guards) is not int or not 0 <= guards <= 3:
        raise ValueError("guards must be an integer in 0..3")
    out, m = [6], 1
    while m < p:
        m = min(2 * m, p)
        out.append(m + guards)
    return out


def rounded_step(prefix, numerator, bits, t):
    """x=numerator/2**bits; prefix=floor(c*2**t)."""
    u = prefix * numerator // (1 << bits)
    return numerator * ((2 << t) - u) // (1 << bits)


def grid_census(p, guards=2, step=rounded_step, with_outputs=False):
    ts = schedule(p, guards)
    top = max(ts)
    size, out_bits = 1 << top, ts[-1]
    denominator = size * (1 << out_bits)
    limit = F(1, 1 << (p + 1))
    outputs = bytearray()
    maximum = minimum_limit = prior = None
    failures, output_runs = [], 0
    for j in range(size, 2 * size):
        a, bits = 5, 3
        for t in ts:
            a = step(j >> (top - t), a, bits, t)
            bits = t
        if a <= 0:
            raise ValueError("nonpositive output")
        outputs.extend(struct.pack(">Q", a))
        output_runs += a != prior
        prior = a
        left_num = denominator - j * a
        right_num = denominator - (j + 1) * a
        maximum = left_num if maximum is None else max(maximum, left_num)
        minimum_limit = right_num if minimum_limit is None else min(minimum_limit, right_num)
        # [left,right): equality at the left fails; equality at the excluded
        # right limit alone does not imply a failure in the input domain.
        if left_num * (1 << (p + 1)) >= denominator:
            lo, hi, x = F(j, size), F(j + 1, size), F(a, 1 << bits)
            cut = (1 - limit) / x
            failures.append({"cell": j, "output": str(x), "sign": "positive",
                             "lo": str(lo), "hi": str(min(hi, cut)),
                             "lo_closed": True, "hi_closed": cut < hi})
        if right_num * (1 << (p + 1)) < -denominator:
            lo, hi, x = F(j, size), F(j + 1, size), F(a, 1 << bits)
            cut = (1 + limit) / x
            failures.append({"cell": j, "output": str(x), "sign": "negative",
                             "lo": str(max(lo, cut)), "hi": str(hi),
                             "lo_closed": True, "hi_closed": False})
    row = {"target": p, "guards": guards, "working_bits": ts,
            "grid_bits": top, "cells": size, "output_runs": output_runs,
            "outputs_sha256": hashlib.sha256(outputs).hexdigest(),
            "max_left_residual": str(F(maximum, denominator)),
            "min_right_residual_limit": str(F(minimum_limit, denominator)),
            "positive_slack": str(limit - F(maximum, denominator)),
            "negative_limit_slack": str(limit + F(minimum_limit, denominator)),
            "failures": failures}
    return (row, bytes(outputs)) if with_outputs else row


def certificate(with_outputs=False):
    pairs = [grid_census(p, with_outputs=True) for p in range(1, 16)]
    positive, positive_outputs = grid_census(15, 3, with_outputs=True)
    rows = [r for r, _ in pairs]
    receipt = {"schema_version": 1,
            "claim": "complete real-input first-failure census; no_new_kappa",
            "domain": "1 <= c < 2; integer p=1..15; fixed seed5/8, warm-up6, two guards",
            "digest_encoding": "SHA256 of one unsigned 64-bit big-endian final-grid significand per increasing finest-prefix cell",
            "total_two_guard_cells": sum(r["cells"] for r in rows),
            "first_failing_target": next(r["target"] for r in rows if r["failures"]),
            "rows": rows, "three_guard_positive_control": positive}
    return (receipt, [out for _, out in pairs] + [positive_outputs]) if with_outputs else receipt
