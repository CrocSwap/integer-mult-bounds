#!/usr/bin/env python3
"""Exact joint eigenspace counts and the credited binary Schur-header sum."""

from collections import Counter
from hashlib import sha256
from itertools import product
import json
from math import prod
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate(n: int, q: int) -> None:
    require(type(n) is int and 0 <= n <= 32, "dimension outside 0..32")
    require(type(q) is int and 2 <= q <= 64, "field order outside 2..64")
    powers = {p**k for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
                             31, 37, 41, 43, 47, 53, 59, 61)
              for k in range(1, 7) if p**k <= 64}
    require(q in powers, "field order is not a prime power")


def gaussian(n: int, k: int, q: int) -> int:
    if not 0 <= k <= n:
        return 0
    numerator = prod(q**n - q**j for j in range(k))
    denominator = prod(q**k - q**j for j in range(k))
    require(numerator % denominator == 0, "nonintegral Gaussian coefficient")
    return numerator // denominator


def injections(n: int, k: int, q: int) -> int:
    return prod(q**n - q**j for j in range(k)) if 0 <= k <= n else 0


def joint_count(n: int, a: int, b: int, q: int) -> int:
    """Count H with nullity H=a and nullity(I-H)=b."""
    validate(n, q)
    require(type(a) is int and type(b) is int and 0 <= a <= n
            and 0 <= b <= n, "invalid nullities")
    t = n - a - b
    if t < 0:
        return 0
    total = 0
    for i in range(t + 1):
        for j in range(t - i + 1):
            exponent = (i * (i - 1) // 2 + j * (j - 1) // 2
                        + i * j + b * i + a * j + n * (t - i - j))
            total += ((-1)**(i + j) * q**exponent
                      * gaussian(t, i, q) * gaussian(t - i, j, q))
    count = gaussian(n, a, q) * gaussian(n - a, b, q) * q**(a * b) * total
    require(count >= 0, "negative joint count")
    return count


def distribution(n: int, q: int) -> dict[tuple[int, int], int]:
    validate(n, q)
    counts = {(a, b): joint_count(n, a, b, q)
              for a in range(n + 1) for b in range(n + 1)}
    require(sum(counts.values()) == q**(n * n), "wrong total matrix count")
    require(all(counts[a, b] == counts[b, a] for a, b in counts),
            "H -> I-H symmetry failed")
    return counts


def add(x: int, y: int, q: int) -> int:
    return x ^ y if q == 4 else (x + y) % q


def multiply(x: int, y: int, q: int) -> int:
    if q != 4:
        return x * y % q
    value = (x if y & 1 else 0) ^ (x << 1 if y & 2 else 0)
    return value ^ 7 if value & 4 else value


def rank(entries: tuple[int, ...], n: int, q: int) -> int:
    rows = [list(entries[n * i:n * (i + 1)]) for i in range(n)]
    r = 0
    for col in range(n):
        pivot = next((i for i in range(r, n) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[r], rows[pivot] = rows[pivot], rows[r]
        inverse = next(x for x in range(1, q)
                       if multiply(rows[r][col], x, q) == 1)
        rows[r] = [multiply(x, inverse, q) for x in rows[r]]
        for i in range(r + 1, n):
            coefficient = rows[i][col]
            for j in range(col, n):
                value = multiply(coefficient, rows[r][j], q)
                negative = value if q == 4 else -value
                rows[i][j] = add(rows[i][j], negative, q)
        r += 1
    return r


def enumerate_matrices(n: int, q: int) -> Counter:
    require(q in (2, 3, 4, 5) and 0 <= n <= 4
            and q**(n * n) <= 65536, "literal census exceeds capacity")
    counts = Counter()
    for entries in product(range(q), repeat=n * n):
        shifted = tuple(add(int(i == j), entries[n * i + j]
                            if q in (2, 4) else -entries[n * i + j], q)
                        for i in range(n) for j in range(n))
        counts[n - rank(entries, n, q), n - rank(shifted, n, q)] += 1
    require(sum(counts.values()) == q**(n * n), "incomplete literal census")
    return counts


def factor_count(r: int, d: int, rho: int, full: bool) -> int:
    """U/A from ssafwann #4678, equations (1)-(2), at q=2."""
    if full:
        if r < d:
            return 0
        return (injections(r, d, 2) * 2**(rho * (r - d))
                * injections(r - d, d - rho, 2))
    return sum(gaussian(d - rho, d - k, 2) * injections(r, k, 2)
               * 2**(d * (r - k)) for k in range(rho, min(d, r) + 1))


def header_split_counts(sectors: tuple[int, ...], d: int) -> tuple[int, int]:
    require(len(sectors) == 4 and all(type(r) is int and 0 <= r <= 64
                                    for r in sectors), "invalid sectors")
    require(type(d) is int and 1 <= d <= 32 and d <= sum(sectors),
            "invalid block dimension")
    sharp, admitted = 0, 0
    for (a, b), multiplicity in distribution(d, 2).items():
        h, w = d - a, d - b
        ranks = (w, w, w, h)
        sharp += multiplicity * prod(factor_count(r, d, rho, j != 0)
                                     for j, (r, rho) in enumerate(zip(sectors, ranks, strict=True)))
        admitted += multiplicity * prod(factor_count(r, d, rho, False)
                                        for r, rho in zip(sectors, ranks, strict=True))
    require(0 <= sharp <= admitted, "header counts are inconsistent")
    return sharp, admitted


def literal_header_sum(sectors: tuple[int, ...], d: int) -> tuple[int, int]:
    require(1 <= d <= 3, "literal compressed-product sum exceeds capacity")
    sharp, admitted = 0, 0
    for entries in product(range(2), repeat=d * d):
        shifted = tuple(entries[d * i + j] ^ int(i == j)
                        for i in range(d) for j in range(d))
        h, w = rank(entries, d, 2), rank(shifted, d, 2)
        ranks = (w, w, w, h)
        sharp += prod(factor_count(r, d, rho, j != 0)
                      for j, (r, rho) in enumerate(zip(sectors, ranks, strict=True)))
        admitted += prod(factor_count(r, d, rho, False)
                         for r, rho in zip(sectors, ranks, strict=True))
    return sharp, admitted


def check_censuses() -> tuple[int, int]:
    cases, contexts = 0, 0
    for q, maximum in ((2, 4), (3, 3), (4, 2), (5, 2)):
        for n in range(maximum + 1):
            literal = enumerate_matrices(n, q)
            exact = distribution(n, q)
            require(all(literal[key] == value for key, value in exact.items()),
                    f"joint law disagrees with matrices at {(q, n)}")
            cases += sum(literal.values())
            contexts += 1
    return cases, contexts


def check_headers() -> int:
    contexts = 0
    for d in (1, 2, 3):
        for sectors in ((d, d, d, d), (0, d, d, 2 * d),
                        (d, d + 1, d, d + 1), (1, 1, 1, 2), (0, 2, 2, 1)):
            require(header_split_counts(sectors, d) == literal_header_sum(sectors, d),
                    "grouped and literal weighted sums disagree")
            contexts += 1
    require(header_split_counts((1, 1, 1, 2), 1) == (3, 172), "first credited example")
    require(header_split_counts((0, 2, 2, 1), 1) == (9, 100), "second credited example")
    require(header_split_counts((2, 2, 2, 2), 2) == (2592, 1932288),
            "third credited example")
    return contexts


def check_controls() -> int:
    table = distribution(2, 2)
    require(table[1, 1] == 6 and table[0, 0] == 2, "binary base fixture")
    # Missing q^(ab) and missing super-space lift factors are separate errors.
    require(table[1, 1] != gaussian(2, 1, 2), "disjointness control ineffective")
    wrong_fixed = sum((-1)**j * 2**(2 * (1 - j))
                      * gaussian(1, j, 2) for j in range(2))
    require(table[1, 0] != gaussian(2, 1, 2) * wrong_fixed,
            "lift-factor control ineffective")
    left = sum(v for (a, _), v in table.items() if a == 0)
    require(table[0, 0] * 16 != left * left, "independence control ineffective")
    require(joint_count(2, 2, 1, 2) == 0, "disjoint eigenspace boundary failed")
    rejected = 0
    for n, a, b, q in ((-1, 0, 0, 2), (33, 0, 0, 2), (2, -1, 0, 2),
                        (2, 0, 3, 2), (2, 0, 0, 6), (2, 0, 0, 1)):
        try:
            joint_count(n, a, b, q)
        except ValueError:
            rejected += 1
    require(rejected == 6, "an invalid input was accepted")
    try:
        enumerate_matrices(4, 3)
    except ValueError:
        return 11
    raise ValueError("literal capacity guard did not reject")


def main() -> None:
    cases, contexts = check_censuses()
    headers = check_headers()
    controls = check_controls()
    larger = 0
    for q in (2, 3, 4, 5, 7, 8, 9):
        for n in range(9):
            _ = distribution(n, q)  # Check invariants; discard the bounded histogram.
            larger += 1
    sharp, admitted = header_split_counts((4, 4, 4, 4), 4)
    derangements = joint_count(4, 0, 0, 2)
    require(derangements == 5824, "binary dimension-four derangement count")
    require(sharp == 5824 * injections(4, 4, 2)**4, "balanced-sector identity")
    package = Path(__file__).resolve().parent
    files = ("README.md", "PROOF.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
    receipt = {"matrix_cases": cases, "matrix_contexts": contexts,
               "weighted_header_contexts": headers, "controls": controls,
               "larger_distribution_contexts": larger,
               "balanced_d4_sharp_split_pairs": sharp,
               "balanced_d4_identity_split_pairs": admitted,
               "source_sha256": {name: sha256((package / name).read_bytes()).hexdigest()
                                 for name in files}}
    print(json.dumps(receipt, sort_keys=True))
    print("PASS_SCHUR_RANK_PAIR_LAW no_new_kappa")


if __name__ == "__main__":
    main()
