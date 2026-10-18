"""Literal five-line counterexample to extending the P112 Lemma N allowance."""

import hashlib
import json
import sys
from itertools import combinations
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
GEOMETRY = ROOT / "research/p112-simplex-coordinate-bound/vendor/geometry.py"
GEOMETRY_SHA = "b8ac379e41f5ad83bdb6c7f7c55129fc3d9c07801ea61591478f25d72ff0b021"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def geometry():
    require(
        hashlib.sha256(GEOMETRY.read_bytes()).hexdigest() == GEOMETRY_SHA,
        "geometry source changed",
    )
    sys.path.insert(0, str(GEOMETRY.parent))
    try:
        import geometry as module
    finally:
        sys.path.pop(0)
    return module


def binary_rank(columns):
    require(
        len(columns) <= 112 and all(type(x) is int and 0 < x < 512 for x in columns),
        "nine-bit column bounds",
    )
    basis = [0] * 9
    for value in columns:
        for pivot in reversed(range(9)):
            if value >> pivot & 1:
                if basis[pivot]:
                    value ^= basis[pivot]
                else:
                    basis[pivot] = value
                    break
    return sum(value != 0 for value in basis)


def flat_mask(labels, annihilator):
    require(
        len(annihilator) == 2 and binary_rank(annihilator) == 2,
        "flat annihilator must have rank two",
    )
    return sum(
        1 << i
        for i, label in enumerate(labels)
        if all((a & label).bit_count() % 2 == 0 for a in annihilator)
    )


def seven_flat_masks(labels):
    full = (1 << 112) - 1
    kernels = tuple(
        full
        ^ sum(1 << i for i, label in enumerate(labels) if (a & label).bit_count() % 2)
        for a in range(512)
    )
    masks = tuple(
        kernels[a] & kernels[b]
        for a, b in combinations(range(1, 512), 2)
        if b < (a ^ b)
    )
    require(len(masks) == 43435, "incomplete seven-flat enumeration")
    return masks


def determinant3(matrix):
    require(
        len(matrix) == 3 and all(len(row) == 3 for row in matrix),
        "three-dimensional Gram matrix",
    )
    a, b, c = matrix
    return (
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - a[1] * (b[0] * c[2] - b[2] * c[0])
        + a[2] * (b[0] * c[1] - b[1] * c[0])
    )


def check_direction(entry, roots, points, labels, first, all_flats):
    h = tuple(entry["h"])
    require(
        len(h) == 8 and all(type(x) is int for x in h) and h in roots,
        "direction must be a normalized root",
    )
    second = flat_mask(labels, entry["second_flat_annihilator"])
    off = sum(
        1 << i
        for i, r in enumerate(points)
        if sum(x * y for x, y in zip(h, r, strict=True))
    )
    deleted = entry["deleted_lines"]
    require(
        len(deleted) == len(set(deleted)) == 5
        and all(type(i) is int and 0 <= i < 112 for i in deleted),
        "five distinct live deletion indices required",
    )
    deletion_mask = sum(1 << i for i in deleted)
    require(off & ~(first | second) == deletion_mask, "incorrect deletion set")
    residual = off & ~first & ~deletion_mask
    rank = binary_rank(
        tuple(label for i, label in enumerate(labels) if residual >> i & 1)
    )
    require(rank == 7, "residual rank is not seven")
    completions = tuple(
        mask for mask in all_flats if (off & ~(first | mask)).bit_count() <= 5
    )
    require(completions == (second,), "completion is not unique within five cuts")
    return {
        "direction": h,
        "support": off.bit_count(),
        "residual_rank": rank,
        "minimum_deletions": 5,
        "qualifying_second_flats": len(completions),
    }


def check_witness(witness, roots, points, labels):
    require(
        witness["schema_version"] == 1 and len(witness["directions"]) == 3,
        "witness schema",
    )
    first = flat_mask(labels, witness["first_flat_annihilator"])
    all_flats = seven_flat_masks(labels)
    rows, cuts = [], set()
    for entry in witness["directions"]:
        rows.append(check_direction(entry, roots, points, labels, first, all_flats))
        cuts.update(entry["deleted_lines"])
    hs = [row["direction"] for row in rows]
    gram = [[sum(x * y for x, y in zip(a, b, strict=True)) for b in hs] for a in hs]
    determinant = determinant3(gram)
    require(determinant == 256, "three directions are not the independent witness")
    require(cuts == set(range(8)), "the deletion union must have eight lines")
    return {
        "status": "PASS_P112_FIVE_LINE_BOUNDARY",
        "gram": gram,
        "gram_determinant": determinant,
        "directions": rows,
        "seven_flats_checked_per_direction": len(all_flats),
        "common_union_size": len(cuts),
        "common_union_binary_rank": binary_rank(tuple(labels[i] for i in sorted(cuts))),
        "new_historical_profiles": 0,
        "selected_frontier_changed": False,
    }


def run():
    g = geometry()
    roots, points, labels, _ = g.root_data()
    witness = json.loads((PACKAGE / "WITNESS.json").read_text())
    result = check_witness(witness, roots, points, labels)
    expected = json.loads((PACKAGE / "RESULT.json").read_text())
    require(json.loads(json.dumps(result)) == expected, "committed result differs")
    return result


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
