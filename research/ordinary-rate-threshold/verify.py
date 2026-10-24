#!/usr/bin/env python3
"""The ordinary rate is 575/576^2, and the width bound clears 2^20.

The checker uses exact integers. It does not enclose the moment.
"""

import hashlib
import json
from fractions import Fraction
from math import gcd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_ORDINARY_RATE_THRESHOLD rate=575/331776 below_power=true no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_ORDINARY_RATE_THRESHOLD " + message)


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
    kappa = Fraction(selected["kappa"])
    require(kappa == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    rate = Fraction(1, 576)
    saving = rate * (1 - rate)
    require(saving == Fraction(575, 576 ** 2) == Fraction(575, 331776), "the ordinary rate moved")
    require(saving > kappa, "the ordinary rate fell to the selected kappa")
    divisor = gcd(28416, 28425)
    require(divisor == 3 and 28416 * 28425 // divisor == 269241600, "the stock coefficient moved")
    require(Fraction(17, 10000) < rate < Fraction(1, 512), "the rate left its interval")
    require(2 * 8195 == 16390 and 2 * 16390 == 32780, "the doubled coefficient moved")
    threshold = 32780 * Fraction(17, 16) * 20
    require(threshold == 696575 and threshold < (1 << 20), "the width threshold moved")
    require((1 << 20) * (16 ** 576) < 17 ** 576, "the power comparison moved")
    return {
        "rate": "575/331776",
        "threshold": 696575,
        "above_selected": True,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
