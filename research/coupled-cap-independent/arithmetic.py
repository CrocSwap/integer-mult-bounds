# SPDX-License-Identifier: Apache-2.0
"""Exact fixed-point square-root enclosures, independent of retained log/exp code."""

from fractions import Fraction
from math import isqrt

SCALE = 1 << 256
EXP_BITS = 160
WIDTHS = (4, 5, 6, 7, 8, 9)
CAPACITIES = (8, 16, 32, 48)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def ceil_div(numerator, denominator):
    return -(-numerator // denominator)


def power_interval(x, exponent):
    """Enclose x**exponent using 160 iterated roots and integer rounding."""
    require(1 <= x <= 73 and 0 <= exponent <= Fraction(1, 100), "power domain")
    numerator = exponent.numerator * (1 << EXP_BITS)
    lower_bits = numerator // exponent.denominator
    upper_bits = ceil_div(numerator, exponent.denominator)
    low = x.numerator * SCALE // x.denominator
    high = ceil_div(x.numerator * SCALE, x.denominator)
    product_low = product_high = SCALE
    for j in range(1, EXP_BITS + 1):
        low = isqrt(low * SCALE)
        square = high * SCALE
        root = isqrt(square)
        high = root + int(root * root < square)
        bit = 1 << (EXP_BITS - j)
        if lower_bits & bit:
            product_low = product_low * low // SCALE
        if upper_bits & bit:
            product_high = ceil_div(product_high * high, SCALE)
    return Fraction(product_low, SCALE), Fraction(product_high, SCALE)


def child_intervals(lower, upper):
    return {
        r: (r * power_interval(Fraction(73, r), lower)[0],
            r * power_interval(Fraction(73, r), upper)[1])
        for r in range(1, 49)
    }


def moment(profile, exponent, replicas):
    require(replicas > 0, "positive replica count")
    low = high = Fraction(0)
    for rank, count in profile.items():
        require(1 <= rank <= 48 and count >= 0, "moment child domain")
        a, b = power_interval(Fraction(73, rank), exponent)
        low += count * rank * a
        high += count * rank * b
    denominator = 73 * 896 * replicas
    return low / denominator, high / denominator


def catalogue():
    """Enumerate multisets by extending one width at a time, without recursion."""
    result = []
    for capacity in CAPACITIES:
        states = [((), capacity)]
        for width in WIDTHS:
            states = [
                (counts + (n,), left - n * width)
                for counts, left in states
                for n in range(left // width + 1)
            ]
        result.extend((capacity, counts, left) for counts, left in states)
    require(len(result) == 2551, "complete packing pattern domain")
    return result


def features(capacity, counts):
    return tuple(int(capacity == c) for c in CAPACITIES) + counts


def dual_coefficients(basis):
    """Solve B^T y = c_B, keeping costs as four formal idle-rank symbols."""
    idle_ranks = (1, 3, 5, 48)
    rows = []
    for capacity, counts, idle in basis:
        rows.append(list(map(Fraction, features(capacity, counts))) +
                    [Fraction(idle == r) for r in idle_ranks])
    for col in range(10):
        pivot = next((i for i in range(col, 10) if rows[i][col]), None)
        require(pivot is not None, "nonsingular primal basis")
        rows[col], rows[pivot] = rows[pivot], rows[col]
        divisor = rows[col][col]
        rows[col] = [v / divisor for v in rows[col]]
        for i in range(10):
            if i != col:
                multiple = rows[i][col]
                rows[i] = [a - multiple * b
                           for a, b in zip(rows[i], rows[col], strict=True)]
    return [row[10:] for row in rows]


def check_primal(certificate, inventory, local):
    patterns = catalogue()
    basis, amounts = [], []
    for entry in certificate["basis_patterns"]:
        ws = entry["widths"]
        require(all(w in WIDTHS for w in ws), "primal width alphabet")
        pattern = (entry["capacity"], tuple(ws.count(w) for w in WIDTHS),
                   entry["capacity"] - sum(ws))
        require(pattern in patterns, "capacity-feasible primal pattern")
        basis.append(pattern)
        amounts.append(Fraction(entry["count_per_replica"]))
    require(len(basis) == len(set(basis)) == 10, "ten distinct basis columns")
    require(all(n >= 0 for n in amounts), "nonnegative primal")
    rhs = (672, 448, 448, 448) + tuple(9 * inventory[w] for w in WIDTHS)
    for i in range(10):
        require(sum(n * features(c, ns)[i]
                    for (c, ns, _), n in zip(basis, amounts, strict=True)) == rhs[i],
                "complete primal conservation")
    require({int(r): n for r, n in certificate["local_per_call"].items()} == local,
            "cap/local profile binding")
    require({int(w): n for w, n in certificate["inventory_per_call"].items()}
            == inventory, "cap/inventory binding")
    return patterns, basis, amounts, rhs


def check_dual(patterns, basis, rhs, intervals):
    dual = dual_coefficients(basis)
    idle_ranks = (1, 3, 5, 48)
    residue = (-3, -6, -12, 0, 0, 0, 1, 2, 3, 4)
    tight, margins = [], []
    for capacity, counts, idle in patterns:
        column = features(capacity, counts)
        coefficients = {r: Fraction(int(r == idle)) for r in range(1, 49)}
        for j, rank in enumerate(idle_ranks):
            coefficients[rank] -= sum(column[i] * dual[i][j] for i in range(10))
        coefficients = {r: c for r, c in coefficients.items() if c}
        if not coefficients:
            tight.append((capacity, counts))
            expected = 20 * int(capacity == 48 and counts == (0, 0, 0, 0, 0, 5))
            require(sum(a * b for a, b in zip(residue, column, strict=True))
                    == expected, "tight pattern residue identity")
        else:
            margin = sum(c * intervals[r][int(c < 0)]
                         for r, c in coefficients.items())
            require(margin > 0, "strict reduced cost on complete root interval")
            margins.append(margin)
    require(len(tight) == 12 and len(margins) == 2539, "dual domain partition")
    require(sum(a * b for a, b in zip(residue, rhs, strict=True)) == 1323,
            "replica residue coefficient")
    return tight, min(margins)
