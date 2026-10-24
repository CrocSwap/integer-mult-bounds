"""Finite corroboration of the common-covector header law; no files written."""

import hashlib
import itertools
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def add(a, b, q):
    return a ^ b if q == 4 else (a + b) % q


def neg(a, q):
    return a if q == 4 else -a % q


def mul(a, b, q):
    if q != 4:
        return a * b % q
    result = 0
    for _ in range(2):
        if b & 1:
            result ^= a
        b >>= 1
        a <<= 1
        if a & 4:
            a ^= 7
    return result


def dot(a, b, q):
    result = 0
    for x, y in zip(a, b, strict=True):
        result = add(result, mul(x, y, q), q)
    return result


def matrix_product(a, b, q):
    return tuple(tuple(dot(row, col, q) for col in zip(*b, strict=True)) for row in a)


def inverse(a, q):
    m = len(a)
    rows = [list(row) + [int(i == j) for j in range(m)] for i, row in enumerate(a)]
    for j in range(m):
        pivot = next((i for i in range(j, m) if rows[i][j]), None)
        if pivot is None:
            return None
        rows[j], rows[pivot] = rows[pivot], rows[j]
        scale = next(x for x in range(1, q) if mul(rows[j][j], x, q) == 1)
        rows[j] = [mul(x, scale, q) for x in rows[j]]
        for i in range(m):
            if i != j:
                scale = neg(rows[i][j], q)
                rows[i] = [add(x, mul(scale, y, q), q)
                           for x, y in zip(rows[i], rows[j], strict=True)]
    return tuple(tuple(row[m:]) for row in rows)


def full_guard(a, q):
    m = len(a)
    for k in range(1, m):
        block = tuple(tuple(a[i][j] for j in range(k)) for i in range(k))
        if inverse(block, q) is None:
            return False
    return True


def joint(q, m):
    require(q in (2, 3, 4, 5, 7), "unsupported finite field")
    require(isinstance(m, int) and 2 <= m <= 256, "dimension out of finite-check bounds")
    n = m - 1
    alpha = q * q - q + 1
    delta = q * q + (q - 1) ** 3
    return Fraction((q - 1) * (delta**n - alpha**n),
                    (q**m - 1) * (q**m - q) * q ** (m - 2))


def marginal(q, m):
    return Fraction((q - 1) * (q * q - q + 1) ** (m - 1),
                    (q**m - 1) * q ** (m - 1))


def enumerate_headers(q, m):
    require((q, m) in ((2, 2), (3, 2), (4, 2), (5, 2), (7, 2),
                       (2, 3), (3, 3), (2, 4)), "header domain not registered")
    p = tuple(tuple(int(i == j and i != 0) for j in range(m)) for i in range(m))
    v = tuple(tuple(add(p[i][j], neg(int(i == 1 and j == 0), q), q)
                    for j in range(m)) for i in range(m))
    total = left = right = both = 0
    for entries in itertools.product(range(q), repeat=m * m):
        g = tuple(tuple(entries[i * m:(i + 1) * m]) for i in range(m))
        gi = inverse(g, q)
        if gi is None:
            continue
        first = full_guard(matrix_product(matrix_product(g, p, q), gi, q), q)
        second = full_guard(matrix_product(matrix_product(g, v, q), gi, q), q)
        total += 1
        left += first
        right += second
        both += first and second
    require(Fraction(both, total) == joint(q, m), f"header joint: {q},{m}")
    require(Fraction(left, total) == Fraction(right, total) == marginal(q, m),
            f"header marginals: {q},{m}")
    return {"q": q, "m": m, "headers": total, "joint_pass": both,
            "marginal_pass": left, "fraction": str(Fraction(both, total))}


def enumerate_triples(q, m):
    require((q, m) in ((2, 2), (2, 3), (2, 4), (2, 5),
                       (3, 2), (3, 3), (4, 2), (4, 3), (5, 2)),
            "triple domain not registered")
    vectors = tuple(itertools.product(range(q), repeat=m))
    total = good = 0
    for a, c in itertools.product(vectors, repeat=2):
        if not any(a) or any(c == tuple(mul(t, x, q) for x in a) for t in range(q)):
            continue
        for b in vectors:
            if dot(b, a, q) != 1 or dot(b, c, q) != 1:
                continue
            total += 1
            passing = True
            x = y = 0
            for i in range(m - 1):
                x = add(x, mul(b[i], a[i], q), q)
                y = add(y, mul(b[i], c[i], q), q)
                if x == 1 or y == 1:
                    passing = False
            good += passing
    denominator = (q**m - 1) * (q**m - q) * q ** (m - 2)
    require(total == denominator, f"triple orbit size: {q},{m}")
    require(Fraction(good, total) == joint(q, m), f"triple joint: {q},{m}")
    return {"q": q, "m": m, "triples": total, "joint_pass": good}


def transfer_counts(q, width):
    require(q in (2, 3, 4, 5, 7) and width in (1, 2), "transfer bounds")
    states = tuple(itertools.product(range(q), repeat=width))
    weights = Counter()
    for values in itertools.product(range(q), repeat=width + 1):
        weights[tuple(mul(x, values[-1], q) for x in values[:-1])] += 1
    safe = tuple(s for s in states if 1 not in s)
    current = {s: int(not any(s)) for s in safe}
    counts = []
    for _ in range(9):
        counts.append(sum(value * weights[tuple(add(1, neg(x, q), q) for x in s)]
                          for s, value in current.items()))
        current = {t: sum(value * weights[tuple(add(y, neg(x, q), q)
                                                 for x, y in zip(s, t, strict=True))]
                          for s, value in current.items()) for t in safe}
    base = q + (q - 1) ** 2 if width == 1 else q * q + (q - 1) ** 3
    require(counts == [(q - 1) * base**n for n in range(9)], "transfer power law")
    return counts


def controls():
    require(mul(2, 2, 4) == 3 and add(2, 2, 4) == 0, "F4 arithmetic")
    require(joint(2, 2) == Fraction(1, 3), "binary base fixture")
    require(joint(2, 3) == Fraction(4, 21), "binary next fixture")
    require(joint(3, 2) == Fraction(5, 12), "odd-field fixture")
    require(joint(4, 2) == Fraction(1, 2), "extension-field fixture")
    require(joint(2, 2) != marginal(2, 2) ** 2, "independence mutant")
    require(joint(2, 2) != 0, "orthogonal-pair substitution mutant")
    require(Fraction(5, 6) != joint(2, 2), "missing dependent-pair subtraction")
    require(Fraction(5**2 - 3**2, 7 * 6) != joint(2, 3), "missing row fiber")
    for q, m in ((1, 2), (6, 2), (2, 1), (2, 257), (2, 2.5)):
        try:
            joint(q, m)
        except ValueError:
            continue
        raise ValueError("invalid finite-check parameters accepted")
    return 14


def main():
    headers = [enumerate_headers(q, m) for q, m in
               ((2, 2), (3, 2), (4, 2), (5, 2), (7, 2), (2, 3), (3, 3), (2, 4))]
    triples = [enumerate_triples(q, m) for q, m in
               ((2, 2), (2, 3), (2, 4), (2, 5), (3, 2), (3, 3), (4, 2), (4, 3), (5, 2))]
    transfers = []
    for q in (2, 3, 4, 5, 7):
        diagonal, raw = transfer_counts(q, 1), transfer_counts(q, 2)
        for m in range(2, 10):
            denominator = (q**m - 1) * (q**m - q) * q ** (m - 2)
            require(Fraction(raw[m - 1] - diagonal[m - 1], denominator) == joint(q, m),
                    "independent transfer subtraction")
        transfers.append({"q": q, "raw": raw, "diagonal": diagonal})
    for m in range(2, 257):
        require(joint(2, m) > marginal(2, m) ** 2, "binary positive correlation")
        require(3 ** (m - 1) >= 2**m - 1, "binary proof comparison")
    package = Path(__file__).resolve().parent
    files = ("PROOF.md", "README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
    hashes = {name: hashlib.sha256((package / name).read_bytes()).hexdigest() for name in files}
    print(json.dumps({"status": "PASS_COMMON_COVECTOR_HEADER_LAW", "headers": headers,
                      "triples": triples, "transfers": transfers,
                      "binary_dimensions": [2, 256], "controls": controls(),
                      "sha256": hashes}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
