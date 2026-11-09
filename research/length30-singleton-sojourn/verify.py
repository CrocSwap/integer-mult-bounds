#!/usr/bin/env python3
"""Finite checks for the length-30 eight-source sojourn obstructions.

The written argument is PROOF.md. These checks enumerate the admissible
count vectors, the 4-bit bent functions, the coordinate 4+4 union, the
length-32 Gray control, and one explicit length-30 word of coverage 255.
"""

from itertools import product

WITNESS = (
    1, 5, 4, 0, 4, 3, 6, 4, 7, 4, 1, 7, 6, 4, 2, 6, 5, 6, 7, 0,
    6, 5, 6, 2, 5, 0, 3, 7, 4, 0,
)
MISSING = 131


def require(ok, message):
    if not ok:
        raise SystemExit(message)


def prefixes(word):
    state = 0
    points = [0]
    for label in word[:-1]:
        state ^= 1 << label
        points.append(state)
    state ^= 1 << word[-1]
    require(state == 0, "word does not restore the connector")
    return points


def coverage(points):
    points = list(points)
    seen = [0, 0, 0, 0]
    for i, left in enumerate(points):
        for right in points[i:]:
            diff = left ^ right
            seen[diff >> 6] |= 1 << (diff & 63)
    return seen


def covered_count(points):
    return sum(mask.bit_count() for mask in coverage(points))


def full_space(points):
    return covered_count(points) == 256


def pack(vector, bit):
    low_mask = (1 << bit) - 1
    return (vector & low_mask) | ((vector >> (bit + 1)) << bit)


def hyperplane_cover(vectors, bit):
    seen = 0
    width = 1 << 7
    for vector in vectors:
        require((vector >> bit) & 1 == 0, "projection left the deleted coordinate")
        seen |= 1 << pack(vector, bit)
    return seen.bit_count() == width


def sumset(left, right):
    return {a ^ b for a in left for b in right}


def sojourn(word, source):
    positions = [index for index, label in enumerate(word) if label == source]
    require(len(positions) == 2, "sojourn source must occur twice")
    first, second = positions
    between = word[first + 1:second]
    points = prefixes(word)
    layer1 = []
    layer0 = []
    for time, point in enumerate(points):
        projected = point & ~(1 << source)
        if first < time <= second:
            layer1.append(projected)
        else:
            layer0.append(projected)
    return between, layer0, layer1


def gray_transitions(dimension):
    if dimension == 1:
        return [0]
    smaller = gray_transitions(dimension - 1)
    return smaller + [dimension - 1] + smaller


def gray_block(dimension, offset):
    return [offset + label for label in gray_transitions(dimension) + [dimension - 1]]


def is_bent(table):
    for shift in range(1, 16):
        shifted = 0
        for point in range(16):
            shifted |= ((table >> (point ^ shift)) & 1) << point
        if (table ^ shifted).bit_count() != 8:
            return False
    return True


def bent_tables():
    return [table for table in range(1 << 16) if is_bent(table)]


def quadratic_example():
    table = 0
    for point in range(16):
        bit0, bit1 = point & 1, (point >> 1) & 1
        bit2, bit3 = (point >> 2) & 1, (point >> 3) & 1
        if bit0 & bit1 ^ bit2 & bit3:
            table |= 1 << point
    return table


def no_three_dimensional_bent_space(tables):
    members = set(tables)
    neighbors = {}
    for left in tables:
        neighbors[left] = [right for right in tables if right != left and (left ^ right) in members]
    require(any(neighbors[left] for left in tables), "a 2-dimensional bent pair is missing")
    for left in tables:
        adjacent = set(neighbors[left])
        for right in neighbors[left]:
            mixed = left ^ right
            if mixed not in members:
                continue
            for third in adjacent.intersection(neighbors[right], neighbors[mixed]):
                values = (left, right, third, mixed, left ^ third, right ^ third, mixed ^ third)
                if 0 not in values and len(set(values)) == 7:
                    return False
    return True


def admissible_counts():
    found = []
    for counts in product((2, 4, 6), repeat=8):
        if sum(counts) == 30:
            found.append(counts)
    return found


def coordinate_union():
    return {low for low in range(16)} | {high << 4 for high in range(16)}


def omissions_fail(universe):
    require(0 in universe, "the union does not contain zero")
    without_zero = universe - {0}
    require(len(without_zero) == 30 and full_space(without_zero),
            "deleting zero from the union destroyed the cover")
    for dropped in without_zero:
        trial = universe - {dropped}
        require(0 in trial and len(trial) == 30, "nonzero omission changed zero")
        require(not full_space(trial), "a 30-point subset containing zero covers")


def apply_basis(vector, images):
    total = 0
    for bit, image in enumerate(images):
        if (vector >> bit) & 1:
            total ^= image
    return total


def sheared_union():
    images = (
        0b00000001, 0b00000010, 0b00000100, 0b00001000,
        0b00010001, 0b00100000, 0b01000000, 0b10000000,
    )
    rank = {apply_basis(1 << bit, images) for bit in range(8)}
    require(len(rank) == 8, "shear basis is singular")
    return {apply_basis(vector, images) for vector in coordinate_union()}


def outside_thirty_point_cover():
    universe = coordinate_union()
    return (universe - {1, 16}) | {17}


def check_counts():
    rows = admissible_counts()
    require(len(rows) == 1016, "admissible count total changed")
    require(all(2 in row for row in rows), "a length-30 count vector has no double")
    shapes = {tuple(sorted(row, reverse=True)) for row in rows}
    expect = {
        (4, 4, 4, 4, 4, 4, 4, 2),
        (6, 4, 4, 4, 4, 4, 2, 2),
        (6, 6, 4, 4, 4, 2, 2, 2),
        (6, 6, 6, 4, 2, 2, 2, 2),
    }
    require(shapes == expect, "count shapes are not the four predicted types")


def check_rank_thresholds():
    for rank in (0, 1, 2):
        require(2 ** (7 - rank) > 29, "low-rank coset count does not exceed 29")
    require(2 ** (7 - 3) == 16, "rank-3 coset count is not 16")


def check_bent_census():
    tables = bent_tables()
    require(len(tables) == 896, "4-bit bent census is not 896")
    require(is_bent(quadratic_example()), "x0 x1 + x2 x3 is not bent")
    require(not is_bent(0), "the zero function was accepted as bent")
    require(no_three_dimensional_bent_space(tables), "a 3-bit vectorial bent map exists")


def check_direct_sum():
    universe = coordinate_union()
    require(len(universe) == 31 and full_space(universe), "coordinate 4+4 union is not universal")
    omissions_fail(universe)
    sheared = sheared_union()
    require(len(sheared) == 31 and full_space(sheared), "sheared 4+4 union is not universal")
    omissions_fail(sheared)
    extra = outside_thirty_point_cover()
    require(len(extra) == 30 and full_space(extra), "the mixed 30-point set does not cover")
    require(not extra <= universe, "the mixed set stayed inside the coordinate union")


def check_gray_control():
    word = gray_block(4, 0) + gray_block(4, 4)
    require(len(word) == 32 and full_space(prefixes(word)), "Gray concatenation is not universal")
    doubles = [source for source in range(8) if word.count(source) == 2]
    require(doubles, "Gray word has no multiplicity-2 source")
    for source in doubles:
        between, layer0, layer1 = sojourn(word, source)
        require(len(set(between)) >= 3, "Gray sojourn has rank below 3")
        require(hyperplane_cover(sumset(layer0, layer1), source), "Gray cross-sum misses a mask")
        self_sums = sumset(layer0, layer0) | sumset(layer1, layer1)
        require(hyperplane_cover(self_sums, source), "Gray self-sum misses a mask")


def check_witness():
    points = prefixes(WITNESS)
    require(len(WITNESS) == 30 and len(points) == 30, "witness length changed")
    require(len(set(points)) == 30, "witness repeats a prefix")
    counts = [WITNESS.count(source) for source in range(8)]
    require(sum(counts) == 30 and min(counts) == 2, "witness counts are illegal")
    require(all(count in (2, 4, 6) for count in counts), "witness count is outside {2,4,6}")
    seen = coverage(points)
    total = sum(mask.bit_count() for mask in seen)
    require(total == 255, "witness coverage is not 255")
    missing = [mask for mask in range(256) if (seen[mask >> 6] >> (mask & 63)) & 1 == 0]
    require(missing == [MISSING], "witness misses an unexpected mask")
    measured = {}
    for source in range(8):
        if counts[source] != 2:
            continue
        between, layer0, _layer1 = sojourn(WITNESS, source)
        measured[source] = (len(set(between)), len(set(layer0)))
    require(measured == {1: (6, 20), 2: (4, 21), 3: (7, 9)},
            "witness sojourn ranks changed")
    broken = list(WITNESS)
    broken[0], broken[1] = broken[1], broken[0]
    require(covered_count(prefixes(broken)) != 255, "swapped witness kept coverage 255")


def main():
    check_counts()
    check_rank_thresholds()
    check_bent_census()
    check_direct_sum()
    check_gray_control()
    check_witness()
    print("PASS_LENGTH30_SINGLETON_SOJOURN counts=1016 bent=896 gray=32 witness_coverage=255")


if __name__ == "__main__":
    main()
