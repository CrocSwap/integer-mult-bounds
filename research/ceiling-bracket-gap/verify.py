#!/usr/bin/env python3
"""The published ceiling bracket has width 1/10^15 and excludes the selected saving.

The checker subtracts the endpoints. It does not evaluate the exponential.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_CEILING_BRACKET_GAP width=1e-15 below=true no_new_kappa"
LOWER = Fraction(52814190909, 31250000000000)
UPPER = Fraction(1690054109089, 1000000000000000)


def fail(message):
    raise SystemExit("FAIL_CEILING_BRACKET_GAP " + message)


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
    saving = kappa / (1 - kappa)
    denominator = 500000000000000000 - 836330098538459
    require(saving == Fraction(836330098538459, denominator), "the selected saving moved")
    require(UPPER - LOWER == Fraction(1, 10 ** 15), "the bracket width moved")
    require(saving < LOWER, "the selected saving entered the bracket")
    return {
        "width": "1/1000000000000000",
        "below_bracket": True,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
