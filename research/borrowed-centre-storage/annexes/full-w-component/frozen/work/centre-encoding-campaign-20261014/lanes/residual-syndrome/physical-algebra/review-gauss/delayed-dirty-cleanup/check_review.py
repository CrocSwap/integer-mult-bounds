"""Check the two frozen cleanup words without producer imports."""

from collections import Counter
from fractions import Fraction as F
import gzip
from hashlib import sha256
import json
from pathlib import Path
import shutil


HERE = Path(__file__).resolve().parent
PHYS = HERE.parents[1]
LANES = PHYS.parents[1]
SOURCE = PHYS / 'eight-record-review-20261015'
CERT = LANES / 'paired-package-review/upstream-followthrough-20261015/base/research/joint-query/certificate.json.gz'
PINS = {}


def require(value, message):
    if not value:
        raise ValueError(message)


def read(path, digest):
    raw = path.read_bytes()
    require(sha256(raw).hexdigest() == digest, 'Source pin: ' + str(path))
    PINS[str(path.relative_to(LANES))] = digest
    return raw


def axpy(left, right, coefficient=F(1)):
    answer = dict(left)
    for key, value in right.items():
        answer[key] = answer.get(key, 0) + coefficient * value
        if not answer[key]:
            del answer[key]
    return answer


def combination(pairs):
    answer = {}
    for coefficient, row in pairs:
        if coefficient:
            answer = axpy(answer, row, coefficient)
    return answer


def unit(name):
    return {(name, ()): F(1)}


def move(row, letter):
    # A literal full cover map acts on the left of each existing word.
    answer = {}
    for (name, word), value in row.items():
        reduced = word[1:] if word and word[0] == letter else (letter,) + word
        answer[name, reduced] = value
    return answer


def apply_matrix(columns, value):
    answer = 0
    for j, column in enumerate(columns):
        if value >> j & 1:
            answer ^= column
    return answer


def frame_signature(width, columns=None, shift=0):
    # Values on zero, coordinate vectors, and coordinate pairs determine
    # this mod-four quadratic phase. This checks the constant phase too.
    rows = [1 << i for i in range(73)] if columns is None else [
        sum(((column >> i) & 1) << j for j, column in enumerate(columns))
        for i in range(73)]
    mask = (1 << width) - 1
    value = lambda x, parity: ((x & mask).bit_count() + 2 * parity) % 4
    answer = [0]
    answer += [value(rows[i], shift >> i & 1) for i in range(73)]
    answer += [value(rows[i] ^ rows[j], ((shift >> i) ^ (shift >> j)) & 1)
               for i in range(73) for j in range(i + 1, 73)]
    return tuple(answer)


def inverse_scalar(events):
    output = []
    for event in reversed(events):
        new = dict(event)
        c = F(new['c'])
        require(new['op'] in ('add', 'scale'), 'Scalar inverse alphabet')
        new['c'] = str(-c if new['op'] == 'add' else 1 / c)
        output.append(new)
    return output


def invoice(events):
    histogram = Counter(event['op'] for event in events)
    scalar = 0
    for event in events:
        if event['op'] == 'clear':
            scalar += 2
        elif event['op'] in ('add', 'scale'):
            c = F(event['c'])
            n, d = abs(c.numerator), c.denominator
            require(n and d & (d - 1) == 0, 'Nonzero dyadic coefficient')
            if event['op'] == 'add':
                scalar += 2 * (2 + n.bit_length() + n.bit_count() + d.bit_length() - 1)
            else:
                require(n & (n - 1) == 0, 'Scale is a signed power of two')
                scalar += 2 * (abs(n.bit_length() - d.bit_length()) + (c < 0))
    require(not (set(histogram) - {'add', 'scale', 'map', 'clear', 'private_begin', 'private_end'}),
            'No native operation in the cleanup')
    return {'event_counts': dict(sorted(histogram.items())), 'scalar_allowance': scalar,
            'cover_maps': histogram['map'], 'native_children': 0}


def main():
    require(shutil.disk_usage(HERE).free >= 3 * 1024 ** 3, 'At least three GiB free')
    manifest = json.loads(read(SOURCE / 'DELAYED-CLEANUP-MANIFEST.json',
        'b23074aa39523c88da7fe5c27e26e63b2ffc36567762105e55ffad15999da405'))
    for name, digest in manifest['files'].items():
        read(SOURCE / name, digest)
    certificate = json.loads(gzip.decompress(read(CERT,
        'a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7')))
    a, t, u = (tuple(certificate[key]) for key in ('A_ports', 'T_ports', 'U_ports'))
    require(a == (0, 7, 20, 27, 36, 46, 57, 111), 'Actual A ports')
    require(t == (21, 37, 47, 76, 81, 87, 92, 110), 'Actual T ports')
    require(set(a + t + u) == set(range(112)) and len(a + t + u) == 112, 'Port partition')
    off = u + t
    r = [[F(row.get(str(p), 0)) for p in range(112)] for row in certificate['R_rows']]
    require(len(r) == 8, 'Eight centre rows')
    for ports, scale in ((a, 4), (t, 4), (u, 48), (range(112), 56)):
        require(all(sum(r[i][p] * r[j][p] for p in ports) == scale * (i == j)
                    for i in range(8) for j in range(8)), 'Exact centre Gram')
    dot = lambda p, q: sum(r[k][p] * r[k][q] for k in range(8)) / 4

    routes = {}
    axes = tuple(1 << i for i in range(73))
    for stage in (1, 2):
        for p in range(112):
            maps = [event for event in certificate['programs']['F_' + str(stage)]
                    if event[:2] == ['cover_map', ['L', p]]]
            require(len(maps) >= 2, 'The first complete view pair is present')
            first, last = [certificate['map_registry'][event[2]] for event in maps[:2]]
            require(first == last, 'The original inverse is the same full map')
            g = tuple(first['owner_right_matrix_columns'])
            delta = first['payload_translation_at_identity_owner']
            require(tuple(apply_matrix(g, column) for column in g) == axes, 'Owner involution')
            require(apply_matrix(g, delta) == delta, 'Payload involution')
            require(all((g[i] & g[j]).bit_count() % 2 == (i == j)
                        for i in range(73) for j in range(73)), 'Orthogonal owner map')
            require(frame_signature(25, g, delta) == frame_signature(25),
                    'Exact complete F25 phase, including payload')
            routes[stage, p] = g, delta

    x = {p: unit('X' + str(p)) for p in range(112)}
    y = {p: unit('Y' + str(p)) for p in range(112)}
    h = {p: unit('R' + str(p)) for p in a}
    zero_error = {p: {} for p in range(112)}
    ex = dict(zero_error)
    ex.update({p: combination([(-1, h[p])]) for p in a})
    ex.update({p: combination((dot(p, q), h[q]) for q in a) for p in t})
    require(all(not combination((r[k][p], ex[p]) for p in range(112)) for k in range(8)),
            'R0 E_X is zero on all donor columns')

    def aliases(xx, yy):
        return {p: combination([(1, yy[p]), (1, xx[p])] +
                [(-dot(p, q), xx[q]) for q in range(112)]) for p in off}

    def n_read(values, stage=2):
        return {p: move(combination((dot(p, q), move(values[q], (stage, q)))
                                    for q in off), (stage, p)) for p in a}

    v = aliases(x, y)
    ey = {p: combination([(-1, ex[p])]) for p in range(112)}
    require(all(not row for row in aliases(ex, ey).values()), 'V E is zero')
    gz = n_read(v)
    initial = {'X' + str(p): axpy(x[p], ex[p]) for p in range(112)}
    initial.update({'Y' + str(p): axpy(y[p], ex[p], -1) for p in range(112)})
    initial.update({'R' + str(p): axpy(h[p], gz[p]) for p in a})
    initial['C'] = unit('C')
    initial.update({'H' + str(j): unit('H' + str(j)) for j in range(480)})
    identity = {name: unit(name) for name in initial}

    def run(events, rows, wrong_query=False, prefix=None):
        state = {name: dict(row) for name, row in rows.items()}
        frames = {name: (0 if name == 'C' or name.startswith('H') else 25) for name in state}
        private = False
        for index, event in enumerate(events):
            op = event['op']
            if op == 'add':
                dst, src = event['dst'], event['src']
                require(dst != src, 'Independent ADD source')
                require(frames[dst] == frames[src] or not state[src], 'Equal physical ADD frames')
                state[dst] = axpy(state[dst], state[src], F(event['c']))
            elif op == 'scale':
                state[event['field']] = combination([(F(event['c']), state[event['field']])])
            elif op == 'map':
                require(not private, 'No map inside a private sweep')
                field = event['field']
                stage, p = event['letter']
                require(stage == 2 and int(field[1:]) == p, 'Exact stage-2 field view')
                g, delta = routes[stage, p]
                require(tuple(event['g']) == g and event['shift'] == delta, 'Actual full map bytes')
                require(frames[field] == 25, 'Common frame at the cleanup map')
                state[field] = move(state[field], (1 if wrong_query else 2, p))
            elif op == 'clear':
                require(private and event['field'] == 'C', 'Clear only private owned C')
                require(event['frame'] in ('common_F_U2', 'identity'), 'Declared zero view')
                state['C'] = {}
                frames['C'] = 25 if event['frame'] == 'common_F_U2' else 0
            elif op == 'private_begin':
                require(not private, 'One private sweep')
                private = True
            elif op == 'private_end':
                require(private and not state['C'] and frames['C'] == 0, 'Scratch returns zero/identity')
                private = False
            else:
                raise ValueError('Unknown event: ' + op)
            if prefix is not None and op in ('add', 'scale', 'map', 'clear'):
                field = event.get('dst', event.get('field'))
                weight = sum(map(abs, state[field].values()), F(0))
                debt = max((c.denominator.bit_length() - 1 for c in state[field].values()), default=0)
                if weight > prefix['maximum_l1']:
                    prefix.update(maximum_l1=weight, l1_event=index, l1_field=field)
                if debt > prefix['maximum_debt']:
                    prefix.update(maximum_debt=debt, debt_event=index, debt_field=field)
        require(not private, 'Private sweep closes')
        return state

    packets = {name: json.loads((SOURCE / name).read_text()) for name in
               ('DELAYED-CLEANUP-WORD.json', 'DELAYED-CLEANUP-ONE-C-WORD.json')}
    old, one = packets.values()
    require(old['current_stage2_query'] == one['current_stage2_query'], 'Same exact stage-2 query')
    require(old['data_error_correction'] == one['selected_error_correction'], 'Same baseline correction')
    query = old['current_stage2_query']
    expected_fields = ['Y' + str(p) for p in off] + ['R' + str(p) for p in a]
    require([e['field'] for e in query[:112]] == expected_fields and
            all(e['op'] == 'map' for e in query[:112]), 'Complete query gather before all reads')
    require(all(e['op'] == 'add' for e in query[112:-112]), 'Only query ADDs between map sweeps')
    require([e['field'] for e in query[-112:]] == expected_fields[104:] + expected_fields[:104] and
            all(e['op'] == 'map' for e in query[-112:]), 'Complete return after all reads')
    expected_adds = [dict(op='add', dst='R' + str(p), src='Y' + str(q), c=str(-dot(p, q)))
                     for p in a for q in off if dot(p, q)]
    require(query[112:-112] == expected_adds, 'Actual routed N2 coefficients')

    require(old['inverse_scalar_F0_content'] == inverse_scalar(old['scalar_F0_content']),
            'Literal scalar inverse, including all scales')
    full_expected = old['scalar_F0_content'] + query + old['inverse_scalar_F0_content'] + old['data_error_correction']
    require(old['cleanup'] == full_expected, 'Zero-work literal chronology')
    require(one['cleanup'] == one['alias_shear'] + query + one['inverse_alias_shear'] + one['selected_error_correction'],
            'One-C literal chronology')

    bare = {**{'X' + str(p): x[p] for p in range(112)},
            **{'Y' + str(p): y[p] for p in range(112)}, 'C': unit('C')}
    f0 = run(old['scalar_F0_content'], bare)
    expected_x = {p: combination([(1, x[p])] + [(-dot(p, q), x[q]) for q in range(112)]) for p in u}
    expected_x.update({p: combination((dot(p, q), x[q]) for q in t) for p in a})
    expected_x.update({p: combination((dot(p, q), x[q]) for q in range(112)) for p in t})
    for p in range(112):
        expected_y = axpy(y[p], expected_x[p]) if p in u else combination([(1, x[p]), (1, y[p]), (-1, expected_x[p])])
        require(f0['X' + str(p)] == expected_x[p] and f0['Y' + str(p)] == expected_y,
                'F0 content on every arbitrary data input')
    require(run(old['inverse_scalar_F0_content'], f0) == bare, 'Both scalar code directions')
    alias = run(one['alias_shear'], bare)
    require(all(alias['Y' + str(p)] == v[p] for p in off), 'One-C alias on every data input')
    restored = run(one['inverse_alias_shear'], alias)
    require(all(restored[key] == row for key, row in bare.items() if key != 'C') and not restored['C'],
            'Inverse alias restores data and clears only owned scratch')

    outputs, controls = {}, {}
    for name, packet in packets.items():
        result = run(packet['cleanup'], initial)
        want = dict(identity)
        if 'ONE-C' in name:
            want['C'] = {}
        require(result == want, 'Every independent data, donor, helper, and scratch column: ' + name)
        bill = invoice(packet['cleanup'])
        require(bill['scalar_allowance'] == (23780 if 'ONE-C' in name else 25152), 'Complete scalar invoice')
        require(bill['cover_maps'] == 224, 'Complete cover map count')
        outputs[name] = bill
        correction = packet.get('selected_error_correction', packet.get('data_error_correction'))
        no_correction = run(packet['cleanup'][:-len(correction)], initial)
        require(all(no_correction['R' + str(p)] == h[p] for p in a), 'Donors can be clean before data correction')
        require(any(no_correction['X' + str(p)] != x[p] for p in range(112)), 'Omitted data correction fails')
        require(run(packet['cleanup'], initial, True) != want, 'A stage-1 query cannot replace N2')
        controls[name] = ['omitted_E_correction', 'stage1_query_in_place_of_stage2']

    require(any(frame_signature(17, *routes[2, p]) != frame_signature(25) for p in a),
            'A missing second donor advance fails exact frame matching')
    different_owner_word = any(
        tuple(apply_matrix(routes[2, p][0], v) for v in routes[2, q][0]) !=
        tuple(apply_matrix(routes[1, p][0], v) for v in routes[1, q][0])
        for p in a for q in off if dot(p, q))
    require(different_owner_word, 'The two query stages differ on an actual owner coefficient')
    g, delta = routes[2, 0]
    require(frame_signature(25, g, delta ^ 1) != frame_signature(25), 'Wrong payload phase fails')
    costs = {name: invoice(events)['scalar_allowance'] for name, events in
             [('F0', old['scalar_F0_content']), ('F0_inverse', old['inverse_scalar_F0_content']),
              ('alias', one['alias_shear']), ('alias_inverse', one['inverse_alias_shear']),
              ('N2', query), ('minus_E', old['data_error_correction'])]}
    require(costs == dict(F0=10112, F0_inverse=10112, alias=9426, alias_inverse=9426, N2=4160, minus_E=768),
            'All separate scalar bills')
    prefix = dict(maximum_l1=F(1), maximum_debt=0)
    independent_cut = {name: unit(name) for name in initial if not name.startswith('H')}
    run(one['cleanup'], independent_cut, prefix=prefix)
    prefix['maximum_l1'] = str(prefix['maximum_l1'])
    prefix.update(input_columns=233, event_indices='zero-based',
                  scope='Complete scalar events and full cover maps; no primitive interiors or prior input bounds')
    (HERE / 'PREFIX-CHECK.json').write_text(json.dumps(prefix, indent=2, sort_keys=True) + '\n')
    for relative, digest in PINS.items():
        require(sha256((LANES / relative).read_bytes()).hexdigest() == digest, 'Source preserved')
    result = {'status': 'PASS_INDEPENDENT_CONDITIONAL_DELAYED_CLEANUP', 'source_pins': PINS,
              'input_columns_per_word': {'data': 224, 'donors': 8, 'helpers': 480, 'owned_scratch': 1},
              'formal_method': 'Exact rational rows in free involutive full-cover map words',
              'actual_completed_stage_views': 224, 'phase_signature_points_per_view': 2702,
              'whole_words': outputs, 'scalar_parts': costs, 'negative_controls': controls,
              'additional_controls': ['missing_second_donor_advance', 'changed_payload_translation'],
              'producer_imported_or_executed': False, 'inherited_predecessor_replayed': False,
              'source_files_preserved': True}
    (HERE / 'CHECK.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(result['status'])
    print(json.dumps({'whole_words': outputs, 'scalar_parts': costs}, sort_keys=True))


if __name__ == '__main__':
    main()
