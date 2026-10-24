#!/usr/bin/env python3
"""Exact mixed-sign phase checks. Standard library; no predecessor imports."""
from collections import Counter
from hashlib import sha256
from itertools import product
from math import comb
from pathlib import Path
import json


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def dot(x: int, y: int) -> int:
    return (x & y).bit_count() & 1


def apply(columns: tuple[int, ...], x: int) -> int:
    value = 0
    for j, column in enumerate(columns):
        if (x >> j) & 1:
            value ^= column
    return value


def transpose(columns: tuple[int, ...]) -> tuple[int, ...]:
    n = len(columns)
    return tuple(sum(((c >> i) & 1) << j for j, c in enumerate(columns))
                 for i in range(n))


def compose(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(apply(a, column) for column in b)


def identity(n: int) -> tuple[int, ...]:
    return tuple(1 << j for j in range(n))


def orthogonal(columns: tuple[int, ...]) -> bool:
    return all(dot(x, y) == int(i == j)
               for i, x in enumerate(columns) for j, y in enumerate(columns))


def q(b: int, x: int) -> int:
    return (x.bit_count() + 2 * dot(b, x)) % 4


def defect(columns: tuple[int, ...], b: int) -> int:
    differences = tuple((q(b, row) - q(b, 1 << j)) % 4
                        for j, row in enumerate(transpose(columns)))
    require(all(d % 2 == 0 for d in differences), "nonbinary phase defect")
    return sum((d // 2) << j for j, d in enumerate(differences))


def representative(n: int, e: int) -> tuple[int, ...]:
    return tuple((1 << j) ^ (e if (e >> j) & 1 else 0) for j in range(n))


def admissible(b: int, e: int) -> bool:
    return ((b ^ e).bit_count() - b.bit_count()) % 4 == 0


def group_order(n: int) -> int:
    value = 1
    for width in range(2, n + 1):
        value *= (1 << (width - 1)) - (width & 1)
    return value


def orbit_size(n: int, b: int) -> int:
    return sum(comb(n, k) for k in range(b.bit_count() % 4, n + 1, 4))


def enumerate_group(n: int) -> list[tuple[int, ...]]:
    require(1 <= n <= 5, "enumeration width must lie in 1..5")
    odd = tuple(x for x in range(1 << n) if x.bit_count() % 2)
    partial = [()]
    for _ in range(n):
        partial = [prefix + (x,) for prefix in partial for x in odd
                   if all(dot(x, y) == 0 for y in prefix)]
        require(len(partial) <= 32768, "orthogonal-prefix capacity exceeded")
    require(len(set(partial)) == len(partial), "duplicate matrix")
    return partial


def mul(z: tuple[int, int], w: tuple[int, int]) -> tuple[int, int]:
    return z[0] * w[0] - z[1] * w[1], z[0] * w[1] + z[1] * w[0]


def literal_kernel(columns: tuple[int, ...], b: int) -> tuple[tuple[int, int], ...]:
    """Convolve ((1+s*i)I+(1-s*i)X_u), with denominator 2^n."""
    values = [(1, 0)] + [(0, 0)] * ((1 << len(columns)) - 1)
    for j, direction in enumerate(columns):
        sign = -1 if (b >> j) & 1 else 1
        following = []
        for x in range(len(values)):
            a = mul(values[x], (1, sign))
            c = mul(values[x ^ direction], (1, -sign))
            following.append((a[0] + c[0], a[1] + c[1]))
        values = following
    return tuple(values)


def enumerate_checks() -> dict[str, int]:
    counts = Counter()
    for n in range(1, 6):
        matrices = enumerate_group(n)
        require(len(matrices) == group_order(n), "group cardinality")
        counts["orthogonal_matrices"] += len(matrices)
        for b in range(1 << n):
            histogram = Counter()
            original = literal_kernel(identity(n), b)
            for s in matrices:
                require(orthogonal(s), "enumerator returned nonorthogonal map")
                e = defect(s, b)
                require(admissible(b, e), "mixed-sign spectrum necessity")
                require(defect(compose(representative(n, e), s), b) == 0,
                        "canonical phase normalization")
                st = transpose(s)
                actual = literal_kernel(s, b)
                for x in range(1 << n):
                    require(q(b, apply(st, x)) == (q(b, x) + 2 * dot(e, x)) % 4,
                            "quadratic phase identity")
                    sign = -1 if dot(e, x) else 1
                    require(actual[x] == tuple(sign * v for v in original[x]),
                            "literal signed-gate coefficient")
                    counts["literal_coefficients"] += 1
                histogram[e] += 1
                counts["matrix_sign_pairs"] += 1
            expected = {e for e in range(1 << n) if admissible(b, e)}
            require(set(histogram) == expected, "complete mixed-sign image")
            require(len(expected) == orbit_size(n, b), "binomial orbit count")
            require(set(histogram.values()) == {len(matrices) // len(expected)},
                    "equal mixed-sign fiber counts")
    return dict(counts)


def independent_and_constructive_checks() -> dict[str, int]:
    counts = Counter()
    for n in range(1, 5):
        all_maps = product(range(1 << n), repeat=n)
        direct = {s for s in all_maps if compose(transpose(s), s) == identity(n)}
        require(direct == set(enumerate_group(n)), "independent full-matrix census")
        counts["all_binary_matrices"] += 1 << (n * n)
    for n in range(1, 10):
        for b in range(1 << n):
            found = 0
            for e in range(1 << n):
                expected = admissible(b, e)
                require(expected == (q(b, e) == 0), "isotropic-vector criterion")
                counts["sign_defect_candidates"] += 1
                if expected:
                    t = representative(n, e)
                    require(orthogonal(t), "representative orthogonality")
                    require(compose(t, t) == identity(n), "representative involution")
                    require(defect(t, b) == e, "representative mixed-sign defect")
                    found += 1
                    counts["constructive_representatives"] += 1
            require(found == orbit_size(n, b), "all-sign binomial count")
    return dict(counts)


def cocycle_and_controls() -> dict[str, int]:
    matrices = enumerate_group(4)
    pairs = 0
    for b in range(16):
        for a in matrices:
            for c in matrices:
                require(defect(compose(a, c), b) ==
                        defect(a, b) ^ apply(a, defect(c, b)), "twisted cocycle")
                pairs += 1
    t = representative(5, 3)
    require(orthogonal(t) and defect(t, 1) == 3, "first mixed-sign fixture")
    require(defect(t, 0) == 0, "same transvection equal-sign control")
    require(not admissible(1, 15), "equal-sign criterion cannot be reused")
    require(not orthogonal(representative(5, 1)), "odd vector is not orthogonal")
    require(defect(representative(4, 15), 1) == 0, "weight-four need not be defect")
    require(orbit_size(6, 1) == 12 and group_order(6) // 12 == 1920,
            "six-axis mixed-sign stabilizer")
    require(orbit_size(6, 0) == 16, "six-axis equal-sign distinction")
    require(any(defect(compose(a, c), 1) != defect(a, 1) ^ defect(c, 1)
                for a in matrices for c in matrices), "untwisted cocycle mutant")
    require(any(defect(s, 1) != defect(transpose(s), 1) for s in matrices),
            "transpose convention mutant")
    require(any(defect(s, 1) != defect(s, 0) for s in matrices),
            "omitted sign transport mutant")
    return {"cocycle_pairs": pairs, "semantic_controls": 10}


def main() -> None:
    result = {"status": "PASS_MIXED_SIGN_PHASE_SPECTRUM"}
    result.update(enumerate_checks())
    result.update(independent_and_constructive_checks())
    result.update(cocycle_and_controls())
    package = Path(__file__).resolve().parent
    files = sorted(p for p in package.iterdir() if p.is_file())
    require(len(files) <= 12, "package file capacity exceeded")
    result["files_sha256"] = {p.name: sha256(p.read_bytes()).hexdigest() for p in files}
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
