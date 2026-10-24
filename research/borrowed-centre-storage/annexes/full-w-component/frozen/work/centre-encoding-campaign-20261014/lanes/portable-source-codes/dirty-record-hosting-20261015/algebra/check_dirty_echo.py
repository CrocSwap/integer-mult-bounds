"""Check an eight-donor echo on arbitrary data and donor columns.

Use the actual QQ16 matrix and keep ordered cover paths as free words.
This checks logical algebra. It does not admit a native owner schedule.
"""

from collections import Counter
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
from pathlib import Path
import shutil


HERE = Path(__file__).resolve().parent
ROOT = Path('/Users/aliromman/Projects/IntegerMultiplicationBounds')
LANES = ROOT/'work/centre-encoding-campaign-20261014/lanes'
SOURCE = LANES/'paired-package-review/upstream-followthrough-20261015'
A = (0, 7, 20, 27, 36, 46, 57, 111)
T = (21, 37, 47, 76, 81, 87, 92, 110)
V = A+T
U = tuple(p for p in range(112) if p not in V)
PINS = {}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path, expected=None, compressed=False):
    raw = path.read_bytes()
    digest = sha256(raw).hexdigest()
    if expected:
        need(digest == expected, 'Source pin: '+str(path))
    PINS[str(path.relative_to(ROOT))] = digest
    return gzip.decompress(raw) if compressed else raw


def add(a, b, c=Q(1)):
    result = dict(a)
    for key, value in b.items():
        result[key] = result.get(key, 0)+c*value
        if not result[key]:
            del result[key]
    return result


def scale(row, c):
    return {key: c*value for key, value in row.items() if c*value}


def move(row, stage, port):
    if stage == 0:
        return dict(row)
    letter = stage, port
    answer = {}
    for (source, path), value in row.items():
        path = path[1:] if path and path[0] == letter else (letter,)+path
        key = source, path
        answer[key] = answer.get(key, 0)+value
    return {key: value for key, value in answer.items() if value}


def basis(name):
    return {(name, ()): Q(1)}


def query(bank, ports, stage, matrix):
    values = [{} for _ in range(8)]
    for p in ports:
        row = move(bank[p], stage, p)
        for k in range(8):
            values[k] = add(values[k], row, matrix[k][p])
    return values


def scatter(values, ports, stage, matrix):
    answer = {}
    for p in ports:
        row = {}
        for k in range(8):
            row = add(row, values[k], matrix[k][p]/4)
        answer[p] = move(row, stage, p)
    return answer


def forward(x, y, matrix):
    response = scatter(query(x, range(112), 0, matrix), U+T, 0, matrix)
    xx = {p: add(x[p], response[p], -1) for p in U}
    xx.update(scatter(query(x, T, 0, matrix), A, 0, matrix))
    xx.update({p: response[p] for p in T})
    yy = {p: add(y[p], xx[p]) for p in U}
    yy.update({p: add(add(x[p], y[p]), xx[p], -1) for p in V})
    return xx, yy


def backward(x, y, matrix):
    u = dict(y)
    code = scatter(query(y, U+T, 2, matrix), A, 2, matrix)
    for p in A:
        u[p] = add(u[p], code[p])
    a, b = query(x, T, 1, matrix), query(u, range(112), 1, matrix)
    delta = scatter([add(aa, bb, -1) for aa, bb in zip(a, b)], T, 1, matrix)
    v = dict(u)
    for p in T:
        v[p] = add(v[p], delta[p])
    need(query(v, range(112), 1, matrix) == a, 'Exact B1 query exchange')
    response = scatter(a, U+T, 1, matrix)
    yy = dict(v)
    for p in U:
        yy[p] = add(yy[p], response[p])
    for p in T:
        yy[p] = add(yy[p], response[p], -12)
    xx = {p: add(x[p], y[p], -1) for p in U}
    xx.update({p: add(add(x[p], y[p]), yy[p], -1) for p in V})
    return xx, yy


def alias(x, y, matrix):
    f = query(x, range(112), 0, matrix)
    response = scatter(f, U+T, 0, matrix)
    result = {p: add(add(y[p], x[p]), response[p], -1) for p in U}
    result.update({p: add(add(x[p], y[p]), response[p], -1) for p in T})
    return result


def future_read(x, y, matrix):
    return scatter(query(alias(x, y, matrix), U+T, 2, matrix), A, 2, matrix)


def error_map(h, matrix):
    transferred = scatter(query(h, A, 0, matrix), T, 0, matrix)
    dx = {p: {} for p in range(112)}
    dy = {p: {} for p in range(112)}
    for p in A:
        dx[p], dy[p] = scale(h[p], -1), dict(h[p])
    for p in T:
        dx[p], dy[p] = transferred[p], scale(transferred[p], -1)
    return dx, dy


def serialize(rows):
    return [[name, [[source, [list(letter) for letter in path], str(c)]
                     for (source, path), c in sorted(row.items())]]
            for name, row in sorted(rows.items())]


def summary(rows):
    entries = [item for row in rows.values() for item in row.items()]
    return {'rows': len(rows), 'terms': len(entries),
            'distinct_source_columns': len({key[0] for key, _ in entries}),
            'maximum_route_word_length': max((len(key[1]) for key, _ in entries), default=0),
            'row_sha256': sha256(json.dumps(serialize(rows), separators=(',', ':')).encode()).hexdigest()}


def act(columns, vector):
    result = 0
    while vector:
        bit = vector & -vector
        result ^= columns[bit.bit_length()-1]
        vector ^= bit
    return result


def main():
    need(shutil.disk_usage(HERE).free >= 3*1024**3, 'Three GiB free')
    packet = json.loads(read(SOURCE/'base/research/joint-query/certificate.json.gz',
        'a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7', True))
    word = json.loads(read(SOURCE/'common-frame-results/COMMON-F-RESTORATION-WORD.json',
        'c1fa3fe3596d939bbc42c0a41ad0078b43b74dca51fa41d7e3407736af07a74e'))
    for name in ('RELATIVE-REUSE.md', 'CLEAN-IDLE-STORAGE.md'):
        read(LANES/'source-domain/carried-owner-reuse'/name)
    read(SOURCE/'COMMON-F-RESTORATION.md',
         '1b00422c2ba2dcf90ad37ebc7e5fd8e00c1e379f959ec2f6493f166a9a286db0')
    matrix = [[Q(row.get(str(p), 0)) for p in range(112)] for row in packet['R_rows']]
    for ports, gram in ((A, 4), (T, 4), (U, 48)):
        need(all(sum(matrix[i][p]*matrix[j][p] for p in ports) == gram*(i == j)
                 for i in range(8) for j in range(8)), 'Actual minor Gram')
    x = {p: basis('x:'+str(p)) for p in range(112)}
    y = {p: basis('y:'+str(p)) for p in range(112)}
    h = {p: basis('h:'+str(p)) for p in A}
    x1, y1 = forward(x, y, matrix)
    x2, y2 = backward(x1, y1, matrix)
    need(query(y2, range(112), 1, matrix) == query(x1, T, 1, matrix), 'T record source identity')
    rows = {'X'+str(p): x2[p] for p in range(112)}
    rows.update({'Y'+str(p): y2[p] for p in range(112)})
    rows.update({'R'+str(p): add(h[p], x1[p]) for p in A})
    rows['C'] = basis('scratch')

    # Run the new T block before any change to Y outside T.
    off = scatter(query(y2, U+A, 1, matrix), T, 1, matrix)
    for p in T:
        rows['Y'+str(p)] = add(rows['Y'+str(p)], rows['X'+str(p)])
        rows['X'+str(p)] = add(add(scale(rows['X'+str(p)], -1), rows['Y'+str(p)]), off[p])
        need(rows['X'+str(p)] == x1[p], 'T record recovered in place')
        need(rows['Y'+str(p)] == add(x[p], y[p]), 'T selected sum retained')

    repair = word['repair_after_B1']
    first_map = next(i for i, e in enumerate(repair) if e['op'] == 'map')
    need(first_map == 208, 'Frozen prefix boundary')
    prefix = repair[128:first_map]
    for at, p in enumerate(V):
        a, r, yy = 'X'+str(p), 'R'+str(p), 'Y'+str(p)
        expected = [dict(op='add', dst=yy, src=a, c='1'), dict(op='add', dst=a, src=r, c='1'),
                    dict(op='add', dst=r, src=a, c='-1'), dict(op='add', dst=a, src=r, c='1'),
                    dict(op='clear', field=r, frame='identity')]
        need(prefix[5*at:5*at+5] == expected, 'Literal selected exchange block')
    emitted = []
    for p in A:
        at = V.index(p)*5
        emitted.extend(prefix[at:at+4])
        emitted.append(dict(op='add', dst='R'+str(p), src='X'+str(p), c='1'))
    emitted += repair[first_map:]
    for e in emitted:
        op = e['op']
        if op == 'add':
            rows[e['dst']] = add(rows[e['dst']], rows[e['src']], Q(e['c']))
        elif op == 'scale':
            rows[e['field']] = scale(rows[e['field']], Q(e['c']))
        elif op == 'clear':
            need(e['field'] == 'C', 'No donor or data CLEAR')
            rows['C'] = {}
        elif op == 'map':
            stage, p = e['letter']
            rows[e['field']] = move(rows[e['field']], stage, p)
        else:
            need(op in ('private_begin', 'private_end'), 'Scalar tail event')
    xx = {p: rows['X'+str(p)] for p in range(112)}
    yy = {p: rows['Y'+str(p)] for p in range(112)}
    donors = {p: rows['R'+str(p)] for p in A}
    dx, dy = error_map(h, matrix)
    need(all(xx[p] == add(x[p], dx[p]) and yy[p] == add(y[p], dy[p]) for p in range(112)),
         'Exact data error E h')
    query_original = scatter(query(y1, U+T, 2, matrix), A, 2, matrix)
    need(all(donors[p] == add(h[p], query_original[p]) for p in A), 'Exact donor value h+Gx')
    need(alias(xx, yy, matrix) == {p: y1[p] for p in U+T}, 'Dirt-independent Y1 alias')
    need(all(not row for row in future_read(dx, dy, matrix).values()), 'G E equals zero')
    query_now = future_read(xx, yy, matrix)
    need(query_now == query_original, 'Cleanup query is unchanged by donor dirt')
    restored = {p: add(donors[p], query_now[p], -1) for p in A}
    need(restored == h, 'All eight arbitrary donor columns restored')
    ex, ey = error_map(restored, matrix)
    final_x = {p: add(xx[p], ex[p], -1) for p in range(112)}
    final_y = {p: add(yy[p], ey[p], -1) for p in range(112)}
    need(final_x == x and final_y == y and not rows['C'], 'All 224 data columns and scratch')

    # A future-owner path cannot be made from routes which fix E2 pointwise.
    routes = {}
    for stage in (1, 2):
        for p in range(112):
            event = next(e for e in packet['programs']['F_'+str(stage)]
                         if e[0] == 'cover_map' and e[1] == ['L', p])
            routes[stage, p] = packet['map_registry'][event[2]]['owner_right_matrix_columns']
    need(all(len(route) == 73 and all(act(route, act(route, 1 << j)) == 1 << j
             for j in range(73)) for route in routes.values()), 'Actual owner routes are involutions')
    need(all(act(routes[1, p], 1 << j) == 1 << j for p in range(112) for j in range(17, 25)),
         'Every stage-1 route fixes E2')
    witness = None
    for a in A:
        for p in U:
            coefficient = sum(matrix[k][a]*matrix[k][p]/4 for k in range(8))
            if not coefficient:
                continue
            for j in range(17, 25):
                image = act(routes[2, a], act(routes[2, p], 1 << j))
                if image != 1 << j:
                    key = 'y:'+str(p), ((2, a), (2, p))
                    need(query_now[a].get(key) == coefficient, 'Actual future read coefficient')
                    witness = {'donor_A_port': a, 'source_Y_U_port': p, 'coefficient': str(coefficient),
                               'owner_word': [[2, a], [2, p]], 'E2_unit_axis': j, 'image': image}
                    break
            if witness:
                break
        if witness:
            break
    need(witness is not None, 'Future-read route witness')
    controls = {
        'omitted_future_read_does_not_restore_donors': donors != h,
        'dirty_record_as_clean_changes_data': xx != x or yy != y,
        'old_record_erase_is_not_cleanup': any(add(donors[p], x1[p], -1) != h[p] for p in A),
        'cleared_borrowed_donors_lose_arbitrary_columns': any(h[p] for p in A)}
    need(all(controls.values()), 'Negative controls')
    result = {'status': 'PASS_EIGHT_DIRTY_DONOR_ECHO_ALGEBRA', 'source_pins': PINS,
              'source_data_columns': 224, 'arbitrary_donor_columns': 8, 'arbitrary_scratch_columns': 1,
              'donor_CLEAR_operations': 0, 'additional_owned_output_banks': 0,
              'literal_tail_events_replayed': len(emitted), 'T_records_needed': 0,
              'route_checks': {'actual_involutions': len(routes), 'ambient_axes': 73,
                               'stage1_routes_fix_every_E2_axis': True},
              'before_cleanup': {'data': 'z+E h', 'donors': 'h+G z'},
              'Schur_identity': 'G E=0; I-G E=I',
              'inverse': ['h=donors-G data', 'z=data-E h'],
              'cleanup_unique_linear_read': 'A(donors)+L(data)=h for all z,h implies A=I and L=-G.',
              'future_read': summary(query_now), 'donor_error_map': summary({**{'X'+str(p):dx[p] for p in range(112)},
                   **{'Y'+str(p):dy[p] for p in range(112)}}),
              'no_stage2_read_obstruction_witness': witness, 'negative_controls': controls,
              'scope': 'Exact routed logical algebra under a common completed frame and a matched donor transport. No native lowering, owner allocation, phase transport through a delay, precision, full invoice, supplier or kappa claim.',
              'required_reads': ['R1 Y2 over all112 current Y fields, before Y offT is changed',
                  'The actual F0-chart query R0 X on final data',
                  'Y1_U=Y_U+X_U-K0U R0 X and Y1_T=X_T+Y_T-P0T R0 X',
                  'N2 Y1_offA=P2A R2(U union T)Y1_offA, in the actual future owner chart',
                  'J0 h=P0T ell0A h for the final selected compensation'],
              'not_claimed': ['Free clean access to a dirty cache', 'A native read from the wrong frame',
                  'Unchanged donor values after unmatched native advances', 'A scheduler for delayed cleanup']}
    path = HERE/'ALGEBRA.json'
    path.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    (HERE/'FUTURE-READ-ROWS.json').write_text(json.dumps(serialize(query_now), separators=(',', ':'))+'\n')
    print(json.dumps({'status': result['status'], 'receipt_sha256':sha256(path.read_bytes()).hexdigest(),
                      'future_read':result['future_read'], 'route_witness':witness}))


if __name__ == '__main__':
    main()
