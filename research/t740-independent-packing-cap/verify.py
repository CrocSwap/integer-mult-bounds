#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent all-pattern packing-cap audit; execute no predecessor code."""

import argparse
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
import json
from math import gcd, lcm
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
WIDTHS = (4, 5, 6, 7, 8, 9)
CAPACITIES = (8, 16, 32, 48)
BIN_COUNTS = (672, 448, 448, 448)
INVENTORY = (26, 2, 16, 52, 99, 213)
SCALE = 1 << 320
SQUARINGS = 128
LOG_STEPS = 112


def need(condition, message):
    if not condition:
        raise ValueError(message)


def ceil_q(value):
    return -((-value.numerator) // value.denominator)


def exp_bounds(lower, upper=None):
    """Euler bounds followed by 128 outward-rounded integer squarings.

    (1+x/N)^N <= exp(x) <= (1-x/N)^(-N), N=2^128.
    This uses neither a Taylor exponential nor floating-point operations.
    """
    upper = lower if upper is None else upper
    need(type(lower) in (int, Q) and type(upper) in (int, Q), "exact exponential inputs")
    lower, upper = Q(lower), Q(upper)
    need(0 <= lower <= upper <= 8, "exponential domain")
    n = 1 << SQUARINGS
    a = (SCALE * (1 + lower / n)).__floor__()
    b = ceil_q(SCALE / (1 - upper / n))
    for _ in range(SQUARINGS):
        a = a * a // SCALE
        b = (b * b + SCALE - 1) // SCALE
    return Q(a, SCALE), Q(b, SCALE)


@lru_cache(maxsize=64)
def log_bounds(value):
    """Invert certified Euler bounds by rational bisection, never libm."""
    need(1 <= value <= 73, "logarithm domain")
    if value == 1:
        return Q(0), Q(0)
    lower, upper = Q(0), Q(8)
    for _ in range(LOG_STEPS):
        middle = (lower + upper) / 2
        a, b = exp_bounds(middle)
        if b < value:
            lower = middle
        elif a > value:
            upper = middle
        else:
            raise ValueError("logarithm sign unresolved")
    return lower, upper


def rank_bounds(rank, lower, upper):
    a, b = log_bounds(Q(73, rank))
    a, b = exp_bounds(lower * a, upper * b)
    return rank * a, rank * b


def enumerate_patterns():
    """Depth-first enumeration by remaining capacity."""
    def fill(index, remaining, counts):
        if index == len(WIDTHS):
            yield tuple(counts), remaining
            return
        width = WIDTHS[index]
        for count in range(remaining // width + 1):
            yield from fill(index + 1, remaining - count * width, counts + [count])

    return [(cap, counts, idle) for cap in CAPACITIES
            for counts, idle in fill(0, cap, [])]


def column(pattern):
    cap, counts, _ = pattern
    return tuple(int(cap == c) for c in CAPACITIES) + counts


def rref(matrix, variables):
    """Fraction elimination; trailing columns can be symbolic RHS coordinates."""
    rows = [[Q(x) for x in row] for row in matrix]
    pivot_row, pivots = 0, []
    for col in range(variables):
        hit = next((i for i in range(pivot_row, len(rows)) if rows[i][col]), None)
        if hit is None:
            continue
        rows[pivot_row], rows[hit] = rows[hit], rows[pivot_row]
        divisor = rows[pivot_row][col]
        rows[pivot_row] = [x / divisor for x in rows[pivot_row]]
        for i, row in enumerate(rows):
            if i != pivot_row and row[col]:
                multiple = row[col]
                rows[i] = [x - multiple * y for x, y in zip(row, rows[pivot_row])]
        pivots.append(col)
        pivot_row += 1
    return rows, pivots


def parse_basis(certificate, catalogue):
    need(certificate["inventory_per_call"] == dict(zip(map(str, WIDTHS), INVENTORY)),
         "fixed width inventory")
    basis, amounts = [], []
    for entry in certificate["basis_patterns"]:
        cap, widths = entry["capacity"], entry["widths"]
        need(type(cap) is int and type(widths) is list and
             all(type(w) is int and w in WIDTHS for w in widths), "basis alphabet")
        pattern = (cap, tuple(widths.count(w) for w in WIDTHS), cap - sum(widths))
        need(pattern in catalogue, "infeasible basis pattern")
        amount = Q(entry["count_per_replica"])
        need(amount >= 0, "negative primal amount")
        basis.append(pattern)
        amounts.append(amount)
    need(len(basis) == len(set(basis)) == 10, "ten distinct basis patterns")
    return basis, amounts


def divisor_witness(tight, rhs):
    """Derive the primitive integer row isolating the five-nine pattern."""
    target = (48, (0, 0, 0, 0, 0, 5), 3)
    need(target in tight, "five-nine tight pattern")
    rows, pivots = rref([column(p) for p in tight if p != target], 10)
    free = [i for i in range(10) if i not in pivots]
    need(len(free) == 1, "one-dimensional tight annihilator")
    vector = [Q(i == free[0]) for i in range(10)]
    for row, pivot in zip(rows, pivots):
        vector[pivot] = -row[free[0]]
    denominator = lcm(*(v.denominator for v in vector))
    vector = [int(v * denominator) for v in vector]
    common = gcd(*vector)
    vector = [v // common for v in vector]
    coefficient = sum(a * b for a, b in zip(vector, column(target)))
    if coefficient < 0:
        vector = [-v for v in vector]
        coefficient = -coefficient
    total = sum(a * b for a, b in zip(vector, rhs))
    need(all(sum(a * b for a, b in zip(vector, column(p))) ==
             (coefficient if p == target else 0) for p in tight), "tight annihilator")
    need(coefficient > 0 and gcd(coefficient, total) == 1, "coprime residue")
    return vector, coefficient, total


def audit(certificate, providers, finite):
    need((finite["replicas"], finite["calls"], finite["live"]) == (740, 6660, 663040),
         "T740 finite domain")
    catalogue = enumerate_patterns()
    need(len(catalogue) == len(set(catalogue)) == 2551, "complete pattern domain")
    basis, amounts = parse_basis(certificate, set(catalogue))
    rhs = BIN_COUNTS + tuple(9 * n for n in INVENTORY)
    need(all(sum(amount * column(p)[j] for p, amount in zip(basis, amounts)) == rhs[j]
             for j in range(10)), "primal supplies complete bins and widths")
    idle = Counter()
    for pattern, amount in zip(basis, amounts):
        if pattern[2]:
            idle[pattern[2]] += amount
    need(idle == {int(k): Q(v) for k, v in certificate["idle_per_replica"].items()},
         "primal idle histogram")

    # Solve B^T y = c_B in all independent H_r coordinates at once.
    symbols = sorted(idle)
    matrix = [list(column(p)) + [int(p[2] == r) for r in symbols] for p in basis]
    solved, pivots = rref(matrix, 10)
    need(pivots == list(range(10)), "nonsingular primal basis")
    dual = [row[10:] for row in solved]
    need(all(sum(rhs[j] * dual[j][i] for j in range(10)) == idle[r]
             for i, r in enumerate(symbols)), "symbolic primal-dual equality")

    need(set(providers) == {"gauge44", "extra"}, "provider domain")
    profiles = []
    for provider in providers.values():
        widths = provider["widths"]
        need(len(widths) == 408 and Counter(widths) == dict(zip(WIDTHS, INVENTORY)),
             "actual ordered helper inventory")
        profile = {int(r): n for r, n in provider["actual_paid_profile"].items()}
        need(all(1 <= r < 73 and type(n) is int and n > 0 for r, n in profile.items()),
             "positive local profile")
        profiles.append(profile)
    need(profiles[0] == profiles[1], "common actual local profile")
    profile = Counter({r: 6660 * n for r, n in profiles[0].items()})
    profile.update({r: 740 * n for r, n in idle.items()})
    need(all(Q(n).denominator == 1 for n in profile.values()), "integer global profile")
    need(dict(profile) == {int(r): n for r, n in finite["profile"].items()},
         "literal six-skip profile equals primal plus local work")
    need({r: int(740 * n) for r, n in idle.items()} ==
         {int(r): n for r, n in finite["idle"].items()}, "T740 idle agreement")
    need(sum(r * n for r, n in profile.items()) == 740 * 65088, "complete rank mass")

    lower, upper = map(Q, finite["moment"]["root"])
    need(0 < lower < upper <= Q(1, 100) and upper - lower <= Q(1, 10**25),
         "six-skip root bracket domain")
    intervals = {r: rank_bounds(r, lower, upper) for r in range(1, 49)}

    def moment_at(value):
        bounds = [rank_bounds(r, value, value) for r in profile]
        return tuple(sum(n * b[i] for n, b in zip(profile.values(), bounds)) /
                     (73 * 896 * 740) for i in (0, 1))

    left, right = moment_at(lower), moment_at(upper)
    need(left[1] < 1 < right[0], "independently certified cap root")
    tight, slacks = [], []
    for pattern in catalogue:
        coefficients = Counter({pattern[2]: Q(1)}) if pattern[2] else Counter()
        for j, value in enumerate(column(pattern)):
            for i, rank in enumerate(symbols):
                coefficients[rank] -= value * dual[j][i]
        coefficients = {r: v for r, v in coefficients.items() if v}
        if not coefficients:
            tight.append(pattern)
        else:
            slack = sum(value * intervals[rank][0 if value > 0 else 1]
                        for rank, value in coefficients.items())
            need(slack > 0, "strict reduced cost across root bracket")
            slacks.append(slack)
    need(len(tight) == 12 and len(slacks) == 2539, "complete tight/strict split")
    need(all(p in tight for p in basis), "primal uses only tight patterns")
    vector, divisor, total = divisor_witness(tight, rhs)
    need(divisor == 20 and total == 1341, "derived replica residue")
    need(all((20 * n).denominator == 1 for n in amounts), "integral primal at T20")
    need(all((740 * n).denominator == 1 for n in amounts), "integral primal at T740")
    source_cap = finite["moment"]["fixed_inventory_cap"]
    need(source_cap["patterns"] == len(catalogue) and
         source_cap["tight_patterns"] == len(tight) and
         source_cap["strict_patterns"] == len(slacks), "published cap counts")
    need([Q(source_cap[k]) for k in ("cap_lower", "cap_upper")] == [lower, upper],
         "published cap bracket")
    need({int(r): Q(n) for r, n in source_cap["idle_per_replica"].items()} == idle,
         "published cap idle")
    need(source_cap["invariant"]["cap_requires_T_multiple_of"] == divisor and
         source_cap["invariant"]["first_multiple_of_74"] == lcm(divisor, 74),
         "published divisibility claim")
    return {
        "status": "PASS_INDEPENDENT_T740_PACKING_CAP",
        "patterns": len(catalogue), "identically_tight": len(tight),
        "strict_across_root_bracket": len(slacks),
        "minimum_reduced_cost_lower": str(Q((min(slacks) * SCALE).__floor__(), SCALE)),
        "root_bracket": [str(lower), str(upper)],
        "left_moment_upper": str(left[1]), "right_moment_lower": str(right[0]),
        "idle_per_replica": {str(r): str(n) for r, n in sorted(idle.items())},
        "annihilator": vector, "residue_identity": {"coefficient": divisor, "rhs": total},
        "necessary_T_divisor": divisor, "first_multiple_of_74": lcm(divisor, 74),
        "tight_patterns": [[c, list(ns), idle] for c, ns, idle in tight],
        "enclosure": {"scale_bits": 320, "Euler_squarings": 128, "log_bisections": 112},
        "scope": "Fixed-inventory additive-bin relaxation only; no chronological or native admission.",
    }


def inputs():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    data = {}
    for row in manifest["files"]:
        if row["usage"] == "input":
            raw = (ROOT / row["path"]).read_bytes()
            need(sha256(raw).hexdigest() == row["sha256"], "source bytes: " + row["path"])
            data[Path(row["path"]).name] = json.loads(raw)
    return data["RELAX-CAP.json"], data["PROVIDERS.json"], data["FINITE.json"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(*inputs())
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        need(result == json.loads((PACKAGE / "RESULT.json").read_text()), "published result")
    print(result["status"], "patterns=2551 tight=12 strict=2539 divisor=20")


if __name__ == "__main__":
    main()
