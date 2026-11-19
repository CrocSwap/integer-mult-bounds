#!/usr/bin/env python3
"""Check the complete width-four witness and its trace invariant over F2."""

from itertools import combinations, product

WIDTH = 4
CARDINALITY = 1 << WIDTH
# The low-to-high bits represent a, b, f, g.
PROJECTORS = ((1, 3), (3, 2), (5, 9), (11, 6))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def pairing(image, covector):
    return (image & covector).bit_count() % 2


def off_pattern(image, covector):
    pattern = 0
    for row in range(WIDTH):
        if image & (1 << row):
            entries = covector & ~(1 << row)
            pattern |= entries << (WIDTH * row)
    return pattern


def span(generators):
    vectors = {0}
    for generator in generators:
        vectors |= {vector ^ generator for vector in vectors}
    return vectors


def reaches_all_images(start, images):
    reached = {start}
    for _ in range(len(PROJECTORS)):
        reached |= {
            image for image, covector in PROJECTORS
            if any(pairing(vector, covector) for vector in reached)
        }
    return images <= reached


def main():
    patterns = span(tuple(off_pattern(*projector) for projector in PROJECTORS))
    require(len(patterns) == 8, "expected pattern dimension three")
    units = {pattern for pattern in patterns if pattern.bit_count() == 1}
    require(units == {1 << 1}, "expected the single unit E_ab")

    factors = range(1, CARDINALITY)
    idempotents = tuple((x, y) for x, y in product(factors, repeat=2) if pairing(x, y))
    pool = {pair for pair in idempotents if off_pattern(*pair) in patterns - {0}}
    require(len(idempotents) == 120, "incorrect width-four idempotent inventory")
    require(pool == set(PROJECTORS), "complete pool differs from the four displayed lifts")

    images = {image for image, _ in pool}
    require(len(span(images)) == CARDINALITY, "joint image is not the full width-four space")
    for vector in factors:
        require(reaches_all_images(vector, images), f"nonspanning orbit at {vector}")

    reciprocal = {
        (i, j) for i, j in combinations(range(len(PROJECTORS)), 2)
        if pairing(PROJECTORS[i][0], PROJECTORS[j][1])
        and pairing(PROJECTORS[j][0], PROJECTORS[i][1])
    }
    require(reciprocal == {(0, 2), (1, 3)}, "unexpected trace-one pairs")
    print("PASS_EVEN_ONE_EDGE_MAXIMIZER")
    print(f"{len(idempotents)} idempotents scanned, {len(patterns) - 1} nonzero patterns, "
          f"{len(pool)} lifts, {len(factors)} spanning orbits, {len(reciprocal)} trace-one pairs")


if __name__ == "__main__":
    main()
