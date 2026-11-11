#!/usr/bin/env python3
"""Finite checks for one irreducible no-edge pool of pattern dimension 5.

PROOF.md is the all-width argument. This program repeats the explicit
matrix arithmetic, the complete-pool scans, the 127-vector irreducibility
census, and the reducible controls. It raises SystemExit instead of using
assert, so python -O does not skip checks. Standard library only.
"""

import json
from pathlib import Path

MARKER = "PASS_NO_EDGE_DIM5_IRREDUCIBLE_SEVEN"
SELECTED = Path(__file__).resolve().parents[2] / "certificates" / "selected-result.json"
KAPPA = "363005817/100000000000"
DECIMAL = "0.00363005817"

# Two normal-form triples and the linking projector z z^T, z = e2+e5+e6.
WITNESS = (
    (0b0000101, 0b0000110),  # (e0+e2)(e1+e2)^T
    (0b0000110, 0b0000101),  # (e1+e2)(e0+e2)^T
    (0b0000111, 0b0000111),  # (e0+e1+e2)(e0+e1+e2)^T
    (0b0101000, 0b0110000),  # (e3+e5)(e4+e5)^T
    (0b0110000, 0b0101000),  # (e4+e5)(e3+e5)^T
    (0b0111000, 0b0111000),  # (e3+e4+e5)(e3+e4+e5)^T
    (0b1100100, 0b1100100),  # (e2+e5+e6)(e2+e5+e6)^T
)
STAR_POSITIONS = ((2, 5), (2, 6), (5, 2), (5, 6), (6, 2), (6, 5))
BLOCK_A = WITNESS[:3]
BLOCK_B = WITNESS[3:6]


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
    remaining = image
    while remaining:
        if remaining & 1:
            column = 0
            columns = covector
            while columns:
                if columns & 1 and column != row:
                    mask |= 1 << (row * width + column)
                columns >>= 1
                column += 1
        remaining >>= 1
        row += 1
    return mask


def position_bit(row, column, width):
    return 1 << (row * width + column)


def complete_pool(patterns, width):
    pivots = gaussian(patterns)
    found = []
    for image in range(1, 1 << width):
        pivot = (image & -image).bit_length() - 1
        free = [index for index in range(width) if index != pivot]
        for choice in range(1 << (width - 1)):
            covector = 0
            for bit, index in enumerate(free):
                if (choice >> bit) & 1:
                    covector |= 1 << index
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


def space_weights(patterns):
    basis = list(gaussian(patterns).values())
    weights = []
    for choice in range(1 << len(basis)):
        total = 0
        for index, vector in enumerate(basis):
            if (choice >> index) & 1:
                total ^= vector
        weights.append(weight(total))
    return weights


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


def check_selected_frontier():
    payload = json.loads(SELECTED.read_text(encoding="utf-8"))
    require(payload.get("kappa") == KAPPA, "selected kappa changed")
    require(payload.get("decimal") == DECIMAL, "selected decimal changed")


def check_witness_arithmetic(width):
    patterns = [pattern_mask(image, covector, width) for image, covector in WITNESS]
    require(len(set(patterns)) == 7, "the seven patterns are not distinct")
    for image, covector in WITNESS:
        require(dot(image, covector) == 1, "a witness factor is not idempotent")
    require(rank(patterns) == 5, "witness pattern rank is not 5")
    weights = space_weights(patterns)
    require(weights[0] == 0 and min(weights[1:]) >= 3,
            "a nonzero witness pattern has weight below 3")
    require(not contains_unit(patterns, width), "witness pattern space contains a matrix unit")
    star = patterns[6]
    block_basis = [patterns[0], patterns[1], patterns[3], patterns[4]]
    block_span = gaussian(block_basis)
    require(rank(block_basis) == 4, "the four block patterns do not span the even space")
    require(not in_span(block_span, star), "the linking pattern lies in the block span")
    for row, column in STAR_POSITIONS:
        require((star >> (row * width + column)) & 1, "linking pattern misses a forced entry")
        require(all(((other >> (row * width + column)) & 1) == 0 for other in patterns[:6]),
                "a block pattern meets a linking position")
    # Every odd pattern carries all six linking entries; no even pattern carries any.
    basis = block_basis + [star]
    require(rank(basis) == 5, "explicit basis is not the full pattern space")
    for choice in range(32):
        total = 0
        for index, vector in enumerate(basis):
            if (choice >> index) & 1:
                total ^= vector
        odd = (choice & 16) != 0
        for row, column in STAR_POSITIONS:
            bit = (total >> (row * width + column)) & 1
            require(bit == (1 if odd else 0), "linking entries are not constant on a coset")
    images = [image for image, _covector in WITNESS]
    require(rank(images) == 7, "witness images do not span dimension 7")
    require(set(range(128)) == set(span_points(images)), "witness image is not the coordinate 7-space")
    linking = WITNESS[6][0]
    for image, covector in WITNESS[:6]:
        require(dot(linking, image) == 1, "a block image misses the linking covector")
        require(dot(covector, linking) == 1, "a block covector misses the linking image")
    require(dot(linking, linking) == 1, "the linking projector is not idempotent on itself")
    return patterns


def span_points(vectors):
    points = [0]
    for vector in gaussian(vectors).values():
        points += [old ^ vector for old in points]
    return points


def check_dual_bases():
    # Rows are the block covectors on coordinates (0,1,2) and (3,4,5).
    left = (
        (0, 1, 1),
        (1, 0, 1),
        (1, 1, 1),
    )
    right = (
        (0, 1, 1),
        (1, 0, 1),
        (1, 1, 1),
    )
    require(matrix_rank(left) == 3, "block A covectors do not span the dual")
    require(matrix_rank(right) == 3, "block B covectors do not span the dual")
    left_images = (0b101, 0b110, 0b111)
    right_images = (0b0101000, 0b0110000, 0b0111000)
    require(rank(left_images) == 3, "block A images do not span the block")
    require(rank(right_images) == 3, "block B images do not span the block")


def matrix_rank(rows):
    masks = []
    for row in rows:
        mask = 0
        for index, bit in enumerate(row):
            if bit:
                mask |= 1 << index
        masks.append(mask)
    return rank(masks)


def check_complete_pool(width):
    patterns = check_witness_arithmetic(width)
    pool = complete_pool(patterns, width)
    require(sorted(pool) == sorted(WITNESS),
            "complete pool at width %s is not the seven projectors" % width)
    require(rank([image for image, _covector in pool]) == 7, "image rank changed")
    require(rank([covector for _image, covector in pool]) == 7, "covector rank changed")


def check_irreducibility():
    pool = list(WITNESS)
    points = span_points([image for image, _covector in pool])
    require(len(points) == 128, "irreducibility census domain is not the 128-point image")
    proper = 0
    for seed in points:
        if seed == 0:
            continue
        dimension = generated_dimension(seed, pool)
        if dimension != 7:
            proper += 1
    require(proper == 0, "a nonzero vector generates a proper invariant subspace")


def check_deleted_projector():
    pool = list(WITNESS[:-1])
    patterns = [pattern_mask(image, covector, 7) for image, covector in pool]
    found = complete_pool(patterns, 7)
    require(sorted(found) == sorted(pool), "deleting the link changed the remaining pool")
    require(rank([image for image, _covector in pool]) == 6, "deleted pool is not 6-dimensional")
    block = span_points([image for image, _covector in BLOCK_A])
    require(len(block) == 8, "block A is not 3-dimensional")
    require(is_invariant(block, pool), "block A is not invariant after deleting the link")
    require(generated_dimension(BLOCK_A[0][0], pool) <= 3,
            "a block vector escaped its block after the link was deleted")


def even_column_patterns(width):
    patterns = []
    for mask in range(64):
        if weight(mask) % 2 or mask == 0:
            continue
        image = 1 | (mask << 1)  # e0 plus an even vector on coordinates 1..6
        patterns.append(pattern_mask(image, 1, width))
    return patterns


def check_parity_control(width):
    patterns = even_column_patterns(width)
    require(rank(patterns) == 5, "parity pattern rank is not 5")
    require(min(space_weights(patterns)[1:]) >= 2, "parity space contains a unit or zero")
    require(not contains_unit(patterns, width), "parity space contains a matrix unit")
    pool = complete_pool(patterns, width)
    require(len(pool) == 31, "parity pool does not have the 31 even patterns")
    require(all(covector == 1 for _image, covector in pool), "parity covector is not e0")
    images = [image for image, _covector in pool]
    require(rank(images) == 6, "parity image rank is not 6")
    # Every covector is e0, so the even-weight vector e1+e2 is killed and its
    # cyclic subspace is a line. An image vector is not a valid control: e0
    # hits every image, and closing under those hits spans the whole image.
    kernel_line = 0b110
    require(in_span(gaussian(images), kernel_line), "parity kernel vector is outside the image")
    require(all(dot(covector, kernel_line) == 0 for _image, covector in pool),
            "parity kernel vector is not killed")
    require(generated_dimension(kernel_line, pool) == 1,
            "parity control failed to find a proper invariant subspace")


def check_unit_detector():
    require(contains_unit([position_bit(0, 1, 4)], 4), "unit detector missed a matrix unit")
    require(not contains_unit(
        [pattern_mask(image, covector, 7) for image, covector in WITNESS], 7),
        "unit detector fired on the witness")


def main():
    check_selected_frontier()
    check_dual_bases()
    for width in (7, 8, 9):
        check_complete_pool(width)
    check_irreducibility()
    check_deleted_projector()
    for width in (7, 8):
        check_parity_control(width)
    check_unit_detector()
    print(MARKER)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
