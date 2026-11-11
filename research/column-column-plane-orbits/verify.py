#!/usr/bin/env python3
"""Exhaustive census of weight-(2,2,2) column-column pairs, and the
infinite-family checks for minimum weight at least 2.

PROOF.md is the case split and the infinitude argument. This program
enumerates every ordered pair of columns and every pair of 3-sets on
widths 5 through 9, keeps the pairs whose image spaces meet only at 0
and whose support uses every coordinate, and checks the surviving
invariants and labeled counts against the case split. It also checks the
five representatives, two excluded overlaps, the doubling family, and
pool W. It raises SystemExit instead of using assert, so python -O does
not skip checks. Standard library only.
"""

import json
from itertools import combinations, permutations
from pathlib import Path

MARKER = "PASS_COLUMN_COLUMN_PLANE_ORBITS"
SELECTED = Path(__file__).resolve().parents[2] / "certificates" / "selected-result.json"

# support size, cross count, overlap size
EXPECTED_INVARIANTS = {(6, 2, 0), (6, 1, 1), (7, 1, 0), (7, 0, 1), (8, 0, 0)}
EXPECTED_LABELS = {5: 0, 6: 900, 7: 2100, 8: 1120, 9: 0}

REPRESENTATIVES = (
    (6, 0, 1, (1, 2, 3), (0, 4, 5), (6, 2, 0)),
    (6, 0, 1, (1, 2, 3), (2, 4, 5), (6, 1, 1)),
    (7, 0, 1, (1, 2, 3), (4, 5, 6), (7, 1, 0)),
    (7, 0, 1, (2, 3, 4), (2, 5, 6), (7, 0, 1)),
    (8, 0, 1, (2, 3, 4), (5, 6, 7), (8, 0, 0)),
)


def fail(message):
    raise SystemExit("FAIL: " + message)


def require(condition, message):
    if not condition:
        fail(message)


def mask_of(coordinates):
    value = 0
    for coordinate in coordinates:
        value |= 1 << coordinate
    return value


def even_vectors(support):
    first, second, third = support
    return (
        (1 << first) | (1 << second),
        (1 << first) | (1 << third),
        (1 << second) | (1 << third),
    )


def subspace(generators):
    space = {0}
    for generator in generators:
        space |= {vector ^ generator for vector in space}
    return space


def image_space(column, vectors):
    return subspace((1 << column, vectors[0], vectors[1]))


def support_size(column_c, column_d, vectors_t, vectors_s):
    used = (1 << column_c) | (1 << column_d)
    for vector in vectors_t + vectors_s:
        used |= vector
    return used.bit_count()


def invariant(column_c, column_d, support_a, support_b):
    left = set(support_a)
    right = set(support_b)
    crosses = int(column_d in left) + int(column_c in right)
    return (len(left | right | {column_c, column_d}), crosses, len(left & right))


def admits(column_c, column_d, support_a, support_b, width):
    if column_c == column_d or column_c in support_a or column_d in support_b:
        return False
    vectors_t = even_vectors(support_a)
    vectors_s = even_vectors(support_b)
    image_t = image_space(column_c, vectors_t)
    image_s = image_space(column_d, vectors_s)
    if len(image_t) != 8 or len(image_s) != 8:
        return False
    if len(image_t & image_s) != 1:
        return False
    return support_size(column_c, column_d, vectors_t, vectors_s) == width


def census(width):
    found = []
    coordinates = range(width)
    for column_c, column_d in permutations(coordinates, 2):
        room_c = [coordinate for coordinate in coordinates if coordinate != column_c]
        room_d = [coordinate for coordinate in coordinates if coordinate != column_d]
        for support_a in combinations(room_c, 3):
            for support_b in combinations(room_d, 3):
                if admits(column_c, column_d, support_a, support_b, width):
                    found.append((column_c, column_d, support_a, support_b))
    return found


def weights_of_plane(alpha, beta, gamma):
    """Nonzero weights of the plane with class sizes alpha, beta, gamma."""
    return tuple(sorted((alpha + gamma, beta + gamma, alpha + beta)))


def realized_weights(alpha, beta, gamma):
    """Build the plane on fresh coordinates and read its three weights."""
    # Class A coordinates lie in v1 and v1+v2, class B in v2 and v1+v2,
    # class C in v1 and v2. Column 0 is unused by the plane.
    cursor = 1
    class_a = list(range(cursor, cursor + alpha))
    cursor += alpha
    class_b = list(range(cursor, cursor + beta))
    cursor += beta
    class_c = list(range(cursor, cursor + gamma))
    vector_a = mask_of(class_a + class_c)
    vector_b = mask_of(class_b + class_c)
    return tuple(sorted(
        vector.bit_count()
        for vector in (vector_a, vector_b, vector_a ^ vector_b)
    ))


def doubling_family(copies):
    """Printed pair with 2*copies coordinates duplicating coordinate 2."""
    extra = [8 + index for index in range(2 * copies)]
    vector_a = mask_of([2, 3] + extra)
    vector_b = mask_of([2, 4] + extra)
    vectors_t = (vector_a, vector_b, vector_a ^ vector_b)
    vectors_s = even_vectors((5, 6, 7))
    return vectors_t, vectors_s


def check_selected_frontier():
    payload = json.loads(SELECTED.read_text(encoding="utf-8"))
    require(payload.get("kappa") == "363005817/100000000000", "selected kappa changed")
    require(payload.get("decimal") == "0.00363005817", "selected decimal changed")


def check_single_planes():
    for alpha in range(0, 7):
        for beta in range(alpha, 7):
            for gamma in range(beta, 7):
                expected = weights_of_plane(alpha, beta, gamma)
                require(
                    realized_weights(alpha, beta, gamma) == expected,
                    f"class sizes {(alpha, beta, gamma)} gave the wrong weights",
                )
                minimum = expected[0]
                require(
                    (minimum >= 2) == (alpha + beta >= 2),
                    f"minimum-weight gate mismatch at {(alpha, beta, gamma)}",
                )
    require(realized_weights(1, 1, 1) == (2, 2, 2), "the (1,1,1) plane is not weight (2,2,2)")
    require(realized_weights(0, 2, 2) == (2, 2, 4), "the (0,2,2) plane is not weight (2,2,4)")
    require(realized_weights(0, 1, 1)[0] == 1, "the (0,1,1) plane should have a weight-1 vector")


def check_representatives():
    seen = set()
    for width, column_c, column_d, support_a, support_b, expected in REPRESENTATIVES:
        require(
            admits(column_c, column_d, support_a, support_b, width),
            f"representative {expected} failed the image test",
        )
        found = invariant(column_c, column_d, support_a, support_b)
        require(found == expected, f"representative invariant {found} != {expected}")
        seen.add(found)
    require(seen == EXPECTED_INVARIANTS, "the five representatives missed an invariant")


def check_excluded_overlaps():
    # No cross, two shared coordinates: the codes share a weight-2 vector.
    shared = (0, 1, (2, 3, 4), (2, 3, 5))
    # One cross, and both private feet of A contained in B.
    covered = (0, 1, (1, 2, 3), (2, 3, 4))
    for column_c, column_d, support_a, support_b in (shared, covered):
        vectors_t = even_vectors(support_a)
        vectors_s = even_vectors(support_b)
        image_t = image_space(column_c, vectors_t)
        image_s = image_space(column_d, vectors_s)
        require(len(image_t & image_s) > 1, "an excluded overlap had trivial intersection")


def check_census():
    for width, expected_count in EXPECTED_LABELS.items():
        rows = census(width)
        require(len(rows) == expected_count, f"width {width} labeled count {len(rows)} != {expected_count}")
        invariants = {
            invariant(column_c, column_d, support_a, support_b)
            for column_c, column_d, support_a, support_b in rows
        }
        if expected_count == 0:
            require(invariants == set(), f"width {width} should be empty")
        else:
            require(
                invariants <= EXPECTED_INVARIANTS,
                f"width {width} produced an invariant outside the five rows",
            )
    # Every one of the five rows occurs, and the positive widths cover them.
    covered = set()
    for width in (6, 7, 8):
        for column_c, column_d, support_a, support_b in census(width):
            covered.add(invariant(column_c, column_d, support_a, support_b))
    require(covered == EXPECTED_INVARIANTS, "the census missed one of the five orbits")


def check_doubling_family():
    previous = None
    for copies in range(0, 5):
        vectors_t, vectors_s = doubling_family(copies)
        require(len(subspace(vectors_t)) == 4, f"doubling k={copies} collapsed T")
        require(len(subspace(vectors_s)) == 4, f"doubling k={copies} collapsed S")
        weights = tuple(sorted(vector.bit_count() for vector in vectors_t))
        require(weights[0] >= 2, f"doubling k={copies} dropped below weight 2")
        require(weights == (2, 2 + 2 * copies, 2 + 2 * copies), f"doubling weights {weights}")
        image_t = image_space(0, vectors_t)
        image_s = image_space(1, vectors_s)
        require(len(image_t) == 8 and len(image_s) == 8, f"doubling k={copies} image rank")
        require(len(image_t & image_s) == 1, f"doubling k={copies} intersection")
        size = support_size(0, 1, vectors_t, vectors_s)
        require(size == 8 + 2 * copies, f"doubling support {size}")
        require(size != previous, "doubling failed to change the support size")
        previous = size


def check_pool_w():
    vectors_t = (
        mask_of((1, 2)),
        mask_of((3, 4)),
        mask_of((1, 2, 3, 4)),
    )
    vectors_s = even_vectors((6, 7, 8))
    weights_t = tuple(sorted(vector.bit_count() for vector in vectors_t))
    weights_s = tuple(sorted(vector.bit_count() for vector in vectors_s))
    require(weights_t == (2, 2, 4), "pool W lost the weight-4 vector")
    require(weights_s == (2, 2, 2), "pool W second plane is not weight (2,2,2)")
    image_t = image_space(0, vectors_t)
    image_s = image_space(5, vectors_s)
    require(len(image_t) == 8 and len(image_s) == 8, "pool W image rank")
    require(len(image_t & image_s) == 1, "pool W intersection")
    require(support_size(0, 5, vectors_t, vectors_s) == 9, "pool W support")
    # Deleting the two coordinates of the weight-2 vector e1+e2 kills it.
    reduced = tuple(vector & ~mask_of((1, 2)) for vector in vectors_t)
    require(0 in reduced, "pool W should collapse when its repeated type is deleted")


def main():
    check_selected_frontier()
    check_single_planes()
    check_representatives()
    check_excluded_overlaps()
    check_census()
    check_doubling_family()
    check_pool_w()
    print(MARKER)


if __name__ == "__main__":
    main()
