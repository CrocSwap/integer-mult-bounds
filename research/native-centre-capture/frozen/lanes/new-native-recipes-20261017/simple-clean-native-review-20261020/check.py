#!/usr/bin/env python3
"""Check the direct native pair with exact columns."""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import argparse
import importlib.util
import json
import struct


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
HELPER = HERE.parent/'row-capture-native-review-20261020/check.py'
HELPER_PIN = '5b8f2839db4fd4b0e4b24d5b8f8938c74a15497ae0e58f324896cf431d3ecb84'
if sha256(HELPER.read_bytes()).hexdigest() != HELPER_PIN:
    raise ValueError('Independent arithmetic helper pin')
spec = importlib.util.spec_from_file_location('independent_row_tools', HELPER)
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)
q.read(HELPER, HELPER_PIN)
need = q.need
SOURCE = q.RAW/'simple-clean-native-20261020'


def multiply(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def rotate(a, power):
    r, i = a
    return ((r, i), (-i, r), (-r, -i), (i, -r))[power % 4]


def full_kernel(rank):
    result = {}
    for mask in range(1 << rank):
        value = (1, 0)
        for j in range(rank):
            value = multiply(value, (1, -1 if mask >> j & 1 else 1))
        result[mask] = value
    return result


def monomial_table(record):
    if record is None:
        return list(range(512)), [0]*512
    need(set(record) == {'matrix_rows', 'quadratic_rows', 'linear_Z4', 'offset', 'phase'},
         'Complete monomial record')
    rows, quadratic, linear = (record[k] for k in ('matrix_rows', 'quadratic_rows', 'linear_Z4'))
    need(len(rows) == len(quadratic) == len(linear) == 9, 'Nine-axis monomial')
    need(all(0 <= row < 512 for row in rows+quadratic) and
         all(0 <= value < 4 for value in linear) and
         0 <= record['offset'] < 512 and 0 <= record['phase'] < 4, 'Literal monomial domain')
    image, phases = [], []
    for x in range(512):
        image.append(record['offset'] ^ sum(((row & x).bit_count() & 1) << j
                                            for j, row in enumerate(rows)))
        phase = record['phase']
        for j in range(9):
            if x >> j & 1:
                phase += linear[j]+2*((quadratic[j] & x) >> (j+1)).bit_count()
        phases.append(phase % 4)
    need(sorted(image) == list(range(512)), 'Monomial address permutation')
    return image, phases


def phase_check(record, expected, denominator):
    rank = record['rank']
    left, lp = monomial_table(record['left'])
    right, rp = monomial_table(record['right'])
    child = full_kernel(rank)
    need(len(expected) == 1 << rank, 'Exact support rank')
    digest = sha256()
    for x in range(512):
        result = []
        for mask, value in child.items():
            address = right[x] ^ mask
            y = left[address]
            actual = rotate(value, rp[x]+lp[address])
            target = expected.get(x ^ y, (0, 0))
            need((actual[0] << denominator, actual[1] << denominator) ==
                 (target[0] << rank, target[1] << rank), 'Exact spatial coefficient and phase')
            result.append((y, actual))
        need(len({y for y, _ in result}) == len(expected), 'Complete spatial support')
        digest.update(b''.join(struct.pack('<HHii', x, y, value[0], value[1])
                               for y, value in sorted(result)))
    return {'columns': 512, 'nonzero_coefficients': 512*(1 << rank),
            'exact_column_digest': digest.hexdigest()}


def kernels(payload, ports, selected):
    full = [['C', 1 << j, 1] for j in range(9)]
    frames = [[], full]+[[['C', v, 1]] for v in ports]+[
        [['C', v, -1]]+full for v in ports]
    need(payload['physical_frame_circuits'] == frames, 'Every literal physical type')
    wanted = {'full'} | {'advance:'+str(p) for p in range(112)} | {
        'exit:'+str(p) for p in range(112) if p not in selected}
    need(set(payload['native_kernels']) == wanted, 'All209 distinct kernels')
    f9 = full_kernel(9)
    report = {}
    identity = list(range(512)), [0]*512
    for index, (key, item) in enumerate(sorted(payload['native_kernels'].items())):
        if key == 'full':
            edge, rank, kernel, denominator = [0, 1], 9, f9, 9
            need(monomial_table(item['recipe']['left']) == identity and
                 monomial_table(item['recipe']['right']) == identity, 'Direct FULL identity wrappers')
        else:
            kind, port = key.split(':')
            p, vector = int(port), ports[int(port)]
            if kind == 'exit':
                edge, rank, denominator = [1, 114+p], 1, 1
                kernel = {0: (1, -1), vector: (1, 1)}
            else:
                need(kind == 'advance', 'Kernel class')
                edge, rank, denominator = [2+p, 1], 8, 10
                kernel = {}
                for mask in range(512):
                    a, b = multiply((1, -1), f9[mask]), multiply((1, 1), f9[mask ^ vector])
                    value = a[0]+b[0], a[1]+b[1]
                    if value != (0, 0):
                        kernel[mask] = value
        need(item['edge'] == edge and item['rank'] == item['recipe']['rank'] == rank,
             'Declared physical edge and rank')
        report[key] = phase_check(item['recipe'], kernel, denominator)
        if (index+1) % 32 == 0:
            print('Exact independent kernels', index+1, '/209', flush=True)
    return report


def direct_events(capture, ports, pivots):
    selected = set(pivots)
    ordinary = [p for p in range(112) if p not in selected]
    stages = [
        ('source_progress', [['native', p, 2+p, 1, 8, 'advance:'+str(p)] for p in range(112)]),
        ('selected_progress', [['native', 112+p, 2+p, 1, 8, 'advance:'+str(p)] for p in pivots]),
        ('ordinary_full_progress', [['native', 112+p, 0, 1, 9, 'full'] for p in ordinary]),
        ('ordinary_self_adds', [['scalar', ['add', 112+p, p, '1'], 1] for p in ordinary]),
        ('ordinary_negative_lines', [['native', 112+p, 1, 114+p, 1, 'exit:'+str(p)] for p in ordinary]),
        ('source_row_code', [['scalar', gate, 1] for gate in capture]),
        ('signed_selected_exchanges', [
            event for p in pivots for event in (
                ['scalar', ['add', 112+p, p, '1'], 1],
                ['scalar', ['add', p, 112+p, '-1'], 1],
                ['scalar', ['add', 112+p, p, '1'], 1])]),
    ]
    events, ranges = [], {}
    for name, records in stages:
        ranges[name] = [len(events), len(events)+len(records)]
        events.extend(records)
    return events, ranges


def adjoint_events(events, permutation):
    result = []
    for event in events:
        if event[0] == 'native':
            result.append([event[0], permutation[event[1]]]+event[2:])
        else:
            op, target, source, coefficient = event[1]
            coefficient = F(coefficient)
            gate = (['add', permutation[source], permutation[target], str(-coefficient)]
                    if op == 'add' else ['scale', permutation[target], None, str(1/coefficient)])
            result.append(['scalar', gate, event[2]])
    return result


def endpoints(code, selected):
    forward, inverse, custom, custom_inverse = (q.unit(640) for _ in range(4))
    for p in range(112):
        if p in selected:
            forward[p], forward[112+p] = {112+p: F(-1)}, dict(code[p])
            inverse[p] = {112+p: F(1)}
            q.add(inverse[p], {j: -v for j, v in code[p].items() if j != p})
            inverse[112+p] = {p: F(-1)}
            custom[p], custom[112+p] = {112+p: F(1)}, {p: F(-1)}
            custom_inverse[p], custom_inverse[112+p] = {112+p: F(-1)}, {p: F(1)}
        else:
            q.add(forward[112+p], {p: F(1)})
            q.add(inverse[112+p], {p: F(-1)})
            q.add(custom[p], {112+p: F(-1)})
            q.add(custom_inverse[p], {112+p: F(1)})
            for j in selected:
                q.add(custom[p], {112+j: -code[j].get(p, F(0))})
                q.add(custom_inverse[p], {j: code[j].get(p, F(0))})
    for word, back in ((forward, inverse), (custom, custom_inverse)):
        need(q.mul(word, back) == q.mul(back, word) == q.unit(640), 'Both complete inverse orders')
    return {'Fsimple': forward, 'Bcustom': custom}, inverse


def replay(word, expected, start, final, kernels, ranges):
    need(word['start'] == start and word['final'] == final and word['stage_ranges'] == ranges,
         'Exact full boundary and stage ledger')
    current, used, profile = list(start), set(), Counter()
    for event in word['events']:
        if event[0] == 'native':
            _, field, before, after, rank, key = event
            need(0 <= field < 224 and current[field] == before, 'Native field and input type')
            need(kernels[key]['edge'] == [before, after] and kernels[key]['rank'] == rank,
                 'Exact checked kernel occurrence')
            current[field] = after
            used.add(key)
            profile[rank] += 1
        else:
            need(event[0] == 'scalar', 'Complete event grammar')
            (op, target, source, _), frame = event[1:]
            need(0 <= target < 224 and current[target] == frame, 'Scalar target physical type')
            if op == 'add':
                need(0 <= source < 224 and source != target and current[source] == frame,
                     'Equal source and target physical types')
            else:
                need(op == 'scale' and source is None, 'Scalar scale grammar')
    need(current == final and used == set(kernels), 'Complete final and used-kernel ledger')
    need(profile == {1: 96, 8: 128, 9: 96}, 'Exact full native profile')
    scalars = [e[1] for e in word['events'] if e[0] == 'scalar']
    need(q.reverse(scalars, 640) == q.transpose(expected, 640), 'All640 reverse columns')
    rows, growth = q.prefix(scalars, 640)
    need(rows == expected and rows[224:] == q.unit(640)[224:] and
         all(j < 224 for row in rows[:224] for j in row), 'Forward rows and416 arbitrary outside roles')
    prices = {name: q.price([e[1] for e in word['events'][a:b] if e[0] == 'scalar'])
              for name, (a, b) in ranges.items()}
    need(sum(prices.values()) == q.price(scalars) == 2912, 'Complete scalar price')
    need(prices['ordinary_self_adds'] == 768 and prices['source_row_code'] == 1760 and
         prices['signed_selected_exchanges'] == 384, 'Exact scalar stage prices')
    for stage in ('ordinary_self_adds', 'source_row_code'):
        a, b = ranges[stage]
        missing = next(i for i in range(a, b) if word['events'][i][0] == 'scalar'
                       and word['events'][i][1][0] == 'add')
        bad = [e[1] for i, e in enumerate(word['events']) if e[0] == 'scalar' and i != missing]
        need(q.reverse(bad, 640) != q.transpose(expected, 640), 'Missing ADD negative control')
    return {'input_columns': 640, 'unchanged_arbitrary_roles': 416, 'native_profile': dict(profile),
            'native_mass': sum(r*n for r, n in profile.items()), 'native_children': sum(profile.values()),
            'scalar_price': 2912, 'scalar_stage_prices': prices, 'growth': growth,
            'native_side_maps_upper_bound': 448, 'boundary_adapters': 0,
            'extra_fields': 0, 'private_fields': 0, 'odd_divisions': 0}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    q.frozen(SOURCE, 'FREEZE.json', '1e08caf1376ffb3a74eac87200e6165c969a08d71d5c028a7c8940093f830089')
    q.frozen(HERE.parent/'clean-centre-exchange-review-20261020', 'FREEZE.json',
             '6cd34040ecd7d832f1bae3d44c5a7b97dcc11022d843e48007c5474cc4f3701d')
    payload = json.loads(q.read(SOURCE/'run-normal/SIMPLE-CLEAN-NATIVE.json.gz',
                                '1bdddb7955d0ada6dabcf150fce0a568cd336a846f51be3324c081f10dd374c7', True))
    clean = json.loads(q.read(q.RAW/'clean-late-exchange-20261020/run-normal/CLEAN-LATE-EXCHANGE.json.gz',
                              'b0432322c28ad3a03af8da550a0b7c7df048c7ff5a0664acc7f78efffcffd083', True))
    capture = json.loads(q.read(q.ALG/'run-normal/ROW-CAPTURE.json',
                                '4c98af5d7a1437a03f53e84f0f2cbc7cd2ac47d4c6d4ee1523c16bf469692eb7'))
    need(payload['ports'] == clean['ports'] and payload['selected_ports'] == clean['selected_ports'] == q.P,
         'Actual common ports and selected set')
    need(payload['code'] == clean['code'] == capture['code'], 'Exact reviewed row code')
    code, selected = q.rows(payload['code']), set(q.P)
    for p, row in enumerate(code):
        need(row == {p: F(1)} if p not in selected else
             {j: v for j, v in row.items() if j in selected} == {p: F(1)},
             'Row code I+e_P B with B_P zero')
    need(q.reverse(capture['scalar_word'], 112) == q.transpose(code, 112) and
         q.price(capture['scalar_word']) == 1760, 'Actual complete row code')
    phase_report = kernels(payload, payload['ports'], selected)
    events, ranges = direct_events(capture['scalar_word'], payload['ports'], q.P)
    start, final = [0]*640, [0]*640
    for p in range(112):
        start[p], final[p] = 2+p, 1
        start[112+p], final[112+p] = (2+p, 1) if p in selected else (0, 114+p)
    permutation = list(range(640))
    for p in q.P:
        permutation[p], permutation[112+p] = 112+p, p
    need([start[p] for p in permutation] == start and [final[p] for p in permutation] == final,
         'Selected permutation preserves literal endpoint operators')
    need(set(payload['words']) == {'Fsimple', 'Bcustom'}, 'Both complete words')
    need(payload['words']['Fsimple']['events'] == events, 'Exact direct chronology')
    need(payload['words']['Bcustom']['events'] == adjoint_events(events, permutation),
         'Same-order physical inverse-adjoint and every field relabeling')
    need(payload['words']['Bcustom']['wire_permutation'] ==
         {str(i): j for i, j in enumerate(permutation) if i != j}, 'Exact wire permutation')
    expected, back = endpoints(code, selected)
    inverse_transpose = q.transpose(back, 640)
    conjugate = [{permutation[j]: value for j, value in inverse_transpose[permutation[i]].items()}
                 for i in range(640)]
    need(conjugate == expected['Bcustom'], 'Complete selected-conjugate inverse-adjoint identity')
    reports = {}
    for name, word in payload['words'].items():
        need(q.rows(payload['content_maps'][name]) == expected[name][:224], 'Declared content map')
        reports[name] = replay(word, expected[name], start, final, payload['native_kernels'], ranges)
    need(reports['Fsimple']['growth'] == {'row_one_norm': '22', 'binary_height': 1} and
         reports['Bcustom']['growth'] == {'row_one_norm': '4', 'binary_height': 1}, 'Exact prefix bounds')
    report = {
        'status': 'PASS_INDEPENDENT_DIRECT_SIMPLE_CLEAN_NATIVE',
        'words': reports, 'phase_kernels': phase_report,
        'phase_method': 'Every exact spatial column from Gaussian integer convolution coefficients; no compiler or Pauli interpreter.',
        'total_spatial_columns': sum(r['columns'] for r in phase_report.values()),
        'total_nonzero_spatial_coefficients': sum(r['nonzero_coefficients'] for r in phase_report.values()),
        'scope': 'Two complete local tensor-liftable words. No routed caller, recursive hosting, or complete supplier bound.',
    }
    args.out.mkdir(parents=True, exist_ok=True)
    for name, value in [('REVIEW-CHECKS.json', report), ('INPUTS.json', q.INPUTS)]:
        (args.out/name).write_text(json.dumps(value, sort_keys=True, indent=2)+'\n')
    print(report['status'], flush=True)


if __name__ == '__main__':
    main()
