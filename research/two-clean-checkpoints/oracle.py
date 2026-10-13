"""Exhaustive decorated-tree oracle, independent of interval optimization.

Shapes are generated as preorder bit words, then every internal vertex is
decorated D or C. No resource recurrence or optimal-substructure assumption
is used. Apache-2.0.
"""

from functools import lru_cache
from itertools import combinations, product


def _require(ok, message):
    if not ok:
        raise ValueError(message)


@lru_cache(None)
def enumerate_trees(n):
    """Return every ordered decorated full binary tree on leaves 0,...,n-1."""
    _require(type(n) is int and n > 0, "positive integer leaf count")
    result = []
    # One bit per vertex: 1 opens two children, 0 terminates a leaf. Exactly
    # one open slot is present initially and every proper prefix leaves a
    # positive number of slots. This tests complete shapes before decoration.
    for internal_positions in combinations(range(2 * n - 1), n - 1):
        internal = set(internal_positions)
        slots = 1
        for position in range(2 * n - 1):
            slots += 1 if position in internal else -1
            if slots == 0 and position != 2 * n - 2:
                break
        else:
            if slots != 0:
                continue
            leaf_positions = [i for i in range(2 * n - 1) if i not in internal]
            leaves = dict(zip(leaf_positions, range(n)))
            for labels in product("DC", repeat=n - 1):
                decorations = dict(zip(internal_positions, labels))
                stack = []
                for position in reversed(range(2 * n - 1)):
                    if position in internal:
                        left, right = stack.pop(), stack.pop()
                        stack.append((decorations[position], left, right))
                    else:
                        stack.append(leaves[position])
                _require(len(stack) == 1, "invalid preorder shape")
                result.append(stack[0])
    return tuple(result)


def _paths(tree):
    """Yield (leaf, connector/side path), preserving left-to-right order."""
    stack = [(tree, ())]
    while stack:
        node, path = stack.pop()
        if type(node) is int:
            _require(node >= 0, "nonnegative leaf index")
            yield node, path
        else:
            _require(isinstance(node, tuple) and len(node) == 3
                     and node[0] in ("D", "C"), "decorated binary tree")
            kind, left, right = node
            stack.append((right, path + ((kind, "R"),)))
            stack.append((left, path + ((kind, "L"),)))


def required_resources(tree):
    """Peak separately reserved dirty and clean arrays over all leaf paths."""
    paths = [path for _, path in _paths(tree)]
    return (max(sum(kind == "D" for kind, _ in path) for path in paths),
            max(sum(kind == "C" for kind, _ in path) for path in paths))


def leaf_multiplicities(tree):
    """Count invocations by multiplying path-edge call multiplicities."""
    paths = list(_paths(tree))
    _require([leaf for leaf, _ in paths] == list(range(len(paths))),
             "leaves must be 0,...,n-1 in order")
    # All edges double calls except the right edge of a clean connector.
    return tuple(2 ** sum(kind == "D" or side == "L" for kind, side in path)
                 for _, path in paths)


def tree_cost(tree, prices):
    prices = tuple(prices)
    _require(prices and all(type(p) is int and p > 0 for p in prices),
             "positive integer prices")
    counts = leaf_multiplicities(tree)
    _require(len(counts) == len(prices), "one price per leaf")
    return sum(count * price for count, price in zip(counts, prices))


def admissible(tree, total_scratch, clean_budget):
    _require(type(total_scratch) is int and type(clean_budget) is int
             and 0 <= clean_budget <= total_scratch, "scratch contract")
    dirty, clean = required_resources(tree)
    return dirty <= total_scratch - clean_budget and clean <= clean_budget


def best_tree(prices, total_scratch, clean_budget):
    """Minimize by inspecting all whole trees; return (cost, tree) or None."""
    prices = tuple(prices)
    _require(prices and all(type(p) is int and p > 0 for p in prices),
             "positive integer prices")
    _require(type(total_scratch) is int and type(clean_budget) is int
             and 0 <= clean_budget <= total_scratch, "scratch contract")
    best = None
    for tree in enumerate_trees(len(prices)):
        if admissible(tree, total_scratch, clean_budget):
            candidate = tree_cost(tree, prices), tree
            # Tree tie-breaking is deliberately independent of the producer.
            if best is None or candidate[0] < best[0]:
                best = candidate
    return best
