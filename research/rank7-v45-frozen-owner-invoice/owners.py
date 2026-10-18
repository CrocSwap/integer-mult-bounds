# SPDX-License-Identifier: Apache-2.0
"""Source-window and full-bin invoice checks for one frozen assignment.

The source event conventions follow the retained Tekalign/PR2839 owner model.
Within-bin compaction is granted for free, a favorable geometric relaxation.
"""

from collections import Counter, defaultdict

from frames import require


def source_windows(template, order):
    require(
        len(order) == 666 and len(template["execution_schedule"]) <= 64,
        "T74 schedule size",
    )
    require(len(template["idle_children"]) <= 2016, "bounded idle inventory")
    ranks = {}
    for child in template["idle_children"]:
        key, rank = child["child"], child["rank"]
        require(key not in ranks or ranks[key] == rank, "consistent child capacities")
        ranks[key] = rank
    pairs = {e["stage"]: e["pair"] for e in template["recipe"] if e["kind"] == "local"}
    blocks, active = {}, None
    for event in template["execution_schedule"]:
        kind = event["kind"]
        if kind in ("bank_padding_cover_sweep", "translate_every_live_family"):
            continue
        if kind == "local_cover_sweep":
            active = event["stage"]
            require(active not in blocks, "unique source stage")
            blocks[active] = []
        require(active is not None, "source begins with a local call")
        blocks[active].append(event)
    require(set(blocks) == set(pairs) == set(range(9)), "nine source stages")
    progress, last_touch, windows = [0] * 74, {}, {}
    for time, call in enumerate(order):
        require(
            len(call) == 2 and all(type(v) is int for v in call), "integer call shape"
        )
        stage, replica = call
        require(
            0 <= replica < 74 and stage == progress[replica], "per-replica chronology"
        )
        progress[replica] += 1
        for event in blocks[stage]:
            kind = event["kind"]
            if kind == "local_cover_sweep":
                last_touch[replica, pairs[stage]] = time
            elif kind == "bridge":
                for pair in (event["src"], event["dst"]):
                    last_touch[replica, pair] = time
            elif kind == "idle_cover_sweep":
                require(len(event["child_indices"]) <= 18, "bounded idle event")
                for child in event["child_indices"]:
                    if child in ranks:
                        require((replica, child) not in windows, "unique idle window")
                        windows[replica, child] = (
                            ranks[child],
                            last_touch.get((replica, event["pair"]), -1),
                            time,
                        )
            else:
                require(
                    kind in ("terminal_Y_translations", "terminal"),
                    "known source event",
                )
    require(progress == [9] * 74 and len(windows) == 74 * 18, "complete source windows")
    return windows


def check_fill(fill, order, dispatch, plan, windows, widths):
    require(
        fill["columns"]
        == ["time", "helper", "owner_replica", "child", "port", "offset"],
        "role columns",
    )
    require(len(fill["rows"]) == 666 * 408, "complete role count")
    require(
        len(dispatch) == 666 and set(dispatch) == set(map(tuple, order)),
        "dispatch coverage",
    )
    for stage, replica, provider in fill.get("dispatch_overrides", ()):
        require(dispatch[stage, replica] == provider, "dispatch override")
    seen, families, bins = set(), set(), defaultdict(list)
    for row in fill["rows"]:
        require(len(row) == 6 and all(type(v) is int for v in row), "integer role row")
        time, helper, owner, child, port, offset = row
        require(
            0 <= time < 666 and 0 <= helper < 408 and 0 <= port < 112, "role bounds"
        )
        require((time, helper) not in seen, "unique call/helper role")
        seen.add((time, helper))
        require((owner, child) in windows, "known owner window")
        capacity, begin, finish = windows[owner, child]
        require(begin < time <= finish, "source availability window")
        family = (
            time,
            owner,
            2 * plan["pairs"][str(child)] + plan["sides"][str(child)],
            port,
        )
        require(family not in families, "distinct physical families per call")
        families.add(family)
        provider = dispatch[tuple(order[time])]
        require(
            provider in widths and len(widths[provider]) == 408, "bound provider widths"
        )
        width = widths[provider][helper]
        require(0 <= offset and offset + width <= capacity, "bin capacity")
        bins[owner, child, port].append((offset, time, helper, width))
    require(len(seen) == 666 * 408, "every helper at every call")
    for rows in bins.values():
        cursor = 0
        for offset, _time, _helper, width in sorted(rows):
            require(offset == cursor, "nonoverlapping compact source prefix")
            cursor += width
    return bins


def idle_invoice(bins, windows, lowered):
    """Every one of the 149,184 bins is billed, including empty bins."""
    require(set(lowered) <= {25, 27, 41, 43}, "four V45 helper indices")
    idle, touched, journal = Counter(), Counter(), []
    for (owner, child), (capacity, _begin, _finish) in sorted(windows.items()):
        for port in range(112):
            key = (owner, child, port)
            rows = sorted(bins.get(key, ()))
            used = sum(row[3] for row in rows)
            freed = sum(row[2] in lowered for row in rows)
            require(0 <= used <= capacity, "source capacity")
            cursor = 0
            for _offset, time, helper, width in rows:
                new_width = width - (helper in lowered)
                require(
                    new_width > 0 and cursor + new_width <= capacity,
                    "compacted capacity",
                )
                if freed:
                    journal.append([time, helper, owner, child, port, cursor])
                cursor += new_width
            require(cursor == used - freed, "compaction conserves used width")
            if cursor < capacity:
                idle[capacity - cursor] += 1
            if freed:
                touched[capacity - used, freed] += 1
    require(
        sum(n * freed for (_old, freed), n in touched.items()) == 666 * len(lowered),
        "every freed unit charged",
    )
    return idle, touched, journal


def complete_profile(idle, local, dispatch):
    profile = Counter(idle)
    counts = Counter(dispatch.values())
    require(set(counts) == set(local), "all local profiles dispatched")
    for provider, number in counts.items():
        for rank, count in local[provider].items():
            profile[rank] += number * count
    require(sum(r * n for r, n in profile.items()) == 65088 * 74, "complete rank mass")
    return profile


def strict_cost_increase(delta):
    """Certify sum delta[r]*r**(1-a)>0 for every a>0, by equal rank mass."""
    require(
        delta
        and all(type(r) is int and type(n) is int and r > 0 for r, n in delta.items()),
        "integer histogram delta",
    )
    negative = [r for r, n in delta.items() if n < 0]
    require(len(negative) == 1, "one negative rank")
    top = negative[0]
    require(
        all(0 < r < top for r, n in delta.items() if n > 0),
        "all positive ranks below negative rank",
    )
    require(sum(r * n for r, n in delta.items()) == 0, "equal signed rank mass")
    return {
        "negative_rank": top,
        "positive_rank_mass": -top * delta[top],
        "saving_domain": "a > 0",
    }
