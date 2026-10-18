# SPDX-License-Identifier: Apache-2.0
"""The complete fixed-warp A/B/restore frame constraint graph."""

from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import pairwise

from spaces import FULL, ZERO, join, operands, rank, require, span


@dataclass
class Graph:
    labels: list
    frames: list
    edges: list
    fixed_profile: Counter
    widths: Counter


def endpoints(word):
    ports = word["ports"]
    require(len(ports) == len(set(ports)) == 112, "112 distinct ports")
    start = [span([p]) for p in ports] + [ZERO] * 592
    final = [FULL] * 112 + [frozenset(x for x in range(512)
        if (x & p).bit_count() % 2 == 0) for p in ports] + [FULL] * 480
    for r, vectors in word["start_extra"].items():
        require(224 <= int(r) < 704, "helper entrance")
        start[int(r)] = span(vectors)
    for r, vectors in word["helper_final"].items():
        require(224 <= int(r) < 704, "private helper endpoint")
        final[int(r)] = span(vectors)
    return start, final


def chronology(word):
    """Anchors are exact frame constraints; warps separate charged segments."""
    require(len(word["A"]) <= 5000 and len(word["B"]) <= 2500
            and len(word["restore"]) <= 250, "bounded scalar sections")
    require(len(word["centers"]) == len(word["center_frames"]) == 8, "eight centres")
    require(len(word["warps"]) <= 100, "bounded B warps")
    events = []
    for index, gate in enumerate(word["A"]):
        events.append(("warp", gate[1], gate[3], gate[4]) if gate[0] == "warp"
                      else ("gate", "A", index, gate))
    for r, vectors in zip(word["centers"], word["center_frames"], strict=True):
        events.append(("anchor", r, vectors))
    warps = defaultdict(list)
    for position, r, _, before, after in word["warps"]:
        require(type(position) is int and 0 <= position <= len(word["B"]),
                "B warp position")
        warps[position].append(("warp", r, before, after))
    for index in range(len(word["B"]) + 1):
        events.extend(warps[index])
        if index < len(word["B"]):
            events.append(("gate", "B", index, word["B"][index]))
    events.extend(("gate", "restore", i, gate)
                  for i, gate in enumerate(word["restore"]))
    require(len(events) <= 8000, "bounded chronological events")
    return events


def centre_profile(word):
    require(len(word["cut"]) <= 224, "centre-cut bound")
    paid = Counter()
    for r, vectors in zip(word["centers"], word["center_frames"], strict=True):
        previous = span(vectors)
        levels = {span(word["target_levels"].get(str(g[1] - 112), []))
                  for g in word["cut"] if g[2] == r}
        for level in sorted(levels, key=lambda f: (-rank(f), tuple(sorted(f)))):
            require(level <= previous, "descending centre levels")
            if level != previous:
                paid[rank(previous) - rank(level)] += 1
            previous = level
    return paid


def build(word):
    start, final = endpoints(word)
    current = [[(-1, frame)] for frame in start]
    actual = start.copy()
    labels, frames, segments = [], [], []
    for event in chronology(word):
        if event[0] == "gate":
            _, section, position, gate = event
            index, frame = len(frames), span(gate[-1])
            labels.append((section, position))
            frames.append(frame)
            for r in operands(gate):
                require(actual[r] <= frame, "source monotone frame chain")
                current[r].append((index, frame))
                actual[r] = frame
        else:
            _, r, vectors, *after = event
            require(type(r) is int and 0 <= r < 704, "anchor register")
            frame = span(vectors)
            require(actual[r] <= frame, "source fits fixed anchor")
            current[r].append((-1, frame))
            segments.append((r, current[r]))
            actual[r] = span(after[0]) if after else frame
            current[r] = [(-1, actual[r])]
    removed = set(word["removed"])
    require(len(removed) == 72 and all(224 <= r < 704 for r in removed),
            "72 removed helpers")
    for r in range(704):
        if r in removed:
            require(current[r] == [(-1, start[r])] and actual[r] == start[r],
                    "removed helpers have no events")
        else:
            require(actual[r] <= final[r], "source terminal frame")
            current[r].append((-1, final[r]))
            segments.append((r, current[r]))
    edges = [(r, a, fa, b, fb) for r, events in segments
             for (a, fa), (b, fb) in pairwise(events)]
    require(len(frames) <= 7500 and len(edges) <= 15000, "graph capacity")
    widths = Counter(rank(final[r]) - rank(start[r]) for r in range(224, 704)
                     if r not in removed)
    return Graph(labels, frames, edges, centre_profile(word), widths)


def bounds(graph):
    incoming, outgoing = defaultdict(list), defaultdict(list)
    for _, a, fa, b, fb in graph.edges:
        require(a < b or b == -1, "chronological constraint edge")
        incoming[b].append((a, fa))
        outgoing[a].append((b, fb))
    lower, upper = [], [FULL] * len(graph.frames)
    for i in range(len(graph.frames)):
        frame = ZERO
        for a, before in incoming[i]:
            frame = join(frame, lower[a] if a >= 0 else before)
        lower.append(frame)
    for i in reversed(range(len(graph.frames))):
        for b, after in outgoing[i]:
            upper[i] &= upper[b] if b >= 0 else after
        require(lower[i] <= graph.frames[i] <= upper[i], "source in propagated bounds")
    return lower, upper


def profile(edges, assignment):
    paid = Counter()
    for _, a, before, b, after in edges:
        before, after = assignment.get(a, before), assignment.get(b, after)
        require(before <= after, "feasible frame assignment")
        difference = rank(after) - rank(before)
        paid[difference] += 1
    return tuple(paid[r] for r in range(10))


def components(graph, lower, upper):
    variable = {i for i in range(len(lower)) if lower[i] != upper[i]}
    neighbours = {i: set() for i in variable}
    for _, a, _, b, _ in graph.edges:
        if a in variable and b in variable:
            neighbours[a].add(b)
            neighbours[b].add(a)
    result, seen = [], set()
    for root in sorted(variable):
        if root in seen:
            continue
        pending, component = [root], {root}
        seen.add(root)
        for _ in range(len(variable)):
            if not pending:
                break
            for neighbour in sorted(neighbours[pending.pop()]):
                if neighbour not in seen:
                    seen.add(neighbour)
                    component.add(neighbour)
                    pending.append(neighbour)
        require(not pending, "bounded component traversal")
        result.append(tuple(sorted(component)))
    return result
