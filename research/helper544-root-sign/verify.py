#!/usr/bin/env python3
"""Sign of the 360-replica helper544 profile at its published root.

The checker prices the signed profile. It does not replay the words.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_HELPER544_ROOT_SIGN replicas=360 straddle=true no_new_kappa"
PROFILE = {1: 7990332, 2: 2349000, 3: 748971, 4: 330480, 5: 69479, 8: 25920, 32: 1, 48: 137911, 73: -896 * 360}
LOW = Fraction(86522418010381773087, 50000000000000000000000)
HIGH = Fraction(1730448360207635461741, 1000000000000000000000000)
PREVIOUS = Fraction(
    17304188997660711638039999999999999999999998999999999999999999999999,
    10000000000000000000000000000000000000000000000000000000000000000000000,
)
GAIN = Fraction(1841277597768621, 62500000000000000000000)


def fail(message):
    raise SystemExit("FAIL_HELPER544_ROOT_SIGN " + message)


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


def logarithm(rank):
    exponent = rank.bit_length() - 1
    reduced = Fraction(rank, 1 << exponent)

    def series(value):
        slope = (value - 1) / (value + 1)
        total = Fraction(0)
        power = slope
        for index in range(100):
            total += 2 * power / (2 * index + 1)
            power *= slope * slope
        tail = 2 * power / ((201) * (1 - slope * slope))
        return total, total + tail

    low_reduced, high_reduced = series(reduced)
    low_two, high_two = series(Fraction(2))
    low = low_reduced + exponent * low_two
    high = high_reduced + exponent * high_two
    scale = 10 ** 90
    return Fraction((low.numerator * scale) // low.denominator, scale), Fraction(
        -((-high.numerator * scale) // high.denominator), scale
    )


def exponential(value, degree):
    term = Fraction(1)
    total = term
    for index in range(1, degree + 1):
        term *= -value / index
        total += term
    return total


def enclosure(saving):
    low = high = Fraction(0)
    for rank, count in PROFILE.items():
        log_low, log_high = logarithm(rank)
        left = rank * exponential(saving * log_high, 31)
        right = rank * exponential(saving * log_low, 30)
        if count >= 0:
            low += count * left
            high += count * right
        else:
            low += count * right
            high += count * left
    return low, high


def evaluate():
    authenticate()
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    kappa = Fraction(selected["kappa"])
    require(kappa == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    require(HIGH - LOW == Fraction(1, 10 ** 24), "the bracket width moved")
    require(PROFILE[73] == -896 * 360, "the width charge moved")
    low_enclosure = enclosure(LOW)
    high_enclosure = enclosure(HIGH)
    require(low_enclosure[1] < 0 < high_enclosure[0], "the root signs moved")
    endpoint = LOW - Fraction(1, 10 ** 46) - Fraction(1, 10 ** 70)
    require(endpoint - PREVIOUS == GAIN, "the gain moved")
    require(endpoint > kappa, "the endpoint undercuts the selected kappa")
    return {
        "replicas": 360,
        "straddle": True,
        "gain": "1841277597768621/62500000000000000000000",
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
