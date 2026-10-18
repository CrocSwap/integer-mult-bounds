#!/usr/bin/env python3
"""Finite corroboration for the proved Q8 regular-cell rank bound."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
LABELS = ("1", "i", "j", "k", "z", "-i", "-j", "-k")
QUATERNIONS = {
    "1": (1, 0, 0, 0),
    "i": (0, 1, 0, 0),
    "j": (0, 0, 1, 0),
    "k": (0, 0, 0, 1),
    "z": (-1, 0, 0, 0),
    "-i": (0, -1, 0, 0),
    "-j": (0, 0, -1, 0),
    "-k": (0, 0, 0, -1),
}


def fail(message: str) -> None:
    raise RuntimeError(message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def qmul(x: tuple[int, ...], y: tuple[int, ...]) -> tuple[int, ...]:
    a, b, c, d = x
    e, f, g, h = y
    return (
        a * e - b * f - c * g - d * h,
        a * f + b * e + c * h - d * g,
        a * g - b * h + c * e + d * f,
        a * h + b * g - c * f + d * e,
    )


def group_table() -> list[list[int]]:
    reverse = {QUATERNIONS[label]: i for i, label in enumerate(LABELS)}
    table = []
    for left in LABELS:
        row = []
        for right in LABELS:
            product = qmul(QUATERNIONS[left], QUATERNIONS[right])
            if product not in reverse:
                fail("quaternion product escaped Q8")
            row.append(reverse[product])
        table.append(row)
    return table


def identity(n: int) -> list[int]:
    return [1 << i for i in range(n)]


def gf2_rank(rows: list[int]) -> int:
    pivots: dict[int, int] = {}
    for original in rows:
        row = original
        while row:
            pivot = row.bit_length() - 1
            if pivot in pivots:
                row ^= pivots[pivot]
            else:
                pivots[pivot] = row
                break
    return len(pivots)


def matmul(a_rows: list[int], b_rows: list[int], n: int) -> list[int]:
    out = []
    for row in a_rows:
        value = 0
        for k in range(n):
            if (row >> k) & 1:
                value ^= b_rows[k]
        out.append(value)
    return out


def kron(a_rows: list[int], a_cols: int,
         b_rows: list[int], b_cols: int) -> list[int]:
    out = []
    for a_row in a_rows:
        for b_row in b_rows:
            row = 0
            for k in range(a_cols):
                if (a_row >> k) & 1:
                    row |= b_row << (k * b_cols)
            out.append(row)
    return out


def xor_rows(a: list[int], b: list[int]) -> list[int]:
    return [x ^ y for x, y in zip(a, b)]


def regular_permutation(table: list[list[int]], label: int) -> list[int]:
    rows = [0] * len(LABELS)
    for source in range(len(LABELS)):
        target = table[label][source]
        rows[target] |= 1 << source
    return rows


def idempotent_pairs(r: int):
    for u in range(1, 1 << r):
        for v in range(1, 1 << r):
            if (u & v).bit_count() & 1:
                yield u, v


def coupling_matrix(u: int, v: int, r: int) -> list[int]:
    return [sum(1 << j for j in range(r)
                if ((u >> i) & 1) and ((v >> j) & 1))
            for i in range(r)]


def validate_idempotent(u: int, v: int, r: int) -> None:
    if not (0 < u < (1 << r) and 0 < v < (1 << r)):
        raise ValueError("u and v must be nonzero r-bit vectors")
    if ((u & v).bit_count() & 1) != 1:
        raise ValueError("v^T u must equal one over F2")


def check_source_hashes() -> None:
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    for entry in manifest["files"]:
        if entry["usage"] != "input":
            continue
        path = ROOT / entry["path"]
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        require(actual == entry["sha256"], f"source hash mismatch: {entry['path']}")


def check_factor_rank_inequality() -> int:
    # All 256 ordered pairs of 2x2 binary matrices corroborate
    # rank(AB-I) <= rank(A-I)+rank(B-I).
    n = 2
    ident = identity(n)
    matrices = [[code & 3, (code >> 2) & 3] for code in range(16)]
    checked = 0
    for a in matrices:
        da = xor_rows(a, ident)
        for b in matrices:
            db = xor_rows(b, ident)
            product = matmul(a, b, n)
            lhs = gf2_rank(xor_rows(product, ident))
            rhs = gf2_rank(da) + gf2_rank(db)
            require(lhs <= rhs, "rank subadditivity control failed")
            checked += 1
    return checked


def build_receipt() -> dict:
    check_source_hashes()
    table = group_table()
    require(table[1][1] == 4, "i*i is not z")
    require(table[2][2] == 4, "j*j is not z")
    require(table[3][3] == 4, "k*k is not z")
    require(table[4][4] == 0, "z*z is not 1")

    identity8 = identity(8)
    payload_ranks: dict[str, list[int]] = {}
    for label_index, label in enumerate(LABELS):
        p_rows = regular_permutation(table, label_index)
        base_rank = gf2_rank(xor_rows(p_rows, identity8))
        expected = 0 if label_index == 0 else (4 if label_index == 4 else 6)
        require(base_rank == expected,
                f"regular displacement rank mismatch for {label}")
        payload_ranks[label] = []
        for b in (1, 2):
            p_b = kron(p_rows, 8, identity(b), b)
            q_b = xor_rows(p_b, identity(8 * b))
            rank_b = gf2_rank(q_b)
            require(rank_b == b * expected,
                    f"payload tensor rank mismatch for {label}, B={b}")
            payload_ranks[label].append(rank_b)

    fixtures = 0
    idempotents_by_r: dict[str, int] = {}
    for r in (1, 2, 3):
        pairs = list(idempotent_pairs(r))
        idempotents_by_r[str(r)] = len(pairs)
        for u, v in pairs:
            n_rows = coupling_matrix(u, v, r)
            require(gf2_rank(n_rows) == 1, "coupling did not have rank one")
            require(matmul(n_rows, n_rows, r) == n_rows,
                    "declared coupling is not idempotent")
            for b in (1, 2):
                for label_index, label in enumerate(LABELS):
                    p_rows = regular_permutation(table, label_index)
                    p_b = kron(p_rows, 8, identity(b), b)
                    q_b = xor_rows(p_b, identity(8 * b))
                    displacement = kron(n_rows, r, q_b, 8 * b)
                    observed = gf2_rank(displacement)
                    expected = b * (0 if label_index == 0 else
                                    (4 if label_index == 4 else 6))
                    require(observed == expected,
                            f"coupled rank mismatch r={r}, B={b}, g={label}")
                    fixtures += 1

    # Deliberately replace an order-four target by identity; the rank target
    # must reject this wrong-label mutation.
    wrong_label_rank = gf2_rank(
        xor_rows(regular_permutation(table, 0), identity8))
    require(wrong_label_rank != 6,
            "wrong-label mutation unexpectedly survived")
    validate_idempotent(1, 1, 1)  # Positive control: e_0 e_0^T.
    invalid_rejected = False
    try:
        validate_idempotent(1, 2, 2)  # e_0 e_1^T has v^T u=0.
    except ValueError:
        invalid_rejected = True
    require(invalid_rejected, "non-idempotent coupling control was accepted")

    factor_pairs = check_factor_rank_inequality()
    return {
        "schema_version": 1,
        "status": "PASS_Q8_REGULAR_CELL_RANK_BOUND",
        "field": "F2",
        "assumptions": {
            "roles_r": "all finite integers r >= 1",
            "payload_width_B": "all positive integers B >= 1",
            "coupling": "N=u v^T, u,v nonzero, v^T u=1",
            "paid_instruction": "invertible update M with rank(M-I) <= 1 on combined bit cells",
        },
        "proved_displacement_rank": {
            "identity": "0",
            "central_z": "4B",
            "order_four": "6B",
        },
        "proved_instruction_lower_bound": {
            "central_z": "at least 4B",
            "order_four": "at least 6B",
        },
        "finite_checks": {
            "rank_couplings_by_r": idempotents_by_r,
            "roles_checked": [1, 2, 3],
            "payload_widths_checked": [1, 2],
            "labels_checked": list(LABELS),
            "coupled_matrix_fixtures": fixtures,
            "rank_subadditivity_pairs_2x2": factor_pairs,
            "controls": ["Q8 order identities", "wrong-label", "non-idempotent coupling"],
        },
        "regular_rank_by_label_and_B_1_2": payload_ranks,
        "limits": [
            "finite checks corroborate the written all-parameter proof",
            "no shortest-circuit equality is claimed",
            "no selected-supplier caller or physical hosting is established",
        ],
    }


def main() -> None:
    print(json.dumps(build_receipt(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
