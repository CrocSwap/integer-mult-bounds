#!/usr/bin/env python3
"""Exact finite corroboration of the binomial suffix theorem.

Produced by Nick Petalas. Apache-2.0.
"""

from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path

MAX_N = 32
MAX_STATES = 256


def require(ok, message):
    if not ok:
        raise AssertionError(message)


def identity(n):
    return tuple(tuple(F(i == j) for j in range(n)) for i in range(n))


def multiply(a, b):
    n = len(a)
    rows = []
    for row in a:
        active = tuple((k, value) for k, value in enumerate(row) if value)
        rows.append(tuple(sum((v * b[k][j] for k, v in active), F(0))
                          for j in range(n)))
    return tuple(rows)


def norm(a):
    return max(sum(map(abs, row)) for row in a)


def toeplitz(f):
    return tuple(tuple(f[i - j] if i >= j else F(0)
                       for j in range(len(f))) for i in range(len(f)))


def diagonal(a, b):
    m = len(a)
    return tuple(tuple(a[i][j] if i < m and j < m else
                       b[i - m][j - m] if i >= m and j >= m else F(0)
                       for j in range(2 * m)) for i in range(2 * m))


def logical_order(a):
    n = len(a)
    position = tuple(i // 2 + (n // 2 if i % 2 else 0) for i in range(n))
    return tuple(tuple(a[i][j] for j in position) for i in position)


def split(f, wrong_sign=False):
    m = len(f) // 2
    e, o = f[::2], f[1::2]
    k = [F(0)] * m
    for i in range(m):
        k[i] = o[i] - sum((e[j] * k[i - j] for j in range(1, i + 1)), F(0))
    s = list(e)
    for i in range(1, m):
        correction = sum((o[j] * k[i - 1 - j] for j in range(i)), F(0))
        s[i] += correction if wrong_sign else -correction
    left, right = [list(r) for r in identity(2 * m)], [list(r) for r in identity(2 * m)]
    for i in range(m):
        for j in range(i + 1):
            left[m + i][j] = k[i - j]
            if i > j:
                right[i][m + j] = k[i - j - 1]
    return e, tuple(s), tuple(map(tuple, left)), tuple(map(tuple, right))


def all_cuts(f):
    """Bottom-up exact (prefix, suffix) pairs for all child interleavings."""
    n = len(f)
    if not (1 <= n <= MAX_N and n & (n - 1) == 0 and f[0] == 1):
        raise ValueError("expected a bounded unit dyadic symbol")
    symbols = [f]
    for index in range(2 * n - 1):
        node = symbols[index]
        if len(node) > 1:
            e, s, _, _ = split(node)
            symbols.extend((e, s))
    require(len(symbols) == 2 * n - 1, "full binary tree capacity")
    states = {}
    for node in reversed(symbols):
        size = len(node)
        unit, target = identity(size), toeplitz(node)
        if size == 1:
            states[node] = {(unit, unit)}
            continue
        e, s, left, right = split(node)
        endpoint = logical_order(multiply(left, multiply(diagonal(toeplitz(e), toeplitz(s)), right)))
        require(endpoint == target, "literal parity endpoint")
        pairs = {(unit, target), (target, unit)}
        require(len(states[e]) * len(states[s]) + 2 <= MAX_STATES, "cut capacity")
        for pe, qe in states[e]:
            for ps, qs in states[s]:
                p = logical_order(multiply(diagonal(pe, ps), right))
                q = logical_order(multiply(left, diagonal(qe, qs)))
                require(multiply(q, p) == target, "suffix times prefix")
                pairs.add((p, q))
        states[node] = pairs
    return states[f]


def prediction(c, depth):
    return F(1) + sum((abs(c) ** (2 ** j) for j in range(depth)), F(0))


def witness_row(c, depth):
    n = 2 ** depth
    row = [F(0)] * n
    row[-1] = F(1)
    coefficient = c
    for j in range(depth):
        row[n - 1 - 2 ** j] = coefficient
        coefficient = -coefficient ** 2
    return tuple(row)


def check_fixture(c, depth):
    n = 2 ** depth
    f = (F(1),) if n == 1 else (F(1), c, *([F(0)] * (n - 2)))
    pairs = all_cuts(f)
    bound = prediction(c, depth)
    maximum = max(norm(q) for _, q in pairs)
    require(maximum == bound, "exact binomial forward-suffix maximum")
    witnesses = [(p, q) for p, q in pairs if q[-1] == witness_row(c, depth)]
    require(bool(witnesses), "literal attaining last row")
    if depth >= 2 and c:
        require(any(p != identity(n) and p != toeplitz(f) for p, _ in witnesses),
                "attaining proper nontrivial cut")
    require(norm(toeplitz(f)) == (F(1) if depth == 0 else F(1) + abs(c)),
            "completed endpoint norm")
    if abs(c) == 1:
        require(maximum == 1 + depth, "critical logarithmic law")
    return {"c": str(c), "depth": depth, "n": n, "cut_pairs": len(pairs),
            "maximum_suffix_norm": str(maximum)}


def controls():
    passed = []
    f = (F(1), F(1, 2), F(0), F(0))
    e, s, left, right = split(f, wrong_sign=True)
    require(logical_order(multiply(left, multiply(diagonal(toeplitz(e), toeplitz(s)), right)))
            != toeplitz(f), "wrong Schur sign rejection")
    passed.append("wrong Schur sign")
    e, s, left, right = split(f)
    middle = diagonal(toeplitz(e), toeplitz(s))
    require(logical_order(multiply(middle, right)) != toeplitz(f), "missing left shear rejection")
    passed.append("missing left shear")
    require(logical_order(multiply(right, multiply(middle, left))) != toeplitz(f),
            "reversed order rejection")
    passed.append("reversed order")
    require(max(norm(q) for _, q in all_cuts(f)) > norm(toeplitz(f)),
            "endpoint is not a suffix bound")
    passed.append("endpoint-only bound")
    shifted = (F(1), F(0), F(1, 2), F(0))
    require(max(norm(q) for _, q in all_cuts(shifted)) != prediction(F(0), 2),
            "binomial support hypothesis is necessary")
    passed.append("non-binomial support")
    for bad in ((F(1),) * 3, (F(2), F(0)), (F(1),) * 64):
        try:
            all_cuts(bad)
        except ValueError:
            passed.append(f"invalid domain of length {len(bad)}")
            continue
        raise AssertionError("invalid symbol accepted")
    return passed


def main():
    coefficients = tuple(map(F, (0, 1, -1, 2, -2))) + (F(1, 2), F(-1, 2), F(3, 2))
    records = [check_fixture(c, depth) for c in coefficients for depth in range(6)]
    passed_controls = controls()
    pair_count = sum(record["cut_pairs"] for record in records)
    root = Path(__file__).resolve().parent
    names = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {name: sha256((root / name).read_bytes()).hexdigest() for name in names}
    print(json.dumps({"claim_type": "scoped proof with finite corroboration",
                      "fixtures": records, "cut_pairs": pair_count, "controls": passed_controls,
                      "source_sha256": hashes}, indent=2))
    print(f"PASS_BINOMIAL_SUFFIX fixtures={len(records)} controls={len(passed_controls)}")


if __name__ == "__main__":
    main()
