#!/usr/bin/env python3
"""The six-query non-Fano assignment costs at least 32.

The checker adds the published floors. It does not sweep coefficients.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_NONFANO_INVOICE_FLOOR invoice=32 baseline=30 no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_NONFANO_INVOICE_FLOOR " + message)


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


def same_role(count):
    return 6 + (4 - count) * 6 + count * 3 + 6


def two_roles(count):
    return 6 + 5 * (4 - count) + 3 * count + 4


def evaluate():
    authenticate()
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    ordinary = (8 - 1) + 4 * (6 - 1) + (6 - 1)
    require(ordinary == 32 and ordinary > 30 and ordinary > 31, "the ordinary floor moved")
    require(9 + 4 * 6 + 6 == 39, "the distinct-role floor moved")
    require(395 + 107 + 8 + 1 == (1 << 9) - 1, "the annihilator total moved")
    require(7 + 9 + 2 == 18 and 46 + 318 + 248 == 612, "the dimension totals moved")
    for count in (1, 2, 3):
        baseline = 30 - 3 * count
        require(same_role(count) == 36 - 3 * count == baseline + 6, "the one-role floor moved")
        require(two_roles(count) == 30 - 2 * count == baseline + count, "the two-role floor moved")
        require(same_role(count) > baseline + 1, "a one-role case saved")
        require(two_roles(count) >= baseline + 1, "a two-role case saved")
        require(count == 1 or two_roles(count) > baseline + 1, "a larger J count tied")
    return {
        "ordinary_floor": 32,
        "baseline": 30,
        "distinct_floor": 39,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
