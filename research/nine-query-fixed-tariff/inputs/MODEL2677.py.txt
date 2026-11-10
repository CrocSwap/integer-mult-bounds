"""Path-lowered even-subset schedules and abstract invoices. Wentao Li + AI, Apache-2.0.

The complete-call tariff (b,a,x)=(38,2,2) and path-local shear lowering match
Arham Tahir's PR1898 `research/mutable-source-minimum-queries/model.py` on
CrocSwap main `0fdd7d82`. This file is self-contained for fork bases that lack
that package; it does not import predecessor executables.
"""
from collections import Counter
from itertools import combinations


def need(ok, message):
    if not ok:
        raise ValueError(message)


def min_even_subset_R(slots):
    """Minimum total even-subset readout count on connector prefix slots.

    ``slots[0]`` must be 0. The final restored 0 is identified with slot 0, so
    ``slots`` lists the Q distinct time values before the closing query edge.
    """
    need(type(slots) is tuple and slots and slots[0] == 0, "slots must start at 0")
    n = len(slots)
    best = [99] * 32
    for bits in range(1 << n):
        if bits.bit_count() % 2:
            continue
        value = 0
        for i in range(n):
            if bits >> i & 1:
                value ^= slots[i]
        size = bits.bit_count()
        if size < best[value]:
            best[value] = size
    if any(best[mask] >= 99 for mask in range(1, 32)):
        return None
    return sum(best[1:])


def even_subset_reads(slots):
    """One minimum even subset of slot indices per nonzero mask."""
    n = len(slots)
    reads = {}
    for mask in range(1, 32):
        found = None
        for size in range(2, n + 1, 2):
            for subset in combinations(range(n), size):
                value = 0
                for i in subset:
                    value ^= slots[i]
                if value == mask:
                    found = subset
                    break
            if found is not None:
                break
        need(found is not None, f"mask {mask} uncovered")
        reads[mask] = found
    return reads


def path_X(closed):
    """Paid source-XOR count under path-local compute/uncompute lowering."""
    total = 0
    for a, b in zip(closed, closed[1:]):
        delta = a ^ b
        need(delta != 0, "zero query edge")
        total += 2 * (delta.bit_count() - 1)
    return total


def rank_increments(closed):
    rows = [closed[i] ^ closed[i + 1] for i in range(len(closed) - 1)]
    rank = 0
    for bit in range(5):
        pivot = next((i for i in range(rank, len(rows)) if rows[i] >> bit & 1), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(len(rows)):
            if i != rank and rows[i] >> bit & 1:
                rows[i] ^= rows[rank]
        rank += 1
    return rank


def path_word(closed):
    """Literal Q/R/X word for a closed prefix path with even-subset readouts."""
    need(closed[0] == closed[-1] == 0, "path is not closed")
    slots = tuple(closed[:-1])
    reads = even_subset_reads(slots)
    word = []
    for step, point in enumerate(closed):
        word += [["R", mask] for mask, subset in reads.items() if step in subset]
        if step + 1 >= len(closed):
            break
        delta = point ^ closed[step + 1]
        need(delta != 0, "zero query edge")
        target = (delta & -delta).bit_length() - 1
        donors = [j for j in range(5) if j != target and delta >> j & 1]
        word += [["X", j, target] for j in donors]
        word.append(["Q", target])
        word += [["X", j, target] for j in reversed(donors)]
    return word


def root_ops(word, n=5):
    out = []
    for event in word:
        kind = event[0]
        if kind == "Q":
            out.append(["B", f"x{event[1]}", "z"])
        elif kind == "R":
            out.append([f"A{event[1]}", "z", f"y{event[1]}"])
        elif kind == "X":
            out.append(["", f"x{event[1]}", f"x{event[2]}"])
        else:
            raise ValueError("unknown root operation")
    return out


def roles(n=5):
    return [f"x{j}" for j in range(n)] + [f"y{m}" for m in range(1, 1 << n)] + ["z"] + [
        f"w{j}" for j in range(3)
    ]


def interpret(operations, names, initial=None):
    state = {r: {(r,)} for r in names} if initial is None else {r: set(p) for r, p in initial.items()}
    for coefficient, source, target in operations:
        need(source in state and target in state and source != target, "invalid port")
        terms = state[source] if coefficient == "" else {(coefficient,) + term for term in state[source]}
        state[target].symmetric_difference_update(terms)
    return state


def expected(n=5):
    state = {r: {(r,)} for r in roles(n)}
    for mask in range(1, 1 << n):
        for j in range(n):
            if mask >> j & 1:
                state[f"y{mask}"].symmetric_difference_update({(f"A{mask}", "B", f"x{j}")})
    return state


def check_identity(word, n=5):
    ops = root_ops(word, n)
    result = interpret(ops, roles(n))
    need(result == expected(n), "dirty root map or restoration failed")
    need(
        interpret(ops[::-1], roles(n), result) == {r: {(r,)} for r in roles(n)},
        "root inverse failed",
    )
    return Counter(event[0] for event in word)


def invoice(word):
    counts = Counter(event[0] for event in word)
    leaves = 28 * counts["Q"] + counts["R"]
    nodes = 9 * counts["Q"]
    dispatch = len(word)
    return {
        "Q": counts["Q"],
        "R": counts["R"],
        "X": counts["X"],
        "map_leaves": leaves,
        "echo_nodes": nodes,
        "root_dispatches": dispatch,
        "borrowed_dirty_rows": 4,
        "tariff": leaves + nodes + counts["X"] + dispatch,
        "complete_prices": {"b": 38, "a": 2, "x": 2},
    }


def minimum_word_6q():
    """PR1898 minimum-query word for n=5 (credited; used as comparator)."""
    reads = {}
    for mask in range(1, 32):
        coefficients = [mask & 1]
        coefficients += [((mask >> (t - 1)) ^ (mask >> t)) & 1 for t in range(1, 6)]
        reads[mask] = [t for t, bit in enumerate(coefficients) if bit]
    word = []
    for t in range(6):
        word += [["R", mask] for mask, positions in reads.items() if t in positions]
        if t < 5:
            word.append(["Q", t])
    word += [["X", j, 0] for j in range(1, 5)]
    word.append(["Q", 0])
    word += [["X", j, 0] for j in reversed(range(1, 5))]
    return word


def four_x_ten_q():
    """PR1370/PR1898 attributed closed path (credited comparator)."""
    points = [0, 4, 5, 1, 3, 7, 6, 14, 28, 16, 0]
    # Paired readouts as in predecessor path_word.
    readouts = {}
    for mask in range(1, 32):
        pair = next(
            (
                (s, t)
                for s in range(len(points))
                for t in range(s + 1, len(points))
                if points[s] ^ points[t] == mask
            ),
            None,
        )
        need(pair is not None, "ten-query path incomplete")
        readouts[mask] = pair
    word = []
    for s, point in enumerate(points):
        word += [["R", mask] for mask, pair in readouts.items() if s in pair]
        if s + 1 >= len(points):
            break
        delta = point ^ points[s + 1]
        target = (delta & -delta).bit_length() - 1
        donors = [j for j in range(5) if j != target and delta >> j & 1]
        word += [["X", j, target] for j in donors]
        word.append(["Q", target])
        word += [["X", j, target] for j in reversed(donors)]
    return word
