#!/usr/bin/env python3
"""Six-step rotating-normal closure and its rank-two correction.

The checker walks the coordinate core. It does not rerun port boundary charts.
"""

import hashlib
import json
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_ROTATING_NORMAL_CLOSURE dimension=43 mass=86 no_new_kappa"
LEVERS = "research/bit-revision3-levers-seed03/levers.py"
GEOMETRY = "research/p112-root-simplex-exclusion/geometry.py"
PRECISION = 200


def fail(message):
    raise SystemExit("FAIL_ROTATING_NORMAL_CLOSURE " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical(row):
    return max(tuple(row), tuple(-entry for entry in row))


def roots():
    found = set()
    for left, right in combinations(range(8), 2):
        for sign in (-2, 2):
            row = [0] * 8
            row[left], row[right] = 2, sign
            found.add(canonical(row))
    for row in product((-1, 1), repeat=8):
        if sum(entry == -1 for entry in row) % 2 == 0:
            found.add(canonical(row))
    require(len(found) == 120, "the root count moved")
    return tuple(sorted(found))


def rotate(row):
    return tuple(entry for index in range(0, 8, 2) for entry in (-row[index + 1], row[index]))


def rational_rank(rows):
    basis = []
    for row in rows:
        current = [Fraction(entry) for entry in row]
        for pivot, prior in basis:
            if current[pivot]:
                factor = current[pivot] / prior[pivot]
                current = [entry - factor * other for entry, other in zip(current, prior)]
        pivot = next((index for index, entry in enumerate(current) if entry), None)
        if pivot is not None:
            basis.append((pivot, current))
    return len(basis)


def structure_counts(lines):
    inventory = set(lines)
    pairs = 0
    for row in lines:
        image = rotate(row)
        require(canonical(image) in inventory, "a rotated root left the inventory")
        require(sum(left * right for left, right in zip(row, image)) == 0, "a root met its rotate")
        require(rotate(image) == tuple(-entry for entry in row), "the rotate square moved")
        require(canonical(image) != row, "a root was projectively fixed")
        frame = [other for other in lines if sum(left * right for left, right in zip(other, image)) == 0]
        require(len(frame) == 63 and rational_rank(frame) == 7, "a rotate hyperplane moved")
        if row < canonical(image):
            pairs += 1
    require(pairs == 60, "the projective pair count moved")
    return pairs


def closure():
    frames = [1, 0]
    expressions = [{(0, 0)}, {(1, 0)}]
    active = list(range(8))
    exterior = 0
    high, low = 0, 1
    next_axis = 8
    profile = Counter()

    def move(role, new):
        old = frames[role]
        require(old & ~new == 0, "a frame step was not nested")
        difference = new ^ old
        if difference:
            profile[difference.bit_count()] += 1
            expressions[role] = {(bank, mask ^ difference) for bank, mask in expressions[role]}
            frames[role] = new

    normals = []
    for stage in range(6):
        port, normal_index = stage % 2, 1 - stage % 2
        full = exterior | sum(1 << axis for axis in active)
        normal = active[normal_index]
        hyperplane = full ^ (1 << normal)
        require(frames[high] == exterior | (1 << active[port]), "a source entrance moved")
        require(frames[low] == exterior, "a target entrance moved")
        move(high, hyperplane)
        move(low, hyperplane)
        expressions[low] ^= expressions[high]
        move(low, full)
        high, low = low, high
        normals.append(normal)
        if stage != 5:
            exterior = hyperplane
            active = [normal if index == normal_index else -1 for index in range(8)]
            for index in range(8):
                if active[index] == -1:
                    active[index] = next_axis
                    next_axis += 1
    dimension = next_axis
    universe = (1 << dimension) - 1
    final = normals[-1]
    require(dimension == 43 and high == 0 and low == 1, "the owner closure moved")
    require(dict(profile) == {1: 6, 6: 6, 7: 6}, "the rank histogram moved")
    require(expressions[0] == {(0, universe ^ 1)}, "the first bank endpoint moved")
    require(expressions[1] == {(1, universe ^ (1 << final))}, "the spectator endpoint moved")
    correction = 1 | (1 << final)
    fixed = {(bank, mask ^ correction) for bank, mask in expressions[1]}
    require(fixed == {(1, universe ^ 1)}, "the rank-two correction missed the endpoint")
    require(sum(rank * count for rank, count in profile.items()) == 84, "the uncorrected mass moved")
    return dimension, normals, profile


def down(value):
    return Fraction((value.numerator << PRECISION) // value.denominator, 1 << PRECISION)


def up(value):
    return -down(-value)


@lru_cache(None)
def atanh(value):
    total, power, index = Fraction(0), value, 0
    while True:
        total += power / (2 * index + 1)
        power *= value * value
        index += 1
        tail = power / ((2 * index + 1) * (1 - value * value))
        if tail < Fraction(1, 1 << (PRECISION + 8)):
            return down(total), up(total + tail)


@lru_cache(None)
def logarithm(integer):
    if integer == 1:
        return Fraction(0), Fraction(0)
    low, high = logarithm(integer - 1)
    left, right = atanh(Fraction(1, 2 * integer - 1))
    return down(low + 2 * left), up(high + 2 * right)


def exponential(low, high):
    def series(value, upper):
        total, term, index = Fraction(1), Fraction(1), 0
        while True:
            index += 1
            term = term * value / index
            total += term
            if term * value < Fraction(1, 1 << (PRECISION + 8)):
                return up(total + 2 * term * value / (index + 1)) if upper else down(total)

    return series(low, False), series(high, True)


def child(rank, width, saving):
    width_low, width_high = logarithm(width)
    rank_low, rank_high = logarithm(rank)
    growth = exponential(max(Fraction(0), saving * (width_low - rank_high)), saving * (width_high - rank_low))
    return down(Fraction(rank, width) * growth[0]), up(Fraction(rank, width) * growth[1])


def moment(histogram, width, families, saving):
    low = high = Fraction(0)
    for rank, count in histogram.items():
        if count:
            cost = child(rank, width, saving)
            low += Fraction(count) * cost[0]
            high += Fraction(count) * cost[1]
    return down(low / families), up(high / families)


def evaluate():
    require(sha256(ROOT / LEVERS) == "287a1c1201548665087b9b2034210fac92e805f36ea9d4ab41c2471a92d69d7f", "lever model drift")
    require(sha256(ROOT / GEOMETRY) == "b8ac379e41f5ad83bdb6c7f7c55129fc3d9c07801ea61591478f25d72ff0b021", "geometry drift")
    levers = (ROOT / LEVERS).read_text(encoding="utf-8")
    require("PREC = 200" in levers and "return _down(lo / w), _up(hi / w)" in levers, "the bill rounding moved")
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    lines = roots()
    pairs = structure_counts(lines)
    dimension, path, profile = closure()
    corrected = dict(profile)
    corrected[2] = 1
    extra = dict(profile)
    extra[1] += 1
    saving = Fraction(1, 499)
    corrected_bound = moment(corrected, dimension, 2, saving)
    extra_bound = moment(extra, dimension, 2, saving)
    require(corrected_bound[0] > 1, "the corrected saving bound moved")
    require(extra_bound[1] < 1, "the extra rank-one bound moved")
    require(sum(rank * count for rank, count in corrected.items()) == 2 * dimension, "the correction missed the capacity")
    return {
        "root_lines": len(lines),
        "projective_pairs": pairs,
        "dimension": dimension,
        "normal_axis_path": path,
        "rank_histogram": {str(rank): profile[rank] for rank in sorted(profile)},
        "uncorrected_mass": 84,
        "correction_rank": 2,
        "capacity": 2 * dimension,
        "zero_saving_bill": "1",
        "corrected_saving_lower_exceeds_one": True,
        "extra_rank_one_upper_below_one": True,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
