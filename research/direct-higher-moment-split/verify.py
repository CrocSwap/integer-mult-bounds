#!/usr/bin/env python3
"""Exact finite corroboration of the direct higher-moment split theorem.

Produced by Nick Petalas. Apache-2.0.
The universal statement is proved in PROOF.md; this census is bounded.
"""

import argparse
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parameters(t, sigma):
    require(isinstance(t, Q) and isinstance(sigma, Q), "rational parameters required")
    require(0 < t < 1 and 1 < sigma <= 4, "parameter range")
    require(t.denominator <= 16 and sigma.denominator <= 16, "denominator budget")
    return t.numerator, t.denominator, sigma.numerator, sigma.denominator


def critical_polynomial(y, t, sigma):
    a, b, c, d = parameters(t, sigma)
    return a * d + (a * d - b * c) * y**b - b * c * y ** (b - a)


def normalized_power(q, y, t, sigma):
    a, b, c, d = parameters(t, sigma)
    require(isinstance(q, int) and 1 <= q <= 8, "quotient budget")
    require(isinstance(y, Q) and 0 <= y < 1, "remainder parameter")
    return (q + y**a) ** d / (q + y**b) ** c


def literal_split_power(q, y, t, sigma):
    a, b, c, d = parameters(t, sigma)
    numerator, denominator = y.numerator, y.denominator
    cutoff = denominator**b
    remainder = numerator**b
    rank = q * cutoff + remainder
    charge = q * denominator**a + numerator**a
    return Q(charge**d * denominator ** (b * c - a * d), rank**c)


def coefficient_enclosure(t, sigma):
    a, b, c, d = parameters(t, sigma)
    low, high = Q(0), Q(1)
    for _ in range(72):
        middle = (low + high) / 2
        if critical_polynomial(middle, t, sigma) >= 0:
            low = middle
        else:
            high = middle
    require(critical_polynomial(low, t, sigma) >= 0, "lower root bracket")
    require(critical_polynomial(high, t, sigma) < 0, "upper root bracket")
    lower = normalized_power(1, low, t, sigma)
    upper = (1 + high**a) ** d / (1 + low**b) ** c
    require(1 < lower <= upper and upper - lower < Q(1, 2**52), "coefficient bracket")
    return low, high, lower, upper


def census():
    exponents = (Q(1, 4), Q(1, 3), Q(1, 2), Q(2, 3), Q(3, 4), Q(7, 8))
    moments = (Q(5, 4), Q(3, 2), Q(17, 10), Q(2), Q(3))
    rows, cases, quotient_checks, witnesses = [], 0, 0, 0
    for t in exponents:
        for sigma in moments:
            low, high, lower, upper = coefficient_enclosure(t, sigma)
            for k in range(32):
                y = Q(k, 32)
                previous = normalized_power(1, y, t, sigma)
                for q in range(1, 9):
                    value = normalized_power(q, y, t, sigma)
                    require(value == literal_split_power(q, y, t, sigma), "literal integer split")
                    require(value <= upper, "split exceeds certified maximum")
                    if q > 1:
                        require(value < previous, "quotient monotonicity")
                        quotient_checks += 1
                    previous = value
                    if k or q > 1:
                        cases += 1
            a, b, c, d = parameters(t, sigma)
            cutoff, remainder = low.denominator**b, low.numerator**b
            require(0 < remainder < cutoff, "integer sharpness witness")
            require(Q(remainder, cutoff) == low**b, "integer normalization")
            require(normalized_power(1, low, t, sigma) == lower, "witness value")
            require(literal_split_power(1, low, t, sigma) == lower, "literal witness charge")
            witnesses += 1
            rows.append({"t": str(t), "sigma": str(sigma), "root_y": [str(low), str(high)],
                         "K_power": d, "K_power_interval": [str(lower), str(upper)],
                         "witness_cutoff_bits": cutoff.bit_length()})
    require((cases, quotient_checks, witnesses) == (7650, 6720, 30), "census domain")
    return rows, cases, quotient_checks, witnesses


def sharp_fixture():
    t, sigma, y = Q(1, 2), Q(17, 10), Q(1, 4)
    require(critical_polynomial(y, t, sigma) == 0, "exact maximizing remainder")
    power = Q(5, 4) ** 10 * Q(16, 17) ** 17
    require(normalized_power(1, y, t, sigma) == power, "attaining J=16 R=17")
    require(literal_split_power(1, y, t, sigma) == power, "literal attaining charge")
    require(Q(9, 8) ** 10 < power < Q(8, 7) ** 10, "strict rational separation")
    # PR4832's cited half-power coefficient is (1+sqrt(2))/2 > 6/5.
    require(Q(2) > Q(7, 5) ** 2, "old coefficient exceeds 6/5")
    require(power < Q(6, 5) ** 10, "strict improvement over linear-rank transfer")
    return {"t": str(t), "sigma": str(sigma), "J": 16, "R": 17,
            "maximizing_remainder": "1/16", "K_to_10": str(power),
            "K_strict_interval": ["9/8", "8/7"]}


def controls(fixture):
    rejected = 0
    invalid = ((Q(0), Q(2)), (Q(1), Q(2)), (Q(-1), Q(2)),
               (Q(1, 2), Q(1)), (Q(1, 2), Q(0)), (Q(1, 2), Q(5)),
               (Q(1, 17), Q(2)), (Q(1, 2), Q(33, 17)))
    for t, sigma in invalid:
        try:
            parameters(t, sigma)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid parameters accepted")
    for q, y in ((0, Q(1, 2)), (1, Q(-1, 2)), (1, Q(1))):
        try:
            normalized_power(q, y, Q(1, 2), Q(17, 10))
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid split accepted")
    for underclaim in (Q(1), Q(9, 8)):
        require(underclaim**10 < Q(fixture["K_to_10"]), "false coefficient not rejected")
        rejected += 1
    require(rejected == 13, "control count")
    return rejected


def source_hashes():
    package = Path(__file__).resolve().parent
    root = package.parent.parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        data = (package / name).read_bytes()
        require(len(data) <= 2_000_000, "package file budget")
        hashes[f"research/direct-higher-moment-split/{name}"] = hashlib.sha256(data).hexdigest()
    manifest = json.loads((package / "SOURCES.json").read_text())
    inputs = [row for row in manifest["files"] if row["usage"] == "input"]
    require(len(inputs) == 2, "source input count")
    for row in inputs:
        data = (root / row["path"]).read_bytes()
        require(len(data) <= 2_000_000, "source file budget")
        digest = hashlib.sha256(data).hexdigest()
        require(digest == row["sha256"], "source pin mismatch")
        hashes[row["path"]] = digest
    return hashes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    rows, cases, quotient_checks, witnesses = census()
    fixture = sharp_fixture()
    rejected = controls(fixture)
    result = {"status": "PASS_DIRECT_HIGHER_MOMENT_SPLIT", "claim_type": "scoped proof with finite corroboration",
              "split_cases": cases, "quotient_comparisons": quotient_checks,
              "integer_near_maximizers": witnesses, "rejected_controls": rejected,
              "coefficient_enclosures": rows, "sharp_fixture": fixture, "sha256": source_hashes()}
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.receipt is not None:
        target = args.receipt.resolve()
        require(not target.is_relative_to(Path(__file__).resolve().parent.parent.parent),
                "keep generated receipts outside the checkout")
        written = target.write_text(payload)
        require(written == len(payload) and target.read_text() == payload, "receipt write")
    print(payload, end="")


if __name__ == "__main__":
    main()
