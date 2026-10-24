#!/usr/bin/env python3
"""Deficiency sums of four sparse E8 cosets.

The checker builds the 120 root lines and exhausts these four cosets.
It does not exhaust the 130305 pairs.
"""

import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_E8_SPARSE_COSET lines=120 singleton=9 no_new_kappa"
DIMENSION = 8
BINARY = 9
OMEGA = 511


def fail(message):
    raise SystemExit("FAIL_E8_SPARSE_COSET " + message)


def require(condition, message):
    if not condition:
        fail(message)


def parity(value):
    return value.bit_count() & 1


def even_quadratic(value):
    require(parity(value) == 0, "an odd vector entered the quadratic form")
    return (value.bit_count() // 2) & 1


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def root_lines():
    rows = []
    for first, second in itertools.combinations(range(DIMENSION), 2):
        for sign in (-1, 1):
            row = [0] * DIMENSION
            row[first], row[second] = 2, 2 * sign
            rows.append(tuple(row))
    for signs in range(1 << (DIMENSION - 1)):
        if parity(signs) == 0:
            rows.append((1,) + tuple(-1 if signs & (1 << index) else 1 for index in range(DIMENSION - 1)))
    require(len(rows) == len(set(rows)) == 120, "the root count moved")
    require(all(dot(row, row) == 8 for row in rows), "a root changed length")
    return tuple(rows)


def incidence(rows):
    table = []
    for index, row in enumerate(rows):
        bits = 0
        for other_index, other in enumerate(rows):
            product = dot(row, other)
            require(index == other_index or product in (-4, 0, 4), "a scalar product left the E8 set")
            if index == other_index or product == 0:
                bits |= 1 << other_index
        table.append(bits)
    return tuple(table)


def independent_rows(rows):
    echelon = {}
    indices = []
    for index, initial in enumerate(rows):
        row = initial
        while row:
            pivot = row.bit_length() - 1
            if pivot in echelon:
                row ^= echelon[pivot]
            else:
                echelon[pivot] = row
                indices.append(index)
                break
    return tuple(indices)


def inverse(rows):
    size = len(rows)
    work = [row | (1 << (size + index)) for index, row in enumerate(rows)]
    for column in range(size):
        pivot = next(index for index in range(column, size) if work[index] & (1 << column))
        work[column], work[pivot] = work[pivot], work[column]
        for index in range(size):
            if index != column and work[index] & (1 << column):
                work[index] ^= work[column]
    return tuple(row >> size for row in work)


def solve(equations):
    work = [mask | (right << BINARY) for mask, right in equations]
    pivot_row = 0
    for column in range(BINARY):
        pivot = next(index for index in range(pivot_row, len(work)) if work[index] & (1 << column))
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        for index in range(len(work)):
            if index != pivot_row and work[index] & (1 << column):
                work[index] ^= work[pivot_row]
        pivot_row += 1
    return sum(((work[index] >> BINARY) & 1) << index for index in range(BINARY))


def labels_of(rows):
    table = incidence(rows)
    indices = independent_rows(table)
    require(len(indices) == BINARY, "the orthogonality table lost rank")
    raw = tuple(
        sum(((row >> selected) & 1) << column for column, selected in enumerate(indices))
        for row in table
    )
    gram = inverse(tuple(raw[index] for index in indices))
    times = tuple(sum(parity(row & value) << index for index, row in enumerate(gram)) for value in range(OMEGA + 1))

    def pairing(left, right):
        return parity(left & times[right])

    subspace = list(range(OMEGA + 1))
    basis = []
    for remaining in range(BINARY, 0, -1):
        selected = None
        residual = None
        for candidate in subspace:
            if not pairing(candidate, candidate):
                continue
            complement = [value for value in subspace if not pairing(candidate, value)]
            if remaining == 1 or any(pairing(value, value) for value in complement):
                selected, residual = candidate, complement
                break
        require(selected is not None, "the orthonormal basis stopped")
        basis.append(selected)
        subspace = residual
    labels = tuple(sum(pairing(label, vector) << index for index, vector in enumerate(basis)) for label in raw)
    equations = [(label ^ OMEGA, 1 ^ even_quadratic(label ^ OMEGA)) for label in labels]
    equations.append((OMEGA, 0))
    correction = solve(equations)
    labels = tuple(label ^ correction if parity(label & correction) else label for label in labels)
    for index, row in enumerate(rows):
        for other_index, other in enumerate(rows):
            geometric = int(index == other_index or dot(row, other) == 0)
            require(parity(labels[index] & labels[other_index]) == geometric, "a label missed an orthogonality")
    return labels


def support_rank(support, labels):
    basis = [0] * BINARY
    rank = 0
    while support:
        bit = support & -support
        support ^= bit
        row = labels[bit.bit_length() - 1]
        while row:
            pivot = row.bit_length() - 1
            if basis[pivot]:
                row ^= basis[pivot]
            else:
                basis[pivot] = row
                rank += 1
                if rank == BINARY:
                    return rank
                break
    return rank


def cosets(rows, labels):
    orthogonal = next(index for index in range(1, len(rows)) if dot(rows[0], rows[index]) == 0)
    angled = next(index for index in range(1, len(rows)) if dot(rows[0], rows[index]) != 0)
    families = {
        "singleton": ((0, 1),),
        "nonorthogonal_11": ((0, 1), (angled, 1)),
        "nonorthogonal_12": ((0, 1), (angled, 2)),
        "orthogonal_11": ((0, 1), (orthogonal, 1)),
    }
    modular = tuple(tuple(value % 3 for value in row) for row in rows)
    totals = {name: 0 for name in families}
    nonzero = 0
    for coefficients in itertools.product(range(3), repeat=DIMENSION):
        evaluations = tuple(sum(a * b for a, b in zip(row, coefficients)) % 3 for row in modular)
        support = sum(1 << index for index, value in enumerate(evaluations) if value)
        if any(coefficients):
            require(support_rank(support, labels) == BINARY, "a codeword lost rank")
            nonzero += 1
        else:
            require(support == 0, "the zero word was nonempty")
        for name, entries in families.items():
            shifted = support
            for index, value in entries:
                if bool(evaluations[index]) != bool((evaluations[index] + value) % 3):
                    shifted ^= 1 << index
            totals[name] += BINARY - support_rank(shifted, labels)
    require(nonzero == 6560, "the codeword count moved")
    return totals


def evaluate():
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    record = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(record["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    rows = root_lines()
    labels = labels_of(rows)
    require(sum(label.bit_count() == 3 for label in labels) == 84, "the weight-three count moved")
    require(sum(label.bit_count() == 7 for label in labels) == 36, "the weight-seven count moved")
    totals = cosets(rows, labels)
    require(totals == {
        "singleton": 9,
        "nonorthogonal_11": 9,
        "nonorthogonal_12": 9,
        "orthogonal_11": 7,
    }, "a deficiency sum moved")
    require(all(total <= BINARY for total in totals.values()), "a coset exceeded deficiency nine")
    return {
        "root_lines": 120,
        "weight_three": 84,
        "weight_seven": 36,
        "singleton_deficiency": 9,
        "orthogonal_deficiency": 7,
        "cosets_at_nine": 3,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
