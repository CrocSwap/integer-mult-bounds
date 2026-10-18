"""Offline exact certificate for space-capped dirty-echo planning.

No solver, network, floating arithmetic, or assertion-dependent checks.
Small-tree enumeration and an all-cuts recurrence do not import the planner.
The symbolic interpreter checks the emitted operations, including dirty inputs.
"""

import argparse
from collections import Counter
from fractions import Fraction as F
from functools import lru_cache
import hashlib
import importlib.util
from itertools import combinations, product
import json
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def compare_certificate(result, expected):
    # Trees are tuples in memory and JSON arrays on disk. Compare every field
    # after this representation-only normalization, not a selected summary.
    # Canonical JSON also distinguishes integer 1 from boolean true / float 1.0.
    need(json.dumps(result, sort_keys=True, separators=(',', ':')) ==
         json.dumps(expected, sort_keys=True, separators=(',', ':')),
         'exact certificate mismatch')


def sources():
    data = json.loads((ROOT/'SOURCES.json').read_text(encoding='utf-8'))
    for row in data['sources']:
        need(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'],
             'source pin: '+row['path'])
    selected = json.loads((ROOT/'../../certificates/selected-result.json').read_text())
    assembly = json.loads((ROOT/'../../research/community-k492-audit/pr626/replay/ASSEMBLY.json').read_text())
    need(selected['kappa'] == assembly['kappa'] == '51110230636731/31250000000000000',
         'selected context')
    return dict(base_commit=data['base_commit'], files=len(data['sources']),
                selected_kappa=selected['kappa'])


@lru_cache(None)
def shapes(n):
    """Enumerate ALL ordered rooted trees with n leaves and arities >= 2."""
    if n == 1:
        return (None,)
    result = []
    # A subset of n-1 gaps is exactly one ordered positive composition of n.
    for mask in range(1, 1 << (n-1)):
        cuts = (0,)+tuple(i for i in range(1, n) if mask & (1 << (i-1)))+(n,)
        for children in product(*(shapes(b-a) for a, b in zip(cuts, cuts[1:]))):
            result.append(children)
    return tuple(result)


def shape_bill(shape):
    """Different representation: leaves are anonymous; result is a coefficient vector."""
    if shape is None:
        return 0, (1,)
    rows = [shape_bill(x) for x in shape]
    coefficients = tuple(c*(2 if j == 0 or j+1 == len(rows) else 4)
                         for j, (_, cs) in enumerate(rows) for c in cs)
    return len(rows)-1+max(s for s, _ in rows), coefficients


def cuts_oracle(weights, cap):
    """Exact independent recurrence: explicitly enumerate each root cut set.

    Unlike planner.py, no prefix partition DP, capacity pruning, or stored
    witness is used. This is practical for the primary 15-factor instance.
    """
    visited = 0

    @lru_cache(None)
    def opt(left, right, budget):
        nonlocal visited
        if right-left == 1:
            return weights[left], 1
        answer = None
        for k in range(2, min(right-left, budget+1)+1):
            for middle in combinations(range(left+1, right), k-1):
                visited += 1
                ends = (left,)+middle+(right,)
                children = [opt(a, b, budget-k+1) for a, b in zip(ends, ends[1:])]
                if any(x is None for x in children):
                    continue
                coefficients = (2,)+(4,)*(k-2)+(2,)
                candidate = tuple(sum(m*row[j] for m, row in zip(coefficients, children))
                                  for j in (0, 1))
                if answer is None or candidate < answer:
                    answer = candidate
        return answer

    result = opt(0, len(weights), cap)
    return result, visited


def enumeration_check(planner):
    rng = random.Random(58)
    rows, comparisons, tree_count = [], 0, 0
    for n in range(1, 9):
        bills = [shape_bill(t) for t in shapes(n)]
        tree_count += len(bills)
        need(len(shapes(n)) == len(set(shapes(n))), 'duplicate exhaustive tree')
        # Four separately specified cost vectors; uniform and both orientations.
        costs = [(1,)*n, tuple(range(1, n+1)), tuple(range(n, 0, -1)),
                 tuple(rng.randrange(1, 59) for _ in range(n))]
        for weights in costs:
            for cap in range(n):
                candidates = [(sum(a*b for a, b in zip(weights, profile)), sum(profile))
                              for space, profile in bills if space <= cap]
                expected = min(candidates) if candidates else None
                if expected is None:
                    try:
                        planner.optimize(weights, cap)
                    except ValueError:
                        pass
                    else:
                        raise ValueError('accepted infeasible cap')
                else:
                    actual = planner.optimize(weights, cap)
                    need((actual['price'], actual['calls']) == expected, 'exhaustive optimum')
                    need(actual['scratch'] <= cap, 'exhaustive space')
                comparisons += 1
                rows.append((weights, cap, expected))
    need([len(shapes(i)) for i in range(1, 9)] == [1, 1, 3, 11, 45, 197, 903, 4279],
         'complete small-tree census')
    return dict(trees=tree_count, comparisons=comparisons, rows_sha256=digest(rows),
                domain='all reduced ordered rooted trees, n=1..8; four weight vectors; cap=0..n-1')


def plus(target, increment, sign):
    result = dict(target)
    for key, value in increment.items():
        result[key] = result.get(key, 0)+sign*value
        if not result[key]:
            del result[key]
    return result


def linear_state(steps, slots):
    state = [{((), i): 1} for i in range(slots)]
    for f, src, dst, sign in steps:
        need(src != dst and 0 <= src < slots and 0 <= dst < slots, 'linear array address')
        state[dst] = plus(state[dst], {((f,)+word, var): c
                                     for (word, var), c in state[src].items()}, sign)
    return state


def linear_check(steps, n, slots, sign=1):
    expected = [{((), i): 1} for i in range(slots)]
    expected[1][(tuple(reversed(range(n))), 0)] = sign
    need(linear_state(steps, slots) == expected, 'noncommutative endpoint/restoration')


def nonlinear_check(steps, inverse, slots):
    # Opaque deterministic function atoms on canonical additive source values.
    # No distributivity through a function is used.
    state = [{i: 1} for i in range(slots)]
    initial = [dict(x) for x in state]
    atoms, dependencies = {}, {i: {i} for i in range(slots)}

    def execute(program):
        for factor, src, dst, sign in program:
            need(src != dst and 0 <= src < slots and 0 <= dst < slots, 'nonlinear array address')
            key = factor, tuple(sorted(state[src].items()))
            if key not in atoms:
                index = slots+len(atoms)
                atoms[key] = index
                dependencies[index] = set().union(*(dependencies[x] for x in state[src]))
            state[dst] = plus(state[dst], {atoms[key]: 1}, sign)

    execute(steps)
    need(state[0] == initial[0] and state[2:] == initial[2:], 'nonlinear restoration')
    change = plus(state[1], initial[1], -1)
    need(all(1 not in dependencies[atom] for atom in change), 'target-independent increment')
    execute(inverse)
    need(state == initial, 'nonlinear exact inverse')
    return len(atoms)


def word_check(planner, plan, n):
    forward = list(planner.word(plan['tree']))
    backward = list(planner.word(plan['tree'], -1))
    need(backward == [(f, s, t, -q) for f, s, t, q in reversed(forward)], 'inverse chronology')
    counts = Counter(f for f, _, _, _ in forward)
    need([counts[i] for i in range(n)] == plan['occurrences'], 'literal child invoice')
    peak = max(max(s, t) for _, s, t, _ in forward)-1
    need(peak == plan['scratch'], 'literal workspace peak')
    slots = 3+plan['scratch']  # extra untouched spectator
    linear_check(forward, n, slots)
    linear_check(backward, n, slots, -1)
    atoms = nonlinear_check(forward, backward, slots)
    return dict(factors=n, calls=len(forward), scratch=peak, nonlinear_atoms=atoms,
                word_sha256=digest(forward))


def uniform_checks(planner, ternary, echo):
    records, symbolic = [], []
    for n in range(1, 33):
        floor = (n-1).bit_length()
        for cap in sorted({floor, min(n-1, floor+1)}):
            plan = planner.optimize([1]*n, cap)
            records.append(dict(factors=n, cap=cap, **plan))
            symbolic.append(word_check(planner, plan, n))
    # Primary full Pareto row for radix 16. No claim that radix 59 is a kernel.
    primary = []
    for cap in range(4, 15):
        plan = planner.optimize([1]*15, cap)
        oracle, visited = cuts_oracle((1,)*15, cap)
        need(oracle == (plan['price'], plan['calls']), 'primary all-cuts optimum')
        primary.append(dict(cap=cap, **plan, oracle_root_partitions=visited))
    row = next(x for x in primary if x['cap'] == 5)
    need(row['calls'] == 152 and row['scratch'] == 5, 'primary exact result')
    balanced_calls, balanced_space = ternary.resources(15)
    need((balanced_calls, balanced_space) == (160, 5), 'PR689 primary baseline')
    need(len(list(ternary.word(15))) == balanced_calls, 'PR689 literal baseline')
    old_space, old_calls = echo.resources(15, 3)
    need((old_calls, old_space) == (208, 5), 'PR673 primary baseline')
    need(len(list(echo.instructions(0, 15, 0, 1, 2, 3))) == old_calls, 'PR673 literal baseline')
    extra = planner.optimize([1]*58, 8)
    symbolic.append(word_check(planner, extra, 58))
    return dict(domain='n=1..32 at minimum feasible cap and one extra; n=15 caps 4..14; n=58 cap 8',
                resource_rows=records, primary_pareto=primary,
                pr689_primary=dict(calls=balanced_calls, scratch=balanced_space),
                pr673_primary=dict(calls=old_calls, scratch=old_space),
                n58=extra, symbolic=symbolic)


def ceil_log2_fraction(x):
    need(x > 0, 'positive logarithm argument')
    k = x.numerator.bit_length()-x.denominator.bit_length()
    while F(2)**k < x:
        k += 1
    while F(2)**(k-1) >= x:
        k -= 1
    return k


def precision(calls, beta, r, magnitude, target):
    a = F(13*(r+1))/beta**3
    G = 2+F(r)/beta
    bits = max(ceil_log2_fraction(a), ceil_log2_fraction(2/beta**2),
               target+1+ceil_log2_fraction(calls*a*(magnitude+1))
               +(calls-1)*ceil_log2_fraction(G))
    bound = calls*a*(magnitude+1)*G**(calls-1)/2**bits
    need(a/2**bits <= 1 and F(1, 2**bits) <= beta**2/2, 'leaf precision conditions')
    need(bound <= F(1, 2**(target+1)), 'complete word error bound')
    return bits, bound


def rounded_case(planner, leaf_module, tree, factors, beta, r, length, direction, dirt, q=None):
    c = leaf_module.c
    bill = planner.invoice(tree, [1]*len(factors))
    arrays = [[(F(2+j+i, 8), F(3-j+2*i, 8)) for i in range(length)]
              for j in range(3+bill['scratch'])]
    for j in range(2, len(arrays)):
        arrays[j] = [(a+dirt, b-dirt) for a, b in arrays[j]]
    initial = [x[:] for x in arrays]
    D = max(abs(a)+abs(b) for row in arrays for a, b in row)
    bits, bound = precision(bill['calls'], beta, r, D, 64)
    units = [c.ONE, (F(0), F(1)), (F(3, 5), F(4, 5))]
    values = [units[i % len(units)] for i in range(length)]

    class Phases:
        reads = 0

        def __getitem__(self, i):
            self.reads += 1
            return values[i]

    phases = Phases()
    stats = dict(leaves=0, scalar_steps=0)

    def leaf(src, dst, factor, sign):
        leaf_module.leaf(src, dst, factor, phases, beta, bits, direction, sign, stats)

    planner.compose(tree, arrays[0], arrays[1], factors, arrays[2:], leaf, read_only=(values,))
    need(arrays[0] == initial[0] and arrays[2:] == initial[2:], 'rounded dirty restoration')
    reads = sum(n*((6 if f[0] else 5)*length-2) for f, n in zip(factors, bill['occurrences']))
    need(phases.reads == reads and stats == dict(leaves=bill['calls'], scalar_steps=3*length*bill['calls']),
         'actual phase-access and traversal invoice')
    exact = (leaf_module.exact_operator(initial[0], factors, values, direction) if q is None else
             leaf_module.w.solve(leaf_module.w.matrix(q, values, direction), initial[0]))
    net = [c.sub(v, start) for v, start in zip(arrays[1], initial[1])]
    need(all(c.norm2(c.sub(v, e)) <= bound**2 for v, e in zip(net, exact)), 'rounded dense comparison')
    output_hash = digest([[str(a), str(b)] for a, b in net])
    planner.compose(tree, arrays[0], arrays[1], factors, arrays[2:], leaf, -1, read_only=(values,))
    need(arrays == initial, 'rounded exact inverse')
    need(phases.reads == 2*reads and stats['leaves'] == 2*bill['calls'], 'inverse invoice')
    return dict(factors=len(factors), length=length, direction=direction, dirt=dirt,
                calls=bill['calls'], scratch=bill['scratch'], phase_reads=reads,
                lift_loop_visits=3*length*bill['calls'], working_bits=bits,
                execution_target_bits=64, output_sha256=output_hash)


def rounded_checks(planner, ternary, old):
    generic = []
    for n in (1, 2, 3, 5, 8, 15):
        plan = planner.optimize([1]*n, min(n-1, (n-1).bit_length()+1))
        factors = [(i % 2 == 0, (F(1, 4), F((-1)**i, 8)), F(3 if i == 0 else 1))
                   for i in range(n)]
        for length, direction, dirt in product((1, 3), (-1, 1), (-7, 5)):
            generic.append(rounded_case(planner, old, plan['tree'], factors, F(1, 2), 3,
                                        length, direction, dirt))
    fixture = next(x for x in json.loads((ROOT/'vendor/pr628/FACTORS.json').read_text())
                   if x['radix'] == 16 and x['embedding'] == 1)
    certified = old.w.k.certify(fixture)
    factors = [(inside, b, F(16 if i == 0 else 1))
               for i, (inside, b) in enumerate(certified['factors'])]
    # The weights are the ACTUAL leaf phase reads on a length-five cycle.
    weights = [(6 if inside else 5)*5-2 for inside, _, _ in factors]
    plan = planner.optimize(weights, 5)
    oracle, visited = cuts_oracle(tuple(weights), 5)
    need(oracle == (plan['price'], plan['calls']), 'weighted all-cuts optimum')
    balanced = Counter(f for f, _, _, _ in ternary.word(15))
    baseline_reads = sum(weights[i]*balanced[i] for i in range(15))
    uniform = planner.optimize([1]*15, 5)
    kernel = []
    for label, tree in (('uniform', uniform['tree']), ('phase_weighted', plan['tree'])):
        for direction, dirt in product((-1, 1), (-7, 5)):
            # The independent polynomial reference uses the full five-cycle matrix.
            row = rounded_case(planner, old, tree, factors, certified['beta'], 16, 5,
                               direction, dirt, certified['q'])
            row['objective'] = label
            kernel.append(row)
    return dict(generic=generic, kernel=kernel,
                weighted=dict(weights=weights, **plan, pr689_phase_reads=baseline_reads,
                              uniform_phase_reads=sum(a*b for a,b in zip(weights, uniform['occurrences'])),
                              oracle_root_partitions=visited,
                              symbolic=word_check(planner, plan, len(factors))),
                kernel_scope='radix 16 embedding 1, length 5, both directions, two arbitrary-dirt fixtures; represented-factor polynomial and inherited root certificate')


def negative_controls(planner):
    rejected = []

    def reject(name, function):
        try:
            function()
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('accepted negative control: '+name)

    plan = planner.optimize([1]*15, 5)
    steps = list(planner.word(plan['tree']))
    slots = 3+plan['scratch']
    for index in range(len(steps)):
        reject('omit_'+str(index), lambda i=index: linear_check(steps[:i]+steps[i+1:], 15, slots))
        f, s, t, q = steps[index]
        mutant = steps[:index]+[(f,s,t,-q)]+steps[index+1:]
        reject('sign_'+str(index), lambda m=mutant: linear_check(m, 15, slots))
    reject('factor_order', lambda: linear_check([(14-f,s,t,q) for f,s,t,q in steps], 15, slots))
    reject('inverse_order', lambda: nonlinear_check(steps, [(f,s,t,-q) for f,s,t,q in steps], slots))
    reject('scratch_alias', lambda: linear_check([(f,2 if s==3 else s,2 if t==3 else t,q)
                                                 for f,s,t,q in steps], 15, slots))
    for name, weights, cap in [('empty',[],1), ('zero',[0],0), ('negative',[-1],0),
                               ('bool_weight',[True],0), ('bool_cap',[1],True),
                               ('negative_cap',[1],-1), ('infeasible',[1]*15,3)]:
        reject(name, lambda w=weights,c=cap: planner.optimize(w,c))
    reject('missing_factor', lambda: planner.invoice((0,1), [1,1,1]))
    reject('reordered_factor', lambda: planner.invoice((1,0), [1,1]))
    reject('unary_node', lambda: planner.invoice((0,), [1]))
    called = []

    def admission(**kw):
        args = dict(tree=(0,1,2), source=[1], target=[2], factors=[0,1,2],
                    scratch=[[3],[4]], leaf=lambda *a: called.append(a))
        args.update(kw)
        planner.compose(**args)

    same = [1]
    for name, kw in [('source_target',dict(source=same,target=same)),
                     ('source_scratch',dict(source=same,scratch=[same,[4]])),
                     ('target_scratch',dict(target=same,scratch=[same,[4]])),
                     ('scratch_pair',dict(scratch=[same,same])),
                     ('phase_alias',dict(source=same,read_only=(same,))),
                     ('short_scratch',dict(scratch=[[1]])), ('length',dict(target=[1,2])),
                     ('sign',dict(sign=0)), ('bool_sign',dict(sign=True))]:
        reject(name, lambda kw=kw: admission(**kw))
    need(not called, 'admission must reject before mutation')
    return dict(rejected_count=len(rejected), rejected=rejected)


def verify():
    bindings = sources()
    planner = module('planner', ROOT/'planner.py')
    ternary = module('ternary_baseline', ROOT/'vendor/pr689/ternary.py')
    echo = module('echo_baseline', ROOT/'vendor/pr673/echo.py')
    old = module('rounded_leaf', ROOT/'vendor/pr628/dirty.py')
    result = dict(status='PASS_SPACE_CAPPED_DIRTY_ECHO', sources=bindings)
    result['enumeration'] = enumeration_check(planner)
    print('PASS exhaustive small-tree oracle', flush=True)
    result['uniform'] = uniform_checks(planner, ternary, echo)
    print('PASS primary all-cuts optimum, literal words and symbolic restoration', flush=True)
    result['controls'] = negative_controls(planner)
    result['rounded'] = rounded_checks(planner, ternary, old)
    print('PASS weighted optimum, rounded leaves and charged phase accesses', flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path, help='write a new certificate; never overwrite')
    args = parser.parse_args()
    if args.write:
        need(not args.write.exists(), 'output already exists')
    result = verify()
    if args.write:
        with args.write.open('x', encoding='utf-8', newline='\n') as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        compare_certificate(result, json.loads((ROOT/'EXPECTED.json').read_text()))
    print('PASS_SPACE_CAPPED_DIRTY_ECHO calls=160->152 scratch=5 no_new_kappa')


if __name__ == '__main__':
    main()
