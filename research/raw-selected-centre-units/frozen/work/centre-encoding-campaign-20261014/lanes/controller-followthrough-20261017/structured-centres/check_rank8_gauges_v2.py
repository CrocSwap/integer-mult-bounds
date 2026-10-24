#!/usr/bin/env python3
"""Check scalar gauges with the dyadic scale on the owned query field."""
from copy import deepcopy
from fractions import Fraction as F
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import check_rank8_gauges as old

HERE = Path(__file__).resolve().parent
OLD_PIN = '27eb7e2d72fd5c06bb330f1ec6104cd85ae938a55d36aaf8e2e5e94e17c00930'


def step(row, scatter_signs, initial_scale, query_factor):
    ports = sorted(row)
    word = [old.scalar('copy', 112, ports[0])]
    if row[ports[0]] != 1:
        word.append(old.scalar('scale', 112, row[ports[0]]))
    word += [old.scalar('add', 112, i, row[i]) for i in ports[1:]]
    word.append(old.scalar('scale', 112, initial_scale))
    word += [old.scalar('add', i, 112, value) for i, value in sorted(scatter_signs.items())]
    word.append(old.scalar('scale', 112, query_factor / initial_scale))
    word += [old.scalar('add', 112, i, -row[i]) for i in ports]
    return word


def main():
    raw = (HERE / 'RANK8-GAUGES.json').read_bytes()
    old.p.need(sha256(raw).hexdigest() == OLD_PIN, 'Pinned preceding scalar programs')
    original = json.loads(raw)
    raw = gzip.decompress((HERE / 'STRUCTURED-CENTRES-PROGRAM.json.gz').read_bytes())
    old.p.need(sha256(raw).hexdigest() == old.PIN, 'Pinned native centre rows')
    packet = json.loads(raw)
    rows = [{int(i): F(value) for i, value in row.items()} for row in packet['centre_rows']]
    selected, ordinary = original['selected_ports'], original['ordinary_ports']
    signs = {i: F(-1) if i in selected else F(1) for i in range(112)}
    negations = [old.scalar('scale', i, F(-1)) for i in selected]
    programs = {}
    for inverse in (False, True):
        word = deepcopy(negations) if inverse else []
        for row in rows:
            scatter = {i: (1 if inverse else -1) * signs[i] * value for i, value in row.items()}
            word += step(row, scatter, F(1, 4), F(1))
        if not inverse:
            word += negations
        programs['data_inverse' if inverse else 'data'] = word
    for name, coefficient, factor in [('ordinary', F(1, 2), F(-2)),
                                      ('ordinary_inverse', F(1, 4), F(-1, 2))]:
        word = []
        for row in rows:
            row = {i: value for i, value in row.items() if i in ordinary}
            word += step(row, {i: -value for i, value in row.items()}, coefficient, factor)
        programs[name] = word
    maps = {name: old.replay(word) for name, word in programs.items()}
    for name, actual in maps.items():
        old.p.need(actual == old.replay(original['programs'][name]), ('Same exact map', name))
    identity = [{i: F(1)} for i in range(112)]
    for name in ('data', 'ordinary'):
        old.p.need(old.p.product(maps[name], maps[name + '_inverse']) ==
                   old.p.product(maps[name + '_inverse'], maps[name]) == identity,
                   'Both inverse orders')
    spec = importlib.util.spec_from_file_location('scaled_query_probe', old.p.SOURCE / 'probe_readiness.py')
    probe = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(probe)
    reports = {name: {'scalar_real_primitives': probe.e.core_price(word),
                      'old_scalar_real_primitives': original['reports'][name]['scalar_real_primitives'],
                      'native_children': 0, 'owned_fields': 1, 'owned_field_restored': True,
                      'all_input_columns': 112, 'clears_of_nonzero_owned_data': 0}
               for name, word in programs.items()}
    receipt = {'status': 'PASS_SCALED_QUERY_RANK8_GAUGES', 'source_receipt_sha256': OLD_PIN,
               'source_payload_sha256': old.PIN, 'programs': programs, 'reports': reports,
               'checker_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
               'scope': 'Same common-frame scalar maps as the preceding gauge packet. All query values are coherently removed; no data-dependent CLEAR is used.'}
    (HERE / 'RANK8-GAUGES-V2.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(receipt['status'], reports, flush=True)


if __name__ == '__main__':
    main()
