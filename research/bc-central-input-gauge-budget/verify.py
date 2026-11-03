#!/usr/bin/env python3
"""Exact corroboration of the central-input-gauge capacity envelope."""

from decimal import Decimal, ROUND_FLOOR, localcontext
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from math import comb
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
KINDS = {"A": (0, 0, -1), "B": (0, 1, 0), "C": (1, 0, 0)}
MASKS = tuple(product(range(2), repeat=2))
SCALE = 10**12


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def source_profiles() -> dict:
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    inputs = [row for row in manifest["files"] if row["usage"] == "input"]
    require(len(inputs) == 1, "expected one cited contract")
    row = inputs[0]
    path = PACKAGE.parents[1] / row["path"]
    require(path.stat().st_size < 16 * 1024 * 1024, "source size limit")
    raw = path.read_bytes()
    require(sha256(raw).hexdigest() == row["sha256"], "changed cited contract")
    profiles = {}
    for line in raw.decode().splitlines():
        fields = [field.strip() for field in line.split("|")]
        if len(fields) == 6 and fields[1] in ("B", "C"):
            if fields[2].startswith("1:"):
                paid = dict(tuple(map(int, pair.split(":"))) for pair in fields[2].split(", "))
                helpers = dict(tuple(map(int, pair.split(":"))) for pair in fields[3].split(", "))
                profiles[fields[1]] = (paid, helpers)
    require(set(profiles) == {"B", "C"}, "missing cited profile")
    return profiles


def rank2(matrix: tuple) -> int:
    a, b, c, d = matrix
    if a * d != b * c:
        return 2
    return int(any(matrix))


def matrix(kind: str, gauge: tuple, q: Fraction, transverse: int) -> tuple:
    a, b, off = KINDS[kind]
    x, y = gauge
    return (transverse * q ** (a + x), Fraction(0),
            transverse * q ** (off + x), transverse * q ** (b + y))


def literal_profile(kind: str, gauge: tuple, q: Fraction, transverse: int) -> tuple:
    original = matrix(kind, gauge, q, transverse)
    ranks = []
    for central, parity in MASKS:
        changed = matrix(kind, gauge, (-1)**central * q, (-1)**parity * transverse)
        ranks.append(rank2(tuple(a - b for a, b in zip(original, changed))))
    return tuple(ranks)


def parity_profile(kind: str, gauge: tuple) -> tuple:
    a, b, off = KINDS[kind]
    x, y = gauge
    ranks = []
    for central, parity in MASKS:
        diagonal0 = (parity + central * (a + x)) % 2
        diagonal1 = (parity + central * (b + y)) % 2
        lower = (parity + central * (off + x)) % 2
        ranks.append(2 if diagonal0 and diagonal1 else int(bool(diagonal0 or diagonal1 or lower)))
    return tuple(ranks)


def coefficients(profile: tuple) -> tuple:
    # Entries use (c,e) = (0,0), (0,1), (1,0), (1,1).
    require(profile[0] == 0, "identity cut must vanish")
    cross = Fraction(profile[3] - profile[1] - profile[2], 2)
    return (profile[2] + cross, profile[1] + cross, -cross)


def check_pair_ranks() -> tuple:
    tables = {}
    cases = 0
    for kind, gauge in product(KINDS, MASKS):
        profile = parity_profile(kind, gauge)
        for q, transverse in product((Fraction(1), Fraction(2), Fraction(-2), Fraction(2, 3)), (1, 3)):
            require(literal_profile(kind, gauge, q, transverse) == profile, "literal pair rank")
            cases += 4
        tables[kind + "".join(map(str, gauge))] = list(profile)
    require(tables["B10"] != tables["C01"], "B/C gauge distinction control")
    require(tables["A11"] != tables["A01"], "two-input A control")
    return tables, cases


def check_cut_polynomials() -> int:
    cases = 0
    for kind, gauge in product(KINDS, MASKS):
        polynomial = [0] * 9
        for mask in range(256):
            central = mask & 1
            parity = (mask >> 1).bit_count() % 2
            q, d = Fraction(2), 3
            original = matrix(kind, gauge, q, d)
            changed = matrix(kind, gauge, (-1)**central * q, (-1)**parity * d)
            rank = rank2(tuple(a - b for a, b in zip(original, changed)))
            weight = mask.bit_count()
            for degree in range(weight, 9):
                polynomial[degree] += rank * comb(8 - weight, degree - weight) * (-1)**(degree - weight)
            cases += 1
        expected = [Fraction(0)] * 9
        for rank, coefficient in zip((1, 7, 8), coefficients(parity_profile(kind, gauge))):
            for degree in range(1, rank + 1):
                expected[degree] += coefficient * (-1)**(degree + 1) * 2**(degree - 1) * comb(rank, degree)
        require(polynomial == expected, "Bernoulli cut polynomial")
    return cases


def envelope(kind: str, budget: int, delta: Fraction) -> Fraction:
    exceptional = min(budget, 56)
    ordinary_pairs = min(56, max(0, budget - 56) // 2)
    marginal = delta if kind == "B" else (1 + delta) / 2
    return exceptional * marginal + ordinary_pairs * delta


def allocation_oracle(kind: str, numerator: int, denominator: int,
                      cheap_a: bool = False) -> list:
    # Integer scores evaluate phi(1)=1, phi(7)=7, phi(8)=7+delta.
    values = (2 * denominator, 14 * denominator, 14 * denominator + 2 * numerator)
    best = [None] * 225
    best[0] = 0
    for pair_kind in (kind,) * 56 + ("A",) * 56:
        base = coefficients(parity_profile(pair_kind, (0, 0)))
        menu = []
        for gauge in MASKS:
            coeff = coefficients(parity_profile(pair_kind, gauge))
            score = sum((a - b) * v for a, b, v in zip(coeff, base, values))
            require(score.denominator == 1, "integer oracle score")
            cost = sum(gauge)
            if cheap_a and pair_kind == "A" and gauge == (1, 1):
                cost = 1
            menu.append((cost, int(score)))
        next_best = [None] * 225
        for used, score in enumerate(best):
            if score is not None:
                for cost, gain in menu:
                    if used + cost <= 224:
                        old = next_best[used + cost]
                        candidate = score + gain
                        if old is None or candidate > old:
                            next_best[used + cost] = candidate
        best = next_best
    running = 0
    for budget in range(225):
        if best[budget] is not None:
            running = max(running, best[budget])
        best[budget] = running
    return best


def check_allocation() -> int:
    comparisons = 0
    for denominator in range(2, 13):
        for numerator in range(1, denominator):
            delta = Fraction(numerator, denominator)
            for kind in ("B", "C"):
                oracle = allocation_oracle(kind, numerator, denominator)
                for budget in range(225):
                    predicted = envelope(kind, budget, delta) * (2 * denominator)
                    require(oracle[budget] == predicted, "gauge allocation optimum")
                    comparisons += 1
    mutant = allocation_oracle("B", 1, 2, cheap_a=True)
    require(mutant[112] > envelope("B", 112, Fraction(1, 2)) * 4,
            "incorrect one-gauge A tariff must be detected")
    return comparisons


def power_bounds() -> dict:
    result = {}
    scale_power = SCALE**5000
    with localcontext() as context:
        context.prec = 60
        exponent = Decimal(4983) / 5000
        for rank in range(1, 9):
            proposal = int((SCALE * Decimal(rank)**exponent).to_integral_value(rounding=ROUND_FLOOR))
            exact = rank**4983 * scale_power
            require(proposal**5000 <= exact < (proposal + 1)**5000, "rational power enclosure")
            result[rank] = (Fraction(proposal, SCALE), Fraction(proposal + 1, SCALE))
    return result


def linear_interval(coefficients_by_rank: dict, powers: dict) -> tuple:
    lower = upper = Fraction(0)
    for rank, coefficient in coefficients_by_rank.items():
        lo, hi = powers[rank]
        lower += coefficient * (lo if coefficient >= 0 else hi)
        upper += coefficient * (hi if coefficient >= 0 else lo)
    return lower, upper


def decimal_interval(interval: tuple) -> list:
    lower, upper = interval
    scale = 10**6
    integers = (lower.numerator * scale // lower.denominator,
                -((-upper.numerator * scale) // upper.denominator))
    result = []
    for number in integers:
        whole, tail = divmod(abs(number), scale)
        result.append(("-" if number < 0 else "") + f"{whole}.{tail:06d}")
    return result


def check_thresholds(profiles: dict) -> dict:
    powers = power_bounds()
    delta = (powers[8][0] - powers[7][1], powers[8][1] - powers[7][0])
    result = {}
    for kind, expected in (("B", 31), ("C", 23)):
        paid, helpers = profiles[kind]
        deficit = {rank: paid.get(rank, 0) - helpers.get(rank, 0) for rank in range(1, 9)}
        for rank, count in ((1, 28), (7, 140), (8, 84)):
            deficit[rank] -= count
        deficit_interval = linear_interval(deficit, powers)
        margins = {}
        for budget in (expected - 1, expected):
            margins[budget] = (envelope(kind, budget, delta[0]) - deficit_interval[1],
                               envelope(kind, budget, delta[1]) - deficit_interval[0])
        require(margins[expected - 1][1] < 0 < margins[expected][0], "strict gauge threshold")
        require(deficit_interval[0] > 0, "ungauged deficit premise")
        result[kind] = {"first_passing_budget": expected,
                        "deficit": decimal_interval(deficit_interval),
                        "last_failing_margin": decimal_interval(margins[expected - 1]),
                        "first_passing_margin": decimal_interval(margins[expected])}
    return result


def main() -> None:
    profiles = source_profiles()
    tables, literal_cases = check_pair_ranks()
    mask_cases = check_cut_polynomials()
    allocation_cases = check_allocation()
    thresholds = check_thresholds(profiles)
    hashes = {}
    for name in ("README.md", "PROOF.md", "verify.py", "TASK.json", "SOURCES.json", "VERIFY.json"):
        hashes[name] = sha256((PACKAGE / name).read_bytes()).hexdigest()
    receipt = {"claim_type": "scoped proof with exact finite corroboration",
               "pair_profiles": tables, "literal_rank_cases": literal_cases,
               "sign_mask_cases": mask_cases, "allocation_comparisons": allocation_cases,
               "saving": "17/5000", "thresholds": thresholds, "sha256": hashes}
    print(json.dumps(receipt, sort_keys=True))
    print("PASS_BC_CENTRAL_INPUT_GAUGE_BUDGET B=31 C=23 no_new_kappa")


if __name__ == "__main__":
    main()
