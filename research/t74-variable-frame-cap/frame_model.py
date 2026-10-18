"""Literal role/frame graph, with variable scalar and handoff frames.
Frame-invoice model follows PR2322 paid_profile. No producer is imported.
"""

import collections
from functools import lru_cache


def need(ok, message):
    if not ok:
        raise ValueError(message)


def incident(g):
    need(g[0] in ("add", "scale"), "unsupported scalar gate")
    return g[1:3] if g[0] == "add" else g[1:2]


FULL = (1 << 512) - 1


@lru_cache(None)
def mask(bs):
    s = [0]
    for x in bs:
        if x not in s:
            s += [y ^ x for y in s]
    return sum(1 << x for x in s)


@lru_cache(None)
def basis(m):
    out = []
    space = 1
    for x in range(1, 512):
        if (m >> x) & 1 and not ((space >> x) & 1):
            out.append(x)
            space = mask(tuple(out))
    return tuple(out)


@lru_cache(None)
def join(a, b):
    if a & b == a:
        return b
    if a & b == b:
        return a
    return mask(basis(a) + basis(b))


def rank(m):
    return m.bit_count().bit_length() - 1


def model(w):
    frames = []
    locations = []
    edges = []
    transports = {}
    last = {}
    live = set(range(704)) - set(w["removed"])

    def new(F, loc=None):
        i = len(frames)
        frames.append(F)
        locations.append(loc)
        return i

    def touch(r, node):
        if r in last:
            edges.append((last[r], node))
        last[r] = node

    for r in sorted(live):
        bs = [w["ports"][r]] if r < 112 else w["start_extra"].get(str(r), [])
        touch(r, new(mask(tuple(bs))))

    def gate(sec, i):
        g = w[sec][i]
        node = new(mask(tuple(g[-1])), (sec, i))
        for r in incident(g):
            touch(r, node)

    for i in range(len(w["A"])):
        gate("A", i)
    for r, fr in zip(w["centers"], w["center_frames"]):
        touch(r, new(mask(tuple(fr))))
    for r in range(112, 224):
        touch(r, new(mask(tuple(w["target_levels"].get(str(r - 112), [])))))
    warps = collections.defaultdict(list)
    for op, rec in enumerate(w["warps"]):
        warps[rec[0]].append((op, rec))
    for i in range(len(w["B"]) + 1):
        for op, (_, r, G, U, V) in warps[i]:
            before = new(mask(tuple(U)), ("warp_old", op))
            touch(r, before)
            after = new(mask(tuple(V)), ("warp_new", op))
            last[r] = after
            transports[before, after] = tuple(G)
        if i < len(w["B"]):
            gate("B", i)
    for i in range(len(w["restore"])):
        gate("restore", i)
    for r in sorted(live):
        F = FULL
        if 112 <= r < 224:
            F = sum(
                1 << x
                for x in range(512)
                if (x & w["ports"][r - 112]).bit_count() % 2 == 0
            )
        elif str(r) in w["helper_final"]:
            F = mask(tuple(w["helper_final"][str(r)]))
        touch(r, new(F))
    preds = collections.defaultdict(list)
    succs = collections.defaultdict(list)
    for a, b in edges:
        if frames[a] & frames[b] != frames[a]:
            raise ValueError(("invalid initial edge", locations[a], locations[b]))
        preds[b].append(a)
        succs[a].append(b)
    fixed = collections.Counter()
    lev = {int(t): mask(tuple(fr)) for t, fr in w["target_levels"].items()}
    for r, fr in zip(w["centers"], w["center_frames"]):
        f = mask(tuple(fr))
        readers = {lev.get(g[1] - 112, 1) for g in w["cut"] if g[2] == r}
        for t in sorted(readers, key=lambda t: -rank(t)):
            if f != t:
                fixed[rank(f) - rank(t)] += 1
            f = t

    def profile(fs):
        p = fixed.copy()
        for a, b in edges:
            d = rank(fs[b]) - rank(fs[a])
            if d:
                p[d] += 1
        return dict(sorted(p.items()))

    need(
        profile(frames) == {int(k): v for k, v in w["report"]["local_profile"].items()},
        "source invoice mismatch",
    )
    return frames, locations, preds, succs, profile, transports
