#!/usr/bin/env python3
"""Exact bounded replay of a clean root checkpoint; see README and PROOF.

No third-party dependencies. Checks remain active under python -O.
"""
import argparse
import ast
from collections import Counter
from functools import lru_cache
import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent


def module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    out = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(out)
    return out


cp = module('checkpoint')
need = cp.need


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sources():
    record = json.loads((HERE / 'SOURCE.json').read_text())
    for entry in record['sources']:
        data = (HERE / entry['path']).read_bytes()
        need(digest(data) == entry['sha256'], 'source SHA256: ' + entry['path'])
        blob = b'blob ' + str(len(data)).encode() + b'\0' + data
        need(hashlib.sha1(blob).hexdigest() == entry['git_blob'],
             'source Git blob: ' + entry['path'])
    return record


def inverse(word):
    return [(f, x, y, -s) for f, x, y, s in reversed(word)]


def reference(fs, x, y, scratch):
    if len(fs) == 1:
        return [(fs[0], x, y, 1)]
    k = len(fs) // 2
    a = reference(fs[:k], x, scratch[0], scratch[1:])
    b = reference(fs[k:], scratch[0], y, scratch[1:])
    return a + b + inverse(a) + inverse(b)


def pinned_namespace():
    tree = ast.parse((HERE / 'vendor/pr628-dirty.py').read_text())
    defs = [n for n in tree.body if isinstance(n, ast.FunctionDef)
            and n.name == 'compose']
    need(len(defs) == 1, 'unique pinned dispatcher')
    ns = {'c': SimpleNamespace(need=need, norm2=lambda t: t*t, ZERO=0)}
    exec(compile(ast.Module(body=defs, type_ignores=[]), 'pinned-compose', 'exec'), ns)
    return ns


def trace(ns, n, k, sign=1, mutation=None):
    p = cp.plan(n, k)
    arrays = [[0] for _ in range(3 + p['dirty_arrays'])]
    if mutation == 'dirty':
        arrays[2][0] = 1
    if mutation == 'source_alias':
        arrays[2] = arrays[0]
    if mutation == 'target_alias':
        arrays[-1] = arrays[1]
    if mutation == 'shortage':
        arrays.pop()
    phases = [1]
    if mutation and mutation.startswith('phase_alias_'):
        role = int(mutation.rsplit('_', 1)[1])
        phases = arrays[role]
        phases[:] = [1]
    labels = {id(a): i for i, a in enumerate(arrays)}
    word = []
    def leaf(x, y, f, phases, beta, bits, d, s, stats):
        word.append((f, labels[id(x)], labels[id(y)], s))
    ns['leaf'] = leaf
    cp.compose_clean(ns['compose'], ns['c'], arrays[0], arrays[1],
                     list(range(n)), arrays[2], arrays[3:], phases, 1, 1, 1,
                     split=k, sign=sign)
    return word


def initial(size, clean=True):
    return [{} if clean and i == 2 else {(i, ()): 1} for i in range(size)]


def replay(word, state):
    """Free noncommutative linear operators on independent initial columns."""
    result = [dict(v) for v in state]
    for f, x, y, s in word:
        for (variable, monomial), a in list(result[x].items()):
            key = variable, (f,) + monomial
            value = result[y].get(key, 0) + s * a
            if value:
                result[y][key] = value
            else:
                result[y].pop(key, None)
    return result


@lru_cache(None)
def recursive_count(n):
    return 1 if n == 1 else 2 * (recursive_count(n//2) + recursive_count(n-n//2))


def run():
    src = sources()
    ns = pinned_namespace()
    plans, candidates = [], 0
    for n in range(2, 257):
        need(recursive_count(n) == cp.dirty_count(n), 'inherited count')
        costs = [2*recursive_count(k)+recursive_count(n-k) for k in range(1, n)]
        candidates += len(costs)
        optimum = min(costs)
        winners = [k for k in range(1, n) if costs[k-1] == optimum]
        p = cp.plan(n)
        need(p['optimal_splits'] == [winners[0], winners[-1]], 'optimal interval')
        need(winners == list(range(winners[0], winners[-1]+1)), 'no hidden gaps')
        need(p['leaf_calls'] == optimum, 'minimum cost')
        need(1+p['dirty_arrays'] == p['balanced_dirty_arrays'], 'total array count')
        need(5*optimum >= 3*recursive_count(n), 'three-fifths bound')
        need(4*optimum <= 3*recursive_count(n), 'three-quarters bound')
        plans.append(p)
    algebra = []
    cases = [(n, k) for n in range(2, 33) for k in range(1, n)]
    cases += [(54, cp.plan(54)['split']), (63, cp.plan(63)['split'])]
    for n, k in cases:
        p = cp.plan(n, k)
        size = 3 + p['dirty_arrays']
        word = trace(ns, n, k)
        a = reference(list(range(k)), 0, 2, list(range(3, size)))
        b = reference(list(range(k, n)), 2, 1, list(range(3, size)))
        need(word == a+b+inverse(a), 'pinned vs independent compiler')
        need(len(word) == p['leaf_calls'], 'all forward and reverse calls priced')
        state = initial(size)
        expected = initial(size)
        expected[1][(0, tuple(reversed(range(n))))] = 1
        actual = replay(word, state)
        need(actual == expected, 'noncommuting product / all dirty columns restored')
        neg = trace(ns, n, k, -1)
        need(neg == inverse(word), 'inverse chronology')
        need(replay(neg, actual) == state, 'exact inverse')
        need(replay(a+b+inverse(a)+inverse(b), state) == actual,
             'same-split omitted zero-source cancellation')
        # Nonuniform leaf weights are recounted from the actual emitted word;
        # the unit-weight optimum is not asserted for this weighted bill.
        counts = Counter(f for f, _, _, _ in word)
        wa = sum(1+f%7 for f, _, _, _ in a)
        wb = sum(1+f%7 for f, _, _, _ in b)
        need(sum(counts[f]*(1+f%7) for f in counts) == 2*wa+wb, 'weighted bill')
        algebra.append(dict(n=n, split=k, leaves=len(word),
                            trace_sha256=digest(json.dumps(word).encode())))
    controls = []
    for name in ('dirty', 'source_alias', 'target_alias', 'shortage',
                 'phase_alias_0', 'phase_alias_1', 'phase_alias_2',
                 'phase_alias_3', 'phase_alias_4'):
        try:
            trace(ns, 7, 3, mutation=name)
        except ValueError as error:
            if name.startswith('phase_alias_'):
                need(str(error) == 'phase array must be distinct', 'wrong phase rejection')
            controls.append(name)
        else:
            raise ValueError('accepted interface control: ' + name)
    n, k = 7, 3
    p = cp.plan(n, k)
    size = 3+p['dirty_arrays']
    a = reference(list(range(k)), 0, 2, list(range(3, size)))
    b = reference(list(range(k, n)), 2, 1, list(range(3, size)))
    word = a+b+inverse(a)
    state = initial(size)
    good = replay(word, state)
    mutants = {
        'omitted_checkpoint_restoration': a+b,
        'wrong_product_order': [(n-1-f,x,y,s) for f,x,y,s in word],
    }
    for name, mutant in mutants.items():
        actual = replay(mutant, state)
        need(actual != good, 'vacuous mutation: ' + name)
        controls.append(name)
    # An even two-factor product detects same-order sign inversion. For an
    # odd-length ideal product that mutation can accidentally give the inverse.
    short_word = trace(ns, 2, 1)
    short_state = initial(3)
    short_good = replay(short_word, short_state)
    wrong_inverse = [(f,x,y,-s) for f,x,y,s in short_word]
    need(replay(wrong_inverse, short_good) != short_state, 'wrong inverse control')
    controls.append('wrong_inverse_chronology')
    need(replay(word, initial(size, clean=False))[1] != good[1], 'dirty counterexample')
    controls.append('dirty_checkpoint_leaks_to_target')
    need(len(a)+len(b) != len(word), 'unpaid inverse control')
    controls.append('unpaid_inverse_count')
    rounded = module('rounded_check').run()
    return dict(status='PASS_CLEAN_CHECKPOINT', assignment_seed=54,
                base_commit=src['base_commit'], source_pins=src['sources'],
                root_search=dict(min_n=2, max_n=256, candidates=candidates,
                                 stopping_rule='all interior root splits; balanced subtrees'),
                plans=plans, noncommutative_cases=algebra,
                controls=controls, rounded=rounded,
                selected=cp.plan(54),
                scope='Paid clean root only; no new kappa, global scheduler optimum, or full theorem')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', type=Path, help='write a fresh receipt instead of checking EXPECTED')
    args = parser.parse_args()
    result = run()
    if args.write:
        args.write.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        need(result == json.loads((HERE/'EXPECTED.json').read_text()), 'complete certificate mismatch')
    print('PASS_CLEAN_CHECKPOINT: 32640 splits; 498 noncommutative cases; '
          'n=54: 3136 -> 2112 leaves, 1 clean + 5 dirty arrays')


if __name__ == '__main__':
    main()
