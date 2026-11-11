#!/usr/bin/env python3
"""Middle factors after the rank-1 matrix with rows (1, 1, 0, 0).

Over F_2, C is forced to I+A+B. Exactly 296 of the 65536 matrices B satisfy
(I+xA)(I+xB)(I+xC) = I+x I_4. They are the three block families in PROOF.md.
Failures raise SystemExit, so python -O still fails closed.
"""

from __future__ import annotations

import hashlib

EYE = (1, 2, 4, 8)
ZERO = (0, 0, 0, 0)
A = (1, 1, 0, 0)
P = (0, 3, 4, 8)
W = (0, 1, 0, 0)
SHARP = (3, 0, 0, 0)
EXCLUDED = (4, 5, 0, 0)
V = 0b0011
TARGET = tuple(tuple(3 if i == j else 0 for j in range(4)) for i in range(4))
HAND_AFTER_TWO = (
    (3, 0, 0, 0),
    (0, 1, 0, 0),
    (0, 0, 1, 0),
    (0, 0, 0, 1),
)
# SHA256 of the 296 solution integers, ascending, one decimal per line, trailing newline.
SOLUTION_SHA256 = "07a59d5644b30bf5c78ec67fd58bdee01cc1048fc5dc20ea574fffe3e4ec5659"


def fail(message):
    raise SystemExit("FAIL: " + message)


def require(ok, message):
    if not ok:
        fail(message)


def add(left, right):
    return tuple(a ^ b for a, b in zip(left, right))


def mul(left, right):
    """Matrix product over F_2. Bit c of row r is entry (r, c)."""
    rows = []
    for i in range(4):
        mask = 0
        for j in range(4):
            acc = 0
            for k in range(4):
                acc ^= ((left[i] >> k) & 1) & ((right[k] >> j) & 1)
            mask |= acc << j
        rows.append(mask)
    return tuple(rows)


def apply(matrix, vector):
    out = 0
    for row, mask in enumerate(matrix):
        if (mask & vector).bit_count() & 1:
            out |= 1 << row
    return out


def rows_from_bits(bits):
    return tuple((bits >> (4 * row)) & 15 for row in range(4))


def bits_from_rows(rows):
    bits = 0
    for row, mask in enumerate(rows):
        bits |= mask << (4 * row)
    return bits


def pmul(left, right):
    out = 0
    while left:
        bit = left & -left
        out ^= right << (bit.bit_length() - 1)
        left ^= bit
    return out


def gate(matrix):
    rows = []
    for i in range(4):
        row = []
        for j in range(4):
            poly = 1 if i == j else 0
            if (matrix[i] >> j) & 1:
                poly ^= 2
            row.append(poly)
        rows.append(tuple(row))
    return tuple(rows)


def mul_gate(left, right):
    out = [[0] * 4 for _ in range(4)]
    for i in range(4):
        for k in range(4):
            factor = left[i][k]
            if not factor:
                continue
            for j in range(4):
                out[i][j] ^= pmul(factor, right[k][j])
    return tuple(tuple(row) for row in out)


def multiply_gates(factors):
    acc = gate(factors[0])
    for matrix in factors[1:]:
        acc = mul_gate(acc, gate(matrix))
    return acc


def image_size(matrix, dimension):
    return len({apply(matrix, vector) for vector in range(1 << dimension)})


def rank(matrix):
    size = image_size(matrix, 4)
    require(size and (size & (size - 1)) == 0, "image size is not a power of two")
    return size.bit_length() - 1


def is_idempotent(matrix):
    return mul(matrix, matrix) == matrix


def split_std(vector):
    """Write a standard vector as ell * v + k, with k in ker(A).

    v = e0 + e1. Bit 0 of k is the coefficient of e1, bit 1 of e2, bit 2 of e3.
    """
    e0 = (vector >> 0) & 1
    e1 = (vector >> 1) & 1
    e2 = (vector >> 2) & 1
    e3 = (vector >> 3) & 1
    return e0, (e0 ^ e1) | (e2 << 1) | (e3 << 2)


def join_std(ell, kay):
    e0 = ell & 1
    e1 = e0 ^ (kay & 1)
    e2 = (kay >> 1) & 1
    e3 = (kay >> 2) & 1
    return e0 | (e1 << 1) | (e2 << 2) | (e3 << 3)


def dot3(form, vector):
    return (form & vector).bit_count() & 1


def apply_delta(columns, vector):
    out = 0
    for index in range(3):
        if (vector >> index) & 1:
            out ^= columns[index]
    return out


def rows_from_images(images):
    rows = []
    for row in range(4):
        mask = 0
        for column, image in enumerate(images):
            if (image >> row) & 1:
                mask |= 1 << column
        rows.append(mask)
    return tuple(rows)


def matrix_from_blocks(alpha, gee, phi, columns):
    """B(ell v + k) = (alpha ell + phi(k)) v + (ell g + delta(k))."""
    images = []
    for bit in range(4):
        ell, kay = split_std(1 << bit)
        ell_image = ((alpha & ell) ^ dot3(phi, kay)) & 1
        kay_image = (gee if ell else 0) ^ apply_delta(columns, kay)
        images.append(join_std(ell_image, kay_image))
    return rows_from_images(images)


def extract_blocks(matrix):
    alpha, gee = split_std(apply(matrix, V))
    phi = 0
    columns = []
    for index, basis in enumerate((0b0010, 0b0100, 0b1000)):
        ell, kay = split_std(apply(matrix, basis))
        phi |= ell << index
        columns.append(kay)
    return alpha, gee, phi, tuple(columns)


def delta_idempotent(columns):
    for vector in range(8):
        image = apply_delta(columns, vector)
        if apply_delta(columns, image) != image:
            return False
    return True


def delta_kernel(columns):
    return frozenset(vector for vector in range(8) if apply_delta(columns, vector) == 0)


def form_kernel(phi):
    return frozenset(vector for vector in range(8) if dot3(phi, vector) == 0)


def family_of(alpha, gee, phi, columns):
    """Return 1, 2, 3, or 0 when the blocks are not a solution."""
    if alpha != 0 or not delta_idempotent(columns):
        return 0
    if gee != 0 and phi != 0:
        return 0
    if apply_delta(columns, gee) != 0:
        return 0
    if not delta_kernel(columns) <= form_kernel(phi):
        return 0
    if gee == 0 and phi == 0:
        return 1
    if gee == 0:
        return 2
    return 3


def all_deltas():
    for bits in range(512):
        yield tuple((bits >> (3 * index)) & 7 for index in range(3))


def subspaces():
    found = []
    for mask in range(256):
        if (mask & 1) == 0:
            continue
        vectors = [vector for vector in range(8) if (mask >> vector) & 1]
        if all((mask >> (left ^ right)) & 1 for left in vectors for right in vectors):
            found.append(frozenset(vectors))
    return found


def projection_columns(image, kernel):
    location = {}
    for image_vector in image:
        for kernel_vector in kernel:
            location[image_vector ^ kernel_vector] = image_vector
    require(len(location) == 8, "image and kernel are not complementary")
    return tuple(location[1 << index] for index in range(3))


def check_named_matrix():
    require(add(EYE, A) == P, "I+A is not the recorded projection")
    require(is_idempotent(A), "named matrix is not idempotent")
    require(rank(A) == 1, "named matrix does not have rank 1")
    images = {apply(A, vector) for vector in range(16)}
    require(images == {0, V}, "image of A is not span{e0+e1}")
    kernel = [vector for vector in range(16) if apply(A, vector) == 0]
    require(len(kernel) == 8, "kernel of A is not 3-dimensional")
    require(all((vector & 1) == 0 for vector in kernel), "kernel is not x0=0")
    for vector in range(16):
        ell, kay = split_std(vector)
        require(join_std(ell, kay) == vector, "splitting does not round-trip")
        require(split_std(join_std(ell, kay)) == (ell, kay), "join is not split")
    require(split_std(V) == (1, 0), "v is not the pure line vector")


def check_coordinate_bijection():
    seen = set()
    for bits in range(65536):
        alpha = bits & 1
        gee = (bits >> 1) & 7
        phi = (bits >> 4) & 7
        columns = tuple((bits >> (7 + 3 * index)) & 7 for index in range(3))
        matrix = matrix_from_blocks(alpha, gee, phi, columns)
        require(extract_blocks(matrix) == (alpha, gee, phi, columns), "extract missed a block tuple")
        require(matrix not in seen, "two block tuples built the same matrix")
        seen.add(matrix)
    require(len(seen) == 65536, "block tuples do not cover M_4(F_2)")
    for bits in range(65536):
        matrix = rows_from_bits(bits)
        alpha, gee, phi, columns = extract_blocks(matrix)
        require(
            matrix_from_blocks(alpha, gee, phi, columns) == matrix,
            "rebuilt matrix differs from the scanned matrix",
        )


def check_kernel_counts(idempotent_deltas):
    spaces = subspaces()
    by_dimension = {}
    for space in spaces:
        by_dimension.setdefault(len(space).bit_length() - 1, []).append(space)
    require([len(by_dimension[dim]) for dim in range(4)] == [1, 7, 7, 1], "subspace counts of F_2^3")
    lines = by_dimension[1]
    planes = by_dimension[2]
    whole = by_dimension[3][0]
    origin = by_dimension[0][0]
    for line in lines:
        complements = [plane for plane in planes if len(plane & line) == 1]
        require(len(complements) == 4, "a line does not have 4 complementary planes")
        through = [plane for plane in planes if line <= plane]
        require(len(through) == 3, "a line does not lie on 3 planes")
    for plane in planes:
        complements = [line for line in lines if len(plane & line) == 1]
        require(len(complements) == 4, "a plane does not have 4 complementary lines")
        inside = [line for line in lines if line <= plane]
        require(len(inside) == 3, "a plane does not contain 3 lines")
    built = []
    built.append(projection_columns(origin, whole))
    built.append(projection_columns(whole, origin))
    for line in lines:
        for plane in planes:
            if len(plane & line) == 1:
                built.append(projection_columns(line, plane))
    for plane in planes:
        for line in lines:
            if len(plane & line) == 1:
                built.append(projection_columns(plane, line))
    require(len(built) == 58 and len(set(built)) == 58, "subspace projections are not 58")
    require(set(built) == set(idempotent_deltas), "idempotent endomorphisms are not the projections")
    ranks = {}
    for columns in idempotent_deltas:
        image_count = len({apply_delta(columns, vector) for vector in range(8)})
        require(image_count and image_count & (image_count - 1) == 0, "delta image is not a power of two")
        ranks[image_count.bit_length() - 1] = ranks.get(image_count.bit_length() - 1, 0) + 1
    require(ranks == {0: 1, 1: 28, 2: 28, 3: 1}, "idempotent ranks of F_2^3 differ from 1,28,28,1")
    return lines, planes, whole, origin


def family_matrices(idempotent_deltas):
    family1 = [matrix_from_blocks(0, 0, 0, columns) for columns in idempotent_deltas]
    family2 = []
    family3 = []
    per_form = []
    per_vector = []
    for phi in range(1, 8):
        allowed = form_kernel(phi)
        chosen = []
        for columns in idempotent_deltas:
            if delta_kernel(columns) <= allowed:
                chosen.append(columns)
                family2.append(matrix_from_blocks(0, 0, phi, columns))
        per_form.append(len(chosen))
    for gee in range(1, 8):
        chosen = []
        for columns in idempotent_deltas:
            if apply_delta(columns, gee) == 0:
                chosen.append(columns)
                family3.append(matrix_from_blocks(0, gee, 0, columns))
        per_vector.append(len(chosen))
    require(per_form == [17] * 7, "a nonzero form does not admit 17 kernel idempotents")
    require(per_vector == [17] * 7, "a nonzero vector does not lie in 17 idempotent kernels")
    require(len(family1) == 58 and len(family2) == 119 and len(family3) == 119, "family sizes")
    constructed = family1 + family2 + family3
    require(len(set(constructed)) == 296, "the three families are not disjoint")
    return family1, family2, family3


def check_family_shapes(family1, family2, family3):
    for matrix in family1:
        third = add(P, matrix)
        require(is_idempotent(matrix) and is_idempotent(third), "family 1 is not an idempotent pair")
        require(mul(A, matrix) == ZERO and mul(matrix, A) == ZERO, "family 1 is not orthogonal")
    for matrix in family2:
        third = add(P, matrix)
        _alpha, _gee, phi, columns = extract_blocks(matrix)
        require(is_idempotent(matrix) and not is_idempotent(third), "family 2 idempotence pattern")
        require(mul(matrix, A) == ZERO and mul(A, matrix) != ZERO, "family 2 annihilation pattern")
        for vector in range(8):
            require(
                dot3(phi, apply_delta(columns, vector)) == dot3(phi, vector),
                "family 2 does not fix the linear form",
            )
    for matrix in family3:
        third = add(P, matrix)
        require(not is_idempotent(matrix) and is_idempotent(third), "family 3 idempotence pattern")
        require(mul(A, matrix) == ZERO and mul(matrix, A) != ZERO, "family 3 annihilation pattern")
        require(family_of(*extract_blocks(matrix)) == 3, "family 3 extractor label")


def check_rank_histogram(family1, family2, family3):
    def delta_rank(matrix):
        _alpha, _gee, _phi, columns = extract_blocks(matrix)
        image_count = len({apply_delta(columns, vector) for vector in range(8)})
        return image_count.bit_length() - 1

    histogram = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
    nilpotent = 0
    for matrix in family1:
        require(rank(matrix) == delta_rank(matrix), "family 1 rank formula")
        histogram[rank(matrix)] += 1
        if mul(matrix, matrix) == ZERO:
            nilpotent += 1
    for matrix in family2:
        require(rank(matrix) == delta_rank(matrix), "family 2 rank formula")
        histogram[rank(matrix)] += 1
        require(mul(matrix, matrix) == matrix, "family 2 square")
    for matrix in family3:
        require(rank(matrix) == 1 + delta_rank(matrix), "family 3 rank formula")
        histogram[rank(matrix)] += 1
        if mul(matrix, matrix) == ZERO:
            nilpotent += 1
            require(delta_rank(matrix) == 0 and rank(matrix) == 1, "nilpotent family 3 shape")
    require(histogram == {0: 1, 1: 63, 2: 196, 3: 36, 4: 0}, "solution rank histogram")
    require(nilpotent == 8, "nilpotent solution count")


def check_witnesses():
    third_w = add(add(EYE, A), W)
    require(third_w == (0, 2, 4, 8), "hand witness third factor")
    require(multiply_gates((A, W)) == HAND_AFTER_TWO, "hand product of the first two gates")
    require(multiply_gates((A, W, third_w)) == TARGET, "hand witness does not hit the target")
    require(not is_idempotent(W) and is_idempotent(third_w), "hand witness idempotence")
    require(family_of(*extract_blocks(W)) == 3, "hand witness is not family 3")
    third_s = add(add(EYE, A), SHARP)
    require(third_s == (3, 3, 4, 8), "one-sided witness third factor")
    require(is_idempotent(SHARP) and not is_idempotent(third_s), "one-sided witness idempotence")
    require(multiply_gates((A, SHARP, third_s)) == TARGET, "one-sided witness misses the target")
    require(family_of(*extract_blocks(SHARP)) == 2, "one-sided witness is not family 2")
    require(multiply_gates((A, ZERO, P)) == TARGET, "zero middle factor misses the target")
    require(family_of(*extract_blocks(ZERO)) == 1, "zero is not family 1")
    require(multiply_gates((A, EYE, add(add(EYE, A), EYE))) != TARGET, "identity was accepted")
    require(mul(EYE, add(EYE, P)) != ZERO, "identity satisfies the coefficient equation")
    require((bits_from_rows(W) ^ bits_from_rows(A)).bit_count() == 1, "A is not one bit from W")
    require(multiply_gates((A, A, add(add(EYE, A), A))) != TARGET, "one-bit neighbor of W was accepted")
    require(
        extract_blocks(EXCLUDED) == (0, 1, 2, (0, 0, 0)),
        "excluded witness blocks",
    )
    require(family_of(*extract_blocks(EXCLUDED)) == 0, "both-nonzero witness was classified")
    require(multiply_gates((A, EXCLUDED, add(P, EXCLUDED))) != TARGET, "both-nonzero witness was accepted")
    shifted = add(P, (1, 0, 0, 0))
    require(multiply_gates((A, ZERO, shifted)) != TARGET, "a shifted third factor was accepted")


def scan_domain(constructed):
    solutions = []
    solution_bits = []
    family_counts = {1: 0, 2: 0, 3: 0}
    for bits in range(65536):
        matrix = rows_from_bits(bits)
        require(bits_from_rows(matrix) == bits, "row packing is not bijective")
        third = add(P, matrix)
        product_ok = multiply_gates((A, matrix, third)) == TARGET
        coefficient_ok = mul(matrix, add(matrix, P)) == ZERO
        require(product_ok == coefficient_ok, "gate product and BC=0 disagree")
        alpha, gee, phi, columns = extract_blocks(matrix)
        family = family_of(alpha, gee, phi, columns)
        require((family != 0) == product_ok, "block family and gate product disagree")
        if product_ok:
            solutions.append(matrix)
            solution_bits.append(bits)
            family_counts[family] += 1
    require(len(solutions) == 296, "scan count is not 296")
    require(set(solutions) == set(constructed), "scan and block construction differ")
    require(family_counts == {1: 58, 2: 119, 3: 119}, "scanned family counts")
    idempotent_middle = sum(is_idempotent(matrix) for matrix in solutions)
    idempotent_third = sum(is_idempotent(add(P, matrix)) for matrix in solutions)
    both = sum(
        is_idempotent(matrix) and is_idempotent(add(P, matrix)) for matrix in solutions
    )
    neither = sum(
        (not is_idempotent(matrix)) and (not is_idempotent(add(P, matrix)))
        for matrix in solutions
    )
    require(idempotent_middle == 177 and idempotent_third == 177, "idempotent slice counts")
    require(both == 58 and neither == 0, "idempotence overlap")
    require(
        sum(mul(matrix, A) == ZERO for matrix in solutions) == 177,
        "BA=0 slice",
    )
    require(
        sum(mul(A, matrix) == ZERO for matrix in solutions) == 177,
        "AB=0 slice",
    )
    payload = "".join(f"{bits}\n" for bits in solution_bits).encode("ascii")
    digest = hashlib.sha256(payload).hexdigest()
    require(digest == SOLUTION_SHA256, "solution fingerprint changed: " + digest)


def main():
    check_named_matrix()
    check_coordinate_bijection()
    idempotent_deltas = [columns for columns in all_deltas() if delta_idempotent(columns)]
    require(len(idempotent_deltas) == 58, "F_2^3 does not have 58 idempotents")
    check_kernel_counts(idempotent_deltas)
    family1, family2, family3 = family_matrices(idempotent_deltas)
    check_family_shapes(family1, family2, family3)
    check_rank_histogram(family1, family2, family3)
    check_witnesses()
    scan_domain(family1 + family2 + family3)
    print("PASS_NONIDEMPOTENT_MIDDLE_1100")


if __name__ == "__main__":
    main()
