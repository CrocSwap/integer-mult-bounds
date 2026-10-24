"""Exact finite corroboration of the all-size theorem in PROOF.md.

Produced by Nick Petalas. Apache-2.0. Writes only an explicitly requested
exclusive receipt. All checks remain active under optimized Python.
"""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MAX_BUDGET = 8
MAX_LEAVES = 256


def require(condition, message):
    if not condition:
        raise ValueError(message)


def threshold(budget):
    require(type(budget) is int and 0 <= budget <= MAX_BUDGET, "budget domain")
    return (2 ** (budget + 1) + 2) // 3


def construct(budget, leaves):
    """Construct each equality size, with no recursive Python calls."""
    lower = threshold(budget)
    require(type(leaves) is int and lower <= leaves <= 2**budget, "equality size")
    pending = [(budget, leaves)]
    word = []
    # At most n leaves and n-1 internal nodes, each with a finish marker.
    for _ in range(3 * MAX_LEAVES):
        if not pending:
            break
        level, count = pending.pop()
        if level == -1:
            word.append(count)
        elif level == 0:
            require(count == 1, "leaf invariant")
            word.append(0)
        elif count >= 2 * threshold(level - 1):
            first = max(threshold(level - 1), count - 2 ** (level - 1))
            pending.extend([(-1, 2), (level - 1, count - first), (level - 1, first)])
        else:
            require(level >= 2, "ternary level")
            cap = 2 ** (level - 2)
            pending.extend([(-1, 3), (level - 2, cap),
                            (level - 2, count - 2 * cap), (level - 2, cap)])
    require(not pending, "constructor work bound")
    return tuple(word)


def equality_budgets(word):
    """Recognize only the proved structural rules, without call arithmetic."""
    require(1 <= len(word) <= 511, "word length")
    stack = []
    for arity in word:
        require(type(arity) is int and 0 <= arity <= MAX_LEAVES and arity != 1,
                "word arity")
        if arity == 0:
            stack.append((1, 1))
            continue
        require(len(stack) >= arity, "word underflow")
        children = stack[-arity:]
        del stack[-arity:]
        leaves = sum(item[0] for item in children)
        mask = 0
        if arity in (2, 3):
            for budget in range(arity - 1, MAX_BUDGET + 1):
                child_budget = budget - arity + 1
                tight = all(item[1] >> child_budget & 1 for item in children)
                ends_full = arity == 2 or (
                    children[0][0] == children[-1][0] == 2**child_budget)
                if tight and ends_full:
                    mask |= 1 << budget
        stack.append((leaves, mask))
    require(len(stack) == 1 and stack[0][0] <= MAX_LEAVES, "word endpoint")
    return stack[0][1]


def load_oracle():
    spec = importlib.util.spec_from_file_location("equality_oracle", ROOT / "oracle.py")
    require(spec is not None and spec.loader is not None, "oracle loader")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_minima(oracle):
    rows, infinity, transitions = oracle.minima(MAX_BUDGET, MAX_LEAVES)
    equality_counts = []
    witnesses = 0
    cells = 0
    for budget in range(MAX_BUDGET + 1):
        tight_sizes = []
        for leaves in range(1, MAX_LEAVES + 1):
            cells += 1
            cost = rows[budget][leaves]
            bound = 2 ** (budget + 1) * leaves - 4**budget
            feasible = leaves <= 2**budget
            require((cost != infinity) == feasible, "oracle feasibility")
            if not feasible:
                continue
            require(cost >= bound, "oracle lower bound")
            expected = threshold(budget) <= leaves
            require((cost == bound) == expected, "maximal interval")
            if expected:
                tight_sizes.append(leaves)
                word = construct(budget, leaves)
                profile = oracle.resource_profile(word)
                require(profile == (leaves, bound, budget), "constructed resources")
                require(equality_budgets(word) == 1 << budget, "constructed structure")
                witnesses += 1
        equality_counts.append(len(tight_sizes))
    return dict(cells=cells, transitions=transitions,
                equality_sizes_per_budget=equality_counts, witnesses=witnesses)


def check_shapes(oracle):
    census = oracle.ordered_trees(8)
    per_size = [len(group) for group in census[1:]]
    comparisons = 0
    equalities = 0
    for group in census[1:]:
        for word in group:
            leaves, calls, scratch = oracle.resource_profile(word)
            recognized = equality_budgets(word)
            for budget in range(MAX_BUDGET + 1):
                actual = scratch <= budget and calls == (
                    2 ** (budget + 1) * leaves - 4**budget)
                require(bool(recognized >> budget & 1) == actual, "shape equality")
                comparisons += 1
                equalities += actual
    require(sum(per_size) <= 6000, "enumeration capacity")
    return dict(trees_per_size=per_size, trees=sum(per_size),
                tree_budget_comparisons=comparisons, equality_occurrences=equalities)


def rejection_controls(oracle):
    invalid = [(-1, 1), (9, 256), (True, 1), (0, True), (0, 0),
               (1, 1), (4, 10), (4, 17), (6, 42), (8, 170)]
    count = 0
    for budget, leaves in invalid:
        try:
            construct(budget, leaves)
        except ValueError:
            count += 1
        else:
            raise ValueError("invalid constructor accepted")
    bad_words = [(), (1,), (True,), (2,), (0, 0), (0, 0, 3)]
    for word in bad_words:
        for function in (equality_budgets, oracle.resource_profile):
            try:
                function(word)
            except ValueError:
                count += 1
            else:
                raise ValueError("invalid word accepted")
    # A ternary root with an unsaturated endpoint is not tight; a flat
    # four-child root cannot be tight at any budget, despite feasibility.
    unsaturated = construct(2, 3) + construct(2, 3) + construct(2, 4) + (3,)
    require(equality_budgets(unsaturated) == 0, "endpoint control")
    require(equality_budgets((0, 0, 0, 0, 4)) == 0, "arity-four control")
    return dict(rejected_inputs=count, structural_controls=2)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def receipt():
    oracle = load_oracle()
    examples = []
    for budget, leaves in [(4, 11), (6, 43), (8, 171)]:
        word = construct(budget, leaves)
        n, calls, scratch = oracle.resource_profile(word)
        examples.append(dict(budget=budget, leaves=n, calls=calls, scratch=scratch,
                             postfix_sha256=hashlib.sha256(bytes(word)).hexdigest()))
    hashes = {}
    for name in ("PROOF.md", "verify.py", "oracle.py", "test_package.py"):
        hashes[name] = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
    return dict(schema_version=1, status="PASS_DIRTY_ECHO_MAXIMAL_EQUALITY",
                scope="Scoped written theorem; finite exact corroboration only",
                minima=check_minima(oracle), shapes=check_shapes(oracle),
                controls=rejection_controls(oracle), examples=examples,
                source_sha256=hashes)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="create an exclusive generated receipt")
    args = parser.parse_args()
    result = receipt()
    if args.write is not None:
        require(args.write.is_absolute(), "output must be absolute")
        with args.write.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        expected = json.loads((ROOT / "RESULT.json").read_text(),
                              object_pairs_hook=unique_object)
        require(canonical(result) == canonical(expected), "generated receipt mismatch")
    print(result["status"])
    print(canonical(result))


if __name__ == "__main__":
    main()
