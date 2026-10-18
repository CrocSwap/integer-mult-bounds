# SPDX-License-Identifier: Apache-2.0
"""Independent finite chronological cut and literal owner-geometry check.

Only standard-library modules are imported. In particular, neither source owner
engine nor any producer/search code is executed or imported. The source JSON
widths and paid local profiles are premises; native circuit correctness is not
proved here. Run normally or with python3 -O; all checks use explicit exceptions.
"""

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path


SOURCE_COMMIT = "be191346391661f4d35fc0d1508d0a6029572576"
PORTS = 112
T = 37
HELPERS = 408
INTERVAL = (45, 332)
SWAPS = 1063


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == ".gz" else data)


def symbolic_windows(template, plan):
    """Resolve source-event endpoints once in stage labels, before any retiming."""
    child_ports = defaultdict(dict)
    for row in template["idle_children"]:
        c, p, rank = row["child"], row["port"], row["rank"]
        require(p not in child_ports[c], "duplicate source child/port")
        child_ports[c][p] = rank
    require(set(child_ports) == set(range(18)), "retained source child coverage")
    ranks = {}
    for c, ports in child_ports.items():
        require(set(ports) == set(range(PORTS)), "source port coverage")
        require(len(set(ports.values())) == 1, "source port rank consistency")
        ranks[c] = ports[0]
    local_pairs = {e["stage"]: e["pair"] for e in template["recipe"]
                   if e["kind"] == "local"}
    require(set(local_pairs) == set(range(9)), "local stage coverage")
    last_stage, endpoints = {}, {}
    stage = None
    seen_stages = []
    for event in template["execution_schedule"]:
        kind = event["kind"]
        if kind == "local_cover_sweep":
            stage = event["stage"]
            seen_stages.append(stage)
            last_stage[local_pairs[stage]] = stage
        elif kind == "bridge":
            require(stage is not None, "bridge before source stage")
            for pair in (event["src"], event["dst"]):
                last_stage[pair] = stage
        elif kind == "idle_cover_sweep":
            require(stage is not None, "idle event before source stage")
            pair = event["pair"]
            for child in event["child_indices"]:
                # Bank/padding children are not retained owner windows.
                if child not in ranks:
                    continue
                require(child not in endpoints, "duplicate retained idle endpoint")
                require(plan["pairs"][str(child)] == pair, "source pair binding")
                lo = last_stage.get(pair, -1)
                require(lo < stage, "nonempty source stage window")
                endpoints[child] = (ranks[child], lo, stage)
        else:
            require(kind in {"terminal_Y_translations", "terminal",
                             "bank_padding_cover_sweep", "translate_every_live_family"},
                    "unrecognized source event")
    require(seen_stages == list(range(9)), "source stage progression")
    require(set(endpoints) == set(ranks), "complete retained endpoints")
    return endpoints


def timed_windows(order, replicas, endpoints):
    require(len(order) == 9 * replicas, "literal call count")
    positions = {tuple(call): t for t, call in enumerate(order)}
    require(set(positions) == {(s, r) for s in range(9) for r in range(replicas)},
            "literal call coverage")
    for r in range(replicas):
        require(all(positions[s, r] < positions[s + 1, r] for s in range(8)),
                "replica source chronology")
    return {(r, c): (cap, -1 if lo == -1 else positions[lo, r], positions[hi, r])
            for r in range(replicas) for c, (cap, lo, hi) in endpoints.items()}


def check_plan_windows(plan, windows):
    expected = {f"{r},{c}": [cap, list(range(lo + 1, hi + 1))]
                for (r, c), (cap, lo, hi) in windows.items()}
    require(plan["windows"] == expected, "PLAN window equality")


def check_projection(order37, order74):
    expected = [[s, r + T * b] for s, r in order37 for b in range(2)]
    require(order74 == expected, "exact T74 call projection")


def interval_cut(windows, widths_by_call, first, last):
    require(0 <= first <= last < len(widths_by_call), "cut interval bounds")
    demand = sum(widths_by_call[t].count(7) for t in range(first, last + 1))
    counts = Counter(c for (r, c), (cap, lo, hi) in windows.items()
                     if cap == 16 and hi >= first and lo < last)
    bins = PORTS * sum(counts.values())
    return {"interval_inclusive": [first, last], "calls": last - first + 1,
            "width7_demand": demand, "cap16_abstract_windows_by_child": dict(counts),
            "cap16_bins_touching": bins, "required_outside_cap16": max(0, demand - bins)}


def strongest_contiguous_cut(windows, widths_by_call):
    """All 55,611 intervals, not arbitrary subsets or full scheduling feasibility."""
    n = len(widths_by_call)
    prefix = [0]
    for widths in widths_by_call:
        prefix.append(prefix[-1] + widths.count(7))
    cap16 = [(lo + 1, hi) for cap, lo, hi in windows.values() if cap == 16]
    best, attaining, checked = 0, [], 0
    for first in range(n):
        arrivals = Counter(max(first, lo) for lo, hi in cap16 if hi >= first)
        bins = 0
        for last in range(first, n):
            bins += PORTS * arrivals[last]
            bound = prefix[last + 1] - prefix[first] - bins
            checked += 1
            if bound > best:
                best, attaining = bound, [[first, last]]
            elif bound == best:
                attaining.append([first, last])
    return {"intervals_checked": checked, "maximum_required_outside_cap16": best,
            "attaining_intervals_inclusive": attaining}


def geometry(rows, order, windows, dispatch, providers, plan):
    """All literal roles; no native arithmetic or entering-frame proof."""
    require(len(rows) == len(order) * HELPERS, "complete literal role count")
    helper_masks = [0] * len(order)
    families = [set() for _ in order]
    occupied, bin_widths = {}, defaultdict(list)
    width7 = [0, 0]
    outside = [0, 0]
    cut_cap16, cut_other = [0, 0], [0, 0]
    projected = [set(), set()]
    for row in rows:
        require(len(row) == 6 and all(type(x) is int for x in row), "integer role shape")
        time, helper, owner, child, port, offset = row
        require(0 <= time < len(order) and 0 <= helper < HELPERS and
                0 <= port < PORTS and (owner, child) in windows, "role bounds")
        cap, lo, hi = windows[owner, child]
        require(lo < time <= hi, "literal source window")
        require(not helper_masks[time] & (1 << helper), "duplicate helper role")
        helper_masks[time] |= 1 << helper
        family = (owner, plan["pairs"][str(child)], plan["sides"][str(child)], port)
        require(family not in families[time], "same-call physical family collision")
        families[time].add(family)
        width = providers[dispatch[tuple(order[time])]]["widths"][helper]
        require(0 <= offset and offset + width <= cap, "literal bin capacity")
        key = (owner, child, port)
        mask = ((1 << width) - 1) << offset
        require(not occupied.get(key, 0) & mask, "literal coordinate overlap")
        occupied[key] = occupied.get(key, 0) | mask
        bin_widths[key].append(width)
        copy = order[time][1] // T
        require(owner // T == copy, "source witness copy separation")
        projected[copy].add((time // 2, helper, owner % T, child, port, offset))
        if width == 7:
            width7[copy] += 1
            outside[copy] += cap != 16
            if INTERVAL[0] <= time // 2 <= INTERVAL[1]:
                (cut_cap16 if cap == 16 else cut_other)[copy] += 1
    require(all(m == (1 << HELPERS) - 1 for m in helper_masks), "complete helper identities")
    require(projected[0] == projected[1] and len(projected[0]) == 9 * T * HELPERS,
            "exact T74 role projection")
    idle, patterns = Counter(), Counter()
    for (owner, child), (cap, lo, hi) in windows.items():
        for port in range(PORTS):
            key = (owner, child, port)
            mask = occupied.get(key, 0)
            used = mask.bit_count()
            require(mask == (1 << used) - 1, "literal compact prefix")
            ws = bin_widths.get(key, [])
            if cap == 16:
                require(ws.count(7) <= 1, "cap16 one-width7 pattern restriction")
            patterns[cap, tuple(sorted(ws))] += 1
            if used < cap:
                idle[cap - used] += 1
    profile = Counter(idle)
    for call in order:
        profile.update({int(r): n for r, n in
                        providers[dispatch[tuple(call)]]["actual_paid_profile"].items()})
    return {"roles_checked": len(rows), "width7_roles_per_copy": width7,
            "width7_outside_cap16_per_copy": outside,
            "cut_width7_cap16_per_copy": cut_cap16,
            "cut_width7_outside_cap16_per_copy": cut_other,
            "projected_roles_per_copy": len(projected[0]),
            "idle_profile": dict(sorted(idle.items())),
            "conditional_complete_profile": dict(sorted(profile.items()))}, patterns


def verify_hall(package_root=None):
    root = Path(package_root) if package_root is not None else Path(__file__).resolve().parent
    manifest = read_json(root / "SOURCES.json")
    require(manifest["source_commit"] == SOURCE_COMMIT, "frozen source commit")
    exports = {row.get("export_path", row["path"]): row for row in manifest["files"]}
    hashes = {}

    def source(name):
        rel = "sources/" + name
        path = root / rel
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        require(rel in exports and digest == exports[rel]["sha256"], "source hash: " + rel)
        hashes[rel] = digest
        return read_json(path)

    template = source("allocation/vendor/TEMPLATE.json.gz")
    plan = source("allocation/vendor/PLAN.json.gz")
    order74 = source("allocation/ORDER.json")
    dispatch_rows = source("allocation/DISPATCH.json")
    providers = source("allocation/PROVIDERS.json")
    fill = source("allocation/FILL.json.gz")
    face = source("construction/allocation/T37-FACE-MIX.json")
    patterns_record = source("construction/allocation/T37-PATTERNS.json")
    order37 = plan["order"]
    endpoints = symbolic_windows(template, plan)
    windows37 = timed_windows(order37, T, endpoints)
    check_plan_windows(plan, windows37)
    check_projection(order37, order74)
    windows74 = timed_windows(order74, 2 * T, endpoints)
    dispatch = {(s, r): provider for s, r, provider in dispatch_rows}
    require(len(dispatch_rows) == len(dispatch) == len(order74) and
            set(dispatch) == set(map(tuple, order74)) and
            set(dispatch.values()) <= set(providers), "literal dispatch coverage")
    require(all(dispatch[s, r] == dispatch[s, r + T] for s, r in order37),
            "T74 provider projection")
    expected_inventory = Counter({4: 26, 5: 2, 6: 16, 7: 52, 8: 99, 9: 213})
    require(all(Counter(p["widths"]) == expected_inventory for p in providers.values()),
            "source provider width inventory")
    widths37 = [providers[dispatch[s, r]]["widths"] for s, r in order37]
    cut = interval_cut(windows37, widths37, *INTERVAL)
    require(cut["width7_demand"] == 14976, "cut demand")
    require(cut["cap16_bins_touching"] == 13440, "cut accessible bins")
    require(cut["required_outside_cap16"] == 1536, "cut outside requirement")
    strongest = strongest_contiguous_cut(windows37, widths37)
    require(strongest == {"intervals_checked": 55611,
                         "maximum_required_outside_cap16": 1536,
                         "attaining_intervals_inclusive": [[45, 332]]},
            "complete contiguous-interval maximum")
    require(face["target"] == patterns_record["target"], "final source pattern agreement")
    require(face["widths"] == [4, 5, 6, 7, 8, 9], "pattern width ordering")
    final = Counter({(cap, tuple(counts)): n for cap, counts, n in face["target"]})
    swap = Counter({(16, (0, 0, 0, 0, 2, 0)): 1,
                    (32, (0, 0, 0, 2, 0, 2)): 1,
                    (16, (0, 0, 0, 1, 0, 1)): -1,
                    (32, (0, 0, 0, 1, 2, 1)): -1})
    keys = set(final) | set(swap)
    base = {key: final[key] - SWAPS * swap[key] for key in keys}
    width7_index = face["widths"].index(7)
    reserves = []
    for k in range(SWAPS + 1):
        mix = {key: base[key] + k * swap[key] for key in keys}
        require(min(mix.values()) >= 0, "nonnegative face-family multiplicities")
        require(all(counts[width7_index] <= 1 for (cap, counts), n in mix.items()
                    if cap == 16 and n), "face-family one-width7 restriction")
        outside = sum(n * counts[width7_index] for (cap, counts), n in mix.items()
                      if cap != 16)
        require(outside == SWAPS + k, "exact face-family outside reserve")
        reserves.append(outside)
    first_pass = next(k for k, n in enumerate(reserves) if n >= 1536)
    require(first_pass == 473 and reserves[472] == 1535 and reserves[473] == 1536,
            "sharp necessary face-family threshold")
    require(fill["columns"] == ["time", "helper", "owner_replica", "child", "port", "offset"],
            "literal FILL columns")
    require(fill["dispatch_overrides"] == [], "no unhandled fill dispatch overrides")
    witness, actual_patterns = geometry(fill["rows"], order74, windows74,
                                      dispatch, providers, plan)
    expected_patterns = Counter()
    for (cap, counts), n in final.items():
        ws = tuple(w for w, count in zip(face["widths"], counts) for _ in range(count))
        expected_patterns[cap, ws] += 2 * n
    require(actual_patterns == expected_patterns, "literal final face pattern coverage")
    require(witness["width7_roles_per_copy"] == [17316, 17316] and
            witness["width7_outside_cap16_per_copy"] == [2126, 2126],
            "literal width7 counts")
    controls = []

    def reject(name, fn, message):
        try:
            fn()
        except ValueError as error:
            require(str(error) == message, "incorrect control rejection: " + name)
            controls.append({"name": name, "reason": message})
        else:
            raise ValueError("accepted defect: " + name)

    # A real role moved to its excluded source endpoint, preserving all widths.
    row_index = next(i for i, row in enumerate(fill["rows"])
                     if windows74[row[2], row[3]][1] >= 0 and
                     providers[dispatch[tuple(order74[row[0]])]]["widths"][row[1]] == 7)
    rows = list(fill["rows"])
    changed = list(rows[row_index])
    changed[0] = windows74[changed[2], changed[3]][1]
    rows[row_index] = changed
    reject("role_at_excluded_lower_endpoint",
           lambda: geometry(rows, order74, windows74, dispatch, providers, plan),
           "literal source window")
    bad_plan = {**plan, "windows": deepcopy(plan["windows"])}
    key = next(key for key, value in bad_plan["windows"].items() if value[1][0] > 0)
    bad_plan["windows"][key][1].insert(0, bad_plan["windows"][key][1][0] - 1)
    reject("expanded_source_window", lambda: check_plan_windows(bad_plan, windows37),
           "PLAN window equality")
    rows = list(fill["rows"])
    first, second = rows[0], list(rows[1])
    require(first[0] == second[0], "family control same call")
    second[2:5] = first[2:5]
    rows[1] = second
    reject("duplicate_same_call_physical_family",
           lambda: geometry(rows, order74, windows74, dispatch, providers, plan),
           "same-call physical family collision")
    reject("missing_width7_role",
           lambda: geometry(fill["rows"][:row_index] + fill["rows"][row_index + 1:],
                            order74, windows74, dispatch, providers, plan),
           "complete literal role count")
    def false_demand():
        require(cut["width7_demand"] - 1 == sum(widths37[t].count(7)
                for t in range(INTERVAL[0], INTERVAL[1] + 1)), "cut demand")
    reject("undercounted_width7_demand", false_demand, "cut demand")
    bad_order = deepcopy(order74)
    bad_order[0], bad_order[1] = bad_order[1], bad_order[0]
    reject("changed_interleaving_endpoint", lambda: check_projection(order37, bad_order),
           "exact T74 call projection")
    naive_priority = [list(call) for call in sorted(map(tuple, order37),
                      key=lambda call: (4 * call[0] + call[1], call[0], call[1]))]
    require(naive_priority != order37, "source chronology differs from naive priority")
    require(all(hashlib.sha256((root / p).read_bytes()).hexdigest() == h
                for p, h in hashes.items()), "source input drift")
    return {"status": "PASS_INDEPENDENT_CHRONOLOGICAL_FACE_CUT",
            "source_commit": SOURCE_COMMIT, "source_sha256": hashes,
            "symbolic_stage_windows": {str(k): list(v) for k, v in endpoints.items()},
            "PLAN_matches_priority_4s_plus_r": False, "T37_windows_checked": len(windows37),
            "T74_exact_call_and_role_projection": True, "cut": cut,
            "all_contiguous_intervals": strongest,
            "face_family": {"integer_k_inclusive": [0, 1063],
                            "outside_width7_formula": "1063+k",
                            "necessary_k_lower_bound": first_pass,
                            "k472": "REJECTED_BY_CUT",
                            "k473": "PASSES_THIS_NECESSARY_CUT_ONLY"},
            "literal_witness": witness, "controls": controls,
            "scope": "Finite literal owner geometry conditional on source ordered provider widths; "
                     "written necessary inequality for this fixed pattern face. No sufficiency, "
                     "native circuit admission, formal kernel proof, or new kappa claim."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = verify_hall()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf8")
    print(text, end="")


if __name__ == "__main__":
    main()
