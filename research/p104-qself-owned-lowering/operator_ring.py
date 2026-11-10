"""Exact forward certificate over Q(i)[q,D_1,...,D_18]/(q^4-1).

This verifies an operator identity, not values at sampled D substitutions.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from fractions import Fraction as F
import hashlib
import json


def need(ok, why):
    if not ok:
        raise ValueError(why)


def validate(caller):
    need(caller['schema'] == 'mixed-root-caller/1', 'mixed caller schema')
    need(caller['stages'] == 18 and caller['ambient_rank'] == 153, 'fixed stage/ambient family')
    occupied = set()
    ports = []
    for ty in ('A', 'B'):
        t = caller['types'][ty]
        roles = set(range(t['offset'], t['offset'] + t['roles']))
        need(not occupied & roles and len(t['diagonal']) == len(roles), 'complete disjoint roles')
        occupied |= roles
        ports += t['ports']
        for dg in t['diagonal']:
            need(len(dg) == 20 and dg[:2] == [-1, 0] and set(dg[2:]) <= {0, 1}, 'target domain')
    need(occupied == set(range(caller['roles'])), 'complete arbitrary input range')
    need(sorted(ports) == list(range(104)), 'complete disjoint port partition')
    need(F(caller['types']['A']['alpha2']) == -1 and F(caller['types']['A']['beta2']) == 0,
         'exact HOST2 coefficients')
    stages = []
    for e in caller['events']:
        if e[0] == 'J':
            need(len(e) == 4 and len(e[2]) == 4 and len(e[3]) == 4, 'joint contact record')
            stages.append(e[1])
            for ty, touched in (('A', e[2]), ('B', e[3][:2])):
                t = caller['types'][ty]
                need(len(set(touched)) == len(touched) and all(t['offset'] <= r < t['offset']+t['roles'] for r in touched), 'joint distinct fields')
            need(F(e[3][2]) == -1 and F(e[3][3]) == F(1, 2), 'exact hosted gauge')
            continue
        ty, op = e[:2]
        need(ty in ('A', 'B'), 'event tag')
        t = caller['types'][ty]
        arity = {'ADD': 5, 'SWAP': 4, 'SCALE': 4, 'QUERY': 5, 'QSELF': 4,
                 'LAMBDA': 4, 'IDLE_ONE': 4}
        need(op in arity and len(e) == arity[op], 'exact opcode arity')
        touched = e[2:4] if op in ('ADD', 'SWAP', 'QUERY') else e[2:3]
        need(all(type(r) is int and t['offset'] <= r < t['offset']+t['roles'] for r in touched), 'source role domain')
        if len(touched) == 2:
            need(touched[0] != touched[1], 'distinct scalar/query roles')
        if op in ('ADD', 'SCALE'):
            c = F(e[-1])
            need(c and c.denominator & (c.denominator-1) == 0, 'current dyadic coefficient')
        elif op in ('QUERY', 'QSELF', 'LAMBDA'):
            need(e[-1] in (-1, 1), 'signed operator orientation')
        elif op == 'IDLE_ONE':
            need(e[3] and len(e[3]) == len(set(e[3])) and all(type(k) is int and 1 <= k <= 18 for k in e[3]), 'whole idle stage set')
    need(stages == list(range(1, 19)), 'fresh ordered joint stages')


def multiply(row, a=F(1), b=F(0), q=0, d=0, modulus=4):
    """A row key is (independent input, q exponent, square-free D mask)."""
    out = {}
    for (j, p, mask), (x, y) in row.items():
        need(not mask & d, 'repeated D factor exceeds the declared square-free domain')
        c = (a*x-b*y, a*y+b*x)
        if c != (0, 0):
            out[(j, (p+q) % modulus, mask | d)] = c
    return out


def add(a, b):
    out = a.copy()
    for k, (x, y) in b.items():
        u, v = out.get(k, (0, 0))
        c = (x+u, y+v)
        if c == (0, 0):
            out.pop(k, None)
        else:
            out[k] = c
    return out


def expected(caller):
    result = [None] * caller['roles']
    for ty in ('A', 'B'):
        t = caller['types'][ty]
        for j, dg in enumerate(t['diagonal']):
            r = t['offset'] + j
            result[r] = {(r, dg[0] % 4, sum(bit << k for k, bit in enumerate(dg[2:]))): (F(1), F(0))}
    return result


def replay(caller, modulus=4):
    validate(caller)
    R = [{(j, 0, 0): (F(1), F(0))} for j in range(caller['roles'])]
    peak = 0
    peak_row = 0
    for e in caller['events']:
        if e[0] == 'J':
            d = 1 << (e[1]-1)
            src, dst, x2, y2 = e[2]
            R[dst] = add(R[dst], multiply(R[src], q=-1, modulus=modulus))
            R[x2] = add(R[x2], multiply(R[y2], a=F(caller['types']['A']['alpha2']), q=1, modulus=modulus))
            for r in e[2]:
                R[r] = multiply(R[r], d=d, modulus=modulus)
            s, t, al, be = e[3]
            a, b = F(al), F(be)
            # Simultaneous HOST update uses both old rows.
            ns = multiply(add(R[s], multiply(R[t], a=a, q=1, modulus=modulus)), d=d, modulus=modulus)
            nt = multiply(add(multiply(R[s], a=b, q=-1, modulus=modulus), multiply(R[t], a=1+a*b, modulus=modulus)), d=d, modulus=modulus)
            R[s], R[t] = ns, nt
        else:
            op, x = e[1:3]
            if op == 'ADD':
                R[x] = add(R[x], multiply(R[e[3]], a=F(e[4]), modulus=modulus))
            elif op == 'SCALE':
                R[x] = multiply(R[x], a=F(e[3]), modulus=modulus)
            elif op == 'SWAP':
                R[x], R[e[3]] = R[e[3]], R[x]
            elif op == 'QUERY':
                R[x] = add(R[x], multiply(R[e[3]], q=e[4], modulus=modulus))
            elif op == 'QSELF':
                R[x] = multiply(R[x], q=e[3], modulus=modulus)
            elif op == 'IDLE_ONE':
                R[x] = multiply(R[x], d=sum(1 << (k-1) for k in e[3]), modulus=modulus)
            elif op == 'LAMBDA':
                R[x] = add(multiply(R[x], a=F(1, 2), b=F(e[3], 2), modulus=modulus),
                           multiply(R[x], a=F(1, 2), b=F(-e[3], 2), q=2, modulus=modulus))
        peak = max(peak, sum(map(len, R)))
        peak_row = max(peak_row, max(map(len, R)))
        need(peak <= 500000, 'bounded exact replay term ceiling')
    need(R == expected(caller), 'exact formal caller endpoint on every input coefficient')
    encoded = [[[list(k), str(a), str(b)] for k, (a, b) in sorted(row.items())] for row in R]
    return {'events': len(caller['events']), 'independent_inputs': len(R),
            'D_variables': 18, 'q_relation': 'q^4=1', 'peak_terms': peak,
            'peak_row_terms': peak_row, 'endpoint_terms': sum(map(len, R)),
            'endpoint_sha256': hashlib.sha256(json.dumps(encoded, separators=(',', ':')).encode()).hexdigest()}
