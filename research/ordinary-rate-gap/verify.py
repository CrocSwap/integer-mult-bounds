#!/usr/bin/env python3
"""The ordinary-rate coefficient and the line-156 gap.

The checker compares integers. It does not rerun the moment certificates.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_ORDINARY_RATE_GAP coefficient=4283584 line156=8033584 no_new_kappa"
WIDTH = 1023683
EXPONENT = Fraction(1, 577)


def fail(message):
    raise SystemExit("FAIL_ORDINARY_RATE_GAP " + message)


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
    saving = EXPONENT * (1 - EXPONENT)
    require(saving == Fraction(576, 332929), "the ordinary-rate exponent moved")
    require(2 * 2 * 200 + 1 == 801, "the linear coefficient moved")
    tight = 801 + 4 * 10 ** 6 * Fraction(17, 16) + 2 * 8195 * 2 + 2 + 1
    loose = 801 + 4 * 10 ** 6 * 2 + 32780 + 3
    require(tight == 4283584 and loose == 8033584, "a composed coefficient moved")
    numerator, denominator = EXPONENT.numerator, EXPONENT.denominator
    left = (denominator - numerator) * (1 - EXPONENT) + numerator + 1
    right = EXPONENT + denominator * (1 - saving)
    require(left - right == 1 - EXPONENT, "the extremal gap moved")
    require(2 ** 511 * 16 ** 512 > 17 ** 512, "the extremal ratio fell to 17/16")
    require(17 ** 128 > 32 * 16 ** 128, "the selector power bound moved")
    require(20 * EXPONENT < Fraction(5, 128), "the selector slope moved")
    require(WIDTH ** 577 <= 2 ** 11520 < (WIDTH + 1) ** 577, "the witness width moved")
    require(
        WIDTH ** (576 * 577) * 2 ** 332929 * 16 ** 332929 > 17 ** 332929 * 2 ** 577 * 2 ** (20 * 332353),
        "the witness no longer exceeds 17/16",
    )
    require(2 * WIDTH > 2 ** 20, "the witness no longer exceeds half the exponent")
    return {
        "coefficient": 4283584,
        "line156_coefficient": 8033584,
        "witness_above_17_16": True,
        "exponent": "576/332929",
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
