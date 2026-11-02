#!/usr/bin/env python3
"""Exact finite corroboration for the two-call reused-seed drift theorem."""
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import platform


MAX_EXHAUSTIVE_DENOMINATOR = 24


def require(condition: bool, label: str) -> None:
    if not condition:
        raise ValueError(label)


def rounded(numerator: int, denominator: int, seed: int) -> int:
    if denominator < 1 or not 0 <= seed < denominator:
        raise ValueError("invalid rounding domain")
    quotient, remainder = divmod(numerator, denominator)
    return quotient + int(seed < remainder)


def sharp_bound(denominator: int) -> Fraction:
    if denominator < 1:
        raise ValueError("nonpositive denominator")
    return Fraction(denominator * denominator // 4, denominator * denominator)


def policy_total(m: int, first: int, low: int, high: int) -> int:
    """Sum scaled local errors, literally executing every seed."""
    total = 0
    for seed in range(m):
        bit = rounded(first, m, seed)
        second = high if bit else low
        output = rounded(second, m, seed)
        total += m * (bit + output) - first - second
    return total


def exhaustive_policies() -> dict[str, int]:
    policies = 0
    seeds = 0
    for m in range(1, MAX_EXHAUSTIVE_DENOMINATOR + 1):
        smallest, largest = 0, 0
        for first, low, high in product(range(m), repeat=3):
            total = policy_total(m, first, low, high)
            smallest = min(smallest, total)
            largest = max(largest, total)
            require(abs(Fraction(total, m * m)) <= sharp_bound(m), "policy bound")
            policies += 1
            seeds += m
        require(Fraction(largest, m * m) == sharp_bound(m), "positive sharpness")
        require(Fraction(smallest, m * m) == -sharp_bound(m), "negative sharpness")
    return {"denominators": MAX_EXHAUSTIVE_DENOMINATOR,
            "policies": policies, "seed_executions": seeds}


def fresh_and_nonadaptive() -> dict[str, int]:
    fresh_policies = 0
    fresh_tapes = 0
    nonadaptive = 0
    for m in range(1, 9):
        for first, low, high in product(range(m), repeat=3):
            total = 0
            for left, right in product(range(m), repeat=2):
                bit = rounded(first, m, left)
                second = high if bit else low
                total += m * (bit + rounded(second, m, right)) - first - second
                fresh_tapes += 1
            require(total == 0, "fresh adaptive law")
            fresh_policies += 1
        for first, second in product(range(m), repeat=2):
            require(policy_total(m, first, second, second) == 0, "fixed-input reuse")
            nonadaptive += 1
    return {"fresh_policies": fresh_policies, "fresh_tapes": fresh_tapes,
            "nonadaptive_policies": nonadaptive}


def signed_translation_checks() -> int:
    checked = 0
    for m in range(1, 18):
        for residue in range(m):
            for quotient, shift, seed in product((-3, -1, 0, 2), (-2, 0, 3), range(m)):
                numerator = quotient * m + residue
                require(rounded(numerator + shift * m, m, seed)
                        == shift + rounded(numerator, m, seed), "integer translation")
                require(rounded(numerator, m, seed) == quotient + int(seed < residue),
                        "Euclidean signed remainder")
                checked += 1
    return checked


def witness_and_restoration() -> dict[str, int]:
    witness_seeds = 0
    protocols = 0
    for m in range(1, 65):
        r = m // 2
        total = 0
        for seed in range(m):
            first = rounded(r, m, seed)
            second = rounded(r * first, m, seed)
            require(second == first, "attaining two-shear word")
            total += second
            witness_seeds += 1
        require(Fraction(total, m) - Fraction(r * r, m * m) == sharp_bound(m),
                "final-output drift")
    for m in range(1, 10):
        r = m // 2
        for x, y, z, out, seed in product((-2, 0, 3), (-2, 0, 3),
                                            (-2, 0, 3), (-2, 0, 3), range(m)):
            y1 = y + rounded(r * x, m, seed)
            z1 = z + rounded(r * y1, m, seed)
            copied = out + z1
            z2 = z1 - rounded(r * y1, m, seed)
            y2 = y1 - rounded(r * x, m, seed)
            require((x, y2, z2, seed) == (x, y, z, seed), "dirty restoration")
            require(copied - out == z1, "retained output")
            protocols += 1
    return {"witness_denominators": 64, "witness_seeds": witness_seeds,
            "dirty_protocols": protocols}


def rejection_controls() -> int:
    rejected = 0
    for args in ((0, 0, 0), (0, -1, 0), (0, 2, -1), (0, 2, 2)):
        try:
            rounded(*args)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid rounding domain accepted")
    try:
        sharp_bound(0)
    except ValueError:
        rejected += 1
    else:
        raise ValueError("invalid theorem domain accepted")
    # False claims are rejected by literal counterexamples, not a changed oracle.
    total = policy_total(2, 1, 0, 1)
    require(total != 0, "reject restored-seed-implies-unbiased")
    require(abs(Fraction(total, 4)) > Fraction(1, 8), "reject half-size bound")
    require(policy_total(3, 1, 0, 1) == 2, "reject continuous 1/4 equality at odd m")
    return rejected + 3


def main() -> None:
    report = {"claim_type": "scoped proof with finite exact corroboration",
              "exhaustive": exhaustive_policies(),
              "controls": fresh_and_nonadaptive(),
              "signed_translations": signed_translation_checks(),
              "witness": witness_and_restoration(),
              "rejection_controls": rejection_controls(),
              "python": platform.python_version()}
    package = Path(__file__).resolve().parent
    report["package_sha256"] = {
        path.name: sha256(path.read_bytes()).hexdigest()
        for path in sorted(package.iterdir()) if path.is_file()
    }
    print("RESULT " + json.dumps(report, sort_keys=True))
    print("PASS_REUSED_SEED_ADAPTIVE_DRIFT")


if __name__ == "__main__":
    main()
