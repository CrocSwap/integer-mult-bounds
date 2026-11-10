"""Bound the complete caller with exact central characters.

Ali Romman with OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as F
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
W = json.loads((HERE / 'inputs/CONTROLLER.json').read_text())
N = W['roles']
D = W['stages']
Z = (0,) * D

def plus(a, b, c=(F(1), F(0))):
    out = dict(a)
    for k, (u, v) in b.items():
        x, y = out.get(k, (F(0), F(0)))
        x += u * c[0] - v * c[1]
        y += u * c[1] + v * c[0]
        if x or y:
            out[k] = (x, y)
        elif k in out:
            del out[k]
    return out

def rowadd(a, b, c):
    return [plus(x, y, c) for x, y in zip(a, b)]

def scale(a, c):
    return [plus({}, x, c) for x in a]

def shift(a, stages):
    t = tuple((int(k + 1 in stages) for k in range(D)))
    return [{tuple((x + y for x, y in zip(k, t))): v for k, v in c.items()} for c in a]

def unit(k):
    return [(F(1), F(0)), (F(0), F(1)), (F(-1), F(0)), (F(0), F(-1))][k % 4]

def step(M, e, q, trans=False):
    op = e[0]
    if op == 'ADD':
        _, a, b, c = e
        if trans:
            a, b = (b, a)
        M[a] = rowadd(M[a], M[b], (F(c), F(0)))
    elif op == 'SCALE':
        M[e[1]] = scale(M[e[1]], (F(e[2]), F(0)))
    elif op == 'SWAP':
        M[e[1]], M[e[2]] = (M[e[2]], M[e[1]])
    elif op in ['QUERY', 'LOCAL']:
        if op == 'LOCAL':
            _, s, b, a = e
            k = -1
        else:
            _, a, b, k = e
        if op == 'LOCAL':
            M[a] = shift(M[a], [s])
            M[b] = shift(M[b], [s])
        if trans:
            a, b = (b, a)
        M[a] = rowadd(M[a], M[b], unit(q * k))
    elif op == 'Q_POWER':
        M[e[1]] = scale(M[e[1]], unit(q * e[2]))
    elif op == 'LAMBDA':
        M[e[1]] = scale(M[e[1]], (F(1), F(0)) if q % 2 == 0 else (F(0), F(e[2])))
    elif op in ['IDLE', 'IDLE_ONE']:
        roles, stages = (e[1:3], e[3]) if op == 'IDLE' else ([e[1]], e[2])
        for a in roles:
            M[a] = shift(M[a], stages)
    else:
        raise ValueError(op)

def bound(M):
    return [[sum((abs(x) + abs(y) for x, y in c.values()), F(0)) for c in r] for r in M]

def identity():
    return [[{Z: (F(1), F(0))} if i == j else {} for j in range(N)] for i in range(N)]

def tables(backward=False):
    table = []
    for q in range(4):
        current = identity()
        events = list(reversed(W['events'])) if backward else W['events']
        values = [bound(current)]
        for event in events:
            step(current, event, q, backward)
            values.append(bound(current))
        if backward:
            values = [list(map(list, zip(*m))) for m in reversed(values)]
        if not table:
            table = values
        else:
            table = [[[max(a, b) for a, b in zip(r1, r2)] for r1, r2 in zip(m1, m2)] for m1, m2 in zip(table, values)]
    return table

def injections(event, normalizer=True):
    op = event[0]
    if op in ('ADD', 'SCALE'):
        return ('scalar', [event[1]], F(1))
    if op == 'LAMBDA' and normalizer:
        return ('scalar', [event[1]], F(9, 2))
    if op == 'LOCAL':
        return ('local', event[2:4], F(1))
    if op == 'QUERY':
        return ('query', [event[1]], F(1))
    if op in ('IDLE', 'IDLE_ONE'):
        return ('idle', event[1:3] if op == 'IDLE' else [event[1]], F(1))
    return ('scalar', [], F(0))

def calculate():
    prefix, suffix = (tables(), tables(True))
    maximum = max(((sum(row), t, i) for t, m in enumerate(prefix) for i, row in enumerate(m)))
    errors = {k: [F(0)] * N for k in ('scalar', 'local', 'query', 'idle')}
    for t, event in enumerate(W['events']):
        key, roles, weight = injections(event)
        for i in range(N):
            errors[key][i] += weight * sum((suffix[t + 1][i][j] for j in roles))
    return {'prefix': [str(maximum[0]), *maximum[1:]], 'errors': {k: list(map(str, v)) for k, v in errors.items()}, 'common_error': str(max((sum((errors[k][i] for k in errors)) for i in range(N))))}
