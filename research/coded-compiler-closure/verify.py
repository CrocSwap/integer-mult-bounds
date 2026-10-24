#!/usr/bin/env python3
"""Compiler arithmetic conditional on PR4940's declared p19 inventory.

No physical coded caller is admitted. Apache-2.0. Cinna Davis with substantial
OpenAI Codex assistance. The interval engines, strictification and outer ledger
retain their source attribution.
"""
import argparse
import ast
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TESTED, PLANNING_KAPPA = Q(17, 5000), Q(339999, 100000000)
V, LOG_POWER, THETA = 128, 140, Q(63, 64)
NATIVE = {1: 2201, 2: 412, 3: 510, 4: 127, 5: 40}
HELPERS = {4: 28, 7: 7, 8: 47, 9: 326}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def authenticate():
    for row in json.loads((HERE / 'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            path = ROOT / row['path']
            need(not path.is_symlink(), 'Source symlink: ' + row['path'])
            need(sha256(path.read_bytes()).hexdigest() == row['sha256'],
                 'Changed source: ' + row['path'])


def source_invoice():
    """Evaluate only the pinned rank model, without its discovery experiments."""
    path = ROOT / 'research/coded-reverse-controller/verify.py'
    tree = ast.parse(path.read_text(), filename=str(path))
    assignments = {n.targets[0].id: ast.literal_eval(n.value)
                   for n in tree.body if isinstance(n, ast.Assign)
                   and isinstance(n.targets[0], ast.Name)
                   and n.targets[0].id in ('H', 'P_NEW')}
    need(assignments == {'H': HELPERS, 'P_NEW': NATIVE}, 'Pinned source profiles')
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                and n.name == 'invoice')
    env = {'Counter': Counter, 'H': assignments['H']}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), 'exec'), env)
    return env['invoice'](19, 'I' * 9 + 'T' * 9,
                          frozenset(range(1, 38, 2)), assignments['P_NEW'])


def inventory():
    """Census intervals independently of the source invoice function."""
    targets, paid = Counter({153: 224}), Counter({1: 20 * 112})
    thick = set(range(1, 38, 2))
    for pair in range(1, 19):
        if pair <= 9:
            output, idle = range(0, 2 * pair + 1), range(0, 2 * pair)
        else:
            output, idle = range(2 * pair, 39), range(2 * pair + 1, 39)
        targets[1 + 8 * len(thick.intersection(output))] += 224
        paid[8 * len(thick.intersection(idle))] += 224
    need(not any(2 * j in thick for j in range(1, 19)), 'Middle IDLEs have zero rank')
    targets.update({r: 19 * n for r, n in HELPERS.items()})
    paid.update({r: 19 * n for r, n in NATIVE.items()})
    need((targets, paid) == source_invoice(), 'Independent/source inventory equality')
    receipt = json.loads((ROOT / 'research/native-center-free-code/EXPECTED.json').read_text())
    need(all({int(k): v for k, v in run['paid'].items()} == NATIVE
             for run in receipt['runs']), 'Both retained native orientations')
    selected = json.loads((ROOT / 'research/joint-helper-lattice/RESULT.json').read_text())
    need({int(k): n for k, n in selected['local_helpers'].items()} == HELPERS,
         'Source productive-helper inventory')
    need(sum(targets.values()) == 12008 and sum(paid.values()) == 68782,
         'All independent targets and paid calls counted')
    need(sum(r * n for r, n in targets.items()) == 265533
         and sum(r * n for r, n in paid.items()) == 263517, 'Raw mass census')
    return targets, paid


def independent_power(engine, rank, exponent):
    """Positive-series enclosure with rational endpoints, separate from the grid engine."""
    grid = 10 ** 40

    def rounded(a, b):
        return Q((a * grid).__floor__(), grid), Q((b * grid).__ceil__(), grid)

    if rank == 1 or exponent == 0:
        return Q(1), Q(1)
    low, high = engine.log_interval(rank)
    low, high = rounded(low * abs(exponent), high * abs(exponent))
    squares = 0
    while high >= Q(1, 2):
        low /= 2
        high /= 2
        squares += 1
    a, b = rounded(engine.exp_interval(low)[0], engine.exp_interval(high)[1])
    for _ in range(squares):
        a, b = rounded(a * a, b * b)
    return (1 / b, 1 / a) if exponent < 0 else (a, b)


def independent_checks(engine, E, targets, paid, ratios, eta):
    def moment(histogram, exponent):
        values = [(n, independent_power(engine, r, exponent))
                  for r, n in histogram.items()]
        return tuple(sum(n * interval[i] for n, interval in values) for i in (0, 1))

    def divide(a, b):
        return a[0] / b[1], a[1] / b[0]

    t = 1 - TESTED
    target = moment(targets, t)
    alpha = divide(moment(paid, t), target)
    cut = independent_power(engine, 20, Q(1, 5))
    gamma = divide(moment(paid, t + Q(1, 5)),
                   (cut[0] * target[0], cut[1] * target[1]))
    cut = independent_power(engine, 20, TESTED)
    delta = divide((Q(21 * sum(targets.values())),) * 2,
                   (cut[0] * target[0], cut[1] * target[1]))
    base = independent_power(engine, 153, -V * TESTED)
    independent_eta = ((1 - TESTED) * base[0], (1 - TESTED) * base[1])
    for label, a, b in [('alpha', alpha, ratios[0]), ('gamma', gamma, ratios[1]),
                         ('delta', delta, ratios[2]), ('eta', independent_eta, eta)]:
        need(max(a[0], b[0]) <= min(a[1], b[1]), 'Independent enclosure: ' + label)
    need(alpha[1] < Q(249, 250) and gamma[1] < Q(97, 100)
         and delta[1] < Q(97, 100) and independent_eta[0] > THETA ** LOG_POWER,
         'Independent strictification and capacity')
    return {name: E.display(x) for name, x in
            [('alpha', alpha), ('gamma', gamma), ('delta', delta), ('eta', independent_eta)]}


def height(step, power):
    def passes(j):
        return (step * j + 1) ** power < 2 ** j
    lo, hi = 1, 2
    while not passes(hi):
        lo, hi = hi, 2 * hi
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if passes(mid):
            hi = mid
        else:
            lo = mid
    need(passes(hi) and not passes(hi - 1), 'Adjacent integer-height crossing')
    return hi, step * hi


def parameters(kappa):
    gap = Q(1, 700000000)
    return {'kappa': kappa, 'tested_saving': kappa + 7 * gap,
            'complex_uniform_saving': kappa + 6 * gap, 'b': kappa + 5 * gap,
            'a': kappa + 4 * gap, 'q': kappa + 3 * gap, 'bit_saving': Q(17, 5000),
            'epsilon': 1 - gap, 'beta': 1 - 3 * gap, 'r0': gap / 10,
            'stop': gap, 'layout': gap, 'd': gap}


def outer_ledger(L, params):
    out = L.ledger(params)
    out['functional_checks']['actual_new_BIT_stock_sublinear'] = params['beta'] * Q(249, 250)
    return out


def failed(out):
    return [name for part in ('strict_checks', 'functional_checks')
            for name, value in out[part].items() if value <= 0]


def run():
    authenticate()
    targets, paid = inventory()
    E = load('research/higher-moment-strictification/verify.py', 'coded_compiler_intervals')
    other = load('research/kappa-rebuild/architecture/mixed_target_probe.py',
                 'coded_compiler_separate_intervals')
    L = load('research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py',
             'coded_compiler_outer')
    t = 1 - TESTED
    target = E.moment(targets, t)
    alpha = E.divide(E.moment(paid, t), target)
    gamma = E.divide(E.moment(paid, t + Q(1, 5)), E.mul(E.power(20, Q(1, 5)), target))
    delta = E.divide((Q(21 * sum(targets.values())),) * 2,
                     E.mul(E.power(20, TESTED), target))
    need(alpha[1] < Q(249, 250) and gamma[1] < Q(97, 100)
         and delta[1] < Q(97, 100), 'All three charged tail bounds')
    need(Q(97, 100) ** V < Q(1, 16), 'Exact 128-copy decay block')
    bound = 1 / (1 + Q(V, 250)) + 4 * Q(97, 100) ** V
    need(bound < Q(689, 756) < 1 and 20 ** 64 < 21 ** 63,
         'Paid completion, splitting and separation')
    eta = E.scale(E.power(153, -V * TESTED), t)
    need(2 * 20 ** (64 * V) <= 153 ** (63 * V), 'Shifted exit inequality')
    need(eta[0] > THETA ** LOG_POWER and eta[1] < THETA ** (LOG_POWER - 1),
         'Logarithmic power140 passes and139 fails at v128')
    need(E.power(153, V * TESTED)[1] < 2 ** LOG_POWER, 'Ordinary compiler base range')
    independent = independent_checks(other, E, targets, paid, (alpha, gamma, delta), eta)
    params = parameters(PLANNING_KAPPA)
    gap = TESTED - params['complex_uniform_saving']
    need(gap == Q(1, 700000000) and params['tested_saving'] == TESTED, 'Compiler gap grid')
    j, H = height(gap.denominator, LOG_POWER)
    need(H > 8 * V, 'Uniform ambient exceeds the product ambient')
    outer = outer_ledger(L, params)
    need(len(outer['strict_checks']) == 54 and len(outer['functional_checks']) == 4
         and not failed(outer), 'Complete 54+4 strict outer ledger')
    controls = {}
    half = E.power(153, -512 * TESTED)
    old_eta = E.scale(E.mul(half, half), t)
    need(old_eta[1] < THETA ** 1000, 'Inherited 1024/1000 capacity must fail')
    controls['inherited_1024_1000'] = 'eta below theta^1000'
    too_small = 1 / (1 + Q(64, 250)) + 4 * Q(97, 100) ** 64
    need(too_small > 1, 'Same conservative tail bound fails at64 copies')
    controls['tensor64_same_bounds'] = 'charged tail bound exceeds one'
    altered = Counter(paid)
    altered[1] -= 20 * 112
    need((targets, altered) != source_invoice(), 'Dropping the thin queries rejected')
    controls['omit_twenty_queries'] = 'inventory mismatch, 2240 H1 missing'
    for name, patch in [('BIT_cap', {'kappa': TESTED}),
                        ('old_BIT', {'bit_saving': Q(27, 10000)}),
                        ('closed_uniform', {'complex_uniform_saving': params['b']}),
                        ('closed_epsilon', {'epsilon': Q(1)})]:
        bad = parameters(TESTED) if name == 'BIT_cap' else dict(params, **patch)
        failures = failed(outer_ledger(L, bad))
        need(bool(failures), 'Rejected outer control: ' + name)
        controls[name] = failures
    return E.encoded({
        'status': 'PASS_CODED_P19_COMPILER_ARITHMETIC_ONLY',
        'new_admitted_kappa': None, 'planning_outer_endpoint': PLANNING_KAPPA,
        'tested_complex_saving': TESTED, 'uniform_complex_saving': params['complex_uniform_saving'],
        'native_thick_calls': 19, 'thin_queries': 20, 'pairs': 19, 'ambient_rank': 153,
        'targets': dict(sorted(targets.items())), 'paid': dict(sorted(paid.items())),
        'target_count': sum(targets.values()), 'paid_count': sum(paid.values()),
        'raw_rank_mass_surplus': 2016,
        'strictification': {'tensor_power': V, 'cutoff': 20, 'floor': 21, 'tail_offset': Q(1, 5),
                           'alpha': E.display(alpha), 'gamma': E.display(gamma),
                           'delta': E.display(delta), 'normalized_paid_upper': E.display((bound, bound)),
                           'simple_upper_bound': Q(689, 756)},
        'compiler': {'theta': THETA, 'logarithm_power': LOG_POWER, 'eta': E.display(eta),
                     'gap': gap, 'integer_test_exponent': j, 'height': H,
                     'rank_encoding': '2^' + str(H), 'word_materialized': False},
        'independent_intervals': independent, 'outer': outer, 'negative_controls': controls,
        'prerequisites': [
            'An all-width p19 physical coded caller realizes exactly this independent Gaussian inventory.',
            'Physical code/phase charts, inverse recoding, odd division and all helper returns are valid.',
            'Nonrecursive routing, owned storage, precision and fixed-tape work meet the retained ABI.',
            'The source ordinary BIT, integer compiler, analytic and exact-recovery premises apply.'
        ],
        'scope': 'Conditional compiler/outer arithmetic. No native replay, p19 physical word, supplier admission, selected update, or multiplication theorem.'
    })


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = run()
    path = HERE / 'RESULT.json'
    if args.write:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        need(json.loads(path.read_text()) == result, 'Committed arithmetic receipt')
    print(result['status'], 'height=' + str(result['compiler']['height']), 'no_new_kappa')
