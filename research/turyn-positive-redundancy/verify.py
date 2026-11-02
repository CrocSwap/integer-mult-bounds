#!/usr/bin/env python3
"""Exact finite corroboration of positive redundant encoders.

Produced by Nick Petalas. Apache-2.0.
"""
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LIMIT = 32
INPUTS = (
    "research/leech-lattice/TURYN.txt",
    "research/turyn-port-labels/PROOF.txt",
    "research/turyn-port-labels/README.txt",
)
FILES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")


def need(condition, message):
    if not condition:
        raise ValueError(message)


def shape(a):
    need(1 <= len(a) <= LIMIT, "row bound")
    n = len(a[0])
    need(1 <= n <= LIMIT and all(len(row) == n for row in a), "column bound")
    need(all(type(x) in (int, Q) for row in a for x in row), "exact coefficients")
    return len(a), n


def transpose(a):
    shape(a)
    return [list(column) for column in zip(*a)]


def mul(a, b):
    _, n = shape(a)
    m, _ = shape(b)
    need(n == m, "product shape")
    return [[sum(x*y for x, y in zip(row, column, strict=True))
             for column in zip(*b)] for row in a]


def eye(n):
    need(1 <= n <= LIMIT, "identity bound")
    return [[int(i == j) for j in range(n)] for i in range(n)]


def rank(a):
    if not a:
        return 0
    m, n = shape(a)
    work = [[Q(x) for x in row] for row in a]
    pivot_row = 0
    for j in range(n):
        pivot = next((i for i in range(pivot_row, m) if work[i][j]), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        divisor = work[pivot_row][j]
        work[pivot_row] = [x/divisor for x in work[pivot_row]]
        for i in range(pivot_row+1, m):
            scale = work[i][j]
            work[i] = [x-scale*y for x, y in zip(work[i], work[pivot_row], strict=True)]
        pivot_row += 1
    return pivot_row


def det(a):
    n, m = shape(a)
    need(n == m, "square determinant")
    work = [[Q(x) for x in row] for row in a]
    answer = Q(1)
    for j in range(n):
        pivot = next((i for i in range(j, n) if work[i][j]), None)
        if pivot is None:
            return Q(0)
        if pivot != j:
            work[j], work[pivot] = work[pivot], work[j]
            answer = -answer
        divisor = work[j][j]
        answer *= divisor
        for i in range(j+1, n):
            scale = work[i][j]/divisor
            work[i] = [x-scale*y for x, y in zip(work[i], work[j], strict=True)]
    return answer


def positive(h):
    n, m = shape(h)
    need(n == m and h == transpose(h), "symmetric metric")
    need(all(det([row[:k] for row in h[:k]]) > 0 for k in range(1, n+1)),
         "positive definite metric")


def confinement(a, h, k):
    n, r = shape(a)
    need(shape(h) == (r, r) and shape(k) == (n, n), "factorization shape")
    positive(h)
    need(mul(mul(a, h), transpose(a)) == k, "factorization endpoint")
    rk = rank(k)
    need(rank(a) == rk, "equal Gram and encoder ranks")
    joined = [x+y for x, y in zip(k, a, strict=True)]
    need(rank(joined) == rk, "encoder confinement")
    return rk


def binary_rank(labels):
    basis = {}
    for label in labels:
        for pivot in range(4, -1, -1):
            if not (label >> pivot) & 1:
                continue
            if pivot in basis:
                label ^= basis[pivot]
            else:
                basis[pivot] = label
                break
    return len(basis)


def full_support(k, labels, h):
    n, m = shape(k)
    need(n == m and len(labels) == n and 1 <= h <= 5, "support shape")
    need(all(type(x) is int and 0 <= x < 2**h for x in labels), "binary labels")
    rk = rank(k)
    need(rk > 0, "nonzero kernel")
    for functional in range(1, 2**h):
        rows = [row for row, label in zip(k, labels, strict=True)
                if (label & functional).bit_count() % 2]
        need(rank(rows) == rk, "full-support range hypothesis")
    return rk


def bill(a, labels):
    _, n = shape(a)
    costs = [binary_rank([label for row, label in zip(a, labels, strict=True) if row[j]])
             for j in range(n)]
    nonzero = sum(any(row[j] for row in a) for j in range(n))
    return sum(costs), nonzero


def small_gram_cases():
    counts = {"0": 0, "1": 0, "2": 0}
    metrics = [[[a, b], [b, c]] for a, b, c in product(range(1, 4), range(-3, 4), range(1, 4))
               if a*c > b*b]
    for values in product(range(-1, 2), repeat=4):
        a = [list(values[:2]), list(values[2:])]
        # Independent two-by-two rank oracle, including singular and zero A.
        oracle = 2 if values[0]*values[3] != values[1]*values[2] else int(any(values))
        for h in metrics:
            k = mul(mul(a, h), transpose(a))
            rk = confinement(a, h, k)
            need(rk == oracle, "two-by-two rank oracle")
            counts[str(rk)] += 1
    return {"metrics": len(metrics), "cases_by_rank": counts}


def rectangular_cases():
    count = 0
    for n, r, seed in product(range(1, 5), range(1, 6), range(4)):
        a = [[((i+1)*(j+1)+seed) % 5-2 for j in range(r)] for i in range(n)]
        c = [[(2*i+j+seed) % 5-2 for j in range(r)] for i in range(r)]
        h = mul(transpose(c), c)
        for i in range(r):
            h[i][i] += 1
        confinement(a, h, mul(mul(a, h), transpose(a)))
        count += 1
    return count


def duplication(u, extra):
    _, r = shape(u)
    a = [[row[0]]*(extra+1)+row[1:] for row in u]
    h = eye(r+extra)
    for i in range(extra+1):
        h[i][i] = Q(1, extra+1)
    return a, h


def attaining_cases():
    count = 0
    for h, r in product(range(1, 6), range(1, 5)):
        u = [[int(i == j) for j in range(r)] for _ in range(h) for i in range(r)]
        labels = [1 << block for block in range(h) for _ in range(r)]
        k = mul(u, transpose(u))
        need(full_support(k, labels, h) == r, "repeated-coordinate premise")
        for extra in range(4):
            a, metric = duplication(u, extra)
            for coupled in (False, True):
                p, inverse = eye(r+extra), eye(r+extra)
                if coupled and r+extra > 1:
                    p[0][-1], inverse[0][-1] = 2, -2
                candidate = mul(a, p)
                transformed = mul(mul(inverse, metric), transpose(inverse))
                need(confinement(candidate, transformed, k) == r, "attainer rank")
                cost, nonzero = bill(candidate, labels)
                need(nonzero == r+extra and cost == h*nonzero, "exact redundancy tariff")
                count += 1
    return count


def boundary_cases():
    k = [[1, 1], [1, 1]]
    need(full_support(k, [1, 2], 2) == 1, "boundary full-support premise")
    examples = [(eye(2), k, 2), ([[1, 1, 1], [1, 0, 0]],
                                [[1, 0, 0], [0, 1, 0], [0, 0, -1]], 4)]
    for a, metric, expected_cost in examples:
        need(mul(mul(a, metric), transpose(a)) == k, "boundary exact endpoint")
        need(rank([x+y for x, y in zip(k, a, strict=True)]) > rank(k),
             "boundary escapes range confinement")
        cost, nonzero = bill(a, [1, 2])
        need(cost == expected_cost and cost < 2*nonzero, "boundary refutes hR extension")
    return len(examples)


def rejection_cases():
    a, k = [[1], [1]], [[1, 1], [1, 1]]
    cases = [(a, [[0]], k), (a, [[-1]], k), (a, [[1]], eye(2)),
             (eye(2), [[1, 1], [0, 1]], eye(2)),
             (eye(2), [[1, 1], [1, 1]], [[1, 1], [1, 1]])]
    count = 0
    for a, metric, target in cases:
        try:
            confinement(a, metric, target)
        except ValueError:
            count += 1
        else:
            raise ValueError("invalid factorization accepted")
    for target, labels, h in [(k, [1, 1], 2), (eye(2), [1, 2], 2),
                              (k, [1, 4], 2), (k, [1], 2)]:
        try:
            full_support(target, labels, h)
        except ValueError:
            count += 1
        else:
            raise ValueError("invalid support premise accepted")
    return count


def bounded_bytes(path):
    need(path.stat().st_size <= 1024*1024, "file size bound")
    raw = path.read_bytes()
    need(len(raw) <= 1024*1024, "read size bound")
    return raw


def authenticate():
    manifest = json.loads(bounded_bytes(HERE/"SOURCES.json"))
    need(len(manifest["files"]) <= 8, "source row bound")
    pins = {row["path"]: row for row in manifest["files"] if row["usage"] == "input"}
    need(set(pins) == set(INPUTS), "explicit theorem-source inputs")
    for path in INPUTS:
        need(sha256(bounded_bytes(ROOT/path)).hexdigest() == pins[path]["sha256"],
             "cited theorem source hash")


def main():
    authenticate()
    result = {"small_gram": small_gram_cases(), "rectangular_gram": rectangular_cases(),
              "fixed_kernel_attainers": attaining_cases(), "metric_boundaries": boundary_cases(),
              "rejecting_controls": rejection_cases()}
    a = [[1, 0], [1, 0]]
    need(confinement(a, eye(2), [[1, 1], [1, 1]]) == 1, "zero-column confinement")
    need(bill(a, [1, 2]) == (2, 1), "zero-column tariff")
    result["zero_column_controls"] = 1
    print(json.dumps(result, sort_keys=True))
    receipt = {name: sha256(bounded_bytes(HERE/name)).hexdigest() for name in FILES}
    receipt.update({path: sha256(bounded_bytes(ROOT/path)).hexdigest() for path in INPUTS})
    print(json.dumps({"generated_sha256_receipt": receipt}, sort_keys=True))
    print("PASS_TURYN_POSITIVE_REDUNDANCY")


if __name__ == "__main__":
    main()
