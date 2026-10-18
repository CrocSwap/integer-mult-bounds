#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Source-window obstructions to two orders of the fixed coupled inventory.

The combinatorial argument is new here. Authenticated PR3153 arithmetic
supplies the inherited packing-dual and interval-arithmetic premise.
Prepared for commdata2338 with substantial OpenAI Codex assistance.
"""

import argparse
import gzip
import hashlib
import heapq
import json
import types
from collections import Counter
from fractions import Fraction
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
ALLOC = "research/rank7-joint-endframes/allocation/"
PREDECESSOR = "research/coupled-cap-independent/"
INVENTORY = {4: 26, 5: 2, 6: 18, 7: 50, 8: 99, 9: 213}
LOCAL = {1: 2433, 2: 724, 3: 228, 4: 102, 5: 20, 8: 8}
PORTS = 112
DELTA = Fraction(3, 250)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def decoded(raw, compressed=False):
    if compressed:
        raw = gzip.decompress(raw)
    require(len(raw) <= 32_000_000, "bounded decoded input")
    return json.loads(raw, object_pairs_hook=unique_object)


def authenticate(root=ROOT):
    manifest = decoded((PACKAGE / "SOURCES.json").read_bytes())
    data = {}
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        path = row["path"]
        require(not Path(path).is_absolute() and ".." not in Path(path).parts,
                "relative source path")
        target = root / path
        require(target.is_file() and not target.is_symlink() and
                target.stat().st_size <= 2_000_000, "bounded regular source")
        raw = target.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row["sha256"],
                "source bytes: " + path)
        data[path] = raw
    require(len(data) == 6, "six live source inputs")
    return data


def source_types(template, plan):
    """Forward last-touch interpretation of the literal execution schedule."""
    capacities, port_sets = {}, {}
    for entry in template["idle_children"]:
        child, rank, port = entry["child"], entry["rank"], entry["port"]
        require(child not in capacities or capacities[child] == rank,
                "consistent child rank")
        capacities[child] = rank
        ports = port_sets.setdefault(child, set())
        require(port not in ports, "unique declared child port")
        ports.add(port)
    require(set(capacities) == set(range(18)) and
            all(ports == set(range(PORTS)) for ports in port_sets.values()),
            "complete eighteen-child port domain")
    pairs = {e["stage"]: e["pair"] for e in template["recipe"]
             if e["kind"] == "local"}
    touched = dict.fromkeys(range(4))
    stage, result = None, {}
    for event in template["execution_schedule"]:
        kind = event["kind"]
        if kind == "local_cover_sweep":
            stage = event["stage"]
            touched[pairs[stage]] = stage
        elif kind == "bridge":
            touched[event["src"]] = touched[event["dst"]] = stage
        elif kind == "idle_cover_sweep":
            before = touched[event["pair"]]
            require(event["from_level"] == (-1 if before is None else before)
                    and event["to_level"] == stage, "declared/actual source cut")
            for child in event["child_indices"]:
                if child not in capacities:
                    continue
                require(child not in result, "unique source interval")
                require(plan["pairs"][str(child)] == event["pair"], "pair binding")
                family = 2 * event["pair"] + plan["sides"][str(child)]
                result[child] = (capacities[child], before, stage, family)
        else:
            require(kind in {"terminal_Y_translations", "terminal",
                             "bank_padding_cover_sweep", "translate_every_live_family"},
                    "known schedule event")
    require(set(result) == set(range(18)), "all source intervals recovered")
    small = {c: row for c, row in result.items() if row[0] == 8}
    require(small == {1: (8, 1, 2, 2), 3: (8, 1, 2, 3),
                      5: (8, 3, 4, 4), 7: (8, 3, 4, 5),
                      9: (8, 5, 6, 6), 11: (8, 5, 6, 7)},
            "six source-bound short intervals and distinct physical families")
    return result


def times_for(order):
    require(len(order) > 0 and len(order) % 9 == 0, "complete call count")
    replicas = len(order) // 9
    times = [[None] * 9 for _ in range(replicas)]
    for time, entry in enumerate(order):
        require(len(entry) == 2 and all(type(x) is int for x in entry), "typed call")
        stage, replica = entry
        require(0 <= stage < 9 and 0 <= replica < replicas, "call domain")
        require(times[replica][stage] is None, "unique call")
        times[replica][stage] = time
    require(all(None not in row and row == sorted(row) for row in times),
            "complete causal replica order")
    return times


def order_for(replicas, kind):
    require(type(replicas) is int and 1 <= replicas <= 740, "bounded replica count")
    if kind == "stage_major":
        return [(s, r) for s in range(9) for r in range(replicas)]
    require(kind == "replica_major", "named order")
    return [(s, r) for r in range(replicas) for s in range(9)]


def jobs_for(source, times):
    # One unit job is the required [8] placement of one physical child/port.
    return [(row[before] + 1, row[after], PORTS, owner, child, family)
            for owner, row in enumerate(times)
            for child, (rank, before, after, family) in sorted(source.items())
            if rank == 8]


def check_published_windows(source, plan):
    """Compare all reconstructed windows with the original T37 plan tables."""
    times = times_for(plan["order"])
    require(len(times) == plan["T"] == 37, "historical plan replication count")
    expected = {}
    for owner, row in enumerate(times):
        for child, (rank, before, after, _) in source.items():
            left = -1 if before is None else row[before]
            expected[f"{owner},{child}"] = [rank, list(range(left + 1, row[after] + 1))]
    require(plan["windows"] == expected, "all reconstructed historical windows")
    return len(expected)


def interval_matching(jobs, supplies):
    """Maximum interval-to-slot matching; earliest-deadline greedy exchange."""
    require(all(type(n) is int and n >= 0 for n in supplies), "nonnegative supply")
    require(all(0 <= a <= b < len(supplies) and type(n) is int and n > 0
                for a, b, n, *_ in jobs), "valid closed job interval")
    releases = sorted((job[0], i) for i, job in enumerate(jobs))
    cursor, matched, heap, placements = 0, 0, [], []
    for time, supply in enumerate(supplies):
        while cursor < len(releases) and releases[cursor][0] <= time:
            _, i = releases[cursor]
            heapq.heappush(heap, (jobs[i][1], i, jobs[i][2]))
            cursor += 1
        while heap and supply:
            deadline, i, left = heapq.heappop(heap)
            if deadline < time:
                continue
            used = min(left, supply)
            matched += used
            supply -= used
            placements.append((time, i, used))
            if left > used:
                heapq.heappush(heap, (deadline, i, left - used))
    return matched, placements


def validate_matching(jobs, supplies, placements):
    by_job, by_time = Counter(), Counter()
    for time, i, count in placements:
        require(type(count) is int and count > 0 and 0 <= i < len(jobs),
                "positive matching entry")
        require(jobs[i][0] <= time <= jobs[i][1], "matching stays inside source window")
        by_job[i] += count
        by_time[time] += count
    require(all(n <= jobs[i][2] for i, n in by_job.items()), "job capacity")
    require(all(n <= supplies[t] for t, n in by_time.items()), "call capacity")
    return sum(by_job.values())


def hall_witness(jobs, supplies, children):
    subset = [j for j in jobs if j[4] in children]
    neighbors = sorted({t for a, b, *_ in subset for t in range(a, b + 1)})
    demand = sum(j[2] for j in subset)
    available = sum(supplies[t] for t in neighbors)
    return {"children": list(children), "demand": demand,
            "neighbor_calls": neighbors, "available_width8_roles": available,
            "deficit": max(0, demand - available)}


def chronology_result(source, order, kind):
    replicas = len(order) // 9
    jobs = jobs_for(source, times_for(order))
    supplies = [INVENTORY[8]] * len(order)
    matched, placements = interval_matching(jobs, supplies)
    require(validate_matching(jobs, supplies, placements) == matched, "matching witness")
    groups = [hall_witness(jobs, supplies, cs) for cs in ((1, 3), (5, 7), (9, 11))]
    if kind in {"stage_major", "replica_major"}:
        groups_union = set().union(*(set(g["neighbor_calls"]) for g in groups))
        require(len(groups_union) == sum(len(g["neighbor_calls"]) for g in groups),
                "three disjoint Hall neighborhoods")
        expected = 3 * (26 * replicas + 99) if kind == "stage_major" else 375 * replicas
        require(sum(g["deficit"] for g in groups) == expected, "symbolic deficit formula")
        require(672 * replicas - matched == expected, "matching attains Hall upper bound")
    return {"replicas": replicas, "calls": len(order), "required_cap8_bins": 672 * replicas,
            "matched_in_relaxation": matched, "unmatched": 672 * replicas - matched,
            "placement_sha256": hashlib.sha256(json.dumps(placements).encode()).hexdigest(),
            "groups": groups}


def reduced_costs(module, patterns, basis, intervals):
    dual = module.dual_coefficients(basis)
    result = []
    for capacity, counts, idle in patterns:
        if capacity != 8:
            continue
        coefficients = {r: Fraction(r == idle) for r in range(1, 49)}
        for j, rank in enumerate((1, 3, 5, 48)):
            coefficients[rank] -= sum(v * dual[i][j]
                                      for i, v in enumerate(module.features(capacity, counts)))
        if any(coefficients.values()):
            lower = sum(c * intervals[r][int(c < 0)] for r, c in coefficients.items())
            require(lower > DELTA, "strict cap8 reduced-cost lower bound")
            result.append({"counts": list(counts), "idle": idle, "lower": str(lower)})
        else:
            require(counts == (0, 0, 0, 0, 1, 0), "only tight cap8 pattern is [8]")
    require(len(result) == 6, "all six non-[8] patterns")
    return result


def cap_premise(data):
    """Replay the inherited dual, rather than assume stored PASS metadata."""
    providers = decoded(data[PREDECESSOR + "vendor/PROVIDERS.json"])
    require(set(providers) == {"extra", "gauge44"}, "both providers")
    for value in providers.values():
        require(Counter(value["widths"]) == INVENTORY and len(value["widths"]) == 408,
                "source-bound provider widths")
        require({int(k): v for k, v in value["actual_paid_profile"].items()} == LOCAL,
                "source-bound local paid profile")
    module = types.ModuleType("authenticated_pr3153_arithmetic")
    raw = data[PREDECESSOR + "arithmetic.py"]
    exec(compile(raw, PREDECESSOR + "arithmetic.py", "exec", optimize=0), module.__dict__)
    cap = decoded(data[PREDECESSOR + "vendor/CAP.json"])
    patterns, basis, amounts, rhs = module.check_primal(cap, INVENTORY, LOCAL)
    lower, upper = Fraction(cap["cap_lower"]), Fraction(cap["cap_upper"])
    intervals = module.child_intervals(lower, upper)
    tight, margin = module.check_dual(patterns, basis, rhs, intervals)
    require([(c, ns) for c, ns in tight if c == 8] == [(8, (0, 0, 0, 0, 1, 0))],
            "unique tight capacity-eight pattern")
    penalties = reduced_costs(module, patterns, basis, intervals)
    profile = Counter({r: 180 * n for r, n in LOCAL.items()})
    for (_, _, idle), amount in zip(basis, amounts, strict=True):
        require((20 * amount).denominator == 1, "T20 integral primal")
        if idle:
            profile[idle] += int(20 * amount)
    baseline_lower = module.moment(profile, lower, 20)[0]
    return {"cap_interval": [str(lower), str(upper)], "patterns": len(patterns),
            "tight_patterns": len(tight), "all_pattern_margin_lower": str(margin),
            "cap8_bad_patterns": penalties, "uniform_bad_bin_penalty_gt": str(DELTA),
            "relaxation_moment_at_left_lower": str(baseline_lower)}


def verify(data=None):
    if data is None:
        data = authenticate()
    template = decoded(data[ALLOC + "vendor/TEMPLATE.json.gz"], True)
    plan = decoded(data[ALLOC + "vendor/PLAN.json.gz"], True)
    source = source_types(template, plan)
    published_windows = check_published_windows(source, plan)
    cap = cap_premise(data)
    orders = {kind: chronology_result(source, order_for(20, kind), kind)
              for kind in ("stage_major", "replica_major")}
    baseline = decoded(data[ALLOC + "ORDER.json"])
    positive = chronology_result(source, baseline, "published_T74")
    require(positive["replicas"] == 74 and positive["unmatched"] == 0,
            "published staggered order survives necessary matching relaxation")
    lp_lower = Fraction(cap["relaxation_moment_at_left_lower"])
    for result in orders.values():
        gap = result["unmatched"] * DELTA / (73 * 896 * 20)
        require(lp_lower + gap > 1, "complete inherited moment exceeds one at cap left")
        result["moment_excess_over_relaxation_gt"] = str(gap)
        result["moment_at_cap_left_gt"] = str(lp_lower + gap)
    return {"status": "PASS_COUPLED_T20_WINDOW_AUDIT", "source_intervals":
            {str(k): list(v) for k, v in sorted(source.items()) if v[0] == 8},
            "historical_source_windows_checked": published_windows,
            "cap_premise": cap, "orders": orders,
            "positive_T74": {k: v for k, v in positive.items() if k != "groups"},
            "scope": "Two chronology families excluded from the inherited cap; "
                     "arbitrary T20 orders and supplier admission remain open."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    result = verify()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        expected = decoded((PACKAGE / "RESULT.json").read_bytes())
        require(json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
                "complete typed receipt equality")
        print(result["status"], "stage_major_deficit=1857 replica_major_deficit=7500",
              "baseline_T74_deficit=0 cap8_bad_penalty_gt=3/250")


if __name__ == "__main__":
    main()
