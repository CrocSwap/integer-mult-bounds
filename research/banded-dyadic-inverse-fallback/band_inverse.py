"""Exact pivoted band completion, produced by Nick Petalas. Apache-2.0."""

from fractions import Fraction


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(matrix, bandwidth):
    n = len(matrix)
    require(1 <= n <= 256, "dimension must be in 1..256")
    require(type(bandwidth) is int and 0 <= bandwidth < n, "invalid bandwidth")
    require(all(len(row) == n for row in matrix), "matrix must be square")
    for i, row in enumerate(matrix):
        for j, value in enumerate(row):
            require(type(value) is int and value.bit_length() <= 4096,
                    "entries must be integers of at most 4096 bits")
            require(abs(i - j) <= bandwidth or value == 0,
                    "entry outside declared band")
    return n


def forward(matrix, bandwidth):
    """Return normalized upper factor, transformed identity, operations, swaps."""
    n = validate(matrix, bandwidth)
    upper = [[Fraction(value) for value in row] for row in matrix]
    right = [[Fraction(i == j) for j in range(n)] for i in range(n)]
    operations = swaps = 0
    for k in range(n):
        stop = min(n, k + bandwidth + 1)
        pivot = next((i for i in range(k, stop) if upper[i][k]), None)
        require(pivot is not None, "singular matrix")
        if pivot != k:
            upper[k], upper[pivot] = upper[pivot], upper[k]
            right[k], right[pivot] = right[pivot], right[k]
            swaps += 1
        value = upper[k][k]
        end = min(n, k + 2 * bandwidth + 1)
        for j in range(k + 1, end):
            upper[k][j] /= value
            operations += 1
        upper[k][k] = Fraction(1)
        for j in range(n):
            right[k][j] /= value
            operations += 1
        for i in range(k + 1, stop):
            factor = upper[i][k]
            if not factor:
                continue
            upper[i][k] = Fraction(0)
            for j in range(k + 1, end):
                upper[i][j] -= factor * upper[k][j]
                operations += 2
            for j in range(n):
                right[i][j] -= factor * right[k][j]
                operations += 2
    return upper, right, operations, swaps


def inverse(matrix, bandwidth):
    """Invert the integer matrix exactly, with no dominance/sign hypothesis."""
    upper, result, operations, swaps = forward(matrix, bandwidth)
    n = len(matrix)
    for i in range(n - 1, -1, -1):
        for j in range(i + 1, min(n, i + 2 * bandwidth + 1)):
            if not upper[i][j]:
                continue
            for col in range(n):
                result[i][col] -= upper[i][j] * result[j][col]
                operations += 2
    bound = n * n + 2 * n * bandwidth + 4 * n * bandwidth**2
    bound += 6 * n * n * bandwidth
    require(operations <= bound, "field-operation envelope exceeded")
    require(all(not upper[i][j] for i in range(n)
                for j in range(min(n, i + 2 * bandwidth + 1), n)),
            "upper fill escaped twice the input bandwidth")
    return result, {"operations": operations, "bound": bound, "swaps": swaps}


def rounded_candidate(matrix, bandwidth, entry_bits, output_bits):
    """Match #5677's nearest-grid convention, including negative ties."""
    require(type(entry_bits) is int and 0 <= entry_bits <= 4096,
            "invalid entry precision")
    require(type(output_bits) is int and 0 <= output_bits <= 4096,
            "invalid output precision")
    exact, counts = inverse(matrix, bandwidth)
    scale = 1 << (entry_bits + output_bits)
    rounded = [[(2 * value.numerator * scale + value.denominator)
                // (2 * value.denominator) for value in row] for row in exact]
    return rounded, counts
