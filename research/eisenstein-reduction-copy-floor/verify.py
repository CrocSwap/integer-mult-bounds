"""Exact good-reduction premises for the Eisenstein scalar copy-cost theorem.

Jose Manuel (@jmbarrancoml), with substantial OpenAI Codex assistance.
Apache-2.0. Geometry: Jonathan Lam, following Joel Pulikkan / GamingPuzzled.
"""

from fractions import Fraction as F
from hashlib import sha256
import importlib.util
from itertools import combinations
import json
from pathlib import Path
from random import Random


ROOT = Path(__file__).resolve().parents[2]
GEOMETRY = ROOT / "research/eisenstein-clique-copy-bound/geometry.py"
GEOMETRY_SHA = "248df3fb820b5165ca485ad4d43f0271043498c45a59ac1edc310a124073644c"
ZERO = (F(0), F(0))
ONE = (F(1), F(0))
OMEGA = (F(0), F(1))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def add(x, y):
    return x[0] + y[0], x[1] + y[1]


def neg(x):
    return -x[0], -x[1]


def mul(x, y):
    a, b = x
    c, d = y
    return a * c - b * d, a * d + b * c - b * d


def conjugate(x):
    return x[0] - x[1], -x[1]


def inverse(x):
    a, b = x
    norm = a * a - a * b + b * b
    require(norm != 0, "inverse of zero")
    c, d = conjugate(x)
    return c / norm, d / norm


def trace(x):
    return 2 * x[0] - x[1]


def fmul(x, y):
    a, b, c, d = x & 1, x >> 1, y & 1, y >> 1
    return (a * c ^ b * d) | ((a * d ^ b * c ^ b * d) << 1)


def reduce_mod2(x):
    require(all(t.denominator % 2 for t in x), "even denominator")
    return (x[0].numerator & 1) | ((x[1].numerator & 1) << 1)


def rank(matrix, field="K"):
    """Elimination over K, F4, or Q; no numerical tolerance."""
    if not matrix or not matrix[0]:
        return 0
    if field == "K":
        zero, plus, times, minus, inv = ZERO, add, mul, neg, inverse
    elif field == "F4":
        zero, plus, times, minus = 0, lambda a, b: a ^ b, fmul, lambda a: a
        inv = lambda a: fmul(a, a)
    else:
        zero, plus = F(0), lambda a, b: a + b
        times, minus, inv = lambda a, b: a * b, lambda a: -a, lambda a: 1 / a
    rows = [list(row) for row in matrix]
    pivot = 0
    for col in range(len(rows[0])):
        found = next((i for i in range(pivot, len(rows)) if rows[i][col] != zero), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        scale = inv(rows[pivot][col])
        rows[pivot] = [times(x, scale) for x in rows[pivot]]
        for i in range(pivot + 1, len(rows)):
            factor = rows[i][col]
            if factor != zero:
                rows[i] = [plus(x, minus(times(factor, y)))
                           for x, y in zip(rows[i], rows[pivot])]
        pivot += 1
        if pivot == len(rows):
            break
    return pivot


def gram(x, y, jy):
    d0 = sum(a * b for a, b in zip(x, y))
    d1 = sum(a * b for a, b in zip(x, jy))
    require(d0 % 4 == d1 % 4 == 0, "root dot divisibility")
    return F(d0 - d1, 12), F(-d0 - 2 * d1, 12)


def submatrix(matrix, rows, cols):
    return [[matrix[i][j] for j in cols] for i in rows]


def check_witness(matrix, adjacent):
    n = len(matrix)
    for i in range(n):
        require(matrix[i][i] == 1, "fitting diagonal")
        for j in range(n):
            require(matrix[i][j] in (0, 1), "binary fitting entry")
            require(not ((adjacent[i] >> j) & 1) or matrix[i][j] == 0,
                    "forbidden nonorthogonal entry")


def check_hadamard(hbar, matrix):
    require(all(fmul(hbar[i][j], matrix[i][j]) == int(i == j)
                for i in range(len(matrix)) for j in range(len(matrix))),
            "Hadamard identity")


def expect_rejection(call, label):
    try:
        call()
    except ValueError:
        return label
    raise ValueError("negative control accepted: " + label)


def main():
    require(sha256(GEOMETRY.read_bytes()).hexdigest() == GEOMETRY_SHA, "geometry pin")
    spec = importlib.util.spec_from_file_location("pinned_eisenstein_geometry", GEOMETRY)
    geometry = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(geometry)
    reps, images, adjacent, pairs, orbits = geometry.geometry()
    n = len(reps)
    require(n == 40, "line count")
    h = [[gram(x, y, jy) for y, jy in zip(reps, images)] for x in reps]
    hbar = [[reduce_mod2(x) for x in row] for row in h]
    # Check the complete rational trace realization, including the J rows.
    trace_entries = 0
    for i in range(n):
        for j in range(n):
            value = h[i][j]
            require(all(t.denominator in (1, 3) for t in value), "localized Gram")
            require(h[j][i] == conjugate(value), "Hermitian symmetry")
            require((value == ZERO) == (i != j and not ((adjacent[i] >> j) & 1)),
                    "Gram orthogonality pattern")
            require(hbar[i][j] != 0 if i == j or ((adjacent[i] >> j) & 1) else hbar[i][j] == 0,
                    "reduced orthogonality pattern")
            for a, x in enumerate((reps[i], images[i])):
                for b, y in enumerate((reps[j], images[j])):
                    factor = ONE
                    if a:
                        factor = mul(factor, conjugate(OMEGA))
                    if b:
                        factor = mul(factor, OMEGA)
                    require(4 * trace(mul(factor, value)) == geometry.dot(x, y),
                            "trace pairing realization")
                    trace_entries += 1
        require(h[i][i] == ONE and hbar[i][i] == 1, "unit diagonal")
    require(rank(h) == rank(hbar, "F4") == 4, "full Hermitian rank")
    # Check the quotient field and the reduction homomorphism on all Gram values.
    for a in range(4):
        if a:
            require(fmul(a, fmul(a, a)) == 1, "F4 inverse")
        for b in range(4):
            for c in range(4):
                require(fmul(fmul(a, b), c) == fmul(a, fmul(b, c)), "F4 associativity")
                require(fmul(a, b ^ c) == (fmul(a, b) ^ fmul(a, c)), "F4 distributivity")
    values = set(x for row in h for x in row)
    for x in values:
        for y in values:
            require(reduce_mod2(add(x, y)) == reduce_mod2(x) ^ reduce_mod2(y), "reduction sum")
            require(reduce_mod2(mul(x, y)) == fmul(reduce_mod2(x), reduce_mod2(y)), "reduction product")

    # These samples corroborate the universal radical/minor argument in README.
    # Neither finite sampling nor a flat census replaces that argument.
    rng = Random(20261014)
    supports = [[], [0], list(range(n))]
    supports += [[j for j in range(n) if j != i and not ((adjacent[i] >> j) & 1)]
                 for i in range(n)]
    require(all(len(s) == 12 for s in supports[3:]), "orthogonal hyperplanes")
    for support in supports[3:]:
        require(rank(submatrix(hbar, list(range(n)), support), "F4") == 3,
                "hyperplane column rank")
    pairs_to_check = [(supports[i], supports[j]) for i in range(3) for j in range(len(supports))]
    pairs_to_check += [(rng.sample(range(n), rng.randrange(1, 13)),
                       rng.sample(range(n), rng.randrange(1, 13))) for _ in range(80)]
    for r, a in pairs_to_check:
        kernel_rank = rank(submatrix(h, r, a))
        residue_rank = rank(submatrix(hbar, r, a), "F4")
        vr = [x for i in r for x in (reps[i], images[i])]
        va = [x for i in a for x in (reps[i], images[i])]
        rational_gram = [[F(geometry.dot(x, y)) for y in va] for x in vr]
        require(rank(rational_gram, "Q") == 2 * kernel_rank, "pairing rank conversion")
        require(residue_rank <= kernel_rank, "minor specialization rank")

    # Two fitting matrices: identity and the dense directed orthogonal pattern.
    identity = [[int(i == j) for j in range(n)] for i in range(n)]
    fitting = [[int(i == j or not ((adjacent[i] >> j) & 1)) for j in range(n)]
               for i in range(n)]
    for matrix in (identity, fitting):
        check_witness(matrix, adjacent)
        check_hadamard(hbar, matrix)
        cost = 0
        for i, row in enumerate(matrix):
            source = [j for j, value in enumerate(row) if value]
            cost += rank(submatrix(h, [i], source))
        require(cost == 40, "row-star upper bound")
    # Cancelling full rectangles exercise non-clean decompositions and parity.
    rectangles = [([i], [j for j, x in enumerate(row) if x]) for i, row in enumerate(fitting)]
    rectangles += [(list(range(n)), list(range(n)))] * 2
    reconstructed = [[0] * n for _ in range(n)]
    schur_sum = [[0] * n for _ in range(n)]
    cost = residue_cost = 0
    for r, a in rectangles:
        cost += rank(submatrix(h, r, a))
        residue_cost += rank(submatrix(hbar, r, a), "F4")
        for i in r:
            for j in a:
                reconstructed[i][j] ^= 1
                schur_sum[i][j] ^= hbar[i][j]
    require(reconstructed == fitting and schur_sum == identity, "XOR rectangle identity")
    require(cost == residue_cost == 48, "non-clean cancellation cost")

    # The known ten-frame construction attains binary rank ten and cost forty.
    partition = [(0, 28, 29, 39), (1, 22, 23, 38), (2, 16, 17, 37),
                 (9, 10, 11, 36), (3, 15, 26, 32), (5, 12, 24, 35),
                 (7, 14, 21, 34), (4, 18, 25, 31), (6, 19, 20, 33),
                 (8, 13, 27, 30)]
    require(sorted(i for frame in partition for i in frame) == list(range(n)), "frame partition")
    frame_b = [[0] * n for _ in range(n)]
    for frame in partition:
        require(all(not ((adjacent[i] >> j) & 1) for i, j in combinations(frame, 2)),
                "orthogonal frame")
        require(rank(submatrix(h, frame, frame)) == 4, "frame rank")
        for i in frame:
            for j in frame:
                frame_b[i][j] = 1
    check_witness(frame_b, adjacent)
    check_hadamard(hbar, frame_b)
    # Field extension preserves the rank of a binary matrix, so F4 suffices.
    require(rank(frame_b, "F4") == 10, "minrank upper witness")

    # A two-bit message on an orthogonal frame attains the block-linear bound.
    # Mix its two parity channels, then undo that mix at each receiver.
    frame = next(s for s in combinations(range(n), 4)
                 if all(not ((adjacent[i] >> j) & 1) for i, j in combinations(s, 2)))
    frame_cost = rank(submatrix(h, frame, frame))
    require(frame_cost == 4, "orthogonal frame cost")
    encoder = [[int(k % 2 == 0) for k in range(8)], [1] * 8]
    decoder = [[1, 0] if k % 2 == 0 else [1, 1] for k in range(8)]
    block_b = [[sum(decoder[i][a] * encoder[a][j] for a in range(2)) % 2
                for j in range(8)] for i in range(8)]
    lifted = [[hbar[frame[i // 2]][frame[j // 2]] for j in range(8)] for i in range(8)]
    product = [[fmul(lifted[i][j], block_b[i][j]) for j in range(8)] for i in range(8)]
    require(product == [[int(i == j) for j in range(8)] for i in range(8)],
            "block-linear recovery identity")
    require(rank(product, "F4") == 2 * frame_cost == 8, "block-linear sharp cost")
    # Test the q*c estimate on asymmetric, overlapping, mixed-bit block maps.
    block_samples = 16
    for _ in range(block_samples):
        r, a = rng.sample(range(n), 8), rng.sample(range(n), 9)
        rows = [i for i in r for _ in range(rng.randrange(1, 4))]
        cols = [j for j in a for _ in range(rng.randrange(1, 4))]
        q = rng.randrange(1, 4)
        d = [[rng.randrange(2) for _ in range(q)] for _ in rows]
        e = [[rng.randrange(2) for _ in cols] for _ in range(q)]
        b = [[sum(d[i][k] * e[k][j] for k in range(q)) % 2
              for j in range(len(cols))] for i in range(len(rows))]
        masked = [[fmul(hbar[s][t], b[i][j]) for j, t in enumerate(cols)]
                  for i, s in enumerate(rows)]
        require(rank(masked, "F4") <= q * rank(submatrix(h, r, a)),
                "block-linear message rank estimate")

    bad_diagonal = [row[:] for row in hbar]
    bad_diagonal[0][0] = 0
    bad_zero = [row[:] for row in hbar]
    orthogonal = next(j for j in range(1, n) if not ((adjacent[0] >> j) & 1))
    bad_zero[0][orthogonal] = 1
    illegal = [row[:] for row in identity]
    nonorthogonal = next(j for j in range(1, n) if (adjacent[0] >> j) & 1)
    illegal[0][nonorthogonal] = 1
    missing = [row[:] for row in fitting]
    missing[0][0] = 0
    controls = [
        expect_rejection(lambda: check_hadamard(bad_diagonal, fitting), "lost unit diagonal"),
        expect_rejection(lambda: check_hadamard(bad_zero, fitting), "corrupted orthogonal zero"),
        expect_rejection(lambda: check_witness(illegal, adjacent), "illegal side information"),
        expect_rejection(lambda: check_hadamard(hbar, illegal), "non-fitting Schur product"),
        expect_rejection(lambda: check_witness(missing, adjacent), "omitted demanded coordinate"),
        expect_rejection(lambda: reduce_mod2((F(1, 2), F(0))), "bad reduction denominator"),
        expect_rejection(lambda: require(frame_cost >= rank(product, "F4"), "underpriced width"),
                         "charging a two-bit message once"),
    ]
    receipt = {
        "lines": n, "gram_entries": n * n, "trace_entries": trace_entries,
        "gram_values": len(values), "rank_K": 4, "rank_F4": 4,
        "rank_conversion_samples": len(pairs_to_check),
        "hyperplanes": 40, "row_star_cost": 40,
        "binary_minrank_witness": 10,
        "non_clean_control_cost": cost, "negative_controls": controls,
        "block_linear_samples": block_samples, "block_linear_sharp_cost": 8,
        "proof_scope": "all finite scalar binary rectangle decompositions; see README for proof",
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))
    print("PASS_EISENSTEIN_REDUCTION_COPY_FLOOR: sharp abstract scalar cost 40")


if __name__ == "__main__":
    main()
