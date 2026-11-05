#!/usr/bin/env python3
"""Independent sparse forward transport for the literal cut401 contract."""
import argparse
from fractions import Fraction
from hashlib import sha256, sha1
import json
from math import gcd
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
META = {
    'CONTRACT.json': 'b0288cba97a7171a41817d32c255c971201b0ef2b32bbfea6c161bed917a216f',
    'CASES.json': '74f116e973e2fb1cd5653926bd001dc18ddbca3f52f08b14f2d8e3bf3fd0bc34',
    'SOURCE-PINS.json': '1fcb4715775c545350fe2a179e73d11ea02266a3d27ae53d9dd18492d203b5e5',
}
STAGES = 18
ZERO_KEY = (0,) * 20
GZERO = (Fraction(0), Fraction(0))
GONE = (Fraction(1), Fraction(0))
MAX_TERMS = 100000
JSON_LIMIT = 4 * 1024 * 1024
SOURCE_NAMES = {'CONTROLLER.json', 'CONTROLLER-ONE-RETIRED.json',
                'CONTROLLER-UNRETIRED.json', 'RETIREMENT-WITNESSES.json'}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value):
    need(type(value) is int, 'integer excludes Boolean')
    return value


def unique_pairs(pairs):
    obj = {}
    for key, value in pairs:
        need(key not in obj, 'duplicate JSON key')
        obj[key] = value
    return obj


def forbidden_number(_):
    raise ValueError('float/nonfinite JSON token')


def decode(data):
    need(len(data) <= JSON_LIMIT, 'JSON size limit')
    return json.loads(data, object_pairs_hook=unique_pairs,
                      parse_float=forbidden_number, parse_constant=forbidden_number)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True).encode('ascii') + b'\n'


def authenticate(inputs_dir):
    raw_meta = {}
    for name, expected in META.items():
        raw = (HERE / name).read_bytes()
        need(sha256(raw).hexdigest() == expected, 'metadata hash drift: ' + name)
        raw_meta[name] = raw
    contract = decode(raw_meta['CONTRACT.json'])
    cases = decode(raw_meta['CASES.json'])
    pins = decode(raw_meta['SOURCE-PINS.json'])
    need(type(pins) is dict and pins['source_head'] ==
         '435bbe91fb28cb1d7a569ca70c6c4e9eb302d486', 'exact source head')
    need(type(pins['sources']) is list and len(pins['sources']) == 12, 'twelve source pins')
    raw_sources = {}
    for row in pins['sources']:
        name = row['local_path']
        need(type(name) is str and name.startswith('inputs/') and
             name[len('inputs/'):] not in ('', '.', '..') and
             '/' not in name[len('inputs/'):] and name not in raw_sources, 'unique safe source path')
        raw = (inputs_dir / name[len('inputs/'):]).read_bytes()
        need(type(row['bytes']) is int and len(raw) == row['bytes'], 'source byte length: ' + name)
        need(sha256(raw).hexdigest() == row['sha256'], 'source SHA256: ' + name)
        header = b'blob ' + str(len(raw)).encode('ascii') + b'\0'
        need(sha1(header + raw).hexdigest() == row['git_blob'], 'source Git blob: ' + name)
        raw_sources[name] = raw
    # All twelve objects, including inert code text, were authenticated as bytes
    # before any literal controller or witness object is parsed. Never execute it.
    data = {name: decode(raw_sources['inputs/' + name]) for name in SOURCE_NAMES}
    sources = {name: sha256(raw_sources['inputs/' + name]).hexdigest()
               for name in sorted(SOURCE_NAMES)}
    return contract, cases, data, sources


def real_scalar(text):
    need(type(text) is str and len(text) <= 128, 'rational scalar string')
    try:
        value = Fraction(text)
    except (ValueError, ZeroDivisionError):
        raise ValueError('invalid rational scalar') from None
    need(value != 0 and value.denominator & (value.denominator - 1) == 0, 'nonzero dyadic scalar')
    return value


def mono(q=0, stages=(), coefficient=GONE):
    key = [0] * 20
    key[0] = q % 4
    for stage in stages:
        need(type(stage) is int and 1 <= stage <= STAGES, 'stage index')
        key[stage + 1] += 1
    return {tuple(key): coefficient} if coefficient != GZERO else {}


def add_key(a, b):
    return ((a[0] + b[0]) % 4, 0) + tuple(a[k] + b[k] for k in range(2, 20))


def gmul(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def plus(left, right, factor=None):
    factor = mono() if factor is None else factor
    out = dict(left)
    for key, value in right.items():
        for fkey, fvalue in factor.items():
            target = add_key(key, fkey)
            part = gmul(value, fvalue)
            previous = out.get(target, GZERO)
            total = previous[0] + part[0], previous[1] + part[1]
            if total == GZERO:
                out.pop(target, None)
            else:
                out[target] = total
    need(len(out) <= MAX_TERMS, 'polynomial term limit')
    return out


def times(poly, factor):
    return plus({}, poly, factor)


def lambda_poly(sign):
    need(type(sign) is int and sign in (-1, 1), 'lambda sign')
    return plus(mono(coefficient=(Fraction(1, 2), Fraction(sign, 2))),
                mono(q=2, coefficient=(Fraction(1, 2), Fraction(-sign, 2))))


def identity(roles):
    return [{row: mono()} for row in range(roles)]


def role(value, roles):
    need(type(value) is int and 0 <= value < roles, 'role index')
    return value


def instruction(event, roles):
    need(type(event) is list and event and type(event[0]) is str, 'instruction list')
    op = event[0]
    sizes = {'ADD': 4, 'SCALE': 3, 'SWAP': 3, 'QUERY': 4, 'LOCAL': 4,
             'Q_POWER': 3, 'IDLE': 4, 'IDLE_ONE': 3, 'LAMBDA': 3}
    need(op in sizes and len(event) == sizes[op], 'opcode/arity')
    if op == 'LOCAL':
        need(type(event[1]) is int and 1 <= event[1] <= STAGES, 'local stage')
        fields = [role(event[2], roles), role(event[3], roles)]
    elif op in ('ADD', 'SWAP', 'QUERY', 'IDLE'):
        fields = [role(event[1], roles), role(event[2], roles)]
    else:
        fields = [role(event[1], roles)]
    need(len(fields) == len(set(fields)), 'distinct instruction roles')
    if op in ('ADD', 'SCALE'):
        real_scalar(event[-1])
    if op in ('QUERY', 'Q_POWER'):
        integer(event[-1])
    if op == 'LAMBDA':
        need(type(event[2]) is int and event[2] in (-1, 1), 'lambda sign')
    if op in ('IDLE', 'IDLE_ONE'):
        need(type(event[-1]) is list, 'idle stage list')
        for stage in event[-1]:
            need(type(stage) is int and 1 <= stage <= STAGES, 'idle stage')
    return op, fields


def axpy(matrix, dst, src, factor):
    out = dict(matrix[dst])
    for col, poly in matrix[src].items():
        value = plus(out.get(col, {}), poly, factor)
        if value:
            out[col] = value
        else:
            out.pop(col, None)
    matrix[dst] = out


def scale_row(matrix, field, factor):
    matrix[field] = {col: value for col, poly in matrix[field].items()
                     if (value := times(poly, factor))}


def replay(events, roles, snapshots=()):
    need(type(events) is list and len(events) <= 607, 'event limit')
    matrix = identity(roles)
    saved = {}
    for count, event in enumerate(events, 1):
        op, fields = instruction(event, roles)
        if op == 'ADD':
            axpy(matrix, fields[0], fields[1], mono(coefficient=(real_scalar(event[3]), Fraction(0))))
        elif op == 'SCALE':
            scale_row(matrix, fields[0], mono(coefficient=(real_scalar(event[2]), Fraction(0))))
        elif op == 'SWAP':
            matrix[fields[0]], matrix[fields[1]] = matrix[fields[1]], matrix[fields[0]]
        elif op == 'QUERY':
            axpy(matrix, fields[0], fields[1], mono(q=event[3]))
        elif op == 'LOCAL':
            src, dst = fields
            axpy(matrix, dst, src, mono(q=-1))
            factor = mono(stages=(event[1],))
            scale_row(matrix, src, factor)
            scale_row(matrix, dst, factor)
        elif op == 'Q_POWER':
            scale_row(matrix, fields[0], mono(q=event[2]))
        elif op in ('IDLE', 'IDLE_ONE'):
            factor = mono(stages=event[-1])
            for field in fields:
                scale_row(matrix, field, factor)
        elif op == 'LAMBDA':
            scale_row(matrix, fields[0], lambda_poly(event[2]))
        need(sum(len(poly) for row in matrix for poly in row.values()) <= MAX_TERMS,
             'matrix term limit')
        if count in snapshots:
            saved[count] = [{col: dict(poly) for col, poly in row.items()} for row in matrix]
    return matrix, saved


def key20(value):
    need(type(value) is list and len(value) == 20, 'twenty exponent slots')
    for item in value:
        integer(item)
    need(value[1] == 0 and all(x >= 0 for x in value[2:]), 'dummy/stage exponents')
    return (value[0] % 4, 0, *value[2:])


def controller(obj, roles, events):
    need(type(obj) is dict and obj['roles'] == roles and type(obj['roles']) is int,
         'controller roles')
    need(type(obj['stages']) is int and obj['stages'] == STAGES, 'eighteen stages')
    need(type(obj['events']) is list and len(obj['events']) == events, 'controller event count')
    need(type(obj['diagonal']) is list and len(obj['diagonal']) == roles, 'entire diagonal')
    expected = [{i: {key20(key): GONE}} for i, key in enumerate(obj['diagonal'])]
    return expected


def column_combo(matrix, weights):
    return [sum_polys((row.get(int(col), {}), coefficient) for col, coefficient in weights.items())
            for row in matrix]


def sum_polys(terms):
    out = {}
    for poly, coefficient in terms:
        need(type(coefficient) is int, 'pair integer')
        out = plus(out, poly, mono(coefficient=(Fraction(coefficient), Fraction(0))))
    return out


def row_combo(matrix, weights):
    return [sum_polys((matrix[int(row)].get(col, {}), coefficient)
                      for row, coefficient in weights.items()) for col in range(len(matrix))]


def pair_vector(weights, size, factor):
    return [times(mono(coefficient=(Fraction(weights.get(str(i), 0)), Fraction(0))), factor)
            for i in range(size)]


def inverse_event(event):
    op = event[0]
    if op == 'ADD':
        return [op, event[1], event[2], str(-real_scalar(event[3]))]
    if op == 'SCALE':
        return [op, event[1], str(1 / real_scalar(event[2]))]
    if op == 'SWAP':
        return list(event)
    if op == 'LAMBDA':
        return [op, event[1], -event[2]]
    raise ValueError('unsupported cut inverse opcode')


def pairing(left, right):
    return sum(left.get(k, 0) * value for k, value in right.items())


def unit_and_cut(contract, final, witnesses):
    pair = contract['pair']
    need(pairing(pair['d'], pair['c']) == 1 and pairing(pair['b'], pair['a']) == 1,
         'unit pairings')
    need(type(witnesses) is list and len(witnesses) == 2, 'two witnesses')
    witness = witnesses[1]
    need(witness['cut_after'] == 394 and witness['handoff_after'] == 401 and
         witness['pivot'] == 4 and witness['fresh'] == 33, 'second witness indices')
    prefix_target = [-1] + [0] * 19
    prefix_target[11] = 1
    suffix_target = [0] * 20
    for stage in range(11, 15):
        suffix_target[stage + 1] = 1
    need(witness['prefix_stages'] == [10] and
         witness['prefix_target'] == prefix_target and
         witness['suffix_target'] == suffix_target, 'second witness targets')
    basis = witness['cut_basis']
    need(final['events'][398:402] == basis and final['events'][:3] == witness['input_basis'],
         'literal input/cut binding')
    derived = [inverse_event(event) for event in reversed(basis)]
    actual = []
    for source in final['events'][402:406]:
        event = list(source)
        positions = (1, 2) if event[0] in ('ADD', 'SWAP') else (1,)
        for pos in positions:
            if event[pos] == 33:
                event[pos] = 4
        actual.append(event)
    need(actual == derived, 'literal inverse order')
    result, _ = replay(basis + actual, 34)
    need(result == identity(34), 'cut basis inverse')
    ordinary, _ = replay(basis[:-1], 34)
    need(column_combo(ordinary, pair['a']) == pair_vector({'4': 1}, 34, mono()),
         'ordinary cut sends a to pivot')
    need(ordinary[4] == {int(k): mono(coefficient=(Fraction(v), Fraction(0)))
                         for k, v in pair['b'].items()}, 'ordinary pivot row equals b')
    inputs, _ = replay(witness['input_basis'], 34)
    need(column_combo(inputs, {'4': 1}) == pair_vector(pair['c'], 34, mono()),
         'input column equals c')
    need(row_combo(inputs, pair['d']) == pair_vector({'4': 1}, 34, mono()),
         'input dual row normalization')


def mutate(events, case):
    changed = [list(event) for event in events]
    if 'delete' in case:
        del changed[integer(case['delete'])]
    elif 'replace_index' in case:
        changed[integer(case['replace_index'])] = list(case['event'])
    elif 'swap_indices' in case:
        a, b = map(integer, case['swap_indices'])
        changed[a], changed[b] = changed[b], changed[a]
    elif 'insert_index' in case:
        changed.insert(integer(case['insert_index']), list(case['event']))
    elif 'replace_slice' in case:
        a, b = map(integer, case['replace_slice'])
        changed[a:b] = [list(event) for event in case['events']]
    else:
        raise ValueError('unknown semantic control')
    return changed


def encode_poly(poly):
    return [[list(key), [value[0].numerator, value[0].denominator,
                         value[1].numerator, value[1].denominator]]
            for key, value in sorted(poly.items())]


def encode_matrix(matrix):
    return [[encode_poly(row.get(col, {})) for col in range(len(matrix))] for row in matrix]


def calculate(contract, cases, data, sources):
    final = data['CONTROLLER.json']
    expected = controller(final, 34, 606)
    one = data['CONTROLLER-ONE-RETIRED.json']
    controller(one, 33, 592)
    controller(data['CONTROLLER-UNRETIRED.json'], 32, 576)
    witnesses = data['RETIREMENT-WITNESSES.json']
    need(type(witnesses) is list and len(witnesses) == 2, 'two retirement witnesses')
    witness = witnesses[1]
    need(final['events'][:402] == witness['input_basis'] + one['events'][:395] +
         witness['cut_basis'], 'literal entire cut-prefix surgery')
    need(all(4 not in instruction(event, 34)[1] for event in final['events'][402:]),
         'parked4 reused after retirement')
    full, saved = replay(final['events'], 34, (402,))
    need(full == expected, 'endpoint_mismatch')
    prefix = saved[402]
    retired = mono(q=-1, stages=(10,))
    need(prefix[4] == {4: retired} and
         all(row.get(4, {}) == (retired if i == 4 else {}) for i, row in enumerate(prefix)),
         'retired row/column4')
    need(prefix[33] == {33: mono()} and
         all(row.get(33, {}) == (mono() if i == 33 else {}) for i, row in enumerate(prefix)),
         'fresh33 row/column')
    need(all(33 not in instruction(event, 34)[1] for event in final['events'][:402]),
         'fresh33 first chronology')
    one_prefix, _ = replay(one['events'][:395], 33)
    body = times(lambda_poly(1), mono(q=-1, stages=(10,)))
    pair = contract['pair']
    need(column_combo(one_prefix, pair['c']) == pair_vector(pair['a'], 33, body),
         'one-prefix Pc')
    need(row_combo(one_prefix, pair['b']) == pair_vector(pair['d'], 33, body),
         'one-prefix bP')
    unit_and_cut(contract, final, witnesses)
    need(type(cases['controls']) is list and len(cases['controls']) == 7, 'seven controls')
    outcomes = []
    for case in cases['controls']:
        altered, _ = replay(mutate(final['events'], case), 34)
        need(altered != expected, 'semantic control accepted: ' + case['id'])
        outcomes.append({'id': case['id'], 'accepted': False, 'failure_gate': 'endpoint_mismatch'})
    return {'schema': contract['certificate']['schema'], 'sources': sources,
            'matrices': {'final606': encode_matrix(full), 'prefix402': encode_matrix(prefix),
                         'one_prefix395': encode_matrix(one_prefix)},
            'identities': {name: True for name in contract['identities']}, 'controls': outcomes}


def validate_packet(obj, contract, cases):
    need(type(obj) is dict and set(obj) == set(contract['certificate']['keys']), 'packet exact keys')
    need(obj['schema'] == contract['certificate']['schema'], 'packet schema')
    need(type(obj['sources']) is dict and set(obj['sources']) == SOURCE_NAMES and
         all(type(x) is str for x in obj['sources'].values()), 'packet source hashes')
    need(type(obj['matrices']) is dict and set(obj['matrices']) == set(contract['matrices']),
         'three entire matrices')
    total = 0
    for name, desc in contract['matrices'].items():
        matrix = obj['matrices'][name]
        need(type(matrix) is list and len(matrix) == desc['roles'], 'matrix rows')
        for row in matrix:
            need(type(row) is list and len(row) == desc['roles'], 'matrix columns')
            for cell in row:
                need(type(cell) is list, 'polynomial term list')
                last = None
                for term in cell:
                    need(type(term) is list and len(term) == 2, 'term pair')
                    key, coeff = term
                    normalized = key20(key)
                    need(key[0] in range(4) and tuple(key) == normalized, 'canonical exponent key')
                    need(last is None or last < normalized, 'sorted unique monomials')
                    last = normalized
                    need(type(coeff) is list and len(coeff) == 4, 'Gaussian rational quartet')
                    values = [integer(x) for x in coeff]
                    for num, den in ((values[0], values[1]), (values[2], values[3])):
                        need(den > 0 and gcd(num, den) == 1, 'reduced rational coefficient')
                    need(values[0] != 0 or values[2] != 0, 'omit zero terms')
                    total += 1
                    need(total <= 3 * MAX_TERMS, 'packet term limit')
    need(type(obj['identities']) is dict and set(obj['identities']) == set(contract['identities'])
         and all(type(x) is bool and x for x in obj['identities'].values()), 'six true identities')
    need(type(obj['controls']) is list and len(obj['controls']) == 7, 'seven ordered controls')
    for row, case in zip(obj['controls'], cases['controls']):
        need(type(row) is dict and set(row) == {'id', 'accepted', 'failure_gate'} and
             row['id'] == case['id'] and type(row['accepted']) is bool and not row['accepted'] and
             row['failure_gate'] == 'endpoint_mismatch', 'control record')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--certificate-out', type=Path)
    group.add_argument('--check', type=Path)
    parser.add_argument('--inputs-dir', type=Path, default=HERE / 'inputs')
    args = parser.parse_args()
    contract, cases, data, sources = authenticate(args.inputs_dir)
    packet = calculate(contract, cases, data, sources)
    validate_packet(packet, contract, cases)
    expected = canonical(packet)
    need(len(expected) <= JSON_LIMIT, 'certificate byte limit')
    if args.certificate_out:
        args.certificate_out.write_bytes(expected)
    else:
        raw = (args.check or HERE / 'CERTIFICATE.json').read_bytes()
        validate_packet(decode(raw), contract, cases)
        need(raw == expected, 'whole certificate bytes differ')
    print('PASS_CUT401_FORWARD_SPARSE matrices3 identities6 controls7 no_native_admission')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, TypeError, KeyError, IndexError, ZeroDivisionError) as error:
        print('FAIL_CUT401_FORWARD_SPARSE: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
