"""Separate exact replay and exhaustive small-tree oracle; stdlib only.

This module imports neither engine nor the pinned predecessor. Both
implementations were written in the same AI-assisted session, not by an
independent human reviewer. Apache-2.0; Hanson Sun / OpenAI Codex.
"""
from functools import lru_cache
from itertools import product


def check(ok, message):
    if not ok:
        raise ValueError(message)


def shapes(size):
    """Enumerate ordered trees by recursive positive-size compositions."""
    @lru_cache(None)
    def forest(total, count):
        if count == 0:
            return ((),) if total == 0 else ()
        out = []
        for first in range(1, total + 1):
            for rest in forest(total - first, count - 1):
                out.append((first,) + rest)
        return tuple(out)

    @lru_cache(None)
    def trees(n):
        if n == 1:
            return (None,)
        result = []
        for arity in (2, 3, 4):
            for sizes in forest(n, arity):
                result.extend(product(*(trees(s) for s in sizes)))
        return tuple(result)

    def label(node, start):
        if node is None:
            return start, start + 1
        children = []
        for child in node:
            child, start = label(child, start)
            children.append(child)
        return tuple(children), start

    return tuple(label(t, 0)[0] for t in trees(size))


def independent_word(tree, protected=False, src=0, dst=1):
    """Different, explicit sweep description of the multiway commutator."""
    priority = [2, 3, 4, 1] if protected else [2, 3, 4, 0, 1]

    def run(node, src, dst, direction):
        if isinstance(node, int):
            return [(src, dst, node, direction)]
        chain = [src]
        for row in priority:
            if row != src and row != dst and len(chain) < len(node):
                chain.append(row)
        check(len(chain) == len(node), "protected pool cannot host this node")
        chain.append(dst)
        steps = []
        for i in range(len(node)):
            steps.append((i, 1))
        for i in range(len(node) - 2, -1, -1):
            steps.append((i, -1))
        for i in range(1, len(node) - 1):
            steps.append((i, 1))
        steps.append((len(node) - 1, -1))
        for i in range(len(node) - 2, 0, -1):
            steps.append((i, -1))
        if direction == -1:
            steps = [(i, -q) for i, q in steps[::-1]]
        out = []
        for i, q in steps:
            out += run(node[i], chain[i], chain[i + 1], q)
        return out

    check(not protected or dst != 0, "row zero is protected")
    return run(tree, src, dst, 1)


def free_replay(word, size, sign=1, check_inverse=True, src=0, dst=1):
    """Free Z-module: separate symbol for each initial row and factor word."""
    state = [{(r, ()): 1} for r in range(5)]
    initial = [r.copy() for r in state]
    peak_terms = 5
    source_changed = False

    def apply(event):
        src, dst, factor, q = event
        check(0 <= src < 5 and 0 <= dst < 5 and src != dst, "bad oracle port")
        check(0 <= factor < size and q in (-1, 1), "bad oracle factor/sign")
        result = state[dst].copy()
        for (origin, history), coefficient in state[src].items():
            key = origin, (factor,) + history
            result[key] = result.get(key, 0) + q * coefficient
            if result[key] == 0:
                del result[key]
        state[dst] = result

    for event in word:
        apply(event)
        peak_terms = max(peak_terms, sum(len(r) for r in state))
        source_changed |= state[src] != initial[src]
    expected = [r.copy() for r in initial]
    expected[dst][(src, tuple(range(size - 1, -1, -1)))] = sign
    check(state == expected, "free noncommutative endpoint mismatch")
    if check_inverse:
        for inverse_src, inverse_dst, factor, q in word[::-1]:
            apply((inverse_src, inverse_dst, factor, -q))
        check(state == initial, "literal inverse did not restore all rows")
    return dict(leaf_calls=len(word), peak_terms=peak_terms, source_changed=source_changed)


def independent_minima(limit):
    """Min-plus layered paths, without materializing root compositions."""
    costs = {name: [0, 1] for name in ("T", "R", "M")}
    transitions = 0
    for n in range(2, limit + 1):
        answers = {}
        for mode in ("T", "R", "M"):
            best = None
            for arity in range(2, (3 if mode == "T" else 4) + 1):
                if arity > n:
                    continue
                states = {0: 0}
                for child in range(arity):
                    next_states = {}
                    kind = "T" if mode == "R" and child > 0 else mode
                    multiplier = 2 if child in (0, arity - 1) else 4
                    for used, bill in states.items():
                        for length in range(1, n - used - (arity - child - 1) + 1):
                            if length >= n:
                                continue
                            transitions += 1
                            new = used + length
                            price = bill + multiplier * costs[kind][length]
                            if new not in next_states or price < next_states[new]:
                                next_states[new] = price
                    states = next_states
                if n in states:
                    best = states[n] if best is None else min(best, states[n])
            answers[mode] = best
        for mode, value in answers.items():
            check(value is not None, "no independent root plan")
            costs[mode].append(value)
    return costs, transitions


def dense_reference(word, matrices, rows, modulus=None, nonlinear=False):
    state = [list(r) for r in rows]
    for src, dst, factor, sign in word:
        source = [x * x for x in state[src]] if nonlinear else state[src]
        update = [sum(c * x for c, x in zip(r, source)) for r in matrices[factor]]
        for i, value in enumerate(update):
            state[dst][i] += sign * value
            if modulus is not None:
                state[dst][i] %= modulus
    return state


def direct_endpoint(matrices, rows, sign=1, modulus=None):
    vector = list(rows[0])
    for matrix in matrices:
        vector = [sum(c * v for c, v in zip(row, vector)) for row in matrix]
    result = [list(row) for row in rows]
    result[1] = [a + sign * b for a, b in zip(rows[1], vector)]
    if modulus is not None:
        result = [[v % modulus for v in row] for row in result]
    return result


def closed_invoice(word, n, length, width):
    """Independent closed macro counts and explicit address list per leaf."""
    count = len(word)
    mult = count * length**2
    adds = count * (length**2 + length)
    reductions = count * (2 * length**2 + length)
    zeros = count * (length + 4) + 4
    reads = count * (2 * length**2 + length)
    writes = count * length
    distance = 0
    for src, dst, factor, _ in word:
        route = [0]
        for i in range(length):
            for j in range(length):
                route += [src * length + j, 5 * length + factor * length**2 + i * length + j]
            route += [dst * length + i, dst * length + i]
        route.append(0)
        distance += sum(abs(a - b) for a, b in zip(route, route[1:]))
    return dict(multiply=mult, add=adds, reduce=reductions, zero=zeros,
                read=reads, write=writes, commands=mult + adds + reductions + zeros + reads + writes,
                intercell_steps=distance, data_head_steps=width * distance + 2 * (width - 1) * (reads + writes),
                data_bit_actions=width * (reads + writes))
