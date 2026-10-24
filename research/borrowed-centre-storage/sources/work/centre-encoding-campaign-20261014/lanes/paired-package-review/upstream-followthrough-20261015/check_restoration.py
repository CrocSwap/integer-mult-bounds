#!/usr/bin/env python3
"""Check a QQ16 first-pair repair with 16 owned records.

This file uses no predecessor executable. The two QQ16 calls are source
contracts. The new repair has a literal scalar, map, and native-line word.
"""

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'base/research/joint-query/certificate.json.gz'
SOURCE_SHA = 'a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7'
AXES = tuple(1 << i for i in range(73))
OLD = tuple((v, 1) for v in AXES[:9])
STEP = tuple((v, 1) for v in AXES[9:17])
CURRENT = OLD + STEP


def need(ok, message):
    if not ok:
        raise ValueError(message)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def digest(value):
    return hashlib.sha256(value).hexdigest()


def action(g, v):
    answer = 0
    while v:
        bit = v & -v
        answer ^= g[bit.bit_length() - 1]
        v ^= bit
    return answer


def product(g, h):
    return tuple(action(g, v) for v in h)


@lru_cache(None)
def phase(terms):
    linear, quadratic = [0] * 73, [0] * 73
    for vector, coefficient in terms:
        bits = [i for i in range(73) if vector >> i & 1]
        for i in bits:
            linear[i] = (linear[i] + coefficient) % 4
            if coefficient % 2:
                for j in bits:
                    if i < j:
                        quadratic[i] ^= 1 << j
    return tuple(linear), tuple(quadratic)


def transport(terms, g, shift):
    return tuple((action(g, v), c) for v, c in terms) + ((shift, 2),)


def lift(g, count):
    linear, quadratic = phase(tuple((v, 1) for v in g[:count]))
    need(not any(quadratic), 'nonzero quadratic frame residual')
    delta = [((i < count) - linear[i]) % 4 for i in range(73)]
    need(all(x % 2 == 0 for x in delta), 'odd frame residual')
    return sum((x // 2) << i for i, x in enumerate(delta))


def load():
    raw = SOURCE.read_bytes()
    need(digest(raw) == SOURCE_SHA, 'certificate source pin')
    source = json.loads(gzip.decompress(raw))
    R = [[Q(row.get(str(p), 0)) for p in range(112)] for row in source['R_rows']]
    A, T, U = [tuple(source[key + '_ports']) for key in ('A', 'T', 'U')]
    need(A == (0, 7, 20, 27, 36, 46, 57, 111), 'A ports')
    need(T == (21, 37, 47, 76, 81, 87, 92, 110), 'T ports')
    need(U == tuple(p for p in range(112) if p not in A + T), 'U ports')
    for ports, norm in ((A, 4), (T, 4), (U, 48), (tuple(range(112)), 56)):
        need(all(sum(R[i][p] * R[j][p] for p in ports) == norm * (i == j)
                 for i in range(8) for j in range(8)), 'centre Gram identity')
    routes = {}
    registry = source['map_registry']
    for stage in range(1, 9):
        for p in range(112):
            events = [e for e in source['programs']['F_' + str(stage)]
                      if e[0] == 'cover_map' and e[1] == ['L', p]]
            need(len(events) >= 2, 'actual completed X route')
            record = registry[events[0][2]]
            g = tuple(record['owner_right_matrix_columns'])
            need(product(g, g) == AXES, 'route involution')
            need(all((g[i] & g[j]).bit_count() % 2 == (i == j)
                     for i in range(73) for j in range(73)), 'route orthogonality')
            first = 8 * stage + 1
            basis = g[first:first + 8]
            need(all(v < 512 for v in basis), 'local chart basis')
            normals = [q for q in range(1, 512)
                       if all((q & v).bit_count() % 2 == 0 for v in basis)]
            need(len(normals) == 1 and normals[0].bit_count() % 2 == 1, 'odd normal')
            q = normals[0]
            need(action(g, q) == q, 'normal fixed by route')
            shift = record['payload_translation_at_identity_owner']
            need(shift == lift(g, 9 + 8 * stage), 'registered accumulated lift')
            routes[stage, p] = dict(g=g, shift=shift, q=q, registry=events[0][2])
            if stage > 1:
                need(q == routes[1, p]['q'], 'stage-independent port normal')
    for p in A + T:
        for sign in ('positive_', 'inverse_'):
            need(source['native_line_recipes'][sign + str(p)]['label'] == routes[1, p]['q'],
                 'native selected-line binding')
    return source, R, A, T, U, routes


def rowadd(left, right, coefficient=Q(1)):
    result = dict(left)
    for key, value in right.items():
        v = result.get(key, Q(0)) + coefficient * value
        if v:
            result[key] = v
        else:
            result.pop(key, None)
    return result


def rowscale(row, coefficient):
    return {key: coefficient * value for key, value in row.items() if coefficient * value}


def route(row, letter):
    if letter is None:
        return dict(row)
    result = {}
    for (source, word), coefficient in row.items():
        reduced = word[1:] if word and word[0] == letter else (letter,) + word
        key = source, reduced
        result[key] = result.get(key, Q(0)) + coefficient
    return {key: value for key, value in result.items() if value}


def query(bank, ports, R, stage):
    answer = []
    for k in range(8):
        row = {}
        for p in ports:
            if R[k][p]:
                row = rowadd(row, route(bank[p], (stage, p) if stage else None), R[k][p])
        answer.append(row)
    return answer


def inject(values, ports, R, stage):
    answer = {}
    for p in ports:
        row = {}
        for k in range(8):
            if R[k][p]:
                row = rowadd(row, values[k], R[k][p] / 4)
        answer[p] = route(row, (stage, p) if stage else None)
    return answer


def forward(x, y, R, A, T, U, stage=0):
    f = query(x, range(112), R, stage)
    c = query(x, T, R, stage)
    target = inject(f, U + T, R, stage)
    xx = {p: rowadd(x[p], target[p], -1) for p in U}
    xx.update(inject(c, A, R, stage))
    xx.update({p: target[p] for p in T})
    yy = {p: rowadd(y[p], xx[p]) for p in U}
    yy.update({p: rowadd(rowadd(x[p], y[p]), xx[p], -1) for p in A + T})
    return xx, yy


def backward(x, y, R, A, T, U, stage=1, future_stage=2):
    u = dict(y)
    future = inject(query(y, U + T, R, future_stage), A, R, future_stage)
    for p in A:
        u[p] = rowadd(u[p], future[p])
    a = query(x, T, R, stage)
    b = query(u, range(112), R, stage)
    k = inject(a, U, R, stage)
    pt11 = inject([rowadd(b[j], a[j], 11) for j in range(8)], T, R, stage)
    pt12 = inject([rowadd(b[j], a[j], 12) for j in range(8)], T, R, stage)
    yy = {p: u[p] for p in A}
    yy.update({p: rowadd(y[p], k[p]) for p in U})
    yy.update({p: rowadd(u[p], pt11[p], -1) for p in T})
    xx = {p: rowadd(x[p], y[p], -1) for p in U}
    xx.update({p: rowadd(rowadd(x[p], y[p]), u[p], -1) for p in A})
    xx.update(pt12)
    return xx, yy


def inverse_forward(x1, y1, R, A, T, U, stage=0):
    f = query(x1, T, R, stage)
    c = query(x1, A, R, stage)
    correction = inject(f, U, R, stage)
    x = {p: rowadd(x1[p], correction[p]) for p in U}
    zquery = query(x, U, R, stage)
    a = [rowadd(rowadd(f[j], zquery[j], -1), c[j], -1) for j in range(8)]
    x.update(inject(a, A, R, stage))
    x.update(inject(c, T, R, stage))
    y = {p: rowadd(y1[p], x1[p], -1) for p in U}
    y.update({p: rowadd(rowadd(x1[p], y1[p]), x[p], -1) for p in A + T})
    return x, y


def reduction_gates(matrix, ports):
    matrix = deepcopy(matrix)
    gates = []

    def add(i, j, c):
        if c:
            matrix[i] = [a + c * b for a, b in zip(matrix[i], matrix[j])]
            gates.append(dict(op='add', dst='X' + str(ports[i]), src='X' + str(ports[j]), c=str(c)))

    def scale(i, c):
        if c != 1:
            need(abs(c.numerator) & (abs(c.numerator) - 1) == 0 and
                 c.denominator & (c.denominator - 1) == 0, 'dyadic-unit pivot')
            matrix[i] = [c * a for a in matrix[i]]
            gates.append(dict(op='scale', field='X' + str(ports[i]), c=str(c)))

    for j in range(8):
        pivot = next(i for i in range(j, 8) if matrix[i][j])
        if pivot != j:
            add(j, pivot, Q(1))
            add(pivot, j, Q(-1))
            add(j, pivot, Q(1))
            scale(pivot, Q(-1))
        scale(j, 1 / matrix[j][j])
        for i in range(8):
            if i != j:
                add(i, j, -matrix[i][j])
    need(matrix == [[Q(i == j) for j in range(8)] for i in range(8)], 'minor reduction')
    return gates


def inverse_gates(gates):
    result = []
    for gate in reversed(gates):
        e = dict(gate)
        e['c'] = str(-Q(e['c']) if e['op'] == 'add' else 1 / Q(e['c']))
        result.append(e)
    return result


def x_inverse_gates(R, A, T, U, routes, stage):
    word = []

    def emit(op, **fields):
        word.append(dict(op=op, **fields))

    if stage:
        for p in range(112):
            record = routes[stage, p]
            emit('map', field='X' + str(p), letter=[stage, p], g=list(record['g']), shift=record['shift'])
    reduction_A = reduction_gates([[R[k][p] for p in A] for k in range(8)], A)
    reduction_T = reduction_gates([[R[k][p] for p in T] for k in range(8)], T)
    word.extend(inverse_gates(reduction_A))
    word.extend(inverse_gates(reduction_T))
    for p in U:
        for k in range(8):
            if R[k][p]:
                emit('add', dst='X' + str(p), src='X' + str(T[k]), c=str(R[k][p] / 4))
    for ap, tp in zip(A, T):
        emit('add', dst='X' + str(ap), src='X' + str(tp), c='1')
        emit('add', dst='X' + str(tp), src='X' + str(ap), c='-1')
        emit('add', dst='X' + str(ap), src='X' + str(tp), c='1')
        emit('scale', field='X' + str(tp), c='-1')
    for k, p in enumerate(A):
        for u in U:
            if R[k][u]:
                emit('add', dst='X' + str(p), src='X' + str(u), c=str(-R[k][u]))
        emit('add', dst='X' + str(p), src='X' + str(T[k]), c='-1')
    word.extend(reduction_A)
    word.extend(reduction_T)
    if stage:
        for p in range(112):
            record = routes[stage, p]
            emit('map', field='X' + str(p), letter=[stage, p], g=list(record['g']),
                 shift=action(record['g'], record['shift']))
    return word


def make_word(R, A, T, U, routes, stage=0):
    capture, repair = [], []

    def emit(op, **fields):
        repair.append(dict(op=op, **fields))

    for p in A + T:
        capture.append(dict(op='clear', field='R' + str(p), frame='old'))
        capture.append(dict(op='add', dst='R' + str(p), src='X' + str(p), c='1'))
        emit('stage', field='R' + str(p), sign=1, rank=8, stage=stage + 1)
    for p in range(112):
        emit('line', field='Y' + str(p), port=p, sign=1, rank=1)
    for p in A + T:
        emit('add', dst='Y' + str(p), src='X' + str(p), c='1')
        emit('add', dst='X' + str(p), src='R' + str(p), c='1')
        emit('add', dst='R' + str(p), src='X' + str(p), c='-1')
        emit('add', dst='X' + str(p), src='R' + str(p), c='1')
        emit('clear', field='R' + str(p), frame='identity')
    for prefix, ports in (('Y', U), ('X', T)):
        for p in ports:
            record = routes[stage + 1, p]
            emit('map', field=prefix + str(p), letter=[stage + 1, p], g=list(record['g']), shift=record['shift'])
    emit('private_begin')
    for k in range(8):
        emit('clear', field='C', frame='current')
        for p in T:
            if R[k][p]:
                emit('add', dst='C', src='X' + str(p), c=str(R[k][p]))
        for p in U:
            if R[k][p]:
                emit('add', dst='Y' + str(p), src='C', c=str(-R[k][p] / 4))
    emit('clear', field='C', frame='identity')
    emit('private_end')
    for prefix, ports in (('X', T), ('Y', U)):
        for p in ports:
            record = routes[stage + 1, p]
            emit('map', field=prefix + str(p), letter=[stage + 1, p], g=list(record['g']),
                 shift=action(record['g'], record['shift']))
    for p in U:
        emit('add', dst='X' + str(p), src='Y' + str(p), c='1')
        emit('add', dst='Y' + str(p), src='X' + str(p), c='-1')
    repair.extend(x_inverse_gates(R, A, T, U, routes, stage))
    for p in A + T:
        emit('add', dst='Y' + str(p), src='X' + str(p), c='-1')
    for p in range(112):
        emit('line', field='Y' + str(p), port=p, sign=-1, rank=1)
    return capture, repair


def execute(word, rows, frames, routes, allowed_records, stage=0):
    private = False
    old = tuple((v, 1) for v in AXES[:9 + 8 * stage])
    current = tuple((v, 1) for v in AXES[:17 + 8 * stage])
    for at, e in enumerate(word):
        op = e['op']
        if op == 'clear':
            f = e['field']
            need(f in allowed_records or f == 'C', 'borrowed clear')
            need(f != 'C' or private, 'private clear outside its owner body')
            rows[f] = {} if not e.get('keep_dirty') else rows[f]
            frames[f] = {'identity': (), 'old': old, 'current': current}[e['frame']]
        elif op == 'add':
            dst, src = e['dst'], e['src']
            need(phase(frames[dst]) == phase(frames[src]), 'ADD frame mismatch at ' + str(at))
            need('C' not in (dst, src) or private, 'scratch outside its owner body')
            rows[dst] = rowadd(rows[dst], rows[src], Q(e['c']))
        elif op == 'scale':
            c = Q(e['c'])
            need(c and abs(c.numerator) & (abs(c.numerator) - 1) == 0 and
                 c.denominator & (c.denominator - 1) == 0, 'nonunit scale')
            rows[e['field']] = rowscale(rows[e['field']], c)
        elif op == 'line':
            need(e['rank'] == 1 and e['sign'] in (-1, 1), 'line primitive')
            frames[e['field']] += ((routes[1, e['port']]['q'], e['sign']),)
        elif op == 'stage':
            need(e['rank'] == 8 and e['sign'] in (-1, 1), 'stage primitive')
            first = 8 * e['stage'] + 1
            frames[e['field']] += tuple((v, e['sign']) for v in AXES[first:first + 8])
        elif op == 'map':
            f, letter = e['field'], tuple(e['letter'])
            need(tuple(e['g']) == routes[letter]['g'], 'route owner columns')
            frames[f] = transport(frames[f], tuple(e['g']), e['shift'])
            rows[f] = route(rows[f], letter)
        elif op == 'private_begin':
            need(not private, 'nested private body')
            private = True
        elif op == 'private_end':
            need(private and not rows['C'] and phase(frames['C']) == phase(()), 'private cleanup')
            private = False
        else:
            raise ValueError('unknown new event: ' + op)
    need(not private, 'unfinished private body')


def unit_bank(prefix):
    return {p: {(prefix + str(p), ()): Q(1)} for p in range(112)}


def replay(capture, repair, R, A, T, U, routes, stage=0):
    x1, y1 = unit_bank('x1:'), unit_bank('y1:')
    old = tuple((v, 1) for v in AXES[:9 + 8 * stage])
    current = tuple((v, 1) for v in AXES[:17 + 8 * stage])
    rows = {'X' + str(p): dict(x1[p]) for p in range(112)}
    rows.update({'Y' + str(p): dict(y1[p]) for p in range(112)})
    frames = {'X' + str(p): old for p in range(112)}
    frames.update({'Y' + str(p): old + ((routes[1, p]['q'], -1),) for p in range(112)})
    records = {'R' + str(p) for p in A + T}
    for f in records | {'C'}:
        rows[f], frames[f] = {(f + ':dirty', ()): Q(1)}, ()
    execute(capture, rows, frames, routes, records, stage)
    xx, yy = backward(x1, y1, R, A, T, U, stage + 1, stage + 2)
    for p in range(112):
        rows['X' + str(p)], frames['X' + str(p)] = xx[p], current
        rows['Y' + str(p)], frames['Y' + str(p)] = yy[p], current + ((routes[1, p]['q'], -1),)
    execute(repair, rows, frames, routes, records, stage)
    expected_x, expected_y = inverse_forward(x1, y1, R, A, T, U, stage)
    for p in range(112):
        need(rows['X' + str(p)] == expected_x[p], 'X content: ' + str(p))
        need(rows['Y' + str(p)] == expected_y[p], 'Y content: ' + str(p))
        need(phase(frames['X' + str(p)]) == phase(current), 'X output frame')
        need(phase(frames['Y' + str(p)]) == phase(current + ((routes[1, p]['q'], -1),)), 'Y output frame')
    for f in records | {'C'}:
        need(not rows[f] and phase(frames[f]) == phase(()), 'owned retirement: ' + f)
    need(all(all(letter[0] == stage for letter in term[1])
             for p in range(112) for term in rows['X' + str(p)]), 'past-route closure')
    need(all(all(letter[0] == stage for letter in term[1])
             for p in range(112) for term in rows['Y' + str(p)]), 'past-route closure')
    form = {f: [[source, list(word), str(c)] for (source, word), c in sorted(row.items())]
            for f, row in sorted(rows.items())}
    return digest(encoded(form))


def scalar_price(word):
    total, counts = 0, Counter()
    for e in word:
        op = e['op']
        counts[op] += 1
        if op == 'clear':
            total += 2
        elif op in ('add', 'scale'):
            c = Q(e['c'])
            a, b = abs(c.numerator), c.denominator
            need(a and b & (b - 1) == 0, 'dyadic scalar coefficient')
            if op == 'add':
                total += 2 * (2 + a.bit_length() + a.bit_count() + b.bit_length() - 1)
            else:
                need(a & (a - 1) == 0, 'dyadic scalar unit')
                total += 2 * (abs(a.bit_length() - b.bit_length()) + (c < 0))
    ranks = Counter(e['rank'] for e in word if e['op'] in ('line', 'stage'))
    return dict(events=dict(sorted(counts.items())), scalar=total,
                native_profile={str(k): v for k, v in sorted(ranks.items())},
                native_mass=sum(k * v for k, v in ranks.items()),
                native_wrappers=2 * sum(ranks.values()), cover_maps=counts['map'])


def check_cocycle(routes):
    frame_checks = 0
    products = 0
    noncommuting = 0
    for stage in range(1, 9):
        for p in range(112):
            g = routes[stage, p]['g']
            for completed in range(stage, 9):
                size = 9 + 8 * completed
                need(all(g[i] < 1 << size for i in range(size)), 'accumulated subspace')
                eta = lift(g, size)
                need(eta == routes[stage, p]['shift'], 'later lift is the registered old lift')
                terms = tuple((v, 1) for v in AXES[:size])
                need(phase(transport(terms, g, eta)) == phase(terms), 'full accumulated phase')
                frame_checks += 1
            h = routes[1, (p + 1) % 112]['g']
            size = 9 + 8 * stage
            gh = product(g, h)
            need(lift(gh, size) == (lift(g, size) ^ action(g, lift(h, size))), 'translation cocycle')
            products += 1
            noncommuting += product(g, h) != product(h, g)
    return dict(actual_routes=896, accumulated_frame_checks=frame_checks,
                cocycle_product_checks=products, noncommuting_product_checks=noncommuting)


def native_lowering(routes):
    recipes = {}
    checked = 0
    for p in range(112):
        q = routes[1, p]['q']
        pivot = (q & -q).bit_length() - 1
        columns = (q,) + tuple(1 << j for j in range(9) if j != pivot) + AXES[9:]
        inverse9 = {action(columns, x): x for x in range(512)}
        need(len(inverse9) == 512, 'line wrapper is bijective')
        inverse_columns = tuple(inverse9[1 << j] for j in range(9)) + AXES[9:]
        need(product(columns, inverse_columns) == AXES and product(inverse_columns, columns) == AXES,
             'line wrapper inverse')
        for sign in (1, -1):
            for x in range(512):
                middle = action(inverse_columns, x)
                shift = q if sign == -1 else 0
                actual = {action(columns, middle) ^ shift: (1, 1),
                          action(columns, middle ^ 1) ^ shift: (1, -1)}
                expected = {x: (1, sign), x ^ q: (1, -sign)}
                need(actual == expected, 'signed Gaussian line kernel')
                checked += 1
        recipes['line_' + str(p)] = dict(rank=1, label=q, right_columns=list(inverse_columns),
                                         left_columns=list(columns), negative_left_translation=q,
                                         positive_left_translation=0, gaussian_denominator=2)
    for stage in range(1, 9):
        first = 8 * stage + 1
        columns = list(AXES)
        for j in range(8):
            columns[j], columns[first + j] = columns[first + j], columns[j]
        columns = tuple(columns)
        need(product(columns, columns) == AXES, 'rank-eight wrapper inverse')
        for x in range(256):
            need(action(columns, x) == x << first, 'rank-eight axis image')
        recipes['stage_' + str(stage)] = dict(rank=8, right_columns=list(columns),
                                             left_columns=list(columns), positive_left_translation=0)
    # The positive C8 kernel is a tensor product of the same eight line kernels.
    # Its coefficient depends only on the XOR difference. This checks all 256
    # differences, and hence all 65,536 source/target coefficients.
    coefficients = []
    for difference in range(256):
        re, im = 1, 0
        for j in range(8):
            sign = -1 if difference >> j & 1 else 1
            re, im = re - sign * im, sign * re + im
        coefficients.append([re, im])
        # An independent power expansion gives (1+i)^(8-w) (1-i)^w.
        w = difference.bit_count()
        re2, im2 = 1, 0
        for j in range(8):
            sign = 1 if j < 8 - w else -1
            re2, im2 = re2 - sign * im2, sign * re2 + im2
        need((re, im) == (re2, im2), 'rank-eight Gaussian coefficient')
    return recipes, dict(signed_rank_one_columns=checked, rank_eight_axis_images=8 * 256,
                          rank_eight_distinct_coefficients=256, rank_eight_full_coefficients=65536,
                          rank_eight_coefficient_sha256=digest(encoded(coefficients)))


def controls(capture, repair, R, A, T, U, routes):
    mutations = {}
    for name, op, last in [('missing_record_lift', 'stage', False), ('missing_Y_normalization', 'line', False),
                           ('missing_Y_return', 'line', True), ('missing_scratch_cleanup', 'clear', True)]:
        c, w = deepcopy(capture), deepcopy(repair)
        choices = [i for i, e in enumerate(w) if e['op'] == op and
                   (name != 'missing_scratch_cleanup' or e.get('field') == 'C')]
        del w[choices[-1] if last else choices[0]]
        mutations[name] = c, w
    c, w = deepcopy(capture), deepcopy(repair)
    c[0]['keep_dirty'] = True
    mutations['dirty_record_capture'] = c, w
    c, w = deepcopy(capture), deepcopy(repair)
    next(e for e in w if e['op'] == 'map')['shift'] = 0
    mutations['missing_accumulated_translation'] = c, w
    c, w = deepcopy(capture), deepcopy(repair)
    e = next(e for e in w if e['op'] == 'add' and e['src'] == 'C')
    e['c'] = str(-Q(e['c']))
    mutations['wrong_query_correction'] = c, w
    c, w = deepcopy(capture), deepcopy(repair)
    e = next(e for e in w if e['op'] == 'add' and e['dst'].startswith('Y') and e['src'].startswith('X'))
    e['c'] = '-1'
    mutations['wrong_selected_sum'] = c, w
    c, w = deepcopy(capture), deepcopy(repair)
    first = next(i for i, e in enumerate(w) if e['op'] == 'clear' and e.get('field', '').startswith('R'))
    del w[first]
    mutations['unretired_record'] = c, w
    errors = {}
    for name, (c, w) in mutations.items():
        try:
            replay(c, w, R, A, T, U, routes)
        except ValueError as error:
            errors[name] = str(error)
        else:
            raise ValueError('ineffective negative control: ' + name)
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    source, R, A, T, U, routes = load()
    capture, repair = make_word(R, A, T, U, routes)
    xx, yy = unit_bank('x:'), unit_bank('y:')
    fx, fy = forward(xx, yy, R, A, T, U)
    ix, iy = inverse_forward(fx, fy, R, A, T, U)
    need(ix == xx and iy == yy, 'all 224 original inputs through forward and inverse')
    ix, iy = inverse_forward(xx, yy, R, A, T, U)
    fx, fy = forward(ix, iy, R, A, T, U)
    need(fx == xx and fy == yy, 'both inverse orders')
    general_words, general_receipts = {}, {}
    for stage in range(1, 7):
        gc, gr = make_word(R, A, T, U, routes, stage)
        fx, fy = forward(xx, yy, R, A, T, U, stage)
        ix, iy = inverse_forward(fx, fy, R, A, T, U, stage)
        need(ix == xx and iy == yy, 'general forward inverse order')
        ix, iy = inverse_forward(xx, yy, R, A, T, U, stage)
        fx, fy = forward(ix, iy, R, A, T, U, stage)
        need(fx == xx and fy == yy, 'general inverse forward order')
        general_words[str(stage)] = dict(capture=gc, repair=gr,
                                         source_calls=['F_' + str(stage), 'B_' + str(stage + 1) + '_' + str(stage + 2)])
        general_receipts[str(stage)] = dict(operator_sha256=replay(gc, gr, R, A, T, U, routes, stage),
                                            invoice=scalar_price(gc + gr))
    native_recipes, native_checks = native_lowering(routes)
    word = dict(schema='qq16-first-pair-retirement-v1', certificate_sha256=SOURCE_SHA,
                source_call_hashes={name: digest(encoded(source['programs'][name])) for name in ('F_0', 'B_1_2')},
                capture_after_F0=capture, retained_call='B_1_2', repair_after_B1=repair)
    word_bytes = encoded(word)
    result = dict(status='PASS_LOCAL_FIRST_PAIR_RETIREMENT', source_sha256=SOURCE_SHA,
                  word_sha256=digest(word_bytes),
                  all_224_input_operator_rows_sha256=replay(capture, repair, R, A, T, U, routes),
                  formal_ring='rational linear combinations of reduced words in free involutions',
                  original_inputs=224, independent_post_F0_inputs=224, owned_dirty_records=16,
                  owned_local_scratch=1, borrowed_helpers_untouched_by_new_events=480,
                  inherited_calls='QQ16 F_0 and B_1_2 at the pinned source contract',
                  literal_scope='New capture and repair events only; unchanged QQ16 native cores are inherited.',
                  added_invoice=scalar_price(capture + repair),
                  capture_invoice=scalar_price(capture), repair_invoice=scalar_price(repair),
                  accumulated_lift=check_cocycle(routes),
                  native_lowering=native_checks, general_adjacent_F_B=general_receipts,
                  negative_controls=controls(capture, repair, R, A, T, U, routes),
                  open=['16 full-cover record storage and delivery', 'new recursive-child hosting',
                        'full-cover stream and address implementation', 'precision and tape invoice',
                        'all-stage controller and terminal assembly', 'complete supplier moment'])
    (args.out / 'RESTORATION-WORD.json').write_bytes(word_bytes + b'\n')
    (args.out / 'GENERAL-F-B-WORDS.json').write_bytes(encoded(general_words) + b'\n')
    (args.out / 'NATIVE-RECIPES.json').write_bytes(encoded(native_recipes) + b'\n')
    (args.out / 'RESTORATION-CHECKS.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
