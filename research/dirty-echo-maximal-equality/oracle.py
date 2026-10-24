"""Independent bounded all-arity minima and literal ordered-tree enumeration.

Produced by Nick Petalas. Apache-2.0. No predecessor engine is imported.
"""

from itertools import chain, product


def minima(max_budget=8, max_leaves=256):
    """Min-plus root composition; no equality threshold or shape rule."""
    if not 0 <= max_budget <= 8 or not 1 <= max_leaves <= 256:
        raise ValueError("oracle domain")
    # Each edge multiplier is at most 2**(arity-1), so any admitted tree
    # costs at most max_leaves * 2**max_budget <= 65536.
    infinity = 1 << 128
    rows = [[infinity] * (max_leaves + 1) for _ in range(max_budget + 1)]
    transitions = 0
    for budget in range(max_budget + 1):
        rows[budget][1] = 1
        for arity in range(2, budget + 2):
            child = rows[budget - arity + 1]
            capacity = min(max_leaves, 2 ** (budget - arity + 1))
            states = [infinity] * (max_leaves + 1)
            states[0] = 0
            for position in range(arity):
                multiplier = 2 if position in (0, arity - 1) else 4
                following = [infinity] * (max_leaves + 1)
                for prefix in range(max_leaves + 1):
                    if states[prefix] == infinity:
                        continue
                    for size in range(1, min(capacity, max_leaves - prefix) + 1):
                        if child[size] == infinity:
                            continue
                        transitions += 1
                        total = prefix + size
                        value = states[prefix] + multiplier * child[size]
                        following[total] = min(following[total], value)
                states = following
            for size in range(2, max_leaves + 1):
                rows[budget][size] = min(rows[budget][size], states[size])
    return rows, infinity, transitions


def ordered_trees(max_leaves=8):
    """Enumerate root cuts and Cartesian products, as postfix arity words."""
    if not 1 <= max_leaves <= 8:
        raise ValueError("tree enumeration domain")
    trees = [[], [(0,)]]
    for size in range(2, max_leaves + 1):
        current = []
        for cut_mask in range(1, 1 << (size - 1)):
            cuts = [0] + [j for j in range(1, size) if cut_mask >> (j - 1) & 1]
            cuts.append(size)
            sizes = [right - left for left, right in zip(cuts, cuts[1:])]
            for children in product(*(trees[n] for n in sizes)):
                current.append(tuple(chain.from_iterable(children)) + (len(sizes),))
                if len(current) > 5000:
                    raise ValueError("tree capacity exceeded")
        if len(set(current)) != len(current):
            raise ValueError("duplicate ordered tree")
        trees.append(current)
    return trees


def resource_profile(word):
    """Evaluate the literal grammar, separately from the equality classifier."""
    if not 1 <= len(word) <= 511:
        raise ValueError("postfix word length")
    stack = []
    for arity in word:
        if type(arity) is not int or not 0 <= arity <= 256 or arity == 1:
            raise ValueError("postfix arity")
        if arity == 0:
            stack.append((1, 1, 0))
            continue
        if len(stack) < arity:
            raise ValueError("postfix stack underflow")
        children = stack[-arity:]
        del stack[-arity:]
        leaves = sum(item[0] for item in children)
        calls = 2 * children[0][1] + 2 * children[-1][1]
        calls += 4 * sum(item[1] for item in children[1:-1])
        scratch = arity - 1 + max(item[2] for item in children)
        stack.append((leaves, calls, scratch))
    if len(stack) != 1 or stack[0][0] > 256:
        raise ValueError("postfix endpoint")
    return stack[0]
