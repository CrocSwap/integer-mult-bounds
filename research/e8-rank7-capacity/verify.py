"""Exact affine-six E8 support certificate. Apache-2.0, Nick Petalas."""

import argparse
import ast
import json
import stat
from collections import Counter
from fractions import Fraction
from hashlib import sha1, sha256
from itertools import combinations, product
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
GEOMETRY = "research/p112-root-simplex-exclusion/geometry.py"
PIN = "b8ac379e41f5ad83bdb6c7f7c55129fc3d9c07801ea61591478f25d72ff0b021"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_regular(path, limit=200_000):
    info = path.lstat()
    require(stat.S_ISREG(info.st_mode) and info.st_size <= limit, "source boundary")
    return path.read_bytes()


def authenticate(root=ROOT, manifest=None):
    pins = (
        json.loads(read_regular(PACKAGE / "SOURCES.json"))
        if manifest is None
        else manifest
    )
    require(type(pins) is dict, "source manifest object")
    require(
        type(pins.get("schema_version")) is int and pins["schema_version"] == 1,
        "source schema must be integer one",
    )
    require(set(pins) == {"schema_version", "base_commit", "files"}, "source fields")
    require(
        pins["base_commit"] == "463113d675af7410ac91d53a4fed51ec6494eb9a",
        "exact historical base",
    )
    rows = pins["files"]
    expected = {
        (GEOMETRY, "input"),
        ("certificates/selected-result.json", "provenance"),
        ("docs/research/agent-task-catalog.json", "provenance"),
    }
    require(type(rows) is list and len(rows) == 3, "source row count")
    for row in rows:
        require(
            type(row) is dict and set(row) == {"path", "usage", "git_blob", "sha256"},
            "source row fields",
        )
        require(all(type(row[k]) is str for k in row), "source row types")
        for key, size in (("git_blob", 40), ("sha256", 64)):
            require(
                len(row[key]) == size and set(row[key]) <= set("0123456789abcdef"),
                "source digest type",
            )
    require({(r["path"], r["usage"]) for r in rows} == expected, "source inventory")
    pin = next(r for r in rows if r["usage"] == "input")
    raw = read_regular(root / GEOMETRY)
    blob = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    require(
        sha256(raw).hexdigest() == pin["sha256"] == PIN and blob == pin["git_blob"],
        "geometry pin mismatch",
    )
    return raw


def source_basis():
    tree = ast.parse(authenticate())
    nodes = [
        node.value
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "SIMPLE" for t in node.targets)
    ]
    require(len(nodes) == 1, "unique source basis")
    simple = ast.literal_eval(nodes[0])
    require(
        type(simple) is tuple
        and len(simple) == 8
        and all(
            type(row) is tuple
            and len(row) == 8
            and all(type(x) is int and -2 <= x <= 2 for x in row)
            for row in simple
        ),
        "bounded source basis",
    )
    return simple


def root_residues(simple):
    # Reconstruct the canonical root/frame formula; retain its source credit.
    roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-2, 2):
            row = tuple(2 if k == i else sign if k == j else 0 for k in range(8))
            roots.add(max(row, tuple(-x for x in row)))
    for row in product((-1, 1), repeat=8):
        if sum(x == -1 for x in row) % 2 == 0:
            roots.add(max(row, tuple(-x for x in row)))
    frame = {
        tuple(2 if k == i else sign if k == i + 1 else 0 for k in range(8))
        for i in range(0, 8, 2)
        for sign in (-2, 2)
    }
    residues, live = set(), set()
    for root in roots:
        coordinates = solve(simple, root)
        residue = sum((x % 2) << i for i, x in enumerate(coordinates))
        residues.add(residue)
        if root not in frame:
            live.add(residue)
    require(
        len(roots) == len(residues) == 120 and len(live) == 112, "root/frame inventory"
    )
    return residues, frozenset(live)


def solve(simple, root):
    rows = [
        [Fraction(simple[j][i]) for j in range(8)] + [Fraction(root[i])]
        for i in range(8)
    ]
    for j in range(8):
        pivot = next(i for i in range(j, 8) if rows[i][j])
        rows[pivot], rows[j] = rows[j], rows[pivot]
        scale = rows[j][j]
        rows[j] = [x / scale for x in rows[j]]
        for i in range(8):
            if i != j:
                scale = rows[i][j]
                rows[i] = [x - scale * y for x, y in zip(rows[i], rows[j], strict=True)]
    require(all(row[8].denominator == 1 for row in rows), "integral root coordinates")
    return tuple(int(row[8]) for row in rows)


def model():
    simple = source_basis()
    residues, live = root_residues(simple)
    gram = [
        [sum(x * y for x, y in zip(a, b, strict=True)) // 4 for b in simple]
        for a in simple
    ]
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
        set(residues) == {x for x in range(256) if q[x]} and len(set(residues)) == 120,
        "root-residue quadratic bijection",
    )
    polar = tuple(
        sum((q[1 << i] ^ q[1 << j] ^ q[(1 << i) ^ (1 << j)]) << j for j in range(8))
        for i in range(8)
    )
    require(binary_rank(polar) == 8 and sum(q) == 120, "plus-type nondegenerate model")
    for x in range(256):
        for y in range(256):
            b = sum((polar[i] & y).bit_count() for i in range(8) if x >> i & 1) % 2
            require(q[x ^ y] == q[x] ^ q[y] ^ b, "polarization")
    return q, live, polar


def binary_rank(values):
    require(
        len(values) <= 256 and all(type(x) is int and 0 <= x < 512 for x in values),
        "bounded binary vectors",
    )
    basis = [0] * 9
    for original in values:
        value = original
        for bit in range(8, -1, -1):
            if value >> bit & 1:
                if basis[bit]:
                    value ^= basis[bit]
                else:
                    basis[bit] = value
                    break
    return sum(bool(x) for x in basis)


def equality_kind(q, a, b, section):
    """A nonsingular perpendicular plane has one negative-Gauss-sum coset."""
    require(q[a ^ b] ^ q[a] ^ q[b] == 1, "equality needs a nonsingular plane")
    plane = (0, a, b, a ^ b)
    sign = sum(1 - 2 * q[x] for x in plane)
    special = [x for x in plane if (1 - 2 * q[x]) * sign == -2]
    require(len(special) == 1, "unique extremal projection")
    z = special[0]
    require(
        section == (q[a ^ z] ^ q[a] ^ q[z]) + 2 * (q[b ^ z] ^ q[b] ^ q[z]),
        "wrong extremal coset",
    )


def summarize(histogram, equalities, witness):
    require(sum(histogram.values()) == 43180, "all affine six-spaces")
    require(
        len(equalities) == len(set(equalities)) == 5440, "complete equality inventory"
    )
    require(
        all(len(support) == 36 for support in equalities), "full equality support size"
    )
    serial = json.dumps(sorted(equalities), separators=(",", ":")).encode()
    return {
        "schema": "e8-rank7-capacity/v1",
        "affine_six_spaces": 43180,
        "perpendicular_planes": 10795,
        "full_maximum": 36,
        "P112_maximum": 36,
        "full_equality_spaces": 5440,
        "P112_equality_spaces": 448,
        "full_equality_supports_sha256": sha256(serial).hexdigest(),
        "histogram": [[*key, count] for key, count in sorted(histogram.items())],
        "witness": witness,
    }


def compute():
    q, live, _ = model()
    pairing = lambda x, y: q[x ^ y] ^ q[x] ^ q[y]
    planes = {
        tuple(sorted((a, b, a ^ b))) for a in range(1, 256) for b in range(a + 1, 256)
    }
    require(len(planes) == 10795, "all two-dimensional spaces")
    histogram, equalities, live_equalities = Counter(), [], []
    for plane in sorted(planes):
        a, b, _ = plane
        sections = [[] for _ in range(4)]
        for x in range(256):
            if q[x]:
                sections[pairing(a, x) + 2 * pairing(b, x)].append(x)
        for index, support in enumerate(sections):
            surviving = tuple(x for x in support if x in live)
            histogram[(pairing(a, b), len(support), len(surviving))] += 1
            require(len(support) <= 36, "rank-seven support bound")
            if len(support) == 36:
                equality_kind(q, a, b, index)
                equalities.append(tuple(1 | x << 1 for x in support))
            if len(surviving) == 36:
                live_equalities.append((plane, index, surviving))
    require(len(live_equalities) == 448, "fixed-frame equality count")
    plane, section, surviving = live_equalities[0]
    labels = [1 | x << 1 for x in surviving]
    require(binary_rank(labels) == 7, "attainment rank")
    witness = {
        "perpendicular_plane": plane,
        "section": section,
        "support_labels": labels,
    }
    return summarize(histogram, equalities, witness)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = compute()
    if args.output:
        with args.output.open("x") as output:
            json.dump(result, output, indent=2)
            output.write("\n")
    else:
        expected = json.loads(read_regular(PACKAGE / "RESULT.json"))
        require(
            json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
            "receipt mismatch",
        )
    print("PASS_E8_RANK7 full=36 P112=36 full_equality=5440 P112_equality=448")


if __name__ == "__main__":
    main()
