"""Mixed-rank P112 support38 boundary. Nick Petalas. Apache-2.0."""

import argparse
import hashlib
import importlib.util
import json
from collections import Counter
from itertools import combinations
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
GEOMETRY = "research/p112-root-simplex-exclusion/geometry.py"
INPUTS = {
    GEOMETRY,
    "research/p112-root-simplex-exclusion/PROOF.md",
    "research/p112-root-simplex-exclusion/RESULT.json",
}
RETAINED = {
    f"vendor/pr{pr}-{name}"
    for pr in (3260, 3262)
    for name in ("PROOF.md", "RESULT.json")
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_bytes(path, limit=1_000_000):
    require(path.is_file() and not path.is_symlink(), "missing or linked file")
    require(path.stat().st_size <= limit, "file size limit")
    return path.read_bytes()


def authenticate(package=PACKAGE, root=ROOT):
    source = json.loads(read_bytes(package / "SOURCES.json"))
    require(
        set(source) == {"schema_version", "base_commit", "files", "retained_files"},
        "source inventory fields",
    )
    rows, retained = source["files"], source["retained_files"]
    require(type(rows) is list and len(rows) == 5, "source inventory length")
    require(type(retained) is list and len(retained) == 4, "retained inventory length")
    live = [r for r in rows if r["usage"] == "input"]
    require(
        len(live) == 3 and {r["path"] for r in live} == INPUTS, "live source inventory"
    )
    require({r["local_path"] for r in retained} == RETAINED, "retained path inventory")
    for row in live + retained:
        path = root / row["path"] if "path" in row else package / row["local_path"]
        raw = read_bytes(path)
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "source SHA256")
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require(blob == row["git_blob"], "source Git blob")
    return source


def geometry():
    authenticate()
    spec = importlib.util.spec_from_file_location("p112_authenticated", ROOT / GEOMETRY)
    require(spec is not None and spec.loader is not None, "geometry loader")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def basis(values, bits=9):
    require(len(values) <= 512 and 1 <= bits <= 18, "binary capacity")
    require(all(type(v) is int and 0 <= v < 1 << bits for v in values), "binary input")
    rows = []
    for value in values:
        for row in rows:
            value = min(value, value ^ row)
        if value:
            rows = sorted(
                [min(row, row ^ value) for row in rows] + [value], reverse=True
            )
    return tuple(rows)


def coordinates(values):
    rows = basis(values)
    result = {0: 0}
    for i, row in enumerate(rows):
        result.update({v ^ row: c | (1 << i) for v, c in tuple(result.items())})
    require(len(result) == 1 << len(rows), "independent binary coordinates")
    return rows, result


def rank6_capacity(values):
    """Every six-space in an eight-space, via its unique dual two-space."""
    require(len(values) == len(set(values)) == 29, "live D6 axis size")
    rows, codes = coordinates(values)
    require(len(rows) == 8, "live D6 axis rank")
    masks = [
        sum(1 << i for i, v in enumerate(values) if not (codes[v] & f).bit_count() % 2)
        for f in range(256)
    ]
    counts = Counter(
        (masks[f] & masks[h]).bit_count()
        for f, h in combinations(range(1, 256), 2)
        if h < (f ^ h)
    )
    require(sum(counts.values()) == 10795, "complete dual two-space census")
    require(max(counts) == 18, "live D6 rank-six capacity")
    return counts


def d6_receipt(g, roots, points, labels):
    gram = [[g.dot(a, b) for b in roots] for a in roots]
    live_indices = [roots.index(p) for p in points]
    unions, capacities = Counter(), Counter()
    records = []
    for a, b in combinations(range(120), 2):
        if gram[a][b]:
            continue
        union = sum(bool(gram[a][t] or gram[b][t]) for t in live_indices)
        unions[union] += 1
        if union != 82:
            continue
        for x, y in ((a, b), (b, a)):
            values = tuple(
                label
                for t, label in zip(live_indices, labels, strict=True)
                if gram[x][t] and not gram[y][t]
            )
            counts = rank6_capacity(values)
            capacities[max(counts)] += 1
            records.append([a, b, x, sorted(counts.items())])
    require(
        dict(unions) == {82: 448, 84: 2688, 85: 448, 86: 168, 88: 28},
        "orthogonal-pair puncture spectrum",
    )
    require(dict(capacities) == {18: 896}, "minimum-plane axis coverage")
    return {
        "orthogonal_planes": sum(unions.values()),
        "union_histogram": dict(unions),
        "live_axis_fibers": 896,
        "six_spaces_per_fiber": 10795,
        "axis_maximum_histogram": dict(capacities),
        "full_census_sha256": hashlib.sha256(
            json.dumps(records, separators=(",", ":")).encode()
        ).hexdigest(),
    }


def a2_fiber(values, all_labels):
    require(len(values) == 27, "A2 fiber size")
    rows, codes = coordinates(values)
    require(len(rows) == 7, "A2 fiber rank")
    five = Counter()
    for f, h in combinations(range(1, 128), 2):
        if h < (f ^ h):
            five[
                sum(
                    not (codes[v] & f).bit_count() % 2
                    and not (codes[v] & h).bit_count() % 2
                    for v in values
                )
            ] += 1
    require(sum(five.values()) == 2667 and max(five) == 10, "A2 rank-five capacity")
    joint = Counter()
    for f in range(1, 128):
        space = {v for v, c in codes.items() if not (c & f).bit_count() % 2}
        joint[sum(v in space for v in all_labels), sum(v in space for v in values)] += 1
    require(
        dict(joint)
        == {(0, 0): 1, (12, 11): 27, (12, 12): 36, (16, 15): 36, (16, 16): 27},
        "A2 joint inventory",
    )
    return {
        "five_spaces": sum(five.values()),
        "five_fiber_maximum": max(five),
        "hyperplanes": sum(joint.values()),
        "joint_maximum": max(sum(k) for k in joint),
    }


def a2_receipt(g, roots, points, full_labels):
    index = {r: i for i, r in enumerate(roots)}
    planes = set()
    for i, j in combinations(range(120), 2):
        d = g.dot(roots[i], roots[j])
        if abs(d) == 4:
            third = g.canonical(
                tuple(a - d // 4 * b for a, b in zip(roots[i], roots[j], strict=True))
            )
            planes.add(tuple(sorted((i, j, index[third]))))
    require(len(planes) == 1120, "A2 plane inventory")
    permutations = []
    for simple in g.SIMPLE:
        perm = [
            index[
                g.canonical(
                    tuple(
                        x - g.dot(r, simple) // 4 * y
                        for x, y in zip(r, simple, strict=True)
                    )
                )
            ]
            for r in roots
        ]
        pairs = [full_labels[i] | full_labels[perm[i]] << 9 for i in range(120)]
        require(
            len(set(perm)) == 120 and len(basis(pairs, 18)) == 9,
            "reflection is an invertible label map",
        )
        permutations.append(perm)
    orbit, queue = {min(planes)}, [min(planes)]
    for cursor in range(1120):
        require(cursor < len(queue), "A2 orbit ended early")
        for perm in permutations:
            image = tuple(sorted(perm[i] for i in queue[cursor]))
            require(image in planes, "reflection left A2 planes")
            if image not in orbit:
                orbit.add(image)
                queue.append(image)
    require(orbit == planes and len(queue) == 1120, "A2 transitivity")
    unions = Counter(
        sum(any(g.dot(roots[i], p) for i in plane) for p in points) for plane in planes
    )
    require(dict(unions) == {78: 896, 80: 224}, "A2 punctured unions")
    a, b = (roots[i] for i in min(planes)[:2])
    if g.dot(a, b) == -4:
        b = tuple(-x for x in b)
    classes = [[] for _ in range(3)]
    for r, label in zip(roots, full_labels, strict=True):
        values = (0, g.dot(a, r), g.dot(b, r))
        for i in range(3):
            other = [j for j in range(3) if j != i]
            if values[other[0]] == values[other[1]] != values[i]:
                classes[i].append(label)
    return {
        "planes": 1120,
        "union_histogram": dict(unions),
        "reflection_maps": 8,
        "fibers": [a2_fiber(v, full_labels) for v in classes],
    }


def chamber_receipt(g, roots, points, coordinates_):
    result = g.chamber_receipt(roots, points, coordinates_)
    lower_max = max(
        sum(all(c[i] == 0 for i in omitted) for c in coordinates_)
        for omitted in combinations(range(8), 3)
    )
    require(lower_max == 20, "rank-five parabolic bound")
    large = []
    for omitted in combinations(range(8), 2):
        count = sum(all(c[i] == 0 for i in omitted) for c in coordinates_)
        if count >= 30:
            normals = [
                r
                for r in roots
                if all(
                    g.dot(r, s) == 0 for i, s in enumerate(g.SIMPLE) if i not in omitted
                )
            ]
            require(len(normals) in (2, 3), "normal root-plane inventory")
            kind = "D6" if count == 30 else "E6"
            require(
                (kind, omitted) in (("D6", (0, 7)), ("E6", (6, 7))),
                "rank-six classification changed",
            )
            require(
                g.dot(normals[0], normals[1]) == 0 if kind == "D6" else True,
                "D6 normal roots must be orthogonal",
            )
            large.append({"omitted": omitted, "root_lines": count, "kind": kind})
    require(len(large) == 2, "large parabolic coverage")
    return {
        "large_parabolics": large,
        "rank_five_maximum": lower_max,
        "chamber": result,
    }


def receipt():
    g = geometry()
    roots, points, labels, coordinates_ = g.root_data()
    full_labels = tuple(
        1 | sum((int(x) % 2) << (i + 1) for i, x in enumerate(c)) for c in coordinates_
    )
    result = {
        "status": "PASS_MIXED_P112_SUPPORT38",
        "common_support": 38,
        "endpoint_ranks": [5, 5, 6],
        "intersection_upper_bound": 1,
        "chamber": chamber_receipt(g, roots, points, coordinates_),
        "A2": a2_receipt(g, roots, points, full_labels),
        "D6": d6_receipt(g, roots, points, labels),
        "budgets": {
            "E6_required": 80,
            "E6_allowance": 76,
            "D6_required": 44,
            "D6_total_support": 44,
            "D6_rank6_required": 20,
            "D6_fiber_maximum": 18,
        },
    }
    budgets = result["budgets"]
    require(budgets["E6_required"] > budgets["E6_allowance"], "E6 contradiction")
    require(
        budgets["D6_required"] == budgets["D6_total_support"]
        and budgets["D6_fiber_maximum"] < budgets["D6_rank6_required"],
        "D6 equality contradiction",
    )
    return json.loads(json.dumps(result))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = receipt()
    if args.output:
        with args.output.open("x") as f:
            json.dump(result, f, indent=2, sort_keys=True)
            f.write("\n")
    else:
        require(
            result == json.loads(read_bytes(PACKAGE / "RESULT.json")), "receipt changed"
        )
    print(result["status"], "planes=3780 live_fibers=896 rank6_cap=18 no_new_kappa")


if __name__ == "__main__":
    main()
