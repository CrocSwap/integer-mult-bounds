# SPDX-License-Identifier: Apache-2.0
"""Exact replay of a source-bound, two-sided full-frame factorization.

conorholds, with substantial OpenAI Codex assistance.
Two-sided cleanup factorization credits Stephan Arrington's PR1119.
"""
from fractions import Fraction as Q
from network import HERE, price, require, sha, strict_json


def add(target, source, value):
    value = Q(value)
    require(target != source and value != 0, 'cleanup addition alias or zero')
    gate = ['add', target, source, value.numerator, value.denominator, 1]
    price(gate)
    return gate


def scale(target, value):
    value = Q(value)
    require(value != 0 and value != 1, 'cleanup trivial scale')
    gate = ['scale', target, value.numerator, value.denominator, 1]
    price(gate)
    return gate


def operator(word, gates):
    n = 2*word['v'] + word['R']
    rows = [{i: Q(1)} for i in range(n)]
    for gate in gates:
        require(isinstance(gate, list) and gate and gate[0] in ('add', 'scale'), 'cleanup opcode')
        require(len(gate) == (6 if gate[0] == 'add' else 5), 'cleanup gate shape')
        require(all(type(x) is int for x in gate[1:]) and gate[-1] == 1, 'cleanup types or frame')
        registers = gate[1:3] if gate[0] == 'add' else gate[1:2]
        require(all(0 <= x < n and word['final'][x] == 1 and
                    not word['v'] <= x < 2*word['v'] for x in registers), 'cleanup register contract')
        numerator, denominator = gate[3:5] if gate[0] == 'add' else gate[2:4]
        require(denominator > 0 and numerator != 0, 'cleanup coefficient')
        q = Q(numerator, denominator)
        require((q.numerator, q.denominator) == (numerator, denominator), 'cleanup reduced coefficient')
        price(gate); target = gate[1]
        if gate[0] == 'scale':
            rows[target] = {j: q*x for j, x in rows[target].items()}
        else:
            require(target != gate[2], 'cleanup operand alias')
            for j, x in list(rows[gate[2]].items()):
                y = rows[target].get(j, Q(0)) + q*x
                if y:
                    rows[target][j] = y
                else:
                    rows[target].pop(j, None)
    return rows


def factor_block(original, registers, pivots):
    require(isinstance(registers, list) and registers == sorted(set(registers)) and
            all(type(i) is int for i in registers), 'cleanup block registers')
    require(isinstance(pivots, list) and len(pivots) == len(registers), 'cleanup pivot inventory')
    inside = set(registers)
    rows = {i: {j: q for j, q in original[i].items() if j in inside} for i in registers}
    active_rows = inside.copy(); active_columns = inside.copy(); left = []; right = []; diagonal = []
    for pivot in pivots:
        require(isinstance(pivot, list) and len(pivot) == 2 and all(type(i) is int for i in pivot),
                'cleanup pivot shape')
        r, c = pivot
        require(r in active_rows and c in active_columns, 'cleanup repeated or out-of-range pivot')
        q = rows[r].get(c, Q(0))
        require(q and abs(q.numerator) & (abs(q.numerator)-1) == 0 and
                q.denominator & (q.denominator-1) == 0, 'cleanup pivot is not a dyadic unit')
        pivot_row = rows[r].copy()
        for i in registers:
            coefficient = rows[i].get(c, Q(0))
            if i == r or not coefficient:
                continue
            factor = -coefficient/q; left.append(add(i, r, factor))
            for j, x in pivot_row.items():
                y = rows[i].get(j, Q(0)) + factor*x
                if y:
                    rows[i][j] = y
                else:
                    rows[i].pop(j, None)
        for j, x in pivot_row.items():
            if j != c:
                right.append(add(c, j, -x/q))
                rows[r].pop(j)
        diagonal.append((r, c, q)); active_rows.remove(r); active_columns.remove(c)
    require(rows == {r: {c: q} for r, c, q in diagonal}, 'cleanup factorization residual')
    # L M R = S. Execute R^-1, then monomial S, then L^-1.
    # Right inverses keep nomination order; left inverses reverse it.
    result = []
    for gate in right:
        inverse = gate.copy(); inverse[3] *= -1; result.append(inverse)
    wanted = {r: c for r, c, q in diagonal}; where = registers.copy(); signs = [1]*len(registers)
    for k, r in enumerate(registers):
        if where[k] == wanted[r]:
            continue
        j = where.index(wanted[r]); s = registers[j]
        result.extend([add(r, s, 1), add(s, r, -1), add(r, s, 1)])
        where[k], where[j] = where[j], where[k]
        signs[k], signs[j] = signs[j], -signs[k]
    values = {r: q for r, c, q in diagonal}
    for k, r in enumerate(registers):
        q = values[r]*signs[k]
        if q != 1:
            result.append(scale(r, q))
    for gate in reversed(left):
        inverse = gate.copy(); inverse[3] *= -1; result.append(inverse)
    return result


def construct_cleanup(word, recipe=None):
    if recipe is None:
        recipe = strict_json((HERE / 'CLEANUP-RECIPE.json').read_bytes())
    require(recipe['schema_version'] == 1, 'cleanup recipe schema')
    original_raw = json_bytes(word['cleanup'])
    require(sha(original_raw) == recipe['original_cleanup_sha256'], 'cleanup input binding')
    require(recipe['word_sha256'] == strict_json((HERE / 'RECIPE.json').read_bytes())['word_sha256'],
            'cleanup whole-word binding')
    original = operator(word, word['cleanup']); n = len(original)
    active = {i for i, row in enumerate(original) if row != {i: Q(1)}}
    active.update(j for i in active.copy() for j in original[i])
    blocks = recipe['blocks']; require(isinstance(blocks, list) and blocks, 'missing cleanup blocks')
    used = set(); gates = []
    for block in blocks:
        require(isinstance(block, dict) and set(block) == {'registers', 'pivots'}, 'cleanup block schema')
        registers = block['registers']
        require(isinstance(registers, list) and all(type(i) is int and 0 <= i < n
                and word['final'][i] == 1 and not word['v'] <= i < 2*word['v'] for i in registers),
                'cleanup block contract')
        require(not used.intersection(registers), 'cleanup repeated block')
        group = set(registers)
        external = [(i, j, q) for i in registers for j, q in sorted(original[i].items()) if j not in group]
        require(all(j not in used for i, j, q in external), 'cleanup donor already overwritten')
        gates.extend(factor_block(original, registers, block['pivots']))
        gates.extend(add(i, j, q) for i, j, q in external); used.update(group)
    require(active <= used, 'cleanup missing active registers')
    require(operator(word, gates) == original, 'cleanup full arbitrary-input operator')
    counts = dict(before_macros=len(word['cleanup']), after_macros=len(gates),
                  before_real=sum(map(price, word['cleanup'])), after_real=sum(map(price, gates)))
    counts['saving_real'] = counts['before_real']-counts['after_real']
    require(counts == recipe['claimed'], 'cleanup complete paid counts')
    require(counts['saving_real'] > 0 and counts['after_macros'] < counts['before_macros'], 'cleanup no complete gain')
    return gates, counts


def json_bytes(value):
    import json
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()
