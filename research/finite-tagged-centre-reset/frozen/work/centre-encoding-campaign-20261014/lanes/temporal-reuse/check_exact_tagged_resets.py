"""Optimize all eligible resets through three independent groups."""

from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import json


HERE = Path(__file__).resolve().parent
LANES = HERE.parent
CORE_PIN = "f271842a741584389e166e700e262f161b0dd570ce8c7a540f2717e90ead5205"
CENTRES = [92, 57, 81, 224, 11, 240, 9, 256]
GROUPS = [15, 48, 192]
CUT = 12995


def need(value, reason):
    if not value:
        raise ValueError(reason)


def plus(a, b, q):
    out = dict(a)
    for k, v in b.items():
        v = out.get(k, Q(0)) + q * v
        if v:
            out[k] = v
        else:
            out.pop(k, None)
    return out


def scalar(event):
    op = event[1]
    if op[0] == "add":
        value = Q(op[3], op[4])
        return op[0], op[1][1], op[2][1], value.numerator, value.denominator
    need(op[0] == "scale", "Unknown scalar operation")
    value = Q(op[2], op[3])
    return op[0], op[1][1], None, value.numerator, value.denominator


def sources(events):
    rows = [{i: Q(1)} for i in range(704)]
    resets, kinds = {}, {}
    first = min(i for i, e in enumerate(events[:CUT]) if e[0] == "climb")
    for i, event in enumerate(events[:CUT]):
        target = None
        if event[0] == "climb":
            target = event[2]
            kinds[i] = [any(k < 224 for k in rows[target]), any(k >= 224 for k in rows[target])]
        elif event[0] == "scalar":
            kind, target, source, n, d = scalar(event)
            if kind == "add":
                rows[target] = plus(rows[target], rows[source], Q(n, d))
            else:
                rows[target] = {k: v * Q(n, d) for k, v in rows[target].items() if v * n}
        if target is not None:
            data = any(k < 224 for k in rows[target])
            helper = any(k >= 224 for k in rows[target])
            if not (data and helper):
                resets[i] = [target, "data" if data else "helper"]
    need(max(i for i, x in resets.items() if x[1] == "data") < first,
         "Pure-data resets precede all native errors")
    return first, resets, kinds


def dependency(events, first, resets, kinds):
    bits = [(1 << CENTRES.index(i)) if i in CENTRES else 0 for i in range(704)]
    plans = {g: [] for g in GROUPS}
    sites = {g: [] for g in GROUPS}
    native_groups = {}
    reset_support, native_support = {}, {}
    ignored = []
    for i in range(CUT - 1, first - 1, -1):
        event = events[i]
        target = event[2] if event[0] == "climb" else event[1][1][1] if event[0] == "scalar" else None
        if i in resets:
            b = bits[resets[i][0]]
            reset_support[i] = b
            matches = [g for g in GROUPS if b & g]
            if b:
                need(len(matches) == 1 and b & ~matches[0] == 0, "A reset crosses groups")
                sites[matches[0]].append(i)
            else:
                ignored.append(i)
        if target is None:
            continue
        b = bits[target]
        matches = [g for g in GROUPS if b & g]
        if event[0] == "climb" and b:
            need(len(matches) == 1 and b & ~matches[0] == 0, "A native error crosses groups")
            need(kinds[i] == [True, True], "A possible centre ancestor is not mixed")
            native_groups[i] = matches[0]
            native_support[i] = b
        for g in matches:
            if event[0] == "climb":
                plans[g].append(["native", i, target, event[5]])
            else:
                kind, t, source, n, d = scalar(event)
                need(d > 0 and d & (d - 1) == 0, "A scalar denominator is not dyadic")
                plans[g].append([kind, i, t, source, n, d])
        if event[0] == "scalar":
            kind, t, source, n, _ = scalar(event)
            if kind == "add" and n:
                bits[source] |= bits[t]
            elif kind == "scale" and not n:
                bits[t] = 0
    need([len(sites[g]) for g in GROUPS] == [12, 12, 12], "Three twelve-site groups")
    return plans, {g: sorted(v) for g, v in sites.items()}, native_groups, ignored, reset_support, native_support


def evaluate(plan, sites, mask, modes, responses=None):
    width = len(modes)
    zero = (0,) * width
    # The sum of all dyadic denominators bounds every path denominator.
    power = sum(ins[5].bit_length() - 1 for ins in plan if ins[0] != "native")
    unit = 1 << power
    rows = [zero for _ in range(704)]
    for k, mode in enumerate(modes):
        rows[CENTRES[mode]] = tuple(unit if j == k else 0 for j in range(width))
    reset_bits = {event: k for k, event in enumerate(sites)}
    hist = Counter()
    for ins in plan:
        kind, event, target = ins[:3]
        if event in reset_bits and mask & (1 << reset_bits[event]):
            rows[target] = zero
        value = rows[target]
        if kind == "native":
            if responses is not None:
                responses[event] = [Q(value[modes.index(k)], unit) if k in modes else Q(0)
                                    for k in range(8)]
            support = sum(1 << modes[k] for k, v in enumerate(value) if v)
            if support:
                hist[(ins[3], support)] += 1
        elif any(value):
            _, _, _, source, n, d = ins
            need(all((n * v) % d == 0 for v in value), "Exact integer response grid")
            scaled = tuple(n * v // d for v in value)
            if kind == "add":
                rows[source] = tuple(u + v for u, v in zip(rows[source], scaled))
            else:
                rows[target] = scaled
    return [[rank, support, count] for (rank, support), count in sorted(hist.items())]


def forward_impulse(events, event_index, policy, reset_fields):
    """Propagate one native output error in the forward event order."""
    rows = [Q(0) for _ in range(704)]
    rows[events[event_index][2]] = Q(1)
    if event_index in policy:
        rows[reset_fields[event_index]] = Q(0)
    for i in range(event_index + 1, CUT):
        event = events[i]
        if event[0] == "scalar":
            kind, target, source, n, d = scalar(event)
            if kind == "add":
                rows[target] += Q(n, d) * rows[source]
            else:
                rows[target] *= Q(n, d)
        if i in policy:
            rows[reset_fields[i]] = Q(0)
    return [rows[k] for k in CENTRES]


def direct_controls(events, resets, groups, native_groups, best_all):
    reset_fields = {i: x[0] for i, x in resets.items()}
    policies = {"none": set(), "all_eligible": set(resets), "best_all_queries": set(best_all)}
    controls = {}
    for name, policy in policies.items():
        reverse = {}
        for g in GROUPS:
            group = groups[str(g)]
            mask = sum(1 << k for k, i in enumerate(group["reset_events"]) if i in policy)
            evaluate(group["plan"], group["reset_events"], mask, group["modes"], reverse)
        zero_count = 0
        for i in sorted(native_groups):
            value = forward_impulse(events, i, policy, reset_fields)
            need(value == reverse[i], "Forward and reverse native error responses differ")
            zero_count += not any(value)
        controls[name] = {"native_impulses": len(native_groups), "zero_responses": zero_count,
                          "reset_count": len(policy)}
    return controls


def main():
    raw = gzip.decompress((LANES / "history-encoding/FULL-MODE-PROGRAMS.json.gz").read_bytes())
    need(sha256(raw).hexdigest() == CORE_PIN, "Raw word pin")
    events = json.loads(raw)["backward"]
    first, resets, kinds = sources(events)
    plans, sites, native_groups, ignored, reset_support, native_support = dependency(events, first, resets, kinds)
    groups = {}
    for g in GROUPS:
        modes = [k for k in range(8) if g & (1 << k)]
        submasks = [m for m in range(1, 256) if m & ~g == 0]
        best = {m: None for m in submasks}
        cases = []
        for policy in range(1 << len(sites[g])):
            hist = evaluate(plans[g], sites[g], policy, modes)
            need(all(rank in (1, 4) for rank, _, _ in hist), "Only ranks one and four")
            for m in submasks:
                one = sum(count for rank, support, count in hist if rank == 1 and support & m)
                four = sum(count for rank, support, count in hist if rank == 4 and support & m)
                need(four == m.bit_count(), "One fixed rank-four child per query")
                candidate = (one, policy.bit_count(), policy)
                if best[m] is None or candidate < best[m]:
                    best[m] = candidate
            cases.append(hist)
        groups[str(g)] = {"modes": modes, "reset_events": sites[g], "plan": plans[g], "cases": cases,
                          "minima": {str(m): {"rank_one": a, "rank_four": m.bit_count(), "reset_mask": policy}
                                     for m, (a, _, policy) in best.items()}}
        print("group", g, "cases", len(cases), "full", groups[str(g)]["minima"][str(g)], flush=True)
    subsets = []
    for mask in range(1, 256):
        one = 0
        policy = []
        for g in GROUPS:
            part = mask & g
            if not part:
                continue
            entry = groups[str(g)]["minima"][str(part)]
            one += entry["rank_one"]
            policy.extend(event for k, event in enumerate(sites[g]) if entry["reset_mask"] & (1 << k))
        k = mask.bit_count()
        subsets.append({"mask": mask, "mode_count": k, "rank_one": one, "rank_four": k,
                        "mass": one + 4 * k, "reset_events": sorted(policy),
                        "rank_one_surplus_over_removed_mass": one - 8 * k})
    controls = direct_controls(events, resets, groups, native_groups, subsets[-1]["reset_events"])
    result = {"status": "PASS_EXACT_ALL_PURE_RESET_POLICIES", "core_sha256": CORE_PIN,
              "first_native_event": first, "centres": CENTRES,
              "total_post_native_pure_reset_sites": len([i for i in resets if i >= first]),
              "irrelevant_post_native_reset_events": sorted(ignored),
              "reset_boolean_support": reset_support, "native_boolean_support": native_support,
              "native_group_assignment": native_groups, "groups": groups, "subsets": subsets,
              "independent_forward_impulse_controls": controls,
              "minimum_rank_one_surplus": min(x["rank_one_surplus_over_removed_mass"] for x in subsets),
              "scope": "Exact optimum over every subset of post-scalar or post-native resets on individual ideal pure-data or pure-helper fields before the fixed centre cut. No new scalar edges, basis changes, joint resets, native interfaces, or special child-error contracts."}
    data = (json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n").encode()
    (HERE / "EXACT-TAGGED-RESETS.json.gz").write_bytes(gzip.compress(data, mtime=0))
    summary = {k: v for k, v in result.items() if k not in ("groups", "native_group_assignment", "irrelevant_post_native_reset_events", "reset_boolean_support", "native_boolean_support")}
    summary["complete_payload_sha256"] = sha256(data).hexdigest()
    summary["group_case_counts"] = [len(groups[str(g)]["cases"]) for g in GROUPS]
    (HERE / "EXACT-TAGGED-RESETS.json").write_text(json.dumps(summary, sort_keys=True, indent=2) + "\n")
    print(result["status"])
    print("best by count", [(k, min(x["mass"] for x in subsets if x["mode_count"] == k)) for k in range(1, 9)])
    print("rank-one surplus", result["minimum_rank_one_surplus"])


if __name__ == "__main__":
    main()
