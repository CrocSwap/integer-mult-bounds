#!/usr/bin/env python3
"""Exact finite corroboration, produced by Nick Petalas. Apache-2.0.

Writes no files. The universal lower bound is cited in PROOF.md.
"""

from fractions import Fraction
from hashlib import sha256
from itertools import combinations_with_replacement, product
from pathlib import Path
import json


SUPPORTS = ((0, 1, 2), (0, 1, 4), (0, 3, 4), (2, 3, 4), (1, 2, 3))
LABELS = (1, 2, 1, 2, 1)
IDENTITY = (0, 1, 2)
SIMPLE = (IDENTITY, (1, 0, 2), (0, 2, 1))
FILES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def reduced(value, prime):
    return value % prime if prime else value


def identity(size):
    require(1 <= size <= 8, "matrix size")
    return tuple(tuple(int(i == j) for j in range(size)) for i in range(size))


def multiply(left, right, prime):
    size = len(left)
    require(size == len(right) and 1 <= size <= 8, "matrix size")
    return tuple(tuple(reduced(sum(left[i][k] * right[k][j] for k in range(size)), prime)
                       for j in range(size)) for i in range(size))


def rank(matrix, prime):
    size = len(matrix)
    require(1 <= size <= 8, "matrix size")
    rows = [[Fraction(v) if not prime else v % prime for v in row] for row in matrix]
    count = 0
    for column in range(size):
        pivot = next((j for j in range(count, size) if rows[j][column]), None)
        if pivot is None:
            continue
        rows[count], rows[pivot] = rows[pivot], rows[count]
        inverse = 1 / rows[count][column] if not prime else pow(rows[count][column], -1, prime)
        rows[count] = [reduced(v * inverse, prime) for v in rows[count]]
        for j in range(size):
            if j != count:
                multiple = rows[j][column]
                rows[j] = [reduced(a - multiple * b, prime)
                           for a, b in zip(rows[j], rows[count])]
        count += 1
    return count


def gauge(size, variant, prime):
    matrix = identity(size)
    inverse = matrix
    edges = [(0, size - 1), (size - 1, 1)]
    edges += [(j, j + 1) for j in range(size - 1)]
    for index, (i, j) in enumerate(edges):
        value = 1 + variant * (index % 2)
        forward = [list(row) for row in identity(size)]
        backward = [list(row) for row in identity(size)]
        forward[i][j] = value
        backward[i][j] = -value
        matrix = multiply(forward, matrix, prime)
        inverse = multiply(inverse, backward, prime)
    require(multiply(matrix, inverse, prime) == identity(size), "gauge inverse")
    return matrix, inverse


def couplings(size, matrix, inverse, prime):
    result = []
    for support in SUPPORTS:
        projector = tuple(tuple(int(i == j and i in support) for j in range(size))
                          for i in range(size))
        coupling = multiply(multiply(matrix, projector, prime), inverse, prime)
        require(rank(coupling, prime) == 3, "rank cap or rank loss")
        require(multiply(coupling, coupling, prime) == coupling, "projector")
        result.append(coupling)
    return tuple(result)


def compose(left, right):
    return tuple(left[right[j]] for j in range(3))


def formal_scalar(matrix):
    size = len(matrix)
    return {(i, j, IDENTITY): matrix[i][j] for i in range(size) for j in range(size)
            if matrix[i][j]}


def formal_gate(label, coupling, prime):
    size = len(coupling)
    result = {(i, i, IDENTITY): 1 for i in range(size)}
    for i, j in product(range(size), repeat=2):
        value = coupling[i][j]
        for group, sign in ((SIMPLE[label], 1), (IDENTITY, -1)):
            key = (i, j, group)
            result[key] = reduced(result.get(key, 0) + sign * value, prime)
    return {key: value for key, value in result.items() if value}


def formal_product(left, right, prime):
    require(len(left) <= 384 and len(right) <= 384, "formal support capacity")
    result = {}
    for (i, k, g), a in left.items():
        for (other, j, h), b in right.items():
            if other == k:
                key = (i, j, compose(g, h))
                result[key] = reduced(result.get(key, 0) + a * b, prime)
    return {key: value for key, value in result.items() if value}


def formal_endpoint(size, matrix, inverse, gates, prime, omit=-1, flip=-1):
    result = formal_scalar(matrix)
    for index in range(5):
        if index != omit:
            label = 3 - LABELS[index] if index == flip else LABELS[index]
            result = formal_product(formal_gate(label, gates[index], prime), result, prime)
    return formal_product(formal_scalar(inverse), result, prime)


def target(size):
    longest = compose(compose(SIMPLE[1], SIMPLE[2]), SIMPLE[1])
    return {(i, i, longest if i < 5 else IDENTITY): 1 for i in range(size)}


def binary_product(left, right):
    a, b, c, d = left
    e, f, g, h = right
    return ((a * e + b * g) % 2, (a * f + b * h) % 2,
            (c * e + d * g) % 2, (c * f + d * h) % 2)


def regular_scalar(matrix, vector, prime):
    size = len(matrix)
    return [[reduced(sum(matrix[i][j] * vector[j][g] for j in range(size)), prime)
             for g in range(6)] for i in range(size)]


def regular_check(size, matrix, inverse, gates, prime):
    # Separate GL2(F2) address realization, not the permutation table.
    group = tuple(x for x in product(range(2), repeat=4) if (x[0] * x[3] - x[1] * x[2]) % 2)
    generators = ((1, 0, 0, 1), (1, 1, 0, 1), (1, 0, 1, 1))
    swap = (0, 1, 1, 0)
    require(len(group) == 6, "regular group order")
    for role, address in product(range(size), range(6)):
        initial = [[int(i == role and g == address) for g in range(6)] for i in range(size)]
        state = regular_scalar(matrix, initial, prime)
        for label, coupling in zip(LABELS, gates):
            coupled = regular_scalar(coupling, state, prime)
            next_state = [row.copy() for row in state]
            for i, g in product(range(size), range(6)):
                moved = group.index(binary_product(generators[label], group[g]))
                next_state[i][g] -= coupled[i][g]
                next_state[i][moved] += coupled[i][g]
            state = [[reduced(v, prime) for v in row] for row in next_state]
        state = regular_scalar(inverse, state, prime)
        expected = [row.copy() for row in initial]
        if role < 5:
            expected[role][address] = 0
            expected[role][group.index(binary_product(swap, group[address]))] = 1
        require(state == expected, "regular full endpoint")
    return size * 6


def price_checks():
    prices = []
    for slopes in combinations_with_replacement(range(5), 3):
        a, b, c = reversed(slopes)
        prices.append((Fraction(a), Fraction(a + b), Fraction(a + b + c)))
    prices.append((Fraction(1, 2), Fraction(2, 3), Fraction(3, 4)))
    profiles = tuple(q for q in product(range(18), range(9), range(6))
                     if 15 <= q[0] + 2 * q[1] + 3 * q[2] <= 17)
    strict = 0
    for c1, c2, c3 in prices:
        optimum = min(q1 * c1 + q2 * c2 + q3 * c3 for q1, q2, q3 in profiles)
        require(optimum == 5 * c3, "packed tariff")
        require(3 * c2 - 2 * c3 >= 0, "batch saving")
        strict += int(3 * c2 > 2 * c3)
    require(5 * prices[-1][2] == Fraction(15, 4), "rational optimum")
    require(3 * prices[-1][1] + 3 * prices[-1][2] == Fraction(17, 4), "rational baseline")
    return {"prices": len(prices), "rank_profiles": len(profiles),
            "profile_comparisons": len(prices) * len(profiles), "strict_savings": strict}


def verify():
    endpoints = columns = omissions = flips = dirty_coupled = 0
    for prime, size, variant in product((0, 2, 3, 5), (5, 6, 8), range(2)):
        matrix, inverse = gauge(size, variant, prime)
        gates = couplings(size, matrix, inverse, prime)
        require(formal_endpoint(size, matrix, inverse, gates, prime) == target(size), "formal endpoint")
        columns += regular_check(size, matrix, inverse, gates, prime)
        endpoints += 1
        for gate in gates:
            dirty_coupled += int(any(gate[i][j] for i, j in product(range(size), repeat=2)
                                     if (i < 5) != (j < 5)))
        for index in range(5):
            require(formal_endpoint(size, matrix, inverse, gates, prime, omit=index) != target(size),
                    "omitted-call control")
            require(formal_endpoint(size, matrix, inverse, gates, prime, flip=index) != target(size),
                    "label-flip control")
            omissions += 1
            flips += 1
    require(dirty_coupled > 0, "dirty coupling coverage")
    words = tuple(tuple(LABELS[j] for j in range(5) if i in SUPPORTS[j]) for i in range(5))
    require(words == ((1, 2, 1),) * 4 + ((2, 1, 2),), "literal role words")
    result = {"formal_endpoints": endpoints, "paid_calls": 5 * endpoints,
              "regular_basis_columns": columns, "dirty_coupled_calls": dirty_coupled,
              "omission_rejections": omissions, "label_flip_rejections": flips,
              "prices": price_checks(), "rank_profile": [3] * 5,
              "formal_optimum": "5 f(3)", "claim_type": "scoped proof with finite corroboration"}
    package = Path(__file__).resolve().parent
    result["source_sha256"] = {name: sha256((package / name).read_bytes()).hexdigest() for name in FILES}
    result["status"] = "PASS_A2_FIVE_TARGET_CAP_THREE"
    return result


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True, indent=2))
