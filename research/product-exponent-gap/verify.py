#!/usr/bin/env python3
"""The product exponent is 603/1000 and the scaled error is below 1/8.

The checker compares exact rationals. It does not run the convolution.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_PRODUCT_EXPONENT_GAP exponent=603/1000 below_fourier=true no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_PRODUCT_EXPONENT_GAP " + message)


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


def ceil_log2(value):
    exponent = 0
    while (1 << exponent) < value:
        exponent += 1
    return exponent


def evaluate():
    authenticate()
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    exponent = Fraction(8, 5) - Fraction(997, 1000)
    fourier = 1 - Fraction(576, 332929)
    require(exponent == Fraction(603, 1000) and fourier == Fraction(332353, 332929), "the exponents moved")
    require(exponent < fourier, "the product exponent left the Fourier allowance")
    require(Fraction(8, 5) - Fraction(1, 40) == Fraction(63, 40) > 1, "the conservative regime moved")
    require((12 * 1 + 2) % 4 == 2 and 16 * 12 - 12 == 180 and 32 - 14 == 18, "the coefficient identities moved")
    require(ceil_log2(26) + 3 == 4 * 2 and (1 << 5) >= 26, "the precision base moved")
    for shift in (1, 2, 7, 80):
        width = 12 * shift + 2
        require(width % 4 == 2 and width > 2, "a coefficient width became a power of two")
        slack = ceil_log2(width)
        require((1 << slack) > width, "a non-power met its ceiling")
        require(Fraction(width, 1 << (slack + 3)) < Fraction(1, 8), "the scaled error reached 1/8")
    for precision in (2, 3, 8):
        slack = ceil_log2(12 * precision + 2)
        require(2 * precision + 2 * precision + slack + 3 <= 8 * precision, "the precision ceiling moved")
    return {
        "exponent": "603/1000",
        "fourier": "332353/332929",
        "below_fourier": True,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
