# SPDX-License-Identifier: Apache-2.0
"""Independent sparse rational replay and rank certificates. Tekalign/Codex."""
from collections import defaultdict
from fractions import Fraction as Q

PRIME = 1000000007


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def add(destination, source, coefficient):
    for key, value in list(source.items()):
        updated = destination.get(key, Q(0)) + coefficient * value
        if updated:
            destination[key] = updated
        else:
            destination.pop(key, None)


def replay(word):
    """Non-target M after the entry prelude, as defined in PR2908/2979."""
    removed = set(word['removed'])
    live = sorted(set(range(704)) - removed - set(range(112, 224)))
    need(len(live) == 520 and len(removed) == 72, 'source register contract')
    rows = {r: {(r, ()): Q(1)} for r in live}

    def scalar(gate):
        kind, target = gate[:2]
        need(kind in ('add', 'scale'), 'scalar instruction')
        if kind == 'add':
            source, numerator, denominator = gate[2:5]
            need(target != source, 'distinct scalar operands')
            need(not (112 <= source < 224 and not 112 <= target < 224),
                 'omitted target cannot feed non-target')
            value = Q(numerator, denominator)
            if target in rows:
                need(source in rows, 'live scalar source')
                add(rows[target], rows[source], value)
        else:
            value = Q(gate[2], gate[3])
            need(value != 0, 'invertible scale')
            if target in rows:
                rows[target] = {key: value * a for key, a in rows[target].items()}
        need(value.denominator & (value.denominator - 1) == 0, 'dyadic scalar')

    def warp(register, operator):
        need(register in rows, 'live warp register')
        result = {}
        for (column, history), value in rows[register].items():
            new = history[1:] if history and history[0] == -operator else (operator,) + history
            add(result, {(column, new): value}, Q(1))
        rows[register] = result

    need(word['prelude_events'] == 84, 'pinned prelude boundary')
    for gate in word['A'][84:]:
        scalar(gate)
    by_position = defaultdict(list)
    for operator, record in enumerate(word['warps'], 1):
        position, register = record[:2]
        need(0 <= position <= len(word['B']), 'warp chronology')
        by_position[position].append((register, operator))
    for position in range(len(word['B']) + 1):
        for register, operator in by_position[position]:
            warp(register, operator)
        if position < len(word['B']):
            scalar(word['B'][position])
    for gate in word['restore']:
        scalar(gate)
    # Do not infer phase-aware products from binary G multiplication.
    need(all(len(history) <= 1 and (not history or history[0] > 0)
             for row in rows.values() for _, history in row),
         'final M must be affine-linear in positive native warps')
    return {r: {(c, history[0] if history else 0): value
                for (c, history), value in row.items()} for r, row in rows.items()}


def quotient(matrix, aliases):
    result = {}
    for r, row in matrix.items():
        grouped = {}
        for (c, operator), value in row.items():
            add(grouped, {(c, aliases[operator]): value}, Q(1))
        result[r] = grouped
    return result


def constraints(matrix, word):
    live = sorted(matrix)
    protected = (set(map(int, word['helper_final'])) | set(map(int, word['start_extra']))
                 | {item['source'] for item in word['initial_corrections']})
    helpers = sorted(r for r in live if r >= 224 and r not in protected)
    allowed = set(helpers)
    right, left, compensation = defaultdict(dict), defaultdict(dict), defaultdict(dict)
    for r, row in matrix.items():
        for (c, operator), value in row.items():
            if operator and c in allowed:
                right[r, operator][c] = value
            if operator or c not in allowed:
                left[c, operator][r] = value
    for gate in word['compensation']:
        need(gate[0] == 'add' and gate[-1] == [] and 112 <= gate[1] < 224,
             'zero-frame target compensation')
        if gate[2] in allowed:
            add(compensation[gate[1]], {gate[2]: Q(gate[3], gate[4])}, Q(1))
    return (list(right.values()) + list(compensation.values()),
            list(left.values()), helpers, live)


def check_basis(rows, columns, free, basis):
    need(len(set(free)) == len(free) == len(basis), 'basis size')
    need(set(free) <= set(columns), 'free columns in domain')
    for i, vector in enumerate(basis):
        need(set(vector) <= set(columns), 'basis support')
        need(all(vector.get(c, Q(0)) == (i == j) for j, c in enumerate(free)),
             'unit free-coordinate minor')
        need(all(sum((a * vector.get(c, Q(0)) for c, a in row.items()), Q(0)) == 0
                 for row in rows), 'exact null vector')


def nullspace(rows, columns):
    """Rational null vectors with a unit minor certify a lower bound on nullity."""
    columns = set(columns)
    pivots = {}
    for original in rows:
        row = {c: Q(a) for c, a in original.items() if a and c in columns}
        while row:
            p = min(row)
            coefficient = row[p]
            if p not in pivots:
                pivots[p] = {c: a / coefficient for c, a in row.items()}
                break
            add(row, pivots[p], -coefficient)
    free = sorted(columns - set(pivots))
    basis = []
    for column in free:
        vector = {column: Q(1)}
        for p, row in sorted(pivots.items(), reverse=True):
            value = -sum((a * vector.get(c, Q(0)) for c, a in row.items() if c != p), Q(0))
            if value:
                vector[p] = value
        basis.append(vector)
    check_basis(rows, columns, free, basis)
    return free, basis


def modular_rank(rows, columns, prime=PRIME):
    """Modular forward elimination; nonzero pivots certify a lower Q rank bound."""
    columns = set(columns)
    pivots, selected = {}, []
    for index, original in enumerate(rows):
        row = {}
        for c, a in original.items():
            if c in columns:
                a = Q(a)
                value = a.numerator * pow(a.denominator, -1, prime) % prime
                if value:
                    row[c] = value
        for p in sorted(pivots):
            value = row.get(p, 0)
            if value:
                for c, a in pivots[p].items():
                    v = (row.get(c, 0) - value * a) % prime
                    if v:
                        row[c] = v
                    else:
                        row.pop(c, None)
        if row:
            p = min(row)
            factor = pow(row[p], -1, prime)
            pivots[p] = {c: a * factor % prime for c, a in row.items()}
            selected.append(index)
    return len(pivots), selected


def same_kernel(free_rows, native_rows, columns):
    free, basis = nullspace(free_rows, columns)
    check_basis(native_rows, columns, free, basis)
    rank, selected = modular_rank(native_rows, columns)
    need(rank + len(basis) == len(columns), 'native kernel strictly larger or rank unresolved')
    return {'variables': len(columns), 'nullity': len(basis), 'rank': rank,
            'free_equations': len(free_rows), 'native_equations': len(native_rows),
            'free_columns': free, 'native_pivot_rows': selected}
