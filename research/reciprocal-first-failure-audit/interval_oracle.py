"""Independent real-interval floor preimages with exact rational arithmetic.

No census or predecessor code imports. Ross Richardson with Codex. Apache-2.0.
"""
from fractions import Fraction
from hashlib import sha256
from struct import pack


def ceiling(q):
    return -(-q.numerator // q.denominator)


def advance(parts, precision):
    """q=floor(C*x) iff ceil(q/x)<=C<ceil((q+1)/x); C=floor(2**t*c)."""
    if type(precision) is not int or precision < 1:
        raise ValueError("invalid precision")
    scale, result = 2 ** precision, []
    incoming_cursor = Fraction(1)
    for left, right, x in parts:
        if not (left == incoming_cursor and left < right and x > 0):
            raise ValueError("invalid incoming interval")
        incoming_cursor = right
        c_first = (scale * left).__floor__()
        c_last = ceiling(scale * right) - 1
        q_first = (c_first * x).__floor__()
        q_last = (c_last * x).__floor__()
        cursor = left
        for q in range(q_first, q_last + 1):
            low = max(left, Fraction(ceiling(Fraction(q) / x), scale))
            high = min(right, Fraction(ceiling(Fraction(q + 1) / x), scale))
            if low >= high:
                continue
            if low != cursor:
                raise ValueError("rounding-preimage gap or overlap")
            cursor = high
            next_x = Fraction((x * (2 * scale - q)).__floor__(), scale)
            if result and result[-1][1] == low and result[-1][2] == next_x:
                result[-1] = (result[-1][0], high, next_x)
            else:
                result.append((low, high, next_x))
        if cursor != right:
            raise ValueError("rounding-preimage suffix missing")
    if incoming_cursor != 2 or not result or result[0][0] != 1 or result[-1][1] != 2:
        raise ValueError("normalized input coverage missing")
    return result


def interval_census(target, guards=2, with_outputs=False):
    if type(target) is not int or not 1 <= target <= 15:
        raise ValueError("target outside independent census")
    if type(guards) is not int or not 0 <= guards <= 3:
        raise ValueError("guards outside independent census")
    # Derive the capped schedule from powers below target, independently of
    # the mutable min(2*m,p) loop in the uniform-grid evaluator.
    interior = [2 ** k for k in range(1, target.bit_length()) if 2 ** k < target]
    precisions = [6] + ([m + guards for m in interior + [target]] if target > 1 else [])
    pieces = [(Fraction(1), Fraction(2), Fraction(5, 8))]
    for precision in precisions:
        pieces = advance(pieces, precision)
    grid_bits, final_scale = max(precisions), 2 ** precisions[-1]
    grid, bound = 2 ** grid_bits, Fraction(1, 2 ** (target + 1))
    stream, high_residual, low_residual_limit = bytearray(), None, None
    bad, cursor = [], Fraction(1)
    for left, right, x in pieces:
        if left != cursor:
            raise ValueError("final partition gap or overlap")
        cursor = right
        a, b, numerator = left * grid, right * grid, x * final_scale
        if any(v.denominator != 1 for v in (a, b, numerator)):
            raise ValueError("partition escaped the declared dyadic grid")
        stream.extend(pack(">Q", numerator.numerator) * (b.numerator - a.numerator))
        el, er = 1 - left * x, 1 - right * x
        high_residual = el if high_residual is None else max(high_residual, el)
        low_residual_limit = er if low_residual_limit is None else min(low_residual_limit, er)
        # x was found by interval preimages, never by evaluating cell samples.
        if el < bound and er >= -bound:
            continue
        for cell in range(a.numerator, b.numerator):
            lo, hi = Fraction(cell, grid), Fraction(cell + 1, grid)
            upper_cut, lower_cut = (1 - bound) / x, (1 + bound) / x
            if lo <= upper_cut:
                bad.append({"cell": cell, "output": str(x), "sign": "positive",
                            "lo": str(lo), "hi": str(min(hi, upper_cut)),
                            "lo_closed": True, "hi_closed": upper_cut < hi})
            if lower_cut < hi:
                bad.append({"cell": cell, "output": str(x), "sign": "negative",
                            "lo": str(max(lo, lower_cut)), "hi": str(hi),
                            "lo_closed": True, "hi_closed": False})
    row = {"target": target, "guards": guards, "working_bits": precisions,
            "grid_bits": grid_bits, "cells": grid, "output_runs": len(pieces),
            "outputs_sha256": sha256(stream).hexdigest(),
            "max_left_residual": str(high_residual),
            "min_right_residual_limit": str(low_residual_limit),
            "positive_slack": str(bound - high_residual),
            "negative_limit_slack": str(bound + low_residual_limit),
            "failures": bad}
    return (row, bytes(stream)) if with_outputs else row
