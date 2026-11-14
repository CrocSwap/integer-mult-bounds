#!/usr/bin/env python3
"""Independent exact checker for the radius-five Gaussian rounding claim.

Only Python's standard library and the compressed certificate beside this
file are used. No search, optimizer, or author checker is imported.
"""

from __future__ import annotations

import gzip
import hashlib
import itertools
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "R5-OPTIMUM.json.gz"
RAW_SHA256 = "b1fe3d866d2184227f46ec73ec2021c546bba056e98077e657e9205d9db5ad8b"
PACKED_SHA256 = "d26f615aacff4b082c316e491aa1730aabc9cb6ceb377d33fb9a279b2d7f5f16"


def require(condition: bool, explanation: str) -> None:
    if not condition:
        raise RuntimeError(explanation)


def unpack_certificate(packed: bytes) -> tuple[bytes, dict]:
    require(hashlib.sha256(packed).hexdigest() == PACKED_SHA256,
            "compressed certificate SHA-256 mismatch")
    raw = gzip.decompress(packed)
    authenticate_expansion(raw)
    decoded = json.loads(raw)
    require(isinstance(decoded, dict), "certificate root must be an object")
    return raw, decoded


def authenticate_expansion(raw: bytes) -> None:
    require(hashlib.sha256(raw).hexdigest() == RAW_SHA256,
            "expanded certificate SHA-256 mismatch")


def sqnorm(vector: tuple[int, ...] | list[int]) -> int:
    return sum(value * value for value in vector)


def ceil_div(numerator: int, denominator: int) -> int:
    return -((-numerator) // denominator)


def dot_row(row: list[int], vector: tuple[int, ...]) -> int:
    return sum(a * b for a, b in zip(row, vector))


def matmul(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    return [
        [sum(left[i][k] * right[k][j] for k in range(len(right)))
         for j in range(len(right[0]))]
        for i in range(len(left))
    ]


def transpose(matrix: list[list[int]]) -> list[list[int]]:
    return [list(column) for column in zip(*matrix)]


def sum_sqrt_le(a: int, b: int, c: int, d: int) -> bool:
    """Decide sqrt(a)+sqrt(b) <= sqrt(c)+sqrt(d) by integer arithmetic."""
    require(min(a, b, c, d) >= 0, "negative square-root radicand")
    k = c + d - a - b
    p = a * b
    q = c * d
    # The comparison is 2(sqrt(p)-sqrt(q)) <= k.
    if k >= 0:
        if p <= q:
            return True
        if k == 0:
            return False
        e = 4 * (p - q) - k * k
        if e <= 0:
            return True
        return e * e <= 16 * k * k * q
    r = -k
    e = 4 * (q - p) - r * r
    if e < 0:
        return False
    return e * e >= 16 * r * r * p


def compare_gaps(m: int, n: int, a: int, b: int) -> int:
    """Return sign of (sqrt(m)-sqrt(n))-(sqrt(a)-sqrt(b))."""
    left_le = sum_sqrt_le(m, b, a, n)
    right_le = sum_sqrt_le(a, n, m, b)
    require(left_le or right_le, "exact radical order comparison is inconsistent")
    if left_le and right_le:
        return 0
    return -1 if left_le else 1


def parse_vector(raw, label: str) -> tuple[int, int, int, int]:
    require(isinstance(raw, list) and len(raw) == 4,
            f"{label} must have four coordinates")
    require(all(type(value) is int for value in raw),
            f"{label} coordinates must be integers")
    return tuple(raw)  # type: ignore[return-value]


def error_numerator(x: tuple[int, ...], y: tuple[int, ...],
                    matrix: list[list[int]]) -> int:
    """Four times ||y-Hx/2||^2, with no rounding."""
    hx = [dot_row(row, x) for row in matrix]
    return sum((2 * y[i] - hx[i]) ** 2 for i in range(4))


def all_error_one_outputs(x: tuple[int, ...], matrix: list[list[int]]):
    """Enumerate every integer y with ||y-Hx/2|| <= 1."""
    hx = [dot_row(row, x) for row in matrix]
    intervals = [
        range(ceil_div(value - 2, 2), (value + 2) // 2 + 1)
        for value in hx
    ]
    for y_raw in itertools.product(*intervals):
        y = tuple(y_raw)
        error = sum((2 * y[i] - hx[i]) ** 2 for i in range(4))
        if error <= 4:
            yield y, error


def validate_matching(pairs, inputs: set[tuple[int, ...]],
                      matrix: list[list[int]]) -> dict:
    seen_inputs: set[tuple[int, ...]] = set()
    seen_outputs: set[tuple[int, ...]] = set()
    boundary_edges = 0
    threshold_edges = 0
    for raw_pair in pairs:
        require(isinstance(raw_pair, list) and len(raw_pair) == 2,
                "matching entry must be an input/output pair")
        x = parse_vector(raw_pair[0], "matching input")
        y = parse_vector(raw_pair[1], "matching output")
        require(x in inputs, "matching input is outside S5")
        require(x not in seen_inputs, "matching repeats an input")
        require(y not in seen_outputs, "matching outputs are not injective")
        seen_inputs.add(x)
        seen_outputs.add(y)
        error = error_numerator(x, y, matrix)
        require(error <= 4, "matching edge exceeds error bound one")
        boundary_edges += int(error == 4)
        sign = compare_gaps(sqnorm(y), sqnorm(x), 21, 19)
        require(sign <= 0, "matching outward increment exceeds beta")
        threshold_edges += int(sign == 0)
    require(seen_inputs == inputs, "matching does not cover every S5 input")
    require(len(seen_outputs) == 3121, "matching output count is not 3121")
    require(threshold_edges == 58,
            "certificate should have 58 edges attaining beta")
    return {
        "size": len(seen_outputs),
        "error_boundary_edges": boundary_edges,
        "beta_edges": threshold_edges,
    }


def signed_permutation(matrix: list[list[int]]) -> bool:
    return (
        len(matrix) == 4
        and all(len(row) == 4 for row in matrix)
        and all(sum(abs(value) for value in row) == 1 for row in matrix)
        and all(sum(abs(matrix[i][j]) for i in range(4)) == 1
                for j in range(4))
    )


def validate_native_transfer(matrix: list[list[int]]) -> None:
    cplus = [
        [1, -1, 1, 1],
        [1, 1, -1, 1],
        [1, 1, 1, -1],
        [-1, 1, 1, 1],
    ]
    left = [
        [1, 0, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, -1],
        [0, 1, 0, 0],
    ]
    right = [
        [1, 0, 0, 0],
        [0, -1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ]
    identity = [[int(i == j) for j in range(4)] for i in range(4)]
    require(signed_permutation(left) and signed_permutation(right),
            "native transfer matrices are not signed permutations")
    require(matmul(left, transpose(left)) == identity
            and matmul(right, transpose(right)) == identity,
            "native transfer does not preserve Euclidean norm")
    require(matmul(matmul(left, cplus), right) == matrix,
            "exact H4=L(2C_+)R identity failed")
    conjugation = [
        [1, 0, 0, 0],
        [0, -1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, -1],
    ]
    cminus = matmul(matmul(conjugation, cplus), conjugation)
    expected_cminus = [
        [1, 1, 1, -1],
        [-1, 1, 1, 1],
        [1, -1, 1, 1],
        [1, 1, -1, 1],
    ]
    require(signed_permutation(conjugation),
            "complex conjugation is not a lattice isometry")
    require(cminus == expected_cminus,
            "complex conjugation does not transfer C+ to C-")


def validate_certificate(document: dict) -> dict:
    matrix = document.get("matrix_numerator")
    expected_matrix = [
        [1, 1, 1, 1],
        [1, -1, 1, -1],
        [1, 1, -1, -1],
        [1, -1, -1, 1],
    ]
    require(matrix == expected_matrix, "certificate matrix is not the stated H4")
    require(document.get("denominator") == 2
            and document.get("radius") == 5
            and document.get("inputs") == 3121
            and document.get("error_bound_squared") == 1,
            "certificate domain/error cap differs from the theorem")
    for i in range(4):
        for j in range(4):
            dot = sum(matrix[k][i] * matrix[k][j] for k in range(4))
            require(dot == (4 if i == j else 0),
                    "H4 columns fail H^T H=4I")
    validate_native_transfer(matrix)

    inputs = {
        vector for vector in itertools.product(range(-5, 6), repeat=4)
        if sqnorm(vector) <= 25
    }
    require(len(inputs) == 3121, "independent S5 enumeration has wrong size")
    beta = document.get("threshold_pair")
    require(beta == [21, 19]
            and document.get("threshold_expression") == "sqrt(21)-sqrt(19)",
            "certificate threshold is not beta=sqrt(21)-sqrt(19)")
    require(compare_gaps(21, 19, 21, 19) == 0,
            "exact beta equality control failed")

    matching = document.get("matching")
    require(isinstance(matching, list), "certificate matching is absent")
    matching_receipt = validate_matching(matching, inputs, matrix)

    hall = document.get("hall")
    require(isinstance(hall, dict), "Hall witness is absent")
    raw_hall_inputs = hall.get("input_set")
    raw_declared_neighbors = hall.get("output_neighbors")
    require(isinstance(raw_hall_inputs, list)
            and isinstance(raw_declared_neighbors, list),
            "Hall witness fields are malformed")
    hall_inputs = {parse_vector(value, "Hall input") for value in raw_hall_inputs}
    declared_neighbors = {
        parse_vector(value, "declared Hall output")
        for value in raw_declared_neighbors
    }
    require(len(hall_inputs) == 1692 and len(raw_hall_inputs) == 1692,
            "Hall input set must have 1692 distinct points")
    require(hall_inputs <= inputs, "Hall input set leaves the complete S5 ball")
    require(len(declared_neighbors) == 1691
            and len(raw_declared_neighbors) == 1691,
            "declared strict-beta neighborhood must have 1691 distinct points")

    actual_neighbors: set[tuple[int, ...]] = set()
    inclusive_neighbors: set[tuple[int, ...]] = set()
    strict_error_neighbors: set[tuple[int, ...]] = set()
    boundary_candidates = 0
    for x in hall_inputs:
        norm_x = sqnorm(x)
        for y, error in all_error_one_outputs(x, matrix):
            boundary_candidates += int(error == 4)
            sign = compare_gaps(sqnorm(y), norm_x, 21, 19)
            if sign < 0:
                actual_neighbors.add(y)
                if error < 4:
                    strict_error_neighbors.add(y)
            if sign <= 0:
                inclusive_neighbors.add(y)
    require(actual_neighbors == declared_neighbors,
            "declared Hall set differs from the complete strict-beta neighborhood")
    require(len(actual_neighbors) == 1691 < len(hall_inputs),
            "strict-beta graph violates no Hall deficiency")
    require(inclusive_neighbors > actual_neighbors,
            "tie-inclusive negative control did not add beta equality outputs")
    require(boundary_candidates > 0,
            "error-boundary negative control has no boundary candidates")
    require(strict_error_neighbors != actual_neighbors,
            "strict-error mutant did not remove a strict-beta output")

    # Negative controls: compressed-source mutation, duplicate output, one
    # missing Hall neighbor, strict-error truncation, and wrong tie handling.
    corrupted_packed = bytearray(CERTIFICATE.read_bytes())
    corrupted_packed[0] ^= 1
    source_pin_rejected = False
    try:
        unpack_certificate(bytes(corrupted_packed))
    except RuntimeError as error:
        source_pin_rejected = "compressed certificate SHA-256" in str(error)
    require(source_pin_rejected, "certificate-corruption control was not detected")

    corrupt_matching = [[list(pair[0]), list(pair[1])] for pair in matching]
    corrupt_matching[-1][1] = list(corrupt_matching[0][1])
    duplicate_output_rejected = False
    try:
        validate_matching(corrupt_matching, inputs, matrix)
    except RuntimeError as error:
        duplicate_output_rejected = "outputs are not injective" in str(error)
    require(duplicate_output_rejected,
            "duplicate-output negative control was not rejected")

    omitted_set = set(actual_neighbors)
    omitted_set.remove(min(omitted_set))
    omitted_neighbor_detected = omitted_set != declared_neighbors
    require(omitted_neighbor_detected,
            "one-neighbor omission negative control was not detected")
    strict_error_mutant_differs = strict_error_neighbors != actual_neighbors
    require(strict_error_mutant_differs,
            "error<1 mutant failed to remove any candidate")
    wrong_tie_rule_detected = inclusive_neighbors != actual_neighbors
    require(wrong_tie_rule_detected,
            "using <= beta in the Hall obstruction was not detected")

    return {
        "status": "PASS",
        "claim": "exact finite S5 optimum at beta=sqrt(21)-sqrt(19)",
        "global_scope": "necessary lower bound only; no global construction at beta",
        "expanded_certificate_sha256": RAW_SHA256,
        "input_count": len(inputs),
        "matching": matching_receipt,
        "hall": {
            "input_count": len(hall_inputs),
            "strict_beta_neighbor_count": len(actual_neighbors),
            "inclusive_beta_neighbor_count": len(inclusive_neighbors),
            "error_boundary_candidates": boundary_candidates,
        },
        "native_transfer": "H4=L(2C_+)R; inverse F_C=L^-1 F_H R",
        "negative_controls": {
            "certificate_corruption_rejected": source_pin_rejected,
            "duplicate_output_rejected": duplicate_output_rejected,
            "omitted_neighbor_detected": omitted_neighbor_detected,
            "strict_error_mutant_differs": strict_error_mutant_differs,
            "beta_tie_rule_detected": wrong_tie_rule_detected,
        },
    }


def main() -> None:
    _, document = unpack_certificate(CERTIFICATE.read_bytes())
    receipt = validate_certificate(document)
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
