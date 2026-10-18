# SPDX-License-Identifier: Apache-2.0
"""Literal capacity witnesses, with all source bins included in the invoice."""

from collections import Counter, defaultdict
from hashlib import sha256
import json

from local import V45, need


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def window_table(template, order, plan):
    need(template["m"] == 73, "source ambient width 73")
    need(len(order) == 666, "666 ordered calls")
    times = {}
    progress = [0] * 74
    for t, entry in enumerate(order):
        need(len(entry) == 2 and all(type(x) is int for x in entry), "call pair")
        stage, replica = entry
        need(0 <= replica < 74 and stage == progress[replica], "replica stage order")
        progress[replica] += 1
        times[replica, stage] = t
    need(progress == [9] * 74, "complete T74 calls")
    capacities, source_bins = {}, set()
    for item in template["idle_children"]:
        child, rank = item["child"], item["rank"]
        need(type(child) is int and type(rank) is int and 0 < rank <= 48,
             "child capacity")
        need(child not in capacities or capacities[child] == rank, "consistent capacity")
        port = item["port"]
        need(type(port) is int and 0 <= port < 112 and (child, port) not in source_bins,
             "unique source child/port")
        source_bins.add((child, port))
        capacities[child] = rank
    need(set(capacities) == set(range(18)), "18 source idle children")
    need(source_bins == {(child, port) for child in range(18) for port in range(112)},
         "complete source bin inventory")
    local_pairs = {e["stage"]: e["pair"] for e in template["recipe"] if e["kind"] == "local"}
    need(set(local_pairs) == set(range(9)), "nine source local pairs")
    stage, touched, specs = None, {}, {}
    for event in template["execution_schedule"]:
        tag = event["kind"]
        if tag == "local_cover_sweep":
            stage = event["stage"]
            touched[local_pairs[stage]] = stage
        elif tag == "bridge":
            touched[event["src"]] = touched[event["dst"]] = stage
        elif tag == "idle_cover_sweep":
            for child in event["child_indices"]:
                if child in capacities:
                    need(child not in specs, "one deadline per child")
                    need(plan["pairs"][str(child)] == event["pair"], "child physical pair")
                    need(plan["sides"][str(child)] in (0, 1), "child physical side")
                    specs[child] = (touched.get(event["pair"], -1), stage)
        else:
            need(tag in ("terminal_Y_translations", "terminal", "bank_padding_cover_sweep",
                         "translate_every_live_family"), "known source event")
    need(set(specs) == set(capacities), "complete deadline inventory")
    windows = {}
    for replica in range(74):
        for child, (start, stop) in specs.items():
            begin = times[replica, start] if start >= 0 else -1
            windows[replica, child] = (capacities[child], begin, times[replica, stop])
    return windows


def verify_fill(fill, order, dispatch, plan, windows, local_data):
    need(fill["columns"] == ["time", "helper", "owner_replica", "child", "port", "offset"],
         "fill columns")
    need(len(fill["rows"]) == 666 * 408, "complete role row count")
    need(len(dispatch) == 666, "complete dispatch count")
    provider_by_call = {}
    for stage, replica, provider in dispatch:
        key = (stage, replica)
        need(key not in provider_by_call and key in map(tuple, order), "unique dispatch call")
        need(provider in local_data, "known dispatch provider")
        provider_by_call[key] = provider
    for stage, replica, provider in fill.get("dispatch_overrides", []):
        need(provider_by_call[stage, replica] == provider, "dispatch override binding")
    coverage = bytearray(666 * 408)
    families = set()
    bins = defaultdict(list)
    masks = {}
    for row in fill["rows"]:
        need(len(row) == 6 and all(type(x) is int for x in row), "integer fill row")
        t, h, replica, child, port, offset = row
        need(0 <= t < 666 and 0 <= h < 408 and 0 <= port < 112, "role bounds")
        role = 408 * t + h
        need(not coverage[role], "unique call/helper role")
        coverage[role] = 1
        need((replica, child) in windows, "existing owner window")
        capacity, begin, stop = windows[replica, child]
        need(begin < t <= stop, "open-start closed-end source window")
        fam = (t, replica, 2 * plan["pairs"][str(child)] + plan["sides"][str(child)], port)
        need(fam not in families, "distinct physical helper families in a call")
        families.add(fam)
        provider = provider_by_call[tuple(order[t])]
        width = local_data[provider]["widths"][h]
        need(0 <= offset and offset + width <= capacity, "positive source slice fits")
        key = (replica, child, port)
        bits = ((1 << width) - 1) << offset
        need(masks.get(key, 0) & bits == 0, "disjoint occupied source axes")
        masks[key] = masks.get(key, 0) | bits
        bins[key].append((offset, t, h, width))
    need(all(coverage), "all helper roles present")
    for key, mask in masks.items():
        width = sum(row[3] for row in bins[key])
        need(mask == (1 << width) - 1, "compact occupied source prefix")
        bins[key].sort()
    return bins, Counter(provider_by_call.values())


def bill(bins, windows, counts, local_data):
    idle = Counter()
    for (replica, child), (capacity, _begin, _stop) in windows.items():
        for port in range(112):
            used = sum(row[3] for row in bins.get((replica, child, port), []))
            need(0 <= used <= capacity, "whole bin capacity")
            if used < capacity:
                idle[capacity - used] += 1
    full = Counter(idle)
    for provider, calls in counts.items():
        full.update({r: n * calls for r, n in local_data[provider]["profile"].items()})
    need(sum(r * n for r, n in full.items()) == 74 * 65088, "complete rank-mass identity")
    return idle, full


def control_case(bins, windows, helper_indices, widened):
    need(set(widened) <= set(V45), "only four V45 controls")
    selected = {helper_indices[h] for h in widened}
    touched = Counter()
    witnesses = []
    for key, rows in sorted(bins.items()):
        increase = sum(row[2] in selected for row in rows)
        if not increase:
            continue
        capacity, begin, end = windows[key[:2]]
        used = sum(row[3] for row in rows)
        remaining = capacity - used
        touched[remaining, increase] += 1
        excess = increase - remaining
        if excess > 0:
            new_widths = [row[3] + (row[2] in selected) for row in rows]
            # Every positive excess in these actual bins is smaller than any
            # one occupant. The cheapest deletion is therefore one shortest
            # whole occurrence; incoming placements could only increase it.
            need(0 < excess <= min(new_widths), "one-departure deletion relaxation")
            witnesses.append(dict(bin=list(key), capacity=capacity, used_before=used,
                                  extra_width=increase, excess=excess,
                                  minimum_evacuated_width=min(new_widths),
                                  source_window=[begin, end],
                                  placements=[list(row) for row in rows]))
    total_added = sum(m * n for (_remaining, m), n in touched.items())
    need(total_added == 666 * len(widened), "each changed endpoint charged at every call")
    result = dict(widened=list(widened), retained_lowered=[h for h in V45 if h not in widened],
                  feasible_without_reassignment=not witnesses,
                  added_local_children={"1": total_added} if total_added else {},
                  added_width=total_added, overfull_bins=len(witnesses),
                  total_excess=sum(w["excess"] for w in witnesses),
                  touched_bins=[dict(old_idle=r, added_width=m, count=n)
                                for (r, m), n in sorted(touched.items())],
                  first_witness=witnesses[0] if witnesses else None,
                  all_witnesses_sha256=digest(witnesses),
                  moved_occurrences_lower_bound=len(witnesses),
                  moved_width_lower_bound=sum(w["minimum_evacuated_width"] for w in witnesses))
    return result, witnesses
