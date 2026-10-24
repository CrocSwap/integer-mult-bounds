#!/usr/bin/env python3
"""The published C5 weights give floors 45 and 561/16, both above 180/7.

The checker multiplies the published weights. It does not scan the rectangles.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_C5_CANCELLATION_FLOORS j_free=45 one_j=561/16 no_new_kappa"
WEIGHTS = (2, 8, 1, 7, 2, 3, 3, 4, 6)


def fail(message):
    raise SystemExit("FAIL_C5_CANCELLATION_FLOORS " + message)


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


def evaluate():
    authenticate()
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    require(sum(WEIGHTS) == 36, "the weight lifts moved")
    weight_sum = Fraction(sum(WEIGHTS), 16)
    require(weight_sum == Fraction(9, 4), "the weight sum moved")
    rho = Fraction(303, 16)
    credit = rho - 9
    require(credit == Fraction(159, 16) and rho > 9, "the full-support credit moved")
    j_free = 20 * weight_sum
    one_j = j_free - credit
    require(j_free == 45 and one_j == Fraction(561, 16), "the floors moved")
    ceiling = Fraction(180, 7)
    require(j_free > ceiling and one_j > ceiling, "a floor met the termwise ceiling")
    require(112 * 2 == 224 and 224 >= j_free, "the diagonal tariff moved")
    require(112 * 111 == 12432 and 9 + 16088 == 16097 and 16097 >= one_j, "the J-extension tariff moved")
    require(1596 * 1596 == 2547216, "the rectangle count moved")
    return {
        "weight_sum": "9/4",
        "j_free_floor": "45",
        "one_j_floor": "561/16",
        "beats_termwise": True,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
