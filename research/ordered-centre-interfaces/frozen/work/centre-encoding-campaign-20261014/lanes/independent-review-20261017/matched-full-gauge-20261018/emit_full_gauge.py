#!/usr/bin/env python3
"""Emit the actual involution as a common-FULL scalar word."""
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
PINS = {
    'matching': ('controller-followthrough-20261017/matched-involution-20261018/MATCHED-INVOLUTION-PROGRAM.json',
                 'e2443eee2a7081ce3b57b9b7afcf4f1b061b9d8ddf0fbbeb5f7b29ce0d148902'),
    'native': ('oblique-native-20261017/matched-native-involution/MATCHED-NATIVE-PROGRAM.json.gz',
               '95f11d2b13fc75cb0d07e79ea17afdf3f46b4aca294117ffe1a988779e99f025'),
}


def need(test, message):
    if not test:
        raise ValueError(message)


def add(target, source, scale):
    for p, value in source.items():
        result = target.get(p, 0)+scale*value
        if result:
            target[p] = result
        else:
            target.pop(p, None)


def cost(event):
    kind = event[0]
    value = F(*event[-2:])
    a, b = abs(value.numerator), value.denominator
    need(a and b & (b-1) == 0, 'Dyadic coefficient')
    if kind == 'scale':
        need(a & (a-1) == 0, 'Unit scale')
        return 2*(abs(a.bit_length()-b.bit_length())+int(value < 0))
    return 2*(1+a.bit_length()+a.bit_count()+b.bit_length())


def replay(events):
    rows = [{i: F(1)} for i in range(112)]
    maximum = F(1)
    for event in events:
        target = event[1]
        value = F(*event[-2:])
        if event[0] == 'scale':
            rows[target] = {p: value*c for p, c in rows[target].items()}
        else:
            need(event[0] == 'add' and target != event[2], 'Scalar grammar')
            add(rows[target], rows[event[2]], value)
        maximum = max(maximum, sum(abs(c) for c in rows[target].values()))
    return rows, maximum


def reverse_columns(events):
    columns = [{i: F(1)} for i in range(112)]
    for event in reversed(events):
        target = event[1]
        value = F(*event[-2:])
        if event[0] == 'scale':
            columns[target] = {p: value*c for p, c in columns[target].items()}
        else:
            add(columns[event[2]], columns[target], value)
    return columns


def main():
    data = {}
    for name, (relative, pin) in PINS.items():
        raw = (LANES/relative).read_bytes()
        if relative.endswith('.gz'):
            raw = gzip.decompress(raw)
        need(sha256(raw).hexdigest() == pin, 'Actual source pin '+name)
        data[name] = json.loads(raw)
    matching, native = data['matching'], data['native']
    response = [{int(p): F(c) for p, c in row.items()} for row in native['response']]
    events, code = [], []

    def append(kind, target, origin, value, buffer=events):
        value = F(value)
        if kind == 'scale':
            if value != 1:
                buffer.append([kind, target, value.numerator, value.denominator])
        else:
            buffer.append([kind, target, origin, value.numerator, value.denominator])

    for pair in matching['pair_codes']:
        x, y = pair['ports']
        a, b, c, d = [F(value) for row in pair['matrix'] for value in row]
        need(all(abs(v) == 1 for v in (a, b, c, d)) and a*c+b*d == 0, 'Actual pair code')
        append('scale', x, None, a, code)
        append('add', x, y, b, code)
        append('scale', y, None, 2*d, code)
        append('add', y, x, c*a, code)
    events.extend(code)
    code_end = len(events)

    def signed_swap(x, y, weight):
        need(weight in (-1, 1), 'Signed swap weight')
        append('add', x, y, 1)
        append('add', y, x, -1)
        append('add', x, y, 1)
        append('scale', y if weight == 1 else x, None, -1)

    modes = matching['modes']
    mode_swaps = []
    for i, row in enumerate(matching['mode_response']):
        need(len(row) == 1, 'One matched mode')
        j, weight = next(iter(row.items()))
        j, weight = int(j), F(weight)
        if i < j:
            x, y = modes[i]['carrier'], modes[j]['carrier']
            signed_swap(x, y, weight)
            mode_swaps.append([x, y, str(weight)])
    need(len(mode_swaps) == 24, 'All24 mode swaps')
    swap_end = len(events)
    for event in reversed(code):
        value = F(*event[-2:])
        append(event[0], event[1], None if event[0] == 'scale' else event[2],
               1/value if event[0] == 'scale' else -value)
    undo_end = len(events)
    small_swaps = []
    for x in matching['small_ports']:
        need(len(response[x]) == 1, 'Actual small permutation')
        y, weight = next(iter(response[x].items()))
        need(weight == -1 and response[y] == {x: F(-1)}, 'Actual negative involution')
        if x < y:
            signed_swap(x, y, weight)
            small_swaps.append([x, y, str(weight)])
    need(len(small_swaps) == 32, 'All32 small swaps')
    result, bound = replay(events)
    need(result == response and reverse_columns(events) == response, 'Exact rows and independent columns of the symmetric response')
    identity = [{i: F(1)} for i in range(112)]
    need(replay(events+events)[0] == identity and reverse_columns(events+events) == identity, 'The literal gauge is its own inverse')
    invoice = {'pair_code': sum(map(cost, events[:code_end])),
               'mode_swaps': sum(map(cost, events[code_end:swap_end])),
               'pair_undo': sum(map(cost, events[swap_end:undo_end])),
               'small_swaps': sum(map(cost, events[undo_end:]))}
    need(invoice['pair_code']+invoice['pair_undo'] == 940 and invoice['mode_swaps'] == 624
         and invoice['small_swaps'] == 832 and sum(invoice.values()) == 2396, 'Complete common-FULL scalar invoice')
    need(replay(events[:swap_end]+events[undo_end:])[0] != response, 'Omitted pair undo is rejected')
    payload = {'schema': 'matched-common-full-gauge-v1', 'frame': 'FULL', 'live_fields': 112,
               'owned_fields': 0, 'private_fields': 0, 'native_children': 0,
               'events': events, 'mode_swaps': mode_swaps, 'small_swaps': small_swaps,
               'cuts': {'code_end': code_end, 'swap_end': swap_end, 'undo_end': undo_end},
               'response': native['response'], 'source_pins': {k: v[1] for k, v in PINS.items()}}
    (HERE/'FULL-GAUGE.json').write_text(json.dumps(payload, indent=2, sort_keys=True)+'\n')
    receipt = {'status': 'PASS_MATCHED_COMMON_FULL_GAUGE', 'source_pins': {k: v[1] for k, v in PINS.items()},
               'all_rows_and_columns': 112, 'literal_square_identity': True, 'real_scalar_invoice': invoice,
               'total_real_scalar_primitives': sum(invoice.values()), 'top_level_array_norm_bound': str(bound),
               'owned_fields': 0, 'private_fields': 0, 'native_children': 0,
               'payload_sha256': sha256((HERE/'FULL-GAUGE.json').read_bytes()).hexdigest(),
               'checker_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
               'scope': 'Common-FULL scalar implementation of actual E=E^-1. Access at other frames and full controller are separate.'}
    (HERE/'CHECKS.json').write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    print(receipt['status'])


if __name__ == '__main__':
    main()
