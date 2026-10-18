"""Analytic A2 rank-six capacity: exact finite model binding. Apache-2.0."""

import argparse
import json
import runpy
from collections import Counter
from hashlib import sha1, sha256
from itertools import combinations
from math import gcd
from pathlib import Path
from types import SimpleNamespace

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
GEOMETRY = "research/p112-root-simplex-exclusion/geometry.py"
PINNED_MANIFEST_SHA256 = (
    "68678a55f20ff8abbd9d04fac280b2dded4e7a8100e76604ea04a5e901616d5e"
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_bytes(path):
    require(path.is_file() and not path.is_symlink(), "missing or linked input")
    require(path.stat().st_size <= 100_000, "input byte bound")
    return path.read_bytes()


def digests(raw):
    return {
        "sha256": sha256(raw).hexdigest(),
        "git_blob": sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest(),
    }


def authenticate(root=ROOT, package=PACKAGE, manifest=None):
    sources = (
        json.loads(read_bytes(package / "SOURCES.json"))
        if manifest is None
        else manifest
    )
    require(
        sha256(json.dumps(sources, sort_keys=True).encode()).hexdigest()
        == PINNED_MANIFEST_SHA256,
        "source inventory, schema, usage or pin changed",
    )
    for row in sources["files"]:
        if row["usage"] == "input":
            actual = digests(read_bytes(root / row["path"]))
            require(all(actual[k] == row[k] for k in actual), "live input hash")
    for row in sources["retained_files"]:
        actual = digests(read_bytes(package / row["local_path"]))
        require(all(actual[k] == row[k] for k in actual), "retained source hash")
    return read_bytes(root / GEOMETRY)


def geometry():
    authenticate()
    # run_path reads the authenticated .py directly, without import cache lookup.
    return SimpleNamespace(**runpy.run_path(str(ROOT / GEOMETRY)))


def basis(values):
    require(
        len(values) <= 512 and all(type(x) is int and 0 <= x < 512 for x in values),
        "binary input",
    )
    rows = []
    for value in values:
        for row in rows:
            value = min(value, value ^ row)
        if value:
            rows = sorted(rows + [value], reverse=True)
    return tuple(rows)


def span(rows):
    require(
        len(rows) <= 9 and len(basis(rows)) == len(rows), "independent bounded basis"
    )
    values = [0]
    for row in rows:
        values += [x ^ row for x in values]
    require(len(set(values)) == 1 << len(rows), "span size")
    return tuple(sorted(values))


def quadratic(simple):
    edges = [
        (i, j)
        for i, j in combinations(range(8), 2)
        if sum(a * b for a, b in zip(simple[i], simple[j], strict=True)) // 4 % 2
    ]
    return tuple(
        (x.bit_count() + sum((x >> i & 1) * (x >> j & 1) for i, j in edges)) % 2
        for x in range(256)
    )


def polar_rank(vectors, q):
    rows = [
        sum((q[x ^ y] ^ q[x] ^ q[y]) << i for i, y in enumerate(vectors))
        for x in vectors
    ]
    return len(basis(rows))


def projective(x, y):
    d = gcd(x, y)
    return max((x // d, y // d), (-x // d, -y // d)) if d else (0, 0)


def fibers(roots, labels, dot):
    result, planes = set(), set()
    index = {r: i for i, r in enumerate(roots)}
    for i, j in combinations(range(120), 2):
        pairing = dot(roots[i], roots[j])
        if abs(pairing) != 4:
            continue
        third = tuple(
            a - pairing // 4 * b for a, b in zip(roots[i], roots[j], strict=True)
        )
        third = max(third, tuple(-x for x in third))
        plane = tuple(sorted((i, j, index[third])))
        if plane in planes:
            continue
        planes.add(plane)
        groups = {}
        for root, label in zip(roots, labels, strict=True):
            key = projective(dot(roots[i], root), dot(roots[j], root))
            groups.setdefault(key, []).append(label)
        require(
            sorted(map(len, groups.values())) == [1, 1, 1, 27, 27, 27, 36], "A2 fibers"
        )
        result.update(tuple(sorted(g)) for g in groups.values() if len(g) == 27)
    require(len(planes) == 1120 and len(result) == 3360, "complete A2 inventory")
    return tuple(sorted(result))


def fiber_model(fiber, roots, q):
    rows = basis(fiber)
    require(len(rows) == 7, "fiber rank")
    space = span(rows)
    affine = tuple(x >> 1 for x in space if x & 1)
    origin = affine[0]
    direction = basis(tuple(x ^ origin for x in affine))
    missing = tuple(sorted((set(space) & set(roots)) - set(fiber)))
    require(len(affine) == 64 and len(direction) == 6, "affine six-section")
    require(polar_rank(direction, q) == 6, "nondegenerate affine polar form")
    require(sum(1 - 2 * q[x] for x in affine) == 8, "positive affine Gauss sum")
    require(len(missing) == 1, "fiber missing root")
    return rows, missing[0]


def hyperplanes(rows, roots, fiber, live):
    coordinates = {0: 0}
    for i, row in enumerate(rows):
        coordinates.update(
            {x ^ row: c | (1 << i) for x, c in tuple(coordinates.items())}
        )
    histogram, equality = Counter(), []
    for functional in range(1, 128):
        selected = tuple(
            sorted(
                x
                for x, c in coordinates.items()
                if not (c & functional).bit_count() % 2 and x in roots
            )
        )
        singletons = len(set(selected) & set(fiber))
        histogram[len(selected), singletons] += 1
        if len(selected) + singletons == 32:
            equality.append(selected)
    require(
        dict(histogram)
        == {(0, 0): 1, (12, 11): 27, (12, 12): 36, (16, 15): 36, (16, 16): 27},
        "canonical hyperplanes",
    )
    witness = next((x for x in equality if set(x) <= set(live)), equality[0])
    require(len(basis(witness)) == 6, "witness support rank")
    return {
        "histogram": {f"{m},{j}": n for (m, j), n in sorted(histogram.items())},
        "equality_spaces": len(equality),
        "witness_labels": list(witness),
        "witness_all_live": set(witness) <= set(live),
    }


def receipt():
    g = geometry()
    roots, points, live, coordinates = g.root_data()
    labels = tuple(
        1 | sum((int(c) % 2) << (i + 1) for i, c in enumerate(row))
        for row in coordinates
    )
    q = quadratic(g.SIMPLE)
    require(
        {x >> 1 for x in labels} == {x for x in range(256) if q[x]},
        "norm-mod2 root binding",
    )
    require(
        polar_rank(tuple(1 << i for i in range(8)), q) == 8
        and sum(1 - 2 * x for x in q) == 16,
        "positive ambient model",
    )
    inventory = fibers(roots, labels, g.dot)
    models = [fiber_model(a, labels, q) for a in inventory]
    canonical = inventory[0]
    return {
        "claim": "analytic A2 rank6 joint32; outside span(A) <=30; equality classification",
        "root_labels_sha256": sha256(json.dumps(labels).encode()).hexdigest(),
        "full_roots": len(roots),
        "live_roots": len(points),
        "large_fibers": len(inventory),
        "all_fibers_positive_nondegenerate_affine6": True,
        "canonical_fiber": list(canonical),
        "canonical_missing_root": models[0][1],
        "canonical": hyperplanes(models[0][0], labels, canonical, live),
        "analytic_bounds": {
            "global_rank6": 20,
            "inside_rank6": 32,
            "outside_rank6": 30,
            "fiber_rank5": 10,
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write", action="store_true", help="write the initial receipt explicitly"
    )
    args = parser.parse_args()
    result = receipt()
    path = PACKAGE / "RESULT.json"
    if args.write:
        require(not path.exists(), "refuse receipt overwrite")
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(result == json.loads(read_bytes(path)), "receipt differs")
    print("PASS_E8_A2_ANALYTIC_RANK6")


if __name__ == "__main__":
    main()
