#!/usr/bin/env python3
"""Idempotent triples after the rank-1 matrix with rows (1, 1, 0, 0).

Over F_2, an ordered idempotent triple multiplies to I + x I exactly when
the first two factors annihilate each other and the third factor is
I + A + B. For the named rank-1 matrix, the 802-by-802 census finds 58
solutions, and those solutions are the zero-on-image extensions of the
idempotents of its kernel. Failures raise SystemExit, so python -O still
fails closed.
"""

from __future__ import annotations

import itertools

EYE = (1, 2, 4, 8)
ZERO = (0, 0, 0, 0)
NAMED = (1, 1, 0, 0)
E11 = (1, 0, 0, 0)
E33 = (0, 0, 4, 0)
SHARP = (3, 0, 0, 0)
IMAGE_VECTOR = 0b0011


def fail(message):
    raise SystemExit("FAIL: " + message)


def require(ok, message):
    if not ok:
        fail(message)


def add(left, right):
    return tuple(a ^ b for a, b in zip(left, right))


def mul(left, right):
    """Matrix product over F_2. Row masks, bit c of row r is entry (r, c)."""
    size = len(left)
    rows = []
    for i in range(size):
        mask = 0
        for j in range(size):
            acc = 0
            for k in range(size):
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


def rows_from_bits(bits, size):
    width = (1 << size) - 1
    return tuple((bits >> (size * row)) & width for row in range(size))


def gaussian_rank(matrix):
    rows = list(matrix)
    size = len(rows)
    rank = 0
    for col in range(size):
        pivot = next((i for i in range(rank, size) if (rows[i] >> col) & 1), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(size):
            if i != rank and (rows[i] >> col) & 1:
                rows[i] ^= rows[rank]
        rank += 1
    return rank


def image_size(matrix):
    size = len(matrix)
    return len({apply(matrix, vector) for vector in range(1 << size)})


def pmul(left, right):
    out = 0
    while left:
        bit = left & -left
        out ^= right << (bit.bit_length() - 1)
        left ^= bit
    return out


def gate(matrix):
    size = len(matrix)
    rows = []
    for i in range(size):
        row = []
        for j in range(size):
            poly = 1 if i == j else 0
            if (matrix[i] >> j) & 1:
                poly ^= 2
            row.append(poly)
        rows.append(tuple(row))
    return tuple(rows)


def mul_gate(left, right):
    size = len(left)
    out = [[0] * size for _ in range(size)]
    for i in range(size):
        for k in range(size):
            factor = left[i][k]
            if not factor:
                continue
            for j in range(size):
                out[i][j] ^= pmul(factor, right[k][j])
    return tuple(tuple(row) for row in out)


def multiply_gates(factors):
    acc = gate(factors[0])
    for matrix in factors[1:]:
        acc = mul_gate(acc, gate(matrix))
    return acc


def is_target(product):
    size = len(product)
    for i in range(size):
        for j in range(size):
            expected = 3 if i == j else 0
            if product[i][j] != expected:
                return False
    return True


def coefficient_matrices(first, middle, right):
    """Coefficients of x, x^2 and x^3 in (I+xA)(I+xB)(I+xC), over F_2."""
    cross = mul(first, middle)
    mixed = add(first, middle)
    linear = add(mixed, right)
    quadratic = add(cross, mul(mixed, right))
    cubic = mul(cross, right)
    return linear, quadratic, cubic


def subspaces(dimension):
    """Every linear subspace of F_2^dimension, as a frozenset of vectors."""
    ambient = 1 << dimension
    found = []
    for mask in range(1 << ambient):
        if (mask & 1) == 0:
            continue
        vectors = [vector for vector in range(ambient) if (mask >> vector) & 1]
        if all((mask >> (left ^ right)) & 1 for left in vectors for right in vectors):
            found.append(frozenset(vectors))
    return found


def projection(image, kernel, dimension):
    location = {}
    for image_vector in image:
        for kernel_vector in kernel:
            location[image_vector ^ kernel_vector] = image_vector
    require(len(location) == 1 << dimension, "image and kernel are not complementary")
    rows = []
    for row in range(dimension):
        mask = 0
        for col in range(dimension):
            if (location[1 << col] >> row) & 1:
                mask |= 1 << col
        rows.append(mask)
    return tuple(rows)


def projections(dimension, kernel_contains=None):
    """Idempotents, optionally with a fixed vector forced into the kernel."""
    spaces = subspaces(dimension)
    built = []
    complement_counts = {}
    for kernel in spaces:
        if kernel_contains is not None and kernel_contains not in kernel:
            continue
        kernel_dim = (len(kernel)).bit_length() - 1
        complements = 0
        for image in spaces:
            if len(image) * len(kernel) != 1 << dimension:
                continue
            if len(image & kernel) != 1:
                continue
            built.append(projection(image, kernel, dimension))
            complements += 1
        complement_counts.setdefault(kernel_dim, []).append(complements)
    return built, complement_counts


def embed_kernel_idempotent(kernel_rows):
    """Extend a 3-by-3 kernel map by zero on span{e0+e1}.

    Kernel coordinates (y1, y2, y3) are ambient coordinates (1, 2, 3).
    The decomposition e0 = (e0+e1) + e1 forces the first two columns to agree.
    """
    require(len(kernel_rows) == 3, "kernel map is not 3-by-3")
    rows = [0]
    for mask in kernel_rows:
        require(0 <= mask < 8, "kernel row is not a 3-bit mask")
        row = 0
        if mask & 1:
            row |= 0b0011
        if mask & 2:
            row |= 0b0100
        if mask & 4:
            row |= 0b1000
        rows.append(row)
    return tuple(rows)


def idempotents(size):
    found = []
    rank_histogram = {}
    for bits in range(1 << (size * size)):
        matrix = rows_from_bits(bits, size)
        if mul(matrix, matrix) != matrix:
            continue
        rank = gaussian_rank(matrix)
        require(image_size(matrix) == 1 << rank, "Gaussian rank differs from the image")
        rank_histogram[rank] = rank_histogram.get(rank, 0) + 1
        found.append(matrix)
    return found, rank_histogram


def check_named_matrix():
    require(mul(NAMED, NAMED) == NAMED, "named matrix is not idempotent")
    require(gaussian_rank(NAMED) == 1, "named matrix is not rank 1")
    require(NAMED != E11, "named matrix collapsed to E_11")
    require(all(apply(NAMED, vector) == (3 if vector & 1 else 0) for vector in range(16)),
            "named matrix is not x0 |-> x0(e0+e1)")
    kernel = [vector for vector in range(16) if apply(NAMED, vector) == 0]
    image = [vector for vector in range(16) if vector in (0, IMAGE_VECTOR)]
    require(kernel == [vector for vector in range(16) if (vector & 1) == 0], "kernel is not x0=0")
    require(len(kernel) == 8 and image == [0, IMAGE_VECTOR], "kernel or image has the wrong size")
    sums = {IMAGE_VECTOR * bit ^ vector for bit in (0, 1) for vector in kernel}
    require(sums == set(range(16)), "image and kernel do not span")
    require(len(set(kernel) & set(image)) == 1, "image meets the kernel")
    return kernel


def check_coefficient_reduction(named_idempotents):
    eye_gate = gate(EYE)
    one_sided = 0
    orthogonal = []
    for middle in named_idempotents:
        right = add(add(EYE, NAMED), middle)
        product = multiply_gates((NAMED, middle, right))
        linear, quadratic, cubic = coefficient_matrices(NAMED, middle, right)
        left_product = mul(NAMED, middle)
        right_product = mul(middle, NAMED)
        annihilates_on_right = right_product == ZERO
        annihilates_on_left = left_product == ZERO
        require(linear == EYE, "C=I+A+B did not make the linear coefficient I")
        require(quadratic == right_product, "quadratic coefficient is not BA")
        require(cubic == mul(left_product, NAMED), "cubic coefficient is not ABA")
        if annihilates_on_right:
            require(cubic == ZERO, "BA=0 left a cubic term")
        require((product == eye_gate) == (linear == EYE and quadratic == ZERO and cubic == ZERO),
                "coefficient equations disagree with the gate product")
        require((product == eye_gate) == annihilates_on_right, "BA=0 does not match the product")
        require(add(mul(right, right), right) == add(left_product, right_product),
                "C^2+C is not AB+BA")
        require((mul(right, right) == right) == (left_product == right_product),
                "third-factor idempotence is not AB=BA")
        if annihilates_on_right:
            require((mul(right, right) == right) == annihilates_on_left,
                    "with BA=0, third-factor idempotence is not AB=0")
        if annihilates_on_right:
            one_sided += 1
        if annihilates_on_left and annihilates_on_right:
            orthogonal.append(middle)
            require(right == add(add(EYE, NAMED), middle), "orthogonal third factor drifted")
            require(mul(right, right) == right, "orthogonal third factor is not idempotent")
    require(one_sided == 177 and len(orthogonal) == 58, "one-sided and orthogonal counts")
    return orthogonal


def check_kernel_extensions(orthogonal):
    kernel_idempotents, _ = idempotents(3)
    require(len(kernel_idempotents) == 58, "F_2^3 matrix idempotent count")
    spaces = subspaces(3)
    by_dim = {}
    for space in spaces:
        by_dim.setdefault(len(space).bit_length() - 1, []).append(space)
    require((len(by_dim[0]), len(by_dim[1]), len(by_dim[2]), len(by_dim[3])) == (1, 7, 7, 1),
            "F_2^3 subspace counts")
    rank_one = 0
    for line in by_dim[1]:
        complements = [plane for plane in by_dim[2] if len(plane & line) == 1]
        require(len(complements) == 4, "a line does not have four complementary planes")
        rank_one += len(complements)
    require(rank_one == 28, "rank-1 idempotents of F_2^3")
    built, _ = projections(3)
    require(len(built) == 1 + 28 + 28 + 1 == 58, "projection count on F_2^3")
    require(set(built) == set(kernel_idempotents), "projection construction missed a kernel idempotent")
    embedded = [embed_kernel_idempotent(matrix) for matrix in kernel_idempotents]
    require(embed_kernel_idempotent((0, 0, 0)) == ZERO, "zero kernel map")
    require(embed_kernel_idempotent((1, 2, 4)) == add(EYE, NAMED), "kernel identity extends to I+A")
    require(embed_kernel_idempotent((0, 2, 0)) == E33, "kernel line extends to E_33")
    require(set(embedded) == set(orthogonal), "kernel extensions are not the orthogonal idempotents")
    for matrix in embedded:
        require(mul(NAMED, matrix) == ZERO and mul(matrix, NAMED) == ZERO, "extension is not orthogonal")
        require(mul(matrix, matrix) == matrix, "extension is not idempotent")


def check_one_sided_projection_count():
    built, complement_counts = projections(4, kernel_contains=IMAGE_VECTOR)
    require(len(built) == 177, "projection count for matrices killing e0+e1")
    require(len(set(built)) == 177, "projection construction repeated a matrix")
    formula = 0
    for kernel_dim, counts in sorted(complement_counts.items()):
        expected = 1 << (kernel_dim * (4 - kernel_dim))
        require(all(count == expected for count in counts), "complement count is not 2^{k(4-k)}")
        formula += len(counts) * expected
    require(formula == 177, "closed complement formula")
    spaces = subspaces(4)
    containing = {}
    for space in spaces:
        if IMAGE_VECTOR in space:
            containing[len(space).bit_length() - 1] = containing.get(len(space).bit_length() - 1, 0) + 1
    require(containing == {1: 1, 2: 7, 3: 7, 4: 1}, "subspaces containing e0+e1")
    require(1 * 8 + 7 * 16 + 7 * 8 + 1 == 177, "arithmetic 8+112+56+1")
    four_idempotents, _ = idempotents(4)
    killed = [matrix for matrix in four_idempotents if apply(matrix, IMAGE_VECTOR) == 0]
    require(set(killed) == set(built), "BA=0 matrices are not the projections along kernels containing v")


def check_product_census(named_idempotents, orthogonal):
    gates = {matrix: gate(matrix) for matrix in named_idempotents}
    target = gates[EYE]
    hits = []
    visits = 0
    for middle in named_idempotents:
        left = mul_gate(gates[NAMED], gates[middle])
        for right in named_idempotents:
            visits += 1
            if mul_gate(left, gates[right]) != target:
                continue
            hits.append((middle, right))
            require(mul(NAMED, middle) == ZERO and mul(middle, NAMED) == ZERO, "hit is not orthogonal")
            require(right == add(add(EYE, NAMED), middle), "hit missed C=I+A+B")
    require(visits == 802 * 802, "idempotent pair scan was not exhaustive")
    require(len(hits) == 58, "solution count")
    require({middle for middle, _ in hits} == set(orthogonal),
            "solution middles are not the orthogonal idempotents")
    require(len({middle for middle, _ in hits}) == 58, "a middle factor solved twice")


def check_stage_embedding(orthogonal):
    """Place each classified triple on stage 0 of the eight-dimensional leaf space."""
    support = (1, 2, 4, 8, 0, 0, 0, 0)
    target = gate(support)
    for middle in orthogonal:
        right = add(add(EYE, NAMED), middle)
        embedded = tuple(matrix + (0, 0, 0, 0) for matrix in (NAMED, middle, right))
        for matrix in embedded:
            require(matrix[4:] == (0, 0, 0, 0), "embedded row left the stage block")
            require(all(row < 16 for row in matrix[:4]), "embedded column left the stage block")
        require(multiply_gates(embedded) == target, "stage-0 embedding missed I+x E_0")
    shortened = (NAMED + (0, 0, 0, 0), E33 + (0, 0, 0, 0))
    require(multiply_gates(shortened) != target, "two stage-0 factors already met I+x E_0")


def check_explicit_triples(orthogonal):
    third = add(add(EYE, NAMED), E33)
    exhibited = (NAMED, E33, third)
    zero_triple = (NAMED, ZERO, add(EYE, NAMED))
    require(E33 in orthogonal and ZERO in orthogonal, "explicit middles are not orthogonal")
    require(all(is_target(multiply_gates(triple)) for triple in (exhibited, zero_triple)),
            "explicit orthogonal triple missed I+x I_4")
    orders = 0
    for perm in itertools.permutations(exhibited):
        require(is_target(multiply_gates(perm)), "an order of the exhibited triple missed the target")
        orders += 1
    require(orders == 6, "six orders")
    require(not is_target(multiply_gates((NAMED, NAMED, NAMED))), "A cubed met the target")
    require(not is_target(multiply_gates((NAMED, E33, E33))), "a repeated middle factor met the target")
    sharp_right = add(add(EYE, NAMED), SHARP)
    require(mul(SHARP, SHARP) == SHARP, "sharpness middle factor is not idempotent")
    require(mul(SHARP, NAMED) == ZERO and mul(NAMED, SHARP) != ZERO, "sharpness annihilation pattern")
    require(mul(sharp_right, sharp_right) != sharp_right, "sharpness third factor became idempotent")
    require(is_target(multiply_gates((NAMED, SHARP, sharp_right))), "one-sided witness missed the product")
    require(SHARP not in orthogonal, "one-sided witness was counted as orthogonal")
    require((gaussian_rank(NAMED), gaussian_rank(E33), gaussian_rank(third)) == (1, 1, 2),
            "exhibited ranks")
    require((gaussian_rank(NAMED), gaussian_rank(ZERO), gaussian_rank(add(EYE, NAMED))) == (1, 0, 3),
            "endpoint ranks")


def main():
    check_named_matrix()
    named_idempotents, ranks = idempotents(4)
    require(len(named_idempotents) == 802, "M_4(F_2) idempotent count")
    require(ranks == {0: 1, 1: 120, 2: 560, 3: 120, 4: 1}, "idempotent rank histogram")
    require(NAMED in named_idempotents and E11 in named_idempotents, "named matrix or E_11 left the census")
    orthogonal = check_coefficient_reduction(named_idempotents)
    check_kernel_extensions(orthogonal)
    check_one_sided_projection_count()
    check_product_census(named_idempotents, orthogonal)
    check_explicit_triples(orthogonal)
    check_stage_embedding(orthogonal)
    print(
        "idempotents=802 ranks=0:1,1:120,2:560,3:120,4:1 "
        "named=(1,1,0,0) rank=1 "
        "orthogonal_solutions=58 one_sided_BA=177 "
        "kernel_extensions=58 pair_scans=643204 "
        "sharpness_nonidempotent_third=119 stage0_embeddings=58"
    )
    print("PASS_RANK1_IDEMPOTENT_TRIPLE_1100")


if __name__ == "__main__":
    main()
