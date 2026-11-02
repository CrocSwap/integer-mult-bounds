"""Exact finite corroboration of the four-stage pure-shear tariff theorem."""

import hashlib
import itertools
import json
from pathlib import Path
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(n):
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def zero(n):
    return tuple((0,) * n for _ in range(n))


def add(a, b, p):
    return tuple(tuple((x + y) % p for x, y in zip(r, s, strict=True))
                 for r, s in zip(a, b, strict=True))


def neg(a, p):
    return tuple(tuple(-x % p for x in row) for row in a)


def mul(a, b, p):
    columns = tuple(zip(*b, strict=True))
    return tuple(tuple(sum(x * y for x, y in zip(row, col, strict=True)) % p
                       for col in columns) for row in a)


def rank(a, p):
    rows = [[x % p for x in row] for row in a]
    pivots = 0
    for col in range(len(rows[0])):
        candidates = [i for i in range(pivots, len(rows)) if rows[i][col]]
        if not candidates:
            continue
        pivot = candidates[0]
        rows[pivots], rows[pivot] = rows[pivot], rows[pivots]
        inverse = pow(rows[pivots][col], -1, p)
        rows[pivots] = [x * inverse % p for x in rows[pivots]]
        for i in range(pivots + 1, len(rows)):
            coefficient = rows[i][col]
            rows[i] = [(x - coefficient * y) % p
                       for x, y in zip(rows[i], rows[pivots], strict=True)]
        pivots += 1
    return pivots


def shear(a, upper):
    n = len(a)
    eye = identity(n)
    nil = zero(n)
    top = tuple(eye[i] + (a[i] if upper else nil[i]) for i in range(n))
    bottom = tuple((nil[i] if upper else a[i]) + eye[i] for i in range(n))
    return top + bottom


def block_diagonal(a, b):
    n = len(a)
    return tuple(row + (0,) * n for row in a) + tuple((0,) * n + row for row in b)


def antidiagonal(a):
    n = len(a) // 2
    return all(a[i][j] == 0 and a[n + i][n + j] == 0
               for i in range(n) for j in range(n))


def matrices(n, p):
    require(1 <= n <= 2 and p in (2, 3, 5, 7), "enumeration domain")
    for entries in itertools.product(range(p), repeat=n * n):
        yield tuple(tuple(entries[i * n:(i + 1) * n]) for i in range(n))


def tariff_oracle(profiles, n):
    tariffs = tuple((0,) + tail for tail in
                    itertools.combinations_with_replacement(range(5), n))
    count = 0
    for upper, lower in itertools.product(tariffs, repeat=2):
        actual = min(upper[a] + lower[b] + upper[c] + lower[d]
                     for a, b, c, d in profiles)
        predicted = upper[n] + lower[n] + min(upper[r] + lower[n - r]
                                              for r in range(n + 1))
        require(actual == predicted, "arbitrary monotone directional tariff")
        count += 1
    return count


def exhaustive(n, p):
    """Literal full-matrix products, independent of the block classification."""
    alphabet = tuple(matrices(n, p))
    ranks = tuple(rank(a, p) for a in alphabet)
    up = tuple(shear(a, True) for a in alphabet)
    down = tuple(shear(a, False) for a in alphabet)
    pairs = tuple(mul(l, u, p) for u in up for l in down)
    words = endpoints = equality = 0
    best_linear = 4 * n + 1
    best_square = 4 * n * n + 1
    square_profile = None
    profiles = set()
    for ai, a in enumerate(alphabet):
        for bi, b in enumerate(alphabet):
            first = pairs[ai * len(alphabet) + bi]
            cb_target = neg(identity(n), p)
            required_d = add(b, mul(mul(b, a, p), b, p), p)
            for ci, c in enumerate(alphabet):
                cb = mul(c, b, p)
                for di, d in enumerate(alphabet):
                    second = pairs[ci * len(alphabet) + di]
                    actual = antidiagonal(mul(second, first, p))
                    predicted = cb == cb_target and d == required_d
                    require(actual == predicted, "block endpoint classification")
                    words += 1
                    if not actual:
                        continue
                    endpoints += 1
                    profile = (ranks[ai], ranks[bi], ranks[ci], ranks[di])
                    profiles.add(profile)
                    total = sum(profile)
                    require(total >= 3 * n, "rank floor")
                    projector = neg(mul(a, b, p), p)
                    idempotent = mul(projector, projector, p) == projector
                    require((total == 3 * n) == idempotent, "equality classification")
                    equality += int(total == 3 * n)
                    best_linear = min(best_linear, total)
                    squared = sum(x * x for x in profile)
                    if squared < best_square:
                        best_square, square_profile = squared, profile
    require(best_linear == 3 * n, "attained minimum")
    return {"dimension": n, "prime": p, "words": words, "endpoints": endpoints,
            "rank_optima": equality, "minimum_rank": best_linear,
            "minimum_square_tariff": best_square, "square_profile": square_profile,
            "monotone_tariff_pairs": tariff_oracle(profiles, n)}


def attaining_words():
    count = bridged = 0
    named = None
    for n in range(1, 9):
        for p in (2, 3, 5, 7):
            eye = identity(n)
            rotation = tuple(tuple(int(j == (i + 1) % n) for j in range(n))
                             for i in range(n))
            inverse = tuple(zip(*rotation, strict=True))
            transport = block_diagonal(rotation, eye)
            return_map = block_diagonal(inverse, eye)
            for r in range(n + 1):
                projector = tuple(tuple(int(i == j and i < r) for j in range(n))
                                  for i in range(n))
                a, b = neg(projector, p), eye
                c, d = neg(eye, p), add(eye, neg(projector, p), p)
                word = (shear(a, True), shear(b, False), shear(c, True), shear(d, False))
                endpoint = identity(2 * n)
                for gate in word:
                    endpoint = mul(gate, endpoint, p)
                expected = tuple((0,) * n + neg(eye, p)[i] for i in range(n))
                expected += tuple(eye[i] + (0,) * n for i in range(n))
                require(endpoint == expected, "all arbitrary-data columns")
                profile = tuple(rank(x, p) for x in (a, b, c, d))
                require(profile == (r, n, n, n - r), "attaining rank profile")
                transformed = tuple(mul(mul(transport, g, p), return_map, p) for g in word)
                with_bridges = identity(2 * n)
                for gate in transformed:
                    with_bridges = mul(gate, with_bridges, p)
                require(with_bridges == mul(mul(transport, expected, p), return_map, p),
                        "invertible within-bank transport")
                count += 1
                bridged += 1
                if (n, p, r) == (4, 3, 1):
                    named = {"dimension": n, "prime": p, "profile": profile,
                             "total_rank": sum(profile), "endpoint": endpoint}
    require(named is not None, "named first fixture")
    return {"attaining_words": count, "bridged_words": bridged, "first_fixture": named}


def tariff_checks():
    count = 0
    for n in range(1, 33):
        for upper_price, lower_price in itertools.product(range(1, 6), repeat=2):
            values = tuple(upper_price * r + lower_price * (n - r) for r in range(n + 1))
            require(min(values) == min(upper_price, lower_price) * n, "linear tariff")
            square_values = tuple(r * r + (n - r) ** 2 for r in range(n + 1))
            require(min(square_values) == (n * n + 1) // 2, "convex tariff control")
            count += 1
    return {"integer_tariffs": count}


def controls():
    eye = identity(2)
    nil = zero(2)
    swap = mul(shear(neg(eye, 3), True),
               mul(shear(eye, False), shear(neg(eye, 3), True), 3), 3)
    altered = mul(shear(neg(eye, 3), True), shear(eye, False), 3)
    jordan = ((1, 1), (0, 1))
    checks = {
        "three-stage positive": antidiagonal(swap),
        "omitted middle shear": not antidiagonal(altered),
        "zero matrix is singular": antidiagonal(zero(2)) and rank(zero(2), 3) == 0,
        "nonprojector equality": rank(jordan, 2) == 2 and mul(jordan, jordan, 2) != jordan,
        "identity is not a swap": not antidiagonal(shear(nil, True)),
        "field-sensitive rank": rank(((1, 1), (1, -1)), 3) != rank(((1, 1), (1, 1)), 2),
        "complementary supports": rank(((1, 0), (0, 0)), 2) + rank(((0, 0), (0, 1)), 2) == 2,
    }
    for name, passes in checks.items():
        require(passes, name)
    return {"checks": tuple(checks), "count": len(checks)}


def main():
    require(len(sys.argv) == 1, "no command-line arguments supported")
    package = Path(__file__).resolve().parent
    report = {"status": "PASS_FOUR_STAGE_PURE_SHEAR_TARIFF"}
    report["exhaustive"] = [exhaustive(1, p) for p in (2, 3, 5, 7)]
    report["exhaustive"].append(exhaustive(2, 2))
    report["constructions"] = attaining_words()
    report["tariffs"] = tariff_checks()
    report["controls"] = controls()
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    report["sha256"] = {}
    for name in names:
        source = package / name
        require(source.stat().st_size <= 1_000_000, "package file size limit")
        report["sha256"][name] = hashlib.sha256(source.read_bytes()).hexdigest()
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
