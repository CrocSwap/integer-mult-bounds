#!/usr/bin/env python3
"""Read-only exact corroboration of the new tail entropy theorem.

produced by Nick Petalas. Apache-2.0.
The universal assertion is the written proof, not this finite census.
"""

from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def entropy_power(q, p, x):
    """Return (q exp(-D(x||p)))**denominator(x), exactly."""
    require(q >= 1 and 0 < x < p < 1, "invalid entropy regime")
    n, j = x.denominator, x.numerator
    require(n <= 64, "finite check denominator exceeds 64")
    return q**n * (p / x)**j * ((1 - p) / (1 - x))**(n - j)


def binary_gate(a, b, low, high, paid_mean, paid):
    """Classify a two-target law in common logarithmic rank units."""
    require(a > 0 and b > 0 and paid > 0, "nonpositive mass")
    require(0 <= low < high <= 5, "invalid finite rank exponents")
    require(a + b >= paid, "q>=1 is required")
    if paid_mean < low:
        return True
    if paid_mean == low:
        return a < paid
    mean = (a * low + b * high) / (a + b)
    if paid_mean >= mean:
        return False
    x = Q(paid_mean - low, high - low)
    return entropy_power((a + b) / paid, b / (a + b), x) < 1


def derivative_classifier(a, b, low, high, paid_mean, paid):
    """Independent monomial critical-value comparison, without entropy."""
    if paid_mean < low:
        return True
    if paid_mean == low:
        return a < paid
    if (paid_mean - low) * a >= (high - paid_mean) * b:
        return False
    d, j = high - low, paid_mean - low
    critical = a**(d - j) * b**j * d**d
    divisor = (d - j)**(d - j) * j**j
    return critical < paid**d * divisor


def scalar_value(z, a, b, low, high, paid_mean):
    require(0 < z <= 1, "tail variable outside (0,1]")
    return a * z**(low - paid_mean) + b * z**(high - paid_mean)


def passing_point(a, b, low, high, paid_mean, paid):
    """Find a rational z=4**(-lambda) with a literal strict scalar gate."""
    if paid_mean <= low:
        for j in range(1, 129):
            z = Q(1, 2**j)
            if scalar_value(z, a, b, low, high, paid_mean) < paid:
                return z
    else:
        left, right = Q(0), Q(1)
        critical = a * (paid_mean - low) / (b * (high - paid_mean))
        require(0 < critical < 1, "critical point must lie in (0,1)")
        for _ in range(96):
            z = (left + right) / 2
            if scalar_value(z, a, b, low, high, paid_mean) < paid:
                return z
            if z**(high - low) < critical:
                left = z
            else:
                right = z
    raise ValueError("bounded rational witness search exhausted")


def histogram_census():
    counts = Counter()
    for low in range(1, 5):
        for high in range(low + 1, 6):
            for paid_mean in range(high):
                for wa in range(1, 7):
                    for wb in range(1, 7):
                        for wc in range(1, 7):
                            masses = (Q(wa * 2**low), Q(wb * 2**high))
                            paid = Q(wc * 2**paid_mean)
                            if sum(masses) < paid:
                                counts["outside_q_domain"] += 1
                                continue
                            check_histogram(masses, low, high, paid_mean, paid, counts)
    require(counts["passing"] > 0 and counts["failing"] > 0, "empty outcome class")
    return dict(sorted(counts.items()))


def check_histogram(masses, low, high, paid_mean, paid, counts):
    a, b = masses
    decision = binary_gate(a, b, low, high, paid_mean, paid)
    separate = derivative_classifier(a, b, low, high, paid_mean, paid)
    require(decision == separate, "entropy and monomial classifiers disagree")
    counts["histograms"] += 1
    if decision:
        z = passing_point(a, b, low, high, paid_mean, paid)
        require(scalar_value(z, a, b, low, high, paid_mean) < paid, "bad witness")
        counts["passing"] += 1
    else:
        for z in (Q(1), Q(3, 4), Q(1, 2), Q(1, 4), Q(1, 8)):
            require(scalar_value(z, a, b, low, high, paid_mean) >= paid,
                    "failing classification has a passing sample")
            counts["failing_point_controls"] += 1
        counts["failing"] += 1


def interior_census():
    counts = Counter()
    for endpoint_mass in range(1, 9):
        for interior_mass in range(9):
            total = 2 * endpoint_mass + interior_mass
            weights = tuple(Q(m, total) for m in
                            (endpoint_mass, interior_mass, endpoint_mass))
            for denominator in range(2, 6):
                z = Q(1, denominator**2)
                x = z / (1 + z)
                literal = weights[0] + weights[1] / denominator + weights[2] * z
                chord = (1 + z) / 2
                require(literal <= chord, "chord inequality failed")
                require((literal == chord) == (interior_mass == 0), "strictness failed")
                power = chord**x.denominator / z**x.numerator
                require(power == entropy_power(Q(1), Q(1, 2), x), "entropy value failed")
                require(0 < power < 1, "invalid minimized value")
                counts["laws"] += 1
                counts["strict" if interior_mass else "endpoint_equality"] += 1
    return dict(sorted(counts.items()))


def fixture_transition():
    for c in range(1, 129):
        q, p, x = Q(514, 4 * c), Q(256, 257), Q(1, 3)
        require(entropy_power(q, p, x) == Q(6, c)**3, "fixture optimum failed")
        require(binary_gate(Q(2), Q(512), 1, 4, 2, Q(4 * c)) == (c >= 7),
                "incorrect strict c transition")
    u = Q(1, 2**66) * Q(8196, 514) * 4**31
    v = Q(2**198) * Q(3, 224)**32
    require(u == Q(2049, 2056) and u < 1, "mixed tail witness failed")
    require(v == 64 * Q(6, 7)**32 and v < 1, "root tail witness failed")
    require(Q(8196, 514) > 4, "forward ordering failed")
    require(Q(1, 4) + Q(32, 256) == Q(3, 8), "negative moment failed")
    require(2 * 8 + Q(512, 8**2) == 24, "attained minimum failed")
    for j in range(1, 65):
        y = Q(j, 4)
        left = y**3 * (2 - 1024 / y**3)
        right = 2 * (y - 8) * (y**2 + 8 * y + 64)
        require(left == right, "fixture derivative factorization failed")
    return {"integer_cases": 128, "u": str(u), "v": str(v), "minimum": 24}


def mirror_failure():
    cells = ((Q(1, 256), Q(1, 16)), (Q(1, 16), Q(1, 4)))
    values = []
    for left, right in cells:
        z = (left + right) / 2
        source = 2048 if Q(1, 256) < z <= Q(1, 16) else 0
        exits = 8 if Q(1, 16) < z <= Q(1, 4) else 0
        values.append((source, exits))
    require(values == [(2048, 0), (0, 8)], "mirror window boundary changed")
    covered = not any(e > 0 and s == 0 for s, e in values)
    require(not covered, "mirror failure disappeared")
    return {"cells_at_c1": values, "covered": covered}


def rejection_controls():
    require(entropy_power(Q(5, 4), Q(4, 5), Q(1, 2)) == 1,
            "two-point equality must fail strictly")
    require(Q(5, 4) * 2 * (Q(1, 10) + Q(1, 5) / 2 + Q(7, 10) / 4)
            == Q(15, 16), "interior mass must rescue equality")
    require(not binary_gate(Q(2), Q(512), 1, 4, 2, Q(24)), "equality accepted")
    require(not binary_gate(Q(2), Q(2), 1, 3, 2, Q(4)), "mean equality accepted")
    require(not binary_gate(Q(2), Q(2), 1, 3, 3, Q(3)), "reversed mean accepted")
    require(binary_gate(Q(2), Q(8), 2, 4, 1, Q(1)), "below-range gate rejected")
    require(not binary_gate(Q(2), Q(8), 2, 4, 2, Q(2)), "lower-atom equality accepted")
    require(binary_gate(Q(2), Q(8), 2, 4, 2, Q(3)), "lower-atom strict gate rejected")
    invalid = ((Q(1, 2), Q(4, 5), Q(1, 2)), (Q(1), Q(1, 2), Q(3, 4)),
               (Q(1), Q(1), Q(1, 2)))
    for args in invalid:
        try:
            entropy_power(*args)
        except ValueError:
            continue
        raise ValueError("invalid entropy input was accepted")
    return 11


def source_hashes():
    directory = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    for name in names:
        require((directory / name).stat().st_size <= 128 * 1024, "package file exceeds 128 KiB")
    return {name: sha256((directory / name).read_bytes()).hexdigest() for name in names}


def main():
    receipt = {
        "claim_type": "scoped written proof with exact finite corroboration",
        "histogram_census": histogram_census(),
        "interior_census": interior_census(),
        "fixture": fixture_transition(),
        "mirror": mirror_failure(),
        "rejection_controls": rejection_controls(),
        "source_sha256": source_hashes(),
    }
    canonical = json.dumps(receipt, sort_keys=True, separators=(",", ":"))
    receipt["receipt_sha256"] = sha256(canonical.encode()).hexdigest()
    print(json.dumps(receipt, indent=2, sort_keys=True))
    print("PASS_ADAPTIVE_TAIL_ENTROPY no_new_kappa")


if __name__ == "__main__":
    main()
