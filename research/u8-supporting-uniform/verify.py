"""Exact finite certificate for the U8 supporting inequality on 0 < b <= 1/3.

Standard library only. No retained search, moment or interval engine is imported.
The continuum step is the analytic argument in PROOF.md, not finite sampling.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WIDTHS = (4, 5, 7, 8, 9)
PRICES = (-1, -20, -8, -2, 4)
CAPACITIES = {8: (672, 2), 16: (448, 4), 32: (448, 8), 48: (448, -13)}
HELPERS = (80, 32, 54, 122, 216)
SCALE = 10**12
BASE = "407d52ff15b2217b6e22bce44728b4c3907b6515"


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def cube_floor(n: int) -> int:
    """Floor cube root by integer bisection, with no floating-point estimate."""
    require(n >= 0, "cube root input must be nonnegative")
    lo, hi = 0, 1 << ((n.bit_length() + 2) // 3)
    while hi - lo > 1:
        middle = (lo + hi) // 2
        if middle**3 <= n:
            lo = middle
        else:
            hi = middle
    return lo


def root_bracket(rank: int, scale: int = SCALE) -> tuple[int, int]:
    """Numerators enclosing (48/rank)^(1/3) with denominator scale."""
    require(0 < rank <= 48 and scale > 0, "root bracket domain")
    lo = cube_floor(48 * scale**3 // rank)
    hi = lo + 1
    require(rank * lo**3 <= 48 * scale**3 < rank * hi**3,
            "invalid exact cube-root enclosure")
    return lo, hi


def bin_census() -> dict:
    """Multiply five truncated bivariate generating-function factors.

    Product_w sum_{j=0}^{floor(48/w)} x^(w*j) y^(price(w)*j).
    Each coefficient counts width-count vectors, not orderings of helpers.
    Negative powers of y are dictionary keys. Truncating x above 48 is exact
    because all widths are positive. Keep one lexicographic witness per key.
    """
    polynomial = {(0, 0): (1, ())}
    for width, price in zip(WIDTHS, PRICES):
        product = {}
        for (fill, value), (multiplicity, witness) in polynomial.items():
            for count in range((48 - fill) // width + 1):
                key = (fill + width * count, value + price * count)
                vector = witness + (count,)
                old_count, old_witness = product.get(key, (0, vector))
                product[key] = (old_count + multiplicity, min(old_witness, vector))
        polynomial = product

    upper, witnesses, counts = {}, {}, {}
    for cap, (_, bonus) in CAPACITIES.items():
        counts[cap] = 0
        for (fill, value), (multiplicity, vector) in sorted(polynomial.items()):
            if fill > cap:
                continue
            counts[cap] += multiplicity
            rank, price = cap - fill, value + bonus
            if rank not in upper or price > upper[rank]:
                upper[rank] = price
                witnesses[rank] = {"capacity": cap, "counts": list(vector)}
    require(sum(counts.values()) == 1163, "complete 1163-pattern census")
    require((upper[0], upper[1], upper[48]) == (0, 19, -13), "boundary prices")
    for rank, witness in witnesses.items():
        vector, cap = witness["counts"], witness["capacity"]
        require(cap - sum(w * n for w, n in zip(WIDTHS, vector)) == rank,
                "witness residual")
        require(CAPACITIES[cap][1] + sum(p * n for p, n in zip(PRICES, vector)) == upper[rank],
                "witness price")
    return {"upper": upper, "witnesses": witnesses, "counts": counts}


def source_pins(root: Path = ROOT) -> dict:
    pins = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    require(pins["base_commit"] == BASE, "source base commit")
    require(set(pins["files"]) == {
        "research/complex-t21-owner-bound/PROOF.md",
        "research/complex-t37-owners/ALL-T-PROOF.md",
        "research/complex-t37-owners/independent/all_t_bound.py",
        "research/complex-t21-owners/data/CLAIM.json",
        "research/owner-profile-uniform/README.md",
    }, "complete source-pin inventory")
    for relative, expected in pins["files"].items():
        path = root / relative
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        require(actual == expected, "source drift: " + relative)
    return pins


def build_certificate() -> dict:
    census = bin_census()
    upper = census["upper"]
    mass = sum(cap * n for cap, (n, _) in CAPACITIES.items()) - 9 * sum(
        w * n for w, n in zip(WIDTHS, HELPERS))
    signed = sum(n * bonus for n, bonus in CAPACITIES.values()) + 9 * sum(
        p * n for p, n in zip(PRICES, HELPERS))
    require((mass, signed, 48 * signed + 13 * mass) == (14382, -3892, 150),
            "per-replica mass and signed-price accounting")
    require(Q(150, 925) == Q(6, 37), "rank-one equality demand")
    require(48 * 11086 + 6 == 37 * mass, "T37 equality profile mass")
    require(-13 * 11086 + 19 * 6 == 37 * signed, "T37 equality profile price")

    root1_lo, root1_hi = root_bracket(1)
    denominator = root1_hi - SCALE
    require(denominator > 0, "positive ratio denominator")
    rows, margins = [], {}
    for rank in sorted(upper):
        row = {"rank": rank, "upper_price": upper[rank],
               "credit": 48 * upper[rank] + 13 * rank,
               "maximizing_bin": census["witnesses"][rank]}
        if 1 < rank < 48:
            lo, hi = root_bracket(rank)
            require(lo >= SCALE, "nonnegative ratio numerator")
            # Lower numerator / upper positive denominator is a lower bound.
            # Credit is subtracted exactly; its sign never affects rounding.
            margin = Q(925 * rank * (lo - SCALE), denominator) - row["credit"]
            require(margin > 554, "uniform strict margin failed at rank " + str(rank))
            row.update(cube_root_numerators=[lo, hi],
                       scaled_margin_lower=str(margin))
            margins[rank] = margin
        rows.append(row)
    require(set(margins) == set(upper) - {0, 1, 48}, "all strict ranks covered")
    worst = min(margins, key=margins.get)

    # Exact counterexample to extending the same supporting line to b=1.
    # c_1(r)/c_1(1) = (48-r)/47; the cube-root proof is not used here.
    false_extension = Q(925 * (48 - 32), 47) - (48 * upper[32] + 13 * 32)
    require(false_extension == Q(-22800, 47) < 0, "b=1 scope counterexample")
    return {
        "status": "PASS_U8_SUPPORTING_UNIFORM",
        "base_commit": BASE,
        "method": "generating-function census and integer cube-root endpoint bounds",
        "exponent_interval": "0 < b <= 1/3",
        "root_denominator": SCALE,
        "cube_root_48_numerators": [root1_lo, root1_hi],
        "legal_patterns_by_capacity": {str(k): v for k, v in census["counts"].items()},
        "legal_patterns": sum(census["counts"].values()),
        "attainable_residuals": sorted(upper),
        "strict_ranks_checked": len(margins),
        "per_replica": {"residual_mass": mass, "signed_price": signed, "credit_required": 150},
        "support": {"rank_one_credit": 925, "scaled_uniform_margin": 554,
                    "worst_endpoint_rank": worst,
                    "minimum_scaled_margin_lower": str(margins[worst])},
        "equality_profile": {"minimum_replicas": 37, "rank_1": 6, "rank_48": 11086},
        "scope_counterexample": {"exponent": "1", "rank": 32,
                                 "scaled_margin": str(false_extension)},
        "rows": rows,
        "scope": "Exact finite endpoint certificate plus a written continuum proof; fixed whole-helper ledger only. No owner feasibility, outer assembly, new kappa, or full multiplication theorem is certified.",
    }


def check_certificate(candidate: dict, expected: dict) -> None:
    require(candidate == expected, "certificate differs from complete exact recomputation")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, default=HERE / "CERTIFICATE.json")
    parser.add_argument("--write", type=Path, help="write regenerated certificate to a new file")
    args = parser.parse_args()
    source_pins()
    expected = build_certificate()
    if args.write:
        with args.write.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(expected, indent=2, sort_keys=True) + "\n")
    else:
        candidate = json.loads(args.certificate.read_text(encoding="utf-8"))
        check_certificate(candidate, expected)
    print("PASS_U8_SUPPORTING_UNIFORM: 1163 bin patterns; "
          f"{expected['strict_ranks_checked']} strict ranks; 0 < b <= 1/3; scaled margin > 554")


if __name__ == "__main__":
    main()
