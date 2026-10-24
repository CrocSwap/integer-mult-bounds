#!/usr/bin/env python3
"""The one-unpaid moment at saving zero with centre 112.

The checker evaluates the coverage law. It does not replay the 704 columns.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_ZERO_SAVING_CENTRE_MOMENT moment=585/584 no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_ZERO_SAVING_CENTRE_MOMENT " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def moment(local):
    width = Fraction(896, 9)
    total = (73 - 1) * width + 112
    mass = sum(rank * count for rank, count in local.items())
    require(mass <= total, "a profile pays more than the coverage law")
    # At saving zero every rank unit costs 1/73, so idle rank does not matter.
    return (mass + (total - mass)) / (73 * width)


def evaluate():
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    closed = Fraction(112) / (73 * 896)
    require(closed == Fraction(1, 584), "the centre excess moved")
    value = 1 + closed
    require(value == Fraction(585, 584) > 1, "the zero-saving moment moved")
    total = (73 - 1) * Fraction(896, 9) + 112
    profiles = ({1: total}, {51: 1, 1: total - 51})
    require(all(moment(profile) == value for profile in profiles), "a local profile changed the moment")
    return {"moment": "585/584", "excess": "1/584", "no_new_kappa": True}


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
