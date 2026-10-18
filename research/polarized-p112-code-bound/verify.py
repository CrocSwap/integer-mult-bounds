"""Direct deletion-rank certificate for one-sided P112 fitting rigidity.

Jose Manuel, with substantial OpenAI Codex assistance. Apache-2.0.
PR1098 supplies the predecessor support spectra; PR845 supplies its geometry.
This checker imports no predecessor verifier or search program.
"""

from collections import Counter
from functools import reduce
from hashlib import sha256
from math import gcd
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "research/direct-delivery504-global/inputs/hamming/PROTOTYPE.json"
BRIDGE = ROOT / "research/p112-single-lift/reference-geometry.json"
PIN = "327d2a868043e846381aa58a33053c24425e8cad522ff401b10ec8af1d649a3f"
BRIDGE_PIN = "4f44af368e046002553d632ee90c6470990827cea3fae41f0f54018522d7a080"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def binary_rank(rows):
    pivots = {}
    for value in rows:
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return len(pivots)


def integer_basis(rows):
    """Return original row indices forming a basis over Q, using integer gcds."""
    pivots, selected = [], []
    for index, original in enumerate(rows):
        row = list(original)
        for pivot, basis in pivots:
            if row[pivot]:
                a, b = basis[pivot], row[pivot]
                row = [a * x - b * y for x, y in zip(row, basis)]
                divisor = reduce(gcd, row)
                if divisor:
                    row = [x // divisor for x in row]
        pivot = next((i for i, value in enumerate(row) if value), None)
        if pivot is not None:
            divisor = reduce(gcd, row)
            row = [x // divisor for x in row]
            if row[pivot] < 0:
                row = [-x for x in row]
            pivots.append((pivot, row))
            selected.append(index)
    return selected


def integer_determinant(rows):
    """Separate fraction-free determinant for the selected Gram minor."""
    matrix = [row[:] for row in rows]
    n = len(matrix)
    if not n:
        return 1
    need(all(len(row) == n for row in matrix), "square integer minor")
    previous, sign = 1, 1
    for k in range(n - 1):
        pivot_row = next((i for i in range(k, n) if matrix[i][k]), None)
        if pivot_row is None:
            return 0
        if pivot_row != k:
            matrix[k], matrix[pivot_row] = matrix[pivot_row], matrix[k]
            sign = -sign
        pivot = matrix[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = matrix[i][j] * pivot - matrix[i][k] * matrix[k][j]
                need(numerator % previous == 0, "exact fraction-free division")
                matrix[i][j] = numerator // previous
            matrix[i][k] = 0
        previous = pivot
    return sign * matrix[-1][-1]


def certified_basis(rows):
    chosen = integer_basis(rows)
    basis = [rows[i] for i in chosen]
    determinant = integer_determinant([[dot(a, b) for b in basis] for a in basis])
    need(determinant > 0, "independent original rows via positive Gram determinant")
    return chosen, determinant


def support_coloops(rows, support):
    selected = [rows[i] for i in support]
    basis, determinant = certified_basis(selected)
    rank = len(basis)
    coloops, deletions = [], []
    # A row outside this original-row basis cannot be a coloop: the basis remains.
    for local_index in basis:
        reduced = selected[:local_index] + selected[local_index + 1:]
        reduced_basis, reduced_determinant = certified_basis(reduced)
        after = len(reduced_basis)
        need(after in (rank - 1, rank), "single-row deletion rank")
        if after < rank:
            coloops.append(support[local_index])
        deletions.append([support[local_index], after, reduced_determinant])
    return rank, coloops, determinant, deletions


def pinned(raw, expected):
    need(sha256(raw).hexdigest() == expected, "source SHA256")


def geometry(roots, labels, reference):
    need(len(roots) == len(labels) == 112, "112 ports")
    need(all(len(row) == 8 and all(type(x) is int for x in row) and dot(row, row) == 4
             for row in roots), "integer norm-four roots")
    need(len(set(map(tuple, roots))) == 112, "distinct literal root rows")
    need(len(reference) == 112 and set(map(tuple, roots)) == set(map(tuple, reference)),
         "literal row-permutation bridge to PR845/PR1098 X")
    need(len(integer_basis(roots)) == 8, "rational root rank eight")
    need(all(type(x) is int and 0 < x < 512 for x in labels), "nine-bit labels")
    need(binary_rank(labels) == 9, "binary label rank nine")
    need(all(x.bit_count() % 2 for x in labels), "odd binary labels")
    gram = []
    for i, u in enumerate(labels):
        row = 0
        for j, v in enumerate(labels):
            value = (u & v).bit_count() % 2
            need(value == (1 + dot(roots[i], roots[j]) // 2) % 2, "all binary Gram entries")
            row |= value << j
        gram.append(row)
    need(binary_rank(gram) == 9, "rank-nine fitting fixture")


def check_characters(characters, labels):
    need(characters == list(range(1, 512)), "all 511 nonzero characters exactly once")
    masks = [sum(((a & u).bit_count() % 2) << i for i, u in enumerate(labels)) for a in characters]
    need(len(set(masks)) == 511 and all(masks), "distinct nonempty character supports")
    return masks


def validate_pairs(pairs, labels):
    need(len(pairs) == 112 and set(map(tuple, pairs)) == {(u, j) for j, u in enumerate(labels)},
         "only the 112 original-character coloop pairs")


def rejected(name, fn):
    try:
        fn()
    except ValueError as error:
        return {"control": name, "outcome": "REJECTED", "reason": str(error)}
    raise ValueError("corruption accepted: " + name)


def main():
    raw, bridge_raw = SOURCE.read_bytes(), BRIDGE.read_bytes()
    pinned(raw, PIN)
    pinned(bridge_raw, BRIDGE_PIN)
    data = json.loads(raw)
    roots, labels = data["root_lines"][8:], data["binary_ports"][8:]
    reference = json.loads(bridge_raw)["X"]  # No predecessor labels, duals or minors.
    geometry(roots, labels, reference)
    characters = list(range(1, 512))
    masks = check_characters(characters, labels)
    census, pairs, transcript = Counter(), [], sha256()
    deletion_count = 0
    for character, mask in zip(characters, masks):
        support = [i for i in range(112) if (mask >> i) & 1]
        rank, coloops, determinant, deletions = support_coloops(roots, support)
        census[(len(support), rank, len(coloops))] += 1
        deletion_count += len(deletions)
        pairs += [[character, j] for j in coloops]
        for j in coloops:
            others = [i for i in support if i != j]
            need(len(integer_basis([roots[i] for i in others])) == 7, "rank-seven punctured support")
            need(all(dot(roots[i], roots[j]) == 0 for i in others), "unique Gram decoder column")
        record = [character, mask, rank, coloops, determinant, deletions]
        transcript.update(json.dumps(record, separators=(",", ":")).encode())
    validate_pairs(pairs, labels)
    expected = {(48, 8, 0): 7, (52, 8, 0): 224, (56, 7, 0): 8, (56, 8, 0): 40,
                (60, 8, 0): 112, (60, 8, 1): 112, (64, 8, 0): 7, (112, 8, 0): 1}
    need(census == expected and deletion_count == 4080, "complete deletion-rank census")

    # Small controls separate a basis coloop from a redundant basis choice.
    need(support_coloops([[1, 0], [0, 1]], [0, 1])[:2] == (2, [0, 1]), "basis coloop control")
    need(support_coloops([[1, 0], [0, 1], [1, 1]], [0, 1, 2])[:2] == (2, []),
         "dependent-row non-coloop control")
    need(integer_determinant([[0, 1], [1, 0]]) == -1, "signed determinant control")
    need(integer_determinant([[1, 2], [2, 4]]) == 0, "singular determinant control")
    bad_roots = [row[:] for row in roots]
    bad_roots[0][0] += 1
    bad_labels = labels[:]
    bad_labels[0] ^= 1
    bad_reference = reference[:-1] + [reference[0]]
    bad_pairs = pairs[:-1] + [[0, pairs[-1][1]]]
    controls = [
        rejected("prototype bytes altered", lambda: pinned(raw + b" ", PIN)),
        rejected("reference bytes altered", lambda: pinned(bridge_raw + b" ", BRIDGE_PIN)),
        rejected("root coordinate altered", lambda: geometry(bad_roots, labels, reference)),
        rejected("binary label altered", lambda: geometry(roots, bad_labels, reference)),
        rejected("reference row duplicated", lambda: geometry(roots, labels, bad_reference)),
        rejected("one character omitted", lambda: check_characters(characters[:-1], labels)),
        rejected("one character duplicated", lambda: check_characters(characters[:-1] + [1], labels)),
        rejected("zero character admitted", lambda: check_characters([0] + characters[1:], labels)),
        rejected("coloop character changed", lambda: validate_pairs(bad_pairs, labels)),
    ]
    print(json.dumps({
        "status": "PASS_ONE_SIDED_P112_FITTING_RIGIDITY",
        "prototype_sha256": PIN,
        "reference_geometry_sha256": BRIDGE_PIN,
        "characters": 511,
        "rational_ranks": {"7": 8, "8": 503},
        "basis_row_deletions": deletion_count,
        "positive_gram_minors": 511 + deletion_count,
        "coloop_pairs": len(pairs),
        "census": [{"support_size": size, "rank": rank, "coloops": count, "characters": number}
                   for (size, rank, count), number in sorted(census.items())],
        "transcript_sha256": transcript.hexdigest(),
        "controls": controls,
        "scope": "Credited corollary of PR1098 support spectra, independently checked by exact row deletion; only column codes are fixed.",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
