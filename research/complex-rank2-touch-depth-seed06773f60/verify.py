#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Touch-depth capacity screen for same-column rank-2 retiming fusion (gauge44 word).

Scoped capacity/shape screen on the pinned selected gauge44 local program. For
consecutive same-column rank-(1,1) climb pairs (climb-path adjacent), the touch
depth is the number of intervening events referencing that column (scalar
operand `["L", col]`, adapter or residual_adapter). A fusion replaces the two
rank-1 children by one rank-2 child, preserving the 5,586 local rank mass.

This extends `research/complex-rank2-retiming-seed73506` (one-touch class:
exactly one intervening scalar event, 690 candidates per direction, maximum 674
disjoint fusions, below the 720 its zero-overhead profile needs for the 5%
ceiling gate) to touch depth >= 2, the first step named by that package's open
question 1. The touch distribution of all 1,441 (1,1) pairs published in
Discussion #1659 comment 18916048 is reproduced as an anchor.

Favorable model, exactly as the predecessor: retiming the intervening events,
copies, frames, hosting, precision, interface and restoration are all free; all
incumbent source/helper/child/centre/coverage charges stay in the profile. A
pass is a capacity/shape survival of this profile family only, never a physical
bill; a certified miss closes the family for this pinned word.

Aaron Wang, with help from opencode. Apache-2.0.
"""
import bisect
import collections
import gzip
import hashlib
import importlib.util
import io
import json
import sys
import tarfile
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz"
ARCHIVE_SHA256 = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
MEMBER = "candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz"
MEMBER_SHA256 = "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a"
CEILING_PATH = ROOT / "research/complex-local-word-ceiling/ceiling.py"
CEILING_SHA256 = "86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc"
SELECTED_PATH = ROOT / "certificates/selected-result.json"
SELECTED_SHA256 = "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32"

M, FAMILIES, STAGES, CENTRE = 73, 896, 9, 64
PROFILE = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
CLIMB_HIST = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82}
# Published anchors (Discussion #1659 comment 18916048; PR #1703 package).
ANCHOR_ADJACENT_PAIRS = 2782
ANCHOR_PAIRS_11 = 1441
ANCHOR_TOUCH_DIST = {1: 690, 2: 473, 3: 136, 4: 66, 5: 72, "ge6": 4}
ANCHOR_ONE_TOUCH = 690
ANCHOR_ONE_TOUCH_MATCHED = 674
ANCHOR_MIN_FUSIONS = 720
ANCHOR_BASE_HI = Q(1690054109089, 10 ** 15)
ANCHOR_TARGET = Q(35491136290869, 20_000_000_000_000_000)  # 1.05 x selected upper endpoint
GRID = Q(1, 10 ** 15)
WRITE = "--write" in sys.argv


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def source_program():
    raw = ARCHIVE.read_bytes()
    require(sha256(raw) == ARCHIVE_SHA256, "selected replay archive hash mismatch")
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as archive:
        member = archive.extractfile(MEMBER)
        require(member is not None, "pinned local program member missing")
        compressed = member.read()
    require(sha256(compressed) == MEMBER_SHA256, "LOCAL-PROGRAMS member hash mismatch")
    return json.loads(gzip.decompress(compressed))


def load_ceiling():
    raw = CEILING_PATH.read_bytes()
    require(sha256(raw) == CEILING_SHA256, "pinned ceiling engine hash mismatch")
    spec = importlib.util.spec_from_file_location("pinned_ceiling", CEILING_PATH)
    require(spec is not None and spec.loader is not None, "cannot import pinned ceiling engine")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_selected_binding():
    raw = SELECTED_PATH.read_bytes()
    require(sha256(raw) == SELECTED_SHA256, "selected record hash mismatch")
    return json.loads(raw)


def parse(events):
    """Per column: climb path [(index, rank)] and referencing events [(index, tag)]."""
    climbs = collections.defaultdict(list)
    touches = collections.defaultdict(list)
    for index, event in enumerate(events):
        require(isinstance(event, list) and event, "malformed local-program event")
        tag = event[0]
        if tag == "climb":
            require(len(event) >= 6, "malformed climb event")
            climbs[int(event[2])].append((index, int(event[5])))
        elif tag == "scalar":
            require(len(event) >= 2 and isinstance(event[1], list), "malformed scalar event")
            refs = set()
            for operand in event[1][1:]:
                if isinstance(operand, list) and len(operand) >= 2 and operand[0] == "L":
                    refs.add(int(operand[1]))
            for column in sorted(refs):
                touches[column].append((index, tag))
        elif tag in ("adapter", "residual_adapter"):
            require(len(event) >= 3, "malformed adapter event")
            touches[int(event[2])].append((index, tag))
    return climbs, touches


def adjacent_pairs(climbs, touches):
    """All consecutive same-column climb pairs with touch depth and intervening tags."""
    pairs = []
    for column in sorted(climbs):
        sequence = climbs[column]
        column_touches = touches.get(column, [])
        positions = [index for index, _ in column_touches]
        for position in range(len(sequence) - 1):
            (left, rank_left), (right, rank_right) = sequence[position], sequence[position + 1]
            first = bisect.bisect_right(positions, left)
            last = bisect.bisect_left(positions, right)
            between = column_touches[first:last]
            pairs.append({
                "column": column,
                "position": position,
                "ranks": (rank_left, rank_right),
                "touch": len(between),
                "tags": tuple(tag for _, tag in between),
            })
    return pairs


def edges_for(pairs, klass):
    """Candidate edge set (column, climb-path position) for a touch class."""
    if klass == 1:
        # The predecessor's class: exactly one intervening event, and it is a scalar.
        return {
            (p["column"], p["position"])
            for p in pairs
            if p["touch"] == 1 and p["tags"] == ("scalar",)
        }
    return {
        (p["column"], p["position"])
        for p in pairs
        if klass == "all" or p["touch"] <= klass
    }


def matching_dp(edges, sizes):
    """Exact maximum matching per column path with restricted edges (independent DP)."""
    by_column = collections.defaultdict(set)
    for column, position in edges:
        by_column[column].add(position)
    total = 0
    for column, allowed in by_column.items():
        n = sizes[column]
        dp = [0] * (n + 1)  # dp[j]: best matching on the first j vertices
        for j in range(1, n + 1):
            dp[j] = dp[j - 1]
            if j >= 2 and (j - 2) in allowed:  # edge joining vertices j-2 and j-1
                dp[j] = max(dp[j], dp[j - 2] + 1)
        total += dp[n]
    return total


def matching_greedy(edges):
    """Leftmost-edge greedy per column; also returns matched vertices."""
    by_column = collections.defaultdict(set)
    for column, position in edges:
        by_column[column].add(position)
    chosen = []
    vertices = collections.Counter()
    for column in sorted(by_column):
        last_used = -1
        for position in sorted(by_column[column]):
            if position <= last_used:
                continue
            chosen.append((column, position))
            vertices[(column, position)] += 1
            vertices[(column, position + 1)] += 1
            last_used = position + 1
    return chosen, vertices


def profile_after(n):
    profile = dict(PROFILE)
    profile[1] = PROFILE[1] - 2 * n
    profile[2] = PROFILE[2] + n
    return profile


def main():
    program = source_program()
    ceiling = load_ceiling()
    selected = check_selected_binding()

    model = ceiling.model(PROFILE, M, FAMILIES, STAGES, CENTRE)
    require(model["local_mass"] == 5586, "incumbent local mass changed")
    require(model["idle_mass"] == 1646, "incumbent idle mass changed")
    require(model["R"] == 51, "incumbent idle rank cap changed")

    report = {"anchors": {}, "controls": {}}
    per_direction = {}
    parsed = {}
    for orient in ("forward", "backward"):
        climbs, touches = parse(program[orient])
        parsed[orient] = (climbs, touches)
        hist = collections.Counter(rank for seq in climbs.values() for _, rank in seq)
        require(dict(sorted(hist.items())) == CLIMB_HIST, f"{orient} climb histogram changed")
        require(sum(r * n for r, n in hist.items()) == 5522, f"{orient} climb mass changed")
        pairs = adjacent_pairs(climbs, touches)
        require(len(pairs) == ANCHOR_ADJACENT_PAIRS, f"{orient} adjacent pair count != {ANCHOR_ADJACENT_PAIRS}")
        pairs11 = [p for p in pairs if p["ranks"] == (1, 1)]
        require(len(pairs11) == ANCHOR_PAIRS_11, f"{orient} (1,1) pair count != {ANCHOR_PAIRS_11}")
        dist = collections.Counter(min(p["touch"], 6) for p in pairs11)
        dist_key = {str(k): dist.get(k, 0) for k in (1, 2, 3, 4, 5)}
        dist_key["ge6"] = dist.get(6, 0)
        require(dist_key == {str(k): v for k, v in ANCHOR_TOUCH_DIST.items()},
                f"{orient} touch distribution {dist_key} != published")

        sizes = {column: len(seq) for column, seq in climbs.items()}
        classes = {}
        for klass in (1, 2, 3, 4, 5, "all"):
            edges = edges_for(pairs11, klass)
            chosen, vertices = matching_greedy(edges)
            require(max(vertices.values(), default=0) <= 1, f"{orient} greedy matching reuses a climb")
            dp = matching_dp(edges, sizes)
            require(dp == len(chosen), f"{orient} greedy/DP mismatch {len(chosen)} vs {dp}")
            classes[str(klass)] = {"candidates": len(edges), "matched": dp}
        require(classes["1"]["candidates"] == ANCHOR_ONE_TOUCH,
                f"{orient} one-touch candidates != {ANCHOR_ONE_TOUCH}")
        require(classes["1"]["matched"] == ANCHOR_ONE_TOUCH_MATCHED,
                f"{orient} one-touch matching != {ANCHOR_ONE_TOUCH_MATCHED}")
        per_direction[orient] = {
            "adjacent_pairs": len(pairs),
            "pairs_11": len(pairs11),
            "touch_distribution": dist_key,
            "classes": classes,
        }
    require(per_direction["forward"] == per_direction["backward"], "forward and backward disagree")

    # Selected-word ceiling and the 5% target.
    base = ceiling.ceiling(PROFILE, M, FAMILIES, STAGES, CENTRE, grid=GRID)
    require(base[1] == ANCHOR_BASE_HI, f"baseline ceiling {base[1]} changed")
    target = base[1] * Q(21, 20)
    require(target == ANCHOR_TARGET, f"5% target {target} changed")

    def certified_at(n, at=None):
        """(certified pass, certified fail) of the n-fusion profile at the target."""
        at = target if at is None else at
        lo, hi = ceiling.relax(profile_after(n), M, FAMILIES, STAGES, CENTRE, at)
        return hi < 1, lo > 1

    def least_passing(at):
        """Smallest n with a certified pass at `at`; monotone, so binary search."""
        if not certified_at(1206, at)[0]:
            return None
        low, high = 0, 1206
        while low < high:
            mid = (low + high) // 2
            if certified_at(mid, at)[0]:
                high = mid
            else:
                low = mid + 1
        return low

    pass719, fail719 = certified_at(719)
    pass720, fail720 = certified_at(720)
    require(not pass719 and fail719, "719-fusion control: expected certified failure")
    require(pass720, "720-fusion control: expected certified pass")
    # n <= 1206: beyond that the optimistic profile has no rank-1 children left.
    least = least_passing(target)
    require(least is not None and certified_at(least)[0] and not certified_at(least - 1)[0],
            "threshold search is not consistent with the monotone pass predicate")
    require(least == ANCHOR_MIN_FUSIONS, f"least passing fusion count {least} != {ANCHOR_MIN_FUSIONS}")

    rows = {}
    for klass in ("1", "2", "3", "4", "5", "all"):
        n = per_direction["forward"]["classes"][str(klass)]["matched"]
        bracket = ceiling.ceiling(profile_after(n), M, FAMILIES, STAGES, CENTRE, grid=GRID)
        require(bracket[0] <= bracket[1], "ceiling bracket inverted")
        gain_pct = (bracket[1] / base[1] - 1) * 100
        passes, fails = certified_at(n)
        rows[str(klass)] = {
            "candidates": per_direction["forward"]["classes"][str(klass)]["candidates"],
            "matched": n,
            "ceiling_lo": str(bracket[0]),
            "ceiling_hi": str(bracket[1]),
            "gain_pct_vs_baseline_hi": str(gain_pct),
            "passes_5pct_gate": bool(passes),
            "certified_fail_at_target": bool(fails),
        }

    # Failure controls: (a) re-binning one pair must break the published distribution;
    # (b) an inflated target must raise the least passing fusion count.
    mutated = dict(per_direction["forward"]["touch_distribution"])
    mutated["1"] += 1
    mutated["2"] -= 1
    require(mutated != {str(k): v for k, v in ANCHOR_TOUCH_DIST.items()},
            "touch-bin mutation control did not change the distribution")
    inflated = target * Q(21, 20)
    least_inflated = least_passing(inflated)
    require(least_inflated is None or least_inflated > ANCHOR_MIN_FUSIONS,
            "inflated-target control did not raise the threshold")

    report["anchors"] = {
        "archive_sha256": ARCHIVE_SHA256,
        "member_sha256": MEMBER_SHA256,
        "ceiling_sha256": CEILING_SHA256,
        "selected_record_sha256": SELECTED_SHA256,
        "profile": {str(k): v for k, v in PROFILE.items()},
        "local_mass": 5586,
        "idle_mass": 1646,
        "idle_rank_cap": 51,
        "baseline_ceiling_lo": str(base[0]),
        "baseline_ceiling_hi": str(base[1]),
        "target_5pct": str(target),
        "least_passing_fusions": least,
        "least_passing_fusions_inflated_target": least_inflated,
    }
    report["directions"] = per_direction
    report["classes"] = rows
    report["controls"] = {
        "forward_backward_agree": True,
        "greedy_matches_dp": True,
        "greedy_vertex_disjoint": True,
        "control_719_certified_fail": bool(fail719 and not pass719),
        "control_720_certified_pass": bool(pass720),
        "touch_bin_mutation_breaks_anchor": True,
        "inflated_target_raises_threshold": True,
    }
    report["scope"] = (
        "Capacity/shape screen for same-column (1,1) climb-pair retiming fusion on the "
        "pinned gauge44 word in the zero-extra-charge relaxation. No retiming legality, "
        "physical bill, supplier, kappa or frontier claim."
    )

    out_path = Path(__file__).resolve().parent / "RESULT.json"
    payload = json.dumps(report, indent=1, sort_keys=True) + "\n"
    if WRITE:
        out_path.write_text(payload, encoding="utf-8")
    elif out_path.exists():
        require(out_path.read_text(encoding="utf-8") == payload, "RESULT.json drift: rerun --write")

    dist = per_direction["forward"]["touch_distribution"]
    classes = per_direction["forward"]["classes"]
    print(
        "PASS_RANK2_TOUCH_DEPTH "
        f"adjacent={ANCHOR_ADJACENT_PAIRS} pairs11={ANCHOR_PAIRS_11} "
        f"dist={dist} "
        f"matched k1={classes['1']['matched']} k2={classes['2']['matched']} "
        f"k3={classes['3']['matched']} k4={classes['4']['matched']} "
        f"k5={classes['5']['matched']} all={classes['all']['matched']} "
        f"min_fusions={least} gate_all={rows['all']['passes_5pct_gate']}"
    )
    for klass in ("1", "2", "3", "4", "5", "all"):
        row = rows[str(klass)]
        print(
            f"CLASS k={klass}: candidates={row['candidates']} matched={row['matched']} "
            f"ceiling=[{row['ceiling_lo']}, {row['ceiling_hi']}] "
            f"gain_pct={float(Q(row['gain_pct_vs_baseline_hi'])):.4f} "
            f"pass={row['passes_5pct_gate']} certified_fail={row['certified_fail_at_target']}"
        )
    print("PASS_CONTROLS", json.dumps(report["controls"], sort_keys=True))


if __name__ == "__main__":
    main()
