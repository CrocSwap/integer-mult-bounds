#!/usr/bin/env python3
"""Erase the masked-query donor debt through real source families."""

import argparse
from copy import deepcopy
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[2]
SOURCE = LANES / 'paired-package-review/upstream-followthrough-20261015/check_restoration.py'
ERROR = LANES / 'residual-syndrome/physical-algebra/eight-record-review-20261015/DELAYED-CLEANUP-ONE-C-WORD.json'
MASK = HERE / 'masked-sum/MASKED-QUERY-PROGRAM.json.gz'
PINS = {
    SOURCE: '8c6fb324aa898f86b3edbd85252570a2dc43c40455887f789a153191645686ca',
    ERROR: 'bddba461c6f06213c7ab938d24993ac6d5ea44169f9705594227acfdc5b6e880',
    MASK: 'a4fc54c4af9d3f65e60b025ee26a144d133ae935774d73bbb48d5c7d39ef8581',
}


def add(dst, src, c=1):
    return dict(op='add', dst=dst, src=src, c=str(c))


def swap(left, right):
    return [add(left, right), add(right, left, -1), add(left, right),
            dict(op='scale', field=right, c='-1')]


def inverse(events):
    answer = []
    for event in reversed(events):
        event = dict(event)
        if event['op'] == 'add':
            event['c'] = str(-Q(event['c']))
        elif event['op'] == 'scale':
            event['c'] = str(1 / Q(event['c']))
        else:
            raise ValueError('Unsupported scalar inverse')
        answer.append(event)
    return answer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    for path, digest in PINS.items():
        if sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError('Pinned source ' + str(path))
    spec = importlib.util.spec_from_file_location('retained_routes', SOURCE)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    _, R, A, T, U, routes = m.load()
    V = A + T
    off_a = U + T
    packet = json.loads(gzip.decompress(MASK.read_bytes()))
    H = [{int(q): Q(v) for q, v in row.items()} for row in packet['source_response']]
    TB = [{int(q): Q(v) for q, v in row.items()} for row in packet['target_code']]
    section = {(a, p): sum(R[k][a] * R[k][p] for k in range(8)) / 4
               for a in A for p in range(112)}

    def view(field, p, undo=False):
        record = routes[2, p]
        return dict(op='map', field=field, letter=[2, p], g=list(record['g']),
                    shift=m.action(record['g'], record['shift']) if undo else record['shift'])

    def alias(sign):
        events = [dict(op='private_begin')]
        for k in range(8):
            events.append(dict(op='clear', field='C', frame='current'))
            events.extend(add('C', f'X0:{p}', R[k][p])
                          for p in range(112) if R[k][p])
            events.extend(add(f'X1:{p}', 'C', sign * R[k][p] / 4)
                          for p in off_a if R[k][p])
        events += [dict(op='clear', field='C', frame='identity'), dict(op='private_end')]
        return events

    prepare = [add(f'X0:{p}', f'X1:{p}', -1) for p in U]
    for p in V:
        prepare.extend(swap(f'X0:{p}', f'X1:{p}'))
    sum_t = [add(f'Y1:{p}', f'{bank}:{p}') for p in T for bank in ('X0', 'X1')]
    fields = [(f'R{p}', p) for p in A]
    fields += [(f'X1:{p}', p) for p in off_a] + [(f'Y1:{p}', p) for p in T]
    gather = [view(field, p) for field, p in fields]
    query = [add(f'R{a}', f'X1:{p}', section[a, p])
             for a in A for p in off_a if section[a, p]]
    query += [add(f'R{a}', f'Y1:{p}', -section[a, p])
              for a in A for p in T if section[a, p]]
    selected = deepcopy(json.loads(ERROR.read_text())['selected_error_correction'])
    for event in selected:
        for key in ('field', 'dst', 'src'):
            if key in event and event[key][0] in ('X', 'Y'):
                field = event[key]
                event[key] = field[0] + '1:' + field[1:]

    parts = [
        dict(name='query_subtraction', scope='owner_sweep',
             events=[add(f'R{p}', f'Y0:{p}', -1) for p in A]),
        dict(name='source_prepare', scope='owner_sweep', events=prepare),
        dict(name='selected_sum_prepare', scope='owner_sweep', events=sum_t),
        dict(name='source_alias', scope='owner_sweep', events=alias(1)),
        dict(name='source_gather', scope='family_sweep', events=gather),
        dict(name='routed_response', scope='owner_sweep', events=query),
        dict(name='source_return', scope='family_sweep',
             events=[view(field, p, True) for field, p in reversed(fields)]),
        dict(name='source_alias_inverse', scope='owner_sweep', events=alias(-1)),
        dict(name='selected_sum_inverse', scope='owner_sweep', events=inverse(sum_t)),
        dict(name='source_prepare_inverse', scope='owner_sweep', events=inverse(prepare)),
        dict(name='selected_error_correction', scope='owner_sweep', events=selected),
    ]
    word = [event for part in parts for event in part['events']]

    def stream_check(blocks):
        private_bodies = 0
        for part in blocks:
            events = part['events']
            if part['scope'] == 'family_sweep':
                m.need(all(e['op'] == 'map' and e['field'] != 'C' for e in events),
                       'A cover sweep needs a real family')
                continue
            m.need(part['scope'] == 'owner_sweep', 'Known stream scope')
            m.need(all(e['op'] != 'map' for e in events), 'No cover map inside an owner sweep')
            private = False
            last_clear = None
            for event in events:
                op = event['op']
                if op == 'private_begin':
                    m.need(not private, 'Nested private owner body')
                    private = True
                    last_clear = None
                    private_bodies += 1
                elif op == 'private_end':
                    m.need(private and last_clear == 'identity', 'C leaves its owner at zero')
                    private = False
                elif 'C' in (event.get('field'), event.get('src'), event.get('dst')):
                    m.need(private, 'Private C is local to the current owner')
                    if op == 'clear':
                        last_clear = event['frame']
                    else:
                        last_clear = None
            m.need(not private, 'No private value crosses an owner boundary')
        return private_bodies

    m.need(stream_check(parts) == 2, 'Two complete private owner sweeps')
    m.need(not any(e['op'] in ('line', 'stage') for e in word), 'No new native child')
    m.need(not any(e.get(key, '').startswith('Y0:') and int(e[key].split(':')[1]) not in A
                   for e in word for key in ('field', 'dst', 'src')), 'No off-selected Y0 access')
    m.need(not any(e.get(key, '').startswith('Y1:') and int(e[key].split(':')[1]) not in V
                   for e in word for key in ('field', 'dst', 'src')), 'No hole-frame Y1 access')

    def apply(matrix, bank):
        output = {}
        for p, row in enumerate(matrix):
            value = {}
            for q, coefficient in row.items():
                value = m.rowadd(value, m.route(bank[q], (2, q)), coefficient)
            output[p] = m.route(value, (2, p))
        return output

    x, y = m.unit_bank('x:'), m.unit_bank('y:')
    c, beta = m.unit_bank('c:'), m.unit_bank('beta:')
    h = {p: {(f'h:{p}', ()): Q(1)} for p in A}
    error = {p: {} for p in range(112)}
    error.update({p: m.rowscale(h[p], -1) for p in A})
    error.update(m.inject(m.query(h, A, R, 0), T, R, 0))
    local_x = {p: c[p] if p in V else m.rowadd(x[p], c[p]) for p in range(112)}
    local_y = {p: beta[p] if p in V else y[p] for p in range(112)}
    first, second = apply(H, local_x), apply(TB, local_y)
    local_output = {p: m.rowadd(first[p], second[p]) for p in range(112)}
    _, old_target = m.forward(x, y, R, A, T, U)
    debt = m.inject(m.query(old_target, off_a, R, 2), A, R, 2)
    initial = {f'X0:{p}': local_x[p] for p in range(112)}
    initial.update({f'Y0:{p}': local_output[p] for p in range(112)})
    initial.update({f'X1:{p}': m.rowadd(x[p], error[p]) if p in V else c[p]
                    for p in range(112)})
    initial.update({f'Y1:{p}': m.rowadd(y[p], error[p], -1) if p in V
                    else m.rowadd(beta[p], y[p], -1) for p in range(112)})
    initial.update({f'R{p}': m.rowadd(h[p], debt[p]) for p in A})
    initial['C'] = {('private:', ()): Q(1)}
    full = tuple((v, 1) for v in m.AXES[:25])
    frames = {field: full for field in initial}
    for p in range(112):
        if p not in A:
            frames[f'Y0:{p}'] += ((routes[1, p]['q'], -1),)
        if p in U:
            frames[f'Y1:{p}'] += ((routes[1, p]['q'], -1),)
    frames['C'] = ()
    expected = deepcopy(initial)
    for p in V:
        expected[f'X1:{p}'], expected[f'Y1:{p}'] = x[p], y[p]
    for p in A:
        expected[f'R{p}'] = h[p]
    expected['C'] = {}

    def run(blocks):
        stream_check(blocks)
        rows, state = deepcopy(initial), deepcopy(frames)
        for part in blocks:
            m.execute(part['events'], rows, state, routes, set(), stage=1)
        m.need(rows == expected, 'All 448 data, eight donor and one owned input columns')
        m.need(all(m.phase(state[f]) == m.phase(frames[f]) for f in frames), 'Every output frame returns')
        return rows

    output = run(parts)
    controls = {}
    for name in ('query_subtraction', 'selected_sum_prepare', 'source_alias',
                 'routed_response', 'selected_error_correction'):
        try:
            run([part for part in parts if part['name'] != name])
        except ValueError as error:
            controls[name] = str(error)
        else:
            raise ValueError('Ineffective cleanup control ' + name)
    bad = deepcopy(parts)
    bad[3]['events'].insert(2, view('C', U[0]))
    try:
        stream_check(bad)
    except ValueError as error:
        controls['cover_map_of_private_C'] = str(error)
    else:
        raise ValueError('Private cover-map control')
    bad = deepcopy(parts)
    bad[3]['events'].pop(-2)
    try:
        stream_check(bad)
    except ValueError as error:
        controls['C_survives_owner'] = str(error)
    else:
        raise ValueError('Private lifetime control')

    bill = m.scalar_price(word)
    m.need(bill['scalar'] == 25124 and bill['cover_maps'] == 240 and bill['native_mass'] == 0,
           'Exact complete local invoice')
    payload = m.encoded(dict(parts=parts, word=word,
                            source_pins={str(path.relative_to(LANES)): digest for path, digest in PINS.items()})) + b'\n'
    receipt = dict(
        status='PASS_OWNER_LOCAL_MASKED_CLEANUP_457_COLUMNS', word_sha256=sha256(payload).hexdigest(),
        invoice=bill, part_invoices={part['name']: m.scalar_price(part['events']) for part in parts},
        independent_data_columns=448, arbitrary_donor_columns=8, owned_private_columns=1,
        all_output_rows_sha256=sha256(m.encoded({f: [[s, list(w), str(c)] for (s, w), c in sorted(row.items())]
                                               for f, row in sorted(output.items())})).hexdigest(),
        off_selected_Y0_reads=0, hole_frame_Y1_reads=0, private_cover_maps=0,
        private_owner_sweeps=2, peak_owned_scratch=1, negative_controls=controls,
        scope='Local complete-cut access. Each family sweep is complete before the next owner sweep. '
              'Every private value is cleared within its owner. Changed F2 owner admission, later target-code '
              'retirement, primitive precision, recursive hosting and the complete supplier remain open.')
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / 'STREAM-CLEANUP-WORD.json').write_bytes(payload)
    (args.out / 'STREAM-CLEANUP.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(receipt['status'])
    print(json.dumps(bill, sort_keys=True))


if __name__ == '__main__':
    main()
