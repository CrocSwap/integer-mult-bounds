# SPDX-License-Identifier: Apache-2.0
"""Recount the fixed nine-axis frame contract using binary elimination.

No predecessor evaluator, frame accountant or owner checker is imported.
Frame tariffs and centre descent conventions are inherited, not redefined here.
"""

from collections import Counter
from functools import lru_cache

V45 = (249, 251, 265, 267)
FULL = tuple(1 << i for i in range(8, -1, -1))


def need(value, message):
    if not value:
        raise ValueError(message)


def basis(vectors):
    need(len(vectors) <= 9, "nine-axis basis bound")
    need(all(type(v) is int and 0 < v < 512 for v in vectors),
         "nonzero nine-bit generator")
    return _basis_cached(vectors)


@lru_cache(maxsize=4096)
def _basis_cached(vectors):
    pivots = {}
    for v in vectors:
        for p in sorted(pivots, reverse=True):
            if v & (1 << p):
                v ^= pivots[p]
        need(v != 0, "independent frame generators")
        p = v.bit_length() - 1
        for q in pivots:
            if pivots[q] & (1 << p):
                pivots[q] ^= v
        pivots[p] = v
    return tuple(pivots[p] for p in sorted(pivots, reverse=True))


def contains(big, small):
    for v in small:
        for p in big:
            if v & (1 << (p.bit_length() - 1)):
                v ^= p
        if v:
            return False
    return True


def hyperplane(normal):
    need(type(normal) is int and 0 < normal < 512, "nonzero port")
    p = normal.bit_length() - 1
    return basis(tuple((1 << i) ^ (((normal >> i) & 1) << p)
                       for i in range(9) if i != p))


def recount(word, terminal_overrides=None):
    need(word["report"]["v"] == 112 and word["report"]["h"] == 9
         and word["report"]["R"] == 480, "fixed word dimensions")
    need(len(word["ports"]) == 112, "port inventory")
    removed = word["removed"]
    need(len(removed) == len(set(removed)) == 72
         and all(type(r) is int and 224 <= r < 704 for r in removed),
         "removed helper inventory")
    live = set(range(704)) - set(removed)
    start = [basis((q,)) for q in word["ports"]] + [()] * 592
    end = [FULL] * 112 + [hyperplane(q) for q in word["ports"]] + [FULL] * 480
    for r, b in word["start_extra"].items():
        need(int(r) in live, "live entrance")
        start[int(r)] = basis(tuple(b))
    for r, b in word["helper_final"].items():
        need(int(r) in live and int(r) >= 224, "live helper endpoint")
        end[int(r)] = basis(tuple(b))
    for r, b in (terminal_overrides or {}).items():
        need(r in V45, "bounded terminal override")
        end[r] = basis(tuple(b))
    frames, profile, v45_events = list(start), Counter(), []

    def move(r, target, location):
        need(type(r) is int and r in live, "live frame role")
        old = frames[r]
        need(contains(target, old), "monotone frame containment")
        rank = len(target) - len(old)
        if rank:
            profile[rank] += 1
            if r in V45:
                v45_events.append([r, location, list(old), list(target), rank])
        frames[r] = target

    def scalar(g, location):
        if g[0] == "warp":
            need(len(g) == 5 and g[1] in live, "inline warp shape")
            old, new = basis(tuple(g[-2])), basis(tuple(g[-1]))
            need(frames[g[1]] == old and len(old) == len(new), "inline warp frame")
            frames[g[1]] = new
            return
        need(g[0] in ("add", "scale"), "scalar gate kind")
        need(len(g) == (6 if g[0] == "add" else 5), "scalar gate arity")
        target = basis(tuple(g[-1]))
        for r in (g[1:3] if g[0] == "add" else g[1:2]):
            move(r, target, location)

    need(all(len(word[s]) <= 10000 for s in ("A", "B", "restore", "cut")),
         "bounded scalar sections")
    for i, g in enumerate(word["A"]):
        scalar(g, ["A", i])
    need(len(word["centers"]) == len(word["center_frames"]) == 8,
         "eight centre children")
    for r, b in zip(word["centers"], word["center_frames"], strict=True):
        previous = basis(tuple(b))
        need(frames[r] == previous, "centre frame at cut")
        levels = {basis(tuple(word["target_levels"].get(str(g[1] - 112), [])))
                  for g in word["cut"] if g[2] == r}
        for level in sorted(levels, key=lambda x: (-len(x), x)):
            need(contains(previous, level), "nested centre descent")
            if len(previous) > len(level):
                profile[len(previous) - len(level)] += 1
            previous = level
    warps = {}
    need(len(word["warps"]) <= 480, "warp count")
    for position, r, matrix, old, new in word["warps"]:
        need(type(position) is int and 0 <= position <= len(word["B"]),
             "warp position")
        need(len(basis(tuple(matrix))) == 9, "invertible warp matrix")
        before, after = basis(tuple(old)), basis(tuple(new))
        need(len(before) == len(after), "rank preserving warp")
        warps.setdefault(position, []).append((r, before, after))
    for i in range(len(word["B"]) + 1):
        for r, old, new in warps.get(i, []):
            need(r in live and frames[r] == old, "warp entrance frame")
            frames[r] = new
        if i < len(word["B"]):
            scalar(word["B"][i], ["B", i])
    for i, g in enumerate(word["restore"]):
        scalar(g, ["restore", i])
    for r in sorted(live):
        move(r, end[r], ["terminal", r])
    helpers = sorted(live - set(range(224)))
    widths = [len(end[r]) - len(start[r]) for r in helpers]
    need(len(helpers) == 408 and all(0 < n <= 9 for n in widths),
         "408 positive helper widths")
    private = {r for g in word["cleanup"]
               for r in (g[1:3] if g[0] == "add" else g[1:2]) if r >= 704}
    need(private == {704 + int(r) for r in word["helper_final"]},
         "private names match restored helpers")
    need(sum(r * n for r, n in profile.items()) - sum(widths) == 1856,
         "local rank mass minus helper width mass")
    return dict(profile=profile, helpers=helpers, widths=widths,
                private_names=sorted(private), v45_events=v45_events)
