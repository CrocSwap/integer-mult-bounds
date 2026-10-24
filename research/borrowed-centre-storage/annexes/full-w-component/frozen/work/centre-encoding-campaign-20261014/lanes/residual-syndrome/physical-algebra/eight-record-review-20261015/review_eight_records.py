"""Check the eight-record word without producer imports.

Keep different ordered owner routes as different free words. Check each
physical frame as a quadratic phase over Z/4Z.
"""

from collections import Counter
from fractions import Fraction
from functools import lru_cache
import gzip
from hashlib import sha256
import json
from pathlib import Path
import shutil


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[2]
INPUT = LANES / 'portable-source-codes/dirty-record-hosting-20261015'
BASE = LANES / 'paired-package-review/upstream-followthrough-20261015'
A = (0, 7, 20, 27, 36, 46, 57, 111)
T = (21, 37, 47, 76, 81, 87, 92, 110)
U = tuple(p for p in range(112) if p not in A + T)
ALL = tuple(range(112))
AXES = tuple(1 << i for i in range(73))
OLD = tuple((v, 1) for v in AXES[:9])
FULL = tuple((v, 1) for v in AXES[:17])
PINS = {}


def require(test, message):
    if not test:
        raise ValueError(message)


def pinned(path, digest):
    raw = path.read_bytes()
    require(sha256(raw).hexdigest() == digest, 'Source hash: ' + str(path))
    PINS[str(path.relative_to(LANES))] = digest
    return raw


def plus(row, other, coefficient=Fraction(1)):
    result = row.copy()
    for key, value in other.items():
        new = result.get(key, 0) + coefficient * value
        if new:
            result[key] = new
        elif key in result:
            del result[key]
    return result


def times(row, coefficient):
    return {key: coefficient * value for key, value in row.items() if coefficient * value}


def symbol(index):
    return {(index, ()): Fraction(1)}


def route(row, stage, port):
    if stage == 0:
        return row.copy()
    letter = (stage, port)
    result = {}
    for (index, word), value in row.items():
        new_word = word[1:] if word and word[0] == letter else (letter,) + word
        key = index, new_word
        result[key] = result.get(key, 0) + value
    return {key: value for key, value in result.items() if value}


def read_query(bank, ports, stage, r):
    result = [{} for _ in range(8)]
    for p in ports:
        value = route(bank[p], stage, p)
        for k in range(8):
            if r[k][p]:
                result[k] = plus(result[k], value, r[k][p])
    return result


def response(query, ports, stage, r):
    result = {}
    for p in ports:
        value = {}
        for k in range(8):
            if r[k][p]:
                value = plus(value, query[k], r[k][p] / 4)
        result[p] = route(value, stage, p)
    return result


def source_forward(x, y, r):
    f = read_query(x, ALL, 0, r)
    t = read_query(x, T, 0, r)
    kf = response(f, U + T, 0, r)
    out_x = {p: plus(x[p], kf[p], -1) for p in U}
    out_x.update(response(t, A, 0, r))
    out_x.update({p: kf[p] for p in T})
    out_y = {p: plus(y[p], out_x[p]) for p in U}
    out_y.update({p: plus(plus(x[p], y[p]), out_x[p], -1) for p in A + T})
    return out_x, out_y


def source_backward(x, y, r):
    # Use the stated ordered source equations. Do not use the repair.
    n = response(read_query(y, U + T, 2, r), A, 2, r)
    u = y.copy()
    for p in A:
        u[p] = plus(u[p], n[p])
    a = read_query(x, T, 1, r)
    b = read_query(u, ALL, 1, r)
    out_y = u.copy()
    ku = response(a, U, 1, r)
    kt = response([plus(bb, aa, 11) for bb, aa in zip(b, a)], T, 1, r)
    for p in U:
        out_y[p] = plus(y[p], ku[p])
    for p in T:
        out_y[p] = plus(u[p], kt[p], -1)
    out_x = {p: plus(x[p], y[p], -1) for p in U}
    out_x.update({p: plus(plus(x[p], y[p]), out_y[p], -1) for p in A + T})
    require(read_query(out_y, ALL, 1, r) == a, 'R1 Y2 = ell1T X1T')
    return out_x, out_y


def act(columns, value):
    answer = 0
    while value:
        bit = value & -value
        answer ^= columns[bit.bit_length() - 1]
        value ^= bit
    return answer


@lru_cache(maxsize=None)
def phase(terms):
    linear = [0] * 73
    quadratic = [0] * 73
    for vector, coefficient in terms:
        positions = [i for i in range(73) if (vector >> i) & 1]
        for i in positions:
            linear[i] = (linear[i] + coefficient) % 4
        if coefficient % 2:
            for at, i in enumerate(positions):
                for j in positions[at + 1:]:
                    quadratic[i] ^= 1 << j
    return tuple(linear), tuple(quadratic)


def transport(terms, columns, shift):
    return tuple((act(columns, v), c) for v, c in terms) + ((shift, 2),)


def parse_routes(certificate):
    result = {}
    for stage in (1, 2):
        for p in ALL:
            events = [e for e in certificate['programs']['F_' + str(stage)]
                      if e[0] == 'cover_map' and e[1] == ['L', p]]
            require(len(events) >= 2, 'Completed-X views occur in both directions')
            record = certificate['map_registry'][events[0][2]]
            g = tuple(record['owner_right_matrix_columns'])
            delta = record['payload_translation_at_identity_owner']
            require(tuple(act(g, v) for v in g) == AXES, 'Actual route involution')
            require(all(((g[i] & g[j]).bit_count() & 1) == (i == j)
                        for i in range(73) for j in range(73)), 'Actual orthogonal route')
            require(all(g[i] == AXES[i] for i in range(9 + 8 * stage, 73)),
                    'Actual route fixes the later axes')
            basis = g[1 + 8 * stage:9 + 8 * stage]
            require(all(v < 512 for v in basis), 'The moved chart is in the old nine-space')
            normals = [q for q in range(1, 512)
                       if all((q & v).bit_count() % 2 == 0 for v in basis)]
            require(len(normals) == 1, 'One port normal')
            q = normals[0]
            if p in A + T:
                require(certificate['native_line_recipes']['positive_' + str(p)]['label'] == q,
                        'The native selected recipe has the same normal')
            require(act(g, q) == q, 'Actual route fixes its own port')
            frame = tuple((v, 1) for v in AXES[:9 + 8 * stage])
            require(phase(transport(frame, g, delta)) == phase(frame),
                    'Exact complete-frame view, including translation')
            result[stage, p] = g, delta, q
    return result


def execute(events, rows, frames, routes, dirty, counters):
    private = False
    for event in events:
        op = event['op']
        if op == 'add':
            dst, src = event['dst'], event['src']
            require(phase(frames[dst]) == phase(frames[src]) or not rows[src],
                    'ADD uses one physical frame: ' + dst + ' <- ' + src)
            rows[dst] = plus(rows[dst], rows[src], Fraction(event['c']))
            counters['physical_ADD_checks'] += 1
        elif op == 'scale':
            rows[event['field']] = times(rows[event['field']], Fraction(event['c']))
        elif op == 'clear':
            field = event['field']
            require(field == 'C' or (field.startswith('R') and not dirty),
                    'Only an owned field can be cleared')
            require(field != 'C' or private, 'Scratch clear is inside its owner body')
            rows[field] = {}
            frames[field] = {'old': OLD, 'current': FULL, 'identity': ()}[event['frame']]
        elif op == 'line':
            require(event['field'] == 'Y' + str(event['port']) and event['sign'] == 1
                    and event['rank'] == 1, 'Literal positive Y line')
            q = routes[1, event['port']][2]
            frames[event['field']] += ((q, 1),)
        elif op == 'stage':
            require(event['field'] in {'R' + str(p) for p in A} and event['stage'] == 1
                    and event['sign'] == 1 and event['rank'] == 8, 'Literal record E1 lift')
            frames[event['field']] += tuple((v, 1) for v in AXES[9:17])
        elif op == 'map':
            require(not private, 'No owner route inside the private body')
            stage, p = event['letter']
            g, delta, _ = routes[stage, p]
            require(tuple(event['g']) == g, 'Literal actual owner view')
            require(event['shift'] in (delta, act(g, delta)), 'Literal forward or inverse translation')
            field = event['field']
            rows[field] = route(rows[field], stage, p)
            frames[field] = transport(frames[field], g, event['shift'])
            counters['physical_map_checks'] += 1
        elif op == 'private_begin':
            require(not private, 'One private body')
            private = True
        elif op == 'private_end':
            require(private and not rows['C'] and phase(frames['C']) == phase(()),
                    'Scratch returns to zero and identity before next owner')
            private = False
        else:
            raise ValueError('Unknown event: ' + op)
    require(not private, 'Private body closes')


def invoice(events):
    count = Counter(event['op'] for event in events)
    profile = Counter(event['rank'] for event in events if event['op'] in ('stage', 'line'))
    scalar = 0
    for event in events:
        if event['op'] == 'clear':
            scalar += 2
        elif event['op'] in ('add', 'scale'):
            c = Fraction(event['c'])
            n, d = abs(c.numerator), c.denominator
            require(d & (d - 1) == 0, 'Dyadic scalar coefficient')
            if event['op'] == 'add':
                scalar += 2 * (2 + n.bit_length() + n.bit_count() + d.bit_length() - 1)
            else:
                scalar += 2 * (abs(n.bit_length() - d.bit_length()) + int(c < 0))
    return dict(event_counts=dict(sorted(count.items())), native_profile=dict(sorted(profile.items())),
                native_mass=sum(k * v for k, v in profile.items()), scalar_allowance=scalar,
                native_wrappers=2 * sum(profile.values()), cover_maps=count['map'])


def row_digest(rows):
    literal = [[field, [[index, list(word), str(value)] for (index, word), value in sorted(row.items())]]
               for field, row in sorted(rows.items())]
    return sha256(json.dumps(literal, separators=(',', ':')).encode()).hexdigest()


def case(program, r, routes, dirty):
    x = {p: symbol(p) for p in ALL}
    y = {p: symbol(112 + p) for p in ALL}
    h = {p: symbol(224 + at) for at, p in enumerate(A)}
    x1, y1 = source_forward(x, y, r)
    x2, y2 = source_backward(x1, y1, r)
    rows = {'X' + str(p): x1[p] for p in ALL}
    rows.update({'Y' + str(p): y1[p] for p in ALL})
    rows.update({'R' + str(p): h[p] for p in A})
    rows['C'] = symbol(232)
    helpers = {'H' + str(i): symbol(233 + i) for i in range(480)}
    rows.update(helpers)
    frames = {'X' + str(p): OLD for p in ALL}
    frames.update({'Y' + str(p): OLD + ((routes[1, p][2], -1),) for p in ALL})
    frames.update({'R' + str(p): OLD if dirty else () for p in A})
    frames.update({'C': (), **{name: () for name in helpers}})
    counters = Counter()
    execute(program['capture'], rows, frames, routes, dirty, counters)
    for p in ALL:
        rows['X' + str(p)], rows['Y' + str(p)] = x2[p], y2[p]
        frames['X' + str(p)] = FULL
        frames['Y' + str(p)] = FULL + ((routes[1, p][2], -1),)
    execute(program['repair'], rows, frames, routes, dirty, counters)
    dx = {p: {} for p in ALL}
    if dirty:
        dx.update({p: times(h[p], -1) for p in A})
        dx.update(response(read_query(h, A, 0, r), T, 0, r))
    g = response(read_query(y1, U + T, 2, r), A, 2, r)
    for p in ALL:
        require(rows['X' + str(p)] == plus(x[p], dx[p]), 'All original X columns')
        require(rows['Y' + str(p)] == plus(y[p], dx[p], -1), 'All original Y columns')
        require(phase(frames['X' + str(p)]) == phase(FULL), 'Common X output frame')
        require(phase(frames['Y' + str(p)]) == phase(FULL), 'Common Y output frame')
    for p in A:
        require(rows['R' + str(p)] == (plus(h[p], g[p]) if dirty else {}), 'All donor columns')
    require(not rows['C'], 'Arbitrary owned scratch is cleared')
    require(all(rows[name] == value for name, value in helpers.items()), 'All 480 helper columns')
    all_events = program['capture'] + program['repair']
    return {**invoice(all_events), **counters, 'output_rows_sha256': row_digest(rows)}, rows


def main():
    require(shutil.disk_usage(HERE).free >= 3 * 1024 ** 3, 'Three GiB of free disk')
    raw = pinned(BASE / 'base/research/joint-query/certificate.json.gz',
                 'a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7')
    certificate = json.loads(gzip.decompress(raw))
    r = [[Fraction(row.get(str(p), 0)) for p in ALL] for row in certificate['R_rows']]
    for ports, value in ((A, 4), (T, 4), (U, 48), (ALL, 56)):
        require(all(sum(r[i][p] * r[j][p] for p in ports) == value * (i == j)
                    for i in range(8) for j in range(8)), 'Actual minor and centre Gram')
    routes = parse_routes(certificate)
    programs = json.loads(pinned(INPUT / 'eight-records/EIGHT-RECORD-WORDS.json',
                                 '8dcb0f29d2b0275e5d5395511d10451b8675c9ffe37ebdbd452c0132a17b15f4'))
    inherited = pinned(BASE / 'common-frame-results/COMMON-F-RESTORATION-WORD.json',
                       'c1fa3fe3596d939bbc42c0a41ad0078b43b74dca51fa41d7e3407736af07a74e')
    old_native = [e for e in json.loads(inherited)['repair_after_B1'] if e['op'] in ('line', 'stage')]
    results = {}
    for name, program in programs.items():
        dirty = name.startswith('dirty')
        for event in program['repair']:
            if event['op'] in ('line', 'stage'):
                require(event in old_native, 'Unchanged reviewed native child record')
        results[name], _ = case(program, r, routes, dirty)
        require(results[name]['native_mass'] == 176, 'Native mass')
        require(results[name]['scalar_allowance'] == (20322 if dirty else 20290), 'Scalar invoice')
        require(results[name]['cover_maps'] == 240, 'Complete cover views')
    controls = {}
    owned = programs['owned_eight_A']
    bad = json.loads(json.dumps(owned))
    for at, e in enumerate(bad['repair']):
        if e['op'] == 'add' and e.get('dst') == 'X' + str(T[0]) and e.get('src', '').startswith('Y'):
            if int(e['src'][1:]) not in T:
                del bad['repair'][at]
                break
    try:
        case(bad, r, routes, False)
    except ValueError as error:
        controls['missing_current_query_term'] = str(error)
    require('missing_current_query_term' in controls, 'Query control fails')
    bad = json.loads(json.dumps(owned))
    next(e for e in bad['repair'] if e['op'] == 'map')['shift'] ^= 1
    try:
        case(bad, r, routes, False)
    except ValueError as error:
        controls['changed_actual_view_translation'] = str(error)
    require('changed_actual_view_translation' in controls, 'Translation control fails')
    result = {'status': 'PASS_INDEPENDENT_EIGHT_RECORD_REPAIR', 'source_pins': PINS,
              'cases': results, 'negative_controls': controls,
              'source_data_columns': 224, 'record_columns': 8, 'owned_scratch_columns': 1,
              'unchanged_helper_columns': 480, 'actual_completed_view_recipes': len(routes),
              'inherited': ['Full original QQ16 core maps and helper native jobs',
                            'Unchanged positive line and E1 child kernels'],
              'excluded': ['New child hosting', 'Record owner allocation', 'Physical stream invoice',
                           'Recursive precision', 'Dirty record cleanup', 'Complete supplier']}
    output = HERE / 'CHECK.json'
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(result['status'])
    print(sha256(output.read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
