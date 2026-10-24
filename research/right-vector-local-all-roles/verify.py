#!/usr/bin/env python3
"""Bounded exact corroboration of the arbitrary-role local cost theorem."""

import hashlib
import itertools
import json
from pathlib import Path
import random


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def gf4(a, b):
    result = 0
    for _ in range(2):
        if b & 1:
            result ^= a
        b >>= 1
        a <<= 1
        if a & 4:
            a ^= 7
    return result


class Ring:
    def __init__(self, kind):
        settings = {"dual": (2, 2), "cube": (3, 3),
                    "squarezero": (2, 3), "field4": (2, 2), "skew": (2, 4)}
        if kind not in settings:
            raise ValueError("unknown ring")
        self.kind = kind
        self.p, self.dim = settings[kind]
        self.size = self.p ** self.dim
        self.coeff = tuple(tuple((a // self.p**i) % self.p
                                 for i in range(self.dim))
                           for a in range(self.size))
        self.add = tuple(tuple(self.encode(tuple((x + y) % self.p
                                for x, y in zip(self.coeff[a], self.coeff[b])))
                               for b in range(self.size))
                         for a in range(self.size))
        self.neg = tuple(self.encode(tuple(-v % self.p for v in c))
                         for c in self.coeff)
        self.mul = tuple(tuple(self.product(a, b) for b in range(self.size))
                         for a in range(self.size))
        self.inv = tuple(next((b for b in range(self.size)
                               if self.mul[a][b] == self.mul[b][a] == 1), None)
                         for a in range(self.size))

    def encode(self, coefficients):
        return sum(v * self.p**i for i, v in enumerate(coefficients))

    def product(self, a, b):
        if self.kind == "field4":
            return gf4(a, b)
        if self.kind == "skew":
            c, d = a & 3, a >> 2
            e, f = b & 3, b >> 2
            return gf4(c, e) + 4 * (gf4(c, f) ^ gf4(d, gf4(e, e)))
        x, y = self.coeff[a], self.coeff[b]
        if self.kind == "squarezero":
            values = (x[0] * y[0],) + tuple(x[0] * y[i] + x[i] * y[0]
                                           for i in range(1, self.dim))
        else:
            values = tuple(sum(x[j] * y[i-j] for j in range(i+1))
                           for i in range(self.dim))
        return self.encode(tuple(v % self.p for v in values))


def check_ring(r):
    q = r.size
    nonunits = tuple(a for a in range(q) if r.inv[a] is None)
    require(0 in nonunits and 1 not in nonunits, "proper nonunit set")
    for a, b in itertools.product(range(q), repeat=2):
        require(r.mul[a][1] == r.mul[1][a] == a, "unit")
        require(r.add[a][r.neg[a]] == 0, "additive inverse")
        if a in nonunits:
            require(r.mul[a][b] in nonunits and r.mul[b][a] in nonunits,
                    "two-sided nonunit ideal")
            if b in nonunits:
                require(r.add[a][b] in nonunits, "nonunit addition")
        for c in range(q):
            require(r.mul[r.mul[a][b]][c] == r.mul[a][r.mul[b][c]], "associativity")
            require(r.mul[a][r.add[b][c]] == r.add[r.mul[a][b]][r.mul[a][c]],
                    "left distributivity")
            require(r.mul[r.add[a][b]][c] == r.add[r.mul[a][c]][r.mul[b][c]],
                    "right distributivity")
        for c in range(r.p):
            require(r.mul[a][c] == r.mul[c][a], "central base field")
    if r.kind == "skew":
        require(r.mul[2][4] != r.mul[4][2], "noncommutative fixture")


def identity(n):
    if not 1 <= n <= 5:
        raise ValueError("role bound is 1..5")
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def mm(r, a, b):
    n = len(a)
    out = [[0] * n for _ in range(n)]
    for i, j, k in itertools.product(range(n), repeat=3):
        out[i][j] = r.add[out[i][j]][r.mul[a[i][k]][b[k][j]]]
    return tuple(tuple(row) for row in out)


def act(r, a, v):
    result = []
    for row in a:
        total = 0
        for coefficient, value in zip(row, v):
            total = r.add[total][r.mul[coefficient][value]]
        result.append(total)
    return tuple(result)


def inverse(r, a):
    n = len(a)
    work = [list(row) + list(unit) for row, unit in zip(a, identity(n))]
    for k in range(n):
        pivot = next((i for i in range(k, n) if r.inv[work[i][k]] is not None), None)
        if pivot is None:
            return None
        work[k], work[pivot] = work[pivot], work[k]
        unit = r.inv[work[k][k]]
        work[k] = [r.mul[unit][v] for v in work[k]]
        for i in range(n):
            if i != k:
                c = work[i][k]
                work[i] = [r.add[v][r.neg[r.mul[c][w]]]
                           for v, w in zip(work[i], work[k])]
    result = tuple(tuple(row[n:]) for row in work)
    require(mm(r, a, result) == mm(r, result, a) == identity(n), "inverse order")
    return result


def rref(rows, p, n):
    work = [list(row) for row in rows]
    pivots = []
    for j in range(n):
        k = len(pivots)
        pivot = next((i for i in range(k, len(work)) if work[i][j]), None)
        if pivot is None:
            continue
        work[k], work[pivot] = work[pivot], work[k]
        scale = pow(work[k][j], -1, p)
        work[k] = [scale * v % p for v in work[k]]
        for i in range(len(work)):
            if i != k:
                c = work[i][j]
                work[i] = [(v - c*w) % p for v, w in zip(work[i], work[k])]
        pivots.append(j)
    return work, tuple(pivots)


def nullspace(rows, p, n):
    reduced, pivots = rref(rows, p, n)
    result = []
    for j in range(n):
        if j not in pivots:
            v = [0] * n
            v[j] = 1
            for i, pivot in enumerate(pivots):
                v[pivot] = -reduced[i][j] % p
            result.append(tuple(v))
    return tuple(result)


def basis_matrix(vectors, p, n):
    columns = list(vectors)
    require(len(rref(columns, p, n)[1]) == len(columns), "independent input basis")
    for v in identity(n):
        if len(rref(columns + [v], p, n)[1]) > len(columns):
            columns.append(v)
    require(len(columns) == n, "basis extension")
    return tuple(zip(*columns))


def quotient_rows(r, a):
    n = len(a)
    return tuple(tuple(r.coeff[a[i][j]][k] for j in range(n))
                 for i in range(n) for k in range(1, r.dim))


def pivot_permutation(r, a, s):
    n = len(a)
    work, order = [list(row) for row in a], list(range(n))
    for k in range(s, n):
        pivot = next((i for i in range(k, n) if r.inv[work[i][k]] is not None), None)
        require(pivot is not None, "local complementary unit pivot")
        work[k], work[pivot] = work[pivot], work[k]
        order[k], order[pivot] = order[pivot], order[k]
        for i in range(k+1, n):
            c = r.mul[work[i][k]][r.inv[work[k][k]]]
            work[i] = [r.add[v][r.neg[r.mul[c][w]]]
                       for v, w in zip(work[i], work[k])]
    return tuple(order)


def factor(r, u, k):
    n = len(u)
    unit = identity(n)
    return tuple(tuple(r.add[unit[i][j]][u[i] if j == k else 0]
                       for j in range(n)) for i in range(n))


def construct(r, a):
    n = len(a)
    if inverse(r, a) is None:
        raise ValueError("target must be invertible")
    kernel = nullspace(quotient_rows(r, a), r.p, n)
    s = len(kernel)
    h = basis_matrix(kernel, r.p, n)
    images = tuple(act(r, a, v) for v in kernel)
    require(all(x < r.p for v in images for x in v), "scalar images")
    b = basis_matrix(images, r.p, n)
    g = inverse(r, b)
    chart = mm(r, mm(r, g, a), h)
    require(all(chart[i][j] == int(i == j) for i in range(n) for j in range(s)),
            "fixed scalar subspace")
    order = pivot_permutation(r, chart, s)
    chart = tuple(chart[i] for i in order)
    g = tuple(g[i] for i in order)
    prefix, operations = identity(n), []
    for j in range(s, n):
        delta = tuple(r.add[chart[i][j]][r.neg[int(i == j)]] for i in range(n))
        inv_prefix = inverse(r, prefix)
        require(inv_prefix is not None, "invertible column prefix")
        u = act(r, inv_prefix, delta)
        require(any(u), "every paid factor is needed")
        operations.append((u, j))
        prefix = mm(r, prefix, factor(r, u, j))
    require(prefix == chart, "literal column construction")
    return inverse(r, g), tuple(operations), inverse(r, h)


def word_matrix(r, word):
    left, operations, right = word
    product = left
    for u, k in operations:
        product = mm(r, product, factor(r, u, k))
    return mm(r, product, right)


def word_action(r, word, vector):
    left, operations, right = word
    value = act(r, right, vector)
    for u, k in reversed(operations):
        source = value[k]
        value = tuple(r.add[v][r.mul[c][source]] for v, c in zip(value, u))
    return act(r, left, value)


def check_target(r, a):
    n = len(a)
    word = construct(r, a)
    d = len(rref(quotient_rows(r, a), r.p, n)[1])
    require(len(word[1]) == d, "exact column lower bound")
    require(word_matrix(r, word) == a, "literal word target")
    for i, j in itertools.product(range(n), range(r.dim)):
        v = tuple(r.p**j if k == i else 0 for k in range(n))
        require(word_action(r, word, v) == act(r, a, v), "independent basis-data execution")
    return word, d, n * r.dim


def free_chart(r, n, rng):
    result = identity(n)
    for _ in range(4*n):
        i, j = rng.randrange(n), rng.randrange(n)
        rows = [list(row) for row in result]
        if i == j:
            scale = rng.randrange(1, r.p)
            rows[i] = [r.mul[scale][v] for v in rows[i]]
        else:
            c = rng.randrange(r.p)
            rows[i] = [r.add[v][r.mul[c][w]] for v, w in zip(rows[i], rows[j])]
        result = tuple(tuple(row) for row in rows)
    require(inverse(r, result) is not None, "free chart invertible")
    return result


def sampled_targets(r, n):
    rng = random.Random(911 + 37*n + r.size)
    radical = 4 if r.kind == "skew" else r.p
    scalar = 2 if r.kind == "field4" else r.add[1][radical]
    require(scalar >= r.p and r.inv[scalar] is not None, "non-scalar unit")
    targets = set()
    for d, _ in itertools.product(range(n+1), range(32)):
        s = n-d
        core = [list(row) for row in identity(n)]
        for j in range(s, n):
            core[j][j] = scalar
            for i in range(j):
                core[i][j] = rng.randrange(r.size)
        a = tuple(tuple(row) for row in core)
        left, right = free_chart(r, n, rng), free_chart(r, n, rng)
        targets.add(mm(r, mm(r, left, a), right))
    return tuple(sorted(targets))


def literal_delta(r, a, charts):
    n = len(a)
    values = []
    for t in charts:
        mt = mm(r, a, t)
        rows = tuple(tuple(r.coeff[r.add[mt[i][j]][r.neg[int(i == j)]]][k]
                           for j in range(n)) for i in range(n) for k in range(r.dim))
        values.append(len(rref(rows, r.p, n)[1]))
    return min(values)


def controls(r, examples):
    rich = next((a, w) for a, w in examples if len(w[1]) >= 2
                and word_matrix(r, (w[0], tuple(reversed(w[1])), w[2])) != a)
    a, word = rich
    left, operations, right = word
    require(word_matrix(r, (left, operations[1:], right)) != a, "dropped factor detected")
    u, k = operations[0]
    changed = (r.add[u[0]][1],) + u[1:]
    require(word_matrix(r, (left, ((changed, k),) + operations[1:], right)) != a,
            "changed coefficient detected")
    require(word_matrix(r, (identity(len(a)), operations, identity(len(a)))) != a,
            "missing free endpoints detected")
    zero = tuple((0,) * 3 for _ in range(3))
    try:
        construct(r, zero)
    except ValueError as error:
        require(str(error) == "target must be invertible", "singular error")
    else:
        raise AssertionError("singular target accepted")
    unit = r.add[1][4]
    a = ((0, unit, 0), (unit, 0, 0), (0, 0, unit))
    require(pivot_permutation(r, a, 0) == (1, 0, 2), "row permutation required")
    require(check_target(r, a)[1] == 3, "unit pivot permutation fixture")
    a = tuple(tuple(r.add[int(i == j)][4 if i == j else 0]
                    for j in range(3)) for i in range(3))
    require(check_target(r, a)[1] == 3, "nilpotents cannot be ignored")
    nonidentity = ((0, 1, 0), (1, 0, 0), (0, 0, 1))
    require(check_target(r, nonidentity)[1] == 0, "free target has zero cost")
    return 8


def binary_calibration(r):
    charts = tuple(tuple(tuple(bits[3*i+j] for j in range(3)) for i in range(3))
                   for bits in itertools.product(range(2), repeat=9)
                   if len(rref(tuple(bits[3*i:3*i+3] for i in range(3)), 2, 3)[1]) == 3)
    require(len(charts) == 168, "complete GL3(F2)")
    for bits in itertools.islice(itertools.product(range(2), repeat=9), 16):
        a = tuple(tuple(int(i == j) + 2*bits[3*i+j] for j in range(3)) for i in range(3))
        require(literal_delta(r, a, charts) == check_target(r, a)[1], "literal minimum over T")
    first = ((1, 2, 0), (2, 1, 2), (0, 2, 1))
    require(check_target(r, first)[1] == 2, "three-role first working example")
    return 16 * len(charts)


def main():
    rows, digest, basis_checks = [], hashlib.sha256(), 0
    kinds = ("dual", "squarezero", "cube", "field4", "skew")
    control_examples, control_ring, calibration = [], None, 0
    for kind in kinds:
        r = Ring(kind)
        check_ring(r)
        if kind == "dual":
            calibration = binary_calibration(r)
        for n in (3, 4, 5):
            targets = sampled_targets(r, n)
            histogram = [0] * (n+1)
            for a in targets:
                word, d, checked = check_target(r, a)
                histogram[d] += 1
                basis_checks += checked
                digest.update(json.dumps([kind, a, word], separators=(",", ":")).encode())
                if kind == "skew" and n == 3:
                    control_examples.append((a, word))
            rows.append({"ring": kind, "roles": n, "targets": len(targets),
                         "cost_histogram": histogram})
        if kind == "skew":
            control_ring = r
    count = controls(control_ring, control_examples)
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    files = {name: hashlib.sha256((package / name).read_bytes()).hexdigest() for name in names}
    receipt = {"rows": rows, "basis_data_checks": basis_checks, "controls": count,
               "literal_delta_charts": calibration, "word_digest": digest.hexdigest(),
               "package_sha256": files}
    print(json.dumps(receipt, sort_keys=True))
    print("PASS_RIGHT_VECTOR_LOCAL_ALL_ROLES targets=" + str(sum(x["targets"] for x in rows))
          + " controls=" + str(count) + " no_new_kappa")


if __name__ == "__main__":
    main()
