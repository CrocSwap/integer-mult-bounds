#!/usr/bin/env python3
"""Exact witnesses for a uniform width theorem, not an asymptotic experiment.

The chronological flow and least-width implementation are authenticated
predecessor inputs. New plateau, contraction and divisibility checks below
exercise the hypotheses of the written proof; they do not prove it by census.
Prepared for codyw912 with substantial OpenAI and Anthropic assistance.
Apache-2.0.
"""

from bisect import bisect_right
from collections import Counter
from hashlib import sha256
from math import gcd, lcm, prod
from pathlib import Path
from types import ModuleType
import argparse
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticated_sources():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    pins = {}
    for row in sources["files"]:
        if row["usage"] != "input":
            continue
        raw = (ROOT / row["path"]).read_bytes()
        require(sha256(raw).hexdigest() == row["sha256"], "Source bytes: " + row["path"])
        pins[row["path"]] = raw
    return pins


def load(pins, relative, name):
    raw = pins[relative]
    module = ModuleType(name)
    module.__file__ = str(ROOT / relative)
    exec(compile(raw, module.__file__, "exec"), module.__dict__)
    return module


def floor_log(n, base=2):
    require(type(n) is int and n >= 1 and type(base) is int and base >= 2,
            "Positive logarithm domain")
    exponent = 0
    while n >= base:
        n //= base
        exponent += 1
    return exponent


def ceil_log2(n):
    require(type(n) is int and n >= 1, "Positive logarithm domain")
    return (n - 1).bit_length()


def prime_support(ranks):
    result = set()
    for rank in ranks:
        require(type(rank) is int and rank >= 1, "Positive integer rank")
        p = 2
        while p * p <= rank:
            while rank % p == 0:
                result.add(p)
                rank //= p
            p += 1
        if rank > 1:
            result.add(rank)
    return sorted(result)


def semigroup(ranks, cap):
    """Enumerate distinct products, not prime-smooth numbers outside the rule."""
    require(cap >= 1, "Positive cap")
    generators = sorted(set(r for r in ranks if r > 1))
    require(generators, "Nontrivial target generator")
    seen, stack = {1}, [1]
    while stack:
        x = stack.pop()
        for r in generators:
            if r > cap // x:
                break
            y = r * x
            if y not in seen:
                seen.add(y)
                stack.append(y)
    return sorted(seen)


def signature(flow):
    """Full compressed chronological inventory, including per-cut repetitions."""
    return (
        tuple(sorted(flow["sources"].items())),
        tuple(sorted(flow["exits"].items())),
        tuple(sorted(flow["boundary_exits"].items())),
        tuple(tuple(sorted(cut.items())) for cut in flow["cuts"]),
        flow["height"], flow["units"], flow["column_mass"], flow["matched_jobs"],
    )


def valuation(n, p):
    require(n >= 1 and p >= 2, "Valuation domain")
    exponent = 0
    while n % p == 0:
        exponent += 1
        n //= p
    return exponent


def digest_integers(values):
    digest = sha256()
    for value in values:
        raw = value.to_bytes(max(1, (value.bit_length() + 7) // 8), "big")
        digest.update(len(raw).to_bytes(8, "big"))
        digest.update(raw)
    return digest.hexdigest()


def verify_case(name, targets, paid, maximum, batches, original):
    m, kmin = max(targets), min(targets)
    W, P = sum(targets.values()), sum(paid.values())
    cap = maximum // m
    gamma = semigroup(set(targets) | set(paid), cap)
    primes = prime_support(set(targets) | set(paid))
    smooth_box = prod(1 + floor_log(cap, p) for p in primes)
    require(len(gamma) <= smooth_box, "Smooth exponent-box bound")
    tau = m * ceil_log2(kmin)
    require(2 * (m - 1) ** m < m ** m, "Integer block contraction")

    by_cap, starts, changes = {}, {}, []
    prior_signature = None
    predecessor_comparisons = 0
    for c in range(1, cap + 1):
        flow = batches.direct_flow(targets, paid, m * c)
        current = signature(flow)
        if current != prior_signature:
            require(c in gamma, "Flow changes only at rank-semigroup thresholds")
            changes.append(c)
        if c in gamma:
            starts[c] = sum(flow["sources"].values())
        source_count = sum(flow["sources"].values())
        require(W <= source_count <= W * (W + P) ** flow["height"],
                "Source count bounds include all paid multiplicities")
        require(flow["height"] == floor_log(c, kmin), "Default height")
        plateau = gamma[bisect_right(gamma, c) - 1]
        require(source_count == starts[plateau], "Constant source count on plateau")
        # The older exponent-vector implementation does not aggregate collisions
        # before matching. Compare it with the polynomial predecessor explicitly.
        older = original.Flow(targets, paid, m * c).merged()
        for key in ("sources", "exits", "boundary_exits", "units", "column_mass", "matched_jobs"):
            require(flow[key] == older[key], "Two source representations: " + key)
        predecessor_comparisons += 1
        # Bound retained functools caches; no source file or algorithm is altered.
        for method in (original.Flow.column, original.Flow.points,
                       original.Flow.units, original.Flow.demand):
            method.cache_clear()
        by_cap[c] = flow
        prior_signature = current

    compiled = batches.compile_widths(targets, paid, maximum)
    widths = compiled["widths"]
    product_bound = prod(starts.values()) ** tau
    lcm_sources = lcm(*starts.values())
    depth_bound = m * (floor_log(maximum // m) + 1)
    coarser_bound = lcm_sources ** depth_bound
    # All values here are integers; the displayed log bound is an upper bound
    # in bits, not a floating-point logarithm used for acceptance.
    source_bits = ceil_log2(W) + floor_log(cap, kmin) * ceil_log2(W + P)
    bit_bound = tau * smooth_box * source_bits
    require(product_bound <= 1 << bit_bound, "Explicit logarithmic envelope")

    depths = [0] * m
    visits = [{} for _ in range(m)]
    valuation_primes = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31)
    chains = {p: [0] * m for p in valuation_primes}
    maximum_visit = 0
    exact_constraints = 0
    for n in range(m, maximum + 1):
        flow = by_cap[n // m]
        rows = batches.requirements(flow, n)
        require(all(m * e <= (m - 1) * n for e, _ in rows), "Every child contracts")
        require(all(m * (n - s) < (m - 1) * n for s in flow["sources"]),
                "Strict complement contraction")
        require(all(m * e <= max(paid) * n for e in flow["exits"]),
                "Paid-exit contraction")
        child_ranks = sorted(set(e for e, _ in rows))
        depth = 1 + max(depths[e] for e in child_ranks)
        depths.append(depth)
        require(depth <= m * (floor_log(n // m) + 1), "Integer chain-depth bound")
        here = gamma[bisect_right(gamma, n // m) - 1]
        counts = {}
        for e in child_ranks:
            for label, count in visits[e].items():
                counts[label] = max(counts.get(label, 0), count)
        counts[here] = counts.get(here, 0) + 1
        visits.append(counts)
        require(max(counts.values()) <= tau, "Bounded visits per plateau")
        maximum_visit = max(maximum_visit, max(counts.values()))
        S = sum(flow["sources"].values())
        for p in valuation_primes:
            v = valuation(S, p) + max(chains[p][e] for e in child_ranks)
            chains[p].append(v)
            require(valuation(widths[n], p) <= v, "Width valuation bounded by a chain")
            require(v <= tau * sum(valuation(s, p) for s in starts.values()),
                    "Plateau valuation envelope")
            require(v <= depth * max(valuation(s, p) for s in starts.values()),
                    "Coarse valuation envelope")
        require(product_bound % widths[n] == 0, "Sharp all-prime divisor")
        require(coarser_bound % widths[n] == 0, "Coarse all-prime divisor")
        exact_constraints += len(rows)

    require(compiled["nested_widths"][-1] % widths[-1] == 0,
            "Predecessor nested width is a multiple")
    return {
        "name": name, "maximum_rank": maximum, "targets": targets, "paid": paid,
        "rank_primes": primes, "semigroup_plateaus": len(gamma),
        "observed_flow_changes": len(changes), "distinct_source_counts": len(set(starts.values())),
        "smooth_box": smooth_box, "tau": tau, "largest_observed_plateau_visits": maximum_visit,
        "largest_chain_depth": max(depths), "coarse_depth_bound": depth_bound,
        "source_representation_comparisons": predecessor_comparisons,
        "chronological_constraints": exact_constraints,
        "least_width_bits": widths[-1].bit_length(),
        "nested_width_bits": compiled["nested_widths"][-1].bit_length(),
        "sharp_divisor_bits": product_bound.bit_length(),
        "explicit_log2_upper_bound": bit_bound,
        "width_sequence_sha256": digest_integers(widths),
        "sharp_divisor_sha256": digest_integers([product_bound]),
        "normalized_cost_agreement": True,
        "all_rank_statement_source": "README.md symbolic proof; finite checks are witnesses only",
    }


def rejection_controls(batches, original):
    controls = []
    targets, paid = {2: 1, 5: 1}, {1: 1, 3: 1}
    before, after = (batches.direct_flow(targets, paid, 5 * c) for c in (2, 3))
    require(3 not in semigroup(targets, 3) and signature(before) != signature(after),
            "Omitting paid generators must miss an actual threshold")
    controls.append({"name": "omit_paid_generator", "cap": 3,
                     "source_counts": [sum(before["sources"].values()), sum(after["sources"].values())]})

    shifted = original.Flow({2: 1, 5: 1}, {1: 2, 4: 1}, 50, height_base=5).merged()
    require(not shifted["all_sources_above_n_over_m"] and 4 in shifted["sources"],
            "Changed height invalidates the default source premise")
    controls.append({"name": "changed_height_breaks_source_bound", "n": 50,
                     "source_rank": 4, "n_over_m": 10})

    one = batches.direct_flow({2: 4, 3: 1}, {1: 6, 2: 2}, 12)
    compiled = batches.compile_widths({2: 4, 3: 1}, {1: 6, 2: 2}, 12)
    a = batches.multiplier(compiled["widths"], batches.requirements(one, 12))
    pooled = batches.multiplier(compiled["widths"], batches.requirements(one, 12, True))
    bad = next(c for c in one["cuts"] if pooled * c["count"] % compiled["widths"][c["rank"]])
    require(pooled == 175 and a == 700, "Frozen chronological counterexample")
    controls.append({"name": "aggregate_pooling_not_admitted", "pooled": pooled,
                     "required": a, "cut_rank": bad["rank"], "cut_count": bad["count"]})

    small = batches.compile_widths({2: 4, 3: 1}, {1: 6, 2: 2}, 12)["widths"]
    require(any(B % 5 == 0 for B in small), "Nontrivial prime in actual width")
    # A claimed all-prime divisor with every factor 5 erased cannot bound even
    # the smallest width-5 instance, regardless of passing other prime checks.
    sources = [sum(batches.direct_flow({2: 4, 3: 1}, {1: 6, 2: 2}, 3 * c)["sources"].values())
               for c in semigroup({1, 2, 3}, 4)]
    sharp = prod(sources) ** 3
    erased = sharp // (5 ** valuation(sharp, 5))
    require(erased % small[3] != 0, "Deleting required prime must reject")
    controls.append({"name": "omit_required_source_prime", "prime": 5, "rank": 3,
                     "width": small[3]})
    for method in (original.Flow.column, original.Flow.points,
                   original.Flow.units, original.Flow.demand):
        method.cache_clear()
    return controls


def run():
    pins = authenticated_sources()
    batches = load(pins, "research/chronological-batch-width/batches.py", "frozen_batches")
    original = load(pins, "research/direct-mixed-flow/flow.py", "frozen_direct_flow")
    raw = json.loads(pins["research/higher-moment-strictification/RESULT.json"])["invoice_oracle"]
    raw_targets = {int(k): v for k, v in raw["targets"].items()}
    raw_paid = {int(k): v for k, v in raw["paid"].items()}
    cases = [
        ("overlapping_two_rank", {2: 1, 5: 1}, {1: 2, 4: 1}, 1000),
        ("chronology_counterexample_family", {2: 4, 3: 1}, {1: 6, 2: 2}, 1000),
        ("product_collisions", {2: 1, 4: 1, 8: 1}, {1: 2, 3: 1, 7: 1}, 300),
        ("raw_p7", raw_targets, raw_paid, 1000),
        ("unit_width_degenerate", {2: 1}, {1: 1}, 100),
    ]
    reports = [verify_case(*case, batches, original) for case in cases]
    controls = rejection_controls(batches, original)
    return {"schema": "chronological-width-bound/v1", "claim_type": "conditional uniform width theorem",
            "no_new_kappa": True, "source_sha256": {k: sha256(v).hexdigest() for k, v in pins.items()},
            "cases": reports, "rejected_controls": controls,
            "theorem": "For a fixed default-height rule, log B_N = O((log N)^(d+1)); see symbolic proof."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Regenerate this package's own receipt")
    args = parser.parse_args()
    report = run()
    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    path = HERE / "RESULT.json"
    if args.write:
        path.write_text(encoded)
    else:
        require(json.loads(path.read_text()) == json.loads(encoded), "Committed receipt equality")
    print("PASS_CHRONOLOGICAL_WIDTH_BOUND", json.dumps({
        "cases": len(report["cases"]),
        "constraints": sum(c["chronological_constraints"] for c in report["cases"]),
        "controls": len(report["rejected_controls"]), "no_new_kappa": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
