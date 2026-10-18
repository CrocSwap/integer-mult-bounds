"""Independent exhaustive, algebraic, and execution checks for schedule.py."""

from __future__ import annotations

from collections import Counter
from functools import cache
from hashlib import sha256
from itertools import combinations, product
import json

from schedule import Plan, compose, optimal_plan, plan_table, word


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@cache
def trees(leaves):
    if leaves == 1:
        return ((),)
    result = []
    for cuts_count in range(1, leaves):
        for cuts in combinations(range(1, leaves), cuts_count):
            boundaries = (0, *cuts, leaves)
            sizes = tuple(right - left for left, right in zip(boundaries, boundaries[1:]))
            result.extend(product(*(trees(size) for size in sizes)))
    return tuple(result)


@cache
def tree_statistics(tree):
    if not tree:
        return 1, 1, 0
    children = [tree_statistics(child) for child in tree]
    calls = 2 * (children[0][1] + children[-1][1])
    calls += 4 * sum(child[1] for child in children[1:-1])
    return sum(child[0] for child in children), calls, len(tree) - 1 + max(child[2] for child in children)


@cache
def as_plan(tree):
    return Plan(tuple(as_plan(child) for child in tree))


def as_tree(plan):
    return tuple(as_tree(child) for child in plan.children)


def expected_multiplicities(tree):
    if not tree:
        return [1]
    counts = []
    for position, child in enumerate(tree):
        weight = 2 if position == 0 or position == len(tree) - 1 else 4
        counts.extend(weight * value for value in expected_multiplicities(child))
    return counts


def inspect_word(plan):
    leaves, calls, scratch = tree_statistics(as_tree(plan))
    require((plan.factors, plan.calls, plan.scratch) == (leaves, calls, scratch), "incorrect plan metadata")
    forward = tuple(word(plan))
    backward = tuple(word(plan, -1))
    require(len(forward) == calls, "leaf-call count disagrees with the expanded word")
    require(backward == tuple((factor, src, dst, -sign) for factor, src, dst, sign in reversed(forward)),
            "inverse is not the reversed, sign-negated complete word")
    for command in forward:
        require(len(command) == 4 and all(type(value) is int for value in command), "malformed instruction")
        factor, source, target, sign = command
        require(0 <= factor < leaves, "factor index out of range")
        require(0 <= source < scratch + 2 and 0 <= target < scratch + 2, "array index out of range")
        require(source != target and target != 0, "illegal source or target alias")
        require(sign in (-1, 1), "invalid instruction sign")
    counts = Counter(command[0] for command in forward)
    require([counts[index] for index in range(leaves)] == expected_multiplicities(as_tree(plan)),
            "per-factor restoration multiplicities disagree")
    require(max(max(command[1:3]) for command in forward) - 1 == scratch, "scratch peak disagrees")
    return forward, backward


def polynomial_initial(scratch):
    # Negative letters identify independent initial dirt; nonnegative letters are ordered factors.
    return [{(-index - 1,): 1} for index in range(scratch + 2)]


def polynomial_execute(state, commands):
    for factor, source, target, sign in commands:
        for monomial, coefficient in tuple(state[source].items()):
            term = (*monomial, factor)
            value = state[target].get(term, 0) + sign * coefficient
            if value:
                state[target][term] = value
            else:
                state[target].pop(term, None)


def polynomial_expected(leaves, scratch, sign=1):
    expected = polynomial_initial(scratch)
    expected[1][(-1, *range(leaves))] = sign
    return expected


def check_polynomials(plan, forward, backward):
    initial = polynomial_initial(plan.scratch)
    for sign, commands, inverse in ((1, forward, backward), (-1, backward, forward)):
        state = polynomial_initial(plan.scratch)
        polynomial_execute(state, commands)
        require(state == polynomial_expected(plan.factors, plan.scratch, sign),
                "noncommutative product or dirt restoration failed")
        polynomial_execute(state, inverse)
        require(state == initial, "symbolic complete inverse failed")


def check_exhaustive(table):
    oracle = [[None] * 9 for _ in range(9)]
    counts = []
    symbolic_count = 0
    for leaves in range(1, 9):
        shapes = trees(leaves)
        counts.append(len(shapes))
        for tree in shapes:
            actual_leaves, calls, scratch = tree_statistics(tree)
            require(actual_leaves == leaves, "exhaustive tree has the wrong leaf count")
            for budget in range(scratch, 9):
                previous = oracle[budget][leaves]
                if previous is None or calls < previous:
                    oracle[budget][leaves] = calls
            if leaves <= 7:
                plan = as_plan(tree)
                check_polynomials(plan, *inspect_word(plan))
                symbolic_count += 1
        for budget in range(9):
            plan = table[budget][leaves]
            observed = None if plan is None else plan.calls
            require(observed == oracle[budget][leaves], f"exhaustive optimum mismatch at n={leaves}, s={budget}")
    require(counts == [1, 1, 3, 11, 45, 197, 903, 4279], "ordered-tree enumeration is incomplete")
    return {
        "max_factors": 8,
        "max_scratch": 8,
        "trees_by_factors": counts,
        "trees": sum(counts),
        "optimum_cells": 72,
        "optimum_sha256": digest(oracle),
        "symbolic_trees": symbolic_count,
        "symbolic_max_factors": 7,
    }


def nonlinear_leaf(phase, call_count):
    modulus = 65521

    def leaf(source, target, factor, sign):
        call_count[0] += 1
        for index in range(len(source)):
            value = source[index] ** 2 + phase[factor] * source[(index + 1) % len(source)] + index
            rounded = value // (2 + factor % 7)
            target[index] = (target[index] + sign * rounded) % modulus

    return leaf


def check_nonlinear(plan):
    calls = 0
    for seed in (1, 7, 31):
        phase = [(factor + 3) * (seed + 11) for factor in range(plan.factors)]
        for sign in (1, -1):
            arrays = [[((index + 1) * 101 + component * 37 + seed * 13) % 65521
                       for component in range(3)] for index in range(plan.scratch + 3)]
            before = [array[:] for array in arrays]
            phase_before = phase[:]
            count = [0]
            leaf = nonlinear_leaf(phase, count)
            compose(plan, arrays[0], arrays[1], arrays[2:], leaf, sign=sign, readonly=(phase,))
            require(arrays[0] == before[0] and arrays[2:] == before[2:],
                    "nonlinear call failed to restore source, dirt, or unused extra scratch")
            require(phase == phase_before, "nonlinear call changed a read-only input")
            require(count[0] == plan.calls, "compose did not execute the full restoration bill")
            compose(plan, arrays[0], arrays[1], arrays[2:], leaf, sign=-sign, readonly=(phase,))
            require(arrays == before and phase == phase_before, "nonlinear complete inverse failed")
            require(count[0] == 2 * plan.calls, "inverse leaf-call count disagrees")
            calls += count[0]
    return calls


def check_mutations():
    plan = Plan((Plan(), Plan(), Plan()))
    forward, _ = inspect_word(plan)
    expected = polynomial_expected(plan.factors, plan.scratch)
    mutants = []
    for index, command in enumerate(forward):
        mutants.append((f"delete_{index}", forward[:index] + forward[index + 1:], expected))
        factor, source, target, sign = command
        changed = (*forward[:index], (factor, source, target, -sign), *forward[index + 1:])
        mutants.append((f"flip_sign_{index}", changed, expected))
    reused = tuple((factor, 2 if source == 3 else source, 2 if target == 3 else target, sign)
                   for factor, source, target, sign in forward)
    mutants.append(("reuse_live_scratch", reused, expected))
    binary_forward = tuple(word(Plan((Plan(), Plan()))))
    wrong_inverse = tuple((factor, source, target, -sign)
                          for factor, source, target, sign in binary_forward)
    mutants.append(("inverse_without_reversing", binary_forward + wrong_inverse,
                    polynomial_initial(plan.scratch)))
    for name, commands, desired in mutants:
        state = polynomial_initial(plan.scratch)
        polynomial_execute(state, commands)
        require(state != desired, f"negative control escaped detection: {name}")
    return {"deletions": len(forward), "sign_flips": len(forward), "live_scratch_reuse": 1,
            "incorrect_inverse_order": 1, "detected": len(mutants),
            "names_sha256": digest([name for name, _, _ in mutants])}


def check_lower_bound(table):
    checked = 0
    for budget, row in enumerate(table):
        for factors, plan in enumerate(row[1:], 1):
            if plan is not None:
                require(plan.calls >= 2 ** (budget + 1) * factors - 4 ** budget,
                        "plan violates the universal call lower bound")
                checked += 1
    equality_cases = []
    for budget in range(2, 7):
        blocks = 2 ** (budget - 2)
        for factors in range(3 * blocks, 4 * blocks + 1):
            four_blocks = factors - 3 * blocks
            forest = [(((), ()), ((), ()))] * four_blocks
            forest.extend([((), (), ())] * (blocks - four_blocks))
            while len(forest) > 1:
                forest = [(forest[index], forest[index + 1]) for index in range(0, len(forest), 2)]
            tree = forest[0]
            expected = 2 ** (budget + 1) * factors - 4 ** budget
            require(tree_statistics(tree) == (factors, expected, budget), "equality-family construction failed")
            plan = as_plan(tree)
            check_polynomials(plan, *inspect_word(plan))
            require(table[budget][factors].calls == expected, "DP misses a proved sharp lower bound")
            equality_cases.append([budget, factors, expected])
    return {"formula": "2^(s+1)*n - 4^s", "feasible_cells": checked,
            "equality_family_scratch": [2, 6], "equality_family_plans": len(equality_cases),
            "equality_family_sha256": digest(equality_cases)}


def must_reject(call, label):
    try:
        call()
    except ValueError:
        return
    raise RuntimeError(f"invalid input was accepted: {label}")


def check_guards(table):
    probe = Plan((Plan(), Plan(), Plan()))
    patches = [
        ("source_target_alias", lambda args: args.update(target=args["source"])),
        ("source_scratch_alias", lambda args: args["scratch"].__setitem__(0, args["source"])),
        ("target_scratch_alias", lambda args: args["scratch"].__setitem__(0, args["target"])),
        ("scratch_alias", lambda args: args["scratch"].__setitem__(1, args["scratch"][0])),
        ("extra_scratch_alias", lambda args: args["scratch"].append(args["source"])),
        ("readonly_source_alias", lambda args: args.update(readonly=(args["source"],))),
        ("readonly_target_alias", lambda args: args.update(readonly=(args["target"],))),
        ("readonly_scratch_alias", lambda args: args.update(readonly=(args["scratch"][0],))),
        ("readonly_extra_alias", lambda args: args["scratch"].append(args["readonly"][0])),
        ("insufficient_scratch", lambda args: args["scratch"].pop()),
        ("tuple_source", lambda args: args.update(source=tuple(args["source"]))),
        ("tuple_scratch", lambda args: args["scratch"].__setitem__(0, tuple(args["scratch"][0]))),
        ("empty_source", lambda args: args["source"].clear()),
        ("target_length", lambda args: args["target"].pop()),
        ("scratch_length", lambda args: args["scratch"][0].pop()),
        ("extra_scratch_length", lambda args: args["scratch"].append([1])),
        ("invalid_plan", lambda args: args.update(plan=None)),
        ("noncallable_leaf", lambda args: args.update(leaf=None)),
    ]
    patches.extend((f"sign_{repr(sign)}", lambda args, sign=sign: args.update(sign=sign))
                   for sign in (0, 2, -2, True, 1.0, "1"))
    for name, patch in patches:
        count = [0]
        phase = [41, 43, 47]
        args = {"plan": probe, "source": [2, 3, 5], "target": [7, 11, 13],
                "scratch": [[17, 19, 23], [29, 31, 37]], "leaf": nonlinear_leaf(phase, count),
                "sign": 1, "readonly": (phase,)}
        patch(args)
        arrays = [args["source"], args["target"], *args["scratch"], *args["readonly"], phase]
        snapshots = [(array, array[:]) for array in arrays if isinstance(array, list)]
        must_reject(lambda: compose(**args), name)
        require(count[0] == 0 and all(array == before for array, before in snapshots),
                f"API rejection mutated caller data: {name}")

    invalid_queries = [(0, 0), (-1, 0), (True, 1), (1.0, 1), ("1", 1),
                       (1, -1), (1, True), (1, 1.0), (1, "1")]
    for factors, budget in invalid_queries:
        must_reject(lambda: optimal_plan(factors, budget), "optimal_plan argument")
        must_reject(lambda: plan_table(factors, budget), "plan_table argument")
    for children in ([], (Plan(),), (None, None)):
        must_reject(lambda: Plan(children), "plan children")
    for sign in (0, 2, -2, True, 1.0, "1"):
        must_reject(lambda: tuple(word(probe, sign)), "word sign")
    must_reject(lambda: tuple(word(None)), "word plan")
    infeasible = 0
    for budget, row in enumerate(table):
        for factors in range(1, len(row)):
            if row[factors] is None:
                must_reject(lambda: optimal_plan(factors, budget), "infeasible budget")
                infeasible += 1
    for factors, budget in ((1, 0), (2, 1), (3, 2), (50, 6), (50, 7), (50, 8), (64, 6)):
        plan = optimal_plan(factors, budget)
        require(plan.calls == table[budget][factors].calls and plan.scratch <= budget,
                "optimal_plan disagrees with the certificate table")
    return {"compose_rejections_without_mutation": len(patches), "query_argument_rejections": 2 * len(invalid_queries),
            "plan_rejections": 3, "word_rejections": 7, "infeasible_queries": infeasible,
            "valid_optimal_plan_queries": 7}


def run_checks():
    table = plan_table(64, 8)
    require(len(table) == 9 and all(len(row) == 65 for row in table), "incorrect table dimensions")
    exhaustive = check_exhaustive(table)
    words = sha256()
    checked = 0
    nonlinear_calls = 0
    for budget, row in enumerate(table):
        for factors in range(1, 65):
            plan = row[factors]
            require((plan is not None) == (factors <= 2 ** budget), "incorrect feasible domain")
            if plan is None:
                continue
            require(plan.factors == factors and plan.scratch <= budget, "plan exceeds its requested budget")
            forward, backward = inspect_word(plan)
            check_polynomials(plan, forward, backward)
            nonlinear_calls += check_nonlinear(plan)
            words.update(json.dumps([budget, factors, forward], separators=(",", ":")).encode())
            checked += 1
    require(checked == 255, "incorrect feasible plan count")
    lower_bound = check_lower_bound(table)
    symbolic_plans = checked + exhaustive["symbolic_trees"] + lower_bound["equality_family_plans"]
    costs = [[None if plan is None else plan.calls for plan in row[1:]] for row in table]
    main_costs = {str(budget): table[budget][50].calls for budget in (6, 7, 8)}
    require(main_costs == {"6": 2304, "7": 1472, "8": 1120}, "main instance disagrees with independent recurrence")
    return {
        "exhaustive": exhaustive,
        "table": {"max_factors": 64, "max_scratch": 8, "feasible_plans": checked,
                  "costs_sha256": digest(costs), "expanded_words_sha256": words.hexdigest()},
        "lower_bound": lower_bound,
        "symbolic": {"table_plans": checked, "small_trees": exhaustive["symbolic_trees"],
                     "equality_family_plans": lower_bound["equality_family_plans"],
                     "signed_identities": 2 * symbolic_plans,
                     "round_trips": 2 * symbolic_plans,
                     "coefficient_ring": "free noncommutative integer polynomials"},
        "nonlinear": {"map": "integer square and floor modulo 65521", "width": 3,
                      "seeds": [1, 7, 31], "round_trips": 6 * checked, "leaf_calls": nonlinear_calls,
                      "extra_unused_scratch_per_call": 1},
        "negative_controls": check_mutations(),
        "guards": check_guards(table),
        "main_factors": 50,
        "main_calls_by_scratch_budget": main_costs,
    }
