#!/usr/bin/env python3
"""Finite checks for the length-30 rank-3 arc obstruction.

The written argument is PROOF.md. The C search exhausts the two surviving
rank-3 families. These Python checks cover the size floors, the height-step
reduction, the quotient-walk orbits, the coverage-255 witness, and the
length-32 Gray control.
"""

import itertools
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
WITNESS = (
    1, 5, 4, 0, 4, 3, 6, 4, 7, 4, 1, 7, 6, 4, 2, 6, 5, 6, 7, 0,
    6, 5, 6, 2, 5, 0, 3, 7, 4, 0,
)
FIVE_TESTS = 224164584
FOUR_TESTS = 9418680
PASS_LINE = re.compile(
    r"^PASS_RANK3_NONE walks=108 digest=([0-9a-f]{16}) "
    r"five=(\d+) four=(\d+) best_miss=(\d+) sec=[0-9.]+$"
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


def covered_mask(points):
    seen = 0
    for index, left in enumerate(points):
        for right in points[index:]:
            seen |= 1 << (left ^ right)
    return seen


def covered_count(points):
    return covered_mask(points).bit_count()


def gray_transitions(dimension):
    if dimension == 1:
        return [0]
    smaller = gray_transitions(dimension - 1)
    return smaller + [dimension - 1] + smaller


def pair_floor(rank):
    outside = 128 - (1 << rank)
    smallest = 2
    while smallest * (smallest - 1) // 2 < outside:
        smallest += 1
    return smallest


def fiber_floor(rank, layer1):
    return (1 << (7 - rank)) * (((1 << rank) + layer1 - 1) // layer1)


def integer_window(rank, layer0, layer1):
    if layer0 < 1 or layer1 < 1 or layer0 + layer1 > 30:
        return False
    if layer1 > (1 << rank):
        return False
    if layer0 < fiber_floor(rank, layer1):
        return False
    if rank < 7 and layer0 < pair_floor(rank):
        return False
    return True


def difference_basis(heights):
    got = 0
    ordered = list(heights)
    for index, left in enumerate(ordered):
        for right in ordered[index:]:
            got |= 1 << (left ^ right)
    return got == 0xFF


def stored_heights(steps, slots, start, length):
    chosen = set(slots)
    level = start
    found = {0, level}
    used = 0
    for index in range(length - 1):
        if index in chosen:
            level ^= 1 << steps[used]
            used += 1
            found.add(level)
    return found


def quotient_walks():
    found = []

    def walk(pos, steps, counts, seen, path):
        if steps == 16:
            if seen == 0xFFFF and all(count in (2, 4, 6) for count in counts):
                found.append(tuple(path))
            return
        if 16 - steps < 16 - seen.bit_count():
            return
        for direction in range(4):
            if counts[direction] >= 6:
                continue
            nxt = pos ^ (1 << direction)
            counts[direction] += 1
            path.append(direction)
            walk(nxt, steps + 1, counts, seen | (1 << nxt), path)
            path.pop()
            counts[direction] -= 1

    walk(0, 0, [0, 0, 0, 0], 1, [])
    return found


def canonical_digest(walks):
    orbits = set()
    for path in walks:
        best = path
        for perm in itertools.permutations(range(4)):
            image = tuple(perm[step] for step in path)
            if image < best:
                best = image
        orbits.add(best)
    digest = 14695981039346656037
    for path in sorted(orbits):
        for step in path:
            digest ^= step
            digest = (digest * 1099511628211) & ((1 << 64) - 1)
    return len(orbits), digest


def sojourn_layers(word, source):
    positions = [index for index, label in enumerate(word) if label == source]
    require(len(positions) == 2, "sojourn source must occur twice")
    first, second = positions
    between = word[first + 1:second]
    points = prefixes(word)
    layer0 = []
    layer1 = []
    for time, point in enumerate(points):
        projected = point & ~(1 << source)
        if first < time <= second:
            layer1.append(projected)
        else:
            layer0.append(projected)
    return len(set(between)), len(set(layer0)), len(set(layer1))


def check_floors():
    require([pair_floor(rank) for rank in (3, 4, 5, 6)] == [16, 16, 15, 12],
            "pair-count floors changed")
    require(not integer_window(3, 22, 7), "rank 3 accepted a 7-point layer")
    require(all(integer_window(3, layer0, 8) for layer0 in range(16, 23)),
            "rank 3 rejected a full 3-flat window")
    require(not integer_window(3, 15, 8), "rank 3 pair floor dropped below 16")
    require(integer_window(4, 16, 14) and not integer_window(4, 15, 14),
            "rank 4 boundary moved")
    require(not integer_window(4, 16, 15) and not integer_window(4, 16, 7),
            "rank 4 admitted an excluded layer-1 size")
    require(integer_window(5, 15, 15) and integer_window(5, 24, 6),
            "rank 5 endpoint window is missing")
    require(not integer_window(5, 14, 15) and not integer_window(5, 23, 6),
            "rank 5 floor dropped")
    require(integer_window(6, 12, 11) and integer_window(6, 12, 18),
            "rank 6 window is missing")
    require(not integer_window(6, 11, 18) and not integer_window(6, 13, 10),
            "rank 6 floor dropped")
    require(integer_window(7, 9, 21) and integer_window(7, 22, 6),
            "rank 7 window is missing")
    require(not integer_window(7, 4, 21), "rank 7 accepted too small a layer")


def check_low_height():
    spanning = 0
    examined = 0
    for steps_n in (1, 2, 3):
        for length in range(steps_n, 22):
            for steps in itertools.product(range(3), repeat=steps_n):
                start = 0
                for bit in steps:
                    start ^= 1 << bit
                for slots in itertools.combinations(range(length), steps_n):
                    examined += 1
                    if difference_basis(stored_heights(steps, slots, start, length)):
                        spanning += 1
    require(spanning == 0, "a height word of length at most 3 spans F_2^3")
    require(examined > 100000, "height enumeration did not cover the arc lengths")
    sample = {0, 1, 2, 4, 7}
    require(difference_basis(sample), "the size-5 basis control failed")
    require(not difference_basis({0, 1, 2, 4}), "a 4-point set was accepted as a basis")


def check_orbits():
    orbits, digest = canonical_digest(quotient_walks())
    require(orbits == 108, "quotient-walk orbit count is not 108")
    return digest


def check_witness_and_gray():
    points = prefixes(WITNESS)
    require(len(points) == 30 and len(set(points)) == 30, "witness prefix count changed")
    missing = [mask for mask in range(256) if not ((covered_mask(points) >> mask) & 1)]
    require(missing == [131], "witness does not miss exactly mask 131")
    measured = {}
    for source in range(8):
        if WITNESS.count(source) != 2:
            continue
        rank, layer0, layer1 = sojourn_layers(WITNESS, source)
        measured[source] = (rank, layer0, layer1)
        require(rank >= 4, "witness sojourn fell into the excluded ranks")
        require(integer_window(rank, layer0, layer1), "witness misses a new size floor")
    require(measured == {1: (6, 20, 10), 2: (4, 21, 9), 3: (7, 9, 21)},
            "witness sojourn measurements changed")
    broken = list(WITNESS)
    broken[0], broken[1] = broken[1], broken[0]
    require(covered_count(prefixes(broken)) != 255, "swapped witness kept coverage 255")

    def block(dimension, offset):
        return [offset + label for label in gray_transitions(dimension) + [dimension - 1]]

    word = block(4, 0) + block(4, 4)
    require(len(word) == 32 and covered_count(prefixes(word)) == 256,
            "Gray concatenation is not universal")


def packed_layer0(path, steps, slots, start):
    vertices = [0]
    point = 0
    for step in path:
        point ^= 1 << step
        vertices.append(point)
    level = start
    station = 0
    used = 0
    chosen = set(slots)
    points = {0, level | (vertices[0] << 3)}
    for index in range(len(path) + len(steps) - 1):
        if index in chosen:
            level ^= 1 << steps[used]
            used += 1
        else:
            station += 1
        points.add(level | (vertices[station] << 3))
    return points


def outside_miss_count(points):
    got = 0
    ordered = list(points)
    for index, left in enumerate(ordered):
        for right in ordered[index:]:
            got |= 1 << (left ^ right)
    covered = sum(1 for mask in range(8, 128) if (got >> mask) & 1)
    return 120 - covered


def control_word_layer0():
    arc_a = gray_transitions(3)
    require(arc_a == [0, 1, 0, 2, 0, 1, 0], "3-cube Gray path changed")
    quotient = (0, 1, 2, 3, 0, 1, 2, 1, 0, 1, 2, 3, 0, 1, 2, 1)
    height = (0, 0, 1, 1, 2)
    arc_b = []
    used = 0
    station = 0
    for index in range(21):
        if index < 5:
            arc_b.append(height[used])
            used += 1
        else:
            arc_b.append(3 + quotient[station])
            station += 1
    word = (7, *arc_a, 7, *arc_b)
    require(len(word) == 30, "control word length is not 30")
    points = prefixes(word)
    layer0 = []
    for time, point in enumerate(points):
        if not (0 < time <= 8):
            layer0.append(point & ~(1 << 7))
    return set(layer0)


def control_miss():
    path = (0, 1, 2, 3, 0, 1, 2, 1, 0, 1, 2, 3, 0, 1, 2, 1)
    steps = (0, 0, 1, 1, 2)
    slots = (0, 1, 2, 3, 4)
    packed = packed_layer0(path, steps, slots, 4)
    require(packed == control_word_layer0(), "packed layer 0 disagrees with the length-30 word")
    require(outside_miss_count(packed) == 60, "control word does not miss 60 outside vectors")


def run_search(digest):
    source = PACKAGE / "rank3_search.c"
    require(source.is_file(), "rank-3 search source is missing")
    with tempfile.TemporaryDirectory(prefix="rank3-arc-") as directory:
        binary = str(Path(directory) / "rank3_search")
        compiled = subprocess.run(
            ["gcc", "-O3", "-std=c11", "-Wall", "-Wextra", "-Werror",
             "-o", binary, str(source)],
            check=False, capture_output=True, text=True)
        require(compiled.returncode == 0, "gcc failed: " + compiled.stderr[-400:])
        ran = subprocess.run([binary], check=False, capture_output=True, text=True)
        require(ran.returncode == 0, "rank-3 search failed: " + ran.stdout + ran.stderr)
    lines = [line for line in ran.stdout.splitlines() if line.startswith("PASS_RANK3_NONE")]
    require(len(lines) == 1, "search did not report one pass line")
    match = PASS_LINE.match(lines[0])
    require(match is not None, "pass line does not match the contract")
    reported, five, four, best = match.groups()
    require(int(reported, 16) == digest, "canonical-walk digest disagrees with Python")
    require(int(five) == FIVE_TESTS and int(four) == FOUR_TESTS,
            "exhaustive test counts changed")
    require(int(best) == 2, "minimum outside miss is not 2")


def main():
    check_floors()
    check_low_height()
    digest = check_orbits()
    check_witness_and_gray()
    control_miss()
    run_search(digest)
    print("PASS_LENGTH30_ARC_SUMSET rank3=none best_miss=2 walks=108 floors=16,16,15,12")


if __name__ == "__main__":
    main()
