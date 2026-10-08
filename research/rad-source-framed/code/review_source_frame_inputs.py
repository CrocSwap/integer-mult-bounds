#!/usr/bin/env python3
"""Independent exact generic-bit arithmetic for the new nonzero-auxiliary-source h53 graph.

This checker does not reconstruct the finite graph. Its certificate explicitly
keeps the separate finite and all-size transfer review as an input obligation.
No candidate selector or new characteristic producer is imported.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import resource
import time

from review_parameter_audit import log_integer


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def logs(n):
    lower, upper = log_integer(n, 160)
    scale = 2**448
    lo = Q(lower.numerator * scale // lower.denominator, scale)
    hi = Q(-((-upper.numerator * scale) // upper.denominator), scale)
    require(lo <= lower <= upper <= hi, "Outward exact logarithm failed")
    return lo, hi


def reconstruct(row):
    h = row["h"]
    logical = row["final"]["logical"]
    c, q, links = logical["additions"], logical["partial_outputs"], row["final"]["links"]
    roles = c + q - links
    require(h == 53 and roles == 529181 == row["compiled_roles"] == row["final"]["roles"],
            "Wrong selected compound graph or register-retention budget")
    require(q == 3 * comb(h, 3), "Actual designated output count differs")
    v, m = comb(h, 3), h**3
    N = v**3
    W = 2*N + 2*v*v*(roles+h)
    L = 3*v*v*h*h
    counts = dict(h=h, side_roles=roles, v=v, m=m, N=N, W=W, L=L,
                  D=N-2*L, s=W*m-N+2*L)
    raw = row["exact_counts"]
    for key in ("m", "N", "W", "L", "D", "s"):
        require(Q(raw[key]) == counts[key], "Actual physical count differs: " + key)
    total_rank = total_edges = 0
    for name, category in raw["categories"].items():
        histogram = {int(r): int(n) for r, n in category["rank_histogram"].items()}
        require(all(0 <= r <= m and n >= 0 for r, n in histogram.items()),
                "Invalid actual residual histogram: " + name)
        rank = sum(r*n for r, n in histogram.items())
        edges = sum(histogram.values())
        require(rank == category["rank_sum"] and edges == category["edge_count"],
                "Physical histogram framing differs: " + name)
        total_rank += rank
        total_edges += edges
    require(total_rank == counts["s"], "Full actual histogram total differs")
    G = 3*v*v*(4*(c+roles-v)+20*v)
    E = 64*(W+m+1)**3
    charged = 2*G*W*W+4*counts["s"]+4*W+4
    guard = row["literal_scalar_guard"]
    require(all(Q(guard[k]) == x for k, x in
                dict(G=G, E=E, depth=charged, slack=E-charged).items()) and E > charged,
            "Actual compound scalar count or coefficient guard differs")
    return counts, dict(additions=c, designated_outputs=q, retained_links=links,
                        roles=roles, actual_rank_mass=total_rank,
                        actual_edges=total_edges, scalar_gates=G, E=E,
                        literal_depth=charged, strict_guard_slack=E-charged)


def characteristic(base, protected):
    n = dict(base)
    h, v, m, R = (n[k] for k in ("h", "v", "m", "side_roles"))
    require(protected in (0, 1, 2), "Only independently reviewed zero/one/two-star chart")
    n["L"] -= protected*3*v*v
    n["D"] += protected*6*v*v
    n["s"] -= protected*6*v*v
    require(n["s"] == n["W"]*m-n["D"] and 0 < n["D"] and n["s"] < m**5,
            "Modified exact physical budget fails")
    deficits = dict(middle=h, joined=2*h, data=h*h+h-1)
    copies = dict(middle=(R+h)*v*v, joined=(R+h)*v*v, data=2*n["N"])
    runs = {name: m-2*d for name, d in deficits.items()}
    family_ranks = {name: copies[name]*(m-deficits[name]) for name in deficits}
    hist = Counter()
    for name, r in runs.items():
        hist[r] += copies[name]
    credited = sum(r*c for r, c in hist.items())
    individual = n["s"]-credited
    require(0 < individual and sum(family_ranks.values()) < n["s"],
            "Changed credited families overlap or exhaust the rank budget")
    lm = logs(m)[1]
    log_data = {str(r): [str(x) for x in logs(r)] for r in hist}
    M = sum(r*c*Q(log_data[str(r)][0]) for r, c in hist.items())
    linear = n["s"]*lm-M
    quadratic = Q(n["s"], 2)*lm*lm
    require(linear > 0, "Normalized characteristic is not decreasing near zero")

    def gap(a):
        require(0 <= a*lm < 1, "Positive-exponential Taylor range fails")
        return n["D"]-a*linear-a*a*quadratic/(1-a*lm)

    scale = 10**24
    low, high = 0, 10**19
    require(gap(Q(high, scale)) < 0, "Root bracket is not discriminating")
    while high-low > 1:
        mid = (low+high)//2
        if gap(Q(mid, scale)) > 0:
            low = mid
        else:
            high = mid
    a = Q(low, scale)
    require(gap(a) > 0 >= gap(Q(low+1, scale)), "Strict rational saving bracket fails")
    largest = max(runs.values())
    depth = 1
    while m**depth <= 2*largest**depth:
        depth += 1
    require(depth == 974 and m**depth > 2*largest**depth
            and m**(depth-1) <= 2*largest**(depth-1), "Exact new halving degree differs")
    Wbits = n["W"].bit_length()
    require(2**(Wbits-1) <= n["W"] < 2**Wbits, "New wire-stock logarithm differs")
    product_coefficient = Q(Wbits*depth+41*272)*(2+Q(1,25))
    degree = 1000*(-(-product_coefficient.numerator//(1000*product_coefficient.denominator)))
    require(degree == 123000 and product_coefficient < degree, "Joint row product does not fit")
    return dict(protected_centers=protected, counts=n, saving=str(a), tau=str(1-a),
                kernel_dimensions=deficits, family_multiplicities=copies,
                family_ranks=family_ranks, grouped_runs=runs,
                long_run_histogram={str(r):c for r,c in sorted(hist.items())},
                long_grouped_rank=credited, individual_pivot_count=individual,
                log_m_upper=str(lm), log_intervals=log_data,
                rank_log_moment_lower=str(M), normalized_linear_upper=str(linear),
                normalized_quadratic_upper=str(quadratic), strict_gap=str(gap(a)),
                next_grid_point_nonpositive_gap=str(gap(Q(low+1,scale))),
                maximum_child=largest, halving_degree=depth, wire_log2_ceiling=Wbits,
                exact_joint_row_coefficient=str(product_coefficient), row_degree=degree,
                reservoir_slope=4*degree, log_terms=160, outward_dyadic_bits=448,
                giant_native_table_and_admissible_prime_materialized=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--protected-review", type=Path, required=True)
    parser.add_argument("--protected-report", type=Path, required=True)
    parser.add_argument("--two-protected-review", type=Path, required=True)
    parser.add_argument("--two-protected-report", type=Path, required=True)
    parser.add_argument("--source-frame-review", type=Path, required=True)
    parser.add_argument("--incidence-review", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), "Choose a fresh output path")
    start = time.monotonic()
    require(digest(args.candidate) == "ca6ce8791888f67474b522a955bbd5465b73b94ee117b8b9a3709a97ff2a767e",
            "Frozen selected compound producer bytes differ")
    require(digest(args.protected_report) == "c096bf8b16a8e7871f8a44d8fd3c8ea9476f03d0142dfd9cd50b191a041781f9",
            "Written one-star all-size transfer changed")
    protected = json.loads(args.protected_review.read_text())
    require(protected["status"] == "PASS" and any(
        entry["h"] == 53 and entry["all_source_containments_and_normal_target_orthogonalities_exact"]
        for entry in protected["metric_inputs"]), "One-star review omits the new ground")
    two = json.loads(args.two_protected_review.read_text())
    require(digest(args.two_protected_report) == "9a20c7427acedfbb1de5b75dd03c52f94e51fd672fb59b071fce2f134316128f"
            and two["status"] == "PASS INDEPENDENT TWO DISJOINT PROTECTED CENTERS"
            and two["all_size_transfer_accepted"], "Two-star all-size transfer missing or changed")
    candidate = json.loads(args.candidate.read_text())
    require(candidate["candidate_id"] == "439f31afa89e659a2bacb35a7d1474ba67e0410369a5d9cca22dcee4359ff741"
            and candidate["checked"]["compiled_sha256"]
            == "c7eed569818909583b4df314dd0e05d809c2254905cebf6f6d405a3296f80484"
            and candidate["selection_scope"] == "Exact greedy integer capacity/formal-child subset in a genuinely different earlier parent order; no MILP or optimality claim",
            "Wrong selected direct-first-allocation finite identity")
    n, budget = reconstruct(candidate)
    source = json.loads(args.source_frame_review.read_text())
    incidence = json.loads(args.incidence_review.read_text())
    require(digest(args.source_frame_review) == "a15f9c1aa618afd435861e7f2e13c7f3a2056c8d46c0be8d49726ab5e77bd252"
            and source["status"] == "PASS INDEPENDENT NONZERO AUXILIARY SOURCE TRANSFER COMPONENT",
            "Independent new all-size source-frame component changed")
    require(digest(args.incidence_review) == "9908951fc8f06f53d3be78c01c05d225745e64d0ac013f6fca0e5e87079b37a6"
            and incidence["candidate_id"] == candidate["candidate_id"]
            and incidence["compiled_sha256"] == candidate["checked"]["compiled_sha256"]
            and incidence["actual_side_endpoints"]["every_actual_physical_role_has_D0_first_and_D1_last"]
            and incidence["actual_side_endpoints"]["early_or_late_retained_gate_exclusions"] == 0
            and incidence["centers"]["exclusions"] == 0, "Actual source-frame incidence not verified")
    hist = Counter({int(r): int(c) for r,c in candidate["exact_counts"]["rank_histogram"].items()})
    count = (n["side_roles"]+n["h"])*n["v"]**2
    for r,c in ((n["h"]**2-n["h"],-count),(n["m"]-n["h"]**2,-count),
                (0,count),(n["m"]-n["h"],count)): hist[r]+=c
    hist = Counter({r:c for r,c in hist.items() if c})
    require(all(c>=0 for c in hist.values()) and sum(r*c for r,c in hist.items()) == n["s"]
            and sum(hist.values()) == candidate["exact_counts"]["edge_count"]
            and {str(r):c for r,c in hist.items()} ==
                {r:c for r,c in incidence["normal"]["rank_histogram"].items() if c},
            "New entire actual normal histogram or boundary rank conservation differs")
    own_variants = [characteristic(n,j) for j in (0,1,2)]
    for own, peer in zip(own_variants, source["variants"], strict=True):
        require(own["protected_centers"] == peer["protected_centers"]
                and Q(own["saving"]) == Q(peer["saving"])
                and own["halving_degree"] == peer["least_halving_degree"] == 974
                and own["row_degree"] == peer["joint_row_degree"] == 123000,
                "Independent new source-frame characteristic or depth differs")
    result = dict(status="PASS independent source-frame generic characteristic arithmetic",
                  campaign="20261007T222521Z", generated_utc=datetime.now(timezone.utc).isoformat(),
                  input_sha256={str(p):digest(p) for p in
                                (args.candidate,args.protected_review,args.protected_report,
                                 args.two_protected_review,args.two_protected_report,
                                 args.source_frame_review,args.incidence_review)},
                  source_sha256=digest(Path(__file__)),
                  dependency_sha256={"review_parameter_audit.py":digest(Path(__file__).with_name("review_parameter_audit.py"))},
                  candidate_id=candidate["candidate_id"],
                  compiled_sha256=candidate["checked"]["compiled_sha256"],
                  actual_physical_budget=budget, variants=own_variants,
                  exact_relocated_normal_histogram={str(r):c for r,c in sorted(hist.items())},
                  eligible_middle_auxiliaries=count,
                  wall_seconds=time.monotonic()-start,
                  peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  limitations=["Independent final finite reconstruction and complete transfer are separate obligations",
                               "Arithmetic does not instantiate the giant rational native table or new odd prime",
                               "Zero and separately reviewed one/two-star F2-payload variants are included",
                               "No complete multiplication exponent is claimed by this component"])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    for row in result["variants"]:
        print("PASS",row["protected_centers"],row["saving"],row["row_degree"],flush=True)


if __name__ == "__main__":
    main()
