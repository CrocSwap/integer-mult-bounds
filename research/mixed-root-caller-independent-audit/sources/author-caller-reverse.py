"""Check the 570-event caller by reverse output functionals.

The source engine propagates a matrix forward in Q(i)[Q,D]/(Q^4-1).
This engine uses four exact Q characters and separate reverse rows.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
import json


def need(ok, message):
    if not ok:
        raise ValueError(message)


def add(a, b):
    return a[0]+b[0], a[1]+b[1]


def multiply(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def power(q, exponent):
    out = (Q(1), Q(0))
    for _ in range(exponent % 4):
        out = multiply(out, q)
    return out


def accumulate(dst, src, coefficient=(Q(1), Q(0))):
    for monomial, value in src.items():
        value = add(dst.get(monomial, (Q(0), Q(0))), multiply(coefficient, value))
        if value == (0, 0):
            dst.pop(monomial, None)
        else:
            dst[monomial] = value


def scaled(poly, coefficient):
    return {monomial: multiply(value, coefficient) for monomial, value in poly.items()}


def stages(poly, selected, count):
    need(len(selected) == len(set(selected)) and all(1 <= x <= count for x in selected),
         'Every formal stage is distinct and within the declared range')
    delta = tuple(int(i in selected) for i in range(1, count+1))
    return {tuple(x+y for x, y in zip(monomial, delta)): value for monomial, value in poly.items()}


def check(word):
    n, count = word['roles'], word['stages']
    need(sorted(e[1] for e in word['events'] if e[0] == 'LOCAL') == list(range(1, count+1)),
         'Every native stage occurs exactly once')
    digest = sha256()
    for character in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        q = tuple(Q(x) for x in character)
        for output in range(n):
            row = [{} for _ in range(n)]
            row[output][(0,)*count] = (Q(1), Q(0))
            for event in reversed(word['events']):
                op = event[0]
                if op == 'ADD':
                    _, dst, src, coefficient = event
                    accumulate(row[src], row[dst], (Q(coefficient), Q(0)))
                elif op == 'SCALE':
                    _, dst, coefficient = event
                    row[dst] = scaled(row[dst], (Q(coefficient), Q(0)))
                elif op == 'SWAP':
                    _, a, b = event
                    row[a], row[b] = row[b], row[a]
                elif op == 'LOCAL':
                    _, stage, src, dst = event
                    row[src] = stages(row[src], [stage], count)
                    row[dst] = stages(row[dst], [stage], count)
                    accumulate(row[src], row[dst], power(q, -1))
                elif op == 'QUERY':
                    _, dst, src, exponent = event
                    accumulate(row[src], row[dst], power(q, exponent))
                elif op == 'Q_POWER':
                    _, role, exponent = event
                    need(exponent in (-2, 2), 'An ordinary translation uses an even central power')
                    row[role] = scaled(row[role], power(q, exponent))
                elif op == 'LAMBDA':
                    _, role, sign = event
                    need(sign in (-1, 1), 'The normalizer sign is specified')
                    a = (Q(1, 2), Q(sign, 2))
                    b = (Q(1, 2), Q(-sign, 2))
                    row[role] = scaled(row[role], add(a, multiply(b, power(q, 2))))
                elif op == 'IDLE':
                    _, a, b, selected = event
                    row[a], row[b] = stages(row[a], selected, count), stages(row[b], selected, count)
                elif op == 'IDLE_ONE':
                    _, role, selected = event
                    row[role] = stages(row[role], selected, count)
                else:
                    raise ValueError('Unknown caller operation: '+op)
            diagonal = word['diagonal'][output]
            need(len(diagonal) == count+2 and diagonal[1] == 0, 'The unused stage-zero exponent is zero')
            expected = [{} for _ in range(n)]
            expected[output] = {tuple(diagonal[2:]): power(q, diagonal[0])}
            need(row == expected, 'Complete reverse-functional endpoint, character '+str(character)+', output '+str(output))
            digest.update(json.dumps([character, output, diagonal], separators=(',', ':')).encode())
    return digest.hexdigest()


def run(word):
    digest = check(word)
    controls = {}
    for op in ('LOCAL', 'QUERY', 'IDLE', 'IDLE_ONE', 'LAMBDA', 'Q_POWER'):
        bad = deepcopy(word)
        del bad['events'][next(i for i, event in enumerate(bad['events']) if event[0] == op)]
        try:
            check(bad)
        except ValueError:
            controls['missing_'+op.lower()] = 'rejected'
        else:
            raise ValueError('The reverse engine accepted an omitted '+op)
    bad = deepcopy(word)
    bad['events'].append(['ADD', 0, 1, '1'])
    try:
        check(bad)
    except ValueError:
        controls['off_diagonal_output'] = 'rejected'
    else:
        raise ValueError('The reverse engine accepted an off-diagonal output')
    return {'status': 'PASS_REVERSE_CHARACTER_CALLER', 'events': len(word['events']),
            'matrix_entries': word['roles']**2, 'central_characters': 4,
            'formal_stage_polynomials_checked': 4*word['roles']**2,
            'endpoint_digest': digest, 'controls': controls,
            'scope': 'All formal caller coefficients. No physical native, price or compiler check is supplied by this engine.'}
