"""Exact alpha74 deletion-quantifier witness. Nick Petalas, Apache-2.0."""

import hashlib
import json
import runpy
from collections import Counter
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
MANIFEST_HASHES = {
    "SOURCES.json": "fa15f5bb7d2cbce142800f0d239a5bca8cab7e85cdd35a5c5f5e99e342c0755b",
    "PREDECESSORS.json": (
        "769bc633b1558b6297744108c71baf83ab65467474e02986b2a035bca57b5e1b"
    ),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_bytes(path):
    with path.open("rb") as stream:
        data = stream.read(100_001)
    require(len(data) <= 100_000, "input size")
    return data


def read_json(path):
    return json.loads(read_bytes(path))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def authenticate(root=ROOT):
    package = root / "research/p112-alpha74-cut-quantifiers"
    rows = []
    for name, expected in MANIFEST_HASHES.items():
        data = read_bytes(package / name)
        require(hashlib.sha256(data).hexdigest() == expected, "manifest pin")
        manifest = json.loads(data)
        require(type(manifest["schema_version"]) is int, "manifest schema type")
        require(manifest["schema_version"] == 1, "manifest version")
        rows.extend(row for row in manifest["files"] if row["usage"] == "input")
    require(len(rows) == 4, "fixed live source inventory")
    for row in rows:
        data = read_bytes(root / row["path"])
        require(hashlib.sha256(data).hexdigest() == row["sha256"], "source SHA256")
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        require(hashlib.sha1(blob).hexdigest() == row["git_blob"], "source Git blob")
    return root / "research/p112-root-simplex-exclusion/geometry.py"


def geometry(root=ROOT):
    # This fixed authenticated .py source is compiled without a .pyc import.
    module = runpy.run_path(str(authenticate(root)))
    return module["root_data"]()[1:3]


def binary_basis(values):
    basis = {}
    for value in values:
        for bit in range(8, -1, -1):
            if value & (1 << bit):
                if bit in basis:
                    value ^= basis[bit]
                else:
                    basis[bit] = value
                    break
    return basis


def in_span(value, basis):
    for bit in range(8, -1, -1):
        if value & (1 << bit):
            if bit not in basis:
                return False
            value ^= basis[bit]
    return True


def dot(left, right):
    return sum(x * y for x, y in zip(left, right, strict=True))


def indices(values, length):
    require(type(values) is list and len(values) == length, "index list length")
    require(all(type(t) is int and 0 <= t < 112 for t in values), "root index")
    require(len(set(values)) == length, "duplicate root index")


def validate_witness(witness):
    require(type(witness["schema_version"]) is int, "witness schema type")
    require(witness["schema_version"] == 1, "witness version")
    indices(witness["U_roots"], 32)
    indices(witness["V_roots"], 8)
    directions, cuts = witness["directions"], witness["individual_cuts"]
    require(type(directions) is list and len(directions) == 8, "eight directions")
    require(type(cuts) is list and len(cuts) == 8, "eight cuts")
    for direction, cut in zip(directions, cuts, strict=True):
        require(type(direction) is list and len(direction) == 8, "direction shape")
        require(all(type(x) is int and -4 <= x <= 4 for x in direction), "direction")
        indices(cut, 1)


def flat(labels, roots, dimension):
    basis = binary_basis(labels[t] for t in roots)
    require(len(basis) == dimension, "cover binary dimension")
    closure = [t for t, label in enumerate(labels) if in_span(label, basis)]
    require(closure == sorted(roots), "cover is not its full root closure")


def direction_row(points, labels, covered, direction, cut):
    own = cut[0]
    require(tuple(direction) == points[own], "cut is not the direction root")
    off = [t for t, point in enumerate(points) if dot(direction, point)]
    outside = [t for t in off if t not in covered]
    require(len(binary_basis(labels[t] for t in outside)) == 8, "uncut rank eight")
    retained = [t for t in outside if t != own]
    require(len(binary_basis(labels[t] for t in retained)) == 7, "individual cut rank")
    small, spectrum = set(), Counter()
    for functional in range(512):
        support = tuple(t for t in outside if (functional & labels[t]).bit_count() & 1)
        spectrum[len(support)] += 1
        if 0 < len(support) <= 2:
            small.add(support)
    require(small == {(own,)}, "other small binary cocircuit")
    return {
        "root": own,
        "off": len(off),
        "outside": len(outside),
        "uncut_rank": 8,
        "individual_cut_rank": 7,
        "small_functional_supports": [list(s) for s in sorted(small)],
        "functional_weight_spectrum": dict(sorted(spectrum.items())),
    }


def certificate(witness, root=ROOT):
    validate_witness(witness)
    points, labels = geometry(root)
    flat(labels, witness["U_roots"], 7)
    flat(labels, witness["V_roots"], 4)
    directions = witness["directions"]
    require(
        all(
            dot(a, b) == 8 * (i == j)
            for i, a in enumerate(directions)
            for j, b in enumerate(directions)
        ),
        "orthogonal direction basis",
    )
    covered = set(witness["U_roots"]) | set(witness["V_roots"])
    rows = [
        direction_row(points, labels, covered, h, cut)
        for h, cut in zip(directions, witness["individual_cuts"], strict=True)
    ]
    require(len({row["root"] for row in rows}) == 8, "distinct indispensable roots")
    return {
        "schema_version": 1,
        "status": "PASS_ALPHA74_DELETION_QUANTIFIERS",
        "cover_dimensions": [7, 4],
        "cover_root_counts": [32, 8],
        "direction_dependent_one_cut_span": 8,
        "common_two_cut_max_on_these_eight": 2,
        "directions": rows,
        "universal_common_two_cut_question_settled": False,
        "caller_exclusion_claimed": False,
        "new_kappa_claimed": False,
    }


def main():
    result = certificate(read_json(PACKAGE / "WITNESS.json"))
    require(
        canonical(result) == canonical(read_json(PACKAGE / "RESULT.json")),
        "computed result differs from receipt",
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
