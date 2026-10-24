#!/usr/bin/env python3
"""Check one integral four-plane COPY certificate. Apache-2.0."""
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import combinations, product
import json
from pathlib import Path


LABELS = (11, 19, 35, 67, 296, 392, 400, 416)
QUADRUPLE = (0, 1, 44, 49)
FILES = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")


class CheckFailure(ValueError):
    """A certificate or semantic control failed."""


def need(condition, message):
    if not condition:
        raise CheckFailure(message)


def identity(n):
    need(1 <= n <= 16, "identity dimension")
    return [[int(i == j) for j in range(n)] for i in range(n)]


def pairing():
    return [[(a & b).bit_count() % 2 for b in LABELS] for a in LABELS]


def indices(mask):
    need(type(mask) is int and 1 <= mask < 16, "nonempty plane mask")
    return [i for i in range(8) if mask >> (i // 2) & 1]


def rectangle(matrix, rows, columns):
    return [[matrix[i][j] for j in columns] for i in rows]


def binary_rank(matrix):
    basis = [0] * 8
    for row in matrix:
        value = sum(x << j for j, x in enumerate(row))
        for j in range(7, -1, -1):
            if not value >> j & 1:
                continue
            if basis[j]:
                value ^= basis[j]
            else:
                basis[j] = value
                break
    return sum(bool(x) for x in basis)


def rational_rank(matrix):
    work = [[Fraction(x) for x in row] for row in matrix]
    rank = 0
    for column in range(len(work[0])):
        pivot = next((i for i in range(rank, len(work)) if work[i][column]), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        value = work[rank][column]
        work[rank] = [x / value for x in work[rank]]
        for i in range(rank + 1, len(work)):
            value = work[i][column]
            work[i] = [x - value * y for x, y in zip(work[i], work[rank])]
        rank += 1
        if rank == len(work):
            break
    return rank


def determinant(matrix):
    """Integer Bareiss elimination, independent of the rational rank engine."""
    work = [row[:] for row in matrix]
    n = len(work)
    need(1 <= n <= 8 and all(len(row) == n for row in work), "minor shape")
    previous, sign = 1, 1
    for column in range(n - 1):
        pivot = next((i for i in range(column, n) if work[i][column]), None)
        if pivot is None:
            return 0
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            sign = -sign
        value = work[column][column]
        for i in range(column + 1, n):
            for j in range(column + 1, n):
                numerator = work[i][j] * value - work[i][column] * work[column][j]
                need(numerator % previous == 0, "exact Bareiss division")
                work[i][j] = numerator // previous
            work[i][column] = 0
        previous = value
    return sign * work[-1][-1]


def upper_minors(matrix, rank):
    """Every (rank+1)-minor vanishes in Z, hence in every field."""
    count = 0
    for rows in combinations(range(len(matrix)), rank + 1):
        for columns in combinations(range(len(matrix[0])), rank + 1):
            need(determinant(rectangle(matrix, rows, columns)) == 0,
                 "nonzero integer minor exceeds the binary tariff")
            count += 1
    return count


def certificate(gram):
    for plane in range(4):
        local = (2 * plane, 2 * plane + 1)
        need(rectangle(gram, local, local) == identity(2), "Gram-I2 plane")
    tariffs, histogram, minors = {}, Counter(), 0
    stream = hashlib.sha256()
    for source, reader in product(range(1, 16), repeat=2):
        block = rectangle(gram, indices(source), indices(reader))
        tariff = binary_rank(block)
        need(rational_rank(block) == tariff, "rational/binary rank equality")
        minors += upper_minors(block, tariff)
        tariffs[source, reader] = tariff
        histogram[tariff] += 1
        stream.update(bytes((source, reader, tariff)))
    need(len(tariffs) == 225, "all ordered closure pairs")
    return tariffs, dict(sorted(histogram.items())), minors, stream.hexdigest()


def outer(left, right):
    return [[a * b for b in right] for a in left]


def shadow(matrix, gram):
    """Phi(M)[(i,a),(j,b)] = M[i,j] G[(plane(i),a),(plane(j),b)]."""
    return [[matrix[i][j] * gram[2 * (i // 2) + a][2 * (j // 2) + b]
             for j in range(8) for b in range(2)]
            for i in range(8) for a in range(2)]


def rank_three(matrix):
    work = [[x % 3 for x in row] for row in matrix]
    rank = 0
    for column in range(len(work[0])):
        pivot = next((i for i in range(rank, len(work)) if work[i][column]), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = pow(work[rank][column], -1, 3)
        work[rank] = [x * inverse % 3 for x in work[rank]]
        for i in range(rank + 1, len(work)):
            value = work[i][column]
            work[i] = [(x - value * y) % 3 for x, y in zip(work[i], work[rank])]
        rank += 1
        if rank == len(work):
            break
    return rank


def vectors():
    out = []
    for choices in product(range(3), repeat=4):
        if not any(choices):
            continue
        vector = [0] * 8
        mask = 0
        for plane, choice in enumerate(choices):
            if choice:
                vector[2 * plane + choice - 1] = 1
                mask |= 1 << plane
        out.append((vector, mask))
    need(len(out) == 80, "one-coordinate-per-touched-plane domain")
    return out


def atom_checks(gram, tariffs):
    cases, stream = 0, hashlib.sha256()
    choices = vectors()
    for (left, source), (right, reader) in product(choices, repeat=2):
        lifted = shadow(outer(left, right), gram)
        need(rank_three(lifted) <= tariffs[source, reader], "literal atom bound")
        stream.update(bytes(x % 3 for row in lifted for x in row))
        cases += 1
    return cases, stream.hexdigest()


def total(matrices, size):
    need(len(matrices) <= 10, "finite endpoint fixture")
    return [[sum(matrix[i][j] for matrix in matrices) for j in range(size)]
            for i in range(size)]


def endpoints(gram, tariffs):
    coordinate = [outer(row, row) for row in identity(8)]
    need(total(coordinate, 8) == identity(8), "coordinate identity endpoint")
    need(sum(tariffs[1 << (i // 2), 1 << (i // 2)] for i in range(8)) == 16,
         "attaining coordinate tariff")
    need(shadow(identity(8), gram) == identity(16), "full-rank identity shadow")
    dense = outer([1] * 8, [1, -1] * 4)
    negative = [[-x for x in row] for row in dense]
    overcomplete = coordinate + [dense, negative]
    need(total(overcomplete, 8) == identity(8), "ten-term cancellation endpoint")
    need(total([shadow(m, gram) for m in overcomplete], 16) == identity(16),
         "shadow linearity includes cancelling terms")
    return coordinate


def rejects(check):
    try:
        check()
    except CheckFailure:
        return
    raise CheckFailure("semantic mutation was accepted")


def controls(gram, coordinate):
    rejects(lambda: indices(0))
    rejects(lambda: indices(True))
    rejects(lambda: need(total(coordinate[:-1], 8) == identity(8), "omitted term"))
    rejects(lambda: need(rank_three(shadow(coordinate[0], gram)) <= 1,
                         "underpriced self-plane COPY"))
    nonlift = [[1, 1, 0], [1, 0, 1], [0, 1, 1]]
    need(binary_rank(nonlift) == 2 and rational_rank(nonlift) == 3,
         "characteristic-sensitive rank control")
    rejects(lambda: upper_minors(nonlift, 2))
    wrong = [row[:] for row in gram]
    wrong[0][0] = 0
    rejects(lambda: need(shadow(identity(8), wrong) == identity(16),
                         "missing diagonal normalization"))
    free = outer(identity(8)[0], identity(8)[2])
    need(rank_three(free) == 1 and rank_three(shadow(free, gram)) == 0,
         "free cross atom must vanish in the shadow")
    return 6


def main():
    gram = pairing()
    tariffs, histogram, minors, tariff_digest = certificate(gram)
    atom_cases, atom_digest = atom_checks(gram, tariffs)
    coordinate = endpoints(gram, tariffs)
    control_count = controls(gram, coordinate)
    hashes = {}
    for name in FILES:
        with Path(__file__).with_name(name).open("rb") as source:
            data = source.read(1_000_001)
        need(len(data) <= 1_000_000, "bounded package file")
        hashes[name] = hashlib.sha256(data).hexdigest()
    result = {"status": "PASS_FOUR_PLANE_INTEGRAL_SHADOW", "quadruple": QUADRUPLE,
              "closure_pairs": len(tariffs), "rank_histogram": histogram,
              "vanishing_integer_minors": minors, "tariff_sha256": tariff_digest,
              "literal_atoms": atom_cases, "atom_sha256": atom_digest,
              "minimum_mass": 16, "coefficient_fields": "all",
              "rejecting_controls": control_count, "files": hashes}
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
