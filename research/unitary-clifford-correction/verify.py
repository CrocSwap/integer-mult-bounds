#!/usr/bin/env python3
"""Exact bounded corroboration of the unitary correction-rank theorem.

Produced by Nick Petalas. Apache-2.0. All Gaussian arithmetic uses integers.
Universal quantifiers are proved in PROOF.md, not inferred from these checks.
"""

import hashlib
import itertools
import json
import math
from pathlib import Path
import sys


ZERO = (0, 0)
ONE = (1, 0)
ROOTS = ((1, 0), (0, 1), (-1, 0), (0, -1))
MAX_DIM = 32


def need(condition, message):
    if not condition:
        raise ValueError(message)


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def neg(a):
    return (-a[0], -a[1])


def mul(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def scale(a, c):
    return (a[0] * c, a[1] * c)


def conjugate(a):
    return (a[0], -a[1])


def identity(n, coefficient=1):
    need(type(n) is int and 1 <= n <= MAX_DIM, "matrix capacity")
    return [[(coefficient, 0) if i == j else ZERO for j in range(n)]
            for i in range(n)]


def adjoint(a):
    return [[conjugate(a[j][i]) for j in range(len(a))]
            for i in range(len(a[0]))]


def product(a, b):
    n, k, m = len(a), len(b), len(b[0])
    need(1 <= n <= MAX_DIM and 1 <= k <= MAX_DIM and 1 <= m <= MAX_DIM,
         "product capacity")
    need(all(len(row) == k for row in a) and all(len(row) == m for row in b),
         "product shape")
    out = [[ZERO for _ in range(m)] for _ in range(n)]
    for i, row in enumerate(a):
        for t, value in enumerate(row):
            if value != ZERO:
                for j, other in enumerate(b[t]):
                    if other != ZERO:
                        out[i][j] = add(out[i][j], mul(value, other))
    return out


def difference(a, b):
    return [[add(x, neg(y)) for x, y in zip(row, other, strict=True)]
            for row, other in zip(a, b, strict=True)]


def times(a, c):
    return [[scale(x, c) for x in row] for row in a]


def rank_mod(a, prime, imag):
    need((prime, imag) in ((5, 2), (13, 5), (17, 4)), "modular field")
    rows = [[(x + imag * y) % prime for x, y in row] for row in a]
    n, m, rank = len(rows), len(rows[0]), 0
    need(1 <= n <= MAX_DIM and 1 <= m <= MAX_DIM, "rank capacity")
    for col in range(m):
        pivot = next((j for j in range(rank, n) if rows[j][col]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inv = pow(rows[rank][col], -1, prime)
        rows[rank] = [(x * inv) % prime for x in rows[rank]]
        for j in range(rank + 1, n):
            factor = rows[j][col]
            rows[j] = [(x - factor * y) % prime
                       for x, y in zip(rows[j], rows[rank], strict=True)]
        rank += 1
        if rank == n:
            break
    return rank


def block_rank(a):
    """Exact Q(i) rank for a matrix supported on diagonal 2-by-2 blocks."""
    n = len(a)
    need(n % 2 == 0 and n <= MAX_DIM, "block dimension")
    need(all(a[i][j] == ZERO for i in range(n) for j in range(n)
             if i // 2 != j // 2), "off-block entry")
    rank = 0
    for j in range(0, n, 2):
        x, y, z, w = a[j][j], a[j][j + 1], a[j + 1][j], a[j + 1][j + 1]
        determinant = add(mul(x, w), neg(mul(y, z)))
        rank += 2 if determinant != ZERO else int(any(t != ZERO for t in (x, y, z, w)))
    return rank


def multiplicities(h):
    need(type(h) is int and 1 <= h <= 65, "spectral width")
    return tuple(sum(math.comb(h, k) for k in range(j, h + 1, 4)) for j in range(4))


def shifted_counts(counts, phase, direction):
    out = [0] * 4
    for label, count in enumerate(counts):
        out[(phase + direction * label) % 4] += count
    return tuple(out)


def assignment(s, phase, direction):
    need(type(s) is int and 0 <= s <= 4, "dense lane exponent")
    need(type(phase) is int and 0 <= phase < 4, "fourth-root phase")
    need(type(direction) is int and direction in (-1, 1), "child direction")
    n = 1 << (s + 1)
    labels = [(phase + direction * j.bit_count()) % 4 for j in range(n)]
    groups = [[j for j in range(n) if labels[j] == label] for label in range(4)]
    used = [0] * 4
    order = [-1] * n
    for j in range(n):
        label = j % 2
        if used[label] < len(groups[label]):
            order[j] = groups[label][used[label]]
            used[label] += 1
    remaining = iter(j for j in range(n) if j not in order)
    for j in range(n):
        if order[j] == -1:
            order[j] = next(remaining)
    need(sorted(order) == list(range(n)), "assignment bijection")
    return order, labels


def kernel(s, phase, direction):
    order, labels = assignment(s, phase, direction)
    n = len(order)
    out = []
    for x in range(n):
        row = []
        for j in range(n):
            a = (-1) ** ((x & order[j - j % 2]).bit_count())
            b = (-1) ** ((x & order[j - j % 2 + 1]).bit_count())
            row.append((a + (-1) ** (j % 2) * b, 0))
        out.append(row)
    return out, [labels[j] for j in order]


def tensor_child(h, phase, direction):
    """Numerator of i^phase C_h^direction with denominator 2^h."""
    a = (1, direction)
    b = (1, -direction)
    out = [[ONE]]
    for _ in range(h):
        size = len(out)
        need(2 * size <= MAX_DIM, "tensor capacity")
        out = [[mul(a if i // size == j // size else b, out[i % size][j % size])
                for j in range(2 * size)] for i in range(2 * size)]
    return [[mul(ROOTS[phase], x) for x in row] for row in out]


def distance_child(h, phase, direction):
    """Separate complete entry formula indexed only by Hamming distance."""
    n = 1 << h
    need(n <= MAX_DIM, "distance capacity")
    entries = []
    for distance in range(h + 1):
        value = ROOTS[phase]
        for j in range(h):
            value = mul(value, (1, -direction if j < distance else direction))
        entries.append(value)
    return [[entries[(x ^ y).bit_count()] for y in range(n)] for x in range(n)]


def paired_operator(labels):
    """Twice the operator with these eigenvalues in the block-Walsh basis."""
    n = len(labels)
    out = [[ZERO for _ in range(n)] for _ in range(n)]
    for j in range(0, n, 2):
        a, b = ROOTS[labels[j]], ROOTS[labels[j + 1]]
        out[j][j] = out[j + 1][j + 1] = add(a, b)
        out[j][j + 1] = out[j + 1][j] = add(a, neg(b))
    return out


def check_kernel(k):
    need(product(adjoint(k), k) == identity(len(k), 2 * len(k)),
         "encoder fails norm preservation")


def check_intertwiner(h, k, b):
    n = len(k)
    need(times(product(h, k), 2) == times(product(k, b), n),
         "child/encoder endpoint mismatch")


def spectral_checks():
    recurrence = (1, 0, 0, 0)
    cases = 0
    for h in range(1, 66):
        recurrence = tuple(recurrence[j] + recurrence[(j - 1) % 4] for j in range(4))
        counts = multiplicities(h)
        need(counts == recurrence and sum(counts) == 1 << h, "weight counts")
        scores = []
        for phase in range(4):
            for direction in (-1, 1):
                shifted = shifted_counts(counts, phase, direction)
                need(max(shifted) <= 1 << (h - 1), "matching capacity")
                scores.append(shifted[2] + shifted[3])
                cases += 1
        need(min(scores) == (1 << (h - 1)) - (1 << ((h - 1) // 2)),
             "phase-optimized unitary rank")
    return cases


def permutation_checks():
    cases = 0
    for s in range(3):
        n = 1 << (s + 1)
        for phase in range(4):
            for direction in (-1, 1):
                _, labels = assignment(s, phase, direction)
                best = n
                for order in itertools.permutations(range(n)):
                    score = sum(labels[order[j]] != j % 2 for j in range(n))
                    best = min(best, score)
                    cases += 1
                need(best == sum(label >= 2 for label in labels), "permutation optimum")
    return cases


def dense_checks():
    cases, entries, witness = 0, 0, None
    for s in range(5):
        for phase in range(4):
            for direction in (-1, 1):
                k, labels = kernel(s, phase, direction)
                n = len(k)
                h = tensor_child(s + 1, phase, direction)
                need(h == distance_child(s + 1, phase, direction), "native entries")
                b, t = paired_operator(labels), paired_operator([j % 2 for j in range(n)])
                check_kernel(k)
                check_intertwiner(h, k, b)
                f = product(t, adjoint(b))
                need(product(f, b) == times(t, 4), "corrected full endpoint")
                need(product(adjoint(f), f) == identity(n, 16), "unitary correction")
                defect = difference(f, identity(n, 4))
                rank = block_rank(defect)
                need(rank == sum(label >= 2 for label in labels), "attaining rank")
                need(rank_mod(defect, 5, 2) == rank_mod(defect, 13, 5) == rank,
                     "independent finite-field rank lower bounds")
                if (s, phase, direction) == (4, 2, 1):
                    need(rank == 12 and {x for row in k for x in row} ==
                         {ZERO, (2, 0), (-2, 0)}, "dyadic sixteen-lane witness")
                    witness = {"rank": rank, "encoder_denominator": 8,
                               "kernel_sha256": hashlib.sha256(json.dumps(k).encode()).hexdigest()}
                cases += 1
                entries += n * n
    need(witness is not None, "missing sixteen-lane witness")
    return cases, entries, witness


def mixed_checks():
    cases = 0
    _, labels = kernel(4, 2, 1)
    b = paired_operator(labels)
    t = paired_operator([j % 2 for j in range(32)])
    for j in range(1, 32):
        r = identity(32, 5)
        r[0][0], r[j][j], r[0][j], r[j][0] = (3, 0), (3, 0), (4, 0), (-4, 0)
        need(product(adjoint(r), r) == identity(32, 25), "rational rotation")
        rotated = product(product(adjoint(r), b), r)
        defect = difference(times(t, 25), rotated)
        need(rank_mod(defect, 13, 5) >= 12 and rank_mod(defect, 17, 4) >= 12,
             "mixed unitary encoder lower bound")
        cases += 1
    return cases


def controls():
    rejected, semantic = 0, 0
    for args in ((-1, 0, 1), (True, 0, 1), (5, 0, 1), (0, 4, 1), (0, 0, 0)):
        try:
            assignment(*args)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid domain accepted")
    k, labels = kernel(4, 2, 1)
    corrupt = [row[:] for row in k]
    corrupt[0][0] = add(corrupt[0][0], ONE)
    try:
        check_kernel(corrupt)
    except ValueError:
        rejected += 1
    else:
        raise ValueError("corrupted encoder accepted")
    try:
        check_intertwiner(tensor_child(5, 1, 1), k, paired_operator(labels))
    except ValueError:
        rejected += 1
    else:
        raise ValueError("wrong child phase accepted")
    b0 = [[(1, -2), (-2, 0)], [(0, -2), (-2, 1)]]
    t0 = [[ONE, ZERO], [ZERO, (0, 1)]]
    need(block_rank(difference(t0, b0)) == 1, "nonunitary escape rank")
    need(product(adjoint(b0), b0) != identity(2), "nonunitary escape detected")
    need(add(b0[0][0], b0[1][1]) == (-1, -1) and
         add(mul(b0[0][0], b0[1][1]), neg(mul(b0[0][1], b0[1][0]))) == (0, 1),
         "escape characteristic polynomial")
    semantic += 1
    need(block_rank(difference(t0, [[(-1, 0), ZERO], [ZERO, (0, -1)]])) == 2,
         "unitary two-dimensional contrast")
    semantic += 1
    need(paired_operator(labels) != paired_operator([j % 2 for j in range(32)]),
         "omitted correction must fail")
    semantic += 1
    need(sum(label >= 2 for label in labels) > max(labels.count(2), labels.count(3)),
         "maximum multiplicity is insufficient with unitary encoding")
    semantic += 1
    return {"rejected_inputs_or_mutations": rejected, "semantic_controls": semantic}


def receipt():
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    out = {}
    for name in names:
        path = Path(__file__).resolve().parent / name
        need(path.is_file() and path.stat().st_size <= 1_000_000, "receipt file bound")
        out[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return out


def main():
    cases, entries, witness = dense_checks()
    result = {"status": "PASS_UNITARY_CLIFFORD_CORRECTION", "claim_type": "scoped-proof",
              "spectral_cases": spectral_checks(), "dense_operator_cases": cases,
              "native_entries_compared": entries, "spectral_permutations": permutation_checks(),
              "mixed_unitary_encoders": mixed_checks(), "sixteen_lane_witness": witness,
              "controls": controls(), "python": sys.version.split()[0], "sha256": receipt()}
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
