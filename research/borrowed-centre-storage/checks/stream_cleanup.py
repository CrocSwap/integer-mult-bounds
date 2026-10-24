"""Check the owner-local cleanup without a producer import.

Use exact rows, actual registered views, and a separate storage audit.
"""

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from functools import lru_cache
import gzip
from hashlib import sha256
import json
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1] / 'sources'
LANES = ROOT / 'work/centre-encoding-campaign-20261014/lanes'
HERE = ROOT / 'work/centre-encoding-campaign-20261014/lanes/portable-source-codes/dirty-record-hosting-20261015/algebra/stream-cleanup-review'
PACK = HERE.parent.parent / 'masked-query'
A = (0, 7, 20, 27, 36, 46, 57, 111)
T = (21, 37, 47, 76, 81, 87, 92, 110)
V = A + T
U = tuple(p for p in range(112) if p not in V)
OFF = U + T
AXES = tuple(1 << i for i in range(73))
FULL = tuple((v, 1) for v in AXES[:25])
PINS = {}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def read(path, expected, compressed=False):
    raw = path.read_bytes()
    digest = sha256(raw).hexdigest()
    need(digest == expected, 'Source pin: ' + str(path))
    PINS[str(path.relative_to(ROOT))] = digest
    return gzip.decompress(raw) if compressed else raw


def add(a, b, c=Q(1)):
    out = dict(a)
    for key, value in b.items():
        out[key] = out.get(key, 0) + c * value
        if not out[key]:
            del out[key]
    return out


def scale(row, c):
    return {key: c * value for key, value in row.items() if c * value}


def move(row, port):
    letter = (2, port)
    out = {}
    for (name, path), c in row.items():
        path = path[1:] if path and path[0] == letter else (letter,) + path
        key = name, path
        out[key] = out.get(key, 0) + c
    return {key: c for key, c in out.items() if c}


def bank(name):
    return {p: {(name + str(p), ()): Q(1)} for p in range(112)}


def query(rows, ports, R, routed=False):
    out = [{} for _ in range(8)]
    for p in ports:
        value = move(rows[p], p) if routed else rows[p]
        for k in range(8):
            if R[k][p]:
                out[k] = add(out[k], value, R[k][p])
    return out


def scatter(values, ports, R, routed=False):
    out = {}
    for p in ports:
        row = {}
        for k in range(8):
            if R[k][p]:
                row = add(row, values[k], R[k][p] / 4)
        out[p] = move(row, p) if routed else row
    return out


def routed_matrix(matrix, rows):
    gathered = {p: move(rows[p], p) for p in range(112)}
    out = {}
    for p, coefficients in enumerate(matrix):
        row = {}
        for q, c in coefficients.items():
            row = add(row, gathered[q], c)
        out[p] = move(row, p)
    return out


def apply(columns, vector):
    answer = 0
    while vector:
        bit = vector & -vector
        answer ^= columns[bit.bit_length() - 1]
        vector ^= bit
    return answer


@lru_cache(None)
def phase(terms):
    linear, pairs = [0] * 73, set()
    for vector, coefficient in terms:
        support = [i for i in range(73) if vector >> i & 1]
        for i in support:
            linear[i] = (linear[i] + coefficient) % 4
        if coefficient % 2:
            for at, i in enumerate(support):
                for j in support[at + 1:]:
                    if (i, j) in pairs:
                        pairs.remove((i, j))
                    else:
                        pairs.add((i, j))
    return tuple(linear), frozenset(pairs)


def transport(terms, g, shift):
    return tuple((apply(g, v), c) for v, c in terms) + ((shift, 2),)


def actual_routes(certificate):
    routes = {}
    for p in range(112):
        entries = [e for e in certificate['programs']['F_2'] if e[0] == 'cover_map' and e[1] == ['L', p]]
        need(len(entries) >= 2, 'Source has the complete stage-2 X route')
        record = certificate['map_registry'][entries[0][2]]
        g = tuple(record['owner_right_matrix_columns'])
        shift = record['payload_translation_at_identity_owner']
        need(len(g) == 73 and tuple(apply(g, v) for v in g) == AXES, 'Actual owner involution')
        need(all((g[i] & g[j]).bit_count() % 2 == (i == j) for i in range(73) for j in range(73)), 'Actual owner orthogonality')
        need(phase(transport(FULL, g, shift)) == phase(FULL), 'Registered full-frame phase')
        back = apply(g, shift)
        need(phase(transport(FULL, g, back)) == phase(FULL), 'Inverse full-frame phase')
        need(apply(g, shift) ^ back == 0 and apply(g, back) ^ shift == 0, 'Both affine inverse translations')
        need(all(v < 512 for v in g[17:25]), 'Actual local chart')
        normals = [q for q in range(1, 512) if all((q & v).bit_count() % 2 == 0 for v in g[17:25])]
        need(len(normals) == 1 and normals[0].bit_count() % 2 == 1, 'Actual odd port normal')
        q = normals[0]
        need(apply(g, q) == q, 'Normal fixed by owner route')
        routes[p] = dict(g=g, shift=shift, inverse_shift=back, q=q, registry=entries[0][2])
    return routes


def gate(dst, src, coefficient=1):
    return dict(op='add', dst=dst, src=src, c=str(coefficient))


def reverse(events):
    answer = []
    for e in reversed(events):
        e = dict(e)
        e['c'] = str(-Q(e['c']) if e['op'] == 'add' else 1 / Q(e['c']))
        answer.append(e)
    return answer


def reconstruct(R, routes):
    prepare = [gate(f'X0:{p}', f'X1:{p}', -1) for p in U]
    for p in V:
        a, b = f'X0:{p}', f'X1:{p}'
        prepare += [gate(a, b), gate(b, a, -1), gate(a, b), dict(op='scale', field=b, c='-1')]
    sums = [gate(f'Y1:{p}', f'{b}:{p}') for p in T for b in ('X0', 'X1')]

    def alias(sign):
        events = [dict(op='private_begin')]
        for k in range(8):
            events += [dict(op='clear', field='C', frame='current')]
            events += [gate('C', f'X0:{p}', R[k][p]) for p in range(112) if R[k][p]]
            events += [gate(f'X1:{p}', 'C', sign * R[k][p] / 4) for p in OFF if R[k][p]]
        return events + [dict(op='clear', field='C', frame='identity'), dict(op='private_end')]

    fields = [(f'R{p}', p) for p in A] + [(f'X1:{p}', p) for p in OFF] + [(f'Y1:{p}', p) for p in T]

    def views(items, inverse=False):
        return [dict(op='map', field=name, letter=[2, p], g=list(routes[p]['g']),
                     shift=routes[p]['inverse_shift' if inverse else 'shift']) for name, p in items]

    response = []
    for b, ports, sign in (('X1', OFF, 1), ('Y1', T, -1)):
        for a in A:
            for p in ports:
                coefficient = sum(R[k][a] * R[k][p] for k in range(8)) / 4
                if coefficient:
                    response.append(gate(f'R{a}', f'{b}:{p}', sign * coefficient))
    correction = []
    for a in A:
        correction += [gate(f'X1:{a}', f'R{a}'), gate(f'Y1:{a}', f'R{a}', -1)]
    for p in T:
        for a in A:
            coefficient = sum(R[k][p] * R[k][a] for k in range(8)) / 4
            if coefficient:
                correction += [gate(f'X1:{p}', f'R{a}', -coefficient), gate(f'Y1:{p}', f'R{a}', coefficient)]
    content = [
        ('query_subtraction', 'owner_sweep', [gate(f'R{p}', f'Y0:{p}', -1) for p in A]),
        ('source_prepare', 'owner_sweep', prepare),
        ('selected_sum_prepare', 'owner_sweep', sums),
        ('source_alias', 'owner_sweep', alias(1)),
        ('source_gather', 'family_sweep', views(fields)),
        ('routed_response', 'owner_sweep', response),
        ('source_return', 'family_sweep', views(reversed(fields), True)),
        ('source_alias_inverse', 'owner_sweep', alias(-1)),
        ('selected_sum_inverse', 'owner_sweep', reverse(sums)),
        ('source_prepare_inverse', 'owner_sweep', reverse(prepare)),
        ('selected_error_correction', 'owner_sweep', correction)]
    return [dict(name=name, scope=scope, events=events) for name, scope, events in content]


def invoice(events):
    counts, coefficients, scalar = Counter(), Counter(), 0
    for e in events:
        op = e['op']
        counts[op] += 1
        if op == 'clear':
            scalar += 2
        elif op in ('add', 'scale'):
            c = Q(e['c'])
            n, d = abs(c.numerator), c.denominator
            need(n and not n & (n - 1) and not d & (d - 1), 'Dyadic-unit coefficient')
            coefficients[op + ':' + str(c)] += 1
            scalar += (2 * (2 + n.bit_length() + n.bit_count() + d.bit_length() - 1)
                       if op == 'add' else 2 * (abs(n.bit_length() - d.bit_length()) + (c < 0)))
    return dict(scalar=scalar, cover_maps=counts['map'], native_mass=0, native_profile={},
                native_wrappers=0, events=dict(counts), coefficients=dict(coefficients))


def storage_audit(parts):
    private_bodies, owner_blocks, family_blocks = 0, 0, 0
    real = {f'{b}:{p}' for b in ('X0', 'Y0', 'X1', 'Y1') for p in range(112)} | {f'R{p}' for p in A}
    for part in parts:
        private, initialized, zero_at_identity = False, False, False
        if part['scope'] == 'family_sweep':
            family_blocks += 1
            need(all(e['op'] == 'map' and e['field'] in real for e in part['events']), 'A map needs a complete real family')
            continue
        need(part['scope'] == 'owner_sweep', 'Known complete-sweep extent')
        owner_blocks += 1
        for e in part['events']:
            op = e['op']
            need(op in ('add', 'scale', 'clear', 'private_begin', 'private_end'), 'No map or native job inside an owner body')
            if op == 'private_begin':
                need(not private, 'No nested private lifetime')
                private, initialized, zero_at_identity = True, False, False
                private_bodies += 1
            elif op == 'private_end':
                need(private and zero_at_identity, 'Scratch must end at zero and identity inside its owner')
                private = False
            else:
                names = [e[k] for k in ('field', 'dst', 'src') if k in e]
                need(all(f in real or f == 'C' for f in names), 'Known real field or the one local scratch')
                if op == 'clear':
                    need(e['field'] == 'C' and private, 'Only the current owned scratch may be cleared')
                    initialized, zero_at_identity = True, e['frame'] == 'identity'
                elif 'C' in names:
                    need(private and initialized, 'Scratch must be initialized inside its current owner')
                    if e.get('dst', e.get('field')) == 'C':
                        zero_at_identity = False
        need(not private, 'No scratch lifetime crosses a complete-sweep boundary')
    return dict(owner_sweeps=owner_blocks, family_sweeps=family_blocks, private_owner_bodies=private_bodies,
                peak_owned_scratch=1, private_cover_maps=0, destructive_real_field_clears=0)


def row_encoding(rows):
    return {field: [[name, list(path), str(c)] for (name, path), c in sorted(row.items())]
            for field, row in sorted(rows.items())}


def replay(parts, initial, frames, routes, checkpoints=None):
    storage_audit(parts)
    rows, frames = deepcopy(initial), deepcopy(frames)
    phase_checks, maps, boundary_states = 0, 0, []
    for part in parts:
        for e in part['events']:
            op = e['op']
            if op == 'add':
                dst, src = e['dst'], e['src']
                need(phase(frames[dst]) == phase(frames[src]), 'Exact native phase at every ADD')
                rows[dst] = add(rows[dst], rows[src], Q(e['c']))
                phase_checks += 1
            elif op == 'scale':
                rows[e['field']] = scale(rows[e['field']], Q(e['c']))
            elif op == 'clear':
                rows['C'] = {}
                frames['C'] = FULL if e['frame'] == 'current' else ()
            elif op == 'map':
                f, (stage, p) = e['field'], e['letter']
                need(stage == 2 and tuple(e['g']) == routes[p]['g'], 'Exact right-owner route')
                need(e['shift'] in (routes[p]['shift'], routes[p]['inverse_shift']), 'Exact registered view translation')
                need(phase(frames[f]) == phase(FULL), 'Every gathered real family is FULL')
                frames[f] = transport(frames[f], tuple(e['g']), e['shift'])
                need(phase(frames[f]) == phase(FULL), 'Every physical view preserves FULL phase')
                rows[f] = move(rows[f], p)
                maps += 1
            elif op == 'private_end':
                need(not rows['C'] and phase(frames['C']) == phase(()), 'Exact zero/I scratch at owner exit')
        if checkpoints and part['name'] in checkpoints:
            for field, expected in checkpoints[part['name']].items():
                need(rows[field] == expected, 'Intermediate identity: ' + part['name'] + ':' + field)
        boundary_states.append(dict(part=part['name'], C_zero=not rows['C'], C_identity=phase(frames['C']) == phase(())))
    return rows, frames, dict(add_phase_checks=phase_checks, physical_views=maps, boundaries=boundary_states)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    need(shutil.disk_usage(HERE).free >= 3 * 1024**3, 'At least three GiB free')
    manifest = json.loads(read(PACK / 'STREAM-CLEANUP-MANIFEST.json',
        '1ce42dd7732c39b4f6f9dec1329e7e3145751e8827e7020fe6d5ee04c7e67e03'))
    files = {name: read(PACK / name, pin) for name, pin in manifest['files'].items()}
    packet = json.loads(files['stream-cleanup/STREAM-CLEANUP-WORD.json'])
    producer = json.loads(files['stream-cleanup/STREAM-CLEANUP.json'])
    for path, digest in packet['source_pins'].items():
        read(LANES / path, digest)
    accepted = json.loads(read(HERE.parent / 'masked-query-review/REVIEW.json',
        '04dfde7cd7182f711bca4d75f0a258f447131dd65b779bef7095e4729d542488'))
    mask_raw = gzip.decompress((PACK / 'masked-sum/MASKED-QUERY-PROGRAM.json.gz').read_bytes())
    need(sha256(mask_raw).hexdigest() == accepted['final_masked_sum_payload_sha256'], 'Accepted masked-query payload')
    mask = json.loads(mask_raw)
    certificate = json.loads(read(LANES / 'paired-package-review/upstream-followthrough-20261015/base/research/joint-query/certificate.json.gz',
        'a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7', True))
    R = [[Q(row.get(str(p), 0)) for p in range(112)] for row in certificate['R_rows']]
    need([list(A), list(T), list(U)] == [certificate[k + '_ports'] for k in ('A', 'T', 'U')], 'Actual source port partition')
    need(R == [[Q(row.get(str(p), 0)) for p in range(112)] for row in mask['R']], 'Actual source matrix')
    routes = actual_routes(certificate)
    parts = reconstruct(R, routes)
    need(parts == packet['parts'], 'Every independently reconstructed block and scope')
    word = [e for part in parts for e in part['events']]
    need(word == packet['word'], 'Every literal event in order')
    storage = storage_audit(parts)
    need(storage['owner_sweeps'] == 9 and storage['family_sweeps'] == 2 and storage['private_owner_bodies'] == 2, 'Exact sweep extents')

    x, y, c, beta = (bank(n) for n in ('x:', 'y:', 'c:', 'beta:'))
    h = {p: {('h:' + str(p), ()): Q(1)} for p in A}
    error = {p: {} for p in range(112)}
    error.update({p: scale(h[p], -1) for p in A})
    error.update(scatter(query(h, A, R), T, R))
    dx = {p: add(x[p], error[p]) for p in range(112)}
    dy = {p: add(y[p], error[p], -1) for p in range(112)}
    ell = {p: c[p] if p in V else add(x[p], c[p]) for p in range(112)}
    v = {p: beta[p] if p in V else y[p] for p in range(112)}
    H, TB = ([{int(q): Q(value) for q, value in row.items()} for row in mask[key]]
             for key in ('source_response', 'target_code'))
    response_h, response_t = routed_matrix(H, ell), routed_matrix(TB, v)
    output_y0 = {p: add(response_h[p], response_t[p]) for p in range(112)}
    f = query(x, range(112), R)
    need(query(dx, range(112), R) == f, 'Dirty source has the same old query')
    projection = scatter(f, OFF, R)
    old_y1 = {p: add(add(x[p], y[p]), projection[p], -1) for p in OFF}
    debt = scatter(query(old_y1, OFF, R, True), A, R, True)
    frozen_g = json.loads(read(HERE.parent / 'FUTURE-READ-ROWS.json',
        'bce692e721ee7e0db485509cc12a3384a2e24ec2014626954aab5d4dde0059d5'))
    need([[p, [[n, [list(t) for t in w], str(v)] for (n, w), v in sorted(row.items())]]
          for p, row in sorted(debt.items())] == frozen_g, 'Exact frozen donor-debt rows')
    q = query({p: add(ell[p], y[p]) for p in U}, U, R, True)
    q_selected = scatter(q, A, R, True)
    need(all(output_y0[p] == q_selected[p] for p in A), 'Accepted selected query in actual source order')
    initial = {f'X0:{p}': ell[p] for p in range(112)}
    initial.update({f'Y0:{p}': output_y0[p] for p in range(112)})
    initial.update({f'X1:{p}': dx[p] if p in V else c[p] for p in range(112)})
    initial.update({f'Y1:{p}': dy[p] if p in V else add(beta[p], y[p], -1) for p in range(112)})
    initial.update({f'R{p}': add(h[p], debt[p]) for p in A})
    initial['C'] = {('private:', ()): Q(1)}
    latent = {name for row in initial.values() for name, _ in row}
    need(len(latent) == 457, 'All 448 data, eight donor, and one scratch input columns')
    frames = {field: FULL for field in initial}
    frames['C'] = ()
    for p in range(112):
        if p not in A:
            frames[f'Y0:{p}'] += ((routes[p]['q'], -1),)
        if p in U:
            frames[f'Y1:{p}'] += ((routes[p]['q'], -1),)
    alias = {p: add(c[p], projection[p]) if p in OFF else c[p] for p in range(112)}
    sums = {p: add(add(c[p], dx[p]), dy[p]) for p in T}
    checkpoints = {
        'source_prepare': {**{f'X0:{p}': dx[p] for p in range(112)}, **{f'X1:{p}': c[p] for p in range(112)}},
        'selected_sum_prepare': {f'Y1:{p}': sums[p] for p in T},
        'source_alias': {**{f'X0:{p}': dx[p] for p in range(112)}, **{f'X1:{p}': alias[p] for p in range(112)}},
        'routed_response': {f'R{p}': move(h[p], p) for p in A},
        'source_return': {**{f'R{p}': h[p] for p in A}, **{f'X1:{p}': alias[p] for p in range(112)}, **{f'Y1:{p}': sums[p] for p in T}},
        'source_alias_inverse': {f'X1:{p}': c[p] for p in range(112)},
        'selected_sum_inverse': {f'Y1:{p}': dy[p] for p in T},
        'source_prepare_inverse': {field: row for field, row in initial.items() if field.startswith(('X0:', 'X1:'))}}
    expected = deepcopy(initial)
    for p in V:
        expected[f'X1:{p}'], expected[f'Y1:{p}'] = x[p], y[p]
    for p in A:
        expected[f'R{p}'] = h[p]
    expected['C'] = {}
    rows, end_frames, replay_receipt = replay(parts, initial, frames, routes, checkpoints)
    need(rows == expected, 'Every final output row on all 457 latent inputs')
    need(all(phase(end_frames[f]) == phase(frames[f]) for f in frames), 'Every native endpoint frame returns')
    output_hash = sha256(encoded(row_encoding(rows))).hexdigest()
    need(output_hash == producer['all_output_rows_sha256'], 'Independent output digest agrees')
    bill = invoice(word)
    need({k: v for k, v in bill.items() if k != 'coefficients'} == producer['invoice'], 'Independent total invoice')
    part_bills = {part['name']: invoice(part['events']) for part in parts}
    need(all({k: v for k, v in bill.items() if k != 'coefficients'} == producer['part_invoices'][name]
             for name, bill in part_bills.items()), 'Every independent component invoice')
    accesses = [e[k] for e in word for k in ('field', 'dst', 'src') if k in e]
    need(not any(f.startswith('Y0:') and int(f[3:]) not in A for f in accesses), 'No off-A Y0 access')
    need(not any(f.startswith('Y1:') and int(f[3:]) in U for f in accesses), 'No hole-frame Y1 access')
    need(all(isinstance(c, Q) for row in rows.values() for c in row.values()), 'Exact rational coefficients throughout')

    controls = {}
    for name in ('query_subtraction', 'selected_sum_prepare', 'source_alias', 'routed_response', 'selected_error_correction'):
        changed = [p for p in parts if p['name'] != name]
        result, _, _ = replay(changed, initial, frames, routes)
        controls['omit_' + name] = result != expected
    bad = deepcopy(parts)
    bad[3]['events'].insert(2, dict(parts[4]['events'][0], field='C'))
    try:
        storage_audit(bad)
    except ValueError as e:
        controls['map_private_C'] = str(e)
    bad = deepcopy(parts)
    bad[3]['events'].pop(-2)
    try:
        storage_audit(bad)
    except ValueError as e:
        controls['C_survives_owner_boundary'] = str(e)
    bad = deepcopy(parts)
    bad[3]['events'].pop(1)
    try:
        storage_audit(bad)
    except ValueError as e:
        controls['missing_initial_C_clear'] = str(e)
    bad = deepcopy(parts)
    bad[4]['events'][0]['shift'] ^= 1
    first_view = parts[4]['events'][0]
    changed_phase = phase(transport(FULL, tuple(first_view['g']), first_view['shift'] ^ 1))
    need(changed_phase != phase(FULL) and changed_phase[0][0] == 3, 'Concrete nontrivial phase from the wrong translation')
    try:
        replay(bad, initial, frames, routes)
    except ValueError as e:
        controls['wrong_registered_translation'] = str(e)
    need(len(controls) == 9 and all(controls.values()), 'All algebra, storage, and phase controls reject')
    receipt = dict(status='PASS_INDEPENDENT_OWNER_LOCAL_MASKED_CLEANUP', source_pins=PINS,
        latent_input_columns=457, output_fields=457, independent_data_columns=448,
        arbitrary_donor_columns=8, arbitrary_owned_scratch_columns=1,
        actual_stage2_routes=112, actual_cover_maps=240, output_rows_sha256=output_hash,
        storage_audit=storage, replay=replay_receipt, intermediate_checkpoints=list(checkpoints),
        invoice=bill, part_invoices=part_bills, negative_controls=controls,
        wrong_translation_phase_witness=dict(character=1, correct_exponent_mod4=1, changed_exponent_mod4=3),
        producer_imported_or_executed=False, native_kernel_replayed=False,
        global_schedule_replayed=False, off_selected_Y0_accesses=0, hole_frame_Y1_accesses=0,
        withdrawn_25360_scalar_1072_map_word_accepted=False,
        scope='The stated post-F2 local cut, with real disjoint family roles and complete barriers between the recorded sweeps.',
        open=['Actual changed F2 global owner admission', 'Later B3 admission and mixed target-code retirement',
              'Donor alignment and restoration in the new global schedule',
              'Recursive child hosting, primitive precision, complete stream invoice, supplier and kappa'])
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(receipt['status'])
    print(json.dumps(dict(invoice=bill, output_rows_sha256=output_hash, storage=storage), sort_keys=True))


if __name__ == '__main__':
    main()
