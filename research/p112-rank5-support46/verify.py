"""Exact frame-puncture obstruction for three rank-five P112 endpoints."""

import argparse
import json
import sys
from collections import Counter
from hashlib import sha1, sha256
from itertools import combinations, product
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
GEOMETRY = "research/p112-root-simplex-exclusion/geometry.py"
RETAINED = {
    "vendor/PR3249-PROOF.md",
    "vendor/PR3249-RESULT.json",
    "vendor/PR3257-PROOF.md",
    "vendor/PR3257-RESULT.json",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def bounded_bytes(path):
    with path.open("rb") as stream:
        data = stream.read(100001)
    require(len(data) <= 100000, "source size limit")
    return data


def authenticate():
    manifest = json.loads(bounded_bytes(PACKAGE / "SOURCES.json"))
    rows = manifest["retained_files"]
    require(len(rows) == 4, "retained inventory size")
    require({r["local_path"] for r in rows} == RETAINED, "retained inventory paths")
    for row in rows:
        data = bounded_bytes(PACKAGE / row["local_path"])
        require(sha256(data).hexdigest() == row["sha256"], "retained source digest")
        blob = sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        require(blob == row["git_blob"], "retained Git blob digest")
    pins = [r for r in manifest["files"] if r["path"] == GEOMETRY]
    require(len(pins) == 1, "geometry inventory")
    require(
        sha256(bounded_bytes(ROOT / GEOMETRY)).hexdigest() == pins[0]["sha256"],
        "geometry source digest",
    )
    sys.path.insert(0, str((ROOT / GEOMETRY).parent))
    import geometry

    return geometry


def binary_coordinates(labels):
    require(0 < len(labels) <= 120, "bounded label inventory")
    require(len(set(labels)) == len(labels), "duplicate label")
    require(all(type(x) is int and 0 < x < 512 for x in labels), "nine-bit labels")
    coordinates = {0: 0}
    basis = []
    for label in labels:
        if label not in coordinates:
            index = len(basis)
            basis.append(label)
            coordinates.update(
                {x ^ label: c | (1 << index) for x, c in tuple(coordinates.items())}
            )
    return tuple(coordinates[x] for x in labels), len(basis)


def five_flat_masks(labels):
    coordinates, dimension = binary_coordinates(labels)
    require(dimension in (7, 8), "expected seven/eight-dimensional fiber")
    kernels = tuple(
        sum(1 << i for i, x in enumerate(coordinates) if not (x & h).bit_count() % 2)
        for h in range(1 << dimension)
    )
    masks = []
    for pivots in combinations(range(dimension), dimension - 5):
        choices = []
        for pivot in pivots:
            free = tuple(c for c in range(pivot) if c not in pivots)
            choices.append(
                tuple(
                    kernels[
                        (1 << pivot)
                        | sum(((n >> i) & 1) << c for i, c in enumerate(free))
                    ]
                    for n in range(1 << len(free))
                )
            )
        for selected in product(*choices):
            mask = (1 << len(labels)) - 1
            for kernel in selected:
                mask &= kernel
            masks.append(mask)
    require(len(masks) == {7: 2667, 8: 97155}[dimension], "incomplete flat census")
    return masks


def puncture_check(tight, removed):
    require(len(tight) == 120 and len(set(tight)) == 120, "tight-set inventory")
    require(type(removed) is int and 0 <= removed < (1 << 33), "puncture range")
    require(removed.bit_count() == 4, "four-root puncture")
    survivors = tuple(mask for mask in tight if not mask & removed)
    require(len(survivors) == 12, "punctured tight-set count")
    intersections = Counter((a & b).bit_count() for a, b in combinations(survivors, 2))
    require(intersections == {2: 12, 4: 24, 8: 30}, "disjoint punctured tight sets")
    return survivors


def inspect_axis(geometry, roots, labels, indices):
    require(len(indices) == 33, "axis fiber size")
    masks = five_flat_masks(tuple(labels[i] for i in indices))
    histogram = Counter(mask.bit_count() for mask in masks)
    tight = tuple(mask for mask in masks if mask.bit_count() == 12)
    require(max(histogram) == 12 and len(tight) == 120, "axis rank-five capacity")
    gram = tuple(
        tuple(geometry.dot(roots[i], roots[j]) for j in indices) for i in indices
    )
    punctures = []
    for chosen in combinations(range(33), 4):
        if all(gram[i][j] == 0 for i, j in combinations(chosen, 2)):
            removed = sum(1 << i for i in chosen)
            puncture_check(tight, removed)
            punctures.append(removed)
    require(len(punctures) == 120, "orthogonal four-root puncture inventory")
    disjoint = sum(not (a & b) for a, b in combinations(tight, 2))
    require(disjoint == 240, "unpunctured positive control")
    return {
        "five_spaces": len(masks),
        "capacity_histogram": dict(sorted(histogram.items())),
        "tight_sets": len(tight),
        "orthogonal_punctures": len(punctures),
        "survivors_per_puncture": 12,
        "minimum_survivor_intersection": 2,
        "unpunctured_disjoint_pairs": disjoint,
        "tight_masks_sha256": sha256(repr(sorted(tight)).encode()).hexdigest(),
        "punctures_sha256": sha256(repr(sorted(punctures)).encode()).hexdigest(),
    }


def inspect_parabolics(geometry, roots, coordinates):
    six = []
    for omitted in combinations(range(8), 2):
        subsystem = tuple(
            root
            for root, c in zip(roots, coordinates, strict=True)
            if all(c[i] == 0 for i in omitted)
        )
        if len(subsystem) >= 30:
            normal = tuple(
                root
                for root in roots
                if all(geometry.dot(root, r) == 0 for r in subsystem)
            )
            require(len(normal) == {30: 2, 36: 3}[len(subsystem)], "normal root count")
            pairing = abs(geometry.dot(normal[0], normal[1]))
            require(pairing == {30: 0, 36: 4}[len(subsystem)], "normal root type")
            six.append(
                {
                    "omitted": list(omitted),
                    "lines": len(subsystem),
                    "normal_roots": len(normal),
                    "normal_pairing": pairing,
                }
            )
    five_maximum = max(
        sum(all(c[i] == 0 for i in omitted) for c in coordinates)
        for omitted in combinations(range(8), 3)
    )
    require(five_maximum == 20 and len(six) == 2, "parabolic classification")
    return {"five_node_maximum": five_maximum, "qualifying_six_node_faces": six}


def inspect_planes(geometry, roots, points):
    histogram = Counter()
    minimum_planes = 0
    for a, b in combinations(roots, 2):
        if geometry.dot(a, b):
            continue
        union = sum(bool(geometry.dot(a, r) or geometry.dot(b, r)) for r in points)
        histogram[union] += 1
        if union == 82:
            types = Counter(
                (bool(geometry.dot(a, r)), bool(geometry.dot(b, r)))
                for r in geometry.frame_lines()
            )
            require(types == {(True, False): 4, (False, True): 4}, "frame puncture")
            minimum_planes += 1
    require(histogram == {82: 448, 84: 2688, 85: 448, 86: 168, 88: 28}, "D6 unions")
    return {
        "orthogonal_pairs": sum(histogram.values()),
        "live_union_histogram": dict(sorted(histogram.items())),
        "minimum_planes_with_four_plus_four_axis_puncture": minimum_planes,
    }


def inspect_weyl_orbit(geometry, roots, labels):
    permutations = []
    for j, simple in enumerate(geometry.SIMPLE):
        permutation = []
        parity = sum(
            ((geometry.dot(s, simple) // 4) % 2) << (i + 1)
            for i, s in enumerate(geometry.SIMPLE)
        )
        for root, label in zip(roots, labels, strict=True):
            scale = geometry.dot(root, simple) // 4
            image = geometry.canonical(
                tuple(x - scale * y for x, y in zip(root, simple, strict=True))
            )
            index = roots.index(image)
            transformed = label ^ (((label & parity).bit_count() % 2) << (j + 1))
            require(labels[index] == transformed, "reflection label linearity")
            permutation.append(index)
        require(len(set(permutation)) == 120, "reflection permutation")
        permutations.append(tuple(permutation))
    start = (
        0,
        next(i for i, root in enumerate(roots) if not geometry.dot(roots[0], root)),
    )
    orbit = {start}
    queue = [start]
    for cursor in range(3780):
        require(cursor < len(queue), "incomplete orthogonal-pair orbit")
        a, b = queue[cursor]
        for permutation in permutations:
            image = tuple(sorted((permutation[a], permutation[b])))
            if image not in orbit:
                require(len(queue) < 3780, "orthogonal-pair orbit capacity")
                orbit.add(image)
                queue.append(image)
    require(len(orbit) == len(queue) == 3780, "orthogonal-pair orbit size")
    return {"orbit_size": len(orbit), "reflection_label_checks": 960}


def compute():
    geometry = authenticate()
    roots, points, _, coordinates = geometry.root_data()
    labels = tuple(
        1 | sum((int(x) % 2) << (i + 1) for i, x in enumerate(c)) for c in coordinates
    )
    a = roots[0]
    b = next(root for root in roots if geometry.dot(a, root) == 0)
    axes = []
    for x, y in ((a, b), (b, a)):
        indices = tuple(
            i
            for i, root in enumerate(roots)
            if geometry.dot(x, root) and not geometry.dot(y, root)
        )
        axes.append(inspect_axis(geometry, roots, labels, indices))
    small = []
    for sign in (-1, 1):
        fiber = tuple(
            labels[i]
            for i, root in enumerate(roots)
            if geometry.dot(a, root) == sign * geometry.dot(b, root) != 0
        )
        require(len(fiber) == 12, "diagonal fiber size")
        small.append(Counter(mask.bit_count() for mask in five_flat_masks(fiber)))
    require(all(max(histogram) == 8 for histogram in small), "small fiber capacity")
    require(2 * (78 - 46) == 64 > 63, "A2 incidence contradiction")
    require(82 - 46 == 3 * 12, "D6 equality budget")
    return {
        "claim": "three-rank5-common-support46-intersection-at-most-one",
        "parabolics": inspect_parabolics(geometry, roots, coordinates),
        "planes": inspect_planes(geometry, roots, points),
        "axes": axes,
        "weyl": inspect_weyl_orbit(geometry, roots, labels),
        "small_fiber_five_spaces_each": 2667,
        "small_fiber_capacity_each": 8,
        "a2_required_twice_union": 64,
        "a2_incidence_budget": 63,
        "d6_required_residual_union": 36,
        "scope": "sufficient threshold; characteristic zero; sharpness unproved",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.loads(json.dumps(compute()))
    if args.output:
        require(
            not args.output.resolve().is_relative_to(ROOT), "external output required"
        )
        with args.output.open("x") as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(
            result == json.loads((PACKAGE / "RESULT.json").read_text()),
            "receipt differs",
        )
    print("PASS_P112_RANK5_SUPPORT46 axes=2 flats=194310 punctures=240 pairs=3780")


if __name__ == "__main__":
    main()
