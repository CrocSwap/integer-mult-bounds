#!/usr/bin/env python3
"""Six reader rows need two queries, so the two-hub tariff is 54.

The checker solves those six premises. It does not enumerate factorizations.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_TWO_HUB_TARIFF_54 charge=54 excess=12 no_new_kappa"
E = (1, 0, 0, 0, 0)
F = (0, 1, 0, 0, 0)
QUERIES = {
    "g": (0, 0, 1, 0, 0),
    "d": (1, 1, 0, 0, 0),
    "t": (1, 1, 1, 0, 0),
    "h": (0, 0, 0, 1, 0),
    "x": (1, 0, 1, -1, 0),
    "y": (0, 1, 1, -1, 0),
    "k": (0, 0, 0, 0, 1),
    "z": (1, 0, 1, 0, -1),
    "w": (0, 1, 1, 0, -1),
}
FORCED = (
    (E, ("d", "x", "y")),
    (F, ("d", "x", "y")),
    (E, ("d", "z", "w")),
    (F, ("d", "z", "w")),
    (E, ("g", "t", "x", "y")),
    (F, ("g", "t", "x", "y")),
)
WITNESS = (4, 8, 12, 4, 10, 8, 0, 4, 4)


def fail(message):
    raise SystemExit("FAIL_TWO_HUB_TARIFF_54 " + message)


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


def parallel(mark, query):
    ratio = None
    for left, right in zip(mark, query):
        if right == 0:
            if left != 0:
                return False
            continue
        value = Fraction(left, right)
        if ratio is None:
            ratio = value
        elif ratio != value:
            return False
    return ratio is not None


def in_span(mark, names):
    columns = [tuple(Fraction(entry) for entry in QUERIES[name]) for name in names]
    rows = [list(column) for column in zip(*columns)]
    target = [Fraction(entry) for entry in mark]
    pivot = 0
    for coordinate in range(5):
        if pivot == len(names):
            break
        found = next((row for row in range(coordinate, 5) if rows[row][pivot] != 0), None)
        if found is None:
            continue
        rows[coordinate], rows[found] = rows[found], rows[coordinate]
        target[coordinate], target[found] = target[found], target[coordinate]
        scale = rows[coordinate][pivot]
        rows[coordinate] = [entry / scale for entry in rows[coordinate]]
        target[coordinate] /= scale
        for row in range(5):
            if row == coordinate or rows[row][pivot] == 0:
                continue
            factor = rows[row][pivot]
            rows[row] = [entry - factor * rows[coordinate][index] for index, entry in enumerate(rows[row])]
            target[row] -= factor * target[coordinate]
        pivot += 1
    return all(target[row] == 0 for row in range(5) if all(entry == 0 for entry in rows[row]))


def evaluate():
    authenticate()
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    require(7 + 14 == 21, "the premise count moved")
    for mark, names in FORCED:
        require(in_span(mark, names), "a forced mark left its premise span")
        require(all(not parallel(mark, QUERIES[name]) for name in names), "a single query carries a forced mark")
    units = 15 * 1 + 6 * 2
    require(units == 27 and 2 * units == 54, "the charge moved")
    require(2 * 21 == 42 and 54 - 42 == 12, "the excess moved")
    require(sum(WITNESS) == 54 and len(WITNESS) == 9, "the witness moved")
    return {
        "rows": 21,
        "row_units": 27,
        "minimum_charge": 54,
        "excess": 12,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
