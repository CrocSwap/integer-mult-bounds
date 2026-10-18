"""Exact additive echo with ancestor ports borrowed from a fixed dirty pool.

Apache-2.0. Prepared for bitplane with substantial OpenAI Codex assistance.
The echo word and sibling allocator are credited to PR673/730/822; see NOTICE.
"""
from functools import lru_cache


def leaves(tree):
    if type(tree) is int and tree >= 0:
        return [tree]
    if not isinstance(tree, (tuple, list)) or len(tree) not in (2, 3):
        raise ValueError("an ordered binary/ternary tree is required")
    return [i for child in tree for i in leaves(child)]


def validate(tree):
    ids = leaves(tree)
    if ids != list(range(len(ids))):
        raise ValueError("ordered consecutive leaf indices required")
    return len(ids)


def macro(arity):
    chain = [(i, 1) for i in range(arity - 1)]
    inv = lambda word: [(i, -q) for i, q in reversed(word)]
    return (chain + [(arity - 1, 1)] + inv(chain) + chain[1:]
            + [(arity - 1, -1)] + inv(chain[1:]))


def instructions(tree, dirty_rows=3, sign=1):
    """Yield (source, target, factor, sign); row zero is globally read-only.

    Four mutable rows suffice for all binary/ternary trees. Three suffice for
    binary trees. Smaller supplied pools can fail during iteration; callers
    needing atomic validation must materialize the word before executing it.
    """
    validate(tree)
    if type(dirty_rows) is not int or dirty_rows < 0:
        raise ValueError("nonnegative integer dirty row count required")
    if type(sign) is not int or sign not in (-1, 1):
        raise ValueError("integer sign +1 or -1 required")
    # This fixed priority makes the nonlinear boundary witness reproducible.
    pool = [r for r in [2, 3, 1, 4] if r < dirty_rows + 2]
    pool += list(range(5, dirty_rows + 2))

    def emit(node, src, dst, direction):
        if type(node) is int:
            yield src, dst, node, direction
            return
        connectors = [r for r in pool if r not in (src, dst)][:len(node)-1]
        if len(connectors) != len(node)-1:
            raise ValueError("insufficient mutable ports")
        ports = [src] + connectors + [dst]
        word = macro(len(node))
        if direction < 0:
            word = [(i, -q) for i, q in reversed(word)]
        for i, q in word:
            yield from emit(node[i], ports[i], ports[i+1], q)

    yield from emit(tree, 0, 1, sign)


def unit_plan(limit):
    """Minimize unit leaf calls over the stated binary/ternary echo class.

    Ties use (bill, arity, split sizes). Planning is separate from execution.
    """
    if type(limit) is not int or limit < 1:
        raise ValueError("positive integer limit required")
    bills, splits = [0, 1], [None, None]
    candidates = 0
    for n in range(2, limit+1):
        best = None
        for a in range(1, n):
            candidate = (2*(bills[a]+bills[n-a]), 2, (a, n-a))
            candidates += 1
            if best is None or candidate < best:
                best = candidate
        for a in range(1, n-1):
            for b in range(1, n-a):
                c = n-a-b
                candidate = (2*bills[a]+4*bills[b]+2*bills[c], 3, (a, b, c))
                candidates += 1
                if candidate < best:
                    best = candidate
        bills.append(best[0])
        splits.append(best[2])

    def build(n, start=0):
        if n == 1:
            return start
        children = []
        for size in splits[n]:
            children.append(build(size, start))
            start += size
        return tuple(children)

    return bills, [build(n) for n in range(1, limit+1)], candidates


def resources(tree):
    """(leaves, calls, reserved dirty rows, sibling dirty rows, depth)."""
    if type(tree) is int:
        return 1, 1, 0, 0, 0
    children = [resources(t) for t in tree]
    k = len(tree)
    weights = [2, 2] if k == 2 else [2, 4, 2]
    return (sum(r[0] for r in children),
            sum(w*r[1] for w, r in zip(weights, children)),
            k-1+max(r[2] for r in children),
            max([k-1]+[r[3]+(1 if i in (0, k-1) else 2)
                        for i, r in enumerate(children)]),
            1+max(r[4] for r in children))


def norm_bound(tree, factor_norm):
    """Bound every prefix on the joint maximum norm, including scalar work."""
    if type(factor_norm) is not int or factor_norm < 1:
        raise ValueError("positive integer factor norm required")
    if type(tree) is int:
        return 1+factor_norm
    return ((len(tree)+1)*factor_norm**len(leaves(tree))
            * max(norm_bound(child, factor_norm) for child in tree))


def reserved_instructions(tree, sign=1):
    """Old fully reserved allocator, used only as an address-cost comparator."""
    validate(tree)

    def emit(node, src, dst, pool, q):
        if type(node) is int:
            yield src, dst, node, q
            return
        connectors = pool[:len(node)-1]
        ports = [src]+connectors+[dst]
        word = macro(len(node))
        if q < 0:
            word = [(i, -s) for i, s in reversed(word)]
        for i, s in word:
            yield from emit(node[i], ports[i], ports[i+1],
                            pool[len(node)-1:], s)

    yield from emit(tree, 0, 1, list(range(2, resources(tree)[2]+2)), sign)


@lru_cache(None)
def balanced_binary(n, offset=0):
    if n == 1:
        return offset
    left = n//2
    return balanced_binary(left, offset), balanced_binary(n-left, offset+left)
