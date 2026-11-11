#!/usr/bin/env python3
"""Finite corroboration of the coupled resonant Jordan-pair theorem.

Produced by Nick Petalas. Apache-2.0. No predecessor code is imported.
"""

from hashlib import sha256
from itertools import product
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def field(p, degree, modulus):
    require((p, degree, modulus) in (
        (2, 1, (0,)), (3, 1, (0,)), (5, 1, (0,)),
        (7, 1, (0,)), (11, 1, (0,)), (13, 1, (0,)),
        (2, 2, (1, 1)), (2, 3, (1, 1, 0)), (3, 2, (1, 0))),
        "unsupported field")
    q = p**degree
    digits = [tuple(x // p**i % p for i in range(degree)) for x in range(q)]
    plus, times = [[0]*q for _ in range(q)], [[0]*q for _ in range(q)]
    for x, y in product(range(q), repeat=2):
        a, b = digits[x], digits[y]
        plus[x][y] = sum((a[i]+b[i]) % p * p**i for i in range(degree))
        c = [0]*(2*degree-1)
        for i, j in product(range(degree), repeat=2):
            c[i+j] = (c[i+j]+a[i]*b[j]) % p
        for i in range(2*degree-2, degree-1, -1):
            for j in range(degree):
                c[i-degree+j] = (c[i-degree+j]-c[i]*modulus[j]) % p
        times[x][y] = sum(c[i]*p**i for i in range(degree))
    negative = [next(y for y in range(q) if plus[x][y] == 0) for x in range(q)]
    inverse = [0]+[next(y for y in range(1, q) if times[x][y] == 1)
                   for x in range(1, q)]
    return (p, q, plus, times, negative, inverse)


def check_field(f):
    _, q, add, mul, neg, inv = f
    for x in range(q):
        require(add[x][0] == x and mul[x][1] == x, "field units")
        require(add[x][neg[x]] == 0, "additive inverse")
        require(x == 0 or mul[x][inv[x]] == 1, "multiplicative inverse")
    for x, y, z in product(range(q), repeat=3):
        require(add[x][y] == add[y][x] and mul[x][y] == mul[y][x], "commutativity")
        require(add[add[x][y]][z] == add[x][add[y][z]], "addition associativity")
        require(mul[mul[x][y]][z] == mul[x][mul[y][z]], "product associativity")
        require(mul[x][add[y][z]] == add[mul[x][y]][mul[x][z]], "distributivity")


def zero(n):
    require(n in (2, 4, 8), "matrix dimension")
    return [[0]*n for _ in range(n)]


def eye(n):
    a = zero(n)
    for i in range(n):
        a[i][i] = 1
    return a


def add_matrix(f, a, b, subtract=False):
    n = len(a)
    require(n in (2, 4, 8) and len(b) == n, "sum dimension")
    op, neg = f[2], f[4]
    return [[op[a[i][j]][neg[b[i][j]] if subtract else b[i][j]]
             for j in range(n)] for i in range(n)]


def mm(f, a, b):
    n = len(a)
    require(n in (2, 4, 8) and len(b) == n, "product dimension")
    out, add, mul = zero(n), f[2], f[3]
    for i, j, k in product(range(n), repeat=3):
        out[i][j] = add[out[i][j]][mul[a[i][k]][b[k][j]]]
    return out


def eliminate(f, matrix, invert=False):
    n = len(matrix)
    require(n in (2, 4, 8) and all(len(row) == n for row in matrix), "square matrix")
    require(all(type(x) is int and 0 <= x < f[1] for row in matrix for x in row),
            "field coordinates")
    a = [row[:] for row in matrix]
    if invert:
        for i in range(n):
            a[i] += [int(i == j) for j in range(n)]
    pivot, determinant = 0, 1
    add, mul, neg, inv = f[2:]
    for col in range(n):
        row = next((i for i in range(pivot, n) if a[i][col]), None)
        if row is None:
            determinant = 0
            continue
        if row != pivot:
            determinant = neg[determinant]
        a[pivot], a[row] = a[row], a[pivot]
        scale = a[pivot][col]
        determinant = mul[determinant][scale]
        a[pivot] = [mul[inv[scale]][x] for x in a[pivot]]
        for i in range(n):
            if i == pivot:
                continue
            scale = a[i][col]
            a[i] = [add[x][neg[mul[scale][y]]] for x, y in zip(a[i], a[pivot])]
        pivot += 1
    require(not invert or pivot == n, "singular inverse")
    return pivot, determinant, [row[n:] for row in a] if invert else None


def jordan_pair(f, signs):
    require(len(signs) == 2 and all(f[3][x][x] == 1 for x in signs), "resonant signs")
    p = zero(4)
    for j, lam in enumerate(signs):
        p[2*j][2*j] = p[2*j+1][2*j+1] = lam
        p[2*j][2*j+1] = 1
    return p


def perturbation(values):
    require(len(values) == 4, "four entries")
    r = zero(4)
    for (i, j), x in zip(((0, 1), (0, 3), (2, 1), (2, 3)), values):
        r[i][j] = x
    return r


def error_block(f, p, q):
    a = add_matrix(f, mm(f, p, p), eye(4), True)
    r = add_matrix(f, q, p, True)
    return [a[i]+r[i] for i in range(4)]+[r[i]+[0]*4 for i in range(4)]


def mv(f, a, v):
    n = len(a)
    require(n == len(v) == 4, "vector dimension")
    out = [0]*n
    for i, j in product(range(n), repeat=2):
        out[i] = f[2][out[i]][f[3][a[i][j]][v[j]]]
    return out


def wrapper_rank(f, p, pinv, q, qinv):
    """Execute all six wrapper operations on every original input basis column."""
    columns, add, neg = [], f[2], f[4]
    for column in range(8):
        h0 = [int(column == i) for i in range(4)]
        d0 = [int(column == i+4) for i in range(4)]
        h, d = h0[:], d0[:]
        d = [add[x][neg[y]] for x, y in zip(d, h)]
        h, d = mv(f, p, d), mv(f, pinv, h)
        d = [add[x][y] for x, y in zip(d, h)]
        h, d = mv(f, q, d), mv(f, qinv, h)
        d = [neg[x] for x in d]
        d = [add[x][y] for x, y in zip(d, h)]
        columns.append([add[x][neg[y]] for x, y in zip(h+d, d0+h0)])
    matrix = [[columns[j][i] for j in range(8)] for i in range(8)]
    return eliminate(f, matrix)[0]


def parameter(f, signs, values):
    two = f[2][1][1]
    scaled = [f[3][f[3][two][signs[i//2]]][x] for i, x in enumerate(values)]
    return perturbation(scaled)


def context(f, signs):
    pchar, qsize = f[:2]
    p = jordan_pair(f, signs)
    pinv = eliminate(f, p, True)[2]
    expected_rank = 0 if pchar == 2 else 2
    accepted, literal, rank_one = set(), 0, 0
    for values in product(range(qsize), repeat=4):
        q = add_matrix(f, p, perturbation(values))
        actual = eliminate(f, error_block(f, p, q))[0] == expected_rank
        if actual:
            accepted.add(values)
    expected = set()
    for values in product(range(qsize), repeat=4):
        s = [list(values[:2]), list(values[2:])]
        if mm(f, s, s) != zero(2):
            continue
        r = parameter(f, signs, values)
        expected.add(tuple(r[i][j] for i, j in ((0, 1), (0, 3), (2, 1), (2, 3))))
    require(accepted == expected, "complete coupling catalogue")
    require(len(accepted) == (1 if pchar == 2 else qsize*qsize), "all-field count")
    for values in sorted(accepted):
        q = add_matrix(f, p, perturbation(values))
        _, determinant, qinv = eliminate(f, q, True)
        require(determinant == 1, "determinant filter")
        require(wrapper_rank(f, p, pinv, q, qinv) == expected_rank, "literal wrapper")
        rank_one += eliminate(f, perturbation(values))[0] == 1
        literal += 1
    require(rank_one == len(accepted)-1, "perturbation rank distribution")
    return {"q": qsize, "signs": signs, "candidates": qsize**4,
            "optimal": len(accepted), "literal": literal, "rank_one": rank_one}


def binary_full_census():
    """Every binary second map, without the forced-support restriction."""
    f = field(2, 1, (0,))
    p = jordan_pair(f, (1, 1))
    optimal, invertible = 0, 0
    for bits in range(1 << 16):
        q = [[(bits >> (4*i+j)) & 1 for j in range(4)] for i in range(4)]
        if eliminate(f, q)[0] != 4:
            continue
        invertible += 1
        qinv = eliminate(f, q, True)[2]
        actual = wrapper_rank(f, p, p, q, qinv)
        require((actual == 0) == (q == p), "full-domain wrapper optimum")
        optimal += actual == 0
    require(invertible == 20160 and optimal == 1, "full binary census")
    return {"all_matrices": 65536, "invertible": invertible, "optimal": optimal}


def controls():
    f = field(3, 1, (0,))
    p = jordan_pair(f, (1, 1))
    pinv = eliminate(f, p, True)[2]
    q = add_matrix(f, p, parameter(f, (1, 1), (0, 1, 0, 0)))
    require(q != p, "coupling exists")
    require(wrapper_rank(f, p, pinv, q, eliminate(f, q, True)[2]) == 2, "coupling optimum")
    for values in ((1, 0, 0, 0), (0, 1, 1, 0)):
        bad = add_matrix(f, p, parameter(f, (1, 1), values))
        require(wrapper_rank(f, p, pinv, bad, eliminate(f, bad, True)[2]) > 2,
                "non-square-zero coupling rejection")
    off_support = 0
    for i, j in product(range(4), repeat=2):
        if i in (0, 2) and j in (1, 3):
            continue
        r = zero(4)
        r[i][j] = 1
        bad = add_matrix(f, p, r)
        require(eliminate(f, error_block(f, p, bad))[0] > 2, "support rejection")
        off_support += 1
    f2 = field(2, 1, (0,))
    p2 = jordan_pair(f2, (1, 1))
    bad2 = add_matrix(f2, p2, perturbation((0, 1, 0, 0)))
    require(wrapper_rank(f2, p2, p2, bad2, eliminate(f2, bad2, True)[2]) > 0,
            "odd formula cannot transfer to characteristic two")
    return {"non_square_zero": 2, "off_support": off_support,
            "coupling_positive": 1, "characteristic_two_rejection": 1}


def main():
    presentations = ((2, 1, (0,)), (3, 1, (0,)), (2, 2, (1, 1)),
                     (5, 1, (0,)), (7, 1, (0,)), (2, 3, (1, 1, 0)),
                     (3, 2, (1, 0)), (11, 1, (0,)), (13, 1, (0,)))
    cases = []
    for args in presentations:
        f = field(*args)
        check_field(f)
        signs = sorted(set((1, f[4][1])))
        for pair in product(signs, repeat=2):
            cases.append(context(f, pair))
    report = {"claim_type": "scoped proof with finite corroboration", "contexts": cases,
              "binary_census": binary_full_census(), "controls": controls()}
    package = Path(__file__).resolve().parent
    names = ("PROOF.md", "README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
    report["package_sha256"] = {name: sha256((package/name).read_bytes()).hexdigest() for name in names}
    print(json.dumps(report, sort_keys=True))
    print("PASS_COUPLED_RESONANT_JORDAN_PAIR no_new_kappa")


if __name__ == "__main__":
    main()
