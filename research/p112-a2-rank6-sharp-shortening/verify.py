"""Exact premises and witness for sharp rank-six P112 shortening. Apache-2.0."""

import argparse
import importlib.util
import json
from collections import Counter, deque
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
GEOMETRY = "research/p112-root-simplex-exclusion/geometry.py"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def source_geometry():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    for row in sources["files"]:
        if row["usage"] == "input":
            require(
                sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"],
                "live source differs from its pin",
            )
    spec = importlib.util.spec_from_file_location(
        "p112_pinned_geometry", ROOT / GEOMETRY
    )
    require(spec is not None and spec.loader is not None, "geometry loader unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def binary_basis(values, bits=9):
    require(
        0 < bits <= 18
        and len(values) <= 512
        and all(type(x) is int and 0 <= x < (1 << bits) for x in values),
        "expected at most 512 bounded binary vectors",
    )
    basis = []
    for original in values:
        value = original
        for row in basis:
            value = min(value, value ^ row)
        if value:
            basis = sorted(
                [min(row, row ^ value) for row in basis] + [value], reverse=True
            )
    return tuple(basis)


def coordinate_map(basis):
    require(len(basis) <= 9, "binary span exceeds ambient dimension")
    coordinates = {0: 0}
    for i, row in enumerate(basis):
        coordinates.update(
            {value ^ row: code | (1 << i) for value, code in tuple(coordinates.items())}
        )
    require(len(coordinates) == 1 << len(basis), "dependent binary basis")
    return coordinates


def singleton_classes(geometry, roots, labels, a, b):
    require(geometry.dot(a, b) == 4, "simplex roots must have inner product four")
    classes = [[], [], []]
    distinct = []
    for root, label in zip(roots, labels, strict=True):
        values = (0, geometry.dot(a, root), geometry.dot(b, root))
        if len(set(values)) == 3:
            distinct.append(label)
        for i in range(3):
            j, k = (x for x in range(3) if x != i)
            if values[j] == values[k] != values[i]:
                classes[i].append(label)
    require(list(map(len, classes)) == [27, 27, 27], "singleton class sizes changed")
    require(len(distinct) == 3, "three-distinct class changed")
    return tuple(tuple(row) for row in classes), tuple(distinct)


def class_receipt(labels, all_labels):
    basis = binary_basis(labels)
    require(len(labels) == 27 and len(basis) == 7, "expected a rank-seven class")
    coordinates = coordinate_map(basis)
    histogram = Counter()
    maximizing = []
    for functional in range(1, 128):
        space = {
            value
            for value, code in coordinates.items()
            if not (functional & code).bit_count() % 2
        }
        total = sum(label in space for label in all_labels)
        singletons = sum(label in space for label in labels)
        histogram[total, singletons] += 1
        if total + singletons == 32:
            maximizing.append(sorted(set(labels) & space))
    require(
        dict(histogram)
        == {(0, 0): 1, (12, 11): 27, (12, 12): 36, (16, 15): 36, (16, 16): 27},
        "joint hyperplane inventory changed",
    )
    five_max = 0
    five_count = 0
    for a, b in combinations(range(1, 128), 2):
        if not a < b < (a ^ b):
            continue
        count = sum(
            not (a & coordinates[label]).bit_count() % 2
            and not (b & coordinates[label]).bit_count() % 2
            for label in labels
        )
        five_max = max(five_max, count)
        five_count += 1
    require((five_count, five_max) == (2667, 10), "rank-five class capacity changed")
    return {
        "hyperplanes": 127,
        "joint_total_singleton_histogram": {
            f"{total},{singletons}": n
            for (total, singletons), n in sorted(histogram.items())
        },
        "five_spaces": five_count,
        "rank_five_singleton_maximum": five_max,
        "support_plus_singleton_maximum": 32,
        "maximizing_sets_sha256": sha256(
            json.dumps(sorted(maximizing), separators=(",", ":")).encode()
        ).hexdigest(),
    }


def reflection_permutations(geometry, roots, all_labels):
    index = {root: i for i, root in enumerate(roots)}
    require(len(binary_basis(all_labels)) == 9, "labels must span the ambient space")
    permutations = []
    label_index = dict(zip(roots, all_labels, strict=True))
    for simple in geometry.SIMPLE:
        permutation = []
        pairs = []
        for root in roots:
            reflected = geometry.canonical(
                tuple(
                    x - (geometry.dot(root, simple) // 4) * y
                    for x, y in zip(root, simple, strict=True)
                )
            )
            permutation.append(index[reflected])
            pairs.append(label_index[reflected] | (label_index[root] << 9))
        require(len(binary_basis(pairs, 18)) == 9, "reflection label map is not linear")
        require(len(set(permutation)) == 120, "reflection is not invertible")
        permutations.append(permutation)
    return permutations


def plane_receipt(geometry, roots, points, all_labels):
    index = {root: i for i, root in enumerate(roots)}
    planes = set()
    for i, j in combinations(range(120), 2):
        dot = geometry.dot(roots[i], roots[j])
        if abs(dot) == 4:
            third = geometry.canonical(
                tuple(
                    x - (dot // 4) * y for x, y in zip(roots[i], roots[j], strict=True)
                )
            )
            planes.add(tuple(sorted((i, j, index[third]))))
    require(len(planes) == 1120, "A2 plane count changed")
    permutations = reflection_permutations(geometry, roots, all_labels)
    seen = {min(planes)}
    queue = deque(seen)
    for _ in range(1120):
        require(bool(queue), "reflection orbit ended early")
        plane = queue.popleft()
        for permutation in permutations:
            image = tuple(sorted(permutation[i] for i in plane))
            require(image in planes, "reflection left A2 inventory")
            if image not in seen:
                seen.add(image)
                queue.append(image)
    require(not queue and seen == planes, "A2 transitivity failed")
    unions = Counter(
        sum(any(geometry.dot(roots[i], p) for i in plane) for p in points)
        for plane in planes
    )
    require(dict(unions) == {78: 896, 80: 224}, "A2 punctured union spectrum changed")
    return {"planes": 1120, "reflection_maps": 8, "union_histogram": dict(unions)}


def rational_rank(rows):
    require(
        0 < len(rows) <= 112
        and 0 < len(rows[0]) <= 11
        and all(len(row) == len(rows[0]) for row in rows),
        "rational matrix exceeds witness bounds",
    )
    matrix = [list(map(Fraction, row)) for row in rows]
    rank = 0
    for col in range(len(matrix[0])):
        pivot = next((i for i in range(rank, len(matrix)) if matrix[i][col]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        scale = matrix[rank][col]
        matrix[rank] = [x / scale for x in matrix[rank]]
        for i in range(rank + 1, len(matrix)):
            scale = matrix[i][col]
            matrix[i] = [
                x - scale * y for x, y in zip(matrix[i], matrix[rank], strict=True)
            ]
        rank += 1
    return rank


def validate_witness(geometry, points, live_labels, witness):
    cut = witness["common_cut_indices"]
    supports = witness["piece_support_indices"]
    coefficients = witness["piece_coefficients"]
    require(
        len(cut) == len(set(cut)) == 30 and all(0 <= i < 112 for i in cut),
        "witness must delete exactly thirty distinct live indices",
    )
    require(len(supports) == len(coefficients) == 3, "witness needs three pieces")
    pieces = []
    for support, values in zip(supports, coefficients, strict=True):
        require(
            len(support) == len(values) == len(set(support)) == 16
            and all(0 <= t < 112 and t not in cut for t in support)
            and all(type(x) is int and x != 0 for x in values),
            "malformed witness piece",
        )
        require(
            len(binary_basis(tuple(live_labels[t] for t in support))) == 6,
            "witness piece binary rank differs from six",
        )
        pieces.append(dict(zip(support, values, strict=True)))
    require(len(set().union(*map(set, supports))) == 48, "pieces are not disjoint")
    a, b = witness["directions"]
    rows = []
    for t in range(112):
        if t not in cut:
            q = [piece.get(t, 0) for piece in pieces]
            require(
                q[1] - q[0] == geometry.dot(a, points[t])
                and q[2] - q[0] == geometry.dot(b, points[t]),
                "witness code identity failed",
            )
            rows.append(list(points[t]) + q)
    ranks = [
        rational_rank([r[:8] for r in rows]),
        rational_rank([r[8:] for r in rows]),
        rational_rank(rows),
    ]
    require(ranks == [8, 3, 9], "witness intersection rank calculation failed")
    return {
        "rational_ranks_code_pieces_join": ranks,
        "intersection_dimension": 2,
        "piece_binary_ranks": [6, 6, 6],
    }


def witness_receipt(geometry, roots, points, live_labels, all_labels):
    a = (0, 0, 0, 0, 0, 2, -2, 0)
    b = (0, 0, 0, -2, 0, 2, 0, 0)
    classes, _ = singleton_classes(geometry, roots, all_labels, a, b)
    selected = []
    for labels in classes:
        candidates = []
        for functional in range(1, 512):
            support = tuple(
                label for label in labels if not (label & functional).bit_count() % 2
            )
            if len(support) == 16 and set(support) <= set(live_labels):
                candidates.append(support)
        require(bool(candidates), "no unpunctured sixteen-singleton witness")
        selected.append(min(candidates))
    union = {
        i for i, p in enumerate(points) if geometry.dot(a, p) or geometry.dot(b, p)
    }
    supports = [
        tuple(i for i, label in enumerate(live_labels) if label in row)
        for row in selected
    ]
    cut = tuple(sorted(union - set().union(*map(set, supports))))
    coefficients = []
    for i, support in enumerate(supports):
        values = []
        for t in support:
            aa, bb = geometry.dot(a, points[t]), geometry.dot(b, points[t])
            values.append(-aa if i == 0 else (aa if i == 1 else bb))
        coefficients.append(values)
    witness = {
        "directions": [a, b],
        "common_cut_indices": cut,
        "piece_support_indices": supports,
        "piece_coefficients": coefficients,
        "code_difference_coefficients": [[-1, 1, 0], [-1, 0, 1]],
    }
    witness.update(validate_witness(geometry, points, live_labels, witness))
    return witness


def compute():
    geometry = source_geometry()
    roots, points, live_labels, coordinates = geometry.root_data()
    all_labels = tuple(
        1 | sum((int(x) % 2) << (i + 1) for i, x in enumerate(row))
        for row in coordinates
    )
    chamber = geometry.chamber_receipt(roots, points, coordinates)
    roots_plane = geometry.root_plane_receipt(roots)
    a, b = (2, 2, 0, 0, 0, 0, 0, 0), (2, 0, 2, 0, 0, 0, 0, 0)
    classes, _ = singleton_classes(geometry, roots, all_labels, a, b)
    return {
        "claim": "sharp-three-rank6-common-support29-intersection-at-most-one",
        "scope": "fixed P112; characteristic zero; arbitrary residual coefficients",
        "class_receipts": [class_receipt(c, all_labels) for c in classes],
        "six_flat_capacity": geometry.flat_capacity(live_labels, 6),
        "chamber": chamber,
        "root_planes": roots_plane,
        "a2_planes": plane_receipt(geometry, roots, points, all_labels),
        "support29": {"required_twice_union": 98, "allowed": 96},
        "support30_counting_boundary": {"required_twice_union": 96, "allowed": 96},
        "witness30": witness_receipt(geometry, roots, points, live_labels, all_labels),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, help="write computed receipt to this path"
    )
    args = parser.parse_args()
    result = json.loads(json.dumps(compute()))
    if args.output:
        require(
            not args.output.resolve().is_relative_to(ROOT), "external output required"
        )
        encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
        with args.output.open("x", encoding="utf-8") as stream:
            require(stream.write(encoded) == len(encoded), "short receipt write")
    else:
        expected = json.loads((PACKAGE / "RESULT.json").read_text())
        require(result == expected, "committed result differs from exact replay")
    print(
        "PASS_P112_RANK6_SHARP_SHORTENING support29=98>96 witness30=48 "
        "binary_ranks=6,6,6 intersection=2"
    )


if __name__ == "__main__":
    main()
