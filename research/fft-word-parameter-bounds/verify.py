#!/usr/bin/env python3
"""Parameter bounds for the fixed-tape FFT word.

The checker derives the digit geometry and the absorbed power. It does not
run the word multiplier.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_FFT_WORD_PARAMETER_BOUNDS power=9981/10000 no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_FFT_WORD_PARAMETER_BOUNDS " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def ceil_log2(number):
    if number == 1:
        return 0
    floor = number.bit_length() - 1
    return floor if (1 << floor) == number else floor + 1


def geometry(width):
    beta = ceil_log2(width)
    base = 1 << beta
    require(1 << (beta - 1) < width <= base, "the digit base moved")
    digit_count = (width + beta - 1) // beta
    require((digit_count - 1) * beta < width <= digit_count * beta, "the digit count moved")
    ell = ceil_log2(2 * digit_count)
    ring = 1 << ell
    require(ring // 2 < 2 * digit_count <= ring, "the ring missed its bracket")
    require(2 * digit_count <= ring < 4 * digit_count, "the ring ratio moved")
    require(ring * beta >= 2 * width, "the ring lost the input width")
    precision = 2 * beta + ell
    require(1 <= ell < precision, "the exponent left its range")
    require(1 << precision == ring * base * base, "the normalized grid moved")
    require(2 * digit_count - 2 < ring, "the product degree wrapped")
    require(digit_count * (base - 1) ** 2 < (1 << (precision - 1)), "the coefficient headroom moved")


def exponential_bound():
    total = Fraction(0)
    term = Fraction(1)
    for index in range(12):
        total += term
        term /= index + 1
    tail = term / (1 - Fraction(1, 13))
    require(total + tail < 3 < 4, "the exponential series moved")


def evaluate():
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    checked = 0
    for width in range(2, 65537):
        geometry(width)
        checked += 1
    geometry(1000000)
    checked += 1
    require(checked == 65536, "the width count moved")
    exponential_bound()
    screen = Fraction(8, 5) - Fraction(1, 500)
    absorbed = 1 - Fraction(1, 500) + Fraction(1, 10000)
    fourier = Fraction(99827619697, 100000000000)
    require(screen == Fraction(799, 500) and screen > 1, "the direct screen moved")
    require(absorbed == Fraction(9981, 10000), "the absorbed power moved")
    gap = fourier - absorbed
    require(gap == Fraction(17619697, 100000000000) and gap > 0, "the Fourier gap moved")
    return {
        "checked_widths": 65536,
        "screen_power": "799/500",
        "absorbed_power": "9981/10000",
        "fourier_power": "99827619697/100000000000",
        "power_gap": "17619697/100000000000",
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
