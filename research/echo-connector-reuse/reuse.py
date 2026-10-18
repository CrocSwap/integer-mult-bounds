"""Ordered dirty echo with restored sibling connectors borrowed by children.

Prepared for shhxera with substantial OpenAI Codex assistance. Apache-2.0.
Echo identity: androolloyd / PR673. Reserved-tree DP: Sagar Thakrar / PR730.
"""
from functools import lru_cache


def resources(tree, prices):
    if type(tree) is int:
        return 0, prices[tree]
    k = len(tree)
    if k not in (2, 3):
        raise ValueError('binary/ternary trees only')
    children = [resources(t, prices) for t in tree]
    peak = max([k - 1] + [s + (1 if i in (0, k - 1) else 2)
                           for i, (s, _) in enumerate(children)])
    bill = sum(c * (2 if i in (0, k - 1) else 4)
               for i, (_, c) in enumerate(children))
    return peak, bill


def optimize(prices, budget):
    prices = tuple(prices)
    if not prices or any(type(c) is not int or c <= 0 for c in prices):
        raise ValueError('positive integer prices required')
    if type(budget) is not int or budget < 0:
        raise ValueError('nonnegative integer budget required')

    @lru_cache(None)
    def solve(lo, hi, b):
        if b < 0:
            return None
        if hi == lo + 1:
            return prices[lo], lo
        best = None
        for cut in range(lo + 1, hi):
            a, c = solve(lo, cut, b - 1), solve(cut, hi, b - 1)
            if a is not None and c is not None:
                candidate = 2 * (a[0] + c[0]), (a[1], c[1])
                if best is None or candidate[0] < best[0]:
                    best = candidate
        if b >= 2:
            for cut in range(lo + 1, hi - 1):
                a = solve(lo, cut, b - 1)
                if a is None:
                    continue
                for end in range(cut + 1, hi):
                    m, c = solve(cut, end, b - 2), solve(end, hi, b - 1)
                    if m is not None and c is not None:
                        candidate = 2 * a[0] + 4 * m[0] + 2 * c[0], (a[1], m[1], c[1])
                        if best is None or candidate[0] < best[0]:
                            best = candidate
        return best

    answer = solve(0, len(prices), budget)
    if answer is None:
        raise ValueError('infeasible scratch budget')
    return answer


def instructions(tree, budget, sign=1):
    """Yield (source, target, factor, sign), excluding outer ports from scratch."""
    leaves = []
    def collect(node):
        if type(node) is int:
            leaves.append(node)
        else:
            if not isinstance(node, (tuple, list)) or len(node) not in (2, 3):
                raise ValueError('invalid tree')
            for child in node:
                collect(child)
    collect(tree)
    if leaves != list(range(len(leaves))):
        raise ValueError('ordered consecutive factor indices required')
    if type(budget) is not int or budget < resources(tree, [1] * len(leaves))[0]:
        raise ValueError('insufficient scratch')
    if type(sign) is not int or sign not in (-1, 1):
        raise ValueError('invalid sign')

    def emit(node, src, dst, pool, direction):
        if type(node) is int:
            yield src, dst, node, direction
            return
        k = len(node)
        connectors = pool[:k - 1]
        ports = [src] + connectors + [dst]
        chain = [(i, 1) for i in range(k - 1)]
        inv = lambda word: [(i, -q) for i, q in reversed(word)]
        word = chain + [(k - 1, 1)] + inv(chain) + chain[1:] + [(k - 1, -1)] + inv(chain[1:])
        if direction < 0:
            word = inv(word)
        for i, q in word:
            s, d = ports[i:i + 2]
            child_pool = [a for a in pool if a not in (s, d)]
            yield from emit(node[i], s, d, child_pool, q)

    yield from emit(tree, 0, 1, list(range(2, budget + 2)), sign)
