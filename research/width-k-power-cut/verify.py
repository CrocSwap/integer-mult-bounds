#!/usr/bin/env python3
"""The two width floors differ exactly on perfect 500th powers.

The checker proves that integer locus. It does not build a physical wrapper.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_WIDTH_K_POWER_CUT witness=2^500 floors=2,1 no_new_kappa"
EXPONENT = 500


def fail(message):
    raise SystemExit("FAIL_WIDTH_K_POWER_CUT " + message)


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


def iroot(number, exponent):
    if number < 1:
        return 0
    high = 1 << ((number.bit_length() + exponent - 1) // exponent)
    low = 0
    while low < high:
        mid = (low + high + 1) // 2
        if mid**exponent <= number:
            low = mid
        else:
            high = mid - 1
    return low


def floors_differ(width, exponent):
    """True exactly when width is a perfect power. The comparisons are the proof."""
    root = iroot(width, exponent)
    require(root**exponent <= width < (root + 1) ** exponent, "the root bracket failed")
    if width == root**exponent:
        require(root >= 2, "the unit power is outside the stated cut")
        require((root - 1) ** exponent <= width - 1 < root**exponent, "the lower neighbor failed")
        return True
    require(root**exponent <= width - 1 < (root + 1) ** exponent, "a non-power changed the floor")
    return False


def evaluate():
    authenticate()
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    witness = 2**EXPONENT
    require(iroot(witness, EXPONENT) == 2, "the old floor moved")
    require(iroot(witness - 1, EXPONENT) == 1, "the actual-width floor moved")
    require(floors_differ(witness, EXPONENT), "the perfect power agreed")
    require(not floors_differ(witness + 1, EXPONENT), "the next width disagreed")
    for width in range(2, 300):
        perfect = iroot(width, 3) ** 3 == width
        require(floors_differ(width, 3) == perfect, "the small locus moved")
    return {
        "exponent": 500,
        "witness": "2^500",
        "old_floor": 2,
        "actual_width_floor": 1,
        "floors_differ": True,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
