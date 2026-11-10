#!/usr/bin/env python3
"""Finite checks for the pattern-dimension-4 no-edge image bound.

PROOF.md is the all-width argument. This program repeats the finite census
of six-point subsets of F2^4, the GL(3,2) no-edge triple census, the
complete pools of four explicit witnesses, and their subspace lattices.
It raises SystemExit instead of using assert, so python -O does not skip
checks. Standard library only.
"""

import itertools
import json
from pathlib import Path

MARKER = "PASS_NO_EDGE_DIM4_IMAGE_AT_MOST_SIX"
SELECTED = Path(__file__).resolve().parents[2] / "certificates" / "selected-result.json"


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


def span_vectors(vectors):
    points = [0]
    for vector in gaussian(vectors).values():
        points += [old ^ vector for old in points]
    return points


def rank(vectors):
    return len(gaussian(vectors))


def min_span_weight(patterns):
    basis = list(gaussian(patterns).values())
    if not basis:
        return 0
    lowest = None
    for choice in range(1, 1 << len(basis)):
        total = 0
        for index, vector in enumerate(basis):
            if (choice >> index) & 1:
                total ^= vector
        count = weight(total)
        if lowest is None or count < lowest:
            lowest = count
    return lowest


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


def complete_pool(patterns, width):
    pivots = gaussian(patterns)
    found = []
    for image, covector in idempotents(width):
        mask = pattern_mask(image, covector, width)
        if mask and in_span(pivots, mask):
            found.append((image, covector, mask))
    return found


def contains_unit(patterns, width):
    pivots = gaussian(patterns)
    for row in range(width):
        for col in range(width):
            if row != col and in_span(pivots, 1 << (row * width + col)):
                return True
    return False


def subspaces(universe):
    found = {frozenset([0])}
    pending = [frozenset([0])]
    points = list(universe)
    while pending:
        current = pending.pop()
        for vector in points:
            if vector in current:
                continue
            enlarged = current | frozenset(old ^ vector for old in current)
            if enlarged not in found:
                found.add(enlarged)
                pending.append(enlarged)
    return found


def is_invariant(space, pool):
    members = set(space)
    for image, covector in pool:
        if any(dot(covector, vector) for vector in members) and image not in members:
            return False
    return True


def zero_subsets(points, size):
    found = []
    point_set = set(points)
    for prefix in itertools.combinations(points, size - 1):
        total = 0
        for value in prefix:
            total ^= value
        if total in point_set and total not in prefix:
            found.append(tuple(sorted(prefix + (total,))))
    return set(found)


def classify_six(points):
    triples = zero_subsets(points, 3)
    quads = zero_subsets(points, 4)
    pairs = list(itertools.combinations(triples, 2))
    meet1 = any(len(set(left) & set(right)) == 1 for left, right in pairs)
    disjoint_pairs = [pair for pair in pairs if set(pair[0]).isdisjoint(pair[1])]
    if meet1:
        kind = "meet1"
    elif not triples:
        kind = "cap"
    elif len(triples) == 1:
        kind = "one"
    elif len(triples) == 2 and len(disjoint_pairs) == 1 and not quads:
        kind = "two"
    else:
        kind = "other"
    return kind, triples, quads


def check_census():
    counts = {"meet1": 0, "cap": 0, "one": 0, "two": 0, "other": 0}
    cap_quads = one_quads = two_quads = 0
    for points in itertools.combinations(range(1, 16), 6):
        kind, _triples, quads = classify_six(points)
        counts[kind] += 1
        if kind == "cap":
            cap_quads += len(quads) == 3
        elif kind == "one":
            one_quads += len(quads) == 1
        elif kind == "two":
            two_quads += len(quads) == 0
    require(sum(counts.values()) == 5005, "six-subset census is not a partition of C(15,6)")
    require(counts == {"meet1": 2625, "cap": 420, "one": 1680, "two": 280, "other": 0},
            "six-subset counts changed: " + str(counts))
    require(cap_quads == 420 and one_quads == 1680 and two_quads == 280,
            "quad counts inside the three admissible types changed")
    # The displayed cap and one-triple examples are the shapes used in the proof.
    cap_kind, _, cap_q = classify_six((1, 2, 4, 7, 8, 11))
    one_kind, _, one_q = classify_six((1, 2, 3, 4, 8, 13))
    two_kind, two_t, two_q = classify_six((1, 2, 3, 4, 8, 12))
    require(cap_kind == "cap" and len(cap_q) == 3, "cap example was reclassified")
    require(one_kind == "one" and len(one_q) == 1, "one-triple example was reclassified")
    require(two_kind == "two" and len(two_t) == 2 and not two_q, "two-triple example was reclassified")


def check_triple_classification():
    survivors = []
    invertible = 0
    for columns in itertools.product(range(1, 8), repeat=3):
        if rank(columns) < 3:
            continue
        invertible += 1
        covectors = []
        for index in range(3):
            matches = [mask for mask in range(8)
                       if all(dot(mask, columns[other]) == (index == other) for other in range(3))]
            require(len(matches) == 1, "a GL(3,2) basis has a unique dual covector")
            covectors.append(matches[0])
        weights = [weight(image) * weight(covector) - weight(image & covector)
                   for image, covector in zip(columns, covectors)]
        if min(weights) >= 2:
            survivors.append((columns, tuple(covectors), tuple(weights)))
    require(invertible == 168, "GL(3,2) has 168 elements, found " + str(invertible))
    require(len(survivors) == 18, "no-edge triple census found " + str(len(survivors)))
    for columns, covectors, weights in survivors:
        require(sorted(weights) == [3, 3, 6], "survivor pattern weights are not 3,3,6")
        require(sorted(weight(column) for column in columns) == [2, 2, 3],
                "survivor column weights are not 2,2,3")
        heavy = [index for index, column in enumerate(columns) if weight(column) == 3][0]
        light = [index for index in range(3) if index != heavy]
        require(covectors[heavy] == columns[heavy], "weight-3 column is not self-dual")
        require(covectors[light[0]] == columns[light[1]] and covectors[light[1]] == columns[light[0]],
                "weight-2 columns are not dual to each other")


def embed_patterns(pairs, width):
    masks = []
    for image, covector in pairs:
        source = max(image.bit_length(), covector.bit_length(), 1)
        mask = pattern_mask(image, covector, source)
        positions = [(row, col) for row in range(source) for col in range(source)
                     if (mask >> (row * source + col)) & 1]
        embedded = 0
        for row, col in positions:
            require(row < width and col < width, "witness does not embed in the checked width")
            embedded |= 1 << (row * width + col)
        masks.append(embedded)
    return masks


def check_pool(pairs, widths, expected_size, expected_image, expected_covector, label):
    reports = []
    for width in widths:
        patterns = embed_patterns(pairs, width)
        require(rank(patterns) == 4, label + " pattern rank changed at width " + str(width))
        require(min_span_weight(patterns) >= 2, label + " pattern span contains a unit or zero")
        require(not contains_unit(patterns, width), label + " pattern span contains a matrix unit")
        pool = complete_pool(patterns, width)
        require(len(pool) == expected_size,
                label + " pool size " + str(len(pool)) + " at width " + str(width))
        images = [image for image, _covector, _mask in pool]
        covectors = [covector for _image, covector, _mask in pool]
        require(rank(images) == expected_image, label + " image rank changed")
        require(rank(covectors) == expected_covector, label + " covector rank changed")
        reports.append((width, [(image, covector) for image, covector, _mask in pool], span_vectors(images)))
    return reports


def check_one_block(pairs, width, label):
    patterns = embed_patterns(pairs, width)
    pool = [(image, covector) for image, covector, _mask in complete_pool(patterns, width)]
    universe = span_vectors([image for image, _covector in pool])
    proper = [space for space in subspaces(universe)
              if len(space) not in (1, len(universe)) and is_invariant(space, pool)]
    require(rank(patterns) == 2 and len(pool) == 3 and rank([image for image, _c in pool]) == 3,
            label + " is not the three-projector normal form")
    require(proper, label + " lost its invariant subspace; the lattice scan is not discriminating")


def check_normal_pair():
    def normal(shift):
        e = lambda index: 1 << (index + shift)
        return [
            (e(0) ^ e(2), e(1) ^ e(2)),
            (e(1) ^ e(2), e(0) ^ e(2)),
            (e(0) ^ e(1) ^ e(2), e(0) ^ e(1) ^ e(2)),
        ]
    pairs = normal(0) + normal(3)
    reports = check_pool(pairs, (6, 7, 8), 6, 6, 6, "normal-normal")
    for _width, pool, universe in reports:
        require(len(universe) == 64, "normal-normal image is not 6-dimensional")
        left = span_vectors([image for image, _covector in pool[:3]])
        right = span_vectors([image for image, _covector in pool[3:]])
        require(len(left) == 8 and len(right) == 8, "a normal-form block is not 3-dimensional")
        require(is_invariant(left, pool) and is_invariant(right, pool),
                "a normal-form block is not invariant")
        proper = [space for space in subspaces(universe)
                  if len(space) not in (1, len(universe)) and is_invariant(space, pool)]
        require(proper, "normal-normal lattice scan found no proper invariant subspace")
        require(frozenset(left) in {frozenset(space) for space in proper},
                "the explicit block is missing from the invariant lattice")
    # One block alone is reducible. If the lattice scan always reported
    # irreducibility, the six-projector check above would still pass and
    # this one would fail.
    check_one_block(normal(0), 6, "one-normal-block")


def check_column_pairs():
    def column(pivot, offsets):
        first, second = offsets
        nonzero = (first, second, first ^ second)
        return [(pivot ^ vector, pivot) for vector in nonzero]

    disjoint = column(1 << 0, (1 << 1 ^ 1 << 2, 1 << 1 ^ 1 << 3)) + column(
        1 << 4, (1 << 5 ^ 1 << 6, 1 << 5 ^ 1 << 7))
    reports = check_pool(disjoint, (8, 9), 6, 6, 2, "column-column")
    for _width, pool, universe in reports:
        kernel = [vector for vector in universe if vector and all(dot(covector, vector) == 0
                                                                   for _image, covector in pool)]
        require(len(kernel) == 15, "column-column kernel is not 4-dimensional")
        require(is_invariant(kernel + [0], pool), "column-column kernel is not invariant")
    mixed = [
        (0b101, 0b110),
        (0b110, 0b101),
        (0b111, 0b111),
    ] + column(1 << 3, (1 << 4 ^ 1 << 5, 1 << 4 ^ 1 << 6))
    mixed_reports = check_pool(mixed, (7, 8), 6, 6, 4, "column-normal")
    for _width, pool, universe in mixed_reports:
        kernel = [vector for vector in universe if vector and all(dot(covector, vector) == 0
                                                                   for _image, covector in pool)]
        require(len(kernel) == 3, "column-normal kernel is not 2-dimensional")
        require(is_invariant(kernel + [0], pool), "column-normal kernel is not invariant")


def check_dimension_five_witness():
    # The irreducible dimension-5 pool from #7094, rechecked here as sharpness.
    pairs = [
        (0b00101, 0b00110),
        (0b00110, 0b00101),
        (0b00111, 0b00111),
        (0b01100, 0b01011),
        (0b11101, 0b10010),
    ]
    reports = check_pool(pairs, (5, 6, 7, 8), 5, 5, 5, "dimension-five")
    for _width, pool, universe in reports:
        require(len(universe) == 32, "dimension-five image is not 5-dimensional")
        proper = [space for space in subspaces(universe)
                  if len(space) not in (1, len(universe)) and is_invariant(space, pool)]
        require(not proper, "dimension-five witness has a proper invariant subspace")
    # Deleting the last projector leaves a proper invariant subspace, so the
    # lattice scan is not hard-wired to report irreducibility.
    patterns = embed_patterns(pairs[:-1], 5)
    pool = [(image, covector) for image, covector, _mask in complete_pool(patterns, 5)]
    universe = span_vectors([image for image, _covector in pool])
    proper = [space for space in subspaces(universe)
              if len(space) not in (1, len(universe)) and is_invariant(space, pool)]
    require(proper, "deleted dimension-five pool stayed irreducible")


def check_selected_frontier():
    payload = json.loads(SELECTED.read_text(encoding="utf-8"))
    require(payload.get("kappa") == "781451/250000000", "selected kappa changed")
    require(payload.get("decimal") == "0.003125804", "selected decimal changed")


def main():
    check_selected_frontier()
    check_census()
    check_triple_classification()
    check_normal_pair()
    check_column_pairs()
    check_dimension_five_witness()
    print(MARKER)


if __name__ == "__main__":
    main()
