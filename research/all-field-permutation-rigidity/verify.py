#!/usr/bin/env python3
"""Exact finite corroboration of the written all-field permutation theorem.

Produced by Nick Petalas. Apache-2.0. No files are written.
"""

from fractions import Fraction
from hashlib import sha256
from itertools import permutations, product
import json
from pathlib import Path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def scalar(value, prime):
    return value % prime if prime else Fraction(value)


def identity(size):
    return tuple(tuple(int(i == j) for j in range(size)) for i in range(size))


def plus(left, right, prime, sign=1):
    return tuple(tuple(scalar(a + sign * b, prime) for a, b in zip(x, y, strict=True))
                 for x, y in zip(left, right, strict=True))


def times(left, right, prime):
    size = len(left)
    return tuple(tuple(scalar(sum(left[i][k] * right[k][j] for k in range(size)), prime)
                       for j in range(size)) for i in range(size))


def compose(left, right):
    return tuple(left[j] for j in right)


def inversions(word):
    return sum(word[i] > word[j] for i in range(len(word)) for j in range(i + 1, len(word)))


def adjacent(size):
    result = []
    for i in range(size - 1):
        value = list(range(size))
        value[i], value[i + 1] = value[i + 1], value[i]
        result.append(tuple(value))
    return tuple(result)


def rank(matrix, prime):
    work = [list(row) for row in matrix]
    height, width = len(work), len(work[0])
    pivot = 0
    for column in range(width):
        selected = next((i for i in range(pivot, height) if work[i][column]), None)
        if selected is None:
            continue
        work[pivot], work[selected] = work[selected], work[pivot]
        value = work[pivot][column]
        inverse = pow(value, -1, prime) if prime else 1 / Fraction(value)
        work[pivot] = [scalar(x * inverse, prime) for x in work[pivot]]
        for row in range(pivot + 1, height):
            coefficient = work[row][column]
            if coefficient:
                work[row] = [scalar(x - coefficient * y, prime)
                             for x, y in zip(work[row], work[pivot], strict=True)]
        pivot += 1
        if pivot == height:
            break
    return pivot


def projectors(size, prime):
    need(size in (2, 3) and prime == 3, "unsupported exhaustive projector domain")
    vectors = tuple(product(range(prime), repeat=size))
    result = set()
    for u in vectors:
        for v in vectors:
            if sum(a * b for a, b in zip(u, v, strict=True)) % prime == 1:
                result.add(tuple(tuple(a * b % prime for b in v) for a in u))
    for matrix in result:
        need(times(matrix, matrix, prime) == matrix, "projector idempotence")
        need(rank(matrix, prime) == 1, "projector rank")
    return tuple(sorted(result))


def accumulate(coefficients, label, matrix, prime):
    size = len(matrix)
    zero = tuple((0,) * size for _ in range(size))
    value = plus(coefficients.get(label, zero), matrix, prime)
    if any(any(row) for row in value):
        coefficients[label] = value
    else:
        coefficients.pop(label, None)


def formal_word(labels, couplings, prime):
    need(1 <= len(labels) <= 8 and len(labels) == len(couplings), "word bounds")
    size = len(couplings[0])
    unit = identity(size)
    result = {tuple(range(len(labels[0]))): unit}
    for label, coupling in zip(labels, couplings, strict=True):
        updated = {}
        complement = plus(unit, coupling, prime, -1)
        for old, matrix in result.items():
            accumulate(updated, old, times(matrix, complement, prime), prime)
            accumulate(updated, compose(old, label), times(matrix, coupling, prime), prime)
        result = updated
    return result


def target(word, projector, prime):
    result = {}
    accumulate(result, tuple(range(len(word))), plus(identity(len(projector)), projector, prime, -1), prime)
    accumulate(result, word, projector, prime)
    return result


def crossing(coefficients, size, prime):
    first = next(iter(coefficients))
    positive = tuple((i, j) for i in range(len(first)) for j in range(i + 1, len(first)))
    negative = tuple((j, i) for i, j in positive)
    index = {pair: j for j, pair in enumerate(negative)}
    width = len(positive)
    result = [[0] * (size * width) for _ in range(size * width)]
    for word, matrix in coefficients.items():
        for column, (a, b) in enumerate(positive):
            row = index.get((word[a], word[b]))
            if row is not None:
                for i in range(size):
                    for j in range(size):
                        result[i * width + row][j * width + column] += matrix[i][j]
    return rank(tuple(tuple(scalar(x, prime) for x in row) for row in result), prime)


def peel(word, endpoint, coupling, label, prime):
    size = len(coupling)
    unit = identity(size)
    ec = plus(unit, endpoint, prime, -1)
    nc = plus(unit, coupling, prime, -1)
    result = {}
    for group, matrix in (
        (tuple(range(len(word))), times(ec, nc, prime)),
        (label, times(ec, coupling, prime)),
        (word, times(endpoint, nc, prime)),
        (compose(word, label), times(endpoint, coupling, prime)),
    ):
        accumulate(result, group, matrix, prime)
    return crossing(result, size, prime)


def check_peels():
    counts = {"peels": 0, "decreasing_peels": 0}
    words = tuple(permutations(range(4)))
    for size in (2, 3):
        pool = projectors(size, 3)
        need(len(pool) == (12 if size == 2 else 117), "projector domain size")
        endpoints = pool if size == 2 else (tuple(tuple(int(i == j == 0) for j in range(size))
                                                   for i in range(size)),)
        counts[f"projectors_F3_r{size}"] = len(pool)
        for endpoint in endpoints:
            for word in words:
                length = inversions(word)
                need(crossing(target(word, endpoint, 3), size, 3) == length, "target cut")
                for coupling in pool:
                    for label in adjacent(4):
                        after = peel(word, endpoint, coupling, label, 3)
                        expected = coupling == endpoint and inversions(compose(word, label)) == length - 1
                        need((after == length - 1) == expected, "one-step rigidity")
                        need(abs(after - length) <= 1, "one-step distance bound")
                        counts["peels"] += 1
                        counts["decreasing_peels"] += int(after == length - 1)
    return counts


def reduced_word(word):
    value = word
    peels = []
    for _ in range(inversions(word)):
        label = next(label for label in adjacent(len(word))
                     if inversions(compose(value, label)) == inversions(value) - 1)
        peels.append(label)
        value = compose(value, label)
    need(value == tuple(range(len(word))), "sorting termination")
    return tuple(reversed(peels))


def regular_column(labels, couplings, prime, initial):
    state = {initial: scalar(1, prime)}
    for label, coupling in reversed(tuple(zip(labels, couplings, strict=True))):
        updated = dict(state)
        for (column, word), value in state.items():
            for row in range(len(coupling)):
                delta = coupling[row][column] * value
                same, shifted = (row, word), (row, compose(label, word))
                updated[same] = scalar(updated.get(same, 0) - delta, prime)
                updated[shifted] = scalar(updated.get(shifted, 0) + delta, prime)
        state = {key: value for key, value in updated.items() if value}
    return state


def check_regular(labels, couplings, word, endpoint, prime):
    columns = 0
    for group in permutations(range(len(word))):
        for column in range(len(endpoint)):
            expected = regular_column((word,), (endpoint,), prime, (column, group))
            observed = regular_column(labels, couplings, prime, (column, group))
            need(observed == expected, "faithful regular endpoint")
            columns += 1
    return columns


def check_constructions():
    rational = tuple(tuple(Fraction(a * b, 3) for b in (1, 1, 0)) for a in (1, 2, 1))
    need(times(rational, rational, 0) == rational and rank(rational, 0) == 1, "rational projector")
    columns, endpoints = 0, 0
    for prime, endpoint in ((0, rational), (3, projectors(2, 3)[4])):
        for word in permutations(range(4)):
            if not inversions(word):
                continue
            labels = reduced_word(word)
            couplings = (endpoint,) * len(labels)
            need(formal_word(labels, couplings, prime) == target(word, endpoint, prime), "formal endpoint")
            columns += check_regular(labels, couplings, word, endpoint, prime)
            endpoints += 1
    return {"complete_endpoints": endpoints, "regular_basis_columns": columns}


def check_controls():
    word = (2, 3, 0, 1)
    endpoint = ((1, 0), (0, 0))
    other = ((0, 0), (0, 1))
    mixed = ((1, 1), (0, 0))
    labels = reduced_word(word)
    need(len(labels) == 4, "first working example length")
    wanted = target(word, endpoint, 3)
    omissions = replacements = 0
    for i in range(len(labels)):
        short = labels[:i] + labels[i + 1:]
        need(formal_word(short, (endpoint,) * len(short), 3) != wanted, "omission control")
        changed = tuple(other if j == i else endpoint for j in range(len(labels)))
        need(formal_word(labels, changed, 3) != wanted, "wrong-projector control")
        omissions += 1
        replacements += 1
    extended = (adjacent(4)[0],) * 2 + labels
    couplings = (mixed, mixed) + (endpoint,) * len(labels)
    need(formal_word(extended, couplings, 3) == wanted, "nonminimal mixed-word boundary")
    need(mixed != endpoint, "nonminimal word really uses a spectator")
    need(formal_word((word,), (endpoint,), 3) == wanted, "nonsimple-label boundary")
    need(formal_word(labels, (other,) * len(labels), 3) != wanted, "full-endpoint boundary")
    return {"omission_controls": omissions, "projector_replacements": replacements,
            "boundary_controls": 3}


def main():
    counts = check_peels()
    counts.update(check_constructions())
    counts.update(check_controls())
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {name: sha256((package / name).read_bytes()).hexdigest() for name in names}
    print(json.dumps({"status": "PASS_ALL_FIELD_PERMUTATION_RIGIDITY", "counts": counts,
                      "claim_type": "scoped written proof with finite corroboration",
                      "source_sha256": hashes, "new_kappa": False}, sort_keys=True))


if __name__ == "__main__":
    main()
