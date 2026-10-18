#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact optimistic pricing of the retained-role P104 interleaving scenarios.

This is CEILING_NOT_SUPPLIER: a feasible relaxation is not an admitted word,
owner allocation, or exponent improvement. Query formation is uncharged.
The package's aggregate verifier checks that the two-query chronological
replay gives exactly the public and residual deltas priced here. Thus their
sum is an actual joint perturbation invoice, not an assumption that separate
invoices can be added. This module prices that invoice without replaying it.
Source-query formation remains uncharged, as do the two final query H1
boundaries unless already included in charged query lifetimes. Hosting the
two overlapping owned COPY lifetimes remains unproved.

The interval engine is Douglas Colkitt's attributed complex-local-word-ceiling
work. The selected local profile is retained from PR1042 through the selected
PR1094 assembly and complex-block-rank-optimum. New scenario accounting was
prepared with substantial OpenAI Codex assistance.

Run from any directory, standard library only:
  python3 -I -B research/p104-interleaved-search/budget.py
Add --copy-table for the separate COPY56..60 fallback screen.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import json
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INPUTS = {
    "engine": (
        "research/complex-local-word-ceiling/ceiling.py",
        "86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc",
    ),
    "word": (
        "research/complex-block-rank-optimum/inputs/selected.json.gz",
        "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219",
    ),
    "assembly": (
        "research/community-frontier1094-audit/ASSEMBLY.json",
        "1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045",
    ),
    "selection": (
        "certificates/selected-result.json",
        "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32",
    ),
    "stock": (
        "research/complex-t16-rare-pattern-exchanges/data/SPEC.json",
        "8cb51f25a5da4a29d3783853025b73ff1f452429d4fdb30c599e598bcab0e71d",
    ),
    "source_manifest": (
        "research/community-frontier1094-audit/SELECTED-SOURCE.json",
        "79b3de5db3dbcb9829789ba58e9e45758926031e2a7d80667a08429d369be53b",
    ),
}
SELECTED_PROFILE = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
SELECTED_KAPPA = Q(836330098538459, 500000000000000000)
BIT_LOWER = Q(1733427039589844234749, 1000000000000000000000000)
M, FAMILIES, STAGES, CENTRE = 73, 832, 9, 56

# Final early-placement variants replayed separately and jointly in delivery.py.
# Each descent has mass seven and replaces one hypothetical H7 child.
CHAIN_PROFILES = (
    {
        "a_root": 3,
        "b_root": 113,
        "injections": 14,
        "descent": {1: 1, 2: 1, 4: 1},
        "local_tail_cleanup_delta": {1: 33, 2: 19, 3: -13, 4: -4, 5: -2},
        "residual_width_delta": {1: -5, 4: 1, 5: -1},
    },
    {
        "a_root": 4,
        "b_root": 57,
        "injections": 16,
        "descent": {1: 2, 5: 1},
        "local_tail_cleanup_delta": {1: 40, 2: 24, 3: -12, 4: -6, 5: -4},
        "residual_width_delta": {1: -5, 4: 3, 5: -3},
    },
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def decimal(value: Q) -> str:
    with localcontext() as context:
        context.prec = 24
        return str(Decimal(value.numerator) / Decimal(value.denominator))


def interval(bounds: tuple[Q, Q]) -> dict:
    return {
        "lower": str(bounds[0]),
        "upper": str(bounds[1]),
        "lower_decimal": decimal(bounds[0]),
        "upper_decimal": decimal(bounds[1]),
    }


def profile_json(profile: dict) -> dict[str, int]:
    return {str(rank): int(count) for rank, count in sorted(profile.items()) if count}


def mass(profile: dict) -> int:
    return sum(rank * count for rank, count in profile.items())


def changed(profile: dict, delta: dict) -> dict[int, int]:
    result = Counter(profile)
    result.update(delta)
    require(all(count >= 0 for count in result.values()), "negative local child count")
    return {rank: count for rank, count in sorted(result.items()) if count}


def load_inputs() -> tuple[object, dict, dict, dict]:
    loaded = {}
    for name, (relative, expected) in INPUTS.items():
        data = (ROOT / relative).read_bytes()
        require(hashlib.sha256(data).hexdigest() == expected, f"input hash: {relative}")
        if name != "engine":
            loaded[name] = json.loads(gzip.decompress(data) if relative.endswith(".gz") else data)
    spec = importlib.util.spec_from_file_location("p104_budget_ceiling", ROOT / INPUTS["engine"][0])
    require(spec is not None and spec.loader is not None, "cannot load exact ceiling engine")
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    # Repeated scenarios share most binary-search grid points. This caches
    # exact interval results only; the pinned arithmetic is unchanged.
    engine.child_cost = lru_cache(maxsize=8192)(engine.child_cost)
    word, assembly = loaded["word"], loaded["assembly"]
    require((word["v"], word["R"], word["h"]) == (112, 480, 9), "selected word dimensions")
    require({int(r): n for r, n in word["local_profile"].items()} == SELECTED_PROFILE,
            "selected profile changed")
    require(Q(assembly["kappa"]) == SELECTED_KAPPA, "selected kappa changed")
    require(Q(assembly["bit_lower"]) == BIT_LOWER, "selected bit supplier changed")
    stock = loaded["stock"]
    require(loaded["selection"]["source_manifest"] == INPUTS["source_manifest"][0],
            "selected source-manifest path changed")
    require(loaded["source_manifest"]["files"][INPUTS["stock"][0]] == INPUTS["stock"][1],
            "stock is not bound by the selected source manifest")
    contract, expected = stock["providers"]["gauge44"]["complete_contract"], stock["expected"]
    require((contract["helpers"], contract["centres"], contract["n"]) == (480, 8, 704),
            "selected private-centre stock changed")
    require(expected["physical"] - expected["live"] == contract["helpers"] + contract["centres"] + 2,
            "selected physical stock identity changed")
    require(Q(expected["kappa"]) == SELECTED_KAPPA, "stock certificate selected result differs")
    return engine, word, assembly, {
        "selected_private_centre_families": contract["centres"],
        "selected_ordinary_helper_families": contract["helpers"],
        "selected_physical_families": expected["physical"],
        "selected_live_families": expected["live"],
        "scope": "Capacity only: the eight private centres are separate from ordinary helpers. Their count is not the ambient width m. No concurrent native admission or public-query placement is established.",
    }


def retained_profile(copy_cost: int = CENTRE) -> dict[int, int]:
    """Retain all16 deleted X/Y roles; shorten 64-COPY of eight H8 paths."""
    require(56 <= copy_cost <= 64, "COPY screen domain")
    shortened = 64 - copy_cost
    return changed(SELECTED_PROFILE, {1: 16, 8: -shortened, 7: shortened})


def verify(include_copy_table: bool = False) -> dict:
    engine, _, _, stock = load_inputs()
    target_kappa = SELECTED_KAPPA * Q(101, 100)
    target_a = target_kappa / (1 - target_kappa)
    bit_cap = BIT_LOWER / (1 + BIT_LOWER)
    rank_cap = engine.max_idle_rank(M)
    require(rank_cap == 51, "outer rank cap changed")
    w = Q(FAMILIES, STAGES)
    require(FAMILIES == 2 * 4 * 104, "four-pair P104 family count")
    zero_checks = 0

    def describe(name: str, local: dict, centre: int = CENTRE, m: int = M) -> dict:
        nonlocal zero_checks
        model = engine.model(local, m, FAMILIES, STAGES, centre)
        total = (m - 1) * w + centre
        require(model["local_mass"] + model["idle_mass"] == total, "full coverage mass identity")
        zero = engine.relax(local, m, FAMILIES, STAGES, centre, Q(0))
        require(zero[0] <= total / (m * w) <= zero[1], "zero-saving coverage moment")
        zero_checks += 1
        bounds = engine.ceiling(local, m, FAMILIES, STAGES, centre)
        require(engine.relax(local, m, FAMILIES, STAGES, centre, bounds[0])[1] < 1,
                "lower root bracket is not certified")
        require(engine.relax(local, m, FAMILIES, STAGES, centre, bounds[1])[0] > 1,
                "upper root bracket is not certified")
        moment = engine.relax(local, m, FAMILIES, STAGES, centre, target_a)
        kappa_cap = min(bounds[1] / (1 + bounds[1]), bit_cap)
        return {
            "name": name,
            "status": "CEILING_NOT_SUPPLIER",
            "m": m,
            "local_profile": profile_json(local),
            "centre_COPY_rank": centre,
            "model": {key: str(value) for key, value in model.items()},
            "complex_saving_root_interval": interval(bounds),
            "kappa_upper_bound": str(kappa_cap),
            "kappa_upper_bound_decimal": decimal(kappa_cap),
            "relative_gain_upper_percent_decimal": decimal(100 * (kappa_cap / SELECTED_KAPPA - 1)),
            "moment_at_one_percent_target": interval(moment),
            "per_call_margin_at_one_percent_target": interval(((1 - moment[1]) * w, (1 - moment[0]) * w)),
            "one_percent_target_excluded": moment[0] > 1,
        }

    retained = retained_profile()
    # Each additional dirty save enters at rank2 and finishes at FULL: H2+H7.
    # These 144 units are hosted mass replacing idle mass, not excess travel.
    saved = changed(retained, {2: 16, 7: 16})
    require(mass(saved) - mass(retained) == 16 * 9, "saved-helper lifetime mass")
    chains = saved
    for chain in CHAIN_PROFILES:
        require(mass(chain["descent"]) == 7, "delivery descent mass")
        require(mass(chain["local_tail_cleanup_delta"]) + mass(chain["residual_width_delta"]) == 0,
                "delivery local/residual mass cancellation")
        delta = Counter(chain["local_tail_cleanup_delta"])
        delta.update(chain["descent"])
        delta[7] -= 1
        chains = changed(chains, delta)
    scenarios = [
        describe("retained_16_dirty_roles", retained),
        describe("retained_roles_plus_16_saved_F2_helpers", saved),
        describe("saved_helpers_plus_two_query_delivery_profile", chains),
    ]

    # A genuine extra transport increases paid mass beyond the fixed coverage
    # identity. Calling relax(local+H1) would silently subtract one idle rank.
    # This control makes that error change the 1% screening verdict.
    original_moment = engine.relax(saved, M, FAMILIES, STAGES, CENTRE, target_a)
    child = engine.child_cost(1, M, target_a)
    true_excess = tuple(original_moment[i] + child[i] / w for i in (0, 1))
    falsely_hosted = engine.relax(changed(saved, {1: 1}), M, FAMILIES, STAGES, CENTRE, target_a)
    idle_child = engine.child_cost(rank_cap, M, target_a)
    gap = (true_excess[0] - falsely_hosted[1], true_excess[1] - falsely_hosted[0])
    expected_gap = tuple(x / (rank_cap * w) for x in idle_child)
    require(gap[0] <= expected_gap[0] <= expected_gap[1] <= gap[1], "excess/idle substitution gap")
    require(true_excess[0] > 1 and falsely_hosted[1] < 1, "excess-transport control did not separate verdicts")

    # Upper counts only: favorable rank51 idle, hypothetical legal lifetimes,
    # and all omitted query/gather/remaining delivery work still free.
    helper_limits = {}
    for label, local in (("saved_helpers", saved), ("two_delivery_profiles", chains)):
        moment = engine.relax(local, M, FAMILIES, STAGES, CENTRE, target_a)
        margin = ((1 - moment[1]) * w, (1 - moment[0]) * w)
        helper_limits[label] = {}
        for name, shape in (("H1_plus_H8", {1: 1, 8: 1}), ("H2_plus_H7", {2: 1, 7: 1})):
            costs = {r: engine.child_cost(r, M, target_a) for r in shape}
            penalty = (
                sum(n * costs[r][0] for r, n in shape.items()) - Q(9, rank_cap) * idle_child[1],
                sum(n * costs[r][1] for r, n in shape.items()) - Q(9, rank_cap) * idle_child[0],
            )
            require(penalty[0] > 0, "helper substitution penalty")
            limit_lo, limit_hi = margin[0] // penalty[1], margin[1] // penalty[0]
            require(limit_lo == limit_hi and limit_lo >= 0, "helper count not separated by exact intervals")
            helper_limits[label][name] = int(limit_lo)

    fallback = []
    if include_copy_table:
        fallback = [describe(f"retained_roles_COPY{copy}", retained_profile(copy), copy) for copy in range(56, 61)]
        require(all(item["one_percent_target_excluded"] for item in fallback if item["centre_COPY_rank"] >= 58),
                "COPY58..60 fallback control changed")
    return {
        "status": "CEILING_NOT_SUPPLIER",
        "scope": "Necessary optimistic moment screens; no supplier, native-word, owner, or kappa improvement assertion.",
        "sources": [{"path": path, "sha256": digest} for path, digest in INPUTS.values()],
        "selected_kappa": str(SELECTED_KAPPA),
        "selected_bit_lower": str(BIT_LOWER),
        "fixed_bit_kappa_upper_bound": str(bit_cap),
        "fixed_bit_gain_upper_percent_decimal": decimal(100 * (bit_cap / SELECTED_KAPPA - 1)),
        "target_kappa": str(target_kappa),
        "necessary_complex_saving_for_target": str(target_a),
        "hypotheses": [
            "Retain m=73, nine stages, four pairs, 104 ports, and all-helpers-hosted coverage.",
            "Use the full retained local profile with sixteen deleted X/Y roles converted to dirty helpers.",
            "Shorten eight H8 paths to H7 and charge centre COPY rank56.",
            "The sixteen saved F2 partials each have an H2+H7 lifetime.",
            "All remaining idle mass may be packed fractionally at rank51, even if no such owner packing exists.",
            "Source-query formation, storage, the other six deliveries, and additional transport are uncharged.",
            "The two-query perturbation profile is supplied by the combined delivery replay; this pricing module does not independently prove its schedule.",
            "Two private-copy lifetimes fit the count of eight already allocated private-centre families; overlapping copies alone do not force m74. Concurrent native admission and actual public-query placement remain unproved.",
            "The two supplied-query H_b-to-FULL rank1 boundaries are omitted unless included in an already charged query lifetime.",
            "The fixed-bit and complex kappa caps use the retained balanced-transfer necessary inequalities.",
        ],
        "chain_profile_inputs": [
            {key: profile_json(value) if isinstance(value, dict) else value for key, value in chain.items()}
            for chain in CHAIN_PROFILES
        ],
        "scenarios": scenarios,
        "additional_hosted_width9_helper_count_upper_bounds_at_one_percent": helper_limits,
        "controls": {
            "full_coverage_and_zero_saving_moment_cases": zero_checks,
            "each_delivery_local_plus_residual_mass_is_zero": True,
            "saved_helpers_have_full_rank9_lifetimes": True,
            "one_true_excess_H1_excludes_one_percent_target": True,
            "incorrect_idle_substitution_would_pass_same_target": True,
            "true_excess_moment": interval(true_excess),
            "incorrectly_hosted_moment": interval(falsely_hosted),
            "exact_difference_is_one_rank_of_idle_child_cost": True,
        },
        "optional_COPY_fallback_table": fallback,
        "selected_private_centre_stock": stock,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--copy-table", action="store_true", help="also price retained-role COPY56..60 scenarios")
    args = parser.parse_args()
    print(json.dumps(verify(include_copy_table=args.copy_table), indent=2, sort_keys=True))
