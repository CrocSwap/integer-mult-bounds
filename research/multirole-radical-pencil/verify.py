#!/usr/bin/env python3
"""Finite corroboration of the multi-role radical-pencil obstruction.

Produced by Nick Petalas. Apache-2.0.
Only F2, three roles and two independent square-zero coefficients are executed.
The arbitrary-field, arbitrary-length argument is in README.md.
"""

from hashlib import sha256
from itertools import product
import json
from pathlib import Path


N = 3
SIDE = 1 << N
STATES = 1 << (N * N)
IDENTITY = sum(1 << (N * i + i) for i in range(N))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def row_times(vector, matrix):
    result = 0
    for i in range(N):
        if vector >> i & 1:
            result ^= matrix >> (N * i) & (SIDE - 1)
    return result


def column_times(matrix, vector):
    return sum(((row_times(1 << i, matrix) & vector).bit_count() % 2)
               << i for i in range(N))


def multiply(left, right):
    return sum(row_times(row_times(1 << i, left), right) << (N * i)
               for i in range(N))


def outer(column, row):
    return sum(row << (N * i) for i in range(N) if column >> i & 1)


def rank(matrix):
    basis = [0] * N
    result = 0
    for i in range(N):
        value = row_times(1 << i, matrix)
        for pivot in range(N - 1, -1, -1):
            if value >> pivot & 1:
                if basis[pivot]:
                    value ^= basis[pivot]
                else:
                    basis[pivot] = value
                    result += 1
                    break
    return result


def eigenpairs(matrix):
    return [(v, scalar) for v in range(1, SIDE) for scalar in range(2)
            if row_times(v, matrix) == scalar * v]


def ring_multiply(left, right):
    """Matrix product over F2[x,y]/(x,y)^2, represented by three matrices."""
    a, x, y = left
    b, u, v = right
    return (multiply(a, b), multiply(a, u) ^ multiply(x, b),
            multiply(a, v) ^ multiply(y, b))


def action(matrix, vector):
    """Act directly on three ring elements encoded as bits 1,x,y."""
    a, x, y = matrix
    c, u, v = (sum(((entry >> bit) & 1) << i
                  for i, entry in enumerate(vector)) for bit in range(3))
    images = (column_times(a, c),
              column_times(a, u) ^ column_times(x, c),
              column_times(a, v) ^ column_times(y, c))
    return tuple(sum(((images[bit] >> i) & 1) << bit for bit in range(3))
                 for i in range(N))


def check_first_zero_transitions():
    """Check every single radical-coefficient instance of the first-zero step."""
    rows = tuple(tuple(row_times(v, m) for m in range(STATES))
                 for v in range(SIDE))
    invertible = tuple(rank(m) == N for m in range(STATES))
    cases = 0
    full_rank = 0
    scalar_pairs = 0
    for u in range(1, SIDE):
        for y in range(1, SIDE):
            if (u & y).bit_count() % 2 != 1:
                continue
            scalar = IDENTITY ^ outer(u, y)
            need(rank(scalar) == N - 1, "singular factor rank")
            need(rows[y][scalar] == 0, "left kernel")
            products = tuple(multiply(scalar, c) for c in range(STATES))
            for psi in range(1, SIDE):
                previous = outer(u, psi)
                need(rank(previous) == 1, "last nonzero scalar prefix rank")
                need(multiply(scalar, previous) == 0, "first zero prefix")
                need(rows[y][previous] == psi, "common row")
                scalar_pairs += 1
                for c in range(STATES):
                    for ux in range(SIDE):
                        coefficient = products[c] ^ outer(ux, psi)
                        alpha = (y & ux).bit_count() % 2
                        need(rows[y][coefficient] == alpha * psi,
                             "first-zero coefficient row identity")
                        cases += 1
                        if invertible[coefficient]:
                            need(alpha == 1, "invertible coefficient has nonzero row")
                            full_rank += 1
    return scalar_pairs, cases, full_rank


def check_pencils():
    # Companion of t^3+t+1, with columns e2, e3, e1+e2.
    companion = (0b100 << 0) | (0b101 << 3) | (0b010 << 6)
    need(multiply(companion, multiply(companion, companion))
         ^ companion ^ IDENTITY == 0, "companion polynomial")
    need(not eigenpairs(companion), "explicit pencil is obstructed")
    excluded = [m for m in range(STATES) if not eigenpairs(m)]
    need(len(excluded) == 48, "exhaustive eigenvalue-free matrix count")
    free = [m for m in range(STATES) if rank(m) == N]
    need(len(free) == 168, "GL3 size")
    conjugates = set()
    for g in free:
        inverses = [h for h in free if multiply(g, h) == IDENTITY]
        need(len(inverses) == 1, "unique free inverse")
        h = inverses[0]
        need(multiply(h, g) == IDENTITY, "two-sided free inverse")
        conjugate = multiply(g, multiply(companion, h))
        need(not eigenpairs(conjugate), "free conjugacy preserves obstruction")
        conjugates.add(conjugate)
    need(len(conjugates) == 24, "companion conjugacy orbit")
    return companion, len(excluded), len(conjugates)


def check_reachable_controls(companion):
    # A rootful upper triangular pencil, attained by three legal column factors.
    upper = (1 << 1) | (1 << 5)
    word = (IDENTITY, 0, 0)
    factors = []
    for i in range(N):
        basis = 1 << i
        column = sum(((upper >> (N * j + i)) & 1) << j for j in range(N))
        factor = (IDENTITY ^ outer(basis, basis), outer(basis, basis),
                  outer(column, basis))
        factors.append(factor)
        word = ring_multiply(factor, word)
    need(word == (0, IDENTITY, upper), "rootful pencil word")
    need(bool(eigenpairs(upper)), "eigenvalue hypothesis is discriminating")
    # The x coefficient cannot be dropped from the theorem's hypotheses.
    y_identity = (IDENTITY, 0, 0)
    x_identity = (IDENTITY, 0, 0)
    x_factors, y_factors = [], []
    for i in range(N):
        diagonal = outer(1 << i, 1 << i)
        yf = (IDENTITY ^ diagonal, 0, diagonal)
        xf = (IDENTITY ^ diagonal, diagonal, 0)
        x_factors.append(xf)
        y_factors.append(yf)
        y_identity = ring_multiply(yf, y_identity)
        x_identity = ring_multiply(xf, x_identity)
    only_y = ring_multiply((companion, 0, 0), y_identity)
    collapsed = ring_multiply((IDENTITY ^ companion, 0, 0), x_identity)
    need(only_y == (0, 0, companion), "singular first coefficient control")
    need(collapsed == (0, IDENTITY ^ companion, 0), "identified radicals control")
    comparisons = 0
    for vector in product(range(8), repeat=N):
        expected = tuple((((vector[i] & 1) << 1)
                          ^ ((((vector[i + 1] & 1) << 2) if i < N - 1 else 0)))
                         for i in range(N))
        need(execute(factors, vector) == expected, "independent dirty action")
        constants = sum((entry & 1) << i for i, entry in enumerate(vector))
        only_y_expected = column_times(companion, constants)
        collapsed_expected = column_times(IDENTITY ^ companion, constants)
        need(execute(y_factors + [(companion, 0, 0)], vector)
             == tuple(((only_y_expected >> i) & 1) << 2 for i in range(N)),
             "singular-coefficient dirty action")
        need(execute(x_factors + [(IDENTITY ^ companion, 0, 0)], vector)
             == tuple(((collapsed_expected >> i) & 1) << 1 for i in range(N)),
             "identified-radicals dirty action")
        comparisons += 3
    return comparisons


def execute(factors, vector):
    need(len(factors) <= 4, "bounded control word")
    for factor in factors:
        vector = action(factor, vector)
    return vector


def check_chronology_controls():
    y = 1
    scalar = IDENTITY ^ outer(1, y)
    psi = 1
    coefficient = multiply(scalar, IDENTITY) ^ outer(1, psi)
    need(coefficient == IDENTITY, "radical term restores full coefficient rank")
    need(rank(multiply(scalar, IDENTITY)) == 2, "omitted radical term rejected")
    swap = outer(1, 2) ^ outer(2, 1) ^ outer(4, 4)
    correct = multiply(scalar, swap)
    reversed_order = multiply(swap, scalar)
    need(row_times(y, correct) == 0, "correct chronological annihilator")
    need(row_times(y, reversed_order) != 0, "reversed chronology rejected")
    return 2


def main():
    scalar_pairs, cases, full_rank = check_first_zero_transitions()
    need((scalar_pairs, cases, full_rank) == (196, 802816, 150528),
         "complete bounded transition census")
    companion, excluded, conjugates = check_pencils()
    dirty = check_reachable_controls(companion)
    chronology = check_chronology_controls()
    package = Path(__file__).resolve().parent
    names = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    receipt = {"file_sha256": {name: file_hash(package / name)
                               for name in names},
               "scalar_pairs": scalar_pairs, "coefficient_cases": cases,
               "invertible_cases": full_rank, "excluded_binary_pencils": excluded,
               "companion_conjugates": conjugates, "dirty_action_checks": dirty,
               "chronology_controls": chronology, "claim_type": "scoped proof"}
    print(json.dumps(receipt, sort_keys=True))
    print("PASS_MULTIROLE_RADICAL_PENCIL transitions=802816 full_rank=150528 "
          "excluded_pencils=48 no_new_kappa")


def file_hash(path):
    with path.open("rb") as stream:
        data = stream.read(131073)
    need(len(data) <= 131072, "package source exceeds receipt bound")
    return sha256(data).hexdigest()


if __name__ == "__main__":
    main()
