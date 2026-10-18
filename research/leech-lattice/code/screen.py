#!/usr/bin/env python3
"""Scoped Leech/controller moment relaxations; no supplier or new kappa claim."""

import argparse
import ast
import hashlib
from collections import Counter
from fractions import Fraction
import json
from math import isqrt
from pathlib import Path

V = 98280
H = 25
FEATURES = 2600
FRONTIER_KAPPA = Fraction(400569730495803, 250000000000000000)
FRONTIER_ALPHA = FRONTIER_KAPPA / (1 - FRONTIER_KAPPA)
FRONTIER_HEAD = "6d0e53b66c29abd17981881a09eaff41ac862d85"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def ln_bounds(value, terms=40):
    """Exact atanh-series bounds for rational value >= 1."""
    value = Fraction(value)
    require(value >= 1, "log argument")
    exponent = 0
    while value >= 2:
        value /= 2
        exponent += 1

    def unit_bounds(x):
        z = (x - 1) / (x + 1)
        z2 = z * z
        power = z
        total = Fraction(0)
        for j in range(terms):
            total += power / (2 * j + 1)
            power *= z2
        remainder = 2 * power / ((2 * terms + 1) * (1 - z2))
        return 2 * total, 2 * total + remainder

    low, high = unit_bounds(value)
    low2, high2 = unit_bounds(Fraction(2))
    return low + exponent * low2, high + exponent * high2


def exp_bounds(low, high, terms=20):
    """Positive Taylor sums; geometric majorant of the omitted tail."""
    require(0 <= low <= high < 1, "exponential interval")

    def series(x):
        term = total = Fraction(1)
        for j in range(1, terms + 1):
            term *= x / j
            total += term
        return total, term

    lower, _ = series(low)
    upper, last = series(high)
    next_term = last * high / (terms + 1)
    upper += next_term / (1 - high / (terms + 2))
    return lower, upper


def power_bounds(base):
    low, high = ln_bounds(base)
    return exp_bounds(FRONTIER_ALPHA * low, FRONTIER_ALPHA * high)


def nominal_root(terms, denominator):
    """Floating nomination only; exact comparison is computed separately."""
    if sum(mass for mass, _ in terms) >= denominator:
        return 0.0
    low, high = 0.0, 1.0
    for _ in range(70):
        mid = (low + high) / 2
        moment = sum(mass * base ** mid for mass, base in terms)
        if moment < denominator:
            low = mid
        else:
            high = mid
    return float(format(low / (1 + low), ".12g"))


def exact_frontier_comparison(terms, denominator):
    low = high = Fraction(0)
    for mass, base in terms:
        a, b = power_bounds(base)
        low += mass * a
        high += mass * b
    low = low / denominator - 1
    high = high / denominator - 1
    scale = 10**18
    lower_scaled = low.numerator * scale // low.denominator
    upper_scaled = -((-high.numerator * scale) // high.denominator)
    verdict = ("STRICTLY_BELOW_FRONTIER" if low > 0 else
               "RELAXATION_HAS_HEADROOM" if high < 0 else "UNDECIDED")
    return dict(verdict=verdict, normalized_moment_excess_interval_scaled_1e18=
                [lower_scaled, upper_scaled])


def case(center_rank, pairs):
    stages = 2 * pairs + 1
    m = (H - 1) * stages + 1
    live = 2 * pairs * V
    cap = isqrt(m * m // 2)
    center_bill = FEATURES * center_rank
    deficit = 2 * pairs * V - stages * center_bill
    denominator = m * live
    total_mass = denominator - deficit
    fixed_mass = 2 * V * stages * (H - 1)
    residual_mass = total_mass - fixed_mass
    require(residual_mass >= 0 and cap >= H, "relaxation inputs")

    # The maximally coalesced, zero-helper paired-controller profile.
    profile = Counter({H - 1: 2 * V * stages + 2 * (pairs - 1) * V})
    profile[center_rank] += FEATURES * stages
    for j in range(1, pairs):
        rank = 2 * j * (H - 1)
        full, remainder = divmod(rank, cap)
        profile[cap] += 4 * V * full
        if remainder:
            profile[remainder] += 4 * V
    profile = {r: n for r, n in sorted(profile.items()) if n}
    require(sum(r * n for r, n in profile.items()) == total_mass, "mass identity")
    require(max(profile) <= cap, "two-level cap")
    profile_terms = [(r * n, m / r) for r, n in profile.items()]

    # Keep only mandatory local data paths. Every other paid mass is allowed
    # to form fractional children of the maximum permitted rank.
    relaxed_terms = [(fixed_mass, Fraction(m, H - 1)),
                     (residual_mass, Fraction(m, cap))]
    return dict(pairs=pairs, stages=stages, m=m, live=live, cap=cap,
                center_rank=center_rank, center_bill=center_bill,
                deficit=deficit, total_mass=total_mass,
                mandatory_local_data_mass=fixed_mass,
                relaxed_other_mass=residual_mass,
                zero_helper_fixed_profile=profile,
                zero_helper_fixed_profile_nominal_kappa=
                    nominal_root(profile_terms, denominator),
                all_other_mass_at_cap_nominal_kappa=nominal_root(
                    [(mass, float(base)) for mass, base in relaxed_terms], denominator),
                all_other_mass_at_cap_frontier_check=
                    exact_frontier_comparison(relaxed_terms, denominator))


def basis(vectors):
    rows = {}
    for x in vectors:
        for p in sorted(rows, reverse=True):
            if x >> p & 1:
                x ^= rows[p]
        if x:
            p = x.bit_length() - 1
            for q in rows:
                if rows[q] >> p & 1:
                    rows[q] ^= x
            rows[p] = x
    return tuple(rows[p] for p in sorted(rows, reverse=True))


def perp(vectors, h=25):
    rows = basis(vectors)
    pivots = {r.bit_length() - 1 for r in rows}
    out = []
    for j in range(h):
        if j in pivots:
            continue
        x = 1 << j
        for row in rows:
            if row >> j & 1:
                x |= 1 << (row.bit_length() - 1)
        out.append(x)
    return basis(out)


def distance(a, b):
    return 2 * len(basis(a + b)) - len(basis(a)) - len(basis(b))


def fiber(size):
    ports = {1: [1], 2: [1, 7], 4: [1, 7, 25, 31]}[size]
    u = basis(ports)
    f = tuple(1 << j for j in range(25))
    up = perp(u)
    gram = [[(x & y).bit_count() % 2 for y in ports] for x in ports]
    require(all(all(row) for row in gram), "all-ones Gram")
    walsh = [[(-1)**((i & j).bit_count()) for j in range(size)] for i in range(size)]
    square = [[sum(walsh[i][k] * walsh[k][j] for k in range(size))
               for j in range(size)] for i in range(size)]
    require(square == [[size * (i == j) for j in range(size)]
                              for i in range(size)], "Walsh inverse")
    source = [distance((ports[0],), u), distance(u, f)]
    target = [distance((), up), distance(up, perp((ports[0],)))]
    relabeled_source = [distance((ports[0],), u), distance(u, (ports[-1],)),
                        distance((ports[-1],), f)]
    require(sum(source) == sum(target) == 24, "mass preserving thick paths")
    return dict(size=size, ports=ports, common_frame=list(u), rank=len(u),
                binary_gram=gram, restricted_gram_rank=1,
                radical_dimension=len(u)-1, walsh=walsh,
                inverse_walsh_denominator=size,
                source_path_ranks=source, target_path_ranks=target,
                relabeled_source_path_ranks=relabeled_source,
                both_side_relabel_extra_per_port=2*(sum(relabeled_source)-24))


def moment_case(pairs, center_rank, transformed_sides, port_counts):
    v = sum(port_counts.values())
    stages = 2 * pairs + 1
    m = 24 * stages + 1
    cap = isqrt(m*m//2)
    denominator = m * 2 * pairs * v
    center_bill = 2600 * center_rank
    deficit = 2 * pairs * v - stages * center_bill
    mandatory = Counter({24: (2-transformed_sides)*v*stages})
    for active_blocks, count in port_counts.items():
        for rank in (active_blocks-1, 25-active_blocks):
            if rank:
                mandatory[rank] += transformed_sides * count * stages
    mandatory = {r: n for r, n in sorted(mandatory.items()) if n}
    mass = sum(r*n for r, n in mandatory.items())
    require(mass == 2*v*stages*24, "unchanged mandatory data rank mass")
    other = denominator - deficit - mass
    terms = [(r*n, Fraction(m, r)) for r, n in mandatory.items()]
    terms.append((other, Fraction(m, cap)))
    return dict(pairs=pairs, stages=stages, m=m, cap=cap,
                center_rank=center_rank, center_bill=center_bill,
                transformed_sides=transformed_sides, mandatory_profile=mandatory,
                mandatory_mass=mass, other_mass=other, deficit=deficit,
                nominal_kappa=nominal_root(
                    [(a, float(b)) for a, b in terms], denominator),
                exact_frontier_comparison=exact_frontier_comparison(terms, denominator))



def main():
    parser = argparse.ArgumentParser()
    root = Path(__file__).resolve().parents[1]
    parser.add_argument("--out", type=Path, default=root / "evidence/SCREEN.json")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    sources = json.loads((root / "sources/FRONTIER-SOURCES.json").read_text())
    pr_blob = (root / "sources/PR588.json").read_bytes()
    require(hashlib.sha256(pr_blob).hexdigest() == sources["files"]["PR588.json"], "PR588 source hash")
    pr = json.loads(pr_blob)
    require(pr["headRefOid"] == FRONTIER_HEAD, "PR588 exact head")
    require("0.001602278921983212" in pr["title"], "PR588 title target")
    baseline = [case(rank, k) for rank in (24, 25) for k in range(1, 51)]
    for row in baseline:
        if row["center_rank"] == 25:
            require(row["all_other_mass_at_cap_frontier_check"]["verdict"] ==
                    "STRICTLY_BELOW_FRONTIER", "full-rank center relaxation")
    counts = {1: 360, 2: 5760, 3: 92160}
    cases = [moment_case(k, rank, sides, counts)
             for sides in (1, 2) for rank in (24, 25) for k in range(1, 51)]
    summaries = []
    for sides in (1, 2):
        for rank in (24, 25):
            rows = [x for x in cases if x["center_rank"] == rank and x["transformed_sides"] == sides]
            best = max(rows, key=lambda x:x["nominal_kappa"])
            failed = sum(x["exact_frontier_comparison"]["verdict"] == "STRICTLY_BELOW_FRONTIER" for x in rows)
            if sides == 2:
                require(failed == 50, "every two-sided case must fail target")
            summaries.append(dict(transformed_sides=sides, center_rank=rank,
                best_pairs=best["pairs"], best_nominal_kappa=best["nominal_kappa"],
                exact_below_frontier_count=failed))
    gather_cost = sum(count * (active - 1) for active, count in counts.items())
    require(gather_cost == 190080 > V, "full-fiber source clone cost")
    clone_rows = [dict(pairs=k, stages=2*k+1, effective_center_bill=62400+gather_cost,
                      deficit=2*k*V-(2*k+1)*(62400+gather_cost)) for k in range(1, 51)]
    require(all(x["deficit"] < 0 for x in clone_rows), "clone rank deficit")
    result = dict(status="PASS_SCOPED_LEECH_AND_TURYN_MOMENT_SCREENS",
        frontier=dict(pr=588, head=FRONTIER_HEAD, kappa=str(FRONTIER_KAPPA),
                      alpha=str(FRONTIER_ALPHA), freshly_replayed=False),
        geometry_parameters=dict(v=V, h=H, polynomial_features=FEATURES,
                                 port_counts_by_active_blocks=counts),
        parameter_scope="Center ranks24/25 are supplied scenarios. This script does not construct the dyadic factorization or a scalar side supplier.",
        engine="Fraction log/exp intervals (40/20 terms) at the nominal target; floating roots rounded to12 significant digits are discovery estimates only",
        pair_range=[1,50], baseline=baseline,
        fibers=[fiber(n) for n in (1,2,4)], turyn_summaries=summaries, turyn_cases=cases,
        source_clone=dict(extra_rank_per_local_call=gather_cost,
            proof="Even with zero center bill, D=(L-1)*v-L*gather_cost is negative for every positive L because gather_cost>v.",
            cases=clone_rows),
        both_side_relabel_extra_rank_per_local_call=4*gather_cost,
        scope="Paired controller, original individual-port endpoints, supplied center bill, and floor(m/sqrt2) child cap. Turyn bounds additionally require full common-frame Walsh mixing on every sign fiber. Partial transforms and other interfaces are not excluded.")
    serialized = json.dumps(result, indent=2)+"\n"
    if args.verify:
        require(json.loads(args.out.read_text()) == json.loads(serialized), "stored SCREEN.json")
    else:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(serialized)
    print(json.dumps(dict(status=result["status"], turyn_summaries=summaries)))


if __name__ == "__main__":
    main()
