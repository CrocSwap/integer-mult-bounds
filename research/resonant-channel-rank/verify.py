#!/usr/bin/env python3
"""Exact width-four rank of the frozen resonant partial target coefficient."""

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE_SHA = "a0fe212792f1bffca701a01185b89596ff03bb7fccf5b71accf63a92ca07fd4d"
TARGET_SHA = "445b3e5f8edb6f345981c02c1feb91f2ce473763be74ca7d949421e1ca64d03d"
WIDTH, DIMENSION, TERMS = 4, 4096, 256


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_bytes(name):
    path = HERE / name
    require(path.stat().st_size <= 512 * 1024, "input size cap: " + name)
    return path.read_bytes()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def validate_records(records):
    require(isinstance(records, list) and len(records) == TERMS, "target term count")
    for record in records:
        require(record["coefficient"] in ("1/16", "-1/16"), "target coefficient")
        require(sorted(record["permutation"]) == list(range(8)), "base permutation")
        phases = record["phase_i"]
        require(len(phases) == 8 and all(type(x) is int and 0 <= x < 4 for x in phases),
                "base phases")


def load_records():
    source_bytes = read_bytes("SOURCE-RESULT.json")
    require(hashlib.sha256(source_bytes).hexdigest() == SOURCE_SHA, "source receipt bytes")
    source = json.loads(source_bytes)
    require(source["target_coefficient_sha256"] == TARGET_SHA, "source target digest")
    records = json.loads(read_bytes("TARGET.json"))
    validate_records(records)
    require(digest(records) == TARGET_SHA, "exported target digest")
    return records


def tensor_rows(records):
    """Evaluate each actual word at width four, retaining its coefficient once."""
    rows = {}
    units = ((1, 0), (0, 1), (-1, 0), (0, -1))
    for column in range(DIMENSION):
        entries = {}
        for record in records:
            rest, destination, phase, place = column, 0, 0, 1
            for _ in range(WIDTH):
                digit, rest = rest % 8, rest // 8
                destination += place * record["permutation"][digit]
                place *= 8
                phase += record["phase_i"][digit]
            real, imag = units[phase % 4]
            sign = 1 if record["coefficient"] == "1/16" else -1
            old_real, old_imag = entries.get(destination, (0, 0))
            entries[destination] = old_real + sign * real, old_imag + sign * imag
        for row, (real, imag) in entries.items():
            require(imag == 0 and real % 16 == 0, "real integral width-four coefficient")
            if real:
                rows.setdefault(row, {})[column] = real // 16
    return rows


def row_reduce(rows):
    """Exact echelon reduction supplies an upper bound and selects a minor."""
    pivots, basis_rows, basis_columns = {}, [], []
    reductions = 0
    for label, original in sorted(rows.items()):
        row = {column: Fraction(value) for column, value in original.items()}
        for _ in range(DIMENSION + 1):
            if not row:
                break
            column = min(row)
            if column not in pivots:
                divisor = row[column]
                pivots[column] = {key: value / divisor for key, value in row.items()}
                basis_rows.append(label)
                basis_columns.append(column)
                break
            multiplier = row[column]
            for key, value in pivots[column].items():
                updated = row.get(key, Fraction(0)) - multiplier * value
                if updated:
                    row[key] = updated
                else:
                    row.pop(key, None)
            reductions += 1
        else:
            raise ValueError("row-reduction iteration bound")
    return basis_rows, basis_columns, reductions


def determinant(matrix):
    """Integer Bareiss elimination, independent of the rational upper bound."""
    size = len(matrix)
    require(1 <= size <= 100 and all(len(row) == size for row in matrix), "minor shape")
    work = [row[:] for row in matrix]
    previous, sign = 1, 1
    for column in range(size - 1):
        pivot_row = next((r for r in range(column, size) if work[r][column]), None)
        if pivot_row is None:
            return 0
        if pivot_row != column:
            work[column], work[pivot_row] = work[pivot_row], work[column]
            sign = -sign
        pivot = work[column][column]
        for row in range(column + 1, size):
            for key in range(column + 1, size):
                numerator = work[row][key] * pivot - work[row][column] * work[column][key]
                quotient, remainder = divmod(numerator, previous)
                require(remainder == 0, "Bareiss exact division")
                work[row][key] = quotient
            work[row][column] = 0
        previous = pivot
    return sign * work[-1][-1]


def controls(records, minor, minor_det):
    rejected = []
    for name, field, bad in (("invalid_permutation", "permutation", [0] * 8),
                             ("invalid_phase", "phase_i", [4] * 8),
                             ("invalid_coefficient", "coefficient", "1/8")):
        mutant = [dict(record) for record in records]
        mutant[0][field] = bad
        try:
            validate_records(mutant)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("accepted malformed target: " + name)
    duplicate = [row[:] for row in minor]
    duplicate[1] = duplicate[0][:]
    require(determinant(duplicate) == 0, "duplicated-row control")
    rejected.append("duplicated_minor_row")
    swapped = [row[:] for row in minor]
    swapped[0], swapped[1] = swapped[1], swapped[0]
    require(determinant(swapped) == -minor_det, "minor orientation control")
    rejected.append("wrong_minor_orientation")
    changed = [dict(record) for record in records]
    changed[0]["coefficient"] = "-1/16" if changed[0]["coefficient"] == "1/16" else "1/16"
    require(digest(changed) != TARGET_SHA, "changed valid coefficient digest")
    rejected.append("changed_valid_coefficient_digest")
    return rejected


def verify():
    records = load_records()
    rows = tensor_rows(records)
    basis_rows, basis_columns, reductions = row_reduce(rows)
    rank = len(basis_rows)
    require(rank == 100, "exact upper rank")
    minor = [[rows[row].get(column, 0) for column in basis_columns] for row in basis_rows]
    minor_det = determinant(minor)
    require(minor_det != 0, "exact lower rank")
    canonical = [[row, sorted(values.items())] for row, values in sorted(rows.items())]
    return {"status": "PASS_RESONANT_CHANNEL_RANK", "claim_type": "finite certificate",
            "width": WIDTH, "dimension": DIMENSION, "rank": rank,
            "source_receipt_sha256": SOURCE_SHA, "target_coefficient_sha256": TARGET_SHA,
            "matrix_sha256": digest(canonical), "nonzero_rows": len(rows),
            "nonzero_columns": len({c for values in rows.values() for c in values}),
            "nonzero_entries": sum(map(len, rows.values())), "exact_row_reductions": reductions,
            "minor_rows": basis_rows, "minor_columns": basis_columns,
            "minor_determinant": str(minor_det),
            "rejection_controls": controls(records, minor, minor_det)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-result", action="store_true", help="print generated result JSON")
    args = parser.parse_args()
    result = verify()
    if args.emit_result:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    require(json.loads(read_bytes("RESULT.json")) == result, "frozen generated result")
    names = ("README.md", "RESULT.json", "SOURCE-RESULT.json", "SOURCES.json",
             "TARGET.json", "TASK.json", "VERIFY.json", "verify.py")
    hashes = {name: hashlib.sha256(read_bytes(name)).hexdigest() for name in names}
    print(json.dumps({"status": result["status"], "rank": result["rank"],
                      "dimension": DIMENSION, "file_sha256": hashes}, sort_keys=True))


if __name__ == "__main__":
    main()
