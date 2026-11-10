#!/usr/bin/env python3
"""Finite checks for the weight-1 pattern-dimension-4 image bound.

PROOF.md is the all-width argument. This program enumerates the width-8
witness, the one-column dimension-5 example, the four-line kernel example,
and the partition table. It also runs negative controls. It does not use
assert, so python -O does not skip checks. Standard library only.
"""

import sys

MARKER = "PASS_WEIGHT1_PATTERN_DIM4_REDUCIBLE"


def fail(message):
    raise SystemExit("FAIL: " + message)


def require(condition, message):
    if not condition:
        fail(message)


def weight(mask):
    return mask.bit_count()


def dot(left, right):
    return weight(left & right) & 1


def rank(vectors):
    pivots = {}
    for value in vectors:
        while value:
            lead = value.bit_length() - 1
            if lead in pivots:
                value ^= pivots[lead]
            else:
                pivots[lead] = value
                break
    return len(pivots)


def span(vectors):
    found = [0]
    for value in vectors:
        found += [item ^ value for item in found]
    return found


def pattern_rows(image, covector, width):
    rows = []
    for row in range(width):
        if (image >> row) & 1:
            rows.append(covector & ~(1 << row))
        else:
            rows.append(0)
    return tuple(rows)


def pack(rows):
    packed = 0
    for index, row in enumerate(rows):
        packed |= row << (16 * index)
    return packed


def pattern_weight(rows):
    return sum(weight(row) for row in rows)


def subspace(basis):
    found = [0]
    for value in basis:
        found += [item ^ value for item in found]
    return found


def f_dim(column_dimension):
    if column_dimension <= 0:
        return 0
    if column_dimension == 1:
        return 1
    return 1 + column_dimension


def compositions(total):
    if total == 0:
        yield ()
        return
    for first in range(1, total + 1):
        for rest in compositions(total - first):
            yield (first,) + rest


def partition_maximum(limit):
    best = 0
    winners = []
    for total in range(0, limit + 1):
        for parts in compositions(total):
            score = sum(f_dim(part) for part in parts)
            if score > best:
                best = score
                winners = [parts]
            elif score == best:
                winners.append(parts)
    return best, winners


def lifts(column_space, column, width):
    found = []
    for vector in column_space:
        if vector == 0:
            continue
        require((vector >> column) & 1 == 0, "column vector meets the diagonal")
        image = (1 << column) ^ vector
        covector = 1 << column
        require(dot(image, covector) == 1, "lift is not idempotent")
        found.append((image, covector))
    return found


def kernel_inside(space, covectors):
    return [vector for vector in space if all(dot(covector, vector) == 0 for covector in covectors)]


def check_reducible_kernel(space, pool):
    covectors = [covector for _, covector in pool]
    images = [image for image, _ in pool]
    live = kernel_inside(space, covectors)
    require(len(live) > 1, "kernel is zero")
    require(len(live) < len(space), "kernel is the whole image")
    for image, covector in pool:
        for vector in live:
            require(dot(covector, vector) == 0, "kernel vector is not killed")
            require(dot(covector, vector) * image == 0, "projector moves the kernel")
    require(any(dot(covector, image) == 1 for image, covector in pool), "no pool vector exits the kernel")
    return rank(live)


def census(pattern_set, width):
    found = []
    for image in range(1, 1 << width):
        for covector in range(1, 1 << width):
            if dot(image, covector) != 1:
                continue
            rows = pattern_rows(image, covector, width)
            if pack(rows) in pattern_set and pattern_weight(rows) != 0:
                found.append((image, covector))
    return found


def column_pattern_space(column_spaces, width):
    basis = []
    for column, vectors in column_spaces:
        for vector in vectors:
            if vector == 0:
                continue
            image = (1 << column) ^ vector
            basis.append(pack(pattern_rows(image, 1 << column, width)))
    patterns = set(span(basis))
    return basis, patterns


def two_column_witness():
    width = 8
    left = subspace([(1 << 1) ^ (1 << 2), (1 << 1) ^ (1 << 3)])
    right = subspace([(1 << 5) ^ (1 << 6), (1 << 5) ^ (1 << 7)])
    require(all(weight(vector) != 1 for vector in left + right if vector), "witness has a matrix unit")
    basis, patterns = column_pattern_space([(0, left), (4, right)], width)
    require(rank(basis) == 4, "witness pattern rank")
    require(len(patterns) == 16, "witness pattern count")
    require(all(weight(pack_value) != 1 for pack_value in patterns if pack_value), "packed matrix unit")
    pool = census(patterns, width)
    expected = lifts(left, 0, width) + lifts(right, 4, width)
    require(sorted(pool) == sorted(expected), "witness pool is not the six lifts")
    require(all(weight(covector) == 1 for _, covector in pool), "witness covector weight")
    require(rank([image for image, _ in pool]) == 6, "witness image rank")
    space = span([image for image, _ in pool])
    require(len(space) == 64, "witness image order")
    kernel_rank = check_reducible_kernel(space, pool)
    require(kernel_rank == 4, "witness kernel rank")
    return len(pool), kernel_rank


def one_column_dimension_five():
    width = 6
    basis = [(1 << 1) ^ (1 << (2 + index)) for index in range(4)]
    column = subspace(basis)
    require(rank(column) == 4, "even-weight column rank")
    require(all(weight(vector) % 2 == 0 and weight(vector) != 1 for vector in column if vector), "even-weight column")
    _, patterns = column_pattern_space([(0, column)], width)
    require(rank([pack(pattern_rows((1 << 0) ^ vector, 1, width)) for vector in basis]) == 4, "one-column pattern rank")
    pool = census(patterns, width)
    require(len(pool) == 15, "one-column pool size")
    require(all(weight(covector) == 1 for _, covector in pool), "one-column covector weight")
    space = span([image for image, _ in pool])
    require(rank([image for image, _ in pool]) == 5, "one-column image rank")
    require(check_reducible_kernel(space, pool) == 4, "one-column kernel rank")


def four_line_kernel_vanishes():
    width = 12
    pool = []
    patterns = []
    for block in range(4):
        column = 3 * block
        vector = (1 << (column + 1)) ^ (1 << (column + 2))
        image = (1 << column) ^ vector
        covector = 1 << column
        pool.append((image, covector))
        patterns.append(pack(pattern_rows(image, covector, width)))
    require(rank(patterns) == 4, "four-line pattern rank")
    require(all(weight(covector) == 1 for _, covector in pool), "four-line covector weight")
    require(rank([image for image, _ in pool]) == 4, "four-line image rank")
    space = span([image for image, _ in pool])
    live = kernel_inside(space, [covector for _, covector in pool])
    require(live == [0], "four-line kernel should vanish")
    for image, covector in pool:
        require(dot(covector, image) == 1, "four-line line is not fixed")
        for other, other_covector in pool:
            if other != image:
                require(dot(other_covector, image) == 0, "four-line cross term")


def four_cycle_is_outside():
    width = 4
    pool = []
    for index in range(4):
        covector = (1 << index) ^ (1 << ((index + 1) % 4)) ^ (1 << ((index + 2) % 4))
        image = 1 << index
        require(dot(image, covector) == 1, "four-cycle idempotent")
        pool.append((image, covector))
    require(any(weight(covector) != 1 for _, covector in pool), "four-cycle should leave the hypothesis")
    require(all(weight(covector) == 3 for _, covector in pool), "four-cycle covector weight")


def matrix_unit_is_outside():
    rows = tuple(1 << 1 if row == 0 else 0 for row in range(4))
    require(pattern_weight(rows) == 1, "control pattern should be a matrix unit")


def expect_failure(function, label):
    try:
        function()
    except SystemExit as stopped:
        text = str(stopped)
        require(text.startswith("FAIL:"), label + " did not fail closed")
        return
    fail(label + " did not fail")


def bad_rank_claim():
    require(rank([0b111, 0b1011]) == 6, "truncated witness is not rank 6")


def bad_kernel_claim():
    space = span([0b111])
    pool = [(0b111, 0b1)]
    # The single image is the whole space and is not in the kernel, so this
    # call must succeed. Feeding the image as a fake extra covector of zero
    # weight is not the control. Drop the exiting vector by using an empty
    # pool, which makes the kernel the whole space.
    check_reducible_kernel(space, [])


def main():
    best, winners = partition_maximum(4)
    require(best == 6, "partition maximum")
    require(set(winners) == {(2, 2)}, "only the pair of twos attains 6")
    pool_size, kernel_rank = two_column_witness()
    one_column_dimension_five()
    four_line_kernel_vanishes()
    four_cycle_is_outside()
    matrix_unit_is_outside()
    expect_failure(bad_rank_claim, "truncated rank")
    expect_failure(bad_kernel_claim, "empty pool kernel")
    print(
        MARKER
        + " pool="
        + str(pool_size)
        + " image_dim=6 kernel_dim="
        + str(kernel_rank)
        + " partition_max=6 new_kappa=null"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
