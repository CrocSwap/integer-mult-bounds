# SPDX-License-Identifier: Apache-2.0
"""Independent finite-set recount of the literal nine-bit frame chronology."""

from collections import Counter
from functools import lru_cache

FULL = frozenset(range(512))
ZERO = frozenset({0})


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


@lru_cache(maxsize=4096)
def span(vectors):
    """Enumerate a subspace directly, without Gaussian elimination."""
    require(len(vectors) <= 9, "at most nine frame generators")
    points = {0}
    for vector in vectors:
        require(type(vector) is int and 0 <= vector < 512, "nine-bit vector")
        points |= {point ^ vector for point in points}
    require(len(points) == 1 << len(vectors), "frame generators are independent")
    return frozenset(points)


def dimension(points):
    size = len(points)
    require(size > 0 and size & (size - 1) == 0, "subspace cardinality")
    return size.bit_length() - 1


def registers(gate):
    require(gate[0] in ("add", "scale", "warp"), "known gate kind")
    return gate[1:3] if gate[0] == "add" else gate[1:2]


def climb(current, histories, register, destination, location):
    require(type(register) is int and 0 <= register < 704, "register range")
    previous = current[register]
    require(previous <= destination, f"nonmonotone frame at {location}: {register}")
    low, high = dimension(previous), dimension(destination)
    if low != high:
        histories[register].append([location, low, high])
    current[register] = destination


def step(gate, current, histories, location):
    if gate[0] == "warp":
        register = gate[1]
        require(current[register] == span(tuple(gate[3])), "A warp entrance")
        current[register] = span(tuple(gate[4]))
        return
    destination = span(tuple(gate[-1]))
    for register in registers(gate):
        climb(current, histories, register, destination, location)


def endpoints(word):
    require(word["report"]["h"] == 9 and word["report"]["v"] == 112, "dimensions")
    require(word["report"]["R"] == 480 and len(word["ports"]) == 112, "widths")
    start = [span((port,)) for port in word["ports"]] + [ZERO] * 592
    end = [FULL] * 112
    end += [frozenset(x for x in range(512) if (x & port).bit_count() % 2 == 0)
            for port in word["ports"]]
    end += [FULL] * 480
    for register, vectors in word["start_extra"].items():
        start[int(register)] = span(tuple(vectors))
    for register, vectors in word["helper_final"].items():
        end[int(register)] = span(tuple(vectors))
    return start, end


def cut_bill(word, current):
    paid = Counter()
    for register, vectors in zip(word["centers"], word["center_frames"], strict=True):
        previous = span(tuple(vectors))
        require(current[register] == previous, "center entrance")
        levels = {span(tuple(word["target_levels"].get(str(gate[1] - 112), [])))
                  for gate in word["cut"] if gate[2] == register}
        for level in sorted(levels, key=dimension, reverse=True):
            require(level <= previous, "nested cut levels")
            difference = dimension(previous) - dimension(level)
            if difference:
                paid[difference] += 1
            previous = level
    return paid


def trace(word):
    start, end = endpoints(word)
    current = start.copy()
    histories = [[] for _ in range(704)]
    for section in ("A", "B", "restore"):
        require(len(word[section]) <= 20000, "bounded gate list")
    for index, gate in enumerate(word["A"]):
        step(gate, current, histories, f"A/{index}")
    paid = cut_bill(word, current)
    warps = {}
    require(len(word["warps"]) <= 704, "bounded B warps")
    for record in word["warps"]:
        require(0 <= record[0] <= len(word["B"]), "B warp address")
        warps.setdefault(record[0], []).append(record)
    for index in range(len(word["B"]) + 1):
        for record in warps.get(index, []):
            register = record[1]
            require(current[register] == span(tuple(record[3])), "B warp entrance")
            current[register] = span(tuple(record[4]))
        if index < len(word["B"]):
            step(word["B"][index], current, histories, f"B/{index}")
    for index, gate in enumerate(word["restore"]):
        step(gate, current, histories, f"restore/{index}")
    live = sorted(set(range(704)) - set(word["removed"]))
    require(len(live) == 632, "632 live registers")
    for register in live:
        climb(current, histories, register, end[register], "endpoint")
    for history in histories:
        paid.update(high - low for _, low, high in history)
    helpers = [register for register in live if register >= 224]
    widths = [dimension(end[r]) - dimension(start[r]) for r in helpers]
    require(len(widths) == 408 and all(0 < width <= 9 for width in widths), "helpers")
    return {"profile": dict(sorted(paid.items())), "widths": widths,
            "histories": histories}
