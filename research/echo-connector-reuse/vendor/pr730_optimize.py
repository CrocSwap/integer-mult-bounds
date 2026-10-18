"""Exact ordered binary/ternary dirty-echo trees at a fixed scratch budget.

Prepared for Sagar Thakrar with substantial OpenAI Codex assistance.
Apache-2.0. The instruction emitter adapts androolloyd's PR673 echo.py;
see NOTICE.md and vendor/pr673_echo.py for its unchanged source.
"""

from functools import lru_cache


def optimize(costs, budget):
    """Return (minimum charged cost, tree); raise ValueError if infeasible.

    Prices cover complete leaf calls at one common precision. A tree is a
    factor index or a tuple of two/three children, in original factor order.
    All connector arrays remain reserved during every descendant call.
    """
    costs = tuple(costs)
    if not costs or any(type(c) is not int or c <= 0 for c in costs):
        raise ValueError("positive integer leaf costs required")
    if type(budget) is not int or budget < 0:
        raise ValueError("nonnegative integer scratch budget required")

    @lru_cache(None)
    def solve(lo, hi, available):
        if hi - lo == 1:
            return costs[lo], lo
        if available < 1:
            return None
        best = None
        for mid in range(lo + 1, hi):
            left = solve(lo, mid, available - 1)
            right = solve(mid, hi, available - 1)
            if left is not None and right is not None:
                charge = 2 * (left[0] + right[0])
                if best is None or charge < best[0]:
                    best = charge, (left[1], right[1])
        if available >= 2:
            for first in range(lo + 1, hi - 1):
                left = solve(lo, first, available - 2)
                if left is None:
                    continue
                for second in range(first + 1, hi):
                    middle = solve(first, second, available - 2)
                    right = solve(second, hi, available - 2)
                    if middle is not None and right is not None:
                        charge = 2 * left[0] + 4 * middle[0] + 2 * right[0]
                        if best is None or charge < best[0]:
                            best = charge, (left[1], middle[1], right[1])
        return best

    result = solve(0, len(costs), budget)
    if result is None:
        raise ValueError("scratch budget cannot hold an ordered echo tree")
    return result


def resources(tree, costs):
    """Return actual peak reserved scratch and the complete leaf charge."""
    if isinstance(tree, int):
        return 0, costs[tree]
    children = [resources(child, costs) for child in tree]
    scratch = len(tree) - 1 + max(depth for depth, _ in children)
    charge = sum((2 if i in (0, len(tree) - 1) else 4) * cost
                 for i, (_, cost) in enumerate(children))
    return scratch, charge


def instructions(tree, src=0, dst=1, scratch_first=2, sign=1):
    """Emit the PR673 echo, or its reverse inverse, for an optimized tree."""
    pending = [(tree, src, dst, scratch_first, sign)]
    while pending:
        node, source, target, first, direction = pending.pop()
        if isinstance(node, int):
            yield source, target, node, direction
            continue
        k = len(node)
        chain = [(node[i], source if i == 0 else first + i - 1,
                  first + i, 1) for i in range(k - 1)]
        last = (node[-1], first + k - 2, target, 1)
        invert = lambda commands: [(t, s, d, -q) for t, s, d, q in reversed(commands)]
        commands = chain + [last] + invert(chain) + chain[1:] + invert([last]) + invert(chain[1:])
        if direction == -1:
            commands = invert(commands)
        pending.extend((child, s, d, first + k - 1, q)
                       for child, s, d, q in reversed(commands))
