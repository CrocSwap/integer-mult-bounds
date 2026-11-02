"""Build a binary tree of query suppliers and check every Laurent coefficient.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
The local interface and thin query are from Cinna Davis and the P104 authors.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
import json


def need(ok, message):
    if not ok:
        raise ValueError(message)


T2 = (1, 1)
T3 = (1, T2)
T4 = (T2, T2)
T7 = (T3, T4)
T8 = (T4, T4)
TREE = (T4, T7, T8)


def construct():
    """Emit all scalar steps, native wrappers, thin queries and whole idles."""
    stage = 0
    def label(tree):
        nonlocal stage
        if tree == 1:
            stage += 1
            return {'stage': stage, 'stages': [stage]}
        left, right = map(label, tree)
        return {'left': left, 'right': right,
                'stages': left['stages'] + right['stages']}
    roots = [label(tree) for tree in TREE]
    need(stage == 19, 'Nineteen independent native stages')
    events, targets, nodes = [], {}, []
    next_role = 2
    def emit(op, *args):
        events.append([op, *args])
    def supplier(tree, x, y, exponent):
        nonlocal next_role
        if 'stage' in tree:
            # q = Q^-1. Conjugation by Q^2 changes q to q^-1.
            if exponent == -1:
                emit('Q_POWER', x, -2)
            emit('SWAP', x, y)
            emit('LOCAL', tree['stage'], x, y)
            emit('SWAP', x, y)
            if exponent == -1:
                emit('Q_POWER', x, 2)
            return
        a, b = next_role, next_role + 1
        next_role += 2
        stages = tree['stages']
        nodes.append({'roles': [a, b], 'stages': stages,
                      'exponent': exponent})
        # R(x,y,a,b) = (x+b,a,x,y).
        emit('SWAP', x, b)
        emit('SWAP', y, a)
        emit('SWAP', a, b)
        emit('ADD', x, a, 1)
        # C(q): a <- a + q*(b-y). One paid query.
        emit('ADD', b, y, -1)
        emit('QUERY', a, b, -exponent)
        emit('ADD', b, y, 1)
        # S^-1 makes the A and B query planes the first two fields.
        emit('ADD', x, a, -1)
        emit('IDLE', a, b, stages)
        emit('SCALE', y, -1)
        supplier(tree['left'], y, x, -exponent)
        emit('SCALE', y, -1)
        supplier(tree['right'], x, y, exponent)
        emit('ADD', x, a, 1)
        # L(x,y,a,b) = (x,b,x-a,b-y).
        emit('SCALE', a, -1)
        emit('ADD', a, x, 1)
        emit('SWAP', y, b)
        emit('SCALE', b, -1)
        emit('ADD', b, y, 1)
        targets[a] = (-exponent, stages)
        targets[b] = (exponent, stages)
    supplier(roots[0], 0, 1, 1)
    emit('SCALE', 1, -1)
    supplier(roots[1], 1, 0, -1)
    emit('SCALE', 1, -1)
    supplier(roots[2], 0, 1, 1)
    emit('SWAP', 0, 1)
    emit('SCALE', 0, -1)
    targets[0], targets[1] = (1, list(range(1, 20))), (-1, list(range(1, 20)))
    need(next_role == 34 and len(targets) == 34, 'All main fields have one target')
    diagonal = [[targets[r][0], 0] +
                [int(s in targets[r][1]) for s in range(1, 20)]
                for r in range(34)]
    return {'schema': 'binary-query-tree/1', 'tree': TREE,
            'roles': 34, 'stages': 19, 'nodes': nodes,
            'events': events, 'diagonal': diagonal,
            'ambient_rank': 161}


def plus(dst, src, coefficient):
    for key, value in src.items():
        value = dst.get(key, 0) + coefficient * value
        if value:
            dst[key] = value
        else:
            dst.pop(key, None)


def shifted(row, term):
    return [{tuple(a+b for a, b in zip(key, term)): value
             for key, value in cell.items()} for cell in row]


def replay(word):
    """Use sparse rational polynomials for every input and output field."""
    n, width = word['roles'], 21
    zero = (0,) * width
    rows = [[{zero: Q(1)} if i == j else {} for j in range(n)]
            for i in range(n)]
    seen = []
    for event in word['events']:
        op = event[0]
        if op == 'ADD':
            _, dst, src, coefficient = event
            for a, b in zip(rows[dst], rows[src]):
                plus(a, b, coefficient)
        elif op == 'SCALE':
            _, dst, coefficient = event
            rows[dst] = [{key: coefficient*value for key, value in cell.items()}
                         for cell in rows[dst]]
        elif op == 'SWAP':
            _, a, b = event
            rows[a], rows[b] = rows[b], rows[a]
        elif op in ('LOCAL', 'QUERY'):
            if op == 'LOCAL':
                _, stage, src, dst = event
                exponent = -1
                seen.append(stage)
            else:
                _, dst, src, exponent = event
            term = (exponent,) + (0,) * 20
            for a, b in zip(rows[dst], shifted(rows[src], term)):
                plus(a, b, 1)
            if op == 'LOCAL':
                term = (0,) + tuple(int(s == stage) for s in range(20))
                for r in (src, dst):
                    rows[r] = shifted(rows[r], term)
        elif op == 'Q_POWER':
            _, r, exponent = event
            need(exponent in (-2, 2), 'Only even central powers are ordinary')
            rows[r] = shifted(rows[r], (exponent,) + (0,) * 20)
        elif op == 'IDLE':
            _, a, b, stages = event
            need(len(stages) == len(set(stages)), 'No repeated idle stage')
            term = (0,) + tuple(int(s in stages) for s in range(20))
            for r in (a, b):
                rows[r] = shifted(rows[r], term)
        else:
            raise ValueError('Unknown caller opcode: ' + op)
    need(sorted(seen) == list(range(1, 20)), 'Each native stage occurs once')
    expected = [[{tuple(word['diagonal'][i]): Q(1)} if i == j else {}
                 for j in range(n)] for i in range(n)]
    need(rows == expected, 'All exact Laurent endpoint coefficients')
    return {'inputs': n, 'coefficients': n*n,
            'native_stages': len(seen), 'events': len(word['events']),
            'event_sha256': sha256(json.dumps(word['events'], separators=(',', ':')).encode()).hexdigest()}


def controls(word):
    out = {}
    for label, opcode in [('unpaid_idle', 'IDLE'),
                          ('missing_translation', 'Q_POWER'),
                          ('missing_thin_query', 'QUERY')]:
        bad = deepcopy(word)
        del bad['events'][next(i for i, e in enumerate(bad['events']) if e[0] == opcode)]
        try:
            replay(bad)
        except ValueError as error:
            out[label] = str(error)
        else:
            raise ValueError('Changed caller accepted: ' + label)
    bad = deepcopy(word)
    event = next(e for e in bad['events'] if e[0] == 'QUERY')
    event[3] *= -1
    try:
        replay(bad)
    except ValueError as error:
        out['wrong_central_orientation'] = str(error)
    else:
        raise ValueError('Wrong central orientation accepted')
    return out


def formula_invoice(local):
    """Count the fixed tree without reading the emitted word."""
    targets = Counter({r: 19*n for r, n in local['helpers'].items()})
    paid = Counter({r: 19*n for r, n in local['paid'].items()})
    paid[1] += 16*104
    targets[153] += 208
    for size, count in {2: 9, 3: 1, 4: 4, 7: 1, 8: 1}.items():
        targets[1+8*size] += 208*count
        paid[8*size] += 208*count
    return targets, paid


if __name__ == '__main__':
    word = construct()
    print(replay(word))
    print(controls(word))
