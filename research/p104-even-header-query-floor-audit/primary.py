#!/usr/bin/env python3
"""Direct two-sector even/odd transport and exact Gaussian row ranks."""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from math import gcd
from pathlib import Path
import re
import sys

HOME_DIR = Path(__file__).resolve().parent
PINS = {
    'CONTRACT.json': 'e953a170c71e0bd956b7dafa0d7447d5982d465d65a469869d3ba0bad006c10d',
    'CASES.json': '688c76fd3d68fcbfb9b96090080fc5fbd611e58587d9e890c27cb20ee0c6270f',
    'SOURCE-PINS.json': '56853ff086872d33612e4698540d14caa7ebd69e965432bd9ad89740b5d24557',
}
DIMENSION = 34
BODY_COUNT = 18
BYTE_LIMIT = 8 * 1024 * 1024
ZERO = (Fraction(0), Fraction(0))
ONE = (Fraction(1), Fraction(0))


def demand(ok, message):
    if not ok:
        raise ValueError(message)


class GateFailure(ValueError):
    pass


def gate(ok, message):
    if not ok:
        raise GateFailure(message)


def proof_int(value):
    demand(type(value) is int, 'proof integer excludes Boolean')
    return value


def object_pairs(items):
    output = {}
    for key, value in items:
        demand(key not in output, 'duplicate JSON key')
        output[key] = value
    return output


def no_real_token(_):
    raise ValueError('float/nonfinite JSON token')


def parse(raw):
    demand(len(raw) <= BYTE_LIMIT, 'JSON byte cap')
    return json.loads(raw, object_pairs_hook=object_pairs,
                      parse_float=no_real_token, parse_constant=no_real_token)


def packet_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True).encode('ascii') + b'\n'


def authenticate(base):
    metadata = {}
    for name, sha in PINS.items():
        raw = (base / name).read_bytes()
        demand(hashlib.sha256(raw).hexdigest() == sha, 'metadata hash: ' + name)
        metadata[name] = raw
    source_manifest = parse(metadata['SOURCE-PINS.json'])
    rows = source_manifest['sources']
    demand(type(rows) is list and len(rows) == 8, 'eight source objects')
    seen, source_raw = set(), {}
    for entry in rows:
        path = entry['local_path']
        demand(type(path) is str and path.startswith('inputs/') and
               len(Path(path).parts) == 2 and Path(path).name not in ('.', '..') and
               path not in seen, 'unique safe source path')
        seen.add(path)
        raw = (base / path).read_bytes()
        demand(len(raw) == proof_int(entry['bytes']), 'source size: ' + path)
        demand(hashlib.sha256(raw).hexdigest() == entry['sha256'], 'source SHA256: ' + path)
        header = b'blob ' + str(len(raw)).encode('ascii') + b'\0'
        demand(hashlib.sha1(header + raw).hexdigest() == entry['git_blob'], 'source Git blob: ' + path)
        source_raw[path] = raw
    # Only after all eight inert source objects are authenticated is controller
    # JSON parsed. No source program or another implementation is imported.
    return (parse(metadata['CONTRACT.json']), parse(metadata['CASES.json']),
            parse(source_raw['inputs/CONTROLLER.json']),
            {'CONTROLLER.json': hashlib.sha256(source_raw['inputs/CONTROLLER.json']).hexdigest()})


def add(z, w):
    return z[0] + w[0], z[1] + w[1]


def negate(z):
    return -z[0], -z[1]


def product(z, w):
    return z[0] * w[0] - z[1] * w[1], z[0] * w[1] + z[1] * w[0]


def quotient(z, w):
    norm = w[0] * w[0] + w[1] * w[1]
    demand(norm != 0, 'nonzero Gaussian divisor')
    return ((z[0] * w[0] + z[1] * w[1]) / norm,
            (z[1] * w[0] - z[0] * w[1]) / norm)


def real(value):
    return Fraction(value), Fraction(0)


def scalar(text, unit=False):
    demand(type(text) is str and re.fullmatch(r'[+-]?[0-9]+(?:/[0-9]+)?', text),
           'dyadic scalar string')
    value = Fraction(text)
    demand(value != 0 and value.denominator & (value.denominator - 1) == 0,
           'nonzero dyadic scalar')
    if unit:
        numerator = abs(value.numerator)
        demand(numerator & (numerator - 1) == 0, 'signed dyadic unit')
    return real(value)


def theta_power(theta, exponent):
    proof_int(exponent)
    # Integer parity also handles negative exponents without int**negative
    # producing any float. theta is either +1 or -1.
    return -1 if theta == -1 and exponent % 2 else 1


def null_matrix():
    return [[ZERO for _ in range(DIMENSION)] for _ in range(DIMENSION)]


def identity_matrix():
    result = null_matrix()
    for index in range(DIMENSION):
        result[index][index] = ONE
    return result


def row_rank(matrix):
    work = [row[:] for row in matrix]
    lead = 0
    for column in range(DIMENSION):
        pivot = next((row for row in range(lead, DIMENSION)
                      if work[row][column] != ZERO), None)
        if pivot is None:
            continue
        work[lead], work[pivot] = work[pivot], work[lead]
        divisor = work[lead][column]
        for j in range(column, DIMENSION):
            work[lead][j] = quotient(work[lead][j], divisor)
        for row in range(lead + 1, DIMENSION):
            multiplier = work[row][column]
            if multiplier != ZERO:
                for j in range(column, DIMENSION):
                    work[row][j] = add(work[row][j], negate(product(multiplier, work[lead][j])))
        lead += 1
        if lead == DIMENSION:
            break
    return lead


def fields(event):
    demand(type(event) is list and event and type(event[0]) is str, 'event list')
    slots = {'ADD': (1, 2), 'SCALE': (1,), 'SWAP': (1, 2), 'LAMBDA': (1,),
             'QUERY': (1, 2), 'LOCAL': (2, 3), 'IDLE': (1, 2),
             'IDLE_ONE': (1,), 'Q_POWER': (1,)}
    lengths = {'ADD': 4, 'SCALE': 3, 'SWAP': 3, 'LAMBDA': 3, 'QUERY': 4,
               'LOCAL': 4, 'IDLE': 4, 'IDLE_ONE': 3, 'Q_POWER': 3}
    name = event[0]
    demand(name in slots and len(event) == lengths[name], 'opcode/arity')
    selected = [proof_int(event[pos]) for pos in slots[name]]
    demand(all(0 <= index < DIMENSION for index in selected) and
           len(selected) == len(set(selected)), 'distinct in-range roles')
    if name == 'LOCAL':
        demand(1 <= proof_int(event[1]) <= BODY_COUNT, 'LOCAL stage')
    if name in ('IDLE', 'IDLE_ONE'):
        stages = event[-1]
        demand(type(stages) is list and all(1 <= proof_int(x) <= BODY_COUNT for x in stages),
               'idle stages')
    return name, selected


def row_add(matrix, destination, source, coefficient):
    matrix[destination] = [add(x, product(coefficient, y))
                           for x, y in zip(matrix[destination], matrix[source])]


def row_scale(matrix, index, coefficient):
    matrix[index] = [product(coefficient, item) for item in matrix[index]]


def dispatch(a, b, event, theta):
    opcode, selected = fields(event)
    if opcode == 'ADD':
        coefficient = scalar(event[3])
        row_add(a, selected[0], selected[1], coefficient)
        row_add(b, selected[0], selected[1], coefficient)
    elif opcode == 'SCALE':
        coefficient = scalar(event[2], unit=True)
        row_scale(a, selected[0], coefficient)
        row_scale(b, selected[0], coefficient)
    elif opcode == 'SWAP':
        x, y = selected
        a[x], a[y] = a[y], a[x]
        b[x], b[y] = b[y], b[x]
    elif opcode == 'LAMBDA':
        sign = proof_int(event[2])
        demand(sign in (-1, 1), 'lambda sign')
        coefficient = Fraction(1 + theta, 2), Fraction(sign * (1 - theta), 2)
        row_scale(a, selected[0], coefficient)
        row_scale(b, selected[0], coefficient)
    elif opcode == 'Q_POWER':
        exponent = proof_int(event[2])
        gate(exponent % 2 == 0, 'odd_free_control')
        coefficient = real(theta_power(theta, exponent // 2))
        row_scale(a, selected[0], coefficient)
        row_scale(b, selected[0], coefficient)
    elif opcode in ('IDLE', 'IDLE_ONE'):
        pass  # Every authenticated body symbol is specialized to one.
    else:
        if opcode == 'QUERY':
            destination, source = selected
            exponent, stage = proof_int(event[3]), None
            demand(exponent % 2 == 1, 'QUERY must be odd')
        else:
            source, destination = selected
            exponent, stage = -1, proof_int(event[1])
        coefficient = theta_power(theta, exponent // 2)
        old_a, old_b = a[source][:], b[source][:]
        a[destination] = [add(x, product(real(theta * coefficient), y))
                          for x, y in zip(a[destination], old_b)]
        b[destination] = [add(x, product(real(coefficient), y))
                          for x, y in zip(b[destination], old_a)]
        return {'opcode': opcode, 'source': source, 'destination': destination,
                'stage': stage, 'exponent': exponent}
    return None


def transport(events, theta, tracking):
    demand(type(events) is list and 0 < len(events) <= 607, 'event count cap')
    demand(type(theta) is int and theta in (1, -1), 'sector')
    a, b, trace = identity_matrix(), null_matrix(), []
    for index, event in enumerate(events):
        opcode, _ = fields(event)
        is_query = opcode in ('QUERY', 'LOCAL')
        if tracking and is_query:
            before = row_rank(a)
            if not trace:
                demand(all(cell == ZERO for row in b for cell in row), 'first-query odd part zero')
        info = dispatch(a, b, event, theta)
        if tracking and info is not None:
            after = row_rank(a)
            demand(after >= before - 1, 'query rank drop exceeds one')
            if not trace:
                demand(before == DIMENSION and after == DIMENSION, 'first-query overhead')
            trace.append({'event_index': index, 'ordinal': len(trace) + 1,
                          **info, 'rank_before': before, 'rank_after': after})
    return a, b, trace


def target(diagonal, theta):
    demand(type(diagonal) is list and len(diagonal) == DIMENSION, 'target size')
    a, b = null_matrix(), null_matrix()
    for index, key in enumerate(diagonal):
        demand(type(key) is list and len(key) == 20, 'target exponent vector')
        for value in key:
            proof_int(value)
        demand(key[1] == 0 and all(value >= 0 for value in key[2:]), 'target dummy/body exponents')
        exponent = key[0]
        if exponent % 2:
            b[index][index] = real(theta_power(theta, exponent // 2))
        else:
            a[index][index] = real(theta_power(theta, exponent // 2))
    return a, b


def endpoint(a, b, diagonal, theta):
    expected_a, expected_b = target(diagonal, theta)
    gate(a == expected_a and b == expected_b, 'endpoint_mismatch')


def word_inventory(controller, contract):
    demand(proof_int(controller['roles']) == DIMENSION and
           proof_int(controller['stages']) == BODY_COUNT, 'controller dimensions')
    events = controller['events']
    counts = Counter()
    for event in events:
        name, _ = fields(event)
        counts[name] += 1
    diagonal = controller['diagonal']
    target(diagonal, 1)
    odd = sum(key[0] % 2 for key in diagonal)
    value = {'roles': controller['roles'], 'events': len(events), 'stages': controller['stages'],
             'native_queries': counts['LOCAL'], 'thin_queries': counts['QUERY'],
             'total_queries': counts['LOCAL'] + counts['QUERY'], 'odd_targets': odd,
             'even_targets': DIMENSION - odd, 'opcode_counts': dict(sorted(counts.items()))}
    demand(packet_bytes(value) == packet_bytes(contract['expect']), 'healthy word inventory')
    return value


def modified(controller, case):
    events = [list(event) for event in controller['events']]
    diagonal = [key[:] for key in controller['diagonal']]
    if 'delete_event' in case:
        del events[proof_int(case['delete_event'])]
    elif 'replace_event' in case:
        events[proof_int(case['replace_event'])] = list(case['value'])
    elif 'insert_event' in case:
        events.insert(proof_int(case['insert_event']), list(case['value']))
    elif 'target_field' in case:
        diagonal[proof_int(case['target_field'])][0] = proof_int(case['target_q_exponent'])
    else:
        raise ValueError('unknown control mutation')
    return events, diagonal


def controls(controller, cases):
    demand(type(cases['controls']) is list and len(cases['controls']) == 4, 'four controls')
    rows = []
    for case in cases['controls']:
        events, diagonal = modified(controller, case)
        try:
            for theta in (1, -1):
                a, b, _ = transport(events, theta, False)
                endpoint(a, b, diagonal, theta)
        except GateFailure as error:
            demand(str(error) == case['failure_gate'], 'unexpected control gate')
            rows.append({'id': case['id'], 'accepted': False, 'failure_gate': str(error)})
        else:
            raise ValueError('control accepted: ' + case['id'])
    return rows


def encode(matrix):
    return [[[z[0].numerator, z[0].denominator, z[1].numerator, z[1].denominator]
             for z in row] for row in matrix]


def calculate(contract, cases, controller, source_hashes):
    word = word_inventory(controller, contract)
    sectors = []
    for theta in (1, -1):
        initial = row_rank(identity_matrix())
        a, b, trace = transport(controller['events'], theta, True)
        endpoint(a, b, controller['diagonal'], theta)
        final = row_rank(a)
        demand(initial == 34 and final == 2 and len(trace) == 33, 'actual ranks/query trace')
        minimum = word['odd_targets'] + 1
        demand(minimum == 33 and word['total_queries'] == minimum, 'header count/floor')
        sectors.append({'theta': theta, 'initial_even_rank': initial, 'final_even_rank': final,
                        'minimum_queries': minimum, 'even_final': encode(a), 'odd_final': encode(b),
                        'query_trace': trace})
    return {'schema': contract['certificate']['schema'], 'sources': source_hashes,
            'word': word, 'sectors': sectors, 'controls': controls(controller, cases)}


def validate(value, contract, cases):
    demand(type(value) is dict and set(value) == set(contract['certificate']['keys']), 'certificate keys')
    demand(value['schema'] == contract['certificate']['schema'], 'certificate schema')
    demand(type(value['sources']) is dict and set(value['sources']) == {'CONTROLLER.json'} and
           type(value['sources']['CONTROLLER.json']) is str, 'source hash field')
    word = value['word']
    demand(type(word) is dict and set(word) == set(contract['expect']), 'word keys')
    for key, item in word.items():
        if key == 'opcode_counts':
            demand(type(item) is dict and all(type(name) is str and type(count) is int
                                            for name, count in item.items()), 'opcode counts')
        else:
            proof_int(item)
    demand(type(value['sectors']) is list and len(value['sectors']) == 2, 'two sectors')
    for sector, theta in zip(value['sectors'], (1, -1)):
        demand(type(sector) is dict and set(sector) == set(contract['sector_fields']), 'sector keys')
        demand(proof_int(sector['theta']) == theta, 'sector order')
        for name in ('initial_even_rank', 'final_even_rank', 'minimum_queries'):
            proof_int(sector[name])
        for name in ('even_final', 'odd_final'):
            matrix = sector[name]
            demand(type(matrix) is list and len(matrix) == DIMENSION, 'matrix rows')
            for row in matrix:
                demand(type(row) is list and len(row) == DIMENSION, 'matrix columns')
                for entry in row:
                    demand(type(entry) is list and len(entry) == 4, 'Gaussian quartet')
                    for item in entry:
                        proof_int(item)
                    for num, den in ((entry[0], entry[1]), (entry[2], entry[3])):
                        demand(den > 0 and gcd(num, den) == 1, 'reduced Gaussian rational')
        trace = sector['query_trace']
        demand(type(trace) is list and len(trace) == 33, 'complete query trace')
        for record in trace:
            demand(type(record) is dict and set(record) == set(contract['trace_fields']), 'trace fields')
            demand(record['opcode'] in ('LOCAL', 'QUERY'), 'trace opcode')
            for name in ('event_index', 'ordinal', 'source', 'destination', 'exponent',
                         'rank_before', 'rank_after'):
                proof_int(record[name])
            if record['opcode'] == 'QUERY':
                demand(record['stage'] is None, 'QUERY stage null')
            else:
                proof_int(record['stage'])
    demand(type(value['controls']) is list and len(value['controls']) == 4, 'ordered controls')
    for record, case in zip(value['controls'], cases['controls']):
        demand(type(record) is dict and set(record) == {'id', 'accepted', 'failure_gate'} and
               record['id'] == case['id'] and type(record['accepted']) is bool and
               record['accepted'] is False and record['failure_gate'] == case['failure_gate'], 'control record')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', type=Path, default=HOME_DIR)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument('--certificate-out', type=Path)
    selection.add_argument('--check', type=Path)
    args = parser.parse_args()
    contract, cases, controller, source_hashes = authenticate(args.inputs)
    result = calculate(contract, cases, controller, source_hashes)
    validate(result, contract, cases)
    raw = packet_bytes(result)
    demand(len(raw) <= BYTE_LIMIT, 'certificate byte cap')
    if args.certificate_out:
        args.certificate_out.write_bytes(raw)
    else:
        actual = (args.check or HOME_DIR / 'CERTIFICATE.json').read_bytes()
        validate(parse(actual), contract, cases)
        demand(actual == raw, 'whole certificate bytes differ')
    print('PASS_HEADER_DIRECT_AB sectors2 matrices4 queries33 controls4 known_floor33_no_admission')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, IndexError, ZeroDivisionError) as error:
        print('FAIL_HEADER_DIRECT_AB: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
