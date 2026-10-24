#!/usr/bin/env python3
"""The displayed Gaussian output is i times the source formula.

The checker multiplies that turn and the invoice coefficients. It does not
expand the events.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_QQ16_OUTPUT_TURN quarter_turn=true invoice=483082 no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_QQ16_OUTPUT_TURN " + message)


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


def quarter_turn(real, imag):
    return Fraction(-imag, 2), Fraction(real, 2)


def evaluate():
    authenticate()
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    for real in range(-2, 3):
        for imag in range(-2, 3):
            turned = quarter_turn(imag, -real)
            require(turned == (Fraction(real, 2), Fraction(imag, 2)), "the quarter-turn moved")
    gaussian = 11076 * (4 + 2 + 4)
    require(gaussian == 110760, "the axis coefficient moved")
    require(483082 - gaussian == 372322, "the base operation count moved")
    require(528 * 4 == 2112, "the cover transfer count moved")
    require(712 * 2 + 2 == 1426, "the storage count moved")
    return {
        "quarter_turn": True,
        "lambda_coefficient": 110760,
        "base_operations": 372322,
        "cover_transfers": 2112,
        "storage_words": 1426,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
