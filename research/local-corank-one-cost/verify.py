"""Bounded literal words for the residue-corank-one theorem. No writes."""

from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from random import Random


def require(condition, message):
    if not condition:
        raise ValueError(message)


def f4mul(a, b):
    value = 0
    for bit in range(2):
        if b & (1 << bit):
            value ^= a << bit
    return value ^ 7 if value & 4 else value


class Algebra:
    def __init__(self, name, p, dimension, kind):
        self.name, self.p, self.dimension = name, p, dimension
        self.size = p ** dimension
        require(self.size <= 16, "algebra capacity")
        self.coords = tuple(tuple((x // p**j) % p for j in range(dimension))
                            for x in range(self.size))
        self.add = tuple(tuple(self.encode(tuple((a + b) % p for a, b in
                         zip(self.coords[x], self.coords[y], strict=True)))
                         for y in range(self.size)) for x in range(self.size))
        self.neg = tuple(self.encode(tuple(-a % p for a in c)) for c in self.coords)
        self.mul = tuple(tuple(self.raw_mul(x, y, kind) for y in range(self.size))
                         for x in range(self.size))
        self.res = tuple(x % (4 if kind in ("f4", "twisted", "f4dual") else p)
                         for x in range(self.size))
        self.inv = tuple(next((y for y in range(self.size)
                              if self.mul[x][y] == self.mul[y][x] == 1), None)
                         for x in range(self.size))
        self.validate()

    def encode(self, coordinates):
        return sum(a * self.p**j for j, a in enumerate(coordinates))

    def raw_mul(self, x, y, kind):
        if kind == "f4":
            return f4mul(x, y)
        if kind in ("twisted", "f4dual"):
            a, b, c, d = x % 4, x // 4, y % 4, y // 4
            sigma_c = f4mul(c, c) if kind == "twisted" else c
            return f4mul(a, c) + 4 * (f4mul(a, d) ^ f4mul(b, sigma_c))
        a, b = self.coords[x], self.coords[y]
        return self.encode((a[0] * b[0] % self.p,) + tuple(
            (a[0] * b[j] + a[j] * b[0]) % self.p
            for j in range(1, self.dimension)))

    def validate(self):
        for x in range(self.size):
            require((self.inv[x] is not None) == (self.res[x] != 0), "local units")
            require(self.mul[x][1] == self.mul[1][x] == x, "identity")
            for y in range(self.size):
                require(self.res[self.mul[x][y]] == self.mul[self.res[x]][self.res[y]],
                        "residue homomorphism")
                for z in range(self.size):
                    require(self.mul[self.mul[x][y]][z] == self.mul[x][self.mul[y][z]],
                            "associativity")
                    require(self.mul[x][self.add[y][z]] ==
                            self.add[self.mul[x][y]][self.mul[x][z]], "left distribution")
                    require(self.mul[self.add[y][z]][x] ==
                            self.add[self.mul[y][x]][self.mul[z][x]], "right distribution")
        for x in range(self.size):
            for a in range(self.p):
                require(self.mul[x][a] == self.mul[a][x], "central base field")


def identity(n):
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def mm(a, b, r):
    require(len(a[0]) == len(b), "matrix dimensions")
    out = []
    for row in a:
        result = []
        for j in range(len(b[0])):
            value = 0
            for k in range(len(b)):
                value = r.add[value][r.mul[row[k]][b[k][j]]]
            result.append(value)
        out.append(tuple(result))
    return tuple(out)


def inverse(a, r):
    n = len(a)
    rows = [list(a[i]) + list(identity(n)[i]) for i in range(n)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if r.res[rows[i][j]]), None)
        require(pivot is not None, "nonunit matrix pivot")
        rows[j], rows[pivot] = rows[pivot], rows[j]
        unit_inverse = r.inv[rows[j][j]]
        rows[j] = [r.mul[unit_inverse][x] for x in rows[j]]
        for i in range(n):
            if i != j:
                coefficient = rows[i][j]
                rows[i] = [r.add[x][r.neg[r.mul[coefficient][y]]]
                           for x, y in zip(rows[i], rows[j], strict=True)]
    result = tuple(tuple(row[n:]) for row in rows)
    require(mm(a, result, r) == mm(result, a, r) == identity(n), "inverse identity")
    return result


def prime_rank(columns, p):
    if not columns:
        return 0
    rows = [list(row) for row in zip(*columns, strict=True)]
    rank = 0
    for j in range(len(columns)):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][j] % p), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inv = pow(rows[rank][j], -1, p)
        rows[rank] = [x * inv % p for x in rows[rank]]
        for i in range(len(rows)):
            if i != rank:
                c = rows[i][j]
                rows[i] = [(x - c * y) % p
                           for x, y in zip(rows[i], rows[rank], strict=True)]
        rank += 1
        if rank == len(rows):
            break
    return rank


def residue_rank(a, r):
    rows = [[r.res[x] for x in row] for row in a]
    rank, n = 0, len(a)
    for j in range(n):
        pivot = next((i for i in range(rank, n) if rows[i][j]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inv = r.inv[rows[rank][j]]
        rows[rank] = [r.mul[inv][x] for x in rows[rank]]
        for i in range(n):
            if i != rank:
                c = rows[i][j]
                rows[i] = [r.add[x][r.neg[r.mul[c][y]]]
                           for x, y in zip(rows[i], rows[rank], strict=True)]
        rank += 1
        if rank == n:
            break
    return rank


def from_columns(columns):
    return tuple(zip(*columns, strict=True))


def extend(columns, n, p):
    result = list(columns)
    for column in identity(n):
        if prime_rank(result + [column], p) > len(result):
            result.append(column)
    require(len(result) == n, "basis extension")
    return from_columns(result)


def scalar_charts(m, r):
    n, inputs, outputs = len(m), [], []
    for v in product(range(r.p), repeat=n):
        image = tuple(row[0] for row in mm(m, tuple((x,) for x in v), r))
        if all(x < r.p for x in image) and prime_rank(outputs + [image], r.p) > len(outputs):
            inputs.append(v)
            outputs.append(image)
    h, x = extend(inputs, n, r.p), extend(outputs, n, r.p)
    return h, x, len(outputs)


def pivot_charts(a, r):
    n, rows, cols = len(a), list(range(len(a))), list(range(len(a)))
    work = [list(row) for row in a]
    for j in range(n - 1):
        pivot = next(((i, c) for i in range(j, n) for c in range(j, n)
                      if r.res[work[i][c]]), None)
        require(pivot is not None, "insufficient residue rank")
        i, c = pivot
        rows[j], rows[i] = rows[i], rows[j]
        work[j], work[i] = work[i], work[j]
        cols[j], cols[c] = cols[c], cols[j]
        for row in work:
            row[j], row[c] = row[c], row[j]
        for i in range(j + 1, n):
            multiplier = r.mul[work[i][j]][r.inv[work[j][j]]]
            work[i] = [r.add[x][r.neg[r.mul[multiplier][y]]]
                       for x, y in zip(work[i], work[j], strict=True)]
    return tuple(rows), tuple(cols)


def construct(m, r):
    n = len(m)
    require(1 <= n <= 4 and all(len(row) == n for row in m), "role capacity")
    require(residue_rank(m, r) == n - 1, "requires residue corank exactly one")
    h, x, fixed = scalar_charts(m, r)
    a = mm(mm(inverse(x, r), m, r), h, r)
    rows, cols = pivot_charts(a, r)
    require(rows[:fixed] == cols[:fixed] == tuple(range(fixed)), "fixed columns retained")
    a = tuple(tuple(a[i][j] for j in cols) for i in rows)
    left = tuple(tuple(int(j == rows[i]) for j in range(n)) for i in range(n))
    right = tuple(tuple(int(i == cols[j]) for j in range(n)) for i in range(n))
    free_left = mm(x, inverse(left, r), r)
    free_right = mm(inverse(right, r), inverse(h, r), r)
    current, factors = identity(n), []
    for j in range(fixed, n):
        target = tuple(tuple(a[i][c] if c <= j else int(i == c)
                             for c in range(n)) for i in range(n))
        factor = mm(inverse(current, r), target, r)
        require(all(factor[i][c] == int(i == c)
                    for i in range(n) for c in range(n) if c != j), "paid right vector")
        factors.append(factor)
        current = mm(current, factor, r)
    require(mm(mm(free_left, current, r), free_right, r) == m, "literal endpoint")
    return free_left, tuple(factors), free_right, n - fixed


def expanded_rank(m, r):
    columns = [tuple(c for row in m for c in r.coords[row[j]]) for j in range(len(m))]
    return prime_rank(columns, r.p)


def direct_delta(m, charts, r):
    n, values = len(m), []
    for t in charts:
        mt = mm(m, t, r)
        difference = tuple(tuple(r.add[mt[i][j]][r.neg[int(i == j)]]
                                 for j in range(n)) for i in range(n))
        values.append(expanded_rank(difference, r))
    return min(values)


def fold(factors, n, r):
    result = identity(n)
    for factor in factors:
        result = mm(result, factor, r)
    return result


def apply_word(left, factors, right, vector, r):
    value = mm(right, vector, r)
    for factor in reversed(factors):
        value = mm(factor, value, r)
    return mm(left, value, r)


def check_target(m, r):
    left, factors, right, cost = construct(m, r)
    require(len(factors) == cost, "cost matches word")
    for j in range(len(m)):
        for coordinate in range(r.dimension):
            data = tuple((r.p**coordinate if i == j else 0,) for i in range(len(m)))
            require(apply_word(left, factors, right, data, r) == mm(m, data, r),
                    "basis-data execution")
    return cost, (left, factors, right)


def expect_rejection(action):
    try:
        action()
    except ValueError:
        return
    raise ValueError("negative control was accepted")


def controls(r, witness):
    m, (left, factors, right) = witness
    n = len(m)
    require(len(factors) >= 2, "nontrivial control word")
    expect_rejection(lambda: construct(identity(n), r))
    expect_rejection(lambda: construct(tuple(tuple(0 for _ in range(n)) for _ in range(n)), r))
    expect_rejection(lambda: inverse(m, r))
    target = lambda fs: mm(mm(left, fold(fs, n, r), r), right, r)
    require(target(factors[:-1]) != m, "omitted final factor control")
    require(target(tuple(reversed(factors))) != m, "factor order control")
    require(mm(left, fold(factors, n, r), r) != m or
            mm(fold(factors, n, r), right, r) != m, "free boundary control")
    corrupted = [list(row) for row in factors[-1]]
    corrupted[0][-1] = r.add[corrupted[0][-1]][1]
    require(target(factors[:-1] + (tuple(tuple(row) for row in corrupted),)) != m,
            "changed paid factor control")
    radical = tuple(tuple(r.p if i == j else 0 for j in range(2)) for i in range(2))
    expect_rejection(lambda: construct(radical, r))
    return 8


def sampled_targets(r, n, count):
    rng, found = Random(17011 + r.size * 31 + n), set()
    for _ in range(4000):
        m = tuple(tuple(rng.randrange(r.size) for _ in range(n)) for _ in range(n))
        if residue_rank(m, r) == n - 1:
            found.add(m)
        if len(found) == count:
            return tuple(sorted(found))
    raise ValueError("sample capacity exhausted")


def check_family(index, r, charts):
    records, executions, calibrations, witness = [], 0, 0, None
    for n, count in ((3, 80), (4, 40)):
        targets = set(sampled_targets(r, n, count))
        if index == 0 and n == 3:
            targets.update(tuple(tuple(int(i == j and i < 2) + 2*bits[3*i+j]
                                       for j in range(3)) for i in range(3))
                           for bits in product(range(2), repeat=9))
        histogram = [0] * (n + 1)
        for position, m in enumerate(sorted(targets)):
            cost, word = check_target(m, r)
            histogram[cost] += 1
            executions += n * r.dimension
            if r.p == 2 and n == 3 and position < 8:
                require(direct_delta(m, charts, r) == cost, "independent chart minimum")
                calibrations += len(charts)
            if index == 0 and n == 3 and cost >= 2:
                left, factors, right = word
                if fold(factors, n, r) != fold(tuple(reversed(factors)), n, r):
                    if mm(left, fold(factors, n, r), r) != m:
                        witness = (m, word)
        records.append({"algebra": r.name, "roles": n, "targets": len(targets),
                        "cost_histogram": histogram})
    return records, executions, calibrations, witness


def main():
    algebras = (Algebra("binary dual", 2, 2, "square"),
                Algebra("ternary dual", 3, 2, "square"),
                Algebra("binary two-generator square-zero", 2, 3, "square"),
                Algebra("F4 over F2", 2, 2, "f4"),
                Algebra("twisted F4 dual over F2", 2, 4, "twisted"))
    charts = tuple(tuple(tuple(bits[3*i+j] for j in range(3)) for i in range(3))
                   for bits in product(range(2), repeat=9)
                   if prime_rank([bits[3*i:3*i+3] for i in range(3)], 2) == 3)
    require(len(charts) == 168, "GL3 binary calibration coverage")
    records, executions, calibrations, witness = [], 0, 0, None
    for index, r in enumerate(algebras):
        rows, runs, trials, found = check_family(index, r, charts)
        records.extend(rows)
        executions += runs
        calibrations += trials
        if found is not None:
            witness = found
    require(witness is not None, "control fixture")
    count = controls(algebras[0], witness)
    comparison_ring = Algebra("commutative F4 dual over F2", 2, 4, "f4dual")
    shared_targets = (((1, 0), (0, 4)), ((1, 4), (4, 0)))
    shared_costs = tuple(check_target(m, comparison_ring)[0] for m in shared_targets)
    require(shared_costs == (1, 2), "shared two-role boundary examples")
    package = Path(__file__).resolve().parent
    hashes = {name: sha256((package / name).read_bytes()).hexdigest() for name in
              ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")}
    result = {"records": records, "basis_data_executions": executions,
              "direct_chart_evaluations": calibrations, "controls": count,
              "shared_F4_dual_two_role_costs": shared_costs,
              "package_sha256": hashes}
    print(json.dumps(result, sort_keys=True))
    print("PASS_LOCAL_CORANK_ONE_COST targets=" + str(sum(x["targets"] for x in records))
          + " controls=" + str(count) + " no_new_kappa")


if __name__ == "__main__":
    main()
