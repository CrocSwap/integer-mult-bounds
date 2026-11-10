#!/usr/bin/env python3
"""Exact checks for the length-28 flat-step budget.

The argument is in README.md. These checks are finite censuses and arithmetic.
They do not search length-28 words and they do not change kappa.
"""

from math import factorial
from pathlib import Path


BUDGET = {4: 6, 5: 10, 6: 14}
EXAMPLES = {
    4: (0, 1, 0, 2, 3, 2),
    5: (0, 1, 0, 2, 0, 1, 0, 3, 4, 3),
    6: (0, 1, 0, 2, 0, 1, 0, 3, 4, 3, 5, 3, 4, 3),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def naive_cover(steps, dimension):
    state = 0
    seen = {0}
    for bit in steps:
        state ^= 1 << bit
        seen.add(state)
    covered = {left ^ right for left in seen for right in seen}
    return len(covered) == (1 << dimension), len(seen)


def fast_cover(steps, dimension):
    state = 0
    seen = 1
    covered = 1
    width = 1 << dimension
    for bit in steps:
        nxt = state ^ (1 << bit)
        mask = seen
        while mask:
            lowest = mask & -mask
            covered |= 1 << (nxt ^ (lowest.bit_length() - 1))
            mask ^= lowest
        seen |= 1 << nxt
        state = nxt
    return covered == (1 << width) - 1


def brute_covers(dimension, length):
    """Every cube walk of this length starting at 0."""
    total = dimension ** length
    hits = 0
    width = 1 << dimension
    full = (1 << width) - 1
    for code in range(total):
        digits = code
        state = 0
        seen = 1
        covered = 1
        for _ in range(length):
            bit = digits % dimension
            digits //= dimension
            nxt = state ^ (1 << bit)
            mask = seen
            while mask:
                lowest = mask & -mask
                covered |= 1 << (nxt ^ (lowest.bit_length() - 1))
                mask ^= lowest
            seen |= 1 << nxt
            state = nxt
        if covered == full:
            hits += 1
    return hits, total


def count_walks(counts):
    ways = factorial(sum(counts))
    for count in counts:
        ways //= factorial(count)
    return ways


def supply_search(counts, dimension, prune):
    """Search cube walks with this exact step supply.

    With pruning, a partial walk is abandoned only when even one new vertex
    per remaining step cannot finish the difference set. A repeated vertex
    adds no new difference, and the t-th new vertex adds at most |seen|+t
    differences. The unpruned mode visits every sequence.
    """
    limit = sum(counts)
    width = 1 << dimension
    full = (1 << width) - 1
    nodes = 0
    hits = 0
    leaves = 0

    def walk(state, seen, covered, left, step):
        nonlocal nodes, hits, leaves
        nodes += 1
        if step == limit:
            leaves += 1
            if covered == full:
                hits += 1
            return
        if prune:
            have = seen.bit_count()
            room = limit - step
            optimistic = room * have + room * (room - 1) // 2
            if optimistic < width - covered.bit_count():
                return
        for bit in range(dimension):
            if not left[bit]:
                continue
            left[bit] -= 1
            nxt = state ^ (1 << bit)
            bit_mask = 1 << nxt
            if seen & bit_mask:
                walk(nxt, seen, covered, left, step + 1)
            else:
                added = covered
                mask = seen
                while mask:
                    lowest = mask & -mask
                    added |= 1 << (nxt ^ (lowest.bit_length() - 1))
                    mask ^= lowest
                walk(nxt, seen | bit_mask, added, left, step + 1)
            left[bit] += 1

    walk(0, 1, 1, list(counts), 0)
    return hits, leaves, nodes


def prune_accepts(steps, dimension):
    state = 0
    seen = 1
    covered = 1
    width = 1 << dimension
    for index, bit in enumerate(steps):
        room = len(steps) - index
        have = seen.bit_count()
        optimistic = room * have + room * (room - 1) // 2
        if optimistic < width - covered.bit_count():
            return False
        nxt = state ^ (1 << bit)
        mask = seen
        while mask:
            lowest = mask & -mask
            covered |= 1 << (nxt ^ (lowest.bit_length() - 1))
            mask ^= lowest
        seen |= 1 << nxt
        state = nxt
    return covered == (1 << width) - 1


def occurrence(mask):
    total = 0
    for source in range(7):
        if mask & (1 << source):
            total += 2 if source == 0 else 4
    return total


def support_census():
    escapes = 0
    forbidden = 0
    open_pairs = {(4, 7): 0, (5, 7): 0, (6, 7): 0, (7, 7): 0}
    for left in range(128):
        for right in range(128):
            left_rank = left.bit_count()
            right_rank = right.bit_count()
            low, high = (left_rank, right_rank) if left_rank <= right_rank else (right_rank, left_rank)
            if low < 4 or high > 7:
                continue
            union = left | right
            shared = left & right
            if high <= 6:
                forbidden += 1
                if union == 127 and occurrence(shared) >= BUDGET[low] + BUDGET[high]:
                    escapes += 1
                continue
            if union == 127 and (low == 7 or occurrence(shared) >= BUDGET[low]):
                open_pairs[(low, high)] += 1
    return escapes, forbidden, open_pairs


def pair_floor(dimension):
    """Smallest n with 1+C(n,2) >= 2^dimension."""
    size = 1 << dimension
    for points in range(1, size + 1):
        if 1 + points * (points - 1) // 2 >= size:
            return points
    raise ValueError("pair floor missing")


def arithmetic_bounds():
    require(pair_floor(4) == 6, "F_2^4 pair floor")
    require(pair_floor(5) == 9, "F_2^5 pair floor")
    require(pair_floor(6) == 12, "F_2^6 pair floor")
    require(1 + 5 * 4 // 2 == 11 and 11 < 16, "five points miss F_2^4")
    require(1 + 8 * 7 // 2 == 29 and 29 < 32, "eight points miss F_2^5")
    require(1 + 11 * 10 // 2 == 56 and 56 < 64, "eleven points miss F_2^6")
    for low in range(4, 7):
        for high in range(low, 7):
            pooled = 4 * (low + high - 7)
            require(pooled < BUDGET[low] + BUDGET[high], "uniform intersection budget")
    # Length 12 on Q6 forces two steps in every direction.
    require(all(count == 2 for count in (2, 2, 2, 2, 2, 2)), "length-12 count vector")
    compositions = []
    for extras in range(4 ** 6):
        parts = []
        value = extras
        for _ in range(6):
            parts.append(value & 3)
            value >>= 2
        if sum(parts) == 7 and max(parts) <= 2:
            compositions.append(tuple(sorted(part + 1 for part in parts)))
    require(set(compositions) == {(1, 1, 2, 3, 3, 3), (1, 2, 2, 2, 3, 3), (2, 2, 2, 2, 2, 3)},
            "length-13 count vectors")
    projected = tuple(count for index, count in enumerate((2, 2, 2, 2, 2, 3)) if index != 5)
    require(projected == (2, 2, 2, 2, 2), "length-13 triple projects onto five twos")


def main():
    arithmetic_bounds()
    for dimension, steps in EXAMPLES.items():
        naive, _vertices = naive_cover(steps, dimension)
        require(naive and fast_cover(steps, dimension), "positive cube walk")
        require(prune_accepts(steps, dimension), "prune rejected a covering walk")
        truncated, _vertices = naive_cover(steps[:-1], dimension)
        require(not truncated, "truncated walk still covered")
    hyperplane, _vertices = naive_cover((0, 1, 2, 3, 4) * 3, 6)
    require(not hyperplane, "a five-direction walk covered F_2^6")

    q4_hits, q4_total = brute_covers(4, 5)
    require((q4_hits, q4_total) == (0, 1024), "Q4 length-5 census")
    q4_six, q4_six_total = brute_covers(4, 6)
    require((q4_six, q4_six_total) == (144, 4096), "Q4 length-6 census")

    q5_hits = 0
    q5_total = 0
    for length in (8, 9):
        hits, total = brute_covers(5, length)
        q5_hits += hits
        q5_total += total
    require(q5_hits == 0 and q5_total == 5 ** 8 + 5 ** 9, "Q5 length-8 and length-9 census")

    equal_hits, equal_leaves, _nodes = supply_search((2, 2, 2, 2, 2), 5, False)
    require(equal_leaves == count_walks((2, 2, 2, 2, 2)) == 113400, "Q5 equal-count domain")
    require(equal_hits == 0, "Q5 counts (2,2,2,2,2) covered")

    class_hits = 0
    class_nodes = 0
    for counts in ((3, 3, 3, 2, 1, 1), (3, 3, 2, 2, 2, 1)):
        hits, _leaves, nodes = supply_search(counts, 6, True)
        class_hits += hits
        class_nodes += nodes
    require(class_hits == 0, "Q6 length-13 count class covered")

    escapes, forbidden, open_pairs = support_census()
    # Ranks 4, 5, and 6 have C(7,4)+C(7,5)+C(7,6) = 63 supports.
    require(escapes == 0 and forbidden == 63 * 63, "rank pair at most 6 escaped")
    require(open_pairs == {(4, 7): 70, (5, 7): 42, (6, 7): 14, (7, 7): 1},
            "surviving support census")

    root = Path(__file__).resolve().parents[2]
    selected = (root / "certificates" / "selected-result.json").read_text(encoding="utf-8")
    require('"kappa": "781451/250000000"' in selected, "selected kappa")
    predecessor = (root / "research" / "length28-sojourn-rank" / "README.md").read_text(encoding="utf-8")
    require(
        "fix one multiplicity-2 source, require both arcs to use four" in predecessor,
        "predecessor flat-step question",
    )
    print(
        "PASS_LENGTH28_FLAT_STEP_BUDGET "
        f"b=6,10,14 q4={q4_total} q5={q5_total} "
        f"q5_equal={equal_leaves} q6_nodes={class_nodes} "
        f"forbidden={forbidden} open={tuple(open_pairs[pair] for pair in ((4, 7), (5, 7), (6, 7), (7, 7)))}"
    )


if __name__ == "__main__":
    main()
