"""Independent exact caller audit, requiring only the standard library.

Binary suppliers and the dual-pair retirement method retain the authors
and credits recorded in source6702 and PR6545.  The changed root and its
literal word are independently checked here using a separately written
Fraction Laurent-ring engine.  No author constructor, replay, algebra,
native implementation, or saved mathematical result is imported.
OpenAI Codex assistance. Apache-2.0.

Every fresh stage remains a distinct formal variable; only q^4=1 is
imposed. This does not replace native absolute-phase or physical checks,
discharge framework assumptions, or establish scientific admission.
"""
from argparse import ArgumentParser
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ZERO = F(0), F(0)
ONE = F(1), F(0)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def complex_product(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def plus(a, b, factor=ONE):
    out = dict(a)
    for monomial, coefficient in b.items():
        z = complex_product(coefficient, factor)
        old = out.get(monomial, ZERO)
        z = old[0] + z[0], old[1] + z[1]
        if z == ZERO:
            out.pop(monomial, None)
        else:
            out[monomial] = z
    return out


def scale(a, scalar):
    scalar = F(scalar)
    return {k: complex_product(v, (scalar, F(0))) for k, v in a.items()} if scalar else {}


def shift(a, q=0, stages=(), degree=1):
    out = {}
    for monomial, coefficient in a.items():
        key = list(monomial)
        key[0] = (key[0] + q) % 4
        for stage in stages:
            key[stage] += degree
        out = plus(out, {tuple(key): coefficient})
    return out


def lam(a, sign):
    need(sign in (-1, 1), 'Literal normalization sign')
    return plus(plus({}, a, (F(1, 2), F(sign, 2))),
                shift(a, q=2), (F(1, 2), F(-sign, 2)))


def normalized_central(a):
    return lam(shift(a, q=-1), 1)


def forward(vector, event):
    op = event[0]
    if op == 'ADD':
        vector[event[1]] = plus(vector[event[1]], vector[event[2]], (F(event[3]), F(0)))
    elif op == 'SWAP':
        vector[event[1]], vector[event[2]] = vector[event[2]], vector[event[1]]
    elif op == 'SCALE':
        vector[event[1]] = scale(vector[event[1]], event[2])
    elif op == 'LAMBDA':
        vector[event[1]] = lam(vector[event[1]], event[2])
    elif op == 'Q_POWER':
        vector[event[1]] = shift(vector[event[1]], q=event[2])
    elif op == 'QUERY':
        vector[event[1]] = plus(vector[event[1]], shift(vector[event[2]], q=event[3]))
    elif op == 'LOCAL':
        _, stage, src, dst = event
        vector[dst] = plus(vector[dst], shift(vector[src], q=-1))
        for owner in (src, dst):
            vector[owner] = shift(vector[owner], stages=[stage])
    elif op in ('IDLE', 'IDLE_ONE'):
        owners, stages = (event[1:3], event[3]) if op == 'IDLE' else ([event[1]], event[2])
        need(len(stages) == len(set(stages)), 'Distinct actual idle axes')
        for owner in owners:
            vector[owner] = shift(vector[owner], stages=stages)
    else:
        raise ValueError('Unknown event ' + op)


def right_action(row, event):
    """Right multiplication by a forward event; never an inverse oracle."""
    op = event[0]
    if op == 'ADD':
        row[event[2]] = plus(row[event[2]], row[event[1]], (F(event[3]), F(0)))
    elif op == 'SWAP':
        row[event[1]], row[event[2]] = row[event[2]], row[event[1]]
    elif op == 'SCALE':
        row[event[1]] = scale(row[event[1]], event[2])
    elif op == 'LAMBDA':
        row[event[1]] = lam(row[event[1]], event[2])
    elif op == 'Q_POWER':
        row[event[1]] = shift(row[event[1]], q=event[2])
    elif op == 'QUERY':
        row[event[2]] = plus(row[event[2]], shift(row[event[1]], q=event[3]))
    elif op == 'LOCAL':
        _, stage, src, dst = event
        for owner in (src, dst):
            row[owner] = shift(row[owner], stages=[stage])
        row[src] = plus(row[src], shift(row[dst], q=-1))
    elif op in ('IDLE', 'IDLE_ONE'):
        owners, stages = (event[1:3], event[3]) if op == 'IDLE' else ([event[1]], event[2])
        need(len(stages) == len(set(stages)), 'Distinct actual idle axes')
        for owner in owners:
            row[owner] = shift(row[owner], stages=stages)
    else:
        raise ValueError('Unknown event ' + op)


def vector(n, one, entries):
    out = [{} for _ in range(n)]
    for role, coefficient in entries.items():
        out[role] = scale(one, coefficient)
    return out


def dot(left, right):
    out = {}
    for a, b in zip(left, right):
        for monomial, coefficient in a.items():
            term = shift(b, q=monomial[0])
            for stage, degree in enumerate(monomial[1:], 1):
                if degree:
                    term = shift(term, stages=[stage], degree=degree)
            out = plus(out, term, coefficient)
    return out


def check_pair(base, witness):
    n = base['roles']
    one = {(0,) * (base['stages'] + 1): ONE}
    entries = {'a': {1: 1, 20: -1, 21: 1},
               'b': {0: -2, 2: 2, 20: -2, 21: -1},
               'c': {20: 1, 4: -1}, 'd': {4: -1, 21: -1}}
    for name, value in entries.items():
        need({int(k): F(v) for k, v in witness[name].items()} == value, 'Declared scalar pair ' + name)
    a, b, c, d = [vector(n, one, entries[name]) for name in ('a', 'b', 'c', 'd')]
    need(dot(a, b) == dot(c, d) == one, 'Both scalar dual pairings are one')
    need(witness['pivot'] == 4 and witness['fresh'] == n, 'Independent original pivot and additional fresh role')
    for name, left, right in [('boundary', c, d), ('middle', a, b)]:
        col = deepcopy(right)
        for event in witness[name]:
            forward(col, event)
        need(col == vector(n, one, {4: 1}), 'Declared basis column ' + name)
        row = vector(n, one, {4: 1})
        for event in reversed(witness[name]):
            right_action(row, event)
        need(row == left, 'Declared basis row ' + name)
    cut = witness['cut_after']
    need(cut == 353 and base['events'][cut] == ['LAMBDA', 20, 1], 'Actual normalized query cut')
    col = deepcopy(d)
    for event in base['events'][:cut + 1]:
        forward(col, event)
    need(col == [normalized_central(p) for p in b], 'Actual prefix P d = S b')
    row = deepcopy(a)
    for event in reversed(base['events'][:cut + 1]):
        right_action(row, event)
    need(row == [normalized_central(p) for p in c], 'Actual prefix a P = S c, without an inverse inference')
    return {'cut_after': cut, 'input_pairing': '1', 'cut_pairing': '1',
            'column_identity': 'P d = S b', 'row_identity': 'a P = S c',
            'fresh_variables': base['stages'], 'unpaid_stage_factors_in_bases': False}


def check_word(word):
    n = word['roles']
    one = {(0,) * (word['stages'] + 1): ONE}
    need((n, word['stages'], len(word['events'])) == (35, 18, 586), 'Exact literal independent-input census')
    need(all(t[1] == 0 for t in word['diagonal']), 'No ignored stage-zero factor')
    locals_seen = [e[1] for e in word['events'] if e[0] == 'LOCAL']
    need(sorted(locals_seen) == list(range(1, word['stages'] + 1)), 'Every distinct native stage exactly once')
    for source in range(n):
        x = vector(n, one, {source: 1})
        for event in word['events']:
            forward(x, event)
        d = word['diagonal'][source]
        target = {(d[0] % 4, *d[2:]): ONE}
        expected = [{} for _ in range(n)]
        expected[source] = target
        need(x == expected, 'All-input exact column ' + str(source))
    return {'independent_inputs': n, 'coefficient_equalities': n * n,
            'events': len(word['events']), 'formal_fresh_variables': word['stages']}


def rejected(action):
    try:
        action()
    except ValueError as error:
        return str(error)
    raise ValueError('Invalid control accepted')


def run(root):
    paths = {name: root / filename for name, filename in (
        ('base', 'CONTROLLER-UNRETIRED.json'), ('word', 'CONTROLLER.json'), ('witness', 'WITNESS.json'))}
    base, word, witness = [json.loads(paths[name].read_bytes()) for name in ('base', 'word', 'witness')]
    pair = check_pair(base, witness)
    result = check_word(word)
    controls = {}
    bad = deepcopy(base)
    bad['events'][353][-1] = -1
    controls['wrong_cut_normalizer'] = rejected(lambda: check_pair(bad, witness))
    for label, index in [('input_basis', 0), ('middle_handoff', witness['handoff_after']),
                         ('final_return', len(word['events']) - 1)]:
        bad = deepcopy(word)
        # Keep the event count unchanged: erase only the actual ordinary action.
        bad['events'][index] = ['SCALE', 0, '1']
        controls[label] = rejected(lambda: check_word(bad))
    bad = deepcopy(word)
    bad['diagonal'][-1][0] = -1
    controls['unearned_fresh_rank_one'] = rejected(lambda: check_word(bad))
    return {'status': 'PASS_INDEPENDENT_NEW_ROOT_DUAL_PAIR_AND_ALL_INPUTS',
            'inputs_sha256': {name: sha256(path.read_bytes()).hexdigest() for name, path in paths.items()},
            'pair': pair, 'word': result, 'controls': controls,
            'scope': 'Independent exact logical caller only. No native/all-width phase replay, no framework discharge or admission claim.'}


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--root', type=Path, default=HERE)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = run(args.root)
    raw = json.dumps(result, sort_keys=True, indent=2) + '\n'
    destination = args.root / 'INDEPENDENT.json'
    if args.write:
        destination.write_text(raw)
    else:
        need(destination.read_text() == raw, 'Frozen independent receipt')
    print(result['status'])
