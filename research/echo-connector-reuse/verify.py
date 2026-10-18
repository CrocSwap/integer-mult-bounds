"""Independent evidence for the scoped sibling-connector allocator.

Standard library only. Finite checks support, but do not replace, PROOF.md.
Prepared for shhxera with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import importlib.util
import itertools
import json
from collections import Counter
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@lru_cache(None)
def trees(lo, hi):
    """Enumerate all ordered 2/3-ary trees, independently of optimization."""
    if hi == lo + 1:
        return (lo,)
    result = []
    for cuts in itertools.chain(itertools.combinations(range(lo + 1, hi), 1),
                                itertools.combinations(range(lo + 1, hi), 2)):
        ends = (lo,) + cuts + (hi,)
        result.extend(itertools.product(*(trees(a, b) for a, b in zip(ends, ends[1:]))))
    return tuple(result)


def reference_word(tree, budget, unsafe_target=False):
    """Separate flat-word compiler, with literal 4/8-call macro templates."""
    patterns = {2: ((0, 1), (1, 1), (0, -1), (1, -1)),
                3: ((0, 1), (1, 1), (2, 1), (1, -1),
                    (0, -1), (1, 1), (2, -1), (1, -1))}
    def build(node, source, target, available):
        if type(node) is int:
            return [(source, target, node, 1)]
        require(len(available) >= len(node) - 1, 'reference allocation infeasible')
        route = (source,) + available[:len(node) - 1] + (target,)
        children = []
        for i, child in enumerate(node):
            pool = tuple(a for a in available if a != route[i] and a != route[i + 1])
            # Deliberately invalid negative control: target can affect the increment.
            if unsafe_target and i < len(node) - 1 and type(child) is not int:
                pool = (target,) + pool
            children.append(build(child, route[i], route[i + 1], pool))
        output = []
        for i, sign in patterns[len(node)]:
            part = children[i]
            output.extend(part if sign == 1 else [(s, d, f, -q) for s, d, f, q in reversed(part)])
        return output
    return build(tree, 0, 1, tuple(range(2, budget + 2)))


def min_budget(tree, n):
    for b in range(n):
        try:
            reference_word(tree, b)
            return b
        except ValueError:
            pass
    raise ValueError('no allocation')


def symbolic(word, roles, count, sign=1):
    """Execute in a free noncommutative module over independent dirty inputs."""
    initial = [{((), a): 1} for a in range(roles)]
    state = [dict(row) for row in initial]
    for s, d, f, q in word:
        require(0 <= s < roles and 0 <= d < roles and s != d, 'aliased leaf')
        require(0 <= f < count and q in (-1, 1), 'bad leaf')
        for (prefix, variable), coefficient in list(state[s].items()):
            key = ((f,) + prefix, variable)
            state[d][key] = state[d].get(key, 0) + q * coefficient
            if not state[d][key]:
                del state[d][key]
    target = dict(initial[1])
    target[(tuple(reversed(range(count))), 0)] = sign
    require(state == initial[:1] + [target] + initial[2:], 'ordered product/restoration failed')


def free_nonlinear(word, roles):
    """Uninterpreted unary functions over canonical additive expression DAGs."""
    intern = {}
    children = {}
    def atom(key, inputs=()):
        if key not in intern:
            intern[key] = len(intern)
            children[intern[key]] = inputs
        return intern[key]
    initial = [{atom(('input', i)): 1} for i in range(roles)]
    def run(commands, start):
        state = [dict(row) for row in start]
        for source, target, factor, sign in commands:
            require(source != target, 'free nonlinear alias')
            argument = tuple(sorted(state[source].items()))
            value = atom(('function', factor, argument), tuple(state[source]))
            state[target][value] = state[target].get(value, 0) + sign
            if state[target][value] == 0:
                del state[target][value]
        return state
    final = run(word, initial)
    require(final[:1] + final[2:] == initial[:1] + initial[2:], 'free nonlinear restoration')
    reverse = [(s, d, i, -q) for s, d, i, q in reversed(word)]
    require(run(reverse, final) == initial, 'free nonlinear inverse')
    # The target increment must not contain its independent incoming variable.
    delta = dict(final[1])
    target_atom = next(iter(initial[1]))
    delta[target_atom] = delta.get(target_atom, 0) - 1
    if delta[target_atom] == 0:
        del delta[target_atom]
    pending, visited = list(delta), set()
    while pending:
        a = pending.pop()
        if a not in visited:
            require(a != target_atom, 'free nonlinear target dependence')
            visited.add(a)
            pending.extend(children[a])


def nonlinear(word, initial):
    state = list(initial)
    for s, d, f, q in word:
        require(s != d, 'nonlinear aliased leaf')
        z = state[s]
        increment = (z % 17) ** 2 + (f + 1) * (z % 7) - 3
        state[d] += q * increment
    return state


def nonlinear_checks(word, roles):
    inverse = [(s, d, f, -q) for s, d, f, q in reversed(word)]
    for offset in (0, 1, 59):
        initial = [offset + 3 * a - 7 for a in range(roles)]
        final = nonlinear(word, initial)
        require(final[:1] + final[2:] == initial[:1] + initial[2:], 'nonlinear dirt not restored')
        require(nonlinear(inverse, final) == initial, 'nonlinear inverse failed')
        shifted = list(initial)
        shifted[1] += 91
        other = nonlinear(word, shifted)
        require(other[1] - shifted[1] == final[1] - initial[1], 'target-dependent increment')


def reject(fn, label):
    try:
        fn()
    except (ValueError, IndexError):
        return
    raise ValueError('control accepted: ' + label)


def check_pins():
    data = json.loads((HERE / 'SOURCES.json').read_text())
    for row in data['files']:
        path = HERE / row['local']
        require(hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256'], 'source drift: ' + row['local'])
    return data


def certificate():
    check_pins()
    new = load('reuse', HERE / 'reuse.py')
    old = load('pr730', HERE / 'vendor/pr730_optimize.py')
    shapes = 0
    nonlinear_cases = 0
    exhaustive = 0
    for n in range(1, 8):
        candidates = []
        for tree in trees(0, n):
            b = min_budget(tree, n)
            word = reference_word(tree, b)
            require(list(new.instructions(tree, b)) == word, 'independent words disagree')
            require(new.resources(tree, [1] * n) == (b, len(word)), 'resource count mismatch')
            symbolic(word, b + 2, n)
            symbolic(list(new.instructions(tree, b, -1)), b + 2, n, -1)
            nonlinear_checks(word, b + 2)
            free_nonlinear(word, b + 2)
            nonlinear_cases += 3
            shapes += 1
            candidates.append((b, Counter(f for _, _, f, _ in word)))
        # Complete positive {1,3} price domain through six factors, all caps.
        if n <= 6:
            for prices in itertools.product((1, 3), repeat=n):
                for b in range(n):
                    costs = [sum(prices[i] * c for i, c in census.items())
                             for needed, census in candidates if needed <= b]
                    if costs:
                        got, tree = new.optimize(prices, b)
                        require(got == min(costs), 'exhaustive optimum mismatch')
                        require(new.resources(tree, prices)[1] == got, 'reported price mismatch')
                    else:
                        reject(lambda: new.optimize(prices, b), 'infeasible optimizer')
                    exhaustive += 1

    witnesses = []
    for n, b in ((5, 2), (15, 4), (27, 5), (59, 5), (59, 6)):
        prices = [1] * n
        bill, tree = new.optimize(prices, b)
        peak, _ = new.resources(tree, prices)
        word = list(new.instructions(tree, b))
        require(word == reference_word(tree, b), 'witness word mismatch')
        require(len(word) == bill, 'witness bill mismatch')
        symbolic(word, b + 2, n)
        nonlinear_checks(word, b + 2)
        nonlinear_cases += 3
        try:
            prior, prior_tree = old.optimize(prices, b)
        except ValueError:
            prior, prior_tree = None, None
        prior_scratch = None
        if prior_tree is not None:
            prior_scratch, prior_price = old.resources(prior_tree, prices)
            prior_word = list(old.instructions(prior_tree))
            require(len(prior_word) == prior_price == prior, 'predecessor bill mismatch')
            symbolic(prior_word, prior_scratch + 2, n)
            nonlinear_checks(prior_word, prior_scratch + 2)
        require(max(max(s,d) for s,d,_,_ in word) < peak + 2, 'unused cap unexpectedly addressed')
        witnesses.append(dict(factors=n, budget=b, actual_scratch=peak,
                              reserved_calls=prior, reserved_scratch=prior_scratch, reuse_calls=bill, tree=tree,
                              word_sha256=hashlib.sha256(json.dumps(word, separators=(',', ':')).encode()).hexdigest()))

    tree = ((0, 1), 2, (3, 4))
    word = list(new.instructions(tree, 2))
    controls = 0
    for mutant in (word[:-1], [(s, d, 4-f, q) for s, d, f, q in word],
                   [(s, d, f, -q if i == 1 else q) for i, (s, d, f, q) in enumerate(word)]):
        reject(lambda w=mutant: symbolic(w, 4, 5), 'algebraic mutation')
        controls += 1
    reject(lambda: list(new.instructions(tree, 1)), 'insufficient scratch')
    controls += 1
    bad = reference_word(tree, 2, unsafe_target=True)
    reject(lambda: nonlinear_checks(bad, 4), 'borrow root target')
    controls += 1
    require(all(s != d for s, d, _, _ in bad), 'negative control has accidental alias')
    require(nonlinear(bad, [-7, -4, -1, 2]) == [-7, 55, -51, 2], 'root-target counterexample changed')
    reject(lambda: free_nonlinear(bad, 4), 'free nonlinear target borrowing')
    controls += 1
    reject(lambda: list(new.instructions((1, 0), 1)), 'factor reorder')
    controls += 1
    for bad_prices, bad_budget in (([True], 0), ([0], 0), ([1], True), ([1], -1)):
        reject(lambda p=bad_prices, b=bad_budget: new.optimize(p, b), 'invalid input')
        controls += 1

    # Independent maximal leaf capacities from enumerated shapes and the proof recurrence.
    capacities = [1, 2]
    for b in range(2, 9):
        capacities.append(2 * capacities[-1] + capacities[-2])
    for n in range(1, 60):
        for b in range(6):
            feasible = n <= capacities[b]
            try:
                new.optimize([1] * n, b)
                got = True
            except ValueError:
                got = False
            require(got == feasible, 'capacity mismatch')
    return dict(status='PASS_ECHO_CONNECTOR_REUSE', seed=59,
                exhaustive_price_budget_cases=exhaustive, enumerated_trees=shapes,
                nonlinear_cases=nonlinear_cases, free_nonlinear_trees=shapes, rejected_controls=controls,
                target_borrow_counterexample={'initial': [-7,-4,-1,2], 'final': [-7,55,-51,2]},
                capacity_cases=59*6, capacities=capacities, witnesses=witnesses)


def main():
    result = certificate()
    text = json.dumps(result, indent=2, sort_keys=True) + '\n'
    import sys
    if sys.argv[1:] == ['--write']:
        (HERE / 'CERTIFICATE.json').write_text(text)
    elif not sys.argv[1:]:
        require((HERE / 'CERTIFICATE.json').read_text() == text, 'certificate mismatch')
    else:
        raise ValueError('usage: verify.py [--write]')
    print(result['status'] + ': ' + str(result['enumerated_trees']) + ' trees; '
          + str(result['exhaustive_price_budget_cases']) + ' exhaustive price/budget cases; '
          + 'n=59: 3456 -> 1712 calls, 6 -> 5 borrowed arrays')


if __name__ == '__main__':
    main()
