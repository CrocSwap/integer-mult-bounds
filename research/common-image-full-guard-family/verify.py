#!/usr/bin/env python3
"""Binary full-guard common-image orbit formula and complete small-header census."""
from collections import Counter
from fractions import Fraction
import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
SOURCE_HASH = '680b0d75e9419b4577dd0710a8c430c512f12f9ae70ba9d0ce6c91acc3fbefc9'
CASE_HASH = '3da07e088ca190dc480ce52aab01c44816d334fe32b82ba88a9787f380e99273'
SCHEMA_HASH = 'c01cd12853adcce258701b3d8e56bfff7ba9d370223dcecccc62200ef8bd087a'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode()


def unique(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, 'duplicate JSON key')
        value[key] = item
    return value


def bad_number(value):
    raise ValueError('nonfinite JSON number: ' + value)


def parse(raw):
    return json.loads(raw, object_pairs_hook=unique, parse_constant=bad_number)


def same_typed(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(same_typed(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(same_typed(x, y) for x, y in zip(a, b))
    return a == b


def authenticate():
    for name, expected in [('SOURCE-PINS.json', SOURCE_HASH), ('CASES.json', CASE_HASH), ('SCHEMA.json', SCHEMA_HASH)]:
        require(sha((ROOT / name).read_bytes()) == expected, 'immutable ' + name)
    manifest = parse((ROOT / 'SOURCE-PINS.json').read_bytes())
    require(type(manifest) is dict and len(manifest['files']) == 8, 'eight inert sources')
    for row in manifest['files']:
        path = (ROOT / row['local_path']).resolve()
        require(path.parent == (ROOT / 'inputs').resolve(), 'source containment')
        raw = path.read_bytes()
        require(len(raw) == row['bytes'] and sha(raw) == row['sha256'], 'source bytes/SHA256')
        require(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['git_blob'], 'source Git blob')
    return parse((ROOT / 'CASES.json').read_bytes())


def rational(value):
    return [value.numerator, value.denominator]


def gl_order(m):
    return math.prod((1 << m) - (1 << i) for i in range(m))


def available_columns(j, k):
    if j < k - 1:
        return 0
    return (1 << j) * math.prod((1 << j) - (1 << i) for i in range(k - 1))


def family_row(m, k):
    require(type(m) is int and type(k) is int and m >= 2 and 1 <= k <= m, 'common-image dimensions')
    histogram = [math.comb(m - 1, j) * available_columns(j, k) for j in range(m)]
    numerator = sum(histogram)
    denominator = ((1 << m) - 1) * available_columns(m - 1, k)
    require(gl_order(m) % denominator == 0, 'integer header fiber')
    fiber = gl_order(m) // denominator
    require(fiber == (1 << ((k - 1) * (m - k))) * gl_order(m - k), 'stabilizer block count')
    return {'m': m, 'k': k, 'support_histogram': histogram, 'orbit_numerator': numerator,
            'orbit_denominator': denominator, 'probability': rational(Fraction(numerator, denominator)),
            'header_fiber': fiber}


def inverse(rows, m):
    work = [row | (1 << (m + i)) for i, row in enumerate(rows)]
    for col in range(m):
        pivot = next((r for r in range(col, m) if (work[r] >> col) & 1), None)
        if pivot is None:
            return None
        work[col], work[pivot] = work[pivot], work[col]
        for r in range(m):
            if r != col and ((work[r] >> col) & 1):
                work[r] ^= work[col]
    return [row >> m for row in work]


def rank(rows, m):
    work = list(rows); pivot_row = 0
    for col in range(m):
        pivot = next((r for r in range(pivot_row, len(work)) if (work[r] >> col) & 1), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        for r in range(pivot_row + 1, len(work)):
            if (work[r] >> col) & 1:
                work[r] ^= work[pivot_row]
        pivot_row += 1
    return pivot_row


def multiply(left, right, m):
    value = []
    for row in left:
        result = 0
        for j in range(m):
            if (row >> j) & 1:
                result ^= right[j]
        value.append(result)
    return value


def apply(rows, vector):
    return sum(((row & vector).bit_count() % 2) << i for i, row in enumerate(rows))


def row_apply(row, matrix, m):
    result = 0
    for j in range(m):
        if (row >> j) & 1:
            result ^= matrix[j]
    return result


def outer(u, v, m):
    return [v if (u >> i) & 1 else 0 for i in range(m)]


def projector(u, v, m):
    return [row ^ (1 << i) for i, row in enumerate(outer(u, v, m))]


def minors(rows, m):
    return [int(rank([row & ((1 << size) - 1) for row in rows[:size]], size) == size)
            for size in range(1, m)]


def validate_tuple(u, covectors, m):
    require(type(u) is int and 0 < u < (1 << m), 'nonzero common image vector')
    require(all(type(v) is int and 0 < v < (1 << m) for v in covectors), 'covector encodings')
    require(all((u & v).bit_count() % 2 == 1 for v in covectors), 'idempotence pairing')
    require(rank(covectors, m) == len(covectors), 'independent covectors')


def small_gl(m):
    last = 1 << (m - 1)
    covectors = [last] + [last | (1 << i) for i in range(m - 1)]
    validate_tuple(last, covectors, m)
    projectors = [projector(last, v, m) for v in covectors]
    records, histogram = [], [0] * (1 << m)
    frequencies = [Counter() for _ in range(m)]
    passing_orbits = [set() for _ in range(m)]
    for code in range(1 << (m * m)):
        header = [(code >> (m * i)) & ((1 << m) - 1) for i in range(m)]
        inv = inverse(header, m)
        if inv is None:
            continue
        mask = 0
        for i, p in enumerate(projectors):
            conjugate = multiply(multiply(header, p, m), inv, m)
            if all(minors(conjugate, m)):
                mask |= 1 << i
        records.append([code, mask]); histogram[mask] += 1
        transformed_u = apply(header, last)
        transformed_v = [row_apply(v, inv, m) for v in covectors]
        for k in range(1, m + 1):
            key = (transformed_u, *transformed_v[:k])
            frequencies[k - 1][key] += 1
            if mask & ((1 << k) - 1) == (1 << k) - 1:
                passing_orbits[k - 1].add(key)
    require(len(records) == gl_order(m), 'complete GL census')
    joints = [sum(count for mask, count in enumerate(histogram) if mask & ((1 << k) - 1) == (1 << k) - 1) for k in range(1, m + 1)]
    for k in range(1, m + 1):
        closed = family_row(m, k)
        require(len(frequencies[k - 1]) == closed['orbit_denominator'], 'complete actual orbit coverage')
        require(set(frequencies[k - 1].values()) == {closed['header_fiber']}, 'literal uniform conjugation fibers')
        require(len(passing_orbits[k - 1]) == closed['orbit_numerator'], 'actual passing orbit count')
        require(Fraction(joints[k - 1], len(records)) == Fraction(*closed['probability']), 'literal full-minor joint')
    profile = {'m': m, 'gl_count': len(records), 'mask_histogram': histogram,
               'joint_first_k': joints, 'record_sha256': sha(canonical(records))}
    return profile, {'m': m, 'records': records}


def example(spec):
    m, k, u, vs, header = (spec[key] for key in ['m', 'k', 'u', 'v_rows', 'header_rows'])
    validate_tuple(u, vs, m)
    us = [outer(u, v, m) for v in vs]
    for i, first in enumerate(us):
        require(rank(first, m) == 1 and multiply(first, first, m) == first, 'literal rank-one idempotent')
        nonzero_columns = {apply(first, 1 << j) for j in range(m)} - {0}
        require(nonzero_columns == {u}, 'literal common image')
        for j in range(i):
            require(first != us[j] and multiply(first, us[j], m) == us[j]
                    and multiply(us[j], first, m) == first, 'distinct noncommuting family')
    inv = inverse(header, m); require(inv is not None, 'example complete header')
    guards = [minors(multiply(multiply(header, projector(u, v, m), m), inv, m), m) for v in vs]
    require(all(all(row) for row in guards), 'literal complete proposed header')
    joint = Fraction(*family_row(m, k)['probability'])
    single = Fraction(3 ** (m - 1), ((1 << m) - 1) * (1 << (m - 1)))
    product = single ** k; ratio = joint / product
    require(joint == Fraction(22, 2667) and ratio > 1, 'six-family exact comparison')
    return {'m': m, 'k': k, 'u': u, 'v_rows': vs, 'header_rows': header,
            'proper_minors': guards, 'joint_probability': rational(joint),
            'single_probability': rational(single), 'product_probability': rational(product),
            'ratio': rational(ratio), 'ratio_gt_one': ratio > 1}


def controls():
    require(minors(projector(7, 2, 3), 3) == [1, 0], 'first-pivot-only versus full-guard counterexample')
    require(rank([4, 4], 3) < 2, 'duplicate rank control')
    require(rank([8, 9, 10, 11], 4) == 3, 'distinct but dependent covectors control')
    require((4 & 1).bit_count() % 2 == 0, 'nonidempotent wrong terminal column')
    require(available_columns(0, 2) == 0 and available_columns(1, 2) < 4, 'rank constraint cannot be dropped')
    for m in range(2, 17):
        n = m - 1
        require(family_row(m, 1)['probability'] == rational(Fraction(3 ** n, ((1 << m) - 1) * (1 << n))), 'credited marginal k1')
        prior_pair = Fraction(5 ** n - 3 ** n, ((1 << m) - 1) * ((1 << m) - 2) * (1 << (m - 2)))
        require(family_row(m, 2)['probability'] == rational(prior_pair), 'credited transpose4807 k2')
    require(not same_typed({'v': 1}, {'v': True}) and not same_typed({'v': 1}, {'v': 1.0}), 'strict number aliases')


def admit(value):
    require(type(value) is dict and set(value) == {'schema_version', 'source_manifest_sha256', 'case_manifest_sha256', 'family', 'small_gl', 'example'}, 'receipt keyset')
    require(type(value['schema_version']) is int and value['schema_version'] == 1, 'receipt version')
    for key in ['source_manifest_sha256', 'case_manifest_sha256']:
        require(type(value[key]) is str and re.fullmatch('[0-9a-f]{64}', value[key]), 'receipt digest')
    require(type(value['family']) is list and len(value['family']) == 135, 'family domain')
    for row in value['family']:
        require(type(row) is dict and set(row) == {'m', 'k', 'support_histogram', 'orbit_numerator', 'orbit_denominator', 'probability', 'header_fiber'}, 'family keyset')
        require(all(type(row[key]) is int for key in ['m', 'k', 'orbit_numerator', 'orbit_denominator', 'header_fiber']), 'family integers')
        require(type(row['support_histogram']) is list and all(type(n) is int and n >= 0 for n in row['support_histogram']), 'support integer histogram')
    return value


def compute():
    cases = authenticate()
    families = [family_row(m, k) for m, k in cases['family_cases']]
    small, domains = [], []
    for m in cases['small_gl_dimensions']:
        profile, domain = small_gl(m); small.append(profile); domains.append(domain)
    controls()
    result = {'schema_version': 1, 'source_manifest_sha256': SOURCE_HASH, 'case_manifest_sha256': CASE_HASH,
              'family': families, 'small_gl': small, 'example': example(cases['example'])}
    return admit(result), {'schema_version': 1, 'domains': domains}


def read_small(path):
    with gzip.open(path, 'rb') as stream:
        raw = stream.read(8388609)
    require(len(raw) <= 8388608, 'small-GL decompressed bound')
    return parse(raw)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', type=Path)
    parser.add_argument('--write-small', type=Path)
    args = parser.parse_args(); result, artifact = compute()
    if args.write_small:
        args.write_small.write_bytes(gzip.compress(canonical(artifact), mtime=0))
    path = args.write_small if args.write_small else ROOT / 'SMALL-GL.json.gz'
    require(same_typed(read_small(path), artifact), 'all actual header-code/full-mask rows/types')
    if args.emit:
        args.emit.write_bytes(canonical(result))
    else:
        retained = admit(parse((ROOT / 'RESULT.json').read_bytes()))
        require(same_typed(retained, result), 'whole family/header/example profile')
    print(json.dumps({'status': 'pass', 'family_cases': 135, 'complete_headers': 20334,
                      'all_full_guards': True, 'seven_dimensional_header': 'explicit only'}, sort_keys=True))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as error:
        print('FAIL: ' + str(error), file=sys.stderr)
        raise SystemExit(1) from error
