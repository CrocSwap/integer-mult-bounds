#!/usr/bin/env python3
"""Exact q<=4 search for a three-generator UT4 group-algebra word."""

from __future__ import annotations

import hashlib
import argparse
import json
import struct
from pathlib import Path


N = 4
POSITIONS = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))
POS_INDEX = {p: i for i, p in enumerate(POSITIONS)}
IDENTITY = 0
GROUP_SIZE = 64
ALGEBRA_ONE = 1 << IDENTITY
SEED = "bfe59e1502f6168422d1d522f30c3fba"
BASE = "0b1cccf86e2f5132ed286a26ef0a681a495740ea"
SELECTED_SHA256 = "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32"


def group_multiply(a: int, b: int) -> int:
    """Multiply UT4(F2) elements encoded by their six strict-upper bits."""
    out = 0
    for bit, (i, j) in enumerate(POSITIONS):
        value = ((a >> bit) ^ (b >> bit)) & 1
        for k in range(i + 1, j):
            value ^= ((a >> POS_INDEX[(i, k)]) & 1) & ((b >> POS_INDEX[(k, j)]) & 1)
        out |= value << bit
    return out


MUL = tuple(tuple(group_multiply(a, b) for b in range(GROUP_SIZE)) for a in range(GROUP_SIZE))


def group_inverse(a: int) -> int:
    for b in range(GROUP_SIZE):
        if MUL[a][b] == IDENTITY and MUL[b][a] == IDENTITY:
            return b
    raise AssertionError("group inverse missing")


INV = tuple(group_inverse(a) for a in range(GROUP_SIZE))


def word(*letters: int) -> int:
    result = IDENTITY
    for letter in letters:
        result = MUL[result][letter]
    return result


X = 1 << POS_INDEX[(0, 1)]
Y = 1 << POS_INDEX[(1, 2)]
Z = 1 << POS_INDEX[(2, 3)]
U = word(X, Y, X, Y)
V = word(Y, Z, Y, Z)
TARGET_DIAGONAL = (U, V, IDENTITY, IDENTITY)


def matrix_bits_product(a: int, b: int) -> int:
    """Product of two 4x4 binary matrices encoded row-major in 16 bits."""
    out = 0
    for i in range(N):
        for j in range(N):
            value = 0
            for k in range(N):
                value ^= ((a >> (i * N + k)) & 1) & ((b >> (k * N + j)) & 1)
            out |= value << (i * N + j)
    return out


def rank_binary_rows(rows: list[int], columns: int) -> int:
    """Rank over F2 for row vectors stored as integer bitsets."""
    work = rows[:]
    rank = 0
    for column in range(columns):
        pivot = next((r for r in range(rank, len(work)) if (work[r] >> column) & 1), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        for r in range(len(work)):
            if r != rank and ((work[r] >> column) & 1):
                work[r] ^= work[rank]
        rank += 1
        if rank == len(work):
            break
    return rank


def rank4(matrix: int) -> int:
    return rank_binary_rows([(matrix >> (4 * i)) & 0xF for i in range(4)], 4)


def natural_displacement(group_element: int) -> int:
    result = 0
    for bit, (i, j) in enumerate(POSITIONS):
        if (group_element >> bit) & 1:
            result |= 1 << (4 * i + j)
    return result


def natural_matrix(group_element: int) -> int:
    identity = sum(1 << (4 * i + i) for i in range(4))
    return identity ^ natural_displacement(group_element)


def group_code_from_matrix(matrix: int) -> int:
    return sum(((matrix >> (4 * i + j)) & 1) << bit
               for bit, (i, j) in enumerate(POSITIONS))


def rank_one_idempotents() -> list[int]:
    matrices: list[int] = []
    for column in range(1, 1 << N):
        for row in range(1, 1 << N):
            if (column & row).bit_count() % 2 != 1:
                continue
            matrix = 0
            for i in range(N):
                for j in range(N):
                    if ((column >> i) & 1) and ((row >> j) & 1):
                        matrix |= 1 << (i * N + j)
            assert matrix_bits_product(matrix, matrix) == matrix
            assert rank4(matrix) == 1
            matrices.append(matrix)
    assert len(matrices) == 120 and len(set(matrices)) == 120
    return matrices


IDEMPOTENTS = rank_one_idempotents()
LABELS = (("x", X), ("y", Y), ("z", Z))


def make_factor(label: int, nbits: int) -> tuple[int, ...]:
    """Matrix for I + ([label]+[1])N over F2[G]."""
    delta = ALGEBRA_ONE | (1 << label)
    return tuple((ALGEBRA_ONE if i == j else 0) ^ (delta if ((nbits >> (i * N + j)) & 1) else 0)
                 for i in range(N) for j in range(N))


FACTORS: list[tuple[int, ...]] = []
FACTOR_META: list[tuple[str, int]] = []
for label_name, label in LABELS:
    for nbits in IDEMPOTENTS:
        FACTORS.append(make_factor(label, nbits))
        FACTOR_META.append((label_name, nbits))


def algebra_product(a: int, b: int) -> int:
    """Product in F2[G], using 64-bit masks for coefficients."""
    result = 0
    left = a
    while left:
        low_a = left & -left
        ga = low_a.bit_length() - 1
        left ^= low_a
        right = b
        while right:
            low_b = right & -right
            gb = low_b.bit_length() - 1
            right ^= low_b
            result ^= 1 << MUL[ga][gb]
    return result


def matrix_product(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    result = []
    for i in range(N):
        for j in range(N):
            entry = 0
            for k in range(N):
                entry ^= algebra_product(a[i * N + k], b[k * N + j])
            result.append(entry)
    return tuple(result)


def pack_matrix(matrix: tuple[int, ...]) -> bytes:
    return struct.pack("<16Q", *matrix)


def diagonal_target() -> tuple[int, ...]:
    return tuple(1 << TARGET_DIAGONAL[i] if i == j else 0
                 for i in range(N) for j in range(N))


TARGET = diagonal_target()
TARGET_KEY = pack_matrix(TARGET)


def translate_algebra(left_group_element: int, value: int) -> int:
    result = 0
    while value:
        low = value & -value
        g = low.bit_length() - 1
        value ^= low
        result ^= 1 << MUL[left_group_element][g]
    return result


def left_multiply_diagonal(diagonal: tuple[int, ...], matrix: tuple[int, ...]) -> tuple[int, ...]:
    """Left multiply by a diagonal matrix of single group elements."""
    out = []
    for i in range(N):
        for j in range(N):
            out.append(translate_algebra(diagonal[i * N + i].bit_length() - 1, matrix[i * N + j]))
    return tuple(out)


def direct_word(indices: tuple[int, ...]) -> tuple[int, ...]:
    result = tuple(ALGEBRA_ONE if i == j else 0 for i in range(N) for j in range(N))
    for factor_index in indices:
        result = matrix_product(result, FACTORS[factor_index])
    return result


def direct_control_indices() -> tuple[int, ...]:
    # Rank-one coordinate projectors e1e1^T and e2e2^T, labels x,y,y,z.
    def factor_id(name: str, nbits: int) -> int:
        label_index = next(k for k, (label_name, _) in enumerate(LABELS) if label_name == name)
        return label_index * len(IDEMPOTENTS) + IDEMPOTENTS.index(nbits)
    e1 = 1 << 0
    e2 = 1 << (N + 1)
    # x,y,x,y on role 1 then y,z,y,z on role 2.
    return tuple(factor_id(name, nbits) for name, nbits in (
        ("x", e1), ("y", e1), ("x", e1), ("y", e1),
        ("y", e2), ("z", e2), ("y", e2), ("z", e2),
    ))


def validate_structural_facts() -> None:
    assert len(FACTORS) == 360
    # Independently reconstruct the full group table by ordinary 4x4 matrix
    # multiplication, checking all 64*64 ordered pairs.
    for a in range(GROUP_SIZE):
        for b in range(GROUP_SIZE):
            product_matrix = matrix_bits_product(natural_matrix(a), natural_matrix(b))
            assert group_code_from_matrix(product_matrix) == MUL[a][b]
            assert product_matrix == natural_matrix(MUL[a][b])
    assert all(MUL[g][g] == IDENTITY for _, g in LABELS)
    assert INV[X] == X and INV[Y] == Y and INV[Z] == Z
    assert U == 1 << POS_INDEX[(0, 2)]
    assert V == 1 << POS_INDEX[(1, 3)]
    central_root = 1 << POS_INDEX[(0, 3)]
    assert word(U, Z, U, Z) == central_root
    assert word(X, V, X, V) == central_root
    # In the natural representation the two target displacements have rank one each.
    # The 16x16 target is block diagonal, so its displacement rank is two.
    assert rank4(natural_displacement(U)) == 1 and rank4(natural_displacement(V)) == 1
    target_rows = [0] * 16
    target_rows[0] |= 1 << 2  # E13 in register 1
    target_rows[4 + 1] |= 1 << (4 + 3)  # E24 in register 2
    assert rank_binary_rows(target_rows, 16) == 2
    # Each represented paid call has displacement N tensor (rho(g)+I),
    # whose rank is rank(N)*rank(rho(g)+I)=1.
    for label_name, label in LABELS:
        assert rank4(natural_displacement(label)) == 1, label_name
    # Every call is an involution because (g+1)^2=0 and N^2=N.
    identity = tuple(ALGEBRA_ONE if i == j else 0 for i in range(N) for j in range(N))
    for f in FACTORS:
        assert matrix_product(f, f) == identity


def search() -> dict:
    validate_structural_facts()
    pair_map: dict[bytes, tuple[int, int]] = {}
    duplicate_pairs = 0
    for i, left in enumerate(FACTORS):
        for j, right in enumerate(FACTORS):
            key = pack_matrix(matrix_product(left, right))
            if key in pair_map:
                duplicate_pairs += 1
            else:
                pair_map[key] = (i, j)

    pair_words = len(FACTORS) ** 2
    assert pair_words == 129_600
    # Length 2, then 3. Each factor is self-inverse, so target*last is the
    # required two-factor prefix for length 3.
    witness = None
    if TARGET_KEY in pair_map:
        witness = ("q2", pair_map[TARGET_KEY])
    q3_checked = 0
    if witness is None:
        for k, factor in enumerate(FACTORS):
            needed_prefix = pack_matrix(left_multiply_diagonal(TARGET, factor))
            q3_checked += 1
            if needed_prefix in pair_map:
                witness = ("q3", (*pair_map[needed_prefix], k))
                break

    # For a q4 word P*(a*b)=target, P=target*(b*a), since each
    # individual call is an involution. Enumerate every ordered (a,b).
    q4_checked = 0
    if witness is None:
        for a, factor_a in enumerate(FACTORS):
            for b, factor_b in enumerate(FACTORS):
                inverse_suffix = matrix_product(factor_b, factor_a)
                needed_prefix = pack_matrix(left_multiply_diagonal(TARGET, inverse_suffix))
                q4_checked += 1
                if needed_prefix in pair_map:
                    witness = ("q4", (*pair_map[needed_prefix], a, b))
                    break
            if witness is not None:
                break

    direct_indices = direct_control_indices()
    direct_result = direct_word(direct_indices)
    assert direct_result == TARGET
    omitted_result = direct_word(direct_indices[:-1])
    assert omitted_result != TARGET
    wrong_label_indices = list(direct_indices)
    # Replace the first x coordinate call by z on the same idempotent.
    wrong_label_indices[0] += 2 * len(IDEMPOTENTS)
    wrong_label_result = direct_word(tuple(wrong_label_indices))
    assert wrong_label_result != TARGET

    if witness is None:
        assert q3_checked == 360 and q4_checked == pair_words
        q1_rank_exclusion = "target displacement rank 2; one call changes rank by at most 1"
        outcome = "no_word_of_length_at_most_4"
        witness_data = None
    else:
        length_name, indices = witness
        witness_data = [
            {"factor_index": i, "label": FACTOR_META[i][0], "N_bits": f"0x{FACTOR_META[i][1]:04x}"}
            for i in indices
        ]
        assert direct_word(indices) == TARGET
        q1_rank_exclusion = "target displacement rank 2; one call changes rank by at most 1"
        outcome = f"witness_{length_name}"

    canonical = {
        "seed": SEED,
        "base_commit": BASE,
        "selected_record_sha256": SELECTED_SHA256,
        "group": "UT4(F2)",
        "group_encoding": "six strict-upper bits in order (12,13,14,23,24,34)",
        "paid_labels": {name: f"0x{g:02x}" for name, g in LABELS},
        "targets": {"u": f"0x{U:02x}", "v": f"0x{V:02x}", "diagonal": [f"0x{g:02x}" for g in TARGET_DIAGONAL]},
        "noncentrality_witnesses": {"u_commutator_z": f"0x{word(U, Z, U, Z):02x}", "x_commutator_v": f"0x{word(X, V, X, V):02x}"},
        "rank_one_idempotents": len(IDEMPOTENTS),
        "independent_group_products_checked": GROUP_SIZE * GROUP_SIZE,
        "factors": len(FACTORS),
        "ordered_pair_words": pair_words,
        "distinct_pair_products": len(pair_map),
        "ordered_pair_collisions": duplicate_pairs,
        "q2_checked": "membership in complete ordered pair table",
        "q3_candidates_checked": q3_checked,
        "q4_candidates_checked": q4_checked,
        "outcome": outcome,
        "witness": witness_data,
        "natural_representation_target_displacement_rank": 2,
        "maximum_single_call_displacement_rank": 1,
        "rank_exclusion": q1_rank_exclusion,
        "controls": {
            "direct_8_call_word_equals_target": True,
            "omitted_final_call_differs": True,
            "first_x_changed_to_z_differs": True,
        },
        "pair_table_sha256": hashlib.sha256(b"".join(sorted(pair_map))).hexdigest(),
    }
    return canonical


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-certificate", action="store_true",
                        help="write the deterministic result to certificate.json")
    args = parser.parse_args()
    result = search()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write_certificate:
        out_path = Path(__file__).with_name("certificate.json")
        out_path.write_text(encoded, encoding="utf-8")
    print(encoded, end="")


if __name__ == "__main__":
    main()
