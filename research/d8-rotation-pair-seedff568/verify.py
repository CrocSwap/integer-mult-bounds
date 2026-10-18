#!/usr/bin/env python3
"""Independent exact replay using generic F2[D8] and matrix multiplication."""
from __future__ import annotations

import itertools
import json
from pathlib import Path

ELEMENTS = tuple((i, e) for i in range(4) for e in range(2))
INDEX = {x: i for i, x in enumerate(ELEMENTS)}
IDENTITY_PAIR = (0, 0)
ID = INDEX[IDENTITY_PAIR]

def product_group(x: tuple[int, int], y: tuple[int, int]) -> tuple[int, int]:
    i, e = x
    j, f = y
    return ((i + (j if e == 0 else -j)) % 4, e ^ f)

GTABLE = [[INDEX[product_group(x, y)] for y in ELEMENTS] for x in ELEMENTS]
S = INDEX[(0, 1)]
T = INDEX[(3, 1)]
R = INDEX[(1, 0)]
RI = INDEX[(3, 0)]
assert len(ELEMENTS) == 8
assert all(GTABLE[ID][i] == i and GTABLE[i][ID] == i for i in range(8))
assert all(any(GTABLE[i][j] == ID and GTABLE[j][i] == ID for j in range(8)) for i in range(8))
assert GTABLE[S][S] == ID and GTABLE[T][T] == ID
assert GTABLE[S][T] == R and GTABLE[T][S] == RI
assert GTABLE[R][R] == INDEX[(2, 0)] and GTABLE[R][INDEX[(2, 0)]] == RI
assert all(GTABLE[GTABLE[i][j]][k] == GTABLE[i][GTABLE[j][k]]
           for i in range(8) for j in range(8) for k in range(8))

# A formal group-algebra element is an eight-bit vector of F2 coefficients.
def ring_product(a: int, b: int) -> int:
    out = 0
    for i in range(8):
        if (a >> i) & 1:
            for j in range(8):
                if (b >> j) & 1:
                    out ^= 1 << GTABLE[i][j]
    return out

# A 2x2 matrix is a row-major tuple of four such eight-bit vectors.
I = (1 << ID, 0, 0, 1 << ID)
def matrix_product(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    out = []
    for i in range(2):
        for j in range(2):
            z = 0
            for k in range(2):
                z ^= ring_product(a[2 * i + k], b[2 * k + j])
            out.append(z)
    return tuple(out)

VECTORS = (1, 2, 3)
IDEMPOTENTS = tuple((u, v) for u in VECTORS for v in VECTORS
                    if ((u & v).bit_count() & 1) == 1)
assert len(IDEMPOTENTS) == 6
LABELS = (S, T)
FACTORS = []
for label_index, g in enumerate(LABELS):
    for u, v in IDEMPOTENTS:
        delta = (1 << ID) | (1 << g)
        n = tuple(((u >> i) & 1) * ((v >> j) & 1)
                  for i in range(2) for j in range(2))
        f = tuple(((1 << ID) if i == j else 0) ^ (delta if n[2 * i + j] else 0)
                  for i in range(2) for j in range(2))
        FACTORS.append((label_index, u, v, f))
assert len(FACTORS) == 12
for _, _, _, f in FACTORS:
    assert matrix_product(f, f) == I
    augmentation = tuple(mask.bit_count() & 1 for mask in f)
    assert augmentation == (1, 0, 0, 1)

def word_product(word: tuple[int, ...]) -> tuple[int, ...]:
    out = I
    for fi in word:
        out = matrix_product(out, FACTORS[fi][3])
    return out

# Select the coordinate projections without relying on factor-list positions.
def factor_index(label_index: int, u: int, v: int) -> int:
    for i, (li, ui, vi, _) in enumerate(FACTORS):
        if (li, ui, vi) == (label_index, u, v):
            return i
    raise AssertionError((label_index, u, v))

TARGET = (1 << R, 0, 0, 1 << RI)
DIRECT = (factor_index(0, 1, 1), factor_index(1, 1, 1),
          factor_index(1, 2, 2), factor_index(0, 2, 2))
assert word_product(DIRECT) == TARGET

# Positive control: two different reflections on two separate roles.
CONTROL = (1 << S, 0, 0, 1 << T)
assert word_product((factor_index(0, 1, 1), factor_index(1, 2, 2))) == CONTROL

# Meaningful negative controls: one omitted paid operation and one altered label
# must fail the complete formal boundary, not only a selected group coordinate.
assert word_product(DIRECT[:-1]) != TARGET
mutated = (DIRECT[0], factor_index(0, 1, 1), DIRECT[2], DIRECT[3])
assert word_product(mutated) != TARGET

# Binary rank of a matrix encoded by row bitmasks.
def rank_f2(rows: list[int]) -> int:
    rows = rows[:]
    rank = 0
    width = max((r.bit_length() for r in rows), default=0)
    for col in range(width):
        pivot = next((i for i in range(rank, len(rows)) if (rows[i] >> col) & 1), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(len(rows)):
            if i != rank and ((rows[i] >> col) & 1):
                rows[i] ^= rows[rank]
        rank += 1
    return rank

def regular_difference(g: int) -> list[int]:
    # Conventional rows of L_g + I, with basis vectors indexed by D8 elements.
    rows = []
    for out_index in range(8):
        row = 0
        for in_index in range(8):
            if (out_index == in_index) ^ (out_index == GTABLE[g][in_index]):
                row |= 1 << in_index
        rows.append(row)
    return rows

def projection_rows(u: int, v: int) -> list[int]:
    return [sum((((u >> i) & 1) * ((v >> j) & 1)) << j for j in range(2))
            for i in range(2)]

def tensor_rows(a_rows: list[int], b_rows: list[int]) -> list[int]:
    out = []
    for ai in range(len(a_rows)):
        for bi in range(len(b_rows)):
            row = 0
            for aj in range(len(a_rows)):
                if (a_rows[ai] >> aj) & 1:
                    for bj in range(len(b_rows)):
                        if (b_rows[bi] >> bj) & 1:
                            row |= 1 << (2 * aj + bj)
            out.append(row)
    return out

def target_difference_rows() -> list[int]:
    rows = []
    for out_group in range(8):
        for out_role in range(2):
            row = 0
            for in_group in range(8):
                for in_role in range(2):
                    if out_role == in_role:
                        g = R if out_role == 0 else RI
                        if (out_group == in_group) ^ (out_group == GTABLE[g][in_group]):
                            row |= 1 << (2 * in_group + in_role)
            rows.append(row)
    return rows

reflection_rank = rank_f2(regular_difference(S))
rotation_rank = rank_f2(regular_difference(R))
rotation_inverse_rank = rank_f2(regular_difference(RI))
assert (reflection_rank, rotation_rank, rotation_inverse_rank) == (4, 6, 6)
for g in LABELS:
    for u, v in IDEMPOTENTS:
        assert rank_f2(tensor_rows(regular_difference(g), projection_rows(u, v))) == 4
assert rank_f2(target_difference_rows()) == 12

# Independent exhaustive full-coefficient replay for every word of lengths 0..3.
length_counts = []
hits = []
for n in range(4):
    checked = 0
    for word in itertools.product(range(12), repeat=n):
        checked += 1
        if word_product(word) == TARGET:
            hits.append({"length": n, "factor_indices": list(word)})
    expected = 12 ** n
    assert checked == expected
    length_counts.append({"length": n, "factor_words_checked": checked,
                          "expected": expected, "complete": True})
assert hits == []

result_path = Path(__file__).with_name("RESULT.json")
recorded = json.loads(result_path.read_text())
assert recorded["status"] == "PASS_D8_ROTATION_PAIR_SEARCH"
assert recorded["length_census"] == length_counts
assert recorded["factorizations_at_or_below_3"] == hits
assert recorded["direct_four_call"]["status"] == "PASS"

print("PASS_D8_ROTATION_PAIR minimum=4 lengths=[1,12,144,1728] "
      "regular_ranks=(4,6,6) positive_controls=2 negative_controls=2 no_new_kappa")
