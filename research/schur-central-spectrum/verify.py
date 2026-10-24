#!/usr/bin/env python3
"""Exact finite corroboration of the scalar Schur central-spectrum identity."""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

Matrix = tuple[tuple[int, ...], ...]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def identity(n: int) -> Matrix:
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def multiply(a: Matrix, b: Matrix, q: int) -> Matrix:
    n = len(a)
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(n)) % q
                       for j in range(n)) for i in range(n))


def subtract(a: Matrix, b: Matrix, q: int) -> Matrix:
    return tuple(tuple((x - y) % q for x, y in zip(r, s, strict=True))
                 for r, s in zip(a, b, strict=True))


def scale(a: Matrix, c: int, q: int) -> Matrix:
    return tuple(tuple(c * x % q for x in row) for row in a)


def rank(a: Matrix, q: int) -> int:
    rows = [list(row) for row in a]
    height, width = len(rows), len(rows[0])
    pivot = 0
    for col in range(width):
        candidate = next((i for i in range(pivot, height) if rows[i][col]), None)
        if candidate is None:
            continue
        rows[pivot], rows[candidate] = rows[candidate], rows[pivot]
        inv = pow(rows[pivot][col], -1, q)
        rows[pivot] = [x * inv % q for x in rows[pivot]]
        for i in range(height):
            if i != pivot:
                c = rows[i][col]
                rows[i] = [(x - c * y) % q
                           for x, y in zip(rows[i], rows[pivot], strict=True)]
        pivot += 1
        if pivot == height:
            break
    return pivot


def inverse(a: Matrix, q: int) -> Matrix:
    n = len(a)
    rows = [list(row) + list(unit) for row, unit in zip(a, identity(n), strict=True)]
    for col in range(n):
        candidate = next((i for i in range(col, n) if rows[i][col]), None)
        require(candidate is not None, "singular header")
        rows[col], rows[candidate] = rows[candidate], rows[col]
        inv = pow(rows[col][col], -1, q)
        rows[col] = [x * inv % q for x in rows[col]]
        for i in range(n):
            if i != col:
                c = rows[i][col]
                rows[i] = [(x - c * y) % q
                           for x, y in zip(rows[i], rows[col], strict=True)]
    return tuple(tuple(row[n:]) for row in rows)


def validate_pair(p: Matrix, r: Matrix, q: int) -> None:
    require(q in (2, 3, 5, 7, 11), "unsupported prime")
    n = len(p)
    require(2 <= n <= 8 and len(r) == n, "matrix size outside bounded domain")
    require(all(len(row) == n for row in p + r), "nonsquare matrices")
    require(all(type(x) is int and 0 <= x < q for row in p + r for x in row),
            "noncanonical field entry")
    require(p[0][0] == r[0][0] == 1, "common identity pivot required")
    require(multiply(p, p, q) == p and multiply(r, r, q) == r,
            "idempotent inputs required")
    require(multiply(p, r, q) == multiply(r, p, q), "commuting inputs required")


def schur(p: Matrix, q: int) -> Matrix:
    return tuple(tuple((p[i][j] - p[i][0] * p[0][j]) % q
                       for j in range(1, len(p))) for i in range(1, len(p)))


def check_residual(s: Matrix, t: Matrix, h: int, q: int) -> dict[str, int]:
    unit = identity(len(s))
    d = subtract(s, t, q)
    z = multiply(d, d, q)
    c = subtract(multiply(s, t, q), multiply(t, s, q), q)
    theta = h * (2 - h) % q
    require(multiply(s, s, q) == s and multiply(t, t, q) == t,
            "residual idempotency")
    require(multiply(z, s, q) == multiply(s, z, q), "centrality with S")
    require(multiply(z, t, q) == multiply(t, z, q), "centrality with T")
    require(multiply(z, c, q) == scale(c, theta, q), "central-spectrum identity")
    require(multiply(c, c, q) == subtract(multiply(z, z, q), z, q),
            "universal commutator square")
    polynomial = multiply(multiply(z, subtract(z, unit, q), q),
                          subtract(z, scale(unit, theta, q), q), q)
    require(not any(map(any, polynomial)), "cubic annihilator")
    require(rank(c, q) <= 2, "scalar deletion rank bound")
    return {"h": h, "theta": theta, "commutator_rank": rank(c, q),
            "central_rank": rank(z, q),
            "central_idempotent": int(multiply(z, z, q) == z)}


def diagonal(values: tuple[int, ...]) -> Matrix:
    n = len(values)
    return tuple(tuple(values[i] if i == j else 0 for j in range(n))
                 for i in range(n))


def split_header(a: tuple[int, ...], b: tuple[int, ...], q: int) -> Matrix:
    n = len(a)
    require(sum(x * y for x, y in zip(a, b, strict=True)) % q == 1,
            "split functional must send first column to one")
    pivot = next(i for i, x in enumerate(b) if x)
    columns = [a]
    for j in range(n):
        if j != pivot:
            v = [0] * n
            v[j] = 1
            v[pivot] = -b[j] * pow(b[pivot], -1, q) % q
            columns.append(tuple(v))
    return tuple(tuple(columns[j][i] for j in range(n)) for i in range(n))


def lifted_residual(p: tuple[int, ...], a: tuple[int, ...],
                    b: tuple[int, ...], q: int) -> Matrix:
    n = len(p)
    return tuple(tuple(((p[i] if i == j else 0) - p[i] * a[i] * b[j] * p[j]) % q
                       for j in range(n)) for i in range(n))


def check_split(p: tuple[int, ...], r: tuple[int, ...], a: tuple[int, ...],
                b: tuple[int, ...], q: int, literal: bool) -> dict[str, int]:
    h = sum(b[i] * p[i] * r[i] * a[i] for i in range(len(a))) % q
    s, t = lifted_residual(p, a, b, q), lifted_residual(r, a, b, q)
    result = check_residual(s, t, h, q)
    if literal:
        m = split_header(a, b, q)
        mi = inverse(m, q)
        pp = multiply(multiply(mi, diagonal(p), q), m, q)
        rr = multiply(multiply(mi, diagonal(r), q), m, q)
        validate_pair(pp, rr, q)
        actual = check_residual(schur(pp, q), schur(rr, q), h, q)
        require(actual == result, "lift versus literal Schur invariant")
        ss = multiply(multiply(mi, s, q), m, q)
        require(ss[0] == (0,) * len(a) and all(row[0] == 0 for row in ss),
                "lift must vanish on deleted coordinate")
        require(tuple(row[1:] for row in ss[1:]) == schur(pp, q),
                "lift versus literal Schur matrix")
    return result


def enumerate_profile(q: int, sectors: tuple[int, ...]) -> dict:
    p = tuple(int(i in (1, 3)) for i, size in enumerate(sectors) for _ in range(size))
    r = tuple(int(i in (2, 3)) for i, size in enumerate(sectors) for _ in range(size))
    n = len(p)
    require(q in (2, 3, 5) and 2 <= n <= 5, "profile exceeds enumeration cap")
    vectors = tuple(itertools.product(range(q), repeat=n))
    total = admitted = literal = 0
    histogram: dict[tuple[int, ...], int] = {}
    for a in vectors:
        for b in vectors:
            if sum(x * y for x, y in zip(a, b, strict=True)) % q != 1:
                continue
            total += 1
            if any(sum(b[i] * v[i] * a[i] for i in range(n)) % q != 1 for v in (p, r)):
                continue
            admitted += 1
            direct = admitted <= 12
            literal += int(direct)
            result = check_split(p, r, a, b, q, direct)
            key = tuple(result.values())
            histogram[key] = histogram.get(key, 0) + 1
    require(total == (q ** n - 1) * q ** (n - 1), "complete split domain")
    require(admitted > 0, "empty positive domain")
    return {"q": q, "sectors": sectors, "split_pairs": total,
            "admitted": admitted, "literal_headers": literal,
            "histogram_columns": list(result),
            "histogram": [[list(k), v] for k, v in sorted(histogram.items())]}


def core_examples() -> list[dict]:
    results = []
    p = (0, 0, 1, 1, 0, 0, 1, 1)
    r = (0, 0, 0, 0, 1, 1, 1, 1)
    a = (1, 0) * 4
    for q in (2, 3, 5, 7, 11):
        for h in range(q):
            weights = ((h - 1) % q, (1 - h) % q, (1 - h) % q, h)
            b = tuple(x for w in weights for x in (w, 1))
            result = check_split(p, r, a, b, q, True)
            require(result["h"] == h, "prescribed product scalar")
            results.append({"q": q, **result})
    return results


def rejection_controls() -> int:
    # Hypothesis controls use actual matrices and the same entry validator.
    good = diagonal((1, 0))
    bad_cases = [
        (diagonal((0, 1)), good, 2),
        (((1, 1), (1, 0)), good, 2),
        (((1, 1), (0, 0)), good, 2),
        (good, good, 4),
        (((1, 0, 0), (0, 0, 0)), good, 2),
    ]
    for p, r, q in bad_cases:
        try:
            validate_pair(p, r, q)
        except ValueError:
            pass
        else:
            raise ValueError("hypothesis control accepted")
    # A genuine ternary identity-pivot example has theta=0 but Z^2 != Z.
    p, r = (0, 1, 0, 1), (0, 0, 1, 1)
    a, b = (1, 1, 1, 1), (1, 2, 2, 2)
    check_split(p, r, a, b, 3, True)
    s, t = lifted_residual(p, a, b, 3), lifted_residual(r, a, b, 3)
    z = multiply(subtract(s, t, 3), subtract(s, t, 3), 3)
    c = subtract(multiply(s, t, 3), multiply(t, s, 3), 3)
    require(any(map(any, z)) and not any(map(any, multiply(z, z, 3))),
            "repeated zero root is necessary")
    require(multiply(z, c, 3) != scale(c, 2, 3), "theta=h mutant survived")
    require(multiply(z, z, 3) != z, "central-idempotent mutant survived")
    # A commuting pair is essential; the proposed identity is not universal.
    s, t = ((1, 0), (0, 0)), ((2, 1), (1, 2))
    require(multiply(t, t, 3) == t, "negative residual must be idempotent")
    z = multiply(subtract(s, t, 3), subtract(s, t, 3), 3)
    c = subtract(multiply(s, t, 3), multiply(t, s, 3), 3)
    require(any(map(any, multiply(z, c, 3))), "arbitrary-pair theta=0 control")
    return len(bad_cases) + 3


def main() -> None:
    profiles = [enumerate_profile(2, (1, 1, 1, 2)),
                enumerate_profile(3, (1, 1, 1, 1)),
                enumerate_profile(5, (1, 1, 1, 1))]
    examples = core_examples()
    controls = rejection_controls()
    root = Path(__file__).resolve().parent
    names = ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        path = root / name
        require(path.stat().st_size <= 1024 * 1024, "package file exceeds 1 MiB")
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    print(json.dumps({"profiles": profiles, "all_h_examples": examples,
                      "rejection_controls": controls, "file_sha256": hashes},
                     sort_keys=True))
    print("PASS_SCHUR_CENTRAL_SPECTRUM")


if __name__ == "__main__":
    main()
