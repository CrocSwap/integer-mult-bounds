#!/usr/bin/env python3
"""Exact, bounded corroboration of the cube-zero cost-three target."""

from hashlib import sha256
from itertools import product
import json
from pathlib import Path


FIELDS = (2, 3, 4, 5, 7)
MONOMIALS = ((0, 0), (1, 0), (0, 1), (2, 0), (1, 1), (0, 2))
ZERO = (0,) * 6


def require(condition, message):
    if not condition:
        raise ValueError(message)


def field_add(a, b, q):
    return a ^ b if q == 4 else (a + b) % q


def field_mul(a, b, q):
    if q != 4:
        return (a * b) % q
    result = 0
    for bit in range(2):
        if b & (1 << bit):
            result ^= a << bit
    if result & 4:
        result ^= 7
    return result


def field_neg(a, q):
    return a if q == 4 else (-a) % q


def scale(a, scalar, q):
    return tuple(field_mul(c, scalar, q) for c in a)


def add(a, b, q):
    return tuple(field_add(c, d, q) for c, d in zip(a, b, strict=True))


def multiply(a, b, q):
    result = [0] * 6
    for i, (ix, iy) in enumerate(MONOMIALS):
        for j, (jx, jy) in enumerate(MONOMIALS):
            if ix + iy + jx + jy < 3:
                k = MONOMIALS.index((ix + jx, iy + jy))
                result[k] = field_add(result[k], field_mul(a[i], b[j], q), q)
    return tuple(result)


def basis(index):
    return tuple(int(i == index) for i in range(6))


def matrix_multiply(a, b, q):
    return tuple(add(multiply(a[2*i], b[j], q),
                     multiply(a[2*i+1], b[2+j], q), q)
                 for i in range(2) for j in range(2))


def matrix_vector(a, v, q):
    return tuple(add(multiply(a[2*i], v[0], q),
                     multiply(a[2*i+1], v[1], q), q) for i in range(2))


def paid(left, right, q):
    require(q in FIELDS, "unsupported field")
    require(len(left) == len(right) == 2, "two roles required")
    require(all(type(c) is int and 0 <= c < q for c in right),
            "right vector must lie in the base field")
    return tuple(add(scale(left[i], right[j], q),
                     basis(0) if i == j else ZERO, q)
                 for i in range(2) for j in range(2))


def word(q):
    one, x, y = (basis(i) for i in range(3))
    minus_one = scale(one, field_neg(1, q), q)
    x_minus_one = add(x, minus_one, q)
    return (paid((x_minus_one, y), (1, 0), q),
            paid((y, minus_one), (0, 1), q),
            paid((x_minus_one, ZERO), (1, 0), q))


def rank(rows, q):
    work = [list(row) for row in rows]
    height = 0
    for col in range(6):
        pivot = next((i for i in range(height, len(work)) if work[i][col]), None)
        if pivot is None:
            continue
        work[height], work[pivot] = work[pivot], work[height]
        inverse = next(c for c in range(1, q)
                       if field_mul(work[height][col], c, q) == 1)
        work[height] = [field_mul(c, inverse, q) for c in work[height]]
        for i in range(height + 1, len(work)):
            scalar = field_neg(work[i][col], q)
            work[i] = [field_add(c, field_mul(scalar, d, q), q)
                       for c, d in zip(work[i], work[height], strict=True)]
        height += 1
    return height


def in_right_ideal(a, b, q):
    generators = tuple(multiply(a, basis(i), q) for i in range(6))
    return rank(generators, q) == rank(generators + (b,), q)


def bilinear(matrix, row, col, q):
    result = ZERO
    for i in range(2):
        for j in range(2):
            result = add(result, scale(matrix[2*i+j],
                                      field_mul(row[i], col[j], q), q), q)
    return result


def chart_check(matrix, q):
    # Projective representatives remove only nonzero scalar rescalings.
    lines = ((0, 1),) + tuple((1, c) for c in range(q))
    accepted = 0
    checked = 0
    for row in lines:
        for first in lines:
            for second in lines:
                determinant = field_add(field_mul(first[0], second[1], q),
                                        field_neg(field_mul(first[1], second[0], q), q), q)
                if determinant:
                    a = bilinear(matrix, row, first, q)
                    b = bilinear(matrix, row, second, q)
                    accepted += in_right_ideal(a, b, q)
                    checked += 1
    require(checked == q * (q + 1)**2, "incomplete chart domain")
    return accepted, checked


def check_field(q):
    factors = word(q)
    target = (basis(3), basis(4), basis(4), basis(5))
    actual = matrix_multiply(matrix_multiply(factors[0], factors[1], q), factors[2], q)
    require(actual == target, "three-factor endpoint")
    vectors = tuple(v for v in product(range(q), repeat=2) if v != (0, 0))
    for row in vectors:
        for col in vectors:
            require(bilinear(target, row, col, q) != ZERO, "common bilinear zero")
    accepted, charts = chart_check(target, q)
    require(accepted == 0, "two-factor chart accepted")
    require(chart_check((basis(3), ZERO, ZERO, ZERO), q)[0] > 0,
            "right-ideal test rejects the positive control")
    for i in range(12):
        initial = (basis(i % 6), ZERO) if i < 6 else (ZERO, basis(i % 6))
        final = initial
        for factor in reversed(factors):
            final = matrix_vector(factor, final, q)
        require(final == matrix_vector(target, initial, q), "basis-column action")
    return len(vectors)**2, charts


def exhaustive_binary_action():
    elements = tuple(product(range(2), repeat=6))
    target = (basis(3), basis(4), basis(4), basis(5))
    factors = word(2)
    for initial in product(elements, repeat=2):
        final = initial
        for factor in reversed(factors):
            final = matrix_vector(factor, final, 2)
        require(final == matrix_vector(target, initial, 2), "arbitrary binary data")
    return len(elements)**2


def controls():
    factors = word(3)
    target = (basis(3), basis(4), basis(4), basis(5))
    identity = (basis(0), ZERO, ZERO, basis(0))
    for omit in range(3):
        result = identity
        for i, factor in enumerate(factors):
            if i != omit:
                result = matrix_multiply(result, factor, 3)
        require(result != target, "dropped factor not rejected")
    result = identity
    for factor in reversed(factors):
        result = matrix_multiply(result, factor, 3)
    require(result != target, "reversed word not rejected")
    bad_middle = paid((basis(2), basis(0)), (0, 1), 3)
    wrong_sign = matrix_multiply(matrix_multiply(factors[0], bad_middle, 3), factors[2], 3)
    require(wrong_sign != target, "wrong-sign control")
    for right, q in (((basis(1), basis(2)), 2), ((1, 0), 6)):
        try:
            paid((basis(1), basis(2)), right, q)
        except ValueError:
            continue
        raise ValueError("invalid alphabet or field accepted")
    # The quotient by J^2 kills the target and the bilinear obstruction.
    require(all(entry[:3] == (0, 0, 0) for entry in target), "quotient control")
    return 8


def receipt():
    package = Path(__file__).resolve().parent
    root = package.parent.parent
    sources = json.loads((package / "SOURCES.json").read_text())
    hashes = {}
    for entry in sources["files"]:
        if entry["usage"] == "input":
            digest = sha256((root / entry["path"]).read_bytes()).hexdigest()
            require(digest == entry["sha256"], "source drift: " + entry["path"])
            hashes[entry["path"]] = digest
    for name in ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py"):
        hashes[str(package.relative_to(root) / name)] = sha256((package / name).read_bytes()).hexdigest()
    return {"schema": "cube-zero-three-factor/v1", "sha256": hashes}


def main():
    pairs = charts = 0
    for q in FIELDS:
        pair_count, chart_count = check_field(q)
        pairs += pair_count
        charts += chart_count
    data = exhaustive_binary_action()
    rejected = controls()
    print(json.dumps(receipt(), sort_keys=True))
    print(f"PASS_CUBE_ZERO_THREE_FACTOR fields={','.join(map(str, FIELDS))} "
          f"bilinear_pairs={pairs} ideal_charts={charts} basis_columns=60 "
          f"binary_inputs={data} controls={rejected} exact_cost=3 no_new_kappa")


if __name__ == "__main__":
    main()
