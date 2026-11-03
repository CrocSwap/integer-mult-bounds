#!/usr/bin/env python3
"""Exact sign corollary of the credited common-covector pair formulas."""
from fractions import Fraction
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SOURCE_HASH = '2b8bb283881df3bcad005e11fbe3aeaddc61b563babe9dd95c2dd18ae4fdbc59'
CASE_HASH = 'a8b26ebc34dbeb7f47b91f88eb0863bb4d6e914a6c26630e8cdd64dfe9ddf61b'
SCHEMA_HASH = '70db0325541f073c41886cf9fb43289723a6394d4c1e82d999dd49cda50507f5'
ROW_KEYS = {'q', 'n', 'marginal', 'joint', 'ratio', 'lower_bound', 'positive'}
TOP_KEYS = {'schema_version', 'source_manifest_sha256', 'case_manifest_sha256',
            'identities', 'cases'}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode()


def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def bad_number(value):
    raise ValueError('noninteger JSON number: ' + value)


def parse(raw):
    return json.loads(raw, object_pairs_hook=unique, parse_float=bad_number,
                      parse_constant=bad_number)


def typed_equal(left, right):
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(typed_equal(left[k], right[k]) for k in left)
    if isinstance(left, list):
        return len(left) == len(right) and all(typed_equal(a, b) for a, b in zip(left, right))
    return left == right


def authenticate():
    for name, expected in [('SOURCE-PINS.json', SOURCE_HASH), ('CASES.json', CASE_HASH),
                           ('SCHEMA.json', SCHEMA_HASH)]:
        require(sha((ROOT / name).read_bytes()) == expected, 'immutable ' + name)
    manifest = parse((ROOT / 'SOURCE-PINS.json').read_bytes())
    require(type(manifest) is dict and len(manifest['files']) == 2, 'two inert source documents')
    for row in manifest['files']:
        path = (ROOT / row['local_path']).resolve()
        require(path.parent == (ROOT / 'inputs').resolve(), 'source containment')
        raw = path.read_bytes()
        require(len(raw) == row['bytes'] and sha(raw) == row['sha256'], 'source bytes/SHA256')
        blob = b'blob ' + str(len(raw)).encode() + b'\0' + raw
        require(hashlib.sha1(blob).hexdigest() == row['git_blob'], 'source Git blob')
    return parse((ROOT / 'CASES.json').read_bytes()), parse((ROOT / 'SCHEMA.json').read_bytes())


def alpha(q):
    return q * q - q + 1


def delta(q):
    return q * q + (q - 1) ** 3


def coefficients(evaluate, degree):
    """Exact Vandermonde interpolation, independent of a convolution expansion."""
    work = [[Fraction(x ** power) for power in range(degree + 1)]
            + [Fraction(evaluate(x))] for x in range(degree + 1)]
    for column in range(degree + 1):
        pivot = next(row for row in range(column, degree + 1) if work[row][column])
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        work[column] = [entry / scale for entry in work[column]]
        for row in range(degree + 1):
            if row != column:
                scale = work[row][column]
                work[row] = [a - scale * b for a, b in zip(work[row], work[column])]
    answer = [row[-1] for row in work]
    require(all(x.denominator == 1 for x in answer), 'integer polynomial coefficients')
    result = [x.numerator for x in answer]
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def identities():
    return {
        'qD_minus_A2_q': coefficients(lambda q: q * delta(q) - alpha(q) ** 2, 4),
        'A_minus_q_t': coefficients(lambda t: alpha(t + 2) - (t + 2), 2),
        'twoA_minus_q_qplus1_t': coefficients(lambda t: 2 * alpha(t + 2) - (t + 2) * (t + 3), 2),
        'A2_minus_q3_t': coefficients(lambda t: alpha(t + 2) ** 2 - (t + 2) ** 3, 4),
    }


def pair(value):
    return [value.numerator, value.denominator]


def case(q, n):
    require(type(q) is int and type(n) is int, 'integer parameter domain')
    require(2 <= q <= 64 and 1 <= n <= 16, 'finite parameter domain')
    a, d, x = alpha(q), delta(q), q ** (n + 1)
    marginal = Fraction((q - 1) * a ** n, (x - 1) * q ** n)
    joint = Fraction((q - 1) * (d ** n - a ** n), (x - 1) * (x - q) * q ** (n - 1))
    ratio = joint / marginal ** 2
    lower = Fraction(q * (x - 1), (q - 1) * (x - q)) * (1 - Fraction(q, a) ** n)
    require(0 < marginal < 1 and 0 < joint < 1, 'source probability algebra range')
    require(ratio > lower >= 1, 'strict sign certificate ratio > L >= 1')
    if n == 1:
        require(lower == Fraction(q * q - 1, a), 'n1 exact lower bound')
    else:
        require(a ** n > x and lower > 1, 'n>=2 strict lower bound')
    return {'q': q, 'n': n, 'marginal': pair(marginal), 'joint': pair(joint),
            'ratio': pair(ratio), 'lower_bound': pair(lower), 'positive': ratio > 1}


def profile(cases, schema):
    result = identities()
    expected = {key: row['increasing_coefficients'] for key, row in schema['identities'].items()}
    require(typed_equal(result, expected), 'actual polynomial identity coefficients')
    require(len(cases['cases']) == cases['case_count'] == 205, '205 frozen parameter rows')
    return {'schema_version': 1, 'source_manifest_sha256': SOURCE_HASH,
            'case_manifest_sha256': CASE_HASH, 'identities': result,
            'cases': [case(row['q'], row['n']) for row in cases['cases']]}


def rational(value):
    require(type(value) is list and len(value) == 2, 'rational pair shape')
    require(all(type(x) is int for x in value), 'rational integers')
    require(value[1] > 0 and math.gcd(*value) == 1, 'reduced rational positive denominator')


def admit(value):
    require(type(value) is dict and value.keys() == TOP_KEYS, 'exact receipt keys')
    require(type(value['schema_version']) is int and value['schema_version'] == 1, 'integer receipt version')
    require(value['source_manifest_sha256'] == SOURCE_HASH and value['case_manifest_sha256'] == CASE_HASH,
            'receipt source/case binding')
    require(type(value['identities']) is dict and type(value['cases']) is list, 'receipt containers')
    for coeffs in value['identities'].values():
        require(type(coeffs) is list and all(type(x) is int for x in coeffs), 'identity integer coefficients')
    require(len(value['cases']) == 205, 'receipt case count')
    for row in value['cases']:
        require(type(row) is dict and row.keys() == ROW_KEYS, 'exact case keys')
        require(type(row['q']) is int and type(row['n']) is int, 'case integer parameters')
        require(type(row['positive']) is bool, 'strict positive boolean')
        for key in ['marginal', 'joint', 'ratio', 'lower_bound']:
            rational(row[key])


def check_receipt(value, expected):
    admit(value)
    require(typed_equal(value, expected), 'actual complete retained receipt differs')


def rejected(call, fragment):
    try:
        call()
    except ValueError as error:
        require(fragment in str(error), 'intended rejection: ' + fragment)
        return
    raise ValueError('negative control accepted: ' + fragment)


def controls(expected):
    for q, n in [(1, 1), (2, 0), (65, 1), (2, 17)]:
        rejected(lambda: case(q, n), 'finite parameter domain')
    rejected(lambda: case(True, 1), 'integer parameter domain')
    rejected(lambda: case(2, 1.0), 'integer parameter domain')
    rejected(lambda: parse(b'{"q":2,"q":3}'), 'duplicate')
    rejected(lambda: parse(b'{"q":NaN}'), 'noninteger')
    rejected(lambda: parse(b'{"q":2.0}'), 'noninteger')
    changes = [('schema_version', True), ('extra', 0)]
    for key, value in changes:
        bad = parse(canonical(expected)); bad[key] = value
        rejected(lambda: check_receipt(bad, expected), 'version' if key == 'schema_version' else 'keys')
    for key, value, fragment in [('ratio', [1, 1], 'differs'), ('positive', 1, 'boolean'),
                                  ('marginal', [True, 2], 'integers')]:
        bad = parse(canonical(expected)); bad['cases'][0][key] = value
        rejected(lambda: check_receipt(bad, expected), fragment)
    first = expected['cases'][0]
    require(first['lower_bound'] == [1, 1] and first['ratio'] == [4, 3], 'strict replacement at boundary')
    return 15


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--emit', type=Path)
    args = parser.parse_args()
    frozen_cases, schema = authenticate()
    value = profile(frozen_cases, schema)
    count = controls(value)
    if args.emit:
        args.emit.write_bytes(canonical(value))
    else:
        check_receipt(parse((ROOT / 'RESULT.json').read_bytes()), value)
    print('PASS_COMMON_COVECTOR_ALL_FIELD_POSITIVE cases=205 identities=4 controls=' + str(count))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        print('FAIL: ' + str(error), file=sys.stderr)
        sys.exit(1)
