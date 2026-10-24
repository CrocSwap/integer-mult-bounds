"""Emit and check a common-frame repair with eight A records.

The accepted QQ16 source contracts and native line recipes are inputs.
The new word uses a current-chart read to replace the eight T records.
"""

import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
PACKET = HERE.parents[1] / 'paired-package-review/upstream-followthrough-20261015'
SOURCE = PACKET / 'check_restoration.py'
PIN = '8c6fb324aa898f86b3edbd85252570a2dc43c40455887f789a153191645686ca'


def build(m, R, A, T, U, routes, dirty):
    capture, repair = [], []
    def emit(op, **fields):
        repair.append(dict(op=op, **fields))
    for p in A:
        if not dirty:
            capture.append(dict(op='clear', field=f'R{p}', frame='old'))
        capture.append(dict(op='add', dst=f'R{p}', src=f'X{p}', c='1'))
        emit('stage', field=f'R{p}', sign=1, rank=8, stage=1)
    for p in range(112):
        emit('line', field=f'Y{p}', port=p, sign=1, rank=1)
    for prefix, ports in (('Y', tuple(range(112))), ('X', T)):
        for p in ports:
            r = routes[1, p]
            emit('map', field=f'{prefix}{p}', letter=[1, p], g=list(r['g']), shift=r['shift'])
    for p in T:
        emit('add', dst=f'Y{p}', src=f'X{p}', c='1')
    for p in T:
        emit('scale', field=f'X{p}', c='-1')
        emit('add', dst=f'X{p}', src=f'Y{p}', c='1')
        for q in A + U:
            c = sum(R[k][p] * R[k][q] for k in range(8)) / 4
            if c:
                emit('add', dst=f'X{p}', src=f'Y{q}', c=str(c))
    emit('private_begin')
    for k in range(8):
        emit('clear', field='C', frame='current')
        for p in T:
            if R[k][p]:
                emit('add', dst='C', src=f'X{p}', c=str(R[k][p]))
        for p in U:
            if R[k][p]:
                emit('add', dst=f'Y{p}', src='C', c=str(-R[k][p] / 4))
    emit('clear', field='C', frame='identity')
    emit('private_end')
    for prefix, ports in (('X', T), ('Y', tuple(range(112)))):
        for p in ports:
            r = routes[1, p]
            emit('map', field=f'{prefix}{p}', letter=[1, p], g=list(r['g']),
                 shift=m.action(r['g'], r['shift']))
    for p in A:
        emit('add', dst=f'Y{p}', src=f'X{p}', c='1')
        emit('add', dst=f'X{p}', src=f'R{p}', c='1')
        emit('add', dst=f'R{p}', src=f'X{p}', c='-1')
        emit('add', dst=f'X{p}', src=f'R{p}', c='1')
        if dirty:
            emit('add', dst=f'R{p}', src=f'X{p}', c='1')
        else:
            emit('clear', field=f'R{p}', frame='identity')
    for p in U:
        emit('add', dst=f'X{p}', src=f'Y{p}', c='1')
        emit('add', dst=f'Y{p}', src=f'X{p}', c='-1')
    repair.extend(m.x_inverse_gates(R, A, T, U, routes, 0))
    for p in A + T:
        emit('add', dst=f'Y{p}', src=f'X{p}', c='-1')
    return capture, repair


def replay(m, R, A, T, U, routes, capture, repair, dirty):
    x, y = m.unit_bank('x:'), m.unit_bank('y:')
    x1, y1 = m.forward(x, y, R, A, T, U)
    rows = {f'X{p}': x1[p] for p in range(112)}
    rows.update({f'Y{p}': y1[p] for p in range(112)})
    frames = {f'X{p}': m.OLD for p in range(112)}
    frames.update({f'Y{p}': m.OLD + ((routes[1, p]['q'], -1),) for p in range(112)})
    h = {p: {(f'h:{p}', ()): Q(1)} for p in A}
    for p in A:
        rows[f'R{p}'], frames[f'R{p}'] = h[p], m.OLD if dirty else ()
    rows['C'], frames['C'] = {('scratch:', ()): Q(1)}, ()
    helper = {f'H{p}': {(f'helper:{p}', ()): Q(1)} for p in range(480)}
    rows.update(helper)
    frames.update({f: () for f in helper})
    allowed = set() if dirty else {f'R{p}' for p in A}
    m.execute(capture, rows, frames, routes, allowed)
    x2, y2 = m.backward(x1, y1, R, A, T, U, 1, 2)
    for p in range(112):
        rows[f'X{p}'], frames[f'X{p}'] = x2[p], m.CURRENT
        rows[f'Y{p}'], frames[f'Y{p}'] = y2[p], m.CURRENT + ((routes[1, p]['q'], -1),)
    m.execute(repair, rows, frames, routes, allowed)
    err_x = {p: {} for p in range(112)}
    if dirty:
        err_x.update({p: m.rowscale(h[p], Q(-1)) for p in A})
        err_x.update(m.inject(m.query(h, A, R, 0), T, R, 0))
    for p in range(112):
        m.need(rows[f'X{p}'] == m.rowadd(x[p], err_x[p]), 'X output: ' + str(p))
        m.need(rows[f'Y{p}'] == m.rowadd(y[p], err_x[p], -1), 'Y output: ' + str(p))
        m.need(m.phase(frames[f'X{p}']) == m.phase(m.CURRENT), 'X full frame')
        m.need(m.phase(frames[f'Y{p}']) == m.phase(m.CURRENT), 'Y full frame')
    future = m.inject(m.query(y1, T + U, R, 2), A, R, 2)
    for p in A:
        m.need(rows[f'R{p}'] == (m.rowadd(h[p], future[p]) if dirty else {}),
               'Record endpoint: ' + str(p))
    m.need(not rows['C'], 'Owned scratch clear')
    m.need(all(rows[f] == row for f, row in helper.items()), 'Arbitrary helpers unchanged')
    result = {field: [[s, list(w), str(c)] for (s, w), c in sorted(row.items())]
              for field, row in sorted(rows.items())}
    return sha256(m.encoded(result)).hexdigest()


def price(word):
    counts = Counter(e['op'] for e in word)
    ranks = Counter(e['rank'] for e in word if e['op'] in ('line', 'stage'))
    scalar = 0
    for e in word:
        if e['op'] == 'clear':
            scalar += 2
        elif e['op'] in ('add', 'scale'):
            c = Q(e['c'])
            a, b = abs(c.numerator), c.denominator
            if e['op'] == 'add':
                scalar += 2 * (2 + a.bit_length() + a.bit_count() + b.bit_length() - 1)
            else:
                scalar += 2 * (abs(a.bit_length() - b.bit_length()) + (c < 0))
    return {'event_counts': dict(sorted(counts.items())), 'native_profile': dict(sorted(ranks.items())),
            'native_mass': sum(r * n for r, n in ranks.items()), 'wrappers': 2 * sum(ranks.values()),
            'cover_maps': counts['map'], 'scalar_allowance': scalar}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if sha256(SOURCE.read_bytes()).hexdigest() != PIN:
        raise ValueError('Source module pin')
    spec = importlib.util.spec_from_file_location('retained_math', SOURCE)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    source, R, A, T, U, routes = m.load()
    programs, cases = {}, {}
    for name, dirty in (('owned_eight_A', False), ('dirty_eight_A_before_cleanup', True)):
        capture, repair = build(m, R, A, T, U, routes, dirty)
        digest = replay(m, R, A, T, U, routes, capture, repair, dirty)
        programs[name] = {'capture': capture, 'repair': repair}
        cases[name] = {'all_output_rows_sha256': digest, **price(capture + repair)}
        m.need(cases[name]['native_profile'] == {1: 112, 8: 8}, 'Eight-record profile')
        m.need(cases[name]['cover_maps'] == 240, 'Current-chart map bill')
    capture, repair = build(m, R, A, T, U, routes, False)
    bad = list(repair)
    bad.remove(next(e for e in bad if e['op'] == 'add' and e.get('dst') == f'X{T[0]}'
                    and e.get('src', '').startswith('Y') and int(e['src'][1:]) not in T))
    try:
        replay(m, R, A, T, U, routes, capture, bad, False)
    except ValueError as error:
        control = str(error)
    else:
        raise ValueError('Missing query-term control failed')
    args.out.mkdir(parents=True, exist_ok=True)
    raw = m.encoded(programs) + b'\n'
    (args.out / 'EIGHT-RECORD-WORDS.json').write_bytes(raw)
    receipt = {'status': 'PASS_EIGHT_RECORD_CURRENT_QUERY_REPAIR',
               'source_module_sha256': PIN, 'source_certificate_compressed_sha256': m.SOURCE_SHA,
               'programs_sha256': sha256(raw).hexdigest(), 'cases': cases,
               'negative_control': {'missing_T_query_term': control},
               'scope': 'Exact added local operator and frame words. Dirty case has residual h+N2Y1 and requires cleanup. No new record or child hosting is proved.'}
    (args.out / 'EIGHT-RECORD-CHECKS.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': receipt['status'], 'cases': cases}, sort_keys=True))


if __name__ == '__main__':
    main()
