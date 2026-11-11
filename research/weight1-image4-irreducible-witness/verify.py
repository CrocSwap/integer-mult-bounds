#!/usr/bin/env python3
"""Finite checks for one irreducible weight-1 image-dimension-4 pool.

PROOF.md is the all-width argument. This program repeats the pattern
weights, the pair obstruction, the width-4 through width-8 pool scan, and
the 67 subspaces of the joint image. The four disjoint lines and a deleted
projector are reducible controls. The #6962 four-cycle is a weight-3
control. The program does not use assert, so python -O does not skip
checks. Standard library only.
"""

import itertools
import sys

MARKER = "PASS_WEIGHT1_IMAGE4_IRREDUCIBLE"
WIDTHS = range(4, 9)


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


def transpose_mask(mask, width):
    out = 0
    for row in range(width):
        for col in range(width):
            bit = row * width + col
            if (mask >> bit) & 1:
                out |= 1 << (col * width + row)
    return out


def witness_projectors():
    """N_i = x_i e_i^T, x_i = e_i + e_{i+1} + e_{i+2}."""
    projectors = []
    for index in range(4):
        image = (1 << index) | (1 << ((index + 1) % 4)) | (1 << ((index + 2) % 4))
        covector = 1 << index
        projectors.append((image, covector))
    return tuple(projectors)


def heavy_cycle_projectors():
    """M_i = e_i x_i^T, the #6962 four-cycle, covector weight 3."""
    projectors = []
    for index in range(4):
        image = 1 << index
        covector = (1 << index) | (1 << ((index + 1) % 4)) | (1 << ((index + 2) % 4))
        projectors.append((image, covector))
    return tuple(projectors)


def disjoint_lines():
    """The four weight-1 lines of #7138, Section 5. Operators only."""
    projectors = []
    for block in range(4):
        column = 3 * block
        image = (1 << column) | (1 << (column + 1)) | (1 << (column + 2))
        projectors.append((image, 1 << column))
    return tuple(projectors)


def span_data(masks):
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


def pattern_space(projectors, width):
    generators = [pattern_mask(image, covector, width) for image, covector in projectors]
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


def gaussian_count(dimension, rank):
    numerator = 1
    denominator = 1
    for step in range(rank):
        numerator *= (1 << dimension) - (1 << step)
        denominator *= (1 << rank) - (1 << step)
    return numerator // denominator


def subspaces_of(vectors):
    universe = list(dict.fromkeys(vectors))
    seen = {frozenset((0,))}
    queue = [frozenset((0,))]
    while queue:
        current = queue.pop()
        for vector in universe:
            grown = set(current)
            grown.update(old ^ vector for old in current)
            frozen = frozenset(grown)
            if frozen not in seen:
                seen.add(frozen)
                queue.append(frozen)
    return seen


def is_invariant(subspace, projectors):
    for image, covector in projectors:
        for vector in subspace:
            image_vector = image if dot(vector, covector) else 0
            if image_vector not in subspace:
                return False
    return True


def invariant_subspaces(projectors):
    images = [image for image, _ in projectors]
    dimension, pivots = span_data(images)
    vectors = enumerate_span(pivots)
    require(len(vectors) == (1 << dimension), "image span is not a flat of the computed rank")
    subspaces = subspaces_of(vectors)
    expected = sum(gaussian_count(dimension, rank) for rank in range(dimension + 1))
    require(len(subspaces) == expected, "subspace census missed a flat")
    invariant = [subspace for subspace in subspaces if is_invariant(subspace, projectors)]
    return dimension, vectors, invariant


def kernel_of(vectors, covectors):
    return [vector for vector in vectors if all(dot(vector, covector) == 0 for covector in covectors)]


def check_pattern_weights():
    dimension, space = pattern_space(witness_projectors(), 4)
    require(dimension == 4, "witness pattern dimension")
    require(len(space) == 16, "witness pattern count")
    weights = sorted(mask.bit_count() for mask in space)
    require(weights == [0, 2, 2, 2, 2, 4, 4, 4, 4, 4, 4, 6, 6, 6, 6, 8], "witness pattern weights")
    require(all(item == 0 or item >= 2 for item in weights), "witness matrix unit")


def check_pair_obstruction():
    def shaped(index, alpha):
        return (alpha << index) | (1 << ((index + 1) % 4)) | (1 << ((index + 2) % 4))

    for left, right in itertools.combinations(range(4), 2):
        agreements = [
            (alpha, beta)
            for alpha in (0, 1)
            for beta in (0, 1)
            if shaped(left, alpha) == shaped(right, beta)
        ]
        require(agreements == [], "pair " + str(left) + "," + str(right) + " shares an image")
    images = [image for image, _ in witness_projectors()]
    for index in range(4):
        require(shaped(index, 1) == images[index], "singleton lift")
        require(dot(shaped(index, 0), 1 << index) == 0, "alpha zero is not idempotent")


def check_pool_scans():
    expected = sorted(witness_projectors())
    for width in WIDTHS:
        dimension, space = pattern_space(witness_projectors(), width)
        require(dimension == 4, "pattern dimension at width " + str(width))
        found = sorted(complete_pool(width, space))
        require(found == expected, "pool at width " + str(width))
        require(all(weight(covector) == 1 for _, covector in found), "covector weight")
        image_rank, _ = span_data([image for image, _ in found])
        require(image_rank == 4, "image dimension at width " + str(width))


def check_support_closure():
    full = {0, 1, 2, 3}

    def closed(active):
        return all({index, (index + 1) % 4, (index + 2) % 4} <= active for index in active)

    require(closed(full), "the full index set is support-closed")
    require(closed(set()), "the empty index set is vacuously support-closed")
    for mask in range(1, 15):
        active = {index for index in range(4) if (mask >> index) & 1}
        require(not closed(active), "proper support set " + str(sorted(active)) + " closed")


def check_irreducible_lattice():
    projectors = witness_projectors()
    dimension, vectors, invariant = invariant_subspaces(projectors)
    require(dimension == 4, "witness image rank")
    require(len(invariant) == 2, "witness invariant-subspace count")
    orders = sorted(len(subspace) for subspace in invariant)
    require(orders == [1, 16], "witness invariant subspaces are not 0 and V")
    kernel = kernel_of(vectors, [covector for _, covector in projectors])
    require(kernel == [0], "witness common kernel")
    for index, (image, covector) in enumerate(projectors):
        require(dot(image, covector) == 1, "witness idempotent")
        neighbour = projectors[(index + 1) % 4][0]
        require(dot(image, projectors[(index + 1) % 4][1]) == 1, "witness cross term")
        line_rank, _ = span_data([image, neighbour])
        require(line_rank == 2, "witness images are not independent in pairs")
        for vector in vectors:
            once = image if dot(vector, covector) else 0
            twice = image if dot(once, covector) else 0
            require(once == twice, "witness projector is not idempotent on the image")


def check_deleted_projector():
    kept = witness_projectors()[:3]
    line = frozenset((0, 1 << 3))
    require(is_invariant(line, kept), "deleted pool should keep the e3 line")
    require(not is_invariant(line, witness_projectors()), "full pool should move the e3 line")
    _, _, invariant = invariant_subspaces(kept)
    proper = [subspace for subspace in invariant if len(subspace) not in (1, 16)]
    require(proper, "deleted pool should be reducible")


def check_disjoint_lines():
    projectors = disjoint_lines()
    dimension, vectors, invariant = invariant_subspaces(projectors)
    require(dimension == 4, "four-line image rank")
    require(all(weight(covector) == 1 for _, covector in projectors), "four-line covector weight")
    require(kernel_of(vectors, [covector for _, covector in projectors]) == [0], "four-line kernel")
    for image, _ in projectors:
        line = frozenset((0, image))
        require(is_invariant(line, projectors), "four-line span is not invariant")
    proper = [subspace for subspace in invariant if len(subspace) not in (1, len(vectors))]
    require(proper, "four lines should be reducible")


def check_heavy_cycle_control():
    projectors = heavy_cycle_projectors()
    require(all(weight(covector) == 3 for _, covector in projectors), "four-cycle covector weight")
    dimension, _, invariant = invariant_subspaces(projectors)
    require(dimension == 4, "four-cycle image rank")
    require(sorted(len(subspace) for subspace in invariant) == [1, 16], "four-cycle scanner")
    witness = witness_projectors()
    for index in range(4):
        heavy_image, heavy_covector = projectors[index]
        witness_image, witness_covector = witness[index]
        require(heavy_image == witness_covector and heavy_covector == witness_image, "transpose factors")
        heavy_pattern = pattern_mask(heavy_image, heavy_covector, 4)
        witness_pattern = pattern_mask(witness_image, witness_covector, 4)
        require(transpose_mask(heavy_pattern, 4) == witness_pattern, "transpose pattern")


def expect_failure(function, label):
    try:
        function()
    except SystemExit as stopped:
        text = str(stopped)
        require(text.startswith("FAIL:"), label + " did not fail closed")
        return
    fail(label + " did not fail")


def bad_line_claim():
    image = witness_projectors()[0][0]
    require(is_invariant(frozenset((0, image)), witness_projectors()), "witness line is not invariant")


def bad_four_line_claim():
    projectors = disjoint_lines()
    image = projectors[0][0]
    require(not is_invariant(frozenset((0, image)), projectors), "four-line span should not be invariant")


def main():
    check_pattern_weights()
    check_pair_obstruction()
    check_support_closure()
    check_pool_scans()
    check_irreducible_lattice()
    check_deleted_projector()
    check_disjoint_lines()
    check_heavy_cycle_control()
    expect_failure(bad_line_claim, "witness line")
    expect_failure(bad_four_line_claim, "four-line invariance")
    print(MARKER + " pool=4 image_dim=4 kernel_dim=0 new_kappa=null")
    return 0


if __name__ == "__main__":
    sys.exit(main())
