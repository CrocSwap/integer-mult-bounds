#!/usr/bin/env python3
"""Checks for two dimension-6 no-edge pools outside the three printed orbits.

PROOF.md is the all-width argument. This program rebuilds the three
witnesses printed in #7139 Section 9, checks that each complete pool
equals that list at the widths named there, and checks pools W and B:
pattern rank 4, no matrix unit, complete pool equal to the six named
projectors, image rank 6, and the coordinate-permutation invariants.
It raises SystemExit instead of using assert, so python -O does not skip
checks. Standard library only.
"""

import json
from pathlib import Path

MARKER = "PASS_DIM6_NO_EDGE_COORDINATE_CLASS"
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


def rank(vectors):
    return len(gaussian(vectors))


def in_span(pivots, mask):
    current = mask
    while current:
        bit = current & -current
        if bit not in pivots:
            return False
        current ^= pivots[bit]
    return True


def span_weights(patterns):
    basis = list(gaussian(patterns).values())
    found = []
    for choice in range(1 << len(basis)):
        total = 0
        for index, vector in enumerate(basis):
            if (choice >> index) & 1:
                total ^= vector
        found.append(weight(total))
    return sorted(found)


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


def embed_patterns(pairs, width):
    masks = []
    for image, covector in pairs:
        source = max(image.bit_length(), covector.bit_length(), 1)
        mask = pattern_mask(image, covector, source)
        embedded = 0
        for row in range(source):
            for col in range(source):
                if (mask >> (row * source + col)) & 1:
                    require(row < width and col < width, "witness does not embed in the checked width")
                    embedded |= 1 << (row * width + col)
        masks.append(embedded)
    return masks


def complete_pool(patterns, width):
    pivots = gaussian(patterns)
    found = []
    for image, covector in idempotents(width):
        mask = pattern_mask(image, covector, width)
        if mask and in_span(pivots, mask):
            found.append((image, covector))
    return found


def contains_unit(patterns, width):
    pivots = gaussian(patterns)
    for row in range(width):
        for col in range(width):
            if row != col and in_span(pivots, 1 << (row * width + col)):
                return True
    return False


def support_mask(pairs):
    mask = 0
    for image, covector in pairs:
        mask |= image | covector
    return mask


def invariant(pairs):
    return (
        weight(support_mask(pairs)),
        tuple(sorted(weight(image) for image, _covector in pairs)),
        tuple(sorted(weight(covector) for _image, covector in pairs)),
    )


def column(pivot, offsets):
    first, second = offsets
    nonzero = (first, second, first ^ second)
    return [(pivot ^ vector, pivot) for vector in nonzero]


def normal(shift):
    def basis(index):
        return 1 << (index + shift)

    return [
        (basis(0) ^ basis(2), basis(1) ^ basis(2)),
        (basis(1) ^ basis(2), basis(0) ^ basis(2)),
        (basis(0) ^ basis(1) ^ basis(2), basis(0) ^ basis(1) ^ basis(2)),
    ]


def witnesses():
    # Printed lists from #7139 Section 9. The column-column list is also
    # the dimension-6 witness of #7138 Section 6.
    column_column = column(1 << 0, ((1 << 1) ^ (1 << 2), (1 << 1) ^ (1 << 3))) + column(
        1 << 4, ((1 << 5) ^ (1 << 6), (1 << 5) ^ (1 << 7)))
    mixed = [
        (0b101, 0b110),
        (0b110, 0b101),
        (0b111, 0b111),
    ] + column(1 << 3, ((1 << 4) ^ (1 << 5), (1 << 4) ^ (1 << 6)))
    return {
        "normal-normal": normal(0) + normal(3),
        "column-column": column_column,
        "mixed": mixed,
    }


def pool_w():
    # Heavier plane beside a weight-(2,2,2) plane, on disjoint coordinates.
    return column(1 << 0, ((1 << 1) ^ (1 << 2), (1 << 3) ^ (1 << 4))) + column(
        1 << 5, ((1 << 6) ^ (1 << 7), (1 << 6) ^ (1 << 8)))


def pool_b():
    # The printed column-0 plane, with the second column sitting on coordinate 1.
    return column(1 << 0, ((1 << 1) ^ (1 << 2), (1 << 1) ^ (1 << 3))) + column(
        1 << 1, ((1 << 4) ^ (1 << 5), (1 << 4) ^ (1 << 6)))


def check_pool(pairs, widths, expected, label):
    require(len(pairs) == 6, label + " was not built as six projectors")
    require(invariant(pairs) == expected, label + " invariant changed: " + str(invariant(pairs)))
    require(rank([image for image, _covector in pairs]) == 6, label + " image rank is not 6")
    left = [image for image, _covector in pairs[:3]]
    right = [image for image, _covector in pairs[3:]]
    require(rank(left) == 3 and rank(right) == 3, label + " is not two 3-dimensional image spaces")
    require(rank(left + right) == 6, label + " image spaces meet nontrivially")
    for width in widths:
        patterns = embed_patterns(pairs, width)
        require(rank(patterns) == 4, label + " pattern rank changed at width " + str(width))
        weights = span_weights(patterns)
        require(weights[0] == 0 and weights[1] >= 2, label + " pattern span contains a unit or a hole")
        require(len(weights) == 16, label + " pattern span is not 4-dimensional")
        require(not contains_unit(patterns, width), label + " pattern span contains a matrix unit")
        found = complete_pool(patterns, width)
        require(sorted(found) == sorted(pairs),
                label + " complete pool changed at width " + str(width) + ": size " + str(len(found)))
        require(weight(support_mask(found)) == expected[0], label + " support grew at width " + str(width))


def permute_mask(mask, mapping):
    out = 0
    bit = 0
    while mask:
        if mask & 1:
            out |= 1 << mapping[bit]
        mask >>= 1
        bit += 1
    return out


def check_permutation_control(pairs, width):
    # Swapping coordinates 4 and 8 moves pool W. The invariant must stay
    # put, and the complete pool of the moved patterns must be the moved list.
    mapping = list(range(width))
    mapping[4], mapping[8] = mapping[8], mapping[4]
    moved = [(permute_mask(image, mapping), permute_mask(covector, mapping)) for image, covector in pairs]
    require(sorted(moved) != sorted(pairs), "the coordinate swap did not move pool W")
    require(invariant(moved) == invariant(pairs), "the invariant changed under a coordinate swap")
    patterns = embed_patterns(moved, width)
    found = complete_pool(patterns, width)
    require(sorted(found) == sorted(moved), "the moved pool is not the complete pool of its patterns")


def check_selected_frontier():
    payload = json.loads(SELECTED.read_text(encoding="utf-8"))
    require(payload.get("kappa") == "363005817/100000000000", "selected kappa changed")
    require(payload.get("decimal") == "0.00363005817", "selected decimal changed")


def main():
    check_selected_frontier()
    printed = witnesses()
    expected = {
        "normal-normal": (6, (2, 2, 2, 2, 3, 3), (2, 2, 2, 2, 3, 3)),
        "column-column": (8, (3, 3, 3, 3, 3, 3), (1, 1, 1, 1, 1, 1)),
        "mixed": (7, (2, 2, 3, 3, 3, 3), (1, 1, 1, 2, 2, 3)),
    }
    check_pool(printed["normal-normal"], (6, 7), expected["normal-normal"], "normal-normal")
    check_pool(printed["column-column"], (8, 9), expected["column-column"], "column-column")
    check_pool(printed["mixed"], (7, 8), expected["mixed"], "mixed")

    heavy = pool_w()
    placed = pool_b()
    heavy_invariant = (9, (3, 3, 3, 3, 3, 5), (1, 1, 1, 1, 1, 1))
    placed_invariant = (7, (3, 3, 3, 3, 3, 3), (1, 1, 1, 1, 1, 1))
    check_pool(heavy, (9, 10, 11), heavy_invariant, "pool-W")
    check_pool(placed, (7, 8, 9), placed_invariant, "pool-B")
    # Pool W really uses the weight-4 column, not another (2,2,2) plane.
    heavy_patterns = embed_patterns(heavy, 9)
    require(4 in span_weights(heavy_patterns), "pool W lost its weight-4 pattern")
    check_permutation_control(heavy, 9)

    triples = [expected[name] for name in expected] + [heavy_invariant, placed_invariant]
    require(len(set(triples)) == 5, "the five explicit pools are not in five invariant classes")
    print(MARKER)


if __name__ == "__main__":
    main()
