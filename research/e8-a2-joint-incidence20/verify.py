"""Sharp E8 A2 rank-five joint incidence bound. Apache-2.0."""

import argparse
import json
from hashlib import sha1, sha256
from itertools import combinations
from math import gcd
from pathlib import Path
from types import ModuleType

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
GEOMETRY = "research/p112-root-simplex-exclusion/geometry.py"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_bytes(path):
    require(path.is_file() and not path.is_symlink(), "missing or linked input")
    require(path.stat().st_size <= 100_000, "input exceeds byte bound")
    return path.read_bytes()


def authenticate(root=ROOT, manifest=None):
    pins = (
        manifest
        if manifest is not None
        else json.loads(read_bytes(PACKAGE / "SOURCES.json"))
    )
    require(set(pins) == {"schema_version", "base_commit", "files"}, "manifest fields")
    require(pins["schema_version"] == 1, "manifest version")
    require(
        pins["base_commit"] == "463113d675af7410ac91d53a4fed51ec6494eb9a", "base pin"
    )
    rows = pins["files"]
    require(isinstance(rows, list) and len(rows) == 3, "source row count")
    expected = {
        GEOMETRY: "input",
        "docs/research/agent-task-catalog.json": "provenance",
        "certificates/selected-result.json": "provenance",
    }
    for row in rows:
        require(
            isinstance(row, dict)
            and set(row) == {"path", "usage", "git_blob", "sha256"},
            "source row schema",
        )
        require(isinstance(row["path"], str) and row["path"] in expected, "source path")
        require(row["usage"] == expected[row["path"]], "source usage")
        for key, size in (("git_blob", 40), ("sha256", 64)):
            value = row[key]
            require(
                isinstance(value, str)
                and len(value) == size
                and set(value) <= set("0123456789abcdef"),
                "source digest",
            )
    require(len({row["path"] for row in rows}) == 3, "source inventory")
    pin = next(row for row in rows if row["path"] == GEOMETRY)
    raw = read_bytes(root / GEOMETRY)
    blob = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    require(
        sha256(raw).hexdigest() == pin["sha256"] and blob == pin["git_blob"],
        "geometry hash",
    )
    return raw


def geometry():
    raw = authenticate()
    module = ModuleType("authenticated_e8_geometry")
    # Execute these authenticated source bytes, without consulting a pyc file.
    exec(compile(raw, GEOMETRY, "exec"), module.__dict__)
    return module


def basis(values):
    require(
        len(values) <= 512 and all(type(v) is int and 0 <= v < 512 for v in values),
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
    require(len(rows) <= 9 and len(basis(rows)) == len(rows), "independent basis")
    result = [0]
    for row in rows:
        result += [value ^ row for value in result]
    require(len(set(result)) == 1 << len(rows), "span cardinality")
    return tuple(sorted(result))


def projective(x, y):
    divisor = gcd(x, y)
    return (
        max((x // divisor, y // divisor), (-x // divisor, -y // divisor))
        if divisor
        else (0, 0)
    )


def model(g):
    roots, points, labels, coordinates = g.root_data()
    full = tuple(
        1 | sum((int(c) % 2) << (i + 1) for i, c in enumerate(row))
        for row in coordinates
    )
    gram = tuple(tuple(g.dot(x, y) // 4 for y in g.SIMPLE) for x in g.SIMPLE)
    q = tuple(
        (
            x.bit_count()
            + sum(
                gram[i][j]
                for i in range(8)
                for j in range(i + 1, 8)
                if x >> i & 1 and x >> j & 1
            )
        )
        % 2
        for x in range(256)
    )
    require(
        len(set(full)) == 120
        and {v >> 1 for v in full} == {x for x in range(256) if q[x]},
        "root/quadric bijection",
    )
    by_root = dict(zip(roots, full, strict=True))
    require(
        all(by_root[r] == label for r, label in zip(points, labels, strict=True)),
        "live label binding",
    )
    polar = tuple(
        sum((q[(1 << i) ^ (1 << j)] ^ q[1 << i] ^ q[1 << j]) << j for j in range(8))
        for i in range(8)
    )
    require(len(basis(polar)) == 8 and 256 - 2 * sum(q) == 16, "ambient plus form")
    for x in range(256):
        for y in range(256):
            pairing = (
                sum((polar[i] & y).bit_count() for i in range(8) if x >> i & 1) % 2
            )
            require(q[x ^ y] == q[x] ^ q[y] ^ pairing, "polarization")
    return roots, full, q


def all_fibers(g, roots):
    index = {r: i for i, r in enumerate(roots)}
    planes = set()
    for i, j in combinations(range(120), 2):
        pairing = g.dot(roots[i], roots[j])
        if pairing:
            third = g.canonical(
                tuple(
                    a - pairing // 4 * b
                    for a, b in zip(roots[i], roots[j], strict=True)
                )
            )
            require(third in index, "A2 third root")
            planes.add(tuple(sorted((i, j, index[third]))))
    require(len(planes) == 1120, "A2 plane inventory")
    fibers = set()
    for i, j, _ in sorted(planes):
        groups = {}
        for k, root in enumerate(roots):
            key = projective(g.dot(root, roots[i]), g.dot(root, roots[j]))
            groups.setdefault(key, []).append(k)
        require(
            sorted(map(len, groups.values())) == [1, 1, 1, 27, 27, 27, 36],
            "projective fiber inventory",
        )
        for group in groups.values():
            if len(group) == 27:
                fibers.add(tuple(group))
    require(len(fibers) == 3360, "distinct large fibers")
    return tuple(sorted(fibers))


def fiber_signature(A, full, q):
    require(len(A) == len(set(A)) == 27 and set(A) <= set(full), "large fiber input")
    rows = basis(A)
    require(len(rows) == 7, "fiber span dimension")
    W = span(rows)
    H = tuple(value >> 1 for value in W if value & 1)
    require(len(H) == 64, "fiber affine six-space")
    offset = H[0]
    directions = basis([value ^ offset for value in H])
    require(len(directions) == 6, "fiber affine dimension")
    polar = tuple(
        sum((q[x ^ y] ^ q[x] ^ q[y]) << j for j, y in enumerate(directions))
        for x in directions
    )
    require(len(basis(polar)) == 6, "fiber nondegenerate polar form")
    require(sum(1 - 2 * q[x] for x in H) == 8, "fiber positive Gauss sum")
    support = tuple(sorted(set(full).intersection(W)))
    require(
        len(support) == 28 and set(A) <= set(support), "full root closure of fiber span"
    )
    return rows, support


def canonical_census(A, full):
    rows = basis(A)
    encoded = []
    for code in range(128):
        value = 0
        for i in range(7):
            if code >> i & 1:
                value ^= rows[i]
        if value in full:
            encoded.append((code, value))
    histogram, witness = {}, None
    # Unique reverse-echelon bases of every two-dimensional annihilator.
    for p, r in combinations(range(7), 2):
        for left in range(1 << p):
            f = (1 << p) | left
            free = [i for i in range(r) if i != p]
            for code in range(1 << len(free)):
                h = (1 << r) | sum((code >> i & 1) << col for i, col in enumerate(free))
                support = sorted(
                    v
                    for c, v in encoded
                    if not ((c & f).bit_count() % 2 or (c & h).bit_count() % 2)
                )
                pair = (len(support), len(set(support).intersection(A)))
                key = f"{pair[0]},{pair[1]}"
                histogram[key] = histogram.get(key, 0) + 1
                if pair == (10, 10) and witness is None:
                    witness = support
    require(sum(histogram.values()) == 2667, "five-space completeness")
    require(
        witness is not None and len(basis(witness)) == 5, "sharp joint twenty witness"
    )
    return histogram, witness


def compute():
    g = geometry()
    roots, full, q = model(g)
    fibers = all_fibers(g, roots)
    signatures = []
    for fiber in fibers:
        A = tuple(full[i] for i in fiber)
        rows, closure = fiber_signature(A, full, q)
        signatures.append([list(fiber), list(rows), list(closure)])
    first = tuple(full[i] for i in fibers[0])
    histogram, witness = canonical_census(first, full)
    return {
        "schema": "e8-a2-joint-incidence20/v1",
        "ambient_dimension": 8,
        "ambient_Gauss_sum": 16,
        "full_root_labels": 120,
        "live_bindings": 112,
        "polarization_pairs": 65536,
        "A2_planes": 1120,
        "large_fibers": 3360,
        "every_fiber": {
            "linear_span_dimension": 7,
            "full_root_closure": 28,
            "affine_dimension": 6,
            "polar_rank": 6,
            "Gauss_sum": 8,
        },
        "fiber_inventory_sha256": sha256(
            json.dumps(signatures, separators=(",", ":")).encode()
        ).hexdigest(),
        "canonical_fiber_indices": fibers[0],
        "canonical_fiber_labels": sorted(first),
        "canonical_five_space_histogram_full_and_fiber": histogram,
        "attaining_support_labels": witness,
        "attaining_support_rank": 5,
        "upper_bound": 20,
        "old_sufficient_incidence_bound": 21,
        "outside_fiber_span_bounds": {"full": 12, "fiber": 8},
        "inside_fiber_span_bounds": {"full": 10, "fiber": 10},
        "new_shortening_or_supplier_claim": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.loads(json.dumps(compute()))
    if args.output is None:
        require(
            result == json.loads(read_bytes(PACKAGE / "RESULT.json")),
            "receipt mismatch",
        )
    else:
        require(
            not args.output.resolve().is_relative_to(ROOT), "external output required"
        )
        with args.output.open("x", encoding="utf-8") as stream:
            text = json.dumps(result, indent=2, sort_keys=True) + "\n"
            require(stream.write(text) == len(text), "short write")
    print("PASS_E8_A2_JOINT20 full120 rank5 all3360fibers sharp20")


if __name__ == "__main__":
    main()
