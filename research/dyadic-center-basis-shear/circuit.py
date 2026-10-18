"""Exact single-shear center reparameterization and finite cost census.

Copyright 2026 Curtis Dransfield. Apache-2.0; substantial OpenAI Codex assistance.
"""
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import combinations
import json
from math import comb


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(f):
    h = f['h']
    require(type(h) is int and h >= 8 and h % 2 == 0, 'Use even h >= 8')
    require(f['triples'] == list(combinations(range(h), 3)), 'Wrong ordered triples')
    n = comb(h, 3)
    require(len(f['gather']) == len(f['scatter']) == n, 'Wrong factor shape')
    for v in f['gather']:
        require(len({i for i, x in v}) == len(v), 'Repeated gather coordinate')
        require(all(type(i) is int and 0 <= i < h and type(x) is int and x in (-1, 1)
                    for i, x in v), 'Gather requires unit integer coefficients')
    require(all(len(u) == h and all(type(x) is int and abs(x) <= 2 for x in u)
                for u in f['scatter']), 'Scatter requires integer numerators of magnitude at most two')


def shear(f, i, j, sign):
    validate(f)
    require(type(i) is int and type(j) is int and 0 <= i < f['h'] and 0 <= j < f['h']
            and i != j and type(sign) is int and sign in (-1, 1), 'Invalid elementary shear')
    gather = []
    for sparse in f['gather']:
        row = dict(sparse)
        row[i] = row.get(i, 0) + sign*row.get(j, 0)
        gather.append(tuple((a, x) for a, x in sorted(row.items()) if x))
    scatter = []
    for row in f['scatter']:
        updated = list(row)
        updated[j] -= sign*row[i]
        scatter.append(tuple(updated))
    result = dict(h=f['h'], triples=list(f['triples']), gather=gather, scatter=scatter)
    validate(result)
    return result


def charge(f):
    validate(f)
    G = sum(len(v) for v in f['gather'])
    H = sum(1 if abs(x) == 2 else 2 for u in f['scatter'] for x in u if x)
    return dict(G=G, H=H, G_plus_H=G+H)


def verify_product(f):
    validate(f)
    masks = [sum(1 << x for x in T) for T in f['triples']]
    digest = hashlib.sha256()
    for S, u in zip(masks, f['scatter']):
        row = bytearray()
        for T, v in zip(masks, f['gather']):
            value = sum(u[i]*x for i, x in v)
            require(value == (S & T).bit_count()-1, 'Central product coefficient mismatch')
            row.append(value+1)
        digest.update(row)
    return dict(coefficients_checked=len(masks)**2, coefficient_sha256=digest.hexdigest())


def census(f, seed=20):
    """Exhaust exactly one unit elementary shear, preserving the declared alphabet."""
    validate(f)
    h = f['h']
    V = [[dict(v).get(i, 0) for v in f['gather']] for i in range(h)]
    U = list(zip(*f['scatter']))
    def gc(row): return sum(x != 0 for x in row)
    def hc(row): return sum(0 if x == 0 else 1 if abs(x) == 2 else 2 for x in row)
    records, admissible = [], []
    for i in range(h):
        for j in range(h):
            if i == j:
                continue
            for sign in (-1, 1):
                v = [a + sign*b for a, b in zip(V[i], V[j])]
                u = [a - sign*b for a, b in zip(U[j], U[i])]
                gather_ok, scatter_ok = max(map(abs, v)) <= 1, max(map(abs, u)) <= 2
                row = dict(i=i, j=j, sign=sign, gather_admissible=gather_ok,
                           scatter_admissible=scatter_ok)
                if gather_ok and scatter_ok:
                    row.update(delta_G=gc(v)-gc(V[i]), delta_H=hc(u)-hc(U[j]))
                    row['delta'] = row['delta_G'] + row['delta_H']
                    admissible.append(row)
                records.append(row)
    minimum = min(r['delta'] for r in admissible)
    winners = [r for r in admissible if r['delta'] == minimum]
    chosen = winners[seed % len(winners)]
    transcript = json.dumps(records, sort_keys=True, separators=(',', ':')).encode()
    return dict(h=h, assignment_seed=seed, candidate_moves=len(records),
                admissible_moves=len(admissible), rejected_moves=len(records)-len(admissible),
                delta_histogram=dict(sorted(Counter(str(r['delta']) for r in admissible).items())),
                minimum_delta=minimum, minimizers=winners, selected=chosen,
                tie_rule='Lexicographic (i,j,sign) enumeration; seed modulo number of minimizers',
                transcript_sha256=hashlib.sha256(transcript).hexdigest(),
                stopping_rule='All 2*h*(h-1) one-shear moves; no compositions or adaptive search')


def closed_saving(h):
    require(type(h) is int and h >= 8 and h % 2 == 0, 'Use even h >= 8')
    return (h-10)*(h-2)*(h-3)//6


def serializable(value):
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(k): serializable(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [serializable(v) for v in value]
    return value
