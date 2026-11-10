#!/usr/bin/env python3
"""Exact checks for one irreducible no-edge pool of pattern dimension 4.

PROOF.md is the all-width argument. This program repeats the finite parts:
the fifteen-pattern weight and realizability census, the hit-digraph edges,
the width-5 through width-7 pool scan, and the subspace lattice of the
five-dimensional joint image. It also runs negative controls. It does not
use assert, so python -O does not skip checks. Standard library only.
"""

import itertools
import json
from pathlib import Path

MARKER = "PASS_NO_EDGE_DIM4_IMAGE_FIVE"
WIDTHS = (5, 6, 7)
# Order: v, u, o, a, b. The first two and their sum are the normal-form triple.
POOL = (
    (0b00101, 0b00110),  # v: (e0+e2)(e1+e2)^T
    (0b00110, 0b00101),  # u: (e1+e2)(e0+e2)^T
    (0b00111, 0b00111),  # o: (e0+e1+e2)(e0+e1+e2)^T
    (0b01100, 0b01011),  # a: (e2+e3)(e0+e1+e3)^T
    (0b11101, 0b10010),  # b: (e0+e2+e3+e4)(e1+e4)^T
)
# Nonempty sums of the basis (v, u, a, b), written as coefficient tuples,
# that PROOF.md records as unrealizable, with one disagreeing covector bit.
# (coefficients, row_p, row_q, bit, value_on_row_p, value_on_row_q).
CONFLICTS = (
    ((1, 0, 1, 0), 0, 2, 1, 1, 0),
    ((0, 1, 1, 0), 1, 2, 0, 1, 0),
    ((1, 1, 1, 0), 1, 2, 0, 1, 0),
    ((1, 0, 0, 1), 2, 3, 1, 0, 1),
    ((0, 1, 0, 1), 0, 1, 2, 0, 1),
    ((1, 1, 0, 1), 0, 1, 4, 1, 0),
    ((0, 0, 1, 1), 0, 2, 1, 1, 0),
    ((1, 0, 1, 1), 0, 2, 1, 0, 1),
    ((0, 1, 1, 1), 0, 1, 2, 0, 1),
    ((1, 1, 1, 1), 0, 1, 4, 1, 0),
)
CYCLE_EDGES = (
    ("a", "v"),
    ("v", "b"),
    ("b", "o"),
    ("o", "a"),
    ("a", "u"),
    ("u", "a"),
)
LABELS = ("v", "u", "o", "a", "b")


def fail(message):
    raise SystemExit("FAIL: " + message)


def require(condition, message):
    if not condition:
        fail(message)


def dot(left, right):
    return (left & right).bit_count() & 1


def pattern_mask(image, covector, width):
    mask = 0
    for row in range(width):
        if ((image >> row) & 1) == 0:
            continue
        for col in range(width):
            if row != col and ((covector >> col) & 1):
                mask |= 1 << (row * width + col)
    return mask


def row_vector(mask, row, width):
    bits = 0
    for col in range(width):
        if (mask >> (row * width + col)) & 1:
            bits |= 1 << col
    return bits


def gaussian(masks):
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
    return pivots


def in_span(pivots, mask):
    value = mask
    while value:
        bit = value & -value
        known = pivots.get(bit)
        if known is None:
            return False
        value ^= known
    return True


def span_vectors(pivots):
    vectors = [0]
    for vector in pivots.values():
        vectors += [old ^ vector for old in vectors]
    return vectors


def gaussian_count(dimension):
    total = 0
    for rank in range(dimension + 1):
        numerator = 1
        denominator = 1
        for step in range(rank):
            numerator *= (1 << dimension) - (1 << step)
            denominator *= (1 << rank) - (1 << step)
        total += numerator // denominator
    return total


def basis_patterns(width):
    """Return p_v, p_u, p_a, p_b at the given width."""
    images = (POOL[0], POOL[1], POOL[3], POOL[4])
    return tuple(pattern_mask(image, covector, width) for image, covector in images)


def combination(coefficients, width):
    mask = 0
    for bit, pattern in zip(coefficients, basis_patterns(width)):
        if bit:
            mask ^= pattern
    return mask


def implied_bit(mask, row, bit, width):
    require(bit != row, "a row does not determine its own diagonal bit")
    return (row_vector(mask, row, width) >> bit) & 1


def single_column(mask, width):
    columns = set()
    for row in range(width):
        for col in range(width):
            if (mask >> (row * width + col)) & 1:
                columns.add(col)
    return len(columns) <= 1


def realize(mask, width):
    """Return idempotent lifts whose off-diagonal pattern is mask.

    For a pattern that is not supported in a single column, the image support
    is exactly the set of nonzero rows, so the scan below is exhaustive.
    """
    supports = []
    for row in range(width):
        if row_vector(mask, row, width):
            supports.append(row)
    if not supports:
        return []
    image = 0
    for row in supports:
        image |= 1 << row
    forced = {}
    for row in supports:
        bits = row_vector(mask, row, width)
        if (bits >> row) & 1:
            return []
        for col in range(width):
            if col == row:
                continue
            value = (bits >> col) & 1
            previous = forced.get(col)
            if previous is not None and previous != value:
                return []
            forced[col] = value
    free = [col for col in range(width) if col not in forced]
    lifts = []
    for choice in range(1 << len(free)):
        covector = 0
        for col, value in forced.items():
            if value:
                covector |= 1 << col
        for index, col in enumerate(free):
            if (choice >> index) & 1:
                covector |= 1 << col
        if dot(image, covector) == 1 and pattern_mask(image, covector, width) == mask:
            lifts.append((image, covector))
    return lifts


def idempotents(width):
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
            yield image, covector


def subspaces_of(universe):
    """Every subspace of the ambient span `universe`, which includes 0."""
    empty = frozenset([0])
    found = {empty}
    pending = [empty]
    while pending:
        current = pending.pop()
        for vector in universe:
            if vector in current:
                continue
            enlarged = frozenset(old ^ vector for old in current) | current
            if enlarged not in found:
                found.add(enlarged)
                pending.append(enlarged)
    return found


def is_invariant(space, projectors):
    members = set(space)
    for image, covector in projectors:
        if any(dot(covector, vector) for vector in members) and image not in members:
            return False
    return True


def check_pattern_space():
    patterns = basis_patterns(5)
    require(len(gaussian(patterns)) == 4, "basis patterns are not independent")
    weights = []
    realizable = []
    for coefficients in itertools.product((0, 1), repeat=4):
        if coefficients == (0, 0, 0, 0):
            continue
        mask = combination(coefficients, 5)
        weight = mask.bit_count()
        weights.append(weight)
        require(weight >= 2, "pattern weight below 2 for %s" % (coefficients,))
        require(not single_column(mask, 5), "single-column pattern %s" % (coefficients,))
        lifts = realize(mask, 5)
        if lifts:
            realizable.append((coefficients, lifts))
    require(sorted(weights)[0] == 3, "minimum pattern weight moved: %s" % (sorted(weights)[0],))
    require(len(realizable) == 5, "expected 5 realizable patterns, found %s" % len(realizable))
    expected = {
        (1, 0, 0, 0): POOL[0],
        (0, 1, 0, 0): POOL[1],
        (1, 1, 0, 0): POOL[2],
        (0, 0, 1, 0): POOL[3],
        (0, 0, 0, 1): POOL[4],
    }
    for coefficients, lifts in realizable:
        require(len(lifts) == 1, "more than one lift for %s" % (coefficients,))
        require(lifts[0] == expected[coefficients], "unexpected lift %s -> %s" % (coefficients, lifts))
    seen = {item[0] for item in realizable}
    for coefficients, row_p, row_q, bit, value_p, value_q in CONFLICTS:
        require(coefficients not in seen, "conflict listed for a realizable pattern %s" % (coefficients,))
        mask = combination(coefficients, 5)
        require(implied_bit(mask, row_p, bit, 5) == value_p, "row value drifted for %s" % (coefficients,))
        require(implied_bit(mask, row_q, bit, 5) == value_q, "row value drifted for %s" % (coefficients,))
    require({item[0] for item in CONFLICTS} | seen == set(itertools.product((0, 1), repeat=4)) - {(0, 0, 0, 0)},
            "the conflict table does not cover every unrealizable pattern")


def check_pool_scan():
    for width in WIDTHS:
        pivots = gaussian(pattern_mask(image, covector, width) for image, covector in POOL)
        require(len(pivots) == 4, "pattern dimension drifted at width %s" % width)
        for row in range(width):
            for col in range(width):
                if row != col and in_span(pivots, 1 << (row * width + col)):
                    fail("matrix unit entered the pattern space at width %s" % width)
        found = []
        for image, covector in idempotents(width):
            mask = pattern_mask(image, covector, width)
            if mask and in_span(pivots, mask):
                found.append((image, covector))
        require(sorted(found) == sorted(POOL),
                "width %s pool %s" % (width, sorted(found)))


def check_ranks_and_edges():
    images = [image for image, _covector in POOL]
    covectors = [covector for _image, covector in POOL]
    require(len(gaussian(images)) == 5, "images do not span a five-dimensional space")
    require(len(gaussian(covectors)) == 5, "covectors do not span a five-dimensional space")
    for index in range(5):
        require(in_span(gaussian(images), 1 << index), "coordinate e_%s is outside the image span" % index)
        require(in_span(gaussian(covectors), 1 << index), "coordinate functional e_%s is outside the covector span" % index)
    label_index = {label: index for index, label in enumerate(LABELS)}
    for source, target in CYCLE_EDGES:
        image = images[label_index[target]]
        covector = covectors[label_index[source]]
        require(dot(covector, image) == 1, "missing hit edge %s -> %s" % (source, target))
    common = [vector for vector in range(32) if all(dot(covector, vector) == 0 for covector in covectors)]
    require(common == [0], "common kernel is %s" % (common,))


def check_subspace_lattice():
    universe = span_vectors(gaussian(image for image, _covector in POOL))
    require(len(universe) == 32, "joint image is not all of the coordinate five-space")
    spaces = subspaces_of(universe)
    require(len(spaces) == gaussian_count(5),
            "subspace census %s != %s" % (len(spaces), gaussian_count(5)))
    invariant = [space for space in spaces if len(space) not in (1, 32) and is_invariant(space, POOL)]
    require(invariant == [], "found %s invariant subspaces" % len(invariant))


def check_normal_form_control():
    triple = POOL[:3]
    universe = span_vectors(gaussian(image for image, _covector in triple))
    require(len(universe) == 8, "normal-form image is not three-dimensional")
    line = frozenset((0, POOL[1][0]))
    require(line <= frozenset(universe), "the control line is outside the normal-form image")
    require(is_invariant(line, triple), "normal-form line failed to be invariant")
    require(not is_invariant(line, POOL), "the extra projectors left the normal-form line invariant")
    spaces = subspaces_of(universe)
    require(len(spaces) == gaussian_count(3), "normal-form lattice count drifted")
    invariant = [space for space in spaces if len(space) not in (1, 8) and is_invariant(space, triple)]
    require(line in invariant, "normal-form census missed the invariant line")


def check_selected_frontier_untouched():
    selected = json.loads(Path("certificates/selected-result.json").read_text(encoding="utf-8"))
    require(selected["kappa"] == "781451/250000000", "selected kappa moved")
    require(selected["decimal"] == "0.003125804", "selected decimal moved")


def main():
    check_pattern_space()
    check_pool_scan()
    check_ranks_and_edges()
    check_subspace_lattice()
    check_normal_form_control()
    check_selected_frontier_untouched()
    print(MARKER)


if __name__ == "__main__":
    main()
