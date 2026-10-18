# SPDX-License-Identifier: Apache-2.0
"""Independent finite owner geometry, with no predecessor Python imports.

Source-event semantics and physical-family identities follow the pinned
rank7-joint-endframes allocation. Windows are derived first in stage coordinates
and then translated into the literal interleaved call order.

Python allocates during checking. The managed-runtime deviation from fixed
allocation is bounded by 74 replicas, 666 calls, 271728 roles and 149184 bins.
The checker owns all temporary state and performs no I/O or shared mutation.
"""

from collections import Counter

MAX_REPLICAS = 74
MAX_EVENTS = 4096
HELPERS = 408
PORTS = 112


def need(condition, message):
    if not condition:
        raise ValueError(message)


def _call_times(order, replicas):
    need(type(replicas) is int and 1 <= replicas <= MAX_REPLICAS, "replica limit")
    need(type(order) is list and len(order) == 9 * replicas, "call count")
    progress = [0] * replicas
    times = {}
    for time, call in enumerate(order):
        need(type(call) in (list, tuple) and len(call) == 2, "call shape")
        stage, owner = call
        need(type(stage) is int and type(owner) is int, "integer call")
        need(0 <= owner < replicas and stage == progress[owner], "call chronology")
        need(0 <= stage < 9, "stage bounds")
        times[owner, stage] = time
        progress[owner] += 1
    need(progress == [9] * replicas, "complete call coverage")
    return times


def _stage_intervals(template):
    need(type(template) is dict, "template object")
    children = template.get("idle_children")
    recipe = template.get("recipe")
    events = template.get("execution_schedule")
    need(type(children) is list and len(children) == 18 * PORTS, "idle child count")
    need(type(recipe) is list and len(recipe) < MAX_EVENTS, "recipe limit")
    need(type(events) is list and len(events) < MAX_EVENTS, "event limit")
    ranks, pairs, slots = {}, {}, set()
    for child in children:
        need(type(child) is dict, "idle child shape")
        index, rank, port = child.get("child"), child.get("rank"), child.get("port")
        need(type(index) is int and 0 <= index < 18, "idle child index")
        need(type(rank) is int and rank in (8, 16, 32, 48), "idle child rank")
        need(type(port) is int and 0 <= port < PORTS, "idle child port")
        need((index, port) not in slots, "duplicate idle child port")
        need(index not in ranks or ranks[index] == rank, "idle child rank disagreement")
        slots.add((index, port))
        ranks[index] = rank
    for event in recipe:
        need(type(event) is dict, "recipe event shape")
        if event.get("kind") == "local":
            stage, pair = event.get("stage"), event.get("pair")
            need(type(stage) is int and 0 <= stage < 9, "local recipe stage")
            need(type(pair) is int and 0 <= pair < 4, "local recipe pair")
            need(stage not in pairs, "duplicate local recipe stage")
            pairs[stage] = pair
    need(set(pairs) == set(range(9)), "nine local recipe stages")
    return _scan_intervals(events, ranks, pairs), ranks


def _scan_intervals(events, ranks, pairs):
    touched, intervals, seen = {}, {}, set()
    stage = None
    for event in events:
        need(type(event) is dict, "source event shape")
        kind = event.get("kind")
        if kind in ("bank_padding_cover_sweep", "translate_every_live_family"):
            continue
        if kind == "local_cover_sweep":
            stage = event.get("stage")
            need(type(stage) is int and stage == len(seen), "source stage order")
            need(stage in pairs and stage not in seen, "source local stage")
            seen.add(stage)
            touched[pairs[stage]] = stage
        else:
            need(stage is not None, "source event before first local stage")
            if kind == "bridge":
                source, target = event.get("src"), event.get("dst")
                need(
                    all(type(p) is int and 0 <= p < 4 for p in (source, target)),
                    "bridge pair",
                )
                touched[source] = touched[target] = stage
            elif kind == "idle_cover_sweep":
                pair, indices = event.get("pair"), event.get("child_indices")
                need(type(pair) is int and 0 <= pair < 4, "idle source pair")
                need(
                    type(indices) is list and len(indices) <= 18, "idle source children"
                )
                for child in indices:
                    need(
                        type(child) is int and 0 <= child < 20,
                        "unknown idle source child",
                    )
                    if child not in ranks:
                        continue  # Terminal children 18 and 19 have no borrowable rank.
                    need(child not in intervals, "repeated idle source child")
                    intervals[child] = touched.get(pair, -1), stage
            else:
                need(
                    kind in ("terminal_Y_translations", "terminal"),
                    "unknown source event",
                )
    need(
        seen == set(range(9)) and set(intervals) == set(ranks),
        "complete source intervals",
    )
    return intervals


def windows(template, order, T):
    """Map each owner and child to its capacity and half-open source window."""
    times = _call_times(order, T)
    intervals, ranks = _stage_intervals(template)
    result = {}
    for owner in range(T):
        for child, (start_stage, end_stage) in intervals.items():
            lower = -1 if start_stage == -1 else times[owner, start_stage]
            result[owner, child] = ranks[child], lower, times[owner, end_stage]
    return result


def _provider_data(dispatch, order, providers):
    need(type(providers) is dict and 1 <= len(providers) <= 8, "provider count")
    parsed = {}
    for name, provider in providers.items():
        need(type(name) is str and len(name) <= 128, "provider name")
        need(type(provider) is dict, "provider shape")
        widths, profile = provider.get("widths"), provider.get("actual_paid_profile")
        need(type(widths) is list and len(widths) == HELPERS, "ordered helper widths")
        need(all(type(w) is int and 4 <= w <= 9 for w in widths), "helper width bounds")
        need(type(profile) is dict and 1 <= len(profile) <= 72, "local profile shape")
        paid = Counter()
        for rank, count in profile.items():
            need(
                type(rank) is int or (type(rank) is str and len(rank) <= 2),
                "local rank length",
            )
            need(type(rank) is int or rank.isdecimal(), "local rank")
            rank = int(rank)
            need(1 <= rank < 73 and rank not in paid, "local rank bounds or duplicate")
            need(type(count) is int and 0 < count <= 10000, "local count bounds")
            paid[rank] = count
        parsed[name] = widths, paid
    need(type(dispatch) is dict and len(dispatch) == len(order), "dispatch count")
    need(set(dispatch) == set(map(tuple, order)), "dispatch call coverage")
    need(
        all(type(name) is str and name in parsed for name in dispatch.values()),
        "dispatch provider",
    )
    return parsed


def _physical_families(plan, children):
    need(type(plan) is dict, "plan shape")
    pairs, sides = plan.get("pairs"), plan.get("sides")
    need(type(pairs) is dict and type(sides) is dict, "plan family maps")
    need(len(pairs) == len(sides) == len(children), "plan family count")
    expected = {str(child) for child in children}
    need(set(pairs) == set(sides) == expected, "plan family child coverage")
    result = {}
    for child in children:
        pair, side = pairs[str(child)], sides[str(child)]
        need(type(pair) is int and 0 <= pair < 4, "family pair bounds")
        need(type(side) is int and side in (0, 1), "family side bounds")
        result[child] = 2 * pair + side
    return result


def _roles(order, fill, dispatch, win, families, providers):
    need(type(fill) is dict, "fill object")
    columns = ["time", "helper", "owner_replica", "child", "port", "offset"]
    need(fill.get("columns") == columns, "literal role columns")
    rows = fill.get("rows")
    need(
        type(rows) is list and len(rows) == len(order) * HELPERS, "complete role count"
    )
    need(len(rows) <= 271728, "role limit")
    overrides = fill.get("dispatch_overrides", [])
    need(
        type(overrides) is list and len(overrides) <= len(order),
        "dispatch override limit",
    )
    for override in overrides:
        need(type(override) is list and len(override) == 3, "dispatch override shape")
        stage, owner, provider = override
        need(type(stage) is int and type(owner) is int, "dispatch override call")
        need(dispatch.get((stage, owner)) == provider, "dispatch override binding")
    helpers = [0] * len(order)
    occupied_families = [set() for _ in order]
    masks, patterns = {}, {}
    for row in rows:
        need(type(row) is list and len(row) == 6, "integer role shape")
        need(all(type(x) is int for x in row), "integer role shape")
        time, helper, owner, child, port, offset = row
        need(
            0 <= time < len(order) and 0 <= helper < HELPERS,
            "role call or helper bounds",
        )
        need(0 <= port < PORTS and (owner, child) in win, "owner child or port bounds")
        cap, lower, upper = win[owner, child]
        need(lower < time <= upper, "literal source window")
        helper_bit = 1 << helper
        need(not helpers[time] & helper_bit, "duplicate helper")
        helpers[time] |= helper_bit
        family = owner, families[child], port
        need(family not in occupied_families[time], "same-call family collision")
        occupied_families[time].add(family)
        widths, _ = providers[dispatch[tuple(order[time])]]
        width = widths[helper]
        need(0 <= offset and offset + width <= cap, "bin capacity")
        key = owner, child, port
        mask = ((1 << width) - 1) << offset
        need(not masks.get(key, 0) & mask, "bin overlap")
        masks[key] = masks.get(key, 0) | mask
        patterns.setdefault(key, []).append(width)
    need(helpers == [(1 << HELPERS) - 1] * len(order), "complete helper identities")
    return masks, patterns


def _invoice(win, masks, patterns, order, dispatch, providers):
    idle, histogram = Counter(), Counter()
    for (owner, child), (capacity, _, _) in win.items():
        for port in range(PORTS):
            key = owner, child, port
            mask = masks.get(key, 0)
            used = mask.bit_count()
            need(mask == (1 << used) - 1, "compact bin prefix")
            if used < capacity:
                idle[capacity - used] += 1
            histogram[capacity, tuple(sorted(patterns.get(key, [])))] += 1
    profile = idle.copy()
    for call in order:
        _, local = providers[dispatch[tuple(call)]]
        profile.update(local)
    return (
        profile,
        idle,
        [
            [cap, list(widths), count]
            for (cap, widths), count in sorted(histogram.items())
        ],
    )


def check(order, fill, dispatch, plan, template, providers, buffers=91):
    """Check all literal owners and return the complete invoice and stock count."""
    need(type(order) is list and 0 < len(order) <= 9 * MAX_REPLICAS, "call limit")
    need(len(order) % 9 == 0, "nine calls per replica")
    need(type(buffers) is int and 0 <= buffers <= 480, "private buffer limit")
    replicas = len(order) // 9
    win = windows(template, order, replicas)
    parsed = _provider_data(dispatch, order, providers)
    families = _physical_families(plan, {child for _, child in win})
    masks, patterns = _roles(order, fill, dispatch, win, families, parsed)
    profile, idle, histogram = _invoice(win, masks, patterns, order, dispatch, parsed)
    rank_mass = sum(rank * count for rank, count in profile.items())
    need(rank_mass == 65088 * replicas, "complete rank-mass identity")
    return {
        "replicas": replicas,
        "calls": len(order),
        "roles": len(fill["rows"]),
        "live": 896 * replicas,
        "physical": 896 * replicas + HELPERS + 8 + buffers + 2,
        "private_buffers": buffers,
        "rank_mass": rank_mass,
        "idle": dict(sorted(idle.items())),
        "profile": dict(sorted(profile.items())),
        "bin_pattern_histogram": histogram,
    }
