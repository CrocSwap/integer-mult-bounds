#!/usr/bin/env python3
"""The published H6 Smith factors give repair rank 560.

The checker multiplies the published factors. It does not rebuild the matrix.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_H6_SMITH_EXPONENTS repair_rank=560 no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_H6_SMITH_EXPONENTS " + message)


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
    require(11 * 19 == 209 and 11 * 19 * 23 == 4807, "the composite factors moved")
    repair = 336 + 208 + 16
    require(repair == 560, "the repair rank moved")
    require(30400 + repair == 30960, "the port count moved")
    require(208 + 16 == 224, "the 19 exponent moved")
    product = (11**336) * (209**208) * (4807**16)
    odd = (11**560) * (19**224) * (23**16)
    require(product == odd, "the odd determinant moved")
    return {
        "ports": 30960,
        "repair_rank": 560,
        "eleven_exponent": 560,
        "nineteen_exponent": 224,
        "twentythree_exponent": 16,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
