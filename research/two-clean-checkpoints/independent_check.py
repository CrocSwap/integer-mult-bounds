"""Whole-tree and symbolic checks independent of the planning recurrence."""

import json
from collections import Counter
from itertools import product
from math import comb

import oracle
import planner


def _check(condition, message):
    if not condition:
        raise AssertionError(message)


def _add_polynomial(target, increment, sign):
    for word, coefficient in increment.items():
        value = target.get(word, 0) + sign * coefficient
        if value:
            target[word] = value
        else:
            target.pop(word, None)


def _symbolic_execute(word, arrays):
    # Factor i prefixes a noncommuting letter to each source monomial.
    for factor, source, target, sign in word:
        increment = {("f" + str(factor),) + monomial: coefficient
                     for monomial, coefficient in arrays[source].items()}
        _add_polynomial(arrays[target], increment, sign)


def _nonlinear_execute(word, arrays):
    # Zero-preserving, target-independent, and generally nonlinear. Modular
    # arithmetic bounds the values without introducing inexact inverses.
    for factor, source, target, sign in word:
        x = arrays[source]
        increment = (x * x + (factor + 1) * x) % 101
        arrays[target] = (arrays[target] + sign * increment) % 101


def _check_tree(tree, n):
    dirty, clean = oracle.required_resources(tree)
    counts = oracle.leaf_multiplicities(tree)
    produced_profile = planner.profile(tree)
    _check(produced_profile["dirty"] == dirty, "dirty resource mismatch")
    _check(produced_profile["clean"] == clean, "clean resource mismatch")
    _check(produced_profile["leaves"] == dict(enumerate(counts)),
           "leaf multiplicity mismatch")

    dirty_ids = tuple(range(2, 2 + dirty))
    clean_ids = tuple(range(2 + dirty, 2 + dirty + clean))
    word = tuple(planner.emit(tree, 0, 1, dirty_ids, clean_ids))
    inverse = tuple(planner.emit(tree, 0, 1, dirty_ids, clean_ids, -1))
    _check(inverse == tuple((i, s, d, -sign) for i, s, d, sign in reversed(word)),
           "inverse must reverse the complete literal word")
    _check(Counter(i for i, _, _, _ in word) == dict(enumerate(counts)),
           "emitted call count mismatch")

    initial = [{("a" + str(i),): 1} if i not in clean_ids else {}
               for i in range(2 + dirty + clean)]
    arrays = [dict(value) for value in initial]
    _symbolic_execute(word, arrays)
    expected = [dict(value) for value in initial]
    product_word = tuple("f" + str(i) for i in reversed(range(n))) + ("a0",)
    _add_polynomial(expected[1], {product_word: 1}, 1)
    _check(arrays == expected, "noncommutative product or scratch restoration")
    _symbolic_execute(inverse, arrays)
    _check(arrays == initial, "noncommutative forward/inverse restoration")

    nonlinear_initial = [(13 + 17 * i) % 101 if i not in clean_ids else 0
                         for i in range(len(initial))]
    nonlinear = nonlinear_initial.copy()
    _nonlinear_execute(word, nonlinear)
    _check(all(nonlinear[i] == nonlinear_initial[i]
               for i in range(len(initial)) if i != 1),
           "nonlinear source/scratch restoration")
    _nonlinear_execute(inverse, nonlinear)
    _check(nonlinear == nonlinear_initial, "nonlinear inverse restoration")
    return len(word)


def run_checks():
    """Exhaust small trees; return stable, JSON-serializable check counts."""
    tree_counts = {}
    emitted_leaf_calls = 0
    comparisons = 0
    feasible = 0
    tree_resource_checks = 0
    for n in range(1, 7):
        trees = oracle.enumerate_trees(n)
        expected_count = comb(2 * n - 2, n - 1) // n * 2 ** (n - 1)
        _check(len(trees) == expected_count and len(set(trees)) == expected_count,
               "decorated Catalan enumeration is incomplete or duplicated")
        tree_counts[str(n)] = len(trees)
        for tree in trees:
            emitted_leaf_calls += _check_tree(tree, n)
            # Verify admissions for every relevant fixed pool partition,
            # including insufficient and surplus-resource cases.
            for scratch in range(n):
                for clean in range(scratch + 1):
                    allowed = oracle.admissible(tree, scratch, clean)
                    dirty_ids = tuple(range(2, 2 + scratch - clean))
                    clean_ids = tuple(range(2 + scratch - clean, 2 + scratch))
                    try:
                        planner.emit(tree, 0, 1, dirty_ids, clean_ids)
                    except ValueError:
                        _check(not allowed, "emitter rejected an admissible tree")
                    else:
                        _check(allowed, "emitter accepted insufficient resources")
                    tree_resource_checks += 1

        price_vectors = product((1, 3), repeat=n) if n <= 5 else [(1,) * n]
        # Whole-tree minima are grouped by resource profile only to avoid
        # re-inspecting trees for each budget; no child solutions are reused.
        profiles = [(tree, oracle.required_resources(tree),
                     oracle.leaf_multiplicities(tree)) for tree in trees]
        for prices in price_vectors:
            scored = [(sum(p * count for p, count in zip(prices, counts)), d, c)
                      for _, (d, c), counts in profiles]
            for scratch in range(n):
                for clean in range(scratch + 1):
                    costs = [cost for cost, d, c in scored
                             if d <= scratch - clean and c <= clean]
                    expected = min(costs) if costs else None
                    answer = planner.solve(prices, scratch, clean)
                    actual = None if answer is None else answer[0]
                    _check(actual == expected,
                           f"whole-tree optimum mismatch: {prices}, {scratch}, {clean}")
                    if answer is not None:
                        feasible += 1
                        _check(answer[1] in trees, "producer tree outside enumeration")
                        _check(oracle.admissible(answer[1], scratch, clean),
                               "producer optimum violates resources")
                        _check(oracle.tree_cost(answer[1], prices) == answer[0],
                               "producer optimum has incorrect price")
                    comparisons += 1

    return {"decorated_trees_by_leaf_count": tree_counts,
            "trees_checked": sum(tree_counts.values()),
            "tree_resource_admissions_checked": tree_resource_checks,
            "forward_leaf_calls_checked": emitted_leaf_calls,
            "noncommutative_symbolic_cases": sum(tree_counts.values()),
            "nonlinear_mod101_cases": sum(tree_counts.values()),
            "whole_tree_optimum_comparisons": comparisons,
            "feasible_optimum_comparisons": feasible,
            "prices": "all {1,3}^n for 1<=n<=5; unit prices for n=6",
            "budgets": "every 0<=clean<=scratch<=n-1",
            "status": "passed"}


if __name__ == "__main__":
    print(json.dumps(run_checks(), indent=2, sort_keys=True))
