"""Two integral basis shears for the historical rank-h complex center.

Apache-2.0. Ross Richardson, with substantial OpenAI Codex assistance.
The original factor and invocation are Douglas R. Colkitt's work.
"""
from copy import deepcopy


def require(condition, message):
    if not condition:
        raise ValueError(message)


def shear(factor, i, j, sign):
    """Return V'=(I+sign E_ij)V and U'=U(I-sign E_ij)."""
    h = factor['h']
    require(type(i) is int and type(j) is int and 0 <= i < h and
            0 <= j < h and i != j and type(sign) is int and sign in (-1, 1),
            'invalid elementary shear')
    result = deepcopy(factor)
    for k, row in enumerate(factor['gather']):
        values = dict(row)
        values[i] = values.get(i, 0) + sign * values.get(j, 0)
        result['gather'][k] = tuple(sorted((a, x) for a, x in values.items() if x))
    for k, row in enumerate(factor['scatter']):
        values = list(row)
        values[j] -= sign * values[i]
        result['scatter'][k] = tuple(values)
    return result


def candidate(original):
    return shear(shear(original, 1, 0, 1), 2, 0, 1)


def price(factor):
    """One unit gather ADD; scatter numerator ±1 costs two, ±2 one."""
    require(all(type(x) is int and abs(x) == 1
                for row in factor['gather'] for _, x in row),
            'gather outside priced alphabet')
    require(all(type(x) is int and abs(x) <= 2
                for row in factor['scatter'] for x in row),
            'scatter outside priced alphabet')
    g = sum(len(row) for row in factor['gather'])
    h = sum(1 if abs(x) == 2 else 2 for row in factor['scatter'] for x in row if x)
    return {'G': g, 'H': h, 'G_plus_H': g + h}


def second_shear_census(original, seed=39):
    """Exhaust the declared one-step neighborhood of PR809, not all circuits."""
    first = shear(original, 1, 2, -1)
    h = original['h']
    # A move changes exactly one V row and one U column. Avoid copying the
    # unchanged factor for each candidate, but charge its complete cost.
    v = [[dict(row).get(i, 0) for row in first['gather']] for i in range(h)]
    u = list(zip(*first['scatter']))
    moves = [(i, j, s) for i in range(h) for j in range(h) if i != j for s in (-1, 1)]
    offset = seed % len(moves)
    moves = moves[offset:] + moves[:offset]
    baseline = price(first)['G_plus_H']
    rows = []
    def scatter_cost(row):
        return sum(1 if abs(x) == 2 else 2 for x in row if x)
    for i, j, s in moves:
        vr = [a+s*b for a, b in zip(v[i], v[j])]
        ur = [a-s*b for a, b in zip(u[j], u[i])]
        admissible = all(abs(x) <= 1 for x in vr) and all(abs(x) <= 2 for x in ur)
        cost = None
        if admissible:
            cost = baseline + sum(x != 0 for x in vr)-sum(x != 0 for x in v[i])
            cost += scatter_cost(ur)-scatter_cost(u[j])
        rows.append({'move': [i, j, s], 'cost': cost})
    accepted = [row for row in rows if row['cost'] is not None]
    best = min(row['cost'] for row in accepted)
    return {'seed': seed, 'domain': len(rows), 'admissible': len(accepted),
            'best_cost': best, 'best_moves': [r['move'] for r in accepted if r['cost'] == best],
            'histogram': {str(c): sum(r['cost'] == c for r in accepted)
                          for c in sorted({r['cost'] for r in accepted})},
            'rows': rows}
