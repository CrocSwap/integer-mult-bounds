# SPDX-License-Identifier: Apache-2.0
"""Ten interleaved copies and a sparse, preimage-bound allocation journal."""

from collections import Counter, defaultdict

COPIES = 10
BASE_T = 74
HELPERS = 408
BASE_ROLES = 9 * BASE_T * HELPERS
MAX_EDITS = 2000


def need(condition, message):
    if not condition:
        raise ValueError(message)


def row_at(base, index):
    need(type(index) is int and 0 <= index < COPIES * BASE_ROLES, "lift row index")
    copy, original = divmod(index, BASE_ROLES)
    time, helper, owner, child, port, offset = base[original]
    return [COPIES * time + copy, helper, owner + BASE_T * copy, child, port, offset]


def patch(base, journal):
    need(len(base) == BASE_ROLES, "base role count")
    need(journal.get("copies") == COPIES, "journal lift multiplicity")
    edits = journal.get("edits")
    need(type(edits) is list and 0 < len(edits) <= MAX_EDITS, "journal size")
    result = {}
    for entry in edits:
        need(type(entry) is list and len(entry) == 3, "edit shape")
        index, before, after = entry
        need(type(index) is int, "journal integer index")
        need(index not in result, "duplicate journal index")
        need(before == row_at(base, index), "journal preimage")
        need(type(after) is list and len(after) == 6, "replacement row shape")
        need(all(type(x) is int for x in after), "replacement integers")
        need(after[:2] == before[:2], "fixed call/helper identity")
        result[index] = after
    return result


class Rows:
    """Bounded streaming literal witness, in copy-major source-row order."""

    def __init__(self, base, edits):
        need(len(base) == BASE_ROLES, "stream base count")
        self.base, self.edits = base, edits

    def __len__(self):
        return COPIES * BASE_ROLES

    def __iter__(self):
        for index in range(len(self)):
            yield self.edits[index] if index in self.edits else row_at(self.base, index)


def chronology(order, dispatch):
    need(len(order) == len(dispatch) == 9 * BASE_T, "base chronology size")
    lifted_order, lifted_dispatch = [], {}
    for stage, owner in order:
        for copy in range(COPIES):
            call = (stage, owner + BASE_T * copy)
            lifted_order.append(list(call))
            lifted_dispatch[call] = dispatch[stage, owner]
    return lifted_order, lifted_dispatch


def destination_window(key, windows):
    owner, child, port = key
    need(0 <= owner < COPIES * BASE_T and 0 <= port < 112, "destination bounds")
    copy, original = divmod(owner, BASE_T)
    need((original, child) in windows, "destination child")
    capacity, lower, upper = windows[original, child]
    lower = -1 if lower == -1 else COPIES * lower + copy
    return capacity, lower, COPIES * upper + copy


def bin_members(base, index, key, edits):
    copy, owner = divmod(key[0], BASE_T)
    members = {}
    for original in index.get((owner, key[1], key[2]), []):
        global_index = copy * BASE_ROLES + original
        if global_index not in edits:
            members[global_index] = row_at(base, global_index)
    for global_index, row in edits.items():
        if tuple(row[2:5]) == key:
            members[global_index] = row
    return members


def check_bin(key, members, widths, windows):
    capacity, lower, upper = destination_window(key, windows)
    mask, pattern = 0, []
    for row in members.values():
        time, helper, _, _, _, offset = row
        need(lower < time <= upper, "changed source window")
        width = widths[time // COPIES][helper]
        need(0 <= offset and offset + width <= capacity, "changed capacity")
        bits = ((1 << width) - 1) << offset
        need(mask & bits == 0, "changed bin overlap")
        mask |= bits
        pattern.append(width)
    used = mask.bit_count()
    need(mask == (1 << used) - 1, "changed compact prefix")
    return capacity - used, (capacity, tuple(sorted(pattern)))


def affected_calls(base, edits, families):
    times = {row[0] for row in edits.values()}
    need(len(times) <= MAX_EDITS, "affected call count")
    for time in times:
        original, copy = divmod(time, COPIES)
        occupied = set()
        for helper in range(HELPERS):
            index = copy * BASE_ROLES + original * HELPERS + helper
            row = edits[index] if index in edits else row_at(base, index)
            family = row[2], families[row[3]], row[4]
            need(family not in occupied, "changed same-call physical family")
            occupied.add(family)
    return len(times)


def differential(base, edits, widths, windows, families):
    index = defaultdict(list)
    for original, row in enumerate(base):
        need(row[:2] == [original // HELPERS, original % HELPERS], "base row ordering")
        index[tuple(row[2:5])].append(original)
    keys = {tuple(row_at(base, i)[2:5]) for i in edits}
    keys.update(tuple(row[2:5]) for row in edits.values())
    need(len(keys) <= 2 * MAX_EDITS, "affected bin count")
    delta, pattern_delta = Counter(), Counter()
    for key in sorted(keys):
        before = bin_members(base, index, key, {})
        after = bin_members(base, index, key, edits)
        old_idle, old_pattern = check_bin(key, before, widths, windows)
        new_idle, new_pattern = check_bin(key, after, widths, windows)
        if old_idle:
            delta[old_idle] -= 1
        if new_idle:
            delta[new_idle] += 1
        pattern_delta[old_pattern] -= 1
        pattern_delta[new_pattern] += 1
    return {
        "affected_bins": len(keys),
        "affected_calls": affected_calls(base, edits, families),
        "idle_delta": {rank: count for rank, count in sorted(delta.items()) if count},
        "pattern_delta": [
            [cap, list(ws), n] for (cap, ws), n in sorted(pattern_delta.items()) if n
        ],
    }
