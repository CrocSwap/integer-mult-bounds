"""Repeat-aware matching balance. Produced by Nick Petalas. Apache-2.0.

The written theorem has no dimension or length cap; these caps bound replay.
"""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def color(vertex: int, omitted: int) -> int:
    return (vertex & ~(1 << omitted)).bit_count() & 1


def support_data(n: int, omitted: int, support: frozenset[int]) -> dict:
    require(type(n) is int and 2 <= n <= 17, "dimension outside 2..17")
    require(type(omitted) is int and 0 <= omitted < n, "invalid omission")
    require(isinstance(support, frozenset), "support must be a frozenset")
    require(2 <= len(support) <= 64, "support size outside 2..64")
    require(all(type(x) is int and 0 <= x < 1 << n for x in support),
            "vertex outside cube")
    projected = {x & ~(1 << omitted) for x in support}
    require(len(projected) >= 2, "support lies in one matching component")
    sizes = tuple(sum(color(x, omitted) == j for x in support) for j in (0, 1))
    pairs = tuple(sum(color(x, omitted) == j and x ^ (1 << omitted) in support
                      for x in support) // 2 for j in (0, 1))
    components = tuple(sizes[j] - pairs[j] for j in (0, 1))
    debt = (max(0, components[1] - sizes[0]),
            max(0, components[0] - sizes[1]))
    return {"sizes": sizes, "pairs": pairs, "components": components,
            "debt": debt}


def prefix_budget(n: int, omitted: int, support: frozenset[int],
                  length: int, prefix: tuple[int, ...]) -> dict:
    """Necessary budgets for completions with exactly this visited support.

    Prefix positions exclude the final closing occurrence. Repeats are allowed.
    Passing this check does not promise a completion.
    """
    data = support_data(n, omitted, support)
    require(type(length) is int and 4 <= length <= 64 and length % 2 == 0,
            "length must be even in 4..64")
    require(len(support) <= length, "more distinct vertices than positions")
    require(isinstance(prefix, tuple) and 1 <= len(prefix) <= length,
            "invalid prefix size")
    require(all(type(x) is int and x in support for x in prefix),
            "prefix outside prescribed support")
    require(all((x ^ y).bit_count() == 1 for x, y in zip(prefix, prefix[1:])),
            "prefix contains a nonedge")
    counts = tuple(sum(color(x, omitted) == j for x in prefix) for j in (0, 1))
    unique = frozenset(prefix)
    seen = tuple(sum(color(x, omitted) == j for x in unique) for j in (0, 1))
    used = tuple(counts[j] - seen[j] for j in (0, 1))
    lower = tuple(max(used[j], data["debt"][j]) for j in (0, 1))
    total = length - len(support)
    interval = (lower[0], total - lower[1])
    return {**data, "used": used, "lower": lower, "total": total,
            "repeat_zero_interval": interval, "possible": interval[0] <= interval[1]}


def book_walk(pages: int) -> tuple[int, ...]:
    require(type(pages) is int and 1 <= pages <= 16, "pages outside 1..16")
    walk = [0]
    for i in range(pages):
        leaf = 1 << (i + 1)
        walk.extend((leaf, leaf | 1, 1) if i % 2 == 0 else (leaf | 1, leaf, 0))
    if walk[-1] != 0:
        walk.append(0)
    return tuple(walk)
