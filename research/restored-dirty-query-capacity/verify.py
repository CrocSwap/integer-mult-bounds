#!/usr/bin/env python3
"""Exact checks for projection endpoints with restored arbitrary dirty helpers."""

import hashlib
import itertools
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def eye(n):
    require(0 <= n <= 64, "matrix dimension outside fixture bound")
    return tuple(1 << i for i in range(n))


def add(a, b):
    require(len(a) == len(b), "row count mismatch")
    return tuple(x ^ y for x, y in zip(a, b))


def mul(a, b):
    require(len(a) <= 64 and len(b) <= 64, "matrix dimension limit")
    require(all(0 <= row < (1 << len(b)) for row in a), "bad inner dimension")
    result = []
    for row in a:
        value = 0
        for j, other in enumerate(b):
            if (row >> j) & 1:
                value ^= other
        result.append(value)
    return tuple(result)


def factor(matrix):
    """Return a full-rank factorization U V of a binary rectangular matrix."""
    require(len(matrix) <= 64, "too many rows")
    require(all(0 <= row < (1 << 64) for row in matrix), "row width limit")
    pivots = {}
    for row in matrix:
        value = row
        for pivot in sorted(pivots, reverse=True):
            if (value >> pivot) & 1:
                value ^= pivots[pivot]
        if value:
            pivots[value.bit_length() - 1] = value
    basis = tuple(pivots[p] for p in sorted(pivots, reverse=True))
    coordinates = []
    for row in matrix:
        value, code = row, 0
        for j, vector in enumerate(basis):
            if (value >> (vector.bit_length() - 1)) & 1:
                value ^= vector
                code ^= 1 << j
        require(value == 0, "row not in computed span")
        coordinates.append(code)
    u = tuple(coordinates)
    require(mul(u, basis) == matrix, "rank factorization residual")
    return u, basis


def rank(matrix):
    return len(factor(matrix)[1])


def total(matrices, rows):
    result = (0,) * rows
    for matrix in matrices:
        result = add(result, matrix)
    return result


def complement_data(terms, projection):
    """Check the new projection Gram lemma, including its nonidempotent case."""
    size = len(projection)
    require(3 <= len(terms) <= 8 and size <= 4, "fixture bound exceeded")
    require(mul(projection, projection) == projection, "endpoint is not a projection")
    require(total(terms, size) == projection, "wrong complete dirty endpoint")
    u_rows, v_rows, widths = [0] * size, [], []
    for term in terms:
        require(mul(term, term) == (0,) * size, "paid term is not square-zero")
        u, v = factor(term)
        width = len(v)
        require(mul(v, u) == (0,) * width, "factor is not square-zero")
        for j in range(size):
            u_rows[j] |= u[j] << len(v_rows)
        v_rows.extend(v)
        widths.append(width)
    u, v = tuple(u_rows), tuple(v_rows)
    s, n = len(v), rank(projection)
    require(mul(u, v) == projection, "stacked factorization residual")
    x = mul(v, u)
    y = add(eye(s), x)
    require(mul(mul(x, x), x) == mul(x, x), "X cubed differs from X squared")
    require(mul(mul(y, y), y) == y, "Y cubed differs from Y")
    d = s - n
    require(rank(y) == d, "wrong complement dimension")
    a, b = factor(y)
    c = mul(b, a)
    require(mul(c, c) == eye(d), "complement core is not an involution")
    check_blocks(a, b, c, widths, n)
    return c != eye(d), s


def check_blocks(a, b, c, widths, n):
    d, offset, pieces = len(b), 0, []
    for width in widths:
        ai = a[offset:offset + width]
        bi = tuple((row >> offset) & ((1 << width) - 1) for row in b)
        require(mul(ai, bi) == eye(width), "lost diagonal identity block")
        e = mul(bi, ai)
        require(mul(e, e) == e and rank(e) == width, "bad block idempotent")
        pieces.append(e)
        offset += width
    require(total(pieces, d) == c, "block sum residual")
    require(all(width <= d for width in widths), "elementary rank bound")
    k, s = len(widths), sum(widths)
    if k % 2 == 0:
        complements = tuple(add(eye(d), e) for e in pieces)
        require(total(complements, d) == c, "even-call complement sum")
        require(d <= sum(d - width for width in widths), "even-call rank bound")
    m = 2 * ((k - 1) // 2)
    require(n % 2 == 0, "odd projection rank")
    require(s >= n + (n + m - 1) // m, "claimed helper-independent floor")


def square_zeros(size, cap):
    require(1 <= size <= 4 and 0 <= cap <= size // 2, "census bound exceeded")
    result = []
    mask = (1 << size) - 1
    for packed in range(1 << (size * size)):
        matrix = tuple((packed >> (size * j)) & mask for j in range(size))
        if mul(matrix, matrix) == (0,) * size:
            cost = rank(matrix)
            if cost <= cap:
                result.append((matrix, cost))
    return tuple(result)


def apply_matrix(matrix, vector):
    return sum(((row & vector).bit_count() & 1) << j for j, row in enumerate(matrix))


def literal_word(terms, projection):
    """Execute free I+R and paid I+Q R, with Q=1+epsilon, on every dirty input."""
    size = len(projection)
    for value in range(1 << size):
        constant, epsilon = value, 0
        for term in terms:
            free = add(eye(size), term)
            constant = apply_matrix(free, constant)
            epsilon = apply_matrix(free, epsilon)
            old = constant
            constant = apply_matrix(free, old)
            epsilon = apply_matrix(free, epsilon) ^ apply_matrix(term, old)
        require(constant == value, "constant endpoint differs")
        require(epsilon == apply_matrix(projection, value), "dirty epsilon endpoint differs")


def complete_three_coordinate_fixture():
    atoms = square_zeros(3, 1)
    projection = (1, 2, 0)
    pairs = {}
    for first, second in itertools.product(atoms, repeat=2):
        pairs.setdefault(add(first[0], second[0]), []).append((first[0], second[0]))
    count, defects, executions, witness, short = 0, 0, 0, None, None
    for value, left_pairs in pairs.items():
        for left in left_pairs:
            for right in pairs.get(add(value, projection), ()):
                terms = left + right
                defect, cost = complement_data(terms, projection)
                literal_word(terms, projection)
                count += 1
                defects += int(defect)
                executions += 8
                if defect and witness is None:
                    witness = {"terms": terms, "projection": projection, "total_rank": cost}
                if short is None and (0, 0, 0) in terms:
                    short = tuple(term for term in terms if term != (0, 0, 0))
    require(witness is not None, "nilpotent-defect case was not exercised")
    require(short is not None and len(short) == 3, "missing three-call fixture")
    for k in range(3, 9):
        complement_data(short + ((0, 0, 0),) * (k - 3), projection)
    packed_atoms = tuple(sum(row << (3 * j) for j, row in enumerate(a)) for a, _ in atoms)
    raw_count = sum(a ^ b ^ c ^ d == 17
                    for a, b, c, d in itertools.product(packed_atoms, repeat=4))
    require(count == raw_count == 648 and defects == 288, "complete census mismatch")
    return {"words": count, "nonidentity_cores": defects,
            "dirty_input_executions": executions, "defect_witness": witness,
            "raw_four_tuple_candidates": len(atoms) ** 4, "call_counts_checked": list(range(3, 9))}


def four_coordinate_minima():
    projection = (1, 2, 0, 0)
    minima = {}
    for cap in (1, 2):
        atoms = square_zeros(4, cap)
        pair_cost = {}
        for (first, a), (second, b) in itertools.product(atoms, repeat=2):
            key = add(first, second)
            pair_cost[key] = min(pair_cost.get(key, 65), a + b)
        best = min(cost + pair_cost[add(value, projection)]
                   for value, cost in pair_cost.items()
                   if add(value, projection) in pair_cost)
        require(best == 3, "four-coordinate dirty minimum changed")
        minima[str(cap)] = {"minimum_total_rank": best,
                            "pair_sums": len(pair_cost), "ordered_pairs": len(atoms) ** 2}
    return minima


def rejecting_controls():
    projection = (1, 2, 0)
    valid = ((0, 6, 6), (6, 6, 6), (0, 5, 0), (7, 7, 0))
    damaged = (add(valid[0], (1, 0, 0)), add(valid[1], (1, 0, 0))) + valid[2:]
    bad = [
        (damaged, projection, "paid term is not square-zero"),
        (((0, 0, 0),) * 4, projection, "wrong complete dirty endpoint"),
        (((0, 0, 0),) * 4, (2, 0, 0), "endpoint is not a projection"),
    ]
    rejected = 0
    for terms, endpoint, message in bad:
        try:
            complement_data(terms, endpoint)
        except ValueError as error:
            require(str(error) == message, "wrong rejection reason")
            rejected += 1
    try:
        square_zeros(5, 2)
    except ValueError as error:
        require(str(error) == "census bound exceeded", "wrong dimension rejection")
        rejected += 1
    require(rejected == len(bad) + 1, "a malformed candidate passed")
    # These terms twist both coordinates. A zero second input stays zero,
    # but an arbitrary dirty second input is twisted and is not restored.
    clean_only = ((2, 0), (0, 1), (3, 3))
    literal_word(clean_only, eye(2))
    require(apply_matrix(eye(2), 1) == 1, "clean entrance control failed")
    require(apply_matrix(eye(2), 2) != apply_matrix((1, 0), 2),
            "arbitrary dirty input did not distinguish endpoints")
    return {"rejected_candidates": rejected, "clean_helper_boundary": True}


def main():
    report = {
        "status": "PASS_RESTORED_DIRTY_QUERY_CAPACITY",
        "three_coordinate_complete_fixture": complete_three_coordinate_fixture(),
        "four_coordinate_exact_minima": four_coordinate_minima(),
        "controls": rejecting_controls(),
    }
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    report["source_sha256"] = {
        name: hashlib.sha256((package / name).read_bytes()).hexdigest() for name in names
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
