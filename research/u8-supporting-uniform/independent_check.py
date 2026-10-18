"""Independent recursive census and Newton-root check of the U8 certificate.

Imports only the Python standard library. All checks remain active under -O.
The analytic continuum argument is supplied separately by PROOF.md.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "407d52ff15b2217b6e22bce44728b4c3907b6515"
WIDTHS = (4, 5, 7, 8, 9)
PRICES = (-1, -20, -8, -2, 4)
BINS = ((8, 672, 2), (16, 448, 4), (32, 448, 8), (48, 448, -13))
HELPERS = (80, 32, 54, 122, 216)
D = 10**12


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def newton_cube_root(n: int) -> int:
    """Integer Newton iteration from an upper bound; return floor(cuberoot(n))."""
    need(type(n) is int and n >= 0, "nonnegative integer root input")
    if n < 2:
        return n
    current = 1 << ((n.bit_length() + 2) // 3)
    while True:
        following = (2 * current + n // (current * current)) // 3
        if following >= current:
            need(current**3 <= n < (current + 1)**3, "Newton root postcondition")
            return current
        current = following


def recursive_census() -> tuple[dict, dict, set]:
    upper, totals, patterns = {}, {}, set()
    for capacity, _, bonus in BINS:
        totals[capacity] = 0

        def visit(index: int, space: int, price: int, counts: tuple) -> None:
            if index == len(WIDTHS):
                totals[capacity] += 1
                patterns.add((capacity, counts))
                upper[space] = max(upper.get(space, price), price)
                return
            for count in range(space // WIDTHS[index] + 1):
                visit(index + 1, space - count * WIDTHS[index],
                      price + count * PRICES[index], counts + (count,))

        visit(0, capacity, bonus, ())
    need(totals == {8: 6, 16: 27, 32: 215, 48: 915}, "recursive census counts")
    need(len(patterns) == sum(totals.values()) == 1163, "recursive pattern coverage")
    need(sorted(upper) == list(range(42)) + [43, 44, 48], "attainable ranks")
    need((upper[0], upper[1], upper[48]) == (0, 19, -13), "boundary prices")
    return upper, totals, patterns


def check_pins() -> None:
    pins = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    need(pins["base_commit"] == BASE, "source base commit")
    expected_paths = {
        "research/complex-t21-owner-bound/PROOF.md",
        "research/complex-t37-owners/ALL-T-PROOF.md",
        "research/complex-t37-owners/independent/all_t_bound.py",
        "research/complex-t21-owners/data/CLAIM.json",
        "research/owner-profile-uniform/README.md",
    }
    need(set(pins["files"]) == expected_paths, "complete source-pin inventory")
    for relative, expected in pins["files"].items():
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        need(actual == expected, "source drift: " + relative)


def check_bracket(pair: list, rank: int) -> tuple[int, int]:
    need(isinstance(pair, list) and len(pair) == 2, "two root endpoints")
    lower, higher = pair
    need(type(lower) is int and type(higher) is int and higher == lower + 1,
         "consecutive integer root endpoints")
    need(0 <= lower and rank * lower**3 <= 48 * D**3 < rank * higher**3,
         "certificate root bracket at rank " + str(rank))
    return lower, higher


def check(candidate: dict) -> None:
    check_pins()
    upper, counts, patterns = recursive_census()
    need(candidate["status"] == "PASS_U8_SUPPORTING_UNIFORM", "certificate status")
    need(candidate["base_commit"] == BASE, "certificate base commit")
    need(candidate["exponent_interval"] == "0 < b <= 1/3", "exponent scope")
    need(candidate["root_denominator"] == D, "root denominator")
    need(candidate["legal_patterns"] == 1163, "certificate pattern count")
    need(candidate["legal_patterns_by_capacity"] == {str(k): v for k, v in counts.items()},
         "certificate per-capacity counts")
    need(candidate["attainable_residuals"] == sorted(upper), "certificate rank coverage")
    rows = candidate["rows"]
    need([row["rank"] for row in rows] == sorted(upper), "complete ordered unique rows")
    root48_lower, root48_upper = check_bracket(candidate["cube_root_48_numerators"], 1)
    need(root48_lower == newton_cube_root(48 * D**3), "independent root of 48")
    need(root48_upper == 3634241185665, "proof's root upper numerator")
    need(root48_upper > D, "positive ratio denominator")

    margins, proof_integers = {}, {}
    bonuses = {capacity: bonus for capacity, _, bonus in BINS}
    for row in rows:
        rank = row["rank"]
        credit = 48 * upper[rank] + 13 * rank
        need(row["upper_price"] == upper[rank] and row["credit"] == credit,
             "independent price and credit at rank " + str(rank))
        witness = row["maximizing_bin"]
        capacity, vector = witness["capacity"], tuple(witness["counts"])
        need((capacity, vector) in patterns, "legal maximizing witness")
        need(capacity - sum(w * n for w, n in zip(WIDTHS, vector)) == rank,
             "witness residual rank")
        need(bonuses[capacity] + sum(p * n for p, n in zip(PRICES, vector)) == upper[rank],
             "witness attains independent maximum")
        expected_keys = {"rank", "upper_price", "credit", "maximizing_bin"}
        if rank not in (0, 1, 48):
            expected_keys |= {"cube_root_numerators", "scaled_margin_lower"}
            lower, _ = check_bracket(row["cube_root_numerators"], rank)
            need(lower >= D, "nonnegative endpoint numerator")
            margin = Fraction(925 * rank * (lower - D), root48_upper - D) - credit
            need(row["scaled_margin_lower"] == str(margin) and margin > 554,
                 "certificate's exact margin at rank " + str(rank))
            margins[rank] = margin
            # Different algebraic radicand from the primary certificate:
            # q(r) = (cuberoot(48*r*r)-r)/(cuberoot(48)-1).
            root = newton_cube_root(48 * rank * rank * D**3)
            need(root > rank * D, "positive independent numerator")
            value = 925 * (root - rank * D) - (credit + 554) * (root48_upper - D)
            need(value > 0, "independent proof inequality at rank " + str(rank))
            proof_integers[rank] = value
        need(set(row) == expected_keys, "row fields at rank " + str(rank))
    need(len(margins) == candidate["strict_ranks_checked"] == 42, "42 strict inequalities")
    need(min(proof_integers, key=proof_integers.get) == 44
         and proof_integers[44] == 1794386594565, "proof's minimum exact integer")
    need(candidate["support"] == {
        "rank_one_credit": 925, "scaled_uniform_margin": 554,
        "worst_endpoint_rank": min(margins, key=margins.get),
        "minimum_scaled_margin_lower": str(min(margins.values()))}, "support summary")

    mass = sum(c * n for c, n, _ in BINS) - 9 * sum(w * n for w, n in zip(WIDTHS, HELPERS))
    signed = sum(n * p for _, n, p in BINS) + 9 * sum(p * n for p, n in zip(PRICES, HELPERS))
    need((mass, signed, 48 * signed + 13 * mass) == (14382, -3892, 150), "ledger arithmetic")
    need(candidate["per_replica"] == {"residual_mass": mass, "signed_price": signed,
                                        "credit_required": 150}, "certificate ledger")
    rank_one = Fraction(150, 925)
    rank48 = (mass - rank_one) / 48
    need(rank_one == Fraction(6, 37) and rank48 == Fraction(11086, 37), "equality arithmetic")
    need(candidate["equality_profile"] == {"minimum_replicas": rank_one.denominator,
         "rank_1": rank_one.numerator, "rank_48": rank48.numerator}, "integer equality profile")
    false_margin = Fraction(925 * (48 - 32), 47) - (48 * upper[32] + 13 * 32)
    need(false_margin == Fraction(-22800, 47) < 0, "outside-interval counterexample")
    need(candidate["scope_counterexample"] == {"exponent": "1", "rank": 32,
         "scaled_margin": str(false_margin)}, "certificate scope counterexample")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, default=HERE / "CERTIFICATE.json")
    args = parser.parse_args()
    check(json.loads(args.certificate.read_text(encoding="utf-8")))
    print("PASS_U8_SUPPORTING_INDEPENDENT: 1163 recursive patterns; 42 exact inequalities; "
          "proof minimum 1794386594565 at rank 44")


if __name__ == "__main__":
    main()
