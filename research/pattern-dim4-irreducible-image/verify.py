#!/usr/bin/env python3
"""Finite checks for the pattern-dimension-4 four-cycle pool.

PROOF.md is the all-width argument. This program repeats the finite tables,
the complete subspace lattice of the joint image, and the width-4 through
width-8 pool scan. It also runs negative controls. It does not use assert,
so python -O does not skip checks. Standard library only.
"""

import itertools
import sys

MARKER = "PASS_PATTERN_DIM4_IRREDUCIBLE_IMAGE"
WIDTHS = range(4, 9)
PARITY_IMAGES = (7, 11, 13, 19, 21, 25, 31, 35, 37, 41, 47, 49, 55, 59, 61)


def fail(message):
    raise SystemExit("FAIL: " + message)


def require(condition, message):
    if not condition:
        fail(message)


def weight(mask):
    return mask.bit_count()


def dot(left, right):
    return weight(left & right) & 1


def pattern_mask(image, covector, width):
    mask = 0
    for row in range(width):
        if ((image >> row) & 1) == 0:
            continue
        for col in range(width):
            if row != col and ((covector >> col) & 1):
                mask |= 1 << (row * width + col)
    return mask


def cycle_projectors():
    """N_i = e_i (e_i + e_{i+1} + e_{i+2})^T on Z/4Z."""
    projectors = []
    for index in range(4):
        image = 1 << index
        covector = (1 << index) | (1 << ((index + 1) % 4)) | (1 << ((index + 2) % 4))
        projectors.append((image, covector))
    return tuple(projectors)


def rows_of(image, covector, width):
    return [covector if ((image >> row) & 1) else 0 for row in range(width)]


def matmul(left, right, width):
    product = []
    for row in left:
        acc = 0
        for index in range(width):
            if (row >> index) & 1:
                acc ^= right[index]
        product.append(acc)
    return product


def gaussian_count(dimension, rank):
    """Number of rank-dimensional subspaces of F2^dimension."""
    numerator = 1
    denominator = 1
    for step in range(rank):
        numerator *= (1 << dimension) - (1 << step)
        denominator *= (1 << rank) - (1 << step)
    return numerator // denominator


def span_data(masks):
    """Return (dimension, pivot map) for the XOR-span of masks."""
    pivots = {}
    for mask in masks:
        value = mask
        while value:
            bit = value & -value
            known = pivots.get(bit)
            if known is None:
                for other, vector in list(pivots.items()):
                    if vector & bit:
                        pivots[other] = vector ^ value
                pivots[bit] = value
                break
            value ^= known
    return len(pivots), pivots


def enumerate_span(pivots):
    vectors = [0]
    for vector in pivots.values():
        vectors += [old ^ vector for old in vectors]
    return vectors


def pattern_space(width):
    generators = [pattern_mask(image, covector, width) for image, covector in cycle_projectors()]
    dimension, pivots = span_data(generators)
    return dimension, set(enumerate_span(pivots))


def complete_pool(width, space):
    found = []
    for image, covector in itertools.product(range(1 << width), repeat=2):
        if dot(image, covector) != 1:
            continue
        mask = pattern_mask(image, covector, width)
        if mask and mask in space:
            found.append((image, covector))
    return found


def subspace_masks(dimension):
    """Every XOR-closed subset of F2^dimension, as a membership bitmask.

    Bit v of the membership mask is set when vector v belongs to the subset.
    The scan covers the power set, so the list is the complete subspace lattice.
    """
    size = 1 << dimension
    found = []
    for membership in range(1 << size):
        if (membership & 1) == 0:
            continue
        closed = True
        members = [vector for vector in range(size) if (membership >> vector) & 1]
        for left in members:
            for right in members:
                if ((membership >> (left ^ right)) & 1) == 0:
                    closed = False
                    break
            if not closed:
                break
        if closed:
            found.append(membership)
    return found


def preserves(membership, projectors):
    size = membership.bit_length()  # only used as a bound; vectors are below 1<<dim
    for vector in range(size):
        if ((membership >> vector) & 1) == 0:
            continue
        for image, covector in projectors:
            if dot(covector, vector) and ((membership >> image) & 1) == 0:
                return False
    return True


def generated_span(seed, projectors):
    """Smallest subspace containing seed and closed under the projectors."""
    span = {0, seed}
    growing = True
    while growing:
        growing = False
        for vector in list(span):
            for image, covector in projectors:
                if dot(covector, vector) and image not in span:
                    span.update(old ^ image for old in tuple(span))
                    growing = True
                    break
            if growing:
                break
    return span


def check_covector_basis():
    rows = [covector for _image, covector in cycle_projectors()]
    require(rows == [0b0111, 0b1110, 0b1101, 0b1011], "cycle covectors moved: %s" % (rows,))
    for index, row in enumerate(rows):
        require(weight(row) == 3, "covector %s does not have weight 3" % index)
        require(dot(1 << index, row) == 1, "projector %s is not idempotent" % index)
    matrix = [row for row in rows]
    # The row operations written in PROOF.md section 3.
    matrix[2] ^= matrix[0]
    matrix[3] ^= matrix[0]
    matrix[1] ^= matrix[2]
    matrix[0] ^= matrix[2]
    matrix[3] ^= matrix[1]
    matrix[0] ^= matrix[1]
    matrix[0] ^= matrix[3]
    matrix[2] ^= matrix[3]
    require(matrix == [1, 4, 2, 8],
            "covector reduction did not reach e0, e2, e1, e3: %s" % matrix)
    matrix[1], matrix[2] = matrix[2], matrix[1]
    require(matrix == [1, 2, 4, 8], "swapping the middle covector rows did not reach the identity")
    for column in range(4):
        hits = [row for row in rows if (row >> column) & 1]
        require(len(hits) == 3, "column %s has weight %s" % (column, len(hits)))


def check_pattern_space_and_pool():
    expected = cycle_projectors()
    for image, covector in expected:
        rows = rows_of(image, covector, 4)
        require(matmul(rows, rows, 4) == rows, "matrix square failed for %s, %s" % (image, covector))
    for width in WIDTHS:
        dimension, space = pattern_space(width)
        require(dimension == 4, "pattern dimension at width %s is %s" % (width, dimension))
        require(len(space) == 16, "pattern space at width %s is not 16 vectors" % width)
        for mask in space:
            if mask == 0:
                continue
            require(weight(mask) >= 2 and weight(mask) % 2 == 0,
                    "pattern weight %s at width %s is not a positive even number" % (weight(mask), width))
        unit = 1 << 1  # E_01 in row-major layout
        require(weight(unit) == 1 and unit not in space, "E_01 was not detected as a missing edge")
        edge_line = {0, unit}
        require(any(weight(mask) == 1 for mask in edge_line),
                "the edge control space does not contain a matrix unit")
        found = complete_pool(width, space)
        require(sorted(found) == sorted(expected),
                "width %s pool is %s" % (width, sorted(found)))
        for image, covector in found:
            require(image < 16 and covector < 16, "a factor uses a coordinate outside Z/4Z")


def check_irreducible_lattice():
    projectors = cycle_projectors()
    memberships = subspace_masks(4)
    by_size = {}
    for membership in memberships:
        by_size[weight(membership)] = by_size.get(weight(membership), 0) + 1
    expected_sizes = {1 << rank: gaussian_count(4, rank) for rank in range(5)}
    require(by_size == expected_sizes,
            "F2^4 subspace census %s does not match the Gaussian counts %s" % (by_size, expected_sizes))
    invariant = [membership for membership in memberships
                 if weight(membership) not in (1, 16) and preserves(membership, projectors)]
    require(invariant == [], "the four-cycle lattice has an invariant subspace")
    for seed in range(1, 16):
        require(generated_span(seed, projectors) == set(range(16)),
                "seed %s does not generate the joint image" % seed)

    plane_failures = (
        (0, 1, 2, 0),
        (0, 2, 1, 2),
        (0, 3, 1, 3),
        (1, 2, 0, 1),
        (1, 3, 0, 1),
        (2, 3, 0, 2),
    )
    rows = [covector for _image, covector in projectors]
    seen_pairs = set()
    for left, right, outsider, hit in plane_failures:
        seen_pairs.add(frozenset((left, right)))
        require((rows[outsider] >> hit) & 1,
                "plane pair %s,%s is not rejected by phi_%s" % (left, right, outsider))
    require(len(seen_pairs) == 6, "the six coordinate planes were not all tested")


def check_deletion_control():
    kept = cycle_projectors()[:3]
    line = 0b1011  # e0 + e1 + e3
    for image, covector in kept:
        require(dot(covector, line) == 0, "a retained projector moves the deleted-pool line")
    image, covector = cycle_projectors()[3]
    require(dot(covector, line) == 1 and image == 8, "N_3 does not move the control line")
    require(generated_span(line, kept) == {0, line}, "the deleted pool does not leave this line invariant")


def check_known_actions():
    # #6921 sharp example, restricted to span(e0, e1, e2). Must be irreducible.
    sharp = ((0b001, 0b111), (0b010, 0b011), (0b100, 0b101))
    sharp_spaces = subspace_masks(3)
    require(sum(gaussian_count(3, rank) for rank in range(4)) == len(sharp_spaces),
            "F2^3 subspace census is incomplete")
    sharp_invariant = [item for item in sharp_spaces if weight(item) not in (1, 8) and preserves(item, sharp)]
    require(sharp_invariant == [], "the dimension-3 sharp example was reported reducible")
    # Normal-form triple from #6921. Must be reducible.
    normal = ((0b110, 0b101), (0b101, 0b110), (0b111, 0b111))
    normal_invariant = [item for item in sharp_spaces if weight(item) not in (1, 8) and preserves(item, normal)]
    require(normal_invariant != [], "the normal-form triple was reported irreducible")


def check_parity_pool():
    images = []
    for mask in range(32):
        if weight(mask) % 2 == 0:
            images.append(1 ^ (mask << 1))
    images = [image for image in images if image != 1]
    require(sorted(images) == sorted(PARITY_IMAGES),
            "parity images differ from the #6838 width-6 witness: %s" % sorted(images))
    projectors = tuple((image, 1) for image in images)
    patterns = [pattern_mask(image, 1, 6) for image, _covector in projectors]
    dimension, pivots = span_data(patterns)
    require(dimension == 4, "parity pattern dimension is %s" % dimension)
    for mask in enumerate_span(pivots):
        require(weight(mask) != 1, "parity pattern space contains a matrix unit")
    image_dimension, image_pivots = span_data(images)
    require(image_dimension == 5, "parity joint image has dimension %s" % image_dimension)
    kernel = [vector for vector in enumerate_span(image_pivots) if (vector & 1) == 0]
    require(len(kernel) == 16, "parity kernel on the joint image has size %s" % len(kernel))
    require(any(vector & 1 for vector in enumerate_span(image_pivots)),
            "parity image has no vector with a nonzero e0 coordinate")
    # U is invariant because every covector is e0.
    require(all(dot(1, vector) == 0 for vector in kernel), "parity kernel is not the e0 kernel")


def main():
    check_covector_basis()
    check_pattern_space_and_pool()
    check_irreducible_lattice()
    check_deletion_control()
    check_known_actions()
    check_parity_pool()
    print(MARKER)
    return 0


if __name__ == "__main__":
    sys.exit(main())
