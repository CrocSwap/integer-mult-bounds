#!/usr/bin/env python3
"""Independent exact row-span oracle for the pinned jf0 pairing problem.

This implementation uses set closure under XOR, not Gaussian elimination or
predecessor routines.  The fixed witness is an input: missing files are errors.
It checks a finite matrix completion, not circuit realizability or an exponent.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE_SHA256 = "cd8a8c2436e0a025348af0b52ccb48a4f64535b0ff8df32cbe13da73673266b7"
SOURCE_HEAD = "113a718265c62aec301c5695f4bfb9c421bef7ab"
SOURCE_PATH = "research/char2-jets/data/jf0.json"


def _rational(value: object) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, str, Fraction)):
        raise ValueError("source entries must be exact rational values")
    try:
        return Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError("invalid exact rational source entry") from exc


def _source_rows(rows: object) -> list[list[Fraction]]:
    if not isinstance(rows, (list, tuple)) or len(rows) != 11:
        raise ValueError("the pinned problem requires eleven source rows")
    result = []
    for row in rows:
        if not isinstance(row, (list, tuple)) or len(row) != 3:
            raise ValueError("the pinned problem requires three coordinates")
        result.append([_rational(value) for value in row])
    return result


def _matrix_rows(matrix: object) -> list[list[int]]:
    if not isinstance(matrix, (list, tuple)) or len(matrix) != 11:
        raise ValueError("the pairing matrix must have eleven rows")
    result = []
    for row in matrix:
        if not isinstance(row, (list, tuple)) or len(row) != 11:
            raise ValueError("the pairing matrix must have eleven columns")
        if any(type(value) is not int or value not in (0, 1) for value in row):
            raise ValueError("pairing entries must be binary integers")
        result.append(list(row))
    return result


def row_span(words: list[int]) -> set[int]:
    """Enumerate the full binary row span by finite additive set closure."""
    span = {0}
    for word in words:
        span = span.union({value ^ word for value in span})
    return span


def inspect(P: object, Q: object, B: object) -> dict:
    """Validate all entries and return exact supports and complete row spans."""
    p, q, b = _source_rows(P), _source_rows(Q), _matrix_rows(B)
    allowed = []
    for i in range(11):
        if sum(p[i][k] * q[i][k] for k in range(3)) == 0:
            raise ValueError("source requires a nonzero rational diagonal")
        if b[i][i] != 1:
            raise ValueError("pairing diagonal must equal one")
        for j in range(11):
            if i == j:
                continue
            zero = sum(p[i][k] * q[j][k] for k in range(3)) == 0
            if zero:
                allowed.append([i, j])
            elif b[i][j]:
                raise ValueError(f"nonzero rational pairing forbids B[{i}][{j}]=1")
    blocks = []
    relevant = set()
    for coordinate in range(3):
        rows = [i for i in range(11) if p[i][coordinate] != 0]
        columns = [j for j in range(11) if q[j][coordinate] != 0]
        words = [sum(b[i][j] << bit for bit, j in enumerate(columns)) for i in rows]
        span = row_span(words)
        cardinality = len(span)
        if cardinality & (cardinality - 1):
            raise ValueError("binary row-span cardinality is not a power of two")
        blocks.append({
            "coordinate": coordinate,
            "rows": rows,
            "columns": columns,
            "row_words": words,
            "span_cardinality": cardinality,
            "rank": cardinality.bit_length() - 1,
        })
        relevant.update((i, j) for i, j in allowed if i in rows and j in columns)
    return {
        "allowed_offdiagonal_positions": allowed,
        "relevant_offdiagonal_positions": [list(pair) for pair in sorted(relevant)],
        "blocks": blocks,
        "ranks": [block["rank"] for block in blocks],
        "total": sum(block["rank"] for block in blocks),
    }


def evaluate(P: object, Q: object, B: object) -> tuple[int, int, int]:
    """Return the three exact ranks; reject malformed or inadmissible input."""
    return tuple(inspect(P, Q, B)["ranks"])


def _check_reciprocal_pairs(pairs: object, matrix: object) -> None:
    """Bind the sparse descriptive witness to exactly the supplied matrix."""
    if not isinstance(pairs, list):
        raise ValueError("reciprocal_pairs must be a list")
    described = [[int(i == j) for j in range(11)] for i in range(11)]
    used = set()
    for pair in pairs:
        if not isinstance(pair, list) or len(pair) != 2:
            raise ValueError("each reciprocal pair must contain two indices")
        if any(type(index) is not int or not 0 <= index < 11 for index in pair):
            raise ValueError("reciprocal pair indices must be integers in range")
        i, j = pair
        if i == j or i in used or j in used:
            raise ValueError("reciprocal pair indices must be distinct and disjoint")
        used.update(pair)
        described[i][j] = described[j][i] = 1
    if described != matrix:
        raise ValueError("reciprocal_pairs must describe exactly binary_matrix")


def verify(source_path: Path | str, witness_path: Path | str) -> dict:
    """Replay the immutable source and the supplied, already-existing witness."""
    source_bytes = Path(source_path).read_bytes()
    source_hash = hashlib.sha256(source_bytes).hexdigest()
    if source_hash != SOURCE_SHA256:
        raise ValueError("source byte hash does not match the pinned jf0 object")
    source = json.loads(source_bytes)
    if not isinstance(source, list) or len(source) != 2:
        raise ValueError("source must contain exactly [P, Q]")
    witness = json.loads(Path(witness_path).read_bytes())
    if not isinstance(witness, dict):
        raise ValueError("witness must be an object")
    origin = witness.get("source")
    if not isinstance(origin, dict):
        raise ValueError("witness source metadata must be an object")
    if origin.get("sha256") != SOURCE_SHA256:
        raise ValueError("witness source hash is not the pinned hash")
    if origin.get("head") != SOURCE_HEAD:
        raise ValueError("witness predecessor head is not the pinned head")
    if origin.get("path") != SOURCE_PATH:
        raise ValueError("witness predecessor path is not the canonical source path")
    result = inspect(source[0], source[1], witness["binary_matrix"])
    _check_reciprocal_pairs(witness.get("reciprocal_pairs"), witness["binary_matrix"])
    if witness.get("expected_ranks") != result["ranks"]:
        raise ValueError("declared ranks disagree with complete row-span enumeration")
    if witness.get("expected_total") != result["total"]:
        raise ValueError("declared total disagrees with complete row-span enumeration")
    if witness.get("row_span_witness") != result["blocks"]:
        raise ValueError("declared row-span witness disagrees with the computed blocks")
    if len(result["allowed_offdiagonal_positions"]) != 41:
        raise ValueError("pinned object must have 41 admissible offdiagonal positions")
    if result["relevant_offdiagonal_positions"] != result["allowed_offdiagonal_positions"]:
        raise ValueError("pinned object must have no objective-irrelevant free position")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=HERE / "source" / "jf0.json")
    parser.add_argument("--witness", type=Path, default=HERE / "candidate-witness.json")
    args = parser.parse_args()
    result = verify(args.source, args.witness)
    print(json.dumps({
        "status": "PASS_JF0_INDEPENDENT_ROW_SPAN",
        "ranks": result["ranks"],
        "span_cardinalities": [block["span_cardinality"] for block in result["blocks"]],
        "total": result["total"],
        "allowed_bits": len(result["allowed_offdiagonal_positions"]),
        "objective_relevant_bits": len(result["relevant_offdiagonal_positions"]),
        "source_sha256": SOURCE_SHA256,
        "no_new_kappa": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
