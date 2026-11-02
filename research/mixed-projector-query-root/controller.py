"""Emit the mixed projector root and its paid binary query suppliers.

The binary child emitter is adapted from PR6348. Cinna Davis supplies the
native and thin-query interface. Ali Romman with OpenAI Codex assistance.
Apache-2.0. All ordinary normalization occurs outside tensor powers.
"""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json

from algebra import Q, accumulate, coefficient, eye, matrix, need, shifted, zmul

HERE = Path(__file__).resolve().parent


def construct():
    data = json.loads((HERE/'ROOT.json').read_text())
    events, targets, nodes = [], {}, []
    stage, next_role = 0, 6

    def emit(op, *args):
        events.append([op, *args])

    def mix(rows):
        a = matrix(rows)
        ops = []
        for j in range(6):
            k = next(k for k in range(j, 6) if a[k][j])
            if k != j:
                a[j], a[k] = a[k], a[j]
                ops.append(['SWAP', j, k])
            c = 1/a[j][j]
            if c != 1:
                a[j] = [x*c for x in a[j]]
                ops.append(['SCALE', j, str(c)])
            for k in range(6):
                if k != j and a[k][j]:
                    c = -a[k][j]
                    a[k] = [x+c*y for x, y in zip(a[k], a[j])]
                    ops.append(['ADD', k, j, str(c)])
        need(a == eye(6), 'Complete scalar basis elimination')
        for e in reversed(ops):
            if e[0] == 'SCALE':
                e[-1] = str(1/Q(e[-1]))
            elif e[0] == 'ADD':
                e[-1] = str(-Q(e[-1]))
            emit(*e)

    def label(tree):
        nonlocal stage
        if tree == 1:
            stage += 1
            return {'stage': stage, 'stages': [stage]}
        left, right = map(label, tree)
        return {'left': left, 'right': right, 'stages': left['stages']+right['stages']}

    roots = [label(t) for t in data['children']]

    def supplier(tree, x, y, exponent):
        nonlocal next_role
        if 'stage' in tree:
            if exponent == -1:
                emit('Q_POWER', x, -2)
            emit('SWAP', x, y)
            emit('LOCAL', tree['stage'], x, y)
            emit('SWAP', x, y)
            if exponent == -1:
                emit('Q_POWER', x, 2)
            return
        a, b = next_role, next_role+1
        next_role += 2
        stages = tree['stages']
        nodes.append({'roles': [a, b], 'stages': stages, 'exponent': exponent})
        emit('SWAP', x, b)
        emit('SWAP', y, a)
        emit('SWAP', a, b)
        emit('ADD', x, a, 1)
        emit('ADD', b, y, -1)
        emit('QUERY', a, b, -exponent)
        emit('ADD', b, y, 1)
        emit('ADD', x, a, -1)
        emit('IDLE', a, b, stages)
        emit('SCALE', y, -1)
        supplier(tree['left'], y, x, -exponent)
        emit('SCALE', y, -1)
        supplier(tree['right'], x, y, exponent)
        emit('ADD', x, a, 1)
        emit('SCALE', a, -1)
        emit('ADD', a, x, 1)
        emit('SWAP', y, b)
        emit('SCALE', b, -1)
        emit('ADD', b, y, 1)
        targets[a], targets[b] = (-exponent, stages), (exponent, stages)

    mix(data['input_basis'])
    full_index = 0
    for site in data['sites']:
        mix(site['inverse'])
        # lambda=(1+i)/2+(1-i)*q^2/2, q=Q^-1. Its square is q^2.
        emit('LAMBDA', 0, -1)
        if site['full']:
            tree = roots[full_index]
            full_index += 1
            supplier(tree, 0, 1, 1)
            for r in range(2, site['stage_rank']):
                emit('IDLE_ONE', r, tree['stages'])
        else:
            emit('QUERY', 0, 1, -1)
        emit('LAMBDA', 0, 1)
        emit('ADD', 0, 1, -1)
        mix(site['basis'])
    mix(data['output_basis'])
    for r, mask in enumerate(data['masks']):
        emit('LAMBDA', r, -1)
        selected = [s for bit, tree in zip(mask, roots) if bit for s in tree['stages']]
        targets[r] = (-1, selected)
    need(stage == 18 and next_role == 34, 'Complete mixed-root dimensions')
    diagonal = [[targets[r][0], 0]+[int(s in targets[r][1]) for s in range(1, stage+1)]
                for r in range(next_role)]
    return {'schema': 'mixed-projector-query-root/1', 'roles': next_role,
            'stages': stage, 'ambient_rank': 9+8*stage, 'nodes': nodes,
            'events': events, 'diagonal': diagonal}


def replay(word):
    n, width = word['roles'], word['stages']+2
    zero = (0,)*width
    rows = [[{zero: coefficient(1)} if i == j else {} for j in range(n)] for i in range(n)]
    seen = []
    for event in word['events']:
        op = event[0]
        if op == 'ADD':
            _, dst, src, c = event
            for a, b in zip(rows[dst], rows[src]):
                accumulate(a, b, coefficient(c))
        elif op == 'SCALE':
            _, dst, c = event
            rows[dst] = [{key: zmul(coefficient(c), value) for key, value in cell.items()}
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
            term = (exponent,)+(0,)*(width-1)
            for a, b in zip(rows[dst], shifted(rows[src], term)):
                accumulate(a, b)
            if op == 'LOCAL':
                term = (0,)+tuple(int(s == stage) for s in range(width-1))
                for r in (src, dst):
                    rows[r] = shifted(rows[r], term)
        elif op == 'Q_POWER':
            _, r, exponent = event
            need(exponent in (-2, 2), 'Only even powers are ordinary translations')
            rows[r] = shifted(rows[r], (exponent,)+(0,)*(width-1))
        elif op == 'LAMBDA':
            _, r, sign = event
            need(sign in (-1, 1), 'Unitary normalization or its inverse')
            old = rows[r]
            other = shifted(old, (2,)+(0,)*(width-1))
            rows[r] = [{} for _ in range(n)]
            for dst, a, b in zip(rows[r], old, other):
                accumulate(dst, a, (Q(1,2), Q(sign,2)))
                accumulate(dst, b, (Q(1,2), Q(-sign,2)))
        elif op in ('IDLE', 'IDLE_ONE'):
            roles, stages = (event[1:3], event[3]) if op == 'IDLE' else ([event[1]], event[2])
            need(len(stages) == len(set(stages)), 'Distinct whole-idle stages')
            term = (0,)+tuple(int(s in stages) for s in range(width-1))
            for r in roles:
                rows[r] = shifted(rows[r], term)
        else:
            raise ValueError('Unknown caller opcode: '+op)
    expected = [[{(word['diagonal'][i][0] % 4,)+tuple(word['diagonal'][i][1:]): coefficient(1)}
                 if i == j else {} for j in range(n)] for i in range(n)]
    need(sorted(seen) == list(range(1, word['stages']+1)), 'Every native stage exactly once')
    need(rows == expected, 'Every Q(i)[Q,D]/(Q^4-1) endpoint coefficient')
    return {'inputs': n, 'coefficients': n*n, 'native_stages': len(seen),
            'events': len(word['events']), 'event_sha256': sha256(json.dumps(word['events'],separators=(',',':')).encode()).hexdigest()}


def controls(word):
    result = {}
    for op in ['LOCAL', 'QUERY', 'IDLE', 'IDLE_ONE', 'LAMBDA', 'Q_POWER']:
        bad = deepcopy(word)
        del bad['events'][next(i for i,e in enumerate(bad['events']) if e[0] == op)]
        try:
            replay(bad)
        except ValueError as error:
            result['missing_'+op.lower()] = str(error)
        else:
            raise ValueError('Mutation accepted: '+op)
    return result


def formula_invoice(local):
    targets = Counter({r: 18*n for r,n in local['helpers'].items()})
    paid = Counter({r: 18*n for r,n in local['paid'].items()})
    paid[1] += 17*104
    # Four child trees: 7, 2, 1 and 8 leaves.
    for size, count in {2:8, 3:1, 4:3, 7:1, 8:1}.items():
        targets[1+8*size] += 208*count
        paid[8*size] += 208*count
    for rank,count in {145:1,17:1,73:2,9:2}.items():
        targets[rank] += 104*count
    paid[16] += 104
    paid[8] += 208
    return targets, paid


if __name__ == '__main__':
    word = construct()
    print(replay(word))
    print(controls(word))
