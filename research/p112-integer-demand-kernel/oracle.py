#!/usr/bin/env python3
"""Independent vector-DFS checking of a sealed integer-demand certificate.

The source matrix and real certificates are inert authenticated data. This
checker imports no predecessor or primary executable and uses no solver.
Prior real deletions and integral points retain their authors' credit.
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
MANIFEST_SHA = 'c326b2a83adb02af94954c3904ee6e59822bf5fd274c847851abdcb63c1b9c64'
PINS = {
    'MATRIX-6425.json': (22234, 'f8d15306112914af299acca8720779fbc9f6f07bb1336c51e99304fdea5caf89',
                         'e18f92e001b8ce9d44287760516bf6ea002bcbcd'),
    'REAL-RESULT-6455.json': (31660, 'b477f2a8d144ed884c78ee29ac76fd88c95b076eb2dd290ef2431dd7e4969704',
                              '1ee2f6269556d155b5d265b8c1a0ace6b0e13e22'),
    'README-6455.md': (5522, 'dd2849071a27cf4fa8023a8d3cba767199afeb977cc7e5c5acab361e5006804d',
                       '27aea79adbd206d95ffe94f01fa69d8ca478ab5e'),
}
DIMENSION, ROWS = 14, 280
MAX_BYTES = 1024 * 1024
MAX_ROW_PROFILES, MAX_TOTAL_PROFILES = 120000, 5000000


class CapacityError(ValueError):
    pass


def require(ok, message):
    if not ok:
        raise ValueError(message)


def capacity(ok, message):
    if not ok:
        raise CapacityError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def decode(raw):
    def unique(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    def bad(value):
        raise ValueError('nonfinite JSON value: ' + value)
    def floating(value):
        number = float(value)
        require(math.isfinite(number), 'nonfinite JSON number')
        return number
    return json.loads(raw, object_pairs_hook=unique, parse_constant=bad, parse_float=floating)


def read(path):
    with path.open('rb') as handle:
        raw = handle.read(MAX_BYTES+1)
    capacity(len(raw) <= MAX_BYTES, 'input exceeds one-MiB capacity')
    return raw


def authenticate(values, manifest):
    require(hashlib.sha256(manifest).hexdigest() == MANIFEST_SHA, 'source manifest SHA256')
    require(set(values) == set(PINS), 'exact three-source closure')
    for name, (length, digest, blob) in PINS.items():
        raw = values[name]
        require(len(raw) == length, 'source byte length: '+name)
        require(hashlib.sha256(raw).hexdigest() == digest, 'source SHA256: '+name)
        framed = b'blob '+str(len(raw)).encode('ascii')+b'\0'+raw
        require(hashlib.sha1(framed).hexdigest() == blob, 'source Git blob: '+name)


def mask(value):
    require(type(value) is str and 1 <= len(value) <= 6, 'bounded hex mask')
    try:
        number = int(value, 16)
    except ValueError:
        raise ValueError('invalid hex mask') from None
    require(value == hex(number) and 0 < number < 1 << DIMENSION, 'canonical nonempty 14-bit mask')
    return number


def rational(value):
    require(type(value) is str and len(value) <= 512, 'bounded rational string')
    require(re.fullmatch(r'-?(?:0|[1-9][0-9]*)(?:/[1-9][0-9]*)?', value) is not None, 'rational quotient grammar')
    number = Fraction(value)
    capacity(abs(number.numerator).bit_length() <= 256 and number.denominator.bit_length() <= 256,
             'rational exceeds 256-bit input capacity')
    require(str(number) == value, 'canonical rational')
    return number


def matrix(raw):
    source = decode(raw)
    require(type(source) is dict and source.get('kernel_rows') == ROWS, '280 source rows')
    require(type(source.get('alphabet')) is list and len(source['alphabet']) == DIMENSION, '14 source columns')
    records = source.get('kernel')
    require(type(records) is list and len(records) == ROWS, 'source kernel records')
    rows = {}
    for record in records:
        require(type(record) is list and len(record) == 3, 'source row shape')
        number = mask(record[0])
        require(number not in rows and type(record[1]) is int and 1 <= record[1] <= 8, 'source demand/unique mask')
        rows[number] = record[1]
    return dict(sorted(rows.items()))


def dot(number, vector):
    return sum(value for column, value in enumerate(vector) if number >> column & 1)


def integer_point(target, vector, rows):
    require(type(vector) is list and len(vector) == DIMENSION, '14 integer coordinates')
    require(all(type(value) is int and value >= 0 for value in vector), 'nonnegative integer coordinates')
    capacity(all(value.bit_length() <= 256 for value in vector), 'point exceeds 256-bit input capacity')
    require(dot(target, vector) < rows[target], 'point must strictly violate target')
    require(all(dot(other, vector) >= demand for other, demand in rows.items() if other != target),
            'point violates another original inequality')
    return {'target': hex(target), 'x': vector, 'target_lhs': dot(target, vector),
            'target_demand': rows[target], 'other_original_rows_checked': ROWS-1}


def old_deletion(record, retained, rows):
    target = mask(record['target'])
    require(target in rows and target not in retained, 'old deletion target')
    terms = record['multipliers']
    require(type(terms) is list and 1 <= len(terms) <= ROWS, 'old multiplier list')
    coefficients, rhs, used = [Fraction(0) for _ in range(DIMENSION)], Fraction(0), set()
    for term in terms:
        require(type(term) is list and len(term) == 2, 'old multiplier pair')
        donor, weight = mask(term[0]), rational(term[1])
        require(donor in retained and donor not in used and weight >= 0, 'old nonnegative unique retained premise')
        require(weight == 0 or donor != target and donor & target == donor, 'old strict-subset premise')
        used.add(donor)
        rhs += weight*rows[donor]
        for column in range(DIMENSION):
            coefficients[column] += weight*(donor >> column & 1)
    require(all(value <= (target >> k & 1) for k, value in enumerate(coefficients)), 'old coefficient overrun')
    require(rhs >= rows[target], 'old demand implication')
    return target


def prior_data(raw, rows):
    prior = decode(raw)
    require(type(prior) is dict and prior.get('dimension') == DIMENSION and prior.get('source_rows') == ROWS, 'prior dimensions')
    retained = {mask(value) for value in prior['retained']}
    require(len(retained) == 237 and retained <= rows.keys(), '237 prior retained rows')
    removed = [old_deletion(record, retained, rows) for record in prior['deletions']]
    require(len(removed) == 43 and len(set(removed)) == 43 and set(removed) == rows.keys()-retained, '43 prior real deletions')
    require(type(prior.get('separators')) is list and len(prior['separators']) == 237, '237 prior separator records')
    integral, seen = {}, set()
    for record in prior['separators']:
        target = mask(record['target'])
        require(target in retained and target not in seen, 'distinct prior separator target')
        seen.add(target)
        require(type(record['x']) is list and len(record['x']) == DIMENSION, 'prior separator dimension')
        vector = [rational(value) for value in record['x']]
        if all(value.denominator == 1 for value in vector):
            converted = [value.numerator for value in vector]
            integer_point(target, converted, rows)
            integral[target] = converted
    require(len(integral) == 134, '134 actual integral prior points')
    return set(removed), integral


def profiles(width, budget):
    """Every nonnegative vector with sum<=budget has one root-to-leaf path."""
    pending = [(0, budget, ())]
    while pending:
        column, remaining, prefix = pending.pop()
        if column == width:
            yield prefix
        else:
            for value in range(remaining+1):
                pending.append((column+1, remaining-value, prefix+(value,)))


def first_miss(vector, constraints):
    for number, demand, columns in constraints:
        if sum(vector[column] for column in columns) < demand:
            return number
    return None


def obstruction(target, rows, budget_limit=MAX_ROW_PROFILES):
    coordinates = [column for column in range(DIMENSION) if target >> column & 1]
    budget = rows[target]-1
    expected = math.comb(len(coordinates)+budget, len(coordinates))
    capacity(expected <= budget_limit, 'row profile capacity exceeded')
    constraints = [(number, demand, tuple(k for k, column in enumerate(coordinates) if number >> column & 1))
                   for number, demand in rows.items() if number != target and number & target == number]
    histogram, checked = {}, 0
    for vector in profiles(len(coordinates), budget):
        checked += 1
        capacity(checked <= expected, 'enumerator exceeded closed-form coverage')
        missed = first_miss(vector, constraints)
        require(missed is not None, 'obstruction has an integer counterexample')
        histogram[missed] = histogram.get(missed, 0)+1
    require(checked == expected, 'enumerator incomplete closed-form coverage')
    return {'target': hex(target), 'coordinates': coordinates, 'budget': budget,
            'expected_profiles': expected, 'checked_profiles': checked,
            'miss_histogram': [[hex(number), count] for number, count in sorted(histogram.items())]}


def partition(certificate, rows, old_removed, old_points):
    require(type(certificate) is dict, 'certificate object')
    for key, value in [('schema_version', 1), ('dimension', DIMENSION), ('source_rows', ROWS)]:
        require(type(certificate.get(key)) is int and certificate[key] == value, 'typed '+key)
    require(certificate.get('source_manifest_sha256') == MANIFEST_SHA, 'certificate source binding')
    require(type(certificate.get('retained')) is list, 'retained list')
    ordered = [mask(value) for value in certificate['retained']]
    retained = set(ordered)
    require(len(ordered) == len(retained) and old_points.keys() <= retained <= rows.keys(), 'retained distinct/prior coverage')
    require(type(certificate.get('reused_real_deletions')) is list, 'reused deletion list')
    reused = [mask(value) for value in certificate['reused_real_deletions']]
    require(len(reused) == 43 and set(reused) == old_removed, 'exact reused real deletions')
    require(type(certificate.get('obstructions')) is list and type(certificate.get('witnesses')) is list, 'obstruction/witness lists')
    removed = [mask(record['target']) for record in certificate['obstructions']]
    require(len(set(removed)) == len(removed), 'distinct obstruction targets')
    require(not(retained & old_removed or retained & set(removed) or old_removed & set(removed)), 'disjoint partition')
    require(retained | old_removed | set(removed) == rows.keys(), 'complete 280-row partition')
    expected = sum(math.comb(number.bit_count()+rows[number]-1, number.bit_count()) for number in removed)
    capacity(expected <= MAX_TOTAL_PROFILES, 'total profile capacity exceeded')
    return retained


def positive_checks(records, retained, rows, old_points):
    require(len(records) == len(retained), 'positive witness count')
    checked, seen = [], set()
    for record in records:
        require(type(record) is dict, 'positive witness record')
        target = mask(record.get('target'))
        require(target in retained and target not in seen, 'unique retained witness')
        seen.add(target)
        if target in old_points:
            require(record.get('origin') == 'prior-integral' and record.get('x') == old_points[target], 'literal credited prior integral witness')
        else:
            require(record.get('origin') == 'new-integer', 'new integer witness origin')
        point = integer_point(target, record.get('x'), rows)
        point['origin'] = record['origin']
        checked.append(point)
    return sorted(checked, key=lambda item: mask(item['target']))


def verify_certificate(certificate, rows, old_removed, old_points):
    retained = partition(certificate, rows, old_removed, old_points)
    points = positive_checks(certificate['witnesses'], retained, rows, old_points)
    negative = []
    for record in certificate['obstructions']:
        target = mask(record['target'])
        expected = obstruction(target, rows)
        same_obstruction(record, expected)
        negative.append(expected)
    return {'retained': [hex(value) for value in sorted(retained)],
            'integer_witnesses': points, 'new_obstructions': sorted(negative, key=lambda item: mask(item['target']))}


def same_obstruction(record, expected):
    for key, value in expected.items():
        require(key in record and canonical(record[key]) == canonical(value), 'exact obstruction '+key)


def reject(callback, expected):
    try:
        callback()
    except ValueError as error:
        require(expected in str(error), 'unexpected rejection reason: '+str(error))
        return str(error)
    raise ValueError('negative control accepted: '+expected)


def prior_negative_controls(sources, rows):
    prior = decode(sources['REAL-RESULT-6455.json'])
    retained = {mask(value) for value in prior['retained']}
    result = {}
    bad = deepcopy(prior['deletions'][0])
    bad['multipliers'][0][1] = '-1'
    result['old_negative_multiplier'] = reject(lambda: old_deletion(bad, retained, rows), 'old nonnegative')
    bad = deepcopy(prior['deletions'][0])
    bad['multipliers'][0][1] = str(rational(bad['multipliers'][0][1])+2)
    result['old_coefficient_overrun'] = reject(lambda: old_deletion(bad, retained, rows), 'old coefficient overrun')
    bad = deepcopy(prior['deletions'][0])
    for term in bad['multipliers']:
        term[1] = '0'
    result['old_zero_rhs'] = reject(lambda: old_deletion(bad, retained, rows), 'old demand implication')
    return result


def negative_controls(certificate, rows, old_removed, old_points, sources, manifest, checked):
    result = {}
    retained = {mask(value) for value in certificate['retained']}
    bad = deepcopy(certificate['witnesses'])
    bad[0]['x'][0] = -1
    result['negative_point'] = reject(lambda: integer_point(mask(bad[0]['target']), bad[0]['x'], rows), 'nonnegative integer coordinates')
    target = mask(certificate['witnesses'][0]['target'])
    result['nonviolating_point'] = reject(lambda: integer_point(target, [8]*DIMENSION, rows), 'strictly violate target')
    result['other_row_point_violation'] = reject(lambda: integer_point(target, [0]*DIMENSION, rows), 'another original inequality')
    target = min(old_points)
    result['false_obstruction'] = reject(lambda: obstruction(target, rows), 'integer counterexample')
    result['row_capacity_UNKNOWN'] = reject(lambda: obstruction(target, rows, 0), 'profile capacity')
    bad = deepcopy(certificate)
    bad['reused_real_deletions'].pop()
    result['missing_prior_deletion'] = reject(lambda: partition(bad, rows, old_removed, old_points), 'exact reused real deletions')
    bad = deepcopy(certificate['witnesses'])
    prior_index = next(i for i, record in enumerate(bad) if mask(record['target']) in old_points)
    bad[prior_index]['x'] = list(bad[prior_index]['x'])
    bad[prior_index]['x'][0] += 1
    result['altered_prior_point'] = reject(lambda: positive_checks(bad, retained, rows, old_points), 'literal credited prior')
    altered = dict(sources)
    altered['MATRIX-6425.json'] = b'X'+sources['MATRIX-6425.json'][1:]
    result['source_byte_mutation'] = reject(lambda: authenticate(altered, manifest), 'source SHA256')
    result['duplicate_key'] = reject(lambda: decode('{"x":1,"x":2}'), 'duplicate JSON key')
    result['nonfinite'] = reject(lambda: decode('{"x":1e999}'), 'nonfinite JSON')
    result['rational_exponent'] = reject(lambda: rational('1e999999'), 'quotient grammar')
    if checked['new_obstructions']:
        expected_record = checked['new_obstructions'][0]
        bad = deepcopy(expected_record)
        bad['checked_profiles'] -= 1
        result['altered_saved_profile_count'] = reject(lambda: same_obstruction(bad, expected_record), 'exact obstruction checked_profiles')
        bad = deepcopy(expected_record)
        bad['miss_histogram'][0][1] += 1
        result['altered_saved_first_miss_histogram'] = reject(lambda: same_obstruction(bad, expected_record), 'exact obstruction miss_histogram')
    else:
        result['obstruction_mutation_scope'] = 'Not applicable: no new obstruction certificate exists.'
    expected = {(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (2, 0)}
    observed = list(profiles(2, 2))
    require(len(observed) == math.comb(4, 2) and set(observed) == expected, 'literal vector-DFS toy coverage')
    result['literal_vector_DFS_toy'] = {'profiles': sorted(observed), 'count': len(observed)}
    result.update(prior_negative_controls(sources, rows))
    return result


def compute():
    manifest = read(ROOT/'SOURCE-PINS.json')
    sources = {name: read(ROOT/'sources'/name) for name in PINS}
    authenticate(sources, manifest)
    rows = matrix(sources['MATRIX-6425.json'])
    old_removed, old_points = prior_data(sources['REAL-RESULT-6455.json'], rows)
    raw = read(ROOT/'RESULT.json')
    certificate = decode(raw)
    checked = verify_certificate(certificate, rows, old_removed, old_points)
    controls = negative_controls(certificate, rows, old_removed, old_points, sources, manifest, checked)
    return {'schema_version': 1, 'status': 'PASS_INDEPENDENT_INTEGER_DEMAND_KERNEL',
            'source_manifest_sha256': MANIFEST_SHA, 'primary_certificate_sha256': hashlib.sha256(raw).hexdigest(),
            'dimension': DIMENSION, 'source_rows': ROWS, 'retained_rows': len(checked['retained']),
            'reused_real_deletions': len(old_removed), 'reused_integral_points': len(old_points),
            'new_obstructions': len(checked['new_obstructions']),
            'total_new_obstruction_profiles': sum(record['checked_profiles'] for record in checked['new_obstructions']),
            'new_integer_points': len(checked['integer_witnesses'])-len(old_points),
            'method': 'Independent iterative vector-budget DFS verifies sealed primary data; literal all279-original-row integer points; no solver or primary/predecessor executable import',
            'checked': checked, 'negative_controls': controls,
            'limits': ['Fixed original280-row nonnegative-integer system; outside=8 constructs witnesses, not a global cap.',
                       'Every new obstruction exhausts all inside totals<=demand-1; strict-subset source premises yield simultaneous implication by induction.',
                       '43 real implications and134 integral source points are authenticated credited reuse, not new coverage.',
                       'Five-million total profiles,120000 per row,one-MiB inputs and256-bit input integers/rationals are fail-UNKNOWN capacities.',
                       'No smallest arbitrary inequality description, changed cap alphabet, COPY floor, decoder, native supplier, kappa or frontier claim.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true')
    args = parser.parse_args()
    result = compute()
    if args.emit:
        print(canonical(result))
    else:
        retained = decode(read(ROOT/'ORACLE.json'))
        require(canonical(retained) == canonical(result), 'strict complete oracle receipt drift')
        print('PASS_INDEPENDENT_INTEGER_DEMAND_KERNEL')


if __name__ == '__main__':
    try:
        main()
    except CapacityError as error:
        print('UNKNOWN: '+str(error), file=sys.stderr)
        sys.exit(1)
    except (ValueError, KeyError, TypeError, OSError) as error:
        print('FAIL: '+str(error), file=sys.stderr)
        sys.exit(1)
