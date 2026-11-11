#!/usr/bin/env python3
"""Length-6 support for five rank-one frames plus one old projector.

PROOF.md holds the argument. This program checks the construction, the
splitting identity, the integral character obstruction, and the exhaustive
incidence census that makes the construction necessary.
"""

from fractions import Fraction
from itertools import combinations, permutations
from math import gcd


TARGETS = ((1, 0, 1), (2, 1, -1), (0, 1, 1), (1, 2, -1))
TARGET_NAME = {
    (1, 0, 1): "A+P",
    (2, 1, -1): "A+Q",
    (0, 1, 1): "B+P",
    (1, 2, -1): "B+Q",
}
PROJECTORS = (
    ("A", (1, 0, 0)),
    ("B", (0, 1, 0)),
    ("P", (0, 0, 1)),
    ("Q", (1, 1, -1)),
)
BY_NAME = dict(PROJECTORS)
OPPOSITE = {"A": "B", "B": "A", "P": "Q", "Q": "P"}
OTHER_PAIR = {"A": ("P", "Q"), "B": ("P", "Q"), "P": ("A", "B"), "Q": ("A", "B")}
TOTAL = (4, 4, 0)
TWO_I = (2, 2, 0)
MASKS = tuple(m for m in range(64) if bin(m).count("1") in (2, 3, 4))
PERMS = tuple(permutations(range(4)))
HAND_MASKS = (3, 5, 6, 9)
HAND_E = (1, 0, 0)
HAND_FRAMES = (
    (Fraction(3, 2), Fraction(0), Fraction(-1, 2)),
    (Fraction(-1, 2), Fraction(0), Fraction(3, 2)),
    (Fraction(1, 2), Fraction(1), Fraction(-1, 2)),
    (Fraction(-1, 2), Fraction(2), Fraction(-1, 2)),
    (Fraction(2), Fraction(1), Fraction(0)),
)
FULL_SHAPES = {
    (1, 0, 0, 1, -1): 800,
    (0, 1, 0, 1, -1): 640,
    (0, 1, 1, 0, -1): 640,
    (1, 0, 1, 0, -1): 640,
    (0, 0, 1, 1, -1): 560,
    (1, 1, 0, 0, -1): 560,
}


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


def quad(frame):
    a, b, c = frame
    return 2 * a * b + c * (a + b)


def add(frames):
    return tuple(sum(frame[i] for frame in frames) for i in range(3))


def sub(left, right):
    return tuple(left[i] - right[i] for i in range(3))


def rank_one_nonzero(frame):
    return frame != (0, 0, 0) and quad(frame) == 0


def det4(a, b, c, d):
    return (
        a[0] * (b[1] * (c[2] * d[3] - c[3] * d[2]) - b[2] * (c[1] * d[3] - c[3] * d[1]) + b[3] * (c[1] * d[2] - c[2] * d[1]))
        - a[1] * (b[0] * (c[2] * d[3] - c[3] * d[2]) - b[2] * (c[0] * d[3] - c[3] * d[0]) + b[3] * (c[0] * d[2] - c[2] * d[0]))
        + a[2] * (b[0] * (c[1] * d[3] - c[3] * d[1]) - b[1] * (c[0] * d[3] - c[3] * d[0]) + b[3] * (c[0] * d[1] - c[1] * d[0]))
        - a[3] * (b[0] * (c[1] * d[2] - c[2] * d[1]) - b[1] * (c[0] * d[2] - c[2] * d[0]) + b[2] * (c[0] * d[1] - c[1] * d[0]))
    )


def minors(rows):
    cofactors = [[0] * 5 for _ in range(5)]
    for i in range(5):
        for j in range(5):
            minor = []
            for ii in range(5):
                if ii == i:
                    continue
                minor.append(tuple(rows[ii][jj] for jj in range(5) if jj != j))
            sign = 1 if ((i + j) & 1) == 0 else -1
            cofactors[i][j] = sign * det4(*minor)
    determinant = sum(rows[0][j] * cofactors[0][j] for j in range(5))
    return determinant, cofactors


def adj_identity(rows, cofactors, determinant):
    for p in range(5):
        for q in range(5):
            got = sum(rows[p][k] * cofactors[q][k] for k in range(5))
            require(got == (determinant if p == q else 0), "cofactor expansion is not the adjugate")


def solve4(mat, rhs):
    determinant = det4(*(tuple(row) for row in mat))
    if determinant == 0:
        return None
    solution = []
    for col in range(4):
        replaced = []
        for r in range(4):
            row = list(mat[r])
            row[col] = rhs[r]
            replaced.append(tuple(row))
        solution.append(Fraction(det4(*replaced), determinant))
    return solution


def primitive(vec):
    scale = 0
    for value in vec:
        scale = gcd(scale, abs(value))
    require(scale != 0, "primitive of the zero vector")
    vec = tuple(value // scale for value in vec)
    for value in vec:
        if value > 0:
            return vec
        if value < 0:
            return tuple(-item for item in vec)
    return vec


def monom(a=0, b=0, c=0, coeff=1):
    return {} if coeff == 0 else {(a, b, c): coeff}


def poly_add(left, right):
    out = dict(left)
    for key, value in right.items():
        out[key] = out.get(key, 0) + value
        if out[key] == 0:
            del out[key]
    return out


def poly_scale(poly, factor):
    return {key: factor * value for key, value in poly.items() if factor * value}


def poly_mul(left, right):
    out = {}
    for (a, b, c), u in left.items():
        for (d, e, f), v in right.items():
            key = (a + d, b + e, c + f)
            out[key] = out.get(key, 0) + u * v
            if out[key] == 0:
                del out[key]
    return out


def splitting_identity():
    a, b, c = monom(1, 0, 0), monom(0, 1, 0), monom(0, 0, 1)
    qx = poly_add(poly_scale(poly_mul(a, b), 2), poly_mul(c, poly_add(a, b)))
    ya = poly_add(monom(coeff=2), poly_scale(a, -1))
    yb = poly_add(monom(coeff=2), poly_scale(b, -1))
    yc = poly_scale(c, -1)
    qy = poly_add(poly_scale(poly_mul(ya, yb), 2), poly_mul(yc, poly_add(ya, yb)))
    difference = poly_add(qy, poly_scale(qx, -1))
    expect = poly_add(monom(coeff=8), poly_add(poly_scale(a, -4), poly_add(poly_scale(b, -4), poly_scale(c, -4))))
    require(difference == expect, "Q(2I-X)-Q(X) is not 4(2-trace X)")
    # (2-c)^2 - 2 c (c-2) = 4-c^2, the discriminant of the trace-2 slice.
    cc = monom(0, 0, 1)
    two = monom(coeff=2)
    two_minus = poly_add(two, poly_scale(cc, -1))
    disc = poly_add(poly_mul(two_minus, two_minus), poly_scale(poly_mul(cc, poly_add(cc, poly_scale(two, -1))), -2))
    expect_disc = poly_add(monom(coeff=4), poly_scale(poly_mul(cc, cc), -1))
    require(disc == expect_disc, "the trace-2 discriminant is not 4-c^2")


def integral_splits():
    # For an integer c with |c| >= 3, c^2 >= 3^2 = 9 > 4, so 4-c^2 < 0.
    require(3 * 3 == 9 and 9 > 4, "the integer bound 3^2 > 4 failed")
    found = []
    nonsquares = []
    for c_value in range(-2, 3):
        disc = 4 - c_value * c_value
        root = int(disc ** 0.5)
        if root * root != disc:
            nonsquares.append(c_value)
            continue
        for sign in { -root, root }:
            if (2 - c_value + sign) % 2:
                continue
            a_value = (2 - c_value + sign) // 2
            b_value = 2 - c_value - a_value
            frame = (a_value, b_value, c_value)
            partner = (2 - a_value, 2 - b_value, -c_value)
            if rank_one_nonzero(frame) and rank_one_nonzero(partner):
                found.append(frame)
    require(nonsquares == [-1, 1], "the only non-square discriminants in -2..2 are not c=±1")
    require(sorted(set(found)) == [(0, 0, 2), (0, 2, 0), (2, 0, 0), (2, 2, -2)], "integral 2I splits changed")
    for frame in found:
        require(quad(sub(TWO_I, frame)) == 0, "integral partner left the cone")
        require(frame[2] % 2 == 0, "an integral splitting has odd c")


def chart(parameter):
    parameter = Fraction(parameter)
    den = 1 + parameter * parameter
    return (
        Fraction(2 * (1 - parameter), den),
        Fraction(2 * parameter * (parameter - 1), den),
        Fraction(4 * parameter, den),
    )


def direction_of(frame):
    scale_frame = coefficient_direction(frame)
    require(scale_frame is not None, "frame is not a primitive rank-one expansion")
    return scale_frame


def coefficient_direction(frame):
    # Recover a primitive integer direction when the frame is s uu^T.
    a, b, c = (Fraction(value) for value in frame)
    if c == 0:
        if a == 0 and b != 0:
            return ((0, 1), b)
        if b == 0 and a != 0:
            return ((1, 0), a)
        return None
    if a == 0 and b == 0:
        # u = v, and c = 2 s u^2, so the direction is (1,1) and s = c/2.
        return ((1, 1), c / 2)
    if a == 0:
        return None
    # b/a = -v/u when a != 0. Use c = 2 s u v.
    ratio = -b / a
    # ratio = v/u. Choose a small integer representation.
    num, den = ratio.numerator, ratio.denominator
    direction = (den, num)
    g = gcd(abs(direction[0]), abs(direction[1]))
    direction = (direction[0] // g, direction[1] // g)
    u, v = direction
    base = (u * (u - v), v * (v - u), 2 * u * v)
    require(base[0] != 0, "direction formula lost the a coordinate")
    scale = a / base[0]
    require(tuple(scale * value for value in base) == (a, b, c), "scale does not reproduce the frame")
    return direction, scale


def support_pairs(name):
    opposite = OPPOSITE[name]
    first, second = OTHER_PAIR[name]
    return (
        add((BY_NAME[opposite], BY_NAME[first])),
        add((BY_NAME[opposite], BY_NAME[second])),
        add((BY_NAME[name], BY_NAME[first])),
        add((BY_NAME[name], BY_NAME[second])),
    )


def construction():
    require(add((BY_NAME["A"], BY_NAME["B"], BY_NAME["P"], BY_NAME["Q"])) == TWO_I, "the four projectors do not sum to 2I")
    for name, projector in PROJECTORS:
        require(rank_one_nonzero(projector), name + " is not rank one")
        require(sum(projector) == 1, name + " does not have trace 1")
        require(not rank_one_nonzero(sub(TWO_I, projector)), "2I-E is rank one for " + name)
        others = [BY_NAME[item] for item in (OPPOSITE[name],) + OTHER_PAIR[name]]
        require(add(others) == sub(TWO_I, projector), "the complementary projectors do not sum to 2I-E")
        pairs = support_pairs(name)
        require(sorted(pairs) == sorted(TARGETS), "the four cross pairs are not the four targets for " + name)
        for left, right in (((2, 0, 0), (0, 2, 0)), ((0, 0, 2), (2, 2, -2))):
            frames = others + [left, right]
            require(add(frames) == sub(TOTAL, projector), "integral witness misses 4I-E for " + name)
            for frame in frames:
                require(rank_one_nonzero(frame), "integral witness frame is not rank one")
            detected = sum(frame[2] % 2 for frame in frames) + (projector[2] % 2)
            require(detected == 2, "integral witness does not detect exactly two odd-c calls")
    for parameter in (0, 1, 2, 3, Fraction(1, 2), 5):
        left = chart(parameter)
        right = sub(TWO_I, left)
        require(rank_one_nonzero(left) and rank_one_nonzero(right), "chart point is not a splitting at " + str(parameter))
        require(sum(left) == 2, "chart point does not have trace 2")
    # The point at infinity of this chart is 2B.
    require(rank_one_nonzero((0, 2, 0)) and sub(TWO_I, (0, 2, 0)) == (2, 0, 0), "2B is not a splitting")
    nonparallel = chart(2)
    partner = sub(TWO_I, nonparallel)
    directions = []
    for frame, expected in (
        (BY_NAME["A"], (1, 0)),
        (BY_NAME["P"], (1, 1)),
        (BY_NAME["Q"], (1, -1)),
        (nonparallel, (1, 2)),
        (partner, (2, -1)),
    ):
        direction, _scale = direction_of(frame)
        # Normalise sign so the first nonzero coordinate is positive.
        if direction[0] < 0 or (direction[0] == 0 and direction[1] < 0):
            direction = (-direction[0], -direction[1])
        require(direction == expected, "direction moved: " + str(direction))
        directions.append(direction)
    for i, left in enumerate(directions):
        for right in directions[i + 1 :]:
            require(left[0] * right[1] - left[1] * right[0] != 0, "two witness directions are parallel")
    frames = [BY_NAME["A"], BY_NAME["P"], BY_NAME["Q"], nonparallel, partner]
    require(add(frames) == sub(TOTAL, BY_NAME["B"]), "nonparallel witness misses 4I-B")
    require(set(support_pairs("B")) == set(TARGETS), "nonparallel pattern misses a target")


def character_targets():
    detected = 0
    for target in TARGETS:
        require((target[0] + target[1]) % 2 == 1 and target[2] % 2 == 1, "a target is not odd in both parities")
        detected += target[2] % 2
    require(detected == 4, "not every target has odd P-coefficient")


def hand_invertible():
    rows = [[(mask >> column) & 1 for column in range(5)] for mask in HAND_MASKS]
    rows.append([1, 1, 1, 1, 1])
    determinant, cofactors = minors(rows)
    require(determinant == -2, "the worked incidence determinant is not -2")
    adj_identity(rows, cofactors, determinant)
    rhs = []
    for index, target in enumerate(TARGETS):
        rhs.append(target)
    rhs.append(sub(TOTAL, HAND_E))
    frames = []
    for column in range(5):
        coords = []
        for coord in range(3):
            numer = sum(cofactors[row][column] * rhs[row][coord] for row in range(5))
            coords.append(Fraction(numer, determinant))
        frames.append(tuple(coords))
    require(tuple(frames) == HAND_FRAMES, "worked frames moved")
    for frame in frames:
        require(quad(frame) != 0, "worked invertible frame met the cone")
    # Positive control: the same matrix recovers the nonparallel witness from its own subset sums.
    witness = [BY_NAME["A"], BY_NAME["P"], BY_NAME["Q"], chart(2), sub(TWO_I, chart(2))]
    true_rhs = []
    for row in rows:
        true_rhs.append(tuple(sum(row[column] * witness[column][coord] for column in range(5)) for coord in range(3)))
    recovered = []
    for column in range(5):
        coords = []
        for coord in range(3):
            numer = sum(cofactors[row][column] * true_rhs[row][coord] for row in range(5))
            coords.append(Fraction(numer, determinant))
        recovered.append(tuple(coords))
    require(recovered == witness, "solver did not recover the nonparallel witness")
    tampered = [tuple(true_rhs[row]) for row in range(5)]
    tampered[4] = (tampered[4][0] + 1, tampered[4][1], tampered[4][2])
    moved = []
    for column in range(5):
        coords = []
        for coord in range(3):
            numer = sum(cofactors[row][column] * tampered[row][coord] for row in range(5))
            coords.append(Fraction(numer, determinant))
        moved.append(tuple(coords))
    require(moved != witness, "tampered total still recovered the witness")


def target_differences():
    bad = {projector for _name, projector in PROJECTORS}
    for left in TARGETS:
        for right in TARGETS:
            if left == right:
                continue
            require(sub(left, right) not in bad, "a target difference equals a projector")


def matrix_rows(masks):
    rows = [[(mask >> column) & 1 for column in range(5)] for mask in masks]
    rows.append([1, 1, 1, 1, 1])
    return rows


def rhs_for(masks, perm, projector):
    rhs = []
    for index in range(4):
        target = TARGETS[perm[index]]
        bit = (masks[index] >> 5) & 1
        rhs.append(tuple(target[coord] - bit * projector[coord] for coord in range(3)))
    rhs.append(sub(TOTAL, projector))
    return rhs


def particular_solution(rows, cofactors, rhs):
    pivot = None
    for i in range(5):
        for j in range(5):
            if cofactors[i][j] != 0:
                pivot = (i, j)
                break
        if pivot:
            break
    require(pivot is not None, "particular solution requested on a zero adjugate")
    i, j = pivot
    kernel = cofactors[i][:]
    require(kernel[j] != 0, "pivot cofactor vanished")
    for row in range(5):
        require(sum(rows[row][col] * kernel[col] for col in range(5)) == 0, "cofactor row is not a kernel vector")
    keep_rows = [row for row in range(5) if row != i]
    keep_cols = [col for col in range(5) if col != j]
    mat = [[rows[row][col] for col in keep_cols] for row in keep_rows]
    columns = []
    for coord in range(3):
        solved = solve4(mat, [rhs[row][coord] for row in keep_rows])
        require(solved is not None, "the pivot minor was singular")
        full = [None] * 5
        for col, value in zip(keep_cols, solved):
            full[col] = value
        full[j] = Fraction(0)
        columns.append(full)
    frames = [(columns[0][f], columns[1][f], columns[2][f]) for f in range(5)]
    for row in range(5):
        for coord in range(3):
            got = sum(rows[row][col] * frames[col][coord] for col in range(5))
            require(got == rhs[row][coord], "particular solution misses an equation")
    return frames, kernel


def left_kernel(rows):
    matrix = [[Fraction(rows[r][c]) for r in range(5)] for c in range(5)]
    pivots = {}
    rank = 0
    for col in range(5):
        pivot = None
        for row in range(rank, 5):
            if matrix[row][col] != 0:
                pivot = row
                break
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        pivot_value = matrix[rank][col]
        for entry in range(5):
            matrix[rank][entry] /= pivot_value
        for row in range(5):
            if row != rank and matrix[row][col] != 0:
                factor = matrix[row][col]
                for entry in range(5):
                    matrix[row][entry] -= factor * matrix[rank][entry]
        pivots[col] = rank
        rank += 1
    free = [col for col in range(5) if col not in pivots]
    basis = []
    for column in free:
        vector = [Fraction(0)] * 5
        vector[column] = Fraction(1)
        for col, row in pivots.items():
            vector[col] = -matrix[row][column]
        basis.append(vector)
    return rank, basis


def polar_blocks(frames, kernel, moving):
    """Linear conditions for every moving frame but the first to be rank one when the first is."""
    first = moving[0]
    scale = Fraction(kernel[first])
    equations = []
    for other in moving[1:]:
        ratio = Fraction(kernel[other]) / scale
        shift = tuple(frames[other][coord] - ratio * frames[first][coord] for coord in range(3))
        # B(shift, X) = -Q(shift)/ratio, with X the first moving frame.
        equations.append(
            (
                2 * shift[1] + shift[2],
                2 * shift[0] + shift[2],
                shift[0] + shift[1],
                -quad(shift) / ratio,
            )
        )
    return equations


def linear_rank(equations):
    if not equations:
        return 0, [], {}
    matrix = [[Fraction(value) for value in row] for row in equations]
    pivots = {}
    rank = 0
    for col in range(3):
        pivot = None
        for row in range(rank, len(matrix)):
            if matrix[row][col] != 0:
                pivot = row
                break
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        pivot_value = matrix[rank][col]
        for entry in range(4):
            matrix[rank][entry] /= pivot_value
        for row in range(len(matrix)):
            if row != rank and matrix[row][col] != 0:
                factor = matrix[row][col]
                for entry in range(4):
                    matrix[row][entry] -= factor * matrix[rank][entry]
        pivots[col] = rank
        rank += 1
    for row in range(rank, len(matrix)):
        if matrix[row][3] != 0:
            return -1, None, None
    return rank, matrix, pivots


def completes(frames, kernel, moving):
    equations = polar_blocks(frames, kernel, moving)
    for equation in equations:
        if equation[0] == 0 and equation[1] == 0 and equation[2] == 0 and equation[3] != 0:
            return False
    usable = [equation for equation in equations if equation[:3] != (0, 0, 0)]
    rank, matrix, pivots = linear_rank(usable)
    if rank < 0:
        return False
    point = [Fraction(0), Fraction(0), Fraction(0)]
    for col, row in pivots.items():
        point[col] = matrix[row][3]
    free = [col for col in range(3) if col not in pivots]
    if free:
        # The only open families in this census are the trace-2 planes, handled
        # structurally before this call. A free polar system would be a new case.
        return None
    candidate = tuple(point)
    return quad(candidate) == 0 and candidate != (0, 0, 0)


def census():
    require(len(MASKS) == 50, "subset count is not 50")
    require(len(list(combinations(range(50), 4))) == 230300, "unordered domain is not 230300")
    twin = 0
    rank3 = 0
    invertible = 0
    hits = 0
    full_shapes = {}
    zero_masks = {1: 0, 3: 0}
    frozen_killed = {1: 0, 3: 0}
    consistent = {1: 0, 3: 0}
    survivors = 0
    by_projector = {name: 0 for name, _ in PROJECTORS}
    placements = set()
    for comb in combinations(range(50), 4):
        masks = [MASKS[index] for index in comb]
        groups = {}
        for mask in masks:
            groups.setdefault(mask & 31, []).append(mask)
        if any(len(group) > 1 for group in groups.values()):
            twin += 1
            for group in groups.values():
                require(len(group) <= 2, "a frame projection has more than two masks")
                if len(group) == 2:
                    require(group[0] ^ group[1] == 32, "duplicate rows are not an E-bit pair")
            continue
        rows = matrix_rows(masks)
        determinant, cofactors = minors(rows)
        adj_identity(rows, cofactors, determinant)
        if determinant != 0:
            invertible += 1
            columns = list(zip(*cofactors))
            for perm in PERMS:
                for _name, projector in PROJECTORS:
                    rhs = rhs_for(masks, perm, projector)
                    good = True
                    for column in columns:
                        numer = [
                            sum(column[row] * rhs[row][coord] for row in range(5))
                            for coord in range(3)
                        ]
                        if numer == [0, 0, 0] or 2 * numer[0] * numer[1] + numer[2] * (numer[0] + numer[1]) != 0:
                            good = False
                            break
                    if good:
                        hits += 1
            continue
        if all(cofactors[i][j] == 0 for i in range(5) for j in range(5)):
            rank3 += 1
            rank, basis = left_kernel(rows)
            require(rank == 3 and len(basis) == 2, "a zero adjugate was not rank 3")
            for vector in basis:
                for col in range(5):
                    require(sum(vector[row] * rows[row][col] for row in range(5)) == 0, "rank-3 vector is not a left kernel")
            require(basis[0] != basis[1], "rank-3 kernel vectors repeat")
            for perm in PERMS:
                for _name, projector in PROJECTORS:
                    rhs = rhs_for(masks, perm, projector)
                    inconsistent = False
                    for vector in basis:
                        for coord in range(3):
                            if sum(vector[row] * rhs[row][coord] for row in range(5)) != 0:
                                inconsistent = True
                                break
                        if inconsistent:
                            break
                    require(inconsistent, "a rank-3 system was consistent")
            continue
        row_index = next(i for i in range(5) if any(cofactors[i][j] for j in range(5)))
        kernel = cofactors[row_index]
        zeros = [index for index in range(5) if kernel[index] == 0]
        if not zeros:
            column = next(j for j in range(5) if kernel[j])
            shape = primitive([cofactors[row][column] for row in range(5)])
            require(shape[4] == -1 and sum(shape[:4]) == 2 and set(shape[:4]) <= {0, 1}, "full kernel shape is not a pair of subset rows")
            full_shapes[shape] = full_shapes.get(shape, 0) + 1
            for row in range(5):
                require(sum(shape[i] * rows[i][row] for i in range(5)) == 0, "full-kernel lambda misses the row dependence")
            continue
        require(len(zeros) in (1, 3), "unexpected frozen-frame count " + str(len(zeros)))
        zero_masks[len(zeros)] += 1
        moving = [index for index in range(5) if kernel[index] != 0]
        if len(zeros) == 3:
            require(len(moving) == 2, "three frozen frames did not leave two moving frames")
            require(kernel[moving[0]] + kernel[moving[1]] == 0, "a three-frozen kernel does not cancel")
        column = next(j for j in range(5) if kernel[j])
        lam = [cofactors[row][column] for row in range(5)]
        for row in range(5):
            require(sum(lam[i] * rows[i][row] for i in range(5)) == 0, "singular lambda is not a left kernel")
        for perm in PERMS:
            for name, projector in PROJECTORS:
                rhs = rhs_for(masks, perm, projector)
                if any(sum(lam[row] * rhs[row][coord] for row in range(5)) != 0 for coord in range(3)):
                    continue
                consistent[len(zeros)] += 1
                frames, solved_kernel = particular_solution(rows, cofactors, rhs)
                require(all((solved_kernel[i] == 0) == (kernel[i] == 0) for i in range(5)), "kernel zeros moved")
                killed = False
                for index in zeros:
                    if not rank_one_nonzero(frames[index]):
                        killed = True
                if killed:
                    frozen_killed[len(zeros)] += 1
                    continue
                if len(zeros) == 1:
                    completed = completes(frames, solved_kernel, moving)
                    require(completed is False, "a one-frozen family met the cone")
                    continue
                survivors += 1
                by_projector[name] += 1
                require(solved_kernel[moving[0]] + solved_kernel[moving[1]] == 0, "moving kernel coefficients do not cancel")
                moving_sum = add((frames[moving[0]], frames[moving[1]]))
                require(moving_sum == TWO_I, "survivor moving frames do not sum to 2I")
                frozen = []
                for index in zeros:
                    require(all(value.denominator == 1 for value in frames[index]), "frozen frame is not integral")
                    frozen.append(tuple(int(value) for value in frames[index]))
                expected = {BY_NAME[item] for item in (OPPOSITE[name],) + OTHER_PAIR[name]}
                require(set(frozen) == expected, "survivor frozen frames are not the complementary projectors")
                explicit = [None] * 5
                for index, frame in zip(zeros, frozen):
                    explicit[index] = frame
                explicit[moving[0]] = (2, 0, 0)
                explicit[moving[1]] = (0, 2, 0)
                placements.add((name, tuple(zip(zeros, frozen))))
                for row in range(5):
                    for coord in range(3):
                        got = sum(rows[row][col] * explicit[col][coord] for col in range(5))
                        require(got == rhs[row][coord], "2A+2B misses a survivor equation")
                for frame in explicit:
                    require(rank_one_nonzero(frame), "explicit survivor frame is not rank one")
    require(twin == 22370, "twin count changed: " + str(twin))
    require(rank3 == 2450, "rank-3 count changed: " + str(rank3))
    require(invertible == 120400, "invertible count changed: " + str(invertible))
    require(hits == 0, "an invertible system met the cone")
    require(full_shapes == FULL_SHAPES, "full-kernel shapes changed: " + str(full_shapes))
    require(consistent == {1: 17280, 3: 28800}, "consistent singular counts changed: " + str(consistent))
    require(frozen_killed == {1: 16320, 3: 28560}, "frozen-kill counts changed: " + str(frozen_killed))
    require(survivors == 240, "survivor count changed: " + str(survivors))
    require(by_projector == {"A": 60, "B": 60, "P": 60, "Q": 60}, "survivors are not uniform in E")
    require(len(placements) == 240, "projector placements are not in bijection with the survivors")
    require(zero_masks == {1: 27840, 3: 53400}, "frozen-pattern counts changed: " + str(zero_masks))
    require(
        twin + rank3 + invertible + sum(full_shapes.values()) + zero_masks[1] + zero_masks[3] == 230300,
        "the mask domain was not partitioned",
    )


def failure_controls():
    require(not rank_one_nonzero((0, 0, 0)), "zero was accepted")
    require(not rank_one_nonzero((1, 1, 0)), "I was accepted")
    require(quad((1, 1, 0)) == 2, "Q(I) changed")
    broken = (1, 0, 1)
    require(quad(broken) == 1, "Q(A+P) changed")
    require(not rank_one_nonzero(broken), "A+P was accepted as rank one")


def main():
    require(len(PERMS) == 24, "there are not 24 target assignments")
    require(det4((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)) == 1, "det I_4 is not 1")
    for target in TARGETS:
        require(sum(target) == 2, "a target trace is not 2")
        require(quad(target) == 1, "twice a target determinant is not 1")
        complement = (4 - target[0], 4 - target[1], -target[2])
        require(quad(complement) == 17, "twice det(4I-H) is not 17")
    splitting_identity()
    integral_splits()
    construction()
    character_targets()
    target_differences()
    hand_invertible()
    failure_controls()
    census()
    print("PASS five-signed-one-old checks")


if __name__ == "__main__":
    main()
