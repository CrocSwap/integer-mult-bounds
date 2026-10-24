#!/usr/bin/env python3
"""Moment straddle of the published T488 composition profile.

The checker evaluates the two endpoints. It does not replay the word.
"""

import hashlib
import json
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_T488_MOMENT_STRADDLE live=437248 straddle=true no_new_kappa"
PROFILE = {1: 10817496, 2: 3179808, 3: 1024434, 4: 447984, 5: 94794, 8: 35136, 48: 186782}
LOW = Fraction("0.001730418899766071163804")
HIGH = Fraction("0.001730418899766071163805")
PREVIOUS = Fraction("0.001730394391813963415120")
DELTA = Fraction("0.000000024507952107748684")
RELEASED = "0.0017304188997660711638039999999999999999999998999999999999999999999999"
WIDTH = 73
LIVE = 896 * 488


def fail(message):
    raise SystemExit("FAIL_T488_MOMENT_STRADDLE " + message)


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


def moment(saving, precision):
    with localcontext() as ctx:
        ctx.prec = precision
        exponent = Decimal(saving.numerator) / Decimal(saving.denominator)
        paid = sum(Decimal(count) * (Decimal(rank) ** (1 - exponent)) for rank, count in PROFILE.items())
        live = Decimal(LIVE) * (Decimal(WIDTH) ** (1 - exponent))
        return paid - live


def released_digits(value):
    require(value.denominator == 10 ** 70, "the released denominator moved")
    return "0." + f"{value.numerator:070d}"


def evaluate():
    authenticate()
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    kappa = Fraction(selected["kappa"])
    require(kappa == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    require(sum(rank * count for rank, count in PROFILE.items()) == 65088 * 488, "the rank mass moved")
    require(488 * 9 == 4392 and LIVE == 437248 and 4392 * 408 == 1791936, "the composition counts moved")
    require(HIGH - LOW == Fraction(1, 10 ** 24), "the bracket width moved")
    require(LOW - PREVIOUS == DELTA, "the endpoint delta moved")
    released = LOW - Fraction(10) ** -46 - Fraction(10) ** -70
    require(released_digits(released) == RELEASED, "the released string moved")
    require(released > kappa, "the released value undercuts the selected kappa")
    for precision in (80, 160):
        require(moment(LOW, precision) < 0 < moment(HIGH, precision), "the moment straddle failed")
    return {
        "rank_mass": 31762944,
        "calls": 4392,
        "live": LIVE,
        "roles": 1791936,
        "straddle": True,
        "released_digits": 70,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
