#!/usr/bin/env python3
"""Finite corroboration of the split-pencil theorem. Apache-2.0.

Produced by Nick Petalas. This verifier imports no predecessor code.
"""

from collections import Counter
from hashlib import sha256
from itertools import permutations, product
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def field(q):
    require(q in (2, 3, 4, 5, 7), "unsupported field")
    add = tuple(tuple(a ^ b if q == 4 else (a + b) % q
                      for b in range(q)) for a in range(q))
    mul = []
    for a in range(q):
        row = []
        for b in range(q):
            c = (a * b) % q
            if q == 4:
                c = ((a & 1) * (b & 1)) ^ (((a & 1) * (b >> 1)) << 1)
                c ^= (((a >> 1) * (b & 1)) << 1) ^ ((a >> 1) * (b >> 1) * 3)
            row.append(c)
        mul.append(tuple(row))
    neg = tuple(next(b for b in range(q) if add[a][b] == 0) for a in range(q))
    return add, tuple(mul), neg


def total(values, f):
    result = 0
    for value in values:
        result = f[0][result][value]
    return result


def eye(n):
    return tuple(int(i == j) for i in range(n) for j in range(n))


def mm(a, b, n, f):
    return tuple(total((f[1][a[i*n+k]][b[k*n+j]] for k in range(n)), f)
                 for i in range(n) for j in range(n))


def mv(a, v, n, f):
    return tuple(total((f[1][a[i*n+j]][v[j]] for j in range(n)), f)
                 for i in range(n))


def inverse(a, n, q, f):
    rows = [list(a[i*n:(i+1)*n]) + list(eye(n)[i*n:(i+1)*n]) for i in range(n)]
    for col in range(n):
        pivot = next((r for r in range(col, n) if rows[r][col]), None)
        if pivot is None:
            return None
        rows[col], rows[pivot] = rows[pivot], rows[col]
        inv = next(x for x in range(1, q) if f[1][rows[col][col]][x] == 1)
        rows[col] = [f[1][inv][x] for x in rows[col]]
        for r in range(n):
            if r != col:
                scale = f[2][rows[r][col]]
                rows[r] = [f[0][x][f[1][scale][y]]
                           for x, y in zip(rows[r], rows[col], strict=True)]
    return tuple(x for row in rows for x in row[n:])


def poly_mul(a, b, f):
    result = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            result[i+j] = f[0][result[i+j]][f[1][x][y]]
    return tuple(result)


def characteristic(a, n, f):
    result = [0] * (n + 1)
    for perm in permutations(range(n)):
        sign = sum(perm[i] > perm[j] for i in range(n) for j in range(i+1, n)) % 2
        term = (f[2][1] if sign else 1,)
        for i, j in enumerate(perm):
            term = poly_mul(term, (f[2][a[i*n+j]], int(i == j)), f)
        for i, value in enumerate(term):
            result[i] = f[0][result[i]][value]
    require(result[-1] == 1, "characteristic polynomial is not monic")
    return tuple(result)


def evaluate(poly, value, f):
    result = 0
    for coefficient in reversed(poly):
        result = f[0][f[1][result][value]][coefficient]
    return result


def splits(poly, q, f):
    for root in range(q):
        for _ in range(len(poly) - 1):
            if len(poly) == 1 or evaluate(poly, root, f):
                break
            quotient = [0] * (len(poly) - 1)
            quotient[-1] = poly[-1]
            for i in range(len(quotient)-2, -1, -1):
                quotient[i] = f[0][poly[i+1]][f[1][root][quotient[i+1]]]
            require(f[0][poly[0]][f[1][root][quotient[0]]] == 0, "bad division")
            poly = tuple(quotient)
    return len(poly) == 1


def triangular_basis(a, n, q, f):
    """Build a full invariant flag, independently of characteristic()."""
    vectors = tuple(product(range(q), repeat=n))
    span = {tuple(0 for _ in range(n))}
    columns = []
    for _ in range(n):
        chosen = None
        for v in vectors:
            if v in span:
                continue
            av = mv(a, v, n, f)
            if any(tuple(f[0][av[i]][f[2][f[1][lam][v[i]]]] for i in range(n))
                   in span for lam in range(q)):
                chosen = v
                break
        if chosen is None:
            return None
        columns.append(chosen)
        span = {tuple(f[0][w[i]][f[1][c][chosen[i]]] for i in range(n))
                for w in span for c in range(q)}
        require(len(span) == q ** len(columns), "dependent flag column")
    return tuple(columns[j][i] for i in range(n) for j in range(n))


def ring_mm(a, b, n, f):
    scalar = mm(a[0], b[0], n, f)
    coefficients = []
    for k in (1, 2):
        left, right = mm(a[0], b[k], n, f), mm(a[k], b[0], n, f)
        coefficients.append(tuple(f[0][x][y] for x, y in zip(left, right, strict=True)))
    return (scalar, *coefficients)


def pencil(a, n):
    return (tuple(0 for _ in a), eye(n), a)


def attaining_word(a, basis, n, q, f):
    inv = inverse(basis, n, q, f)
    require(inv is not None, "singular flag basis")
    t = mm(mm(inv, a, n, f), basis, n, f)
    require(all(t[i*n+j] == 0 for i in range(n) for j in range(i)), "not triangular")
    zero = tuple(0 for _ in a)
    word = []
    for j in range(n):
        scalar, xpart, ypart = list(eye(n)), list(zero), list(zero)
        scalar[j*n+j] = 0
        xpart[j*n+j] = 1
        for i in range(n):
            ypart[i*n+j] = t[i*n+j]
        word.append((tuple(scalar), tuple(xpart), tuple(ypart)))
    result = (eye(n), zero, zero)
    for factor in word:
        result = ring_mm(factor, result, n, f)
    require(result == pencil(t, n), "column replacement word failed")
    result = ring_mm((basis, zero, zero), result, n, f)
    result = ring_mm(result, (inv, zero, zero), n, f)
    require(result == pencil(a, n), "free conjugation failed")
    return word, t


def census(q, n):
    f = field(q)
    counts = Counter()
    for a in product(range(q), repeat=n*n):
        poly = characteristic(a, n, f)
        split = splits(poly, q, f)
        basis = triangular_basis(a, n, q, f)
        require(split == (basis is not None), "polynomial and flag criteria disagree")
        if split:
            attaining_word(a, basis, n, q, f)
            counts["split"] += 1
        elif any(evaluate(poly, root, f) == 0 for root in range(q)):
            counts["rootful_nonsplit"] += 1
        else:
            counts["rootless"] += 1
    require(sum(counts.values()) == q ** (n*n), "incomplete census")
    return dict(counts)


def ring_action(a, v, n, f):
    return (mv(a[0], v[0], n, f),
            tuple(f[0][x][y] for x, y in zip(mv(a[0], v[1], n, f),
                  mv(a[1], v[0], n, f), strict=True)),
            tuple(f[0][x][y] for x, y in zip(mv(a[0], v[2], n, f),
                  mv(a[2], v[0], n, f), strict=True)))


def dirty_checks():
    f, n = field(2), 3
    a = (0, 1, 1, 0, 1, 1, 0, 0, 0)
    word, t = attaining_word(a, eye(n), n, 2, f)
    count = 0
    for entries in product(range(2), repeat=3*n):
        v = tuple(tuple(entries[k*n:(k+1)*n]) for k in range(3))
        result = v
        for factor in word:
            result = ring_action(factor, result, n, f)
        require(result == ring_action(pencil(t, n), v, n, f), "dirty action mismatch")
        count += 1
    return count


def controls():
    f = field(2)
    # Scalar block plus irreducible quadratic: a root is insufficient.
    a = (0, 0, 0, 0, 0, 1, 0, 1, 1)
    poly = characteristic(a, 3, f)
    require(evaluate(poly, 0, f) == 0 and not splits(poly, 2, f), "rootful control")
    require(triangular_basis(a, 3, 2, f) is None, "partial flag accepted")
    require(poly[0] == 0 and poly == (0, 1, 1, 1), "singular A control")
    # The attaining word has an essential chronological direction.
    upper = (0, 1, 1, 0, 1, 1, 0, 0, 0)
    word, t = attaining_word(upper, eye(3), 3, 2, f)
    zero = tuple(0 for _ in upper)
    reverse = (eye(3), zero, zero)
    for factor in reversed(word):
        reverse = ring_mm(factor, reverse, 3, f)
    require(reverse != pencil(t, 3), "reversed word escaped control")
    for omit in range(3):
        result = (eye(3), zero, zero)
        for j, factor in enumerate(word):
            if j != omit:
                result = ring_mm(factor, result, 3, f)
        require(result != pencil(t, 3), "dropped factor escaped control")
    odd = field(3)
    require(characteristic((0, 1, 2, 0), 2, odd) == (1, 0, 1), "odd sign control")
    extension = field(4)
    require(extension[1][2][2] == 3 and extension[1][2][3] == 1, "F4 field control")
    require(not splits((1, 1, 1), 2, f), "irreducible polynomial accepted")
    return 9


def determinant_lift_checks():
    """Evaluate full polynomial lifts, without truncating degree-two terms."""
    f, n = field(3), 3
    t = (1, 2, 1, 0, 2, 2, 0, 0, 0)
    word, _ = attaining_word(t, eye(n), n, 3, f)
    comparisons = 0
    for x, y in product(range(3), repeat=2):
        result = eye(n)
        for factor in word:
            evaluated = tuple(total((factor[0][i], f[1][x][factor[1][i]],
                                    f[1][y][factor[2][i]]), f) for i in range(n*n))
            result = mm(evaluated, result, n, f)
        expected = 1
        for j in range(n):
            expected = f[1][expected][f[0][x][f[1][y][t[j*n+j]]]]
        actual = characteristic(result, n, f)[0]
        require(f[2][actual] == expected, "lifted determinant product mismatch")
        comparisons += 1
    return comparisons


def main():
    domains = ((2, 2), (2, 3), (3, 2), (3, 3), (4, 2), (5, 2), (7, 2))
    results = {f"q{q}_n{n}": census(q, n) for q, n in domains}
    require(results["q2_n3"] == {"split": 352, "rootful_nonsplit": 112,
                                "rootless": 48}, "binary census changed")
    dirty, control_count, lifts = dirty_checks(), controls(), determinant_lift_checks()
    package = Path(__file__).resolve().parent
    files = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {}
    for name in files:
        with (package / name).open("rb") as stream:
            raw = stream.read(128 * 1024 + 1)
        require(len(raw) <= 128 * 1024, "package file too large")
        hashes[name] = sha256(raw).hexdigest()
    print(json.dumps({"censuses": results, "dirty_inputs": dirty,
                      "controls": control_count, "determinant_lifts": lifts,
                      "sha256": hashes}, sort_keys=True))
    print("PASS_SPLIT_RADICAL_PENCIL binary_three_role=352/512 "
          "rootful_excluded=112 no_new_kappa")


if __name__ == "__main__":
    main()
