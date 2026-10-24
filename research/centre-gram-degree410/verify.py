"""Certify a new scalar-polynomial obstruction for two Bell blocks."""

import argparse
from hashlib import sha256, shake_256
import json
from pathlib import Path

import numpy as np


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
SOURCE = (
    "research/centre-polynomial-cache-limits/frozen/work/"
    "centre-encoding-campaign-20261014/lanes/circuit-interface/INTERFACE.json"
)
SOURCE_HASH = "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3"
PRIME = 65537
DEGREE = 410
MOMENTS = 2 * DEGREE - 1
SEED = "new-degree410-centre-gram"
FILES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(raw):
    require(sha256(raw).hexdigest() == SOURCE_HASH, "actual query source digest")


def read_source():
    path = ROOT / SOURCE
    require(path.stat().st_size <= 1_000_000, "bounded query input")
    raw = path.read_bytes()
    authenticate(raw)
    data = json.loads(raw)
    roots = np.zeros((112, 8), dtype=np.int64)
    require(len(data["R"]) == 8 and len(data["ports"]) == 112, "query shape")
    for row, entries in enumerate(data["R"]):
        for column, value in entries.items():
            roots[int(column), row] = int(value)
    ports = tuple(data["ports"])
    require(len(set(ports)) == 112, "distinct port labels")
    require(all(type(q) is int and 0 < q < 512 for q in ports), "nine-bit labels")
    require(np.array_equal(roots.T @ roots, 56 * np.eye(8, dtype=np.int64)), "query normalization")
    require(np.all(np.count_nonzero(roots, axis=1) == 4), "four root entries")
    require(np.all(np.isin(roots, (-1, 0, 1))), "signed root entries")
    return raw, roots, ports


def seed_vector(suffix):
    raw = shake_256((SEED + suffix).encode("ascii")).digest(8192)
    return np.frombuffer(raw, dtype="<u2").astype(np.int64).reshape(8, 512)


def action_tables(ports, constant):
    require(constant in (1, 11), "declared Bell block")
    addresses = np.arange(512, dtype=np.int64)
    targets = np.empty((112, 512), dtype=np.int64)
    signs = np.empty((112, 512), dtype=np.int64)
    for index, q in enumerate(ports):
        shift = (q & constant).bit_count() % 2
        targets[index] = addresses ^ (q if shift else 0)
        signs[index] = [1 if shift else 1 - 2 * ((q & a).bit_count() % 2)
                        for a in range(512)]
    return targets, signs


def factored_apply(value, roots, targets, signs):
    lifted = (roots @ value) % PRIME
    moved = np.take_along_axis(lifted, targets, axis=1) * signs
    return ((roots.T @ moved) % PRIME) * pow(4, -1, PRIME) % PRIME


def literal_apply(value, roots, ports, constant):
    output = np.zeros((8, 512), dtype=np.int64)
    addresses = np.arange(512, dtype=np.int64)
    for index, q in enumerate(ports):
        support = np.flatnonzero(roots[index])
        lifted = np.zeros(512, dtype=np.int64)
        for row in support:
            lifted += int(roots[index, row]) * value[row]
        if (q & constant).bit_count() % 2:
            moved = lifted[addresses ^ q]
        else:
            phase = np.array([1 - 2 * ((q & a).bit_count() % 2)
                              for a in range(512)], dtype=np.int64)
            moved = lifted * phase
        for row in support:
            output[row] += int(roots[index, row]) * moved
    return (output % PRIME) * pow(4, -1, PRIME) % PRIME


def block_moments(roots, ports, constant):
    targets, signs = action_tables(ports, constant)
    initial = seed_vector("")
    observer = seed_vector("-observer")
    value = initial.copy()
    literal = initial.copy()
    moments = []
    for index in range(MOMENTS):
        require(np.array_equal(value, literal), "factored/literal Krylov vectors agree")
        moments.append(int(np.sum(value * observer) % PRIME))
        if index + 1 < MOMENTS:
            value = factored_apply(value, roots, targets, signs)
            literal = literal_apply(literal, roots, ports, constant)
    return moments


def hankel(moments):
    require(len(moments) == MOMENTS, "exact moment count")
    require(all(type(x) is int and 0 <= x < PRIME for x in moments), "prime-field moments")
    return np.asarray([[moments[i + j] for j in range(DEGREE)]
                       for i in range(DEGREE)], dtype=np.int64)


def determinant(matrix):
    require(matrix.ndim == 2 and matrix.shape[0] == matrix.shape[1], "square determinant")
    require(0 < len(matrix) <= DEGREE, "bounded determinant")
    work = matrix.copy() % PRIME
    result = 1
    for column in range(len(work)):
        nonzero = np.flatnonzero(work[column:, column])
        if not len(nonzero):
            return 0
        pivot_row = column + int(nonzero[0])
        if pivot_row != column:
            work[[column, pivot_row]] = work[[pivot_row, column]]
            result = -result
        pivot = int(work[column, column])
        result = result * pivot % PRIME
        scaled = work[column, column + 1:] * pow(pivot, -1, PRIME) % PRIME
        work[column + 1:, column + 1:] = (
            work[column + 1:, column + 1:]
            - work[column + 1:, column, None] * scaled[None, :]
        ) % PRIME
        work[column + 1:, column] = 0
    return result


def condensed_determinant(matrix):
    """Fraction-free condensation with Python integers, reduced modulo p."""
    require(matrix.ndim == 2 and matrix.shape[0] == matrix.shape[1], "square condensation")
    require(0 < len(matrix) <= DEGREE, "bounded condensation")
    rows = [[int(x) % PRIME for x in row] for row in matrix]
    previous = 1
    sign = 1
    for column in range(len(rows) - 1):
        candidates = [i for i in range(column, len(rows)) if rows[i][column]]
        if not candidates:
            return 0
        pivot_row = candidates[0]
        if pivot_row != column:
            rows[column], rows[pivot_row] = rows[pivot_row], rows[column]
            sign = -sign
        top = rows[column]
        pivot = top[column]
        inverse = pow(previous, -1, PRIME)
        for i in range(column + 1, len(rows)):
            row = rows[i]
            left = row[column]
            for j in range(column + 1, len(rows)):
                row[j] = ((pivot * row[j] - left * top[j]) * inverse) % PRIME
            row[column] = 0
        previous = pivot
    return sign * rows[-1][-1] % PRIME


def failure_controls(matrix, blocks, raw):
    require(determinant(hankel(blocks[11])) == 0, "duplicated c=11 cannot certify 410")
    duplicate_row = matrix.copy()
    duplicate_row[-1] = duplicate_row[0]
    require(determinant(duplicate_row) == 0, "dependent-row control")
    duplicate_column = matrix.copy()
    duplicate_column[:, -1] = duplicate_column[:, 0]
    require(determinant(duplicate_column) == 0, "dependent-column control")
    fixtures = (([[0, 1], [1, 0]], PRIME - 1), ([[1, 2], [2, 4]], 0), ([[3]], 3))
    for rows, expected in fixtures:
        small = np.array(rows, dtype=np.int64)
        require(determinant(small) == expected, "small elimination fixture")
        require(condensed_determinant(small) == expected, "small condensation fixture")
    try:
        authenticate(raw + b" ")
    except ValueError as error:
        require(str(error) == "actual query source digest", "specific source rejection")
    else:
        raise ValueError("source mutation accepted")
    try:
        hankel(blocks[1][:-1])
    except ValueError as error:
        require(str(error) == "exact moment count", "specific truncated-moment rejection")
    else:
        raise ValueError("truncated moment sequence accepted")


def report():
    require(all(PRIME % divisor for divisor in range(2, 257)), "prime modulus")
    raw, roots, ports = read_source()
    blocks = {constant: block_moments(roots, ports, constant) for constant in (1, 11)}
    moments = [(x + y) % PRIME for x, y in zip(blocks[1], blocks[11])]
    matrix = hankel(moments)
    answer = determinant(matrix)
    require(answer == 58805, "new nonzero 410 minor")
    require(condensed_determinant(matrix) == answer, "independent integer condensation")
    failure_controls(matrix, blocks, raw)
    hashes = {name: sha256((PACKAGE / name).read_bytes()).hexdigest() for name in FILES}
    hashes[SOURCE] = sha256(raw).hexdigest()
    return {
        "status": "PASS_CENTRE_GRAM_DEGREE410",
        "prime": PRIME,
        "bell_blocks": [1, 11],
        "direct_sum_dimension": 8192,
        "seed": SEED,
        "observer_seed": SEED + "-observer",
        "seed_expansion": "SHAKE2568192bytes, little-endian uint16, reshape8by512",
        "moments_count": MOMENTS,
        "block_moments": {str(c): blocks[c] for c in (1, 11)},
        "direct_sum_moments": moments,
        "hankel_size": DEGREE,
        "determinant_mod_prime": answer,
        "krylov_vector_comparisons": 2 * MOMENTS,
        "determinant_methods": ["modular Gaussian elimination", "integer fraction-free condensation"],
        "controls": ["omitted c=1 block", "dependent row", "dependent column",
                     "row-swap fixture", "singular fixture", "one-dimensional fixture",
                     "changed source bytes", "truncated moments"],
        "all_positive_tensor_degree_lower_bound": DEGREE,
        "scalar_polynomial_inverse_degree_lower_bound": DEGREE - 1,
        "source_sha256": hashes,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-result", action="store_true", help="print regenerated receipt as JSON")
    args = parser.parse_args()
    actual = report()
    if args.emit_result:
        print(json.dumps(actual, indent=2, sort_keys=True))
        return
    print("PASS_CENTRE_GRAM_DEGREE410 degree>=410 inverse_degree>=409 det=58805 mod=65537")


if __name__ == "__main__":
    main()
