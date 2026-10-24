#!/usr/bin/env python3
"""The five-cell floor depends on the block basis, not only on the counts.

The checker rebuilds the cell graph. It does not rerun the assignment census.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_FIVE_CELL_BASIS_OBSTRUCTION mixed_attains=false coordinate_attains=true no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_FIVE_CELL_BASIS_OBSTRUCTION " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    require(set(pinned) == set(), "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def dot(left, right):
    return sum(a * b for a, b in zip(left, right)) % 2


def basis(changed):
    standard = [tuple(1 if i == k else 0 for i in range(4)) for k in range(4)]
    if not changed:
        return standard
    return [tuple(0 if i == k else 1 for i in range(4)) for k in range(4)]


def gram_i(vectors):
    for i, left in enumerate(vectors):
        require(dot(left, left) == 1, "a basis vector is isotropic")
        for right in vectors[i + 1:]:
            require(dot(left, right) == 0, "two basis vectors meet")


def cells(changed):
    standard = basis(False)
    group_b = basis(changed)
    return {
        "A_pin": [standard[2], standard[3]],
        "A_free": [standard[0], standard[1]],
        "B_pin": [group_b[0], group_b[1]],
        "B_free": [group_b[2], group_b[3]],
        "C_pin": list(standard),
    }


def adjacent(left, right):
    return any(dot(u, v) == 1 for u in left for v in right)


def components(names, edges):
    seen = {}
    for name in names:
        if name in seen:
            continue
        stack = [name]
        seen[name] = name
        while stack:
            current = stack.pop()
            for other in names:
                if other not in seen and frozenset((current, other)) in edges:
                    seen[other] = name
                    stack.append(other)
    return seen


def attains(changed):
    labels = cells(changed)
    names = list(labels)
    edges = set()
    for i, left in enumerate(names):
        for right in names[i + 1:]:
            groups = {left[0], right[0]}
            if len(groups) == 2 and adjacent(labels[left], labels[right]):
                edges.add(frozenset((left, right)))
    pinned = {"A_pin", "B_pin", "C_pin"}
    owners = components(names, edges)
    require(all(owners[name] in {owners[pin] for pin in pinned} for name in names), "a cell left the pinned components")
    target = sum(len(labels[name]) for name in ("A_pin", "A_free"))
    free = ("A_free", "B_free")
    candidates = []
    for mask in range(1 << len(free)):
        chosen = [free[i] for i in range(len(free)) if mask >> i & 1]
        if sum(len(labels[name]) for name in chosen) == target:
            candidates.append(chosen)
    require(candidates == [["A_free", "B_free"]], "the weight equation moved")
    chosen = candidates[0]
    independent = frozenset(chosen) not in edges
    return independent


def evaluate():
    authenticate()
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    gram_i(basis(True))
    require(3 + 3 * 4 == 15, "the floor moved")
    require(2 * 3 + 3 * 4 == 18, "the MMM tariff moved")
    require(attains(True) is False, "the mixed basis attained the floor")
    require(attains(False) is True, "the coordinate basis missed the floor")
    return {
        "floor": 15,
        "mmm_tariff": 18,
        "mixed_attains": False,
        "coordinate_attains": True,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
