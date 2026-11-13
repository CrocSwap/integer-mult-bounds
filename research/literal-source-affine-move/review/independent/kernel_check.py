#!/usr/bin/env python3
"""Portable derivative of the independent exact one-column kernel checker.

The mathematical kernel and negative-control functions are unchanged from
original/kernel_check.py. Only the two input paths and source-byte loading are
adapted so this published copy needs no repository subprocess.
"""
from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path
import sys


COMMIT = "e54523517d0f03e58352e647c403a5af3e525a57"
SOURCE = "research/shared-wire-split-composition/data/final.json.gz"
BLOB = "74563a7867d9d762b6588f65362369668841bb3e"
COMPRESSED_SIZE = 350722
COMPRESSED_SHA = "2b94953dc14a122e3ef089633f05b58ec689ec5156feb7c784ed3e137dc01883"
CANONICAL_SHA = "91429a6b96729292a8764836e00c87a6f7cd3b76f05159033f4867f69a98d097"
EVENT_INDEX = 24476
EVENT = ["MOVE", 727, 3, 470, False]
START_FRAME = []
END_FRAME = [75, 137, 265]
RECIPE_SHA = "8303e04baa838553257773a6d0e7d9b57389f2f9adf0de183a6d6c644d243a79"


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def parity(x: int) -> int:
    return x.bit_count() & 1


def rank(vectors: list[int]) -> int:
    pivots: dict[int, int] = {}
    for value in vectors:
        x = value
        while x:
            bit = x.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = x
                break
            x ^= pivots[bit]
    return len(pivots)


def extend_basis(selected: list[int], n: int) -> list[int]:
    out: list[int] = []
    for v in selected + [1 << i for i in range(n)]:
        if rank(out + [v]) > len(out):
            out.append(v)
    require(len(out) == n, "basis extension did not span the source space")
    return out


def rows_from_columns(columns: list[int], n: int) -> list[int]:
    return [sum(((columns[j] >> i) & 1) << j for j in range(n)) for i in range(n)]


def inverse_rows(rows: list[int], n: int) -> list[int]:
    a = [rows[i] | (1 << (n + i)) for i in range(n)]
    for col in range(n):
        pivot = next((r for r in range(col, n) if (a[r] >> col) & 1), None)
        require(pivot is not None, "singular source basis")
        a[col], a[pivot] = a[pivot], a[col]
        for r in range(n):
            if r != col and ((a[r] >> col) & 1):
                a[r] ^= a[col]
    require([a[i] & ((1 << n) - 1) for i in range(n)] == [1 << i for i in range(n)], "GF(2) inverse check failed")
    return [a[i] >> n for i in range(n)]


def linear(rows: list[int], x: int) -> int:
    return sum(parity(row & x) << i for i, row in enumerate(rows))


def quadratic_phase(rows: list[int], linear_z4: list[int], constant: int, x: int) -> int:
    p = constant
    n = len(rows)
    for i in range(n):
        if (x >> i) & 1:
            p += linear_z4[i]
            for j in range(i + 1, n):
                p += 2 * (((rows[i] >> j) & 1) * ((x >> j) & 1))
    return p & 3


def mul_gaussian(a: tuple[int, int], b: tuple[int, int]) -> tuple[int, int]:
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def times_i(a: tuple[int, int], exponent: int) -> tuple[int, int]:
    exponent &= 3
    return ((a[0], a[1]), (-a[1], a[0]), (-a[0], -a[1]), (a[1], -a[0]))[exponent]


def canonical_source_kernel(columns: list[int], r: int, n: int, *, inverse_orientation: bool = False, adjoint_center: bool = False) -> list[dict[int, tuple[int, int]]]:
    """Return columns of K C^r K^-1 as exact Gaussian numerators / 2^r."""
    basis = extend_basis(columns, n)
    g = rows_from_columns(basis, n)
    gi = inverse_rows(g, n)
    gi_columns = rows_from_columns(gi, n)
    qrows = []
    for i, col_i in enumerate(gi_columns):
        qrows.append((1 << i) ^ sum(parity(col_i & col_j) << j for j, col_j in enumerate(gi_columns)))
    alpha = [(qrows[i] >> i) & 1 for i in range(n)]

    def q(x: int) -> int:
        return quadratic_phase(qrows, alpha, 0, x)

    # Inverse orientation is a negative control, not the source convention.
    out_cols: list[dict[int, tuple[int, int]]] = []
    for x in range(1 << n):
        col: dict[int, tuple[int, int]] = {}
        if not inverse_orientation:
            # K^-1: D_Q^-1 then P_G^-1; C^r; then K=D_Q P_G.
            z = linear(gi, x)
            start_phase = (-q(x)) & 3
            for low_out in range(1 << r):
                v = low_out | (z & ~((1 << r) - 1))
                amp = (1, 0)
                for bit in range(r):
                    same = ((low_out >> bit) & 1) == ((z >> bit) & 1)
                    # C=(1+i)I/2 + (1-i)X/2. C^dagger swaps these signs.
                    factor = (1, 1) if same else (1, -1)
                    if adjoint_center:
                        factor = (factor[0], -factor[1])
                    amp = mul_gaussian(amp, factor)
                y = linear(g, v)
                amp = times_i(amp, (start_phase + q(y)) & 3)
                col[y] = (col.get(y, (0, 0))[0] + amp[0], col.get(y, (0, 0))[1] + amp[1])
        else:
            # K C^r K^-1 with K and K^-1 exchanged: K^-1 C^r K.
            z = linear(g, x)
            start_phase = q(x)
            for low_out in range(1 << r):
                v = low_out | (z & ~((1 << r) - 1))
                amp = (1, 0)
                for bit in range(r):
                    same = ((low_out >> bit) & 1) == ((z >> bit) & 1)
                    factor = (1, 1) if same else (1, -1)
                    amp = mul_gaussian(amp, factor)
                y = linear(gi, v)
                amp = times_i(amp, (start_phase - q(y)) & 3)
                col[y] = (col.get(y, (0, 0))[0] + amp[0], col.get(y, (0, 0))[1] + amp[1])
        out_cols.append({y: a for y, a in col.items() if a != (0, 0)})
    return out_cols


def apply_monomial(factor: dict, x: int, *, phase_mode: str = "as_written", offset_mode: str = "after") -> tuple[int, int]:
    rows = factor["matrix_rows"]
    b = factor["offset"]
    p = quadratic_phase(factor["quadratic_rows"], factor["linear_Z4"], factor["phase"], x)
    if phase_mode == "negate":
        p = (-p) & 3
    if offset_mode == "after":
        y = linear(rows, x) ^ b
    elif offset_mode == "before":
        y = linear(rows, x ^ b)
    else:
        raise ValueError("unknown offset mode")
    return y, p


def factorized_kernel(recipe: dict, *, reverse_factors: bool = False, wrong_phase: bool = False, wrong_offset: bool = False, phase_mode: str = "as_written", center_adjoint: bool = False) -> list[dict[int, tuple[int, int]]]:
    n = len(recipe["left"]["matrix_rows"])
    r = recipe["rank"]
    left, right = recipe["left"], recipe["right"]
    if right is None:
        raise ValueError("rank-three recipe must have two monomial factors")
    if wrong_phase:
        right = dict(right)
        right["phase"] = (right["phase"] + 1) & 3
    # Denominator 2^r is common to every central C^r amplitude.
    result: list[dict[int, tuple[int, int]]] = []
    for x in range(1 << n):
        if not reverse_factors:
            z, p0 = apply_monomial(right, x, phase_mode=phase_mode, offset_mode="before" if wrong_offset else "after")
            phase0 = p0
            col: dict[int, tuple[int, int]] = {}
            for low_out in range(1 << r):
                v = low_out | (z & ~((1 << r) - 1))
                amp = (1, 0)
                for bit in range(r):
                    same = ((low_out >> bit) & 1) == ((z >> bit) & 1)
                    factor = (1, 1) if same else (1, -1)
                    if center_adjoint:
                        factor = (factor[0], -factor[1])
                    amp = mul_gaussian(amp, factor)
                y, p1 = apply_monomial(left, v, phase_mode=phase_mode)
                amp = times_i(amp, (phase0 + p1) & 3)
                col[y] = (col.get(y, (0, 0))[0] + amp[0], col.get(y, (0, 0))[1] + amp[1])
        else:
            z, p0 = apply_monomial(left, x, phase_mode=phase_mode)
            col = {}
            for low_out in range(1 << r):
                v = low_out | (z & ~((1 << r) - 1))
                amp = (1, 0)
                for bit in range(r):
                    same = ((low_out >> bit) & 1) == ((z >> bit) & 1)
                    factor = (1, 1) if same else (1, -1)
                    amp = mul_gaussian(amp, factor)
                y, p1 = apply_monomial(right, v, phase_mode=phase_mode)
                amp = times_i(amp, (p0 + p1) & 3)
                col[y] = (col.get(y, (0, 0))[0] + amp[0], col.get(y, (0, 0))[1] + amp[1])
        result.append({y: a for y, a in col.items() if a != (0, 0)})
    return result


def source_input(archive_path: Path) -> tuple[dict, dict]:
    raw = archive_path.read_bytes()
    git_blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    require(git_blob == BLOB, "bundled Git blob hash changed")
    require(len(raw) == COMPRESSED_SIZE, "compressed byte count changed")
    require(hashlib.sha256(raw).hexdigest() == COMPRESSED_SHA, "compressed source hash changed")
    word = json.loads(gzip.decompress(raw))
    canon = json.dumps(word, separators=(",", ":"), sort_keys=True).encode()
    require(hashlib.sha256(canon).hexdigest() == CANONICAL_SHA, "canonical source hash changed")
    require(word["program"][EVENT_INDEX] == EVENT, "source event identity changed")
    require(word["frames"][3] == START_FRAME and word["frames"][470] == END_FRAME, "source frame identity changed")
    return word, {"git_blob": git_blob, "compressed_sha256": hashlib.sha256(raw).hexdigest(), "canonical_sha256": hashlib.sha256(canon).hexdigest()}


def same_kernel(a: list[dict[int, tuple[int, int]]], b: list[dict[int, tuple[int, int]]]) -> bool:
    return len(a) == len(b) and all(a[i] == b[i] for i in range(len(a)))


def run(recipe_path: Path, archive_path: Path) -> dict:
    _, source_receipt = source_input(archive_path)
    raw = recipe_path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == RECIPE_SHA, "RECIPE hash changed")
    recipe_doc = json.loads(raw)
    require(recipe_doc["canonical_main"] == COMMIT and recipe_doc["event_index"] == EVENT_INDEX and recipe_doc["event"] == EVENT, "RECIPE source identity mismatch")
    require(recipe_doc["frames"] == {"3": START_FRAME, "470": END_FRAME}, "RECIPE frame binding mismatch")
    recipe = recipe_doc["recipe"]
    require(recipe["rank"] == 3 and recipe["left"]["offset"] == 0 and recipe["right"]["offset"] == 5, "rank/offset binding mismatch")
    require(recipe["left"]["phase"] == 0 and recipe["right"]["phase"] == 2, "absolute phase binding mismatch")
    direct = canonical_source_kernel(END_FRAME, 3, 9)
    factored = factorized_kernel(recipe)
    require(same_kernel(direct, factored), "source kernel differs from L C^3 R")

    # Five deliberately wrong conventions must be rejected by the complete kernel comparison.
    mutants = {
        "inverse_orientation": canonical_source_kernel(END_FRAME, 3, 9, inverse_orientation=True),
        "reverse_factor_order": factorized_kernel(recipe, reverse_factors=True),
        "wrong_absolute_phase": factorized_kernel(recipe, wrong_phase=True),
        "offset_before_linear_map": factorized_kernel(recipe, wrong_offset=True),
        "adjoint_central_kernel": factorized_kernel(recipe, center_adjoint=True),
    }
    for label, kernel in mutants.items():
        require(not same_kernel(direct, kernel), f"negative control unexpectedly passed: {label}")
    return {
        "schema": "source-affine-move-independent-kernel-check/1",
        "source": source_receipt,
        "event_index": EVENT_INDEX,
        "event": EVENT,
        "frames": {"3": START_FRAME, "470": END_FRAME},
        "recipe_sha256": hashlib.sha256(raw).hexdigest(),
        "rank": 3,
        "central": "C^tensor3, C=((1+i)I+(1-i)X)/2, exact Gaussian numerators over 2^3",
        "formula_checked": "K C^tensor3 K^-1 = M_left C^tensor3 M_right; K=D_Q P_G from the source frame basis",
        "one_column_basis_inputs_checked": 1 << 9,
        "nonzero_kernel_entries_checked": sum(map(len, direct)),
        "denominator": 1 << 3,
        "right_offset_applied_after_G": True,
        "right_constant_phase": 2,
        "negative_controls_rejected": sorted(mutants),
        "all_f_phase_lift": {"statement": "(i^a) tensor-f = i^(a*f)", "checked_target_right_phase": 2, "residues_by_f_1_to_8": [((2*f) & 3) for f in range(1, 9)]},
        "scope": "Exact one-column source-kernel check only; fixed-f tensor lift follows by tensor product. It is not an all-f tape execution or tariff review.",
    }


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: python3 kernel_check.py IMPLEMENTATION_RECIPE.json SELECTED_FINAL.json.gz")
    result = run(Path(sys.argv[1]), Path(sys.argv[2]))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
