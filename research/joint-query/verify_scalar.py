"""Rebuild the QQ16 scalar blocks and check the complete local maps.

This code follows the independent QQ16 scalar review. It does not import
an emitter. The retained source loader has a separate sparse replay.
New code is Apache-2.0. Research and verification used Codex assistance.
"""

from fractions import Fraction as F


A = [0, 7, 20, 27, 36, 46, 57, 111]
T = [21, 37, 47, 76, 81, 87, 92, 110]
U = [p for p in range(112) if p not in A + T]


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def add(left, right, value=F(1)):
    result = left.copy()
    for j, x in right.items():
        x = result.get(j, 0) + value * x
        if x:
            result[j] = x
        else:
            result.pop(j, None)
    return result


def multiply(left, right):
    result = []
    for row in left:
        out = {}
        for j, value in row.items():
            out = add(out, right[j], value)
        result.append(out)
    return result


def rational(matrix):
    return [{int(j): F(x) for j, x in row.items()} for row in matrix]


def register(token):
    kind, i = token
    need(kind in ('L', 'C') and 0 <= i < (704 if kind == 'L' else 8),
         'Declared scalar register')
    return i + (704 if kind == 'C' else 0)


def scalar_cost(gate):
    if gate[0] == 'clear':
        return 2
    value = F(gate[3], gate[4]) if gate[0] == 'add' else F(gate[2], gate[3])
    a, b = abs(value.numerator), value.denominator
    need(a and b & (b - 1) == 0, 'Nonzero dyadic coefficient')
    if gate[0] == 'add':
        return 2 * (2 + a.bit_length() + a.bit_count() + b.bit_length() - 1)
    need(gate[0] == 'scale' and a & (a - 1) == 0, 'Signed power-of-two SCALE')
    return 2 * (abs(a.bit_length() - b.bit_length()) + (value < 0))


def replay(events, initial):
    rows = [row.copy() for row in initial]
    for event in events:
        if event[0] != 'scalar':
            need(event[0] in ('climb', 'phase', 'adapter', 'residual_adapter'),
                 'Known retained event')
            continue
        gate = event[1]
        at = register(gate[1])
        if gate[0] == 'clear':
            need(at >= 704, 'Only owned private contents are cleared')
            rows[at] = {}
        elif gate[0] == 'add':
            source = register(gate[2])
            need(source != at, 'Distinct scalar source and target')
            rows[at] = add(rows[at], rows[source], F(gate[3], gate[4]))
        else:
            need(gate[0] == 'scale', 'Known scalar gate')
            rows[at] = {j: x * F(gate[2], gate[3]) for j, x in rows[at].items()}
    return rows


def event(kind, at, source=None, value=F(1)):
    value = F(value)
    reg = lambda p: ['C', p - 704] if p >= 704 else ['L', p]
    gate = [kind, reg(at)]
    if kind == 'add':
        gate += [reg(source), value.numerator, value.denominator]
    elif kind == 'scale':
        gate += [value.numerator, value.denominator]
    else:
        need(kind == 'clear', 'Known emitted scalar gate')
    return ['scalar', gate, 'chart-bound-by-native-recipe']


def rebuild(r):
    """Derive each coefficient from the actual centre matrix R."""
    k = [{i: row[p] / 4 for i, row in enumerate(r) if p in row} for p in range(112)]
    minor = lambda ports: [{j: row[p] for j, p in enumerate(ports) if p in row} for row in r]
    restrict = lambda ports: [{p: v for p, v in row.items() if p in ports} for row in r]
    ra, rt, ru = minor(A), minor(T), restrict(U)
    ka, kt = [k[p] for p in A], [k[p] for p in T]
    identity = [{i: F(1)} for i in range(8)]
    need(multiply(ra, ka) == multiply(ka, ra) == identity, 'Both A minor inverse orders')
    need(multiply(rt, kt) == multiply(kt, rt) == identity, 'Both T minor inverse orders')
    need(multiply(ru, k) == [{i: F(12)} for i in range(8)], 'R_U K_U = 12I')
    need(multiply(r, k) == [{i: F(14)} for i in range(8)], 'RK = 14I')
    b = multiply(kt, restrict([p for p in range(112) if p not in T]))
    c, ci, d = multiply(ka, rt), multiply(kt, ra), multiply(k, rt)
    nrows = multiply(ka, restrict([p for p in range(112) if p not in A]))
    n = [nrows[A.index(p)] if p in A else {} for p in range(112)]
    need(multiply(n, n) == [{} for _ in range(112)], 'Future query shear squares to zero')
    need(multiply(c, ci) == multiply(ci, c) == identity, 'Selected change of basis')
    need(multiply(b, [d[p] if p in U else {} for p in range(112)]) ==
         [{i: F(12)} for i in range(8)], 'BD = 12I')
    copies = {'B': [], 'F': []}
    typed = {'B': [], 'F': []}
    for j, p in enumerate(A):
        for side in ('B', 'F'):
            begin = [event('clear', 704), event('add', 704, 112 + p if side == 'B' else p,
                                               1 if side == 'B' else -1)]
            middle = [event('add', 704, T[i], -v if side == 'B' else v)
                      for i, v in sorted(c[j].items())]
            end = [event('add', p if side == 'B' else 112 + p, 704), event('clear', 704)]
            copies[side] += begin + middle + end
            typed[side].append({'target_port': p,
                               'same_port_Y_read' if side == 'B' else 'same_port_X_read': begin,
                               'current_normalized_X_T_read' if side == 'B' else 'current_completed_X_T_read': middle,
                               'target_add_and_clear': end})
    swaps = []
    for p in T:
        swaps += [event('add', p, 112 + p), event('add', 112 + p, p, -1),
                  event('add', p, 112 + p), event('scale', 112 + p, value=-1)]
    bblocks = {
        'A_input_copies': copies['B'],
        'future_E_t': [event('add', 112 + p, 112 + q, v) for p, row in zip(A, nrows) for q, v in sorted(row.items())],
        'Y_U_from_X_T': [event('add', 112 + p, T[j], v) for p in U for j, v in sorted(d[p].items())],
        'eight_unsigned_swaps': swaps,
        'Y_T_query_subtract': [event('add', 112 + p, 112 + q, -v) for p, row in zip(T, b) for q, v in sorted(row.items())],
    }
    au = multiply(ka, ru)
    fblocks = {
        'X_A_fused_query': [event('add', p, T[j], 2*v) for p, row in zip(A, c) for j, v in sorted(row.items())]
            + [event('add', p, q, v) for p, row in zip(A, au) for q, v in sorted(row.items())],
        'X_T_query_subtract': [event('add', p, A[j], -v) for p, row in zip(T, ci) for j, v in sorted(row.items())],
        'X_A_restore_selected': [event('add', p, T[j], v) for p, row in zip(A, c) for j, v in sorted(row.items())],
        'X_T_sign': [event('scale', p, value=-1) for p in T],
        'X_U_query_subtract': [event('add', p, T[j], -v) for p in U for j, v in sorted(d[p].items())],
        'A_output_copies': copies['F'],
    }
    return {'R': r, 'K': k, 'N': n, 'R_U': ru, 'B_blocks': bblocks, 'F_blocks': fblocks,
            'B_typed_A_copies': typed['B'], 'F_typed_A_copies': typed['F'],
            'B_order': list(bblocks), 'F_order': list(fblocks)}


def formulas(scalar):
    r, k, n, ru = (scalar[key] for key in ('R', 'K', 'N', 'R_U'))
    query = lambda ports, x: multiply([{p: v for p, v in row.items() if p in ports} for row in r], x)

    def backward(data, inverse=False):
        x, y = data[:112], data[112:224]
        if inverse:
            a = multiply(r, y)
            b = [add(row, ar, -12) for row, ar in zip(query(T, x), a)]
            ka, kb = multiply(k, a), multiply(k, b)
            ey = [add(y[p], ka[p], -1) if p in U else
                  add(add(y[p], kb[p]), ka[p], 11) if p in T else y[p].copy() for p in range(112)]
            yy = [add(row, extra, -1) for row, extra in zip(ey, multiply(n, ey))]
            xx = [add(x[p], yy[p]) if p in U else
                  add(add(x[p], yy[p], -1), ey[p]) if p in A else ka[p] for p in range(112)]
        else:
            ey = [add(row, extra) for row, extra in zip(y, multiply(n, y))]
            ka, kb = multiply(k, query(T, x)), multiply(k, multiply(r, ey))
            xx = [add(x[p], y[p], -1) if p in U else
                  add(add(x[p], y[p]), ey[p], -1) if p in A else add(kb[p], ka[p], 12)
                  for p in range(112)]
            yy = [add(y[p], ka[p]) if p in U else ey[p] if p in A else
                  add(add(ey[p], kb[p], -1), ka[p], -11) for p in range(112)]
        return xx + yy

    def forward(data, inverse=False):
        x, y = data[:112], data[112:224]
        if inverse:
            f, c = query(T, x), query(A, x)
            kf, kc = multiply(k, f), multiply(k, c)
            xx = [add(x[p], kf[p]) if p in U else kc[p] if p in T else x[p].copy()
                  for p in range(112)]
            a = [add(add(fr, cr, -1), ur, -1) for fr, cr, ur in zip(f, c, multiply(ru, xx))]
            ka = multiply(k, a)
            for p in A:
                xx[p] = ka[p]
            yy = [add(y[p], x[p], -1) if p in U else add(add(y[p], xx[p], -1), x[p])
                  for p in range(112)]
        else:
            kf, kc = multiply(k, multiply(r, x)), multiply(k, query(T, x))
            xx = [add(x[p], kf[p], -1) if p in U else kc[p] if p in A else kf[p]
                  for p in range(112)]
            yy = [add(y[p], xx[p]) if p in U else add(add(y[p], x[p]), xx[p], -1)
                  for p in range(112)]
        return xx + yy

    return {'B': backward, 'F': forward}


def verify(data, packet, scalar):
    need(packet['R_rows'] and rational(packet['R_rows']) == scalar['R'] == data['R'], 'Actual R source')
    need(rational(packet['K_rows']) == scalar['K'], 'K = R transpose / 4')
    need((packet['A_ports'], packet['T_ports'], packet['U_ports']) == (A, T, U), 'Exact selected sets')
    need(packet['core_words'] == data['clean_programs'], 'Both retained core words')
    basis = [{i: F(1)} for i in range(712)]
    contract = formulas(scalar)
    cores = data['clean_programs']
    blocks = {side: scalar[side + '_blocks'] for side in ('B', 'F')}
    wrappers = {side: sum(blocks[side].values(), []) for side in ('B', 'F')}
    programs = {'B': wrappers['B'] + cores['backward'], 'F': cores['forward'] + wrappers['F']}
    results = {}
    for side, events in programs.items():
        result = replay(events, basis)
        need(result[:224] == contract[side](basis[:224]), 'Complete data map: ' + side)
        need(result[224:704] == basis[224:704] and result[704:] == [{} for _ in range(8)],
             'All borrowed helpers restore and all private outputs are zero')
        need(contract[side](result[:224], True) == basis[:224], 'Left data inverse: ' + side)
        need(contract[side](contract[side](basis[:224], True)) == basis[:224], 'Right data inverse: ' + side)
        for p in A + T:
            need(add(result[p], result[112+p]) == {p: F(1), 112+p: F(1)}, 'Selected pair sum')
        total = sum(scalar_cost(e[1]) for e in events if e[0] == 'scalar')
        need(total == (214986 if side == 'B' else 211210), 'Complete scalar invoice')
        results[side] = {'formal_input_columns': 712, 'inverse_orders': 2, 'conserved_pair_sums': 16,
                         'arbitrary_helpers_restored': 480, 'owned_private_outputs_zero': 8,
                         'scalar_real_primitives': total,
                         'block_costs': {name: sum(scalar_cost(e[1]) for e in block)
                                         for name, block in blocks[side].items()}}
    # Composition is on data. The owned private contents are discarded.
    composite = replay(programs['B'] + programs['F'], basis)
    restored = contract['B'](contract['F'](composite[:224], True), True)
    need(restored == basis[:224], 'The algebraic inverse of F after B')
    opposite = replay(programs['F'] + programs['B'], basis)
    need(contract['F'](contract['B'](opposite[:224], True), True) == basis[:224],
         'The algebraic inverse of B after F')
    b, f = blocks['B'], blocks['F']
    tail = sum([b[key] for key in ('Y_U_from_X_T', 'eight_unsigned_swaps', 'Y_T_query_subtract')], [])
    fbody = wrappers['F'][:-len(f['A_output_copies'])]
    mutations = {
        'late_original_Y_copy': b['future_E_t'] + b['A_input_copies'] + tail + cores['backward'],
        'early_T_query': b['A_input_copies'] + b['future_E_t'] + b['Y_T_query_subtract']
            + b['Y_U_from_X_T'] + b['eight_unsigned_swaps'] + cores['backward'],
        'early_F_source_update': fbody + cores['forward'] + f['A_output_copies'],
        'early_F_target_copy': cores['forward'] + f['A_output_copies'] + fbody,
        'missing_owned_clear': programs['B'][1:],
    }
    for name, events in mutations.items():
        side = 'F' if '_F_' in name else 'B'
        need(replay(events, basis)[:224] != contract[side](basis[:224]), 'Mutation must fail: ' + name)
    try:
        scalar_cost(['add', ['L', 0], ['L', 1], 1, 13])
    except ValueError:
        pass
    else:
        raise ValueError('Odd denominator accepted by the dyadic cost ledger')
    return {'status': 'PASS_QQ16_SCALAR_MAPS', 'orientations': results,
            'data_compositions_with_algebraic_inverses': 2,
            'timing_and_private_controls_rejected': list(mutations), 'odd_denominator_control': 'REJECTED',
            'scope': 'Exact common-chart scalar words and algebraic data inverses. B and F are not inverse circuits. Native access to the algebraic inverses and global controller closure are not established.'}
