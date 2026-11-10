#!/usr/bin/env python3
"""Exact finite corroboration of the cross-rim determinant theorem."""

from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import platform

PACKAGE = Path(__file__).resolve().parent
MAX_SIZE = 24


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dimensions(b, m):
    require(type(b) is int and type(m) is int, "integer dimensions required")
    require(1 <= b <= m and m + 2 * b <= MAX_SIZE, "finite replay domain")
    return m + 2 * b


def determinant(matrix):
    """Fraction-free Bareiss after clearing each row's denominators."""
    n = len(matrix)
    require(n <= MAX_SIZE and all(len(row) == n for row in matrix), "square matrix")
    a, scale = [], 1
    for row in matrix:
        denominator = 1
        for value in row:
            denominator *= F(value).denominator
        a.append([int(F(value) * denominator) for value in row])
        scale *= denominator
    previous, sign = 1, 1
    for k in range(n - 1):
        pivot = next((i for i in range(k, n) if a[i][k]), None)
        if pivot is None:
            return F(0)
        if pivot != k:
            a[k], a[pivot] = a[pivot], a[k]
            sign = -sign
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = a[i][j] * a[k][k] - a[i][k] * a[k][j]
                require(numerator % previous == 0, "Bareiss division not exact")
                a[i][j] = numerator // previous
            a[i][k] = 0
        previous = a[k][k]
    return F(sign * a[-1][-1], scale) if n else F(1)


def inverse(matrix):
    n = len(matrix)
    require(1 <= n <= MAX_SIZE and all(len(row) == n for row in matrix), "square matrix")
    a = [[F(x) for x in row] + [F(i == j) for j in range(n)]
         for i, row in enumerate(matrix)]
    for k in range(n):
        pivot = next((i for i in range(k, n) if a[i][k]), None)
        require(pivot is not None, "singular interior")
        a[k], a[pivot] = a[pivot], a[k]
        value = a[k][k]
        a[k] = [x / value for x in a[k]]
        for i in range(n):
            if i != k:
                value = a[i][k]
                a[i] = [x - value * y for x, y in zip(a[i], a[k], strict=True)]
    require(all(a[i][j] == (i == j) for i in range(n) for j in range(n)), "inverse residual")
    return [row[n:] for row in a]


def gaussian(b, m, q):
    n = dimensions(b, m)
    require(isinstance(q, F) and q != 0, "nonzero rational kernel parameter")
    return [[q ** ((i - j) ** 2) if abs(i - j) <= b else F(0)
             for j in range(n)] for i in range(n)]


def cross_rim(matrix, b, m):
    n = dimensions(b, m)
    require(len(matrix) == n and all(len(row) == n for row in matrix), "host dimensions")
    require(all(matrix[i][j] == 0 for i in range(n) for j in range(n)
                if abs(i - j) > b), "host bandwidth")
    interior = [row[b:b + m] for row in matrix[b:b + m]]
    inv = inverse(interior)
    left_inverse = [[sum(matrix[i][b + k] * inv[k][j] for k in range(m))
                     for j in range(m)] for i in range(b)]
    cross = [[matrix[i][b + m + j] - sum(
        left_inverse[i][k] * matrix[b + k][b + m + j] for k in range(m))
        for j in range(b)] for i in range(b)]
    return interior, cross


def check_case(matrix, b, m):
    interior, cross = cross_rim(matrix, b, m)
    pivot_det = determinant(interior)
    edge_product = F(1)
    for i in range(m + b):
        edge_product *= matrix[i][i + b]
    expected = (-1) ** (b * m) * edge_product / pivot_det
    actual = determinant(cross)
    require(actual == expected, "cross-rim determinant formula")
    # Block determinant supplies a separate full-host minor calculation.
    rows = list(range(b + m))
    columns = list(range(b, m + 2 * b))
    block_minor = determinant([[matrix[i][j] for j in columns] for i in rows])
    require(actual * pivot_det == (-1) ** (b * m) * block_minor, "block minor identity")
    return actual, pivot_det


def gaussian_cases():
    count = 0
    parameters = (F(-1, 2), F(1, 4), F(1, 3), F(1, 2), F(2, 3), F(2))
    for b in range(1, 5):
        for m in range(b, b + 6):
            for q in parameters:
                actual, pivot = check_case(gaussian(b, m, q), b, m)
                require(actual * pivot == (-1) ** (b * m) * q ** (b * b * (m + b)),
                        "Gaussian exponent or sign")
                require(actual != 0, "full rim rank")
                count += 1
    return count


def asymmetric_cases():
    count = 0
    for b in range(1, 5):
        for m in range(b, b + 5):
            n = dimensions(b, m)
            a = [[F(0) for _ in range(n)] for _ in range(n)]
            for i in range(n):
                for j in range(n):
                    if i == j:
                        a[i][j] = F(10 * n)
                    elif abs(i - j) <= b:
                        a[i][j] = F(1 + (3 * i + 5 * j) % 7)
            actual, _ = check_case(a, b, m)
            require(actual != 0, "asymmetric full rim rank")
            count += 1
    return count


def gauge_cases():
    count = 0
    for b in range(1, 5):
        for m in range(b, b + 3):
            a = gaussian(b, m, F(1, 2))
            n = len(a)
            left = [F((-1) ** i * (i + 1), i + 2) for i in range(n)]
            right = [F(i + 3, 2 * i + 1) for i in range(n)]
            gauged = [[left[i] * a[i][j] * right[j] for j in range(n)] for i in range(n)]
            _, plain = cross_rim(a, b, m)
            _, changed = cross_rim(gauged, b, m)
            require(all(changed[i][j] == left[i] * plain[i][j] * right[b + m + j]
                        for i in range(b) for j in range(b)), "boundary gauge identity")
            check_case(gauged, b, m)
            count += 1
    return count


def controls():
    rejected = 0
    for b, m in ((0, 2), (3, 2), (True, 2), (2, 30)):
        try:
            dimensions(b, m)
        except ValueError:
            rejected += 1
    for q in (F(0), 0.5):
        try:
            gaussian(2, 4, q)
        except ValueError:
            rejected += 1
    bad = gaussian(2, 4, F(1, 2))
    bad[0][-1] = F(1)
    for matrix in (bad, gaussian(2, 2, F(1))):
        try:
            cross_rim(matrix, 2, 4 if matrix is bad else 2)
        except ValueError:
            rejected += 1
    require(rejected == 8, "a rejection control did not reject")
    a = gaussian(2, 3, F(1, 2))
    a[0][2] = F(0)
    singular_cross, _ = check_case(a, 2, 3)
    require(singular_cross == 0, "missing outer edge must permit rank loss")
    actual, pivot = check_case(gaussian(1, 2, F(1, 2)), 1, 2)
    require(actual != -F(1, 2) ** 3 / pivot, "wrong parity control")
    actual, pivot = check_case(gaussian(2, 3, F(1, 2)), 2, 3)
    require(actual != F(1, 2) ** 4 / pivot, "missing rim factors control")
    return {"invalid_inputs": rejected, "semantic_counterexamples": 3}


def package_hashes():
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        path = PACKAGE / name
        require(path.stat().st_size <= 256 * 1024, "package file cap")
        hashes[name] = sha256(path.read_bytes()).hexdigest()
    return hashes


def main():
    result = {"claim_type": "scoped proof with finite corroboration",
              "gaussian_cases": gaussian_cases(), "asymmetric_cases": asymmetric_cases(),
              "gauged_cases": gauge_cases(), "controls": controls()}
    actual, pivot = check_case(gaussian(2, 3, F(1, 2)), 2, 3)
    result["fixture"] = {"b": 2, "m": 3, "t": "1/2", "det_interior": str(pivot),
                         "det_cross": str(actual), "rank": 2}
    result["python"] = platform.python_version()
    result["files_sha256"] = package_hashes()
    print(json.dumps(result, sort_keys=True, indent=2))
    print("PASS_GAUSSIAN_CROSS_RIM_DETERMINANT")


if __name__ == "__main__":
    main()
