#!/usr/bin/env python3
"""Independent exhaustive GF(2) checker for the d=2 arbitrary-pivot fixtures.

Krzysztof Wojt, substantial OpenAI Codex and bounded Luna assistance. Apache-2.0.
This deliberately uses only raw-matrix arithmetic and the Python standard
library. Matrix rows are represented as integers, with bit j storing column j.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Callable


D = 2
MAX_DIMENSION = 16
MAX_FILE_BYTES = 2 * 1024 * 1024
DEFAULT_FIXTURES = Path(__file__).with_name("FIXTURES.json")


class CheckError(Exception):
    """Raised when an input or mathematical check fails."""


def fail(message: str) -> None:
    raise CheckError(message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def mask(width: int) -> int:
    return (1 << width) - 1


def matrix_from_json(value: Any, label: str, dimension: int | None = None) -> tuple[int, ...]:
    require(type(value) is list, f"{label}: expected a list of rows")
    size = len(value)
    require(0 < size <= MAX_DIMENSION, f"{label}: dimension must be in 1..{MAX_DIMENSION}")
    if dimension is not None:
        require(size == dimension, f"{label}: expected {dimension} rows, got {size}")

    rows: list[int] = []
    for row_index, row in enumerate(value):
        require(type(row) is list, f"{label}[{row_index}]: expected a list")
        require(len(row) == size, f"{label}[{row_index}]: expected {size} entries")
        bits = 0
        for column, entry in enumerate(row):
            require(type(entry) is int and entry in (0, 1),
                    f"{label}[{row_index}][{column}]: expected integer bit 0 or 1")
            bits |= entry << column
        rows.append(bits)
    return tuple(rows)


def matmul(left: tuple[int, ...], right: tuple[int, ...],
           output_columns: int) -> tuple[int, ...]:
    """Multiply bitset-row matrices over GF(2), with explicit output width."""
    require(len(right) > 0, "matrix product: empty inner dimension")
    require(0 < output_columns <= MAX_DIMENSION,
            "matrix product: output width is outside the bounded domain")
    inner_mask = mask(len(right))
    out_mask = mask(output_columns)
    require(all((row & ~out_mask) == 0 for row in right),
            "matrix product: right operand row exceeds output width")
    require(all((row & ~inner_mask) == 0 for row in left),
            "matrix product: left operand row exceeds inner width")
    output: list[int] = []
    for row in left:
        result = 0
        remaining = row
        while remaining:
            bit = remaining & -remaining
            result ^= right[bit.bit_length() - 1]
            remaining ^= bit
        output.append(result & out_mask)
    return tuple(output)


def xor(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    require(len(left) == len(right), "matrix xor: row-count mismatch")
    return tuple(a ^ b for a, b in zip(left, right))


def rank(rows: tuple[int, ...], columns: int) -> int:
    work = list(rows)
    pivot_row = 0
    for column in range(columns):
        pivot = next((i for i in range(pivot_row, len(work))
                      if (work[i] >> column) & 1), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        for i in range(pivot_row + 1, len(work)):
            if (work[i] >> column) & 1:
                work[i] ^= work[pivot_row]
        pivot_row += 1
        if pivot_row == len(work):
            break
    return pivot_row


def inverse(rows: tuple[int, ...], dimension: int, label: str) -> tuple[int, ...]:
    require(len(rows) == dimension, f"{label}: inverse requires a square matrix")
    augmented = [rows[i] | (1 << (dimension + i)) for i in range(dimension)]
    pivot_row = 0
    for column in range(dimension):
        pivot = next((i for i in range(pivot_row, dimension)
                      if (augmented[i] >> column) & 1), None)
        if pivot is None:
            fail(f"{label}: singular pivot")
        augmented[pivot_row], augmented[pivot] = augmented[pivot], augmented[pivot_row]
        for i in range(dimension):
            if i != pivot_row and ((augmented[i] >> column) & 1):
                augmented[i] ^= augmented[pivot_row]
        pivot_row += 1
    right_mask = mask(dimension) << dimension
    return tuple((row & right_mask) >> dimension for row in augmented)


def submatrix(rows: tuple[int, ...], row_start: int, column_start: int,
              row_count: int, column_count: int) -> tuple[int, ...]:
    column_mask = mask(column_count) << column_start
    return tuple((rows[i] & column_mask) >> column_start
                 for i in range(row_start, row_start + row_count))


def matrix_key(rows: tuple[int, ...]) -> tuple[int, ...]:
    return rows


def parse_case(value: Any, index: int) -> dict[str, Any]:
    label = f"fixtures[{index}]"
    require(type(value) is dict, f"{label}: expected an object")
    expected_fields = {"A", "B", "H", "P", "Q"}
    require(set(value) == expected_fields, f"{label}: expected exactly keys {sorted(expected_fields)}")
    parsed: dict[str, Any] = {name: matrix_from_json(value[name], f"{label}.{name}", D)
                              for name in ("A", "B", "H")}
    parsed["P"] = matrix_from_json(value["P"], f"{label}.P")
    parsed["Q"] = matrix_from_json(value["Q"], f"{label}.Q")
    n = len(parsed["P"])
    require(n > D, f"{label}: ambient dimension {n} must exceed d={D}")
    require(len(parsed["Q"]) == n, f"{label}: P and Q dimensions differ")
    parsed["n"] = n
    parsed["label"] = label
    return parsed


def case_key(case: dict[str, Any]) -> tuple[tuple[int, ...], ...]:
    return tuple(matrix_key(case[name]) for name in ("A", "B", "H"))


def exact_case_key(value: Any, index: int) -> tuple[tuple[int, ...], ...]:
    return case_key(parse_case(value, index))


def check_reported_dimension(n: int, minimum: int, label: str) -> None:
    require(n == minimum, f"{label}: ambient dimension {n} does not equal formula value {minimum}")


def check_case(case: dict[str, Any]) -> dict[str, int | bool]:
    label = case["label"]
    n = case["n"]
    m = n - D
    A, B, H = case["A"], case["B"], case["H"]
    P, Q = case["P"], case["Q"]

    A_inv = inverse(A, D, f"{label}.A")
    B_inv = inverse(B, D, f"{label}.B")

    require(matmul(P, P, n) == P, f"{label}: P is not idempotent")
    require(matmul(Q, Q, n) == Q, f"{label}: Q is not idempotent")
    PQ = matmul(P, Q, n)
    QP = matmul(Q, P, n)
    require(PQ == QP, f"{label}: P and Q do not commute")
    require(submatrix(P, 0, 0, D, D) == A, f"{label}: leading block of P differs from A")
    require(submatrix(Q, 0, 0, D, D) == B, f"{label}: leading block of Q differs from B")
    require(submatrix(PQ, 0, 0, D, D) == H,
            f"{label}: leading block of PQ differs from H")

    R = submatrix(P, 0, D, D, m)
    C = submatrix(P, D, 0, m, D)
    D_block = submatrix(P, D, D, m, m)
    L = submatrix(Q, 0, D, D, m)
    E = submatrix(Q, D, 0, m, D)
    F = submatrix(Q, D, D, m, m)
    S = xor(D_block, matmul(matmul(C, A_inv, D), R, m))
    Z = xor(F, matmul(matmul(E, B_inv, D), L, m))
    rank_S = rank(S, m)
    rank_Z = rank(Z, m)
    actual_rank_P = rank(P, n)
    actual_rank_Q = rank(Q, n)
    require(actual_rank_P == D + rank_S,
            f"{label}: rank(P)={actual_rank_P}, Schur elimination gives {D + rank_S}")
    require(actual_rank_Q == D + rank_Z,
            f"{label}: rank(Q)={actual_rank_Q}, Schur elimination gives {D + rank_Z}")
    schur_commutator = xor(matmul(S, Z, m), matmul(Z, S, m))
    commutator_rank = rank(schur_commutator, m)
    require(commutator_rank == 2 * D,
            f"{label}: Schur-complement commutator rank {commutator_rank}, expected {2 * D}")

    null_AH = D - rank(xor(A, H), D)
    null_BH = D - rank(xor(B, H), D)
    null_H = D - rank(H, D)
    expected_rank_P = 2 * D + null_AH + null_H
    expected_rank_Q = 2 * D + null_BH + null_H
    require(actual_rank_P == expected_rank_P,
            f"{label}: rank(P)={actual_rank_P}, formula gives {expected_rank_P}")
    require(actual_rank_Q == expected_rank_Q,
            f"{label}: rank(Q)={actual_rank_Q}, formula gives {expected_rank_Q}")

    identity = tuple(1 << i for i in range(D))
    # In characteristic two, I-A-B+H is I xor A xor B xor H.
    dimension_term = rank(xor(xor(xor(identity, A), B), H), D)
    minimum = 3 * D + dimension_term + null_AH + null_BH + null_H
    check_reported_dimension(n, minimum, label)

    AB, BA = matmul(A, B, D), matmul(B, A, D)
    AH, HA = matmul(A, H, D), matmul(H, A, D)
    BH, HB = matmul(B, H, D), matmul(H, B, D)
    noncommuting_ab = AB != BA
    all_three_noncommuting = noncommuting_ab and AH != HA and BH != HB
    return {
        "minimum": minimum,
        "commutator_rank": commutator_rank,
        "noncommuting_ab": noncommuting_ab,
        "all_three_noncommuting": all_three_noncommuting,
    }


def all_2x2_matrices() -> list[tuple[int, ...]]:
    return [tuple((code >> (2 * row)) & 3 for row in range(D)) for code in range(1 << 4)]


def expected_triples() -> set[tuple[tuple[int, ...], ...]]:
    matrices = all_2x2_matrices()
    invertible = [matrix for matrix in matrices if rank(matrix, D) == D]
    require(len(invertible) == 6, "internal error: GL(2,2) enumeration has wrong size")
    return {(A, B, H) for A in invertible for B in invertible for H in matrices}


def check_exact_coverage(keys: list[tuple[tuple[int, ...], ...]]) -> None:
    expected = expected_triples()
    seen: set[tuple[tuple[int, ...], ...]] = set()
    for index, key in enumerate(keys):
        require(key in expected, f"coverage: unexpected triple at index {index}")
        require(key not in seen, f"coverage: duplicate triple at index {index}")
        seen.add(key)
    missing = expected - seen
    require(not missing, f"coverage: {len(missing)} expected triple(s) missing")
    require(len(seen) == 576, f"coverage: expected 576 distinct triples, got {len(seen)}")


def reject_duplicate_object_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            fail(f"JSON object has duplicate key {key!r}")
        result[key] = value
    return result


def reject_nonfinite_constant(value: str) -> None:
    fail(f"JSON constant {value!r} is not permitted")


def load_document(path: Path) -> dict[str, Any]:
    try:
        size = path.stat().st_size
    except OSError as error:
        fail(f"cannot stat fixture file {path}: {error}")
    require(size <= MAX_FILE_BYTES, f"fixture file exceeds {MAX_FILE_BYTES} bytes")
    try:
        with path.open("rb") as handle:
            raw = handle.read(MAX_FILE_BYTES + 1)
    except OSError as error:
        fail(f"cannot read fixture file {path}: {error}")
    require(len(raw) <= MAX_FILE_BYTES, f"fixture file exceeds {MAX_FILE_BYTES} bytes")
    try:
        source = raw.decode("utf-8")
        document = json.loads(source, object_pairs_hook=reject_duplicate_object_keys,
                              parse_constant=reject_nonfinite_constant)
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as error:
        fail(f"invalid UTF-8 JSON: {error}")
    require(type(document) is dict, "document: expected a JSON object")
    return document


def validate_document(document: Any) -> tuple[int, int, int]:
    require(type(document) is dict, "document: expected a JSON object")
    expected_fields = {"schema_version", "field", "d", "fixtures"}
    require(set(document) == expected_fields,
            f"document: expected exactly keys {sorted(expected_fields)}")
    require(type(document["schema_version"]) is int and document["schema_version"] == 1,
            "document.schema_version must be integer 1")
    require(type(document["field"]) is int and document["field"] == 2,
            "document.field must be integer 2 for GF(2)")
    require(type(document["d"]) is int and document["d"] == D,
            f"document.d must be integer {D}")
    fixtures = document["fixtures"]
    require(type(fixtures) is list, "document.fixtures must be a list")
    require(len(fixtures) == 576, f"document.fixtures must contain 576 entries, got {len(fixtures)}")

    keys: list[tuple[tuple[int, ...], ...]] = []
    noncommuting_ab = 0
    all_three_noncommuting = 0
    for index, value in enumerate(fixtures):
        case = parse_case(value, index)
        keys.append(case_key(case))
        result = check_case(case)
        noncommuting_ab += int(result["noncommuting_ab"])
        all_three_noncommuting += int(result["all_three_noncommuting"])
    check_exact_coverage(keys)
    return len(fixtures), noncommuting_ab, all_three_noncommuting


def expect_rejected(label: str, operation: Callable[[], Any]) -> None:
    try:
        operation()
    except CheckError:
        return
    fail(f"rejection control accepted invalid input: {label}")


def run_rejection_controls(document: dict[str, Any]) -> int:
    first = parse_case(document["fixtures"][0], 0)
    first_raw = document["fixtures"][0]

    mutated_p = json.loads(json.dumps(first_raw))
    mutated_p["P"][0][0] ^= 1
    expect_rejected("mutated P", lambda: check_case(parse_case(mutated_p, 0)))

    altered_h = json.loads(json.dumps(first_raw))
    altered_h["H"][0][0] ^= 1
    expect_rejected("altered H", lambda: check_case(parse_case(altered_h, 0)))

    expect_rejected("falsely reduced minimum",
                     lambda: check_reported_dimension(first["n"] - 1,
                                                      check_case(first)["minimum"],
                                                      "reduced-minimum control"))

    truncated = json.loads(json.dumps(first_raw))
    for name in ("P", "Q"):
        truncated[name] = [row[:-1] for row in truncated[name][:-1]]
    expect_rejected("truncated P,Q", lambda: check_case(parse_case(truncated, 0)))

    singular = json.loads(json.dumps(first_raw))
    singular["A"] = [[0, 0], [0, 0]]
    expect_rejected("singular A pivot", lambda: check_case(parse_case(singular, 0)))

    keys = [exact_case_key(value, index) for index, value in enumerate(document["fixtures"])]
    duplicate_and_missing = list(keys)
    duplicate_and_missing[-1] = duplicate_and_missing[0]
    expect_rejected("duplicate/missing triple", lambda: check_exact_coverage(duplicate_and_missing))
    expect_rejected("missing triple", lambda: check_exact_coverage(keys[:-1]))
    return 7


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", type=Path, default=DEFAULT_FIXTURES,
                        help=f"fixture JSON path (default: {DEFAULT_FIXTURES})")
    arguments = parser.parse_args(argv)
    try:
        document = load_document(arguments.fixtures)
        count, noncommuting_ab, all_three_noncommuting = validate_document(document)
        controls = run_rejection_controls(document)
    except CheckError as error:
        print(f"FAIL_BINARY_ARBITRARY_PIVOT: {error}", file=sys.stderr)
        return 1
    print("PASS_BINARY_ARBITRARY_PIVOT "
          f"fixtures={count} noncommuting_AB={noncommuting_ab} "
          f"pairwise_noncommuting_ABH={all_three_noncommuting} controls={controls}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
