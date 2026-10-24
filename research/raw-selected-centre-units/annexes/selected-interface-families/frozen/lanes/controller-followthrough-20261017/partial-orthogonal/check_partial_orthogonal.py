#!/usr/bin/env python3
"""Check the partial orthogonal response and its native words."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
import ast
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[1] / 'oblique-native-20261017' / 'interior-cut'
PINS = {
    'UNIT-MODE-CANDIDATE.json': 'd61d7447a499973afe49b7e422c51070262fc83229a82b7ff0ebb0238605d2fd',
    'RESPONSE-SPACE.json': '320e25fec5c0f52285aa2e945b2e0f30d43e2504de207595b0f35ec93bab7337',
}
PRIME = 1000003


def need(test, label):
    if not test:
        raise ValueError(label)


def read(name):
    raw = (SOURCE / name).read_bytes()
    need(sha256(raw).hexdigest() == PINS[name], ('Source pin', name))
    return json.loads(raw)


def lift(value):
    for denominator in (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024):
        numerator = int(value) * denominator % PRIME
        if numerator > PRIME // 2:
            numerator -= PRIME
        if abs(numerator) <= 64:
            return F(numerator, denominator)
    raise ValueError(('No small dyadic lift', value))


def add(target, source, coefficient=F(1)):
    for key, value in source.items():
        total = target.get(key, F(0)) + coefficient * value
        if total:
            target[key] = total
        else:
            target.pop(key, None)


def product(left, right):
    result = []
    for row in left:
        output = {}
        for index, value in row.items():
            add(output, right[index], value)
        result.append(output)
    return result


def transpose(matrix):
    result = [{} for _ in matrix]
    for i, row in enumerate(matrix):
        for j, value in row.items():
            result[j][i] = value
    return result


def encode(matrix):
    return [{str(key): str(value) for key, value in row.items()} for row in matrix]


def determinant(matrix):
    rows = [dict(row) for row in matrix]
    result = F(1)
    for column in range(len(rows)):
        candidates = [i for i in range(column, len(rows)) if rows[i].get(column)]
        if not candidates:
            return F(0)
        pivot = min(candidates, key=lambda i: len(rows[i]))
        if pivot != column:
            rows[column], rows[pivot] = rows[pivot], rows[column]
            result = -result
        value = rows[column][column]
        result *= value
        for i in range(column + 1, len(rows)):
            if rows[i].get(column):
                add(rows[i], rows[column], -rows[i][column] / value)
    return result


def main():
    candidate, space = read('UNIT-MODE-CANDIDATE.json'), read('RESPONSE-SPACE.json')
    selected = candidate['selected_modes']
    doubled = [mode for mode in selected if mode < 64 and mode % 4 in (2, 3)]
    need(len(doubled) == 32, 'Exactly 32 changed mode weights')
    original = [{int(k): F(v) for k, v in row.items()} for row in candidate['J']]
    left = [{int(k): F(v) for k, v in row.items()} for row in candidate['L']]
    right = [{int(k): F(v) for k, v in row.items()} for row in candidate['R']]
    need(product(left, right) == original, 'Original exact factorization')
    need(determinant(left) == -1 and determinant(right) == 2**56,
         'Exact original dyadic determinants')
    for row in left:
        for column in row:
            if selected[column] in doubled:
                row[column] *= 2
    response = product(left, right)
    need(determinant(left) * determinant(right) == -2**88,
         'Exact changed dyadic determinant')
    independent = [{} for _ in range(112)]
    weights = {}
    for mode in selected:
        coefficient = 2 if mode in doubled else 1
        direction = space['directions'][mode]
        for pair, value in direction['effect'].items():
            i, j = ast.literal_eval(pair)
            add(independent[i], {j: lift(value)}, coefficient)
        for position, value in direction['events'].items():
            position = int(position)
            weights[position] = weights.get(position, F(0)) + coefficient * lift(value)
    weights = {key: value for key, value in weights.items() if value}
    need(response == independent, 'Independent response direction sum')
    changed = [i for i in range(112) if response[i] != original[i]]
    remaining = sorted(set(range(112)) - set(changed))
    need(len(changed) == 64 and len(remaining) == 48, 'Exact port split')
    need(all(set(response[i]) <= set(changed) for i in changed), 'Closed 64-port response')
    need(all(set(response[i]) <= set(remaining) for i in remaining), 'Closed 48-port response')
    squared = product(response, response)
    gram = product(response, transpose(response))
    need(all(squared[i] == gram[i] == {i: F(4)} for i in changed), '64-port inverse and Gram')
    need(all(response[i] == transpose(response)[i] for i in changed), '64-port symmetry')
    need(all(response[i] == original[i] for i in remaining), '48-port response unchanged')
    need(all(not response[i].get(i) for i in range(112)), 'Zero diagonal')

    spec = importlib.util.spec_from_file_location('partial_probe', SOURCE / 'probe_readiness.py')
    probe = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(probe)
    payload = {'schema': 'native-partial-orthogonal-response-v1', 'source_pins': PINS,
               'source_core_sha256': probe.PIN, 'response': encode(response),
               'doubled_modes': sorted(doubled), 'orthogonal_ports': changed,
               'remaining_ports': remaining, 'providers': {}}
    receipt = {'status': 'PASS_NATIVE_PARTIAL_ORTHOGONAL_RESPONSE', 'source_pins': PINS,
               'source_core_sha256': probe.PIN, 'orthogonal_ports': changed,
               'remaining_ports': remaining, 'doubled_modes': sorted(doubled),
               'orthogonal_gram_factor': 4, 'determinant': str(-2**88), 'providers': {}}
    for provider, item in probe.core['providers'].items():
        word = item['canonical']
        n = len(word['start'])
        identity = {i: {(i, ()): F(1)} for i in range(n + 8)}
        split = item['programs']['forward'].index(['phase', 'zero_frame_precondition'])
        programs, reports = {}, {}
        for direction in ('forward', 'backward'):
            backward = direction == 'backward'
            program = [['phase', 'partial_orthogonal_response']] + [
                ['scalar', ['clear', ['C', i]], 0] for i in range(8)]
            for position in range(split, len(item['programs'][direction])):
                forward = item['programs']['forward'][position]
                event = deepcopy(item['programs'][direction][position])
                if forward[0] == 'scalar' and forward[1][0] == 'add':
                    target, source = forward[1][1:3]
                    is_y = lambda slot: slot[0] == 'L' and 112 <= slot[1] < 224
                    if is_y(target) and not is_y(source):
                        coefficient = weights.get(position, F(0))
                        if not coefficient:
                            continue
                        if backward:
                            need(event[1][1:3] == [source, target], 'Native transpose site')
                            coefficient = -coefficient
                        event[1][3:5] = [coefficient.numerator, coefficient.denominator]
                program.append(event)
            actual = probe.e.core_replay(program, identity, word, backward)[0]
            expected = deepcopy(identity)
            for i in range(n, n + 8):
                expected[i] = {}
            for i, row in enumerate(response):
                for j, coefficient in row.items():
                    if backward:
                        add(expected[j], identity[112 + i], -coefficient)
                    else:
                        add(expected[112 + i], identity[j], coefficient)
            need(all(actual[i] == expected[i] for i in range(n + 8)),
                 ('All columns, helpers, and owned zeros', provider, direction))
            native = lambda event: event[0] in ('climb', 'warp', 'adapter', 'residual_adapter')
            need([event for event in program if native(event)] ==
                 [event for event in item['programs'][direction] if native(event)],
                 'Native records unchanged')
            profile = Counter(event[5] for event in program if event[0] == 'climb')
            reports[direction] = {'all_input_columns': n + 8,
                                  'borrowed_helpers_restored': n - 224,
                                  'private_zero_buffers_restored': len(word['zero_buffers']),
                                  'owned_outputs_zero': 8,
                                  'scalar_real_primitives': probe.e.core_price(program),
                                  'native_profile': dict(sorted(profile.items())),
                                  'native_rank_mass': sum(k*v for k, v in profile.items()),
                                  'native_children': sum(profile.values()),
                                  'native_records_identical': True}
            programs[direction] = program
        payload['providers'][provider] = {'canonical': word, 'programs': programs}
        receipt['providers'][provider] = reports
        print(provider, reports, flush=True)
    raw = (json.dumps(payload, sort_keys=True, separators=(',', ':')) + '\n').encode()
    (HERE / 'PARTIAL-ORTHOGONAL-PROGRAM.json.gz').write_bytes(gzip.compress(raw, mtime=0))
    receipt['payload_decompressed_sha256'] = sha256(raw).hexdigest()
    receipt['checker_sha256'] = sha256(Path(__file__).read_bytes()).hexdigest()
    receipt['scope'] = ('The local response is a dyadic unit. Its 64-port restriction is symmetric '
                        'and has square 4I. Its 48-port restriction is unchanged. A whole-supplier '
                        'decoder and recursive cost are not established.')
    (HERE / 'PARTIAL-ORTHOGONAL.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(receipt['status'], receipt['payload_decompressed_sha256'], flush=True)


if __name__ == '__main__':
    main()
