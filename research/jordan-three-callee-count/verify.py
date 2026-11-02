#!/usr/bin/env python3
"""Exact finite evidence for the regular J3 optimal-second-callee count.

Produced by Nick Petalas. Apache-2.0.
No predecessor executable is imported. The all-field proof is in PROOF.md.
"""

from dataclasses import dataclass
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class Field:
    q: int
    add: tuple
    mul: tuple
    neg: tuple
    inv: tuple


def digits(value, p, degree):
    out = []
    for _ in range(degree):
        out.append(value % p)
        value //= p
    require(value == 0, "field encoding too large")
    return out


def field(p, modulus):
    allowed = {(2, (1, 1)), (3, (1, 1)), (5, (1, 1)),
               (7, (1, 1)), (11, (1, 1)), (13, (1, 1)),
               (2, (1, 1, 1)), (2, (1, 1, 0, 1)), (3, (1, 0, 1))}
    require((p, modulus) in allowed, "unsupported field presentation")
    degree = len(modulus) - 1
    q = p ** degree
    coefficients = [digits(x, p, degree) for x in range(q)]
    add = [[0] * q for _ in range(q)]
    mul = [[0] * q for _ in range(q)]
    for x, y in product(range(q), repeat=2):
        a, b = coefficients[x], coefficients[y]
        add[x][y] = sum(((a[i] + b[i]) % p) * p**i for i in range(degree))
        c = [0] * (2 * degree - 1)
        for i, j in product(range(degree), repeat=2):
            c[i+j] = (c[i+j] + a[i] * b[j]) % p
        for i in range(2 * degree - 2, degree - 1, -1):
            for j in range(degree):
                c[i-degree+j] = (c[i-degree+j] - c[i] * modulus[j]) % p
        mul[x][y] = sum(c[i] * p**i for i in range(degree))
    neg = tuple(next(y for y in range(q) if add[x][y] == 0) for x in range(q))
    inv = (0,) + tuple(next(y for y in range(1, q) if mul[x][y] == 1)
                       for x in range(1, q))
    return Field(q, tuple(map(tuple, add)), tuple(map(tuple, mul)), neg, inv)


def check_field(f):
    for x in range(f.q):
        require(f.add[x][0] == x and f.mul[x][1] == x, "field identity")
        require(f.add[x][f.neg[x]] == 0, "field additive inverse")
        if x:
            require(f.mul[x][f.inv[x]] == 1, "field multiplicative inverse")
    for x, y, z in product(range(f.q), repeat=3):
        require(f.add[x][y] == f.add[y][x], "additive commutativity")
        require(f.mul[x][y] == f.mul[y][x], "multiplicative commutativity")
        require(f.add[f.add[x][y]][z] == f.add[x][f.add[y][z]], "associativity")
        require(f.mul[f.mul[x][y]][z] == f.mul[x][f.mul[y][z]], "associativity")
        require(f.mul[x][f.add[y][z]] == f.add[f.mul[x][y]][f.mul[x][z]],
                "distributivity")


def dot(f, a, b):
    require(len(a) == len(b) and len(a) <= 6, "dot dimensions")
    out = 0
    for x, y in zip(a, b):
        out = f.add[out][f.mul[x][y]]
    return out


def matmul(f, a, b, n=3):
    require(n in (3, 6) and len(a) == len(b) == n*n, "matrix dimensions")
    return tuple(dot(f, a[i*n:(i+1)*n], b[j::n])
                 for i, j in product(range(n), repeat=2))


def identity(n):
    require(n in (3, 6), "identity dimensions")
    return tuple(int(i == j) for i, j in product(range(n), repeat=2))


def eliminate(f, matrix, n, invert=False):
    require(n in (3, 6) and len(matrix) == n*n, "elimination dimensions")
    a = [list(matrix[i*n:(i+1)*n]) for i in range(n)]
    if invert:
        for i in range(n):
            a[i] += [int(i == j) for j in range(n)]
    pivot = 0
    for col in range(n):
        row = next((i for i in range(pivot, n) if a[i][col]), None)
        if row is None:
            continue
        a[pivot], a[row] = a[row], a[pivot]
        scale = f.inv[a[pivot][col]]
        a[pivot] = [f.mul[scale][x] for x in a[pivot]]
        for i in range(n):
            if i == pivot:
                continue
            scale = a[i][col]
            a[i] = [f.add[x][f.neg[f.mul[scale][y]]]
                    for x, y in zip(a[i], a[pivot])]
        pivot += 1
    if not invert:
        return pivot
    require(pivot == n, "singular inverse")
    return tuple(x for row in a for x in row[n:])


def determinant(f, a):
    require(len(a) == 9, "determinant dimensions")
    out = 0
    for i, j, k, sign in ((0, 4, 8, 1), (1, 5, 6, 1), (2, 3, 7, 1),
                           (2, 4, 6, -1), (1, 3, 8, -1), (0, 5, 7, -1)):
        term = f.mul[f.mul[a[i]][a[j]]][a[k]]
        out = f.add[out][term if sign == 1 else f.neg[term]]
    return out


def square_zero(f, a):
    require(len(a) == 9, "square-zero dimensions")
    for i, j in product(range(3), repeat=2):
        if dot(f, a[3*i:3*i+3], a[j::3]):
            return False
    return True


def catalogue(f):
    matrices = {(0,) * 9}
    vectors = tuple(product(range(f.q), repeat=3))
    for u in vectors:
        if next((x for x in u if x), 0) != 1:
            continue
        for v in vectors:
            if not any(v) or dot(f, u, v):
                continue
            s = tuple(f.mul[x][y] for x in u for y in v)
            require(s not in matrices, "duplicate projective representative")
            require(square_zero(f, s), "constructed non-square-zero parameter")
            matrices.add(s)
    require(len(matrices) == f.q**4 + f.q**3 - f.q, "parameter total")
    return tuple(sorted(matrices))


def regular(f, lam):
    require(type(lam) is int and 0 < lam < f.q, "invalid lambda")
    require(f.mul[lam][lam] != 1, "resonant lambda is outside this theorem")


def first_map(f, lam):
    regular(f, lam)
    return (lam, 1, 0, 0, lam, 1, 0, 0, lam)


def second_map(f, p, s):
    p2 = matmul(f, p, p)
    a = tuple(f.add[x][f.neg[y]] for x, y in zip(p2, identity(3)))
    r = matmul(f, a, s)
    return tuple(f.add[x][y] for x, y in zip(p, r))


def predicted(f, lam):
    regular(f, lam)
    q = f.q
    exceptional = f.mul[lam][lam] == f.neg[1]
    ordinary_fiber = q**3 if exceptional else q*q*(q+1)
    special_fiber = 2*q**3-q if exceptional else q**3+q*q-q
    special = f.mul[f.mul[lam][lam]][lam]
    return [special_fiber if d == special else ordinary_fiber for d in range(q)]


def compare_distribution(actual, expected):
    require(list(actual) == list(expected), "wrong determinant distribution")


def wrapper_error(f, p, q):
    pinv = eliminate(f, p, 3, invert=True)
    qinv = eliminate(f, q, 3, invert=True)
    columns = []
    for col in range(6):
        h = tuple(int(i == col) for i in range(3))
        d = tuple(int(i+3 == col) for i in range(3))
        original_h, original_d = h, d
        d = tuple(f.add[x][f.neg[y]] for x, y in zip(d, h))
        h, d = tuple(dot(f, p[i:i+3], d) for i in (0, 3, 6)), tuple(
            dot(f, pinv[i:i+3], h) for i in (0, 3, 6))
        d = tuple(f.add[x][y] for x, y in zip(d, h))
        h, d = tuple(dot(f, q[i:i+3], d) for i in (0, 3, 6)), tuple(
            dot(f, qinv[i:i+3], h) for i in (0, 3, 6))
        d = tuple(f.neg[x] for x in d)
        d = tuple(f.add[x][y] for x, y in zip(d, h))
        columns.append(tuple(f.add[x][f.neg[y]]
                             for x, y in zip(h+d, original_d+original_h)))
    return tuple(columns[j][i] for i, j in product(range(6), repeat=2))


def direct_matrix_domain(f, parameters):
    require(f.q in (4, 5), "exhaustive domain exceeds configured bound")
    found = set()
    inspected = 0
    for a in product(range(f.q), repeat=9):
        inspected += 1
        if square_zero(f, a):
            found.add(a)
    require(found == set(parameters), "full matrix domain disagrees with catalogue")
    return inspected


def expect_rejection(function, *args):
    try:
        function(*args)
    except ValueError:
        return 1
    raise ValueError("control was not rejected")


def controls(fields):
    f4, f5, f7 = fields[2], fields[3], fields[4]
    count = 0
    for bad in (0, 1, f5.neg[1], 5, -1, True):
        count += expect_rejection(regular, f5, bad)
    count += expect_rejection(field, 4, (1, 1))
    count += expect_rejection(determinant, f4, (0,))
    count += expect_rejection(eliminate, f5, (0,)*9, 3, True)
    require(not square_zero(f5, identity(3)), "non-square-zero control")
    require(f4.add[1][1] == 0 and f4.mul[2][3] == 1, "extension field control")
    p = first_map(f7, 2)
    bad_q = second_map(f7, p, identity(3))
    require(determinant(f7, bad_q) != 0, "nonoptimal control must be invertible")
    require(eliminate(f7, wrapper_error(f7, p, bad_q), 6) > 3,
            "nonsquare-zero control must be suboptimal in the literal wrapper")
    for f, lam in ((f5, 2), (f7, 2)):
        expected = predicted(f, lam)
        altered = list(expected)
        altered[0] += 1
        count += expect_rejection(compare_distribution, altered, expected)
        altered = list(expected)
        altered[f.mul[f.mul[lam][lam]][lam]] -= 1
        count += expect_rejection(compare_distribution, altered, expected)
    return count


def check_context(f, lam, parameters, literal):
    p = first_map(f, lam)
    expected = predicted(f, lam)
    observed = [0] * f.q
    wrapper_count = 0
    for s in parameters:
        q = second_map(f, p, s)
        d = determinant(f, q)
        observed[d] += 1
        if literal and d:
            require(eliminate(f, wrapper_error(f, p, q), 6) == 3,
                    "accepted second callee does not attain minimum error rank")
            wrapper_count += 1
    compare_distribution(observed, expected)
    accepted = sum(observed) - observed[0]
    exceptional = f.mul[lam][lam] == f.neg[1]
    expected_count = f.q**4-f.q if exceptional else f.q**4-f.q*f.q-f.q
    require(accepted == expected_count, "filtered count")
    return {"q": f.q, "lambda": lam, "exceptional": exceptional,
            "determinant_fibers": observed, "accepted": accepted,
            "literal_wrappers": wrapper_count}


def main():
    presentations = ((2, (1, 1)), (3, (1, 1)), (2, (1, 1, 1)),
                     (5, (1, 1)), (7, (1, 1)), (2, (1, 1, 0, 1)),
                     (3, (1, 0, 1)), (11, (1, 1)), (13, (1, 1)))
    fields = [field(p, m) for p, m in presentations]
    report = {"contexts": [], "complete_matrix_domains": [], "field_sizes": [],
              "parameters_enumerated": 0, "determinants_computed": 0}
    for f in fields:
        check_field(f)
        report["field_sizes"].append(f.q)
        parameters = catalogue(f)
        report["parameters_enumerated"] += len(parameters)
        if f.q in (4, 5):
            inspected = direct_matrix_domain(f, parameters)
            report["complete_matrix_domains"].append({"q": f.q, "matrices": inspected,
                                                      "square_zero": len(parameters)})
        for lam in range(1, f.q):
            if f.mul[lam][lam] == 1:
                continue
            report["contexts"].append(check_context(f, lam, parameters, f.q in (4, 5)))
            report["determinants_computed"] += len(parameters)
    report["rejection_controls"] = controls(fields)
    report["literal_wrappers"] = sum(x["literal_wrappers"] for x in report["contexts"])
    root = Path(__file__).resolve().parent
    paths = sorted(p for p in root.iterdir() if p.is_file())
    require(len(paths) <= 12, "unexpected package growth")
    report["package_sha256"] = {p.name: sha256(p.read_bytes()).hexdigest() for p in paths}
    report["status"] = "PASS_JORDAN_THREE_CALLEE_COUNT"
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
