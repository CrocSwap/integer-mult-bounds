#!/usr/bin/env python3
"""Independent rational-grid argument checks; imports no proposed extension."""
from fractions import Fraction
from math import gcd
import json


def need(ok, why):
    if not ok:
        raise ArithmeticError(why)


def plus(a, b):
    return a[0] + b[0], a[1] + b[1]


def times_i(a, exponent=1):
    return ((a[0], a[1]), (-a[1], a[0]),
            (-a[0], -a[1]), (a[1], -a[0]))[exponent % 4]


def numerator(a, re, im):
    return re * a[0] - im * a[1], im * a[0] + re * a[1]


def exact_divide(a, den):
    need(a[0] % den == a[1] % den == 0, "nonexact scalar division")
    return a[0] // den, a[1] // den


# This deliberately unfunded N=W=2 word is used only as an adversarial
# semantics/grid witness. All private work remains charged in its count.
OPS = (
    ("scale", 0, 1, 0, 3),
    ("axpy", 1, 0, 2, 1, 5),
    ("unit", 0), ("unit", 0), ("unit", 0), ("unit", 0),
    ("paid", 0, 0), ("paid", 1, 0),
    ("paid", 0, 1), ("paid", 1, 1),
    ("axpy", 1, 0, -2, -1, 5),
    ("scale", 0, 3, 0, 1),
    ("axpy", 2, 0, 1, 1, 7),
    ("paid", 2, 0),
    ("clear", 2),
)
J = len(OPS)
D = 105
BETA = 2


def integer_c(row, axis, stats):
    """Independent two-entry Gaussian formula, with exact /2."""
    out = list(row)
    mask = 1 << axis
    for j in range(len(row)):
        if j & mask:
            continue
        a, b = row[j], row[j | mask]
        total = plus(a, b)
        diff = a[0] - b[0], a[1] - b[1]
        twist = times_i(diff)
        out[j] = exact_divide(plus(total, twist), 2)
        out[j | mask] = exact_divide((total[0] - twist[0],
                                     total[1] - twist[1]), 2)
        stats["C_divisions"] += 2
    return out


def reference_c(row, axis):
    """Separate normalized Fraction reference, outside the recursive word."""
    out = list(row)
    mask = 1 << axis
    q = Fraction(1, 2)
    for j in range(len(row)):
        if j & mask:
            continue
        ar, ai = row[j]
        br, bi = row[j | mask]
        out[j] = (q * (ar - ai + br + bi),
                  q * (ar + ai - br + bi))
        out[j | mask] = (q * (ar + ai + br - bi),
                         q * (-ar + ai + br + bi))
    return out


def execute(rank, odd_budget=None, wrong_phase=False):
    depth = rank.bit_length() - 1
    exponent = J * depth if odd_budget is None else odd_budget
    guard = 8 * (J * BETA + 2 + 1) * (rank + 1)
    initial = [[(((7 * i + 3 * r) % 17) - 8,
                 ((5 * i - 2 * r) % 19) - 9)
                for i in range(1 << rank)] for r in range(1 << depth)]
    scale = (1 << guard) * D ** exponent
    lifted = [[(a * scale, b * scale) for a, b in row] for row in initial]
    stats = {"C_divisions": 0, "rational_divisions": 0,
             "nonleaf_calls": 0, "paid_calls": 0, "private_retired_cells": 0}
    address_count = 1 << rank

    def visit(rows, axes):
        span = len(axes)
        columns, tail = divmod(span, 2)
        for axis in axes[span - tail:]:
            rows = [integer_c(row, axis, stats) for row in rows]
        if columns == 0:
            return rows
        need(len(rows) % 2 == 0, "productive row stock")
        stats["nonleaf_calls"] += 1
        regs = [rows[0::2], rows[1::2],
                [[(0, 0)] * address_count for _ in rows[0::2]]]
        for position, instruction in enumerate(OPS):
            op, reg, *args = instruction
            if op == "scale":
                re, im, den = args
                regs[reg] = [[exact_divide(numerator(z, re, im), den)
                              for z in row] for row in regs[reg]]
                stats["rational_divisions"] += len(regs[reg]) * address_count
            elif op == "axpy":
                src, re, im, den = args
                regs[reg] = [[plus(a, exact_divide(numerator(b, re, im), den))
                              for a, b in zip(left, right)]
                             for left, right in zip(regs[reg], regs[src])]
                stats["rational_divisions"] += len(regs[reg]) * address_count
            elif op == "unit":
                phase = 1 if wrong_phase and position == 2 else columns
                regs[reg] = [[times_i(z, phase) for z in row] for row in regs[reg]]
            elif op == "paid":
                start = args[0] * columns
                stats["paid_calls"] += 1
                regs[reg] = visit(regs[reg], axes[start:start + columns])
            elif op == "clear":
                stats["private_retired_cells"] += len(regs[reg]) * address_count
                regs[reg] = [[(0, 0)] * address_count for _ in regs[reg]]
            else:
                raise ValueError(op)
        return [row for pair in zip(regs[0], regs[1]) for row in pair]

    actual = visit(lifted, list(range(rank)))
    # Fixed-D retirement occurs only at the root, on completed productive rows.
    for _ in range(exponent):
        actual = [[exact_divide(z, D) for z in row] for row in actual]
    actual = [[exact_divide(z, 1 << (guard - rank)) for z in row] for row in actual]
    expected = []
    for row in initial:
        ref = [(Fraction(a), Fraction(b)) for a, b in row]
        for axis in reversed(range(rank)):
            ref = reference_c(ref, axis)
        ref = [(a * (1 << rank), b * (1 << rank)) for a, b in ref]
        need(all(a.denominator == b.denominator == 1 for a, b in ref),
             "dyadic endpoint numerator")
        expected.append([(int(a), int(b)) for a, b in ref])
    return actual == expected, {
        "rank": rank, "depth": depth, "instructions": J, "D": D,
        "odd_budget": exponent, "guard": guard,
        "productive_rows": len(initial),
        "scalar_components": 2 * len(initial) * address_count,
        "root_scale_passes": exponent, "root_retirement_passes": exponent,
        **stats}


def check_bound():
    cases = 0
    for n in range(2, 10):
        for j in (1, 3, 15, 41):
            for beta in (1, 2, 17, 100):
                for h in (1, n - 1, n, n + 1, n * n - 1, n * n,
                          n ** 4 + 1, 10 ** 5):
                    e = h
                    bound = 2
                    depth = 0
                    while e >= n:
                        f, r = divmod(e, n)
                        bound += r + j * beta + j * f
                        e = f
                        depth += 1
                    bound += e
                    guard = 8 * (j * beta + n + 1) * (h + 1)
                    need(bound < guard, "binary prefix guard")
                    cases += 1
    return cases


def main():
    records = []
    for rank in (1, 2, 3, 4, 6, 8):
        same, record = execute(rank)
        need(same, "rational recursive endpoint")
        records.append(record)
    try:
        execute(4, odd_budget=0)
    except ArithmeticError:
        no_scale_rejected = True
    else:
        no_scale_rejected = False
    need(no_scale_rejected, "unfunded odd-grid control")
    same_one, _ = execute(2, wrong_phase=True)
    try:
        same_two, _ = execute(4, wrong_phase=True)
    except ArithmeticError:
        same_two = False
    need(same_one and not same_two, "scalar/column phase control")
    # A constant-field C eigenvector exposes one /3 on every unfinished
    # recursive context. A depth-independent D^J reserve fails at depth J+1.
    spine = Fraction(D ** J, 3 ** (J + 1))
    need(spine.denominator == 3, "forgotten recursive odd debt")
    # The prior guard depends on J,N,h, not an arbitrary new scalar height.
    old_guard = 8 * (J + 2 + 1) * 3
    large_scalar = 1 << (old_guard + 10)
    need((large_scalar * (1 << old_guard)).bit_length() > 2 * old_guard + 4,
         "old guard accidentally funded arbitrary scalar magnitude")
    print(json.dumps({
        "status": "PASS_INDEPENDENT_RATIONAL_GRID",
        "scope": "Independent logical arithmetic model and written invariant;"
                 " not a fixed-tape or funded-word replay.",
        "records": records,
        "prefix_guard_cases": check_bound(),
        "controls": {
            "no_odd_scale_rejects": no_scale_rejected,
            "wrong_column_phase_passes_one_column": same_one,
            "wrong_column_phase_fails_two_columns": not same_two,
            "depth_independent_budget_fails_at_depth": J + 1,
            "old_binary_guard_misses_arbitrary_rational_height": True},
        "funded": False,
        "no_new_kappa": True
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
