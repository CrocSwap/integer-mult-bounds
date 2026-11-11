#!/usr/bin/env python3
"""Finite census for the rank-4 length-30 layer of size 16.

The written argument is PROOF.md. Python checks the size window, the symmetry
reduction, one independent branch of the fiber tree, the coverage-255 witness,
and the length-32 Gray control. The C census exhausts the normalized tree.
"""

import itertools
import re
import subprocess
import tempfile
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
WITNESS = (
    1, 5, 4, 0, 4, 3, 6, 4, 7, 4, 1, 7, 6, 4, 2, 6, 5, 6, 7, 0,
    6, 5, 6, 2, 5, 0, 3, 7, 4, 0,
)
MISSING = 131
BRANCH_NODES = 515051
FULL_NODES = 57685490
PASS_LINE = re.compile(
    r"^PASS_RANK4_LAYER16 solutions=(\d+) nodes=(\d+) "
    r"branch1_nodes=(\d+) branch1_solutions=(\d+) checksum=(\d+) "
    r"subsets=120 sec=[0-9.]+$"
)
CONTROL = (
    (1 << 0) | (1 << 1),
    (1 << 0) | (1 << 2),
    (1 << 4) | (1 << 5),
    (1 << 0) | (1 << 2),
    (1 << 8) | (1 << 9),
    (1 << 0) | (1 << 2),
    (1 << 12) | (1 << 13),
    (1 << 0) | (1 << 2),
)


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


def covered_count(points):
    seen = 0
    for index, left in enumerate(points):
        for right in points[index:]:
            seen |= 1 << (left ^ right)
    return seen.bit_count()


def gray_transitions(dimension):
    if dimension == 1:
        return [0]
    smaller = gray_transitions(dimension - 1)
    return smaller + [dimension - 1] + smaller


def two_point_subsets():
    return [(1 << left) | (1 << right)
            for left, right in itertools.combinations(range(16), 2)]


def sumset(left, right):
    got = 0
    for a in range(16):
        if left & (1 << a):
            for b in range(16):
                if right & (1 << b):
                    got |= 1 << (a ^ b)
    return got


def build_tables(subsets):
    sums = [[0] * len(subsets) for _ in subsets]
    spans = [[False] * len(subsets) for _ in subsets]
    for i, left in enumerate(subsets):
        for j, right in enumerate(subsets):
            block = sumset(left, right)
            sums[i][j] = block
            spans[i][j] = block.bit_count() == 4
    checksum = 0
    for row in sums:
        for value in row:
            checksum = (checksum + value) & 0xFFFFFFFF
    return sums, spans, checksum


def direction_partitions(masks, delta):
    seen = 0
    pair_count = 0
    for left in range(8):
        right = left ^ delta
        if right < left:
            continue
        block = sumset(masks[left], masks[right])
        if block.bit_count() != 4 or (seen & block):
            return False
        seen |= block
        pair_count += 1
    return pair_count == 4 and seen == 0xFFFF


def independent(vectors):
    span = {0}
    for vector in vectors:
        span |= {item ^ vector for item in span}
    return len(span) == (1 << len(vectors))


def check_symmetry():
    images = []
    for first in range(1, 16):
        basis = [first]
        for vector in range(16):
            if independent(basis + [vector]):
                basis.append(vector)
            if len(basis) == 4:
                break
        require(len(basis) == 4 and independent(basis), "a nonzero vector does not start a basis")
        # The unique linear map sending basis[i] to e_i sends `first` to e_0.
        require(basis[0] == first, "basis construction dropped the requested vector")
        images.append(1)
    require(images == [1] * 15, "symmetry reduction missed a nonzero difference")


def fiber_floor(layer1):
    return 8 * ((16 + layer1 - 1) // layer1)


def fits(layer1, layer0):
    if not 1 <= layer1 <= 16 or layer0 < 1 or layer0 + layer1 > 30:
        return False
    return layer0 >= max(16, fiber_floor(layer1))


def check_window():
    require(16 * 15 // 2 >= 112 and 15 * 14 // 2 < 112, "pair floor is not 16")
    require(8 * 2 == 16 and (16 * 15 // 2) - 8 == 112, "cross-pair count is not 112")
    feasible = sorted(
        layer1 for layer1 in range(1, 17)
        if any(fits(layer1, layer0) for layer0 in range(1, 31))
    )
    require(feasible == [6, 8, 9, 10, 11, 12, 13, 14],
            "rank-4 layer-1 window changed")
    require(fits(6, 24) and not fits(6, 23), "the size-6 layer is not exactly 24 points")
    require(not any(fits(7, layer0) for layer0 in range(1, 31)),
            "a 7-point layer-1 set still fits")
    for layer1 in range(8, 15):
        require(fiber_floor(layer1) == 16, "rank-4 fiber floor is not 16")
        require(fits(layer1, 16), "the size-16 layer left the 8-to-14 window")
    require(fits(14, 16) and not fits(14, 17),
            "14 layer-1 points no longer force 16 layer-0 points")
    require(not fits(15, 15) and not fits(16, 14),
            "a layer-1 size above 14 still fits")


def check_control(subsets):
    require(subsets[0] == 3 and subsets[1] == 5, "subset order changed")
    for delta in range(1, 8):
        require(direction_partitions(CONTROL, delta) is bool(delta & 1),
                "the eight-fiber fixture changed")
    compatible = 0
    identity = subsets[0]
    for mask in subsets:
        if sumset(identity, mask).bit_count() == 4:
            compatible += 1
    require(compatible == 112, "the identity fiber no longer meets 112 partners")


def search_branch(sums, spans, locked_second):
    """Nested recount of one branch.

    This is a second formulation of the census prune. It recomputes each
    completed direction from the fibers chosen so far, instead of maintaining
    the incremental masks used by layer16_census.c.
    """
    chosen = [0] * 8
    nodes = 0
    solutions = 0

    def partial(just):
        for earlier in range(just):
            delta = earlier ^ just
            if not spans[chosen[earlier]][chosen[just]]:
                return False
            covered = sums[chosen[earlier]][chosen[just]]
            pair_count = 1
            for left in range(just):
                for right in range(left + 1, just):
                    if (left ^ right) != delta:
                        continue
                    block = sums[chosen[left]][chosen[right]]
                    if covered & block:
                        return False
                    covered |= block
                    pair_count += 1
            if pair_count == 4 and covered != 0xFFFF:
                return False
        return True

    def search(depth):
        nonlocal nodes, solutions
        nodes += 1
        if depth == 8:
            solutions += 1
            return
        begin, end = 0, 120
        if depth == 0:
            end = 1
        if depth == 1:
            begin, end = locked_second, locked_second + 1
        for index in range(begin, end):
            chosen[depth] = index
            if partial(depth):
                search(depth + 1)

    search(0)
    return nodes, solutions


def sojourn_layers(word, source):
    positions = [index for index, label in enumerate(word) if label == source]
    require(len(positions) == 2, "sojourn source must occur twice")
    points = prefixes(word)
    first, second = positions
    layer0 = []
    layer1 = []
    for time, point in enumerate(points):
        projected = point & ~(1 << source)
        if first < time <= second:
            layer1.append(projected)
        else:
            layer0.append(projected)
    return word[first + 1:second], layer0, layer1


def normalized_rank4(word, source):
    points = prefixes(word)
    first = next(index for index, label in enumerate(word) if label == source)
    origin = points[first]
    require(((origin >> source) & 1) == 0, "the prefix before the first occurrence has the source bit set")
    rotated = word[first:] + word[:first]
    rotated_points = prefixes(rotated)
    positions = [index for index, label in enumerate(rotated) if label == source]
    left, right = positions
    layer0 = []
    layer1 = []
    for time, point in enumerate(rotated_points):
        projected = point & ~(1 << source)
        if left < time <= right:
            layer1.append(projected)
        else:
            layer0.append(projected)
    return set(layer0), set(layer1)


def check_witness_and_gray():
    points = prefixes(WITNESS)
    require(len(points) == 30 and len(set(points)) == 30, "witness prefix count changed")
    seen = 0
    for index, left in enumerate(points):
        for right in points[index:]:
            seen |= 1 << (left ^ right)
    missing = [mask for mask in range(256) if not ((seen >> mask) & 1)]
    require(missing == [MISSING], "witness does not miss exactly mask 131")
    between, layer0, layer1 = sojourn_layers(WITNESS, 2)
    require(len(set(between)) == 4, "witness source 2 is not a rank-4 sojourn")
    require(len(set(layer0)) == 21 and len(set(layer1)) == 9,
            "witness rank-4 layer sizes changed")
    require(len(set(layer0)) >= 17 and len(set(layer1)) <= 13,
            "witness rank-4 sojourn misses the new floor")
    normalized0, normalized1 = normalized_rank4(WITNESS, 2)
    require(0 in normalized0 and 0 in normalized1,
            "normalization does not put 0 in both layers")
    broken = list(WITNESS)
    broken[0], broken[1] = broken[1], broken[0]
    require(covered_count(prefixes(broken)) != 255, "swapped witness kept coverage 255")

    def block(dimension, offset):
        return [offset + label for label in gray_transitions(dimension) + [dimension - 1]]

    word = block(4, 0) + block(4, 4)
    require(len(word) == 32 and covered_count(prefixes(word)) == 256,
            "Gray concatenation is not universal")


def check_selected_record():
    text = (ROOT / "certificates" / "selected-result.json").read_text(encoding="utf-8")
    require('"kappa": "781451/250000000"' in text, "selected kappa text changed")


def run_census(checksum):
    source = PACKAGE / "layer16_census.c"
    require(source.is_file(), "layer-16 census source is missing")
    with tempfile.TemporaryDirectory(prefix="rank4-layer16-") as directory:
        binary = str(Path(directory) / "layer16_census")
        compiled = subprocess.run(
            ["gcc", "-O3", "-std=c11", "-Wall", "-Wextra", "-Werror",
             "-o", binary, str(source)],
            check=False, capture_output=True, text=True)
        require(compiled.returncode == 0, "gcc failed: " + compiled.stderr[-400:])
        ran = subprocess.run([binary], check=False, capture_output=True, text=True)
        require(ran.returncode == 0, "layer-16 census failed: " + ran.stdout + ran.stderr)
    lines = [line for line in ran.stdout.splitlines() if line.startswith("PASS_RANK4_LAYER16")]
    require(len(lines) == 1, "census did not report one pass line")
    match = PASS_LINE.match(lines[0])
    require(match is not None, "pass line does not match the contract")
    solutions, nodes, branch_nodes, branch_solutions, reported = match.groups()
    require(int(solutions) == 0 and int(branch_solutions) == 0,
            "the census found a sixteen-point cover")
    require(int(branch_nodes) == BRANCH_NODES, "Python and C branch sizes differ")
    require(int(reported) == checksum, "sumset checksum disagrees with Python")
    require(int(nodes) == FULL_NODES, "full census node count changed")
    return int(nodes)


def main():
    check_window()
    check_symmetry()
    subsets = two_point_subsets()
    require(len(subsets) == 120, "two-point subset count is not 120")
    sums, spans, checksum = build_tables(subsets)
    check_control(subsets)
    nodes, solutions = search_branch(sums, spans, 1)
    require(nodes == BRANCH_NODES and solutions == 0,
            "independent branch recount changed")
    check_witness_and_gray()
    check_selected_record()
    full_nodes = run_census(checksum)
    print(
        "PASS_LENGTH30_RANK4_LAYER16 solutions=0 "
        f"nodes={full_nodes} branch1_nodes={BRANCH_NODES} "
        "layer0_floor=17 layer1_ceiling=13 witness_coverage=255"
    )


if __name__ == "__main__":
    main()
