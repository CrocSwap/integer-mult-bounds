#!/usr/bin/env python3
"""Exact finite corroboration of the prime-band product envelope.

Produced by Nick Petalas. Apache-2.0.
The dimension-uniform argument is in README.md. No prime theorem is replayed.
"""

from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from math import prod
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dimension(d):
    require(type(d) is int and 2 <= d <= 512, "finite checker requires 2<=d<=512")


def envelope(d):
    dimension(d)
    return Fraction(3 * d, 3 * d - 1) ** (d - 1)


def product_ratio(d, coordinates):
    dimension(d)
    require(len(coordinates) == d - 1, "the caller has exactly D=d-1 axes")
    low, high = 1 - Fraction(1, 3 * d), 1 - Fraction(1, 4 * d)
    for s, t in coordinates:
        require(s > 0 and t > 0, "lengths must be positive")
        require(low < s / t <= high, "point outside the half-open prime band")
    return prod((t / s for s, t in coordinates), start=Fraction(1))


def log_interval(x):
    """Integrate the positive geometric series, with an exact tail bound."""
    require(Fraction(1) <= x <= Fraction(6, 5), "log probe outside bounded range")
    z = (x - 1) / (x + 1)
    lower = 2 * sum((z ** (2 * j + 1) / (2 * j + 1) for j in range(12)),
                    start=Fraction(0))
    tail = 2 * z**25 / (25 * (1 - z * z))
    return lower, lower + tail


def exp_third_interval():
    term, lower = Fraction(1), Fraction(1)
    for j in range(1, 11):
        term /= 3 * j
        lower += term
    first_omitted = term / 33
    upper = lower + first_omitted / (1 - Fraction(1, 36))
    require(lower < upper < Fraction(349, 250) < Fraction(3, 2),
            "rational corollary failed")
    return lower, upper


def check_boxes():
    count = 0
    for d in range(2, 7):
        low = 1 - Fraction(1, 3 * d)
        width = Fraction(1, 12 * d)
        for digits in product(range(1, 5), repeat=d - 1):
            coordinates = []
            log_upper = Fraction(0)
            for i, digit in enumerate(digits):
                t = Fraction(2 ** (3 + i % 2))
                s = t * (low + width * digit / 4)
                coordinates.append((s, t))
                log_upper += log_interval(t / s)[1]
            require(product_ratio(d, coordinates) < envelope(d), "box envelope failed")
            require(log_upper < Fraction(1, 3), "box logarithm bound failed")
            count += 1
    return count


def check_envelopes():
    for d in range(2, 513):
        lower, upper = log_interval(Fraction(3 * d, 3 * d - 1))
        require(Fraction(d - 1, 3 * d) < (d - 1) * lower,
                "lower integral bound failed")
        require((d - 1) * upper < Fraction(d - 1, 3 * d - 1) < Fraction(1, 3),
                "upper integral bound failed")
    return 511


def check_sharpness():
    finite = 0
    for d in range(2, 65):
        low, width = 1 - Fraction(1, 3 * d), Fraction(1, 12 * d)
        previous = Fraction(0)
        for j in range(1, 9):
            q = low + width / 2**j
            ratio = product_ratio(d, [(q, Fraction(1))] * (d - 1))
            require(previous < ratio < envelope(d), "endpoint approach failed")
            previous = ratio
            finite += 1
    for j in range(1, 17):
        d = 2**j
        q = 1 - Fraction(1, 3 * d) + Fraction(1, 12 * d * d)
        lower, upper = log_interval(1 / q)
        require(Fraction(1, 3) - Fraction(5, 12 * d) < (d - 1) * lower,
                "sharpness lower squeeze failed")
        require((d - 1) * upper < Fraction(1, 3), "sharpness upper squeeze failed")
    return finite, 16


def check_controls(exp_upper):
    valid = [(Fraction(7, 8), Fraction(1))]
    require(product_ratio(2, valid) == Fraction(8, 7), "closed upper endpoint rejected")
    invalid = [
        (1, valid), (True, valid), (513, valid), (2, []), (2, valid * 2),
        (2, [(Fraction(5, 6), Fraction(1))]),
        (2, [(Fraction(9, 10), Fraction(1))]),
        (2, [(Fraction(-1), Fraction(1))]),
        (2, [(Fraction(1), Fraction(0))]),
    ]
    rejected = 0
    for d, coordinates in invalid:
        try:
            product_ratio(d, coordinates)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid fixture accepted")
    # Distinct band primes, but the false D=d contract invalidates the bound.
    for prime in (107, 109):
        require(Fraction(5, 6) < Fraction(prime, 128) <= Fraction(7, 8),
                "bad control band")
    require(Fraction(128**2, 107 * 109) > exp_upper, "wrong axis count went undetected")
    d = 128
    q = 1 - Fraction(1, 3 * d) + Fraction(1, 12 * d * d)
    require(q ** (1 - d) > Fraction(139, 100), "smaller constant control failed")
    return rejected, 2


def file_hashes():
    root = Path(__file__).resolve().parent
    names = ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        with (root / name).open("rb") as source:
            data = source.read(262145)
        require(len(data) <= 262144, "package file exceeds fixed read bound")
        hashes[name] = sha256(data).hexdigest()
    return hashes


def main():
    exp_lower, exp_upper = exp_third_interval()
    boxes = check_boxes()
    dimensions = check_envelopes()
    approaches, limits = check_sharpness()
    rejected, counterexamples = check_controls(exp_upper)
    receipt = {
        "marker": "PASS_MANY_AXIS_PRIME_PRODUCT_LOSS",
        "rational_boxes": boxes, "envelope_dimensions": dimensions,
        "endpoint_approaches": approaches, "limit_probes": limits,
        "rejected_inputs": rejected, "boundary_counterexamples": counterexamples,
        "exp_third_interval": [str(exp_lower), str(exp_upper)],
        "package_sha256": file_hashes(),
        "claim_type": "scoped proof with finite corroboration", "no_new_kappa": True,
    }
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
