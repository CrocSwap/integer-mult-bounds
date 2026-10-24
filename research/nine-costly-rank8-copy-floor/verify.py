#!/usr/bin/env python3
"""Rank-(8, 8) copy bill for every term count of the E8 root Gram.

Finite census and witness controls for the written argument in PROOF.md.
Standard library only. Explicit checks stay active under python -O.
"""

from fractions import Fraction
import itertools
import math


def fail(message):
    raise SystemExit("FAIL_NINE_COSTLY_RANK8_COPY_FLOOR " + message)


def check(name, condition, detail):
    if not condition:
        fail(name + ": " + detail)
    print("PASS", name)


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def doubled_inner(left, right):
    value = dot(left, right)
    if value % 4 != 0:
        fail("doubled inner product is not a multiple of 4")
    return value // 4


def e8_roots():
    roots = []
    for i, j in itertools.combinations(range(8), 2):
        for si in (1, -1):
            for sj in (1, -1):
                vector = [0] * 8
                vector[i] = 2 * si
                vector[j] = 2 * sj
                roots.append(tuple(vector))
    for signs in itertools.product((1, -1), repeat=8):
        if signs.count(-1) % 2 == 0:
            roots.append(tuple(signs))
    return roots


def root_lines(roots):
    lines = []
    seen = set()
    for root in roots:
        opposite = tuple(-entry for entry in root)
        key = root if root > opposite else opposite
        if key not in seen:
            seen.add(key)
            lines.append(root)
    return lines


def f2_rank(rows):
    basis = {}
    for value in rows:
        while value:
            pivot = value.bit_length() - 1
            if pivot in basis:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                break
    return len(basis)


def rational_rank(columns):
    if not columns:
        return 0
    width = len(columns)
    height = len(columns[0])
    matrix = [[Fraction(column[row]) for column in columns] for row in range(height)]
    rank = 0
    for column in range(width):
        pivot = next((row for row in range(rank, height) if matrix[row][column]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        scale = matrix[rank][column]
        for row in range(height):
            if row != rank and matrix[row][column]:
                factor = matrix[row][column] / scale
                for entry in range(column, width):
                    matrix[row][entry] -= factor * matrix[rank][entry]
        rank += 1
    return rank


def real_span_rank(vectors):
    return rational_rank([[Fraction(entry) for entry in vector] for vector in vectors])


def solve_linear(matrix, rhs):
    size = len(matrix)
    augmented = [[Fraction(entry) for entry in row] + [Fraction(value)]
                 for row, value in zip(matrix, rhs)]
    for column in range(size):
        pivot = next(row for row in range(column, size) if augmented[row][column])
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scale = augmented[column][column]
        for row in range(size):
            if row != column and augmented[row][column]:
                factor = augmented[row][column] / scale
                augmented[row] = [entry - factor * other
                                  for entry, other in zip(augmented[row], augmented[column])]
    return [augmented[row][size] / augmented[row][row] for row in range(size)]


def determinant(matrix):
    size = len(matrix)
    rows = [[Fraction(entry) for entry in row] for row in matrix]
    sign = 1
    for column in range(size):
        pivot = next((row for row in range(column, size) if rows[row][column]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            rows[column], rows[pivot] = rows[pivot], rows[column]
            sign = -sign
        for row in range(column + 1, size):
            factor = rows[row][column] / rows[column][column]
            for entry in range(column, size):
                rows[row][entry] -= factor * rows[column][entry]
    value = Fraction(sign)
    for index in range(size):
        value *= rows[index][index]
    return value


def pairing_rows(lines):
    count = len(lines)
    inner = [[doubled_inner(lines[i], lines[j]) for j in range(count)] for i in range(count)]
    rows = [sum(((inner[i][j] + 1) & 1) << j for j in range(count)) for i in range(count)]
    return inner, rows


def label_masks(pairing):
    basis = []
    for index, row in enumerate(pairing):
        if f2_rank([pairing[item] for item in basis] + [row]) == len(basis) + 1:
            basis.append(index)
        if len(basis) == 9:
            break
    coordinates = [sum(((pairing[index] >> bit) & 1) << place
                       for place, bit in enumerate(basis))
                   for index in range(len(pairing))]
    masks = []
    for functional in range(1, 512):
        mask = 0
        for index, coordinate in enumerate(coordinates):
            if (functional & coordinate).bit_count() & 1:
                mask |= 1 << index
        masks.append(mask)
    return masks


def support_of(lines, normal):
    mask = 0
    for index, line in enumerate(lines):
        if dot(line, normal):
            mask |= 1 << index
    return mask


def pair_rank(pairing, left_mask, right_mask):
    rows = []
    left = left_mask
    while left:
        bit = left.bit_length() - 1
        rows.append(pairing[bit] & right_mask)
        left ^= 1 << bit
    return f2_rank(rows)


def span_of(pairing, mask):
    rows = []
    value = mask
    while value:
        bit = value.bit_length() - 1
        rows.append(pairing[bit])
        value ^= 1 << bit
    return f2_rank(rows)


def profile(masks, support):
    hits = [mask & support for mask in masks]
    ordered = sorted(hit.bit_count() for hit in hits)
    smallest_pair = min((hits[left] | hits[right]).bit_count()
                        for left in range(len(hits)) for right in range(left + 1, len(hits)))
    return ordered[0], ordered[1], smallest_pair


def simple_roots():
    system = [(1, -1, -1, -1, -1, -1, -1, 1), (2, 2, 0, 0, 0, 0, 0, 0),
              (-2, 2, 0, 0, 0, 0, 0, 0)]
    for index in range(1, 6):
        vector = [0] * 8
        vector[index] = -2
        vector[index + 1] = 2
        system.append(tuple(vector))
    return system


def fundamental_weights(system):
    weights = []
    for index in range(8):
        matrix = [[Fraction(entry, 2) for entry in root] for root in system]
        weights.append(solve_linear(matrix, [1 if place == index else 0 for place in range(8)]))
    return weights


def dominant_weights(gram, norm_limit):
    bounds = []
    for index in range(8):
        limit = 0
        while gram[index][index] * (limit + 1) * (limit + 1) <= norm_limit:
            limit += 1
        bounds.append(limit)
    found = []

    def walk(index, coefficients, norm):
        if index == 8:
            found.append((tuple(coefficients), norm))
            return
        for value in range(bounds[index] + 1):
            extra = gram[index][index] * value * value
            extra += 2 * value * sum(gram[index][earlier] * coefficients[earlier]
                                     for earlier in range(index))
            if norm + extra > norm_limit:
                break
            coefficients.append(value)
            walk(index + 1, coefficients, norm + extra)
            coefficients.pop()

    walk(0, [], 0)
    return found


def integer_weights(weights):
    denominator = 1
    for weight in weights:
        for coordinate in weight:
            denominator = denominator * coordinate.denominator // math.gcd(
                denominator, coordinate.denominator)
    return denominator, [tuple(int(coordinate * denominator) for coordinate in weight)
                         for weight in weights]


def flat_mask(lines, coefficients, integer_weight):
    vector = [0] * 8
    for coefficient, weight in zip(coefficients, integer_weight):
        if coefficient:
            for index in range(8):
                vector[index] += coefficient * weight[index]
    mask = 0
    orthogonal = []
    for index, line in enumerate(lines):
        if dot(vector, line) == 0:
            mask |= 1 << index
            orthogonal.append(line)
    return mask, orthogonal, vector


def frame_normals():
    normals = []
    for plane in range(4):
        for sign in (1, -1):
            vector = [0] * 8
            vector[2 * plane] = 1
            vector[2 * plane + 1] = sign
            normals.append(tuple(vector))
    return normals


def split_normals():
    left = [(1, 1, 0, 0, 0, 0, 0, 0), (1, -1, 0, 0, 0, 0, 0, 0)]
    right = [(1, 0, 0, 0, 0, 0, 0, 0), (1, 0, 0, 0, 0, 0, 0, 0)]
    for index in range(1, 8):
        row = [0] * 8
        column = [0] * 8
        row[index] = 2
        column[index] = 1
        left.append(tuple(row))
        right.append(tuple(column))
    return left, right


def sum_outer(left_normals, right_normals):
    matrix = [[0] * 8 for _ in range(8)]
    for left, right in zip(left_normals, right_normals):
        for row in range(8):
            for column in range(8):
                matrix[row][column] += left[row] * right[column]
    return matrix


def is_twice_identity(matrix):
    for row in range(8):
        for column in range(8):
            expected = 2 if row == column else 0
            if matrix[row][column] != expected:
                return False
    return True


def term_costs(lines, pairing, left_normals, right_normals, deleted=0):
    costs = []
    for left, right in zip(left_normals, right_normals):
        left_mask = support_of(lines, left) & ~deleted
        right_mask = support_of(lines, right) & ~deleted
        costs.append(pair_rank(pairing, left_mask, right_mask))
    return costs


def frame_deletion(lines):
    deleted = 0
    for normal in frame_normals():
        doubled = tuple(2 * entry for entry in normal)
        deleted |= 1 << lines.index(doubled)
    return deleted


def section_geometry(lines, pairing, inner):
    count = len(lines)
    check("A.lines", count == 120, "expected 120 root lines")
    off_values = {inner[i][j] for i in range(count) for j in range(count) if i != j}
    check("A.inner-products",
          all(inner[i][i] == 2 for i in range(count)) and off_values == {-1, 0, 1},
          "line inner products must be 2, 0 or ±1")
    check("A.pairing-rank", f2_rank(pairing) == 9 and len(set(pairing)) == count,
          "the label pairing must have rank 9 and distinct rows")
    system = simple_roots()
    cartan = [[doubled_inner(system[i], system[j]) for j in range(8)] for i in range(8)]
    check("A.cartan-det", determinant(cartan) == 1 and
          all(cartan[i][j] <= 0 for i in range(8) for j in range(8) if i != j),
          "the simple-root Gram determinant must be 1")
    coefficients = []
    for root in e8_roots():
        right = [doubled_inner(root, simple) for simple in system]
        coefficients.append(solve_linear(cartan, right))
    check("A.roots-in-lattice",
          all(value.denominator == 1 for row in coefficients for value in row),
          "every root must be an integer combination of the simple system")
    check("A.root-span", real_span_rank(system) == 8, "the simple roots must span R^8")
    return system, cartan


def section_census(lines, pairing, masks):
    violator_sizes = sorted({mask.bit_count() for mask in masks})
    check("B.violator-sizes", violator_sizes == [56, 64, 120],
          "nonzero label violators must have sizes 56, 64 and 120")
    universe = (1 << 120) - 1
    kernel_spans = sorted({span_of(pairing, universe ^ mask) for mask in masks if mask.bit_count() != 120})
    check("B.kernel-sizes", kernel_spans == [8],
          "the complement of every proper violator must span exactly 8 label dimensions")
    system = simple_roots()
    weights = fundamental_weights(system)
    gram = [[sum(weights[i][place] * weights[j][place] for place in range(8))
             for j in range(8)] for i in range(8)]
    denominator, integer_weight = integer_weights(weights)
    check("B.weight-denominator", denominator == 2, "fundamental weights must clear over denominator 2")
    dominant = dominant_weights(gram, 128)
    check("B.dominant-count", len(dominant) == 383, "expected 383 dominant vectors of norm at most 128")
    unique = {}
    root_direction = (0, 0, 0, 0, 0, 0, 1, 1)
    root_like = []
    for coefficients, norm in dominant:
        if norm == 0:
            continue
        mask, orthogonal, vector = flat_mask(lines, coefficients, integer_weight)
        unique.setdefault(mask, (coefficients, norm, orthogonal, vector))
        if mask.bit_count() == 63:
            root_like.append(vector)
    rank7 = []
    lower = []
    for mask, (coefficients, norm, orthogonal, vector) in unique.items():
        rank = real_span_rank(orthogonal)
        record = (mask.bit_count(), rank, coefficients, norm, vector, orthogonal)
        if rank == 7:
            rank7.append((mask,) + record)
        else:
            lower.append(record)
    sizes = sorted({item[1] for item in rank7})
    check("B.hyperplane-sizes", sizes == [14, 16, 22, 23, 28, 37, 42, 63],
          "root-spanned hyperplanes must have one of the eight flat sizes")
    check("B.no-large-lower-flat", all(item[0] <= 42 for item in lower),
          "a dominant vector whose orthogonal roots span at most 6 dimensions has at most 42 lines")
    nonroot_ok = True
    root_ok = True
    for mask, size, rank, coefficients, norm, vector, orthogonal in (
            (item[0], item[1], item[2], item[3], item[4], item[5], item[6]) for item in rank7):
        smallest, second, pair = profile(masks, ((1 << 120) - 1) ^ mask)
        span = span_of(pairing, ((1 << 120) - 1) ^ mask)
        if size == 63:
            root_ok = root_ok and smallest == 1 and second == 24 and pair == 25 and span == 9
        else:
            nonroot_ok = nonroot_ok and smallest >= 14 and pair >= 25 and span == 9
    check("B.root-flat-profile", root_ok and len(root_like) == 8,
          "the only 63-line dominant flat must be the root profile")
    check("B.root-direction",
          all(vector[index] * root_direction[place] == vector[place] * root_direction[index]
              for vector in root_like for index in range(8) for place in range(8)),
          "every 63-line dominant normal must be a multiple of the root weight")
    check("B.nonroot-flat-profile", nonroot_ok,
          "every other root hyperplane needs at least 14 violators and 25 for a pair")
    root_profiles = True
    self_line = True
    for index, line in enumerate(lines):
        orthogonal = 0
        for other, candidate in enumerate(lines):
            if doubled_inner(line, candidate) == 0:
                orthogonal |= 1 << other
        support = ((1 << 120) - 1) ^ orthogonal
        smallest, second, pair = profile(masks, support)
        root_profiles = root_profiles and orthogonal.bit_count() == 63 and smallest == 1
        root_profiles = root_profiles and second == 24 and pair == 25 and span_of(pairing, support) == 9
        hits = [mask & support for mask in masks if (mask & support).bit_count() == 1]
        self_line = self_line and hits == [1 << index]
    check("B.every-root", root_profiles and self_line,
          "every root complement has profile (1, 24, 25), span 9, and self-line violator")
    samples = [[1 if place == index else 0 for place in range(8)] for index in range(8)]
    samples.append((1, 1, 1, 0, 0, 0, 0, 0))
    sample_spans = [span_of(pairing, support_of(lines, sample)) for sample in samples]
    check("B.sample-spans", sample_spans == [9] * len(samples),
          "axis and triple samples are controls, not a substitute for the census")


def section_witnesses(lines, pairing):
    frame = frame_normals()
    check("C.frame-identity", is_twice_identity(sum_outer(frame, frame)),
          "the coordinate frame must factor 2I")
    frame_costs = term_costs(lines, pairing, frame, frame)
    check("C.frame-cost", frame_costs == [9] * 8 and rational_rank(frame) == 8,
          "eight root-linear frame terms cost 9 each")
    left, right = split_normals()
    split_costs = term_costs(lines, pairing, left, right)
    check("C.split-identity", is_twice_identity(sum_outer(left, right)) and rational_rank(left) == 8,
          "the nine-term split must remain inside factor rank 8 and factor 2I")
    check("C.split-cost", split_costs == [9] * 9 and sum(split_costs) == 81,
          "nine rank-8 terms cost 81 on all 120 lines")
    deleted = frame_deletion(lines)
    punctured = term_costs(lines, pairing, left, right, deleted)
    check("C.punctured-cost", deleted.bit_count() == 8 and punctured == [8, 8, 9, 9, 9, 9, 9, 9, 9],
          "the same nine terms cost 79 after deleting the coordinate frame")
    partial = frame[:7]
    check("C.seven-terms", not is_twice_identity(sum_outer(partial, partial)),
          "seven frame terms do not factor 2I")
    mutated = [list(normal) for normal in left]
    mutated[0][0] += 1
    mutated = [tuple(normal) for normal in mutated]
    check("C.mutated-split", not is_twice_identity(sum_outer(mutated, right)),
          "changing one split coordinate must leave 2I")
    excursion = excursion_control(lines, pairing, frame)
    check("C.excursion", excursion == (9, 80, 8),
          "a rank-9 excursion must be able to drop one term to cost 8")
    odd = odd_pair_cost(lines, pairing)
    check("C.odd-pair", odd == 7, "two odd punctured roots must have live pairing rank 7")
    root_support = support_of(lines, (1, 1, 0, 0, 0, 0, 0, 0))
    removed = root_support ^ (1 << lines.index((2, 2, 0, 0, 0, 0, 0, 0)))
    check("C.self-line-drop", span_of(pairing, root_support) == 9 and span_of(pairing, removed) == 8,
          "deleting a root from its own complement drops the label span from 9 to 8")


def excursion_control(lines, pairing, frame):
    columns = []
    for normal in frame:
        columns.append([dot(line, normal) for line in lines])
    pivot = next(index for index, value in enumerate(columns[0]) if value)
    spike = [0] * len(lines)
    spike[pivot] = columns[0][pivot]
    plus = [value + extra for value, extra in zip(columns[0], spike)]
    minus = [value - extra for value, extra in zip(columns[0], spike)]
    new_columns = [plus, minus] + columns[1:]
    rank = rational_rank(new_columns)
    costs = []
    for column, normal in zip(new_columns, [frame[0], frame[0]] + frame[1:]):
        right = support_of(lines, normal)
        left = 0
        for index, value in enumerate(column):
            if value:
                left |= 1 << index
        costs.append(pair_rank(pairing, left, right))
    # (x+e) y^T + (x-e) y^T = 2 x y^T, so halving both new right factors
    # preserves the frame identity. The supports are unchanged by that scale.
    if not is_twice_identity(sum_outer(frame, frame)):
        return None
    return rank, sum(costs), min(costs)


def odd_pair_cost(lines, pairing):
    alpha = (1, 1, 0, 0, 0, 0, 0, 0)
    beta = (1, 0, 1, 0, 0, 0, 0, 0)
    if doubled_inner((2, 2, 0, 0, 0, 0, 0, 0), (2, 0, 2, 0, 0, 0, 0, 0)) != 1:
        fail("the odd-pair sample is not an odd root pair")
    deleted = (1 << lines.index((2, 2, 0, 0, 0, 0, 0, 0))) | (
        1 << lines.index((2, 0, 2, 0, 0, 0, 0, 0)))
    left = support_of(lines, alpha) & ~deleted
    right = support_of(lines, beta) & ~deleted
    return pair_rank(pairing, left, right)


def main():
    roots = e8_roots()
    lines = root_lines(roots)
    inner, pairing = pairing_rows(lines)
    masks = label_masks(pairing)
    section_geometry(lines, pairing, inner)
    section_census(lines, pairing, masks)
    section_witnesses(lines, pairing)
    print("PASS_NINE_COSTLY_RANK8_COPY_FLOOR rank88_cost=9t "
          "p120_nine=81 p112_nine=79 excursion_rank9_cost=80 no_new_kappa")


if __name__ == "__main__":
    main()
