#!/usr/bin/env python3
"""Check serial centre gauges in a common physical frame."""
from copy import deepcopy
from fractions import Fraction as F
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import check_structured_centres as source

HERE = Path(__file__).resolve().parent
PIN = '2b9de1454c2025ae4e230bd64de36b4f6c937628c63fc5afede6640dd3c0e1e1'
p = source.p


def scalar(kind, target, value, coefficient=None):
    gate = [kind, ['C', 0] if target == 112 else ['L', target]]
    if kind == 'scale':
        gate += [value.numerator, value.denominator]
    else:
        gate.append(['C', 0] if value == 112 else ['L', value])
        if kind == 'add':
            gate += [coefficient.numerator, coefficient.denominator]
    return ['scalar', gate, 0]


def centre_step(row, scatter, query_factor):
    ports = sorted(row)
    word = [scalar('copy', 112, ports[0])]
    if row[ports[0]] != 1:
        word.append(scalar('scale', 112, row[ports[0]]))
    word += [scalar('add', 112, i, row[i]) for i in ports[1:]]
    word += [scalar('add', i, 112, coefficient) for i, coefficient in sorted(scatter.items())]
    if query_factor != 1:
        word.append(scalar('scale', 112, query_factor))
    word += [scalar('add', 112, i, -row[i]) for i in ports]
    return word


def replay(word):
    state = [{i: F(1)} for i in range(112)] + [{}]
    def slot(value):
        return 112 if value[0] == 'C' else value[1]
    for event in word:
        p.need(event[0] == 'scalar' and event[2] == 0, 'One common frame')
        gate = event[1]
        target = slot(gate[1])
        if gate[0] == 'copy':
            p.need(target == 112 and not state[target], 'Only copy into the zero owned field')
            state[target] = dict(state[slot(gate[2])])
        elif gate[0] == 'add':
            p.need(target != slot(gate[2]), 'Distinct ADD operands')
            p.add(state[target], state[slot(gate[2])], F(*gate[3:5]))
        else:
            p.need(gate[0] == 'scale', 'Allowed scalar operation')
            coefficient = F(*gate[2:4])
            state[target] = {i: coefficient * value for i, value in state[target].items()}
    p.need(not state[112], 'Owned C0 returns to zero')
    return state[:112]


def main():
    raw = gzip.decompress((HERE / 'STRUCTURED-CENTRES-PROGRAM.json.gz').read_bytes())
    p.need(sha256(raw).hexdigest() == PIN, 'Pinned native centre packet')
    packet = json.loads(raw)
    receipt = json.loads((HERE / 'STRUCTURED-CENTRES.json').read_text())
    rows = [{int(i): F(value) for i, value in row.items()} for row in packet['centre_rows']]
    selected = receipt['gauge_identities']['3']['selected_ports']
    ordinary = receipt['gauge_identities']['3']['ordinary_ports']
    signs = {i: F(-1) if i in selected else F(1) for i in range(112)}
    negative = [scalar('scale', i, F(-1)) for i in selected]
    words = {}
    for inverse in (False, True):
        word = deepcopy(negative) if inverse else []
        for row in rows:
            scatter = {i: (1 if inverse else -1) * signs[i] * value / 4 for i, value in row.items()}
            word += centre_step(row, scatter, F(1))
        if not inverse:
            word += negative
        words['data_inverse' if inverse else 'data'] = word
    for name, coefficient, factor in [('ordinary', F(-1, 2), F(-2)),
                                      ('ordinary_inverse', F(-1, 4), F(-1, 2))]:
        word = []
        for row in rows:
            row = {i: value for i, value in row.items() if i in ordinary}
            word += centre_step(row, {i: coefficient * value for i, value in row.items()}, factor)
        words[name] = word
    maps = {name: replay(word) for name, word in words.items()}
    identity = [{i: F(1)} for i in range(112)]
    for name in ('data', 'ordinary'):
        p.need(p.product(maps[name], maps[name + '_inverse']) ==
               p.product(maps[name + '_inverse'], maps[name]) == identity, 'Both inverse orders')
    outer = [{} for _ in range(112)]
    for row in rows:
        for i, value in row.items():
            p.add(outer[i], row, value)
    expected = [{i: signs[i]} for i in range(112)]
    for i in range(112):
        p.add(expected[i], outer[i], F(-1, 4))
    p.need(maps['data'] == expected, 'Data gauge equals E minus KtK/4')
    expected = deepcopy(identity)
    for i in ordinary:
        p.add(expected[i], {j: value for j, value in outer[i].items() if j in ordinary}, F(-1, 2))
    p.need(maps['ordinary'] == expected, 'Ordinary gauge equals I minus KuT Ku/2')
    spec = importlib.util.spec_from_file_location('gauge_probe', p.SOURCE / 'probe_readiness.py')
    probe = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(probe)
    reports = {name: {'scalar_real_primitives': probe.e.core_price(word), 'native_children': 0,
                      'owned_fields': 1, 'owned_field_restored': True, 'all_input_columns': 112}
               for name, word in words.items()}
    result = {'status': 'PASS_SERIAL_RANK8_GAUGES', 'source_payload_sha256': PIN,
              'selected_ports': selected, 'ordinary_ports': ordinary, 'reports': reports,
              'programs': words, 'checker_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
              'scope': 'Exact scalar gauges on the 48-port block in a common physical frame. The other 64 ports are unchanged. No mixed-frame or whole-supplier access is asserted.'}
    (HERE / 'RANK8-GAUGES.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(result['status'], reports, flush=True)


if __name__ == '__main__':
    main()
