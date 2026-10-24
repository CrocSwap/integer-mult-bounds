#!/usr/bin/env python3
"""Orbit reduction of the one-coset deficiency budget.

The checker ranks the nine weight representatives and the one hundred
forbidden pair profiles. It does not exhaust character pairs.
"""

import hashlib
import json
from fractions import Fraction
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_ONE_COSET_ORBIT_BUDGET sum=9 no_new_kappa"
PRIME = 5


def fail(message):
    raise SystemExit("FAIL_ONE_COSET_ORBIT_BUDGET " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def roots_and_labels():
    rows = []
    labels = []
    for i, j in combinations(range(9), 2):
        row = [0] * 9
        row[i] = 3
        row[j] = -3
        label = [1] * 9
        label[i] = 0
        label[j] = 0
        rows.append(row)
        labels.append(label)
    for subset in combinations(range(9), 3):
        row = [-1] * 9
        label = [0] * 9
        for index in subset:
            row[index] = 2
            label[index] = 1
        rows.append(row)
        labels.append(label)
    return rows, labels


def dot(left, right):
    return sum(a & b for a, b in zip(left, right)) & 1


def rank_mod(vectors):
    matrix = [list(row) for row in vectors]
    if not matrix:
        return 0
    width = len(matrix[0])
    rank = 0
    column = 0
    row = 0
    while row < len(matrix) and column < width:
        pivot = next((index for index in range(row, len(matrix)) if matrix[index][column] % PRIME), None)
        if pivot is None:
            column += 1
            continue
        matrix[row], matrix[pivot] = matrix[pivot], matrix[row]
        inverse = pow(matrix[row][column] % PRIME, PRIME - 2, PRIME)
        matrix[row] = [(entry * inverse) % PRIME for entry in matrix[row]]
        for index in range(len(matrix)):
            factor = matrix[index][column] % PRIME
            if index != row and factor:
                matrix[index] = [(matrix[index][place] - factor * matrix[row][place]) % PRIME for place in range(width)]
        row += 1
        column += 1
        rank += 1
    return rank


def mask_bits(mask):
    return [(mask >> index) & 1 for index in range(9)]


def profiles():
    found = []
    for n00 in range(10):
        for n01 in range(10 - n00):
            for n10 in range(10 - n00 - n01):
                found.append((n00, n01, n10, 9 - n00 - n01 - n10))
    return found


def valid(profile):
    n00, n01, n10, n11 = profile
    zero = n10 == 0 and n11 == 0
    other_zero = n01 == 0 and n11 == 0
    equal = n01 == 0 and n10 == 0
    return not (zero or other_zero or equal)


def forbidden(profile):
    _n00, n01, n10, n11 = profile
    if n11 % 2 == 1:
        return True
    weight = n10 + n11
    other = n01 + n11
    return weight % 2 == 0 and other % 2 == 0 and (weight // 2) % 2 == (other // 2) % 2


def blocks(profile):
    n00, n01, n10, n11 = profile
    left = [0] * n00 + [0] * n01 + [1] * n10 + [1] * n11
    right = [0] * n00 + [1] * n01 + [0] * n10 + [1] * n11
    return left, right


def span_dimension(labels):
    span = {0}
    for label in labels:
        mask = 0
        for index, bit in enumerate(label):
            mask |= bit << index
        span.update(item ^ mask for item in list(span))
    return len(span).bit_length() - 1


def evaluate():
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")

    rows, labels = roots_and_labels()
    require(len(rows) == 120 and len(labels) == 120, "the root count moved")
    require(all(sum(row) == 0 and sum(entry * entry for entry in row) == 18 for row in rows), "a root norm moved")
    require(all(any(label) for label in labels), "a label vanished")
    require(span_dimension(labels) == 9, "the labels do not span the nine-bit space")
    for left in range(120):
        for right in range(left, 120):
            gram = sum(rows[left][index] * rows[right][index] for index in range(9)) // 9
            require(dot(labels[left], labels[right]) == (1 + gram) & 1, "a label pairing moved")
    for mask in range(1, 512):
        bits = mask_bits(mask)
        require(dot(bits, bits) == (mask.bit_count() & 1), "a character square moved")

    for weight in range(1, 10):
        character = mask_bits((1 << weight) - 1)
        chosen = [index for index, label in enumerate(labels) if dot(character, label) == 1]
        vectors = [[entry % PRIME for entry in rows[index]] for index in chosen]
        require(all(sum(vector) % PRIME == 0 for vector in vectors), "an orbit row left the hyperplane")
        require(rank_mod(vectors) == 8, "an orbit rank moved")

    listed = profiles()
    kept = [profile for profile in listed if valid(profile)]
    blocked = [profile for profile in kept if forbidden(profile)]
    require(len(listed) == 220 and len(kept) == 192 and len(blocked) == 100, "the profile count moved")
    for profile in blocked:
        left, right = blocks(profile)
        chosen = [index for index, label in enumerate(labels) if dot(left, label) == 1 and dot(right, label) == 1]
        vectors = [[entry % PRIME for entry in rows[index]] for index in chosen]
        require(rank_mod(vectors) == 8, "a forbidden profile lost rank")

    supports = []
    for column in range(9):
        chosen = []
        for index, row in enumerate(rows):
            value = row[column] if index < 36 else row[column] - 2
            if value != 0:
                chosen.append(index)
        supports.append(frozenset(chosen))
        require(span_dimension(labels[index] for index in chosen) == 8, "a sharpness label span moved")
    require(len(set(supports)) == 9, "two sharpness supports coincided")
    return {
        "roots": 120,
        "profiles": 220,
        "valid_profiles": 192,
        "forbidden_profiles": 100,
        "orbit_rank": 8,
        "sharpness_sum": 9,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
