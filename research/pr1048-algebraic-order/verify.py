#!/usr/bin/env python3
"""Recompute the algebraic certificate and bounded independent cross-check.

Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path

from compare import Profile, crossing, difference, root_order
import oracle

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SEED = 78


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def source_check():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    checked = {}
    for entry in sources["files"]:
        if entry["usage"] == "input":
            digest = sha256((ROOT / entry["path"]).read_bytes()).hexdigest()
            require(digest == entry["sha256"], "source drift: " + entry["path"])
            checked[entry["path"]] = digest
    return sources["base_commit"], checked


def independent_order(a, b, intervals=None):
    pa = oracle.polynomial(a.counts, a.roles)
    pb = oracle.polynomial(b.counts, b.roles)
    ia = None if intervals is None else intervals[a]
    ib = None if intervals is None else intervals[b]
    return oracle.root_order(pa, pb, ia, ib)


def agree(a, b, claimed=None, intervals=None):
    actual = root_order(a, b) if claimed is None else claimed
    expected = independent_order(a, b, intervals)
    require(actual == expected, "algebraic comparison disagrees with independent oracle")
    return actual


def coefficient_difference(a, b):
    pa, pb = oracle.polynomial(a.counts, a.roles), oracle.polynomial(b.counts, b.roles)
    return [(pa[i] if i < len(pa) else Q(0)) -
            (pb[i] if i < len(pb) else Q(0)) for i in range(4)]


def fixtures():
    a, b = Profile((0, 15, 0), 4), Profile((14, 0, 4), 4)
    c, separator = crossing(a, b), Q(31, 30)
    require(c == Q(8, 7), "historical crossing changed")
    require(a.residual(separator) > 0 > b.residual(separator), "separator failed")
    require(agree(a, b) == -1, "historical root reversal failed")
    require(15**2 * 2 < 22**2, "historical score order failed")
    require(c**2 < 2, "half-exponent must be beyond the crossing")
    tie_a, tie_b = Profile((64, 0, 4), 30), Profile((56, 10, 1), 30)
    require(tie_a != tie_b and tie_a.mass == tie_b.mass == 80, "tie fixture invalid")
    require(crossing(tie_a, tie_b) == Q(3, 2), "tie crossing changed")
    require(tie_a.residual(Q(3, 2)) == tie_b.residual(Q(3, 2)) == 0, "tie not exact")
    require(agree(tie_a, tie_b) == 0, "distinct-profile tie failed")
    return {
        "retained_pr1048": {
            "a": list(a.counts), "b": list(b.counts), "roles": 4, "mass": a.mass,
            "root_order": -1, "crossing_t": str(c),
            "residual_difference_coefficients_ascending": [int(x) for x in coefficient_difference(a, b)],
            "separator_t": str(separator),
            "residual_a_at_separator": str(a.residual(separator)),
            "residual_b_at_separator": str(b.residual(separator)),
            "residual_a_at_crossing": str(a.residual(c)),
            "score_at_half": "15*sqrt(2) < 22; opposite to root order",
        },
        "distinct_profile_tie": {
            "a": list(tie_a.counts), "b": list(tie_b.counts), "roles": 30,
            "mass": 80, "common_root_t": "3/2", "root_order": 0,
            "residual_difference_coefficients_ascending": [int(x) for x in coefficient_difference(tie_a, tie_b)],
        },
    }


def controls():
    rejected = []

    def reject(name, operation):
        try:
            operation()
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("negative control accepted: " + name)

    a, b = Profile((0, 15, 0), 4), Profile((14, 0, 4), 4)
    reject("negative_count", lambda: Profile((-1, 15, 0), 4))
    reject("fractional_count", lambda: Profile((Q(1, 2), 15, 0), 4))
    reject("boolean_count", lambda: Profile((True, 15, 0), 4))
    reject("extra_full_rank_count", lambda: Profile((0, 15, 0, 1), 4))
    reject("zero_roles", lambda: Profile((0, 15, 0), 0))
    reject("root_at_a_zero", lambda: Profile((8, 0, 0), 1))
    reject("root_at_a_one", lambda: Profile((1, 0, 0), 1))
    reject("no_root_in_domain", lambda: Profile((9, 0, 0), 1))
    reject("unequal_roles", lambda: root_order(a, Profile((14, 0, 4), 5)))
    reject("unequal_mass", lambda: root_order(a, Profile((13, 0, 4), 4)))
    reject("fixed_half_score_used_as_root_order", lambda: agree(a, b, claimed=1))
    reject("equal_mass_mistaken_for_equal_roots", lambda: agree(a, b, claimed=0))
    tie_a, tie_b = Profile((64, 0, 4), 30), Profile((56, 10, 1), 30)
    reject("distinct_profiles_mistaken_for_strict_order", lambda: agree(tie_a, tie_b, claimed=1))
    reject("reciprocal_crossing", lambda: require(crossing(a, b) == Q(7, 8), "wrong crossing"))
    # Omitting the rank factor still leaves a well-bracketed root, but reverses
    # its comparison with B. Domain checks alone cannot detect this corruption.
    reject("rank_factor_omitted", lambda: require(
        oracle.root_order([Q(-32), Q(0), Q(15)], oracle.polynomial(b.counts, b.roles))
        == root_order(a, b), "rank-weight corruption changed the root order"))
    # With zero bisections two unequal roots both have [1,2]. Overlap must not
    # be mistaken for equality; the independent path refines before deciding.
    pa, pb = oracle.polynomial(a.counts, a.roles), oracle.polynomial(b.counts, b.roles)
    require(oracle.root_order(pa, pb, (Q(1), Q(2)), (Q(1), Q(2))) == -1,
            "coarse overlapping brackets were not resolved")
    require(agree(a, a) == 0 and agree(b, a) == 1, "identity or reverse orientation failed")
    return {"rejected": rejected, "positive": ["identical_profile", "swapped_profiles",
                                                "coarse_overlapping_brackets_refined"]}


def census():
    groups = defaultdict(list)
    # Complete Cartesian domain, not random sampling. Seed only orders cases.
    for roles in range(1, 9):
        for counts in product(range(9), repeat=3):
            mass = sum(rank * count for rank, count in zip((1, 2, 4), counts))
            if mass < 8 * roles and sum(counts) > roles:
                profile = Profile(counts, roles)
                groups[roles, mass].append(profile)
    profiles = [p for group in groups.values() for p in group]
    intervals = {p: oracle.isolate(oracle.polynomial(p.counts, p.roles)) for p in profiles}
    order_counts, branch_counts, interior_orders = Counter(), Counter(), Counter()
    digest, pairs = sha256(), 0
    keys = sorted(groups, key=lambda k: sha256(f"{SEED}:{k[0]}:{k[1]}".encode()).digest())
    for key in keys:
        for a, b in combinations(sorted(groups[key], key=lambda p: p.counts), 2):
            u, v = difference(a, b)
            delta = coefficient_difference(a, b)
            require(delta == [0, 4*v, -u-4*v, u], "factored identity failed")
            order = agree(a, b, intervals=intervals)
            require(root_order(b, a) == -order, "reversed comparison failed")
            c = None if u == 0 else Q(4*v, u)
            branch = ("u_zero" if c is None else "c_at_or_below_one" if c <= 1 else
                      "c_at_or_above_two" if c >= 2 else "interior_crossing")
            branch_counts[branch] += 1
            if branch == "interior_crossing":
                interior_orders[str(order)] += 1
            order_counts[str(order)] += 1
            digest.update((canonical([key, a.counts, b.counts, order,
                                      None if crossing(a, b) is None else str(c)]) + "\n").encode())
            pairs += 1
    return {
        "domain": "W=1..8; n1,n2,n4=0..8; mass<8W and n1+n2+n4>W; all unordered distinct equal-mass pairs",
        "assignment_seed": SEED, "seed_use": "SHA256-sorted traversal; coverage is exhaustive",
        "profiles": len(profiles), "equal_mass_groups": len(groups), "pairs": pairs,
        "oracle": "rational bisection and polynomial Euclidean GCD; no factored comparison",
        "oracle_initial_bisections": 64, "oracle_max_bisections": 512,
        "root_orders": dict(sorted(order_counts.items())),
        "comparison_branches": dict(sorted(branch_counts.items())),
        "interior_crossing_root_orders": dict(sorted(interior_orders.items())),
        "pair_transcript_sha256": digest.hexdigest(),
    }


def build():
    base, sources = source_check()
    return {"schema_version": 1, "base_commit": base, "sources": sources,
            "scope": "Abstract unsurcharged m=8 profiles on proper ranks 1,2,4 with equal W and mass; not a supplier or full theorem replay",
            "fixtures": fixtures(), "controls": controls(), "census": census()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print recomputed receipt for review")
    args = parser.parse_args()
    result = build()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        expected = json.loads((HERE / "RESULT.json").read_text())
        require(result == expected, "committed receipt differs from recomputation")
        print("PASS_DYADIC_ROOT_ORDER:", result["census"]["pairs"], "pair comparisons;",
              len(result["controls"]["rejected"]), "rejection controls; exact crossing and distinct-profile tie")


if __name__ == "__main__":
    main()
