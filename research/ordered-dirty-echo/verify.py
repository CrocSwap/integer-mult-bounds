"""Independent finite checks for ordered mixed-arity dirty echoes.

Prepared for Sagar Thakrar with substantial OpenAI Codex assistance.
Apache-2.0. These finite checks are not a proof of the multiplication theorem.
Run with Python normally or with -O; no check uses an assert statement.
"""

import argparse
from collections import Counter
from functools import lru_cache
import hashlib
import importlib.util
from itertools import product
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from optimize import instructions, optimize, resources


def check(condition, message):
    if not condition:
        raise AssertionError(message)


@lru_cache(None)
def all_trees(count):
    """Enumerate postfix leaf/binary/ternary words by stack reduction."""
    found = []

    def visit(next_leaf, stack):
        if next_leaf == count and len(stack) == 1:
            found.append(stack[0])
            return
        if next_leaf < count:
            visit(next_leaf + 1, stack + (next_leaf,))
        for arity in (2, 3):
            if len(stack) >= arity:
                visit(next_leaf, stack[:-arity] + (stack[-arity:],))

    visit(0, ())
    check(len(found) == len(set(found)), "duplicate exhaustive tree")
    return tuple(found)


def oracle_resources(tree, costs):
    """Price each root-to-leaf path; do not call the production recurrence."""
    pending = [(tree, 0, 1)]
    scratch = weighted = 0
    leaves = []
    while pending:
        node, occupied, multiplicity = pending.pop()
        if isinstance(node, int):
            scratch = max(scratch, occupied)
            weighted += multiplicity * costs[node]
            leaves.append(node)
            continue
        arity = len(node)
        for position in range(arity - 1, -1, -1):
            copies = 2 if position in (0, arity - 1) else 4
            pending.append((node[position], occupied + arity - 1,
                            multiplicity * copies))
    check(leaves == list(range(len(costs))), "factor order or coverage")
    return scratch, weighted


@lru_cache(None)
def leaf_counts(tree):
    return Counter(index for _, _, index, _ in instructions(tree))


def run_formal(word, register_count):
    """Exact free-algebra expressions: (operator word, initial register)."""
    registers = [{((), origin): 1} for origin in range(register_count)]
    for source, target, factor, sign in word:
        check(source != target, "aliased source and destination")
        check(sign in (-1, 1), "invalid instruction sign")
        for (prefix, origin), coefficient in registers[source].items():
            term = ((factor,) + prefix, origin)
            registers[target][term] = registers[target].get(term, 0) + sign * coefficient
        registers[target] = {term: value for term, value in registers[target].items()
                             if value}
    return registers


def validate_word(tree, costs, budget, word=None, claimed_cost=None, sign=1):
    if word is None:
        word = tuple(instructions(tree, sign=sign))
    else:
        word = tuple(word)
    check(word, "empty instruction word")
    largest = max(max(source, target) for source, target, _, _ in word)
    check(largest < budget + 2, "insufficient scratch")
    measured_cost = sum(costs[factor] for _, _, factor, _ in word)
    if claimed_cost is not None:
        check(measured_cost == claimed_cost, "weighted leaf price")
    registers = run_formal(word, budget + 2)
    expected = [{((), origin): 1} for origin in range(budget + 2)]
    expected[1][(tuple(range(len(costs) - 1, -1, -1)), 0)] = sign
    check(registers == expected, "ordered product and dirty restoration")


def nonlinear_restore(tree, budget):
    """Exact nonlinear integer maps with bounded values, not rounded floats."""
    word = tuple(instructions(tree))
    inverse = tuple(instructions(tree, sign=-1))
    check(inverse == tuple((s, t, i, -q) for s, t, i, q in reversed(word)),
          "reverse-inverse instruction word")
    for offset in (0, 7):
        initial = [(-1) ** i * (3 * i + offset + 2) for i in range(budget + 2)]
        registers = initial[:]
        for source, target, factor, sign in word:
            value = registers[source] % 17
            nonlinear = (value * value + (factor + 2) * value + factor) % 17 - 8
            registers[target] += sign * nonlinear
        check(registers[0] == initial[0] and registers[2:] == initial[2:],
              "nonlinear dirty restoration")
        for source, target, factor, sign in inverse:
            value = registers[source] % 17
            nonlinear = (value * value + (factor + 2) * value + factor) % 17 - 8
            registers[target] += sign * nonlinear
        check(registers == initial, "nonlinear reverse-inverse restoration")


def rejected(call, expected_message):
    try:
        call()
    except AssertionError as error:
        check(expected_message in str(error), "mutation failed for the wrong reason")
    else:
        raise AssertionError("mutation was accepted: " + expected_message)


def exhaustive_check():
    cases = 0
    checked_trees = set()
    counts = []
    for count in range(1, 7):
        trees = all_trees(count)
        counts.append(len(trees))
        for costs in product((1, 3), repeat=count):
            priced = [(oracle_resources(tree, costs), tree) for tree in trees]
            for budget in range(count):
                feasible = [(price, tree) for (scratch, price), tree in priced
                            if scratch <= budget]
                try:
                    actual, tree = optimize(costs, budget)
                except ValueError:
                    check(not feasible, "optimizer rejected a feasible domain")
                else:
                    check(feasible, "optimizer accepted an infeasible domain")
                    check(actual == min(price for price, _ in feasible),
                          "optimizer differs from exhaustive minimum")
                    scratch, oracle_price = oracle_resources(tree, costs)
                    check((scratch, actual) == resources(tree, costs),
                          "production resource accounting")
                    check(actual == oracle_price and scratch <= budget,
                          "optimizer witness resources")
                    check(actual == sum(costs[i] * n for i, n in leaf_counts(tree).items()),
                          "weighted instruction accounting")
                    checked_trees.add(tree)
                cases += 1
        # Check every enumerated shape, including shapes the optimizer never chooses.
        for tree in trees:
            costs = (1,) * count
            scratch, price = oracle_resources(tree, costs)
            validate_word(tree, costs, scratch, claimed_cost=price)
            validate_word(tree, costs, scratch, claimed_cost=price, sign=-1)
            nonlinear_restore(tree, scratch)
    check(counts == [1, 1, 3, 10, 38, 154], "exhaustive tree counts")
    return cases, sum(counts), len(checked_trees)


def witness_check():
    weighted = (3, 2, 1, 9, 8, 7, 6)
    cases = (((1,) * 27, 6, 464, 464), ((1,) * 56, 8, 1600, 1600),
             (weighted, 4, 180, 36), (weighted, 5, 168, 40))
    records = []
    for costs, budget, expected, calls in cases:
        price, tree = optimize(costs, budget)
        check(price == expected, "recorded witness")
        scratch, oracle_price = oracle_resources(tree, costs)
        check(price == oracle_price and scratch <= budget, "witness path accounting")
        check(sum(leaf_counts(tree).values()) == calls, "witness call count")
        validate_word(tree, costs, budget, claimed_cost=price)
        validate_word(tree, costs, budget, claimed_cost=price, sign=-1)
        nonlinear_restore(tree, budget)
        word = tuple(instructions(tree))
        encoded = (json.dumps(word, separators=(",", ":")) + "\n").encode("utf-8")
        records.append(dict(costs=list(costs), budget=budget, scratch=scratch,
                            weighted_cost=price, calls=calls,
                            tree=json.loads(json.dumps(tree)),
                            leaf_multiplicities=[leaf_counts(tree)[i]
                                                 for i in range(len(costs))],
                            word_sha256=hashlib.sha256(encoded).hexdigest()))
    return records


def refined_ternary_baseline(count):
    """PR689's longer-end split, independently priced as a level frontier."""
    pending = [(count, 0, 1)]
    calls = scratch = 0
    while pending:
        size, occupied, copies = pending.pop()
        if size == 1:
            calls += copies
            scratch = max(scratch, occupied)
        elif size == 2:
            pending.extend(((1, occupied + 1, copies * 2),) * 2)
        else:
            quotient, remainder = divmod(size, 3)
            pending.extend(((quotient + (remainder > 0), occupied + 2, copies * 2),
                            (quotient, occupied + 2, copies * 4),
                            (quotient + (remainder > 1), occupied + 2, copies * 2)))
    return scratch, calls


def baseline_check():
    # Pinned PR689 ternary.py's public resources order is (calls, scratch).
    for count, expected in ((7, (4, 40)), (15, (5, 160)),
                            (27, (6, 512)), (56, (8, 2112))):
        check(refined_ternary_baseline(count) == expected, "PR689 baseline")


def check_pins():
    manifest = (HERE / "SOURCES.json").read_bytes()
    sources = json.loads(manifest)
    checked = []
    for predecessor in sources["predecessors"]:
        for source in predecessor["files"]:
            if "local_copy" in source:
                digest = hashlib.sha256((HERE / source["local_copy"]).read_bytes()).hexdigest()
                check(digest == source["sha256"], "predecessor source pin")
                checked.append(dict(path=source["local_copy"], sha256=digest,
                                    commit=predecessor["commit"]))
    check(checked, "missing local predecessor pins")
    return sources, dict(manifest_sha256=hashlib.sha256(manifest).hexdigest(),
                         local_files=checked)


def predecessor_check():
    spec = importlib.util.spec_from_file_location("pr673_echo", HERE / "vendor/pr673_echo.py")
    predecessor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(predecessor)

    def balanced(first, count, fanout):
        if count == 1:
            return first
        arity = min(count, fanout)
        quotient, remainder = divmod(count, arity)
        children = []
        for position in range(arity):
            size = quotient + (position < remainder)
            children.append(balanced(first, size, fanout))
            first += size
        return tuple(children)

    compared = 0
    for count in range(1, 17):
        for fanout in (2, 3):
            tree = balanced(0, count, fanout)
            costs = (1,) * count
            scratch, price = oracle_resources(tree, costs)
            check((scratch, price) == predecessor.resources(count, fanout),
                  "pinned predecessor resource comparison")
            for sign in (1, -1):
                word = tuple(instructions(tree, sign=sign))
                pinned = tuple(predecessor.instructions(0, count, 0, 1, 2, fanout, sign))
                check(word == pinned, "pinned predecessor instruction comparison")
                validate_word(tree, costs, scratch, word=word, claimed_cost=price, sign=sign)
                compared += 1
    return compared


def nonlinear_counterexample():
    increments = []
    for dirty in (0, 1):
        registers = [1, 0, dirty]
        for source, target, factor, sign in instructions((0, 1)):
            increment = registers[source] if factor == 0 else registers[source] ** 2
            registers[target] += sign * increment
        check(registers[0] == 1 and registers[2] == dirty,
              "nonlinear counterexample restoration")
        increments.append(registers[1])
    check(increments == [1, 3], "nonlinear dirty-dependent increment")
    return dict(first_map="f(x)=x", second_map="g(x)=x^2", source=1,
                initial_scratch=[0, 1], target_increments=increments,
                composed_value=1)


def input_check():
    cases = (((), 0), ((0,), 0), ((True,), 0), ((1.5,), 0),
             ((1,), -1), ((1,), True))
    for costs, budget in cases:
        try:
            optimize(costs, budget)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid optimizer input accepted")
    check(optimize([1], 0) == (1, 0), "valid list input")
    return len(cases)


def mutation_check():
    tree = (0, 1, 2)
    costs = (1, 1, 1)
    word = tuple(instructions(tree))
    rejected(lambda: validate_word(tree, costs, 2, word=word[:-1]),
             "ordered product and dirty restoration")
    reversed_order = [(s, t, 2 - i, q) for s, t, i, q in word]
    rejected(lambda: validate_word(tree, costs, 2, word=reversed_order),
             "ordered product and dirty restoration")
    rejected(lambda: validate_word(tree, costs, 2, claimed_cost=6),
             "weighted leaf price")
    rejected(lambda: validate_word(tree, costs, 1), "insufficient scratch")
    return dict(omitted_restore="rejected", reversed_factor_order="rejected",
                underpriced_middle="rejected", insufficient_scratch="rejected")


def build_certificate():
    sources, pins = check_pins()
    cases, trees, optimal_shapes = exhaustive_check()
    witnesses = witness_check()
    baseline_check()
    mutations = mutation_check()
    return dict(schema_version=1, base_commit=sources["base_commit"],
                assignment_seed=sources["assignment_seed"], source_pins=pins,
                exhaustive_domain=dict(leaf_counts=list(range(1, 7)), cost_alphabet=[1, 3],
                                       scratch_budgets="0 through leaf_count-1",
                                       cost_budget_cases=cases, ordered_trees=trees,
                                       optimizer_shapes=optimal_shapes),
                predecessor_words=predecessor_check(),
                invalid_inputs_rejected=input_check(),
                word_encoding="UTF-8 compact JSON instruction array followed by LF",
                witnesses=witnesses,
                pr689_baselines=[dict(leaves=n, scratch=refined_ternary_baseline(n)[0],
                                      calls=refined_ternary_baseline(n)[1])
                                 for n in (7, 15, 27, 56)],
                nonlinear_counterexample=nonlinear_counterexample(),
                mutation_controls=mutations)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print the recomputed certificate")
    args = parser.parse_args()
    certificate = build_certificate()
    if args.emit:
        print(json.dumps(certificate, indent=2, sort_keys=True))
        return
    recorded = json.loads((HERE / "CERTIFICATE.json").read_text())
    check(json.dumps(certificate, sort_keys=True) == json.dumps(recorded, sort_keys=True),
          "certificate differs from complete replay")
    domain = certificate["exhaustive_domain"]
    print(f"PASS_ORDERED_DIRTY_ECHO: {domain['cost_budget_cases']} exhaustive cases; "
          f"{domain['ordered_trees']} ordered trees; "
          f"{certificate['predecessor_words']} pinned predecessor words; "
          f"{len(certificate['witnesses'])} witnesses; "
          f"{len(certificate['mutation_controls'])} rejected mutations")
    print("Exact formal ordered products and nonlinear integer restoration checked; "
          "finite coverage only.")


if __name__ == "__main__":
    main()
