#!/usr/bin/env python3
"""Finite checks for odd-fresh links on two normal-form blocks.

PROOF.md is the all-width argument. This program repeats the explicit
arithmetic, the complete pools, the irreducibility closures, the reducible
controls, and two exhaustive censuses. It raises SystemExit instead of
using assert, so python -O does not skip checks. Standard library only.
"""

import json
from pathlib import Path

MARKER = "PASS_NO_EDGE_DIM5_FRESH_LINK"
SELECTED = Path(__file__).resolve().parents[2] / "certificates" / "selected-result.json"
KAPPA = "363005817/100000000000"
DECIMAL = "0.00363005817"

# Normal-form projectors on A = {0,1,2} and B = {3,4,5}.
# Images omit one leaf or none: e0+e2 omits leaf 1, e1+e2 omits leaf 0.
BLOCK = (
    (0b0000101, 0b0000110),  # (e0+e2)(e1+e2)^T
    (0b0000110, 0b0000101),  # (e1+e2)(e0+e2)^T
    (0b0000111, 0b0000111),  # (e0+e1+e2)(e0+e1+e2)^T
    (0b0101000, 0b0110000),  # (e3+e5)(e4+e5)^T
    (0b0110000, 0b0101000),  # (e4+e5)(e3+e5)^T
    (0b0111000, 0b0111000),  # (e3+e4+e5)(e3+e4+e5)^T
)
HUB_A = 2
HUB_B = 5
LEAVES_A = (0, 1)
LEAVES_B = (3, 4)


def fail(message):
    raise SystemExit("FAIL: " + message)


def require(condition, message):
    if not condition:
        fail(message)


def weight(mask):
    return mask.bit_count()


def dot(left, right):
    return weight(left & right) & 1


def gaussian(vectors):
    pivots = {}
    for vector in vectors:
        current = vector
        while current:
            bit = current & -current
            if bit not in pivots:
                for other_bit, other in list(pivots.items()):
                    if other & bit:
                        pivots[other_bit] = other ^ current
                pivots[bit] = current
                break
            current ^= pivots[bit]
    return pivots


def in_span(pivots, mask):
    current = mask
    while current:
        bit = current & -current
        if bit not in pivots:
            return False
        current ^= pivots[bit]
    return True


def rank(vectors):
    return len(gaussian(vectors))


def pattern_mask(image, covector, width):
    mask = 0
    row = 0
    shift = 0
    remaining = image
    while remaining:
        if remaining & 1:
            mask |= (covector & ~(1 << row)) << shift
        remaining >>= 1
        row += 1
        shift += width
    return mask


def position_bit(row, column, width):
    return 1 << (row * width + column)


def complete_pool(patterns, width):
    """Every rank-one idempotent whose off-diagonal pattern lies in the span."""
    pivots = gaussian(patterns)
    found = []
    for image in range(1, 1 << width):
        pivot = (image & -image).bit_length() - 1
        for choice in range(1 << (width - 1)):
            low = choice & ((1 << pivot) - 1)
            high = choice >> pivot
            covector = low | (high << (pivot + 1))
            if dot(image, covector) == 0:
                covector |= 1 << pivot
            mask = pattern_mask(image, covector, width)
            if mask and in_span(pivots, mask):
                found.append((image, covector))
    return found


def contains_unit(patterns, width):
    pivots = gaussian(patterns)
    for row in range(width):
        for column in range(width):
            if row != column and in_span(pivots, position_bit(row, column, width)):
                return True
    return False


def span_points(vectors):
    points = [0]
    for vector in gaussian(vectors).values():
        points += [old ^ vector for old in points]
    return points


def generated_dimension(seed, pool):
    if seed == 0:
        return 0
    pivots = gaussian([seed])
    while True:
        members = [0]
        for vector in pivots.values():
            members += [old ^ vector for old in members]
        grew = False
        for image, covector in pool:
            if any(dot(covector, vector) for vector in members) and not in_span(pivots, image):
                current = image
                while current:
                    bit = current & -current
                    if bit not in pivots:
                        for other_bit, other in list(pivots.items()):
                            if other & bit:
                                pivots[other_bit] = other ^ current
                        pivots[bit] = current
                        break
                    current ^= pivots[bit]
                grew = True
                break
        if not grew:
            return len(pivots)


def is_invariant(space, pool):
    members = set(space)
    for image, covector in pool:
        if any(dot(covector, vector) for vector in members) and image not in members:
            return False
    return True


def fresh_bits(count):
    return ((1 << count) - 1) << 6


def hub_link(count):
    return (1 << HUB_A) | (1 << HUB_B) | fresh_bits(count)


def support_size(mask):
    return weight(mask)


def check_selected_frontier():
    payload = json.loads(SELECTED.read_text(encoding="utf-8"))
    require(payload.get("kappa") == KAPPA, "selected kappa changed")
    require(payload.get("decimal") == DECIMAL, "selected decimal changed")


def space_vectors(patterns):
    basis = list(gaussian(patterns).values())
    vectors = []
    for choice in range(1 << len(basis)):
        total = 0
        for index, vector in enumerate(basis):
            if (choice >> index) & 1:
                total ^= vector
        vectors.append(total)
    return vectors


def check_family(count, width):
    require(count % 2 == 1 and count >= 1, "fresh count is not a positive odd integer")
    require(width >= 6 + count, "width does not hold the fresh coordinates")
    link = hub_link(count)
    require(weight(link) == 2 + count, "hub link has the wrong weight")
    require(dot(link, link) == 1, "hub link is not idempotent")
    pool_factors = BLOCK + ((link, link),)
    patterns = [pattern_mask(image, covector, width) for image, covector in pool_factors]
    require(rank(patterns) == 5, "fresh-link pattern rank is not 5 at k=%s width=%s" % (count, width))
    block_basis = [patterns[0], patterns[1], patterns[3], patterns[4]]
    require(rank(block_basis) == 4, "the two blocks are not a 4-dimensional pattern space")
    require(not in_span(gaussian(block_basis), patterns[6]), "the link pattern lies in the block span")
    weights = [weight(vector) for vector in space_vectors(patterns)]
    require(weights.count(0) == 1 and min(weight for weight in weights if weight) >= 3,
            "a nonzero fresh-link pattern has weight below 3")
    require(not contains_unit(patterns, width), "fresh-link pattern space contains a matrix unit")
    require(weight(patterns[6]) == (2 + count) * (1 + count),
            "link pattern weight is not |S|(|S|-1)")
    found = complete_pool(patterns, width)
    require(sorted(found) == sorted(pool_factors),
            "complete pool at k=%s width=%s is not the seven projectors" % (count, width))
    images = [image for image, _covector in found]
    require(rank(images) == 7, "fresh-link image rank is not 7")
    require(rank([covector for _image, covector in found]) == 7, "fresh-link covector rank is not 7")
    points = span_points(images)
    require(len(points) == 128, "fresh-link image is not 7-dimensional")
    for seed in points:
        if seed == 0:
            continue
        require(generated_dimension(seed, found) == 7,
                "a fresh-link vector generates a proper subspace at k=%s" % count)
    block_a = span_points([image for image, _covector in BLOCK[:3]])
    require(len(block_a) == 8, "block A is not 3-dimensional")
    require(not is_invariant(block_a, found), "block A stayed invariant after the hub link was added")
    return found


def gram_matrix(pool):
    images = [image for image, _covector in pool]
    covectors = [covector for _image, covector in pool]
    rows = []
    for covector in covectors:
        row = 0
        for index, image in enumerate(images):
            if dot(covector, image):
                row |= 1 << index
        rows.append(row)
    return rows


def check_gram_and_weights():
    small = BLOCK + ((hub_link(1), hub_link(1)),)
    large = BLOCK + ((hub_link(3), hub_link(3)),)
    require(gram_matrix(small) == gram_matrix(large),
            "the image/covector incidence changed with the fresh set")
    expected = [0b1111111] + [1 << index for index in range(6)]
    # Row i bit j means covector i meets image j. The 6x6 block is the
    # identity and the link row and link column are all ones.
    actual = gram_matrix(small)
    require(actual[6] == 0b1111111, "the link covector misses a pool image")
    for index in range(6):
        require(actual[index] == (1 << index) | (1 << 6),
                "a block covector does not meet only its image and the link")
    small_images = sorted(weight(image) for image, _covector in small)
    large_images = sorted(weight(image) for image, _covector in large)
    require(small_images == [2, 2, 2, 2, 3, 3, 3], "k=1 image weights changed")
    require(large_images == [2, 2, 2, 2, 3, 3, 5], "k=3 image weights changed")
    small_patterns = sorted(
        weight(pattern_mask(image, covector, 7)) for image, covector in small)
    large_patterns = sorted(
        weight(pattern_mask(image, covector, 9)) for image, covector in large)
    require(small_patterns == [3, 3, 3, 3, 6, 6, 6], "k=1 pattern weights changed")
    require(large_patterns == [3, 3, 3, 3, 6, 6, 20], "k=3 pattern weights changed")
    require(expected[0] == 0b1111111, "gram control constant drifted")


def avoiding_image(leaf):
    if leaf in LEAVES_A:
        other = LEAVES_A[0] if leaf == LEAVES_A[1] else LEAVES_A[1]
        return (1 << other) | (1 << HUB_A)
    if leaf in LEAVES_B:
        other = LEAVES_B[0] if leaf == LEAVES_B[1] else LEAVES_B[1]
        return (1 << other) | (1 << HUB_B)
    fail("avoiding image asked for a non-leaf")


def check_square_pool(link, width, label):
    require(dot(link, link) == 1, label + " is not idempotent")
    factors = BLOCK + ((link, link),)
    patterns = [pattern_mask(image, covector, width) for image, covector in factors]
    require(rank(patterns) == 5, label + " pattern rank is not 5")
    require(not contains_unit(patterns, width), label + " pattern space contains a unit")
    found = complete_pool(patterns, width)
    require(sorted(found) == sorted(factors), label + " pool is not the seven projectors")
    require(rank([image for image, _covector in found]) == 7, label + " image rank is not 7")
    return found


def check_reducible_controls():
    # Every one-from-A, one-from-B, one-fresh square at width 7.
    for point_a in (0, 1, 2):
        for point_b in (3, 4, 5):
            link = (1 << point_a) | (1 << point_b) | (1 << 6)
            found = check_square_pool(link, 7, "leaf link %s,%s" % (point_a, point_b))
            if point_a == HUB_A and point_b == HUB_B:
                points = span_points([image for image, _covector in found])
                require(all(generated_dimension(seed, found) == 7 for seed in points if seed),
                        "the hub-hub link was reducible")
                continue
            leaf = point_a if point_a != HUB_A else point_b
            line = avoiding_image(leaf)
            require(dot(link, line) == 0, "a leaf link meets the avoiding image")
            require(is_invariant([0, line], found), "the avoiding line is not invariant")
            require(generated_dimension(line, found) == 1, "the avoiding line grew")
    # Hub on one block only, or on neither.
    miss_a = (1 << HUB_B) | (1 << 6) | (1 << 7)
    found = check_square_pool(miss_a, 8, "link missing A")
    block_a = span_points([image for image, _covector in BLOCK[:3]])
    require(is_invariant(block_a, found), "L is not invariant when the link misses A")
    require(generated_dimension(BLOCK[0][0], found) <= 3, "L grew when the link misses A")
    miss_b = (1 << HUB_A) | (1 << 6) | (1 << 7)
    found = check_square_pool(miss_b, 8, "link missing B")
    block_b = span_points([image for image, _covector in BLOCK[3:6]])
    require(is_invariant(block_b, found), "R is not invariant when the link misses B")
    leaf_fresh = (1 << 0) | (1 << 6) | (1 << 7)
    found = check_square_pool(leaf_fresh, 8, "leaf plus two fresh")
    line = avoiding_image(0)
    require(is_invariant([0, line], found), "leaf-plus-fresh avoiding line is not invariant")
    three_fresh = (1 << 6) | (1 << 7) | (1 << 8)
    found = check_square_pool(three_fresh, 9, "three fresh coordinates")
    require(is_invariant(block_a, found), "L is not invariant for a link outside both blocks")
    # Deleting the k=3 link restores the block invariant subspace.
    deleted = list(BLOCK)
    patterns = [pattern_mask(image, covector, 9) for image, covector in deleted]
    found = complete_pool(patterns, 9)
    require(sorted(found) == sorted(deleted), "deleting the k=3 link changed the block pool")
    require(is_invariant(block_a, found), "block A is not invariant after deleting the k=3 link")


def irreducible_image7(patterns, width):
    if rank(patterns) != 5 or contains_unit(patterns, width):
        return None
    pool = complete_pool(patterns, width)
    images = [image for image, _covector in pool]
    if rank(images) != 7:
        return None
    for seed in span_points(images):
        if seed and generated_dimension(seed, pool) != 7:
            return None
    return pool


def check_width7_idempotent_census():
    """Every idempotent at width 7, adjoined to the two fixed blocks."""
    width = 7
    base = [pattern_mask(image, covector, width) for image, covector in BLOCK]
    base_pivots = gaussian(base)
    seen = set()
    hits = []
    visited = 0
    for image in range(1, 1 << width):
        pivot = (image & -image).bit_length() - 1
        for choice in range(1 << (width - 1)):
            visited += 1
            low = choice & ((1 << pivot) - 1)
            high = choice >> pivot
            covector = low | (high << (pivot + 1))
            if dot(image, covector) == 0:
                covector |= 1 << pivot
            mask = pattern_mask(image, covector, width)
            if mask == 0 or mask in seen or in_span(base_pivots, mask):
                continue
            seen.add(mask)
            pool = irreducible_image7(base + [mask], width)
            if pool is not None:
                hits.append(mask)
    require(visited == 127 * 64, "width-7 idempotent count is not (2^7-1)2^6 = 8128")
    witness = pattern_mask(hub_link(1), hub_link(1), width)
    require(hits == [witness], "width-7 irreducible image-7 extensions are not exactly the k=1 link")


def predicted_square_hits(width):
    hits = []
    for fresh in range(6, width):
        hits.append((1 << HUB_A) | (1 << HUB_B) | (1 << fresh))
    fresh_count = width - 6
    if fresh_count >= 3 and fresh_count % 2 == 1:
        hits.append(hub_link(fresh_count))
    return hits


def check_square_census(width):
    base = [pattern_mask(image, covector, width) for image, covector in BLOCK]
    base_pivots = gaussian(base)
    hits = []
    visited = 0
    for link in range(1 << width):
        if weight(link) % 2 == 0:
            continue
        visited += 1
        mask = pattern_mask(link, link, width)
        if mask == 0 or in_span(base_pivots, mask):
            continue
        pool = irreducible_image7(base + [mask], width)
        if pool is not None:
            hits.append(link)
    require(visited == 1 << (width - 1), "odd-vector count at width %s drifted" % width)
    require(sorted(hits) == sorted(predicted_square_hits(width)),
            "square hits at width %s are not the predicted hub links: %s"
            % (width, [format(link, "b") for link in hits]))


def check_unit_detector():
    require(contains_unit([position_bit(0, 1, 4)], 4), "unit detector missed a matrix unit")
    witness = [pattern_mask(image, covector, 7) for image, covector in BLOCK]
    witness.append(pattern_mask(hub_link(1), hub_link(1), 7))
    require(not contains_unit(witness, 7), "unit detector fired on the k=1 witness")


def main():
    check_selected_frontier()
    check_family(1, 7)
    check_family(1, 8)
    check_family(3, 9)
    check_family(3, 10)
    check_family(5, 11)
    check_gram_and_weights()
    check_reducible_controls()
    check_unit_detector()
    check_width7_idempotent_census()
    check_square_census(8)
    check_square_census(9)
    print(MARKER)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
