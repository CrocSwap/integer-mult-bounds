"""Independent lattice/RREF/dual-functional census; no producer imports."""

import json
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from math import gcd, lcm
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
SIMPLE = (
    (1, -1, -1, -1, -1, -1, -1, 1),
    (2, 2, 0, 0, 0, 0, 0, 0),
    (-2, 2, 0, 0, 0, 0, 0, 0),
    (0, -2, 2, 0, 0, 0, 0, 0),
    (0, 0, -2, 2, 0, 0, 0, 0),
    (0, 0, 0, -2, 2, 0, 0, 0),
    (0, 0, 0, 0, -2, 2, 0, 0),
    (0, 0, 0, 0, 0, -2, 2, 0),
)


def check(condition, message):
    if not condition:
        raise ValueError(message)


def solve(matrix, rhs):
    rows = [
        [Fraction(x) for x in row] + [Fraction(y)]
        for row, y in zip(matrix, rhs, strict=True)
    ]
    for j in range(8):
        pivot = next(i for i in range(j, 8) if rows[i][j])
        rows[j], rows[pivot] = rows[pivot], rows[j]
        scale = rows[j][j]
        rows[j] = [x / scale for x in rows[j]]
        for i in range(8):
            if i != j:
                scale = rows[i][j]
                rows[i] = [x - scale * y for x, y in zip(rows[i], rows[j], strict=True)]
    return tuple(row[-1] for row in rows)


def normalize(row):
    divisor = gcd(*row)
    check(divisor != 0, "zero direction")
    if next(x for x in row if x) < 0:
        divisor = -divisor
    return tuple(x // divisor for x in row)


def lattice_data():
    roots = tuple(
        row
        for row in product(range(-2, 3), repeat=8)
        if sum(x * x for x in row) == 8
        and sum(row) % 4 == 0
        and len({x % 2 for x in row}) == 1
        and next(x for x in row if x) > 0
    )
    check(len(roots) == 120, "lattice root count")
    frame = {
        tuple(2 * int(j == k) + sign * int(j == k + 1) for j in range(8))
        for k in range(0, 8, 2)
        for sign in (-2, 2)
    }
    points = tuple(row for row in roots if row not in frame)
    coordinates = [solve(tuple(zip(*SIMPLE, strict=True)), row) for row in points]
    check(all(x.denominator == 1 for row in coordinates for x in row), "lattice labels")
    labels = tuple(
        1 + sum((int(x) % 2) << (j + 1) for j, x in enumerate(row))
        for row in coordinates
    )
    check(len(set(labels)) == 112, "live label count")
    return roots, points, labels


def rref_flats(labels):
    rows = []
    for high_pivots in combinations(range(9), 2):
        options = []
        for pivot in high_pivots:
            free = [j for j in range(pivot) if j not in high_pivots]
            options.append(
                [
                    1 << pivot | sum(((n >> i) & 1) << j for i, j in enumerate(free))
                    for n in range(1 << len(free))
                ]
            )
        for a, b in product(*options):
            span = sorted((a, b, a ^ b))
            rows.append(tuple(span[:2]))
    check(len(rows) == len(set(rows)) == 43435, "RREF two-plane enumeration")
    rows.sort()
    violations = tuple(
        sum(1 << i for i, label in enumerate(labels) if (label & a).bit_count() % 2)
        for a in range(512)
    )
    full = (1 << 112) - 1
    flats = tuple(full ^ (violations[a] | violations[b]) for a, b in rows)
    return tuple(rows), flats, violations


def validate_quotient(roots, points, flats, representatives, sizes):
    orders = []
    for k in range(4):
        order = list(range(8))
        order[2 * k : 2 * k + 2] = reversed(order[2 * k : 2 * k + 2])
        orders.append((order, set()))
    for k in range(3):
        order = list(range(8))
        order[2 * k : 2 * k + 4] = (
            order[2 * k + 2 : 2 * k + 4] + order[2 * k : 2 * k + 2]
        )
        orders.append((order, set()))
    orders.append((list(range(8)), {0, 2}))
    lookup, tables = {r: i for i, r in enumerate(points)}, []
    for order, negative in orders:
        mapped = {
            r: tuple((-r[j] if j in negative else r[j]) for j in order) for r in roots
        }
        mapped = {r: max(v, tuple(-x for x in v)) for r, v in mapped.items()}
        check(set(mapped.values()) == set(roots), "reference E8 permutation")
        permutation = [lookup[mapped[r]] for r in points]
        tables.append(
            [
                [
                    sum(1 << permutation[8 * b + j] for j in range(8) if x >> j & 1)
                    for x in range(256)
                ]
                for b in range(14)
            ]
        )
    remaining = set(flats)
    for seed, size in zip(representatives, sizes, strict=True):
        check(seed in remaining, "invalid or repeated flat representative")
        queue, orbit = [seed], {seed}
        for cursor in range(43181):
            if cursor == len(queue):
                break
            for table in tables:
                m = queue[cursor]
                image = sum(table[b][(m >> (8 * b)) & 255] for b in range(14))
                check(image in remaining, "reference orbit escaped remaining flats")
                if image not in orbit:
                    check(len(queue) < 43181, "reference orbit capacity")
                    orbit.add(image)
                    queue.append(image)
        check(len(orbit) == size, "reference orbit size")
        remaining.difference_update(orbit)
    check(not remaining, "reference quotient is incomplete")


def low_support_directions(points):
    inventory = set()
    for j, expected in ((0, 1080), (7, 120)):
        rational = solve(SIMPLE, [int(i == j) for i in range(8)])
        denominator = lcm(*(x.denominator for x in rational))
        seed = normalize(tuple(int(x * denominator) for x in rational))
        pending, orbit = [seed], {seed}
        for cursor in range(4000):
            if cursor == len(pending):
                break
            h = pending[cursor]
            for alpha in SIMPLE:
                coefficient = sum(x * y for x, y in zip(h, alpha, strict=True))
                v = normalize(
                    tuple(
                        4 * x - coefficient * y for x, y in zip(h, alpha, strict=True)
                    )
                )
                if v not in orbit:
                    check(len(pending) < 4000, "reference direction capacity")
                    orbit.add(v)
                    pending.append(v)
        check(len(orbit) == expected, "reference direction orbit size")
        inventory.update(orbit)
    directions = sorted(inventory)
    supports = [
        sum(
            1 << i
            for i, r in enumerate(points)
            if sum(x * y for x, y in zip(h, r, strict=True))
        )
        for h in directions
    ]
    check(len(directions) == 1200, "reference direction inventory")
    return directions, supports


def dual_census(flats, annihilators, violations, representatives, supports):
    # If at most five points violate TWO equations, at most five violate each.
    # Enumerate the cheap individual equations first, then all their two-planes.
    flat_index = {pair: i for i, pair in enumerate(annihilators)}
    records = []
    for first in representatives:
        maximum_union = max((first | second).bit_count() for second in flats)
        check(maximum_union <= 68, "reference two-flat union cap")
        entries = []
        for h, support in enumerate(supports):
            if support.bit_count() > maximum_union + 5:
                continue
            residual = support & ~first
            eligible = [
                (a, residual & violations[a])
                for a in range(1, 512)
                if (residual & violations[a]).bit_count() <= 5
            ]
            for (a, cut_a), (b, cut_b) in combinations(eligible, 2):
                cut = cut_a | cut_b
                if b < (a ^ b) and cut.bit_count() <= 5:
                    entries.append([h, flat_index[(a, b)], str(cut)])
        records.append([maximum_union, sorted(entries)])
    return records


def common_five_bound(records):
    maximum = 0
    for _, entries in records:
        unions = {0}
        for _, _, raw_cut in entries:
            cut = int(raw_cut)
            unions.update(
                old | cut for old in tuple(unions) if (old | cut).bit_count() <= 5
            )
            check(len(unions) <= 65536, "reference common-cut union capacity")
        for union in unions:
            directions = {h for h, _, cut in entries if int(cut) & ~union == 0}
            maximum = max(maximum, len(directions))
            check(len(directions) <= 2, "reference common-five bound failed")
    check(maximum == 2, "reference two-direction attainment")
    return maximum


def witness_check(witness, roots, points, labels, annihilators, flats):
    def mask(pair):
        check(
            len(pair) == 2
            and len(set(pair + [pair[0] ^ pair[1]])) == 3
            and all(0 < a < 512 for a in pair),
            "reference annihilator",
        )
        return flats[annihilators.index(tuple(sorted(pair + [pair[0] ^ pair[1]])[:2]))]

    first = mask(witness["first_flat_annihilator"])
    hs = [tuple(entry["h"]) for entry in witness["directions"]]
    check(len(hs) == 3 and all(h in roots for h in hs), "reference root triple")
    gram = [[sum(x * y for x, y in zip(a, b, strict=True)) for b in hs] for a in hs]
    check(gram == [[8, 0, 0], [0, 8, 0], [0, 0, 8]], "reference orthogonal triple")
    cuts = []
    for h in hs:
        support = sum(
            1 << i
            for i, r in enumerate(points)
            if sum(x * y for x, y in zip(h, r, strict=True))
        )
        cuts.append(
            [
                support & ~(first | second)
                for second in flats
                if (support & ~(first | second)).bit_count() <= 5
            ]
        )
    check(all(0 < len(row) <= 16 for row in cuts), "reference completion capacity")
    minimum_union = min((a | b | c).bit_count() for a, b, c in product(*cuts))
    common = sum(1 << i for i in witness["common_deleted_lines"])
    for h, entry in zip(hs, witness["directions"], strict=True):
        off = sum(
            1 << i
            for i, r in enumerate(points)
            if sum(x * y for x, y in zip(h, r, strict=True))
        )
        cut = off & ~(first | mask(entry["second_flat_annihilator"]))
        check(cut & ~common == 0, "reference common-six containment")
        check(
            [i for i in range(112) if cut >> i & 1] == entry["deleted_lines"],
            "reference literal completion cuts",
        )
    check(minimum_union == common.bit_count() == 6, "reference sharp boundary")
    return {
        "minimum_common_union_for_witness": minimum_union,
        "witness_completion_counts": [len(row) for row in cuts],
        "gram_determinant": 512,
    }


def run():
    expected = json.loads((PACKAGE / "RESULT.json").read_text())
    roots, points, labels = lattice_data()
    annihilators, flats, violations = rref_flats(labels)
    representatives = [int(value) for value in expected["representative_masks"]]
    validate_quotient(
        roots, points, flats, representatives, expected["flat_orbit_sizes"]
    )
    directions, supports = low_support_directions(points)
    records = dual_census(flats, annihilators, violations, representatives, supports)
    check(records == expected["classes"], "independent complete cut tables disagree")
    histogram = {
        str(k): v for k, v in sorted(Counter(s.bit_count() for s in supports).items())
    }
    check(
        histogram == expected["classification"]["support_histogram"],
        "reference supports",
    )
    check(
        len(directions) == 1200 and len(set(flats)) == 43181, "reference finite domains"
    )
    witness = witness_check(
        json.loads((PACKAGE / "WITNESS.json").read_text()),
        roots,
        points,
        labels,
        annihilators,
        flats,
    )
    return {
        "status": "PASS_P112_COMMON_FIVE_REFERENCE",
        "seven_spaces": 43435,
        "direction_count": 1200,
        "maximum_directions_with_five_common_cuts": common_five_bound(records),
        "complete_cut_records": sum(len(r[1]) for r in records),
        **witness,
    }


if __name__ == "__main__":
    result = run()
    check(
        result == json.loads((PACKAGE / "REFERENCE.json").read_text()),
        "reference receipt differs",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
