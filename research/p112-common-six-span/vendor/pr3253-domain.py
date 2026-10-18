"""Reconstruct the complete low-support direction and seven-flat domains."""

import hashlib
import json
import runpy
from collections import Counter
from itertools import combinations
from math import gcd
from pathlib import Path
from types import SimpleNamespace

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
GEOMETRY_PATH = "research/p112-simplex-coordinate-bound/vendor/geometry.py"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def geometry():
    pins = json.loads((PACKAGE / "SOURCES.json").read_text())["files"]
    pin = next(row for row in pins if row["path"] == GEOMETRY_PATH)
    source = ROOT / GEOMETRY_PATH
    require(
        hashlib.sha256(source.read_bytes()).hexdigest() == pin["sha256"],
        "geometry source changed",
    )
    # run_path executes this authenticated source file, not an import-cache entry.
    return SimpleNamespace(**runpy.run_path(str(source)))


def binary_rank(columns):
    require(
        len(columns) <= 112 and all(type(x) is int and 0 < x < 512 for x in columns),
        "nine-bit labels",
    )
    basis = [0] * 9
    for value in columns:
        for pivot in reversed(range(9)):
            if value >> pivot & 1:
                if basis[pivot]:
                    value ^= basis[pivot]
                else:
                    basis[pivot] = value
                    break
    return sum(x != 0 for x in basis)


def flat_mask(labels, rows):
    require(len(rows) == 2 and binary_rank(rows) == 2, "rank-two annihilator")
    return sum(
        1 << i
        for i, label in enumerate(labels)
        if all((a & label).bit_count() % 2 == 0 for a in rows)
    )


def seven_flats(labels):
    full = (1 << 112) - 1
    kernels = tuple(
        full
        ^ sum(1 << i for i, label in enumerate(labels) if (a & label).bit_count() % 2)
        for a in range(512)
    )
    result = tuple(
        (kernels[a] & kernels[b], (a, b))
        for a, b in combinations(range(1, 512), 2)
        if b < (a ^ b)
    )
    require(len(result) == 43435, "seven-space count")
    require(len({mask for mask, _ in result}) == 43181, "seven-space trace count")
    return result


def permutation_tables(permutations):
    width = len(permutations[0])
    require(width in (112, 120), "root permutation width")
    require(
        all(sorted(p) == list(range(width)) for p in permutations), "not a permutation"
    )
    return tuple(
        tuple(
            tuple(
                sum(1 << p[8 * b + k] for k in range(8) if x >> k & 1)
                for x in range(256)
            )
            for b in range(width // 8)
        )
        for p in permutations
    )


def image(mask, table):
    return sum(table[b][(mask >> (8 * b)) & 255] for b in range(len(table)))


def mask_orbit(seed, tables, capacity, domain=None):
    queue, seen = [seed], {seed}
    for cursor in range(capacity):
        if cursor == len(queue):
            return seen
        for table in tables:
            value = image(queue[cursor], table)
            require(domain is None or value in domain, "orbit left its domain")
            if value not in seen:
                require(len(queue) < capacity, "mask orbit capacity")
                seen.add(value)
                queue.append(value)
    return seen


def frame_generators(g, roots, points):
    orders = []
    for pair in range(4):
        order = list(range(8))
        order[2 * pair], order[2 * pair + 1] = order[2 * pair + 1], order[2 * pair]
        orders.append((order, ()))
    for pair in range(3):
        order = list(range(8))
        order[2 * pair : 2 * pair + 4] = (
            order[2 * pair + 2 : 2 * pair + 4] + order[2 * pair : 2 * pair + 2]
        )
        orders.append((order, ()))
    orders.append((list(range(8)), (0, 2)))
    root_set, point_lookup = set(roots), {r: i for i, r in enumerate(points)}
    permutations = []
    for order, negatives in orders:
        images = tuple(
            g.canonical(tuple(-r[j] if j in negatives else r[j] for j in order))
            for r in roots
        )
        require(set(images) == root_set, "signed permutation left E8")
        mapped = dict(zip(roots, images, strict=True))
        require(all(mapped[r] in point_lookup for r in points), "frame not preserved")
        permutations.append(tuple(point_lookup[mapped[r]] for r in points))
    return permutation_tables(permutations)


def flat_representatives(flats, tables):
    domain = {mask for mask, _ in flats}
    remaining = set(domain)
    representatives, sizes = [], []
    for _ in range(43181):
        if not remaining:
            break
        seed = min(remaining)
        orbit = mask_orbit(seed, tables, 43181, domain)
        require(orbit <= remaining, "overlapping flat orbits")
        representatives.append(seed)
        sizes.append(len(orbit))
        remaining.difference_update(orbit)
    require(not remaining and len(representatives) == 121, "incomplete flat quotient")
    require(sum(sizes) == 43181, "flat quotient coverage")
    return tuple(representatives), tuple(sizes)


def primitive(vector):
    divisor = gcd(*vector)
    require(divisor > 0, "zero direction")
    if next(x for x in vector if x) < 0:
        divisor = -divisor
    return tuple(x // divisor for x in vector)


def direction_orbit(seed, simple):
    queue, seen = [seed], {seed}
    for cursor in range(4000):
        if cursor == len(queue):
            return seen
        h = queue[cursor]
        for alpha in simple:
            pairing = sum(x * y for x, y in zip(h, alpha, strict=True))
            reflected = primitive(
                tuple(4 * x - pairing * y for x, y in zip(h, alpha, strict=True))
            )
            if reflected not in seen:
                require(len(queue) < 4000, "direction orbit capacity")
                seen.add(reflected)
                queue.append(reflected)
    return seen


def directions(g, roots, points, coordinates):
    # A successful pair has at most 68+5=73 off-lines, hence >=39 zeros.
    # Every rank-at-most-six parabolic has at most 36 full root lines.
    rank_six_maximum = max(
        sum(all(c[j] == 0 for j in omitted) for c in coordinates)
        for omitted in combinations(range(8), 2)
    )
    require(rank_six_maximum == 36, "rank-six parabolic cap")
    zeros = [sum(c[j] == 0 for c in coordinates) for j in range(8)]
    require(zeros == [42, 28, 22, 14, 16, 23, 37, 63], "rank-seven parabolics")
    inventory, orbits = set(), []
    for j, count in enumerate(zeros):
        if count < 39:
            continue
        seed = g.primitive(g.solve(g.SIMPLE, [int(i == j) for i in range(8)]))
        orbit = direction_orbit(seed, g.SIMPLE)
        inventory.update(orbit)
        orbits.append([j, count, len(orbit)])
    require(orbits == [[0, 42, 1080], [7, 63, 120]], "rank-seven direction orbits")
    selected = tuple(sorted(inventory))
    supports = tuple(
        sum(1 << i for i, r in enumerate(points) if g.dot(h, r)) for h in selected
    )
    histogram = dict(sorted(Counter(mask.bit_count() for mask in supports).items()))
    require(
        len(selected) == 1200
        and histogram == {53: 112, 56: 8, 70: 128, 73: 896, 76: 56},
        "complete direction superset for support at most 73",
    )
    return (
        selected,
        supports,
        {
            "orbits": orbits,
            "support_histogram": histogram,
            "rank_six_parabolic_maximum": rank_six_maximum,
        },
    )
