"""Replay all changed-word scalar divisions and calculate the width of a raw context."""

from fractions import Fraction
from math import gcd, prod
from pathlib import Path
import json
import sys


def audit(runtime):
    sys.path.insert(0, str(runtime))
    from upstream import install

    install()
    from strong_complex import GRID, ODD, DYADIC, load_changed, digest
    from spool import short_divisors

    data = runtime / "inputs"
    graph, layout = load_changed(data)
    assert (
        digest(graph)
        == "ed3bea7186f962f3a8a8ae389cecce3d1ef48a7a832cf9af6c9048a6b5919b35"
    )
    n = len(graph["initial"])
    stocks = {~i: {i: GRID} for i in range(n)}
    mass = {~i: Fraction(1) for i in range(n)}
    moves = {k for k, _, _ in graph["moves"]}
    forms = {k: [(s, Fraction(c)) for s, c in row] for k, row in graph["forms"]}
    want = [{i: GRID} for i in range(n)]
    for i, x in enumerate(layout["live"]):
        y = x + 112
        if i in layout["hosted"]["Dports"]:
            want[y][x] = GRID
        else:
            want[x][y] = -GRID
            want[y] = {x: GRID // 2, y: GRID // 2}
    for x, y in zip(layout["hosted"]["X2"], layout["hosted"]["Y2"], strict=True):
        want[x][y] = -GRID
    peak = Fraction(1)
    common = GRID
    factors = set()
    total = divisions = 0
    for k in graph["schedule"]:
        row = {}
        weight = Fraction(0)
        for s, c in forms[k]:
            a, b = c.numerator, c.denominator
            factors.add(c)
            weight += abs(c) * mass[s]
            for i, v in stocks[s].items():
                quotient, rem = divmod(v, b)
                if rem:
                    raise ArithmeticError(
                        f"inexact physical division: node {k}, donor {s}, basis {i}, numerator {a}, denominator {b}, input {v}, remainder {rem}"
                    )
                term = a * quotient
                if common != 1:
                    common = gcd(common, term)
                row[i] = row.get(i, 0) + term
            count = len(stocks[s])
            total += count
            divisions += count if b != 1 else 0
        peak = max(peak, weight)
        nonzero = {i: v for i, v in row.items() if v}
        if k in moves:
            stocks[k] = nonzero
            mass[k] = weight
        else:
            assert nonzero == want[k - graph["first_output"]], k
    largest = width = 0
    for c in factors | {Fraction(ODD), Fraction(1, ODD)}:
        pieces = short_divisors(c.denominator)
        assert prod(pieces) == c.denominator and all(1 < v < 2**24 for v in pieces)
        largest = max(largest, *pieces, 0)
        width = max(width, c.numerator.bit_length(), c.denominator.bit_length())
    assert common == 1 and ODD << DYADIC == GRID
    return dict(
        grid=GRID,
        odd=ODD,
        dyadic=DYADIC,
        roles=n,
        products=total,
        nontrivial=divisions,
        peak=str(peak),
        distinct_literals=len(factors),
        maximum_literal_bits=width,
        largest_divisor=largest,
    )


if __name__ == "__main__":
    if not __debug__:
        raise ValueError("Run with assertions enabled")
    print(json.dumps(audit(Path(sys.argv[1]).resolve()), sort_keys=True), flush=True)
