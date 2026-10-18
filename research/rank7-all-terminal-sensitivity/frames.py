# SPDX-License-Identifier: Apache-2.0
"""Literal nine-dimensional frame accounting, with no producer imports."""

from collections import Counter


def require(condition, message):
    if not condition:
        raise ValueError(message)


def basis(vectors):
    require(len(vectors) <= 512, "bounded frame")
    pivots = [0] * 9
    for value in vectors:
        require(type(value) is int and 0 <= value < 512, "frame vector domain")
        for bit in range(8, -1, -1):
            if value & (1 << bit):
                if pivots[bit]:
                    value ^= pivots[bit]
                else:
                    pivots[bit] = value
                    break
    for bit in range(9):
        for higher in range(bit + 1, 9):
            if pivots[higher] & (1 << bit):
                pivots[higher] ^= pivots[bit]
    return tuple(v for v in reversed(pivots) if v)


def contains(outer, inner):
    return basis(outer + inner) == outer


def endpoints(word):
    report = word["report"]
    require((report["h"], report["v"], report["R"]) == (9, 112, 480),
            "literal word dimensions")
    full = basis([1 << bit for bit in range(9)])
    start = [(p,) for p in word["ports"]] + [()] * 592
    end = [full] * 112 + [
        basis([v for v in range(1, 512) if not (v & p).bit_count() % 2])
        for p in word["ports"]
    ] + [full] * 480
    require(len(start) == len(end) == 704, "complete register domain")
    for key, frame in word["start_extra"].items():
        require(0 <= int(key) < 704, "entrance register")
        start[int(key)] = basis(frame)
    for key, frame in word["helper_final"].items():
        require(224 <= int(key) < 704, "terminal helper")
        end[int(key)] = basis(frame)
    return start, end


def climb(current, register, frame, paid):
    require(0 <= register < 704, "gate register")
    target = basis(frame)
    require(contains(target, current[register]), "nonmonotone frame")
    difference = len(target) - len(current[register])
    if difference:
        paid[difference] += 1
    current[register] = target


def scalar(current, gate, paid):
    require(gate[0] in ("add", "scale"), "scalar operation")
    for register in gate[1:3] if gate[0] == "add" else gate[1:2]:
        climb(current, register, gate[-1], paid)


def warp(current, register, before, after):
    require(0 <= register < 704, "warp register")
    require(current[register] == basis(before), "warp entrance")
    current[register] = basis(after)


def prefix(word, start):
    """Return every register's frame immediately before terminal completion."""
    current, paid = list(start), Counter()
    for section in ("A", "B", "restore", "cut", "warps"):
        require(len(word[section]) <= 6000, "bounded literal section")
    for gate in word["A"]:
        if gate[0] == "warp":
            warp(current, gate[1], gate[3], gate[4])
        else:
            scalar(current, gate, paid)
    require(len(word["centers"]) == len(word["center_frames"]) == 8,
            "eight centre paths")
    for register, frame in zip(word["centers"], word["center_frames"], strict=True):
        frame = basis(frame)
        require(current[register] == frame, "centre entrance")
        levels = {basis(word["target_levels"].get(str(g[1] - 112), []))
                  for g in word["cut"] if g[2] == register}
        for target in sorted(levels, key=lambda value: (-len(value), value)):
            require(contains(frame, target), "centre chain")
            if frame != target:
                paid[len(frame) - len(target)] += 1
            frame = target
    scheduled = {}
    for record in word["warps"]:
        require(0 <= record[0] <= len(word["B"]), "B warp position")
        scheduled.setdefault(record[0], []).append(record)
    for position in range(len(word["B"]) + 1):
        for record in scheduled.get(position, []):
            warp(current, record[1], record[3], record[4])
        if position < len(word["B"]):
            scalar(current, word["B"][position], paid)
    for gate in word["restore"]:
        scalar(current, gate, paid)
    return current, paid


def recount(word):
    start, end = endpoints(word)
    current, paid = prefix(word, start)
    before_terminal = tuple(current)
    removed = set(word["removed"])
    require(len(removed) == 72 and all(224 <= r < 704 for r in removed),
            "removed helper domain")
    live = sorted(set(range(704)) - removed)
    for register in live:
        climb(current, register, end[register], paid)
    widths = Counter(len(end[r]) - len(start[r]) for r in live if r >= 224)
    require(sum(widths.values()) == 408, "all live helpers charged")
    require(dict(paid) == {int(r): n for r, n in word["report"]["local_profile"].items()},
            "literal local profile")
    require(dict(widths) == {int(r): n for r, n in word["report"]["width_inventory"].items()},
            "literal entrance-relative widths")
    return start, end, before_terminal, paid, widths


def terminal_changes(word, record):
    start, end, current, paid, widths = recount(word)
    changes = record["helper_final_changes"]
    groups = record["groups"]
    helpers = [r for _, members in groups.values() for r in members]
    require(len(helpers) == len(set(helpers)) == len(changes) == 22,
            "all 22 distinct lowered helpers")
    require(set(helpers) == set(map(int, changes)), "group/change coverage")
    rows = []
    for group, (shared, members) in sorted(groups.items()):
        for register in members:
            change = changes[str(register)]
            old, new = basis(change["old"]), basis(change["new"])
            require(new == basis(shared) == end[register], "literal new endpoint")
            require(len(new) == 7 and len(old) == 8 and contains(old, new),
                    "one-dimensional terminal widening")
            require(current[register] == new, "no existing terminal child")
            require(contains(new, start[register]), "entrance inside endpoint")
            width = len(new) - len(start[register])
            require(width in (6, 7), "widening width class")
            rows.append({"helper": register, "group": group,
                         "width_before": width, "width_after": width + 1,
                         "entrance": list(start[register]), "new": list(new),
                         "old": list(old), "local_delta": {"1": 1}})
    return rows, paid, widths
