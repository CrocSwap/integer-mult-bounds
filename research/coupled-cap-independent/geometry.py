# SPDX-License-Identifier: Apache-2.0
"""Time-major independent allocation replay with fixed-capacity occupancy arrays."""

from array import array
from collections import Counter

from arithmetic import WIDTHS, require

HELPERS = 408
PORTS = 112
CHILDREN = 18
BASE_T = 74
BASE_ROWS = 9 * BASE_T * HELPERS


def pending_types(template):
    """Find each idle interval's prior touch by scanning its event prefix backwards."""
    require(len(template["execution_schedule"]) <= 64, "bounded source schedule")
    require(len(template["idle_children"]) == CHILDREN * PORTS,
            "eighteen complete idle port declarations")
    ranks = {}
    for child in template["idle_children"]:
        c, rank = child["child"], child["rank"]
        require(c not in ranks or ranks[c] == rank, "consistent repeated idle rank")
        ranks[c] = rank
    pairs = {e["stage"]: e["pair"] for e in template["recipe"]
             if e["kind"] == "local"}
    history, result, stage = [], {}, None
    for event in template["execution_schedule"]:
        kind = event["kind"]
        if kind == "local_cover_sweep":
            stage = event["stage"]
            history.append((stage, (pairs[stage],)))
        elif kind == "bridge":
            history.append((stage, (event["src"], event["dst"])))
        elif kind == "idle_cover_sweep":
            previous = next((s for s, touched in reversed(history)
                             if event["pair"] in touched), None)
            for child in event["child_indices"]:
                if child in ranks:
                    require(child not in result, "unique pending interval")
                    result[child] = ranks[child], previous, stage
        else:
            require(kind in {"terminal_Y_translations", "terminal",
                             "bank_padding_cover_sweep", "translate_every_live_family"},
                    "known source event")
    require(set(result) == set(range(CHILDREN)), "all eighteen pending intervals")
    return result


def chronology(base_order, base_dispatch, copies):
    require(copies in (1, 10), "bounded copy count")
    require(len(base_order) == len(base_dispatch) == 9 * BASE_T, "base call coverage")
    dispatch = {(s, r): p for s, r, p in base_dispatch}
    require(len(dispatch) == len(base_dispatch), "unique base dispatch")
    order, providers = [], []
    for stage, replica in base_order:
        for copy in range(copies):
            order.append((stage, replica + BASE_T * copy))
            providers.append(dispatch[stage, replica])
    times = [[None] * 9 for _ in range(BASE_T * copies)]
    for time, (stage, replica) in enumerate(order):
        require(0 <= stage < 9 and 0 <= replica < len(times), "call bounds")
        require(times[replica][stage] is None, "unique lifted call")
        times[replica][stage] = time
    require(all(all(t is not None for t in row) and row == sorted(row)
                for row in times), "complete increasing replica progression")
    return times, providers


def source_windows(types, times):
    return [[(capacity, -1 if before is None else row[before], row[after])
             for _, (capacity, before, after) in sorted(types.items())]
            for row in times]


def journal_edits(base, journal):
    require(journal["copies"] == 10 and len(journal["edits"]) == 145,
            "complete ten-copy journal")
    result = {}
    for index, before, after in journal["edits"]:
        require(type(index) is int and 0 <= index < 10 * BASE_ROWS,
                "journal index domain")
        require(index not in result, "unique journal edit")
        copy, original = divmod(index, BASE_ROWS)
        t, h, owner, child, port, offset = base[original]
        expected = [10 * t + copy, h, owner + BASE_T * copy, child, port, offset]
        require(before == expected, "literal journal preimage")
        require(len(after) == 6 and all(type(v) is int for v in after),
                "integer replacement row")
        require(after[:2] == before[:2], "fixed call/helper identity")
        result[index] = after
    return result


def place(row, width, time, windows, families, occupied, signatures, same_call):
    require(len(row) == 6 and all(type(v) is int for v in row), "integer role row")
    t, helper, owner, child, port, offset = row
    require(t == time and 0 <= helper < HELPERS, "role identity")
    require(0 <= owner < len(windows) and 0 <= child < CHILDREN and
            0 <= port < PORTS, "owner/child/port bounds")
    capacity, lower, upper = windows[owner][child]
    require(lower < time <= upper, "chronological source availability")
    family = (owner * 8 + families[child]) * PORTS + port
    require(family not in same_call, "same-call physical-family exclusion")
    same_call.add(family)
    require(width in WIDTHS and 0 <= offset <= capacity - width, "role capacity")
    index = (owner * CHILDREN + child) * PORTS + port
    mask = ((1 << width) - 1) << offset
    require(not occupied[index] & mask, "disjoint bin intervals")
    occupied[index] |= mask
    signatures[index] += 1 << (4 * WIDTHS.index(width))


def summarize(windows, occupied, signatures):
    idle, patterns = Counter(), Counter()
    for owner, children in enumerate(windows):
        for child, (capacity, _, _) in enumerate(children):
            for port in range(PORTS):
                index = (owner * CHILDREN + child) * PORTS + port
                mask = occupied[index]
                used = mask.bit_count()
                require(mask == (1 << used) - 1, "compact paid prefix")
                if used < capacity:
                    idle[capacity - used] += 1
                patterns[capacity, signatures[index]] += 1
    decoded = {}
    for (capacity, signature), count in patterns.items():
        counts = tuple((signature >> (4 * i)) & 15 for i in range(len(WIDTHS)))
        decoded[capacity, counts] = count
    return idle, decoded


def audit(base, base_order, dispatch, providers, plan, template, copies, edits):
    require(len(base) == BASE_ROWS, "complete base roles")
    times, provider_ids = chronology(base_order, dispatch, copies)
    windows = source_windows(pending_types(template), times)
    bins = copies * BASE_T * CHILDREN * PORTS
    occupied = array("Q", [0]) * bins
    signatures = array("I", [0]) * bins
    families = {c: 2 * plan["pairs"][str(c)] + plan["sides"][str(c)]
                for c in range(CHILDREN)}
    require(set(families.values()) == set(range(8)), "eight physical families")
    for original_time in range(9 * BASE_T):
        for copy in range(copies):
            time = copies * original_time + copy
            same_call = set()
            widths = providers[provider_ids[time]]["widths"]
            require(len(widths) == HELPERS, "ordered width count")
            for helper in range(HELPERS):
                original = original_time * HELPERS + helper
                row = base[original]
                require(row[:2] == [original_time, helper], "base role order")
                index = copy * BASE_ROWS + original
                lifted = [time, helper, row[2] + BASE_T * copy, *row[3:]]
                candidate = edits.get(index, lifted)
                require(candidate[:2] == [time, helper], "complete helper identities")
                place(candidate, widths[helper], time, windows, families,
                      occupied, signatures, same_call)
    idle, patterns = summarize(windows, occupied, signatures)
    return idle, patterns
