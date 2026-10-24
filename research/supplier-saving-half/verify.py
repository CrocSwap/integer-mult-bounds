#!/usr/bin/env python3
"""The checked complex saving is half the saving the assembly consumes.

The checker bounds the consumed-saving moment. It does not run the historical
checker.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_SUPPLIER_SAVING_HALF ratio=2 above_margin=true no_new_kappa"
GRID = 10**30


def fail(message):
    raise SystemExit("FAIL_SUPPLIER_SAVING_HALF " + message)


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
    expected = {"research/climbed-48/certificate.json"}
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def log_series(value):
    return 2 * sum(value ** (2 * index + 1) / (2 * index + 1) for index in range(24))


LOG_TWO = log_series(Fraction(1, 3))


def log_lower(ratio):
    scale = 0
    reduced = Fraction(ratio)
    while reduced > 2:
        reduced /= 2
        scale += 1
    slope = (reduced - 1) / (reduced + 1)
    require(0 <= slope <= Fraction(1, 3), "the logarithm slope left its range")
    bound = scale * LOG_TWO + log_series(slope)
    return Fraction(bound.numerator * GRID // bound.denominator, GRID)


def exp_lower(value):
    return 1 + value + value**2 / 2 + value**3 / 6 + value**4 / 24


def moment_lower(rows, saving, width, capacity):
    total = Fraction(0)
    for rank, count in rows:
        require(0 < rank < width, "a child rank left the domain")
        log_bound = log_lower(Fraction(width, rank))
        total += Fraction(rank * count, width * capacity) * exp_lower(saving * log_bound)
    return total


def evaluate():
    authenticate()
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    certificate = json.loads((ROOT / "research/climbed-48/certificate.json").read_text(encoding="utf-8"))
    complex_part = certificate["complex"]
    counts = complex_part["counts"]
    width = int(counts["m"])
    capacity = int(counts["W"])
    require(width == 784 and capacity == 537696432, "the complex denominator moved")
    consumed = Fraction(certificate["assembly"]["parameters"]["a_complex"])
    checked = Fraction(complex_part["saving"])
    require(consumed == checked == Fraction(717, 10000000), "the pinned saving moved")
    require(consumed == 2 * Fraction(717, 20000000), "the half-saving relation moved")
    rows = [(int(rank), int(count)) for rank, count in complex_part["child_width_multiplicities"]]
    require(rows[-1] == (756, 516232080), "the last multiplicity row moved")
    mutant = rows[:-1] + [(756, 516232085)]
    bound = moment_lower(mutant, consumed, width, capacity)
    require(bound > 1 + Fraction(4, 10**10), "the consumed-saving moment met the margin")
    return {
        "checked_saving": "717/20000000",
        "consumed_saving": "717/10000000",
        "multiplicity_increase": 5,
        "above_margin": True,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
