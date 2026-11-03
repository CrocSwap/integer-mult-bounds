"""Exact corroboration of the smaller finite-cap Gaussian norm bound.

This contribution was produced by Nick Petalas. Apache-2.0.
The universal theorem is the written argument in PROOF.md.
"""
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
MAX_SIZE = 128
FILES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")


def need(condition, message):
    if not condition:
        raise ValueError(message)


def validate(size, q):
    need(type(size) is int and 1 <= size <= MAX_SIZE, "size must be an integer in 1..128")
    need(type(q) is Q and 0 < q < 1, "q must be a Fraction strictly between zero and one")
    need(max(q.numerator.bit_length(), q.denominator.bit_length()) <= 20, "q encoding exceeds limit")


def majorant_squared(size, q):
    validate(size, q)
    x = q ** 4
    geometric = ((size - 1) * x - size * x * x + x ** (size + 1)) / (1 - x) ** 2
    return Q(size * (size + 1), 2) + geometric


def pivot_product(size, q):
    validate(size, q)
    value = Q(1)
    for r in range(1, size):
        value *= 1 - q ** (2 * r)
    need(value > 0, "positive finite pivot product")
    return value


def direct_majorant(size, q):
    """Sum an entrywise matrix, independently of the closed geometric sum."""
    validate(size, q)
    return sum((Q(1) if i <= j else q ** (4 * (i - j))
                for i in range(size) for j in range(size)), Q(0))


def shifted_matrix(root, size, shift_index):
    need(type(root) is Q and 0 < root < 1, "rational kernel root")
    need(type(size) is int and 1 <= size <= 6, "matrix size in 1..6")
    need(type(shift_index) is int and -4 <= shift_index <= 4, "shift index in -4..4")
    # q=root^4, s=shift_index/8. Every exponent is an integer.
    return [[root ** (4 * (j - i) ** 2 - shift_index * (j - i))
             for j in range(size)] for i in range(size)]


def inverse(matrix):
    size = len(matrix)
    need(1 <= size <= 6 and all(len(row) == size for row in matrix), "bounded square matrix")
    rows = [list(row) + [Q(i == j) for j in range(size)] for i, row in enumerate(matrix)]
    for column in range(size):
        candidates = [i for i in range(column, size) if rows[i][column]]
        need(bool(candidates), "singular matrix")
        pivot = candidates[0]
        rows[column], rows[pivot] = rows[pivot], rows[column]
        scale = rows[column][column]
        rows[column] = [value / scale for value in rows[column]]
        for i in range(size):
            if i != column:
                scale = rows[i][column]
                rows[i] = [a - scale * b for a, b in zip(rows[i], rows[column])]
    need(all(rows[i][j] == (i == j) for i in range(size) for j in range(size)), "elimination identity")
    return [row[size:] for row in rows]


def check_inverse(matrix, candidate):
    size = len(matrix)
    for left, right in ((matrix, candidate), (candidate, matrix)):
        for i in range(size):
            for j in range(size):
                need(sum((left[i][k] * right[k][j] for k in range(size)), Q(0)) == (i == j),
                     "literal left/right inverse")


def geometric_checks():
    cases = strict = 0
    for q in (Q(1, 16), Q(1, 4), Q(1, 2), Q(3, 4), Q(7, 8), Q(15, 16), Q(31, 32)):
        for size in range(1, MAX_SIZE + 1):
            value = majorant_squared(size, q)
            # A separate one-dimensional weighted sum checks the closed formula.
            direct = Q(size * (size + 1), 2) + sum(
                ((size - d) * q ** (4 * d) for d in range(1, size)), Q(0))
            need(value == direct, "closed geometric sum")
            need(value <= size * size, "old norm ceiling")
            if size > 1:
                need(value < size * size, "strict improvement at every nontrivial size")
                strict += 1
            x = q ** 4
            tail_majorant = Q(size * (size + 1), 2) + size * x / (1 - x)
            need(value < tail_majorant, "linear remainder and bound-ratio limit")
            cases += 1
    return cases, strict


def finite_matrix_checks():
    matrices = entries = shifted_sums = 0
    for root in (Q(1, 2), Q(2, 3), Q(3, 4), Q(7, 8)):
        q = root ** 4
        for size in (1, 2, 3, 4, 6):
            ceiling = majorant_squared(size, q)
            need(ceiling == direct_majorant(size, q), "entrywise majorant reconstruction")
            bound = ceiling / pivot_product(size, q) ** 6
            for shift_index in range(-4, 5):
                decay = Q(size)
                for d in range(1, size):
                    decay += (size - d) * (root ** ((8 + 2 * shift_index) * d) +
                                           root ** ((8 - 2 * shift_index) * d))
                need(decay <= ceiling, "closed-half-shift envelope")
                if size > 1 and abs(shift_index) < 4:
                    need(decay < ceiling, "interior-shift strict envelope")
                shifted_sums += 1
                matrix = shifted_matrix(root, size, shift_index)
                candidate = inverse(matrix)
                check_inverse(matrix, candidate)
                norm_squared = sum((value * value for row in candidate for value in row), Q(0))
                need(norm_squared <= bound, "new norm bound on a literal inverse")
                matrices += 1
                entries += size * size
    return matrices, entries, shifted_sums


def reject_size(size):
    try:
        majorant_squared(size, Q(1, 2))
    except ValueError:
        return
    raise ValueError("invalid size accepted")


def reject_q(q):
    try:
        majorant_squared(2, q)
    except ValueError:
        return
    raise ValueError("invalid q accepted")


def controls():
    bad_sizes = (0, -1, 129, True, Q(2), 2.0)
    bad_qs = (Q(0), Q(1), Q(-1), Q(2), 0.5, 1, True, Q(1, 1 << 21))
    for size in bad_sizes:
        reject_size(size)
    for q in bad_qs:
        reject_q(q)
    need(majorant_squared(1, Q(1, 2)) == 1, "size-one equality retained")
    need(majorant_squared(2, Q(1, 2)) == Q(49, 16), "lower-triangle term cannot be omitted")
    need(majorant_squared(2, Q(1, 2)) != 3, "upper triangle alone is insufficient")
    need(majorant_squared(3, Q(1, 2)) != 3, "diagonal alone is insufficient")
    matrix = shifted_matrix(Q(1, 2), 2, 4)
    wrong = inverse(matrix)
    wrong[0][1] = -wrong[0][1]
    try:
        check_inverse(matrix, wrong)
    except ValueError:
        pass
    else:
        raise ValueError("wrong inverse sign accepted")
    try:
        inverse([[Q(1), Q(1)], [Q(1), Q(1)]])
    except ValueError:
        pass
    else:
        raise ValueError("singular inverse accepted")
    need(Q(49, 16) / pivot_product(2, Q(1, 2)) ** 6 == Q(112, 27) ** 2,
         "exact improved example")
    need(Q(2) / pivot_product(2, Q(1, 2)) ** 3 == Q(128, 27), "credited old example")
    need(Q(112, 128) == Q(7, 8), "exact one-eighth reduction")
    groups = ("size-one equality", "distance term", "missing lower triangle", "missing off-diagonal",
              "wrong inverse sign", "singular inverse", "new example", "old example", "reduction ratio")
    return {"rejected_inputs": len(bad_sizes) + len(bad_qs), "semantic_groups": list(groups)}


def file_hashes():
    result = {}
    for name in FILES:
        path = HERE / name
        need(path.is_file() and path.stat().st_size <= 262144, "bounded package file")
        with path.open("rb") as stream:
            raw = stream.read(262145)
        need(len(raw) <= 262144, "bounded package read")
        result[name] = sha256(raw).hexdigest()
    return result


def main():
    cases, strict = geometric_checks()
    matrices, entries, shifted_sums = finite_matrix_checks()
    result = {"status": "PASS_GAUSSIAN_FINITE_CAP_FROBENIUS", "claim_type": "scoped proof with finite corroboration",
              "geometric_cases": cases, "strict_improvements": strict, "literal_inverses": matrices,
              "inverse_entries": entries, "shift_envelopes": shifted_sums, "controls": controls(),
              "example": {"q": "1/2", "size": 2, "old_bound": "128/27", "new_bound": "112/27"},
              "python": sys.version.split()[0], "sha256": file_hashes()}
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
