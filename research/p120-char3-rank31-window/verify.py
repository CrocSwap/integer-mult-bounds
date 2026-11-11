#!/usr/bin/env python3
"""Check a fixed-space P120 obstruction and one rank-31 pattern, without Git."""

import hashlib
import json
from pathlib import Path
import time

PACKAGE = Path(__file__).resolve().parent
ORDER = 120
RANK = 31
MAX_ARTIFACT_BYTES = 65536


def require(condition, message):
    if not condition:
        raise ValueError(message)


def vertices():
    return [v for v in range(512) if v.bit_count() % 4 == 3]


def validate_matrix(matrix, rows, columns):
    require(type(matrix) is list and len(matrix) == rows, "matrix row count")
    for row in matrix:
        require(type(row) is list and len(row) == columns, "matrix width")
        require(all(type(x) is int and 0 <= x < 3 for x in row), "field entry")


def validate_indices(indices, size=RANK):
    require(type(indices) is list and len(indices) == size, "minor index count")
    require(all(type(i) is int and 0 <= i < ORDER for i in indices), "minor index")
    require(len(set(indices)) == size, "minor repeated index")


def validate_artifact(data):
    require(type(data) is dict, "artifact object")
    require(data.get("schema") == "p120-f3-rank-factorization/1", "schema")
    require(type(data.get("field_order")) is int and data["field_order"] == 3, "field")
    require(type(data.get("rank")) is int and data["rank"] == RANK, "rank")
    require(data.get("vertex_order") ==
            "ascending integers v in [0,512) with bit_count(v) mod 4 = 3", "order")
    validate_matrix(data.get("left"), ORDER, RANK)
    validate_matrix(data.get("right"), RANK, ORDER)
    validate_indices(data.get("minor_rows"))
    validate_indices(data.get("minor_columns"))
    require(data.get("space") ==
            "span(x_i+x_8-1, x_i*x_j+1-x_8 : 0<=i<8, 0<=i<j<8) over F3", "space")
    validate_matrix(data.get("left_in_space"), 36, RANK)
    validate_matrix(data.get("forced_coefficients"), 16, 36)
    require(type(data.get("constraint_minor_rows")) is list and
            len(data["constraint_minor_rows"]) == 16, "constraint minor count")
    for indices in data["constraint_minor_rows"]:
        validate_indices(indices, 36)
    validate_indices(data.get("forced_minor_rows"), 16)
    labels = data.get("forced_vertices")
    require(type(labels) is list and len(labels) == len(set(labels)) == 16,
            "forced vertex count")
    require(all(type(v) is int and v in vertices() for v in labels), "forced vertex")


def product(left, right):
    return [[sum(left[i][t] * right[t][j] for t in range(RANK)) % 3
             for j in range(ORDER)] for i in range(ORDER)]


def mask_counts(matrix, ports):
    validate_matrix(matrix, ORDER, ORDER)
    diagonal = 0
    forced_zeros = 0
    for i in range(ORDER):
        require(matrix[i][i] == 1, "nonunit diagonal")
        diagonal += 1
        for j in range(ORDER):
            if (ports[i] & ports[j]).bit_count() % 2 == 0:
                require(matrix[i][j] == 0, "orthogonal entry")
                forced_zeros += 1
    return diagonal, forced_zeros


def determinant(matrix):
    """Independent square elimination, with row swaps and all arithmetic in F3."""
    n = len(matrix)
    require(1 <= n <= ORDER and all(len(row) == n for row in matrix), "square")
    work = [row[:] for row in matrix]
    result = 1
    for col in range(n):
        pivot = next((r for r in range(col, n) if work[r][col] % 3), None)
        if pivot is None:
            return 0
        if pivot != col:
            work[col], work[pivot] = work[pivot], work[col]
            result = -result % 3
        value = work[col][col] % 3
        result = result * value % 3
        for r in range(col + 1, n):
            scale = work[r][col] * value % 3
            for c in range(col, n):
                work[r][c] = (work[r][c] - scale * work[col][c]) % 3
    return result


def rank_checks(data, matrix):
    rows, cols = data["minor_rows"], data["minor_columns"]
    left = [data["left"][i][:] for i in rows]
    right = [[data["right"][i][j] for j in cols] for i in range(RANK)]
    minor = [[matrix[i][j] for j in cols] for i in rows]
    det_left, det_right, det_minor = map(determinant, (left, right, minor))
    require(det_left != 0 and det_right != 0, "singular factor minor")
    require(det_minor == det_left * det_right % 3 and det_minor != 0,
            "singular product minor")
    return det_left, det_right, det_minor


def feature_rows(ports):
    rows = []
    for v in ports:
        x = [(v >> i) & 1 for i in range(9)]
        row = [(x[i] + x[8] - 1) % 3 for i in range(8)]
        row += [(x[i] * x[j] + 1 - x[8]) % 3
                for i in range(8) for j in range(i + 1, 8)]
        rows.append(row)
    return rows


def obstruction_checks(data, ports):
    features = feature_rows(ports)
    coordinates = data["left_in_space"]
    for i in range(ORDER):
        for j in range(RANK):
            value = sum(features[i][t] * coordinates[t][j] for t in range(36)) % 3
            require(value == data["left"][i][j], "factor outside fixed space")
    forced = [[sum(row[t] * c[t] for t in range(36)) % 3
               for c in data["forced_coefficients"]] for row in features]
    constraint_dets = []
    equations = 0
    for j, vertex in enumerate(data["forced_vertices"]):
        index = ports.index(vertex)
        for i in range(ORDER):
            orthogonal = (ports[i] & vertex).bit_count() % 2 == 0
            if orthogonal or i == index:
                require(forced[i][j] == int(i == index), "illegal forced column")
                equations += 1
        chosen = data["constraint_minor_rows"][j]
        require(all(i == index or (ports[i] & vertex).bit_count() % 2 == 0
                    for i in chosen), "minor uses an unconstrained row")
        det = determinant([features[i] for i in chosen])
        require(det != 0, "forced column not unique")
        constraint_dets.append(det)
    det = determinant([forced[i] for i in data["forced_minor_rows"]])
    require(det != 0, "dependent forced columns")
    return {"forced_columns": len(data["forced_vertices"]),
            "forced_equations": equations, "forced_independence_det": det,
            "uniqueness_determinants": constraint_dets,
            "factor_membership_entries": ORDER * RANK}


def rejects(call, *args):
    try:
        call(*args)
    except ValueError:
        return 1
    raise ValueError("negative control was accepted")


def controls(data, matrix, ports):
    count = 0
    changed = [row[:] for row in matrix]
    changed[0][0] = 0
    count += rejects(mask_counts, changed, ports)
    orthogonal = next(j for j in range(ORDER)
                      if (ports[0] & ports[j]).bit_count() % 2 == 0)
    changed = [row[:] for row in matrix]
    changed[0][orthogonal] = 1
    count += rejects(mask_counts, changed, ports)
    changed = [row[:] for row in matrix]
    changed[0][0] = 3
    count += rejects(mask_counts, changed, ports)
    changed = dict(data)
    changed["minor_rows"] = [data["minor_rows"][0]] * RANK
    count += rejects(validate_artifact, changed)
    changed = dict(data)
    changed["left"] = [row[:-1] for row in data["left"]]
    count += rejects(validate_artifact, changed)
    changed = dict(data)
    changed["field_order"] = True
    count += rejects(validate_artifact, changed)
    changed = dict(data)
    changed["left"] = [[0] * RANK for _ in range(ORDER)]
    count += rejects(rank_checks, changed, matrix)
    require(determinant([[1, 0], [0, 1]]) == 1, "identity determinant")
    require(determinant([[0, 1], [1, 0]]) == 2, "swap determinant")
    require(determinant([[1, 2], [2, 1]]) == 0, "singular determinant")
    changed = dict(data)
    changed["left_in_space"] = [[0] * RANK for _ in range(36)]
    count += rejects(obstruction_checks, changed, ports)
    changed = dict(data)
    changed["forced_coefficients"] = [[0] * 36 for _ in range(16)]
    count += rejects(obstruction_checks, changed, ports)
    changed = dict(data)
    changed["forced_minor_rows"] = [data["forced_minor_rows"][0]] * 16
    count += rejects(obstruction_checks, changed, ports)
    changed = dict(data)
    indices = [row[:] for row in data["constraint_minor_rows"]]
    indices[0] = [indices[0][0]] * 36
    changed["constraint_minor_rows"] = indices
    count += rejects(obstruction_checks, changed, ports)
    return count


def main():
    started = time.monotonic()
    with (PACKAGE / "FACTOR.json").open("rb") as stream:
        raw = stream.read(MAX_ARTIFACT_BYTES + 1)
    require(len(raw) <= MAX_ARTIFACT_BYTES, "artifact size")
    data = json.loads(raw)
    validate_artifact(data)
    ports = vertices()
    require(len(ports) == ORDER, "port count")
    matrix = product(data["left"], data["right"])
    diagonal, forced = mask_counts(matrix, ports)
    dets = rank_checks(data, matrix)
    obstruction = obstruction_checks(data, ports)
    rejected = controls(data, matrix, ports)
    # Receipt is generated from the actual checked artifact and package sources.
    names = ("README.md", "PROOF.md", "NOTICE", "TASK.json", "SOURCES.json",
             "VERIFY.json", "verify.py", "FACTOR.json")
    hashes = {name: hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest()
              for name in names}
    receipt = {"claim_type": "finite certificate with scoped proof", "field": 3, "rank": RANK,
               "fixed_space_obstruction": obstruction,
               "ports": len(ports), "product_entries": sum(map(len, matrix)),
               "diagonal_entries": diagonal, "forced_zero_entries": forced,
               "determinants": dets, "rejected_controls": rejected,
               "matrix_sha256": hashlib.sha256(bytes(x for row in matrix for x in row)).hexdigest(),
               "sources_sha256": hashes}
    print(json.dumps(receipt, sort_keys=True))
    print("PASS_P120_CHAR3_RANK31 no_new_kappa")
    print("elapsed_seconds=%.6f" % (time.monotonic() - started))


if __name__ == "__main__":
    main()
