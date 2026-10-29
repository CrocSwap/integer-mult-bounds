#!/usr/bin/env python3
"""Exact optimistic screen for replacing eight rank-1 terms by one rank-2 block call."""

from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
BASE = "20ecf2891d80b5acf18f980b2164fb44ea7faa90"
PINS = {
    "certificates/selected-result.json": "bb2eaa58647b353f88d0aec2eafb9d30df1be53589231b23e12ceef3e4bad129",
    "docs/research/community-batch1099-review.md": "7e76d2c38e5fce30587835b7251df1430488ae4dd372611ef69a3f03f476b6cb",
    "research/community-frontier1094-audit/ASSEMBLY.json": "1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045",
    "research/community-frontier1094-audit/SELECTED-SOURCE.json": "79b3de5db3dbcb9829789ba58e9e45758926031e2a7d80667a08429d369be53b",
    "research/community-frontier1094-audit/INDEPENDENT1094.json": "301fb8a0e4ab7e3c383ff974c54c08178283b2a3453c5282757f692a3c7a4bfd",
    "research/complex-local-word-ceiling/ceiling.py": "86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc",
    "research/complex-local-word-ceiling/verify.py": "06b59955c69a2e7f49aa031d2ebaac2f39dbe107f4087122704f2a37ce9806d5",
}

sys.path.insert(0, str(ROOT / "research" / "complex-local-word-ceiling"))
import ceiling as C  # noqa: E402
import verify as selected_ceiling  # noqa: E402

GRID = Q(1, 10**12)
EXPECTED_LOCAL = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}


def require(ok, why):
    if not ok:
        raise AssertionError(why)


def candidate(local, t):
    max_t = local.get(1, 0) // 8
    require(isinstance(t, int) and 0 <= t <= max_t, "block count outside complete rank-1 groups")
    out = dict(local)
    out[1] = out.get(1, 0) - 8 * t
    out[2] = out.get(2, 0) + t
    return {r: n for r, n in out.items() if n}


def main():
    for rel, expected in PINS.items():
        actual = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
        require(actual == expected, f"source hash changed: {rel}")

    rec, asm, _, _, calls, live, local = selected_ceiling.selected()
    require(local == EXPECTED_LOCAL, "selected per-call paid profile changed")
    require(rec["audited_source_head"] == "0fc329d0bec93ca7cd288eaea1295172e8789810",
            "selected audited source head changed")
    require(calls % 9 == 0 and live == Q(896 * calls, 9), "selected call/live binding changed")

    baseline_model = C.model(local, 73, 896, 9, 64)
    require(baseline_model["R"] == 51 and baseline_model["idle_mass"] == 1646,
            "baseline coverage or halving-guard bill changed")
    total_mass = baseline_model["total_mass"]
    require(total_mass == 7232 and baseline_model["local_mass"] == 5586,
            "baseline paid mass changed")

    base_lo, base_hi = C.ceiling(local, 73, 896, 9, 64, grid=GRID)
    tmax = local[1] // 8
    changed = candidate(local, tmax)
    changed_model = C.model(changed, 73, 896, 9, 64)
    require(tmax == 301 and changed == {1: 4, 2: 719, 3: 432, 4: 142, 5: 82, 8: 8},
            "maximal candidate inventory changed")
    require(changed_model["local_mass"] == 3780 and changed_model["idle_mass"] == 3452,
            "candidate rank/idle bill changed")
    require(changed_model["local_mass"] + changed_model["idle_mass"] == total_mass,
            "candidate does not conserve the coverage mass")

    changed_lo, changed_hi = C.ceiling(changed, 73, 896, 9, 64, grid=GRID)
    at_base = C.relax(changed, 73, 896, 9, 64, base_hi)
    at_lo = C.relax(changed, 73, 896, 9, 64, changed_lo)
    at_hi = C.relax(changed, 73, 896, 9, 64, changed_hi)
    require(at_base[1] < 1, "candidate does not strictly improve the baseline ceiling")
    require(at_lo[1] < 1 and at_hi[0] > 1, "candidate root bracket signs are not certified")

    bit_b = Q(asm["bit_lower"])
    bit_kappa_cap = bit_b / (1 + bit_b)
    complex_kappa_cap = changed_hi / (1 + changed_hi)
    selected_kappa = Q(rec["kappa"])
    five_percent_target = selected_kappa * Q(105, 100)
    planning_target = Q(1, 99)
    overall_cap = min(bit_kappa_cap, complex_kappa_cap)

    # Locate the first complete-block count whose complex root clears the unchanged bit root.
    lo_t, hi_t = 0, tmax
    while hi_t - lo_t > 1:
        mid_t = (lo_t + hi_t) // 2
        if C.relax(candidate(local, mid_t), 73, 896, 9, 64, bit_b)[1] < 1:
            hi_t = mid_t
        else:
            lo_t = mid_t
    cross_profile = candidate(local, hi_t)
    before_bit = C.relax(candidate(local, hi_t - 1), 73, 896, 9, 64, bit_b)
    at_bit = C.relax(cross_profile, 73, 896, 9, 64, bit_b)
    cross_model = C.model(cross_profile, 73, 896, 9, 64)
    require(before_bit[0] > 1 and at_bit[1] < 1,
            "minimal bit-cap crossing is not certified on both adjacent counts")
    require(complex_kappa_cap < planning_target, "candidate unexpectedly reaches 1/99")
    require(overall_cap < five_percent_target, "candidate unexpectedly clears the 5% system target")
    require(bit_kappa_cap < five_percent_target < planning_target, "bit-side stop test changed")

    # One replacement strictly decreases the relaxed moment for every a > 0:
    # 8 - 2^(1-a) - 6*51^(-a) has value zero at a=0 and positive derivative.
    require(candidate(local, 0) == local, "zero-block candidate control failed")
    try:
        candidate(local, tmax + 1)
    except AssertionError as exc:
        require(str(exc) == "block count outside complete rank-1 groups",
                "out-of-range block control failed for the wrong reason")
    else:
        raise AssertionError("out-of-range block count was accepted")

    result = {
        "status": "PASS_RANK2_BLOCK_HELPER_SCREEN",
        "base": BASE,
        "selected_record_sha256": PINS["certificates/selected-result.json"],
        "selected_kappa": str(selected_kappa),
        "baseline_a_bracket_1e-12": [str(base_lo), str(base_hi)],
        "contract": "8 rank-1 scalar products -> 1 recursive rank-2 2x2 block helper",
        "blocks_per_call_max": tmax,
        "candidate_profile_per_call": {str(k): v for k, v in sorted(changed.items())},
        "local_mass": str(changed_model["local_mass"]),
        "idle_mass": str(changed_model["idle_mass"]),
        "total_coverage_mass": str(total_mass),
        "candidate_a_bracket_1e-12": [str(changed_lo), str(changed_hi)],
        "candidate_moment_at_baseline_hi": [str(at_base[0]), str(at_base[1])],
        "candidate_moment_at_a_lo": [str(at_lo[0]), str(at_lo[1])],
        "candidate_moment_at_a_hi": [str(at_hi[0]), str(at_hi[1])],
        "complex_kappa_cap_upper": str(complex_kappa_cap),
        "min_blocks_per_call_to_clear_bit_root": hi_t,
        "bit_crossing_profile_per_call": {str(k): v for k, v in sorted(cross_profile.items())},
        "bit_crossing_local_mass": str(cross_model["local_mass"]),
        "bit_crossing_idle_mass": str(cross_model["idle_mass"]),
        "moment_at_bit_root_previous_blocks": [str(before_bit[0]), str(before_bit[1])],
        "moment_at_bit_root_first_crossing": [str(at_bit[0]), str(at_bit[1])],
        "bit_b": str(bit_b),
        "bit_kappa_cap_upper": str(bit_kappa_cap),
        "overall_cap_with_bit_fixed": str(overall_cap),
        "five_percent_system_target": str(five_percent_target),
        "planning_target_1_over_99": str(planning_target),
        "scope": "optimistic profile only; source matching and extra physical charges are unproved",
    }
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    args = sys.argv[1:]
    receipt = Path(__file__).with_name("RESULT.json")
    if args == ["--write"]:
        receipt.write_text(rendered, encoding="utf-8", newline="\n")
        print("WROTE_RANK2_BLOCK_HELPER_RESULT")
    elif args == ["--check"]:
        require(json.loads(receipt.read_text()) == result, "RESULT.json differs from recomputed evidence")
        print("PASS_RANK2_BLOCK_HELPER_SCREEN")
        print(rendered, end="")
    else:
        require(not args, "usage: verify.py [--write|--check]")
        print(rendered, end="")


if __name__ == "__main__":
    main()
