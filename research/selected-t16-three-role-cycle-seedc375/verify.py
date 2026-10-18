"""Exact census of selected-map, same-invocation three-owner cycles.

This is a scoped negative result. It does not search cross-call cycles or
longer owner-exchange sequences. The selected source map and both moment
engines are pinned in SOURCES.json and checked against the frozen base by
scripts/research_package.py.
"""
from collections import Counter, defaultdict
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PLAN_PATH = "research/complex-t16-rare-pattern-exchanges/data/PLAN.json"
OWNERS_PATH = "research/complex-t16-rare-pattern-exchanges/data/OWNERS.json.gz"
ASSEMBLY_PATH = "research/community-frontier1094-audit/ASSEMBLY.json"
SELECTED_PATH = "certificates/selected-result.json"
CEILING_PATH = "research/complex-local-word-ceiling/RESULT.json"
BIT_PATH = "research/e8-bit-p111-tuned/tune/EXPECTED.json"
MOMENT_PATH = "research/complex-k492-owner-repair/vendor/multicold/engines/moment.py"
BASE_TWO_PATH = "research/complex-k492-owner-repair/vendor/multicold/engines/base_two_moment.py"
V = 112
HELPERS = 480
CALLS = 144
M = 73
W = 14336
ALPHA_DENOMINATOR_TICK = 10**24

PINS = {
    PLAN_PATH: "7bd786ba8e66408f02aa9ef446eaf20c1bfe981ea2e4dd1e5a929f0aa7767bc0",
    OWNERS_PATH: "87902c528dfab7d503dcf8a784260e3ab6fb7424c418a1820f7261f25be7b6bc",
    ASSEMBLY_PATH: "1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045",
    SELECTED_PATH: "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32",
    CEILING_PATH: "d91d6c46509875abf1f61de67c2609656d3dc685451299f83caa6f922493692d",
    BIT_PATH: "b9f0e5ca038abe837b0007c8fe006f366a6f02009244ac57705a8a200e2301f4",
    MOMENT_PATH: "81cbc864e106418fc7854322746f72180cb8110ff39f74450a3b8d55a82c1482",
    BASE_TWO_PATH: "aee70c242a2f1d225528fabe2002e1564d1dc884797c07d28a831c7878ee9098",
}


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def read_json(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def load_engine(relative, module_name):
    spec = importlib.util.spec_from_file_location(module_name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rank_histogram(values):
    return tuple(sorted(Counter(r for r in values if r > 0).items()))


def cycle_slacks(old, widths):
    """A(width x)->B, B(width y)->C, C(width z)->A."""
    ra, rb, rc = old
    x, y, z = widths
    return (ra + x - z, rb + y - x, rc + z - y)


def distinct_type_support(types, counts):
    return all(counts[t] >= n for t, n in Counter(types).items())


def interval_difference(old_hist, new_hist, rank_costs, engine_name):
    """Certified interval for cost(new)-cost(old), with rank 0 priced as zero."""
    old, new = dict(old_hist), dict(new_hist)
    lower = sum(n * rank_costs[r][0] for r, n in new.items())
    lower -= sum(n * rank_costs[r][1] for r, n in old.items())
    upper = sum(n * rank_costs[r][1] for r, n in new.items())
    upper -= sum(n * rank_costs[r][0] for r, n in old.items())
    return {"lower": str(lower), "upper": str(upper), "engine": engine_name}


def selected_supplier_receipts(plan, assembly, bit_data, M_engine, B_engine):
    complex_profile = {int(r): int(n) for r, n in assembly["complex_profile"].items()}
    require(complex_profile == {int(r): int(n) for r, n in plan["profile"].items()},
            "selected PLAN and accepted assembly profile differ")
    alpha = Q(assembly["complex_lower"])
    bit = bit_data["nine"]
    bit_profile = {int(r): int(n) for r, n in bit["profile"].items()}
    bit_alpha = Q(bit["bit_lower"])

    def paired_moment(profile, m, live, at, bad):
        mercator = M_engine.moment(profile, m, live, at, bad)
        base_two = B_engine.moment(m, live, list(profile.items()), at)
        if bad:
            surcharge_profile = [(1, 32 * m * m * sum(profile.values()))]
            sl, su = B_engine.moment(m, live, surcharge_profile, at)
            base_two = (base_two[0] + sl / 10**16, base_two[1] + su / 10**16)
        return mercator, base_two

    complex_now = paired_moment(complex_profile, M, W, alpha, False)
    complex_next = paired_moment(complex_profile, M, W,
                                 alpha + Q(1, ALPHA_DENOMINATOR_TICK), False)
    require(complex_now[0][0] - 1 == Q(assembly["moments"][2]["mercator"][0]),
            "selected complex Mercator lower receipt mismatch")
    require(complex_now[0][1] - 1 == Q(assembly["moments"][2]["mercator"][1]),
            "selected complex Mercator upper receipt mismatch")
    require(complex_now[1][0] - 1 == Q(assembly["moments"][2]["base_two"][0]),
            "selected complex base-two lower receipt mismatch")
    require(complex_now[1][1] - 1 == Q(assembly["moments"][2]["base_two"][1]),
            "selected complex base-two upper receipt mismatch")
    require(complex_now[0][1] < 1 and complex_now[1][1] < 1,
            "selected complex endpoint does not pass")
    require(complex_next[0][0] > 1 and complex_next[1][0] > 1,
            "selected complex next tick is not rejected")

    bit_live = int(bit["bit"]["live"])
    bit_now = paired_moment(bit_profile, 64, bit_live, bit_alpha, True)
    bit_next = paired_moment(bit_profile, 64, bit_live,
                             bit_alpha + Q(1, ALPHA_DENOMINATOR_TICK), True)
    require(str(bit_alpha) == assembly["bit_lower"], "selected bit endpoint differs")
    require(bit_now[0][1] < 1 and bit_now[1][1] < 1,
            "unchanged bit supplier endpoint does not pass")
    require(bit_next[0][0] > 1 and bit_next[1][0] > 1,
            "unchanged bit supplier next tick is not rejected")
    return {
        "complex_endpoint": str(alpha),
        "complex_moment_upper_below_one": True,
        "complex_next_tick_lower_above_one": True,
        "bit_endpoint": str(bit_alpha),
        "bit_moment_upper_below_one_with_selected_surcharge": True,
        "bit_next_tick_lower_above_one_with_selected_surcharge": True,
        "bit_profile_sha256": PINS[BIT_PATH],
        "binding_side": assembly["binding"],
    }


def load_and_check_map():
    plan = read_json(PLAN_PATH)
    with gzip.open(ROOT / OWNERS_PATH, "rt", encoding="utf-8") as stream:
        owners = json.load(stream)
    require((plan["K"], plan["T"], plan["M"], plan["L"], plan["live"]) == (4, 16, 73, 9, 14336),
            "not the pinned selected T16 geometry")
    order = [tuple(c) for c in plan["order"]]
    require(len(order) == CALLS and len(set(order)) == CALLS, "call order is incomplete")
    caps = {}
    windows = {}
    family_of = {}
    for key, (cap, times) in plan["windows"].items():
        owner_replica, child = map(int, key.split(","))
        require(len(times) == len(set(times)), "duplicate call in a group window")
        for port in range(V):
            g = (owner_replica, child, port)
            caps[g] = int(cap)
            windows[g] = set(times)
            family_of[g] = (owner_replica * 8 * V
                            + (2 * plan["pairs"][str(child)] + plan["sides"][str(child)]) * V
                            + port)
    used = Counter()
    by_call = defaultdict(list)
    group_at_call = {}
    widths_by_helper = {}
    for z in owners:
        t, h = int(z["time"]), int(z["helper"])
        g = (int(z["owner_replica"]), int(z["child"]), int(z["port"]))
        require(0 <= t < CALLS and 0 <= h < HELPERS, "role outside the selected domain")
        require((int(z["stage"]), int(z["replica"])) == order[t], "role call key mismatch")
        require(g in caps and t in windows[g], "role violates its selected window")
        require(int(z["width"]) > 0, "nonpositive helper width")
        require(int(z["copy"]) == g[0] * V + g[2], "copy-coordinate mismatch")
        require(int(z["family"]) == family_of[g], "physical-family mismatch")
        require((g, t) not in group_at_call, "more than one role in a group at one call")
        group_at_call[(g, t)] = z
        previous = widths_by_helper.setdefault(h, int(z["width"]))
        require(previous == int(z["width"]), "helper width changes across calls")
        used[g] += int(z["width"])
        by_call[t].append(z)
    require(len(owners) == CALLS * HELPERS, "owner role inventory count mismatch")
    require(set(widths_by_helper) == set(range(HELPERS)), "helper IDs are not complete")
    require(all(len(by_call[t]) == HELPERS for t in range(CALLS)), "a call has the wrong role count")
    for t, roles in by_call.items():
        require(len({int(z["helper"]) for z in roles}) == HELPERS, "helper repeated in one call")
        require(len({int(z["family"]) for z in roles}) == HELPERS,
                "physical family repeated in one call")
    require(all(used[g] <= cap for g, cap in caps.items()), "selected owner map exceeds a group capacity")
    remainder = {g: cap - used[g] for g, cap in caps.items()}
    require(all(r >= 0 for r in remainder.values()), "negative source slack")
    idle_histogram = Counter(remainder.values())
    idle_histogram.pop(0, None)
    expected_idle = {1: 2276, 3: 377, 7: 7, 48: 4866}
    require(dict(sorted(idle_histogram.items())) == expected_idle,
            "selected owner-map idle histogram mismatch")
    return plan, owners, caps, windows, family_of, remainder, by_call, group_at_call


def find_exact_domain(plan, owners, caps, windows, family_of, remainder, by_call,
                      group_at_call, assembly, M_engine, B_engine):
    alpha = Q(assembly["complex_lower"])
    full_profile = {int(r): int(n) for r, n in assembly["complex_profile"].items()}
    rank_costs = {}
    ranks_needed = set(full_profile)
    for r in range(1, 49):
        mercator = M_engine.moment({r: 1}, M, W, alpha, False)
        base_two = B_engine.moment(M, W, [(r, 1)], alpha)
        rank_costs[r] = (mercator, base_two)

    supported_patterns = capacity_feasible_patterns = 0
    transfer_states = set()
    witnesses_by_transition = {}
    for t in range(CALLS):
        members = defaultdict(list)
        for z in by_call[t]:
            g = (int(z["owner_replica"]), int(z["child"]), int(z["port"]))
            typ = (remainder[g], int(z["width"]))
            members[typ].append(z)
        counts = Counter({typ: len(rows) for typ, rows in members.items()})
        for type_a, type_b, type_c in __import__("itertools").product(counts, repeat=3):
            types = (type_a, type_b, type_c)
            if not distinct_type_support(types, counts):
                continue
            supported_patterns += 1
            old = (type_a[0], type_b[0], type_c[0])
            widths = (type_a[1], type_b[1], type_c[1])
            new = cycle_slacks(old, widths)
            if min(new) < 0:
                continue
            capacity_feasible_patterns += 1
            transfer_states.add((*type_a, *type_b, *type_c, new))
            old_hist, new_hist = rank_histogram(old), rank_histogram(new)
            transition = (old_hist, new_hist)
            if transition not in witnesses_by_transition:
                picked = []
                used_groups = set()
                for typ in types:
                    role = next((row for row in members[typ]
                                 if (int(row["owner_replica"]), int(row["child"]),
                                     int(row["port"])) not in used_groups), None)
                    require(role is not None, "compressed type support lost distinct groups")
                    g = (int(role["owner_replica"]), int(role["child"]), int(role["port"]))
                    used_groups.add(g)
                    picked.append((g, role))
                require(len(used_groups) == 3, "cycle groups are not distinct")
                require(len({family_of[g] for g, _ in picked}) == 3,
                        "occupied cycle groups do not have distinct families")
                witnesses_by_transition[transition] = {
                    "call": t,
                    "old_slacks": list(old),
                    "outgoing_widths": list(widths),
                    "new_slacks": list(new),
                    "moves": [
                        {"helper": int(picked[i][1]["helper"]),
                         "source_group": list(picked[i][0]),
                         "destination_group": list(picked[(i + 1) % 3][0]),
                         "width": int(picked[i][1]["width"])}
                        for i in range(3)
                    ],
                }

    require(supported_patterns == 49408, "supported-pattern census changed")
    require(capacity_feasible_patterns == 4417, "capacity-feasible pattern census changed")
    require(len(transfer_states) == 255, "transfer-state census changed")
    require(len(witnesses_by_transition) == 35, "rank-histogram transition census changed")

    priced = []
    strict_increases = []
    equal_histograms = strictly_worse = improving = 0
    for (old_hist, new_hist), witness in sorted(witnesses_by_transition.items()):
        if old_hist == new_hist:
            equal_histograms += 1
            priced.append({"old_histogram": old_hist, "new_histogram": new_hist,
                           "classification": "exact-tie"})
            continue
        mercator = interval_difference(old_hist, new_hist,
                                       {r: pair[0] for r, pair in rank_costs.items()},
                                       "selected Mercator")
        base_two = interval_difference(old_hist, new_hist,
                                       {r: pair[1] for r, pair in rank_costs.items()},
                                       "selected base-two")
        ml, mu = Q(mercator["lower"]), Q(mercator["upper"])
        bl, bu = Q(base_two["lower"]), Q(base_two["upper"])
        if mu < 0 or bu < 0:
            improving += 1
        elif ml > 0 and bl > 0:
            strictly_worse += 1
        else:
            raise AssertionError("exact rank-moment intervals did not decide a nonidentity transition")
        row = {"old_histogram": old_hist, "new_histogram": new_hist,
               "classification": "strict-increase" if ml > 0 and bl > 0 else "strict-decrease",
               "mercator_delta": [mercator["lower"], mercator["upper"]],
               "base_two_delta": [base_two["lower"], base_two["upper"]]}
        priced.append(row)
        if ml > 0 and bl > 0:
            strict_increases.append((ml, row, witness))
    require(equal_histograms == 19 and strictly_worse == 16 and improving == 0,
            "exact selected-endpoint price classification changed")
    _, worst_transition, worst_witness = min(strict_increases, key=lambda entry: entry[0])
    require(Q(worst_transition["mercator_delta"][0]) > 0,
            "minimum-cost nonidentity transition is not strictly more expensive")
    require(Q(worst_transition["base_two_delta"][0]) > 0,
            "second engine does not certify the minimum increase")
    return {
        "ordered_supported_type_patterns": supported_patterns,
        "capacity_feasible_type_patterns": capacity_feasible_patterns,
        "unique_ordered_transfer_states": len(transfer_states),
        "distinct_rank_histogram_transitions": len(witnesses_by_transition),
        "equal_histogram_transitions": equal_histograms,
        "strictly_more_expensive_transitions": strictly_worse,
        "strictly_cheaper_transitions": improving,
        "minimum_strict_increase": {
            "old_histogram": worst_transition["old_histogram"],
            "new_histogram": worst_transition["new_histogram"],
            "mercator_delta": worst_transition["mercator_delta"],
            "base_two_delta": worst_transition["base_two_delta"],
            "feasible_source_witness": worst_witness,
        },
        "all_transitions": priced,
    }


def verify():
    for relative, expected in PINS.items():
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        require(actual == expected, "source hash mismatch: " + relative)
    selected = read_json(SELECTED_PATH)
    assembly = read_json(ASSEMBLY_PATH)
    ceiling = read_json(CEILING_PATH)
    bit_data = read_json(BIT_PATH)
    require(selected["kappa"] == "836330098538459/500000000000000000",
            "selected record changed")
    require(assembly["binding"] == "complex", "selected binding side changed")
    alpha_cap = Q(ceiling["ceiling"]["a_ceiling"])
    kappa_cap = alpha_cap / (1 + alpha_cap)
    require(ceiling["ceiling"]["kappa_upper_bound"] == "0.0016872026453254019",
            "fixed-word packing ceiling changed")
    M_engine = load_engine(MOMENT_PATH, "selected_moment_engine")
    B_engine = load_engine(BASE_TWO_PATH, "selected_base_two_engine")
    supplier_prices = selected_supplier_receipts(read_json(PLAN_PATH), assembly,
                                                 bit_data, M_engine, B_engine)
    plan, owners, caps, windows, family_of, remainder, by_call, group_at_call = load_and_check_map()
    census = find_exact_domain(plan, owners, caps, windows, family_of, remainder,
                               by_call, group_at_call, assembly, M_engine, B_engine)
    current_kappa = Q(selected["kappa"])
    return {
        "status": "SCOPED_NEGATIVE_RESULT_NO_IMPROVING_SAME_CALL_3_CYCLES",
        "assignment": {
            "seed": "c37585e64a1b0aaf41a29afcbfd3f5c7",
            "track": "incumbent-optimization",
            "task_id": "selected-packing",
            "priority_revision": 3,
            "base_commit": "0b1cccf86e2f5132ed286a26ef0a681a495740ea",
            "selected_record_sha256": PINS[SELECTED_PATH],
            "claim": "https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18923820",
        },
        "overlap_snapshot": {
            "refreshed_at": "2026-10-14T12:38:03Z/12:39:37Z",
            "open_prs": 529,
            "discussions": 508,
            "complete_pagination": True,
            "nearest_open_prs": [
                {"number": 1790, "head": "48ee04ee708081c8713e8868a370bbbf5aa099e1",
                 "scope": "selected PR1094 map two-role census; three-role cycles left open"},
                {"number": 1617, "head": "536bc90ea2de310e0e08d2cb65f7add1d9de92b5",
                 "scope": "selected PR1094 neutral two-move census"},
                {"number": 1819, "head": "eb519ed5b0013e03f4d9657730d57acee65cafd4",
                 "scope": "selected PR1094 neutral move followed by strict two-step gain"},
                {"number": 1154, "head": "390de2866a03758e7f4ddbb2846e5b2ee4e72154",
                 "scope": "positive three-owner cycle on the different PR1117 route and changed local word"},
            ],
        },
        "selected_source": {
            "plan_sha256": PINS[PLAN_PATH],
            "owners_sha256": PINS[OWNERS_PATH],
            "calls": CALLS,
            "roles_per_call": HELPERS,
            "owner_groups_in_capacity_model": len(caps),
            "whole_role_placements": len(owners),
            "positive_idle_remainders": {str(r): n for r, n in sorted(Counter(remainder.values()).items()) if r},
        },
        "census": census,
        "supplier_prices": supplier_prices,
        "packing_cap": {
            "a_upper_bound": str(alpha_cap),
            "kappa_upper_bound": str(kappa_cap),
            "selected_kappa": str(current_kappa),
            "remaining_kappa_headroom": str(kappa_cap - current_kappa),
            "headroom_realized_by_this_domain": "0",
            "fraction_of_packing_headroom_realized": "0",
        },
        "scope_limit": "One same-invocation three-role permutation among three distinct currently occupied groups. Cross-call cycles, chains, longer sequences, changed local words and a global packing optimum are not covered.",
    }


def main():
    result = verify()
    (HERE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(result["status"])
    print(json.dumps({k: result["census"][k] for k in (
        "ordered_supported_type_patterns", "capacity_feasible_type_patterns",
        "unique_ordered_transfer_states", "distinct_rank_histogram_transitions",
        "equal_histogram_transitions", "strictly_more_expensive_transitions",
        "strictly_cheaper_transitions")}, sort_keys=True))
    print("selected packing cap", result["packing_cap"]["kappa_upper_bound"],
          "headroom realized", result["packing_cap"]["fraction_of_packing_headroom_realized"])


if __name__ == "__main__":
    main()
