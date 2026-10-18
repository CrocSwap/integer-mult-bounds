# SPDX-License-Identifier: Apache-2.0
"""Finite frame accountant, using explicit subsets of the nine-bit space.

The frame/centre tariff conventions are those of Kothe's retained supplier.
No predecessor Python implementation is imported or executed.
"""

from collections import Counter
from copy import deepcopy
from functools import lru_cache

HELPERS = (249, 251, 265, 267)
W = (256, 128, 64, 35, 16, 11, 5)
FULL = frozenset(range(512))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def span(generators):
    require(len(generators) <= 9, "at most nine frame generators")
    require(
        all(type(v) is int and 0 <= v < 512 for v in generators),
        "nine-bit frame generator",
    )
    return cached_span(generators)


@lru_cache(maxsize=4096)
def cached_span(generators):
    points = {0}
    for v in generators:
        points |= {x ^ v for x in points}
    return frozenset(points)


def dimension(space):
    return len(space).bit_length() - 1


def recount(word):
    require(
        word["report"]["v"] == 112 and word["report"]["R"] == 480, "fixed word size"
    )
    start = [span((p,)) for p in word["ports"]] + [span(())] * 592
    end = [FULL] * 112
    end += [
        frozenset(x for x in range(512) if (x & p).bit_count() % 2 == 0)
        for p in word["ports"]
    ] + [FULL] * 480
    for role, frame in word["start_extra"].items():
        start[int(role)] = span(tuple(frame))
    for role, frame in word["helper_final"].items():
        end[int(role)] = span(tuple(frame))
    current, paid = list(start), Counter()

    def climb(role, frame):
        require(0 <= role < 704 and current[role] <= frame, "monotone frame climb")
        rank = dimension(frame) - dimension(current[role])
        if rank:
            paid[rank] += 1
        current[role] = frame

    def step(gate):
        if gate[0] == "warp":
            old, new = span(tuple(gate[-2])), span(tuple(gate[-1]))
            require(
                current[gate[1]] == old and len(old) == len(new), "warp frame boundary"
            )
            current[gate[1]] = new
        else:
            require(gate[0] in ("add", "scale"), "known scalar operation")
            for role in gate[1:3] if gate[0] == "add" else gate[1:2]:
                climb(role, span(tuple(gate[-1])))

    for section in ("A", "B", "restore"):
        require(len(word[section]) <= 10000, "bounded word section")
    for gate in word["A"]:
        step(gate)
    centre_costs(word, current, paid)
    warps = {}
    require(len(word["warps"]) <= 480, "bounded warp list")
    for position, role, _matrix, old, new in word["warps"]:
        require(0 <= position <= len(word["B"]), "warp position")
        warps.setdefault(position, []).append(["warp", role, old, new])
    for position in range(len(word["B"]) + 1):
        for gate in warps.get(position, ()):
            step(gate)
        if position < len(word["B"]):
            step(word["B"][position])
    for gate in word["restore"]:
        step(gate)
    live = sorted(set(range(704)) - set(word["removed"]))
    for role in live:
        climb(role, end[role])
    widths = [dimension(end[r]) - dimension(start[r]) for r in live if r >= 224]
    require(len(widths) == 408 and min(widths) > 0, "408 positive helper widths")
    return paid, widths


def centre_costs(word, current, paid):
    require(len(word["centers"]) == len(word["center_frames"]) == 8, "eight centres")
    require(len(word["cut"]) <= 10000, "bounded centre readout")
    for role, frame in zip(word["centers"], word["center_frames"], strict=True):
        previous = span(tuple(frame))
        require(current[role] == previous, "centre entrance frame")
        levels = {
            span(tuple(word["target_levels"].get(str(g[1] - 112), [])))
            for g in word["cut"]
            if g[2] == role
        }
        for level in sorted(levels, key=lambda s: (-len(s), tuple(sorted(s)))):
            require(level <= previous, "nested centre readout")
            rank = dimension(previous) - dimension(level)
            if rank:
                paid[rank] += 1
            previous = level


def v45_word(parent, record, subset):
    require(set(subset) <= set(HELPERS), "V45 endpoint subset")
    require(record["groups"]["V45"] == [list(W), list(HELPERS)], "V45 source group")
    require(len(record["frame_edits"]) == 139, "source edit inventory")
    result, edits = deepcopy(parent), 0
    for edit in record["frame_edits"]:
        new = span(tuple(edit["new_frame"]))
        containing = [
            name
            for name, (frame, _) in record["groups"].items()
            if new <= span(tuple(frame))
        ]
        require(len(containing) == 1, "unique edit group")
        if containing[0] != "V45":
            continue
        section, index = edit["section"], edit["index"]
        require(
            section in ("B", "restore") and 0 <= index < len(result[section]),
            "edit position",
        )
        gate = result[section][index]
        require(
            gate[:-1] == edit["gate"] and gate[-1] == edit["old_frame"], "edit preimage"
        )
        old = span(tuple(gate[-1]))
        require(new < old and len(old) == 2 * len(new), "codimension-one gate edit")
        gate[-1] = list(edit["new_frame"])
        edits += 1
    require(edits == 61, "61 V45 partner edits")
    for role in subset:
        old = span(tuple(parent["helper_final"][str(role)]))
        require(span(W) < old and len(old) == 256, "rank-eight old endpoint")
        result["helper_final"][str(role)] = list(W)
    require(result["cleanup"] == parent["cleanup"], "unchanged cleanup syntax")
    return result
