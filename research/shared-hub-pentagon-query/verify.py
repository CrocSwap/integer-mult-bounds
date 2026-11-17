#!/usr/bin/env python3
"""Exact conformance for the shared-hub two-coordinate query theorem.

Produced by Nick Petalas. Apache-2.0.
The universal lower bound is a written proof, not a finite matrix search.
"""

import hashlib
import itertools
import json
import platform
from fractions import Fraction
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def edges():
    return ((0, 1), (1, 2), (2, 3), (3, 4), (4, 0),
            (0, 5), (5, 6), (6, 7), (7, 8), (8, 0))


def channels():
    # Coordinate (vertex, local-coordinate) is 2*vertex + local-coordinate.
    return ((0, 2), (3, 4), (5, 6), (7, 8), (9, 1),
            (10, 12), (11, 13), (14, 16), (15, 17))


def allowed(i, j):
    return any({i, j} == {u, v} for u, v in edges())


def matmul(a, b, prime):
    require(a and b and len(a[0]) == len(b), "matrix shape")
    rows, inner, cols = len(a), len(b), len(b[0])
    require(max(rows, inner, cols) <= 18, "matrix capacity")
    require(all(len(row) == inner for row in a), "ragged left matrix")
    require(all(len(row) == cols for row in b), "ragged right matrix")
    result = [[sum(a[i][k] * b[k][j] for k in range(inner))
               for j in range(cols)] for i in range(rows)]
    return [[x % prime for x in row] for row in result] if prime else result


def rank(matrix, prime):
    require(matrix and len(matrix) <= 18, "rank capacity")
    cols = len(matrix[0])
    require(cols <= 18 and all(len(row) == cols for row in matrix), "rank shape")
    work = [[x % prime if prime else Fraction(x) for x in row] for row in matrix]
    pivot = 0
    for col in range(cols):
        found = next((i for i in range(pivot, len(work)) if work[i][col]), None)
        if found is None:
            continue
        work[pivot], work[found] = work[found], work[pivot]
        inverse = pow(work[pivot][col], -1, prime) if prime else 1 / work[pivot][col]
        work[pivot] = [x * inverse for x in work[pivot]]
        if prime:
            work[pivot] = [x % prime for x in work[pivot]]
        for i in range(pivot + 1, len(work)):
            scale = work[i][col]
            work[i] = [x - scale * y for x, y in zip(work[i], work[pivot])]
            if prime:
                work[i] = [x % prime for x in work[i]]
        pivot += 1
        if pivot == len(work):
            break
    return pivot


def check_fitting(matrix, prime):
    require(len(matrix) == 18 and all(len(row) == 18 for row in matrix), "fit shape")
    for i in range(18):
        for j in range(18):
            value = matrix[i][j] % prime if prime else matrix[i][j]
            if i // 2 == j // 2:
                require(value == int(i == j), "diagonal block")
            elif not allowed(i // 2, j // 2):
                require(value == 0, "forbidden block")


def base_factors():
    pairs = channels()
    require(sorted(itertools.chain.from_iterable(pairs)) == list(range(18)),
            "coordinate partition")
    require(all(allowed(i // 2, j // 2) for i, j in pairs), "channel edge")
    encoder = [[int(i in pair) for i in range(18)] for pair in pairs]
    decoder = [list(row) for row in zip(*encoder)]
    return decoder, encoder


def inverse2(a, prime):
    determinant = a[0][0] * a[1][1] - a[0][1] * a[1][0]
    require(determinant % prime != 0 if prime else determinant != 0, "singular basis")
    scale = pow(determinant, -1, prime) if prime else Fraction(1, determinant)
    result = [[a[1][1] * scale, -a[0][1] * scale],
              [-a[1][0] * scale, a[0][0] * scale]]
    return [[x % prime for x in row] for row in result] if prime else result


def all_gl2(prime):
    result = []
    for values in itertools.product(range(prime), repeat=4):
        a, b, c, d = values
        if (a * d - b * c) % prime:
            result.append([[a, b], [c, d]])
    require(len(result) == (prime * prime - 1) * (prime * prime - prime), "GL2 size")
    return result


def basis_profile(index, prime, binary_bases):
    result = []
    for vertex in range(9):
        if prime == 2:
            digit = index // (6 ** (vertex // 2)) % 6 if vertex in (0, 2, 4) else 0
            result.append(binary_bases[digit])
        else:
            a = (index + 3 * vertex) % 7 - 3
            b = (2 * index + vertex) % 5 - 2
            result.append([[1, a], [b, 1 + a * b]])
    return result


def transformed_factors(profile, prime):
    a, b = base_factors()
    left = [[0] * 18 for _ in range(18)]
    right = [[0] * 18 for _ in range(18)]
    for vertex, basis in enumerate(profile):
        inverse = inverse2(basis, prime)
        for i in range(2):
            for j in range(2):
                left[2 * vertex + i][2 * vertex + j] = basis[i][j]
                right[2 * vertex + i][2 * vertex + j] = inverse[i][j]
    return matmul(left, a, prime), matmul(b, right, prime)


def check_constructions():
    binary_bases = all_gl2(2)
    cases = entries = 0
    noncommuting = asymmetric = False
    for prime in (2, 3, 5, 7, 101, 0):
        for index in range(216 if prime == 2 else 32):
            profile = basis_profile(index, prime, binary_bases)
            a, b = transformed_factors(profile, prime)
            matrix = matmul(a, b, prime)
            check_fitting(matrix, prime)
            require(rank(matrix, prime) == 9, "attaining rank")
            require(rank(a, prime) == rank(b, prime) == 9, "factor rank")
            asymmetric |= any(matrix[i][j] != matrix[j][i]
                              for i in range(18) for j in range(18))
            p = [row[2:4] for row in matrix[0:2]]
            q = [row[8:10] for row in matrix[0:2]]
            noncommuting |= matmul(p, q, prime) != matmul(q, p, prime)
            cases += 1
            entries += 18 * 18
    require(asymmetric and noncommuting, "block generality fixture")
    return {"factorizations": cases, "ordered_entries": entries,
            "asymmetric_fixture": asymmetric, "noncommuting_fixture": noncommuting}


def check_local_lower_steps():
    # Exhaust the local saturated branch in the proof, not all fitting matrices.
    total = 0
    for prime in (2, 3):
        invertibles = all_gl2(prime)
        identity = [[1, 0], [0, 1]]
        zero = [[0, 0], [0, 0]]
        for x in invertibles:
            inverse = inverse2(x, prime)
            for values in itertools.product(range(prime), repeat=4):
                y = [list(values[:2]), list(values[2:])]
                b2 = x + y
                a2 = [inverse[i] + [0, 0] for i in range(2)]
                require(matmul(a2, b2, prime) == identity, "branch left inverse")
                for t in invertibles:
                    b4 = zero + t
                    require(matmul(a2, b4, prime) == zero, "branch nonedge")
                    require(rank(b4, prime) == 2, "saturated terminal")
                    total += 1
                p = y
                require((matmul(p, x, prime) == zero) == (p == zero),
                        "hub coefficient forced to zero")
    require(total == 187200, "local branch count")
    return total


def check_literal_binary():
    partner = [0] * 18
    query_for = [0] * 18
    for query, (i, j) in enumerate(channels()):
        partner[i], partner[j] = j, i
        query_for[i] = query_for[j] = query
    comparisons = 0
    for inputs in range(1 << 18):
        responses = [((inputs >> i) ^ (inputs >> j)) & 1 for i, j in channels()]
        for coordinate in range(18):
            recovered = responses[query_for[coordinate]] ^ ((inputs >> partner[coordinate]) & 1)
            require(recovered == ((inputs >> coordinate) & 1), "literal recovery")
            comparisons += 1
    return {"inputs": 1 << 18, "coordinate_recoveries": comparisons}


def check_controls():
    a, b = base_factors()
    rejected = 0
    for omitted in range(9):
        smaller_a = [row[:omitted] + row[omitted + 1:] for row in a]
        smaller_b = b[:omitted] + b[omitted + 1:]
        try:
            check_fitting(matmul(smaller_a, smaller_b, 2), 2)
        except ValueError:
            rejected += 1
    for row, col in ((0, 0), (0, 1), (0, 4)):
        matrix = matmul(a, b, 2)
        matrix[row][col] ^= 1
        try:
            check_fitting(matrix, 2)
        except ValueError:
            rejected += 1
    require(rejected == 12, "rejection controls")
    return {"rejected_mutants": rejected, "relaxed_mask_rank": check_relaxed_mask()}


def check_relaxed_mask():
    # Adding only the edge 0--2 permits two triangle channels and six edge channels.
    groups = ((0, 2, 4), (1, 3, 5), (6, 8), (7, 9),
              (10, 12), (11, 13), (14, 16), (15, 17))
    encoder = [[int(i in group) for i in range(18)] for group in groups]
    matrix = matmul([list(row) for row in zip(*encoder)], encoder, 2)
    for i in range(18):
        for j in range(18):
            if i // 2 == j // 2:
                require(matrix[i][j] == int(i == j), "relaxed diagonal")
            elif not allowed(i // 2, j // 2) and {i // 2, j // 2} != {0, 2}:
                require(matrix[i][j] == 0, "relaxed zero mask")
    require(rank(matrix, 2) == 8, "relaxed-mask rank")
    try:
        check_fitting(matrix, 2)
    except ValueError:
        return 8
    raise ValueError("relaxed mask accepted by original contract")


def main():
    result = {"status": "PASS_SHARED_HUB_PENTAGON_QUERY", "claim_type": "scoped-proof",
              "minimum_query_dimension": 9, "payload_width": 2,
              "construction": check_constructions(),
              "local_saturated_branches": check_local_lower_steps(),
              "literal_binary": check_literal_binary(), "controls": check_controls(),
              "python": platform.python_version()}
    package = Path(__file__).resolve().parent
    names = {"README.md", "PROOF.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py"}
    require({p.name for p in package.iterdir() if p.is_file()} == names,
            "package inventory")
    hashes = {}
    for path in sorted(package.iterdir()):
        if path.is_file():
            require(path.stat().st_size <= 1_048_576, "package file capacity")
            hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    result["sha256"] = hashes
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
