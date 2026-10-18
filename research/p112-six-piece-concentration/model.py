"""Exact finite D6 concentration certificates. Nick Petalas, Apache-2.0."""

import hashlib
import json
import sys
from itertools import combinations, product
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "research/p112-root-simplex-exclusion/geometry.py"
SOURCE_HASH = "b8ac379e41f5ad83bdb6c7f7c55129fc3d9c07801ea61591478f25d72ff0b021"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    require(len(pairs) == len({key for key, _ in pairs}), "duplicate JSON key")
    return dict(pairs)


def read_json(path):
    require(
        path.is_file() and not path.is_symlink() and path.stat().st_size <= 262144,
        "bounded regular JSON input",
    )
    return json.loads(path.read_bytes(), object_pairs_hook=unique_object)


def geometry():
    require(
        SOURCE.is_file()
        and not SOURCE.is_symlink()
        and SOURCE.stat().st_size <= 262144,
        "bounded regular geometry",
    )
    require(
        hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_HASH,
        "geometry source hash",
    )
    sys.path.insert(0, str(SOURCE.parent))
    import geometry as g

    roots, points, _, coordinates = g.root_data()
    labels = tuple(
        1 | sum((int(x) % 2) << (j + 1) for j, x in enumerate(row))
        for row in coordinates
    )
    require(len(set(labels)) == 120, "full root-label inventory")
    return g, roots, points, labels, coordinates


def basis(values, width=9):
    pivots = [0] * width
    for original in values:
        value = original
        for bit in range(width - 1, -1, -1):
            if value >> bit & 1:
                if pivots[bit]:
                    value ^= pivots[bit]
                else:
                    pivots[bit] = value
                    for lower in range(bit):
                        if pivots[bit] >> lower & 1:
                            pivots[bit] ^= pivots[lower]
                    for higher in range(bit + 1, width):
                        if pivots[higher] >> bit & 1:
                            pivots[higher] ^= pivots[bit]
                    break
    return tuple(value for value in pivots if value)


def span(rows):
    values = [0]
    for row in rows:
        values += [value ^ row for value in values]
    return values


def flat_masks(labels, ambient, dimension):
    n = len(ambient)
    require(
        n <= 8 and dimension in (5, 6) and dimension <= n, "flat enumeration dimensions"
    )
    coordinates = {value: i for i, value in enumerate(span(ambient))}
    inside = [
        (i, coordinates[label])
        for i, label in enumerate(labels)
        if label in coordinates
    ]
    kernels = tuple(
        sum(1 << i for i, x in inside if not (x & h).bit_count() % 2)
        for h in range(1 << n)
    )
    for pivots in combinations(range(n), n - dimension):
        choices = []
        for pivot in pivots:
            free = [j for j in range(pivot) if j not in pivots]
            choices.append(
                [
                    (1 << pivot)
                    | sum(((code >> k) & 1) << j for k, j in enumerate(free))
                    for code in range(1 << len(free))
                ]
            )
        for rows in product(*choices):
            mask = kernels[0]
            for row in rows:
                mask &= kernels[row]
            yield mask


def digest_masks(masks):
    return hashlib.sha256(
        b"".join(mask.to_bytes(15, "big") for mask in sorted(masks))
    ).hexdigest()


def check_concentration(mask, axis_mask, labels, dimension):
    require(mask & ~axis_mask == 0, "concentrated span escapes its axis")
    selected = [label for i, label in enumerate(labels) if mask >> i & 1]
    require(len(basis(selected)) == dimension, "critical intersection does not span")


def axis_certificate(labels, axis):
    ambient = basis([labels[i] for i in axis])
    require(len(axis) == 33 and len(ambient) == 8, "full D6 axis")
    axis_mask = sum(1 << i for i in axis)
    result = []
    for dimension, threshold, expected in [(5, 10, 97155), (6, 18, 10795)]:
        critical = set()
        histogram = {}
        count = 0
        for mask in flat_masks(labels, ambient, dimension):
            count += 1
            size = (mask & axis_mask).bit_count()
            if size >= threshold:
                check_concentration(mask, axis_mask, labels, dimension)
                histogram[str(size)] = histogram.get(str(size), 0) + 1
                critical.add(mask)
        require(count == expected, "incomplete full-axis space enumeration")
        require(
            histogram == ({"10": 512, "12": 120} if dimension == 5 else {"20": 16}),
            "critical concentration histogram",
        )
        result.append(
            {
                "dimension": dimension,
                "threshold": threshold,
                "spaces": count,
                "critical_histogram": histogram,
                "critical_sha256": digest_masks(critical),
            }
        )
    return result


def canonical_fibers(g, roots):
    a = (0, 0, 0, 0, 0, 2, -2, 0)
    b = (0, 2, -2, 0, 0, 0, 0, 0)
    fibers = {}
    for i, root in enumerate(roots):
        x, y = g.dot(a, root), g.dot(b, root)
        if x or y:
            divisor = gcd(x, y)
            key = (x // divisor, y // divisor)
            key = max(key, tuple(-value for value in key))
            fibers.setdefault(key, []).append(i)
    require(sorted(map(len, fibers.values())) == [12, 12, 33, 33], "full D6 fibers")
    return a, b, fibers


def small_fiber_certificate(labels, fiber):
    ambient = basis([labels[i] for i in fiber])
    require(len(ambient) == 7 and len(fiber) == 12, "small D6 fiber span")
    mask = sum(1 << i for i in fiber)
    counts = [(space & mask).bit_count() for space in flat_masks(labels, ambient, 5)]
    require(len(counts) == 2667 and max(counts) == 8, "small-fiber rank-five capacity")
    return {"spaces": len(counts), "maximum": max(counts)}


def reflection_orbit(g, roots, labels, coordinates, initial):
    index = {root: i for i, root in enumerate(roots)}
    permutations = []
    for k, simple in enumerate(g.SIMPLE):
        permutation = []
        coefficients = [g.dot(other, simple) // 4 for other in g.SIMPLE]
        for i, root in enumerate(roots):
            multiple = g.dot(root, simple) // 4
            image = g.canonical(
                tuple(x - multiple * y for x, y in zip(root, simple, strict=True))
            )
            j = index[image]
            parity = (
                sum(
                    int(x) * y
                    for x, y in zip(coordinates[i], coefficients, strict=True)
                )
                % 2
            )
            require(
                labels[j] == labels[i] ^ (parity << (k + 1)), "Weyl label linearity"
            )
            permutation.append(j)
        require(len(set(permutation)) == 120, "reflection permutation")
        permutations.append(permutation)
    expected = {
        pair
        for pair in combinations(range(120), 2)
        if not g.dot(roots[pair[0]], roots[pair[1]])
    }
    start = tuple(sorted(index[root] for root in initial))
    queue, seen = [start], {start}
    for position in range(3780):
        require(position < len(queue), "orthogonal pair orbit ended early")
        pair = queue[position]
        for permutation in permutations:
            image = tuple(sorted(permutation[i] for i in pair))
            if image not in seen:
                seen.add(image)
                queue.append(image)
    require(seen == expected and len(queue) == 3780, "orthogonal root-pair transport")
    return {"root_label_checks": 960, "transported_pairs": len(queue)}


def normal_faces(g, roots, coordinates):
    five = [
        sum(all(row[i] == 0 for i in omitted) for row in coordinates)
        for omitted in combinations(range(8), 3)
    ]
    qualifying = []
    for omitted in combinations(range(8), 2):
        face = [
            root
            for root, row in zip(roots, coordinates, strict=True)
            if all(row[i] == 0 for i in omitted)
        ]
        if len(face) >= 28:
            normal = [root for root in roots if all(g.dot(root, t) == 0 for t in face)]
            require((len(face), len(normal)) in [(30, 2), (36, 3)], "normal-plane type")
            require(
                abs(g.dot(normal[0], normal[1])) == (0 if len(face) == 30 else 4),
                "orthogonal/A2 normal basis",
            )
            qualifying.append(
                {
                    "omitted": list(omitted),
                    "lines": len(face),
                    "normal_roots": len(normal),
                }
            )
    require(len(five) == 56 and max(five) == 20, "rank-at-most-five parabolic cap")
    return {
        "five_node_faces": len(five),
        "maximum_five_node_lines": max(five),
        "qualifying_six_node_faces": qualifying,
    }


def plane_inventory(g, roots, points):
    histogram = {}
    relevant = {}
    for a, b in combinations(roots, 2):
        if g.dot(a, b):
            continue
        fibers = {}
        for root in points:
            x, y = g.dot(a, root), g.dot(b, root)
            if x or y:
                divisor = gcd(x, y)
                key = (x // divisor, y // divisor)
                key = max(key, tuple(-value for value in key))
                fibers[key] = fibers.get(key, 0) + 1
        live = sum(fibers.values())
        histogram[str(live)] = histogram.get(str(live), 0) + 1
        if live <= 84:
            sizes = sorted(fibers.values())
            require(
                sizes == ([12, 12, 29, 29] if live == 82 else [11, 11, 31, 31]),
                "actual small-fiber coverage",
            )
            relevant[str(live)] = sizes
    require(
        histogram == {"82": 448, "84": 2688, "85": 448, "86": 168, "88": 28},
        "D6 live-union inventory",
    )
    return {"histogram": histogram, "relevant_live_fibers": relevant}


def incidence_certificate(capacities=(8, 12, 12, 12, 20, 20)):
    require(
        len(capacities) == 6 and all(type(x) is int and x > 0 for x in capacities),
        "six capacity bounds",
    )
    budget = sum(capacities)
    excess = budget - 82
    singleton = [capacity - excess for capacity in capacities]
    require(
        budget <= 84 and min(singleton[1:4]) >= 10 and min(singleton[4:]) >= 18,
        "D6 concentration allowance",
    )
    e6_allowance = 16 + 3 * 22 + 2 * 32
    require(
        e6_allowance < 2 * 78 and capacities[0] < 22, "complete six-piece contradiction"
    )
    return {
        "capacities": list(capacities),
        "support_budget": budget,
        "maximum_D6_excess": excess,
        "singleton_lower_bounds": singleton,
        "minimum_D6_small_fiber_union": 22,
        "only_remaining_piece_capacity": capacities[0],
        "E6_joint_allowance": e6_allowance,
        "E6_required_incidence": 156,
        "deleted_pieces": 4,
        "retained_code_dimension": 2,
        "excluded_profile": [4, 5, 5, 5, 6, 6, 6, 6, 6, 6],
    }


def result():
    g, roots, points, labels, coordinates = geometry()
    a, b, fibers = canonical_fibers(g, roots)
    axes = [
        axis_certificate(labels, value) for value in fibers.values() if len(value) == 33
    ]
    small = [
        small_fiber_certificate(labels, value)
        for value in fibers.values()
        if len(value) == 12
    ]
    return {
        "schema": "p112-six-piece-concentration/v1",
        "geometry_sha256": SOURCE_HASH,
        "axes": axes,
        "small_fibers": small,
        "transport": reflection_orbit(g, roots, labels, coordinates, (a, b)),
        "normalization": normal_faces(g, roots, coordinates),
        "planes": plane_inventory(g, roots, points),
        "incidence": incidence_certificate(),
    }
