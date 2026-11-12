#!/usr/bin/env python3
"""Check the exact kernel projector and its least denominator.

Produced by Nick Petalas. Apache-2.0. Standard library only; no file writes.
The predecessor matrix and basis are inputs, not reconstructed here.
"""
from fractions import Fraction
from hashlib import sha256
import json
from math import gcd, lcm
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
DIMENSION = 216
PRIME = 1000003
SOURCE = "research/a1-joint-216-charpoly/evidence/"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    raw = path.read_bytes()
    require(len(raw) <= 1_000_000, "input exceeds the one-MiB capacity")
    return json.loads(raw)


def square_matrix(rows, size, cap):
    require(isinstance(rows, list) and len(rows) == size, "wrong row count")
    for row in rows:
        require(isinstance(row, list) and len(row) == size, "wrong column count")
        require(all(type(x) is int and abs(x) <= cap for x in row),
                "matrix entries exceed the integer contract")
    return rows


def load_inputs():
    pins = read_json(PACKAGE / "SOURCES.json")["files"]
    for name in ("matrix.json", "basis.json"):
        path = SOURCE + name
        matches = [row for row in pins if row["path"] == path]
        require(len(matches) == 1, "missing or duplicate source pin")
        raw = (ROOT / path).read_bytes()
        require(sha256(raw).hexdigest() == matches[0]["sha256"],
                "predecessor bytes differ from their pin")
    matrix = square_matrix(read_json(ROOT / (SOURCE + "matrix.json"))["rows"],
                           DIMENSION, 28)
    vectors = read_json(ROOT / (SOURCE + "basis.json"))["vectors"]
    require(isinstance(vectors, list) and len(vectors) == DIMENSION,
            "wrong orbit-basis count")
    seen = set()
    weights = []
    for vector in vectors:
        require(isinstance(vector, list) and 1 <= len(vector) <= 16,
                "orbit support exceeds capacity")
        for address, coefficient in vector:
            require(type(address) is int and 0 <= address < 4096,
                    "orbit address outside the historical block")
            require(type(coefficient) is int and coefficient in (-1, 1),
                    "orbit coefficient is not a sign")
            require(address not in seen, "orbit supports overlap")
            seen.add(address)
        weights.append(len(vector))
    return matrix, weights


def multiply(left, right):
    size = len(left)
    require(1 <= size <= DIMENSION, "matrix dimension exceeds capacity")
    sparse_right = [[(j, x) for j, x in enumerate(row) if x] for row in right]
    result = [[0] * size for _ in range(size)]
    for i, row in enumerate(left):
        for k, x in enumerate(row):
            if x:
                for j, y in sparse_right[k]:
                    result[i][j] += x * y
    return result


def determinant_mod(rows, prime):
    size = len(rows)
    require(1 <= size <= DIMENSION and prime == PRIME, "invalid minor contract")
    work = [[x % prime for x in row] for row in rows]
    determinant = 1
    for column in range(size):
        pivot = next((r for r in range(column, size) if work[r][column]), None)
        if pivot is None:
            return 0
        if pivot != column:
            work[pivot], work[column] = work[column], work[pivot]
            determinant = -determinant
        value = work[column][column]
        determinant = determinant * value % prime
        inverse = pow(value, -1, prime)
        for r in range(column + 1, size):
            scale = work[r][column] * inverse % prime
            if scale:
                for j in range(column + 1, size):
                    work[r][j] = (work[r][j] - scale * work[column][j]) % prime
                work[r][column] = 0
    return determinant % prime


def certify(matrix, weights, numerator, denominator):
    size = len(matrix)
    require(1 <= size <= DIMENSION, "unsupported dimension")
    square_matrix(matrix, size, 1_000_000)
    square_matrix(numerator, size, 1_000_000)
    require(type(denominator) is int and 1 <= denominator <= 1_000_000,
            "invalid common denominator")
    require(len(weights) == size and all(type(w) is int and 1 <= w <= 16
                                        for w in weights), "invalid Gram weights")
    for i in range(size):
        for j in range(size):
            require(weights[i] * matrix[i][j] == weights[j] * matrix[j][i],
                    "source is not self-adjoint in the orbit Gram form")
            require(weights[i] * numerator[i][j] == weights[j] * numerator[j][i],
                    "projector is not self-adjoint in the orbit Gram form")
    require(gcd(denominator, *(x for row in numerator for x in row)) == 1,
            "the declared common denominator is not least")
    scaled = [[denominator * x for x in row] for row in numerator]
    require(multiply(numerator, numerator) == scaled, "idempotence fails")
    require(all(x == 0 for row in multiply(matrix, numerator) for x in row),
            "the claimed image is not in the kernel")
    require(all(x == 0 for row in multiply(numerator, matrix) for x in row),
            "the source image is not killed")
    joined = [[a + b for a, b in zip(row, qrow, strict=True)]
              for row, qrow in zip(matrix, numerator, strict=True)]
    residue = determinant_mod(joined, PRIME)
    require(residue != 0, "the claimed projector may omit kernel directions")
    return residue


def controls(matrix, weights, numerator, denominator):
    require(certify([[1, 2], [1, 2]], [1, 2], [[2, -2], [-1, 1]], 3) != 0,
            "weighted nonsymmetric positive fixture fails")
    changed = [row[:] for row in numerator]
    changed[0][0] += 1
    shifted = [row[:] for row in matrix]
    for i in range(DIMENSION):
        shifted[i][i] += 1
    cases = [
        (matrix, weights, changed, denominator),
        (shifted, weights, numerator, denominator),
        (matrix, weights, [[2*x for x in row] for row in numerator], 2*denominator),
        (matrix, weights, [[0]*DIMENSION for _ in range(DIMENSION)], 1),
    ]
    for args in cases:
        try:
            certify(*args)
        except ValueError:
            continue
        raise ValueError("a false projector certificate was accepted")
    return len(cases)


def main():
    matrix, weights = load_inputs()
    certificate = read_json(PACKAGE / "PROJECTOR.json")
    require(certificate["schema_version"] == 1, "unknown certificate schema")
    denominator = certificate["denominator"]
    numerator = certificate["numerator"]
    residue = certify(matrix, weights, numerator, denominator)
    require(denominator == 12480 == 2**6 * 3 * 5 * 13, "unexpected denominator")
    witnesses = certificate["witnesses"]
    require(witnesses == [[10, 60, 9, 4160], [4, 4, 47, 156],
                          [6, 6, 71, 260], [0, 0, 5, 416]], "wrong witness list")
    for i, j, a, b in witnesses:
        require(Fraction(numerator[i][j], denominator) == Fraction(a, b),
                "a reduced-entry witness is false")
        require(gcd(a, b) == 1, "witness fraction is not reduced")
    require(lcm(*(b for _, _, _, b in witnesses)) == denominator,
            "witnesses do not force the whole denominator")
    rejected = controls(matrix, weights, numerator, denominator)
    rank = Fraction(sum(numerator[i][i] for i in range(DIMENSION)), denominator)
    require(rank == 24, "unexpected projector trace")
    print(json.dumps({"status": "PASS_A1_ZERO_PROJECTOR_DENOMINATOR",
                      "dimension": DIMENSION, "denominator": denominator,
                      "rank": int(rank), "nonzero_entries": sum(
                          x != 0 for row in numerator for x in row),
                      "det_M_plus_Q_mod_1000003": residue,
                      "rejected_controls": rejected,
                      "projector_sha256": sha256(
                          (PACKAGE / "PROJECTOR.json").read_bytes()).hexdigest()},
                     sort_keys=True))


if __name__ == "__main__":
    main()
