"""Finite references. These use integer prices and do not import the residue solver."""
from fractions import Fraction
from itertools import product
from math import lcm


def amount_bills(rows, stop):
    """Process one width at a time. Entries are least costs over integer multisets."""
    unit = lcm(*(Fraction(price).denominator for _, price in rows))
    costs = [0] + [None] * stop
    for width, price in rows:
        fee = int(price * unit)
        for n in range(width, stop + 1):
            previous = costs[n - width]
            if previous is not None:
                candidate = previous + fee
                if costs[n] is None or candidate < costs[n]:
                    costs[n] = candidate
    return [None if x is None else Fraction(x, unit) for x in costs]


def literal_bills(rows, stop):
    """Enumerate every count vector with total width <= stop directly."""
    costs = [None] * (stop + 1)
    visited = 0
    for counts in product(*(range(stop // w + 1) for w, _ in rows)):
        n = sum(w * k for (w, _), k in zip(rows, counts, strict=True))
        if n > stop:
            continue
        visited += 1
        fee = sum(c * k for (_, c), k in zip(rows, counts, strict=True))
        if costs[n] is None or fee < costs[n]:
            costs[n] = fee
    return costs, visited


def common_bills(cuts, parent, stop):
    tables = [(q, amount_bills(rows, q * stop)) for q, rows in cuts]
    out = [None]
    for a in range(1, stop + 1):
        bills = [values[q*a] for q, values in tables]
        out.append(None if None in bills else sum(bills) / (a * parent))
    return out


def strict_records(bills):
    best = None
    points = []
    for a, price in enumerate(bills[1:], start=1):
        if price is not None and (best is None or price < best):
            points.append((a, price))
            best = price
    return points
