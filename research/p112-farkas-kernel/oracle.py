#!/usr/bin/env python3
"""Independent exact certificate checking; no solver or predecessor execution.

This consumes the primary's sealed RESULT as untrusted certificate data. It is
independent verification of a discovered certificate, not blind rediscovery.
Credit Nick Petalas/6425, Jeremy Diviney/1422 and the retained geometry lineage.
New material: ToikY with OpenAI Codex assistance, Apache-2.0.
"""
import argparse
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
MANIFEST_SHA = 'd9d9e3785d6496adf112ccafbe25689057e9a1f28384ca28a536660c9f55f6e9'
PINS = {
    'README-6425.md': (7410, 'f35f0a30796e94ced74686bc3614b4478f5460bac0adb7c8d80827991f70ed0c',
                       'd9ce3b644cff65dadd88663189638a4bfd52bac3'),
    'RESULT-6425.json': (22234, 'f8d15306112914af299acca8720779fbc9f6f07bb1336c51e99304fdea5caf89',
                        'e18f92e001b8ce9d44287760516bf6ea002bcbcd'),
}
DIMENSION = 14
ROWS = 280
MAX_BYTES = 1024 * 1024


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def decode(raw):
    def unique(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    def nonfinite(value):
        raise ValueError('nonfinite JSON value: ' + value)
    def floating(value):
        number = float(value)
        require(math.isfinite(number), 'nonfinite JSON number')
        return number
    return json.loads(raw, object_pairs_hook=unique, parse_constant=nonfinite, parse_float=floating)


def bounded_read(path):
    with path.open('rb') as handle:
        value = handle.read(MAX_BYTES + 1)
    require(len(value) <= MAX_BYTES, 'input size bound')
    return value


def authenticate_sources(values, manifest):
    require(hashlib.sha256(manifest).hexdigest() == MANIFEST_SHA, 'source manifest SHA256')
    require(set(values) == set(PINS), 'exact two-source closure')
    for name, (length, digest, blob) in PINS.items():
        raw = values[name]
        require(len(raw) == length, 'source byte length: ' + name)
        require(hashlib.sha256(raw).hexdigest() == digest, 'source SHA256: ' + name)
        framed = b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw
        require(hashlib.sha1(framed).hexdigest() == blob, 'source Git blob: ' + name)


def mask(value):
    require(type(value) is str and 1 <= len(value) <= 6, 'hex mask string')
    try:
        number = int(value, 16)
    except ValueError:
        raise ValueError('invalid hex mask') from None
    require(value == hex(number) and 0 < number < 1 << DIMENSION, 'canonical 14-bit nonempty mask')
    return number


def rational(value):
    require(type(value) is str and 1 <= len(value) <= 512, 'bounded rational string')
    require(re.fullmatch(r'-?(?:0|[1-9][0-9]*)(?:/[1-9][0-9]*)?', value) is not None,
            'rational integer/quotient grammar')
    try:
        number = Fraction(value)
    except (ValueError, ZeroDivisionError):
        raise ValueError('invalid rational') from None
    require(abs(number.numerator).bit_length() <= 256 and number.denominator.bit_length() <= 256,
            'rational 256-bit capacity')
    require(str(number) == value, 'canonical rational string')
    return number


def source_rows(raw):
    source = decode(raw)
    require(type(source) is dict and source.get('kernel_rows') == ROWS, 'source row count')
    require(type(source.get('alphabet')) is list and len(source['alphabet']) == DIMENSION, 'source dimension')
    require(type(source.get('kernel')) is list and len(source['kernel']) == ROWS, 'source kernel list')
    rows = {}
    for record in source['kernel']:
        require(type(record) is list and len(record) == 3, 'source row shape')
        hit, demand, witness = record
        number = mask(hit)
        require(number not in rows, 'unique source masks')
        require(type(demand) is int and 1 <= demand <= 8, 'source demand integer')
        require(type(witness) is str and witness.startswith('0x'), 'source witness provenance')
        rows[number] = demand
    return rows


def certificate_sets(certificate, rows):
    require(type(certificate) is dict, 'certificate object')
    for name, expected in [('schema_version', 1), ('dimension', DIMENSION), ('source_rows', ROWS)]:
        require(type(certificate.get(name)) is int and certificate[name] == expected, 'typed ' + name)
    require(certificate.get('source_manifest_sha256') == MANIFEST_SHA, 'certificate source binding')
    retained = certificate.get('retained')
    require(type(retained) is list and 1 <= len(retained) < ROWS, 'strict retained-row reduction')
    numbers = [mask(value) for value in retained]
    require(len(set(numbers)) == len(numbers) and set(numbers) <= rows.keys(), 'distinct original retained rows')
    require(type(certificate.get('deletions')) is list and len(certificate['deletions']) == ROWS-len(numbers), 'deletion count')
    require(type(certificate.get('separators')) is list and len(certificate['separators']) == len(numbers), 'separator count')
    return set(numbers)


def deletion_check(record, retained, rows):
    require(type(record) is dict, 'deletion record')
    target = mask(record.get('target'))
    require(target in rows and target not in retained, 'deleted original row')
    terms = record.get('multipliers')
    require(type(terms) is list and 1 <= len(terms) <= ROWS, 'bounded multiplier list')
    coefficients, rhs, used = [Fraction(0) for _ in range(DIMENSION)], Fraction(0), set()
    for term in terms:
        require(type(term) is list and len(term) == 2, 'multiplier pair')
        donor, weight = mask(term[0]), rational(term[1])
        require(donor in retained and donor not in used, 'retained unique donor; no self or cyclic premise')
        require(weight >= 0, 'nonnegative multiplier')
        used.add(donor)
        rhs += weight * rows[donor]
        for column in range(DIMENSION):
            if donor >> column & 1:
                coefficients[column] += weight
    require(all(value <= (target >> k & 1) for k, value in enumerate(coefficients)), 'coefficient exceeds target')
    require(rhs >= rows[target], 'right-hand side below target demand')
    return {'target': hex(target), 'premises': len(terms), 'right_hand_side': str(rhs),
            'demand': rows[target], 'coefficients': [str(value) for value in coefficients]}


def dot(row, vector):
    total = Fraction(0)
    for column, value in enumerate(vector):
        if row >> column & 1:
            total += value
    return total


def separator_check(record, retained, rows):
    require(type(record) is dict, 'separator record')
    target = mask(record.get('target'))
    require(target in retained, 'retained separator target')
    encoded = record.get('x')
    require(type(encoded) is list and len(encoded) == DIMENSION, '14-coordinate separator')
    vector = [rational(value) for value in encoded]
    require(all(value >= 0 for value in vector), 'nonnegative separator coordinates')
    value = dot(target, vector)
    require(value < rows[target], 'separator must strictly violate target')
    slacks = [(dot(other, vector)-demand, other) for other, demand in rows.items() if other != target]
    require(len(slacks) == ROWS-1 and all(slack >= 0 for slack, _other in slacks), 'separator violates another original inequality')
    minimum, tight = min(slacks)
    return {'target': hex(target), 'x': [str(value) for value in vector], 'target_lhs': str(value),
            'target_demand': rows[target], 'strict_violation': str(rows[target]-value),
            'other_original_rows_checked': len(slacks), 'minimum_other_slack': str(minimum),
            'minimum_slack_row': hex(tight), 'integral_witness': all(value.denominator == 1 for value in vector)}


def verify_certificate(certificate, rows):
    retained = certificate_sets(certificate, rows)
    deletions = [deletion_check(record, retained, rows) for record in certificate['deletions']]
    targets = [mask(record['target']) for record in deletions]
    require(len(set(targets)) == len(targets) and set(targets) == rows.keys()-retained, 'complete disjoint deletion coverage')
    separators = [separator_check(record, retained, rows) for record in certificate['separators']]
    witnessed = [mask(record['target']) for record in separators]
    require(len(set(witnessed)) == len(witnessed) and set(witnessed) == retained, 'complete distinct separator coverage')
    return {'retained': [hex(value) for value in sorted(retained)],
            'deletions': sorted(deletions, key=lambda item: mask(item['target'])),
            'separators': sorted(separators, key=lambda item: mask(item['target']))}


def rejected(callback, expected):
    try:
        callback()
    except ValueError as error:
        require(expected in str(error), 'mutation rejected for unexpected reason: ' + str(error))
        return str(error)
    raise ValueError('mutated certificate unexpectedly accepted: ' + expected)


def negative_controls(certificate, rows, sources, manifest):
    controls = {}
    bad = deepcopy(certificate)
    bad['deletions'][0]['multipliers'][0][1] = '-1'
    controls['negative_multiplier'] = rejected(lambda: verify_certificate(bad, rows), 'nonnegative multiplier')
    bad = deepcopy(certificate)
    term = bad['deletions'][0]['multipliers'][0]
    term[1] = str(rational(term[1])+2)
    controls['coefficient_overrun'] = rejected(lambda: verify_certificate(bad, rows), 'coefficient exceeds target')
    bad = deepcopy(certificate)
    for term in bad['deletions'][0]['multipliers']:
        term[1] = '0'
    controls['zero_rhs'] = rejected(lambda: verify_certificate(bad, rows), 'right-hand side below target demand')
    bad = deepcopy(certificate)
    bad['deletions'][0]['multipliers'][0][0] = bad['deletions'][0]['target']
    controls['self_premise'] = rejected(lambda: verify_certificate(bad, rows), 'no self or cyclic premise')
    bad = deepcopy(certificate)
    bad['separators'][0]['x'][0] = '-1'
    controls['negative_coordinate'] = rejected(lambda: verify_certificate(bad, rows), 'nonnegative separator coordinates')
    bad = deepcopy(certificate)
    bad['separators'][0]['x'] = ['8'] * DIMENSION
    controls['nonviolating_witness'] = rejected(lambda: verify_certificate(bad, rows), 'strictly violate target')
    bad = deepcopy(certificate)
    bad['separators'][0]['x'] = ['0'] * DIMENSION
    controls['other_row_violation'] = rejected(lambda: verify_certificate(bad, rows), 'another original inequality')
    bad = deepcopy(certificate)
    bad['separators'].pop()
    controls['missing_witness'] = rejected(lambda: verify_certificate(bad, rows), 'separator count')
    altered = dict(sources)
    altered['RESULT-6425.json'] = b'X'+sources['RESULT-6425.json'][1:]
    controls['source_byte_mutation'] = rejected(lambda: authenticate_sources(altered, manifest), 'source SHA256')
    controls['duplicate_key'] = rejected(lambda: decode('{"a":1,"a":2}'), 'duplicate JSON key')
    controls['nonfinite_json'] = rejected(lambda: decode('{"a":NaN}'), 'nonfinite JSON')
    controls['overflowing_json_number'] = rejected(lambda: decode('{"a":1e999}'), 'nonfinite JSON')
    controls['noncanonical_rational'] = rejected(lambda: rational('2/4'), 'canonical rational')
    controls['exponent_rational'] = rejected(lambda: rational('1e999999999'), 'quotient grammar')
    return controls


def compute():
    manifest = bounded_read(ROOT / 'SOURCE-PINS.json')
    sources = {name: bounded_read(ROOT / 'sources' / name) for name in PINS}
    authenticate_sources(sources, manifest)
    rows = source_rows(sources['RESULT-6425.json'])
    certificate_bytes = bounded_read(ROOT / 'RESULT.json')
    certificate = decode(certificate_bytes)
    checked = verify_certificate(certificate, rows)
    controls = negative_controls(certificate, rows, sources, manifest)
    return {'schema_version': 1, 'status': 'PASS_INDEPENDENT_EXACT_FARKAS_CERTIFICATE_CHECK',
            'source_manifest_sha256': MANIFEST_SHA, 'source_result_sha256': PINS['RESULT-6425.json'][1],
            'primary_certificate_sha256': hashlib.sha256(certificate_bytes).hexdigest(),
            'method': 'Independent direct exact-rational checking of sealed primary certificate data; no solver, primary import, clique census or predecessor execution',
            'dimension': DIMENSION, 'source_rows': len(rows), 'retained_rows': len(checked['retained']),
            'removed_rows': len(checked['deletions']), 'checked': checked, 'negative_controls': controls,
            'limits': ['Fixed 14-rectangle nonnegative-real demand system from exact source6425 RESULT only.',
                       'Each deletion uses retained source rows only; every retained separator satisfies all other279 original rows.',
                       'Fractional separators prove real nonimplication; integral_witness labels an inspected stronger witness, not physical decoder admission.',
                       'Source clique census/witness validity and geometry-to-demand equivalence remain credited predecessor results, not rerun here.',
                       'No claim of fewest arbitrary inequalities, coefficient synthesis, COPY floor, native realization, kappa or frontier change.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true')
    args = parser.parse_args()
    result = compute()
    if args.emit:
        print(canonical(result))
    else:
        retained = decode(bounded_read(ROOT / 'ORACLE.json'))
        require(canonical(retained) == canonical(result), 'strict complete retained oracle receipt mismatch')
        print('PASS_INDEPENDENT_EXACT_FARKAS_CERTIFICATE_CHECK')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as error:
        print('FAIL: ' + str(error), file=sys.stderr)
        sys.exit(1)
