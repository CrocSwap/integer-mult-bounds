"""Exact finite premises for three rank-five P112 endpoints. Apache-2.0."""

import argparse
import json
import sys
from collections import Counter, deque
from hashlib import sha256
from itertools import combinations
from math import gcd
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SOURCE = "research/p112-root-simplex-exclusion/geometry.py"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def source_geometry():
    pins = json.loads((PACKAGE / "SOURCES.json").read_text())["files"]
    pin = next(row for row in pins if row["path"] == SOURCE)
    path = ROOT / SOURCE
    require(
        sha256(path.read_bytes()).hexdigest() == pin["sha256"],
        "geometry source differs from its pin",
    )
    sys.path.insert(0, str(path.parent))
    import geometry

    return geometry


def binary_basis(values):
    require(
        len(values) <= 512 and all(type(x) is int and 0 <= x < 512 for x in values),
        "invalid nine-bit vector set",
    )
    basis = []
    for value in values:
        for row in basis:
            value = min(value, value ^ row)
        if value:
            basis = sorted(
                [min(row, row ^ value) for row in basis] + [value], reverse=True
            )
    return tuple(basis)


def projective(pair):
    require(
        len(pair) == 2 and all(type(x) is int for x in pair),
        "expected an integer evaluation pair",
    )
    divisor = gcd(*pair)
    if not divisor:
        return (0, 0)
    pair = tuple(x // divisor for x in pair)
    return pair if next(x for x in pair if x) > 0 else tuple(-x for x in pair)


def slice_capacity(labels):
    """Enumerate all 2667 codimension-two subspaces in a seven-space."""
    require(len(labels) == len(set(labels)) == 27, "expected a 27-line slice")
    basis = binary_basis(labels)
    require(len(basis) == 7, "slice must span seven binary dimensions")
    coordinates = {0: 0}
    for i, row in enumerate(basis):
        coordinates.update(
            {x ^ row: c | (1 << i) for x, c in tuple(coordinates.items())}
        )
    code = tuple(coordinates[label] for label in labels)
    histogram = Counter()
    witness = ()
    for a, b in combinations(range(1, 128), 2):
        if not a < b < (a ^ b):
            continue
        support = tuple(
            label
            for label, x in zip(labels, code, strict=True)
            if not ((a & x).bit_count() & 1) and not ((b & x).bit_count() & 1)
        )
        histogram[len(support)] += 1
        if len(support) > len(witness):
            witness = support
    require(sum(histogram.values()) == 2667, "incomplete slice census")
    require(
        len(witness) == 10 and len(binary_basis(witness)) == 5,
        "rank-five slice maximum is not ten",
    )
    return {
        "subspaces": 2667,
        "maximum": 10,
        "histogram": dict(sorted(histogram.items())),
        "witness": witness,
    }


def plane_inventory(geometry, roots):
    index = {root: i for i, root in enumerate(roots)}
    planes = set()
    for i, j in combinations(range(120), 2):
        dot = geometry.dot(roots[i], roots[j])
        if abs(dot) == 4:
            sign = 1 if dot > 0 else -1
            third = geometry.canonical(
                tuple(x - sign * y for x, y in zip(roots[i], roots[j], strict=True))
            )
            planes.add(tuple(sorted((i, j, index[third]))))
    require(len(planes) == 1120, "A2 plane inventory changed")
    permutations = []
    for simple in geometry.SIMPLE:
        permutation = []
        for root in roots:
            factor = geometry.dot(root, simple) // 4
            image = geometry.canonical(
                tuple(x - factor * y for x, y in zip(root, simple, strict=True))
            )
            permutation.append(index[image])
        require(len(set(permutation)) == 120, "reflection is not a permutation")
        permutations.append(permutation)
    seen = {min(planes)}
    queue = deque(seen)
    for _ in range(1120):
        require(bool(queue), "A2 orbit ended early")
        plane = queue.popleft()
        for permutation in permutations:
            image = tuple(sorted(permutation[i] for i in plane))
            require(image in planes, "reflection left the A2 inventory")
            if image not in seen:
                seen.add(image)
                queue.append(image)
    require(not queue and seen == planes, "A2 planes are not one Weyl orbit")
    return tuple(sorted(planes))


def support_bound(common_support, piece_capacity=12, singleton_capacity=10):
    require(
        type(common_support) is int and 0 <= common_support <= 112,
        "invalid common support",
    )
    require(
        type(piece_capacity) is int
        and 1 <= piece_capacity <= 112
        and type(singleton_capacity) is int
        and 1 <= singleton_capacity <= piece_capacity,
        "invalid capacities",
    )
    # N nonzero code coordinates, L singleton sites and M piece incidences:
    # 2N <= M + L <= 3*piece_capacity + 3*singleton_capacity.
    residual_cap = 3 * (piece_capacity + singleton_capacity) // 2
    return {
        "common_support": common_support,
        "minimum_code_union": 78,
        "residual_union_cap": residual_cap,
        "excluded_by_count": 78 - common_support > residual_cap,
    }


def compute():
    geometry = source_geometry()
    roots, points, labels, coordinates = geometry.root_data()
    chamber = geometry.chamber_receipt(roots, points, coordinates)
    counts = chamber["rank_six_parabolic_counts"]
    require(sorted(counts)[-2:] == [30, 36], "E6 classification gap changed")
    omitted = tuple(combinations(range(8), 2))[counts.index(36)]
    parabolic = tuple(geometry.SIMPLE[i] for i in range(8) if i not in omitted)
    normal_roots = tuple(
        i
        for i, root in enumerate(roots)
        if all(geometry.dot(root, row) == 0 for row in parabolic)
    )
    require(len(normal_roots) == 3, "E6 normal is not an A2 plane")
    planes = plane_inventory(geometry, roots)
    require(normal_roots in planes, "E6 normal missing from A2 inventory")
    unions = Counter(
        sum(any(geometry.dot(roots[i], point) for i in plane) for point in points)
        for plane in planes
    )
    require(dict(unions) == {78: 896, 80: 224}, "P112 A2 union spectrum changed")
    all_labels = tuple(
        1 | sum((int(x) % 2) << (i + 1) for i, x in enumerate(row))
        for row in coordinates
    )
    a, b = (roots[i] for i in planes[0][:2])
    classes = {}
    for root, label in zip(roots, all_labels, strict=True):
        key = projective((geometry.dot(a, root), geometry.dot(b, root)))
        if key != (0, 0):
            classes.setdefault(key, []).append(label)
    require(
        sorted(map(len, classes.values())) == [1, 1, 1, 27, 27, 27],
        "full E8 A2 projective fibers changed",
    )
    slices = {
        str(key): slice_capacity(value)
        for key, value in sorted(classes.items())
        if len(value) == 27
    }
    flat = geometry.flat_capacity(labels, 5)
    require(not support_bound(45)["excluded_by_count"], "counting boundary changed")
    require(support_bound(44)["excluded_by_count"], "claimed threshold is not proved")
    return {
        "claim": "three-rank5-common-support44-intersection-at-most-one",
        "scope": "characteristic-zero; sufficient threshold, not sharpness",
        "p112_lines": 112,
        "a2_planes": len(planes),
        "a2_union_histogram": unions,
        "rank_six_parabolic_counts": counts,
        "e6_normal_root_indices": normal_roots,
        "full_e8_projective_slice_capacities": slices,
        "p112_five_flats": flat,
        "threshold44": support_bound(44),
        "counting_boundary45": support_bound(45),
    }


def write_result(output, result):
    require(not output.resolve().is_relative_to(ROOT), "external output required")
    with output.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.loads(json.dumps(compute()))
    if args.output:
        write_result(args.output, result)
    else:
        expected = json.loads((PACKAGE / "RESULT.json").read_text())
        require(result == expected, "finite receipt differs")
    print(
        "PASS_P112_A2_RANK5_SHORTENING threshold=44 intersection<=1 "
        "a2_planes=1120 slice_max=10 five_flats=3309747 nonsharp"
    )


if __name__ == "__main__":
    main()
